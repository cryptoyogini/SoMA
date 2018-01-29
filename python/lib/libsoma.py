'''
Contains SoMA Core functions and classes
'''
from uuid import *
import json
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from BeautifulSoup import BeautifulSoup
import ConfigParser
import time,os,urllib2
from datetime import datetime
from uuid import *
from pygments import highlight, lexers, formatters
import pygsheets
DEBUG=False



'''
SoMA Post objects store a JSON object as a named tuple as well as a dictionary, so that attributes can be referenced both in the dot notation as well as by key/value lookups. 
'''

def get_color_json(dictionary):
	formatted_json=get_formatted_json(dictionary)
	colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
	return colorful_json

def get_formatted_json(dictionary):
	formatted_json=json.dumps(dictionary,sort_keys=True, indent=4)
	return formatted_json

class SoMAPost:
	def __init__(self,jsoncontent=None):
		self.uuid=uuid4()
		if jsoncontent==None:
			self.content=None
		else:
			#Got this nice little object factory like implementation from https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object for the dot notation support
			self.attributes=json.loads(jsoncontent,object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			#This just loads the same content into a dict as well
			self.dictionary=json.loads(jsoncontent)

class SoMAPerson:
	def __init__(self,jsonfile):
		self.jsonfile=jsonfile	
		if not os.path.exists(jsonfile):
			self.uuid=str(uuid4())
			self.jsonprofile={}
			self.jsonprofile['uuid']=self.uuid
			with open(jsonfile,"w") as f:
				f.write(json.dumps(self.jsonprofile,indent=4,sort_keys=True))
		else:
			#This just loads the same content into a dict as well
			with open(jsonfile,"r") as f:
				self.jsonprofile=json.loads(f.read())
			self.uuid=self.jsonprofile['uuid']
	def show_profile(self):
		print get_color_json(self.jsonprofile)
	def save_profile(self):
		with open(self.jsonfile,"w") as f:
			f.write(json.dumps(self.jsonprofile,indent=4,sort_keys=True))
	def get_property(self,propertyname):
		if propertyname in self.jsonprofile.keys():
			return self.jsonprofile[propertyname]
		else:
			return None
	def set_property(self,propertyname,value):
		self.jsonprofile[propertyname]=value
	def populate_fbprofile(self,cyborg,url):
		fbprofile=cyborg.fb_get_profile_data(url)
		fbprofilejson=cyborg.save_json(fbprofile,path=os.path.split(self.jsonfile)[0])
		fbprofiles=self.get_property("fbprofiles")
		if fbprofiles==None:
			fbprofiles=[]
		fbprofiles.append(fbprofilejson)
		self.set_property("fbprofiles",fbprofiles)
		self.set_property("name",fbprofile['fbdisplayname'].replace("\n"," "))
		self.set_property("profilepic",fbprofile['profilepic'])
	def add_note(self,text):
		notes=self.get_property("notes")
		if notes==None:
			notes=[]
		ts=datetime.now().strftime("%Y-%d-%m %H:%M:%S")
		notedict={}
		notedict['ts']=ts
		notedict['text']=text
		notes.append(notedict)
		self.set_property("notes",notes)

class SoMACyborg(object):
	def __init__(self,configfile,headless=False):
		config=ConfigParser.ConfigParser()
		config.read(configfile)
		self.config=config
		try:
			self.fbusr = config.get("User","fbusername")
			self.fbpwd = config.get("User","fbpassword")
		except:
			print "Cyborg did not have an FB id configured"
		try:
			self.googleusr = config.get("User","googleusername")
			self.googlepwd = config.get("User","googlepassword")
		except:
			print "Cyborg did not have an Google id configured"
		try:
			self.outhstore = config.get("Google","outhstore")
			self.outhfile = config.get("Google","outhfile")
		except:
			print "Cyborg did not get a google client secret"
		try:
			print "Trying to log in"
			self.gc=pygsheets.authorize(outh_file=self.outhfile,outh_nonlocal=True,outh_creds_store=self.outhstore)
		except:
			print "Failed to log in to google drive"
		self.datapath=config.get("System","datapath")
		sessionpathprefix=config.get("System","sessionpathprefix")
		ts=datetime.now()
		sessiondir=sessionpathprefix+"-"+ts.strftime("%Y%b%d-%H%M%S")
		self.sessionpath=os.path.join(self.datapath,sessiondir)
		self.sessiondownloaddir=os.path.join(self.sessionpath,"downloads")
		self.sessionjsonpath=os.path.join(self.sessionpath,"json")
		if not os.path.exists(self.datapath):
			os.mkdir(self.datapath)
		if not os.path.exists(self.sessionpath):
			os.mkdir(self.sessionpath)
		if not os.path.exists(self.sessiondownloaddir):
			os.mkdir(self.sessiondownloaddir)
		if not os.path.exists(self.sessionjsonpath):
			os.mkdir(self.sessionjsonpath)
		
		if headless==True:
			os.environ['MOZ_HEADLESS'] = '1'
		
		firefox_profile = webdriver.FirefoxProfile()
		firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
		firefox_profile.set_preference("browser.download.dir", self.sessiondownloaddir);
		firefox_profile.set_preference("browser.download.folderList", 2);
		firefox_profile.set_preference("browser.download.manager.showWhenStarting", False);
		firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain, text/csv",)
		driver = webdriver.Firefox(firefox_profile=firefox_profile)
		self.driver=driver
		
		
	
	
	
	
	def goto_url(self,url):
 		self.driver.get(url)
 			
	def download_file(self,url,path=None,filename=None,prefix=None,suffix=None):
		print "Trying to download "+ url
		if path==None:
			path=self.sessiondownloaddir
		if filename==None:
			filename=str(uuid4())
		if prefix != None:
			filename=prefix+filename
		if suffix != None:
			filename=filename+suffix
		try:
			response = urllib2.urlopen(url)
			data=response.read()
			fname=os.path.join(path,filename)
			f=open(fname,"w")
			f.write(data)
			f.close()
			
			return fname
		except:
			return None
	
	def save_json(self,jsonobj,path=None,filename=None):
		print "Trying to save json"
		if path==None:
			path=self.sessionjsonpath
		if filename==None:
			filename=str(uuid4())+".json"
		try:
			fname=os.path.join(path,filename)
			f=open(fname,"w")
			f.write(json.dumps(jsonobj,indent=4,sort_keys=True))
			f.close()
			return fname
		except:
			return None

	def scroll_page(self):
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	
	def scroll_up(self):
		self.driver.execute_script("window.scrollTo(0,window.scrollY-450);")
	
	def scroll_to_bottom(self):
		ticks_at_bottom = 0
		while True:
			js_scroll_code = "if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {return true;} else {return false;}"
			if self.driver.execute_script(js_scroll_code):
				if ticks_at_bottom > 1000:
					break
				else:
					ticks_at_bottom += 1
			else:
				self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				ticks_at_bottom = 0
		print("At bottom of page.")
		
	def close_modal(self):
		self.driver.find_element_by_link_text("Close").click()

	def google_login(self):
		self.goto_url("https://accounts.google.com")
		self.driver.find_element_by_id("identifierId")
		user=self.driver.find_element_by_id("identifierId")
		user.send_keys(self.googleusr)
		user.send_keys(Keys.RETURN)
		time.sleep(10)
		self.driver.find_element_by_name("password")
		passw=self.driver.find_element_by_name("password")
		passw.send_keys(self.googlepwd)
		passw.send_keys(Keys.RETURN)

		
	def fb_login(self):
		# or you can use Chrome(executable_path="/usr/bin/chromedriver")
		self.goto_url("http://www.facebook.com")
		assert "Facebook" in self.driver.title
		elem = self.driver.find_element_by_id("email")
		elem.send_keys(self.fbusr)
		elem = self.driver.find_element_by_id("pass")
		elem.send_keys(self.fbpwd)
		elem.send_keys(Keys.RETURN)
		time.sleep(10)
	
	def fb_get_album_from_profile(self,profileurl,count=5):
		self.goto_url(profileurl+"/photos_albums")
		
		
	
	def fb_load_profile_from_json(self,jsonpath):
		profiledata={}
		if os.path.exists(jsonpath):
			with open(jsonpath) as f:
				profiledata=json.load(f)
		return profiledata
	
	def fb_get_profile_data(self,url):
		profiledata={}
		profilepic={}
		self.goto_url(url)
		time.sleep(5)
		
		profile=self.driver.current_url
		if profile=="http://www.facebook.com/profile.php":
			plink=self.driver.find_element_by_xpath("//a[@title='Profile']")
			profile=plink.get_attribute("href")
			
		
		profiledata['url']=profile
		#plink=self.driver.find_element_by_xpath("//a[@title='Profile']")
	
		profiledata['fbdisplayname']=self.fb_get_cur_page_displayname()
		
		self.driver.find_element_by_class_name("profilePic").click()
		time.sleep(10)
		try:
			profilepic['alttext']=self.driver.find_element_by_class_name("spotlight").get_property("alt")
			profilepic['src']=self.driver.find_element_by_class_name("spotlight").get_property("src")
			profilepic['profileguard']=False
		except:
			profilepic['alttext']=self.driver.find_element_by_class_name("profilePic").get_property("alt")
			profilepic['src']=self.driver.find_element_by_class_name("profilePic").get_property("src")
			profilepic['profileguard']=True
		try:
			localfile=self.download_file(profilepic['src'],prefix=profiledata['fbdisplayname'].replace(" ",""),suffix=".jpg")
			profilepic['localfile']=localfile
		
		except:
			print "Failed to download"
		
		
		
		profiledata['tabdata'] = self.fb_get_profile_tab_data(url)
		profiledata['friendcount']=profiledata['tabdata']['friends']['count']
		profiledata['profilepic']=profilepic
		return profiledata
		
	def fb_get_profile_tab_data(self,profileurl):
		tabdata={"friends":{},"photos":{},"about":{}}
		self.goto_url(profileurl)
		time.sleep(5)
		phototab=self.driver.find_element_by_xpath("//a[@data-tab-key='photos']").get_property("href")
		friendtab=self.driver.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("href")
		abouttab=self.driver.find_element_by_xpath("//a[@data-tab-key='about']").get_property("href")
		tabdata['friends']['url']=friendtab
		if self.driver.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("text").replace("Friends","") != "" and "Mutual" not in self.driver.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("text"):
			tabdata['friends']['count']=int(self.driver.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("text").replace("Friends",""))
		else:
			tabdata['friends']['count']=-1
		tabdata['photos']['url']=phototab
		tabdata['about']['url']=abouttab
		return tabdata
	
	def fb_update_self_profile(self):
		self.fbprofiledata=self.fb_get_profile_data("http://facebook.com/profile.php")
		
	def fb_get_cur_page_displayname(self):
		displayname=self.driver.find_element_by_id("fb-timeline-cover-name").find_element_by_tag_name("a").text
		return displayname
	
	def fb_like_page_toggle(self,pageurl):
		self.driver.get(pageurl)
		likebutton=self.driver.find_element_by_xpath("//button[@data-testid='page_profile_like_button_test_id']")
		likebutton.click()
	
	def fb_like_all_posts(self,pageurl,count=10):
		self.driver.get(pageurl)
		time.sleep(10)
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 		
		time.sleep(10)	
		for i in range (0,count):
			time.sleep(5)
			postlikebuttons=self.driver.find_elements_by_xpath("//a[@data-testid='fb-ufi-likelink']")
			for button in postlikebuttons:
				try:
					button.click()
					time.sleep(2)
				except:
					print "Ouch!"
				time.sleep(5)
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 		
		
			i+=1	

	def fb_post_to_wall(self,msg,wallurl="https://facebook.com"):
		self.driver.get(wallurl)
		time.sleep(7)
		#driver.find_element_by_xpath("//textarea[@name='xhpc_message']")
		#element.click()
		#time.sleep(7)
		element=self.driver.find_element_by_xpath("//div[@data-testid='status-attachment-mentions-input']")
		element.click()
		time.sleep(7)
		element.send_keys(unicode(msg.decode('utf-8')))
		time.sleep(10)
		button=self.driver.find_element_by_xpath("//button[@data-testid='react-composer-post-button']")
		button.click()

	def fb_get_notifications(self,count=10):
		self.driver.get("https://facebook.com/notifications")
		last_height = self.driver.execute_script("return document.body.scrollHeight")
		self.scroll_to_bottom()
		print last_height
		time.sleep(5)
		notifications=[]
		while len(notifications)<count:
			notificationslist=self.driver.find_element_by_xpath("//ul[@data-testid='see_all_list']")
			notifications=notificationslist.find_elements_by_xpath("//li")
			scroll_to_bottom(driver)
			time.sleep(5)
			new_height= self.driver.execute_script("return document.body.scrollHeight")
			print new_height
			
			if new_height==last_height:
				break
			last_height=new_height
		return notifications

	def fb_post_fortune_to_wall(self,wallurl,count=20,fortunefile='',hashtag=""):
		for i in range(0,count):
			sleeptime=73+2*i
			msg=os.popen("fortune %s" %fortunefile).read().strip()
			msg=msg+"\n"+hashtag
			print msg
			try:
				self.fb_post_to_wall(msg,wallurl)
			except:
				print "Post failed, trying again in %s seconds" %sleeptime 
			print "Sleeping for %s seconds" %sleeptime 
			time.sleep(sleeptime)

	def fb_get_friends(self,count=50,friendspage=None,download_images=False):
		if count>=self.fbfriendcount:
			print "Not enough friends, but getting whoever is there"
			count=self.fbfriendcount
		friends=[]
		if friendspage==None:
			friendspage=self.fbfriendsurl
		self.driver.get(friendspage)
		frienddivs=[]
		while len(frienddivs)<count:
			prevlen = len(frienddivs)
			newfrienddivs=self.driver.find_elements_by_xpath("//div[@data-testid='friend_list_item']")
			frienddivs+=newfrienddivs
			frienddivs=list(set(frienddivs))
			if len(frienddivs)==prevlen:
				print "Some of this persons friends have gone away"
				break
			self.scroll_to_bottom()
			time.sleep(10)
		frienddivs=frienddivs[:count]
		
		for frienddiv in frienddivs:
			friend={}
			soup=BeautifulSoup(frienddiv.get_property("innerHTML"))
			buttons=soup.findAll("button")
			links=soup.findAll("a")
			ismyfriend=False
			#print links
			for link in links:
				if link.text=="FriendFriends":
					ismyfriend=True
			friend['ismyfriend']=ismyfriend
			imagetag=links[0].find("img")
			friend['imagelink']=imagetag.get("src")
			friend['profileurl']=links[0].get("href").split("&")[0]
			if "?fref=pb" in friend['profileurl']:
				friend['profileurl']=friend['profileurl'].replace("?fref=pb","")
			friend['name']=imagetag.get("aria-label")
			friends.append(friend)
			for link in links:
				if " friends" in link.text:
					#print "It looks like we have mutual friends"
					if " mutual" in link.text:
						friend['mutualfriendcount']=int(link.text.replace(" mutual friends","").replace(",",""))
					else:
						friend['friendcount']=int(link.text.replace(" friends","").replace(",",""))
				
					

		return friends
		
	def fb_get_pic_reacters(self,url,count=10,tries=10):
		fblikers=[]
		self.goto_url(url)
		time.sleep(10)
		profpic=self.driver.find_element_by_class_name("profilePic")
		profpic.click()
		while len(fblikers)<count:
			tries-=1
			print tries
			if tries==0:
				break
		
			time.sleep(10)
			try:
				reacts=self.driver.find_elements_by_class_name("_4arz")
				print reacts
				reacts[len(reacts)-1].click()
				time.sleep(5)
				profiles=self.driver.find_elements_by_class_name("_5i_q")
				for profile in profiles:                               
					psoup=BeautifulSoup(profile.get_property("innerHTML"))
					a=psoup.find("a").get("href")
					fblikers.append(a)
					fblikers=list(set(fblikers))
				self.close_modal()
				time.sleep(5)
				
			except:
				print "No reactions"
			try:
				self.driver.find_element_by_class_name("next").click()
			except:
				print "Looks like a guarded profile"
			
		return fblikers[:count]
	
	def fb_update_friends_json(self,frjson):
		for friend in frjson:
			profileurl=friend['profileurl']
			friend['tabs']=self.fb_get_friend_tabs(profileurl)
		return frjson
	
	def fb_get_image_set_manifest(self,imageset):
		self.goto_url(imageset['url'])
		time.sleep(5)
		imageicons=self.driver.find_elements_by_class_name("uiMediaThumbImg")
		if len(imageicons)==0:
			imageicons=self.driver.find_elements_by_class_name("_2eea")
		images=[]
		counter=0
		imageicons[0].click()
		skip=imageset['skip']
		while counter<imageset['count']:
			
			image={}
			time.sleep(15)
			imageelement=self.driver.find_element_by_class_name("spotlight")
			alttext=imageelement.get_property("alt")
			imagesrc=imageelement.get_property("src")
			image['alttext']=alttext
			image['src']=imagesrc
			if skip>0:
				print "Skipping this image"
				skip=skip-1
				self.driver.find_element_by_class_name("next").click()
				continue
			else:
				images.append(image)
				counter+=1
			self.driver.find_element_by_class_name("next").click()
		self.driver.find_element_by_link_text("Close").click()
		
		imageset['images']=images
		
		return imageset
	
	def fb_download_image_set(self,imageset):
		imagesjson=imageset['images']
		for image in imagesjson:
			imagefile=self.download_file(image['src'],prefix=imageset['prefix'],suffix=".jpg")
			image['localfile']=imagefile
		return imageset
	def fb_get_image_set(self,url,count=50,skip=0,setname=None):
		imageset={}
		if setname==None:
			setname=str(uuid4())
		imageset['url']=url
		imageset['count']=count
		imageset['name']=setname
		imageset['prefix']=setname+"-"
		imageset['skip']=skip
		imageset=self.fb_get_image_set_manifest(imageset)
		imageset=self.fb_download_image_set(imageset)
		jsonname=self.save_json(imageset,filename=imageset['name']+".json")
		return jsonname

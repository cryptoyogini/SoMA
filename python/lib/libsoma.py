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

DEBUG=False



'''
SoMA Post objects store a JSON object as a named tuple as well as a dictionary, so that attributes can be referenced both in the dot notation as well as by key/value lookups. 
'''

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
	def __init__(self,configfile):
		config=ConfigParser.ConfigParser()
		config.read(configfile)
		self.config=config
		self.fbusr = config.get("User","fbusername")
		self.fbpwd = config.get("User","fbpassword")
		self.datapath=config.get("System","datapath")
		sessionpathprefix=config.get("System","sessionpathprefix")
		ts=datetime.now()
		sessiondir=sessionpathprefix+"-"+ts.strftime("%Y%b%d-%H%M%S")
		self.sessionpath=os.path.join(self.datapath,sessiondir)
		self.sessiondownloaddir=os.path.join(self.sessionpath,"downloads")
		
		if not os.path.exists(self.sessionpath):
			os.mkdir(self.sessionpath)
		if not os.path.exists(self.sessiondownloaddir):
			os.mkdir(self.sessiondownloaddir)
			
			
	def download_file(self,url,path=None,filename=None):
		print "Trying to download "+ url
		if path==None:
			path=self.sessiondownloaddir
		if filename==None:
			filename=str(uuid4())
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
	
	def fb_login(self):
		firefox_profile = webdriver.FirefoxProfile()
		firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
		driver = webdriver.Firefox(firefox_profile=firefox_profile)
		# or you can use Chrome(executable_path="/usr/bin/chromedriver")
		driver.get("http://www.facebook.com")
		assert "Facebook" in driver.title
		elem = driver.find_element_by_id("email")
		elem.send_keys(self.fbusr)
		elem = driver.find_element_by_id("pass")
		elem.send_keys(self.fbpwd)
		elem.send_keys(Keys.RETURN)
		self.fbdriver=driver
	
	def fb_scroll_to_bottom(self):
		self.fbdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	
	def fb_set_self_profile(self):
		plink=self.fbdriver.find_element_by_xpath("//a[@title='Profile']")
		profile=plink.get_attribute("href")
		self.fbprofileurl=profile
		self.fbdriver.get(self.fbprofileurl)	
		self.fbdisplayname=self.fb_get_cur_page_displayname()
		friendstab=self.fbdriver.find_elements_by_xpath("//a[@data-tab-key='friends']")[0]
		self.fbfriendcount=int(friendstab.get_property("text").replace("Friends",""))
		self.fbfriendsurl=friendstab.get_property("href")
	
	def fb_get_cur_page_displayname(self):
		displayname=self.fbdriver.find_element_by_id("fb-timeline-cover-name").find_element_by_tag_name("a").text
		return displayname
	
	def fb_like_page_toggle(self,pageurl):
		self.fbdriver.get(pageurl)
		likebutton=self.fbdriver.find_element_by_xpath("//button[@data-testid='page_profile_like_button_test_id']")
		likebutton.click()
	
	def fb_goto_url(self,url):
 		self.fbdriver.get(url)
	
	def fb_like_all_posts(self,pageurl,count=10):
		self.fbdriver.get(pageurl)
		time.sleep(10)
		self.fbdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 		
		time.sleep(10)	
		for i in range (0,count):
			time.sleep(5)
			postlikebuttons=self.fbdriver.find_elements_by_xpath("//a[@data-testid='fb-ufi-likelink']")
			for button in postlikebuttons:
				try:
					button.click()
					time.sleep(2)
				except:
					print "Ouch!"
				time.sleep(5)
			self.fbdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 		
		
			i+=1	

	def fb_post_to_wall(self,msg,wallurl="https://facebook.com"):
		self.fbdriver.get(wallurl)
		time.sleep(7)
		#driver.find_element_by_xpath("//textarea[@name='xhpc_message']")
		#element.click()
		#time.sleep(7)
		element=self.fbdriver.find_element_by_xpath("//div[@data-testid='status-attachment-mentions-input']")
		element.click()
		time.sleep(7)
		element.send_keys(unicode(msg.decode('utf-8')))
		time.sleep(10)
		button=self.fbdriver.find_element_by_xpath("//button[@data-testid='react-composer-post-button']")
		button.click()

	def fb_get_notifications(self,count=10):
		self.fbdriver.get("https://facebook.com/notifications")
		last_height = self.fbdriver.execute_script("return document.body.scrollHeight")
		self.fb_scroll_to_bottom()
		print last_height
		time.sleep(5)
		notifications=[]
		while len(notifications)<count:
			notificationslist=self.fbdriver.find_element_by_xpath("//ul[@data-testid='see_all_list']")
			notifications=notificationslist.find_elements_by_xpath("//li")
			scroll_to_bottom(driver)
			time.sleep(5)
			new_height= self.fbdriver.execute_script("return document.body.scrollHeight")
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

	def fb_update_friend_count(self):
		self.fbdriver.get(self.fbprofileurl)
		friendstab=self.fbdriver.find_elements_by_xpath("//a[@data-tab-key='friends']")[0]
		self.fbfriendcount=int(friendstab.get_property("text").replace("Friends",""))
		self.fbfriendsurl=friendstab.get_property("href")
	
	def fb_attributes(self):
		fb_attributes={}
		fb_attributes['username']=self.fbusr
		fb_attributes['profileurl']=self.fbprofileurl
		fb_attributes['friendcount']=self.fbfriendcount
		fb_attributes['displayname']=self.fbdisplayname
		return fb_attributes
	
	def fb_get_friends(self,count=50,friendspage=None,download_images=False):
		if count>=self.fbfriendcount:
			print "Not enough friends, but getting whoever is there"
			count=self.fbfriendcount
		friends=[]
		if friendspage==None:
			friendspage=self.fbfriendsurl
		self.fbdriver.get(friendspage)
		frienddivs=[]
		while len(frienddivs)<count:
			prevlen = len(frienddivs)
			newfrienddivs=self.fbdriver.find_elements_by_xpath("//div[@data-testid='friend_list_item']")
			frienddivs+=newfrienddivs
			frienddivs=list(set(frienddivs))
			if len(frienddivs)==prevlen:
				print "Some of this persons friends have gone away"
				break
			self.fb_scroll_to_bottom()
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
		

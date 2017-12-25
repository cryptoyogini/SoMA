from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import ConfigParser
import time,os


def setup(configfile):
	config=ConfigParser.ConfigParser()
	config.read(configfile)
	return config

def scroll_to_bottom(driver):
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	
def login_to_fb(configfile):
	config=setup(configfile)
	usr = config.get("User","fbusername")
	pwd = config.get("User","fbpassword")
	firefox_profile = webdriver.FirefoxProfile()
	firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
	driver = webdriver.Firefox(firefox_profile=firefox_profile)
	# or you can use Chrome(executable_path="/usr/bin/chromedriver")
	driver.get("http://www.facebook.com")
	assert "Facebook" in driver.title
	elem = driver.find_element_by_id("email")
	elem.send_keys(usr)
	elem = driver.find_element_by_id("pass")
	elem.send_keys(pwd)
	elem.send_keys(Keys.RETURN)
	return driver

def get_self_profile(driver):
	plink=driver.find_element_by_xpath("//a[@title='Profile']")
	profile=plink.get_attribute("href")
	return profile
#elem = driver.find_element_by_css_selector(".input.textInput")
#elem.send_keys("Posted using Python's Selenium WebDriver bindings!")
#elem = driver.find_element_by_css_selector("input[value=\"Publicar\"]")
#elem.click()

def like_page_toggle(driver,pageurl):
	driver.get(pageurl)
	likebutton=driver.find_element_by_xpath("//button[@data-testid='page_profile_like_button_test_id']")
	likebutton.click()
#driver.close()
#DONE
def like_all_posts(driver,pageurl,count=10):
	driver.get(pageurl)
	time.sleep(10)
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 		
	time.sleep(10)	
	for i in range (0,count):
		time.sleep(5)
		postlikebuttons=driver.find_elements_by_xpath("//a[@data-testid='fb-ufi-likelink']")
		for button in postlikebuttons:
			try:
				button.click()
				time.sleep(2)
			except:
				print "Ouch!"
			time.sleep(5)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 		
	
		i+=1	

def post_to_wall(driver,msg,wallurl="https://facebook.com"):
	driver.get(wallurl)
	time.sleep(7)
	#driver.find_element_by_xpath("//textarea[@name='xhpc_message']")
	#element.click()
	#time.sleep(7)
	element=driver.find_element_by_xpath("//div[@data-testid='status-attachment-mentions-input']")
	element.click()
	time.sleep(7)
	element.send_keys(unicode(msg.decode('utf-8')))
	time.sleep(10)
	button=driver.find_element_by_xpath("//button[@data-testid='react-composer-post-button']")
	button.click()

def get_notifications(driver,count=10):
	driver.get("https://facebook.com/notifications")
	last_height = driver.execute_script("return document.body.scrollHeight")
	scroll_to_bottom(driver)
	print last_height
	time.sleep(5)
	notifications=[]
	while len(notifications)<count:
		notificationslist=driver.find_element_by_xpath("//ul[@data-testid='see_all_list']")
		notifications=notificationslist.find_elements_by_xpath("//li")
		scroll_to_bottom(driver)
		time.sleep(5)
		new_height= driver.execute_script("return document.body.scrollHeight")
		print new_height
		
		if new_height==last_height:
			break
		last_height=new_height
	return notifications
def post_fortune_to_wall(driver,wallurl,count=20,fortunefile='',hashtag=""):
	for i in range(0,count):
		sleeptime=73+2*i
		msg=os.popen("fortune %s" %fortunefile).read().strip()
		msg=msg+"\n"+hashtag
		print msg
		try:
			post_to_wall(driver,msg,wallurl)
		except:
			print "Post failed, trying again in %s seconds" %sleeptime 
		print "Sleeping for %s seconds" %sleeptime 
		time.sleep(sleeptime)

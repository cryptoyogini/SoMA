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
from shutil import copyfile
from copy import deepcopy
import coloredlogs, logging
from libsomautils import *
from libsomacyborg import *


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
		try:
			self.name=self.get_property("name")			
		except:
			self.name=self.get_property("uuid")
		
	def update_name(self):
		try:
			self.name=self.get_property("name")			
		except:
			self.name=self.get_property("uuid")
		logFormatter=logging.Formatter(SOMA_LOG_FORMAT)
		fileHandler = logging.FileHandler("{0}/{1}.log".format(os.path.split(self.jsonfile)[0], "somasession"))
		fileHandler.setFormatter(logFormatter)
		fileHandler.addFilter(coloredlogs.HostNameFilter())
		self.logger.addHandler(fileHandler)
	
		self.logger.info("Saving messages to log at " + os.path.join(os.path.split(self.jsonfile)[0],"somasession.log"))
		
	def show_profile(self):
		self.logger.info("Showing self profile")
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
	
	def export(self,exportpath):
		self.show_profile()
		newjson=deepcopy(self.jsonprofile)
		self.logger.info("Copyting fbprofiles...")
		i=0
		for fbprofile in self.jsonprofile['fbprofiles']:
			self.logger.info("Original path " + fbprofile)
			self.logger.info("New path "+os.path.join(exportpath,os.path.split(fbprofile)[1]))
			copyfile(fbprofile, os.path.join(exportpath,os.path.split(fbprofile)[1]))
			
			newjson['fbprofiles'][i]= os.path.join("./",os.path.split(fbprofile)[1])
			i+=1
		i=0
		self.logger.info("Copyting imagesets...")
		for imageset in self.jsonprofile['imagesets']:
			self.logger.info("Original path " + imageset)
			self.logger.info("New path " + os.path.join(exportpath,os.path.split(imageset)[1]))
			copyfile(imageset, os.path.join(exportpath,os.path.split(imageset)[1]))
			newjson['imagesets'][i]= os.path.join("./",os.path.split(imageset)[1])
			i+=1
		self.logger.info("Copying profilepic...")
		self.logger.info("Original path " + self.jsonprofile['profilepic']['localfile'])
		print "Original path ", os.path.join(exportpath,os.path.split(self.jsonprofile['profilepic']['localfile'])[1])
		copyfile(self.jsonprofile['profilepic']['localfile'], os.path.join(exportpath,os.path.split(self.jsonprofile['profilepic']['localfile'])[1]))
			
		newjson['profilepic']['localfile']=os.path.join("./",os.path.split(self.jsonprofile['profilepic']['localfile'])[1])
		
		#print get_color_json(newjson)
		newfile=os.path.join(exportpath,os.path.split(self.jsonfile)[1])
		with open(newfile,"w") as f:
			f.write(json.dumps(newjson,indent=4,sort_keys=True))
		for imageset in newjson['imagesets']:
			imagesetpath = os.path.join(exportpath,os.path.split(imageset)[1])
			with open(imagesetpath,"r") as f:
				imagesetjson=json.loads(f.read())
			for image in imagesetjson['images']:
				print image['localfile']
		for fbprofile in newjson['fbprofiles']:
			print fbprofile

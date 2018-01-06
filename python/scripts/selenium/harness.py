import sys
sys.path.append("/opt/SoMA/python/lib")
from libsoma import *

if __name__=="__main__":
		
		'''
		ab=SoMACyborg("/home/cryptoyogini/ids/ab.conf")
		ab.fb_login()
		ab.fb_update_self_profile()
		print ab.fbprofiledata
		
		'''
		mn=SoMACyborg("/home/cryptoyogini/ids/mn.conf")
		mn.fb_login()
		mn.fb_update_self_profile()
		print get_color_json(mn.fbprofiledata)
		
	
		'''
	
		pa=SoMACyborg("/home/cryptoyogini/ids/pa.conf")
		pa.fb_login()
		pa.fb_update_self_profile()
		print pa.fbprofiledata
		'''

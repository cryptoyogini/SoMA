import sys
sys.path.append("/opt/SoMA/python/lib")
from libsoma import *

def get_cyborg(configfile):
	cyborg=SoMACyborg(configfile)
	cyborg.fb_login()
	cyborg.fb_update_self_profile()
	print get_color_json(cyborg.fbprofiledata)
	return cyborg


if __name__=="__main__":
		print "Welcome to SoMA"
		

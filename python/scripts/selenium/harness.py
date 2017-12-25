import sys
sys.path.append("/opt/SoMA/python/lib")
from libsoma import *

if __name__=="__main__":
		mn=SoMAPerson("/home/arjun/ids/mn.conf")
		pa=SoMAPerson("/home/arjun/ids/pa.conf")
		mn.fb_login()
		pa.fb_login()
		mn.fb_set_self_profile()
		pa.fb_set_self_profile()
		mn.fb_update_friend_count()
		pa.fb_update_friend_count()

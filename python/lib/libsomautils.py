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



SOMA_FIELD_STYLES={'hostname': {'color': 'magenta'}, 'programname': {'color': 'cyan'}, 'name': {'color': 'cyan', 'bold': True}, 'levelname': {'color': 'green', 'bold': True}, 'asctime': {'color': 'green'}}

SOMA_LEVEL_STYLES={'info': {'color': 'blue'}, 'notice': {'color': 'magenta'}, 'verbose': {}, 'success': {'color': 'green', 'bold': True}, 'spam': {'color': 'green', 'faint': True}, 'critical': {'color': 'red', 'bold': True}, 'error': {'color': 'red'}, 'debug': {'color': 'green'}, 'warning': {'color': 'yellow'}}

SOMA_CONSOLE_FORMAT="%(asctime)s %(name)s-[%(funcName)s] %(levelname)s : %(message)s"

SOMA_LOG_FORMAT="%(asctime)s %(hostname)s %(name)s[%(funcName)s] %(levelname)s : %(message)s"


def get_color_json(dictionary):
	formatted_json=get_formatted_json(dictionary)
	colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
	return colorful_json

def get_formatted_json(dictionary):
	formatted_json=json.dumps(dictionary,sort_keys=True, indent=4)
	return formatted_json


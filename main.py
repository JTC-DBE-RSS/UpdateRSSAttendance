import logging
import logging.handlers
import os

import requests

import json
import pandas as pd
import numpy
from datetime import date

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    SOME_SECRET = os.environ["SOME_SECRET"]
except KeyError:
    SOME_SECRET = "Token not available!"
    #logger.info("Token not available!")
    #raise

#Wrapper

class GenericWrapper:
	def __init__(self, wrapped):
		self.wrapped = wrapped

	# Fallback lookup for undefined methods
	def __getattr__(self, name):
		return getattr(self.wrapped, name)
    
    
#Comments 

#!/bin/python
# coding: utf-8

##########################################################################################################################################

# For templating
import re

# The parser
try:
	import ujson as json
except ImportError:
	import json

# For templating
#from jsonspec.pointer import extract, ExtractError


##########################################################################################################################################

# Comments
COMMENT_PREFIX = ("#",";","//")
MULTILINE_START = "/*"
MULTILINE_END = "*/"

# Data strings
LONG_STRING = '"""'

# JSON Pointer template
TEMPLATE_RE = re.compile(r"\{\{(.*?)\}\}")

##########################################################################################################################################

class JsonComment(GenericWrapper):
	def __init__(self, wrapped=json):
		super().__init__(wrapped)

	# Loads a JSON string with comments
	# Allows to expand the JSON Pointer templates
	def loads(self, jsonsc, *args, template=True, **kwargs):
		# Splits the string in lines
		lines = jsonsc.splitlines()
		# Process the lines to remove commented ones
		jsons = self._preprocess(lines)
		# Calls the wrapped to parse JSON
		self.obj = self.wrapped.loads(jsons, *args, **kwargs)
		# If there are templates, subs them
		if template:
			self._templatesub(self.obj)
		return self.obj

	# Loads a JSON opened file with comments
	def load(self, jsonf, *args, **kwargs):
		# Reads a text file as a string
		# Process the readed JSON string
		return self.loads(jsonf.read(), *args, **kwargs)

	# Opens a JSON file with comments
	# Allows a default value if loading or parsing fails
	def loadf(self, path, *args, default = None, **kwargs):
		# Preparing the default
		json_obj = default

		# Opening file in append+read mode
		# Allows creation of empty file if non-existent
		with open( path, mode="a+", encoding="UTF-8" ) as jsonf:
			try:
				# Back to file start
				jsonf.seek(0)
				# Parse and load the JSON
				json_obj = self.load(jsonf, *args, **kwargs)
			# If fails, default value is kept
			except ValueError:
				pass

		return json_obj

	# Saves a JSON file with indentation
	def dumpf(self, json_obj, path, *args, indent=4, escape_forward_slashes=False, **kwargs):
		# Opening file in write mode
		with open( path, mode="w", encoding="UTF-8" ) as jsonf:
			# Dumping the object
			# Keyword escape_forward_slashes is only for ujson, standard json raises an exception for unknown keyword
			# In that case, the method is called again without it
			try:
				json.dump(json_obj, jsonf, *args, indent=indent, escape_forward_slashes=escape_forward_slashes, **kwargs)
			except TypeError:
				json.dump(json_obj, jsonf, *args, indent=indent, **kwargs)

	# Reads lines and skips comments
	def _preprocess(self, lines):
		standard_json = ""
		is_multiline = False
		keep_trail_space = 0

		for line in lines:
			# 0 if there is no trailing space
			# 1 otherwise
			keep_trail_space = int(line.endswith(" "))

			# Remove all whitespace on both sides
			line = line.strip()

			# Skip blank lines
			if len(line) == 0:
				continue

			# Skip single line comments
			if line.startswith(COMMENT_PREFIX):
				continue

			# Mark the start of a multiline comment
			# Not skipping, to identify single line comments using multiline comment tokens, like
			# /***** Comment *****/
			if line.startswith(MULTILINE_START):
				is_multiline = True

			# Skip a line of multiline comments
			if is_multiline:
				# Mark the end of a multiline comment
				if line.endswith(MULTILINE_END):
					is_multiline = False
				continue

			# Replace the multi line data token to the JSON valid one
			if LONG_STRING in line:
				line = line.replace(LONG_STRING, '"')

			standard_json += line + " " * keep_trail_space

		# Removing non-standard trailing commas
		standard_json = standard_json.replace(",]", "]")
		standard_json = standard_json.replace(",}", "}")

		return standard_json

	# Walks the json object and subs template strings with pointed value
	def _templatesub(self, obj):
		# Gets items for iterables
		if isinstance(obj, dict):
			items = obj.items()
		elif isinstance(obj, list):
			items = enumerate(obj)
		else:
			items = None

		# Walks the iterable
		for key, subobj in items:
			# If subobj is another iterable, call this method again
			if isinstance(subobj, (dict, list)):
				self._templatesub(subobj)
			# If is a string:
			# - Find all matches to the template
			# - For each match, get through JSON Pointer the value, which must be a string
			# - Substitute each match to the pointed value, or ""
			# - The string with all templates substitued is written back to the parent obj
			elif isinstance(subobj, str):
				obj[key] = TEMPLATE_RE.sub(self._repl_getvalue, subobj)

	# Replacement function
	# The match has the JSON Pointer
	def _repl_getvalue(self, match):
		try:
			# Extracts the pointed value from the root object
			value = extract(self.obj, match[1])
			# If it's not a string, it's not valid
			if not isinstance(value, str):
				raise ValueError("Not a string: {}".format(value))
		except (ExtractError, ValueError) as e:
			# Sets value to empty string
			value = ""
			print(e)
		return value

##########################################################################################################################################

import json
#from jsoncomment import JsonComment
from collections import defaultdict

def jsonParser(text):
    '''
    Get parse string to json.
    return: converted_Jsontext
    '''
    parser = JsonComment(json)
    converted_Jsontext = parser.loads(text)
    return converted_Jsontext


def groupFormDataDetails(list_formDataInstances):
    groupLists_formDataInstances = defaultdict(list)

    for formDataInstance in list_formDataInstances:
        # print(formDataInstance)
        # break
        groupLists_formDataInstances[formDataInstance['formData']['type']].append(
            formDataInstance['formData'])

    return groupLists_formDataInstances


def groupIssueDataDetails(list_issueDataInstances):
    groupLists_issueDataInstances = defaultdict(list)

    for issues in list_issueDataInstances:
        # print(formDataInstance)
        # break
        groupLists_issueDataInstances[issues['issue']['type']].append(
            issues['issue'])

    return groupLists_issueDataInstances

def errorhandler(function, errorMessage):
    print(function, errorMessage)
    exit()


### Auth

class Auth:
    def __init__(self, client_id, client_secret, scope):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.url = "https://ims.bentley.com/connect/token"

    def getToken(self):
        '''
        Get access token.
        return: (str)bearer_token
        '''
        try:
            # Data required grant_type, client_id, client_secret and scope
            data = {'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'scope': self.scope
                    }

            response = requests.post(self.url, data=data)
            #print(self.client_id)
            #print(self.client_secret)
            if(response.status_code == 200):
                content = json.loads(response.content)
                token_type = content['token_type']
                access_token = content['access_token']
                bearer_token = f"{token_type} {access_token}"
                return bearer_token

            else:
                errorhandler('getToken', f'failed, {response.status_code}')           

        except Exception as e:
            errorhandler('getToken', f'exception trigged, {e}')
            
class ProjectsAPI:
    def __init__(self, key):
        self.authorization_key = key

    def getAllProjects(self):
        '''
        Get all projects.
        return: list_projects
        '''
        url = 'https://api.bentley.com/projects'

        try:
            headers = {'Accept': "application/vnd.bentley.itwin-platform.v1+json",
                       'Authorization': self.authorization_key}
            response = requests.get(url, headers=headers)

            if(response.status_code == 200):
                content = jsonParser(response.text)
                list_projects = (content['projects'])
                return list_projects

            else:
                errorhandler('getAllProjects', 'failed'+ response.status_code )

        except Exception as e:
            errorhandler('getAllProjects', 'exception trigged'+ e )

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

from datetime import datetime
###Testing Account
##Name:Testing API
# client_id = "service-TWoDsHSXkpUxst90rlqNu0rqP"
# client_secret = "rwmPcsphk5AgkLeUh0u0kRac5NqF88IL7AFxnFQnKSKJybxXwn3dBuEEjN6jYiXpln8+LneyR+HbBcJCvMZqcA=="

##Implementation Account
## Name:JTC_DBE_API
client_id = "service-ic9GskfCxPWYu4NeVGxAVGZ75"
client_secret = "Ci8/yLvhfUqF1fLb8AlRmhJT8bRjn7S952Yyy1OZyQhdMnI8vX6o5lsP/HyzIRdDBV8BmcMl4qpTjYKnZyf1nw=="
scope = ["projects:read"]

print(datetime.now())
# Create auth object, and get access token.
auth = Auth(client_id, client_secret, scope)
authorization_key = auth.getToken()
print(authorization_key)

print(datetime.now())

# Create projects_API object, and get all projects.
projects_API = ProjectsAPI(authorization_key)
list_projects = projects_API.getAllProjects()

if(list_projects == None):
    print('No projects.')
    exit()


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info('Admin logged in')

#print(list_projects)
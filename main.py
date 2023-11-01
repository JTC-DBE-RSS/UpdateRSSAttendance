import json
import logging
import logging.handlers
import os
from datetime import date, datetime

import pandas as pd
import requests

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
    # logger.info("Token not available!")
    # raise

# Wrapper


class GenericWrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    # Fallback lookup for undefined methods
    def __getattr__(self, name):
        return getattr(self.wrapped, name)


# Comments

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
# from jsonspec.pointer import extract, ExtractError


##########################################################################################################################################

# Comments
COMMENT_PREFIX = ("#", ";", "//")
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
    def loadf(self, path, *args, default=None, **kwargs):
        # Preparing the default
        json_obj = default

        # Opening file in append+read mode
        # Allows creation of empty file if non-existent
        with open(path, mode="a+", encoding="UTF-8") as jsonf:
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
    def dumpf(
        self, json_obj, path, *args, indent=4, escape_forward_slashes=False, **kwargs
    ):
        # Opening file in write mode
        with open(path, mode="w", encoding="UTF-8") as jsonf:
            # Dumping the object
            # Keyword escape_forward_slashes is only for ujson, standard json raises an exception for unknown keyword
            # In that case, the method is called again without it
            try:
                json.dump(
                    json_obj,
                    jsonf,
                    *args,
                    indent=indent,
                    escape_forward_slashes=escape_forward_slashes,
                    **kwargs,
                )
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

# from jsoncomment import JsonComment
from collections import defaultdict


def jsonParser(text):
    """
    Get parse string to json.
    return: converted_Jsontext
    """
    parser = JsonComment(json)
    converted_Jsontext = parser.loads(text)
    return converted_Jsontext


def groupFormDataDetails(list_formDataInstances):
    groupLists_formDataInstances = defaultdict(list)

    for formDataInstance in list_formDataInstances:
        # print(formDataInstance)
        # break
        groupLists_formDataInstances[formDataInstance["formData"]["type"]].append(
            formDataInstance["formData"]
        )

    return groupLists_formDataInstances


def groupIssueDataDetails(list_issueDataInstances):
    groupLists_issueDataInstances = defaultdict(list)

    for issues in list_issueDataInstances:
        # print(formDataInstance)
        # break
        groupLists_issueDataInstances[issues["issue"]["type"]].append(issues["issue"])

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
        """
        Get access token.
        return: (str)bearer_token
        """
        try:
            # Data required grant_type, client_id, client_secret and scope
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope,
            }

            response = requests.post(self.url, data=data)
            # print(self.client_id)
            # print(self.client_secret)
            if response.status_code == 200:
                content = json.loads(response.content)
                token_type = content["token_type"]
                access_token = content["access_token"]
                bearer_token = f"{token_type} {access_token}"
                return bearer_token

            else:
                errorhandler("getToken", f"failed, {response.status_code}")

        except Exception as e:
            errorhandler("getToken", f"exception trigged, {e}")


class ProjectsAPI:
    def __init__(self, key):
        self.authorization_key = key

    def getAllProjects(self):
        """
        Get all projects.
        return: list_projects
        """
        url = "https://api.bentley.com/projects"

        try:
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                content = jsonParser(response.text)
                list_projects = content["projects"]
                return list_projects

            else:
                errorhandler("getAllProjects", "failed" + response.status_code)

        except Exception as e:
            errorhandler("getAllProjects", "exception trigged" + e)

    def getProjectTeamMembers(self, projectId):
        """
        Get all projects team member.
        return: list_projects_team
        """
        url = f"https://api.bentley.com/projects/{projectId}/members"
        # print(url)
        try:
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }
            response = requests.get(url, headers=headers)

            list_projectTeamMember = []

            while True:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    content = jsonParser(response.text)
                    list_projectTeamMember.extend(content["members"])

                    if "next" in content["_links"]:
                        url = content["_links"]["next"]["href"]

                    else:
                        return list_projectTeamMember

                else:
                    print("getFormDataDetails failed", response.status_code)
                    return None

        #             if(response.status_code == 200):
        #                 content = jsonParser(response.text)
        #                 list_projects_team = (content['members'])
        #                 return list_projects_team

        #             else:
        #                 errorhandler('getProjectTeamMembers', 'failed'+ response.status_code )

        except Exception as e:
            errorhandler("getProjectTeamMembers", "exception trigged" + e)


###### iTwinsAPI
class iTwinsAPI:
    def __init__(self, key):
        self.authorization_key = key

    def getAllProjectsviaiTwins(self):
        """
        Get all projects via iTwinsAPI.
        return: list_projects
        """
        url = "https://api.bentley.com/itwins/?subClass=Project"

        """
        Returns in the format:
        [{'id': '8e6d360a-eb84-4e87-8a31-e99229d9128f', 'class': 'Endeavor', 'subClass': 'Project', 'type': None, 'number': 'JTC Semiconspace (Synchro)', 'displayName': 'JTC D&B Semiconspace @ Tampines WFP', 'status': 'Active'}]
        """

        try:
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                content = jsonParser(response.text)
                list_projects = content["iTwins"]
                return list_projects

            else:
                errorhandler(
                    "getAllProjectsviaiTwins", f"failed {response.status_code}"
                )

        except Exception as e:
            errorhandler("getAllProjectsviaiTwins", "exception trigged" + e)


###### Forms


class FormsAPI:
    def __init__(self, key):
        self.authorization_key = key

    def getProjectFormData(self, projectId, formtype):
        """
        Get form data instances.
        input: (str)projectId, The GUID of the project to get forms for.
        return: (list)list_formDataInstances, The list of form data instances under the project.
                [object1, object2 ...], object1->{id:'', displayname:'', type:'', state:''}
        """
        try:
            url = "https://api.bentley.com/forms/"
            # url = f'https://api.bentley.com/forms/?projectId={projectId}'
            params = {"type": formtype, "projectId": projectId}
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }
            list_formDataInstances = []

            while True:
                response = requests.get(url, headers=headers, params=params)
                # print(response)
                if response.status_code == 200:
                    content = jsonParser(response.text)
                    list_formDataInstances.extend(content["formDataInstances"])

                    if "next" in content["_links"]:
                        url = content["_links"]["next"]["href"]

                    else:
                        return list_formDataInstances

                else:
                    print("getFormDataDetails failed", response.status_code)
                    return None

        except Exception as e:
            print("getFormDataDetails except trigged", e)
            return None

    def getFormDataDetails(self, formId):
        """
        Get form data details.
        input: (str)formId, The ID of the form data instance to retrieve.
        return: (dict)content, The dict of form data details.
                {
                    'formData':{
                        id:'',
                        subject:'',
                        description:'',
                        dueDate:'',
                        type:'',
                        ...}
                }
        """
        try:
            url = f"https://api.bentley.com/forms/{formId}"
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                content = jsonParser(response.text)

                return content

            else:
                errorhandler("getFormDataDetails", "failed" + response.status_code)

        except Exception as e:
            errorhandler("getFormDataDetails", "exception trigged" + e)

    def getFormDataAttachments(self, formId):
        """
        Get form data attachments ID.
        input: (str)formId, The ID of the form data instance to retrieve.
        return: (dict)content, The dict of form data attachments details.
                {
                    "attachments": [{
                             "id": "XZzxOCC8sVvUcgeXz1Ih_exlLgPfRTpAuShXz1cTpAu",
                             "fileName": "CrackedConcrete.png",
                             "createdDateTime": "2020-10-20T16:16:30.6704320Z",
                             "size": 34770,
                             "caption": "Picture of the cracked concrete",
                             "binding": null,
                             "type": "png"
                        },
                        {
                             "id": "XZzxOCC8sVvUcgeXz1Ih_exlLgPfRTpAuShXz1cTpAu",
                             "fileName": "StreetView.png",
                             "createdDateTime": "2020-10-20T16:08:30.2804722Z",
                             "size": 56893,
                             "caption": "Picture showing the bridge from the perspective of an approaching car",
                             "binding": "Location",
                             "type": "png"
                        }
                    ]
                }
        Dict{Attachments: List[Dict{"id": },{"id"}]}
        """
        try:
            url = f"https://api.bentley.com/forms/{formId}/attachments"
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                content = jsonParser(response.text)

                return content

            else:
                errorhandler("getFormDataAttachments", "failed" + response.status_code)

        except Exception as e:
            errorhandler("getFormDataAttachments", "exception trigged" + e)

    def getFormAttachments(self, formId, attachmentId):
        """
        Get form data attachments based on form Id and attachment ID.
        input: (str)formId, The ID of the form data instance to retrieve.
        (str)attachmentId, The ID of the form attachment to retrieve.
        return: The attachment's file contents

        """
        try:
            url = f"https://api.bentley.com/forms/{formId}/attachments/{attachmentId}"

            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # content = response.read()
                # content = jsonParser(response)

                return response

            else:
                errorhandler("getFormAttachments", "failed" + response.status_code)

        except Exception as e:
            errorhandler("getFormAttachments", "exception trigged" + e)

    def exportFormPdfs(self, formId, folderId):
        """
        Get form data attachments based on form Id and folder ID.
        input: (str)formId, The ID of the form data instance to retrieve.
        (str)folderId, The ID of the folder to retrieve.
        return: The export's file contents
        fb8p_AI-gEmA8dDxsQ-yiJ2t0gYGwz1PoazaH1hSMOM
        """
        try:
            # https://api.bentley.com/forms/storageExport?ids[&includeHeader][&fileType][&folderId]
            url = f"https://api.bentley.com/forms/storageExport?ids={formId}&folderId={folderId}"

            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            #             params = {"folderId": folderId,
            #                     }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # content = jsonParser(response)

                return response

            else:
                errorhandler("exportFormPdfs", "failed" + str(response.status_code))

        except Exception as e:
            print(e)
            # errorhandler('exportFormPdfs', 'exception trigged'+ str(e) )

    def updateFormData(self, formId, updateformjsonload):
        """
        Create issue data form
        input: (str)issueId, The ID of the issue data instance to retrieve.
        return: (dict)content, The dict of issue data details.
                {
                    'issueData':{
                        id:'',
                        subject:'',
                        description:'',
                        dueDate:'',
                        type:'',
                        ...}
                }
        """
        try:
            url = f"https://api.bentley.com/forms/{formId}"
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            # convert string or dictionary into json format
            # json_data = payload
            # print (json_data)
            response = requests.patch(url, data=updateformjsonload, headers=headers)

            if response.status_code == 200:
                content = jsonParser(response.text)

                return content

            else:
                errorhandler("updateFormData", " failed " + str(response.status_code))

        except Exception as e:
            errorhandler("updateFormData", " exception trigged " + str(e))


##### Issues


class IssuesAPI:
    def __init__(self, key):
        self.authorization_key = key

    def getProjectIssueDefinitions(self, projectId, formtype):
        """
        Get issue data definition.
        input: (str)projectId, The GUID of the project to get issue.
        return: (list)list_IssueDataInstances, The list of issue data instances under the project.
                [object1, object2 ...], object1->{id:'', displayname:'', type:'', state:''}
        """
        try:
            url = "https://api.bentley.com/issues/formDefinitions?"

            params = {"type": formtype, "projectId": projectId}
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            # list_issueDataDefinition = []

            while True:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    content = jsonParser(response.text)
                    return content

                else:
                    print("getIssueDataDefinitions failed", response.status_code)
                    return None

        except Exception as e:
            print("getIssueDataDefinition except trigged", e)
            return None

    def getProjectIssueData(self, projectId, issuetype):
        """
        Get issue data instances.
        input: (str)projectId, The GUID of the project to get issue.
        return: (list)list_IssueDataInstances, The list of issue data instances under the project.
                [object1, object2 ...], object1->{id:'', displayname:'', type:'', state:''}
        """
        try:
            # url = f'https://api.bentley.com/issues/'
            url = f"https://api.bentley.com/issues/?projectId={projectId}&type={issuetype}"
            #             params = {'type': issuetype,
            #                       '?projectId': projectId
            #                    }
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }
            list_issueDataInstances = []

            while True:
                response = requests.get(url, headers=headers)
                # response = requests.get(url, headers=headers, params = params)
                if response.status_code == 200:
                    content = jsonParser(response.text)
                    list_issueDataInstances.extend(content["issues"])

                    if "next" in content["_links"]:
                        url = content["_links"]["next"]["href"]

                    else:
                        return list_issueDataInstances

                else:
                    print("getProjectIssueData failed", response.status_code)
                    return None

        except Exception as e:
            print("getProjectIssueData except trigged", e)
            return None

    def getIssueDataDetails(self, issueId):
        """
        Get issue data details.
        input: (str)issueId, The ID of the issue data instance to retrieve.
        return: (dict)content, The dict of issue data details.
                {
                    'issueData':{
                        id:'',
                        subject:'',
                        description:'',
                        dueDate:'',
                        type:'',
                        ...}
                }
        """
        try:
            url = f"https://api.bentley.com/issues/{issueId}"
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                content = jsonParser(response.text)

                return content

            else:
                errorhandler("getIssueDataDetails", "failed" + response.status_code)

        except Exception as e:
            errorhandler("getIssueDataDetails", "exception trigged" + e)

    def postIssueData(self, jsonload):
        """
        Create issue data form
        input: (str)issueId, The ID of the issue data instance to retrieve.
        return: (dict)content, The dict of issue data details.
                {
                    'issueData':{
                        id:'',
                        subject:'',
                        description:'',
                        dueDate:'',
                        type:'',
                        ...}
                }
        """
        try:
            url = "https://api.bentley.com/issues/"
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            # convert string or dictionary into json format
            # json_data = payload
            # print (json_data)
            response = requests.post(url, data=jsonload, headers=headers)

            if response.status_code == 201:
                content = jsonParser(response.text)

                return content

            else:
                errorhandler("postIssueData", "failed" + str(response.status_code))

        except Exception as e:
            errorhandler("postIssueData", "exception trigged" + str(e))

    def updateIssueData(self, issueId, updatejsonload):
        """
        update issue data form
        input: (str)issueId, The ID of the issue data instance to retrieve.
        return: (dict)content, The dict of issue data details.
                {
                    'issueData':{
                        id:'',
                        subject:'',
                        description:'',
                        dueDate:'',
                        type:'',
                        ...}
                }
        """
        try:
            url = f"https://api.bentley.com/issues/{issueId}"
            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            # convert string or dictionary into json format
            # json_data = payload
            # print (json_data)
            response = requests.patch(url, data=updatejsonload, headers=headers)

            if response.status_code == 200:
                content = jsonParser(response.text)

                return content

            else:
                errorhandler("updateIssueData", " failed " + str(response.status_code))

        except Exception as e:
            errorhandler("updateIssueData", " exception trigged " + str(e))

    def exportIssuePdfs(self, IssueId, folderId):
        """
        Get issue data attachments based on issue Id and issue ID.
        input: (str)issueId, The ID of the issue data instance to retrieve.
        (str)folderId, The ID of the folder to retrieve.
        return: The export's file contents
        fb8p_AI-gEmA8dDxsQ-yiJ2t0gYGwz1PoazaH1hSMOM
        """
        try:
            # https://api.bentley.com/issues/storageExport?ids[&includeHeader][&fileType][&folderId]
            # https://api.bentley.com/issues/storageExport?ids[&includeHeader][&fileType][&folderId]
            url = f"https://api.bentley.com/issues/storageExport?ids={IssueId}&folderId={folderId}"

            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            #             params = {"folderId": folderId,
            #                       "fileType": "pdf",
            #                       "includeHeader": "true"
            #                     }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # content = jsonParser(response)

                return response

            else:
                errorhandler("exportIssuePdfs", "failed" + str(response.status_code))

        except Exception as e:
            errorhandler("exportIssuePdfs", "exception trigged" + str(e))


##Export


class StorageAPI:
    def __init__(self, key):
        self.authorization_key = key

    def getTopLevelFolder(self, projectId):
        try:
            url = f"https://api.bentley.com/storage/?projectId={projectId}"

            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            list_folderInstances = []

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                content = jsonParser(response.text)
                list_folderInstances.extend(content["items"])

                return list_folderInstances
                # return content

            else:
                print("getTopLevelFolder failed", response.status_code)
                return None

        #             while(True):
        #                 response = requests.get(url, headers=headers)
        #                 #response = requests.get(url, headers=headers, params = params)
        #                 if(response.status_code == 200):
        #                     content = jsonParser(response.text)
        #                     list_folderInstances.extend(content['items'])

        #                     if('next' in content['_links']):
        #                         url = content['_links']['next']['href']
        #                         print("next")

        #                     else:
        #                         return list_folderInstances

        #                 else:
        #                     print('getTopLevelFolder failed', response.status_code)
        #                     return None

        except Exception as e:
            print("getTopLevelFolder except trigged", e)
            return None

    def createFolder(self, folderId, jsonload):
        """
        create a new folder
        "displayName": "test",
        "description": "test folder"
        """

        try:
            url = f"https://api.bentley.com/storage/folders/{folderId}/folders"

            headers = {
                "Accept": "application/vnd.bentley.itwin-platform.v1+json",
                "Authorization": self.authorization_key,
            }

            response = requests.post(url, data=jsonload, headers=headers)

            if response.status_code == 201:
                content = jsonParser(response.text)

                return content

            else:
                errorhandler("createFolder", "failed" + str(response.status_code))

        except Exception as e:
            errorhandler("createFolder", "exception trigged" + str(e))


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

##Implementation Account
## Name:JTC_DBE_API
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
scope = ["itwins:read"]

print(datetime.now())
# Create auth object, and get access token.
auth = Auth(client_id, client_secret, scope)
authorization_key = auth.getToken()
print(authorization_key)

print(datetime.now())

# Create projects_API object, and get all projects.
# projects_API = ProjectsAPI(authorization_key)
# list_projects = projects_API.getAllProjects()

# Create iTwins_API object, and get all projects.
itwins_API = iTwinsAPI(authorization_key)
list_projects = itwins_API.getAllProjectsviaiTwins()

if list_projects is None:
    print("No projects.")
    exit()

##Read the forms

# list_projects = [{'id': '69c70697-3747-4120-b185-dbd7d54388a0', 'displayName': 'JTC R&R to Biopolis Phase 1 (Synchro)', 'projectNumber': 'JTC BIOR (Synchro)'}]

today = date.today()

for project in list_projects:
    if project["id"] == "69c70697-3747-4120-b185-dbd7d54388a0":
        # print(project['id'])

        # Get Post OT Form
        # Request token for with scope forms:read.
        auth.scope = ["issues:read"]
        authorization_key = auth.getToken()
        issues_API = IssuesAPI(authorization_key)
        # Get all OT Request form
        list_issueDataInstances = issues_API.getProjectIssueData(
            project["id"], "Post OT Form"
        )

        list_issueDetails = []
        # Iterate every form ID to get form data details
        for issues in list_issueDataInstances:
            # print(issues)
            # for every issue ID, get the Issue data details
            issueDetail = issues_API.getIssueDataDetails(issues["id"])

            if issueDetail is not None:
                # add to a list
                list_issueDetails.append(issueDetail)
                # print(list_issueDetails)

        # Group if there is more than one RSS attendance form type
        dictLists_IssueDataDetails = groupIssueDataDetails(list_issueDetails)
        # print(dictLists_IssueDataDetails)
        # print("Extracted Post OT Forms")
        # iterate for every Post OT issue
        for key in dictLists_IssueDataDetails.keys():
            # convert into dataframe
            dfPostOT = pd.json_normalize(dictLists_IssueDataDetails[key])
            # Convert the datetime into just day, month and year
            dfPostOT["createdDateTime"] = dfPostOT["createdDateTime"].apply(
                lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")
            )
            # To filter month and year
            dfPostOT["yearmonth"] = dfPostOT["createdDateTime"].apply(
                lambda x: pd.to_datetime(x).strftime("%Y-%m")
            )

            ##Update OT hours
        ##Only update days that there are values
        OTHourlist = []

        dfPostOT["PostOTTimeIn"] = pd.to_datetime(
            dfPostOT["properties.ActualOTStart"], format="%H:%M", errors="coerce"
        )
        dfPostOT["PostOTTimeOut"] = pd.to_datetime(
            dfPostOT["properties.ActualOTEnd"], format="%H:%M", errors="coerce"
        )
        dfPostOT["PostOTHour"] = (
            (
                dfPostOT["PostOTTimeOut"].apply(lambda x: x.hour)
                - dfPostOT["PostOTTimeIn"].apply(lambda x: x.hour)
            )
            + (
                dfPostOT["PostOTTimeOut"].apply(lambda x: x.minute)
                - dfPostOT["PostOTTimeIn"].apply(lambda x: x.minute)
            )
            / 60
            - dfPostOT["properties.RSSMeal1"]
        )

        ## if OT hours = -ve, need to add 24 hours
        dfPostOT["PostOTHour"] = dfPostOT["PostOTHour"].apply(
            lambda x: x + 24 if x < 0 else x
        )

        # Update Attendance Form
        auth.scope = ["issues:modify"]
        authorization_key = auth.getToken()
        issues_API = IssuesAPI(authorization_key)

        for id in dfPostOT["id"]:
            if dfPostOT["state"].loc[dfPostOT["id"] == id].values[0] == "Open":
                # print(dfPostOT["PostOTHour"].loc[dfPostOT["id"] == id].values[0])
                updatejsonload = {
                    "assignee": {
                        "displayName": str(
                            dfPostOT[dfPostOT["id"] == id][
                                "assignee.displayName"
                            ].values[0]
                        ),
                        "id": str(
                            dfPostOT[dfPostOT["id"] == id]["assignee.id"].values[0]
                        ),
                    },
                    "properties": {
                        "Updated__x0020__Date": str(today),
                        "RSS__x0020__OT__x0020__1": dfPostOT[dfPostOT["id"] == id][
                            "PostOTHour"
                        ].values[0],
                    },
                    # "formId": formId
                }
                updatejson_data = json.dumps(updatejsonload)

                # print(updatejson_data)
                updateissue = issues_API.updateIssueData(id, updatejson_data)
                print(
                    str(
                        dfPostOT[dfPostOT["id"] == id]["assignee.displayName"].values[0]
                    )
                    + "'s Post OT Form updated"
                )

            else:
                continue

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logging.info("Admin logged in")

##Read the forms

# list_projects = [{'id': '69c70697-3747-4120-b185-dbd7d54388a0', 'displayName': 'JTC R&R to Biopolis Phase 1 (Synchro)', 'projectNumber': 'JTC BIOR (Synchro)'}]

# Form Type for OT Request Form
OTReq = "Overtime Request Form"

# Issue Type for RSS Attendance Form
RSS = "RSS Attendance V1"

today = date.today()

for project in list_projects:
    # Update RSS Attendance Form
    auth.scope = ["issues:read"]
    authorization_key = auth.getToken()
    issues_API = IssuesAPI(authorization_key)

    # print(authorization_key)
    ##Get Attendance Form

    ##Get all the issue data ID related to RSS Attendance V1
    # print(project['id'])
    list_issueDataInstances = issues_API.getProjectIssueData(
        project["id"], "RSS Attendance V1"
    )
    # print(list_issueDataInstances)
    list_issueDetails = []
    # print(list_issueDataInstances)
    for issues in list_issueDataInstances:
        # for every issue ID, get the Issue data details
        issueDetail = issues_API.getIssueDataDetails(issues["id"])

        if issueDetail is not None:
            # add to a list
            list_issueDetails.append(issueDetail)
            # print(list_issueDetails)

    # Group if there is more than one RSS attendance form type
    dictLists_IssueDataDetails = groupIssueDataDetails(list_issueDetails)

    print("Extracted RSS Attendance Form")
    # iterate for every RSS attendance issue
    for key in dictLists_IssueDataDetails.keys():
        # convert into dataframe
        dfRSS = pd.json_normalize(dictLists_IssueDataDetails[key])
        # Convert the datetime into just day, month and year
        dfRSS["createdDateTime"] = dfRSS["createdDateTime"].apply(
            lambda x: pd.to_datetime(x).strftime("%Y-%m-%d")
        )
        # To filter month and year
        dfRSS["yearmonth"] = dfRSS["createdDateTime"].apply(
            lambda x: pd.to_datetime(x).strftime("%Y-%m")
        )

        # To create a dataframe for all RSS form within the month
        # dfRSS2 = dfRSS.loc[(dfRSS["yearmonth"] == str(today)[:-3])]

        ## Testing for within a month and after
        dfRSS2 = dfRSS

    ## Update RSS Form Data

    # TotalOff
    # TotalLeaves
    # TotalOtherRemarks
    # TotalCovered
    # TotalNonCovered
    # Total_x200_Working_Days
    # TotalWorkingHours
    # Total_x200_Overtime_Hours

    ##Calculate the total leave, off, mc, hospitalisation

    dfRSS2["Sum_FullLeave"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Full Day Leave"), axis=1
    )

    dfRSS2["Sum_HalfLeave"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Half Day Leave"), axis=1
    )

    dfRSS2["Sum_FullOff"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Full Day Off"), axis=1
    )

    dfRSS2["Sum_HalfOff"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Half Day Off"), axis=1
    )

    dfRSS2["Sum_Leave"] = dfRSS2["Sum_FullLeave"] + dfRSS2["Sum_HalfLeave"] * 0.5

    dfRSS2["TotalOff"] = dfRSS2["Sum_FullOff"] + dfRSS2["Sum_HalfOff"] * 0.5

    dfRSS2["Sum_HalfMC"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Half Day MC"), axis=1
    )

    dfRSS2["Sum_FullMC"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Full Day MC"), axis=1
    )

    dfRSS2["Sum_Hospitalisation"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Hospitalisation Leave"), axis=1
    )

    dfRSS2["Sum_SickLeave"] = (
        dfRSS2["Sum_FullMC"]
        + dfRSS2["Sum_HalfMC"] * 0.5
        + dfRSS2["Sum_Hospitalisation"]
    )

    dfRSS2["TotalLeaves"] = dfRSS2["Sum_SickLeave"] + dfRSS2["Sum_Leave"]

    dfRSS2["Sum_FullOthers"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Full Day Others"), axis=1
    )

    dfRSS2["Sum_HalfOthers"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Half Day Others"), axis=1
    )

    dfRSS2["Sum_Others"] = dfRSS2["Sum_FullOthers"] + dfRSS2["Sum_HalfOthers"] * 0.5

    # Calculate absent day with covering officer
    dfRSS2["TotalFullCovered"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Full Day Cover"), axis=1
    )
    dfRSS2["TotalHalfCovered"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Half Day Cover"), axis=1
    )
    dfRSS2["TotalCovered"] = (
        dfRSS2["TotalFullCovered"] + dfRSS2["TotalHalfCovered"] * 0.5
    )

    dfRSS2["TotalNonCovered"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "No Cover"), axis=1
    )

    dfRSS2["TotalAbsentDays"] = (
        dfRSS2["TotalOff"] + dfRSS2["Sum_Others"] + dfRSS2["TotalLeaves"]
    )

    dfRSS2["TotalHalfCovered"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Half Day Cover"), axis=1
    )
    dfRSS2["TotalCovered"] = (
        dfRSS2["TotalFullCovered"] + dfRSS2["TotalHalfCovered"] * 0.5
    )

    dfRSS2["TotalNonCovered"] = dfRSS2["TotalAbsentDays"] - dfRSS2["TotalCovered"]

    dfRSS2["Sum_NotAvailable"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Not Available"), axis=1
    )
    dfRSS2["Sum_NA"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "NA"), axis=1
    )

    dfRSS2["Sum_Weekend"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Weekend (Sunday)"), axis=1
    )

    dfRSS2["Sum_Public Holiday"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Public Holiday"), axis=1
    )

    dfRSS2["Sum_Saturday"] = dfRSS2.apply(
        lambda row: sum(row[0 : len(dfRSS2.columns)] == "Sat"), axis=1
    )

    dfRSS2["Sum_Day"] = 31

    dfRSS2["Sum_WorkingDays"] = (
        dfRSS2["Sum_Day"]
        - dfRSS2["Sum_NotAvailable"]
        - dfRSS2["Sum_SickLeave"]
        - dfRSS2["Sum_Others"]
        - dfRSS2["Sum_Leave"]
        - dfRSS2["Sum_Public Holiday"]
        - dfRSS2["Sum_Weekend"]
        - dfRSS2["Sum_NA"]
    )

    dfRSS2["Sum_Day_Month"] = 26

    dfRSS2["Total__x0020__Working__x0020__Days"] = (
        dfRSS2["Sum_Day_Month"] - dfRSS2["TotalNonCovered"] - dfRSS2["Sum_NotAvailable"]
    )

    # Total__x0020__Working__x0020__Days
    # dfRSS2["Sum_WorkingHours"] = dfRSS2["Sum_WorkingDays"] * 8

    ##Update OT hours
    ##Only update days that there are values
    OTHourlist = []
    for d in range(1, 32):
        if "properties.D" + str(d) + "OTTimein" in dfRSS2.columns:
            dfRSS2["D" + str(d) + "OTTimein"] = pd.to_datetime(
                dfRSS2["properties.D" + str(d) + "OTTimein"],
                format="%H:%M",
                errors="coerce",
            )
        else:
            continue
        if "properties.D" + str(d) + "OTTimeOut" in dfRSS2.columns:
            dfRSS2["D" + str(d) + "OTTimeOut"] = pd.to_datetime(
                dfRSS2["properties.D" + str(d) + "OTTimeOut"],
                format="%H:%M",
                errors="coerce",
            )
        else:
            continue
        if "properties.D" + str(d) + "__x0020__OT__x0020__Meal" in dfRSS2.columns:
            dfRSS2["D" + str(d) + "__x0020__OT__x0020__Meal"] = dfRSS2[
                "properties.D" + str(d) + "__x0020__OT__x0020__Meal"
            ]
        else:
            continue

        dfRSS2["D" + str(d) + "OT"] = (
            (
                dfRSS2["D" + str(d) + "OTTimeOut"].apply(lambda x: x.hour)
                - dfRSS2["D" + str(d) + "OTTimein"].apply(lambda x: x.hour)
            )
            + (
                dfRSS2["D" + str(d) + "OTTimeOut"].apply(lambda x: x.minute)
                - dfRSS2["D" + str(d) + "OTTimein"].apply(lambda x: x.minute)
            )
            / 60
            - dfRSS2["properties.D" + str(d) + "__x0020__OT__x0020__Meal"]
        )

        ## if OT hours = -ve, need to add 24 hours
        dfRSS2["D" + str(d) + "OT"] = dfRSS2["D" + str(d) + "OT"].apply(
            lambda x: x + 24 if x < 0 else x
        )

        # print(dfRSS2["D" + str(d) + "_Work_Hour"])
        OTHourlist.append("D" + str(d) + "OT")

    # WorkHourlist
    dfRSS2["Total_x200_Overtime_Hours"] = dfRSS2[OTHourlist].sum(axis=1)

    ##Update Working Hours

    WorkHourlist = []
    for d in range(1, 32):
        if "properties.D" + str(d) + "__x0020__Time__x0020__In" in dfRSS2.columns:
            dfRSS2["D" + str(d) + "__x0020__Time__x0020__In"] = pd.to_datetime(
                dfRSS2["properties.D" + str(d) + "__x0020__Time__x0020__In"],
                format="%H:%M",
                errors="coerce",
            )
        else:
            continue
        if "properties.D" + str(d) + "__x0020__Time__x0020__Out" in dfRSS2.columns:
            dfRSS2["D" + str(d) + "__x0020__Time__x0020__Out"] = pd.to_datetime(
                dfRSS2["properties.D" + str(d) + "__x0020__Time__x0020__Out"],
                format="%H:%M",
                errors="coerce",
            )
        else:
            continue
        dfRSS2["D" + str(d) + "_Work_Hour"] = (
            dfRSS2["D" + str(d) + "__x0020__Time__x0020__Out"].apply(lambda x: x.hour)
            - dfRSS2["D" + str(d) + "__x0020__Time__x0020__In"].apply(lambda x: x.hour)
        ) + (
            dfRSS2["D" + str(d) + "__x0020__Time__x0020__Out"].apply(lambda x: x.minute)
            - dfRSS2["D" + str(d) + "__x0020__Time__x0020__In"].apply(
                lambda x: x.minute
            )
        ) / 60
        # print(dfRSS2["D" + str(d) + "_Work_Hour"])
        ## if OT hours = -ve, need to add 24 hours
        dfRSS2["D" + str(d) + "_Work_Hour"] = dfRSS2["D" + str(d) + "_Work_Hour"].apply(
            lambda x: x + 24 if x < 0 else x
        )

        ##If more than 8, put 8. Elif if between 4 to 8, minus 1 and less than 4, remain

        dfRSS2["D" + str(d) + "_Work_Hour"] = dfRSS2["D" + str(d) + "_Work_Hour"].apply(
            lambda x: 8 if x > 8 else ((x - 1) if x > 4 else x)
        )
        WorkHourlist.append("D" + str(d) + "_Work_Hour")

    # WorkHourlist

    dfRSS2["Sum_WorkingHours"] = dfRSS2[WorkHourlist].sum(axis=1)

    # Update Attendance Form
    auth.scope = ["issues:modify"]
    authorization_key = auth.getToken()
    issues_API = IssuesAPI(authorization_key)

    for id in dfRSS2["id"]:
        # print(dfRSS2["status"].loc[dfRSS2["id"] == id].values[0])
        if (
            dfRSS2["status"].loc[dfRSS2["id"] == id].values[0] == "Assigned to RSS"
            or dfRSS2["status"].loc[dfRSS2["id"] == id].values[0]
            == "Send to Main Contractor For Verification"
            or dfRSS2["status"].loc[dfRSS2["id"] == id].values[0]
            == "Send to Consultant For Verification"
            or dfRSS2["status"].loc[dfRSS2["id"] == id].values[0]
            == "Send to JTC For Verification"
            or dfRSS2["status"].loc[dfRSS2["id"] == id].values[0]
            == "Send to Lead RSS For Verification"
        ):
            ##Collate all the work hour needs to be updated
            AddRemarks = {}
            for Day in range(1, 32):
                DDay = "D" + str(Day) + "_Work_Hour"
                if DDay in dfRSS2.columns:
                    # if it is not a null value
                    if not (
                        pd.isnull(
                            dfRSS2[dfRSS2["id"] == id][
                                "D" + str(Day) + "_Work_Hour"
                            ].values[0]
                        )
                    ):
                        # Append the work hour into the remarks to be updated
                        AddRemarks["D" + str(Day) + "__x0020__Work__x0020__Hour"] = int(
                            dfRSS2[dfRSS2["id"] == id][
                                "D" + str(Day) + "_Work_Hour"
                            ].values[0]
                        )
                        test = "D" + str(Day) + "OT"
                        if test in dfRSS2.columns:
                            if not (
                                pd.isnull(
                                    dfRSS2[dfRSS2["id"] == id][
                                        "D" + str(Day) + "OT"
                                    ].values[0]
                                )
                            ):
                                AddRemarks["D" + str(Day) + "__x0020__OT"] = dfRSS2[
                                    dfRSS2["id"] == id
                                ]["D" + str(Day) + "OT"].values[0]
                                # print("ok")
                            else:
                                continue
                        else:
                            continue
                    else:
                        test = "D" + str(Day) + "OT"
                        if test in dfRSS2.columns:
                            if not (
                                pd.isnull(
                                    dfRSS2[dfRSS2["id"] == id][
                                        "D" + str(Day) + "OT"
                                    ].values[0]
                                )
                            ):
                                AddRemarks["D" + str(Day) + "__x0020__OT"] = dfRSS2[
                                    dfRSS2["id"] == id
                                ]["D" + str(Day) + "OT"].values[0]
                            else:
                                continue
                            # print("ok")
                        else:
                            continue
                else:
                    continue
            # print(id)
            updatejsonload = {
                "assignee": {
                    "displayName": str(
                        dfRSS2[dfRSS2["id"] == id]["assignee.displayName"].values[0]
                    ),
                    "id": str(dfRSS2[dfRSS2["id"] == id]["assignee.id"].values[0]),
                },
                "properties": {
                    "Updated__x0020__Date__x0020__By": str(today),
                    "TotalOff": dfRSS2[dfRSS2["id"] == id]["TotalOff"].values[0],
                    "TotalLeaves": dfRSS2[dfRSS2["id"] == id]["TotalLeaves"].values[0],
                    # "TotalMCs": dfRSS2[dfRSS2['id'] == id]["Sum_SickLeave"].values[0],
                    "TotalOtherRemarks": dfRSS2[dfRSS2["id"] == id][
                        "Sum_Others"
                    ].values[0],
                    "TotalCovered": dfRSS2[dfRSS2["id"] == id]["TotalCovered"].values[
                        0
                    ],
                    "TotalNonCovered": dfRSS2[dfRSS2["id"] == id][
                        "TotalNonCovered"
                    ].values[0],
                    "Total__x0020__Working__x0020__Days": str(
                        dfRSS2[dfRSS2["id"] == id][
                            "Total__x0020__Working__x0020__Days"
                        ].values[0]
                    ),
                    "TotalWorkingHours": dfRSS2[dfRSS2["id"] == id][
                        "Sum_WorkingHours"
                    ].values[0],
                    "Total__x0020__Overtime__x0020__Hours": dfRSS2[dfRSS2["id"] == id][
                        "Total_x200_Overtime_Hours"
                    ].values[0],
                },
                # "formId": formId
            }
            updatejsonload["properties"].update(AddRemarks)
            # print(updatejsonload)
            updatejson_data = json.dumps(updatejsonload)

            # print(updatejson_data)
            updateissue = issues_API.updateIssueData(id, updatejson_data)
            print(
                str(dfRSS2[dfRSS2["id"] == id]["assignee.displayName"].values[0])
                + "'s RSS Form updated"
            )
        else:
            continue

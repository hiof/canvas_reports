# -*- coding: cp1252 -*-
#!/usr/bin/env python
import requests
import time, json, os
import re, pprint

# Change this to match your access token
token="13~UXIoEduXhYRqtIuIAnulCrqflIvp0H18MF7XYZmCt8jzBew7YvdVI9Ee6p5THiOf"

# Change this to match the domain you use to access Canvas.
CANVAS_DOMAIN  = "domain.instructure.com"

# Change this to the full path of your desired output folder.  I've set it to the current
# directory for the sake of this script
OUTPUT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Change this to the term to pull for, otherwise this will pull for all terms.
ENROLLMENT_TERM = False

# Edit each of these to determine which to include in the report
deleted_items = False
accounts = True
courses = True
enrollments = True
sections = True
terms = True
users = True
xlist = True
group_membership = True
groups = True

###################################################################################
#### DON'T CHANGE anything after this unless you know what you are doing. #########
BASE_DOMAIN = "https://%s/api/v1/%%s/" %  CANVAS_DOMAIN
BASE_URI = BASE_DOMAIN % "accounts/self/reports" 
BASE_START_URI = BASE_DOMAIN % "accounts/self/reports/%s" 
BASE_FILE_URI =  BASE_DOMAIN % "files/%s"

# This headers dictionary is used for almost every request
headers = {"Authorization":"Bearer %s" % token}

# This is the list of parameters used for the sis_export_csv report, I think I'm actually
# missing one, parameters[enrollment_term], but I'm not sure
report_parameters = {
  "parameters[accounts]": accounts,
  "parameters[courses]": courses,
  "parameters[enrollments]": enrollments,
  "parameters[groups]": groups,
  "parameters[group_membership]": group_membership,
  "parameters[include_deleted]": deleted_items,
  "parameters[sections]": sections,
  "parameters[terms]": terms,
  "parameters[users]": users,
  "parameters[xlist]": xlist}

# If ENROLLMENT_TERM isn't False, add it to the parameters list
if ENROLLMENT_TERM != False:
  report_parameters["parameters[enrollment_term]"]=ENROLLMENT_TERM

# Step 1: Start the report
start_report_url = BASE_START_URI % "provisioning_csv"
start_report_response = requests.post(start_report_url,headers=headers,params=report_parameters)

# Use the id from that output to check the progress of the report. 
status_url = start_report_url + "%s" % start_report_response.json()['id']
status_response = requests.get(status_url,headers=headers)
status_response_json = status_response.json()

# Step 2: Wait for the report to be finished
while status_response_json['progress'] < 100:
  status_response = requests.get(status_url,headers=headers)
  status_response_json = status_response.json()
  time.sleep(4)

file_url = status_response_json['file_url']

file_id_pattern = re.compile('files\/(\d+)\/download')

# Once "progress" is 100 then parse out the number between "files" and "download",

# Step 3: Download the file

file_info_url = status_response_json['attachment']['url']
file_response = requests.get(file_info_url,headers=headers,stream=True)

# Step 4: Save the file
with open(status_response_json['attachment']['filename'],'w+b') as filename:
    filename.write(file_response.content)

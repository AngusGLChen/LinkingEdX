'''
Created on Nov 11, 2015

@author: Angus
'''

import os
import json

import csv

# import code for encoding urls and generating md5 hashes
import urllib, urllib2, hashlib

from lxml import html
import requests

import re


# Read large data file
#path = "/Volumes/NETAC/Linking/StackExchange/Dataset/test/Content/stackoverflow.com.7z/Posts.xml"

path = "/Users/Angus/Downloads/Users.xml"
#output_path = "/Users/Angus/Downloads/test"
'''
if os.path.isfile(output_path):
    os.remove(output_path)
output_file = open(output_path, "w")
'''
i = 0
input = open(path, "r")
lines = input.readlines()
for line in lines:
    #sub = line[0: 100]
    print line
    '''
    if "INSERT INTO `users` VALUES" in sub:
        if i < 2:
            #output_file.write(line + "\n")
            i += 1
    '''
    i += 1
print i

#output_file.close()


url = "github.com/ShinNoNoir"
#url = "stackoverflow.com/users/2310951/"
#url = "https://twitter.com/dtunkelang"

url = "http://stackoverflow.com/users/1798473"


'''
try:
    pic = urllib2.urlopen(url)
    #output = open("/Users/Angus/Downloads/kk.jpg", "wb")
    #output.write(pic.read())
    content = pic.read()
    
    parser = MyHTMLParser()
    parser.feed(content)
    
    
    
except Exception as e:
    print e
'''
'''
url = "http://github.com/k-yamame"
page = requests.get(url)
tree = html.fromstring(page.content)

print page
print
print tree
'''
#print page.content


####################
# For GitHub
'''
link = tree.xpath('//a[@class="url"]/text()')[0]
pic_link = tree.xpath('//a[@class="vcard-avatar"]/img[@class="avatar"]/@src')[0]


pic = urllib2.urlopen(pic_link)
output = open("/Users/Angus/Downloads/kk.jpg", "wb")
output.write(pic.read())

print link
print pic_link
###################3
'''
####################

'''
# url

url = "https://twitter.com/dtunkelang"
page = requests.get(url)
tree = html.fromstring(page.content)
link = tree.xpath('//a[@class="u-textUserColor"]/@title')[0]
# pic
pic_link = tree.xpath('//img[@class="ProfileAvatar-image "]/@src')[0]
# full_name
# link = tree.xpath('//h1[@class="ProfileHeaderCard-name"]/a/text()')[0]
# login
# link = tree.xpath('//h2[@class="ProfileHeaderCard-screenname u-inlineBlock u-dir"]/a/span/text()')[0]

pic = urllib2.urlopen(pic_link)
output = open("/Users/Angus/Downloads/kk.jpg", "wb")
output.write(pic.read())

print link
print pic_link
'''
'''
####### For StackExchange
link = tree.xpath('//a[@class="url"]/@href')[0]
pic_link = tree.xpath('//img[@class="avatar-user"]/@src')[0]
# platform/users/id

pic = urllib2.urlopen(pic_link)
output = open("/Users/Angus/Downloads/kk.jpg", "wb")
output.write(pic.read())


print link 
print pic_link
'''


'''
# Set your variables here
email = "eleni.skrekou@gmail.com"
size = 40
default = 404
 
# construct the url
gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
gravatar_url += urllib.urlencode({'d':str(default), 's':str(size)})

print gravatar_url

try:
    pic = urllib2.urlopen(gravatar_url)
    #print pic.read()
    output = open("/Users/Angus/Downloads/kk.jpg", "wb")
    output.write(pic.read())
except Exception as e:
    print e
'''

'''
# Set your variables here
size = 40
default = 404

total = 0
num = 0 

input_path = "/Users/Angus/Downloads/course_email_list"
input = open(input_path, "r")
lines = input.readlines()
for line in lines:
    
    total += 1
    
    array = line.replace("\n", "").split("\t")
    email = array[1]
    
    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d':str(default), 's':str(size)})

    try:
        pic = urllib2.urlopen(gravatar_url)
        output = open("/Users/Angus/Downloads/gravatar/" + str(email) + ".jpg", "wb")
        output.write(pic.read())
        num += 1
    except Exception as e:
        print str(num) + "\tout of\t" + str(total)
        
print "Downloading pics finished."
'''   
######################################
'''
input_path = "/Users/Angus/Downloads/gravatar_pic/"
files = os.listdir(input_path)
for file in files:
    email = file.replace(".jpg", "")
    gravatar_url = "https://www.gravatar.com/" + hashlib.md5(email.lower()).hexdigest() + ".json"
    try:
        result = urllib2.urlopen(gravatar_url)
        #output = open("/Users/Angus/Downloads/gravatar/" + str(email) + ".jpg", "wb")
        #output.write(pic.read())
        #num += 1
        #print gravatar_url
        line = result.read()
        #print line
        jsonObject = json.loads(line)
        for entry in jsonObject:
            for zero in jsonObject[entry]:
                for zero in jsonObject[entry]:
                    if "urls" in zero:
                        for url in zero["urls"]:
                            print url["value"]
        print 
        
        
        
    except Exception as e:
        #print str(num) + "\tout of\t" + str(total)
        #print error
        k= 1
'''
######################################
'''
input_path = "/Users/Angus/Downloads/test"
file = open(input_path, "r")
lines = file.readlines()
for line in lines:
    jsonObject = json.loads(line)
    for entry in jsonObject:
        for element in jsonObject[entry]:
            for account in element["accounts"]:
                if "stack" in account["domain"]:
                
            for url in element["urls"]:
                if "stack" in url["value"]:

'''
'''
def ReadEdX(path):
    
    edx_learners_map = {}
    edx_learners_set = set()
    
    input = open(path, "r")
    lines = input.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        course_id = array[0]
        email = array[1]
        username = array[2]
        name = array[3]
        
        if email in edx_learners_set:
            edx_learners_map[email]["courses"].append(course_id)
        else:
            edx_learners_set.add(email)
            edx_learners_map[email] = {"username":username, "name": name, "courses":[course_id]}
        
    input.close()
            
    return (edx_learners_set, edx_learners_map)


def ReadSocialWeb(path):
    
    web_learners_set = set()
    
    files = os.listdir(path)
    for file in files:
        file = file[0:len(file)-4]
        web_learners_set.add(file)
    
    return web_learners_set

def MatchLearnersExplicitly(edx_path, web_path):
    
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    web_learners_set = ReadSocialWeb(web_path)
    
    matched_learners = {}
    
    for email in edx_learners_set:        
        if email in web_learners_set:
            matched_learners[email] = {"courses":edx_learners_map[email]["courses"]}
    
    # Output matching results
    output_path = os.path.dirname(web_path) + "/explicit_matching"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    
    # Analyze
    print "The number of matched learners in total is: " + str(len(matched_learners)) + "\n"
    
    course_learner_map = {}
    
    for email in matched_learners.keys():
        for course in matched_learners[email]["courses"]:
            if course not in course_learner_map.keys():
                course_learner_map[course] = set()
            course_learner_map[course].add(email)
        output_file.write(email + "\t" + str(','.join(matched_learners[email]["courses"])) + "\n")
    
    output_file.close()
    
    count_course_learner_map = {}
    for course in course_learner_map.keys():
        count_course_learner_map[course] = len(course_learner_map[course])    
    sorted_count_course_learner_map = sorted(count_course_learner_map.items(), key=lambda d:d[1], reverse=True)
    for record in sorted_count_course_learner_map:
        #print "The number of matched learners from course\t" + str(record[0]) + "\tis:\t" + str(record[1])
        print str(record[0]) + "\t" + str(record[1])
    print
    


edx_path = "/Users/Angus/Downloads/course_email_list"
web_path = "/Users/Angus/Downloads/gravatar_pic/"
MatchLearnersExplicitly(edx_path, web_path)
'''

'''
total = 0
ill = 0
ill_email = 0
empty_email = 0


with open('/Users/Angus/Downloads/users.csv') as f:
    f_csv = csv.reader(f)
    headers = next(f_csv)
    for row in f_csv:
        
        total += 1
                
        if len(row) != 10:
            ill += 1
            continue
        
        login = row[1]
        if login == "\\N":
            print row
        
        email = row[5]
        if email != "\\N":
            
            email = email.lower()
            
            email = email.replace(" at ", "@")
            email = email.replace(" dot ", ".")
                       
            email = email.replace("(at)", "@")
            email = email.replace("(dot)", ".")
            
            email = email.replace("[at]", "@")
            email = email.replace("[dot]", ".")
            
            email = email.replace("{at}", "@")
            email = email.replace("{dot}", ".")
            
            email = email.replace("_at_", "@")
            email = email.replace("_dot_", ".")
            
            email = email.replace("-at-", "@")
            email = email.replace("-dot-", ".")
            
            email = email.replace("<at>", "@")
            email = email.replace("<dot>", ".")
            
            while "\t" in email:
                email = email.replace("\t", "")
            
            if "@" not in email or "." not in email:
                ill_email += 1
        else:
            empty_email += 1

print total
print ill
print ill_email
print empty_email
'''
'''
a = set()
a.add(1)
a.add(2)

print a.pop()
'''
'''
line = "[{'platform': 'stackoverflow.com', 'id': '1798473'}]"
line = line.replace("[", "").replace("]", "")
line = line.replace("\'", '"')
print line
jsonObject = json.loads(line)
print jsonObject


a = set()

test = {"platform": "github", "url": 1}
a.add(test)
print test
'''








 
    

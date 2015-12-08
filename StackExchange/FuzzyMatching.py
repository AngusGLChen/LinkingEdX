'''
Created on Nov 27, 2015

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import re
import time
import string

from lxml import etree
from happyfuntokenizing import *

import urllib, urllib2
import hashlib

import json
from PIL import Image

import requests
from lxml import html

import Levenshtein

happyemoticons = [":-)", ":)", ":o)", ":]", ":3", ":c)", ":>", "=]", "8)", "=)", ":}", ":^)", ":-D", ":D", "8-D", "8D", "x-D", "xD", "X-D", "XD", "=-D", "=D","=-3", "=3", "B^D", ":-)", ";-)", ";)", "*-)", "*)", ";-]", ";]", ";D", ";^)", ":-,"]
sademoticons = [">:[", ":-(", ":(", ":-c", ":c", ":-<", ":<", ":-[", ":[", ":{", ":-||", ":@", ">:(", "'-(", ":'(", ">:O", ":-O", ":O"]    
codetext = ["<code>"]

def fast_iterUser(context, output_file):
    
    numbatch = 0
    counter = 0
    MAXINQUERY = 10000
    
    start_time = time.time()
    print "... START TIME at:" + str(start_time)
    
    urlsreg = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    
    tok = Tokenizer(preserve_case=False)

    for event, elem in context:
        
        counter+=1

        stripped = None
        lenText = 0
        hemo = 0
        semo = 0
        upper = 0
        punctu = 0
        code = False
        hasURL = False
        uurls = None
        numurls = 0
        
        try:
            if(elem.get("AboutMe")):
                stripped = elem.get("AboutMe").encode('utf-8','ignore')
                lenText = len(stripped)    
                tokenized = tok.tokenize(stripped)
                hemo = sum(p in happyemoticons for p in tokenized)
                semo =  sum(p in sademoticons for p in tokenized)
                upper =  float(sum(x.isupper() for x in stripped)) / float(len(stripped)) * 100
                punctu =  sum(o in string.punctuation for o in stripped)
                code = True if sum(o in codetext for o in tokenized) > 0 else False
                result = re.findall(urlsreg, stripped)
                if(result):                    
                    uurls = ""
                    for u in result:
                        uurls = str(uurls) + str(u) + "|"

                    if(len(uurls) > 1):                        
                        uurls = uurls[:-1]
                
                    numurls = len(result)
                    if(numurls > 0):
                        hasURL = True

                del result
                del tokenized

        except UnicodeDecodeError, e:
            print 'Error %s' % e   
        
        '''
        user = (elem.get("Id"),              #"Id": 
                elem.get("Reputation"),      #"Reputation": 
                elem.get("CreationDate"),    #"CreationDate": 
                elem.get("DisplayName"),     #"DisplayName": 
                elem.get("LastAccessDate"),  #"LastAccessDate": 
                elem.get("Location"),        #"Location": 
                stripped,                    #"AboutMe": 
                elem.get("Views"),           #"Views": 
                elem.get("UpVotes"),         #"UpVotes": 
                elem.get("DownVotes"),       #"DownVotes": 
                elem.get("EmailHash"),       #"EmailHash": 
                lenText,
                hemo,
                semo,
                upper,
                punctu,
                code,
                hasURL,
                uurls,
                numurls
        )
        
        del user
        '''
            
        user_id = ""
        display_name = ""
        
        #website_url = ""
        #avatar_url = ""
        
        if elem.get("Id") != None:
            user_id = elem.get("Id")
        if elem.get("DisplayName") != None:
            display_name = elem.get("DisplayName")
        
        #if elem.get("WebsiteUrl") != None:
        #    website_url = str(elem.get("WebsiteUrl"))
        
        #if elem.get("ProfileImageUrl") != None:
        #    avatar_url = str(elem.get("ProfileImageUrl"))
        
        if user_id != "" and display_name != "":
            output_file.write(user_id + "\t" + display_name.replace("\n", " ") + "\n")
        
        if(counter == MAXINQUERY or elem.getnext() == False):
            numbatch += 1            
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)            
            counter = 0            
                    
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
        
def CollectStackExchangeUserProfile(user_path, output_path):
    
    # Output users' profile information
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    
    # Collect users' profile information
    context = etree.iterparse(user_path, events=('end',), tag='row')
    fast_iterUser(context, output_file)
    
    output_file.close()
    
def CompareImages(img1, img2):

    #img1 = r"E:\stackexchange.jpg"
    #img2 = r"E:\gravatar.jpg"
        
    hash1 = avhash(img1)
    hash2 = avhash(img2)
    
    #print hash1
    #print hash2
        
    dist = hamming(hash1, hash2)
        
    similarity = (36 - dist) / 36
    
    # print similarity
        
    if similarity >= 0.9:
        return True
    else:
        return False
    
def avhash(im):
    
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    
    im = im.resize((6, 6), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 36.
    return reduce(lambda x, (y, z): x | (z << y),
                  enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                  0)

def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

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
   
def SearchUsers(name, stackexchange_users_map):
    
    results = []
    for id in stackexchange_users_map.keys():
        user_name = stackexchange_users_map[id]
        
        similarity = Levenshtein.ratio(name, user_name)
        if similarity >= 0.95:
            results.append({"id":id, "similarity":similarity})
            # print str(similarity) + "\t" + name + "\t\t\t" + user_name
        
    return results

def FindMostSimilarResult(results):
    
    max_similarity = -1
    max_id = ""
    index = -1
    
    for i in range(len(results)):
        if max_similarity < results[i]["similarity"]:
            max_similarity = results[i]["similarity"]
            max_id = results[i]["id"]
            index = i
            
    results.pop(index)
                
    return max_id, results

def FuzzyMatching(path):
    
    # Read EdX learners
    edx_path = path + "/course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    profile_pics_learners_set = set()
    profile_pics_path = path + "/profile_pics/"
    files = os.listdir(profile_pics_path)
    for file in files:
        if file != ".DS_Store":
            profile_pics_learners_set.add(file)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
        
    # Gather the unmatched stackexchange learners
    unmatched_learner_set = set()
    
    matching_results_set = set()
    for learner in matching_results_map.keys():
        if "stackexchange" in matching_results_map[learner]["checked_platforms"]:
            matching_results_set.add(learner)
        else:
            unmatched_learner_set.add(learner)
                    
    for learner in profile_pics_learners_set:
        if learner not in matching_results_set:
            unmatched_learner_set.add(learner)    
         
    print "# unmatched learners is:\t" + str(len(unmatched_learner_set)) + "\n"
    
    # Gather the stackoverflow (data dump) user profiles
    stackexchange_users_map = {}
    stackexchange_users_path = path + "stackexchange/stackexchange_users_profile"
    stackexchange_users_file = open(stackexchange_users_path, "r")
    lines = stackexchange_users_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        id = array[0]
        name = array[1]
        stackexchange_users_map[id] = name
    stackexchange_users_file.close()
    
    # Remove the ids of matched learners
    for learner in matching_results_set:
        for link_record in matching_results_map[learner]["matched_platforms"]:
            if "http://stackoverflow.com/users/" in link_record["url"]:
                id = link_record["url"].replace("http://stackoverflow.com/users/", "")
                if "/" in id:
                    id = id[0:str(id).index("/")]
                stackexchange_users_map.pop(id)
                
    print "# users with profile information is:\t" + str(len(stackexchange_users_map)) + "\n"
    
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/stackexchange/fuzzy_matching"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        for i in range(len(lines)-5):
            line = lines[i].replace("\r\n", "").replace("\n", "")
            array = line.split("\t")
            learner = array[0]
            stackexchange_id = array[1]
            fuzzy_matching_results_map[learner] = stackexchange_id
            fuzzy_matching_results_set.add(learner)        
        
        for learner in fuzzy_matching_results_map.keys():
            if fuzzy_matching_results_map[learner] != "":
                num_matched_learners += 1  
        print "# previous matched learners is:\t" + str(num_matched_learners) + "\n"
        
    else:
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "w")
        
    count = len(fuzzy_matching_results_map)
    multitask_count = 0
    
    current_time = time.time()
    print "... START TIME at:" + str(current_time)
    
    candidates_map = {}
    candidates_set = set()
    
    for learner in unmatched_learner_set:
        
        if learner in fuzzy_matching_results_set:
            continue
        
        count += 1
        if count % 5 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
            
        multitask_count += 1
        if multitask_count < 22000:
            continue
        
        names = []
        if edx_learners_map[learner]["name"] != edx_learners_map[learner]["username"]:
            if len(edx_learners_map[learner]["name"]) >= 5: 
                names.append(edx_learners_map[learner]["name"])
            if len(edx_learners_map[learner]["username"]) >= 5: 
                names.append(edx_learners_map[learner]["username"])
        else:
            if len(edx_learners_map[learner]["name"]) >= 5: 
                names.append(edx_learners_map[learner]["name"])
                
        matched_links = set()
        if learner in matching_results_set:        
            for link_record in matching_results_map[learner]["matched_platforms"]:
                matched_links.add(link_record["url"])
            for link_record in matching_results_map[learner]["link_records"]:
                matched_links.add(link_record["url"])
            
        # Check whether the searched learner has profile pictures                           
        profile_pic_path = path + "/profile_pics/" + str(learner)                        
          
        if len(matched_links) > 0 or os.path.exists(profile_pic_path):
            
            search_mark = True
        
            for name in names:            
                if search_mark:                                        
                    cnt_results = 0                    
                    results = SearchUsers(name, stackexchange_users_map)
                    
                    if len(results) > 0:                        
                        while cnt_results < 20 and cnt_results < len(results):                            
                            cnt_results += 1                        
                            max_id, results = FindMostSimilarResult(results)
                        
                            # Check whether the candidate user's information has been downloaded or not
                            url = "http://stackoverflow.com/users/" + max_id
                            candidate_pic_path = path + "/stackexchange/candidate_pics/" + max_id + ".jpg"
                            
                            if max_id not in candidates_set:                                
                                try:
                                    page = requests.get(url)
                                    tree = html.fromstring(page.content)
                                    
                                    return_link = tree.xpath('//a[@class="url"]/@href')
                                    if len(return_link) != 0:
                                        return_link = return_link[0]
                                    else:
                                        return_link = ""
                                        
                                    pic_link = tree.xpath('//img[@class="avatar-user"]/@src')
                                    if len(pic_link) != 0:
                                        pic_link = pic_link[0]
                                    else:
                                        pic_link = ""
                                    
                                    if pic_link != "":
                                        pic = urllib2.urlopen(pic_link)
                                        
                                        output = open(candidate_pic_path, "wb")
                                        output.write(pic.read())
                                        output.close()
                                        
                                    candidates_set.add(max_id)
                                    candidates_map[max_id] = return_link
                                
                                except Exception as e:                                    
                                    print "Error occurs when downloading information...\t" + str(url) + "\t" + str(e)
                            
                            if max_id in candidates_set:
                                if candidates_map[max_id] in matched_links:
                                    search_mark = False
                                    fuzzy_matching_results_map[learner] = max_id
                                    fuzzy_matching_results_file.write(learner + "\t" + str(max_id) + "\n")
                                    num_matched_learners += 1
                                    break
                                else:                        
                                    if os.path.exists(candidate_pic_path):
                                    
                                        files = os.listdir(profile_pic_path)
                                    
                                        compare_mark = False
                                        for file in files:
                                        
                                            # Compare the candidate pic and the matched profile picture
                                            compare_mark = CompareImages(profile_pic_path + "/" + file, candidate_pic_path)
                                        
                                            if compare_mark:
                                                search_mark = False
                                                fuzzy_matching_results_map[learner] = max_id
                                                fuzzy_matching_results_file.write(learner + "\t" + str(max_id) + "\n")
                                                num_matched_learners += 1
                                                break
                                        
                                        if compare_mark:
                                            break
                
            if search_mark:
                fuzzy_matching_results_file.write(learner + "\t" + "" + "\n")
        
        else:
            fuzzy_matching_results_file.write(learner + "\t" + "" + "\n")
                    
    
    num_matched_learners = 0
    for learner in fuzzy_matching_results_map.keys():
        if fuzzy_matching_results_map[learner] != "":
            num_matched_learners += 1
                    
    print "# matched learners is:\t" + str(num_matched_learners) + "\n"
    
    fuzzy_matching_results_file.close()
    
def MergeMatchingResults(path):
    
    # 1. Read unmatched learners 
    
    profile_pics_learners_set = set()
    profile_pics_path = path + "/profile_pics/"
    files = os.listdir(profile_pics_path)
    for file in files:
        if file != ".DS_Store":
            profile_pics_learners_set.add(file)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
        
    # Gather the unmatched stackexchange learners
    unmatched_learner_set = set()
    
    matching_results_set = set()
    for learner in matching_results_map.keys():
        if "stackexchange" in matching_results_map[learner]["checked_platforms"]:
            matching_results_set.add(learner)
        else:
            unmatched_learner_set.add(learner)
                    
    for learner in profile_pics_learners_set:
        if learner not in matching_results_set:
            unmatched_learner_set.add(learner)    
         
    print "# unmatched learners is:\t" + str(len(unmatched_learner_set)) + "\n"
    
    # 2. Read fuzzy matching results
    fuzzy_matching_results = {}
    files = ["fuzzy_matching_local", "fuzzy_matching_remote"]
    for file in files:
        result_path = path + "stackexchange/" + file
        result_file = open(result_path, "r")
        lines = result_file.readlines()
        
        for line in lines:
            array = line.replace("\n", "").split("\t")
            learner = array[0]
            id = array[1]
            
            if learner in unmatched_learner_set:
                unmatched_learner_set.remove(learner)
                
            if id != "":
                fuzzy_matching_results[learner] = id
                
    print "# fuzzy matching learners is:\t" + str(len(fuzzy_matching_results))
    # print len(unmatched_learner_set)
    
    output_path = path + "stackexchange/fuzzy_matching"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(fuzzy_matching_results))
    output_file.close()
    
    
    








#################################################################################

# 1. Collect stackoverflow users' profile information
user_path = "/Users/Angus/Downloads/Users.xml"
output_path = "/Users/Angus/Downloads/stackexchange_users_profile"
# CollectStackExchangeUserProfile(user_path, output_path)

# 2. Fuzzy matching StackExchange learners
path = "/Users/Angus/Downloads/"
# FuzzyMatching(path)

# 3. Merge matching results
path = "/Users/Angus/Downloads/"
MergeMatchingResults(path)

print "Finished."



































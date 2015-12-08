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

import urllib, urllib2
import hashlib

import json
from PIL import Image

import requests
from lxml import html

import Levenshtein

import tweepy
    
def CompareImages(img1, img2):
    
    hash1 = avhash(img1)
    hash2 = avhash(img2)
    
    dist = hamming(hash1, hash2)       
    similarity = (36 - dist) / 36
 
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
        login = array[2]
        name = array[3]
        
        if email in edx_learners_set:
            edx_learners_map[email]["courses"].append(course_id)
        else:
            edx_learners_set.add(email)
            edx_learners_map[email] = {"login":login, "name": name, "courses":[course_id]}
        
    input.close()
            
    return (edx_learners_set, edx_learners_map)

def FuzzyMatching(path):
    
    # Read EdX learners
    edx_path = path + "/course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    # Gather the unmatched twitter learners  
    matching_results_set = set()
    for learner in matching_results_map.keys():
        if "twitter" in matching_results_map[learner]["checked_platforms"]:            
            edx_learners_set.remove(learner)
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
        
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/twitter/fuzzy_matching_5"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        for i in range(len(lines)-5):
            line = lines[i].replace("\r\n", "").replace("\n", "")
            array = line.split("\t")
            learner = array[0]
            twitter_login = array[1]
            fuzzy_matching_results_map[learner] = twitter_login
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
    
    candidates_map = {}
    candidates_set = set()
    
    # Twitter connection
    
    # consumerkey, consumerSecret, accessToken, accessTokenSecret
    
    # 0
    oauth_keys = [['CRMCoLrLjJBcK6HaGZ7Nn9dWC',
                   'SumAXkM9lZ50KBs4RQdrRdkWMBzrdVyS2YfceY8Te0CqwOqq2L',
                   '2609369460-otRuCCeuDmZxOwug2gJZlhF3PKPNA4tn0msGwH9',
                   'mejOpj5q4mgg03wMOxBTVuZ6ZOjiTuxhBpMGFne1Cj4c0']]
    
    # 1
    oauth_keys = [['ImxPrCI2dwPhrVP6F7MT3xXpl',
                   'jJpQ2gRGM31SHs5w1YhyZX7SPrkSu86PVhRfFwG5GGimZo81nE',
                   '2983438302-TqEZPHeTtWHSYRfDi2oJzxfmLkzrSH99QXe1dpd',
                   'SM6azouMW3bddVcwIlKuFqaWJB6bU4Opv6o76NaZZNpYB']]
    # 2
    oauth_keys = [['3eFaiFlmRVvMg4wSkgCsmfzMi',
                   'n4vjxdbegqkgmQZpHAT40JyPuxvO8SMq7A41ava66rmli9uHtr',
                   '2983438302-jP08K022DdkEm5TQHiV5XlF1USGTcPlz606zQHc',
                   '4K8Jg5lny1r5iKFYmDRzpz8bpm6NG8qtKgEmzuKLMgahp']]
    # 3
    oauth_keys = [['HEQkKdMbP029P1NybPYwoThoH',
                   'WTdFLVpiarx7xzKTz38jSlEWbNRETKoyOwNPwd2Sh7sJGAczLK',
                   '2609369460-4J2FJBLSW2UEK4yoSTIPnBIEpqQk2ZnlvwfFIRo',
                   '2UWmhdAwJLLfN8BeNFoKSVFzoUHrd2HsJ3IzfpC3FJT8o']]
    
    oauth_keys = [['3CBCHEMcRc4SuudrWGNCskUgD',
                   'lW8V6lHr55eZ2jxnw83znvGbAZ6eDwuTFSaKsz69y3uCLSbM8P',
                   '2983438302-HJoYZD4dPppINFz4BDhIcX3119mjcBEp7wPLpbn',
                   'sVONXbKI3JPvu7Sj4oKi1PgLmpTYUd6ACgXqAXXzGIHwa']]
    
    oauth_keys = [['6tbcOoHtfysOqklyHbDM4zZYv',
                   '4LO5XKPQhmeqfhATrqUL1i9BuBj1LTrBdT2qFCG8yOAoG4qCLf',
                   '2609369460-YZBezh1tkqtqmP7gL6sA5t9WZTa3gyBMF6oNFcx',
                   'Sej4ILlK2SxAjcooT7fiEetAfuwe8YwBqyexYpN6F4q7m']]
    
    auths = []
    global Tweeapi
    
    for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_key, access_secret)
        auths.append(auth)

        Tweeapi = tweepy.API(auths[0], retry_count=10, retry_delay=60, wait_on_rate_limit=True,
                             wait_on_rate_limit_notify=True)
    
    
    for learner in edx_learners_set:
        
        if learner in fuzzy_matching_results_set:
            continue
        
        multitask_count += 1
        
        #if multitask_count > 50000:
        #    continue
        
        #if multitask_count < 50000 or multitask_count > 100000:
        #    continue
        
        #if multitask_count < 100000 or multitask_count > 150000:
        #    continue
        
        #if multitask_count < 150000 or multitask_count > 200000:
        #    continue
        
        #if multitask_count < 200000 or multitask_count > 260000:
        #    continue
        
        if multitask_count < 260000:
            continue
        
        count += 1
        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
        
        names = {}
        names["login"] = edx_learners_map[learner]["login"]
        names["name"] = edx_learners_map[learner]["name"]
            
        matched_links = set()
        if learner in matching_results_set:        
            for link_record in matching_results_map[learner]["matched_platforms"]:
                matched_links.add(link_record["url"])
            for link_record in matching_results_map[learner]["link_records"]:
                matched_links.add(link_record["url"])
                
        search_mark = True
        
        keys = ["login", "name"]
        for key in keys:       
            
            if search_mark:
                
                users = []
                
                try:
                    users = Tweeapi.search_users(q=names[key], per_page=10, page=0)
                except Exception as e:
                    print "Errors occur when crawlling Twiter...\t" + str(e) 
                
                for user in users:
                    
                    login = user._json['screen_name'].encode('utf-8')
                    name = user._json['name'].encode('utf-8')
                    
                    # Check whether the candidate user's information has been downloaded or not
                    url = "http://twitter.com/" + login
                    candidate_pic_path = path + "/twitter/candidate_pics/" + login + ".jpg"
                    
                    if login not in candidates_set:
                        
                        try:
                            page = requests.get(url)
                            tree = html.fromstring(page.content)
                                    
                            return_link = tree.xpath('//a[@class="u-textUserColor"]/@title')
                            if len(return_link) != 0:
                                return_link = return_link[0]
                            else:
                                return_link = ""
                                        
                            pic_link = tree.xpath('//img[@class="ProfileAvatar-image "]/@src')
                            if len(pic_link) != 0:
                                pic_link = pic_link[0]
                            else:
                                pic_link = ""
                                
                                    
                            candidates_set.add(login)
                            candidates_map[login] = {"return_link": return_link, "name":name}                           
                                    
                            if pic_link != "":
                                pic = urllib2.urlopen(pic_link)
                                        
                                output = open(candidate_pic_path, "wb")
                                output.write(pic.read())
                                output.close()
                                        
                        except Exception as e:                                    
                            
                            print "Error occurs when downloading information...\t" + str(url) + "\t" + str(e)
                            
                    if login in candidates_set:
                        
                        if candidates_map[login]["return_link"] in matched_links:
                            search_mark = False
                            fuzzy_matching_results_map[learner] = login
                            fuzzy_matching_results_file.write(learner + "\t" + str(login) + "\n")
                            num_matched_learners += 1
                            break
                        else:
                            if login == edx_learners_map[learner]["login"] and candidates_map[login]["name"] == edx_learners_map[learner]["name"]:
                                search_mark = False
                                fuzzy_matching_results_map[learner] = login
                                fuzzy_matching_results_file.write(learner + "\t" + str(login) + "\n")
                                num_matched_learners += 1
                                break
                            else:
                                profile_pic_path = path + "/profile_pics/" + str(learner)
                                    
                                if os.path.exists(candidate_pic_path) and os.path.exists(profile_pic_path):
                                    
                                    files = os.listdir(profile_pic_path)
                                    
                                    compare_mark = False
                                    for file in files:
                                        
                                        # Compare the candidate pic and the matched profile picture
                                        compare_mark = CompareImages(profile_pic_path + "/" + file, candidate_pic_path)
                                        
                                        if compare_mark:
                                            search_mark = False
                                            fuzzy_matching_results_map[learner] = login
                                            fuzzy_matching_results_file.write(learner + "\t" + str(login) + "\n")
                                            num_matched_learners += 1
                                            break
                                        
                                    if compare_mark:
                                        break
                
        if search_mark:
            fuzzy_matching_results_file.write(learner + "\t" + "" + "\n")
            
    num_matched_learners = 0
    for learner in fuzzy_matching_results_map.keys():
        if fuzzy_matching_results_map[learner] != "":
            num_matched_learners += 1
                    
    print "# matched learners is:\t" + str(num_matched_learners) + "\n"
    
    fuzzy_matching_results_file.close()

  
def MergeMatchingResults(path):
    
    # 1. Read unmatched learners
    
    # Read EdX learners
    edx_path = path + "/course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    # Gather the unmatched twitter learners
    for learner in matching_results_map.keys():
        if "twitter" in matching_results_map[learner]["checked_platforms"]:            
            edx_learners_set.remove(learner)
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # 2. Read fuzzy matching results
    fuzzy_matching_results = {}
    files = ["fuzzy_matching_local", "fuzzy_matching_remote"]
    for file in files:
        result_path = path + "/twitter/" + file
        result_file = open(result_path, "r")
        lines = result_file.readlines()
        
        for line in lines:
            array = line.replace("\n", "").split("\t")
            learner = array[0]
            id = array[1]
            
            if learner in edx_learners_set:
                edx_learners_set.remove(learner)
                
            if id != "":
                fuzzy_matching_results[learner] = id
                
    print "# fuzzy matching learners is:\t" + str(len(fuzzy_matching_results))
    
    output_path = path + "/twitter/fuzzy_matching"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(fuzzy_matching_results))
    output_file.close()
    
    
    








#################################################################################

# 1. Fuzzy matching github learners
path = "/Users/Angus/Downloads/"
path = "/data/guanliang"
FuzzyMatching(path)

# 2. Merge matching results
path = "/Users/Angus/Downloads/"
#MergeMatchingResults(path)

print "Finished."



































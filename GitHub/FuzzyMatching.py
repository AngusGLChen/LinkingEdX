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

import mysql.connector
    
def CompareImages(img1, img2):

    #img1 = r"E:\github.jpg"
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
        login = array[2]
        name = array[3]
        
        if email in edx_learners_set:
            edx_learners_map[email]["courses"].append(course_id)
        else:
            edx_learners_set.add(email)
            edx_learners_map[email] = {"login":login, "name": name, "courses":[course_id]}
        
    input.close()
            
    return (edx_learners_set, edx_learners_map)
   
def SearchUsers(names, key, github_users_map):
    
    results = []
    
    for user in github_users_map.keys():
        
        candidate = github_users_map[user][key]        
        
        similarity = Levenshtein.ratio(str(names[key]), str(candidate))
        
        # print str(similarity) + "\t" + key + "\t" + str(names[key]) + "\t\t\t" + str(candidate)
        
        if similarity >= 0.5:
            results.append({"login": github_users_map[user]["login"], "similarity":similarity})
            # print str(similarity) + "\t" + key + "\t" + str(names[key]) + "\t\t\t" + str(candidate)
        
    return results

def FindMostSimilarResult(results):
    
    max_similarity = -1
    max_login = ""
    index = -1
    
    for i in range(len(results)):
        if max_similarity < results[i]["similarity"]:
            max_similarity = results[i]["similarity"]
            max_login = results[i]["login"]
            index = i
            
    results.pop(index)
                
    return max_login, results

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
    
    
    # Gather the unmatched github learners  
    matching_results_set = set()
    for learner in matching_results_map.keys():
        if "github" in matching_results_map[learner]["checked_platforms"]:            
            edx_learners_set.remove(learner)
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    
    # Gather the github (data dump) user profiles
    github_users_map = {}
    github_users_path = path + "/github/github_users"
    github_users_file = open(github_users_path, "r")
    jsonLine = github_users_file.read()
    github_users_map = json.loads(jsonLine)
    
    github_users_set = set()
    for learner in github_users_map.keys():
        github_users_set.add(learner)
    
    github_users_file.close()
    
    
    # Remove the login of matched learners
    for learner in matching_results_set:
        if learner in github_users_set:
            if "github" in matching_results_map[learner]["checked_platforms"]:
                github_users_map.pop(learner)
    print "# users with profile information is:\t" + str(len(github_users_map)) + "\n"
        
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/github/fuzzy_matching"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        for i in range(len(lines)-5):
            line = lines[i].replace("\r\n", "").replace("\n", "")
            array = line.split("\t")
            learner = array[0]
            github_login = array[1]
            fuzzy_matching_results_map[learner] = github_login
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
    
    for learner in edx_learners_set:
        
        if learner in fuzzy_matching_results_set:
            continue
        
        count += 1
        if count % 10 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
            
        #multitask_count += 1
        #if multitask_count < 22000:
        #    continue
        
        names = {}
        if len(edx_learners_map[learner]["login"]) >= 5:
            names["login"] = edx_learners_map[learner]["login"]
        if len(edx_learners_map[learner]["name"]) >= 5:
            names["name"] = edx_learners_map[learner]["name"]
            
        matched_links = set()
        if learner in matching_results_set:        
            for link_record in matching_results_map[learner]["matched_platforms"]:
                matched_links.add(link_record["url"])
            for link_record in matching_results_map[learner]["link_records"]:
                matched_links.add(link_record["url"])
                
        search_mark = True
        
        keys = ["name", "login"]
        for key in keys:
            
            if not key in names.keys():
                continue          
            
            if search_mark:
                
                cnt_results = 0
                results = SearchUsers(names, key, github_users_map)
                    
                if len(results) > 0:
                        
                    while cnt_results < 20 and cnt_results < len(results):
                            
                        cnt_results += 1                        
                        max_login, results = FindMostSimilarResult(results)
                    
                        # Check whether the candidate user's information has been downloaded or not
                        url = "http://github.com/" + max_login
                        candidate_pic_path = path + "/github/candidate_pics/" + max_login + ".jpg"
                    
                        if max_login not in candidates_set:
                        
                            try:
                                page = requests.get(url)
                                tree = html.fromstring(page.content)
                                    
                                return_link = tree.xpath('//a[@class="url"]/text()')
                                if len(return_link) != 0:
                                    return_link = return_link[0]
                                else:
                                    return_link = ""
                                        
                                pic_link = tree.xpath('//a[@class="vcard-avatar"]/img[@class="avatar"]/@src')
                                if len(pic_link) != 0:
                                    pic_link = pic_link[0]
                                else:
                                    pic_link = ""
                                
                                '''
                                login = ""
                                login = tree.xpath('//span[@class="vcard-username"]/text()')
                                if len(login) != 0:
                                    login = login[0]
                                else:
                                    login = ""
                                '''
                            
                                candidate_name = ""
                                candidate_name = tree.xpath('//span[@class="vcard-fullname"]/text()')
                                if len(candidate_name) != 0:
                                    candidate_name = candidate_name[0]
                                else:
                                    candidate_name = ""
                                    
                                candidates_set.add(max_login)
                                candidates_map[max_login] = {"return_link": return_link, "name":candidate_name}                           
                                    
                                if pic_link != "":
                                    pic = urllib2.urlopen(pic_link)
                                        
                                    output = open(candidate_pic_path, "wb")
                                    output.write(pic.read())
                                    output.close()
                                        
                            except Exception as e:                                    
                            
                                print "Error occurs when downloading information...\t" + str(url) + "\t" + str(e)
                            
                        if max_login in candidates_set:
                        
                            if candidates_map[max_login]["return_link"] in matched_links:
                                search_mark = False
                                fuzzy_matching_results_map[learner] = max_login
                                fuzzy_matching_results_file.write(learner + "\t" + str(max_login) + "\n")
                                num_matched_learners += 1
                                break
                            else:
                                if max_login == edx_learners_map[learner]["login"] and candidates_map[max_login]["name"] == edx_learners_map[learner]["name"]:
                                    search_mark = False
                                    fuzzy_matching_results_map[learner] = max_login
                                    fuzzy_matching_results_file.write(learner + "\t" + str(max_login) + "\n")
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
                                                fuzzy_matching_results_map[learner] = max_login
                                                fuzzy_matching_results_file.write(learner + "\t" + str(max_login) + "\n")
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

def FuzzyMatchingDatabaseVersion(path):
    
    # Read EdX learners
    edx_path = path + "/course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()

    
    # Gather the unmatched github learners  
    matching_results_set = set()
    for learner in matching_results_map.keys():
        if "github" in matching_results_map[learner]["checked_platforms"]:            
            edx_learners_set.remove(learner)
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/github/fuzzy_matching_7"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        for i in range(len(lines)-5):
            line = lines[i].replace("\r\n", "").replace("\n", "")
            array = line.split("\t")
            learner = array[0]
            github_login = array[1]
            fuzzy_matching_results_map[learner] = github_login
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
    
    # Connect database
    connection = mysql.connector.connect(user='root', password='Fa8j9tn4dBBxwx3V', host='127.0.0.1', database='GitHub')
    cursor = connection.cursor()
    
    for learner in edx_learners_set:
        
        if learner in fuzzy_matching_results_set:
            continue
        
        multitask_count += 1
        
        #if multitask_count > 40000:
        #    continue
        
        #if multitask_count < 40000 or multitask_count > 80000:
        #    continue
        
        #if multitask_count < 80000 or multitask_count > 120000:
        #    continue
        
        #if multitask_count < 120000 or multitask_count > 160000:
        #    continue
        
        #if multitask_count < 160000 or multitask_count > 200000:
        #    continue
        
        #if multitask_count < 200000 or multitask_count > 240000:
        #    continue
        
        #if multitask_count < 240000 or multitask_count > 280000:
        #    continue
        
        if multitask_count < 280000:
            continue
        
        count += 1
        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
        
        
        names = {}
        names["login"] = edx_learners_map[learner]["login"]
        names["name"] = edx_learners_map[learner]["name"]
        
        
        if "\"" in names["login"]:
            names["login"] = names["login"].replace("\"", "")
        if "\"" in names["name"]:
            names["name"] = names["name"].replace("\"", "")
         
            
        matched_links = set()
        if learner in matching_results_set:        
            for link_record in matching_results_map[learner]["matched_platforms"]:
                matched_links.add(link_record["url"])
            for link_record in matching_results_map[learner]["link_records"]:
                matched_links.add(link_record["url"])
                
        sql_query = "SELECT login, name FROM `users` WHERE login LIKE \"%" + names["login"] + "%\" or name LIKE \"%" + names["name"] + "%\""
        
        cursor.execute(sql_query)
        query_results = cursor.fetchall()
        
        results = {}
        for query_result in query_results:
            results[query_result[0]] = query_result[1]
        
        if len(results) > 10:
            
            similarity_map = {}
            
            for login in results.keys():
                name = results[login]
                
                similarity = (Levenshtein.ratio(str(names["login"]), str(login)) + Levenshtein.ratio(str(names["name"]), str(name))) / 2
                similarity_map[login] = similarity
            
            results.clear()
            
            while len(results) != 10:
                
                max_similarity = -1
                max_login = ""
                    
                for login in similarity_map.keys():
                    if max_similarity < similarity_map[login]:
                        max_similarity = similarity_map[login]
                        max_login = login
                    
                similarity_map.pop(max_login)        
                results[max_login] = max_similarity
        
        # print "# results...\t" + str(len(results))
        
        search_mark = True
        
        for login in results.keys():
            
            # login = result[0]
            
            # Check whether the candidate user's information has been downloaded or not
            url = "http://github.com/" + login
            candidate_pic_path = path + "/github/candidate_pics/" + login + ".jpg"
                    
            if login not in candidates_set:
                        
                try:
                    page = requests.get(url)
                    tree = html.fromstring(page.content)
                                    
                    return_link = tree.xpath('//a[@class="url"]/text()')
                    if len(return_link) != 0:
                        return_link = return_link[0]
                    else:
                        return_link = ""
                                        
                    pic_link = tree.xpath('//a[@class="vcard-avatar"]/img[@class="avatar"]/@src')
                    if len(pic_link) != 0:
                        pic_link = pic_link[0]
                    else:
                        pic_link = ""
                       
                    candidate_name = ""
                    candidate_name = tree.xpath('//span[@class="vcard-fullname"]/text()')
                    if len(candidate_name) != 0:
                        candidate_name = candidate_name[0]
                    else:
                        candidate_name = ""
                        
                    candidates_set.add(login)
                    candidates_map[login] = {"return_link": return_link, "name":candidate_name}                      
                                    
                    if pic_link != "":
                        pic = urllib2.urlopen(pic_link)
                                        
                        output = open(candidate_pic_path, "wb")
                        output.write(pic.read())
                        output.close()               
                               
                except Exception as e:                                    
                            
                    print "Error occurs when downloading information...\t" + str(url) + "\t" + str(e)
            
            # print len(candidates_set)
               
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
        
    # Gather the unmatched github learners
    unmatched_learner_set = set()
    
    matching_results_set = set()
    for learner in matching_results_map.keys():
        if "github" in matching_results_map[learner]["checked_platforms"]:
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
        result_path = path + "/github/" + file
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
    
    output_path = path + "/github/fuzzy_matching"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(fuzzy_matching_results))
    output_file.close()
    
    
    








#################################################################################

# 1. Fuzzy matching github learners
path = "/Users/Angus/Downloads/"
path = "/data"
FuzzyMatchingDatabaseVersion(path)

# 2. Merge matching results
path = "/Users/Angus/Downloads/"
#MergeMatchingResults(path)

print "Finished."



































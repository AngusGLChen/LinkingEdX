import sys
import time
reload(sys)
sys.setdefaultencoding("utf-8")

import stackexchange
from time import sleep
import random

import os
import urllib, urllib2

import json
from PIL import Image

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

def FuzzyMatching(path):
    
    # Read EdX learners
    edx_path = path + "/course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    profile_pics_learners_set = set()
    profile_pics_path = path + "/profile_pics/"
    files = os.listdir(profile_pics_path)
    for file in files:
        profile_pics_learners_set.add(file)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_input = open(matching_results_path, "r")
    jsonLine = matching_results_input.read()
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
            
    # StackExchange Searcher
    so = stackexchange.Site(stackexchange.StackOverflow, app_key='tlgwyuns3SvFf5thJ7Hpkw((', impose_throttling=True)
    
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
    
    for learner in unmatched_learner_set:
        
        if learner in fuzzy_matching_results_set:
            continue
        
        count += 1
        if count % 20 == 0:
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners)
            
        multitask_count += 1
        if multitask_count < 20000:
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
                    
                    block_mark = False
                    query_mark = False
                    
                    while not query_mark:
                        try:
                            results = so.users([], **{'inname': name, 'order':'desc', 'sort':'reputation'})
                            query_mark = True
                        except Exception as e:
                            print str(e) + "\t" + str(time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time())))
                            block_mark = True
                            
                        if block_mark:                            
                            sleep(60 * 5)                                        
                    
                    
                    # results = so.users([], **{'inname': name, 'order':'desc', 'sort':'reputation'})
                    results = results.fetch()
                    
                    cnt_results = 0
                
                    for item in results:
                        
                        cnt_results += 1
                        if cnt_results > 300:
                            break
                    
                        object = dir(item)
                        candidate = {"id": "", "url": "", "profile_image": ""}
                     
                        if "id" in object:
                            candidate["id"] = item.id
                        if "website_url" in object:
                            candidate["url"] = item.website_url
                        if "profile_image" in object:
                            candidate["profile_image"] = item.profile_image
                        
                        if candidate["url"] in matched_links:
                            search_mark = False
                            fuzzy_matching_results_map[learner] = candidate["id"]
                            fuzzy_matching_results_file.write(learner + "\t" + str(candidate["id"]) + "\n")
                            num_matched_learners += 1
                            break
                        else:                        
                            if candidate["profile_image"] != "":
                                
                                # Check whether the candidate user's profile picture has been downloaded or not
                                candidate_pic_path = path + "/stackexchange/candidate_pics/" + str(candidate["id"]) + ".jpg"
                                
                                pic_mark = False
                                if not os.path.exists(candidate_pic_path):
                                    
                                    try:
                                        candidate_pic = urllib2.urlopen(candidate["profile_image"])
                                        # print candidate["url"]
                                        output = open(candidate_pic_path, "wb")
                                        output.write(candidate_pic.read())
                                        output.close()
                                        pic_mark = True
                                    except Exception as e:
                                        print "Error occurs when downloading candidate pic...\t" + str(e)
                                else:
                                    pic_mark = True
                                        
                                if pic_mark:                                    
                                    
                                    files = os.listdir(profile_pic_path)
                                    
                                    compare_mark = False
                                    for file in files:
                                        
                                        # Compare the candidate pic and the matched profile picture
                                        compare_mark = CompareImages(profile_pic_path + "/" + file, candidate_pic_path)
                                        
                                        if compare_mark:
                                            search_mark = False
                                            fuzzy_matching_results_map[learner] = candidate["id"]
                                            fuzzy_matching_results_file.write(learner + "\t" + str(candidate["id"]) + "\n")
                                            num_matched_learners += 1
                                            break
                                        
                                    if compare_mark:
                                        break
                                                
                    sleep(0.5 + random.random())
                
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
    
    
path = "/Users/Angus/Downloads"
#path = "/data"
FuzzyMatching(path)
# CompareImages()
print "Finished."
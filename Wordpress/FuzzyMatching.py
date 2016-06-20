'''
Created on Dec 11, 2015

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os, time, urllib2, json, requests, Levenshtein
from lxml import etree, html
from PIL import Image
from Functions.CommonFunctions import ReadEdX, CompareImages



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
    
    # Gather the unmatched wordpress learners  
    matching_results_set = set()
    for learner in matching_results_map.keys():
        
        matching_results_set.add(learner)
        
        # Version 1
        # if "wordpress" in matching_results_map[learner]["checked_platforms"]:            
        #     edx_learners_set.remove(learner)
        
        # Version 2        
        for link_record in matching_results_map[learner]["link_records"]:       
            link = link_record["url"]
            if "wordpress.com" in link:
                if learner in edx_learners_set:
                    edx_learners_set.remove(learner)
        
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
        
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/wordpress/fuzzy_matching"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        for i in range(len(lines)-5):
            line = lines[i].replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                print file + "\t" + line
                continue
            
            if array[1] != "" and "wordpress.com" not in array[1]:
                print file + "\t" + line
                continue
            
            learner = array[0]
            link = array[1]
            fuzzy_matching_results_map[learner] = link
            fuzzy_matching_results_set.add(learner)        
        
        for learner in fuzzy_matching_results_map.keys():
            if fuzzy_matching_results_map[learner] != "":
                num_matched_learners += 1  
        print "# previous matched learners is:\t" + str(num_matched_learners) + "\n"
    else:
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "w")
        
    count = 0
    current_time = time.time()
    
    for learner in edx_learners_set:
        
        count += 1
        
        if learner in fuzzy_matching_results_set:
            continue
        
        #if count > 100000:
        #    continue
        
        #if count < 100000 or count > 200000:
        #    continue
        
        #if count < 200000:
        #    continue
        
        if count % 500 == 0:
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
        
        urls = []
        urls.append("http://" + names["login"] + ".wordpress.com/about/")
        
        full_name = ""
        names_array = names["name"].split("\t")
        if len(names_array) == 1:
            full_name = names_array[0]
            full_name = filter(str.isalnum, full_name)
            urls.append("http://" + full_name + ".wordpress.com/about/")
        else:
            if len(names_array) == 2:
                
                full_name = names_array[0] + names_array[1]
                full_name = filter(str.isalnum, full_name)
                urls.append("http://" + full_name + ".wordpress.com/about/")
                
                full_name = names_array[1] + names_array[0]
                full_name = filter(str.isalnum, full_name)
                urls.append("http://" + full_name + ".wordpress.com/about/")
            else:
                
                for element in names_array:
                    full_name += element
                    
                full_name = filter(str.isalnum, full_name)
                urls.append("http://" + full_name + ".wordpress.com/about/")
            
        for url in urls:       
            
            if search_mark:
                
                try:
                    
                    page = requests.get(url)
                    tree = html.fromstring(page.content)

                    # Determine whether the page exists
                    pagehead = tree.xpath('//div[@class="pagehead"]/h2/text()')
                    if len(pagehead) != 0:
                        # print "Page does not exist!"
                        continue
                
                    # If exists, determine whether the user matches the learner
                    # (1) Link
                    links = tree.xpath('//div[@class="entry-content"]//p/a/@href')
                    if len(links) != 0:
                        for link in links:
                            if link in matched_links:
                                search_mark = False
                                fuzzy_matching_results_map[learner] = url
                                fuzzy_matching_results_file.write(learner + "\t" + str(url) + "\n")
                                num_matched_learners += 1
                                break
                        if not search_mark:
                            break
                
                    # (2) Full name
                    introductions = tree.xpath('//div[@class="entry-content"]//p/text()')
                    line = ""
                    if len(introductions) != 0:
                        for introduction in introductions:
                            line += introduction + "\t"

                        postfix = url.replace("http://", "")
                        postfix = url.replace(".wordpress.com/about/", "")
                        
                        if postfix == names["login"]:

                            if str.lower(names["name"]) in str.lower(line):
                                search_mark = False
                                fuzzy_matching_results_map[learner] = url
                                fuzzy_matching_results_file.write(learner + "\t" + str(url) + "\n")
                                num_matched_learners += 1
                                break
                    
                    # (3) Pics
                    pic_links = tree.xpath('//div[@class="entry-content"]//img/@src')
                    if len(pic_links) != 0:
                        for pic_link in pic_links:
                            if pic_link != "":
                            
                                candidate_pic_path = path + "wordpress/candidate_pics/" + learner + ".jpg"
                            
                                try:
                                    pic = urllib2.urlopen(pic_link)
                                    output = open(candidate_pic_path, "wb")
                                    output.write(pic.read())
                                    output.close()
                                except Exception as e:
                                    print "Error occurs when downloading picture...\t" + str(e)
                                
                                profile_pic_path = path + "/profile_pics/" + str(learner)
                                    
                                if os.path.exists(candidate_pic_path) and os.path.exists(profile_pic_path):
                                    
                                    files = os.listdir(profile_pic_path)
                                    
                                    compare_mark = False
                                    for file in files:
                                        
                                        # Compare the candidate pic and the matched profile picture
                                        try:
                                            compare_mark = CompareImages(profile_pic_path + "/" + file, candidate_pic_path)
                                        except Exception as e:
                                            print e
                                            
                                        if compare_mark:
                                            search_mark = False
                                            fuzzy_matching_results_map[learner] = url
                                            fuzzy_matching_results_file.write(learner + "\t" + str(url) + "\n")
                                            num_matched_learners += 1
                                            break
                                        
                                    if compare_mark:
                                        break
                
                except Exception as e:
                    print "Errors occur when trying to visit the link...\t" + str(e) 
                    continue
                
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
    
    # Gather the unmatched wordpress learners
    for learner in matching_results_map.keys():
        
        # Version 1
        # if "wordpress" in matching_results_map[learner]["checked_platforms"]:            
        #     edx_learners_set.remove(learner)
        
        # Version 2        
        for link_record in matching_results_map[learner]["link_records"]:       
            link = link_record["url"]
            if "wordpress.com" in link:
                if learner in edx_learners_set:
                    edx_learners_set.remove(learner)
        
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # 2. Read fuzzy matching results
    fuzzy_matching_results = {}
    files = ["fuzzy_matching_0", "fuzzy_matching_1", "fuzzy_matching_2"]
    for file in files:
        result_path = path + "/wordpress/" + file
        result_file = open(result_path, "r")
        lines = result_file.readlines()
        
        for line in lines:
            
            line = line.replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                print file + "\t" + line
                continue
            
            if array[1] != "" and "wordpress.com" not in array[1]:
                print file + "\t" + line
                continue
            
            learner = array[0]
            link = array[1]
            
            if learner in edx_learners_set:
                edx_learners_set.remove(learner)
                
            fuzzy_matching_results[learner] = link
                
    print "# fuzzy matching learners is:\t" + str(len(fuzzy_matching_results))
    print len(edx_learners_set)
    
    output_path = path + "/wordpress/fuzzy_matching"
    output_file = open(output_path, "w")
    
    #output_file.write(json.dumps(fuzzy_matching_results))
    
    for learner in fuzzy_matching_results.keys():
        output_file.write(learner + "\t" + fuzzy_matching_results[learner] + "\n")
    
    output_file.close()

    
    








#################################################################################

# 1. Fuzzy matching github learners
path = "/Volumes/NETAC/LinkingEdX/"
#path = "/data/guanliang/"
#FuzzyMatching(path)

# 2. Merge matching results
path = "/Volumes/NETAC/LinkingEdX/"
MergeMatchingResults(path)

print "Finished."

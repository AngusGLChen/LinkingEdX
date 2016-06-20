'''
Created on Dec 11, 2015

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os, time, urllib2, json
from selenium import webdriver

import proxy
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
    
    # Gather the unmatched linkedin learners
    for learner in matching_results_map.keys():
        
        # Version 1
        # if "linkedin" in matching_results_map[learner]["checked_platforms"]:            
        #     edx_learners_set.remove(learner)
        
        # Version 2        
        for link_record in matching_results_map[learner]["link_records"]:       
            link = link_record["url"]
            if "linkedin.com" in link:
                if learner in edx_learners_set:
                    edx_learners_set.remove(learner)
        
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
        
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/linkedin/fuzzy_matching_test"
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
            
            if array[1] != "" and "www.linkedin.com" not in array[1]:
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
    
    proxy_list = []
    driver = None
    url_limit = 0
    
    for learner in edx_learners_set:
        
        count += 1
        
        if learner in fuzzy_matching_results_set:
            continue
        
        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
        
        #if count > 100000:
        #    continue
        
        #if count < 100000 or count > 200000:
        #    continue
        
        #if count < 200000:
        #    continue        
        
        names = {}
        names["login"] = edx_learners_map[learner]["login"]
        names["name"] = edx_learners_map[learner]["name"]
                
        search_mark = True
        
        urls = set()
               
        urls.add("https://www.linkedin.com/in/" + names["login"])
        
        full_name = ""
        names_array = names["name"].split("\t")
        if len(names_array) == 1:
            full_name = names_array[0]
            full_name = filter(str.isalnum, full_name)
            urls.add("https://www.linkedin.com/in/" + full_name)
        else:
            if len(names_array) == 2:
                
                full_name = names_array[0] + names_array[1]
                full_name = filter(str.isalnum, full_name)
                urls.add("https://www.linkedin.com/in/" + full_name)
                
                full_name = names_array[1] + names_array[0]
                full_name = filter(str.isalnum, full_name)
                urls.add("https://www.linkedin.com/in/" + full_name)
            else:
                
                for element in names_array:
                    full_name += element
                    
                full_name = filter(str.isalnum, full_name)
                urls.add("https://www.linkedin.com/in/" + full_name)
         
        for url in urls:
            
            if search_mark:                
                
                url_mark = True
                notFound_mark = False
                
                while url_mark:
                    
                    if driver != None and url_limit > 10:
                        driver.quit()
                        url_limit = 0
                        driver = None
                    
                    if driver == None:
                        
                        if len(proxy_list) == 0:
                            proxy_list = proxy.GetProxyList()
                        
                        ip = proxy_list.pop()                                            
                        ip_array = ip.split(":")
                                         
                        profile = webdriver.FirefoxProfile()
                        profile.set_preference("network.proxy.http", ip_array[0])
                        profile.set_preference("network.proxy.http_port", ip_array[1])
                        driver = webdriver.Firefox(firefox_profile=profile)
                    
                    driver.get(url)
                    url_limit += 1
                    
                    if "Sign Up" in driver.title or "Sign In" in driver.title:
                        continue
                                        
                    try:
                        page_title = driver.find_element_by_id("page-title").text
                        if "Profile Not Found" in page_title:
                            notFound_mark = True
                            break
                    except Exception as e:
                        nothing_to_do = 0
                        
                    try:
                        page_title = driver.find_element_by_tag_name('h1').text
                        if "Page Not Found" in page_title:
                            url_limit = 100
                            continue
                        if "Profile Not Found" in page_title:
                            notFound_mark = True
                            break 
                    except Exception as e:
                        nothing_to_do = 0
                    
                    url_mark = False                   
                    
                if notFound_mark:
                    continue
                                    
                # If exists, determine whether the user matches the learner                
                # (1) Full name
                try:
                    display_name = driver.find_element_by_id('name').text
                    postfix = url.replace("https://www.linkedin.com/in/", "")
                    if postfix == names["login"]:
                        if str.lower(str(display_name)) == str.lower(names["name"]):
                            search_mark = False
                            fuzzy_matching_results_map[learner] = url
                            fuzzy_matching_results_file.write(learner + "\t" + str(url) + "\n")
                            num_matched_learners += 1
                            break                        
                except Exception as e:
                    print "Errors occur when trying to download the name...\t" + str(driver.title) + "\t" + url
                    continue
                    
                
                # (2) Pics
                profile_pic_path = path + "/profile_pics/" + str(learner)
                if not os.path.exists(profile_pic_path):
                    continue
                
                try:
                    pic_link = driver.find_element_by_xpath('//div[@class="profile-picture"]/a/img').get_attribute("src")
                    if pic_link != "":                            
                        candidate_pic_path = path + "linkedin/candidate_pics/" + learner + ".jpg"
                            
                        try:
                            pic = urllib2.urlopen(pic_link)
                            output = open(candidate_pic_path, "wb")
                            output.write(pic.read())
                            output.close()
                        except Exception as e:
                            print str(e)
                                    
                        if os.path.exists(candidate_pic_path):
                                    
                            files = os.listdir(profile_pic_path)
                                    
                            compare_mark = False
                            for file in files:
                                        
                                # Compare the candidate pic and the matched profile picture
                                try:
                                    compare_mark = CompareImages(profile_pic_path + "/" + file, candidate_pic_path)
                                except Exception as e:
                                    print "Image comparison error..."
                                        
                                if compare_mark:
                                    search_mark = False
                                    fuzzy_matching_results_map[learner] = url
                                    fuzzy_matching_results_file.write(learner + "\t" + str(url) + "\n")
                                    num_matched_learners += 1
                                    break
                                        
                            if compare_mark:
                                break
                except Exception as e:
                    nothing_to_do = 0
                    
        if search_mark:
            fuzzy_matching_results_file.write(learner + "\t" + "" + "\n")
    
    if driver != None:    
        driver.quit()
            
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
    
    # Gather the unmatched linkedin learners
    for learner in matching_results_map.keys():
        
        # Version 1
        # if "linkedin" in matching_results_map[learner]["checked_platforms"]:            
        #     edx_learners_set.remove(learner)
        
        # Version 2        
        for link_record in matching_results_map[learner]["link_records"]:       
            link = link_record["url"]
            if "linkedin.com" in link:
                if learner in edx_learners_set:
                    edx_learners_set.remove(learner)
        
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # 2. Read fuzzy matching results
    fuzzy_matching_results = {}
    files = ["fuzzy_matching_acer", "fuzzy_matching_kai"]
    for file in files:
        result_path = path + "linkedin/" + file
        result_file = open(result_path, "r")
        lines = result_file.readlines()
        
        for line in lines:
            
            line = line.replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                print file + "\t" + line
                continue
            
            if array[1] != "" and "www.linkedin.com" not in array[1]:
                print file + "\t" + line
                continue
            
            learner = array[0]
            link = array[1]
            
            if learner in edx_learners_set:
                edx_learners_set.remove(learner)
                
            fuzzy_matching_results[learner] = link
                
    print "# fuzzy matching learners is:\t" + str(len(fuzzy_matching_results))
    print len(edx_learners_set)

    output_path = path + "/linkedin/fuzzy_matching"
    output_file = open(output_path, "w")
    #output_file.write(json.dumps(fuzzy_matching_results))
    
    for learner in fuzzy_matching_results.keys():
        output_file.write(learner + "\t" + fuzzy_matching_results[learner] + "\n")
    
    output_file.close()

#################################################################################

# 1. Fuzzy matching github learners
path = "/Volumes/NETAC/LinkingEdX/"
# path = "/data/guanliang/"
FuzzyMatching(path)

# 2. Merge matching results
path = "/Volumes/NETAC/LinkingEdX/"
#MergeMatchingResults(path)

print "Finished."

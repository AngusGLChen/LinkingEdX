'''
Created on Jan 7, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import json, os, time, random
from time import sleep
from selenium import webdriver

import proxy
from Functions.CommonFunctions import ReadEdX

def DownloadPage(path):
    
    matcher_link_map = {}
    matcher_set = set()
    
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
              
        for link_record in matching_results_map[learner]["link_records"]:       
            link = link_record["url"]
            if "linkedin.com" in link:
                if learner in edx_learners_set:
                    matcher_link_map[learner] = link
                    matcher_set.add(learner)
        
    print "# matched learners is:\t" + str(len(matcher_link_map))
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/linkedin/fuzzy_matching"
    
    fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
    lines = fuzzy_matching_results_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        array = line.split("\t")
        
        learner = array[0]
        link = array[1]
        
        if learner in edx_learners_set and "linkedin.com" in link:
            matcher_link_map[learner] = link
            matcher_set.add(learner)

    print "# matched learners is:\t" + str(len(matcher_link_map)) + "\n"
    
    # Read downloaded learners
    downloaded_matcher_set = set()
    download_path = path + "/linkedin/download/"
    files = os.listdir(download_path)
    for file in files:
        if file != ".DS_Store":
            downloaded_matcher_set.add(file)
            matcher_set.remove(file)
        
    print "# previously downloaded learners is:\t" + str(len(downloaded_matcher_set)) + "\n"
    
    proxy_list = []
    driver = None
    url_limit = 0
    
    while len(matcher_set) > 0:
        
        learner = matcher_set.pop()
        url = matcher_link_map[learner]
        
        if " " in url:
            continue

        url_mark = True
                
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
                break
                                    
            try:
                page_title = driver.find_element_by_id("page-title").text
                if "Profile Not Found" in page_title:
                    break
            except Exception as e:
                nothing_to_do = 0
                        
            try:
                page_title = driver.find_element_by_tag_name('h1').text
                if "Page Not Found" in page_title:
                    url_limit = 100
                    continue
                if "Profile Not Found" in page_title:
                    break 
            except Exception as e:
                nothing_to_do = 0
            
            url_mark = False
            page_content = driver.page_source
            
            if page_content != "":
                output_path = path + "linkedin/download/" + learner
                output_file = open(output_path, "w")
                output_file.write(page_content)
                output_file.close()
        
    if driver != None:    
        driver.quit()
            
    
    
    
    
    
    


#################################################################################
path = "/Volumes/NETAC/LinkingEdX/"
DownloadPage(path)
print "Finished."
    
        
    
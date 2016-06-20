'''
Created on Apr 10, 2016

@author: Angus
'''

import os, json
from Functions.CommonFunctions import ReadEdX

def AggregateMatchingResult(platforms, path):
    
    # Read EdX learners
    edx_path = path + "course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)

    learner_matching_result_map = {}
    learner_set = set()
    
    true_path = path + "latest_matching_result_0"
    true_file = open(true_path,"r")
    true_result = json.loads(true_file.read())
    
    for learner in true_result:
        
        if learner not in edx_learners_set:
            continue
        
        learner_matching_result_map[learner] = {}
        learner_matching_result_map[learner]["platforms"] = []
        learner_matching_result_map[learner]["true_links"] = []
        
        learner_set.add(learner)
        
        for matched_record in true_result[learner]["matched_platforms"]:
            url = matched_record["url"]
            platform = matched_record["platform"]
            
            if platform not in learner_matching_result_map[learner]["platforms"]:
                learner_matching_result_map[learner]["platforms"].append(platform)
                learner_matching_result_map[learner]["true_links"].append(url)
                
        for matched_record in true_result[learner]["link_records"]:
            url = matched_record["url"]
            platform = ""
            
            if "linkedin.com" in url:
                platform = "linkedin"
                
            if "witter.com" in url:
                platform = "twitter"
                
            if platform not in learner_matching_result_map[learner]["platforms"] and platform != "":
                learner_matching_result_map[learner]["platforms"].append(platform)
                learner_matching_result_map[learner]["true_links"].append(url)
         
    for platform in platforms:
        
        if platform == "gravatar":
            continue
        
        platform_path = path + platform + "/"
        
        fuzzy_path = platform_path + "fuzzy_matching"
        fuzzy_file = open(fuzzy_path, "r")
        lines = fuzzy_file.readlines()
        for line in lines:
            line = line.replace("\n", "")

            if platform == "github":
                array = line.split("    ")
            else:
                array = line.split("\t")
                
            if platform in ["github", "linkedin"] and len(array) < 2:
                continue
                
            learner = array[0]
            url = array[1]
            
            if url == "" or learner not in edx_learners_set:
                continue
            
            if platform == "stackexchange":
                url = "http://stackoverflow.com/users/" + url
                
            if platform == "twitter":
                url = "twitter.com/" + url
            
            if learner not in learner_set:
                
                learner_set.add(learner)
                
                learner_matching_result_map[learner] = {}
                learner_matching_result_map[learner]["platforms"] = []
            
            learner_matching_result_map[learner]["maybe_links"] = []
            
            if platform not in learner_matching_result_map[learner]["platforms"]:
                learner_matching_result_map[learner]["platforms"].append(platform)
                learner_matching_result_map[learner]["maybe_links"].append(url)
        
        
    output_path = path + "aggregation_matching_result"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(learner_matching_result_map))
    output_file.close()
    
    
    # Analysis
    for i in range(2,7):
        count = 0
        for learner in learner_matching_result_map.keys():
            if len(learner_matching_result_map[learner]["platforms"]) == i:
                count += 1
            
        print str(i) + "\t" + str(count)
    
    
    
platforms = ['stackexchange', 'github', 'gravatar', 'linkedin', 'twitter']
path = "/Volumes/NETAC/LinkingEdX/"
AggregateMatchingResult(platforms, path)
print "Finished."
    
    

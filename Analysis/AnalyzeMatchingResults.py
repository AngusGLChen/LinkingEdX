'''
Created on Nov 25, 2015

@author: Angus
'''

import json
from sets import Set
import re

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

def AnalyzeMatchingResults(course_path, result_path):
    
    edx_learners_set, edx_learners_map = ReadEdX(course_path)
    
    input_file = open(result_path, "r")
    jsonLine = input_file.read()
    jsonObject = json.loads(jsonLine)
    
    # Analysis - matched links
    course_map = {}
    learner_with_any_platform = set()
    
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_map.keys():
                course_map[course] = {}
                course_map[course]["registers"] = set()
                course_map[course]["stackexchange"] = set()
                course_map[course]["github"] = set()
                course_map[course]["twitter"] = set()
                course_map[course]["gravatar"] = set()
            course_map[course]["registers"].add(learner)
    
    for learner in jsonObject:
        learner_with_any_platform.add(learner)
        for checked_platform in jsonObject[learner]["checked_platforms"]:
            
            for course in edx_learners_map[learner]["courses"]:
                if checked_platform == "stackexchange":
                    course_map[course]["stackexchange"].add(learner)
                
                if checked_platform == "github":
                    course_map[course]["github"].add(learner)
                
                if checked_platform == "twitter":
                    course_map[course]["twitter"].add(learner)
                
                if checked_platform == "gravatar":
                    course_map[course]["gravatar"].add(learner)
       
    for course in course_map.keys():
        print course + "\t" + str(len(course_map[course]["registers"])) + "\t" + str(len(course_map[course]["stackexchange"])) + "\t" + str(len(course_map[course]["github"])) + "\t" + str(len(course_map[course]["twitter"])) + "\t" + str(len(course_map[course]["gravatar"])) + "\t"
    print
    
    print "# learners with any of the platforms is:\t" + str(len(learner_with_any_platform)) + "\n"
    
    # Analysis - unmatched links
    links_map = {}
    for learner in jsonObject:
        for link_record in jsonObject[learner]["link_records"]:
            link = link_record["url"]
            
            regex = re.compile("\w+\.com")
            if not len(regex.findall(link)) == 0:
                link = regex.findall(link)[0]
            
                if link not in links_map.keys():
                    links_map[link] = 0
            
                links_map[link] += 1
    
    sorted_links_map = sorted(links_map.items(), key=lambda d:d[1], reverse=True)
    for record in sorted_links_map:
        if record[1] > 10:
            print str(record[0]) + "\t" + str(record[1])
    print
    
    
    for course in course_map.keys():
        for learner in course_map[course]["twitter"]:
            name = edx_learners_map[learner]["name"]
            link = jsonObject[learner]["matched_platforms"]
            
            print name + "\t" + str(link)
                
    
    
    
    
course_path = "/Users/Angus/Downloads/course_metadata/course_email_list"
result_path = "/Users/Angus/Downloads/latest_matching_result_0"
AnalyzeMatchingResults(course_path, result_path)
print "Finished."



























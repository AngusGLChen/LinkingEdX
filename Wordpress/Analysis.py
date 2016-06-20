'''
Created on Dec 21, 2015

@author: Angus
'''

import json
from Functions.CommonFunctions import ReadEdX

def AnalyzeMatchingResults(platform, path):
    
    course_matcher_map = {}
    
    matched_link_set = set()
    
    # Read EdX learners
    edx_path = path + "course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)
    
    # 2. Direct matching
    direct_path = path + "latest_matching_result_0"
    direct_file = open(direct_path, "r")
    jsonLine = direct_file.read()
    direct_results_map = json.loads(jsonLine)
    direct_file.close()
    
    for learner in direct_results_map.keys():
        
        for link_record in direct_results_map[learner]["link_records"]:       
            link = link_record["url"]
            if "wordpress.com" in link:
                if learner in edx_learners_set:
                    for course in edx_learners_map[learner]["courses"]:
                        if course not in course_matcher_map.keys():
                            course_matcher_map[course] = set()
                        course_matcher_map[course].add(learner)
                    matched_link_set.add(link)
    
    # 3. Fuzzy matching
    fuzzy_path = path + platform + "/fuzzy_matching"
    fuzzy_file = open(fuzzy_path, "r")
    lines = fuzzy_file.readlines()
    for line in lines:
        
        line = line.replace("\r\n", "")
        line = line.replace("\n", "")
            
        array = line.split("\t")
        
        learner = array[0]
        url = array[1]
        
        if learner not in edx_learners_set:
            continue
        
        if url != "":
            for course in edx_learners_map[learner]["courses"]:
                if course not in course_matcher_map.keys():
                    course_matcher_map[course] = set()
                course_matcher_map[course].add(learner)
            url = url.replace("/about/", "").replace("/about", "")
            matched_link_set.add(url)
    
    # Output analysis results
    count_course_learner_map = {}
    for course in course_learners_map.keys():
        count_course_learner_map[course] = len(course_learners_map[course])    
    sorted_count_course_learner_map = sorted(count_course_learner_map.items(), key=lambda d:d[1], reverse=True)
    for record in sorted_count_course_learner_map:
        # print str(record[0]) + "\t" + str(record[1]) + "\t" + str(len(course_matcher_map[str(record[0])]))
        print str(len(course_matcher_map[str(record[0])]))
    print
    
    
    # Output matched links
    output_path = path + platform + "/matched_links"
    output_file = open(output_path, "w")
    for link in matched_link_set:
        output_file.write(link + "\n")
    output_file.close()
    
    
    
    
    
    
    
    
    
    




path = "/Volumes/NETAC/LinkingEdX/"
platform = "wordpress"
AnalyzeMatchingResults(platform, path)
print "Finished."

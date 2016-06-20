'''
Created on Dec 21, 2015

@author: Angus
'''

import json
from Functions.CommonFunctions import ReadEdX

def AnalyzeMatchingResults(platform, path):
    
    course_matcher_map = {}    
    
    non_duplicate_matcher_set = set()
    
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
        if platform in direct_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:
                
                non_duplicate_matcher_set.add(learner)
                
                for course in edx_learners_map[learner]["courses"]:
                    if course not in course_matcher_map.keys():
                        course_matcher_map[course] = set()
                    course_matcher_map[course].add(learner)                    
    '''                   
    
    print
    
    # 3. Fuzzy matching
    fuzzy_path = path + platform + "/fuzzy_matching"
    fuzzy_file = open(fuzzy_path, "r")
    lines = fuzzy_file.readlines()
    for line in lines:
        
        line = line.replace("\r\n", "")
        line = line.replace("\n", "")
            
        array = line.split("\t")
            
        if len(array) != 2:
            # print file + "\t" + line
            continue
            
        
        # if array[1] != "" and "twitter.com" not in array[1]:
        #     print file + "\t" + line
        #     continue
        
            
        learner = array[0]
        login = array[1]
        
        if learner not in edx_learners_set:
            continue
        
        if login != "":
            
            non_duplicate_matcher_set.add(learner)
            
            for course in edx_learners_map[learner]["courses"]:
                if course not in course_matcher_map.keys():
                    course_matcher_map[course] = set()
                course_matcher_map[course].add(learner)
            
    print
    '''
    # Output analysis results
    count_course_learner_map = {}
    for course in course_learners_map.keys():
        count_course_learner_map[course] = len(course_learners_map[course])    
    sorted_count_course_learner_map = sorted(count_course_learner_map.items(), key=lambda d:d[1], reverse=True)
    for record in sorted_count_course_learner_map:
        #print str(record[0]) + "\t" + str(record[1]) + "\t" + str(len(course_matcher_map[str(record[0])]))
        print str(len(course_matcher_map[str(record[0])]))
    print
    
    print "# non-duplicate matchers is:\t" + str(len(non_duplicate_matcher_set))
    
    
    
    
    
    
    
    
    




path = "/Volumes/NETAC/LinkingEdX/"
platform = "twitter"
AnalyzeMatchingResults(platform, path)
print "Finished."

'''
Created on Feb 6, 2016

@author: Angus
'''

import os, json, mysql.connector
from Functions.CommonFunctions import ReadEdX

def ReadCourseNameCode(course_meta_path):
    
    course_code_name_map = {}    
    path = course_meta_path + "name_code"
    file = open(path, "r")
    lines = file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        name = array[0]
        code = array[1]
        
        course_code_name_map[code] = name        
    return course_code_name_map 

def AnalyzeNumberActivity(course_meta_path, web_path):
    
    # 1.1 Read EdX learners
    edx_path = course_meta_path + "course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)

            
    # 1.2 Read platform ids data

    platform_pair_map = {}
    
    # 1.1 Explicit matching
    explicit_path = web_path + "/explicit_matching"
    explicit_file = open(explicit_path, "r")
    matched_records = json.loads(explicit_file.read())
    for learner in matched_records.keys():
        if learner in edx_learners_set:
            
            platforms = matched_records[learner]["platforms"]
        
            for platform in platforms:
                platform_name = platform["platform"]
                id = platform["id"]
            
                if platform_name not in platform_pair_map.keys():
                    platform_pair_map[platform_name] = {}
                
                platform_pair_map[platform_name][id] = learner
    
    # 1.2 Direct matching
    direct_path = os.path.dirname(os.path.dirname(course_meta_path)) + "/latest_matching_result_0"
    direct_file = open(direct_path, "r")
    jsonLine = direct_file.read()
    direct_results_map = json.loads(jsonLine)
    direct_file.close()
    
    for learner in direct_results_map.keys():
        if "stackexchange" in direct_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:
                for matched_platform in direct_results_map[learner]["matched_platforms"]:
                    if matched_platform["platform"] == "stackexchange":
                        url = matched_platform["url"]
                        array = url.replace("http://","").split("/")
                        platform = array[0]
                        id = array[-1]
                        
                        if not str.isdigit(str(id)):
                            continue
                        
                        if platform not in platform_pair_map.keys():
                            continue
                        
                        platform_pair_map[platform][id] = learner
                            
    # 1.3 Fuzzy matching
    fuzzy_path = web_path + "/fuzzy_matching"
    fuzzy_file = open(fuzzy_path, "r")
    lines = fuzzy_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        id = array[1]
        if id != "":
            if learner in edx_learners_set:
                platform_pair_map["stackoverflow.com"][id] = learner
    
    
    # Connect to the database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1')
    cursor = connection.cursor()
    
    activity_statistic_map = {}
    
    for platform in platform_pair_map.keys():
        
        # print platform
        
        database_name = platform.replace(".", "_")
        cursor.execute("USE " + database_name + ";")
        
        # Questions
        sql = "SELECT questions.owneruserid FROM questions"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            user_id = str(result[0])
            
            learner = platform_pair_map[platform][user_id]
            
            for course in edx_learners_map[learner]["courses"]:
                
                if course not in activity_statistic_map.keys():
                    activity_statistic_map[course] = {}
                    activity_statistic_map[course]["questions"] = 0
                    activity_statistic_map[course]["answers"] = 0
                    activity_statistic_map[course]["comments"] = 0
                    
                activity_statistic_map[course]["questions"] += 1
                
        # Answers
        sql = "SELECT answers.owneruserid FROM answers"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            user_id = str(result[0])
            learner = platform_pair_map[platform][user_id]
            
            for course in edx_learners_map[learner]["courses"]:
                
                if course not in activity_statistic_map.keys():
                    activity_statistic_map[course] = {}
                    activity_statistic_map[course]["questions"] = 0
                    activity_statistic_map[course]["answers"] = 0
                    activity_statistic_map[course]["comments"] = 0
                    
                activity_statistic_map[course]["answers"] += 1
                
        # Answers
        sql = "SELECT comments.userid FROM comments"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            user_id = str(result[0])
            learner = platform_pair_map[platform][user_id]
            
            for course in edx_learners_map[learner]["courses"]:
                
                if course not in activity_statistic_map.keys():
                    activity_statistic_map[course] = {}
                    activity_statistic_map[course]["questions"] = 0
                    activity_statistic_map[course]["answers"] = 0
                    activity_statistic_map[course]["comments"] = 0
                    
                activity_statistic_map[course]["comments"] += 1
                
    # Output analysis result
    # Read course_code & name
    course_code_name_map =  ReadCourseNameCode(course_meta_path)
    
    for course in activity_statistic_map.keys():
        print course_code_name_map[course] + "\t" + str(activity_statistic_map[course]["questions"]) + "\t" + str(activity_statistic_map[course]["answers"]) + "\t" + str(activity_statistic_map[course]["comments"])
    
def GatherRelevantQuestionTag(course_meta_path, web_path):
    
    course_code_name_map =  ReadCourseNameCode(course_meta_path)
    
    # 1. Read EdX learners
    edx_path = course_meta_path + "course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)
            
    # 2. Read platform ids data

    platform_pair_map = {}
    
    learner_pair_map = {}
    learner_pair_set = set()
    
    # 2.1 Explicit matching
    explicit_path = web_path + "/explicit_matching"
    explicit_file = open(explicit_path, "r")
    matched_records = json.loads(explicit_file.read())
    for learner in matched_records.keys():
        if learner in edx_learners_set:
            
            platforms = matched_records[learner]["platforms"]
        
            for platform in platforms:
                platform_name = platform["platform"]
                id = platform["id"]
            
                if platform_name not in platform_pair_map.keys():
                    platform_pair_map[platform_name] = {}
                platform_pair_map[platform_name][id] = learner
                
                if learner not in learner_pair_set:
                    learner_pair_set.add(learner)
                    learner_pair_map[learner] = {}
                    
                learner_pair_map[learner][platform_name] = id
    
    # 1.2 Direct matching
    direct_path = os.path.dirname(os.path.dirname(course_meta_path)) + "/latest_matching_result_0"
    direct_file = open(direct_path, "r")
    jsonLine = direct_file.read()
    direct_results_map = json.loads(jsonLine)
    direct_file.close()
    
    for learner in direct_results_map.keys():
        if "stackexchange" in direct_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:
                for matched_platform in direct_results_map[learner]["matched_platforms"]:
                    if matched_platform["platform"] == "stackexchange":
                        url = matched_platform["url"]
                        array = url.replace("http://","").split("/")
                        platform = array[0]
                        id = array[-1]
                        
                        if not str.isdigit(str(id)):
                            continue
                        
                        if platform not in platform_pair_map.keys():
                            continue
                        platform_pair_map[platform][id] = learner
                        
                        if learner not in learner_pair_set:
                            learner_pair_set.add(learner)
                            learner_pair_map[learner] = {}
                    
                        learner_pair_map[learner][platform_name] = id
                            
    # 1.3 Fuzzy matching
    fuzzy_path = web_path + "/fuzzy_matching"
    fuzzy_file = open(fuzzy_path, "r")
    lines = fuzzy_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        id = array[1]
        if id != "":
            if learner in edx_learners_set:
                platform_pair_map["stackoverflow.com"][id] = learner
                
                if learner not in learner_pair_set:
                    learner_pair_set.add(learner)
                    learner_pair_map[learner] = {}
                    
                learner_pair_map[learner]["stackoverflow.com"] = id
    
    
    # Connect to the database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1')
    cursor = connection.cursor()
    
    course_tag_map = {}
    
    for course in course_learners_map.keys():
        
        course_tag_map[course] = {}
        num_questions = 0
        
        for learner in course_learners_map[course]:
            if learner in learner_pair_set:
                
                question_id_set = set()
                
                for platform in learner_pair_map[learner].keys():
                    platform_id = learner_pair_map[learner][platform]
                    
                    database_name = platform.replace(".", "_")
                    cursor.execute("USE " + database_name + ";")
                    
                    # Comments
                    sql = "SELECT comments.postid FROM comments WHERE comments.userid = " + str(platform_id)
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for result in results:
                        question_id = result[0]
                        question_id_set.add(question_id)
                        
                    # Answers
                    sql = "SELECT answers.parentId FROM answers WHERE answers.owneruserid = " + str(platform_id)
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for result in results:
                        question_id = result[0]
                        question_id_set.add(question_id)
                        
                    # Questions
                    sql = "SELECT questions.id FROM questions WHERE questions.owneruserid = " + str(platform_id)
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    for result in results:
                        question_id = result[0]
                        question_id_set.add(question_id)
                        
                    num_questions += len(question_id_set)
                        
                    for question_id in question_id_set:
                        sql = "SELECT questions.tags FROM questions WHERE questions.id = " + str(question_id)
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        for result in results:
                            tags = result[0].split("|")
                            for tag in tags:
                                if tag not in course_tag_map[course].keys():
                                    course_tag_map[course][tag] = 0
                                course_tag_map[course][tag] += 1
                
        # print course_code_name_map[course] + "\t" + str(num_questions)              
        sorted_course_tages = sorted(course_tag_map[course].items(), key=lambda t: t[1], reverse=True)
        
        print
        print course_code_name_map[course]
        for i in range(50):
            print sorted_course_tages[i][0] + "\t" + str(sorted_course_tages[i][1])
        print
          

def AnalyzeFP101xTags():
    
    tag_seeds = ["functional-programming", "haskell", "scala", "clojure", "monads"]
    
    # Connect to the database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='stackoverflow_com')
    cursor = connection.cursor()
    
    tag_map = {}
    tag_set = set()
    
    # Questions
    sql = "SELECT questions.tags FROM questions"
    cursor.execute(sql)
    results = cursor.fetchall()
    for result in results:
        tags = result[0].split("|")
        mark = False
        for tag in tags:
            if tag in tag_seeds:
                mark = True
        if mark:
            for tag in tags:
                if tag not in tag_set:
                    tag_set.add(tag)
                    tag_map[tag] = 0
                tag_map[tag] += 1
                
    sorted_tag_map = sorted(tag_map.items(), key=lambda t: t[1], reverse=True)
    for i in range(100):
        print sorted_tag_map[i][0] + "\t" + str(sorted_tag_map[i][1])
    




course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/stackexchange/"
# AnalyzeNumberActivity(course_meta_path, web_path)
# GatherRelevantQuestionTag(course_meta_path, web_path)
AnalyzeFP101xTags()

print "Finished."




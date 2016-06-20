'''
Created on Feb 11, 2016

@author: Angus
'''

import mysql.connector, json, os, math, datetime
from lxml import etree
from happyfuntokenizing import *
from Functions.CommonFunctions import ReadEdX

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
    
def QueryRelevantData(web_path):
            
    # 1. Read tags
    tag_set = set()
    tag_path = web_path + "ex_tags"
    tag_file = open(tag_path, "r")
    lines = tag_file.readlines()
    for line in lines:
        tag = line.replace("\n", "")
        tag_set.add(tag)
    tag_file.close()
    
    # 2. Connect to the database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='stackoverflow_com2')
    cursor = connection.cursor()
    
    # 2.1 Questions
    
    questions_map = {}
    questions_set = set()

    sql = "SELECT questions.id, questions.owneruserid, questions.tags, questions.viewcount, questions.answercount, questions.creationdate, questions.closeddate FROM questions"
    cursor.execute(sql)
    results = cursor.fetchall()
    
    for result in results:
        
        tag_line = result[2]

        tags = tag_line.split("|")
        for tag in tags:
            if tag in tag_set:
                
                question_id = result[0]
                user_id = result[1]
                viewcount = result[3]
                answercount = result[4]
                creation_date = str(result[5])
                close_date = str(result[6])
                
                questions_set.add(question_id)
                questions_map[question_id] = {"user_id": user_id, "tags": tags, "viewcount": viewcount, "answercount": answercount, "creation_date": creation_date, "close_date": close_date}
                
                break
            
    question_path = web_path + "so_questions"
    question_file = open(question_path, "w")
    question_file.write(json.dumps(questions_map))
    question_file.close()
    
    # 2.2 Answers
    
    question_answer_map = {}
    question_answer_set = set()
    
    learner_question_map = {}
    learner_question_set = set()
    
    sql = "SELECT answers.id, answers.parentId, answers.score, answers.owneruserid FROM answers"
    cursor.execute(sql)
    results = cursor.fetchall()
    
    for result in results:
        
        question_id = result[1]
        
        if question_id in questions_set:
            
            answer_id  = result[0]
            score = result[2]
            user_id = result[3]
            
            if question_id not in question_answer_set:
                question_answer_set.add(question_id)
                question_answer_map[question_id] = []
                
            question_answer_map[question_id].append({"user_id": user_id, "score": score})
            
            if user_id not in learner_question_set:
                learner_question_set.add(user_id)
                learner_question_map[user_id] = []
                    
            learner_question_map[user_id].append(question_id)
    
    answer_path = web_path + "so_answers"
    answer_file = open(answer_path, "w")
    answer_file.write(json.dumps(question_answer_map))
    answer_file.close()
    
    learner_question_path =  web_path + "learner_question_map"
    learner_question_file = open(learner_question_path, "w")
    learner_question_file.write(json.dumps(learner_question_map))
    learner_question_file.close()
        
   
def AnalyzeEX101xCharacteristics(web_path):
    
    # 1. Read EdX learners
    learner_set = set()
    
    edx_path = course_meta_path + "course_email_list"
    edx_file = open(edx_path, "r")
    lines = edx_file.readlines()
    for line in lines:
        array = line.split("\t")
        course_code = array[0]
        email = array[1]
        
        if course_code == "EX101x/1T2015":
            learner_set.add(email)
      
    # 2. Read platform ids data
    learner_id_map = {}
    id_set = set()

    # 2.1 Explicit matching
    explicit_path = web_path + "/explicit_matching"
    explicit_file = open(explicit_path, "r")
    matched_records = json.loads(explicit_file.read())
    for learner in matched_records.keys():
        if learner in learner_set:
            
            platforms = matched_records[learner]["platforms"]
        
            for platform in platforms:
                platform_name = platform["platform"]
                id = platform["id"]
            
                if platform_name == "stackoverflow.com":
                    learner_id_map[learner] = id
                
    # 2.2 Direct matching
    direct_path = os.path.dirname(os.path.dirname(course_meta_path)) + "/latest_matching_result_0"
    direct_file = open(direct_path, "r")
    jsonLine = direct_file.read()
    direct_results_map = json.loads(jsonLine)
    direct_file.close()
    
    for learner in direct_results_map.keys():
        if "stackexchange" in direct_results_map[learner]["checked_platforms"]:
            if learner in learner_set:
                for matched_platform in direct_results_map[learner]["matched_platforms"]:
                    if matched_platform["platform"] == "stackexchange":
                        url = matched_platform["url"]
                        array = url.replace("http://","").split("/")
                        platform = array[0]
                        id = array[-1]
                        
                        if not str.isdigit(str(id)):
                            continue
                        
                        if platform == "stackoverflow.com":
                            learner_id_map[learner] = id
                   
    # 2.3 Fuzzy matching
    fuzzy_path = web_path + "/fuzzy_matching"
    fuzzy_file = open(fuzzy_path, "r")
    lines = fuzzy_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        id = array[1]
        if id != "":
            if learner in learner_set:
                learner_id_map[learner] = id
                
    print "# 1 matched learner is:\t" + str(len(learner_id_map))
    
    learner_set.clear()
    for learner in learner_id_map.keys():
        learner_set.add(learner)
        id_set.add(learner_id_map[learner])
    
    # 2. Read stackoverflow data
    question_path = web_path + "so_questions"
    question_file = open(question_path, "r")
    questions_map = json.loads(question_file.read())
    question_file.close()
    
    answer_path = web_path + "so_answers"
    answer_file = open(answer_path, "r")
    answers_map = json.loads(answer_file.read())
    answer_file.close()
    
    learner_question_path =  web_path + "learner_question_map"
    learner_question_file = open(learner_question_path, "r")
    learner_question_map = json.loads(learner_question_file.read())
    learner_question_file.close()
    
    time_num_question_map = {}
    
    for question in questions_map.keys():
        
        question = str(question)
        
        tags = questions_map[question]["tags"]
        
        mark = False
        for tag in tags:
            if "excel" in tag:
                mark = True
                break
        
        # mark = True
        
        if mark:
            user_id = str(questions_map[question]["user_id"])
            if user_id in id_set or True:
                creation_date = questions_map[question]["creation_date"][0:7]
                
                format="%Y-%m"                          
                creation_date = datetime.datetime.strptime(creation_date,format)
                
                if creation_date not in time_num_question_map.keys():
                    time_num_question_map[creation_date] = 0
                    
                time_num_question_map[creation_date] += 1
    
    sorted_time_num_question_map = sorted(time_num_question_map.items(), key=lambda x: x[0])
    
    print
    for tuple in sorted_time_num_question_map:
        print str(tuple[0])[0:7] + "\t" + str(tuple[1])
    print
    
    time_num_answer_map = {}
    
    for learner in learner_question_map.keys():
        
        #if learner not in id_set:
        #    continue
        
        question_set = learner_question_map[learner]
        
        for question in question_set:
            
            question = str(question)
            
            tags = questions_map[question]["tags"]
            mark = False
            for tag in tags:
                if "excel" in tag:
                    mark = True
                    break
            
            # mark = True
                    
            if mark:
                
                creation_date = questions_map[question]["creation_date"][0:7]
                
                format="%Y-%m"                          
                creation_date = datetime.datetime.strptime(creation_date,format)
                
                if creation_date not in time_num_answer_map.keys():
                    time_num_answer_map[creation_date] = 0
                    
                time_num_answer_map[creation_date] += 1
    
    sorted_time_num_answer_map = sorted(time_num_answer_map.items(), key=lambda x: x[0])
    
    print
    for tuple in sorted_time_num_answer_map:
        print str(tuple[0])[0:7] + "\t" + str(tuple[1])
    print
        
    
    
    
    
    
    
        
        
      

    
    
    
    
    
########################


course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/stackexchange/"

#QueryRelevantData(web_path)
AnalyzeEX101xCharacteristics(web_path)

print "Finished."















    
    
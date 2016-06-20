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
from cgi import log
from sklearn.svm.libsvm_sparse import sparse
from sklearn.metrics import ranking

def SelectRelevantTags(web_path):
    
    tag_path = web_path + "201509/stackoverflow.com/Tags.xml"
    context = etree.iterparse(tag_path, events=('end',), tag='row')
    
    tag_set = set()
    tag_set.add("functional-programming")
    tag_set.add("scala")
    tag_set.add("haskell")
    tag_set.add("clojure")
    tag_set.add("monads")
    
    for event, elem in context:
        tag = elem.get("TagName")
        
        if "scala" in tag:
            tag_set.add(tag)
            
        if "haskell" in tag:
            tag_set.add(tag)
            
        if "clojure" in tag:
            tag_set.add(tag)
            
    print "# tags is:\t" + str(len(tag_set))
            
    output_path = web_path + "fp_tags"
    output_file = open(output_path, "w")
            
    for tag in tag_set:
        output_file.write(tag + "\n")
    
    output_file.close()
    
def QueryRelevantData(web_path):
            
    # 1. Read tags
    tag_set = set()
    tag_path = web_path + "fp_tags"
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
        
def ComputeMEC(course_meta_path, web_path):
    
    # 1. Read EdX learners
    learner_set = set()
    
    edx_path = course_meta_path + "course_email_list"
    edx_file = open(edx_path, "r")
    lines = edx_file.readlines()
    for line in lines:
        array = line.split("\t")
        course_code = array[0]
        email = array[1]
        
        if course_code == "FP101x/3T2014":
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
        
        
    print "# 2 matched learner is:\t" + str(len(learner_set))
    print "# 3 matched learner is:\t" + str(len(id_set))
    print
    
    # 3. Read stackoverflow data
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
    
    print "# stackoverflow users is:\t" + str(len(learner_question_map))
    
    learner_mec_map = {}
    
    avg_debatableness = 0
    for question in questions_map.keys():
        avg_debatableness += questions_map[question]["answercount"]
    avg_debatableness = float(avg_debatableness) / len(questions_map)
    
    # print "The value of avg_debatableness is:\t" + str(avg_debatableness)
    
    count = 0
    '''
    for learner in learner_set:
        
        id = learner_id_map[learner]
        
        mec_score = 0
        
        if id not in learner_question_map.keys():
            continue
        
        questions_set = learner_question_map[id]
        
        for question in questions_set:
            
            question = str(question)
            
            question_answers = answers_map[question]
            sorted_question_answers = sorted(question_answers, key=lambda question_answers: question_answers["score"], reverse=True)
            
            rank = -1
            for i in range(len(sorted_question_answers)):
                user_id = sorted_question_answers[i]["user_id"]
                if str(user_id) == str(id):
                    rank = i + 1
                    break
            
            if rank > 0:
                utility = 1 / float(rank)
                debatableness = questions_map[question]["answercount"]
            
                mec_score += utility * debatableness / avg_debatableness
        
        mec_score /= len(questions_set)
        learner_mec_map[id] = mec_score
        
        if mec_score >= 1:
            count += 1
    '''
    
    for id in learner_question_map.keys():
        
        mec_score = 0
        questions_set = learner_question_map[id]
        
        for question in questions_set:
            
            question = str(question)
            
            question_answers = answers_map[question]
            sorted_question_answers = sorted(question_answers, key=lambda question_answers: question_answers["score"], reverse=True)
            
            rank = -1
            for i in range(len(sorted_question_answers)):
                user_id = sorted_question_answers[i]["user_id"]
                if str(user_id) == str(id):
                    rank = i + 1
                    break
            
            if rank > 0:
                utility = 1 / float(rank)
                debatableness = questions_map[question]["answercount"]
            
                mec_score += utility * debatableness / avg_debatableness
        
        mec_score /= len(questions_set)
        
        course_mark = False
        
        if id in id_set:
            course_mark = True
            if mec_score >= 1:
                count += 1
        
        learner_mec_map[id] = {"mec_score": mec_score, "course_mark": course_mark}
    
    print count
    
    print "# mec records is:\t" + str(len(learner_mec_map))
    
    mec_path = web_path + "mec_scores"
    mec_file = open(mec_path, "w")
    mec_file.write(json.dumps(learner_mec_map))
    mec_file.close()
    
    
    
def AnalyzeMEC(web_path):
    
    mec_path = web_path + "mec_scores"
    mec_file = open(mec_path, "r")
    learner_mec_map = json.loads(mec_file.read())
    mec_file.close()
    
    array = []
    
    for learner in learner_mec_map.keys():
        if learner_mec_map[learner]["course_mark"]:
            array.append(learner_mec_map[learner]["mec_score"])
            
    print "# array is:\t" + str(len(array))        
    
    array.sort()

    # Plot of the distribution of the certificate numbers
    
    array_to_plot = [3.5 if i > 3 else i for i in array]
    bins = np.arange(0.5, 4, 0.5)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    _, bins, patches = plt.hist(array_to_plot, bins=bins, color='r')

    xlabels = np.array(bins[1:], dtype='|S4')
    xlabels[-1] = '3.5+'

    N_labels = len(xlabels)

    plt.xticks(0.5 * (np.arange(N_labels) + 1) + 0.5)
    ax.set_xticklabels(xlabels)
    
    plt.xlim(xmin=0.5)
    plt.setp(patches, linewidth=0)
    
    plt.show()
    
    course_count = 0
    for learner in learner_mec_map.keys():
        if learner_mec_map[learner]["course_mark"]:
            if learner_mec_map[learner]["mec_score"] >= 1:
                course_count += 1
                
    print "# course owls is:\t" + str(course_count)
    

def AnalyzeMecChracteristics(web_path):
    
    # 1. Read MEC scores
    mec_path = web_path + "mec_scores"
    mec_file = open(mec_path, "r")
    learner_mec_map = json.loads(mec_file.read())
    mec_file.close()
    
    overall_set = set()
    owl_set = set()
    sparrow_set = set()
    
    for learner in learner_mec_map.keys():
        if learner_mec_map[learner]["course_mark"]:
            
            score = learner_mec_map[learner]["mec_score"]
            if score > 0:
                overall_set.add(learner)
                if score >= 1:
                    owl_set.add(learner)
                else:
                    sparrow_set.add(learner)
                    
    print "# overall learners is:\t" + str(len(overall_set))
                
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
    
    # 3. Compute metrics   
    overall_array = []
    owl_array = []
    sparrow_array = []
    
    # Connect to the database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='stackoverflow_com2')
    cursor = connection.cursor()
    
    # 3.1 # answers
    '''
    for learner in overall_set:
        num_answers = 0
        question_set = learner_question_map[learner]
        for question in question_set:
            answer_set = answers_map[str(question)]
            for answer in answer_set:
                user_id = answer["user_id"]
                if str(user_id) == str(learner):
                    num_answers += 1
        
        num_answers = math.log(num_answers)
        overall_array.append(num_answers)
        
        if learner in owl_set:
            owl_array.append(num_answers)
        else:
            sparrow_array.append(num_answers)
    
    # 3.2 Reputation
    for learner in overall_set:
        sql = "SELECT users.reputation FROM users WHERE users.id = " + str(learner)
        cursor.execute(sql)
        result = cursor.fetchone()
        reputation = result[0]
        
        print reputation
        reputation = math.log(reputation)
        
        overall_array.append(reputation)
        
        if learner in owl_set:
            owl_array.append(reputation)
        else:
            sparrow_array.append(reputation)
    
    # 3.3 Z-score
    for learner in overall_set:
        z_score = 0
        
        num_answers = 0
        question_set = learner_question_map[learner]
        for question in question_set:
            answer_set = answers_map[str(question)]
            for answer in answer_set:
                user_id = answer["user_id"]
                if str(user_id) == str(learner):
                    num_answers += 1
        
        sql = "SELECT COUNT(*)FROM questions WHERE questions.owneruserid = " + str(learner)
        cursor.execute(sql)
        result = cursor.fetchone()
        num_questions = result[0]
        
        z_score = (num_answers - num_questions) / math.sqrt(num_answers + num_questions)
        overall_array.append(z_score)
        
        if learner in owl_set:
            owl_array.append(z_score)
        else:
            sparrow_array.append(z_score)

    # 3.7 Popularity
    for learner in overall_set:
        viewcount = 0
        question_set = learner_question_map[learner]
        for question in question_set:
            question = str(question)
            viewcount = questions_map[question]["viewcount"]
            
            viewcount = math.log(viewcount)
        
            overall_array.append(viewcount)
        
            if learner in owl_set:
                owl_array.append(viewcount)
            else:
                sparrow_array.append(viewcount)
    
    # 3.7 Popularity
    for learner in overall_set:
        duration = 0
        question_set = learner_question_map[learner]
        for question in question_set:
            question = str(question)
            creation_date = questions_map[question]["creation_date"]
            close_date = questions_map[question]["close_date"]
            
            format="%Y-%m-%d %H:%M:%S"                          
            creation_date = datetime.datetime.strptime(creation_date,format)
            close_date = datetime.datetime.strptime(close_date,format)
            
            duration = (close_date - creation_date).days * 24 + (close_date - creation_date).seconds / float(3600)
        
            overall_array.append(duration)
        
            if learner in owl_set:
                owl_array.append(duration)
            else:
                sparrow_array.append(duration)
    '''
    
    
    
    # Boxplot
    fig = plt.figure(1, figsize=(9, 6))
    ax = fig.add_subplot(111)
    bp = ax.boxplot([overall_array, owl_array, sparrow_array])
    
    for box in bp['boxes']:
        box.set( color='#7570b3', linewidth=2)
        #box.set( facecolor = '#1b9e77' )        
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=2)        
    for cap in bp['caps']:
        cap.set(color='#7570b3', linewidth=2)        
    for median in bp['medians']:
        median.set(color='#ff3300', linewidth=2)        
    for flier in bp['fliers']:
        flier.set(marker='o', color='#7570b3', alpha=0.5)        
    ax.set_xticklabels(["Overall", "Owls", "Sparrows"])
    
    
    plt.show()
    '''
    # 3.4 Participation
    question_overall_array = []
    question_owl_array = []
    question_sparrow_array = []
    
    answer_overall_array = []
    answer_owl_array = []
    answer_sparrow_array = []
    
    for learner in overall_set:
        
        num_answers = 0
        question_set = learner_question_map[learner]
        for question in question_set:
            answer_set = answers_map[str(question)]
            for answer in answer_set:
                user_id = answer["user_id"]
                if str(user_id) == str(learner):
                    num_answers += 1
                    
        answer_overall_array.append(num_answers)
        if learner in owl_set:
            answer_owl_array.append(num_answers)
        else:
            answer_sparrow_array.append(num_answers)
        
        sql = "SELECT COUNT(*)FROM questions WHERE questions.owneruserid = " + str(learner)
        cursor.execute(sql)
        result = cursor.fetchone()
        num_questions = result[0]
        
       
        question_overall_array.append(num_questions)
        
        if learner in owl_set:
            question_owl_array.append(num_questions)
        else:
            question_sparrow_array.append(num_questions)
    
    question_group = [np.mean(question_overall_array), np.mean(question_owl_array), np.mean(question_sparrow_array)]
    answer_group = [np.mean(answer_overall_array), np.mean(answer_owl_array), np.mean(answer_sparrow_array)]
    
    print question_group
    print answer_group
    
    # 3.5 Debatableness
    for learner in overall_set:
        question_set = learner_question_map[learner]
        for question in question_set:
            answer_set = answers_map[str(question)]
            
            debatableness = len(answer_set)
            
            overall_array.append(debatableness)
            if learner in owl_set:
                owl_array.append(debatableness)
            else:
                sparrow_array.append(debatableness)
    
    overall_array_to_plot = [11 if i > 10 else i for i in overall_array]
    owl_array_to_plot = [11 if i > 10 else i for i in owl_array]
    sparrow_array_to_plot = [11 if i > 10 else i for i in sparrow_array]
    
    bins = np.arange(0, 12, 1)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    _, bins, patches = plt.hist([overall_array_to_plot, owl_array_to_plot, sparrow_array_to_plot], bins=bins, label=["Overall", "Owls", "Sparrows"], histtype='bar')
    
    print bins
    
    xlabels = np.array(bins[1:], dtype='|S4')
    xlabels[-2] = '10+'
    xlabels[-1] = ' '

    N_labels = len(xlabels)

    plt.xticks(1 * (np.arange(N_labels) - 1) + 2.5)
    ax.set_xticklabels(xlabels)
    
    plt.setp(patches, linewidth=0)
    
    plt.xlabel("Debatableness")  
    plt.legend()
    plt.show()
    '''
    '''
    # 3.6 Quality
    
    owl_array = []
    sparrow_array = []
    
    for question in answers_map.keys():
        owl_mark = False
        sparrow_mark = False
        
        debatableness = len(answers_map[question])
        
        for answer_tuple in answers_map[question]:
            user_id = answer_tuple["user_id"]
            if str(user_id) in owl_set:
                owl_mark = True
            if str(user_id) in sparrow_set:
                sparrow_mark = True
                
        if owl_mark and sparrow_mark:
            question_answers = answers_map[question]
            sorted_question_answers = sorted(question_answers, key=lambda question_answers: question_answers["score"], reverse=True)
            
            for i in range(len(sorted_question_answers)):
                tuple = sorted_question_answers[i]
                user_id = tuple["user_id"]
                
                if str(user_id) in overall_set:
                    
                    ranking = 1 - 1 / ( 1 / float(i + 1) * debatableness)

                    if str(user_id) in owl_set:
                        owl_array.append((debatableness, ranking))
                    else:
                        sparrow_array.append((debatableness, ranking))
    '''
    '''
    owl_array.sort()
    
    x_array = []
    y_array = []
    for tuple in owl_array:
        print tuple
        x_array.append(tuple[0])
        y_array.append(tuple[1])
        
    sparrow_array.sort()
    
    w_array = []
    z_array = []
    for tuple in sparrow_array:
        w_array.append(tuple[0])
        z_array.append(tuple[1])
    
    plt.plot(x_array, y_array, label="Owl")
    plt.plot(w_array, z_array, label="Sparrow")
                    
    owl_array.sort()
    x_array = [10, 20, 30, 40, 50]
    y_array = [0, 0, 0, 0, 0]
    
    count_array = [0, 0, 0, 0, 0]
    
    for tuple in owl_array:
        debatableness = tuple[0]
        ranking = tuple[1]
        
        if debatableness < x_array[0]:
            y_array[0] += ranking
            count_array[0] += 1
        
        if debatableness >= x_array[0] and debatableness < x_array[1]:
            y_array[1] += ranking
            count_array[1] += 1
            
        if debatableness >= x_array[1] and debatableness < x_array[2]:
            y_array[2] += ranking
            count_array[2] += 1
            
        if debatableness >= x_array[2] and debatableness < x_array[3]:
            y_array[3] += ranking
            count_array[3] += 1
            
        if debatableness >= x_array[3]:
            y_array[4] += ranking
            count_array[4] += 1
            
    for i in range(5):
        if count_array[i] != 0:
            y_array[i] /= count_array[i]
        
    plt.plot(x_array, y_array, label="Owl")
        
    sparrow_array.sort()
    x_array = [10, 20, 30, 40, 50]
    y_array = [0, 0, 0, 0, 0]
    
    count_array = [0, 0, 0, 0, 0]
    
    for tuple in sparrow_array:
        debatableness = tuple[0]
        ranking = tuple[1]
        
        if debatableness < x_array[0]:
            y_array[0] += ranking
            count_array[0] += 1
        
        if debatableness >= x_array[0] and debatableness < x_array[1]:
            y_array[1] += ranking
            count_array[1] += 1
            
        if debatableness >= x_array[1] and debatableness < x_array[2]:
            y_array[2] += ranking
            count_array[2] += 1
            
        if debatableness >= x_array[2] and debatableness < x_array[3]:
            y_array[3] += ranking
            count_array[3] += 1
            
        if debatableness >= x_array[3]:
            y_array[4] += ranking
            count_array[4] += 1
            
    for i in range(5):
        if count_array[i] != 0:
            y_array[i] /= count_array[i]
                    
    plt.plot(x_array, y_array, label="Sparrow")
    plt.xlabel("Debatableness")  
    plt.legend()
    plt.show()
    '''
    
    
def AnalyzeFP101xCharacteristics(web_path):
    
    # 1. Read EdX learners
    learner_set = set()
    
    edx_path = course_meta_path + "course_email_list"
    edx_file = open(edx_path, "r")
    lines = edx_file.readlines()
    for line in lines:
        array = line.split("\t")
        course_code = array[0]
        email = array[1]
        
        if course_code == "FP101x/3T2014":
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
            if tag == "haskell":
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
                if tag == "haskell":
                    mark = True
            
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

#SelectRelevantTags(web_path)
#QueryRelevantData(web_path)

#ComputeMEC(course_meta_path, web_path)
#AnalyzeMEC(web_path)

#AnalyzeMecChracteristics(web_path)

AnalyzeFP101xCharacteristics(web_path)

print "Finished."















    
    
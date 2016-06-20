'''
Created on Feb 12, 2016

@author: Angus
'''

import json, mysql.connector

def BasicStatisticsAnalysis(web_path):
    
    # 1. Read platform ids data
    platform_id_path =  web_path + "/platform_ids"
    platform_id_file = open(platform_id_path, "r")
    platform_ids_map = json.loads(platform_id_file.read())
    platform_id_file.close()
    
    # Connect to the database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1')
    cursor = connection.cursor()
    
    num_questions = 0
    num_answers = 0
    num_comments = 0
    
    for platform in platform_ids_map.keys():
        
        learner_id_set = platform_ids_map[platform]
        
        if platform != "stackoverflow.com":
            continue
        
        database_name = platform.replace(".", "_")
        
        # 1. Use the database
        cursor.execute("USE " + database_name + ";")
        
        # 2. Questions
        sql = "SELECT questions.owneruserid FROM questions"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            id = str(result[0])
            if id in learner_id_set:
                num_questions += 1
                
        print "Questions done."
                
        # 3. Answers
        sql = "SELECT answers.owneruserid FROM answers"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            id = str(result[0])
            if id in learner_id_set:
                num_answers += 1
                
        print "Answers done."
        
        # 4. Comments
        sql = "SELECT comments.userid FROM comments"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            id = str(result[0])
            if id in learner_id_set:
                num_comments += 1
                
        print platform + "\t" + str(num_questions) + "\t" + str(num_answers) + "\t" + str(num_comments)
    
    print
    print str(num_questions) + "\t" + str(num_answers) + "\t" + str(num_comments) 
    
    
web_path = "/Volumes/NETAC/LinkingEdX/stackexchange/"
BasicStatisticsAnalysis(web_path)

















'''
Created on Dec 21, 2015

@author: Angus
'''

import os, mysql.connector
from Functions.CommonFunctions import ReadEdX

def MatchLearnersExplicitly(edx_path, web_path):
    
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    matched_learners = {}
    
    # Connect database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='GitHub')
    cursor = connection.cursor()
    
    for learner in edx_learners_set:
        
        sql_query = "SELECT login, email FROM `users` WHERE email=\"" + learner + "\""
        
        try:        
            cursor.execute(sql_query)
        except Exception as e:
            print "Database error..."
            continue
        
        results = cursor.fetchall()
        if len(results) > 0:
            matched_learners[learner] = results[0][0]
                
    # Output matching results
    output_path = os.path.dirname(web_path) + "/explicit_matching"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    
    # Analyze
    print "The number of matched learners in total is: " + str(len(matched_learners)) + "\n"
    
    course_learner_map = {}    
    
    for email in matched_learners.keys():
        for course in edx_learners_map[email]["courses"]:
            if course not in course_learner_map.keys():
                course_learner_map[course] = set()
            course_learner_map[course].add(email)
        
        output_file.write(email + "\t" + str(','.join(edx_learners_map[email]["courses"])) + "\t" +  matched_learners[email] +"\n")
    
    output_file.close()
    
    '''
    count_course_learner_map = {}
    for course in course_learner_map.keys():
        count_course_learner_map[course] = len(course_learner_map[course])    
    sorted_count_course_learner_map = sorted(count_course_learner_map.items(), key=lambda d:d[1], reverse=True)
    for record in sorted_count_course_learner_map:
        #print "The number of matched learners from course\t" + str(record[0]) + "\tis:\t" + str(record[1])
        print str(record[0]) + "\t" + str(record[1])
    print
    '''
    
edx_path = "/Volumes/NETAC/LinkingEdX/course_metadata/course_email_list"
web_path = "/Volumes/NETAC/LinkingEdX/github/"
MatchLearnersExplicitly(edx_path, web_path)
print "Finished."
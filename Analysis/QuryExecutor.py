'''
Created on Sep 7, 2015

@author: Angus
'''

import mysql.connector
import time,datetime
from time import *

def GetMatchedLearners(path):
    
    matched_learner_email_set = set()
    
    fp = open(path, "r")
    for line in fp:
        array = line.split(",")
        email = str.lower(array[0])
        matched_learner_email_set.add(email)
    
    return matched_learner_email_set   

def EdXQueryExecutor(path):
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='MOOC')
    cursor = connection.cursor()
    
    # To query the set of completed learners
    completed_learner_set = set()
    sql_query = "SELECT course_user.course_user_id FROM course_user, global_user WHERE course_user.course_user_id=global_user.course_user_id AND global_user.course_id=\"DelftX/FP101x/3T2014\" AND course_user.certificate_status=\"downloadable\""
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        completed_learner_set.add(result[0])
        
    # To query the mapping relation between email and edxID
    email_edxID_map = {}
    sql_query = "SELECT user_pii.email, global_user.course_user_id FROM user_pii, global_user WHERE user_pii.global_user_id=global_user.global_user_id AND global_user.course_id=\"DelftX/FP101x/3T2014\""
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        email = str(result[0])
        email = str.lower(email)
        course_user_id = result[1]        
        email_edxID_map[email] = course_user_id
    
    print str(len(email_edxID_map))
        
    matched_learner_email_set = GetMatchedLearners(path)    
    num_pass = 0
    
    for email in matched_learner_email_set:
        course_user_id = email_edxID_map[email]
        if course_user_id in completed_learner_set:
            num_pass += 1
    
    print "Out of\t" + str(len(matched_learner_email_set)) + "\tmatched learners,\t" + str(num_pass) + "\tpass the course."  

def CommentsQueryExecutor():
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='StackOverflow')
    cursor = connection.cursor()
    
    format="%Y-%m-%d %H:%M:%S"
    start_time = "2014-10-14 07:00:00"
    start_time = datetime.datetime.strptime(start_time,format)
    end_time = "2014-12-31 23:59:00"
    end_time = datetime.datetime.strptime(end_time,format)
    
    # For comments
    print "Processing comments..."
    
    # Number of records
    sql_query = "SELECT COUNT(*) FROM comments"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    print "The number of records is: " + str(result[0])
    
    # Number of learners
    sql_query = "SELECT COUNT(DISTINCT(comments.userid)) FROM comments"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    print "The number of learners is: " + str(result[0])
    
    # Number of questions
    sql_query = "SELECT COUNT(DISTINCT(comments.postid)) FROM comments"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    print "The number of learners is: " + str(result[0])
    
    print "Before/During/After the course..."
    set_before = set()
    set_during = set()
    set_after = set()
    
    sql_query = "SELECT comments.id, comments.postid, comments.userid, comments.creationdate FROM comments"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        time = result[3]
        if time < start_time:
            set_before.add(result[0])
        if time > start_time and time < end_time:
            set_during.add(result[0])
        if time > end_time:
            set_after.add(result[0])
        
    print "The number of before/during/after records is: " + str(len(set_before)) + "\t" + str(len(set_during)) + "\t" + str(len(set_after))
    
    sql_query = "SELECT comments.id, comments.postid, comments.userid, comments.creationdate FROM comments"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        time = result[3]
        if time < start_time:
            set_before.add(result[2])
        if time > start_time and time < end_time:
            set_during.add(result[2])
        if time > end_time:
            set_after.add(result[2])
        
    print "The number of before/during/after learners is: " + str(len(set_before)) + "\t" + str(len(set_during)) + "\t" + str(len(set_after))
    
    sql_query = "SELECT comments.id, comments.postid, comments.userid, comments.creationdate FROM comments"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        time = result[3]
        if time < start_time:
            set_before.add(result[1])
        if time > start_time and time < end_time:
            set_during.add(result[1])
        if time > end_time:
            set_after.add(result[1])
        
    print "The number of before/during/after questions is: " + str(len(set_before)) + "\t" + str(len(set_during)) + "\t" + str(len(set_after))
    
def AnswersQueryExecutor():
        
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='StackOverflow')
    cursor = connection.cursor()
    
    format="%Y-%m-%d %H:%M:%S"
    start_time = "2014-10-14 07:00:00"
    start_time = datetime.datetime.strptime(start_time,format)
    end_time = "2014-12-31 23:59:00"
    end_time = datetime.datetime.strptime(end_time,format)
    
    # For comments
    print "Processing comments..."
    '''
    # Number of records
    sql_query = "SELECT COUNT(*) FROM comments"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    print "The number of records is: " + str(result[0])
    
    # Number of learners
    sql_query = "SELECT COUNT(DISTINCT(comments.userid)) FROM comments"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    print "The number of learners is: " + str(result[0])
    
    # Number of questions
    sql_query = "SELECT COUNT(DISTINCT(comments.postid)) FROM comments"
    cursor.execute(sql_query)
    result = cursor.fetchone()
    print "The number of learners is: " + str(result[0])
    '''
    print "Before/During/After the course..."
    set_before = set()
    set_during = set()
    set_after = set()
    '''
    sql_query = "SELECT comments.id, comments.postid, comments.userid, comments.creationdate FROM comments"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        time = result[3]
        if time < start_time:
            set_before.add(result[0])
        if time > start_time and time < end_time:
            set_during.add(result[0])
        if time > end_time:
            set_after.add(result[0])
        
    print "The number of before/during/after records is: " + str(len(set_before)) + "\t" + str(len(set_during)) + "\t" + str(len(set_after))
    
    sql_query = "SELECT comments.id, comments.postid, comments.userid, comments.creationdate FROM comments"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        time = result[3]
        if time < start_time:
            set_before.add(result[2])
        if time > start_time and time < end_time:
            set_during.add(result[2])
        if time > end_time:
            set_after.add(result[2])
        
    print "The number of before/during/after learners is: " + str(len(set_before)) + "\t" + str(len(set_during)) + "\t" + str(len(set_after))
    
    sql_query = "SELECT comments.id, comments.postid, comments.userid, comments.creationdate FROM comments"
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        time = result[3]
        if time < start_time:
            set_before.add(result[1])
        if time > start_time and time < end_time:
            set_during.add(result[1])
        if time > end_time:
            set_after.add(result[1])
        
    print "The number of before/during/after questions is: " + str(len(set_before)) + "\t" + str(len(set_during)) + "\t" + str(len(set_after))
    '''
    
def Test():
    
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='StackOverflow')
    cursor = connection.cursor()
    
    format="%Y-%m-%d %H:%M:%S"
    start_time = "2014-10-14 07:00:00"
    start_time = datetime.datetime.strptime(start_time,format)
    end_time = "2014-12-31 23:59:00"
    end_time = datetime.datetime.strptime(end_time,format)
    
    sql_query = "SELECT questions.id, questions.owneruserid, questions.creationdate FROM questions"
    
    set_before = set()
    set_during = set()
    set_after = set()
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    for result in results:
        time = result[2]
        if time < start_time:
            set_before.add(result[0])
        if time > start_time and time < end_time:
            set_during.add(result[0])
        if time > end_time:
            set_after.add(result[0])
    
    print len(set_before)
    print len(set_during)
    print len(set_after)
    
    

############################################################
# CommentsQueryExecutor()

# path = "/Volumes/NETAC/StackOverflow/fp_matched_learners.txt"
# EdXQueryExecutor(path)

Test()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
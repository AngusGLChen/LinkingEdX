'''
Created on Feb 5, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, json, mysql.connector, re, string, time
from Functions.CommonFunctions import ReadEdX
from lxml import etree
from happyfuntokenizing import *
import csv


happyemoticons = [":-)", ":)", ":o)", ":]", ":3", ":c)", ":>", "=]", "8)", "=)", ":}", ":^)", ":-D", ":D", "8-D", "8D", "x-D", "xD", "X-D", "XD", "=-D", "=D","=-3", "=3", "B^D", ":-)", ";-)", ";)", "*-)", "*)", ";-]", ";]", ";D", ";^)", ":-,"]
sademoticons = [">:[", ":-(", ":(", ":-c", ":c", ":-<", ":<", ":-[", ":[", ":{", ":-||", ":@", ">:(", "'-(", ":'(", ">:O", ":-O", ":O"]    
codetext = ["<code>"]
    
def SelectCommentData(web_path):
     
    # 1. Read platform ids data
    platform_id_path =  web_path + "/platform_ids"
    platform_id_file = open(platform_id_path, "r")
    platform_ids_map = json.loads(platform_id_file.read())
    platform_id_file.close()
    
    platform = "stackoverflow.com"
    learner_id_set = platform_ids_map[platform]
    
    # 2.3 Comments
    comment_path = web_path + "201509/" + platform + "/Comments.xml"
    context = etree.iterparse(comment_path, events=('end',), tag='row')
        
    numbatch = 0
    counter = 0
    MAXINQUERY = 100000
        
    start_time = time.time()
    
    print "... START TIME at:" + str(start_time)

    tok = Tokenizer(preserve_case=False)
    
    # Output
    output_path = web_path + "answers_filter_0"
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    
    for event, elem in context:
            
        counter+=1
        
        comment = ( elem.get("Id"),   #"Id": 
                    elem.get("PostId") if elem.get("PostId") else None, 
                    elem.get("Score") if elem.get("Score") else None, 
                    elem.get("Text") if elem.get("Text") else None, 
                    elem.get("CreationDate") if elem.get("CreationDate") else None,                                          
                    elem.get("UserDisplayName") if elem.get("UserDisplayName") else None,
                    elem.get("UserId") if elem.get("UserId") else None
        )
        
        
        if comment[6] in learner_id_set:
            writer.writerow(comment)
            

        del comment

        if(counter == MAXINQUERY or elem.getnext() == False):
            numbatch+=1
            counter = 0
            #print counter
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)
            
        
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    output_file.close()
        
        

            
            


########################
course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/stackexchange/"
SelectCommentData(web_path)
print "Finished."





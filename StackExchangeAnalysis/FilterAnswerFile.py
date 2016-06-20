'''
Created on Feb 5, 2016

@author: Angus
'''

import os, json, mysql.connector, re, string, time
from Functions.CommonFunctions import ReadEdX
from lxml import etree
from happyfuntokenizing import *
import csv


happyemoticons = [":-)", ":)", ":o)", ":]", ":3", ":c)", ":>", "=]", "8)", "=)", ":}", ":^)", ":-D", ":D", "8-D", "8D", "x-D", "xD", "X-D", "XD", "=-D", "=D","=-3", "=3", "B^D", ":-)", ";-)", ";)", "*-)", "*)", ";-]", ";]", ";D", ";^)", ":-,"]
sademoticons = [">:[", ":-(", ":(", ":-c", ":c", ":-<", ":<", ":-[", ":[", ":{", ":-||", ":@", ">:(", "'-(", ":'(", ">:O", ":-O", ":O"]    
codetext = ["<code>"]
    
def SelectAnswerData(web_path):
     
    # 1. Read platform ids data
    platform_id_path =  web_path + "/platform_ids"
    platform_id_file = open(platform_id_path, "r")
    platform_ids_map = json.loads(platform_id_file.read())
    platform_id_file.close()
    
    platform = "stackoverflow.com"
    learner_id_set = platform_ids_map[platform]
    
    # 2.3 Answers
    answer_path = web_path + "201509/" + platform + "/Posts.xml"
    context = etree.iterparse(answer_path, events=('end',), tag='row')
        
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
        
        if(counter % MAXINQUERY == 0 or elem.getnext() == False):
            numbatch+=1
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)
        
        if numbatch < 400 or numbatch > 900:
            elem.clear()
            continue
        
        if(elem.get("PostTypeId") != "2"):
            elem.clear()
            continue
            
        stripped = ""
        tags= ""
        tagnumber = 0
        
        bodylen= 0
        bhemo= 0
        bsemo= 0 
        bupper= 0 
        bpunctu = 0
        bcode = False
        
        titlelen= 0
        themo= 0
        tsemo= 0
        tupper= 0
        tpunctu = 0
        tcode = False
         
        tagsintitle = 0
        tagsinbody = 0
            
        answer = (  elem.get("Id"), #"Id": 
                    elem.get("ParentId") if elem.get("ParentId") else None, #"acceptedanswer": 
                    elem.get("CreationDate"), #"CreationDate": 
                    None, #"ClosedDate":                     
                    True, #"isclosed":                     
                    None, #"score": 
                    None, #"ViewCount":                     
                    None,
                    elem.get("OwnerUserId") if elem.get("OwnerUserId") else None, #"OwnerUserId":
                    None, #"OwnerDisplayName"
                    None, #"Location": 
                    None, #"LastEditorUserId": 
                    None, #"LastEditorDisplayName"                    
                    None, #"LastEditDate": 
                    None, #"LastActivityDate": 
                    tags,
                    tagnumber,
                    None, #"AnswerCount": 
                    None, #"CommentCount": 
                    None, #"AnswerCount":                     
                    bodylen, 
                    bhemo, 
                    bsemo, 
                    bupper, 
                    bpunctu, 
                    bcode,
                    titlelen, 
                    themo, 
                    tsemo, 
                    tupper, 
                    tpunctu, 
                    tagsintitle, 
                    tagsinbody,
                    tcode
            )

        if answer[8] in learner_id_set:
            writer.writerow(answer)

        del answer
        
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    output_file.close()
        
        

            
            


########################
course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/stackexchange/"
SelectAnswerData(web_path)
print "Finished."





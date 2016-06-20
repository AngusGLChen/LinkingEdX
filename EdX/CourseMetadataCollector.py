'''
Created on Dec 18, 2015

@author: Angus
'''

import os
import json
import time,datetime

def CollectCourseMetadata(path):
    
    folders = os.listdir(path)
    
    email_set = set()
    
    course_map = {}
    course_email_map = {}
    email_id_map = {}
    email_username_map = {}
    id_name_map = {}
    
    id_certification_map = {}
    id_certification_set = set()
    
    format="%Y-%m-%d %H:%M:%S"
    
    for folder in folders:
        
        if folder in ["EconSec101x-1T2015", "block-v1:DelftX+TXT1x+3T2015+type@course+block@course"]:
            continue
        
        course_path = path + folder + "/"
        
        if not os.path.isdir(course_path):
            continue
        
        files = os.listdir(course_path)
        
        course_id = ""
        
        # Extract course metadata
        course_mark = False
        for file in files:
            if "course_structure" in file:
                course_mark = True
                fp = open(course_path + file, "r")     
                lines = fp.readlines()
                jsonLine = ""   
                for line in lines:                
                    line = line.replace("\n", "")
                    jsonLine += line
                    
                course_name = ""
                course_start_time = ""
                course_end_time = ""

                jsonObject = json.loads(jsonLine)
                for record in jsonObject:
                    if jsonObject[record]["category"] == "course":
                        course_id = record
                        if "display_name" in jsonObject[record]["metadata"]:
                            course_name = jsonObject[record]["metadata"]["display_name"]
                        if "start" in jsonObject[record]["metadata"]:
                            course_start_time = jsonObject[record]["metadata"]["start"][0:19]
                            course_start_time = course_start_time.replace("T", " ")
                            course_start_time = datetime.datetime.strptime(course_start_time,format)
                        if "end" in jsonObject[record]["metadata"]:
                            course_end_time = jsonObject[record]["metadata"]["end"][0:19]
                            course_end_time = course_end_time.replace("T", " ")
                            course_end_time = datetime.datetime.strptime(course_end_time,format)
                        
                        print course_id
                        
                        if "i4x://DelftX/" in course_id:
                            course_id = course_id.replace("i4x://DelftX/", "")
                        if "/course/" in course_id:
                            course_id = course_id.replace("/course/", "/")
                            
                        # print course_id + "\t" + course_name + "\t" + str(course_start_time) + "\t" + str(course_end_time)
                        # print
                        
                        course_map[course_id] = {"course_name":course_name, "course_start_time":course_start_time, "course_end_time":course_end_time}
        
        if not course_mark:
            print "Course\tmetadata\t" + folder + "\tmissing."
        
        # Extract number of enrolled learners 
        register_mark = False
        
        for file in files:
            if "auth_user-" in file:
                register_mark = True
                fp = open(course_path + file, "r")     
                fp.readline()
                lines = fp.readlines()
                        
                for line in lines:
                    record = line.split("\t")
                    id = record[0]
                    user_name = record[1]
                    email = record[4]
                    
                    #if "'" in email:
                    #    email = email.replace("'", "\\'")
                    
                    if not course_id in course_email_map.keys():
                        course_email_map[course_id] = set()
                    course_email_map[course_id].add(email)
                    
                    email_id_map[email] = id
                    email_username_map[email] = user_name
                    
                    email_set.add(email)
                    
        if not register_mark:
            print "Course\tregister\t" + folder + "\tmissing."
        
        # Extract name of learners
        for file in files:
            if "auth_userprofile" in file:
                fp = open(course_path + file, "rb")
                content = fp.read().replace('\r\\n', '')
                lines = content.split("\n")
                                
                for i in range(1, len(lines)):
                    line = lines[i]
                    if line != "":
                        record = line.split("\t")
                        
                        id = record[1]
                        name = record[2]
                        
                        id_name_map[id] = name
                        
        # Extract certification
        for file in files:       
            if "certificates_generatedcertificate" in file:
                fp = open(course_path + file, "r")
                fp.readline()
                lines = fp.readlines()
                
                for line in lines:
                    record = line.split("\t")
                    global_user_id = record[1]
                    final_grade = record[3]
                    enrollment_mode = record[14].replace("\n", "")
                    certificate_status = record[7]                         
                    
                    if global_user_id not in id_certification_set:
                        id_certification_set.add(global_user_id)
                        id_certification_map[global_user_id] = {}
                        
                    id_certification_map[global_user_id][course_id] = certificate_status
                                  
    print "----------------------------------------------------"
    print "# non-duplicated learners is:\t" + str(len(email_set))
            
    print "----------------------------------------------------"
    sorted_course_map = sorted(course_map.items(), key=lambda d:d[1]["course_start_time"])
    for record in sorted_course_map:
        # print record[0] + "\t" + record[1]["course_name"] + "\t" + str(record[1]["course_start_time"]) + "\t" + str(record[1]["course_end_time"]) + "\t" + str(len(course_email_map[record[0]]))
        print record[0] + "\t" + record[1]["course_name"]
        # print course + "\t" + str(len(course_user_map[course]))
        
    print "----------------------------------------------------" 
        
    # To output all course-email pair

    output_path = path + "course_email_list"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output = open(output_path, "w")
    
    for course in course_email_map.keys():
        for email in course_email_map[course]:
            id = email_id_map[email]
            
            certificate_status = "notpassing"
            if id in id_certification_set:
                if course in id_certification_map[id].keys():
                    certificate_status = id_certification_map[id][course]
            
            
            
            output.write(str(course) + "\t" + str(email) + "\t" + certificate_status + "\t" + str(email_username_map[email]) + "\t" + str(id_name_map[id]) + "\n")
            #if id_name_map[email_id_map[email]] == "":
            #    print "Empty"
    
    output.close()
    

####################################################
path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
CollectCourseMetadata(path)
print "Finished."

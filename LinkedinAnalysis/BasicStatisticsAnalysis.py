'''
Created on Feb 1, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, nltk, json
import numpy
from lxml import html


def BasicJobTitleAnalysis(course_meta_path, web_path):
    
    # Read EdX learners
    course_leaner_map = {}
    course_learner_set = set()
    
    edx_path = course_meta_path + "course_email_list"
    edx_file = open(edx_path, "r")
    lines = edx_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        course = array[0]
        email = array[1]
        certificate = array[2]
        
        if course not in course_leaner_map.keys():
            course_leaner_map[course] = {}
            
        course_leaner_map[course][email] = certificate
        
        course_learner_set.add(email)
        
    edx_file.close()
    
    # Search matchers
    matcher_set = set()
    for learner in course_learner_set:
        linkedin_path = web_path + learner
        if os.path.exists(linkedin_path):
            matcher_set.add(learner)
    print "# matchers is:\t" + str(len(matcher_set))
    
    
    job_array = []
    num_zero = 0
    num_non_zero = 0
    num_title_terms = 0
    
    for learner in matcher_set:
        
        num_non_zero += 1
        
        linkedin_path = web_path + learner
        linkedin_file = open(linkedin_path, "r")
        
        page_tree = html.fromstring(linkedin_file.read()) 
        job_title = page_tree.xpath('//p[@class="headline title"]/text()')
        if len(job_title) != 0:
            job_title = job_title[0]
            
            tokens = nltk.word_tokenize(job_title)
            pos_tags = nltk.pos_tag(tokens)
            
            num_title_terms += len(tokens)
            
            sub_job_tile = ""
            
            for pos_tag in pos_tags:
                word = pos_tag[0]                
                label = pos_tag[1]
                
                if "NN" in label:
                    sub_job_tile += word + " "
                else:
                    if sub_job_tile != "":
                        job_array.append(sub_job_tile)
                        sub_job_tile = ""
        else:
            num_zero += 1
    
    print "# empty job title is:\t" + str(num_zero)
    
    #print "# job titles is:\t" + str(len(job_array))
    avg_title_terms = float(num_title_terms) / num_non_zero
    print "Avg. title terms is:\t" + str(avg_title_terms)   
    
def BasicSkillAnalysis(course_meta_path, web_path):
    
    # Read data file
    data_path = "/Volumes/NETAC/LinkingEdX/linkedin/extracted_data"
    data_file = open(data_path, "r")
    data_map = json.loads(data_file.read())
    data_file.close()
    
    matcher_set = set()
    for learner in data_map.keys():
        matcher_set.add(learner)
        
    print "# matchers is:\t" + str(len(matcher_set))
        
    num_zero = 0
    num_non_zero = 0
    num_skills = 0
    
    for learner in matcher_set:
        attributes = data_map[learner]["skills"]
        
        if len(attributes) == 0:
            num_zero += 1
        else:
            num_non_zero += 1
            num_skills += len(attributes)
            
    avg_num_skills = float(num_skills) / num_non_zero
    
    print num_non_zero
    print avg_num_skills
    
    











course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/linkedin/download/"
#BasicJobTitleAnalysis(course_meta_path, web_path)
BasicSkillAnalysis(course_meta_path, web_path)
print "Finished."
'''
Created on Feb 1, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, nltk
import numpy
from lxml import html
from sklearn.feature_extraction.text import CountVectorizer 

def JobDistributionAnalysis(course_code, course_meta_path, web_path):
    
    # Read EdX learners
    course_leaner_map = {}
    
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
        
    edx_file.close()
    
    # Search matchers
    matcher_set = set()
    course_learner_set = course_leaner_map[course_code]
    for learner in course_learner_set:
        linkedin_path = web_path + learner
        if os.path.exists(linkedin_path):
            if course_leaner_map[course_code][learner] != "downloadable":
                matcher_set.add(learner)
    print "# matchers is:\t" + str(len(matcher_set))
    
    
    job_array = []    
    for learner in matcher_set:
        linkedin_path = web_path + learner
        linkedin_file = open(linkedin_path, "r")
        
        page_tree = html.fromstring(linkedin_file.read()) 
        job_title = page_tree.xpath('//p[@class="headline title"]/text()')
        if len(job_title) != 0:
            job_title = job_title[0]
            
            tokens = nltk.word_tokenize(job_title)
            pos_tags = nltk.pos_tag(tokens)
            
            sub_job_tile = ""
            
            for pos_tag in pos_tags:
                word = pos_tag[0]                
                label = pos_tag[1]
                
                if "NN" in label:
                    sub_job_tile += word + " "
                else:
                    if sub_job_tile != "":
                        job_array.append(sub_job_tile)
                        # print job_title + "\t" + sub_job_tile
                        sub_job_tile = ""    
            
    print "# job titles is:\t" + str(len(job_array))
       
    vectorizer = CountVectorizer(ngram_range=(2,2), max_features=30)
    X = vectorizer.fit_transform(job_array)
    
    tuples = zip(vectorizer.get_feature_names(), numpy.asarray(X.sum(axis=0)).ravel())
    for tuple in tuples:
        word = tuple[0]
        frequency = tuple[1]
        
        print word.replace(" ", "_") + ":" + str(frequency)
        
    
    
















course_code = "ET3034TUx/2013_Fall"
course_code = "FP101x/3T2014"
course_code = "CTB3365x/2013_Fall"
course_code = "ET.3034TU/3T2014"
course_code = "Frame101x/1T2015"

course_code = "TPM1x/3T2014"
course_code = "Calc001x/2T2015"
course_code = "block-v1:DelftX+ET3034x+3T2015+type@course+block@course"
course_code = "NGI101x/1T2014"
course_code = "AE1110x/1T2014"

course_code = "AE.1110x/3T2014"


course_code = "EX101x/1T2015"
course_code = "DDA691x/3T2014"
course_code = "RI101x/3T2014"

course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/linkedin/download/"
JobDistributionAnalysis(course_code, course_meta_path, web_path)
print "Finished."
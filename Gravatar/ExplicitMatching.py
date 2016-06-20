'''
Created on Dec 24, 2015

@author: Angus
'''

import os, urllib, urllib2, hashlib, time
from Functions.CommonFunctions import ReadEdX



def MatchLearnersExplicitly(edx_path, web_path):
    
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    explicit_matching_results_map = {}
    explicit_matching_results_set = set()
    
    # Read explicit matching results
    explicit_matching_results_path = web_path + "fuzzy_matching"
    num_matched_learners = 0
    
    if os.path.exists(explicit_matching_results_path):
        explicit_matching_results_file = open(explicit_matching_results_path, "r+")
        lines = explicit_matching_results_file.readlines()
        for i in range(len(lines)-5):
            line = lines[i].replace("\r\n", "").replace("\n", "")
            array = line.split("\t")
            learner = array[0]
            gravatar_url = array[1]
            explicit_matching_results_map[learner] = gravatar_url
            explicit_matching_results_set.add(learner)        
        
        for learner in explicit_matching_results_map.keys():
            if explicit_matching_results_map[learner] != "":
                num_matched_learners += 1  
        print "# previous matched learners is:\t" + str(num_matched_learners) + "\n"
        
    else:
        explicit_matching_results_file = open(explicit_matching_results_path, "w")
        
    count = 0
    current_time = time.time()

    # Set your variables here
    size = 40
    default = 404
    
    for email in edx_learners_set:
        
        count += 1
        
        if learner in explicit_matching_results_set:
            continue        
        
        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time

        # construct the url
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':str(default), 's':str(size)})

        try:
            pic = urllib2.urlopen(gravatar_url)
            num_matched_learners += 1
            explicit_matching_results_map[email] = {"courses":edx_learners_map[email]["courses"]}
            
            explicit_matching_results_file.write(learner + "\t" + str(','.join(explicit_matching_results_map[email]["courses"])) + "\n")
        
        except Exception as e:
            explicit_matching_results_map[email] = ""
            explicit_matching_results_file.write(learner + "\t" + "" + "\n")
            print e
            
    explicit_matching_results_file.close()


####################################################
edx_path = "/Volumes/NETAC/LinkingEdX/course_metadata/course_email_list"
web_path = "/Volumes/NETAC/LinkingEdX/gravatar/"
MatchLearnersExplicitly(edx_path, web_path)
print "Finished."




























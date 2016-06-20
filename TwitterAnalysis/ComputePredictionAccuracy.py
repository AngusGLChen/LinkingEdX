'''
Created on Apr 11, 2016

@author: Angus
'''

import os, scipy.stats
from Functions.CommonFunctions import ReadEdX
import matplotlib.pyplot as plt

def ComputeAccuracy(course_path, prediction_path):
    
    # Read EdX learners
    edx_path = course_path + "course_email_list"
    edx_learners_set, edx_learners_map =ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)
            
    learner_demographic_map = {}
    learner_email_id_map = {}
    learner_id_set = set()
    
    birth_year_array = []
    
    outlier_set = set()
            
    # Read Demographics
    for course in course_learners_map.keys():
        
        #print course
        
        course = course.replace("/", "-")
        
        mooc_path = course_path + course + "/"
        files = os.listdir(mooc_path)
        
        for file in files:            
            if "auth_user-" in file:
                fp = open(mooc_path + file, "r")
                fp.readline()
                lines = fp.readlines()
                        
                for line in lines:
                    record = line.split("\t")
                    id = record[0]                  
                    email = record[4]                    
                    if "'" in email:
                        email = email.replace("'", "\\'")                    
                    
                    if email in edx_learners_set:
                        learner_email_id_map[id] = email
                        learner_id_set.add(id)
                        
                        learner_demographic_map[email] = {}
                        learner_demographic_map[email]["age"] = ""
                        learner_demographic_map[email]["gender"] = ""
                
        for file in files:
            
            if "auth_userprofile" in file:
                fp = open(mooc_path + file, "r")
                fp.readline()
                lines = fp.readlines()
            
                for line in lines:
                    record = line.split("\t")
                    global_user_id = record[1]
                    gender = record[7]
                    year_of_birth = record[9]
                    
                    if global_user_id in learner_id_set:
                        email = learner_email_id_map[global_user_id]
                        
                        if gender in ["f", "m"]:
                            learner_demographic_map[email]["gender"] = gender
                            
                        if year_of_birth != "NULL":
                                                       
                            if int(year_of_birth) < 1940 or int(year_of_birth) > 2005:
                                outlier_set.add(global_user_id)
                                # continue
                            
                            age = 2016 - int(year_of_birth)
                            learner_demographic_map[email]["age"] = age
                            
                            birth_year_array.append(2016 - int(year_of_birth))
    
    print "# outliers is:\t" + str(len(outlier_set))
    print len(birth_year_array)
                            
    plt.hist(birth_year_array)
    plt.show()                    
                    
    # Gender accuracy
    
    gender_sum = 0
    gender_correct = 0
    
    course_gender_map = {}
    
    gender_path = prediction_path + "users.gender"
    gender_file = open(gender_path, "r")
    gender_file.readline()
    lines = gender_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(" ")

        email = array[0]
        course = array[1]
        predicted_gender = array[5]
        
        if course == "block-v1:DelftX+TXT1x+3T2015+type@course+block@course":
            continue
        
        if email not in edx_learners_set:
            continue
        
        if learner_demographic_map[email]["gender"] != "":
            
            if course not in course_gender_map.keys():
                course_gender_map[course] = {}
                course_gender_map[course]["sum"] = 0
                course_gender_map[course]["correct"] = 0
            
            gender_sum += 1
            course_gender_map[course]["sum"] += 1
            
            if (learner_demographic_map[email]["gender"] == "f" and predicted_gender == "female") or  (learner_demographic_map[email]["gender"] == "m" and predicted_gender == "male"):
                gender_correct += 1
                course_gender_map[course]["correct"] += 1
                
    print "Gender prediction..."
    print str(gender_correct) + "\t" + str(gender_sum) + "\t" + str(round(gender_correct/float(gender_sum)*100, 2))
        
    for course in course_gender_map.keys():
        print course + "\t" + str(course_gender_map[course]["correct"]) + "\t" + str(course_gender_map[course]["sum"]) + "\t" + str(round(course_gender_map[course]["correct"]/float(course_gender_map[course]["sum"]), 4))
      
    
    # Age accuracy - Version 1
    '''
    actual_age_array = []
    predicted_age_array = []
    
    course_age_map = {}
    
    age_path = prediction_path + "users.age"
    age_file = open(age_path, "r")
    age_file.readline()
    lines = age_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(" ")

        email = array[0]
        course = array[1]
        predicted_age = float(array[4])
        
        if course == "block-v1:DelftX+TXT1x+3T2015+type@course+block@course":
            continue
        
        if email not in edx_learners_set:
            continue
        
        if learner_demographic_map[email]["age"] != "":
            actual_age = learner_demographic_map[email]["age"]
            
            if course not in course_age_map.keys():
                course_age_map[course] = {}
                course_age_map[course]["actual_age_array"] = []
                course_age_map[course]["predicted_age_array"] = []
            
            actual_age_array.append(actual_age)
            predicted_age_array.append(predicted_age)
            
            course_age_map[course]["actual_age_array"].append(actual_age)
            course_age_map[course]["predicted_age_array"].append(predicted_age)
    
    mae = 0
           
    for i in range(len(actual_age_array)):
        mae += abs(actual_age_array[i] - predicted_age_array[i])
    mae = round(float(mae)/len(actual_age_array), 2)
    
    
    print "\nage prediction..."
    print len(actual_age_array)
    print "Mean absolute error is:\t" + str(mae)
    print scipy.stats.pearsonr(actual_age_array, predicted_age_array)
    
    print
    for course in course_age_map.keys():
        course_mae = 0
        for i in range(len(course_age_map[course]["actual_age_array"])):
            course_mae += abs(course_age_map[course]["actual_age_array"][i] - course_age_map[course]["predicted_age_array"][i])
        course_mae = round(float(course_mae)/len(course_age_map[course]["actual_age_array"]), 2)
        
        print course + "\t" + str(course_mae) + "\t" + str(scipy.stats.pearsonr(course_age_map[course]["actual_age_array"], course_age_map[course]["predicted_age_array"])[0])
     
    '''       
    # Age accuracy - Version 2
    
    age_sum = 0
    age_correct = 0
        
    course_age_map = {}
    
    # Test
    survey_actual_age_array = []
    survey_predicted_age_array = []
    
    age_path = prediction_path + "users.age"
    age_file = open(age_path, "r")
    age_file.readline()
    lines = age_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        array = line.split(" ")

        email = array[0]
        course = array[1]
        predicted_age = float(array[4])
        
        if course == "block-v1:DelftX+TXT1x+3T2015+type@course+block@course":
            continue
        
        if email not in edx_learners_set:
            continue
        
        if learner_demographic_map[email]["age"] != "":
            actual_age = learner_demographic_map[email]["age"]
            
            if course not in course_age_map.keys():
                course_age_map[course] = {}
                course_age_map[course]["sum"] = 0
                course_age_map[course]["correct"] = 0
                
            age_sum += 1
            course_age_map[course]["sum"] += 1
            
            #if (actual_age < 20 and predicted_age < 20) or ((actual_age >= 20 and actual_age < 25) and (predicted_age >= 20 and predicted_age < 25)) or ((actual_age >= 25 and actual_age < 30) and (predicted_age >= 25 and predicted_age < 30)) or ((actual_age >= 30 and actual_age < 35) and (predicted_age >= 30 and predicted_age < 35)) or ((actual_age >= 35 and actual_age < 40) and (predicted_age >= 35 and predicted_age < 40)) or ((actual_age >= 40 and actual_age < 45) and (predicted_age >= 40 and predicted_age < 45)) or ((actual_age >= 45 and actual_age < 50) and (predicted_age >= 45 and predicted_age < 50)) or (actual_age >= 50 and predicted_age >= 50):
            if (actual_age < 20 and predicted_age < 20) or ((actual_age >= 20 and actual_age < 30) and (predicted_age >= 20 and predicted_age < 30)) or ((actual_age >= 30 and actual_age < 40) and (predicted_age >= 30 and predicted_age < 40)) or ((actual_age >= 40 and actual_age < 50) and (predicted_age >= 40 and predicted_age < 50)) or (actual_age >= 50 and predicted_age >= 50):
                age_correct += 1
                course_age_map[course]["correct"] += 1
                
            if predicted_age < 0:
                predicted_age = 0
            if predicted_age > 100:
                predicted_age = 100
                
            survey_actual_age_array.append(actual_age)
            survey_predicted_age_array.append(predicted_age)
            

    print "\nage prediction..."
    print str(age_correct) + "\t" + str(age_sum) + "\t" + str(round(float(age_correct)/age_sum, 4))
    
    print
    for course in course_age_map.keys():
        # print course + "\t" + str(course_age_map[course]["correct"]) + "\t" + str(course_age_map[course]["sum"]) + "\t" + str(round(float(course_age_map[course]["correct"])/course_age_map[course]["sum"], 4))
        print str(round(float(course_age_map[course]["correct"])/course_age_map[course]["sum"], 4))
        
    
    plt.hist(survey_actual_age_array)
    plt.show()
    
    plt.hist(survey_predicted_age_array)    
    plt.show()
    
    
    
            
            
            
            
            
            
            
                
            
    
    
    
    


course_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
prediction_path = "/Volumes/NETAC/LinkingEdX/twitter/WEBSCIENCE2016/"
ComputeAccuracy(course_path, prediction_path)
print "Finished."
    
    

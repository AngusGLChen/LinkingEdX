'''
Created on Apr 12, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, json, random, scipy.stats
from happierfuntokenizing import Tokenizer
from Functions.CommonFunctions import ReadEdX
import matplotlib.pyplot as plt

from sklearn.linear_model import Ridge
import nltk


def GenerateData(course_path, web_path):
    
    # Read EdX learners
    edx_path = course_path + "course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)
            
    learner_demographic_map = {}
    learner_email_id_map = {}
    learner_id_set = set()    
    
    outlier_set = set()
            
    # Read Demographics
    for course in course_learners_map.keys():
                
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
                                                       
                            if int(year_of_birth) < 1950 or int(year_of_birth) > 2005:
                                outlier_set.add(global_user_id)
                                continue
                            
                            age = 2016 - int(year_of_birth)
                            learner_demographic_map[email]["age"] = age
        
    tok = Tokenizer(preserve_case=False)
        
    learner_data_map = {}        
    
    word_learner_count_map = {}
    word_set = set()
    
    num = 0
                            
    # Read tweets
    for learner in learner_demographic_map.keys():            
        if learner_demographic_map[learner]["age"] != "":
            
            tweet_path = web_path + learner + "/tweet"
                
            if not os.path.isfile(tweet_path):
                continue
                
            tweet_file = open(tweet_path, "r")
            lines = tweet_file.readlines()
                
            count = 0
                
            for line in lines:
                jsonObject = json.loads(line)
                if jsonObject["lang"] == "en":
                    count += 1
                        
                    if count >= 100:
                        break                   
                                        
            if count >= 100:
                
                num += 1         
                    
                individual_word_count_map = {}
                individual_word_count_set = set()
                    
                for line in lines:
                    try:
                        jsonObject = json.loads(line)
                        if jsonObject["lang"] == "en":
                            tweet = jsonObject["text"]
                            tokenized_tweet = tok.tokenize(tweet)
                                                       
                            for word in tokenized_tweet:
                                
                                
                                
                                if word not in individual_word_count_set:
                                    individual_word_count_set.add(word)
                                    individual_word_count_map[word] = 0
                                    
                                individual_word_count_map[word] += 1   
                                
                                                                
                                if word not in word_set:
                                    word_set.add(word)
                                    word_learner_count_map[word] = set()
                                    
                                word_learner_count_map[word].add(learner)                          
                                
                    except Exception as e:
                        print line
                
                learner_data_map[learner] = {}
                learner_data_map[learner]["tweet"] = individual_word_count_map
                learner_data_map[learner]["age"] = learner_demographic_map[learner]["age"]
                    
                if num % 100 == 0:
                    print num
                    
                #if num > 100:
                #    break
                    
    num_learners = len(learner_data_map)
    threshold = int(num_learners * 0.01)
    print "Threshold is:\t" + str(threshold)
    
    for learner in learner_data_map.keys():
        for word in learner_data_map[learner]["tweet"].keys():
            if learner_data_map[learner]["tweet"][word] < threshold:
                del learner_data_map[learner]["tweet"][word]
    
    updated_learner_data_map = {}
    for learner in learner_data_map.keys():
        if len(learner_data_map[learner]["tweet"]) > 0:
            updated_learner_data_map[learner] = learner_data_map[learner]
                            
    output_path = os.path.dirname(os.path.dirname(web_path)) + "/age_data_norm"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(updated_learner_data_map))
    output_file.close()



def GenerateDataNorm(course_path, web_path):
    
    # Read EdX learners
    edx_path = course_path + "course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)
            
    learner_demographic_map = {}
    learner_email_id_map = {}
    learner_id_set = set()    
    
    outlier_set = set()
            
    # Read Demographics
    for course in course_learners_map.keys():
                
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
                                                       
                            if int(year_of_birth) < 1950 or int(year_of_birth) > 2005:
                                outlier_set.add(global_user_id)
                                continue
                            
                            age = 2016 - int(year_of_birth)
                            learner_demographic_map[email]["age"] = age
        
    
        
    learner_data_map = {}        
    
    word_learner_count_map = {}
    word_set = set()
    
    num = 0
                            
    # Read tweets
    for learner in learner_demographic_map.keys():            
        if learner_demographic_map[learner]["age"] != "":
            
            tweet_path = web_path + learner + "/tweet"
                
            if not os.path.isfile(tweet_path):
                continue
            
            
                
            tweet_file = open(tweet_path, "r")
            lines = tweet_file.readlines()
                
            count = 0
                
            for line in lines:
                jsonObject = json.loads(line)
                if jsonObject["lang"] == "en":
                    count += 1
                        
                    if count >= 100:
                        break                   
                                        
            if count >= 100:
                
                num += 1
                
                print num    
                    
                individual_word_count_map = {}
                individual_word_count_set = set()
                    
                for line in lines:
                    try:
                        jsonObject = json.loads(line)
                        if jsonObject["lang"] == "en":
                            tweet = jsonObject["text"]
                            
                            tokens = nltk.word_tokenize(tweet)
                            tags = nltk.pos_tag(tokens)
                                                       
                            for tag in tags:
                                
                                if tag[1] in ["JJ", "RB", "NN", "VB"]:
                                    
                                    word = tag[0]
                                
                                    if word not in individual_word_count_set:
                                        individual_word_count_set.add(word)
                                        individual_word_count_map[word] = 0
                                    
                                    individual_word_count_map[word] += 1   
                                
                                                                
                                    if word not in word_set:
                                        word_set.add(word)
                                        word_learner_count_map[word] = set()
                                    
                                    word_learner_count_map[word].add(learner)                          
                                
                    except Exception as e:
                        print line
                
                learner_data_map[learner] = {}
                learner_data_map[learner]["tweet"] = individual_word_count_map
                learner_data_map[learner]["age"] = learner_demographic_map[learner]["age"]
                    
                if num % 100 == 0:
                    print num
                    
                #if num > 100:
                #    break
                    
    num_learners = len(learner_data_map)
    threshold = int(num_learners * 0.01)
    print "Threshold is:\t" + str(threshold)
    
    for learner in learner_data_map.keys():
        for word in learner_data_map[learner]["tweet"].keys():
            if learner_data_map[learner]["tweet"][word] < threshold:
                del learner_data_map[learner]["tweet"][word]
    
    updated_learner_data_map = {}
    for learner in learner_data_map.keys():
        if len(learner_data_map[learner]["tweet"]) > 0:
            updated_learner_data_map[learner] = learner_data_map[learner]
                            
    output_path = os.path.dirname(os.path.dirname(web_path)) + "/age_data_norm"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(updated_learner_data_map))
    output_file.close()
                            


                            

def BuildPredictionModel(course_path, web_path):
    
    '''
    # Read EdX learners
    edx_path = course_path + "course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)
            
    learner_demographic_map = {}
    learner_email_id_map = {}
    learner_id_set = set()    
    
    outlier_set = set()
            
    # Read Demographics
    for course in course_learners_map.keys():
                
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
                                                       
                            if int(year_of_birth) < 1950 or int(year_of_birth) > 2005:
                                outlier_set.add(global_user_id)
                                continue
                            
                            age = 2016 - int(year_of_birth)
                            learner_demographic_map[email]["age"] = age
    '''
                      
    # Read Tweets
    tweet_path = os.path.dirname(os.path.dirname(web_path)) + "/age_data_1"
    tweet_file = open(tweet_path, "r")    
    learner_data_map = json.loads(tweet_file.read())
    tweet_file.close()
    
    word_set = set()
    
        
    for learner in learner_data_map.keys():        
        for word in learner_data_map[learner]["tweet"]:                                   
            word_set.add(word)
        
    print "# learners is:\t" + str(len(learner_data_map))
    print "# words is:\t" + str(len(word_set))
    
    word_index_map = {}
    for word in word_set:
        word_index_map[word] = len(word_index_map)
                
    index_word_map = {}
    for word in word_index_map.keys():
        index = word_index_map[word]
        index_word_map[index] = word
    
    num_words = len(word_index_map)
    print "# words is:\t" + str(num_words)
    
    # Plot age distribution
    age_distribution_map = {}
    for i in range(5):
        age_distribution_map[i] = {}
            
    for learner in learner_data_map.keys():
        actual_age = learner_data_map[learner]["age"]
        
        if actual_age < 20:
            age_distribution_map[0][learner] = learner_data_map[learner]
             
        if actual_age < 30 and actual_age >= 20:
            age_distribution_map[1][learner] = learner_data_map[learner]
             
        if actual_age < 40 and actual_age >= 30:
            age_distribution_map[2][learner] = learner_data_map[learner]
             
        if actual_age < 50 and actual_age >= 40:
            age_distribution_map[3][learner] = learner_data_map[learner]
             
        if actual_age >= 50:
            age_distribution_map[4][learner] = learner_data_map[learner]
    
    for label in age_distribution_map.keys():
        print str(label) + "\t" + str(len(age_distribution_map[label]))
           
    traning_map = {}
    testing_map = {}
    
    error_array = []
    
    
    # Randomization
    for learner in learner_data_map.keys():
        
        randnum = random.randint(1, 10)
        
        array = [0] * num_words
        
        total_word_count = 0
        for word in learner_data_map[learner]["tweet"]:
            total_word_count += learner_data_map[learner]["tweet"][word]
        
        for word in learner_data_map[learner]["tweet"]:
            index = word_index_map[word]
            array[index] =  learner_data_map[learner]["tweet"][word] / float(total_word_count) 
        
        if randnum == 6:
            testing_map[learner] = {}
            testing_map[learner]["age"] = learner_data_map[learner]["age"]            
            testing_map[learner]["array"] = array
        else:
            traning_map[learner] = {}
            traning_map[learner]["age"] = learner_data_map[learner]["age"]  
            traning_map[learner]["array"] = array
    '''
    
    limit = 500
    
    for label in age_distribution_map.keys():
                
        if len(age_distribution_map[label]) < limit:
            for learner in age_distribution_map[label]:
                
                array = [0] * num_words
        
                total_word_count = 0
                for word in learner_data_map[learner]["tweet"]:
                    total_word_count += learner_data_map[learner]["tweet"][word]
        
                for word in learner_data_map[learner]["tweet"]:
                    index = word_index_map[word]
                    array[index] =  learner_data_map[learner]["tweet"][word] / float(total_word_count)
                
                traning_map[learner] = {}
                traning_map[learner]["age"] = learner_data_map[learner]["age"]            
                traning_map[learner]["array"] = array
        else:
            
            selected_num = 0       
            
            data_array = []
            for learner in age_distribution_map[label]:
                
                array = [0] * num_words
        
                total_word_count = 0
                for word in learner_data_map[learner]["tweet"]:
                    total_word_count += learner_data_map[learner]["tweet"][word]
        
                for word in learner_data_map[learner]["tweet"]:
                    index = word_index_map[word]
                    array[index] =  learner_data_map[learner]["tweet"][word] / float(total_word_count)                
                
                data_array.append([learner, array])
                
            while selected_num < limit:
                index = random.randint(0, len(data_array) - 1)
                
                traning_map[data_array[index][0]] = {}
                traning_map[data_array[index][0]]["age"] = learner_data_map[learner]["age"]    
                traning_map[data_array[index][0]]["array"] = data_array[index][1]
                
                selected_num += 1             
                data_array.pop(index)
            
            ################
            for record in data_array:                
                testing_map[record[0]] = {}
                testing_map[record[0]]["age"] = learner_data_map[learner]["age"]    
                testing_map[record[0]]["array"] = record[1]
            
        
            ################
            selected_num = 0
            while selected_num < limit:
                
                if len(data_array) == 0:
                    break
                
                index = random.randint(0, len(data_array) - 1)
                
                testing_map[data_array[index][0]] = {}
                testing_map[data_array[index][0]]["age"] = learner_data_map[learner]["age"]    
                testing_map[data_array[index][0]]["array"] = data_array[index][1]
                
                selected_num += 1             
                data_array.pop(index)
    '''
            
    print "Size of traning set is:\t" + str(len(traning_map))
    print "Size of testing set is:\t" + str(len(testing_map))
    
    clf = Ridge(alpha=1.0, fit_intercept=True)
    
    X = []
    Y = []
        
    for learner in traning_map.keys():
        Y.append(traning_map[learner]["age"])
        X.append(traning_map[learner]["array"])
        
    clf.fit(X, Y)
    
    
    print
    coefficient_array = clf.coef_.copy()
    
    for i in range(20):
        max = -100
        mark_index = -1
        for j in range(len(coefficient_array)):
            if coefficient_array[j] > max:
                max = coefficient_array[j]
                mark_index = j        
                word = index_word_map[j]
                
        coefficient_array[mark_index] = -1000000
        
        print str(max) + "\t" + word
    print
    
    coefficient_array = clf.coef_.copy()
    for i in range(20):
        min = 100
        mark_index = -1
        for j in range(len(coefficient_array)):
            if coefficient_array[j] < min:
                min = coefficient_array[j]
                mark_index = j        
                word = index_word_map[j]
                
        coefficient_array[mark_index] = 1000000
        
        print str(min) + "\t" + word
    print
    
    correct_num = 0
    
    actual_age_array = []
    predicted_age_array = []
    
    for learner in testing_map.keys():
        predicted_age = clf.predict([testing_map[learner]["array"]])[0]
        actual_age = testing_map[learner]["age"]
        if (actual_age < 20 and predicted_age < 20) or ((actual_age >= 20 and actual_age < 30) and (predicted_age >= 20 and predicted_age < 30)) or ((actual_age >= 30 and actual_age < 40) and (predicted_age >= 30 and predicted_age < 40)) or ((actual_age >= 40 and actual_age < 50) and (predicted_age >= 40 and predicted_age < 50)) or (actual_age >= 50 and predicted_age >= 50):
        #if abs(actual_age - predicted_age) <= 5:
            correct_num += 1
            
        actual_age_array.append(actual_age)
        predicted_age_array.append(predicted_age)
        
        error = predicted_age - actual_age
        error_array.append(error)
            
    print str(correct_num) + "\t" + str(len(testing_map)) + "\t" + str(round(correct_num/float(len(testing_map)), 4))
    
    print str(scipy.stats.pearsonr(actual_age_array, predicted_age_array))
    
    plt.hist(error_array)
    plt.show()    
    
    coefficient_map = {}
    coefficient_array = clf.coef_.copy()
    for i in range(len(coefficient_array)):
        word = index_word_map[i]
        weight = coefficient_array[i]        
        coefficient_map[word] = weight
    
    intercept = clf.intercept_   
    print "Intercept is:\t" + str(round(clf.intercept_, 2))
        
    output_path = os.path.dirname(os.path.dirname(web_path)) + "/coefficient"
    output_file = open(output_path, "w")
    output_file.write(str(intercept) + "\n")
    output_file.write(json.dumps(coefficient_map))
    output_file.close()
    

def PredictAllLearners(web_path):
    
    # Read coefficient model
    coefficient_path = web_path + "coefficient"
    coefficient_file = open(coefficient_path, "r")
    intercept = float(coefficient_file.readline())
    coefficient_map = json.loads(coefficient_file.read())
    coefficient_file.close()
    
    word_set = set()
    for word in coefficient_map.keys():
        word_set.add(word)
        
    # Output_prediction result
    output_path = web_path + "age_prediction_result"
    output_file = open(output_path, "w")
    output_file.write("learner,num_english_tweet,predicted_age\n")
    
    # Read learner_tweets file
    tweet_path = web_path + "all_tokenized_tweets"
    tweet_file = open(tweet_path, "r")
    learner_tweet_map = json.loads(tweet_file.read())
    tweet_file.close()
    
    result_array = []
    
    
    for learner in learner_tweet_map.keys():
        num_english_tweet = learner_tweet_map[learner]["num_english_tweet"]
        word_count_map = learner_tweet_map[learner]["tweet"]
        
        predicted_age = intercept
        
        total_word_count = 0
        
        for word in word_count_map.keys():
            if word in word_set:
                total_word_count += word_count_map[word]
                
        for word in word_count_map.keys():
            if word in word_set:
                weight = coefficient_map[word]
                predicted_age += weight * word_count_map[word]/float(total_word_count)
                
        output_file.write(learner + "," + str(num_english_tweet) + "," + str(predicted_age) + "\n")
        
        if num_english_tweet >= 100:
            result_array.append(predicted_age)        
    
    output_file.close()
    
    plt.hist(result_array)
                         
                            
                            
                            
course_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/twitter/download/"

#GenerateData(course_path, web_path)
#GenerateDataNorm(course_path, web_path)

#BuildPredictionModel(course_path, web_path)

web_path = "/Volumes/NETAC/LinkingEdX/twitter/"
PredictAllLearners(web_path)


print "Finished."    
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
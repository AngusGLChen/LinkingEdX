'''
Created on Jan 29, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD, PCA, RandomizedPCA
from sklearn import manifold

import matplotlib.pyplot as plt

def GatherCourseTweets(course_codes, course_meta_path, web_path):
    
    # Read EdX learners
    course_leaner_map = {}
    
    edx_path = course_meta_path + "course_email_list"
    edx_file = open(edx_path, "r")
    lines = edx_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        course = array[0]
        email = array[1]   
        if course not in course_leaner_map.keys():
            course_leaner_map[course] = set() 
        course_leaner_map[course].add(email)
    edx_file.close()
    
    for i in range(len(course_codes)):
        
        course_code = course_codes[i]
        
        course_tweet_path = os.path.dirname(os.path.dirname(web_path)) + "/" + str(course_code.replace("/", "_")) + "_tweets"
        if os.path.exists(course_tweet_path):
            continue
        
        course_code = course_codes[i]
    
        # Search matchers
        matcher_set = set()
        course_learner_set = course_leaner_map[course_code]
        for learner in course_learner_set:
            tweet_path = web_path + learner + "/tweet"
            if os.path.exists(tweet_path):
                matcher_set.add(learner)
        print "# matchers is:\t" + str(len(matcher_set))
    
        # Output tweets    
        learner_tweet_map = {}
        for learner in matcher_set:
        
            if learner not in learner_tweet_map.keys():
                learner_tweet_map[learner] = []
        
            tweet_path = web_path + learner + "/tweet"
            tweet_file = open(tweet_path, "r")
            lines = tweet_file.readlines()
            for line in lines:
                jsonObject = json.loads(line)
                if jsonObject["lang"] == "en":
                    tweet = jsonObject["text"]
                    learner_tweet_map[learner].append(tweet)
    
    
        course_tweet_file = open(course_tweet_path, "w")
        course_tweet_file.write(json.dumps(learner_tweet_map))
        course_tweet_file.close()

def TSNE(course_codes, web_path):
    
    color_array = ["g", "r", "y"]
    
    # 1. Read course_tweet_file
    tweets_array = []
    data_point_color_array = []
    
    for i in range(len(course_codes)):
        
        course_code = course_codes[i]
                
        course_tweet_path = os.path.dirname(os.path.dirname(web_path)) + "/" + str(course_code.replace("/", "_")) + "_tweets"
        course_tweet_file = open(course_tweet_path, "r")
        learner_tweet_map = json.loads(course_tweet_file.read())
        course_tweet_file.close()
    
        
        for learner in learner_tweet_map.keys():
            tweets = ""
            
            if len(learner_tweet_map[learner]) < 50:
                continue
            
            for tweet in learner_tweet_map[learner]:
                tweets += tweet + "\t"
            tweets_array.append(tweets)
            data_point_color_array.append(color_array[i])
            
        # if len(tweets_array) > 1000:
        #     break
        
        print course_code + "\tThe length of tweets_array is:\t" + str(len(tweets_array))
    
    # 2. Build TF-IDF / TF vector and conduct T-SNE
    # vectors = TfidfVectorizer(stop_words='english', min_df=20).fit_transform(tweets_array)
    vectors = CountVectorizer(stop_words='english', min_df=1).fit_transform(tweets_array)
    
    print "# features is:\t" + str(vectors.shape[0]) + "\t" + str(vectors.shape[1]) 
    
    # SVD-truncated
    X_reduced = TruncatedSVD(n_components=50, random_state=0).fit_transform(vectors)
    
    # PCA
    # X_reduced = RandomizedPCA(n_components=50).fit_transform(vectors.toarray())
    
    X_embedded = manifold.TSNE(n_components=2).fit_transform(X_reduced)
    
    plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c=data_point_color_array, marker="x")
    plt.show()




#"EX101x/1T2015"
#"Calc001x/2T2015"
#"FP101x/3T2014", "ET3034TUx/2013_Fall", 

course_codes = ["EX101x/1T2015", "DDA691x/3T2014"]

course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/twitter/download/"
#GatherCourseTweets(course_codes, course_meta_path, web_path)
TSNE(course_codes, web_path)
print "Finished."
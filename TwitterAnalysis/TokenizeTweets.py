'''
Created on Apr 14, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os, json

from happierfuntokenizing import Tokenizer

def TokenizeTweets(data_path):
    
    learner_tweet_map = {}
        
    tok = Tokenizer(preserve_case=False)
    
    learners = os.listdir(data_path)
    for learner in learners:
        
        tweet_path = data_path + learner + "/tweet"
        
        if os.path.isfile(tweet_path):
            
            tweet_file = open(tweet_path, "r")
            lines = tweet_file.readlines()          
                            
            individual_word_count_map = {}
            individual_word_count_set = set()
            
            num_english_tweet = 0
                
            for line in lines:
                try:
                    jsonObject = json.loads(line)
                    if jsonObject["lang"] == "en":
                        tweet = jsonObject["text"]
                        tokenized_tweet = tok.tokenize(tweet)
                        
                        num_english_tweet += 1
                                                       
                        for word in tokenized_tweet:
                                
                            if word not in individual_word_count_set:
                                individual_word_count_set.add(word)
                                individual_word_count_map[word] = 0
                                    
                            individual_word_count_map[word] += 1
                except Exception as e:
                    print line
            
            learner_tweet_map[learner] = {}
            learner_tweet_map[learner]["tweet"] = individual_word_count_map
            learner_tweet_map[learner]["num_english_tweet"] = num_english_tweet
            
            #if num > 30:
            #    break
            
            if len(learner_tweet_map) % 100 == 0:
                print len(learner_tweet_map)
            
    output_path = os.path.dirname(os.path.dirname(data_path)) + "all_tokenized_tweets"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(learner_tweet_map))
    output_file.close()
    
                    
    
    
    
    
data_path = "/Volumes/NETAC/LinkingEdX/twitter/download/"
TokenizeTweets(data_path)
print "Finished."
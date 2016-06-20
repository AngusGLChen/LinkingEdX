'''
Created on Jan 7, 2016

@author: Angus
'''

import sys
import shutil
reload(sys)
sys.setdefaultencoding("utf-8")

import json, os, time, tweepy

from Functions.CommonFunctions import ReadEdX

def DownloadPage(path):
    
    matcher_login_map = {}
    matcher_set = set()
    
    # Read EdX learners
    edx_path = path + "/course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    # Gather the unmatched twitter learners
    for learner in matching_results_map.keys():
        if "twitter" in matching_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:
                for link_record in matching_results_map[learner]["matched_platforms"]:
                    url = link_record["url"].replace("https://twitter.com/","").replace("http://twitter.com/", "")
                    platform = link_record["platform"]
                    
                    if platform == "twitter":
                        matcher_login_map[learner] = url
                        matcher_set.add(learner)
        
    print "# matched learners is:\t" + str(len(matcher_login_map))

    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "/twitter/fuzzy_matching"
    
    fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
    lines = fuzzy_matching_results_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        array = line.split("\t")
        
        learner = array[0]
        login = array[1]
        
        if learner in edx_learners_set and login != "":
            matcher_login_map[learner] = login
            matcher_set.add(learner)

    print "# matched learners is:\t" + str(len(matcher_login_map)) + "\n"
    
    # Read downloaded learners
    downloaded_matcher_set = set()
    download_path = path + "/twitter/download/"
    files = os.listdir(download_path)
    for file in files:
        if file != ".DS_Store":
            downloaded_matcher_set.add(file)
            matcher_set.remove(file)  
    print "# previously downloaded learners is:\t" + str(len(downloaded_matcher_set)) + "\n"
    
    # 0
    oauth_keys = [['CRMCoLrLjJBcK6HaGZ7Nn9dWC',
                   'SumAXkM9lZ50KBs4RQdrRdkWMBzrdVyS2YfceY8Te0CqwOqq2L',
                   '2609369460-otRuCCeuDmZxOwug2gJZlhF3PKPNA4tn0msGwH9',
                   'mejOpj5q4mgg03wMOxBTVuZ6ZOjiTuxhBpMGFne1Cj4c0']]
    '''
    # 1
    oauth_keys = [['ImxPrCI2dwPhrVP6F7MT3xXpl',
                   'jJpQ2gRGM31SHs5w1YhyZX7SPrkSu86PVhRfFwG5GGimZo81nE',
                   '2983438302-TqEZPHeTtWHSYRfDi2oJzxfmLkzrSH99QXe1dpd',
                   'SM6azouMW3bddVcwIlKuFqaWJB6bU4Opv6o76NaZZNpYB']]
    
    
    # 2
    oauth_keys = [['3eFaiFlmRVvMg4wSkgCsmfzMi',
                   'n4vjxdbegqkgmQZpHAT40JyPuxvO8SMq7A41ava66rmli9uHtr',
                   '2983438302-jP08K022DdkEm5TQHiV5XlF1USGTcPlz606zQHc',
                   '4K8Jg5lny1r5iKFYmDRzpz8bpm6NG8qtKgEmzuKLMgahp']]
    
    # 3
    oauth_keys = [['HEQkKdMbP029P1NybPYwoThoH',
                   'WTdFLVpiarx7xzKTz38jSlEWbNRETKoyOwNPwd2Sh7sJGAczLK',
                   '2609369460-4J2FJBLSW2UEK4yoSTIPnBIEpqQk2ZnlvwfFIRo',
                   '2UWmhdAwJLLfN8BeNFoKSVFzoUHrd2HsJ3IzfpC3FJT8o']]

    # 4
    oauth_keys = [['3CBCHEMcRc4SuudrWGNCskUgD',
                   'lW8V6lHr55eZ2jxnw83znvGbAZ6eDwuTFSaKsz69y3uCLSbM8P',
                   '2983438302-HJoYZD4dPppINFz4BDhIcX3119mjcBEp7wPLpbn',
                   'sVONXbKI3JPvu7Sj4oKi1PgLmpTYUd6ACgXqAXXzGIHwa']]
    # 5
    oauth_keys = [['6tbcOoHtfysOqklyHbDM4zZYv',
                   'XGOjGUR9yinTNw1QXZpY7JWaCvTgifQDZB7T2RopPWEBWcPTaA',
                   '2609369460-YZBezh1tkqtqmP7gL6sA5t9WZTa3gyBMF6oNFcx',
                   'Sej4ILlK2SxAjcooT7fiEetAfuwe8YwBqyexYpN6F4q7m']]
    
    # 6
    oauth_keys = [['poPoW3gT05PxObaCyO3wXy1iV',
                   '4LO5XKPQhmeqfhATrqUL1i9BuBj1LTrBdT2qFCG8yOAoG4qCLf',
                   '2902759920-wO9PJmZnBFJAFz7bR2uH05HR8U6UVQISUU1TsV6',
                   'zkZp20dvGurCwLxhOTq3ZkVTElcWN3gPxta57PuMygIJS']]
    '''
    auths = []
    global Tweeapi
    
    for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_key, access_secret)
        auths.append(auth)

        Tweeapi = tweepy.API(auths[0], retry_count=5, retry_delay=5, wait_on_rate_limit=True,
                             wait_on_rate_limit_notify=True)
    
    
    count = 0
    current_time = time.time()
    
    while len(matcher_set) > 0:
        
        learner = matcher_set.pop()
        login = matcher_login_map[learner]
        
        count += 1

        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
        
        
        user_id = ""
        
        try:
            user_id = Tweeapi.get_user(screen_name=login).id
        except Exception as e:
            print "User id...\t" + str(e) + "\t" + login
            
        
        if user_id == "":
            continue
        
        dir_path = path + "twitter/download/" + learner
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)
        
        try:
            # Timeline
            output_path = dir_path + "/tweets"
            output_file = open(output_path, "w")
            
            page = 1
            while page < 160:
                timeline_list = Tweeapi.user_timeline(screen_name=login, count=20, page=page)
                if len(timeline_list) > 0:
                    status_list = []
                    for status in timeline_list:
                        output_file.write(str(status) + "\n")
                    page += 1
                else:
                    break
            output_file.close()
            
        except Exception as e:
            print "Timeline...\t" + str(e) + "\t" + login
            if str(e) == "Not authorized.":
                continue
         
        try: 
            # Friends
            friends = Tweeapi.friends_ids(screen_name=login)
            output_path = dir_path + "/" + str(user_id) + "_friends"
            output_file = open(output_path, "w")
            for friend in friends:
                output_file.write(str(friend) + "\n")
            output_file.close()
        except Exception as e:
            print "Friends...\t" + str(e) + "\t" + login
            
        try: 
            # Followers
            friends = Tweeapi.followers_ids(screen_name=login)
            output_path = dir_path + "/" + str(user_id) + "_followers"
            output_file = open(output_path, "w")
            for friend in friends:
                output_file.write(str(friend) + "\n")
            output_file.close()
        except Exception as e:
            print "Followers...\t" + str(e) + "\t" + login

    output_file.close()
    
    
    
    
    
    


#################################################################################
path = "/Volumes/NETAC/LinkingEdX/"
DownloadPage(path)
print "Finished."
    
        
    
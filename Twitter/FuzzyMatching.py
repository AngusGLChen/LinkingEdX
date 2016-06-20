'''
Created on Nov 27, 2015

@author: Angus
'''

import sys
from sklearn.learning_curve import learning_curve
reload(sys)
sys.setdefaultencoding("utf-8")

import time, os, json, requests, urllib2, tweepy
from lxml import html
from Functions.CommonFunctions import ReadEdX, CompareImages



def FuzzyMatching(path):
    
    # Read EdX learners
    edx_path = path + "course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    # Gather the unmatched twitter learners  
    matching_results_set = set()
    for learner in matching_results_map.keys():
        matching_results_set.add(learner)
        
        if "twitter" in matching_results_map[learner]["checked_platforms"]:            
            edx_learners_set.remove(learner)
        
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "twitter/fuzzy_matching_dec30"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        # for i in range(len(lines)-5):
        for i in range(len(lines)):
            
            line = lines[i].replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                # print file + "\t" + line
                continue
            
            '''
            if array[1] != "" and "twitter.com" not in array[1]:
                print file + "\t" + line
                continue
            '''
            
            learner = array[0]
            login = array[1]
            
            fuzzy_matching_results_map[learner] = login
            fuzzy_matching_results_set.add(learner)
        
        for learner in fuzzy_matching_results_map.keys():
            if fuzzy_matching_results_map[learner] != "":
                num_matched_learners += 1
                
        print "# previous matched learners is:\t" + str(num_matched_learners) + "\n"
        
    else:
        
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "w")
    
    # Twitter connection
    
    # consumerkey, consumerSecret, accessToken, accessTokenSecret
    
    # 0
    oauth_keys = [['CRMCoLrLjJBcK6HaGZ7Nn9dWC',
                   'SumAXkM9lZ50KBs4RQdrRdkWMBzrdVyS2YfceY8Te0CqwOqq2L',
                   '2609369460-otRuCCeuDmZxOwug2gJZlhF3PKPNA4tn0msGwH9',
                   'mejOpj5q4mgg03wMOxBTVuZ6ZOjiTuxhBpMGFne1Cj4c0']]
    
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

    auths = []
    global Tweeapi
    
    for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_key, access_secret)
        auths.append(auth)

        Tweeapi = tweepy.API(auths[0], retry_count=10, retry_delay=60, wait_on_rate_limit=True,
                             wait_on_rate_limit_notify=True)
        
    count = 0
    current_time = time.time()
    
    candidates_map = {}
    candidates_set = set()
    
    # for learner in edx_learner_set:
    for learner in suplement_set:
        
        count += 1
        
        if learner in fuzzy_matching_results_set:
            continue
        
        #if count < 80000:
        #    continue
        
        if count < 27000 or count > 36000:
            continue
        
        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
        
        names = {}
        names["login"] = edx_learners_map[learner]["login"]
        names["name"] = edx_learners_map[learner]["name"]
            
        matched_links = set()
        if learner in matching_results_set:        
            for link_record in matching_results_map[learner]["matched_platforms"]:
                matched_links.add(link_record["url"])
            for link_record in matching_results_map[learner]["link_records"]:
                matched_links.add(link_record["url"])
                
        search_mark = True
        
        keys = ["login", "name"]
        for key in keys:       
            
            if search_mark:
                
                users = []
                
                try:
                    users = Tweeapi.search_users(q=names[key], per_page=10, page=0)
                except Exception as e:
                    if e.message[0]['code'] not in [47]:
                        print "Errors occur when crawlling Twiter...\t" + str(e)
                        return
                
                for user in users:
                    
                    login = user._json['screen_name'].encode('utf-8')
                    name = user._json['name'].encode('utf-8')
                    
                    # Check whether the candidate user's information has been downloaded or not
                    url = "http://twitter.com/" + login
                    candidate_pic_path = path + "twitter/candidate_pics/" + login + ".jpg"
                    
                    if login not in candidates_set:
                        
                        try:
                            #page = requests.get(url)
                            #tree = html.fromstring(page.content)
                            
                            page = urllib2.urlopen(url, timeout=30).read()
                            tree = html.fromstring(page)
                                    
                            return_link = tree.xpath('//a[@class="u-textUserColor"]/@title')
                            if len(return_link) != 0:
                                return_link = return_link[0]
                            else:
                                return_link = ""
                                        
                            pic_link = tree.xpath('//img[@class="ProfileAvatar-image "]/@src')
                            if len(pic_link) != 0:
                                pic_link = pic_link[0]
                            else:
                                pic_link = ""
                            
                            candidates_set.add(login)
                            candidates_map[login] = {"return_link": return_link, "name":name}                           
                                    
                            if pic_link != "" and not os.path.exists(candidate_pic_path):
                                pic = urllib2.urlopen(pic_link) 
                                output = open(candidate_pic_path, "wb")
                                output.write(pic.read())
                                output.close()
                                        
                        except Exception as e:                                    
                            
                            print "Error occurs when downloading information...\t" + str(url) + "\t" + str(e)
                            
                    if login in candidates_set:
                        
                        if candidates_map[login]["return_link"] in matched_links:
                            search_mark = False
                            fuzzy_matching_results_map[learner] = login
                            fuzzy_matching_results_file.write(learner + "\t" + str(login) + "\n")
                            num_matched_learners += 1
                            break
                        else:
                            if str.lower(login) == str.lower(edx_learners_map[learner]["login"]) and str.lower(candidates_map[login]["name"]) == str.lower(edx_learners_map[learner]["name"]):
                                search_mark = False
                                fuzzy_matching_results_map[learner] = login
                                fuzzy_matching_results_file.write(learner + "\t" + str(login) + "\n")
                                num_matched_learners += 1
                                break
                            else:
                                profile_pic_path = path + "profile_pics/" + str(learner)
                                    
                                if os.path.exists(candidate_pic_path) and os.path.exists(profile_pic_path):
                                    
                                    files = os.listdir(profile_pic_path)
                                    
                                    compare_mark = False
                                    for file in files:
                                        
                                        # Compare the candidate pic and the matched profile picture
                                        try:
                                            compare_mark = CompareImages(profile_pic_path + "/" + file, candidate_pic_path)
                                        except Exception as e:
                                            print "Image comparison error..."
                                        
                                        if compare_mark:
                                            search_mark = False
                                            fuzzy_matching_results_map[learner] = login
                                            fuzzy_matching_results_file.write(learner + "\t" + str(login) + "\n")
                                            num_matched_learners += 1
                                            break
                                        
                                    if compare_mark:
                                        break
                
        if search_mark:
            fuzzy_matching_results_file.write(learner + "\t" + "" + "\n")
            
    num_matched_learners = 0
    for learner in fuzzy_matching_results_map.keys():
        if fuzzy_matching_results_map[learner] != "":
            num_matched_learners += 1
                    
    print "# matched learners is:\t" + str(num_matched_learners) + "\n"
    
    fuzzy_matching_results_file.close()

  
def MergeMatchingResults(path):
    
    # 1. Read unmatched learners
    
    # Read EdX learners
    edx_path = path + "course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    ###############################
    '''
    suplement_set = set()
    for learner in matching_results_map.keys():
        if "twitter" not in matching_results_map[learner]["checked_platforms"]:
            matched_links = set()
            for link_record in matching_results_map[learner]["matched_platforms"]:
                matched_links.add(link_record["url"])
            for link_record in matching_results_map[learner]["link_records"]:
                matched_links.add(link_record["url"])
            
            if len(matched_links) != 0 and learner in edx_learners_set:
                suplement_set.add(learner)
    print "# suplement learners is:\t" + str(len(suplement_set)) + "\n"
    '''
    ###############################
    
    # Gather the unmatched twitter learners
    for learner in matching_results_map.keys():
        if "twitter" in matching_results_map[learner]["checked_platforms"]:            
            edx_learners_set.remove(learner)
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # 2. Read fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    files = ["fuzzy_matching_jan5", "fuzzy_matching_jan05_0", "fuzzy_matching_jan05_1", "fuzzy_matching_jan05_2",
             "fuzzy_matching_jan05_3", "fuzzy_matching_jan05_4", "fuzzy_matching_jan05_5", "fuzzy_matching_jan05_6",]
    
    for file in files:
        
        result_path = path + "twitter/temp_results/20160107/" + file
        result_file = open(result_path, "r")
        lines = result_file.readlines()
        
        for line in lines:
            line = line.replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                # print file + "\t" + line
                continue
            
            '''
            if array[1] != "" and "twitter.com" not in array[1]:
                print file + "\t" + line
                continue
            '''
            
            learner = array[0]
            login = array[1]
            
            if learner in edx_learners_set:
                edx_learners_set.remove(learner)
            else:
                continue
            
            if learner not in fuzzy_matching_results_set:
                fuzzy_matching_results_map[learner] = login
            else:
                if fuzzy_matching_results_map[learner] == "":
                    fuzzy_matching_results_map[learner] = login
            
            fuzzy_matching_results_set.add(learner)
    
    ###############################
    '''
    upldated_fuzzy_matching_results_map = {}
    for learner in fuzzy_matching_results_map.keys():
        if learner not in suplement_set or fuzzy_matching_results_map[learner] != "":
            upldated_fuzzy_matching_results_map[learner] = fuzzy_matching_results_map[learner]
            if learner in suplement_set:
                suplement_set.remove(learner)
    fuzzy_matching_results_map.clear()
    fuzzy_matching_results_map = upldated_fuzzy_matching_results_map.copy()
    '''
    ###############################
                
    print "# fuzzy matching learners is:\t" + str(len(fuzzy_matching_results_map))
    print len(edx_learners_set)
    print 
    
    output_path = path + "twitter/fuzzy_matching"
    output_file = open(output_path, "w")
    #output_file.write(json.dumps(fuzzy_matching_results_map))
    
    for learner in fuzzy_matching_results_map.keys():
        output_file.write(learner + "\t" + fuzzy_matching_results_map[learner] + "\n")
    
    #for learner in edx_learners_set:
    #    output_file.write(learner + "\n")
    
    '''
    ###############################
    for learner in edx_learners_set:
        output_file.write(learner + "\n")
        
    for learner in suplement_set:
        if learner not in edx_learners_set:
            output_file.write(learner + "\n")
    ###############################
    '''
    output_file.close()
    
    
    








#################################################################################

# 1. Fuzzy matching github learners
path = "/Users/Angus/Downloads/"
#path = "/data/guanliang"
# FuzzyMatching(path)

# 2. Merge matching results
path = "/Volumes/NETAC/LinkingEdX/"
MergeMatchingResults(path)

print "Finished."



































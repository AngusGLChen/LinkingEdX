'''
Created on Nov 27, 2015

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os, time, urllib2, json, requests, Levenshtein, mysql.connector
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
    
    # Gather the unmatched github learners  
    matching_results_set = set()
    for learner in matching_results_map.keys():
        matching_results_set.add(learner)
        if "github" in matching_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:            
                edx_learners_set.remove(learner)        
    
    ###################################################
    # 1. Explicit matching
    explicit_path = path + "github/explicit_matching"
    explicit_file = open(explicit_path, "r")
    lines = explicit_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        if learner in edx_learners_set:
            edx_learners_set.remove(learner)
    ####################################################
    
    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "github/fuzzy_matching"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        for i in range(len(lines)-5):
            
            line = lines[i].replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                print file + "\t" + line
                continue
            
            if array[1] != "" and "github.com" not in array[1]:
                print file + "\t" + line
                continue
            
            learner = array[0]
            link = array[1]
            fuzzy_matching_results_map[learner] = link
            fuzzy_matching_results_set.add(learner)        
        
        for learner in fuzzy_matching_results_map.keys():
            if fuzzy_matching_results_map[learner] != "":
                num_matched_learners += 1  
        print "# previous matched learners is:\t" + str(num_matched_learners) + "\n"
        
    else:        
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "w")
    
    count = 0
    current_time = time.time()
    
    candidates_map = {}
    candidates_set = set()
    
    # Connect database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1', database='GitHub')
    cursor = connection.cursor()
    
    for learner in edx_learners_set:
        
        count += 1
        
        if learner in fuzzy_matching_results_set:
            continue
        
        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time        
        
        names = {}
        names["login"] = edx_learners_map[learner]["login"]
        names["name"] = edx_learners_map[learner]["name"]        
        
        '''
        if "\"" in names["login"]:
            names["login"] = names["login"].replace("\"", "")
        if "\"" in names["name"]:
            names["name"] = names["name"].replace("\"", "")
        '''
        
        if " " in names["name"]:
            array = names["name"].split(" ")
            name = ""
            for i in range(len(array)):
                name += filter(str.isalnum, array[i])
                if i != len(array) - 1:
                    name += " "
            names["name"] = name
        else:
            names["name"] = filter(str.isalnum, names["name"])
            
        matched_links = set()
        if learner in matching_results_set:        
            for link_record in matching_results_map[learner]["matched_platforms"]:
                matched_links.add(link_record["url"])
            for link_record in matching_results_map[learner]["link_records"]:
                matched_links.add(link_record["url"])
                
        sql_query = "SELECT login, name FROM `users` WHERE login LIKE \"%" + names["login"] + "%\" or name LIKE \"%" + names["name"] + "%\""
        
        cursor.execute(sql_query)
        query_results = cursor.fetchall()
        
        results = {}
        for query_result in query_results:
            results[query_result[0]] = query_result[1]
        
        if len(results) > 10:
            
            similarity_map = {}
            
            for login in results.keys():
                name = results[login]
                
                similarity = (Levenshtein.ratio(str(names["login"]), str(login)) + Levenshtein.ratio(str(names["name"]), str(name))) / 2
                similarity_map[login] = similarity
            
            results.clear()
            
            while len(results) != 10:
                
                max_similarity = -1
                max_login = ""
                    
                for login in similarity_map.keys():
                    if max_similarity < similarity_map[login]:
                        max_similarity = similarity_map[login]
                        max_login = login
                    
                similarity_map.pop(max_login)        
                results[max_login] = max_similarity
        
        search_mark = True
        
        for login in results.keys():
            
            # Check whether the candidate user's information has been downloaded or not
            url = "http://github.com/" + login
            candidate_pic_path = path + "github/candidate_pics/" + login + ".jpg"
                    
            if login not in candidates_set:
                        
                try:
                    page = requests.get(url)
                    tree = html.fromstring(page.content)
                                    
                    return_link = tree.xpath('//a[@class="url"]/text()')
                    if len(return_link) != 0:
                        return_link = return_link[0]
                    else:
                        return_link = ""
                                        
                    pic_link = tree.xpath('//a[@class="vcard-avatar"]/img[@class="avatar"]/@src')
                    if len(pic_link) != 0:
                        pic_link = pic_link[0]
                    else:
                        pic_link = ""
                       
                    candidate_name = ""
                    candidate_name = tree.xpath('//span[@class="vcard-fullname"]/text()')
                    if len(candidate_name) != 0:
                        candidate_name = candidate_name[0]
                    else:
                        candidate_name = ""
                        
                    candidates_set.add(login)
                    candidates_map[login] = {"return_link": return_link, "name":candidate_name}                      
                                    
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
                    fuzzy_matching_results_map[learner] = "http://github.com/" + login
                    fuzzy_matching_results_file.write(learner + "\t" + str("http://github.com/" + login) + "\n")
                    num_matched_learners += 1
                    break
                else:
                    if str.lower(str(login)) == str.lower(str(edx_learners_map[learner]["login"])) and str.lower(str(candidates_map[login]["name"])) == str.lower(str(edx_learners_map[learner]["name"])):
                        search_mark = False
                        fuzzy_matching_results_map[learner] = "http://github.com/" + login
                        fuzzy_matching_results_file.write(learner + "\t" + str("http://github.com/" + login) + "\n")
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
                                    fuzzy_matching_results_map[learner] = "http://github.com/" + login
                                    fuzzy_matching_results_file.write(learner + "\t" + str("http://github.com/" + login) + "\n")
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
    edx_path = path + "/course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)    
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "/latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    # Gather the unmatched github learners
    for learner in matching_results_map.keys():
        if "github" in matching_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:          
                edx_learners_set.remove(learner)

    print "# unmatched learners is:\t" + str(len(edx_learners_set)) + "\n"
    
    # 2. Read fuzzy matching results
    fuzzy_matching_results = {}
    files = ["fuzzy_matching_0", "fuzzy_matching_1", 
             "fuzzy_matching_2", "fuzzy_matching_3"]
    
    for file in files:
        
        result_path = path + "/github/" + file
        result_file = open(result_path, "r")
        lines = result_file.readlines()
        
        for line in lines:
            
            line = line.replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                print file + "\t" + line
                continue
            
            if array[1] != "" and "github.com" not in array[1]:
                print file + "\t" + line
                continue
            
            learner = array[0]
            link = array[1]
            
            if learner in edx_learners_set:
                edx_learners_set.remove(learner)
                
            fuzzy_matching_results[learner] = link
                
    print "# fuzzy matching learners is:\t" + str(len(fuzzy_matching_results))
    print len(edx_learners_set)
    
    output_path = path + "/github/fuzzy_matching"
    output_file = open(output_path, "w")
    
    #output_file.write(json.dumps(fuzzy_matching_results))
    
    for learner in fuzzy_matching_results.keys():
        output_file.write(learner + "\t" + fuzzy_matching_results[learner] + "\n")
    
    output_file.close()
    
    








#################################################################################

# 1. Fuzzy matching github learners
path = "/Volumes/NETAC/LinkingEdX/"
# path = "/data/"
# FuzzyMatching(path)

# 2. Merge matching results
path = "/Volumes/NETAC/LinkingEdX/"
MergeMatchingResults(path)

print "Finished."



































'''
Created on Dec 20, 2015

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import mysql.connector, string, time, os, json, Levenshtein, requests, urllib2
from lxml import etree, html
from happyfuntokenizing import *
from Functions.CommonFunctions import ReadEdX, CompareImages


def ImportDatabase(user, password, host, database, path):
    
    con = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users(id INT PRIMARY KEY, reputation INT, creationdate timestamp, displayname VARCHAR(50), lastaccessdate timestamp, location TEXT, aboutme TEXT, views INT, upvotes INT, downvotes INT, emailhash TEXT, lentext INT, hemo INT, semo INT, upperc FLOAT, punctu INT, code TEXT, hasurl TEXT, uurls TEXT, numurls INT, numgooglecode INT, numgithub INT, numtwitter INT, numlinkedin INT, numgoogleplus INT, numfacebook INT)")
    context = etree.iterparse(path, events=('end',), tag='row')

    # Common variables
    happyemoticons = [":-)", ":)", ":o)", ":]", ":3", ":c)", ":>", "=]", "8)", "=)", ":}", ":^)", ":-D", ":D", "8-D", "8D", "x-D", "xD", "X-D", "XD", "=-D", "=D","=-3", "=3", "B^D", ":-)", ";-)", ";)", "*-)", "*)", ";-]", ";]", ";D", ";^)", ":-,"]
    sademoticons = [">:[", ":-(", ":(", ":-c", ":c", ":-<", ":<", ":-[", ":[", ":{", ":-||", ":@", ">:(", "'-(", ":'(", ">:O", ":-O", ":O"]    
    codetext = ["<code>"]
    
    numbatch = 0
    counter = 0
    
    MAXINQUERY = 10000
    
    start_time = time.time()
    print "... START TIME at:" + str(start_time)
    
    query = "INSERT INTO users (id, reputation, creationdate, displayname, lastaccessdate, location, aboutme, views, upvotes, downvotes, emailhash, lenText, hemo, semo, upperc, punctu, code, hasurl, uurls, numurls, numgooglecode, numgithub, numtwitter, numlinkedin, numgoogleplus, numfacebook) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s)"
    
    urlsreg = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"    
    tok = Tokenizer(preserve_case=False)

    for event, elem in context:
        
        counter+=1

        stripped = None
        lenText = 0
        hemo = 0
        semo = 0
        upper = 0
        punctu = 0
        code = False
        hasURL = False
        uurls = None
        numurls = 0
        numGoogleCode = 0
        numGitHub = 0
        numTwitter = 0
        numLinkedIn = 0
        numGooglePlus = 0
        numFacebook = 0

        try:
            if(elem.get("AboutMe")):
                stripped = elem.get("AboutMe").encode('utf-8','ignore')
                lenText = len(stripped)    
                tokenized = tok.tokenize(stripped)
                hemo = sum(p in happyemoticons for p in tokenized)
                semo =  sum(p in sademoticons for p in tokenized)
                upper =  float(sum(x.isupper() for x in stripped)) / float(len(stripped)) * 100
                punctu =  sum(o in string.punctuation for o in stripped)
                code = True if sum(o in codetext for o in tokenized) > 0 else False
                result = re.findall(urlsreg, stripped)
                if(result):                    
                    uurls = ""
                    for u in result:
                        uurls = str(uurls) + str(u) + "|"
                        if "code.google" in u:
                            numGoogleCode += 1
                        if "plus.google" in u:
                            numGooglePlus += 1
                        if "twitter" in u:
                            numTwitter += 1
                        if "github" in u:
                            numGitHub += 1
                        if "linkedin" in u:
                            numLinkedIn += 1
                        if "facebook" in u:
                            numFacebook += 1

                    if(len(uurls) > 1):                        
                        uurls = uurls[:-1]
                
                    numurls = len(result)
                    if(numurls > 0):
                        hasURL = True

                del result
                del tokenized  

        except UnicodeDecodeError, e:
            print 'Error %s' % e    
        

        user = (elem.get("Id"),              #"Id": 
                elem.get("Reputation"),      #"Reputation": 
                elem.get("CreationDate"),    #"CreationDate": 
                elem.get("DisplayName"),     #"DisplayName": 
                elem.get("LastAccessDate"),  #"LastAccessDate": 
                elem.get("Location"),        #"Location": 
                stripped,                    #"AboutMe": 
                elem.get("Views"),           #"Views": 
                elem.get("UpVotes"),         #"UpVotes": 
                elem.get("DownVotes"),       #"DownVotes": 
                elem.get("EmailHash"),       #"EmailHash": 
                lenText,
                hemo,
                semo,
                upper,
                punctu,
                code,
                hasURL,
                uurls,
                numurls,
                numGoogleCode,
                numGitHub,
                numTwitter,
                numLinkedIn,
                numGooglePlus,
                numFacebook
        )
        
        cur.execute(query,user)
        
        del user

        if(counter == MAXINQUERY or elem.getnext() == False):
            numbatch+=1
            counter = 0
            #print counter
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)
            con.commit()            
        
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
            
    cur.execute("CREATE INDEX displayname_index ON users (displayname);")
    con.commit()
    
def FuzzyMatching(user, password, host, database, path):
    
    # Read EdX learners
    edx_path = path + "course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    profile_pics_learners_set = set()
    profile_pics_path = path + "profile_pics/"
    files = os.listdir(profile_pics_path)
    for file in files:
        if file != ".DS_Store":
            profile_pics_learners_set.add(file)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()    
            
    # Gather the unmatched stackexchange learners
    unmatched_learner_set = set()
    matched_learner_set = set()
    
    matching_results_set = set()
    for learner in matching_results_map.keys():
        
        matching_results_set.add(learner)
        
        if "stackexchange" in matching_results_map[learner]["checked_platforms"]:
            matched_learner_set.add(learner)
        else:
            if learner in edx_learners_set:
                unmatched_learner_set.add(learner)
                    
    for learner in profile_pics_learners_set:
        if learner not in matched_learner_set:
            if learner in edx_learners_set:
                unmatched_learner_set.add(learner)    
         
    ###################################################
    # 1. Explicit matching
    explicit_path = path + "stackexchange/explicit_matching"
    explicit_file = open(explicit_path, "r")
    lines = explicit_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        if learner in unmatched_learner_set:
            unmatched_learner_set.remove(learner)
    ####################################################
    
    print "# unmatched learners is:\t" + str(len(unmatched_learner_set)) + "\n"
    
    # Fuzzy matching results
    fuzzy_matching_results_map = {}
    fuzzy_matching_results_set = set()
    
    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "stackexchange/fuzzy_matching_1"
    num_matched_learners = 0
    
    if os.path.exists(fuzzy_matching_results_path):
        fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
        lines = fuzzy_matching_results_file.readlines()
        for i in range(len(lines)-5):
            line = line.replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                print file + "\t" + line
                continue

            learner = array[0]
            id = array[1]
            
            fuzzy_matching_results_map[learner] = id
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
    connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = connection.cursor()
       
    for learner in unmatched_learner_set:
        
        count += 1
        
        if learner in fuzzy_matching_results_set:
            continue
        
        # Multi-task
        # if count > 16000:
        #    continue
        
        #if count < 16000:
        #    continue
        
        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str(num_matched_learners) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
        
        names = {}
        names["login"] = edx_learners_map[learner]["login"]
        names["name"] = edx_learners_map[learner]["name"]
        
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
                
        sql_query = "SELECT id, displayname FROM `users` WHERE displayname LIKE \"%" + names["login"] + "%\" or displayname LIKE \"%" + names["name"] + "%\""
        
        try:        
            cursor.execute(sql_query)
        except:
            print "Database error...\t" + names["login"] + "\t" + names["name"]
            fuzzy_matching_results_file.write(learner + "\t" + "" + "\n") 
            continue
        
        query_results = cursor.fetchall()
        
        results = {}
        for query_result in query_results:
            results[query_result[0]] = query_result[1]
                
        if len(results) > 10:
            
            similarity_map = {}
            
            for id in results.keys():
                display_name = results[id]
                
                similarity = (Levenshtein.ratio(str(names["login"]), str(display_name)) + Levenshtein.ratio(str(names["name"]), str(display_name))) / 2
                similarity_map[id] = similarity
            
            results.clear()
            
            while len(results) != 10:
                
                max_similarity = -1
                max_id = ""
                    
                for id in similarity_map.keys():
                    if max_similarity < similarity_map[id]:
                        max_similarity = similarity_map[id]
                        max_id = id
                    
                similarity_map.pop(max_id)        
                results[max_id] = max_similarity
               
        search_mark = True
        
        for id in results.keys():
            
            # Check whether the candidate user's information has been downloaded or not
            url = "http://stackoverflow.com/users/" + str(id)
            candidate_pic_path = path + "stackexchange/candidate_pics/" + str(id) + ".jpg"
                    
            if id not in candidates_set:
                        
                try:
                    page = requests.get(url)
                    tree = html.fromstring(page.content)
                                    
                    return_link = tree.xpath('//a[@class="url"]/@href')
                    if len(return_link) != 0:
                        return_link = return_link[0]
                    else:
                        return_link = ""
                                        
                    pic_link = tree.xpath('//img[@class="avatar-user"]/@src')
                    if len(pic_link) != 0:
                        pic_link = pic_link[0]
                    else:
                        pic_link = ""
                                    
                    if pic_link != "" and not os.path.exists(candidate_pic_path):
                        pic = urllib2.urlopen(pic_link)
                        
                        output = open(candidate_pic_path, "wb")
                        output.write(pic.read())
                        output.close()
                                        
                    candidates_set.add(id)
                    candidates_map[id] = return_link
                                
                except Exception as e:                                    
                    
                    print "Error occurs when downloading information...\t" + str(url) + "\t" + str(e)
               
            if id in candidates_set:
                
                if candidates_map[id] in matched_links:
                    search_mark = False
                    fuzzy_matching_results_map[learner] = id
                    fuzzy_matching_results_file.write(learner + "\t" + str(id) + "\n")
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
                                fuzzy_matching_results_map[learner] = id
                                fuzzy_matching_results_file.write(learner + "\t" + str(id) + "\n")
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
    
    profile_pics_learners_set = set()
    profile_pics_path = path + "profile_pics/"
    files = os.listdir(profile_pics_path)
    for file in files:
        if file != ".DS_Store":
            profile_pics_learners_set.add(file)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()    
            
    # Gather the unmatched stackexchange learners
    unmatched_learner_set = set()
    matched_learner_set = set()
    
    matching_results_set = set()
    for learner in matching_results_map.keys():
        
        matching_results_set.add(learner)
        
        if "stackexchange" in matching_results_map[learner]["checked_platforms"]:
            matched_learner_set.add(learner)
        else:
            if learner in edx_learners_set:
                unmatched_learner_set.add(learner)
                    
    for learner in profile_pics_learners_set:
        if learner not in matched_learner_set:
            if learner in edx_learners_set:
                unmatched_learner_set.add(learner)    
         
    ###################################################
    # 1. Explicit matching
    explicit_path = path + "stackexchange/explicit_matching"
    explicit_file = open(explicit_path, "r")
    lines = explicit_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        if learner in unmatched_learner_set:
            unmatched_learner_set.remove(learner)
    ####################################################
    
    print "# unmatched learners is:\t" + str(len(unmatched_learner_set)) + "\n"
    
    # 2. Read fuzzy matching results
    fuzzy_matching_results = {}
    files = ["fuzzy_matching_0", "fuzzy_matching_1"]
    for file in files:
        result_path = path + "stackexchange/" + file
        result_file = open(result_path, "r")
        lines = result_file.readlines()
        
        for line in lines:
            
            line = line.replace("\r\n", "")
            line = line.replace("\n", "")
            
            array = line.split("\t")
            
            if len(array) != 2:
                print file + "\t" + line
                continue
            
            learner = array[0]
            id = array[1]
            
            if learner in unmatched_learner_set:
                unmatched_learner_set.remove(learner)
                
            fuzzy_matching_results[learner] = id
                
    print "# fuzzy matching learners is:\t" + str(len(fuzzy_matching_results))
    print len(unmatched_learner_set)

    output_path = path + "stackexchange/fuzzy_matching"
    output_file = open(output_path, "w")
    #output_file.write(json.dumps(fuzzy_matching_results))
    
    for learner in fuzzy_matching_results.keys():
        output_file.write(learner + "\t" + fuzzy_matching_results[learner] + "\n")
    
    output_file.close()







#################################################################################
# 1. Import into database
user='root'
password='admin'
password='Fa8j9tn4dBBxwx3V'
host='127.0.0.1'
database='StackOverflow'
path = "/Volumes/NETAC/LinkingEdX/stackexchange/201509/stackoverflow.com/Users.xml"

path = "/data/stackexchange/201509/stackoverflow.com/Users.xml"
# ImportDatabase(user, password, host, database, path)

# 2. Fuzzy matching
path = "/Volumes/NETAC/LinkingEdX/"
path = "/data/"
# FuzzyMatching(user, password, host, database, path)

# 3. Merge matching results
path = "/Volumes/NETAC/LinkingEdX/"
MergeMatchingResults(path)

print "Finished."
 

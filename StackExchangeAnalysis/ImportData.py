'''
Created on Feb 5, 2016

@author: Angus
'''

import os, json, mysql.connector, re, string, time
from Functions.CommonFunctions import ReadEdX
from lxml import etree
from happyfuntokenizing import *


happyemoticons = [":-)", ":)", ":o)", ":]", ":3", ":c)", ":>", "=]", "8)", "=)", ":}", ":^)", ":-D", ":D", "8-D", "8D", "x-D", "xD", "X-D", "XD", "=-D", "=D","=-3", "=3", "B^D", ":-)", ";-)", ";)", "*-)", "*)", ";-]", ";]", ";D", ";^)", ":-,"]
sademoticons = [">:[", ":-(", ":(", ":-c", ":c", ":-<", ":<", ":-[", ":[", ":{", ":-||", ":@", ">:(", "'-(", ":'(", ">:O", ":-O", ":O"]    
codetext = ["<code>"]

def ReadCourseNameCode(course_meta_path):
    
    course_code_name_map = {}    
    path = course_meta_path + "name_code"
    file = open(path, "r")
    lines = file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        name = array[0]
        code = array[1]
        
        course_code_name_map[code] = name        
    return course_code_name_map 

def GatherPlatformIDs(course_meta_path, web_path):
    
    # 1. Read matched learners
    
    # 1.1 Read EdX learners
    edx_path = course_meta_path + "course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    course_learners_map = {}
    for learner in edx_learners_map.keys():
        for course in edx_learners_map[learner]["courses"]:
            if course not in course_learners_map.keys():
                course_learners_map[course] = set()
            course_learners_map[course].add(learner)
    
    # 1. Read platform ids
    platform_ids_map = {}
    
    # 1.1 Explicit matching
    explicit_path = web_path + "/explicit_matching"
    explicit_file = open(explicit_path, "r")
    matched_records = json.loads(explicit_file.read())
    for learner in matched_records.keys():
        if learner in edx_learners_set:
            
            platforms = matched_records[learner]["platforms"]
        
            for platform in platforms:
                platform_name = platform["platform"]
                id = platform["id"]
            
                if platform_name not in platform_ids_map.keys():
                    platform_ids_map[platform_name] = set()
                
                platform_ids_map[platform_name].add(id)
    
    # 1.2 Direct matching
    direct_path = os.path.dirname(os.path.dirname(course_meta_path)) + "/latest_matching_result_0"
    direct_file = open(direct_path, "r")
    jsonLine = direct_file.read()
    direct_results_map = json.loads(jsonLine)
    direct_file.close()
    
    for learner in direct_results_map.keys():
        if "stackexchange" in direct_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:
                for matched_platform in direct_results_map[learner]["matched_platforms"]:
                    if matched_platform["platform"] == "stackexchange":
                        url = matched_platform["url"]
                        array = url.replace("http://","").split("/")
                        platform = array[0]
                        id = array[-1]
                        
                        if not str.isdigit(str(id)):
                            continue
                        
                        if platform not in platform_ids_map.keys():
                            continue
                        
                        platform_ids_map[platform].add(id)
                            
    # 1.3 Fuzzy matching
    fuzzy_path = web_path + "/fuzzy_matching"
    fuzzy_file = open(fuzzy_path, "r")
    lines = fuzzy_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        id = array[1]
        if id != "":
            if learner in edx_learners_set:
                platform_ids_map["stackoverflow.com"].add(id)
    '''           
    # Analysis
    for platform in platform_ids_map.keys():
        print platform + "\t" + str(len(platform_ids_map[platform]))
    '''
    
    for platform in platform_ids_map.keys():
        array = []
        for id in platform_ids_map[platform]:
            array.append(id)
        platform_ids_map[platform] = array
        
    output_path = web_path + "/platform_ids"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(platform_ids_map))
    output_file.close()
    
def fast_iterUser(context, cur, con, learner_id_set):
    
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
        
        '''
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
        '''
        '''
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
        
        if user[0] in learner_id_set:
            cur.execute(query,user)
        
        del user
        
        if(counter == MAXINQUERY or elem.getnext() == False):
            numbatch+=1
            counter = 0
            #print counter
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)
            con.commit()            
        '''
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
        
    print counter
    
def ImportUsers(learner_id_set, database_name, connection, cursor, user_path):
    
    #cursor.execute("DROP TABLE IF EXISTS users")
    #cursor.execute("CREATE TABLE users(id INT PRIMARY KEY, reputation INT, creationdate timestamp, displayname VARCHAR(50), lastaccessdate timestamp, location TEXT, aboutme TEXT, views INT, upvotes INT, downvotes INT, emailhash TEXT, lentext INT, hemo INT, semo INT, upperc FLOAT, punctu INT, code TEXT, hasurl TEXT, uurls TEXT, numurls INT, numgooglecode INT, numgithub INT, numtwitter INT, numlinkedin INT, numgoogleplus INT, numfacebook INT)")
    
    context = etree.iterparse(user_path, events=('end',), tag='row')
    
    fast_iterUser(context, cursor, connection, learner_id_set)
    print "... finished committing user data."    
    print "... creating index"
    #cursor.execute("CREATE INDEX users_id_index ON users (id);")
    connection.commit()
    
def fast_iterComments(context, cur, con, learner_id_set):
    
    question_id_set = set()
    
    numbatch = 0
    counter = 0
    MAXINQUERY = 100000

    start_time = time.time()
    
    print "... START TIME at:" + str(start_time)

    query = "INSERT INTO comments (id, postid, score, text, creationdate, userdisplayname, userid) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        
    for event, elem in context:
            
        counter+=1
        
        
        comment = ( elem.get("Id"),   #"Id": 
                    elem.get("PostId") if elem.get("PostId") else None, 
                    elem.get("Score") if elem.get("Score") else None, 
                    elem.get("Text") if elem.get("Text") else None, 
                    elem.get("CreationDate") if elem.get("CreationDate") else None,                                          
                    elem.get("UserDisplayName") if elem.get("UserDisplayName") else None,
                    elem.get("UserId") if elem.get("UserId") else None
        )
        '''
        comment = ( elem.get("Id"),   #"Id": 
                    elem.get("PostId") if elem.get("PostId") else None, 
                    None, 
                    None, 
                    elem.get("CreationDate") if elem.get("CreationDate") else None,                                          
                    None,
                    elem.get("UserId") if elem.get("UserId") else None
        )
        '''
        # if comment[6] in learner_id_set:
        cur.execute(query, comment)
        # if comment[1] != None:
        #         question_id_set.add(comment[1])

        del comment

        if(counter == MAXINQUERY or elem.getnext() == False):
            numbatch+=1
            counter = 0
            #print counter
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)
            con.commit()
        
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    return question_id_set
    
def ImportComments(learner_id_set, database_name, connection, cursor, comment_path):
    
    cursor.execute("DROP TABLE IF EXISTS comments")
    cursor.execute("CREATE TABLE comments(id INT PRIMARY KEY, postid INT, score INT, Text TEXT, creationdate timestamp, userdisplayname TEXT, userid INT)")
    
    context = etree.iterparse(comment_path, events=('end',), tag='row')
    
    question_id_set = fast_iterComments(context, cursor, connection, learner_id_set)
    print "... finished committing comment data."    
    print "... creating index"
    cursor.execute("CREATE INDEX comment_post_id_index ON comments (postid);")    
    cursor.execute("CREATE INDEX comment_user_id_index ON comments (userid);")
    connection.commit()
    
    return question_id_set

def fast_iterAnswers(context, cur, con, learner_id_set):
    
    question_id_set = set()
    
    numbatch = 0
    counter = 0
    MAXINQUERY = 100000
    
    #urls = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    #result = urls.match(string)
    
    start_time = time.time()
    
    print "... START TIME at:" + str(start_time)

    tok = Tokenizer(preserve_case=False)
    
    query = "INSERT INTO answers (id, parentId, creationdate, closeddate, isclosed, score, viewcount, body, owneruserid, ownerdisplayname, title, lasteditoruserid, lasteditordisplayname, lasteditdate, lastactivitydate, tags, numbertags, answercount, commentcount, favoritecount, bodylen, bhemo, bsemo, bupper, bpunctu,bcode, titlelen, themo, tsemo, tupper, tpunctu, tagsintitle, tagsinbody,tcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    for event, elem in context:
        
        if(elem.get("PostTypeId") != "2"):
            elem.clear()
            continue

        counter+=1

        stripped = ""
        tags= ""
        tagnumber = 0
        
        bodylen= 0
        bhemo= 0
        bsemo= 0 
        bupper= 0 
        bpunctu = 0
        bcode = False
        
        titlelen= 0
        themo= 0
        tsemo= 0
        tupper= 0
        tpunctu = 0
        tcode = False
         
        tagsintitle = 0
        tagsinbody = 0
        
        
        try:
            if(elem.get("Body")):
                stripped = elem.get("Body").encode('utf-8','ignore')
                bodylen = len(stripped)                    
                tokenized = tok.tokenize(stripped)
                bhemo = sum(p in happyemoticons for p in tokenized)
                bsemo =  sum(p in sademoticons for p in tokenized)
                bupper =  float(sum(x.isupper() for x in stripped)) / float(len(stripped)) * 100
                bpunctu =  sum(o in string.punctuation for o in stripped)
                bcode = True if sum(o in codetext for o in tokenized) > 0 else False
                del tokenized
                # res = emoticonFinder(stripped)
                # if res != "NA":
            if(elem.get("Title")):
                tstripped = elem.get("Title").encode('utf-8','ignore')
                titlelen = len(elem.get("Title").encode('utf-8','ignore'))
                tokenized = tok.tokenize(tstripped)
                themo = sum(p in happyemoticons for p in tokenized)
                tsemo =  sum(p in sademoticons for p in tokenized)
                tupper =  float(sum(x.isupper() for x in tstripped)) / float(len(tstripped)) * 100
                tpunctu =  sum(o in string.punctuation for o in tstripped)
                tcode = True if sum(o in codetext for o in tokenized) > 0 else False
                del tokenized

        except UnicodeDecodeError, e:
            print 'Error %s' % e
        
        try:
            if(elem.get("Tags")):
                #print elem.get("Tags").encode('utf-8','ignore')
                tags = re.sub('[<]', '', elem.get("Tags").encode('utf-8','ignore'))
                tags = re.sub('[>]', '|', tags)[:-1]
                tagnumber = len(tags.split("|"))
                #tags = strip_tags(elem.get("Tags").encode('utf-8','ignore'))
                for t in tags.split("|"):
                    if(elem.get("Title") != None):
                        if t in elem.get("Title"):
                            tagsintitle += elem.get("Title").count(t);
                    if t in elem.get("Body"):
                        tagsinbody += elem.get("Body").count(t)

            #print tagnumber,tagsInTitle, tagsInBody

        except UnicodeDecodeError, e:
            print 'Error %s' % e
    
        '''
        answer = (  elem.get("Id"), #"Id": 
                    elem.get("ParentId") if elem.get("ParentId") else None, #"acceptedanswer": 
                    elem.get("CreationDate"), #"CreationDate": 
                    None, #"ClosedDate":                     
                    True, #"isclosed":                     
                    None, #"score": 
                    None, #"ViewCount":                     
                    None,
                    elem.get("OwnerUserId") if elem.get("OwnerUserId") else None, #"OwnerUserId":
                    None, #"OwnerDisplayName"
                    None, #"Location": 
                    None, #"LastEditorUserId": 
                    None, #"LastEditorDisplayName"                    
                    None, #"LastEditDate": 
                    None, #"LastActivityDate": 
                    tags,
                    tagnumber,
                    None, #"AnswerCount": 
                    None, #"CommentCount": 
                    None, #"AnswerCount":                     
                    bodylen, 
                    bhemo, 
                    bsemo, 
                    bupper, 
                    bpunctu, 
                    bcode,
                    titlelen, 
                    themo, 
                    tsemo, 
                    tupper, 
                    tpunctu, 
                    tagsintitle, 
                    tagsinbody,
                    tcode
        )
        '''
        
        answer = ( elem.get("Id"), #"Id": 
                    elem.get("ParentId") if elem.get("ParentId") else None, #"acceptedanswer": 
                    elem.get("CreationDate"), #"CreationDate": 
                    elem.get("ClosedDate") if elem.get("ClosedDate") else None, #"ClosedDate":                     
                    True if elem.get("ClosedDate") else False, #"isclosed":                     
                    elem.get("Score") if elem.get("Score") else None, #"score": 
                    elem.get("ViewCount") if elem.get("ViewCount") else None, #"ViewCount":                     
                    stripped,
                    elem.get("OwnerUserId") if elem.get("OwnerUserId") else None, #"OwnerUserId":
                    elem.get("OwnerDisplayName") if elem.get("OwnerDisplayName") else None, #"OwnerDisplayName"
                    elem.get("Title"), #"Location": 
                    elem.get("LastEditorUserId"), #"LastEditorUserId": 
                    elem.get("LastEditorDisplayName") if elem.get("LastEditorDisplayName") else None, #"LastEditorDisplayName"                    
                    elem.get("LastEditDate"), #"LastEditDate": 
                    elem.get("LastActivityDate"), #"LastActivityDate": 
                    tags,
                    tagnumber,
                    elem.get("AnswerCount") if elem.get("AnswerCount") else None, #"AnswerCount": 
                    elem.get("CommentCount") if elem.get("CommentCount") else None, #"CommentCount": 
                    elem.get("FavoriteCount") if elem.get("FavoriteCount") else None, #"AnswerCount":                     
                    bodylen, 
                    bhemo, 
                    bsemo, 
                    bupper, 
                    bpunctu, 
                    bcode,
                    titlelen, 
                    themo, 
                    tsemo, 
                    tupper, 
                    tpunctu, 
                    tagsintitle, 
                    tagsinbody,
                    tcode
        )

        # if answer[8] in learner_id_set:
        
        cur.execute(query, answer)
        #    if answer[1] != None:
        #        question_id_set.add(answer[1])

        del answer

        if(counter == MAXINQUERY or elem.getnext() == False):
            numbatch+=1
            counter = 0
            #print counter
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)
            con.commit()
            #return
        
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
            
    return question_id_set


def ImportAnswers(learner_id_set, database_name, connection, cursor, answer_path):
    
    cursor.execute("DROP TABLE IF EXISTS answers")
    cursor.execute("CREATE TABLE answers(id INT PRIMARY KEY, parentId INT, creationdate timestamp, closeddate timestamp, isclosed TEXT, score INT, viewcount INT, body TEXT, owneruserid INT, ownerdisplayname TEXT, title TEXT, lasteditoruserid INT, lasteditordisplayname TEXT, lasteditdate timestamp, lastactivitydate timestamp, tags TEXT, numbertags INT, answercount INT, commentcount INT, favoritecount INT, bodylen INT, bhemo INT, bsemo INT, bupper FLOAT, bpunctu INT, bcode TEXT, titlelen INT, themo INT, tsemo INT, tupper FLOAT, tpunctu INT, tagsintitle INT, tagsinbody INT, tcode TEXT)")
    
    context = etree.iterparse(answer_path, events=('end',), tag='row')
    
    question_id_set = fast_iterAnswers(context, cursor, connection, learner_id_set)
    print "... finished committing answers data."
    print "... creating index"
    cursor.execute("CREATE INDEX ParentID_index ON answers (ParentID);")
    cursor.execute("CREATE INDEX OwnerUserId_index ON answers (OwnerUserId);")
    connection.commit()
    
    return question_id_set

def fast_iterQuestions(context, cur, con, learner_id_set, question_id_set):
    
    numbatch = 0
    counter = 0
    MAXINQUERY = 100000
    #urls = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    #result = urls.match(string)
    start_time = time.time()
    
    print "... START TIME at:" + str(start_time)

    tok = Tokenizer(preserve_case=False)
    
    query = "INSERT INTO questions (id, acceptedanswer, creationdate, closeddate, isclosed, score, viewcount, body, owneruserid, ownerdisplayname, title, lasteditoruserid, lasteditordisplayname, lasteditdate, lastactivitydate, tags, numbertags, answercount, commentcount, favoritecount, bodylen, bhemo, bsemo, bupper, bpunctu,bcode, titlelen, themo, tsemo, tupper, tpunctu, tagsintitle, tagsinbody,tcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    for event, elem in context:
        
        if(elem.get("PostTypeId") != "1"):
            elem.clear()
            continue

        counter+=1

        stripped = ""
        tags= ""
        tagnumber = 0
        
        bodylen= 0
        bhemo= 0
        bsemo= 0 
        bupper= 0 
        bpunctu = 0
        bcode = False
        
        titlelen= 0
        themo= 0
        tsemo= 0
        tupper= 0
        tpunctu = 0
        tcode = False
         
        tagsintitle = 0
        tagsinbody = 0
        
        
        try:
            if(elem.get("Body")):
                stripped = elem.get("Body").encode('utf-8','ignore')
                bodylen = len(stripped)                    
                tokenized = tok.tokenize(stripped)
                bhemo = sum(p in happyemoticons for p in tokenized)
                bsemo =  sum(p in sademoticons for p in tokenized)
                bupper =  float(sum(x.isupper() for x in stripped)) / float(len(stripped)) * 100
                bpunctu =  sum(o in string.punctuation for o in stripped)
                bcode = True if sum(o in codetext for o in tokenized) > 0 else False
                del tokenized
                # res = emoticonFinder(stripped)
                # if res != "NA":
            if(elem.get("Title")):
                tstripped = elem.get("Title").encode('utf-8','ignore')
                titlelen = len(elem.get("Title").encode('utf-8','ignore'))
                tokenized = tok.tokenize(tstripped)
                themo = sum(p in happyemoticons for p in tokenized)
                tsemo =  sum(p in sademoticons for p in tokenized)
                tupper =  float(sum(x.isupper() for x in tstripped)) / float(len(tstripped)) * 100
                tpunctu =  sum(o in string.punctuation for o in tstripped)
                tcode = True if sum(o in codetext for o in tokenized) > 0 else False
                del tokenized

        except UnicodeDecodeError, e:
            print 'Error %s' % e    
        

        try:
            if(elem.get("Tags")):
                #print elem.get("Tags").encode('utf-8','ignore')
                tags = re.sub('[<]', '', elem.get("Tags").encode('utf-8','ignore'))
                tags = re.sub('[>]', '|', tags)[:-1]
                tagnumber = len(tags.split("|"))
                #tags = strip_tags(elem.get("Tags").encode('utf-8','ignore'))
                for t in tags.split("|"):                    
                    if t in elem.get("Title"):
                        tagsintitle += elem.get("Title").count(t);
                    if t in elem.get("Body"):
                        tagsinbody += elem.get("Body").count(t)

        except UnicodeDecodeError, e:
            print 'Error %s' % e    
        
        question = (elem.get("Id"), #"Id": 
                    elem.get("AcceptedAnswerId") if elem.get("AcceptedAnswerId") else None, #"acceptedanswer": 
                    elem.get("CreationDate"), #"CreationDate": 
                    elem.get("ClosedDate") if elem.get("ClosedDate") else None, #"ClosedDate":                     
                    True if elem.get("ClosedDate") else False, #"isclosed":                     
                    elem.get("Score") if elem.get("Score") else None, #"score": 
                    elem.get("ViewCount") if elem.get("ViewCount") else None, #"ViewCount":                     
                    stripped,
                    elem.get("OwnerUserId") if elem.get("OwnerUserId") else None, #"OwnerUserId":
                    elem.get("OwnerDisplayName") if elem.get("OwnerDisplayName") else None, #"OwnerDisplayName"
                    elem.get("Title"), #"Location": 
                    elem.get("LastEditorUserId"), #"LastEditorUserId": 
                    elem.get("LastEditorDisplayName") if elem.get("LastEditorDisplayName") else None, #"LastEditorDisplayName"                    
                    elem.get("LastEditDate"), #"LastEditDate": 
                    elem.get("LastActivityDate"), #"LastActivityDate": 
                    tags,
                    tagnumber,
                    elem.get("AnswerCount") if elem.get("AnswerCount") else None, #"AnswerCount": 
                    elem.get("CommentCount") if elem.get("CommentCount") else None, #"CommentCount": 
                    elem.get("FavoriteCount") if elem.get("FavoriteCount") else None, #"AnswerCount":                     
                    bodylen, 
                    bhemo, 
                    bsemo, 
                    bupper, 
                    bpunctu, 
                    bcode,
                    titlelen, 
                    themo, 
                    tsemo, 
                    tupper, 
                    tpunctu, 
                    tagsintitle, 
                    tagsinbody,
                    tcode
        )
        '''
        question = (elem.get("Id"), #"Id": 
                    None, #"acceptedanswer": 
                    elem.get("CreationDate"), #"CreationDate": 
                    None, #"ClosedDate":                     
                    True, #"isclosed":                     
                    None, #"score": 
                    None, #"ViewCount":                     
                    None,
                    elem.get("OwnerUserId") if elem.get("OwnerUserId") else None, #"OwnerUserId":
                    None, #"OwnerDisplayName"
                    None, #"Location": 
                    None, #"LastEditorUserId": 
                    None, #"LastEditorDisplayName"                    
                    None, #"LastEditDate": 
                    None, #"LastActivityDate": 
                    tags,
                    tagnumber,
                    None, #"AnswerCount": 
                    None, #"CommentCount": 
                    None, #"AnswerCount":                     
                    bodylen, 
                    bhemo, 
                    bsemo, 
                    bupper, 
                    bpunctu, 
                    bcode,
                    titlelen, 
                    themo, 
                    tsemo, 
                    tupper, 
                    tpunctu, 
                    tagsintitle, 
                    tagsinbody,
                    tcode
        )
        '''
        # if question[8] in learner_id_set or question[1] in question_id_set:
        
        cur.execute(query,question)

        del question

        if(counter == MAXINQUERY or elem.getnext() == False):
            numbatch+=1
            counter = 0
            print "... commiting batch number " + str(numbatch) + ". Elapsed time: " + str(time.time() - start_time)
            con.commit()
            
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    
def ImportQuestions(learner_id_set, database_name, connection, cursor, question_path, question_id_set):
    
    cursor.execute("DROP TABLE IF EXISTS questions")         
    cursor.execute("CREATE TABLE questions(id INT PRIMARY KEY, acceptedanswer INT, creationdate timestamp,    closeddate timestamp, isclosed TEXT, score INT, viewcount INT, body TEXT, owneruserid INT, ownerdisplayname TEXT, title TEXT, lasteditoruserid INT, lasteditordisplayname TEXT, lasteditdate timestamp, lastactivitydate timestamp, tags TEXT, numbertags INT, answercount INT, commentcount INT, favoritecount INT, bodylen INT, bhemo INT, bsemo INT, bupper FLOAT, bpunctu INT, bcode TEXT, titlelen INT, themo INT, tsemo INT, tupper FLOAT, tpunctu INT, tagsintitle INT, tagsinbody INT, tcode TEXT)")
            
    context = etree.iterparse(question_path, events=('end',), tag='row')
    fast_iterQuestions(context, cursor, connection, learner_id_set, question_id_set)
    print "... finished committing question data."
    print "... creating index"
    cursor.execute("CREATE INDEX OwnerUserId_index ON questions (OwnerUserId);")
    connection.commit()
    
def ImportData(web_path):
     
    # 1. Read platform ids data
    platform_id_path =  web_path + "/platform_ids"
    platform_id_file = open(platform_id_path, "r")
    platform_ids_map = json.loads(platform_id_file.read())
    platform_id_file.close()
    
    # Connect to the database
    connection = mysql.connector.connect(user='root', password='admin', host='127.0.0.1')
    cursor = connection.cursor()
    
    test_count = 0
    
    # 2. Import data
    for platform in platform_ids_map.keys():
        
        learner_id_set = platform_ids_map[platform]
        
        print
        print platform
        print
        
        #test_count += 1
        #if test_count < 30:
        #    continue
        
        if platform != "stackoverflow.com":
            continue
        
        database_name = platform.replace(".", "_")  + "2"
        
        # 1. Create the database and use the database
        # cursor.execute("DROP DATABASE IF EXISTS " + database_name + ";")
        # cursor.execute("CREATE DATABASE " + database_name +";")
        cursor.execute("USE " + database_name + ";")
        
        # 2. Import data
        types = ["questions", "answers", "comments"]
        
        # 2.1 Users.xml
        user_path = web_path + "201509/" + platform + "/Users.xml"
        ImportUsers(learner_id_set, database_name, connection, cursor, user_path)
        
        # 2.2 Comments
        comment_path = web_path + "201509/" + platform + "/Comments.xml"
        # question_id_set_by_comments = ImportComments(learner_id_set, database_name, connection, cursor, comment_path)
        
        # 2.3 Answers
        answer_path = web_path + "201509/" + platform + "/Posts.xml"
        # question_id_set_by_answers = ImportAnswers(learner_id_set, database_name, connection, cursor, answer_path)
        
        # 2.4 Questions
        '''
        question_id_set = set()
        
        for question_id in question_id_set_by_answers:
            question_id_set.add(question_id)
        for question_id in question_id_set_by_comments:
            question_id_set.add(question_id)
        
        question_path = web_path + "201509/" + platform + "/Posts.xml"
        ImportQuestions(learner_id_set, database_name, connection, cursor, question_path, question_id_set)
        '''
        
        

            
            


########################
course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
web_path = "/Volumes/NETAC/LinkingEdX/stackexchange/"
# GatherPlatformIDs(course_meta_path, web_path)
ImportData(web_path)
print "Finished."





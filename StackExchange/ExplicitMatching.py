import os,json
import hashlib
from sets import Set
from Functions.CommonFunctions import ReadEdX



def ReadSocialWeb(path):
    
    web_learners_map = {}
    web_learners_set = set()
    
    input = open(path, "r")
    lines = input.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        emailHash = array[0]
        platform = array[1]
        id = array[2]
        
        if emailHash not in web_learners_set:
            web_learners_set.add(emailHash)
            web_learners_map[emailHash] = []
        
        web_learners_map[emailHash].append({"platform":platform, "id":id})
    
    input.close()
    
    return (web_learners_set, web_learners_map)

def MatchLearnersExplicitly(edx_path, web_path):
    
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    web_learners_set, web_learners_map = ReadSocialWeb(web_path)
    
    matched_learners = {}
    
    for email in edx_learners_set:
        emailHash = hashlib.md5(email).hexdigest()
        
        if emailHash in web_learners_set:
            matched_learners[email] = {"courses":edx_learners_map[email]["courses"], "platform_ids": web_learners_map[emailHash]}
    
    # Output matching results
    output_path = os.path.dirname(web_path) + "/explicit_matching"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    
    
    # Analyze
    print "The number of matched learners in total is: " + str(len(matched_learners)) + "\n"
    
    course_learner_map = {}
    platform_learner_map = {}
    
    matched_records = {}
    
    for email in matched_learners.keys():
        for course in matched_learners[email]["courses"]:
            if course not in course_learner_map.keys():
                course_learner_map[course] = set()
            course_learner_map[course].add(email)
        for platform_id in matched_learners[email]["platform_ids"]:
            platform = platform_id["platform"]
            id = platform_id["id"]
            if platform not in platform_learner_map.keys():
                platform_learner_map[platform] = set()
            platform_learner_map[platform].add(email)
        
        matched_records[email] = {"courses": matched_learners[email]["courses"], "platforms": matched_learners[email]["platform_ids"]}
        
        # output_file.write(email + "\t" + str(','.join(matched_learners[email]["courses"])) + "\t" + str(matched_learners[email]["platform_ids"]) + "\n")
    
    output_file.write(json.dumps(matched_records))
    output_file.close()
    
    count_course_learner_map = {}
    for course in course_learner_map.keys():
        count_course_learner_map[course] = len(course_learner_map[course])    
    sorted_count_course_learner_map = sorted(count_course_learner_map.items(), key=lambda d:d[1], reverse=True)
    for record in sorted_count_course_learner_map:
        #print "The number of matched learners from course\t" + str(record[0]) + "\tis:\t" + str(record[1])
        print str(record[0]) + "\t" + str(record[1])
    print
    
    count_platform_learner_map = {}
    for platform in platform_learner_map.keys():
        count_platform_learner_map[platform] = len(platform_learner_map[platform])
    sorted_count_platform_learner_map = sorted(count_platform_learner_map.items(), key=lambda d:d[1], reverse=True)    
    for record in sorted_count_platform_learner_map:
        # print "The number of matched learners from platform\t" + str(record[0]) + "\tis:\t" + str(record[1])
        print str(record[0]) + "\t" + str(record[1])    
    print
    


####################################################
edx_path = "/Volumes/NETAC/LinkingEdX/course_metadata/course_email_list"
web_path = "/Volumes/NETAC/LinkingEdX/stackexchange/stackexchange_users"
MatchLearnersExplicitly(edx_path, web_path)
print "Finished."
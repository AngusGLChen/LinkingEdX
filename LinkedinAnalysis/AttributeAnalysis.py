'''
Created on Feb 3, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json, os, csv, operator, numpy
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn import manifold

import matplotlib.pyplot as plt

def AnalyzeAttribute(course_codes, course_meta_path, data_path):

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
    
    # Read data file
    data_file = open(data_path, "r")
    data_map = json.loads(data_file.read())
    data_file.close()
    
    matcher_set = set()
    for learner in data_map.keys():
        matcher_set.add(learner)
        
    # Get overlapping matchers    
    overlap_set = set()
    for i in range(len(course_codes) - 1):             
        for learner in course_leaner_map[course_codes[i]]:
            if learner in course_leaner_map[course_codes[i+1]]:
                if learner in matcher_set:
                    overlap_set.add(learner)
    print "# overlapping is:\t" + str(len(overlap_set))
    
    color_array = ["#99CC33", "#FF9900", "#FFCC00"]
    
    # 1. Read attributes
    attribute_name = "skills"
    attribute_array = []
    data_point_color_array = []
    
    for i in range(len(course_codes)):
        
        course_code = course_codes[i]
        
        for learner in course_leaner_map[course_code]:
            
            if learner in matcher_set and learner not in overlap_set:
                
                attributes = data_map[learner][attribute_name]
                
                attribute_line = ""
                for attribute in attributes:
                    attribute_line += attribute + ","
                
                if len(attributes) > 20:
                    attribute_array.append(attribute_line)                     
                    data_point_color_array.append(color_array[i])        
        
        print course_code + "\tThe length of attribute_array is:\t" + str(len(attribute_array))
    
    # 2. Build TF vector and conduct T-SNE
    vectors = TfidfVectorizer(stop_words='english', min_df=2, max_df=1000).fit_transform(attribute_array)
    #vectors = CountVectorizer(stop_words='english', min_df=2, max_df=1000).fit_transform(attribute_array)
    
     
    print "# features is:\t" + str(vectors.shape[0]) + "\t" + str(vectors.shape[1]) 
    
    # SVD-truncated
    X_reduced = TruncatedSVD(n_components=50, random_state=0).fit_transform(vectors)
    
    # PCA
    # X_reduced = PCA(n_components=50).fit_transform(vectors.toarray())
    
    X_embedded = manifold.TSNE(n_components=2).fit_transform(X_reduced)
    
    plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c=data_point_color_array)
    plt.show()




def CompareCommonAttributes(course_codes, course_meta_path, data_path):
    
    attribute_name = "interests"
    attribute_name = "skills"
        
    # Read EdX learners
    course_leaner_map = {}
    learner_set = set()
    
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
        
        learner_set.add(email)
        
    edx_file.close()    
    
    # Read data file
    data_file = open(data_path, "r")
    data_map = json.loads(data_file.read())
    data_file.close()
    
    matcher_set = set()
    for learner in data_map.keys():
        if learner in learner_set:
            matcher_set.add(learner)
        
    # Gather common attributes
    common_attribute_map = {}
    common_attribute_set = set()
    for learner in matcher_set:
        attributes = data_map[learner][attribute_name]
        if len(attributes) > 0:
            
            for attribute in attributes:
                
                if attribute == "see less":
                    continue
                
                if attribute not in common_attribute_set:
                    common_attribute_set.add(attribute)
                    common_attribute_map[attribute] = 0
                common_attribute_map[attribute] += 1
    
    sorted_common_attribute_map = sorted(common_attribute_map.items(), key=operator.itemgetter(1), reverse=True)
    common_attribute_set.clear()
    
    # Print the common interests
    for i in range(50):
        common_attribute_set.add(sorted_common_attribute_map[i][0])
        print sorted_common_attribute_map[i][0] + "\t" + str(sorted_common_attribute_map[i][1])
    print
    
    course_attribute_map = {}
    course_attribute_set = {}
   
    for course in course_codes:
            
        course_attribute_set[course] = set()
        course_attribute_map[course] = {}      
        
        for learner in course_leaner_map[course]:
            if learner in matcher_set:
                attributes = data_map[learner][attribute_name] 
                
                if len(attributes) > 0:
                    for attribute in attributes:
                        
                        if attribute == "see less":
                            continue
                        
                        if attribute not in course_attribute_set[course]:
                            course_attribute_set[course].add(attribute)
                            course_attribute_map[course][attribute] = 0
                        course_attribute_map[course][attribute] += 1
        
    frequent_attribute_set_array = []
    
    sizes = numpy.arange(10, 300, 10)
    
    for size in sizes:
    
        for course in course_codes:
        
            frequent_attributes = set()
            sorted_attribute_map = sorted(course_attribute_map[course].items(), key=operator.itemgetter(1), reverse=True)
        
            i  = 0
            count = 0
            while count < size:
                if sorted_attribute_map[i][0] not in common_attribute_set:
                    frequent_attributes.add(sorted_attribute_map[i][0])
                    count += 1
                i += 1
            
            frequent_attribute_set_array.append(frequent_attributes)
    
    
        for i in range(len(frequent_attribute_set_array) - 1):
            set_a = frequent_attribute_set_array[i]
            set_b = frequent_attribute_set_array[i+1]
        
            num_common_attributes = 0
            for attribute in set_a:
                if attribute in set_b:
                    num_common_attributes += 1
        
        print str(size) + "\t" + str(num_common_attributes)
    
    
                            



##############################################################
# Refine codes
##############################################################

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
    
        
def TSNEAttribute(course_meta_path, data_path):
    
    attribute_name = "interests"
    attribute_name = "skills"
    
    # 1. Read course_code & name
    course_code_name_map =  ReadCourseNameCode(course_meta_path)
    course_code_array = []
    
    for course_code in course_code_name_map.keys():
        course_code_array.append(course_code)
    
    # 2. Read EdX learners
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
    
    # 3. Read Linkedin data file
    data_file = open(data_path, "r")
    data_map = json.loads(data_file.read())
    data_file.close()
    
    matcher_set = set()
    for learner in data_map.keys():
        matcher_set.add(learner)
        
    # 4. Generate the T-SNE plot for each pair of courses
    for i in range(len(course_code_array) - 1):
        course_a = course_code_array[i]
        for j in range(i+1, len(course_code_array)):
            
            course_b = course_code_array[j]
            
            #if course_code_name_map[course_a] != "Functional Programming" or course_code_name_map[course_b] != "Framing":
            #    continue
            
            #if course_code_name_map[course_a] != "Delft Design Approach" or course_code_name_map[course_b] != "Topology in Condensed Matter":
            #    continue
            
            if course_code_name_map[course_a] != "Data Analysis" or course_code_name_map[course_b] != "Solar Energy (2015)":
                continue
            
            fig_name = "/Users/Angus/Downloads/" + course_code_name_map[course_a] + " v.s. " +  course_code_name_map[course_b] + ".png"
            #if os.path.exists(fig_name):
            #    continue
            
            # 5. Get overlapping matchers    
            overlap_set = set()
            for learner in course_leaner_map[course_a]:
                if learner in course_leaner_map[course_b]:
                    if learner in matcher_set:
                        overlap_set.add(learner)
            print "# overlapping is:\t" + str(len(overlap_set))
            
            color_a = "y"
            color_b = "b"
    
            # 6. Read attributes    
            attribute_array = []
            data_point_color_array = []
            
            size = 0
            
            for learner in course_leaner_map[course_a]:                
                if learner in matcher_set and learner not in overlap_set:                
                    attributes = data_map[learner][attribute_name]
                
                    attribute_line = ""
                    for attribute in attributes:
                        
                        if attribute in ["see less", "see 35+"]:
                            continue
                        attribute_line += attribute + ","
                
                    if len(attributes) > 0:
                        attribute_array.append(attribute_line)                     
                        data_point_color_array.append(color_a)
                        size += 1
                        
            for learner in course_leaner_map[course_b]:                
                if learner in matcher_set and learner not in overlap_set:                
                    attributes = data_map[learner][attribute_name]
                
                    attribute_line = ""
                    for attribute in attributes:
                        if attribute in ["see less", "see 35+"]:
                            continue
                        attribute_line += attribute + ","
                
                    if len(attributes) > 0:
                        attribute_array.append(attribute_line)                     
                        data_point_color_array.append(color_b)
            
            print           
            print "#Size of attributes is:\t" + str(len(attribute_array))
    
            # 7. Build TF vector and conduct T-SNE
            # vectors = TfidfVectorizer(stop_words='english', min_df=2, max_df=1000).fit_transform(attribute_array)
            vectors = CountVectorizer(stop_words='english', min_df=2, max_df=1811).fit_transform(attribute_array)
    
            print "# features is:\t" + str(vectors.shape[0]) + "\t" + str(vectors.shape[1]) 
    
            # SVD-truncated
            X_reduced = TruncatedSVD(n_components=50, random_state=0).fit_transform(vectors)
    
            # PCA
            # X_reduced = PCA(n_components=50).fit_transform(vectors.toarray())
    
            X_embedded = manifold.TSNE(n_components=2).fit_transform(X_reduced)
            
            fig = plt.figure()
            #plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c=data_point_color_array)
            #plt.show()
            
            feature_dimension = str(vectors.shape[1]) 
            
            X_embedded_a = X_embedded[0:size-1,]
            print size
            X_embedded_b = X_embedded[size:vectors.shape[0],]
            
            scatter_a = plt.scatter(X_embedded_a[:, 0], X_embedded_a[:, 1], color="y", label=course_code_name_map[course_a])
            scatter_b = plt.scatter(X_embedded_b[:, 0], X_embedded_b[:, 1], color="b", label=course_code_name_map[course_b])
            
            plt.legend(loc='lower left')
            plt.title("# dimension of the skill vector: " + str(feature_dimension))

            
            # plt.show()
            
            
            fig.savefig(fig_name, format='png')
            plt.close()
            

    
def SelectFequentAttributes(course_meta_path, data_path):
    
    attribute_name = "interests"
    attribute_name = "skills"
    
    # 1. Read course_code & name
    course_code_name_map =  ReadCourseNameCode(course_meta_path)
    course_code_array = []
    
    for course_code in course_code_name_map.keys():
        course_code_array.append(course_code)
        
    # Read EdX learners
    course_leaner_map = {}
    learner_set = set()
    
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
        learner_set.add(email)
    edx_file.close()    
    
    # Read data file
    data_file = open(data_path, "r")
    data_map = json.loads(data_file.read())
    data_file.close()
    
    matcher_set = set()
    for learner in data_map.keys():
        if learner in learner_set:
            matcher_set.add(learner)
        
    # Gather common attributes
    common_attribute_map = {}
    common_attribute_set = set()
    for learner in matcher_set:
        attributes = data_map[learner][attribute_name]
        if len(attributes) > 0:
            
            for attribute in attributes:
                
                if attribute in ["see less", "see 35+"]:
                    continue
                
                if attribute not in common_attribute_set:
                    common_attribute_set.add(attribute)
                    common_attribute_map[attribute] = 0
                common_attribute_map[attribute] += 1
                
    sorted_common_attribute_map = sorted(common_attribute_map.items(), key=operator.itemgetter(1), reverse=True)
    common_attribute_set.clear()
    
    print "# attributes is:\t" + str(len(sorted_common_attribute_map)) + "\n"
    
    # Print the common attributes
    for i in range(50):
        common_attribute_set.add(sorted_common_attribute_map[i][0])
        print sorted_common_attribute_map[i][0] + "\t" + str(sorted_common_attribute_map[i][1])
    print
    
    course_attribute_map = {}
    course_attribute_set = {}
    
    for course in course_leaner_map.keys():
            
        if course not in course_attribute_map.keys():
            course_attribute_set[course] = set()
            course_attribute_map[course] = {}      
        
        for learner in course_leaner_map[course]:
            if learner in matcher_set:
                attributes = data_map[learner][attribute_name] 
                
                if len(attributes) > 0:
                    
                    for attribute in attributes:
                        
                        if attribute in ["see less", "see 35+"]:
                            continue
                        
                        if attribute not in course_attribute_set[course]:
                            course_attribute_set[course].add(attribute)
                            course_attribute_map[course][attribute] = 0
                        course_attribute_map[course][attribute] += 1
        
    for course in course_attribute_map.keys():
        
        print course_code_name_map[course]
        print "Skills\tFrequency"
        
        sorted_attribute_map = sorted(course_attribute_map[course].items(), key=operator.itemgetter(1), reverse=True)
        i  = 0
        count = 0
        while count < 20:
            if sorted_attribute_map[i][0] not in common_attribute_set:
                print sorted_attribute_map[i][0] + "\t" + str(sorted_attribute_map[i][1])
                count += 1
            i += 1
        
        print
        print
    



    
    
    
###############################################################

course_codes = ["AE1110x/1T2014", "DDA691x/3T2014"]
course_codes = ["FP101x/3T2014", "DDA691x/3T2014"]
course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
data_path = "/Volumes/NETAC/LinkingEdX/linkedin/extracted_data"
#AnalyzeAttribute(course_codes, course_meta_path, data_path)
#SelectFequentAttributes(course_meta_path, data_path)
#CompareCommonAttributes(course_codes, course_meta_path, data_path)

TSNEAttribute(course_meta_path, data_path)


print "Finished."  
                
                
                
'''
Created on Feb 2, 2016

@author: Angus
'''

import json, numpy
import matplotlib.pyplot as plt
from Functions.CommonFunctions import ReadEdX

def AnalyzeCertification(course_meta_path, data_path):
    
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
        
    learner_certification_map = {}
    
    certificated_learner_set = set()
    
    for course in course_leaner_map.keys():
        edx_certification_set = set()
        coursera_certification_set = set()
        for learner in course_leaner_map[course]:
            if learner in matcher_set:
                
                if learner not in learner_certification_map.keys():
                    learner_certification_map[learner] = set()
                
                for tuple in data_map[learner]["certifications"]:
                    link = tuple["link"]                    
    
                    if "https://www.coursera.org/account/accomplishments/" in link or "https://www.coursera.org/signature/certificate/" in link or "https://www.coursera.org/maestro/api/certificate" in link:
                        coursera_certification_set.add(learner)
                        learner_certification_map[learner].add(link)
                        
                        certificated_learner_set.add(learner)
                    
                    #if "coursera" in link and "https://www.coursera.org/account/accomplishments/" not in link:
                    #    print link
                    
                    if "verify.edx.org" in link or "https://courses.edx.org/certificates/" in link or "verify.edxonline.org" in link or "http://edx.prometheus.org" in link:
                        edx_certification_set.add(learner)
                        learner_certification_map[learner].add(link)
                        
                        certificated_learner_set.add(learner)
                    
                    #if "edx" in link and "verify.edx.org" not in link and "https://courses.edx.org/certificates/" not in link and "https://www.datacamp.com/" not in link and "verify.edxonline.org" not in link and "http://edx.prometheus.org" not in link:
                    #    print link
        
        #print course + "\tedx\t" + str(len(edx_certification_set))
        #print course + "\tcoursera\t" + str(len(coursera_certification_set))
        print course + "\t" + str(len(edx_certification_set)) + "\t" + str(len(coursera_certification_set))
    
    print "# unique certificated learners is:\t" + str(len(certificated_learner_set))
    
    print
    
    more_than_15 = 0
    
    array = []
    max_num = -1
    for learner in learner_certification_map.keys():
        if len(learner_certification_map[learner]) > 0:
            array.append(len(learner_certification_map[learner]))
            
            print len(learner_certification_map[learner])
            
            
            if max_num < len(learner_certification_map[learner]):
                max_num = len(learner_certification_map[learner])
                
            #if len(learner_certification_map[learner]) == 74:
            #    print learner
                
            if len(learner_certification_map[learner]) > 15:
                more_than_15 += 1
                
    print "# more than 15:\t" + str(more_than_15)
                
    '''
    # Plot of the distribution of the certificate numbers    
    array_to_plot = [16 if i > 15 else i for i in array]
    bins = numpy.arange(0, 18, 1)
    
    print bins
    
    fig, ax = plt.subplots(figsize=(9, 5))
    _, bins, patches = plt.hist(array_to_plot, normed=True, bins=bins, color='#DF7401')

    xlabels = numpy.array(bins[1:], dtype='|S4')
    xlabels[-1] = ' '
    xlabels[-2] = '15+'

    N_labels = len(xlabels)

    plt.xticks(1 * numpy.arange(N_labels) + 1.5)
    ax.set_xticklabels(xlabels)
    
    plt.title('')
    plt.setp(patches, linewidth=0)
    
    plt.show()
    '''
    
    
    
    
    
    
    #####
    '''
    print max_num
    
    fig, ax = plt.subplots(figsize=(9, 5))
    bins = numpy.arange(0,21,1)
    _, bins, patches = plt.hist(array, bins, normed=True, color=['#DF7401'],)
    
    xlabels = numpy.array(bins[1:], dtype='|S4')    
    N_labels = len(xlabels)
    
    plt.xticks(1*numpy.arange(N_labels + 1) + 1.5)
    ax.set_xticklabels(xlabels)
    plt.setp(patches, linewidth=0)
    
    plt.show()
    '''
            
    
            
            
    
        


course_meta_path = "/Volumes/NETAC/LinkingEdX/course_metadata/"
data_path = "/Volumes/NETAC/LinkingEdX/linkedin/extracted_data"
AnalyzeCertification(course_meta_path, data_path)
print "Finished."
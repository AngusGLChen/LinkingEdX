'''
Created on Feb 2, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from bs4 import BeautifulSoup
from lxml import html
from lxml.etree import XPath
import json

def ExtractData(path):
    
    data_map = {}
    
    files = os.listdir(path)
    for file in files:
        
        if file == ".DS_Store":
            continue
        
        learner = file
        
        job_title = ""
        certifications = []
        skills = []
        interests = []     
        
        linkedin_path = path + learner
        linkedin_file = open(linkedin_path, "r")        
        
        soup = BeautifulSoup(linkedin_file.read(), "lxml")
        
        # 1. Job title
        job_title_element = soup.find('p', class_='headline title')
        
        if job_title_element != None:
            job_title = job_title_element.text
            
        # 2. Certification
        certification_elements = soup.find_all('li', class_="certification")
        for certification_element in certification_elements:
            link = certification_element.find('h4').find('a')
            
            if link != None:
                link = link['href']                       
                course_name = certification_element.find('h4').find('a').text
                certifications.append({"course_name": course_name, "link": link})
        
        # 3. Skills
        skill_elements = soup.find_all('li', class_="skill")        
        for skill_element in skill_elements:
            skills.append(str.lower(str(skill_element.text)))
            
        skill_elements = soup.find_all('li', class_="skill extra")        
        for skill_element in skill_elements:
            skills.append(str.lower(str(skill_element.text)))
            
        # 4. Interests
        interest_elements = soup.find_all('li', class_="interest")        
        for interest_element in interest_elements:
            interests.append(str.lower(str(interest_element.text)))
            
        interest_elements = soup.find_all('li', class_="interest extra")        
        for interest_element in interest_elements:
            interests.append(str.lower(str(interest_element.text)))
            
        data_map[learner] = {"job_title": job_title, "certifications": certifications, "skills": skills, "interests": interests}
    
    
    
    output_path = os.path.dirname(os.path.dirname(web_path)) + "extracted_data"
    output_file = open(output_path, "w")
    output_file.write(json.dumps(data_map))
    output_file.close()
        
    




web_path = "/Volumes/NETAC/LinkingEdX/linkedin/download/"
ExtractData(web_path)
print "Finished."
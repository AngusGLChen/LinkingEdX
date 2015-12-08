
# coding: utf-8

# In[13]:

import os
import csv
import json


# In[14]:

# Gather complete users information from the dataset
def GatherUserInformation(path):
    
    user_map = {}
    
    num_total_rows = 0
    num_error_rows = 0
    num_empty_emails = 0
    num_error_emails = 0
    
    input = open(path  + 'users.csv')
    csv_reader = csv.reader(input)
    for row in csv_reader:
        
        num_total_rows += 1
        
        if len(row) != 10:
            num_error_rows += 1
            continue
        
        login = row[1]
        name = row[2]
        email = row[5]
        
        if email != "\\N":
            
            '''
            email = email.lower()
            email = email.replace(" at ", "@")
            email = email.replace(" dot ", ".")
            
            email = email.replace("(at)", "@")
            email = email.replace("(dot)", ".")
            
            email = email.replace("[at]", "@")
            email = email.replace("[dot]", ".")
            
            email = email.replace("{at}", "@")
            email = email.replace("{dot}", ".")
            
            email = email.replace("_at_", "@")
            email = email.replace("_dot_", ".")
            
            email = email.replace("-at-", "@")
            email = email.replace("-dot-", ".")
            
            email = email.replace("<at>", "@")
            email = email.replace("<dot>", ".")
            
            while "\t" in email:
                email = email.replace("\t", "")
            '''
            
            if "@" not in email or "." not in email:
                num_error_emails += 1
            
            if email != "" and login != "":
                user_map[email] = {"login": login, "name": name}                
        else:
            num_empty_emails += 1
            
    print "# total records:\t" + str(num_total_rows)
    print "# error records:\t" + str(num_error_rows)
    print "# empty emails:\t" + str(num_empty_emails)
    print "# error emails:\t" + str(num_error_emails)
            
    # Output user file
    output_path = os.path.dirname(os.path.dirname(path)) + "/github_users"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    
    print "The number of GitHub users is:\t" + str(len(user_map)) + "\n"
    
    #for user in user_map.keys():
    #    output_file.write(user + "\t" + user_map[user]["login"] + "\t" + user_map[user]["name"] + "\n")
    
    
    output_file.write(json.dumps(user_map))
    output_file.close()


# In[15]:

path = "/Users/Angus/Downloads/github/dump/"
GatherUserInformation(path)
print "Finished."


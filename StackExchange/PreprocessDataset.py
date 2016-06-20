import os, re
import shutil
from sets import Set



def DeleteRedundantFile(path):
    files = os.listdir(path)
    for file in files:
        subpath = path + file + "/"
        if os.path.isdir(subpath):
            subfiles = os.listdir(subpath)
            for subfile in subfiles:
                if subfile != "Users.xml":
                    os.remove(subpath + subfile)


# Gather the email hash information from the 201309 dataset
def GatherEmailHash(path):  
    
    # Output email hash file
    emailHash_output_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/email_hash"
    if os.path.isfile(emailHash_output_path):
        os.remove(emailHash_output_path)
    emailHash_output_file = open(emailHash_output_path, 'w')
    
    # Output platform file
    platform_output_path = os.path.dirname(os.path.dirname(os.path.dirname(path))) + "/platform"
    if os.path.isfile(platform_output_path):
        os.remove(platform_output_path)
    platform_output_file = open(platform_output_path, 'w')  
    
    id_regex = re.compile(" Id=\"[a-zA-Z0-9-_]+\"")
    email_regex = re.compile(" EmailHash=\"[a-zA-Z0-9-_]+\"")
    
    files = os.listdir(path)
    for file in files:
        
        subpath = path + file + "/"
        
        if os.path.isdir(subpath):
            platform = file
            subfiles = os.listdir(subpath)
            
            for subfile in subfiles:
                
                if subfile == "Users.xml":
                    
                    print platform
                    platform_output_file.write(platform + "\n")                 
                    
                    user_file = open(subpath + subfile)                    
                    
                    for line in user_file:
                        
                        user_id = ""
                        email_hash = ""
                        
                        # Seek ID                                                                     
                        id_array = id_regex.findall(line)
                        if len(id_array) == 1:                                
                            user_id = id_array[0]
                            user_id = str.strip(user_id)
                            user_id = user_id[user_id.index("\"") + 1 : len(user_id)-1]
                        
                        # Seek EmailHash
                        email_array = email_regex.findall(line)
                        if len(email_array) == 1:                                
                            email_hash = email_array[0]
                            email_hash = str.strip(email_hash)
                            email_hash = email_hash[email_hash.index("\"") + 1 : len(email_hash)-1]
                        
                        if user_id != "" and email_hash != "":
                            emailHash_output_file.write(platform + "," + email_hash + "," + user_id + "\n")
                    
                    user_file.close()
    
    emailHash_output_file.close()
    platform_output_file.close()


# Gather the id information from the 201509 dataset
def PreprocessLatestDataset(platform_path, dataset_path):
    
    # Gather the platform information
    platform_set = set()
    platform_file = open(platform_path, 'r')
    for line in platform_file:
        platform = line.replace("\n", "")
        platform_set.add(platform)
    print "The number of platforms is: " + str(len(platform_set)) + "\n"
    
    # Gather the latest IDs
    
    # 1. Clear out files that cannot be matched
    matched_platform_set = set()
    files = os.listdir(dataset_path)
    for file in files:
        platform = file
        if platform not in platform_set:
            shutil.rmtree(dataset_path + platform)
        else:
            matched_platform_set.add(platform)
    
    # Check whether the platforms matched to the latest dataset
    for platform in platform_set:
        if platform not in matched_platform_set:
            print platform
    
    # 2. Delete redundant files            
    DeleteRedundantFile(dataset_path)
    
    # 3. Gather latest ID
    # Output the file
    output_path = os.path.dirname(os.path.dirname(dataset_path)) + "/latest_id"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')  
    
    id_regex = re.compile(" Id=\"[a-zA-Z0-9-_]+\"")
    
    files = os.listdir(dataset_path)
    for file in files:
        
        subpath = dataset_path + file + "/"        
        if os.path.isdir(subpath):
            platform = file
            subfiles = os.listdir(subpath)
            
            for subfile in subfiles:
                if subfile == "Users.xml":               
                    user_file = open(subpath + subfile)
                    for line in user_file:
                        
                        user_id = ""
                        
                        # Seek ID                                                                     
                        id_array = id_regex.findall(line)
                        if len(id_array) == 1:                                
                            user_id = id_array[0]
                            user_id = str.strip(user_id)
                            user_id = user_id[user_id.index("\"") + 1 : len(user_id)-1]                      
                                               
                        if user_id != "":
                            output_file.write(platform + "," + user_id + "\n")
                    
                    user_file.close()
        
    output_file.close()


def MatchIDs(path):

    # Gather the email_hash information
    emailHash_set = set()   
    platform_set = set()
    
    platform_id_emailHash_map = {}
    
    emailHash_path = path + "email_hash"
    emailHash_fp = open(emailHash_path, "r")
    for line in emailHash_fp:
        line = line.replace("\n","")
        array = line.split(",")
        platform = array[0]
        email_hash = array[1]
        id = array[2]
        
        emailHash_set.add(email_hash) 
        platform_set.add(platform)
        
        if platform not in platform_id_emailHash_map.keys():
            platform_id_emailHash_map[platform] = {}
        platform_id_emailHash_map[platform][id] = email_hash
        
    emailHash_fp.close()
    
    print "The number of email_hash is: " + str(len(emailHash_set))
    print "The number of platform is: " + str(len(platform_set)) + "\n"
    
    ################################################################################################
    # Gather the latest id information
    latest_platform_id_map = {}
    
    # Gather the latest ID information
    id_path = path + "latest_id"
    id_fp = open(id_path, "r")
    for line in id_fp:
        line = line.replace("\n","")
        array = line.split(",")
        
        platform = array[0]
        id = array[1]
        
        if platform not in latest_platform_id_map.keys():
            latest_platform_id_map[platform] = set()
        latest_platform_id_map[platform].add(id)
        
    id_fp.close()
    
    ################################################################################################
    # Match the id between new & old datasets
    output_path = path + "stackexchange_users"
    if os.path.isfile(output_path):
        os.remove(output_path)
    output_file = open(output_path, 'w')
    
    for platform in platform_id_emailHash_map.keys():
        for id in platform_id_emailHash_map[platform].keys():
            if id in latest_platform_id_map[platform]:
                output_file.write(platform_id_emailHash_map[platform][id] + "\t" + platform + "\t" + id + "\n")
                
    output_file.close()



####################################################
# Preprocess 201309 Dataset
path = "/Volumes/NETAC/LinkingEdX/stackexchange/201309/Content/"
#DeleteRedundantFile(path)
#GatherEmailHash(path)

# Preprocess 201509 Dataset
platform_path = "/Volumes/NETAC/LinkingEdX/stackexchange/platform"
dataset_path = "/Volumes/NETAC/LinkingEdX/stackexchange/201509/"
#PreprocessLatestDataset(platform_path, dataset_path)

# Match new & old dataset ids
path = "/Volumes/NETAC/LinkingEdX/stackexchange/"
MatchIDs(path)

print "Finished."
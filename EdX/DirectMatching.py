
# coding: utf-8

# In[336]:

import os
import json
import requests
import urllib, urllib2, hashlib

from sets import Set
from lxml import html
from time import sleep


# In[337]:

def ReadLatestMatchingResults(path):
    
    file_no = 0
    
    matching_results_map = {}
    matching_results_set = set()
    
    if not os.path.exists(path + "latest_matching_result"):
        
        # StackExchange
        stackexchange_path = path + "stackexchange/explicit_matching"
        stackexchange_input = open(stackexchange_path, "r")
        stackexchange_lines = stackexchange_input.readlines()
        
        for line in stackexchange_lines:
            array = line.replace("\n", "").split("\t")
            email = array[0]
            platforms = array[2]
            
            platforms = platforms.replace("\'", '"')
            jsonObject = json.loads(platforms)
            
            platform = ""
            id = ""
            
            for entry in jsonObject:
                platform = entry["platform"]
                id = entry["id"]
                break
            
            url = "http://" + platform + "/users/" + id
            
            if email not in matching_results_set:
                matching_results_set.add(email)
                matching_results_map[email] = {}
                matching_results_map[email]["matched_platforms"] = []
                matching_results_map[email]["checked_platforms"] = []
                matching_results_map[email]["link_records"] = []
            
            matching_results_map[email]["link_records"].append({"platform": "stackexchange", "url": url})
            
        # Gravatar
        gravatar_path = path + "Gravatar/explicit_matching"
        gravatar_input = open(gravatar_path, "r")
        gravatar_lines = gravatar_input.readlines()
        for line in gravatar_lines:
            array = line.replace("\n", "").split("\t")
            email = array[0]
            
            url = "https://www.Gravatar.com/" + hashlib.md5(email.lower()).hexdigest() + ".json"
            
            if email not in matching_results_set:
                matching_results_set.add(email)
                matching_results_map[email] = {}
                matching_results_map[email]["matched_platforms"] = []
                matching_results_map[email]["checked_platforms"] = []
                matching_results_map[email]["link_records"] = []
                        
            matching_results_map[email]["link_records"].append({"platform": "Gravatar", "url": url})
        
        # GitHub
        github_path = path + "github/explicit_matching"
        github_input = open(github_path, "r")
        github_lines = github_input.readlines()
        for line in github_lines:
            array = line.replace("\n", "").split("\t")
            email = array[0]
            login = array[2]
            
            url = "http://github.com/" + login
            
            if email not in matching_results_set:
                matching_results_set.add(email)
                matching_results_map[email] = {}
                matching_results_map[email]["matched_platforms"] = []
                matching_results_map[email]["checked_platforms"] = []
                matching_results_map[email]["link_records"] = []
                        
            matching_results_map[email]["link_records"].append({"platform": "github", "url": url})
        
    else:
        
        ##################################################
        input = open(path + "latest_matching_result", "r")
        lines = input.readlines()
        #for line in lines:
        #    array = line.split("\t")
        ##################################################
    
    return (file_no, matching_results_map)


# In[338]:

def CrawlStackExchange(email, url, path):
    
    return_link = ""
    
    #print "SE...\t" + email + "\t" + url
    sleep(0.2)
    
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
    
        if pic_link != "":
            pic = urllib2.urlopen(pic_link)
            
            output_path = path + "profile_pics/" + email + "/"
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
            
            output = open(output_path + "stackexchange.jpg", "wb")
            output.write(pic.read())
        
        #print "Finish SE..."
        return (True, return_link)
            
    except Exception as e:
        
        print "Error\t" + str(email) + "\tstackexchange\t" + str(url) + "\t" + str(e)
        return (False, return_link)


# In[339]:

def CrawlGitHub(email, url, path):
    
    return_link = ""
    
    #print "GH...\t" + email + "\t" + url
    sleep(0.2)
    
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
    
        if pic_link != "":
            pic = urllib2.urlopen(pic_link)
            
            output_path = path + "profile_pics/" + email + "/"
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
            
            output = open(output_path + "github.jpg", "wb")
            output.write(pic.read())
        
        #print "Finish GH..."
        return (True, return_link)
            
    except Exception as e:
        
        print "Error\t" + str(email) + "\tgithub\t" + url + "\t" + str(e)
        return (False, return_link)
    


# In[340]:

def CrawlGravatar(email, url, path):
    
    return_links = []
    
    #print "Gravatar...\t" + email + "\t" + url
    sleep(0.2)
    
    # For profile pic
    size = 40
    default = 404
    pic_url = "http://www.Gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    pic_url += urllib.urlencode({'d':str(default), 's':str(size)})
    
    try:
        # For pic
        pic = urllib2.urlopen(pic_url)
        output_path = path + "profile_pics/" + email + "/"
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
            
        output = open(output_path + "Gravatar.jpg", "wb")
        output.write(pic.read())
    
        # For profile
        profile = urllib2.urlopen(url)
        jsonLine = profile.read()
        jsonObject = json.loads(jsonLine)
    
        for entry in jsonObject:
            for entry in jsonObject:
                for zero in jsonObject[entry]:
                    for zero in jsonObject[entry]:
                        if "accounts" in zero:
                            for account in zero["accounts"]:
                                return_links.append(account["url"])
                        if "urls" in zero:
                            for url in zero["urls"]:
                                return_links.append(url["value"])
        
        #print "Finish Gravatar..."
        return (True, return_links)
    
    except Exception as e:
        
        print "Error\t" + str(email) + "\tgravatar\t" + url + "\t" + str(e)
        return (False, return_links)
    


# In[341]:

def CrawlTwitter(email, url, path):
    
    return_link = ""
    
    # print "Twitter...\t" + email + "\t" + url
    sleep(0.2)
    
    try:
        page = requests.get(url)
        tree = html.fromstring(page.content)
    
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
    
        if pic_link != "":
            pic = urllib2.urlopen(pic_link)
            
            output_path = path + "profile_pics/" + email + "/"
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
            
            output = open(output_path + "twitter.jpg", "wb")
            output.write(pic.read())
        
        #print "Finish Twitter..."
        return (True, return_link)
            
    except Exception as e:
        
        print "Error\t" + str(email) + "\ttwitter\t" + str(url) + "\t" + str(e)
        return (False, return_link)

def AnalyzeMatchingResults(matching_results_map, key):
    
    platform_map = {}
    for user in matching_results_map.keys():
        for matched_platform in matching_results_map[user][key]:
            platform = matched_platform["platform"]
            
            if platform not in platform_map.keys():
                platform_map[platform] = set()
                
            platform_map[platform].add(user)
    
    print "\nAnalyzing matched accounts..."
    for platform in platform_map.keys():
        print platform + "\t" + str(len(platform_map[platform]))
    print
        


# In[342]:

def DirectMatching(path):
    
    platforms = ["stackexchange", "Gravatar", "github", "twitter"]    
    
    # Read the latest matching results
    file_no, matching_results_map = ReadLatestMatchingResults(path)
    AnalyzeMatchingResults(matching_results_map, "link_records")
    
    for email in matching_results_map.keys():
        
        unreachable_links = []
        
        while len(matching_results_map[email]["link_records"]) != 0:
            
            link_record = matching_results_map[email]["link_records"].pop()
            
            #print "The size of link_records is:\t" + str(len(matching_results_map[email]["link_records"]))
            
            platform = link_record["platform"]
            url = link_record["url"]
            
            # print platform + "\t" + email + "\t" + str(url)
            if platform == "":
                if (("stackoverflow.com" in url) or ("superuser.com" in url) or ("stackexchange.com" in url) or ("serverfault.com" in url) or ("askubuntu.com" in url)) and "stackexchange" not in matching_results_map[email]["checked_platforms"]:
                    platform = "stackexchange"
                    link_record["platform"] = platform
                    
                if "Gravatar.com" in url and "Gravatar" not in matching_results_map[email]["checked_platforms"]:
                    platform = "Gravatar"
                    link_record["platform"] = platform
                
                if "github.com" in url and "github" not in matching_results_map[email]["checked_platforms"]:
                    platform = "github"
                    link_record["platform"] = platform
                        
                if "twitter.com" in url and "twitter" not in matching_results_map[email]["checked_platforms"]:
                    platform = "twitter"
                    link_record["platform"] = platform
                    
                ####################################################################
                # New platforms
                ####################################################################
                            
            if platform == "":
                unreachable_links.append({"platform":"", "url": url})
                continue
                
            # Crawl the url - Gravatar
            return_links = []
            if platform == "Gravatar" and platform not in matching_results_map[email]["checked_platforms"]:
                mark, return_links = CrawlGravatar(email, url, path)
                matching_results_map[email]["checked_platforms"].append("Gravatar")
                matching_results_map[email]["matched_platforms"].append(link_record)
                
            # Process the returned links
            if len(return_links) != 0:
                for return_link in return_links:
                    #if not type(return_link) == unicode:
                    #    print "\nTest\t" + email + "\t" + url + "\t" + str(return_link) + "\t" + str(type(return_link)) + "\n"
                    #else:
                    matching_results_map[email]["link_records"].append({"platform": "", "url": return_link})
            
            
            # Crawl the url - StackExchange & GitHub & Twitter
            return_link = ""
            if platform == "stackexchange" and platform not in matching_results_map[email]["checked_platforms"]:
                mark, return_link = CrawlStackExchange(email, url, path)
                if mark: 
                    matching_results_map[email]["checked_platforms"].append("stackexchange")
                    matching_results_map[email]["matched_platforms"].append(link_record)
                
            if platform == "github" and platform not in matching_results_map[email]["checked_platforms"]:
                mark, return_link = CrawlGitHub(email, url, path)
                if mark:
                    matching_results_map[email]["checked_platforms"].append("github")
                    matching_results_map[email]["matched_platforms"].append(link_record)
                
            if platform == "twitter" and platform not in matching_results_map[email]["checked_platforms"]:
                mark, return_link = CrawlTwitter(email, url, path)
                if mark: 
                    matching_results_map[email]["checked_platforms"].append("twitter")
                    matching_results_map[email]["matched_platforms"].append(link_record)
                
            ####################################################################
            # New platforms
            ####################################################################
                
            # Process the returned link
            if return_link != "":
                matching_results_map[email]["link_records"].append({"platform": "", "url": return_link})
        
        # Copy and store the directed links that cannot be crawled 
        for link_record in unreachable_links:
            matching_results_map[email]["link_records"].append(link_record)
            
    AnalyzeMatchingResults(matching_results_map, "matched_platforms")
            
    # Output the crawled results
    output_path = path + "latest_matching_result_" + str(file_no)
    if os.path.isfile(output_path):
        os.remove(output_path)
    output = open(output_path, "w")
    
    output.write(json.dumps(matching_results_map))
    
    output.close()


# In[343]:

path = "/data/"
path = "/Users/Angus/Downloads/"
DirectMatching(path)
print "Finished."


__author__ = 'Jun Lin'

import json
import requests
import tweepy
import os
import urllib
import urllib2
from lxml import html

global oauth_keys

# Construct connection to Twitter
def TwitterConnection():
    
    # consumerkey, consumerSecret, accessToken, accessTokenSecret
    oauth_keys = [['CRMCoLrLjJBcK6HaGZ7Nn9dWC', 'SumAXkM9lZ50KBs4RQdrRdkWMBzrdVyS2YfceY8Te0CqwOqq2L',
                   '2609369460-otRuCCeuDmZxOwug2gJZlhF3PKPNA4tn0msGwH9',
                   'mejOpj5q4mgg03wMOxBTVuZ6ZOjiTuxhBpMGFne1Cj4c0']]

    global nums
    global switch_num
    global Tweeapi
    
    switch_num = 0
    auths = []

    for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_key, access_secret)
        auths.append(auth)

        Tweeapi = tweepy.API(auths[0], retry_count=10, retry_delay=60, wait_on_rate_limit=True,
                             wait_on_rate_limit_notify=True)
    
    print "OAuth authentication finished."


def UpdateOAuthKeys(consumer_key, consumer_secret, access_key, access_secret):
    
    new_auth = [consumer_key, consumer_secret, access_key, access_secret]
    oauth_keys.append(new_auth)


# Determine whether the rate limit exceeds
def Rate_Limited_Exceed():
    
    limits = Tweeapi.rate_limit_status()
    resource = limits['resources']
    user = resource['users']
    user = user['/users/lookup']
    remaining = user['remaining']
    
    # print "Remaining calls:" + str(remaining)
    
    if (remaining == 1):
        print "Rate limits exceeded..."
        return True
    else:
        return False


'''
This method provides look up function for single twitter user. By passing the user id list or screen name list(necessary), 'users/lookup' API is called.
Input: screen_name_list(required)
Ouput: User information Type: list of json

def Lookup_Users(screen_name_list):
    try:
        UserIds = Tweeapi.lookup_users(
            screen_names=screen_name_list)
        res = UserIds
    except tweepy.error.TweepError, tweepy.error.RateLimitError:
        print tweepy.error.TweepError
        print tweepy.error.RateLimitError
    return UserIds
'''


'''
This method provides search function on twitter.
Input: query(String, required)
       page(int, optional)
       count(int, optional)
Output: results(list of dic)
'''
def Search_Users(query):
    
    # TODO The name of the file should be modified.
    f1 = open("/Users/Angus/Downloads/test" + ".json", 'w')
    # END TODO
    
    res = []
    user_info = {'name': None, 'screen_name': None, 'id': 0}
    users = Tweeapi.search_users(q=query, per_page=20, page=0)
    
    print len(users)
    
    for user in users:
        user_info = {'name': None, 'screen_name': None, 'id': 0}
        user_info['name'] = user._json['name'].encode('utf-8')
        #print user_info['name']
        user_info['screen_name'] = user._json['screen_name'].encode('utf-8')
        #print user_info['screen_name']
        user_info['id_str'] = user._json['id_str'].encode('utf-8')
        #print user_info['id_str']
        res.append(user_info)
        #print res
    json.dump(res, f1)
    print res
    print "Searching finished..."


'''
Extract required user information from user's profile page.
Input: Json file
Output: Downloaded avatar and extracted user information.
'''
def Data_Extracting(file_name):
    
    url = "https://twitter.com/"  # Common prefix of personal url

    with open(file_name, 'r') as f:
        rf = json.loads(f.readline())


    user_list = []
    for user_info in rf:
        user = {'user_url': None, 'screen_name': None, 'title': None, 'avatar_url': None}
        user['screen_name'] = user_info['screen_name']
        # Form the user url and extract the user page.
        user['user_url'] = url + user_info['screen_name']
        page = requests.get(user['user_url'])
        tree = html.fromstring(page.content)

        # Extracting user's title
        link = tree.xpath('//a[@class="u-textUserColor"]/@title')
        if len(link) != 0:
            link = link[0]
        else:
            link = ""
        user['title'] = link

        # Extracting user's avatar
        pic_link = tree.xpath('//img[@class="ProfileAvatar-image "]/@src')
        if len(pic_link) != 0:
            pic_link = pic_link[0]
        else:
            pic_link = ""
        user['avatar_url'] = pic_link
        if pic_link != "":
            pic = urllib2.urlopen(pic_link)
            #output = open("/Users/Angus/Downloads/kk.jpg", "wb")
            #output.write(pic.read())
        user_list.append(user)
    newfile=open('test_new.json','w')
    json.dump(user_list,newfile)
    print "Data extracting finished..."



if __name__ == '__main__':
    
    TwitterConnection()
    # Rate_Limited()
    Search_Users('Papa Elvis')
    #Data_Extracting('test.json')

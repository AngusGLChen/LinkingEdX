'''
Created on Jan 11, 2016

@author: Angus
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import shutil, json, os, time, tweepy
from Functions.CommonFunctions import ReadEdX
from time import sleep

def Authorization(oauth_keys):
    
    global Tweeapi
    
    auths = []
    for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.secure = True
        auth.set_access_token(access_key, access_secret)
        auths.append(auth)

        Tweeapi = tweepy.API(auths[0], retry_count=5, retry_delay=5, wait_on_rate_limit=True,
                             wait_on_rate_limit_notify=True)
        
def RateLimitChecker():
    
    limits = Tweeapi.rate_limit_status()
    resource = limits['resources']
    
    user_limit = resource['users']['/users/show/:id']['remaining']    
    tweet_limit = resource['statuses']['/statuses/user_timeline']['remaining']
    follower_limit = resource['followers']['/followers/ids']['remaining']
    friends_limit = resource['friends']['/friends/ids']['remaining']
    
    if (user_limit <= 5) or (tweet_limit <= 100) or (follower_limit <= 5) or (friends_limit <= 5):
        return True
    else:
        return False
    
def DownloadPage(path):
    
    matcher_login_map = {}
    matcher_set = set()
    
    # Read EdX learners
    edx_path = path + "course_metadata/course_email_list"
    # edx_learners_set, edx_learners_map = CommonFunctions.ReadEdX(edx_path)
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    # Gather the unmatched twitter learners
    for learner in matching_results_map.keys():
        if "twitter" in matching_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:
                for link_record in matching_results_map[learner]["matched_platforms"]:
                    url = link_record["url"].replace("https://twitter.com/","").replace("http://twitter.com/", "").replace("http://www.twitter.com/", "")
                    platform = link_record["platform"]
                    
                    if platform == "twitter":
                        matcher_login_map[learner] = url
                        matcher_set.add(learner)
        
    print "# matched learners is:\t" + str(len(matcher_login_map))

    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "twitter/fuzzy_matching"
    
    fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
    lines = fuzzy_matching_results_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        array = line.split("\t")
        
        learner = array[0]
        login = array[1]
        
        if learner in edx_learners_set and login != "":
            matcher_login_map[learner] = login
            matcher_set.add(learner)
    
    # Read downloaded learners
    downloaded_learner_path = path + "twitter/downloader_list"
    downloaded_learner_file = open(downloaded_learner_path, "r")
    lines = downloaded_learner_file.readlines()
    for line in lines:
        learner = line.replace("\n", "")
        matcher_set.remove(learner)    
    
    print "# unmatched learners is:\t" + str(len(matcher_set)) + "\n"
    
    # Server
    oauth_keys_array = [['B93daHqICxo0iByUfRUGA0F74',
                    'rdwkc05sz8bUZPh25TMFbC0RIBUuKvemLigVPnd4jQD6h0mscf',
                    '3544524377-zj0QzY7JOwn9QpZOqblo46ueSjg5liTh1U34iEs',
                    'h2Ir8xXLDHpnV2N1pwKg6BqKssxFO32GJeEaRcPoHVtaW'],
                        ['RBgVLb9sqCj29nhLNP3Rn6178',
                    '7ersngqKlRrUwSS0Gs873NdyULCIsIbLvPukFBXIJf3TFJZiDS',
                    '4489115181-DkgHMtxkfojkbGzL2uYc91HH7z8Jb4wlOZFcV0n',
                    'VE6KRJPlugxQl8JdC8arUwntYE6PBJtkCWS6TV3XPectL'],
                        ['YnbdIwfmPutURUa8qUffhEpHy',
                    'FlQtKzNzTEhEVvQResXWxfF8cRuMqBMEKPZOzXdiedOnBrQHod',
                    '1097626442-E7iEuceymdiyKiGoSLeKWxfYraGBOj9hyYS0sDT',
                    'uy7Wd6aepWm116KGgTrEnBn0XgOPIYXSH1bWWlTjeeSdz'],
                        ['yF9v6sIDWD9asNoU8sqYqOtwd',
                    'cwqopAuGNQPHKmNbCU8CYAjANYaC1ulhSoO0TTd4jsbZY0J8TA',
                    '4069018384-TtFXFbVEAFMd0ubhCzGO0vnkbzmNQmVDFAngh8Q',
                    'fjVbvc99Sq4cvyUXzOBjwEgNfeC0wnGIwYwaKTZV9flBx'],
                        ['X2nG4JgMUZTlzvaCVqhAv39wv',
                    'WxfO0vv6jCLDy5dxB4aRZvymvSzQbfw1v8aA6xfeyGzpT8HCaE',
                    '119300775-rMCRZdIWy86R7vLHOg6clCRstILoYLU5BkYipPOy',
                    'XIp5pkNG3P757AlLc3DvJ50AtVPZt0HH0OqDdMmd1H543'],
                        ['2ufHUpISLrOmG1A0jV3bxUUae',
                    'TyRjr8F8CFkxezZ9Nyy3WQtVQKVPd85O33iPRwkARErpBVb5gA',
                    '119299120-y2J7k77yJJgqk5cqsfIlrjkFPLgsGGe8oOEllBd5',
                    'KG56DFBTMtdaE7dGWNSvCaAP22uNWiW4cfxsivE0aqTB4'],
                        ['FzZzCC4L88ZZWnf4L5guVBSO9',
                    '4tvAroJNZ7dUDxW6qJ1BPSkKdSiVQdsyJprQtjqoNLYMCf12vV',
                    '354362541-X4NIbvnfvb1lAOk68DPdfpa8en0X4s3ZxhzCcSUn',
                    'BvKZwqVd8MzJiiwI5C1UxqRBdcJUNiN3IVFHMlYLRuTus'],
                        ['8GjNpZaJsWhYk9V7tcdF4i7Qy',
                    'LDTXSQjDQzci2jq4fJumgytGCFeisrgRv8Gm0b5GRMBhrUJZNM',
                    '364689040-8a72OgRFCT1k10g0egEjv6EzyEmg2hFLMpoRNsU5',
                    'cvvJHmWdvbF9pAl02uXptHnrcL4xgE6dlhzMlEmQNRKlz']
                       ]
    
    # Yue
    oauth_keys_array = [["03NgOuiXVofbfFpYGkgJNhwqp",
                    "DogqwlSJL2uC3O6u26cZ7yIcCHoRTICf2rnriC5HOV7wZGbFoV",
                    "4819138840-e7f4VQ1WxH88THl92dSgX4bcspFS4pwG1DJI7mc",
                    "8auejgsgRH8fnsu6oPW6rtG1KAdJp6CPryHLJNMBV5iyl"],
                        ["2zQi2hFsDOhraxlXoKs6VJwdS",
                    "f2GRFHZbqAVtB9XA3U5pHNNWSIISNf544DDYANxhVcn4dHpLf5",
                    "4776421036-XLCmBRKJZi5Jai9y9dudTFKGXAdayJOucs7hH0X",
                    "XiVXG7mYuUqew7UCGFayGxJnomSgLd5QZ2FkSWTrYAfZ1"],
                        ["En9Ljs2dhiABeWQ8kBG4Q0xhZ",
                    "VQWrm0NP31BD3X5C16jy23SbsyidGBkJSB8BW25c6ynZTLnj5g",
                    "3211786677-VqsfE1LfWlMB1aqgIwSva4ATPWg0Baxe4ELrkq0",
                    "jucCsHlxZOmGu4QIvAqAEwVQF1o43HZA3O5YBvyCk9XoL"],
                        ["FCvf2a6rOGQYlxdMmjtemZtk4",
                    "rof6ye1rn3jzfbfJuvixNuYqEcBplRAzRbLHyhqsaPIaxTG1hq",
                    "4815442252-rj07CmSEFHbkuJyKhDrBmgiNailcXCfDdYwsH1J",
                    "H2rBlPQVxXNOJGOaTGp9lCl3PF9mfBXfbTwVdeJhJmqYE"],
                        ["IbPo28NWf3j9XyyRpRhsEnBe6",
                    "9pUK8peVZ6nF1e7KGKaHlFgc69VLcATwgzpF2kXRX1zvfu1dbW",
                    "4815548603-tdCdyuMsvuvdSdYBVZwKp0VxyEQ959Yv1cpg25q",
                    "WrrotqhC2PfF7i1uDwbGaimZEY3W7h9TCycRK977oPrs7"],
                        ["t2Qepb0qyiLiufQZRFniqm1dl",
                    "WikorbdaTg1NR3VRqta3ry2MppxGsq6mlscpKUQBMbwAZeEyCB",
                    "4814888913-bjduaw65VpCURLTJW3kILasPtCf62xLhxH3IrJr",
                    "dytn7hZE6utEhrRrs2HFz68ztbEa3oaijFMn9QMdvMakF"]
                        ]
    
    # Jie
    oauth_keys_array = [["zdxmkaQAr5b9bl0GU18wEhRNp",
                    "11vh3qic6mkoUlBU2SwYbdAsi7F6gPPKAtUVEDhyRJoanp5qVP",
                    "4819148686-aSZyOOftP8LpdZ2SzakHWrOaWSpoGegdKl9QItx",
                    "VoIIn6bBZ4tuws1IMo7pRLIb2Uu3ZlGbm5XvLn5Al8GFZ"],
                        ["J8Cf3Vtbn6FytedrrQR5Zm8nn",
                    "UkwrGwJegTyY7lMn5Row1xm2FrBp6J3fGudTXDpMnXd8HhOAEL",
                    "4815422122-58GzXShGbftPayyCNd3oqMo0kTLxliidajZT3Hs",
                    "sLui79Ou91jBNLPJZEKl4GSJfaGyvV9WwIXZwikYYc6M8"],
                        ["fW1ydwDxhoBdCneAYL0Iy1H8E",
                    "waK5UjfiKMH4kTs6JO5J1S9MyWc2V7PjPP0O4Z4UDM6DjEwLTm",
                    "4815286959-fDFc7b8tFTbPmMiUtieIPG1qMnKKUqmUIGNsAlM",
                    "4nE6Nr3sRh9yPMC0jNIIvq8NALa7QHmaRI5K7ZGs1tIcS"],
                        ["PuQPS5T1I7zcRUReJXacy2hFG",
                    "shryxAdVGRlezwnEqByi225xc0XoFNGpDdGJONRE2QxPP5pgrd",
                    "4815477467-TDet0kM168rpZ0QP4kbWrkd7qCKteoahhBsEnbq",
                    "AmhXSQZoCVPLmxi2jhNWxSDUF9bIdbLhHeLrQXPn6wFmV"],
                        ["hkn4zSfia4QDI9nGlJVfJTANJ",
                    "kEelUunqFztL1lDkg70hzyHKwjqSxY2NpZOj4GQXr5jJ9ZOFgc",
                    "1942222009-PAGMWAWjpRMJva1gYZI9cNRqZxod4mozbI7iRnC",
                    "nQAC2AKufR1HNlhtSniVQC0AUmwA4cAtBNEmpVsbvg16g"],
                        ["PuQPS5T1I7zcRUReJXacy2hFG",
                    "shryxAdVGRlezwnEqByi225xc0XoFNGpDdGJONRE2QxPP5pgrd",
                    "4815477467-TDet0kM168rpZ0QP4kbWrkd7qCKteoahhBsEnbq",
                    "AmhXSQZoCVPLmxi2jhNWxSDUF9bIdbLhHeLrQXPn6wFmV"]
                        ]
    
    # Wisyue
    oauth_keys_array = [['CRMCoLrLjJBcK6HaGZ7Nn9dWC',
                   'SumAXkM9lZ50KBs4RQdrRdkWMBzrdVyS2YfceY8Te0CqwOqq2L',
                   '2609369460-otRuCCeuDmZxOwug2gJZlhF3PKPNA4tn0msGwH9',
                   'mejOpj5q4mgg03wMOxBTVuZ6ZOjiTuxhBpMGFne1Cj4c0'],
                        ['3eFaiFlmRVvMg4wSkgCsmfzMi',
                   'n4vjxdbegqkgmQZpHAT40JyPuxvO8SMq7A41ava66rmli9uHtr',
                   '2983438302-jP08K022DdkEm5TQHiV5XlF1USGTcPlz606zQHc',
                   '4K8Jg5lny1r5iKFYmDRzpz8bpm6NG8qtKgEmzuKLMgahp'],
                        ['HEQkKdMbP029P1NybPYwoThoH',
                   'WTdFLVpiarx7xzKTz38jSlEWbNRETKoyOwNPwd2Sh7sJGAczLK',
                   '2609369460-4J2FJBLSW2UEK4yoSTIPnBIEpqQk2ZnlvwfFIRo',
                   '2UWmhdAwJLLfN8BeNFoKSVFzoUHrd2HsJ3IzfpC3FJT8o'],
                        ['3CBCHEMcRc4SuudrWGNCskUgD',
                   'lW8V6lHr55eZ2jxnw83znvGbAZ6eDwuTFSaKsz69y3uCLSbM8P',
                   '2983438302-HJoYZD4dPppINFz4BDhIcX3119mjcBEp7wPLpbn',
                   'sVONXbKI3JPvu7Sj4oKi1PgLmpTYUd6ACgXqAXXzGIHwa'],
                        ['DEokJyGA3jcMcsL1eyT88gFgL',
                    'WQWVGLRzUGFfSFLARDnuzb3E97YQ5GOWNjcuu8EcaaTPcyCIQV',
                    '4812654262-E3AoKbaid7IkmA4TRnUnvcsfQ0QfRUs3VL8I5yw',
                    'h6MOemW7yvZhbXNnnILh5kJ51Txhh2vRzyT9LtgezrOJu'],
                        ['RkuVxb2vZx51jb46n2a0Kgy8L',
                    'fuOBgN6hoelaSCJ6YDYDdqkyHIV9VZh61h5zBzgbtmyGpc857B',
                    '4812841702-A6OKLCoUT9VOVq0WR5RePDRBLSPBY82GUXWujFH',
                    'iOxiowLPRvpQMqRhgJaX2RQ6AI0hv3eshRewa2Uiv6Ndc'],
                        ['dpE3GYKsFNOt5JnNMT5Hpn3mp',
                    'dkufK1tiui3E1NQj6e1T0cuKXQscUIkmvkNr4SWmpxWN9HXDTs',
                    '477252588-6wSdCYH09hhrGTMg0rg2ClI0cxdTDfQeJeRxXwCx',
                    'fEHvfQVCBJc74VpvSfnvn5u0WP7VaW6b8GgEleNlbDfOG'],
                        ['iZxEa0gSk948XI8ZFFI10sJfE',
                    'DXPo3pOpaI27Ml1WTTr9PwmmcPxo71tpnzkvMYNeXq3iwID0ml',
                    '3823969697-kt2kREOIG4dpyiAMJNQVZdSK6cn6M3E7kXu0fza',
                    'NVFR9oa9nDLT0mqilXJ2ByX7ee7Z0ausG0t24Pqm150RJ']                                 
                        ]
    
    # Angus
    oauth_keys_array = [['ImxPrCI2dwPhrVP6F7MT3xXpl',
                    'jJpQ2gRGM31SHs5w1YhyZX7SPrkSu86PVhRfFwG5GGimZo81nE',
                    '2983438302-TqEZPHeTtWHSYRfDi2oJzxfmLkzrSH99QXe1dpd',
                    'SM6azouMW3bddVcwIlKuFqaWJB6bU4Opv6o76NaZZNpYB'],
                        ['mwZUwO6dKLVKZ5tEN8XrvDCzd',
                    'lVzAMYefJu7SkPhY7FQEAlSUVtXvZTY1DGRrWPJS1YIFLeMy3h',
                    '1910920183-hNwZ8oGQK2hYkb4zqdapwf8vup3MYzHEixhJ1Os',
                    'p5vECFddZL2sD2PKwmOAFvwYBRsXTv5sTsVRxaXXoahoT'],
                        ['L4AJQZxi3lsASdZHqoHjM1Ekp',
                    'lGM4BRDjz9q3bPyAMsC2Jb91N3jBJwEXAmx0g1NHCMFvACXquK',
                    '425354456-egNrCHBMH2ccvh0FCsydXGw3ehWsH0l8heDnFWDK',
                    'cfwfs0MItaWQYPx7VrTOuX5seWme9bp3J6RWggI0zSTR1'],
                        ['Tgz8p3FsxN270Gln7njDofb7I',
                    'qdUqd1h9FcxHeyZXp7NDBDmoqlGs05B0vGPTlLWCWfiEFSKfwy',
                    '143669555-WkABdpANapIOWLK6wbuWO47OWjeUyJcFXE0eAZUI',
                    'IWUyGNZqC7dCBJL7KoO7Eo0NSK4nTQtWDVFlDRXxK6ibk'],
                        ['9azUHgStBSOKWwPBzfuUw',
                    'INy2xH4hFwygEtogjH1EPyCdX3afulI2uwiLdO6l8g',
                    '1903967041-h9D8HAWxvKIYyWqDokNmznt2ZgPVZh0UPwPMLyI',
                    'XjWcNLh5ewUJ7hvpZUFi6jEjr4uemHgumeEYBkiT7s'],
                        ['FXgOekK0CoEinGU8LmsgybjzD',
                    'nw15kFsp2oazLH80lwpxg1DHNnL1sBHQkdUv1thDPn7Z1iMQEM',
                    '3293907658-chE7Uk3MrtefqloCj2MiKe844emq7IqmEJgIgbY',
                    'IbeiTuZJBYyojEesqC1eIjln30mQDSciIPi1BAh7vZT8m'],
                        ['gbUz0S7lKu1MTIsxvrNOFajbX',
                    '4d7szxQAl7St3IE6wyB8L7j0qA9R0BeTvzZMekGm4LKHjGUUXN',
                    '1266120740-0SSYNx4Go3nB6IWInSqpVf6UddnIlgnkNTTRiXz',
                    'LGaZVTmC9iVuWdPt8QnmPdeVZgMNgccj0zwjJ6zFgwJTo'],
                        ['ErKWTGkbB1GCi0jpruA9zs7mf',
                    'bg8yusuSRFPvDIrtMO5s1UcwPSgcwKHoehqwuc74YLRKcXLyLM',
                    '2277305762-Ft5G0RncltTkfyhGXcvbYVryTwEdPEnGwdru3B0',
                    '6Mgl9Wg2Sv3Y6Js2IemZt0VDQ5RlTPtXq3JeYkHv27Ixn'],        
                        ]
    
    
       
    count = 0
    current_time = time.time()

    oauth_keys_index = 0
    Authorization([oauth_keys_array[oauth_keys_index]])
    oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
    
    #########################################################
    missing_record_path = path + "twitter/missing_record"
    if os.path.exists(missing_record_path):
        missing_record_file = open(missing_record_path, "a+")
    else:
        missing_record_file = open(missing_record_path, "w")
    #########################################################
    
    while len(matcher_set) > 0:
        
        learner = matcher_set.pop()
        login = matcher_login_map[learner]
        
        count += 1

        if count % 100 == 0:
            update_time = time.time()
            print "Current count is:\t" + str(count) + "\t" + str((update_time - current_time) / 60)
            current_time = update_time
        
        dir_path = path + "twitter/download/" + learner
        if os.path.exists(dir_path):
            continue
        os.mkdir(dir_path)
        
        profile_path = dir_path + "/profile"
        profile_file = open(profile_path, "w")
        
        friend_path = dir_path + "/friend"
        friend_file = open(friend_path, "w")
        
        follower_path = dir_path + "/follower"
        follower_file = open(follower_path, "w")
        
        tweet_path = dir_path + "/tweet"
        tweet_file = open(tweet_path, "w")
        
        ####################################################################################
        # 1. Profile       
        try:
            
            if RateLimitChecker():
                Authorization([oauth_keys_array[oauth_keys_index]])
                oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
            
            user = Tweeapi.get_user(screen_name=login)
            
            user_json = {}
            user_json['id'] = user.id
            user_json['screenname'] = user.screen_name
            user_json['name'] = user.name
            user_json['profileimgurl'] = user.profile_image_url
            user_json['location'] = user.location
            user_json['timezone'] = user.time_zone
            user_json['creationdate'] = str(user.created_at)
            user_json['description'] = user.description
            user_json['followers'] = user.followers_count
            user_json['following'] = user.friends_count
            user_json['numtweets'] = user.statuses_count
            user_json['numfavorites'] = user.favourites_count
            user_json['numlisted'] = user.listed_count
            
            profile_file.write(json.dumps(user_json))
        
        except Exception as e:
            
            print "User id...\t" + str(e) + "\t" + login + "\t" + str(oauth_keys_index)  
            
            if str(e) == "[{u'message': u'Sorry, that page does not exist.', u'code': 34}]" or str(e) == "[{u'message': u'User not found.', u'code': 50}]" or str(e) == "[{u'message': u'User has been suspended.', u'code': 63}]":
                shutil.rmtree(dir_path)
                os.mkdir(dir_path)
            else:
                shutil.rmtree(dir_path)
                sleep(60)

                Authorization([oauth_keys_array[oauth_keys_index]])
                oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)

            continue

        ####################################################################################
        # Friends
        try:
                     
            if RateLimitChecker():
                Authorization([oauth_keys_array[oauth_keys_index]])
                oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
            
            friends = Tweeapi.friends_ids(screen_name=login)
            friend_file.write(json.dumps(friends) + "\n")
                    
        except Exception as e:
            
            print "Friends...\t" + str(e) + "\t" + login + "\t" + str(oauth_keys_index)          
            os.remove(friend_path)
            
            if str(e) == "Not authorized.":
                os.remove(follower_path)
                os.remove(tweet_path)              
                continue
            else:
                sleep(60)
        
        ####################################################################################
        # Followers
        try: 
            
            if RateLimitChecker():
                Authorization([oauth_keys_array[oauth_keys_index]])
                oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
                
            followers = Tweeapi.followers_ids(screen_name=login)
            follower_file.write(json.dumps(followers) + "\n")
            
        except Exception as e:
            
            print "Followers...\t" + str(e) + "\t" + login
            os.remove(follower_path)
            sleep(60)
        
        ####################################################################################
        # Timeline              
        page = 1
        while page <= 160:            
            try:
                if RateLimitChecker():
                    Authorization([oauth_keys_array[oauth_keys_index]])
                    oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
                
                timeline_list = Tweeapi.user_timeline(screen_name=login, count=20, page=page)                                
                if len(timeline_list) > 0:
                    
                    for status in timeline_list:
                        
                        tweet = {}                        
                        tweet["coordinates"] = status.coordinates
                        tweet["created_at"] = str(status.created_at)
                        tweet["entities"] = status.entities
                        tweet["favorite_count"] = status.favorite_count
                        tweet["id_str"] = status.id_str
                        tweet["in_reply_to_screen_name"] = status.in_reply_to_screen_name
                        tweet["in_reply_to_status_id_str"] = status.in_reply_to_status_id_str
                        tweet["in_reply_to_user_id_str"] = status.in_reply_to_user_id_str
                        tweet["lang"] = status.lang                                             
                        tweet["retweet_count"] = status.retweet_count
                        tweet["retweeted"] = status.retweeted
                        tweet["source"] = status.source
                        tweet["text"] = status.text
                        tweet["truncated"] = status.truncated                        
                        
                        tweet_file.write(json.dumps(tweet) + "\n")
                else:                    
                    break
        
            except Exception as e:
                
                print "Timeline...\t" + str(e) + "\t" + login + "\t" + str(oauth_keys_index)

                missing_record_file.write(learner + "\t" + login + "\t" + str(page) + "\n")
                sleep(60)

                Authorization([oauth_keys_array[oauth_keys_index]])
                oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)

            page += 1   
        
        if os.path.exists(profile_path): 
            profile_file.close()
        if os.path.exists(profile_path):
            friend_file.close()
        if os.path.exists(follower_path): 
            follower_file.close()
        
        tweet_file.close()
        
    missing_record_file.close()
    
    
def GatherDownloaderList(path):
    
    downloader_set = set()
    
    files = os.listdir(path + "twitter/download/")
    for file in files:
        if file != ".DS_Store":
            downloader_set.add(file)
    
    print "# downloaders is:\t" + str(len(downloader_set))
       
    output_path = path + "twitter/downloader_list"
    output_file = open(output_path, "w")
    for downloader in downloader_set:
        output_file.write(downloader + "\n")
    output_file.close()
    
def CleanDownloaderFolders(path):
    
    matcher_set = set()
    
    # Read EdX learners
    edx_path = path + "course_metadata/course_email_list"
    edx_learners_set, edx_learners_map = ReadEdX(edx_path)
    
    # Read Directly-matched EdX learners
    matching_results_path = path + "latest_matching_result_0"
    matching_results_file = open(matching_results_path, "r")
    jsonLine = matching_results_file.read()
    matching_results_map = json.loads(jsonLine)
    matching_results_file.close()
    
    # Gather the unmatched twitter learners
    for learner in matching_results_map.keys():
        if "twitter" in matching_results_map[learner]["checked_platforms"]:
            if learner in edx_learners_set:
                for link_record in matching_results_map[learner]["matched_platforms"]:
                    url = link_record["url"].replace("https://twitter.com/","").replace("http://twitter.com/", "").replace("http://www.twitter.com/", "")
                    platform = link_record["platform"]
                    
                    if platform == "twitter":
                        matcher_set.add(learner)

    # Read fuzzy matching results
    fuzzy_matching_results_path = path + "twitter/fuzzy_matching"
    
    fuzzy_matching_results_file = open(fuzzy_matching_results_path, "r+")
    lines = fuzzy_matching_results_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        array = line.split("\t")
        
        learner = array[0]
        login = array[1]
        
        if learner in edx_learners_set and login != "":
            matcher_set.add(learner)
            
    print "# matchers is:\t" + str(len(matcher_set))
    
    num = 0
    
    # Collect downloaded folders
    download_path = path + "twitter/download/"
    folders = os.listdir(download_path)
    for folder in folders:
        if folder != ".DS_Store":
            
            folder_path = path + "twitter/download/" + folder
            files = os.listdir(folder_path)
            
            # Step 1 - Empty folder
            # if len(files) == 0:
            #    num += 1
            #    shutil.rmtree(folder_path)
            
            # Step 2 - Missing profile folder
            # if len(files) != 0 and "profile" not in files:
            #    num += 1
            
            # Step 3 - Empty profile folder
            # profile_path = folder_path + "/profile"
            # if len(files) != 0:
            #    size = os.path.getsize(profile_path)
            #    if size == 0:
            #        num += 1
            #        shutil.rmtree(folder_path)
            
            # Step 4 - Missing tweet/friend/follower folder
            # if len(files) not in [0, 1]:
            #    if "tweet" not in files:
            #        num += 1
            #        #shutil.rmtree(folder_path)
    print num
    
def CrawlMissingTweets(path):
    
    # 1. Read missing records
    missing_map = {}
    
    missing_path = path + "twitter/missing_record"
    missing_file = open(missing_path, "r")
    lines = missing_file.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        learner = array[0]
        login = array[1]
        page = int(array[2])
        
        if learner not in missing_map.keys():
            missing_map[learner] = {"login": login, "pages": set()}
        
        missing_map[learner]["pages"].add(page)
        
        # output_path = path + "twitter/download/" + learner + "/tweet"
        # if not os.path.exists(output_path):
        #     print output_path
        
    # Angus
    oauth_keys_array = [['ImxPrCI2dwPhrVP6F7MT3xXpl',
                    'jJpQ2gRGM31SHs5w1YhyZX7SPrkSu86PVhRfFwG5GGimZo81nE',
                    '2983438302-TqEZPHeTtWHSYRfDi2oJzxfmLkzrSH99QXe1dpd',
                    'SM6azouMW3bddVcwIlKuFqaWJB6bU4Opv6o76NaZZNpYB'],
                        ['mwZUwO6dKLVKZ5tEN8XrvDCzd',
                    'lVzAMYefJu7SkPhY7FQEAlSUVtXvZTY1DGRrWPJS1YIFLeMy3h',
                    '1910920183-hNwZ8oGQK2hYkb4zqdapwf8vup3MYzHEixhJ1Os',
                    'p5vECFddZL2sD2PKwmOAFvwYBRsXTv5sTsVRxaXXoahoT'],
                        ['L4AJQZxi3lsASdZHqoHjM1Ekp',
                    'lGM4BRDjz9q3bPyAMsC2Jb91N3jBJwEXAmx0g1NHCMFvACXquK',
                    '425354456-egNrCHBMH2ccvh0FCsydXGw3ehWsH0l8heDnFWDK',
                    'cfwfs0MItaWQYPx7VrTOuX5seWme9bp3J6RWggI0zSTR1'],
                        ['Tgz8p3FsxN270Gln7njDofb7I',
                    'qdUqd1h9FcxHeyZXp7NDBDmoqlGs05B0vGPTlLWCWfiEFSKfwy',
                    '143669555-WkABdpANapIOWLK6wbuWO47OWjeUyJcFXE0eAZUI',
                    'IWUyGNZqC7dCBJL7KoO7Eo0NSK4nTQtWDVFlDRXxK6ibk'],
                        ['9azUHgStBSOKWwPBzfuUw',
                    'INy2xH4hFwygEtogjH1EPyCdX3afulI2uwiLdO6l8g',
                    '1903967041-h9D8HAWxvKIYyWqDokNmznt2ZgPVZh0UPwPMLyI',
                    'XjWcNLh5ewUJ7hvpZUFi6jEjr4uemHgumeEYBkiT7s'],
                        ['FXgOekK0CoEinGU8LmsgybjzD',
                    'nw15kFsp2oazLH80lwpxg1DHNnL1sBHQkdUv1thDPn7Z1iMQEM',
                    '3293907658-chE7Uk3MrtefqloCj2MiKe844emq7IqmEJgIgbY',
                    'IbeiTuZJBYyojEesqC1eIjln30mQDSciIPi1BAh7vZT8m'],
                        ['gbUz0S7lKu1MTIsxvrNOFajbX',
                    '4d7szxQAl7St3IE6wyB8L7j0qA9R0BeTvzZMekGm4LKHjGUUXN',
                    '1266120740-0SSYNx4Go3nB6IWInSqpVf6UddnIlgnkNTTRiXz',
                    'LGaZVTmC9iVuWdPt8QnmPdeVZgMNgccj0zwjJ6zFgwJTo'],
                        ['ErKWTGkbB1GCi0jpruA9zs7mf',
                    'bg8yusuSRFPvDIrtMO5s1UcwPSgcwKHoehqwuc74YLRKcXLyLM',
                    '2277305762-Ft5G0RncltTkfyhGXcvbYVryTwEdPEnGwdru3B0',
                    '6Mgl9Wg2Sv3Y6Js2IemZt0VDQ5RlTPtXq3JeYkHv27Ixn'],        
                        ]

    oauth_keys_index = 0
    Authorization([oauth_keys_array[oauth_keys_index]])
    oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
    
    # 2. Crawl missing records
    while len(missing_map) != 0:
        
        record = missing_map.popitem()
        
        learner = record[0]
        login = record[1]["login"]
        pages = record[1]["pages"]
        
        output_path = output_path = path + "twitter/download/" + learner + "/tweet"
        
        folder_mark = False
        if os.path.exists(output_path):
            folder_mark = True
        
        output_file = open(output_path, "a+")
        
        while len(pages) != 0:
            
            page = pages.pop()
            
            try:
                if RateLimitChecker():
                    Authorization([oauth_keys_array[oauth_keys_index]])
                    oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
                
                timeline_list = Tweeapi.user_timeline(screen_name=login, count=20, page=page)                                
                if len(timeline_list) > 0:
                    
                    for status in timeline_list:
                        
                        tweet = {}                        
                        tweet["coordinates"] = status.coordinates
                        tweet["created_at"] = str(status.created_at)
                        tweet["entities"] = status.entities
                        tweet["favorite_count"] = status.favorite_count
                        tweet["id_str"] = status.id_str
                        tweet["in_reply_to_screen_name"] = status.in_reply_to_screen_name
                        tweet["in_reply_to_status_id_str"] = status.in_reply_to_status_id_str
                        tweet["in_reply_to_user_id_str"] = status.in_reply_to_user_id_str
                        tweet["lang"] = status.lang                                             
                        tweet["retweet_count"] = status.retweet_count
                        tweet["retweeted"] = status.retweeted
                        tweet["source"] = status.source
                        tweet["text"] = status.text
                        tweet["truncated"] = status.truncated                        
                        
                        output_file.write(json.dumps(tweet) + "\n")
                else:                    
                    break
                
            except Exception as e:
                
                print "Timeline...\t" + str(e) + "\t" + login + "\t" + str(oauth_keys_index)
                
                if str(e) == "Not authorized.":
                    pages.clear()
                    if not folder_mark:
                        os.remove(output_path)
                    
                Authorization([oauth_keys_array[oauth_keys_index]])
                oauth_keys_index = (oauth_keys_index + 1) % len(oauth_keys_array)
            
        if len(pages) != 0:
            missing_map[learner] = {"login": login, "pages": pages}
            
        if os.path.exists(output_path):
            output_file.close()
            
    
    
    for learner in missing_map.keys():
        array = []
        for page in missing_map[learner]["pages"]:
            array.append(page)
        missing_map[learner]["pages"] = array
    
    print json.dumps(missing_map)
        
        
            
    
    

#################################################################################
path = "/Volumes/NETAC/LinkingEdX/"
DownloadPage(path)
#GatherDownloaderList(path)
#CleanDownloaderFolders(path)
#CrawlMissingTweets(path)
print "Finished."
    
        
    

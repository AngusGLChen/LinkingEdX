'''
Created on Nov 23, 2015

@author: Angus
'''

import urllib, urllib2
from lxml import html
import requests

import stackexchange
from time import sleep

def SearchStackExchange2():
    
    so = stackexchange.Site(stackexchange.StackOverflow, "tlgwyuns3SvFf5thJ7Hpkw((")
    
    so.impose_throttling = True
    # so.throttle_stop = False
    
    results = so.users_by_name("angus", **{"filter":""})
    print results
    results = results.fetch()
    
    print len(results)

    i = 0
    for i in range(len(results)):
        '''
        d = { 
            'id':item.id, 
            'display_name':item.display_name, 
            'url':item.url, 
            'website':item.website_url
        }
        '''
        print str(i) + "\t" + results[i].display_name + "\t" + results[i].url
        sleep(0.2)
    
    
def SearchStackExchange():
    
    url = "https://api.stackexchange.com/2.2/users?order=desc&sort=reputation&inname=kevin&site=stackoverflow"
    page = requests.get(url)
    content = page.content.replace("\/", "\\\/")
    print content
    
    
       
   
    
    
SearchStackExchange()
print "Finished."

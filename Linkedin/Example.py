'''
Created on Dec 2, 2015

@author: Angus
'''

from linkedin import linkedin

'''
API_KEY = '77069y1u0wk2at'
API_SECRET = 'JT3qR06QloDMoKvB'
RETURN_URL = 'http://www.wis.ewi.tudelft.nl/'

authentication = linkedin.LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL, ['rw_company_admin','r_basicprofile','r_emailaddress'])

print authentication.authorization_url  # open this url on your browser



authentication.authorization_code = 'AQT6ZCKiMHUHCmam2GjPMnPKpNnkhuwqqZelgFF8V5nQvv_78I9qs4HmXGHxcDxXwFzsnDp_1x6A6V40yw6TQn7uq3pGqKy8NPQhksJNdM5oA__T3YE'

token = authentication.get_access_token()

application = linkedin.LinkedInApplication(token)

# print "Finished."
'''

import urllib2

file = urllib2.urlopen('https://www.linkedin.com/vsearch/f?type=all&keywords=' + 'geert-jan&orig=GLHD&rsid=4648513461449138556857&pageKey=voltron_federated_search_internal_jsp&trkInfo=tarId%3A1449138571003&search=Search')

print file.read()
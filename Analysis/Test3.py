'''
Created on Nov 29, 2015

@author: Angus
'''

import requests
from lxml import html


'''
# Read file
path = "/Users/Angus/Downloads/github/dump/users.csv"
i = 0
input = open(path, "r")
lines = input.readlines()
for line in lines:
    #print line
    i += 1
    #if i > 30:
    #    break
print i

# Read large data file
path = "/Users/Angus/Downloads/mysql-2013-10-12.sql"
input_file = open(path, "r")
for line in input_file:
    sub = line[0: 100]
    print sub
    
input_file.close()
'''

url = "www.linkedin.com/in/tejasbondre"

page = requests.get(url)
tree = html.fromstring(page.content)

link = tree.xpath('//a[@class="u-textUserColor"]/@title')[0]
# pic
pic_link = tree.xpath('//img[@class="ProfileAvatar-image "]/@src')[0]
# full_name
# link = tree.xpath('//h1[@class="ProfileHeaderCard-name"]/a/text()')[0]
# login
# link = tree.xpath('//h2[@class="ProfileHeaderCard-screenname u-inlineBlock u-dir"]/a/span/text()')[0]

pic = urllib2.urlopen(pic_link)
output = open("/Users/Angus/Downloads/kk.jpg", "wb")
output.write(pic.read())

print link
print pic_link
            
'''
Created on Jan 7, 2016

@author: Angus
'''

import os
from lxml import html

path = "/Volumes/NETAC/LinkingEdX/linkedin/download/"
files = os.listdir(path)
for file in files:
    page = open(path + file, "r").read()
    tree = html.fromstring(page)
print "Finished."

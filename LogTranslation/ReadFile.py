'''
Created on Aug 29, 2015

@author: Angus
'''

def ReadFile(path):

    fp = open(path)    
   
    for i in range(100):
        print fp.readline()
        
        

#######################################################
path = "/Volumes/NETAC/StackOverflow/Dataset/Posts.xml"
ReadFile(path)
print "Finished."

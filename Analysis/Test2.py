'''
Created on Nov 22, 2015

@author: Angus
'''

'''
def CrawlStackExchange(email, url, path):
    
    return_link = ""
    
    try:
        page = requests.get(url)
        tree = html.fromstring(page.content)
    
        return_link = tree.xpath('//a[@class="url"]/@href')[0]
        pic_link = tree.xpath('//img[@class="avatar-user"]/@src')[0]
    
        if pic_link != "":
            pic = urllib2.urlopen(pic_link)
            
            output_path = path + "profile_pics/" + email + "/"
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
            
            output = open(output_path + "stackexchange.jpg", "wb")
            output.write(pic.read())
        
        retrun (True, return_link)
            
    except Exception as e:
        
        print str(email) + "\t" + str(e)
        return (False, return_link)

path = "/Users/Angus/Downloads/"
email =
'''

import mysql.connector

cnx = mysql.connector.connect(user='root', password='Fa8j9tn4dBBxwx3V',
                             host='145.100.59.223',
                             database='DelftX')

print "Finished."
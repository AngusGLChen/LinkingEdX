'''
Created on Dec 20, 2015

@author: Angus
'''

from PIL import Image

def ReadEdX(path):
    
    edx_learners_map = {}
    edx_learners_set = set()
    
    input = open(path, "r")
    lines = input.readlines()
    for line in lines:
        array = line.replace("\n", "").split("\t")
        course_id = array[0]
        email = array[1]
        login = array[2]
        name = array[3]
        
        if email in edx_learners_set:
            edx_learners_map[email]["courses"].append(course_id)
        else:
            edx_learners_set.add(email)
            edx_learners_map[email] = {"login":login, "name": name, "courses":[course_id]}
        
    input.close()
            
    return (edx_learners_set, edx_learners_map)

def CompareImages(img1, img2):
        
    hash1 = avhash(img1)
    hash2 = avhash(img2)
        
    dist = hamming(hash1, hash2)        
    similarity = (36 - dist) / 36
        
    if similarity >= 0.9:
        return True
    else:
        return False
    
def avhash(im):
    
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    
    im = im.resize((6, 6), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 36.
    return reduce(lambda x, (y, z): x | (z << y),
                  enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                  0)

def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

#!/usr/bin/python
# -*- coding: utf8 -*-

import requests
from bs4 import BeautifulSoup
import time
import threading


class P():    
    
    proxiesqueue = []


class Proxy(object):

    """docstring for Proxy"""

    def __init__(self,):
        super(Proxy, self).__init__()

        self.myheader = {
            "Host": "www.proxy-ip.cn",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0",
            "Accept": "image/png,image/*;q=0.8,*/*;q=0.5",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://www.proxy-ip.cn/guoji",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest"
        }

    def getdata(self, ):
        # ips, ports, speeds = [], [], []

        pagenum = 0
        # print "start to climb proxy"
        speed = 0
        while True:
            if int(speed) > 1000:
                break
            pagenum += 1
            time.sleep(1)
            url = "http://www.proxy-ip.cn/guoji/%s" % pagenum
            try:
                r = requests.get(url, timeout=5)
            except:
                pagenum -= 1
                continue
            # print r.url
            html = r.content
            soup = BeautifulSoup(html, 'lxml')
            proxy_table = soup.find("table", {"class": "content_table"})
            items = proxy_table.find_all("tr")
            for item in items[2:]:
                tds = item.find_all("td")
                ip = tds[0].get_text().split(";")[-1].strip()
                port = tds[1].get_text().split(";")[-1].strip()
                speed = tds[-1].get_text().split("m")[0].strip()
                # proxy = "http://" + ip + ":" + port
                proxy = ip + ":" + port
                # print proxy
                P.proxiesqueue.append(proxy)
                # print proxy
                # print proxiesqueue.qsize(), "++++"
            try:
                speed = int(speed)
            except:
                break

        # return ips, ports, speeds


def outputproxy():
    try:
        # print "Length is:\t" + str(len(P.proxiesqueue))
        raw_proxy = P.proxiesqueue.pop(0)
        proxy = {"http": raw_proxy}
        # return proxy
        return raw_proxy
    except:
        Proxy().getdata()
        outputproxy()
'''
# print raw_proxy, "\ttimeout"

if __name__ == '__main__':
    for i in range(1000):
        print "i is:\t" + str(i)
        print outputproxy()
        
print "Finished."
'''

def GetProxyList():
    proxy_list = []
    print "\nStart to crawl proxies..."
    while len(proxy_list) != 50:
        proxy = outputproxy()
        if proxy != None:
            proxy_list.append(proxy)
    print "# proxies is:\t" + str(len(proxy_list)) + "\n"
    return proxy_list


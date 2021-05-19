from bs4 import BeautifulSoup
import threading
import requests
import time
import re


TAG_RE = re.compile(r'<[^>]+>')

def sanatize(text):
    return TAG_RE.sub('', text)

class searcher():
  def __init__(self,cache,limit=10,domain='',replace={}):
    self.limit = limit
    self.domain = domain
    self.replace = replace
    self.cache = {}
    self.cacheTime = cache
    self.data = None
  def search(self,query):
    address = "http://www.bing.com/search?q=%s" % (query)

    getRequest = requests.get(address, headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'})
    #print(getRequest.status_code)
    htmlResult = getRequest.text
    #print(htmlResult)
    soup = BeautifulSoup(htmlResult,features="html5lib")

    [s.extract() for s in soup('span')]
    unwantedTags = ['strong', 'cite']
    for tag in unwantedTags:
        for match in soup.findAll(tag):
            match.replaceWithChildren()
    results = soup.findAll('li', { "class" : "b_algo" })
    rank = 1
    end = []
    for result in results:
            rank += 1
            url = str(result.find('h2')).replace(" ", " ").split('href="')[1].split('"')[0]
            for i in self.replace:
              url = url.replace(i,self.replace.get(i))
            if(self.domain in url):
              if(rank==self.limit):
                break
              rank+=1
              title = str(result.find('h2')).replace(" ", " ").split('>')[2].split('<')[0]
              temp = {'title':title,'rank':rank,'description':sanatize(str(result.find('p')).replace("\xa0", " ")),'url':url,'ad':False}
              end.append(temp)
    return end

if __name__=='__main__':
    print('________________________')
    print(search(input('>> ')))

from flask import Flask, g, request, render_template, abort
from spellchecker import SpellChecker as sc
from gevent.pywsgi import WSGIServer
from searchbing import searcher
from filterWords import filter
from datetime import date
import threading
import repltalk
import requests
import asyncio
import secrets
import flask
import glob
import time
import json
import os
client = repltalk.Client()


adList = json.loads(requests.get('https://raw.githubusercontent.com/Codemonkey51/crawl-data/master/data3.json').text)
ads = []
for i in adList:
  i['description']=str(i['description'])
  i['title'] = str(i['title'])
  ads.append(i)
adList = ads
class CacheSite:
  def __init__(self,**data):
    self.data = data['data']
    self.query = data['query']
    self.link = data['link']
    self.length = data['length']
    self.neededSpell = data['spellChecked']
    self.checked = data['checked']
    self.phrase2 = data['phrase2']

KEY = secrets.token_hex()

app = Flask('Search')

app.config['SECRET_KEY'] = KEY

cache = {}
sc = sc()
#print(searcher(10,{}).search('lol'))
def spellCheck(phrase,t = 'norm'):
  
  words = phrase.split(' ')
  misspelled = sc.unknown(words)
  if(len(misspelled)==0):
    return(True)
  for i in misspelled:
    if(t=='norm'):
      phrase = phrase.replace(i,sc.correction(i))
    else:
      phrase = phrase.replace(i,'"%s"'%(i))
  return(phrase)
def clearCache(key):
  global cache
  time.sleep(120)
  del cache[key.lower()]
searcher = searcher(10,120,'repl.it',{'staging.repl.it':'repl.it'})

@app.context_processor
def utility_processor():
    def python(code):
      return(None)#exec(code))
    return dict(execCode=python)
 
@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)
def error_403():
    return "<head><title>403 Forbidden</title></head><body><h1>Forbidden</h1><p>You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.</p></body>", 403
@app.route('/')
def _main():
  return render_template('home.html')
@app.route('/clear')
def _clear():
  global cache
  if(request.args.get('pass')==os.getenv('clearPass')):
    del cache
    cache = {}
    return('done')
  #return error_403()
  return error_403()

@app.route('/signup')
def _signup():
  return render_template('signup.html')
@app.route('/search')
def _search():
  global cache
  args = request.args
  #return render_template('temp.html')
  #try:
  if True:
    query = args['search'].lower()
    if(query.lower() in cache):
      data = cache.get(query)
      return(_searchRender(query,data,False))
      #return render_template('temp.html',link=data,length=len(data),search=query)
    #data = searcher.search('site="repl.it" '+ query)
    #cache.update({query:data})
    #threading.Thread(None,clearCache,args=(query,)).start()
    return(_searchRender(query,[]))#data))
  #except KeyError:
  #  return(render_template('invalid.html'))


def _searchRender(query,data,setcache=True,ads=[]):
  global cache
  if(setcache):
    adlen = 0
    ads = adList
    temp = []
    for i in ads:
      i['ad'] = False
      if(i['keywords']==None):
        i['keywords'] = ''
      if(query.lower() in i['description'].lower() or query.lower() in i['title'].lower() or query.lower() in i['keywords'].lower().split(',')):
        data.insert(0,i)
      #adlen += 1
    l = open('ads/crawl.json','w+')
    l.write(json.dumps(temp))
    l.close()
    ads = glob.glob("ads/*.json")
    for i in ads:
      temp = open(i,'r')
      i = json.load(temp)
      temp.close()
      for j in i:
        print(j)
        if(query.lower() in j['title'].lower() or query.lower() in j['description'].lower()):
          print('Hurray! It's add time!')
          j['ad']=True
          data.insert(0,j)
          adlen += 1
    l = open('ads/crawl.json','w+'); l.write(''); l.close()
    neededSpell = True
    temp = spellCheck(query)
    if(temp==True):
      neededSpell = False
    phrase2 = spellCheck(query,'lol')
    if(not isinstance(phrase2,bool)):
      if(phrase2.replace('"','')==temp.replace('"','')):
        neededSpell = False
    temp = CacheSite(data=data,link=data,length=len(data),spellChecked=neededSpell,query=query,checked=temp,phrase2=phrase2)
    cache.update({query.lower():temp})
    threading.Thread(None,clearCache,args=(query,)).start()
    return useCachedResponse(temp)
    #return render_template('temp.html',link=data,length=len(data)-len(ads),spellChecked=neededSpell,search=query,checked=temp,phrase2=phrase2,)
  else:
    return useCachedResponse(cache.get(query.lower()))

def useCachedResponse(cached):
  data = cached.data
  length = cached.length
  neededSpell = cached.neededSpell
  query = cached.query
  checked = cached.checked
  phrase2 = cached.phrase2
  return render_template('temp.html',link=data,length=length,spellChecked=neededSpell,search=query,checked=checked,phrase2=phrase2,)
  
  
class Log:
  def __init__(self,function=date.today,format="%Y-%m-%d"):
    self.function = function
    self.format=format
  def write(self,data):
    if('/ping HTTP/1.1' in data or '/clear' in data):
      pass
    else:
      #open('logs/'+self.function().strftime(self.format),'a+').write(data)
      print('\u001b[31m'+data[:len(data)-1]+'\u001b[0m')
      
def startTrack():
  http_server = WSGIServer(('0.0.0.0', int(8080)), app,log=Log())
  http_server.serve_forever()

startTrack()

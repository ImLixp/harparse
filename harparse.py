import json
import re
from http import client
from urllib import parse
import json
import gzip
from io import BytesIO


def jsonDump(obj):
    return json.dumps(obj, separators=(',',':'))

def jsonLoad(jstr):
    return json.loads(jstr)

def gzdecode(data) :
    compressedstream = BytesIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)  
    data2 = gziper.read()
    return data2

def HttpsReq(host, method, url, body=None, header={}):
    conn=client.HTTPSConnection(host)
    conn.request(method, url, body, header)
    res=conn.getresponse()
    if res.status == 301:
        return {"status":"wait"}
    if res.status:
        compress = res.getheader('content-encoding')
        cookie = res.getheader('Cookie')
        if cookie != None:
            header['Cookie']=cookie
        if compress == "gzip":
            de = gzdecode(res.read())
            return json.loads(de, encoding="UTF-8")
        else:
            a = res.read()
            print(a)
            return json.loads(res.read(),encoding="UTF-8")

class HARRequest(object):
    def __init__(self, request):
        url = parse.urlparse(request['url'])
        self.__url = None
        self.__scheme = url.scheme
        self.__host = url.netloc
        self.__path = url.path
        self.__method = request['method']
        self.__header = {}
        self.__postdata = None
        postdata = request.get('postData')
        if postdata is not None:
            self.__postdata = postdata['text']
        for head in request['headers']:
            self.__header[head['name']] = head['value']
        self.__cookies = {}
        for cookie in request['cookies']:
            self.__cookies[cookie['name']] = cookie['value']
        self.__queryString = {}
        for queryString in request['queryString']:
            self.__queryString[queryString['name']] = queryString['value']
    def url(self):
        return self.__scheme + '://' + self.__host + self.__path + self.encodeQueryString()
    def method(self):
        return self.__method
    def headers(self):
        return self.__header
    def header(self, name):
        return self.__header.get(name)
    def cookies(self):
        return self.__cookies
    def cookie(self, name):
        return self.__cookies.get(name)
    def queryStrings(self):
        return self.__queryString
    def queryString(self, name):
        return self.__queryString.get(name)
    def postData(self):
        return self.__postdata
    def setPostData(self, _postData):
        self.setHeader('Content-Length', len(_postData))
        self.__postdata = _postData
    def setHeader(self, name, value):
        self.__header[name] = value
    def setCookie(self, name, value):
        self.__cookies[name] = value
    def setQueryString(self, name, value):
        self.__queryString[name] = value
    def encodeCookie(self):
        cookies = ''
        for key in self.__cookies:
            if cookies == '':
                cookies = key + '=' + self.__cookies[key]
            else:
                cookies += '; ' + key + '=' + self.__cookies[key]
        return cookies
    def encodeQueryString(self):
        queryString = ''
        for key in self.__queryString:
            if queryString == '':
                queryString = '?' + key + '=' + self.__queryString[key]
            else:
                queryString += '&' + key + '=' + self.__queryString[key]
        return queryString
    def update(self):
        self.__url = self.__scheme + '://' + self.__host + self.__path + self.encodeQueryString()
        self.setHeader('Cookies', self.encodeCookie())
    def request(self):
        self.update()
        return HttpsReq(self.__host, self.__method, self.__url, self.__postdata, self.__header)

class HAR(object):
    def __init__(self, harjson):
        f = open(harjson, 'r')
        har = json.load(f)
        f.close()
        entries = har['log']['entries']
        self.__requests = [] 
        for entry in entries:
            self.__requests.append(entry['request'])
    
    def SearchURL(self, method, regular):
        regular = re.compile(regular)
        for request in self.__requests:
            _url = request['url']
            _method = request['method']
            if method == None or method == _method:
                if regular.match(_url):
                    return HARRequest(request)
        return None

import harparse

harobj = harparse.HAR('har.json')

reqToken = harobj.SearchURL('POST', '.+token')
reqBuy = harobj.SearchURL('POST', '.+buy')

resp = reqToken.request()
print(resp['data'])
postdata = harparse.jsonLoad(reqBuy.postData())
postdata['token'] = resp['data']

raw = harparse.jsonDump(postdata)
reqBuy.setPostData(raw)
resp = reqBuy.request()
print(resp)
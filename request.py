import urllib2
import json
import cv2
import base64
import numpy as np
import urllib
import sys

if sys.argv[1:]:
    imgpath = sys.argv[1]
else:
    imgpath = './test/1.jpg'
with open(imgpath,'rb') as fin:
    image_data = fin.read()
    base64data = base64.b64encode(image_data)
data = {
    'base64Img': base64data
}
headers = {'Content-Type': 'application/json'}
request = urllib2.Request(url='http://ns013x.corp.youdao.com:30008/searchq/ydocr')
response = urllib2.urlopen(request,urllib.urlencode(data))
ocrResult = json.loads(response.read())
recdata = {
	'imgbase64':base64data,
	'ocrResult':ocrResult
}
request = urllib2.Request(url='http://localhost:8080',data=json.dumps(recdata))
response = urllib2.urlopen(request)
print response.read()

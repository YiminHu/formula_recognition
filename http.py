from Tkinter import *
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer  
import io,shutil    
import urllib  
import os, sys
import MathRec
import json
import base64
import cv2
import numpy as np
import recImg
  
class MyRequestHandler(BaseHTTPRequestHandler):  
    def do_GET(self):  
        mpath,margs=urllib.splitquery(self.path) # ?分割  
        self.do_action(mpath, margs)  
  
    def do_POST(self):  
        mpath,margs=urllib.splitquery(self.path)  
        datas = self.rfile.read(int(self.headers['content-length']))  
        self.do_action(mpath, datas)  
  
    def do_action(self, path, args):             
            data = json.loads(args)
            imgData = base64.b64decode(data['imgbase64'])
            ocrResult = data['ocrResult']
            nparr = np.fromstring(imgData,np.uint8)
            img_np = cv2.imdecode(nparr,0)
            resultList = []
            try:
                resultList = recImg.recQuestion(img_np,ocrResult)
            except Exception,e:
                print 'My error', e
            #resultList = ["Asdasd","Sdsds","Dsdsds"]
            if len(resultList):
                code = 200
            else:
                code = 301
            data = {'code':code,'msg':"",'resultlist':resultList}
            resp = json.dumps(data)
            print resp
            self.outputtxt(resp)
            
    def outputtxt(self, content):  
        #指定返回编码  
        enc = "UTF-8"  
        content = content.encode(enc)            
        f = io.BytesIO()  
        f.write(content)  
        f.seek(0)    
        self.send_response(200)    
        self.send_header("Content-type", "text/html; charset=%s" % enc)    
        self.send_header("Content-Length", str(len(content)))    
        self.end_headers()    
        shutil.copyfileobj(f,self.wfile)  
Protocol     = "HTTP/1.0"
 
if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000
server_address = ('127.0.0.1', port)
server = HTTPServer(('localhost', 8080), MyRequestHandler)
print 'Starting server, use <Ctrl-C> to stop'
server.serve_forever()
 


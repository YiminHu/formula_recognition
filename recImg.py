#coding:utf-8
import urllib2
import json
import cv2
import base64
import numpy as np
import urllib
import sys
import MathRec
def rotate(image, angle, center=None, scale=1.0):
    (h, w) = image.shape[:2]
    if center is None:
        center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(center, angle, scale)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return rotated
def drawQuad(img, p1, p2, p3, p4):
    cv2.line(img,p1,p2,255,1)
    cv2.line(img, p2, p3, 255, 1)
    cv2.line(img, p3, p4, 255, 1)
    cv2.line(img, p4, p1, 255, 1)
def check_contain_chinese(check_str):
     for ch in check_str.decode('utf-8'):
         if u'\u4e00' <= ch <= u'\u9fff':
             return True
     return False
def findCutPoint(img):
    height,width = img.shape
    cutpos = width/2
    for i in range(width):
        cnt = 0
        for j in range(height):
            if img[j][i]!=255:
                cnt+=1
        if cnt == 0:
            cutpos = i
    return cutpos
def formulaCut(img):
    height, width = img.shape
    start = 0
    end = width
    headcnt = 0
    for i in range(height):
        if img[i][0]!=255:
            headcnt+=1
    if headcnt!=0:
        for i in range(width):
            cnt = 0
            for j in range(height):
                if img[j][i] != 255:
                    cnt += 1
            if cnt == 0:
                start = i
                break

    headcnt = 0
    for i in range(height):
        if img[i][width-1]!=255:
            headcnt+=1
    if headcnt!=0:
        for i in reversed(range(width)):
            cnt = 0
            for j in range(height):
                if img[j][i] != 255:
                    cnt += 1
            if cnt == 0:
                end = i
                break

    return start,end



def recQuestion(img,ocrResult):
    reload(sys)
    sys.setdefaultencoding('utf8')
    textAngle = float(ocrResult['data']['textAngle'])
    print textAngle
    img = rotate(img,-textAngle)
    ret, test_ex_bin = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resultList = []
    for item in ocrResult['data']['resRegions']:
        for lineitem in item['lines']:
            if len(lineitem['words'])==0:
                continue
            #print lineitem['boundingBox']
            startidx = 0
            hasQuestionNum = False
            print lineitem['words'][0]['word'].find(',')
            print '---------------'
            print 'shit'
            if (lineitem['words'][0]['word'].find(',') != -1 and lineitem['words'][0]['word'].find(',') < 4)or \
                    (lineitem['words'][0]['word'].find('.') != -1 and lineitem['words'][0]['word'].find('.') <4):
                hasQuestionNum = True
            if hasQuestionNum:
                startidx=1
            linestr = lineitem['text']
            for i in range(len(linestr)):
                if linestr[i]=='(':
                    for j in range(i+1,len(linestr)):
                        if linestr[j]==')':
                            for k in range(i+1,j):
                                if check_contain_chinese(linestr[k]):
                                    startidx = j+1
            print startidx
            print 'startindex'+linestr[startidx]
            p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y = lineitem['boundingBox'].split(',')
            p1x = int(p1x)
            p2x = int(p2x)
            p3x = int(p3x)
            p4x = int(p4x)
            p1y = int(p1y)
            p2y = int(p2y)
            p3y = int(p3y)
            p4y = int(p4y)
            drawQuad(img,(p1x,p1y),(p2x,p2y),(p3x,p3y),(p4x,p4y))
            cutPoint = []
            for i in range(len(lineitem['words'])):
                print lineitem['words'][i]['word'][0]
                if lineitem['words'][i]['word'][0]==linestr[startidx]:
                    startidx=i
                    break
            print startidx
            for i in range(startidx,len(lineitem['words'])-1):
                print check_contain_chinese(lineitem['words'][i]['word'])
                print check_contain_chinese(lineitem['words'][i+1]['word'])
                if (check_contain_chinese(lineitem['words'][i]['word'])==True and check_contain_chinese(lineitem['words'][i+1]['word'])==False) or \
                        (check_contain_chinese(lineitem['words'][i]['word']) == False and check_contain_chinese(lineitem['words'][i + 1]['word']) == True):
                    print lineitem['words'][i]['word']+' '+lineitem['words'][i+1]['word']
                    startx = int(lineitem['words'][i]['boundingBox'].split(',')[2])
                    endx = int(lineitem['words'][i+1]['boundingBox'].split(',')[0])
                    starty = p1y
                    endy = p3y
                    cutpos = findCutPoint(test_ex_bin[starty:endy,startx:endx])
                    print startx+cutpos
                    cutPoint.append(startx+cutpos)

            if check_contain_chinese(lineitem['words'][startidx]['word']) == False and len(cutPoint)!=0:
                cutPoint.append(int(lineitem['words'][startidx]['boundingBox'].split(',')[0]))
            if check_contain_chinese(lineitem['words'][len(lineitem['words'])-1]['word']) == False and len(cutPoint)!=0:
                print lineitem['words'][len(lineitem['words'])-1]['word']
                cutPoint.append(int(lineitem['boundingBox'].split(',')[2]))
            if len(cutPoint)==0:
                cutPoint.append(p1x)
                cutPoint.append(p2x)

            for i in range(len(cutPoint)):
                print cutPoint[i]
                #cv2.line(img,(cutPoint[i],p1y),(cutPoint[i],p3y),0,5)

            print '--------'
            print len(cutPoint)
            cutPoint = sorted(cutPoint)
            for i in range(0,len(cutPoint),2):
                formulaimg = img[p1y:p3y,cutPoint[i]:cutPoint[i+1]]
                ret, test_ex_bin = cv2.threshold(formulaimg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                sx,ex = formulaCut(test_ex_bin)
                print sx,ex
                print '======='
                result = MathRec.recline(formulaimg[:,sx:ex])
                if len(result) > 4:
                    resultList.append(result)
                cv2.imwrite(str(i)+str(len(lineitem['words']))+'test.jpg',formulaimg[:,sx:ex])

            for worditem in lineitem['words']:
                print worditem['word']
                #print check_contain_chinese(worditem['word'])
                p11x, p11y, p22x, p22y, p33x, p33y, p44x, p44y = worditem['boundingBox'].split(',')
                #print p11x, p11y, p22x, p22y, p33x, p33y, p44x, p44y
                p11x = int(p11x)
                p22x = int(p22x)
                p33x = int(p33x)
                p44x = int(p44x)
                p11y = int(p11y)
                p22y = int(p22y)
                p33y = int(p33y)
                p44y = int(p44y)
                drawQuad(img, (p11x, p11y), (p22x, p22y), (p33x, p33y), (p44x, p44y))
    return resultList

    cv2.imwrite('tmp.jpg',img)
    print len(ocrResult['data']['resRegions'])



def main():
    imgpath = '/Users/MikeHu/desktop/3.jpg'
    with open(imgpath, 'rb') as fin:
        image_data = fin.read()
        base64data = base64.b64encode(image_data)
    data = {
        'base64Img': base64data
    }
    headers = {'Content-Type': 'application/json'}
    request = urllib2.Request(url='http://ns013x.corp.youdao.com:30008/searchq/ydocr')
    response = urllib2.urlopen(request, urllib.urlencode(data))
    ocrResult = json.loads(response.read())
    img = cv2.imread(imgpath, 0)
    result = recQuestion(img,ocrResult)
    for formula in result:
        print formula.decode()

if __name__ == '__main__':
    main()
from bounding import *
import time
import numpy as np
import cv2
from skimage.measure import label
import skimage
import sys


def recline(originimg):
    height, width = originimg.shape
    if height % 2 == 0:
        block = height + 1
    else:
        block = height
    # ret,test_ex_bin= cv2.threshold(test,127,255,0)
    # cv2.imwrite('test_bin.jpg',test_ex_bin)
    ret, test_ex_bin = cv2.threshold(originimg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # test_ex_bin = cv2.erode(test_ex_bin,erode_kernel)
    # test_ex_bin = cv2.dilate(test_ex_bin,erode_kernel)
    # test_ex_bin = cv2.resize(test_ex_bin,(2*327,2*67)
    # test_ex_bin = cv2.erode(test_ex_bin,kernel)
    poselist = []
    label_img = label(test_ex_bin, connectivity=2, background=255)
    props = skimage.measure.regionprops(label_img)
    index = 0
    tmpimg = originimg.copy()
    for p in props:

        miny, minx, maxy, maxx = p.bbox
        x = minx - 1
        if x < 0:
            x = 0
        y = miny - 1
        if y < 0:
            y = 0
        w = maxx + 1 - (minx - 1)
        h = maxy + 1 - (miny - 1)
        #print x, y, w, h
        if w * h > 20:
            cursymbol = SymbolPos()
            cursymbol.bb = (x, y, w, h)
            cursymbol.center = (y + h / 2, x + w / 2)
            cv2.rectangle(tmpimg, (x, y), (x + w, y + h), (153, 153, 0), 1)
            newimage = originimg[y:y + h, x:x + w]
            newimage_bin = test_ex_bin[y + 1:y + h - 1, x + 1:x + w - 1]
            cnt = 0
            for m in range(h - 2):
                for n in range(w - 2):
                    if newimage_bin[m][n] == 0:
                        cnt = cnt + 1

            total = newimage_bin.shape[0] * newimage_bin.shape[1]

            if float(newimage_bin.shape[0]) / float(newimage_bin.shape[1]) < 0.3:
                #print 'line---------------------------'
                cursymbol.isline = True
            elif float(cnt) / float(total) > 0.65 and \
                    (float(newimage_bin.shape[0]) / float(newimage_bin.shape[1]) > 0.7 and float(
                        newimage_bin.shape[1]) / float(newimage_bin.shape[0]) > 0.7):
                cursymbol.isdot = True
            poselist.append(cursymbol)

    # center = findCenter(poselist)
    # cv2.line(tmpimg,(0,center),(width,center),(153,153,0),1)

    symbolcnt = len(poselist)
    #print 'lensym'
    #print symbolcnt
    for i in range(symbolcnt):
        ix, iy, iw, ih = poselist[i].bb
        curinclued = includeIn(poselist, ix, iy, iw, ih)
        if len(curinclued) != 0:
            poselist[i].isroot = True

    handleDotList = handleDot(poselist)
    #print 'lendot'
    #print len(handleDotList)
    handleLineList = handleLine(handleDotList, height)
    imgList = []

    #for i in reversed(range(len(handleLineList))):
    #   if handleLineList[i].bb[2] ==0 or handleLineList[i].bb[3]==0:
    #       handleLineList.remove(handleLineList[i])

    for recpos in handleLineList:
        if recpos.type != 'undefined':
            recpos.recognition = recpos.type
        if recpos.isroot == False and recpos.isline == False and recpos.isdot == False and recpos.type == 'undefined':
            rx, ry, rw, rh = recpos.bb
            recimage = originimg[ry:ry + rh, rx:rx + rw]
            print rx,ry,rh,rw
            imgList.append(recimage)
    classList = test.classify_img(imgList)
    index = 0
    for recpos in handleLineList:
        if recpos.isroot == False and recpos.isline == False and recpos.isdot == False and recpos.type == 'undefined':
            recpos.recognition =  classList[index]
            index+=1
    result = handleFormula(handleLineList, 0, height,True)
    return result


def recimg(originimg,img_name):
    height, width = originimg.shape
    if height % 2 == 0:
        block = height + 1
    else:
        block = height
    # ret,test_ex_bin= cv2.threshold(test,127,255,0)
    # cv2.imwrite('test_bin.jpg',test_ex_bin)
    ret, test_ex_bin = cv2.threshold(originimg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # test_ex_bin = cv2.erode(test_ex_bin,erode_kernel)
    # test_ex_bin = cv2.dilate(test_ex_bin,erode_kernel)
    # test_ex_bin = cv2.resize(test_ex_bin,(2*327,2*67)
    # test_ex_bin = cv2.erode(test_ex_bin,kernel)
    poselist = []
    label_img = label(test_ex_bin, connectivity=2, background=255)
    props = skimage.measure.regionprops(label_img)
    index = 0
    tmpimg = originimg.copy()
    for p in props:

        miny, minx, maxy, maxx = p.bbox
        x = minx - 1
        if x < 0:
            x = 0
        y = miny - 1
        if y < 0:
            y = 0
        w = maxx + 1 - (minx - 1)
        h = maxy + 1 - (miny - 1)
        #print x, y, w, h
        if w * h > 20:
            cursymbol = SymbolPos()
            cursymbol.bb = (x, y, w, h)
            cursymbol.center = (y + h / 2, x + w / 2)
            cv2.rectangle(tmpimg, (x, y), (x + w, y + h), (153, 153, 0), 1)
            newimage = originimg[y:y + h, x:x + w]
            newimage_bin = test_ex_bin[y + 1:y + h - 1, x + 1:x + w - 1]
            cnt = 0
            for m in range(h - 2):
                for n in range(w - 2):
                    if newimage_bin[m][n] == 0:
                        cnt = cnt + 1

            total = newimage_bin.shape[0] * newimage_bin.shape[1]

            if float(newimage_bin.shape[0]) / float(newimage_bin.shape[1]) < 0.3:
                #print 'line---------------------------'
                cursymbol.isline = True
            elif float(cnt) / float(total) > 0.65 and \
                    (float(newimage_bin.shape[0]) / float(newimage_bin.shape[1]) > 0.7 and float(
                        newimage_bin.shape[1]) / float(newimage_bin.shape[0]) > 0.7):
                cursymbol.isdot = True
            poselist.append(cursymbol)

    # center = findCenter(poselist)
    # cv2.line(tmpimg,(0,center),(width,center),(153,153,0),1)

    symbolcnt = len(poselist)
    #print 'lensym'
    #print symbolcnt
    for i in range(symbolcnt):
        ix, iy, iw, ih = poselist[i].bb
        curinclued = includeIn(poselist, ix, iy, iw, ih)
        if len(curinclued) != 0:
            poselist[i].isroot = True

    handleDotList = handleDot(poselist)
    #print 'lendot'
    #print len(handleDotList)
    handleLineList = handleLine(handleDotList, height)
    imgList = []

    #for i in reversed(range(len(handleLineList))):
    #   if handleLineList[i].bb[2] ==0 or handleLineList[i].bb[3]==0:
    #       handleLineList.remove(handleLineList[i])

    for recpos in handleLineList:
        if recpos.type != 'undefined':
            recpos.recognition = recpos.type
        if recpos.isroot == False and recpos.isline == False and recpos.isdot == False and recpos.type == 'undefined':
            rx, ry, rw, rh = recpos.bb
            recimage = originimg[ry:ry + rh, rx:rx + rw]
            print rx,ry,rh,rw
            imgList.append(recimage)
    classList = test.classify_img(imgList)
    index = 0
    for recpos in handleLineList:
        if recpos.isroot == False and recpos.isline == False and recpos.isdot == False and recpos.type == 'undefined':
            recpos.recognition =  classList[index]
            index+=1


    cv2.imwrite(img_name + "result/write.jpg", tmpimg)
    cv2.imwrite(img_name + "result/bin.jpg", test_ex_bin)

    result = handleFormula(handleLineList, 0, height,True)
    return result


def main():
    #reload(sys)
    #sys.setdefaultencoding('unicode')
    ts = time.time()
    img_name='/Users/MikeHu/desktop/test/bug1.jpg'
    img = cv2.imread(img_name,0)
    print recimg(img,img_name)
    te = time.time()
    print te-ts

if __name__ == '__main__':
    main()
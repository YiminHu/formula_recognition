#coding:utf-8
import cv2
import sys
import os
import numpy as np
import test
from skimage.measure import label
import skimage
def prn_obj(obj):
    print '\n'.join(['%s:%s' % item for item in obj.__dict__.items()])


class SymbolPos(object):
    def __init__(self):
        self.bb = None
        self.center = None
        self.isdot = False
        self.isline = False
        self.isroot = False
        self.type = 'undefined'
        self.recognition = 'a'
        self.handled = False
        self.issuper = False
        self.issub = False

def hasRoot(poselist):
    for symbolpos in poselist:
        if symbolpos.isroot == True:
            return True
    return False

def hasSls(poselist):
    for symbolpos in poselist:
        if symbolpos.type == 'sls':
            return True
    return False
def getRelativePos(bbox1,bbox2):
    return 'pad'
def handleSimpleFormula(poselist,hasscript):

    totalArea = 0
    symbolcnt = len(poselist)
    centerLine = 0
    for sym in poselist:
        totalArea+=sym.bb[2]*sym.bb[3]
        centerLine+=sym.bb[2]*sym.bb[3]*sym.center[0]
    centerLine/=totalArea

    avgArea = totalArea/symbolcnt
    for sym in poselist:
        starty = sym.bb[1]
        endy = sym.bb[1]+sym.bb[3]
        totalh =endy-starty
        if sym.isline == False:
            if centerLine > endy:
                sym.issuper=True
            elif centerLine < starty:
                sym.issub=True
            elif float(abs(centerLine-starty))/float(totalh) < 0.05:
                sym.issub=True
            elif float(abs(endy-centerLine))/float(totalh) < 0.2:
                sym.issuper=True
        if sym.issuper==True and sym.recognition=='z':
            sym.recognition='2'



    formulastr = ''
    curstart = 0
    if hasscript:
        for sym in poselist:
            if sym.recognition == 'sub':
                sym.recognition = '-'
            #formulastr+=sym.recognition
        while curstart < len(poselist):
            formulastr += poselist[curstart].recognition

            curend = curstart+1
            if curend >= len(poselist):
                break
            while curend < len(poselist) and (poselist[curend].issuper == True or poselist[curend].issub == True) :
                curend+=1
            for i in range(curstart+1,curend):
                if poselist[i].issuper:
                    formulastr+='^'+ '{'+poselist[i].recognition+'}'
                elif poselist[i].issub:
                    formulastr+=poselist[i].recognition
            curstart=curend
    else:
        for sym in poselist:
            if sym.recognition == 'sub':
                sym.recognition = '-'
            if sym.issuper==False and sym.issub==False:
                formulastr+=sym.recognition





    return formulastr


def findCenter(poselist):
    totalArea = 0
    symbolcnt = len(poselist)
    centerLine = 0
    for sym in poselist:
        totalArea += sym.bb[2] * sym.bb[3]
        centerLine += sym.bb[2] * sym.bb[3] * sym.center[0]
    centerLine /= totalArea
    avgArea = totalArea / symbolcnt

    formulastr = ''
    for i in range(len(poselist) - 1):
        formulastr += poselist[i].recognition
        formulastr += ' '
        formulastr += getRelativePos(poselist[i].bb, poselist[i + 1].bb)
        formulastr += ' '
    formulastr += poselist[len(poselist) - 1].recognition
    return centerLine


def handleFormula(poselist,upline,lowline,hasscript):
    for item in poselist:
        item.handled=False
    while hasRoot(poselist):
        for symbolpos in poselist:
            if symbolpos.isroot == True:
                curx,cury,curw,curh = symbolpos.bb
                includeList = includeIn(poselist,curx,cury,curw,curh)
                symbolpos.recognition = '\sqrt{'+handleFormula(includeList,upline,lowline,hasscript)+'}'
                for includeSymbol in includeList:
                    includeSymbol.handled = True
                symbolpos.isroot=False
                break
        tmplist = list(poselist)
        poselist = []
        for item in tmplist:
            if item.handled != True:
                poselist.append(item)
    #print len(poselist)


    while hasSls(poselist):
        poselist.sort(compcentery)
        for i in range(len(poselist)):
            if poselist[i].type == 'sls':
                #prn_obj(poselist[i])
                strict_upperbound = upline
                strict_lowerbound = lowline
                upperbound = upline
                lowerbound = lowline
                curx,cury,curw,curh = poselist[i].bb
                if i > 0:
                    for upidx in reversed(range(i-1)):
                        if poselist[upidx].type=='sls' and poselist[upidx].bb[0] < curx and poselist[upidx].bb[0]+poselist[upidx].bb[2] > curx+curw:
                            upperbound = poselist[upidx].bb[1]
                            strict_upperbound = poselist[upidx].bb[1]+poselist[upidx].bb[3]

                if i < len(poselist)-1:
                    for lowidx in range(i+1,len(poselist)):
                        if poselist[lowidx].type=='sls' and poselist[lowidx].bb[0] < curx and poselist[lowidx].bb[0]+poselist[lowidx].bb[2] > curx+curw:
                            lowerbound = poselist[lowidx].bb[1]+poselist[lowidx].bb[3]
                            strict_lowerbound = poselist[lowidx].bb[1]
                upx = curx
                upy = strict_upperbound
                upw = curw
                uph = cury - strict_upperbound
                lowx = curx
                lowy = cury+curh
                loww = curw
                lowh = strict_lowerbound-lowy
                if lowh > lowline-cury:
                    lowh = lowline-lowy
                #print upx,upy,upw,uph
                #print lowx,lowy,loww,lowh
                upinclude = centerIncludeIn(poselist,upx,upy,upw,uph)
                lowinclude = centerIncludeIn(poselist,lowx,lowy,loww,lowh)
                mostup=100000
                mostlow=0
                for upitem in upinclude:
                    if upitem.bb[1]<mostup:
                        mostup = upitem.bb[1]
                for lowitem in lowinclude:
                    if lowitem.bb[1]+lowitem.bb[3]>mostlow:
                        mostlow = lowitem.bb[1]+lowitem.bb[3]
                #print len(upinclude)
                #print len(lowinclude)
                upstr = handleFormula(upinclude,upy,upy+uph,hasscript)
                lowstr = handleFormula(lowinclude,lowy,lowy+lowh,hasscript)
                newSymbol = SymbolPos()
                newSymbol.recognition = '\\frac' + '{'+upstr+'}'+'{' +lowstr+'}'
                newSymbol.bb=(upx,mostup,upw,mostlow-mostup)
                newSymbol.center = (newSymbol.bb[1]+newSymbol.bb[3]/2,newSymbol.bb[0]+newSymbol.bb[2]/2)
                for upitem in upinclude:
                    upitem.handled=True
                for lowitem in lowinclude:
                    lowitem.handled=True
                poselist[i].handled=True
                poselist.append(newSymbol)
                break
        tmplist = list(poselist)
        poselist = []
        for item in tmplist:
            if item.handled != True:
                #print 'handled'
                poselist.append(item)
        #prn_obj(poselist[len(poselist)-1])

    finalList = sorted(poselist,compcenterx)
    return handleSimpleFormula(finalList,hasscript)







def compcentery(x, y):
    if x.center[0] > y.center[0]:
        return 1
    elif x.center[0] < y.center[0]:
        return -1
    else:
        return 0

def compcenterx(x,y):
    if x.center[1] > y.center[1]:
        return 1
    elif x.center[1] < y.center[1]:
        return -1
    else:
        return 0


def dist(p1, p2):
    return (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])

def pointInArea((px,py),x,y,w,h):
    if px > x and px < x+w and py > y and py < y+h:
        return True
    else:
        return False
def includeIn(poseList, x, y, w, h):
    includeList=[]
    for pose in poseList:
        curx,cury,curw,curh = pose.bb
        p1 = (curx,cury)
        p2 = (curx+curw,cury)
        p3 = (curx,cury+curh)
        p4 = (curx+curw,cury+curh)
        #print p1,p2,p3,p4
        if pointInArea(p1,x,y,w,h) and pointInArea(p2,x,y,w,h) and pointInArea(p3,x,y,w,h) and pointInArea(p4,x,y,w,h):
            includeList.append(pose)
    return includeList
def centerIncludeIn(poseList,x,y,w,h):
    centerIncludeList = []
    for pose in poseList:
        cy,cx = pose.center
        if pointInArea((cx,cy),x,y,w,h):
            centerIncludeList.append(pose)
    return centerIncludeList
def handleDot(poselist):
    centerList = sorted(poselist, compcentery)
    newList = []
    delList = []
    vis = np.zeros(len(centerList))
    for i in range(len(centerList)):
        if centerList[i].isdot == True and vis[i] == 0:
            # print i
            dotwidth = centerList[i].bb[2]
            dotcenterx = centerList[i].center[1]
            distance = 10000000
            curidx = i
            for j in range(i + 1, len(centerList)):
                itemx,itemy,itemw,itemh = centerList[j].bb
                if(abs(centerList[j].center[1]-dotcenterx)<=dotwidth or abs(itemx-dotcenterx)<=dotwidth or abs(itemx+itemw-dotcenterx)<=dotwidth):
                    curdist = dist((centerList[j].center[0], centerList[j].center[1]),
                                   (centerList[i].center[0], centerList[i].center[1]))
                    if curdist < distance:
                        distance = curdist
                        curidx = j
            if curidx != i:

                if centerList[curidx].isline == True:
                    vis[i] = 1

                    hasDownDot = False
                    for k in range(curidx + 1, len(centerList)):
                        upperDotWidth = centerList[i].bb[2]
                        if centerList[k].isdot == True and (
                                centerList[k].center[1] > centerList[i].center[1] - upperDotWidth and
                                centerList[k].center[1] < centerList[i].center[1] + upperDotWidth):
                            hasDownDot = True
                            vis[k] = 1

                            curx = centerList[curidx].bb[0]
                            curw = centerList[curidx].bb[2]
                            cury = centerList[i].bb[1]
                            curh = centerList[k].bb[1] + centerList[k].bb[3] - cury
                            newSymbol = SymbolPos()
                            newSymbol.bb = (curx, cury, curw, curh)
                            newSymbol.center = (
                                newSymbol.bb[1] + newSymbol.bb[3] / 2, newSymbol.bb[0] + newSymbol.bb[2] / 2)
                            delList.append(i)
                            delList.append(curidx)
                            delList.append(k)
                            newList.append(newSymbol)
                            newSymbol.type=u'÷'
                    if hasDownDot == False:
                        print 'Wrong Dot & Line'
                else:
                    x1, y1, w1, h1 = centerList[i].bb
                    x2, y2, w2, h2 = centerList[curidx].bb
                    xmin = min(x1, x2)
                    xmax = max(x1 + w1, x2 + w2)
                    ymin = min(y1, y2)
                    ymax = max(y1 + h1, y2 + h2)
                    newSymbol = SymbolPos()
                    newSymbol.bb = (xmin, ymin, (xmax - xmin), (ymax - ymin))
                    newSymbol.center = (newSymbol.bb[1] + newSymbol.bb[3] / 2, newSymbol.bb[0] + newSymbol.bb[2] / 2)
                    delList.append(i)
                    delList.append(curidx)
                    newList.append(newSymbol)
            else:
                centerList[i].type = '·'

    delList.sort(reverse=True)
    for id in delList:
        del centerList[id]
    centerList = centerList + newList
    return centerList


def handleLine(poselist, height):
    removeList = []
    appendList = []
    sortedList = sorted(poselist, compcentery)
    for symbolpos in poselist:
        if symbolpos.handled == False:
            if symbolpos.isline == True:
                y = 0
                w = symbolpos.bb[2]
                h = height
                x = symbolpos.bb[0]
                symidx = sortedList.index(symbolpos)

                for i in reversed(range(symidx)):
                    if sortedList[i].isline == True and sortedList[i].bb[2] > symbolpos.bb[2] \
                            and (symbolpos.center[1] > sortedList[i].bb[0] and symbolpos.center[1] < sortedList[i].bb[0]+sortedList[i].bb[2]):
                        y = sortedList[i].bb[1]
                        break;
                for i in range(symidx+1,len(sortedList)):
                    if sortedList[i].isline == True and sortedList[i].bb[2] > symbolpos.bb[2] \
                            and (symbolpos.center[1] > sortedList[i].bb[0] and symbolpos.center[1] < sortedList[i].bb[0]+sortedList[i].bb[2]):
                        h = sortedList[i].bb[1]
                        break;

                includeList = includeIn(poselist, x, y, w, h)
                centerincludeList = centerIncludeIn(poselist,x,y,w,h)
                centerincludeList.remove(symbolpos)
                if len(centerincludeList)==1:
                    if centerincludeList[0].isline==True:
                        ax,ay,aw,ah = symbolpos.bb
                        bx,by,bw,bh = centerincludeList[0].bb
                        newy = min(ay,by)
                        newx = min(ax,bx)
                        lowest = max(ay+ah,by+bh)
                        widest = max(ax+aw,bx+bw)
                        newh = lowest-newy
                        neww = widest-newx
                        newSymbol = SymbolPos()
                        newSymbol.bb = (newx,newy,neww,newh)
                        newSymbol.center = (newSymbol.bb[1] + newSymbol.bb[3] / 2, newSymbol.bb[0] + newSymbol.bb[2] / 2)
                        newSymbol.type = '='
                        removeList.append(symbolpos)
                        removeList.append(centerincludeList[0])
                        centerincludeList[0].handled=True
                        appendList.append(newSymbol)

                else:
                    if len(includeList) == 0:
                        symbolpos.type = 'sub'
                    else:
                        symbolpos.type = 'sls'
    for rm in removeList:
        poselist.remove(rm)
    for ap in appendList:
        poselist.append(ap)
    return poselist


# def handleRoot(poselist):
def remove_dir(dir):
      dir = dir.replace('\\', '/')
      if(os.path.isdir(dir)):
          for p in os.listdir(dir):
              remove_dir(os.path.join(dir,p))
          if(os.path.exists(dir)):
              os.rmdir(dir)
      else:
          if(os.path.exists(dir)):
              os.remove(dir)


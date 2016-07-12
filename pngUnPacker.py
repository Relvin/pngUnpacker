#encoding=utf-8

import os,sys
from PIL import Image
# from xml.etree import ElementTree

global imageInfo
gl_rect_list = []
gl_plist_rect_list = []

def rectInRectList(rect,rectList):
    for v in rectList:
        if rect == Rect(float(v[0]),float(v[1]),float(v[2]),float(v[3])):
            return True
    return False

def tree_to_dict(tree):
    d={}
    for index,item in enumerate(tree):
        if item.tag =='key':
            if tree[index+1].tag == 'string':
                d[item.text] = tree[index+1].text
            elif tree[index+1].tag == 'true':
                d[item.text]=True
            elif tree[index+1].tag == 'false':
                d[item.text]=False
            elif  tree[index+1].tag == "integer":
                d[item.text]=tree[index+1].text
            elif  tree[index+1].tag == "array":
                d[item.text]=tree[index+1].text
            elif tree[index+1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index+1])
    return d

class Vec2(object):
    x = float(0.0)
    y = float(0.0)

    def __init__(self,xOrVec,y = None):
        if isinstance(xOrVec,Vec2):
            self.x = float(xOrVec.x)
            self.y = float(xOrVec.y)
        elif isinstance(xOrVec,Size):
            self.x = float(xOrVec.width)
            self.y = float(xOrVec.height)
        else:
            self.x = float(xOrVec)
            self.y = float(y)

# <
    def __lt__(self, other):
        if isinstance(other,Vec2):
            if self.x < other.x and self.y < other.y:
                return True
        elif isinstance(other,Size):
            if self.x < other.width and self.y < other.height:
                return True
        return False

    def __repr__(self):
        return "x = %f,y = %f" %(self.x,self.y)

class Size(object):
    width = float(0.0)
    height = float(0.0)

    def __init__(self,wOrther,h = None):
        if isinstance(wOrther,Size):
            self.width = float(wOrther.width)
            self.height = float(wOrther.height)
        elif isinstance(wOrther,Vec2):
            self.width = float(wOrther.x)
            self.height = float(wOrther.y)
        else:
            self.width = float(wOrther)
            self.height = float(h)

# -
    def __sub__(self, other):
        if isinstance(other,Size):
            return Size(self.width - other.width,self.height - other.height)
        elif isinstance(other,Vec2):
            return Size(self.width - other.x,self.height - other.y)

# =
    def __eq__(self, wOrther):
        if isinstance(wOrther,Vec2):
            if self.width == wOrther.x and self.height == wOrther.y:
                return True
        else:
            if self.width == wOrther.width and self.height == wOrther.height:
                return True
        return False
    def __repr__(self):
        return "width = %f,height = %f" %(self.width,self.height)

class Rect(object):
    origin = Vec2(0.0,0.0)
    size = Size(0.0,0.0)

    def __init__(self,xOrVec2 = None ,yOrSize = None ,width = None ,height = None):
        if isinstance(xOrVec2,Rect):
            self.origin.x = float(xOrVec2.x())
            self.origin.y = float(xOrVec2.y())
            self.size.width = float(xOrVec2.width())
            self.size.height = float(xOrVec2.height())
        elif isinstance(xOrVec2,Vec2) and (isinstance(yOrSize,Size) or isinstance(yOrSize,Vec2)):
            self.origin = Vec2(xOrVec2)
            self.size = Size(yOrSize)
        elif xOrVec2 != None and yOrSize != None and width != None and height != None:
            self.origin.x = float(xOrVec2)
            self.origin.y = float(yOrSize)
            self.size.width = float(width)
            self.size.height = float(height)

    def __eq__(self, other):
        if self.x() == other.x() and self.y() == other.y() and self.width() == other.width() and self.height() == other.height():
            return True
        return False

    def intersectsRect(self,other):
        return not (self.getMaxX() < other.getMinX() or
                other.getMaxX() < self.getMinX() or
                self.getMaxY() < other.getMinY() or
                other.getMaxY() < self.getMinY())

    def merge(self,other):
        top1 = self.getMaxY()
        left1 = self.getMinX()
        right1 = self.getMaxX()
        bottom1 = self.getMinY()
        top2 = other.getMaxY()
        left2 = other.getMinX()
        right2 = other.getMaxX()
        bottom2 = other.getMinY()
        self.origin.x = min(left1, left2)
        self.origin.y = min(bottom1, bottom2)
        self.size.width = max(right1, right2) - self.origin.x
        self.size.height = max(top1, top2) - self.origin.y

    def getMinX(self):
        return self.x()

    def getMaxX(self):
        maxX = self.x() + self.width()
        return maxX

    def getMinY(self):
        return  self.y()

    def getMaxY(self):
        maxY = self.y() + self.height()
        return maxY

    def containsPoint(self,point):
        if point.x >= self.origin.x and point.x <= self.getMaxX() and point.y >= self.origin.y and point.y <= self.getMaxY():
            return True
        return False

    def x(self):
        return self.origin.x

    def y(self):
        return self.origin.y

    def width(self):
        return self.size.width

    def height(self):
        return self.size.height

#print
    def __repr__(self):
        return "x = %f ,y = %f,width = %f,height = %f" %(self.x(),self.y(),self.width(),self.height())

def getAlphaByPos(pos):
    point = (pos.x,pos.y)
    color = imageInfo.getpixel(point)
    alpha = 0
    if(color[3] > 0) :
        for value in color:
            alpha += value

    return alpha

def findNextNoneTransparentPixel(beginPoint,rect):
    found = False
    pixelPoint = Vec2(beginPoint)
    while pixelPoint.y < rect.height():#for yIdx in range(rect.size.height - beginPoint.y):
        while pixelPoint.x < rect.width():
            if(getAlphaByPos(pixelPoint) > 0):
                contain = False
                for rect_value in gl_rect_list:
                    if rect_value.containsPoint(pixelPoint) == True:
                        pixelPoint.x = rect_value.getMaxX()
                        contain = True
                        break
                if contain == False:
                    found = True
                    break
            pixelPoint.x += 1
        if found == True:
            break
        pixelPoint.y += 1
        pixelPoint.x = 0
    if found == True:
        return pixelPoint
    else:
        return False

def getSquareValue(x,y,rect):
    sv = 0
    fixedRect = Rect(rect.origin, rect.size-Size(2,2))

    tl = Vec2(x-1, y-1)
    if fixedRect.containsPoint(tl) and getAlphaByPos(tl):
        sv += 1
    tr = Vec2(x, y-1)
    if fixedRect.containsPoint(tr) and getAlphaByPos(tr):
        sv += 2
    bl = Vec2(x-1, y)
    if fixedRect.containsPoint(bl) and getAlphaByPos(bl):
        sv += 4
    br = Vec2(x, y)
    if fixedRect.containsPoint(br) and getAlphaByPos(br):
        sv += 8
    return sv

def getMinPoint(srcPoint,wOrPoint,h = 0):
    point = Vec2(0,0)
    if isinstance(wOrPoint,Size) or isinstance(wOrPoint,Vec2):
        point = wOrPoint
    else:
        point.x = wOrPoint
        point.y = h
    if point.x < srcPoint.x:
        srcPoint.x = point.x
    if point.y < srcPoint.y:
        srcPoint.y = point.y
    return srcPoint

def getMaxSize(srcSize,wOrSize,h = 0):
    size = Size(0,0)
    if isinstance(wOrSize,Size) or isinstance(wOrSize,Vec2):
        size = wOrSize
    else:
        size.width = wOrSize
        size.height = h
    if size.width > srcSize.width:
        srcSize.width = size.width
    if size.height > srcSize.height:
        srcSize.height = size.height
    return srcSize

def getIndexFromPos(x,y,width):
    return y*width+x

def marchSquare(start,rect):
    stepx = 0
    stepy = 0
    prevx = 0
    prevy = 0
    startx = start.x
    starty = start.y
    curx = startx
    cury = starty
    count = 0
    problem = False
    case9s = []
    case6s = []
    i = 0

    orgPoint = start
    subSize = Size(0,0)

    while True:
        sv = getSquareValue(curx, cury, rect)

        if sv == 1 or sv == 5 or sv == 13:
            stepx = 0
            stepy = -1
        elif sv == 8 or sv == 10 or sv == 11:
            stepx = 0
            stepy = 1
        elif sv == 4 or sv == 12 or sv == 14:
            stepx = -1
            stepy = 0
        elif sv == 2 or sv == 3 or sv == 7:
            stepx = 1
            stepy = 0
        elif sv == 9:
            i = getIndexFromPos(curx,cury,rect.size.width)
            if i in case9s:
                stepx = 0
                stepy = 1
                case9s.remove(i)
                problem = True
            else:
                stepx = 0
                stepy = -1
                case9s.append(i)
        elif sv == 6:
            i = getIndexFromPos(curx,cury,rect.size.width)
            if i in case6s:
                stepx = -1
                stepy = 0
                case6s.remove(i)
                problem = True
            else:
                stepx = 1
                stepy = 0
                case6s.append(i)
        else:
            print ""

        curx += stepx
        cury += stepy

        if stepx == prevx and stepy == prevy:
            getMinPoint(orgPoint,curx,cury)
            getMaxSize(subSize,curx,cury)
        elif problem:
            getMinPoint(orgPoint,curx,cury)
            getMaxSize(subSize,curx,cury)
        else:
            getMinPoint(orgPoint,curx,cury)
            getMaxSize(subSize,curx,cury)

        count += 1
        prevx = stepx
        prevy = stepy
        problem = False

        if curx == startx and cury == starty :
            break
    subSize = subSize - orgPoint
    return  Rect(orgPoint,subSize)


def unpackerImage(path):
    global imageInfo
    imageInfo = Image.open(path)
    # imageInfo.show()
    size = Size(imageInfo.width,imageInfo.height)
    rect = Rect(Vec2(0,0),size)
    start = findNextNoneTransparentPixel(Vec2(0,0),rect)
    while isinstance(start,Vec2) and start < rect.size:
        subRect = marchSquare(start,rect)
        print "rect = " ,subRect
        intersect = False
        for v in gl_rect_list:
            if v.intersectsRect(subRect):
                v.merge(subRect)
                intersect = True
                break
        if intersect == False:
            gl_rect_list.append(subRect)

        newStartPot = Vec2(subRect.getMaxX() + 1,subRect.y())
        if newStartPot.x >= rect.width():
            newStartPot.x = 0
            newStartPot.y += 1
        start = findNextNoneTransparentPixel(newStartPot,rect)

    return ""

def saveUnpackerImage(out_path):
    index = 0
    outImageName = "save_%d.png"
    for v in gl_rect_list:
        box = (
            int(v.x()),
            int(v.y()),
            int(v.x() + v.width()),
            int(v.y() + v.height())
        )
        imageName = outImageName %index
        rect_on_big = imageInfo.crop(box)
        outfile = os.path.join(out_path,imageName)
        outpath = os.path.dirname(outfile)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        rect_on_big.save(outfile)
        index += 1

# def plistFrameCompare(plistFile):
#     root = ElementTree.fromstring(open(plistFile,'r').read())
#     plist_dict = tree_to_dict(root[0])
#     to_list = lambda x:x.replace('{','').replace('}','').split(',')
#     for k,v in plist_dict['frames'].items():
#         rectlist = to_list(v['frame'])
#
#         gl_plist_rect_list.append(rectlist)
# outMainScene
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "USAGE:python pngUnPacker.py [XXX.png] [outPath]"
    else:
        global imageInfo
        path = sys.argv[1]
        outpath = sys.argv[2]
        unpackerImage(path)
        saveUnpackerImage(outpath)
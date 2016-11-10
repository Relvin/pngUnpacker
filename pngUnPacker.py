#!/usr/bin/python

# encoding = utf-8

import os
import sys
from PIL import Image
# from xml.etree import ElementTree

image_info = {}
gl_rect_list = []
gl_plist_rect_list = []


def rect_in_rect_list(rect, rect_list):
    for v in rect_list:
        if rect == Rect(float(v[0]), float(v[1]), float(v[2]), float(v[3])):
            return True
    return False


def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index+1].tag == 'string':
                d[item.text] = tree[index+1].text
            elif tree[index+1].tag == 'true':
                d[item.text] = True
            elif tree[index+1].tag == 'false':
                d[item.text] = False
            elif tree[index+1].tag == "integer":
                d[item.text] = tree[index+1].text
            elif tree[index+1].tag == "array":
                d[item.text] = tree[index+1].text
            elif tree[index+1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index+1])
    return d


class Vec2(object):
    x = float(0.0)
    y = float(0.0)

    def __init__(self, x_or_vec, y=None):
        if isinstance(x_or_vec, Vec2):
            self.x = float(x_or_vec.x)
            self.y = float(x_or_vec.y)
        elif isinstance(x_or_vec, Size):
            self.x = float(x_or_vec.width)
            self.y = float(x_or_vec.height)
        else:
            self.x = float(x_or_vec)
            self.y = float(y)

# <
    def __lt__(self, other):
        if isinstance(other, Vec2):
            if self.x < other.x and self.y < other.y:
                return True
        elif isinstance(other, Size):
            if self.x < other.width and self.y < other.height:
                return True
        return False

    def __repr__(self):
        return "x = %f,y = %f" % (self.x, self.y)


class Size(object):
    width = float(0.0)
    height = float(0.0)

    def __init__(self, w_or_other, h=None):
        if isinstance(w_or_other, Size):
            self.width = float(w_or_other.width)
            self.height = float(w_or_other.height)
        elif isinstance(w_or_other, Vec2):
            self.width = float(w_or_other.x)
            self.height = float(w_or_other.y)
        elif isinstance(w_or_other, tuple):
            self.width = w_or_other[0]
            self.height = w_or_other[1]
        else:
            self.width = float(w_or_other)
            self.height = float(h)

# -
    def __sub__(self, other):
        if isinstance(other, Size):
            return Size(self.width - other.width, self.height - other.height)
        elif isinstance(other, Vec2):
            return Size(self.width - other.x, self.height - other.y)
        
# =
    def __eq__(self, w_or_other):
        if isinstance(w_or_other, Vec2):
            if self.width == w_or_other.x and self.height == w_or_other.y:
                return True
        else:
            if self.width == w_or_other.width and self.height == w_or_other.height:
                return True
        return False

    def __repr__(self):
        return "width = %f,height = %f" % (self.width, self.height)


class Rect(object):
    origin = Vec2(0.0, 0.0)
    size = Size(0.0, 0.0)

    def __init__(self, x_or_other=None, y_or_size=None, width=None, height=None):
        if isinstance(x_or_other, Rect):
            self.origin.x = float(x_or_other.x())
            self.origin.y = float(x_or_other.y())
            self.size.width = float(x_or_other.width())
            self.size.height = float(x_or_other.height())
        elif isinstance(x_or_other, Vec2) and (isinstance(y_or_size, Size) or isinstance(y_or_size, Vec2)):
            self.origin = Vec2(x_or_other)
            self.size = Size(y_or_size)
        elif x_or_other is not None and y_or_size is not None and width is not None and height is not None:
            self.origin.x = float(x_or_other)
            self.origin.y = float(y_or_size)
            self.size.width = float(width)
            self.size.height = float(height)
        else:
            self.origin.x = 0
            self.origin.y = 0
            self.size.width = 0
            self.size.height = 0

    def __eq__(self, other):
        if self.x() == other.x() and self.y() == other.y() and \
                        self.width() == other.width() and self.height() == other.height():
            return True
        return False

    def intersects_rect(self, other):
        return not (self.get_max_x() < other.get_min_x() or
                    other.get_max_x() < self.get_min_x() or
                    self.get_max_y() < other.get_min_y() or
                    other.get_max_y() < self.get_min_y())

    def merge(self, other):
        top1 = self.get_max_y()
        left1 = self.get_min_x()
        right1 = self.get_max_x()
        bottom1 = self.get_min_y()
        top2 = other.get_max_y()
        left2 = other.get_min_x()
        right2 = other.get_max_x()
        bottom2 = other.get_min_y()
        self.origin.x = min(left1, left2)
        self.origin.y = min(bottom1, bottom2)
        self.size.width = max(right1, right2) - self.origin.x
        self.size.height = max(top1, top2) - self.origin.y

    def get_min_x(self):
        return self.x()

    def get_max_x(self):
        return self.x() + self.width()

    def get_min_y(self):
        return self.y()

    def get_max_y(self):
        return self.y() + self.height()

    def contains_point(self, point):
        if self.origin.x <= point.x <= self.get_max_x() and \
                        self.origin.y <= point.y <= self.get_max_y():
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

    def __repr__(self):
        return "x = %f ,y = %f,width = %f,height = %f" % (self.x(), self.y(), self.width(), self.height())


def get_alpha_by_pos(pos):
    global image_info
    point = (pos.x, pos.y)
    color = image_info.getpixel(point)
    alpha = 0
    if color[3] > 0:
        for value in color:
            alpha += value

    return alpha


def find_next_none_transparent_pixel(begin_point, rect):
    found = False
    pixel_point = Vec2(begin_point)
    while pixel_point.y < rect.height():
        while pixel_point.x < rect.width():
            if get_alpha_by_pos(pixel_point) > 0:
                contain = False
                for rect_value in gl_rect_list:
                    if rect_value.contains_point(pixel_point) is True:
                        pixel_point.x = rect_value.get_max_x()
                        contain = True
                        break
                if contain is False:
                    found = True
                    break
            pixel_point.x += 1
        if found is True:
            break
        pixel_point.y += 1
        pixel_point.x = 0
    if found is True:
        return pixel_point
    else:
        return False


def get_square_value(x, y, rect):
    sv = 0
    fixed_rect = Rect(rect.origin, rect.size-Size(2, 2))

    tl = Vec2(x-1, y-1)
    if fixed_rect.contains_point(tl) and get_alpha_by_pos(tl):
        sv += 1
    tr = Vec2(x, y-1)
    if fixed_rect.contains_point(tr) and get_alpha_by_pos(tr):
        sv += 2
    bl = Vec2(x-1, y)
    if fixed_rect.contains_point(bl) and get_alpha_by_pos(bl):
        sv += 4
    br = Vec2(x, y)
    if fixed_rect.contains_point(br) and get_alpha_by_pos(br):
        sv += 8
    return sv


def get_min_point(src_point, w_or_point, h=0):
    point = Vec2(0, 0)
    if isinstance(w_or_point, Size) or isinstance(w_or_point, Vec2):
        point = w_or_point
    else:
        point.x = w_or_point
        point.y = h
    if point.x < src_point.x:
        src_point.x = point.x
    if point.y < src_point.y:
        src_point.y = point.y
    return src_point


def get_max_size(src_size, w_or_size, h=0):
    size = Size(0, 0)
    if isinstance(w_or_size, Size) or isinstance(w_or_size, Vec2):
        size = w_or_size
    else:
        size.width = w_or_size
        size.height = h
    if size.width > src_size.width:
        src_size.width = size.width
    if size.height > src_size.height:
        src_size.height = size.height
    return src_size


def get_index_from_pos(x, y, width):
    return y*width+x


def march_square(start, rect):
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

    org_point = start
    sub_size = Size(0, 0)

    while True:
        sv = get_square_value(curx, cury, rect)

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
            i = get_index_from_pos(curx, cury, rect.size.width)
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
            i = get_index_from_pos(curx, cury, rect.size.width)
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
            get_min_point(org_point, curx, cury)
            get_max_size(sub_size, curx, cury)
        elif problem:
            get_min_point(org_point, curx, cury)
            get_max_size(sub_size, curx, cury)
        else:
            get_min_point(org_point, curx, cury)
            get_max_size(sub_size, curx, cury)

        count += 1
        prevx = stepx
        prevy = stepy
        problem = False

        if curx == startx and cury == starty:
            break
    sub_size = sub_size - org_point
    return Rect(org_point, sub_size)


def unpacker_image(path):
    global image_info
    global gl_rect_list
    global gl_plist_rect_list
    gl_plist_rect_list = []
    gl_rect_list = []
    image_info = Image.open(path)
    # image_info.show()
    size = Size(image_info.size)
    rect = Rect(Vec2(0, 0), size)
    start = find_next_none_transparent_pixel(Vec2(0, 0), rect)
    while isinstance(start, Vec2) and start < rect.size:
        sub_rect = march_square(start, rect)
        print "rect = ", sub_rect
        intersect = False
        for v in gl_rect_list:
            if v.intersects_rect(sub_rect):
                v.merge(sub_rect)
                intersect = True
                break
        if intersect is False:
            gl_rect_list.append(sub_rect)

        new_start_pot = Vec2(sub_rect.get_max_x() + 1, sub_rect.y())
        if new_start_pot.x >= rect.width():
            new_start_pot.x = 0
            new_start_pot.y += 1
        start = find_next_none_transparent_pixel(new_start_pot, rect)
    return ""


def save_unpacker_image(imageName, out_path):
    global image_info
    index = 0
    baseName = os.path.basename(imageName)
    baseName = baseName[0:baseName.index('.')]
    outdir = os.path.join(out_path,baseName)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    out_image_name = baseName + "_%d.png"
    for v in gl_rect_list:
        box = (
            int(v.x()),
            int(v.y()),
            int(v.x() + v.width()),
            int(v.y() + v.height())
        )
        image_name = out_image_name % index
        rect_on_big = image_info.crop(box)
        outfile = os.path.join(outdir, image_name)
        out_path_sub = os.path.dirname(outfile)
        if not os.path.exists(out_path_sub):
            os.makedirs(out_path_sub)
        rect_on_big.save(outfile)
        index += 1


def unpacker_png(input_path, out_path):
     for(dirpath, dirnames, filenames) in os.walk(input_path):
            for filename in filenames:
                if filename.endswith(".png"):
                    outdir = os.path.join(out_path,dirpath[len(input_path) + 1:])
                    if not os.path.exists(outdir):
                        os.makedirs(outdir)
                    unpacker_image(filename)
                    save_unpacker_image(os.path.basename(filename), outdir)
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
    if len(sys.argv) < 2:
        print "USAGE:python pngUnPacker.py [XXX.png] [outPath]"
    else:
        path = sys.argv[1]
        out_path = "./"
        if len(sys.argv) > 2:
            out_path = sys.argv[2]
        if os.path.isfile(path):
            unpacker_image(path)
            save_unpacker_image(os.path.basename(path), out_path)
        else:
           unpacker_png(path, out_path)
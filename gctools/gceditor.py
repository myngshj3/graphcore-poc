
# -*- coding: utf-8 -*-

import sys
import json
import re
import math
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
import graphcore as gc
from graphcore.ui_gcpane import Ui_GCPane


class ShapeHolder:

    CIRCLE = 'circle'
    ELLIPSE = 'ellipse'
    BOX = 'box'
    EDGE = 'edge'

    TYPE = 'type'
    NAME = 'name'
    X = 'x'
    Y = 'y'
    R = 'r'
    W = 'w'
    H = 'h'
    SRC = 'src'
    DST = 'dst'
    COLOR = 'color'
    BORDER_COLOR = 'border-color'
    GUI_OBJECT = 'gui-object'

    DEFAULT_SHAPE_CONFIG = 'default-shape.conf'

    # graphics scene
    @property
    def scene(self) -> QGraphicsScene:
        return self._scene

    def set_scene(self, scene):
        self._scene = scene

    # shape property
    @property
    def shapes(self) -> dict:
        return self._shapes

    # edge property
    @property
    def edges(self) -> dict:
        return self._edges

    # default config property
    @property
    def default_config(self):
        return self._default_config

    # initializes this shape holder
    def __init__(self):
        self._default_config = None
        self._shapes = None
        self._edges = None
        self._scene = None

    # loads default config
    def load_default_config(self):
        with open(self.DEFAULT_SHAPE_CONFIG, 'r') as f:
            self._default_config = json.load(fp=f)

    # constructs this shape holder
    def construct(self):
        self.load_default_config()
        self._shapes = {}
        self._edges = {}

    def clear(self):
        for k in self.shapes.keys():
            self.scene.removeItem(self.shapes[k][self.GUI_OBJECT])
        self.shapes.clear()
        for k in self.edges.keys():
            self.scene.removeItem(self.edges[k][self.GUI_OBJECT])
        self.edges.clear()

    def load(self, file: str):
        old_shapes = self._shapes
        for k in old_shapes.keys():
            self.scene.removeItem(old_shapes[k][self.GUI_OBJECT])
        self._shapes = {}
        old_edges = self._edges
        for k in old_edges.keys():
            self.scene.removeItem(old_edges[k][self.GUI_OBJECT])
        self._edges = {}
        with open(file, 'r') as f:
            content = json.load(f)
            shapes = content['shapes']
            for k in shapes.keys():
                if shapes[k][self.TYPE] == self.CIRCLE:
                    self.new_circle(shapes[k][self.X], shapes[k][self.Y], shapes[k][self.W], shapes[k][self.COLOR],
                                    shapes[k][self.BORDER_COLOR])
                elif shapes[k][self.TYPE] == self.ELLIPSE:
                    self.new_ellipse(shapes[k][self.X], shapes[k][self.Y], shapes[k][self.W], shapes[k][self.H],
                                     shapes[k][self.COLOR], shapes[k][self.BORDER_COLOR])
                elif shapes[k][self.TYPE] == self.BOX:
                    self.new_box(shapes[k][self.X], shapes[k][self.Y], shapes[k][self.W], shapes[k][self.H],
                                 shapes[k][self.COLOR], shapes[k][self.BORDER_COLOR])
            edges = content['edges']
            for k in edges.keys():
                self.new_edge(edges[k][self.SRC], edges[k][self.DST])

    def save(self, file: str):
        objs = {}
        for k in self.shapes.keys():
            objs[k] = self.shapes[k][self.GUI_OBJECT]
            self.shapes[k].pop(self.GUI_OBJECT)
        eobjs = {}
        for k in self.edges.keys():
            eobjs[k] = self.edges[k][self.GUI_OBJECT]
            self.edges[k].pop(self.GUI_OBJECT)
        with open(file, 'w') as f:
            js = {}
            js['shapes'] = self._shapes
            js['edges'] = self._edges
            json.dump(js, f, indent=4)
        for k in objs.keys():
            self.shapes[k][self.GUI_OBJECT] = objs[k]
        for k in eobjs.keys():
            self.edges[k][self.GUI_OBJECT] = eobjs[k]

    # deletes shape by specified shape id
    # @shape_id: id of shape to delete
    def delete_shape(self, shape_id):
        obj = self.shapes[shape_id][self.GUI_OBJECT]
        self.scene.removeItem(obj)
        self._shapes.pop(shape_id)
        E = self.collect_edges(shape_id)
        for e in E:
            self.delete_edge(e)

    # deletes shape by specified shape id
    # @shape_id: id of shape to delete
    def delete_shape_by_id(self, shape_id):
        self.delete_shape(shape_id)

    # deletes shape by specified name
    # @name: name of shape to delete
    def delete_shape_by_name(self, name):
        k = None
        for k in self._shapes.keys():
            if name == self._shapes[k][self.NAME]:
                break
        if k is not None:
            self.delete_shape(k)

    # sets shape name
    # @shape_id: shape id to set name
    # @name: shape name to set
    def set_shape_name(self, shape_id, name):
        if name == self._shapes[shape_id][self.NAME]:
            return
        for k in self._shapes.keys():
            if name == self._shapes[k][self.NAME]:
                raise Exception("name '{}' is already used.".format(name))

    # changes shape name
    # @name: shape name to change
    def change_shape_name(self, name, post_name):
        for k in self._shapes.keys():
            if post_name == self._shapes[k][self.NAME]:
                raise Exception("name '{}' is already used.".format(post_name))
        for k in self._shapes.keys():
            if name == self._shapes[k][self.NAME]:
                self._shapes[k][self.NAME] = post_name
                return

    # moves shape to position (x, y)
    def move_shape_to(self, shape_id, x, y):
        dx = x - self._shapes[shape_id][self.X]
        dy = y - self._shapes[shape_id][self.Y]
        self._shapes[shape_id][self.X] = x
        self._shapes[shape_id][self.Y] = y
        self._shapes[shape_id][self.GUI_OBJECT].moveBy(dx, dy)
        E = self.collect_edges(shape_id)
        for e in E:
            self.redraw_edge(e)

    # moves shape with distance (dx, dy)
    def move_shape_by(self, shape_id, dx, dy):
        self._shapes[shape_id][self.X] += dx
        self._shapes[shape_id][self.Y] += dy
        self._shapes[shape_id][self.GUI_OBJECT].moveBy(dx, dy)
        E = self.collect_edges(shape_id)
        for e in E:
            self.redraw_edge(e)

    # collects edges
    def collect_edges(self, shape_id):
        E = []
        for e in self.edges.keys():
            if self.edges[e][self.SRC] == shape_id or self.edges[e][self.DST] == shape_id:
                if e not in E:
                    E.append(e)
        return E

    # deletes edges
    def delete_edge(self, e):
        edge = self.edges[e]
        self.scene.removeItem(edge[self.GUI_OBJECT])
        self.edges.pop(e)

    # redraw edge
    def redraw_edge(self, e):
        src, dst = self.edges[e][self.SRC], self.edges[e][self.DST]
        src_x, src_y, src_type = self.shapes[src][self.X], self.shapes[src][self.Y], self.shapes[src][self.TYPE]
        src_w, src_h = self.shapes[src][self.W], self.shapes[src][self.H]
        dst_x, dst_y, dst_type = self.shapes[dst][self.X], self.shapes[dst][self.Y], self.shapes[dst][self.TYPE]
        dst_w, dst_h = self.shapes[dst][self.W], self.shapes[dst][self.H]
        u1 = (src_x, src_y)
        u2 = (dst_x, dst_y)
        # src side
        src_cross_pt = None
        if self.shapes[src][self.TYPE] in (self.BOX,):
            v1 = [src_x+src_w/2, src_y+src_h/2]
            v2 = [src_x+src_w/2, src_y-src_h/2]
            v3 = [src_x-src_w/2, src_y-src_h/2]
            v4 = [src_x-src_w/2, src_y+src_h/2]
            # v, v1, v2, v3, v4
            src_cross_pt = self.cross_point(u1, u2, v1, v2)
            if src_cross_pt is None:
                src_cross_pt = self.cross_point(u1, u2, v2, v3)
                if src_cross_pt is None:
                    src_cross_pt = self.cross_point(u1, u2, v3, v4)
                    if src_cross_pt is None:
                        src_cross_pt = self.cross_point(u1, u2, v4, v1)
        else:
            p = (src_x, src_y)
            w = src_w/2.0
            h = src_h/2.0
            src_cross_pt = self.cross_point_of_line_and_ellipse(u1, u2, p, w, h)
        # dst side
        dst_cross_pt = None
        if self.shapes[dst][self.TYPE] in (self.BOX,):
            v1 = [dst_x+dst_w/2, dst_y+dst_h/2]
            v2 = [dst_x+dst_w/2, dst_y-dst_h/2]
            v3 = [dst_x-dst_w/2, dst_y-dst_h/2]
            v4 = [dst_x-dst_w/2, dst_y+dst_h/2]
            # v, v1, v2, v3, v4
            dst_cross_pt = self.cross_point(u2, u1, v1, v2)
            if dst_cross_pt is None:
                dst_cross_pt = self.cross_point(u2, u1, v2, v3)
                if dst_cross_pt is None:
                    dst_cross_pt = self.cross_point(u2, u1, v3, v4)
                    if dst_cross_pt is None:
                        dst_cross_pt = self.cross_point(u2, u1, v4, v1)
        else:
            p = (dst_x, dst_y)
            w = dst_w/2.0
            h = dst_h/2.0
            src_cross_pt = self.cross_point_of_line_and_ellipse(u2, u1, p, w, h)

        line: QGraphicsLineItem = self.edges[e][self.GUI_OBJECT]
        line.setLine(src_cross_pt[0], src_cross_pt[1], dst_cross_pt[0], dst_cross_pt[1])

    # cross point between 2 line segments
    def cross_point(self, u1, u2, v1, v2):
        return self.cross_point_of_line_segments(u1, u2, v1, v2)

    # cross point
    def cross_point_of_line_segments(self, u1, u2, v1, v2):
        u = (u2[0]-u1[0], u2[1]-u1[1])
        len_u = math.sqrt(u[0]*u[0] + u[1]*u[1])
        u = (u[0]/len_u, u[1]/len_u)
        v = (v2[0]-v1[0], v2[1]-v1[1])
        len_v = math.sqrt(v[0]*v[0] + v[1]*v[1])
        v = (v[0]/len_v, v[1]/len_v)
        len_v1_v2 = math.sqrt((v2[0]-v1[0])*(v2[0]-v1[0]) + (v2[1]-v1[1])*(v2[1]-v1[1]))
        w = (v1[0] - u1[0], v1[1] - u1[1])
        D = -u[0] * v[1] + u[1] * v[0]
        if D == 0.0:
            return None
        m = (-v[1] * w[0] + v[0] * w[1]) / D
        k = (-u[1]*w[0] + u[0]*w[1])/D
        # crossing
        if m >= 0 and k >= 0 and len_v1_v2 >= k:
            return (m*u[0]+u1[0], m*u[1]+u1[1])
        # not crossing
        else:
            return None

    # cross point
    # (x - p_x)^2/w^2 + (y - p_y)^2/h^2 = 1 ...(1)
    # (x, y) = k(u_x, u_y) + (u_1x, u_1y)   ...(2)
    def cross_point_of_line_and_ellipse(self, u1, u2, p, w, h):
        u = (u2[0]-u1[0], u2[1]-u1[1])
        len_u = math.sqrt(u[0]*u[0] + u[1]*u[1])
        u = (u[0]/len_u, u[1]/len_u)
        a = h*h*u[0]*u[0] + w*w*u[1]*u[1]
        b = 2*(u1[0]*(u1[0]-p[0]) + u1[1]*(u1[1]-p[1]))
        c = (u1[0]-p[0])*(u1[0]-p[0]) + (u1[1]-p[1])*(u1[1]-p[1]) -w*w*h*h
        D = b*b - 4*a*c
        if D < 0:
            return None
        else:
            k = (-b + math.sqrt(D))/(2*a)
            return (k*u[0] + u1[0], k*u[1] + u1[1])

    # moves shape with distance (dx, dy)
    def get_shape_by_name(self, name):
        for k in self._shapes.keys():
            if self._shapes[k][self.NAME] == name:
                return k
        return None

    # sets shape size with (w, h)
    def set_size(self, shape_id, w, h):
        self._shapes[shape_id][self.W] = w
        self._shapes[shape_id][self.H] = h
        obj = self._shapes[shape_id][self.GUI_OBJECT]
        x = self._shapes[shape_id][self.X]
        y = self._shapes[shape_id][self.Y]
        obj.setRect(x - w/2, y - h/2, w, h)

    # change shape size
    def change_size(self, shape_id, w, h):
        self.set_size(shape_id, w, h)

    # get new shape id with attribute holder
    def new_shape_id(self):
        key_len = len(self._shapes.keys())
        for k in range(key_len):
            if k not in self._shapes.keys():
                self._shapes[k] = {}
                return k
        k = key_len
        self._shapes[k] = {}
        return k

    # get new shape id with default attributes
    # t can be CIRCLE, ELLIPSE or BOX
    def new_shape(self, t):
        default_config = self._default_config[t]
        shape_id = self.new_shape_id()
        self._shapes[shape_id][self.TYPE] = t
        self._shapes[shape_id][self.NAME] = str(shape_id)
        self._shapes[shape_id][self.X] = default_config[self.X]
        self._shapes[shape_id][self.Y] = default_config[self.Y]
        self._shapes[shape_id][self.W] = default_config[self.W]
        self._shapes[shape_id][self.H] = default_config[self.H]
        self._shapes[shape_id][self.COLOR] = default_config[self.COLOR]
        self._shapes[shape_id][self.BORDER_COLOR] = default_config[self.BORDER_COLOR]
        return shape_id

    # creates new circle
    # if each attribute not specified, default parameter is set.
    def new_circle(self, x=None, y=None, r=None, color=None, border_color=None):
        shape_id = self.new_shape(self.CIRCLE)
        if x is not None:
            self.shapes[shape_id][self.X] = x
        if y is not None:
            self.shapes[shape_id][self.Y] = y
        if r is not None:
            self.shapes[shape_id][self.W] = r
            self.shapes[shape_id][self.H] = r
        if color is not None:
            self.shapes[shape_id][self.COLOR] = color
        if border_color is not None:
            self.shapes[shape_id][self.BORDER_COLOR] = border_color
        obj = QGraphicsEllipseItem(self.shapes[shape_id][self.X] - self.shapes[shape_id][self.W]/2,
                                   self.shapes[shape_id][self.Y] - self.shapes[shape_id][self.H]/2,
                                   self.shapes[shape_id][self.W], self.shapes[shape_id][self.H])
        self._shapes[shape_id][self.GUI_OBJECT] = obj
        self.scene.addItem(obj)
        return shape_id

    # creates new ellipse
    # if each attribute not specified, default parameter is set.
    def new_ellipse(self, x=None, y=None, w=None, h=None, color=None, border_color=None):
        shape_id = self.new_shape(self.ELLIPSE)
        if x is not None:
            self.shapes[shape_id][self.X] = x
        if y is not None:
            self.shapes[shape_id][self.Y] = y
        if w is not None:
            self.shapes[shape_id][self.W] = w
        if h is not None:
                self.shapes[shape_id][self.H] = h
        if color is not None:
            self.shapes[shape_id][self.COLOR] = color
        if border_color is not None:
            self.shapes[shape_id][self.BORDER_COLOR] = border_color
        obj = QGraphicsEllipseItem(self.shapes[shape_id][self.X] - self.shapes[shape_id][self.W]/2,
                                   self.shapes[shape_id][self.Y] - self.shapes[shape_id][self.H]/2,
                                   self.shapes[shape_id][self.W], self.shapes[shape_id][self.H])
        self._shapes[shape_id][self.GUI_OBJECT] = obj
        self.scene.addItem(obj)
        return shape_id

    # creates new box
    # if each attribute not specified, default parameter is set.
    def new_box(self, x=None, y=None, w=None, h=None, color=None, border_color=None):
        shape_id = self.new_shape(self.BOX)
        if x is not None:
            self.shapes[shape_id][self.X] = x
        if y is not None:
            self.shapes[shape_id][self.Y] = y
        if w is not None:
            self.shapes[shape_id][self.W] = w
        if h is not None:
                self.shapes[shape_id][self.H] = h
        if color is not None:
            self.shapes[shape_id][self.COLOR] = color
        if border_color is not None:
            self.shapes[shape_id][self.BORDER_COLOR] = border_color
        obj = QGraphicsRectItem(self.shapes[shape_id][self.X] - self.shapes[shape_id][self.W]/2,
                                self.shapes[shape_id][self.Y] - self.shapes[shape_id][self.H]/2,
                                self.shapes[shape_id][self.W], self.shapes[shape_id][self.H])
        self._shapes[shape_id][self.GUI_OBJECT] = obj
        self.scene.addItem(obj)
        return shape_id

    # creates new box
    # if each attribute not specified, default parameter is set.
    def new_edge(self, src, dst, color=None):
        src_x, src_y = self.shapes[src][self.X], self.shapes[src][self.Y]
        dst_x, dst_y = self.shapes[dst][self.X], self.shapes[dst][self.Y]
        edge_id = self.new_edge_id()
        self.edges[edge_id] = {}
        self.edges[edge_id][self.SRC] = src
        self.edges[edge_id][self.DST] = dst
        if color is not None:
            self.edges[edge_id][self.COLOR] = color
        obj = QGraphicsLineItem(src_x, src_y, dst_x, dst_y)
        self._edges[edge_id][self.GUI_OBJECT] = obj
        self.redraw_edge(edge_id)
        self.scene.addItem(obj)
        return edge_id

    def new_edge_id(self):
        key_len = len(self._edges.keys())
        for k in range(key_len):
            if k not in self._edges.keys():
                self._edges[k] = {}
                return k
        k = key_len
        self._edges[k] = {}
        return k


class CommandReaderThread(QThread):

    def __init__(self, queue):
        super().__init__()
        self._queue = queue

    def run(self):
        # reader loop
        while True:
            print("waiting for command input")
            instr = input("$self> ")
            if re.match(r"^\s*$", instr):
                continue
            self._queue.put(instr)
            if self.do_quit(instr):
                break

    # do quit
    def do_quit(self, instr: str):
        if re.match("^\s*(quit|exit)\s*$", instr):  # matches `quit' or `exit'
            return True
        return False


class CommandProcessorThread(QThread):

    Signal: pyqtSignal = pyqtSignal(str)
    queue: Queue = Queue()

    def run(self):
        while True:
            item = self.queue.get()
            self.Signal.emit(item)


class GCPane:

    GCPANE_CONFIG = 'gcpane.conf'

    # shape holder
    @property
    def shape_holder(self) -> ShapeHolder:
        return self._shape_holder

    # initializes
    def __init__(self):
        self._app = None
        self._dlg = None
        self._ui = None
        self._queue = None
        self._command_runner = None
        self._reader_runner = None
        self._shape_holder = None

    # constructs
    def construct(self):
        self._queue = Queue()
        self._shape_holder = ShapeHolder()
        self._shape_holder.construct()
        self._command_runner = CommandProcessorThread()
        self._command_runner.Signal.connect(self.do_command)
        self._reader_runner = CommandReaderThread(self._command_runner.queue)

    # loads config
    def load_config(self):
        with open(self.GCPANE_CONFIG, "r") as f:
            conf = json.load(f)
            self._dlg.setGeometry(conf["x"], conf["y"], conf["width"], conf["height"])

    # do quit
    def do_quit(self, instr: str):
        if re.match("^\s*(quit|exit)\s*$", instr):  # matches `quit' or `exit'
            return True
        return False

    # do move
    def do_move(self, instr: str):
        pat = r"^\s*move\-to\s+(?P<name>[^\s]+)\s+(?P<x>(\-|)\d+)\s*,\s*(?P<y>(\-|)\d+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        name = m.group('name')
        x = float(m.group('x'))
        y = float(m.group('y'))
        shape_id = self.shape_holder.get_shape_by_name(name)
        self.shape_holder.move_shape_to(shape_id, x, y)

        return True

    # do move to
    def do_move_to(self, instr: str):
        return self.do_move(instr)

    # do move by
    def do_move_by(self, instr: str):
        pat = r"^\s*move\-by\s+(?P<name>[^\s]+)\s+(?P<dx>(\-|)\d+)\s*,\s*(?P<dy>(\-|)\d+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        name = m.group('name')
        dx = float(m.group('dx'))
        dy = float(m.group('dy'))
        shape_id = self.shape_holder.get_shape_by_name(name)
        self.shape_holder.move_shape_by(shape_id, dx, dy)
        return True

    # do resize
    def do_resize(self, instr: str):
        pat = r"^\s*resize\s+(?P<name>[^\s]+)\s+(?P<w>\d+)x(?P<h>\d+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        name = m.group('name')
        w = float(m.group('w'))
        h = float(m.group('h'))
        shape_id = self.shape_holder.get_shape_by_name(name)
        self.shape_holder.set_size(shape_id, w, h)
        return True

    # rename shape
    def do_rename(self, instr: str):
        pat = r"^\s*rename\s+(?P<pre>[^\s]+)\s+(?P<post>[^\s]+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        name = m.group('pre')
        post_name = m.group('post')
        self.shape_holder.change_shape_name(name, post_name)
        return True

    # lists objects
    def list_objects(self, instr: str):
        pat = r"^\s*list\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        print("Shapes:")
        for k in self.shape_holder.shapes.keys():
            print(k, ":", self.shape_holder.shapes[k])
        print("Edges:")
        for k in self.shape_holder.edges.keys():
            print(k, ":", self.shape_holder.edges[k])
        return True

    # deletes object
    def do_delete(self, instr: str):
        pat = r"^\s*delete\s+(?P<name>[^\s]+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        name = m.group('name')
        self.shape_holder.delete_shape_by_name(name)
        return True

    # adds circle
    def do_add_circle(self, instr: str):
        pat = r"^\s*add\s+circle\s+(?P<x>(\-|)\d+),(?P<y>(\-|)\d+)\+(?P<r>\d+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        x = float(m.group('x'))
        y = float(m.group('y'))
        r = float(m.group('r'))
        self.shape_holder.new_circle(x, y, r)
        return True

    # adds ellipse
    def do_add_ellipse(self, instr: str):
        pat = r"^\s*add\s+ellipse\s+(?P<x>(\-|)\d+),(?P<y>(\-|)\d+)\+(?P<w>\d+)x(?P<h>\d+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        x = float(m.group('x'))
        y = float(m.group('y'))
        w = float(m.group('w'))
        h = float(m.group('h'))
        self.shape_holder.new_ellipse(x, y, w, h)
        return True

    # adds box
    def do_add_box(self, instr: str):
        pat = r"^\s*add\s+box\s+(?P<x>(\-|)\d+),(?P<y>(\-|)\d+)\+(?P<w>\d+)x(?P<h>\d+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        x = float(m.group('x'))
        y = float(m.group('y'))
        w = float(m.group('w'))
        h = float(m.group('h'))
        self.shape_holder.new_box(x, y, w, h)
        return True

    # adds box
    def do_add_edge(self, instr: str):
        pat = r"^\s*add\s+edge\s+(?P<src>\d+)\s+(?P<dst>\d+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        src = int(m.group('src'))
        dst = int(m.group('dst'))
        self.shape_holder.new_edge(src, dst)
        return True

    def do_load(self, instr: str):
        pat = r"^\s*load\s+(?P<file>[^\s]+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        file = m.group('file')
        self.shape_holder.load(file)
        return True

    def do_save(self, instr: str):
        pat = r"^\s*save\s+(?P<file>[^\s]+)\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        file = m.group('file')
        self.shape_holder.save(file)
        return True

    def do_clear(self, instr: str):
        pat = r"^\s*clear\s*$"
        m = re.match(pat, instr)
        if not m:
            return False
        self.shape_holder.clear()
        return True

    # command loop
    def do_command(self, item):
        print("'{}' got".format(item))
        if re.match(r"^\s*$", item):
            pass
        elif re.match(r"^\s*(quit|exit)\s*$", item):  # matches `quit'
            dlg: QDialog = self._dlg
            dlg.close()
        elif self.do_move(item):
            pass
        elif self.do_move_to(item):
            pass
        elif self.do_move_by(item):
            pass
        elif self.do_rename(item):
            pass
        elif self.do_resize(item):
            pass
        elif self.list_objects(item):
            pass
        elif self.do_delete(item):
            pass
        elif self.do_add_box(item):
            pass
        elif self.do_add_ellipse(item):
            pass
        elif self.do_add_circle(item):
            pass
        elif self.do_save(item):
            pass
        elif self.do_load(item):
            pass
        elif self.do_add_edge(item):
            pass
        elif self.do_clear(item):
            pass
        else:
            print("invalid command!")

    def setupCommandReader(self):
        #self._executor = ThreadPoolExecutor(max_workers=2)
        self._reader_runner.start()
        self._command_runner.start()

    def setupGui(self, args):
        self._app = QApplication(args)
        self._dlg = QDialog()
        self._ui = Ui_GCPane()
        self._ui.setupUi(self._dlg)
        scene = QGraphicsScene()
        self.shape_holder.set_scene(scene)
        rect = scene.sceneRect()
        print("rect:", rect.x(), rect.y(), rect.width(), rect.height())
        self._ui.graphicsView.setScene(scene)
        self._ui.graphicsView.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
        self.shape_holder.new_ellipse(0, 100, 100, 150)
        self.shape_holder.new_box(200, 0, 100, 100)

    def show(self):
        self._dlg.show()
        sys.exit(self._app.exec_())


def gceditor():
    print("Hello, I'm GCeditor(local)")
    gcpane = GCPane()
    gcpane.construct()
    gcpane.setupGui(sys.argv)
    gcpane.load_config()
    gcpane.setupCommandReader()
    gcpane.show()

    
    

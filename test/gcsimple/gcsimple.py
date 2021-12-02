# -*- coding: utf-8 -*-

import sys
import json
import re
import math
import networkx as nx
import yaml
import random
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
import graphcore as gc
from graphics import GCPane, GCGraph, CommandParser
from graphicsscene import GCScene
from graphcore.drawutil import straight_edge_ellipse_to_ellipse,\
    straight_edge_ellipse_to_rect, straight_edge_rect_to_ellipse, straight_edge_rect_to_rect


def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

yaml.add_representer(dict, represent_odict)

def construct_odict(loader, node):
    return dict(loader.construct_pairs(node))

yaml.add_constructor('tag:yaml.org,2002:map', construct_odict)


class Parser(CommandParser):

    def __init__(self):
        super().__init__()

    def parse(self, command, graph: GCGraph, scene: GCScene, queue: Queue):
        # print("parse:", command, graph, scene, "].")
        # clear
        pat = r"^\s*clear\s*$"
        m = re.match(pat, command)
        if m:
            for n in graph.nodes:
                scene.removeItem(graph.nodes[n]['item'])
            for e in graph.edges:
                scene.removeItem(graph[e[0]][e[1]]['item'])
            graph.clear()
            return
        # save
        pat = r"^\s*save\s+(?P<file>.+)\s*$"
        m = re.match(pat, command)
        if m:
            file = m.group('file')
            G = nx.DiGraph()
            for k in graph.graph.keys():
                G.graph[k] = graph.graph[k]
            for n in graph.nodes:
                G.add_node(n)
                for k in graph.nodes[n].keys():
                    if k != 'item':
                        G.nodes[n][k] = graph.nodes[n][k]
            for e in graph.edges:
                G.add_edge(e[0], e[1])
                for k in graph[e[0]][e[1]].keys():
                    if k != 'item':
                        G[e[0]][e[1]][k] = graph[e[0]][e[1]][k]
            nx.write_yaml(G, file)
            return
        # load
        pat = r"^\s*load\s+(?P<file>.+)\s*$"
        m = re.match(pat, command)
        if m:
            file = m.group('file')
            # G = nx.read_yaml(file)
            with open(file, "r") as f:
                G = yaml.load(f, Loader=yaml.Loader)
            for k in G.graph.keys():
                graph.graph[k] = G.graph[k]
            for n in G.nodes:
                graph.add_node(n)
                for k in G.nodes[n].keys():
                    if k != 'item':
                        graph.nodes[n][k] = G.nodes[n][k]
                if graph.nodes[n]['shape'] == 'rect':
                    command = 'draw-rect'
                else:
                    command = 'draw-ellipse'
                command = "{} {}".format(command, n)
                queue.put(command)
            for e in G.edges:
                graph.add_edge(e[0], e[1])
                for k in G[e[0]][e[1]].keys():
                    if k != 'item':
                        graph[e[0]][e[1]][k] = G[e[0]][e[1]][k]
                command = "draw-edge {},{}".format(e[0],e[1])
                queue.put(command)
            nx.write_yaml(G, file)
            return
        # list
        pat = r"^\s*list\s*$"
        if re.match(pat, command):
            print("Nodes:")
            for n in graph.nodes:
                print("  {}:{}".format(n, graph.nodes[n]))
            print("Edges:")
            for e in graph.edges:
                print("  {}:{}".format(e, graph[e[0]][e[1]]))
            return
        # add-rect
        pat = r"^\s*add\-rect\s+(?P<x>(\-|)\d+(|\.\d+)),(?P<y>(\-|)\d+(|\.\d+))\+(?P<w>\d+(|\.\d+))x(?P<h>\d+(|\.\d+))\s*$"
        m = re.match(pat, command)
        if m:
            x, y = float(m.group('x')), float(m.group('y'))
            w, h = float(m.group('w')), float(m.group('h'))
            n = graph.next_node_id()
            graph.add_node(n, x=x, y=y, w=w, h=h, shape='rect', name=str(n), label=str(n))
            command = "draw-rect {}".format(n)
            queue.put(command)
            return
        # draw-rect
        pat = r"^\s*draw\-rect\s+(?P<n>\d+)\s*$"
        m = re.match(pat, command)
        if m:
            n = int(m.group('n'))
            x, y = graph.nodes[n]['x'], graph.nodes[n]['y']
            w, h = graph.nodes[n]['w'], graph.nodes[n]['h']
            g = QGraphicsItemGroup()
            r = QGraphicsRectItem(x-w/2, y-h/2, w, h)
            r.setBrush(QColor('lime'))
            g.addToGroup(r)
            l = QGraphicsTextItem(str(n))
            boundRect = l.boundingRect()
            l.setPos(x-boundRect.width()/2, y-boundRect.height()/2)
            g.addToGroup(l)
            scene.addItem(g)
            graph.nodes[n]['item'] = g
            return
        # add-ellipse
        pat = r"^\s*add\-ellipse\s+(?P<x>(\-|)\d+(|\.\d+)),(?P<y>(\-|)\d+(|\.\d+))\+(?P<w>\d+(|\.\d+))x(?P<h>\d+(|\.\d+))\s*$"
        m = re.match(pat, command)
        if m:
            x, y = float(m.group('x')), float(m.group('y'))
            w, h = float(m.group('w')), float(m.group('h'))
            n = graph.next_node_id()
            graph.add_node(n, x=x, y=y, w=w, h=h, shape='ellipse', name=str(n), label=str(n))
            command = "draw-ellipse {}".format(n)
            queue.put(command)
            return
        # draw-ellipse
        pat = r"^\s*draw\-ellipse\s+(?P<n>\d+)\s*$"
        m = re.match(pat, command)
        if m:
            n = int(m.group('n'))
            x, y = graph.nodes[n]['x'], graph.nodes[n]['y']
            w, h = graph.nodes[n]['w'], graph.nodes[n]['h']
            g = QGraphicsItemGroup()
            e = QGraphicsEllipseItem(x-w/2, y-h/2, w, h)
            e.setBrush(QColor('pink'))
            g.addToGroup(e)
            l = QGraphicsTextItem(str(n))
            boundRect = l.boundingRect()
            l.setPos(x-boundRect.width()/2, y-boundRect.height()/2)
            g.addToGroup(l)
            scene.addItem(g)
            graph.nodes[n]['item'] = g
            return
        # add-edge
        pat = r"^\s*add\-edge\s+(?P<uname>.+),(?P<vname>.+)\s*$"
        m = re.match(pat, command)
        if m:
            uname, vname = m.group('uname'), m.group('vname')
            u = graph.name_to_node_id(uname)
            v = graph.name_to_node_id(vname)
            if v not in graph[u].keys():
                graph.add_edge(u, v)
                command = "draw-edge {},{}".format(u,v)
                queue.put(command)
            return
        # draw-edge
        pat = r"^\s*draw\-edge\s+(?P<u>\d+),(?P<v>\d+)\s*$"
        m = re.match(pat, command)
        if m:
            u, v = int(m.group('u')), int(m.group('v'))
            if u in graph.nodes and v in graph[u].keys():
                ushape = graph.nodes[u]['shape']
                src_x, src_y = graph.nodes[u]['x'], graph.nodes[u]['y']
                src_w, src_h = graph.nodes[u]['w'], graph.nodes[u]['h']
                vshape = graph.nodes[v]['shape']
                dst_x, dst_y = graph.nodes[v]['x'], graph.nodes[v]['y']
                dst_w, dst_h = graph.nodes[v]['w'], graph.nodes[v]['h']
                graph.add_edge(u, v)
                graph[u][v]['label'] = "({},{})".format(u,v)
                if ushape == 'rect' and vshape == 'rect':
                    (sp, dp, head) = straight_edge_rect_to_rect(src_x, src_y, src_w, src_h,
                                                                dst_x, dst_y, dst_w, dst_h,
                                                                head_len=25, head_width=10)
                elif ushape == 'rect' and vshape == 'ellipse':
                    (sp, dp, head) = straight_edge_rect_to_ellipse(src_x, src_y, src_w, src_h,
                                                                   dst_x, dst_y, dst_w, dst_h,
                                                                   head_len=25, head_width=10)
                elif ushape == 'ellipse' and vshape == 'rect':
                    (sp, dp, head) = straight_edge_ellipse_to_rect(src_x, src_y, src_w, src_h,
                                                                   dst_x, dst_y, dst_w, dst_h,
                                                                   head_len=25, head_width=10)
                else:
                    (sp, dp, head) = straight_edge_ellipse_to_ellipse(src_x, src_y, src_w, src_h,
                                                                      dst_x, dst_y, dst_w, dst_h,
                                                                      head_len=25, head_width=10)
                g = QGraphicsItemGroup()
                l = QGraphicsTextItem("({},{})".format(u, v))
                boundRect = l.boundingRect()
                if sp is not None and dp is not None:
                    e = QGraphicsLineItem(sp[0], sp[1], dp[0], dp[1])
                    g.addToGroup(e)
                    l.setPos((sp[0]+dp[0])/2 - boundRect.width()/2, (sp[1]+dp[1])/2 - boundRect.height()/2)
                    g.addToGroup(l)
                    poly = QPolygonF()
                    for i in range(len(head)):
                        poly.append(QPointF(head[i][0], head[i][1]))
                    poly.append(QPointF(head[0][0], head[0][1]))
                    p = QGraphicsPolygonItem(poly)
                    g.addToGroup(p)
                else:
                    e = QGraphicsLineItem(src_x, src_y, dst_x, dst_y)
                    g.addToGroup(e)
                    l.setPos((src_x + dst_x) / 2 + boundRect.width() / 2, (src_y + dst_y) / 2 + boundRect.height() / 2)
                    g.addToGroup(l)
                    p = QGraphicsPolygonItem(QPolygonF())
                    g.addToGroup(p)
                scene.addItem(g)
                graph[u][v]['item'] = g
            return
        # redraw-edge
        pat = r"^\s*redraw\-edge\s+(?P<u>\d+),(?P<v>\d+)\s*$"
        m = re.match(pat, command)
        if m:
            u, v = int(m.group('u')), int(m.group('v'))
            if u in graph.nodes and v in graph[u].keys():
                ushape = graph.nodes[u]['shape']
                src_x, src_y = graph.nodes[u]['x'], graph.nodes[u]['y']
                src_w, src_h = graph.nodes[u]['w'], graph.nodes[u]['h']
                vshape = graph.nodes[v]['shape']
                dst_x, dst_y = graph.nodes[v]['x'], graph.nodes[v]['y']
                dst_w, dst_h = graph.nodes[v]['w'], graph.nodes[v]['h']
                if ushape == 'rect' and vshape == 'rect':
                    (sp, dp, head) = straight_edge_rect_to_rect(src_x, src_y, src_w, src_h,
                                                                dst_x, dst_y, dst_w, dst_h,
                                                                head_len=25, head_width=10)
                elif ushape == 'rect' and vshape == 'ellipse':
                    (sp, dp, head) = straight_edge_rect_to_ellipse(src_x, src_y, src_w, src_h,
                                                                   dst_x, dst_y, dst_w, dst_h,
                                                                   head_len=25, head_width=10)
                elif ushape == 'ellipse' and vshape == 'rect':
                    (sp, dp, head) = straight_edge_ellipse_to_rect(src_x, src_y, src_w, src_h,
                                                                   dst_x, dst_y, dst_w, dst_h,
                                                                   head_len=25, head_width=10)
                else:
                    (sp, dp, head) = straight_edge_ellipse_to_ellipse(src_x, src_y, src_w, src_h,
                                                                      dst_x, dst_y, dst_w, dst_h,
                                                                      head_len=25, head_width=10)
                g: QGraphicsItemGroup = graph[u][v]['item']
                children = g.childItems()
                e: QGraphicsLineItem = children[0]
                l: QGraphicsTextItem = children[1]
                boundRect = l.boundingRect()
                p: QGraphicsPolygonItem = children[2]
                if sp is not None and dp is not None:
                    e.setLine(sp[0], sp[1], dp[0], dp[1])
                    l.setPos((sp[0]+dp[0])/2 + boundRect.width()/2, (sp[1]+dp[1])/2 + boundRect.height()/2)
                    poly = QPolygonF()
                    for i in range(len(head)):
                        poly.append(QPointF(head[i][0], head[i][1]))
                    poly.append(QPointF(head[0][0], head[0][1]))
                    p.setPolygon(poly)
                else:
                    e.setLine(src_x, src_y, dst_x, dst_y)
                    l.setPos((src_x+dst_x)/2+boundRect.width()/2, (src_y+dst_y)/2+boundRect.height()/2)
                    p.setPolygon(QPolygonF())
            return
        # del-node
        pat = r"^\s*del\-node\s+(?P<name>.+)\s*$"
        m = re.match(pat, command)
        if m:
            name = m.group('name')
            n = graph.name_to_node_id(name)
            if n >= 0:
                E = graph.node_to_edges(n)
                for e in E:
                    scene.removeItem(graph[e[0]][e[1]]['item'])
                    graph.remove_edge(e[0], e[1])
                scene.removeItem(graph.nodes[n]['item'])
                graph.remove_node(n)
            return
        # del-edge
        pat = r"^\s*del\-edge\s+(?P<uname>[^,]+),(?P<vname>[^,])\s*$"
        m = re.match(pat, command)
        if m:
            uname, vname = m.group('uname'), m.group('vname')
            u = graph.name_to_node_id(uname)
            v = graph.name_to_node_id(vname)
            if u in graph.nodes and v in graph[u]:
                scene.removeItem(graph[u][v]['item'])
                graph.remove_edge(u, v)
            return
        # move-to
        pat = r"^\s*move\-to\s+(?P<name>.+)\s+(?P<x>(\-|)\d+(|\.\d+)),(?P<y>(\-|)\d+(|\.\d+))\s*$"
        m = re.match(pat, command)
        if m:
            name, x, y = m.group('name'), float(m.group('x')), float(m.group('y'))
            n = graph.name_to_node_id(name)
            if n >= 0:
                dx = x - graph.nodes[n]['x']
                dy = y - graph.nodes[n]['y']
                graph.nodes[n]['x'] = x
                graph.nodes[n]['y'] = y
                item: QGraphicsItem = graph.nodes[n]['item']
                item.moveBy(dx, dy)
                E = graph.node_to_edges(n)
                for e in E:
                    command = "redraw-edge {},{}".format(e[0], e[1])
                    queue.put(command)
            return
        # move-by
        pat = r"^\s*move\-by\s+(?P<name>.+)\s+(?P<dx>(\-|)\d+(|\.\d+)),(?P<dy>(\-|)\d+(|\.\d+))\s*$"
        m = re.match(pat, command)
        if m:
            name, dx, dy = m.group('name'), float(m.group('dx')), float(m.group('dy'))
            n = graph.name_to_node_id(name)
            if n >= 0:
                graph.nodes[n]['x'] += dx
                graph.nodes[n]['y'] += dy
                item: QGraphicsItem = graph.nodes[n]['item']
                item.moveBy(dx, dy)
                E = graph.node_to_edges(n)
                for e in E:
                    command = "redraw-edge {},{}".format(e[0], e[1])
                    queue.put(command)
            return
        # resize
        pat = r"^\s*resize\s+(?P<name>.+)\s+(?P<w>\d+(|\.\d+))x(?P<h>\d+(|\.\d+))\s*$"
        m = re.match(pat, command)
        if m:
            name, w, h = m.group('name'), float(m.group('w')), float(m.group('h'))
            n = graph.name_to_node_id(name)
            if n >= 0:
                item: QGraphicsItemGroup = graph.nodes[n]['item']
                x = graph.nodes[n]['x']
                y = graph.nodes[n]['y']
                graph.nodes[n]['w'] = w
                graph.nodes[n]['h'] = h
                for i in item.childItems():
                    if isinstance(i, QGraphicsRectItem) or isinstance(i, QGraphicsEllipseItem):
                        i.setRect(x-w/2, y-h/2, w, h)
            return
        # set-node-label
        pat = r"^\s*set\-node\-label\s+(?P<name>.+)\s+\"(?P<label>(\"\"|[^\"])*)\"\s*$"
        m = re.match(pat, command)
        if m:
            name, label = m.group('name'), m.group('label')
            label = label.replace('""', '"')
            n = graph.name_to_node_id(name)
            if n >= 0:
                graph.nodes[n]['label'] = label
                item: QGraphicsItem = graph.nodes[n]['item']
                for i in item.childItems():
                    if isinstance(i, QGraphicsTextItem):
                        i.setPlainText(label)
                        boundRect = i.boundingRect()
                        x, y = graph.nodes[n]['x'], graph.nodes[n]['y']
                        i.setPos(x-boundRect.width()/2, y-boundRect.height()/2)
            return
        # set-edge-label
        pat = r"^\s*set\-edge\-label\s+(?P<u>[^,]+),(?P<v>[^,]+)\s+(?P<label>\"(\"\"|[^\"])+\")\s*$"
        m = re.match(pat, command)
        if m:
            u, v, label = int(m.group('u')), int(m.group('v')), int(m.group('label'))
            return
        # set-node-color
        pat = r"^\s*set\-node\-color\s+(?P<n>[^,]+)\s+(?P<color>.+)\s*$"
        m = re.match(pat, command)
        if m:
            n, color = m.group('n'), m.group('color')
            n = graph.name_to_node_id(n)
            if n >= 0:
                graph.nodes[n]['color'] = color
                item: QGraphicsItem = graph.nodes[n]['item']
                for i in item.childItems():
                    if isinstance(i, QGraphicsRectItem) or isinstance(i, QGraphicsEllipseItem):
                        i.setBrush(QColor(color))
            return
        # set-edge-color
        pat = r"^\s*set\-edge\-label\s+(?P<u>[^,]+),(?P<v>[^,]+)\s+(?P<color>.+)\s*$"
        m = re.match(pat, command)
        if m:
            u, v, color = int(m.group('u')), int(m.group('v')), int(m.group('color'))
            return
        print("invalid command:", command)
        pass


def main():
    app = QApplication(sys.argv)
    parser = Parser()
    pane = GCPane()
    pane.set_command_parser(parser)
    pane.setGeometry(100, 100, 800, 600)
    # # test shapes
    # g = QGraphicsItemGroup()
    # r = QGraphicsRectItem()
    # r.setRect(0, 0, 200, 200)
    # r.setBrush(QColor('green'))
    # g.addToGroup(r)
    # t = QGraphicsTextItem('hello')
    # rect = t.sceneBoundingRect()
    # t.setPos(50, 100)
    # g.addToGroup(t)
    # pane.scene.addItem(g)
    pane.show()
    pane.startCommandReader()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

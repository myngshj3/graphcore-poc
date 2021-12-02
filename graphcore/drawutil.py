# -*- coding: utf-8 -*-

import numpy as np
import math
from PyQt5.Qt import *


# rotate 2D vector
def gcore_rot_vec(u, v, a):
    a11, a12, a21, a22 = np.cos(a), -np.sin(a), np.sin(a), np.cos(a)
    x = a11 * u + a12 * v
    y = a21 * u + a22 * v
    return x, y


# compute arrow polygon
def gcore_arrow_polygon(x_u, y_u, r_u, x_v, y_v, r_v, head_len, head_angle):
    polygon = QPolygonF()
    try:
        vec = (x_v - x_u, y_v - y_u)
        len_vec = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        vec = (vec[0] / len_vec, vec[1] / len_vec)
        x_s, y_s = vec[0] * r_u + x_u, vec[1] * r_u + y_u
        x_d, y_d = x_v - vec[0] * r_v, y_v - vec[1] * r_v
        polygon.fill(QPointF(x_s, y_s))
        polygon.append(QPointF(x_s, y_s))
        polygon.append(QPointF(x_d, y_d))
        vec2 = gcore_rot_vec(vec[0], vec[1], math.pi - head_angle)
        polygon.append(QPointF(x_d + vec2[0] * head_len, y_d + vec2[1] * head_len))
        vec3 = gcore_rot_vec(vec[0], vec[1], - math.pi + head_angle)
        polygon.append(QPointF(x_d + vec3[0] * head_len, y_d + vec3[1] * head_len))
        polygon.append(QPointF(x_d, y_d))
    except ZeroDivisionError as ex:
        print(ex)
    finally:
        return polygon


def gcore_arrow_arc(x_u, y_u, r_u, x_v, y_v, r_v, start_angle, span_angle, head_len, head_angle):
    painter = QPainter()
    polygon = QPolygonF()
    try:
        vec = (x_v - x_u, y_v - y_u)
        len_vec = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        vec = (vec[0] / len_vec, vec[1] / len_vec)
        x_s, y_s = vec[0] * r_u + x_u, vec[1] * r_u + y_u
        x_d, y_d = x_v - vec[0] * r_v, y_v - vec[1]

        painter.drawChord(x_s, y_s, x_d - x_s, y_d - y_s, start_angle, span_angle)
        vec2 = gcore_rot_vec(vec[0], vec[1], math.pi - head_angle)
        polygon.append(QPointF(x_d, y_d))
        polygon.append(QPointF(x_d + vec2[0] * head_len, y_d + vec2[1] * head_len))
        vec3 = gcore_rot_vec(vec[0], vec[1], - math.pi + head_angle)
        polygon.append(QPointF(x_d + vec3[0] * head_len, y_d + vec3[1] * head_len))
        polygon.append(QPointF(x_d, y_d))
    except ZeroDivisionError as ex:
        print(ex)
    finally:
        return polygon


_global_pixmaps = {}


def gcore_get_pixmap(path) -> QPixmap:
    global _global_pixmaps
    if path == "uml-actor":
        if path in _global_pixmaps.keys():
            pixmap = _global_pixmaps[path]
        else:
            pixmap = QPixmap("images/uml-actor.png")
            _global_pixmaps[path] = pixmap
    elif path == "uml-folder":
        if path in _global_pixmaps.keys():
            pixmap = _global_pixmaps[path]
        else:
            pixmap = QPixmap("images/uml-folder.png")
            _global_pixmaps[path] = pixmap
    else:
        pixmap = QPixmap(path)
    return pixmap

def cross_point(u1, u2, v1, v2):
    return cross_point_of_line_segments(u1, u2, v1, v2)


def cross_point_of_line_segments(u1, u2, v1, v2):
    u = (u2[0]-u1[0], u2[1]-u1[1])
    len_u = math.sqrt(u[0]*u[0] + u[1]*u[1])
    if len_u == 0:
        return None
    u = (u[0]/len_u, u[1]/len_u)
    v = (v2[0]-v1[0], v2[1]-v1[1])
    len_v = math.sqrt(v[0]*v[0] + v[1]*v[1])
    if len_v == 0:
        return None
    v = (v[0]/len_v, v[1]/len_v)
    len_v1_v2 = math.sqrt((v2[0]-v1[0])*(v2[0]-v1[0]) + (v2[1]-v1[1])*(v2[1]-v1[1]))
    w = (v1[0] - u1[0], v1[1] - u1[1])
    D = -u[0] * v[1] + u[1] * v[0]
    if D == 0.0:
        return None
    m = (-v[1] * w[0] + v[0] * w[1]) / D
    k = (-u[1] * w[0] + u[0] * w[1]) / D
    if m >= 0 and k >= 0 and len_v1_v2 >= k:
        return (m*u[0]+u1[0], m*u[1]+u1[1])
    else:
        return None


def cross_point_of_line_and_ellipse(u1, u2, p, w, h):
    u = (u2[0]-u1[0], u2[1]-u1[1])
    len_u = math.sqrt(u[0]*u[0] + u[1]*u[1])
    if len_u == 0:
        return None
    u = (u[0]/len_u, u[1]/len_u)
    a = h*h*u[0]*u[0] + w*w*u[1]*u[1]
    b = 2*(u1[0]*(u1[0]-p[0]) + u1[1]*(u1[1]-p[1]))
    c = (u1[0]-p[0])*(u1[0]-p[0]) + (u1[1]-p[1])*(u1[1]-p[1]) - w*w*h*h
    D = b*b - 4*a*c
    if D < 0:
        return None
    else:
        k = (-b + math.sqrt(D))/(2*a)
        return (k*u[0] + u1[0], k*u[1] + u1[1])


def arrow_head(src_x, src_y, dst_x, dst_y, head_len, head_width):
    u = (src_x - dst_x, src_y - dst_y)
    u_len = math.sqrt(u[0]*u[0] + u[1]*u[1])
    u = (u[0]/u_len, u[1]/u_len)
    v = (-u[1], u[0])
    p0 = (dst_x + head_len*u[0], dst_y + head_len*u[1])
    p1 = (p0[0] + v[0]*head_width/2, p0[1] + v[1]*head_width/2)
    p2 = (dst_x, dst_y)
    p3 = (p0[0] - v[0]*head_width/2, p0[1] - v[1]*head_width/2)
    return (p0, p1, p2, p3)

def straight_edge_rect_to_rect(src_x, src_y, src_w, src_h, dst_x, dst_y, dst_w, dst_h, head_len, head_width):
    u1 = (src_x, src_y)
    u2 = (dst_x, dst_y)
    # src side
    v1 = [src_x+src_w/2, src_y+src_h/2]
    v2 = [src_x+src_w/2, src_y-src_h/2]
    v3 = [src_x-src_w/2, src_y-src_h/2]
    v4 = [src_x-src_w/2, src_y+src_h/2]
    src_cross_pt = cross_point(u1, u2, v1, v2)
    if src_cross_pt is None:
        src_cross_pt = cross_point(u1, u2, v2, v3)
        if src_cross_pt is None:
            src_cross_pt = cross_point(u1, u2, v3, v4)
            if src_cross_pt is None:
                src_cross_pt = cross_point(u1, u2, v4, v1)
    # dst side
    v1 = [dst_x+dst_w/2, dst_y+dst_h/2]
    v2 = [dst_x+dst_w/2, dst_y-dst_h/2]
    v3 = [dst_x-dst_w/2, dst_y-dst_h/2]
    v4 = [dst_x-dst_w/2, dst_y+dst_h/2]
    dst_cross_pt = cross_point(u2, u1, v1, v2)
    if dst_cross_pt is None:
        dst_cross_pt = cross_point(u2, u1, v2, v3)
        if dst_cross_pt is None:
            dst_cross_pt = cross_point(u2, u1, v3, v4)
            if dst_cross_pt is None:
                dst_cross_pt = cross_point(u2, u1, v4, v1)
    # arrow head
    if src_cross_pt is None or dst_cross_pt is None:
        return (None, None, None)
    head = arrow_head(src_cross_pt[0], src_cross_pt[1], dst_cross_pt[0], dst_cross_pt[1], head_len, head_width)
    # return
    return (src_cross_pt, head[0], head)


def straight_edge_rect_to_ellipse(src_x, src_y, src_w, src_h, dst_x, dst_y, dst_w, dst_h, head_len, head_width):
    u1 = (src_x, src_y)
    u2 = (dst_x, dst_y)
    # src side
    v1 = [src_x+src_w/2, src_y+src_h/2]
    v2 = [src_x+src_w/2, src_y-src_h/2]
    v3 = [src_x-src_w/2, src_y-src_h/2]
    v4 = [src_x-src_w/2, src_y+src_h/2]
    src_cross_pt = cross_point(u1, u2, v1, v2)
    if src_cross_pt is None:
        src_cross_pt = cross_point(u1, u2, v2, v3)
        if src_cross_pt is None:
            src_cross_pt = cross_point(u1, u2, v3, v4)
            if src_cross_pt is None:
                src_cross_pt = cross_point(u1, u2, v4, v1)
    # dst side
    p = (dst_x, dst_y)
    w = dst_w/2.0
    h = dst_h/2.0
    dst_cross_pt = cross_point_of_line_and_ellipse(u2, u1, p, w, h)
    # arrow head
    if src_cross_pt is None or dst_cross_pt is None:
        return (None, None, None)
    head = arrow_head(src_cross_pt[0], src_cross_pt[1], dst_cross_pt[0], dst_cross_pt[1], head_len, head_width)
    # return
    return (src_cross_pt, head[0], head)


def straight_edge_ellipse_to_rect(src_x, src_y, src_w, src_h, dst_x, dst_y, dst_w, dst_h, head_len, head_width):
    u1 = (src_x, src_y)
    u2 = (dst_x, dst_y)
    # src side
    p = (src_x, src_y)
    w = src_w/2.0
    h = src_h/2.0
    src_cross_pt = cross_point_of_line_and_ellipse(u1, u2, p, w, h)
    # dst side
    v1 = [dst_x+dst_w/2, dst_y+dst_h/2]
    v2 = [dst_x+dst_w/2, dst_y-dst_h/2]
    v3 = [dst_x-dst_w/2, dst_y-dst_h/2]
    v4 = [dst_x-dst_w/2, dst_y+dst_h/2]
    dst_cross_pt = cross_point(u2, u1, v1, v2)
    if dst_cross_pt is None:
        dst_cross_pt = cross_point(u2, u1, v2, v3)
        if dst_cross_pt is None:
            dst_cross_pt = cross_point(u2, u1, v3, v4)
            if dst_cross_pt is None:
                dst_cross_pt = cross_point(u2, u1, v4, v1)
    # arrow head
    if src_cross_pt is None or dst_cross_pt is None:
        return (None, None, None)
    head = arrow_head(src_cross_pt[0], src_cross_pt[1], dst_cross_pt[0], dst_cross_pt[1], head_len, head_width)
    # return
    return (src_cross_pt, head[0], head)


def straight_edge_ellipse_to_ellipse(src_x, src_y, src_w, src_h, dst_x, dst_y, dst_w, dst_h, head_len, head_width):
    u1 = (src_x, src_y)
    u2 = (dst_x, dst_y)
    # src side
    p = (src_x, src_y)
    w = src_w/2.0
    h = src_h/2.0
    src_cross_pt = cross_point_of_line_and_ellipse(u1, u2, p, w, h)
    # dst side
    p = (dst_x, dst_y)
    w = dst_w/2.0
    h = dst_h/2.0
    dst_cross_pt = cross_point_of_line_and_ellipse(u2, u1, p, w, h)
    # arrow head
    if src_cross_pt is None or dst_cross_pt is None:
        return (None, None, None)
    head = arrow_head(src_cross_pt[0], src_cross_pt[1], dst_cross_pt[0], dst_cross_pt[1], head_len, head_width)
    # return
    return (src_cross_pt, head[0], head)

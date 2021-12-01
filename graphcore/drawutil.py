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

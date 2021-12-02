# -*- coding: utf-8 -*-

import numpy as np
from graphcore.shell import GraphCoreContextHandler
# import tensorflow as tf
import threading


def sigmoid(x) -> float:
    return 1/(1+np.exp(-x))


class GraphCoreGenericSolver:
    def __init__(self, handler: GraphCoreContextHandler, dt=1.0):
        self._handler = handler
        self._t = 0
        self._dt = dt
        self._computation_nodes = {}
        self._dataflow_edges = {}
        self._control_volumes = {}

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @property
    def t(self) -> float:
        return self._t

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def computation_nodes(self):
        return self._computation_nodes

    @property
    def dataflow_edges(self):
        return self._dataflow_edges

    @property
    def control_volumes(self):
        return self._control_volumes

    def setup_network(self):
        # setup computation-nodes and control-volumes
        for n in self.handler.context.nodes:
            t = self.handler.node_attr(n, 'type')
            # node is process, computation-node or controller
            if t in ('process', 'computation-node'):
                self.computation_nodes[n] = {}
                self.computation_nodes[n]['computation-process'] = {
                    "in": self.in_edges(n),
                    "out": self.out_edges(n),
                    "passed-time": 0,
                    "ready": self.handler.node_attr(n, 'ready'),
                    "progress": 0,
                    "complexity": self.handler.node_attr(n, 'complexity'),
                    "consume-time": self.handler.node_attr(n, 'consume-time'),
                    # function to calculate progress of n at time x
                    # "func": lambda c, x: 1/2*(1 + tf.math.sigmoid((-c['consume-time']/2+x)/c['consume-time']/np.sqrt(2)))
                    "compute-progress": lambda c, x: sigmoid((-c['consume-time'] / 2 + x) * 5 / c['consume-time'])
                }
                if self.handler.node_attr(n, 'ready'):
                    self.handler.call("change_node_attr", [n, 'fill-color', 'lightblue'])
                else:
                    self.handler.call("change_node_attr", [n, 'fill-color', 'red'])
            # node is control-volume
            elif t in ('control-volume'):
                self.control_volumes[n] = {}
                self.control_volumes[n]['computation-process'] = {
                    "passed-time": 0,
                    "ready": self.handler.node_attr(n, 'ready'),
                    "progress": 0,
                    "complexity": self.handler.node_attr(n, 'complexity'),
                    "consume-time": self.handler.node_attr(n, 'consume-time'),
                    "compute-progress": lambda c, x: sigmoid((-c['consume-time'] / 2 + x) * 5 / c['consume-time'])
                }
                if self.handler.node_attr(n, 'ready'):
                    self.handler.call("change_node_attr", [n, 'fill-color', 'lightblue'])
                else:
                    self.handler.call("change_node_attr", [n, 'fill-color', 'red'])

        # setup dataflow-edges
        for e in self.handler.context.edges:
            t = self.handler.edge_attr(e[0], e[1], 'type')
            if t in ('dataflow'):
                self.dataflow_edges[e] = {}
                self.dataflow_edges[e]['computation-process'] = {
                    "ready": self.handler.edge_attr(e[0], e[1], 'ready'),
                    "distance": self.handler.edge_attr(e[0], e[1], 'distance'),
                    "consume-time": self.handler.edge_attr(e[0], e[1], 'consume-time'),
                    "compute-distance": lambda c, x: 1 - sigmoid((-c['consume-time'] / 2 + x) * 5 / c['consume-time'])
                }
                if self.handler.edge_attr(e[0], e[1], 'ready'):
                    self.handler.call("change_edge_attr", [e[0], e[1], 'fill-color', 'lightblue'])
                else:
                    self.handler.call("change_edge_attr", [e[0], e[1], 'fill-color', 'red'])

    def in_edges(self, n):
        edges = []
        for e in self.handler.context.edges:
            if e[1] == n:
                edges.append(e)
        return edges

    def out_edges(self, n):
        edges = []
        for e in self.handler.context.edges:
            if e[0] == n:
                edges.append(e)
        return edges

    def is_completed(self, n) -> bool:
        cn = self.computation_nodes[n]
        cp = cn['computation-process']
        if cp['progress'] == 1:
            return True

    def is_ready(self, n) -> bool:
        cn = self.computation_nodes[n]
        cp = cn['computation-process']
        return cp["ready"]

    def is_input_ready(self, n) -> bool:
        cn = self.computation_nodes[n]
        cp = cn['computation-process']
        for e in cp["in"]:
            c = self.dataflow_edges[e]['computation-process']
            if not c["ready"]:
                return False
            c = self.control_volumes[e[0]]['computation-process']
            if not c["ready"]:
                return False
        return True

    def compute(self, condition_to_stop, err=0.05, timeup=3600*24*30*12) -> bool:
        while True:
            if condition_to_stop():
                return True
            if timeup < self.t:
                return False
            self.compute_one_step(err)

    def compute_one_step(self, err):
        # print("compute_one_step t_prev={}, dt={}".format(self.t, self.dt))
        self._t += self.dt
        for n in self.computation_nodes.keys():
            # skip if not ready
            if self.is_completed(n):
                continue
            if not self.is_ready(n):
                continue
            if not self.is_input_ready(n):
                continue
            cn = self.computation_nodes[n]
            cp = cn['computation-process']
            # access to data sources(shrink distances)
            close_count = 0
            for e in cp["in"]:
                c = self.dataflow_edges[e]['computation-process']
                if c['distance'] == 0:
                    close_count += 1
                else:
                    distance = c['distance']
                    # complexity = c['complexity']
                    next_distance = c['compute-distance'](c, self.t)
                    if next_distance < err:
                        c['distance'] = 0
                        print("t={} e{} set distance=0".format(self.t, e))
                        close_count += 1
                    else:
                        c['distance'] = next_distance
                    self.handler.call('change_edge_attr', [e[0], e[1], 'distance', c['distance']])
                    self.handler.call('update_edge', [e[0], e[1]])
            # process if all data source flow edges are accessed
            if close_count == len(cp["in"]):
                # set progress completed if close to end enough
                next_progress = cp["compute-progress"](cp, self.t)
                if 1 - next_progress < err:
                    cp["progress"] = 1
                    # set all data target flow edges accessible
                    for e in cp["out"]:
                        c = self.dataflow_edges[e]
                        c['ready'] = True
                        print("t={} e{} set ready=True".format(self.t, e))
                        self.handler.call('change_edge_attr', [e[0], e[1], 'fill-color', 'lightblue'])
                        self.control_volumes[e[1]]['computation-process']['ready'] = True
                        print("t={} v{} set ready=True".format(self.t, e[1]))
                        self.handler.call('change_node_attr', [e[1], 'fill-color', "blue"])
                    self.handler.call('change_node_attr', [n, "fill-color", "blue"])
                else:
                    cp["progress"] = next_progress
            cp["passed-time"] = self.t

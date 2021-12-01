# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np


class ComputationNetwork:
    def __init__(self, graph: nx.DiGraph):
        self._graph = graph
        self._computation_matrix = None
        self._computation_nodes = None
        self._control_volumes = None
        self._prev_states = None
        self._in_edges = None
        self._out_edges = None
        pass

    def graph(self):
        return self._graph

    def computation_matrix(self):
        return self._computation_matrix

    def computation_nodes(self):
        return self._computation_nodes

    def control_volumes(self):
        return self._control_volumes

    def collect_computation_nodes(self):
        nodes = {}
        for n in self.graph():
            node = self.graph().nodes[n]
            if node['type'] == 'computation-node':
                nodes[n] = node
        return nodes

    def collect_control_volumes(self):
        nodes = {}
        for n in self.graph():
            node = self.graph().nodes[n]
            if node['type'] == 'control-volume':
                nodes[n] = node
        return nodes

    def in_edges(self):
        return self._in_edges

    def out_edges(self):
        return self._out_edges

    def setup_computation_network(self):
        G = self.graph()
        computation_nodes = self.collect_computation_nodes()
        control_volumes = self.control_volumes()
        out_edges = {}
        in_edges = {}
        for cn in computation_nodes:
            in_edges[cn] = []
            out_edges[cn] = []
            for cv in control_volumes:
                if (cn, cv) in G.edges:
                    out_edges[cv].append((cn, cv))
                if (cv, cn) in G.edges:
                    in_edges[cv].append((cv, cn))
        self._in_edges = in_edges
        self._out_edges = out_edges

    def compute(self):
        G = self.graph()
        computation_nodes = self.computation_nodes()
        node_diffs = {}
        for cn in computation_nodes:
            in_edges = self.in_edges()[cn]
            out_edges = self.out_edges()[cn]
            cnattr = G.nodes[cn]
            compute = cnattr['computation-compute']
            applydiff = cnattr['computation-applydiff']
            in_diffs, out_diffs = compute(in_edges, out_edges)
            for node, diff in in_diffs:
                if node not in node_diffs.keys():
                    node_diffs[node] = diff
                else:
                    applydiff(node_diffs[node], diff)
        for cv in node_diffs.keys():
            node = G.nodes[cv]
            node['computation-applydiff'](node, node_diffs[cv])

    def build_computation_network(self):
        # initialize computation matrix and node vector
        computation_nodes = self.collect_computation_nodes()
        control_volumes = self.collect_control_volumes()
        computation_nodes.extend(control_volumes)
        n = len(computation_nodes)
        # m = len(control_volumes)
        matrix_shape = (n, n)
        matrix = np.ndarray(matrix_shape, dtype=np.object)
        g = self.graph()
        for i, cn in enumerate(computation_nodes):
            if cn not in control_volumes:
                for j, an in enumerate(computation_nodes):
                    if (cn, an) in g.edges:
                        # attr = g.edges[cn, an]
                        matrix[i, j] = (cn, an)
                        # attr['computation-assign'](matrix[i, j], an)
                    if (an, cn) in g.edges:
                        # attr = g.edges[an, cn]
                        matrix[j, i] = (an, cn)
                        # attr['computation-assign'](matrix[j, i], an)

        # set computation matrix and vector to context
        self._computation_matrix = matrix
        self._computation_nodes = computation_nodes


    # def collect_source_nodes(self, e):
    #     nodes = []
    #     for n in self.graph():
    #         node = self.graph().nodes[n]
    #         if node['type'] == 'control-volume':
    #             nodes.append(n)
    #     return nodes

    def compute_once(self):
        G = self.graph()
        A = self.computation_matrix()
        X = []
        for x in self.computation_nodes():
            X.append(G.nodes[x].copy())
        n, m = A.shape
        Y = []
        for i in range(n):
            y = None
            for j in range(m):
                a = A[i, j]
                x = X[j]
                if a is not None and x is not None:
                    e = G.edges[a[0], a[1]]
                    mult = e['computation-multiply']
                    add = e['computation-add']
                    s, d = G.nodes[e[0]], G.nodes[e[1]]
                    y_ = mult(e, x)
                    if y is None:
                        y = y_
                    else:
                        y = add(y, y_)
            Y.append(y)
        return Y

    def update_operator(self, Y):
        G = self.graph()
        X = self.computation_nodes()
        for i, x in enumerate(X):
            x = G.nodes[x]
            x['computation-assign'](x, Y[i])

    def print_computation_nodes(self):
        for cn in self.computation_nodes():
            print(cn)


def add(x, y):
    if x is None or y is None:
        return None
    return {'x': x['x'] + y['x'], 'y': x['y'] + y['y'], 'temperature': x['temperature'] + y['temperature']}


def multiply(x, y):
    if x is None or y is None:
        return None
    return {'x': x['x'] * y['x'], 'y': x['y'] * y['y'], 'temperature': x['temperature'] * y['temperature']}


def assign(x, y):
    if x is None or y is None:
        return None
    x['x'] = y['x']
    x['y'] = y['y']
    x['temperature'] = y['temperature']


def compute(G, cn, dt, in_edge, out_edge):
    n = G.nodes[cn]
    s = G.nodes[in_edge[0]]
    d = G.nodes[out_edge[1]]
    distance = in_edge['distance'] + out_edge['distance']
    area = n['area']
    conductance = n['heat-conductance']
    temp_diff = d['temperature'] - s['temperature']
    heat = area / distance * conductance * temp_diff
    out_info = (out_edge[1], heat)
    return out_info


def applydiff(G, cv, diff):
    # = cnattr['computation-applydiff']
    node = G.nodes[cv]
    node['x'] += diff['x']
    node['y'] += diff['y']
    node['temperature'] += diff['temperature']


def main():
    graph = nx.DiGraph()
    # set vertices and edges
    length = 100
    grid_hpoints = 5
    grid_vpoints = 5
    dt = 0.1
    grid_width = length / (grid_hpoints - 1)
    grid_height = length / (grid_vpoints - 1)
    for i in range(grid_hpoints):
        x = grid_width * i
        for j in range(grid_vpoints - 1):
            y = grid_height * j
            u = "v({},{})".format(i, j)
            graph.add_node(u)
            uattr = graph.nodes[u]
            uattr['temperature'] = 0.0
            uattr['x'] = x
            uattr['y'] = y
            uattr['w'] = grid_width
            uattr['h'] = grid_height
            v = "v({},{})".format(i, j+1)
            graph.add_node(v)
            vattr = graph.nodes[v]
            vattr['temperature'] = 0.0
            vattr['x'] = x
            vattr['y'] = y
            vattr['w'] = grid_width
            vattr['h'] = grid_height
            graph.add_edge(u, v)
            eattr = graph.edges[u, v]
            eattr['distance'] = grid_height
            eattr['vector'] = [0, grid_height]
            graph.add_edge(v, u)
            eattr = graph.edges[v, u]
            eattr['distance'] = grid_height
            eattr['vector'] = [0, -grid_height]
    for j in range(grid_vpoints):
        y = grid_height * j
        for i in range(grid_hpoints - 1):
            x = grid_width * i
            u = "v({},{})".format(i, j)
            uattr = graph.nodes[u]
            uattr['type'] = 'control-volume'
            uattr['temperature'] = 0.0
            uattr['x'] = x
            uattr['y'] = y
            uattr['w'] = grid_width
            uattr['h'] = grid_height
            v = "v({},{})".format(i+1, j)
            vattr = graph.nodes[v]
            vattr['type'] = 'control-volume'
            vattr['temperature'] = 0.0
            vattr['x'] = x
            vattr['y'] = y
            vattr['w'] = grid_width
            vattr['h'] = grid_height
            graph.add_edge(u, v)
            eattr = graph.edges[u, v]
            eattr['type'] = 'control-volume'
            eattr['distance'] = grid_width
            eattr['vector'] = [-grid_width, 0]
            graph.add_edge(v, u)
            eattr = graph.edges[v, u]
            eattr['type'] = 'control-volume'
            eattr['distance'] = grid_width
            eattr['vector'] = [-grid_width, 0]
    # set computation node attributes
    hcn_count = int((grid_hpoints - 1) / 2)
    vcn_count = int((grid_vpoints - 1) / 2)
    for i in range(hcn_count):
        row = 2 * i + 1
        for j in range(vcn_count):
            col = 2 * j + 1
            u = "v({},{})".format(row, col)
            cn = graph.nodes[u]
            cn['type'] = 'computation-node'
            cn['heat-conductance'] = 20
            # cn['computation-add'] = add
            # cn['computation-multiply'] = multiply
            # cn['computation-assign'] = assign
            cn['computation-compute'] = lambda in_edges, out_edges: compute(graph, cn, dt, in_edges, out_edges)
            cn['computation-applydiff'] = lambda diff: applydiff(graph, cn, diff)
    # setup computation network
    network = ComputationNetwork(graph)
    network.build_computation_network()
    for i in range(5):
        Y = network.compute_once()
        network.update_operator(Y)
        network.print_computation_nodes()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

import sys
import numpy as np
import networkx as nx
import json




class GCSolver:

    def __init__(self, G: nx.DiGraph, dt: float):
        self._G = G
        self._dt = dt

    @property
    def G(self) -> nx.DiGraph:
        return self._G

    @G.setter
    def G(self, value: nx.DiGraph):
        self._G = value

    def clone_graph(self, G) -> nx.DiGraph:
        g = nx.readwrite.node_link_data(G)
        return nx.readwrite.node_link_graph(g)

    def calc_one_step(self, value_sym, max_value_sym, velocity_sym, max_velocity_sym, current_max_velocity_sym,
                      distance_sym, t: float):
        # symbol setup
        w_sym = current_max_velocity_sym
        x_sym = value_sym
        H_sym = max_value_sym
        V_sym = max_velocity_sym
        v_sym = velocity_sym
        l_sym = distance_sym
        G: nx.DiGraph = self.clone_graph(self._G)
        dt = self._dt
        for i in G.nodes:
            F = tuple(G.successors(i))
            D = tuple([(i, _) for _ in F])
            for d in D:
                # val = 1.0/len(D)*(G.nodes[d[1]][H_sym] - G.nodes[d[1]][x_sym])/(G.edges[d[0], d[1]][l_sym]*dt)
                val = 1.0/len(D)*(G.nodes[d[1]][H_sym] - G.nodes[d[1]][x_sym])/dt
                if val <= G.edges[d[0], d[1]][V_sym]:
                    G.edges[d[0], d[1]][w_sym] = val
                else:
                    G.edges[d[0], d[1]][w_sym] = G.edges[d[0], d[1]][V_sym]
            # sum of w^d
            sum_w = 0
            for d in D:
                sum_w += G.edges[d[0], d[1]][w_sym]
            for d in D:
                if sum_w == 0:
                    k = 0
                else:
                    k = G.edges[d[0],d[1]][w_sym] / sum_w
                if sum_w * dt <= G.nodes[i][x_sym]:
                    G.edges[d[0], d[1]][v_sym] = k * G.edges[d[0], d[1]][w_sym]
                elif G.nodes[i][x_sym] < sum_w * dt and k*G.nodes[i][x_sym] / dt <= G.edges[d[0], d[1]][w_sym]:
                    G.edges[d[0], d[1]][v_sym] = k * G.nodes[i][x_sym] / dt
                    if G.edges[d[0], d[1]][w_sym] < G.edges[d[0], d[1]][v_sym]:
                        G.edges[d[0], d[1]][v_sym] = G.edges[d[0], d[1]][w_sym]
                else:
                    G.edges[d[0], d[1]][w_sym] = G.edges[d[0], d[1]][w_sym]

        H: nx.DiGraph = self.clone_graph(G)
        for i in G.nodes:
            S = G.predecessors(i)
            D = G.successors(i)
            sum_v_s = 0
            for s in S:
                sum_v_s += G.edges[s, i][v_sym] / G.edges[s, i][l_sym]
            sum_v_d = 0
            for d in D:
                sum_v_d += G.edges[i, d][v_sym] / G.edges[i, d][l_sym]
            H.nodes[i][x_sym] = G.nodes[i][x_sym] + sum_v_s * dt - sum_v_d * dt + self.generated_value(G, i, t, dt)
        self._G = H
        return H

    def generated_value(self, G: nx.DiGraph, i: str, t: float, dt: float):
        node = G.nodes[i]
        # print("generated_value(i={}, t={}, dt={}) node type:'{}'".format(i, t, dt, node['type']))
        if node['type'] != 'signal-generator':
            return 0
        a = node['generator-arg1']
        b = node['generator-arg2']
        c = node['generator-arg3']
        delay = node['delay']
        duration = node['duration']
        # print("generator-type='{}', t={}, delay={}, duration={}".format(node['generator-type'], t, delay, duration))
        # outside interval
        if t + dt <= delay or delay + duration <= t:
            return 0
        if t <= delay:
            t1 = delay
        else:
            t1 = t
        if duration <= t + dt:
            t2 = duration
        else:
            t2 = t + dt
        if node['generator-type'] == 'step':
            ret = a * (t2-t1) / 2
            # print("step={}".format(ret))
            return ret
        elif node['generator-type'] == 'normal':
            ret = a*(self.normal(t2,b,c) + self.normal(t1,b,c))/2*dt
            return ret
        elif node['generator-type'] == 'uniform':
            ret = (a*np.random.uniform(0, 1) + a*np.random.uniform(0, 1) + 2*b) / 2 * dt
            # print("uniform = {}".format(ret))
            return ret
        elif node['generator-type'] == 'sin':
            ret = a*(np.sin(np.pi/b*t2) + np.sin(np.pi/b*t1) + 2*c) / 2 * dt
            # print("{}(sin({}*{}) + sin({}*{}) + {}){}/2 = {}".format(a, b, t2, b, t1, 2*c, dt, ret))
            return ret
        elif node['generator-type'] == 'cos':
            ret = a*(np.cos(np.pi/b*t2) + np.cos(np.pi/b*t1) + 2*c) / 2 * dt
            # print("{}(cos({}*{}) + cos({}*{}) + {}){}/2 = {}".format(a, b, t2, b, t1, 2*c, dt, ret))
            return ret
        else:
            return 0

    def calc(self, steps: int):
        G = self.clone_graph(self._G)
        G_array = []
        for _ in range(steps):
            H = self.calc_one_step()
            data = nx.node_link_data(H)
            G_array.append(data)
            self._G = H
        self._G = G
        return tuple(G_array)

    @staticmethod
    def normal(x, mu, sigma):
        return 1 / np.sqrt(2 * np.pi * sigma) * np.exp(-(x - mu) * (x - mu) / (2 * sigma))


def main(argv):
    if len(argv) < 3:
        sys.exit(-1)
    model_file = argv[0]
    param_file = argv[1]
    post_file = argv[2]
    with open(model_file, 'r') as f:
        model_data = json.load(f)
        G = nx.node_link_graph(model_data)
    with open(param_file, 'r') as f:
        param_data = json.load(f)
    solver = GCSolver(G, param_data['dt'])
    G_array = solver.calc(param_data['steps'])
    G_array = [nx.node_link_data(_) for _ in G_array]
    post_data = {'post-data': G_array}
    with open(post_file, 'w') as f:
        json.dump(post_data, f)


if __name__ == "__main__":
    main(sys.argv[1:])

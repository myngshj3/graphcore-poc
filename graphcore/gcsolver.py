# -*- coding: utf-8 -*-

import sys
import networkx as nx
import json




class GCSolver:

    def __init__(self, G: nx.DiGraph, dt: float):
        self._G = G
        self._dt = dt

    def clone_graph(self, G) -> nx.DiGraph:
        g = nx.readwrite.node_link_data(G)
        return nx.readwrite.node_link_graph(g)

    def calc_one_step(self, value_sym, max_value_sym, velocity_sym, max_velocity_sym, current_max_velocity_sym):
        # symbol setup
        w_sym = current_max_velocity_sym
        x_sym = value_sym
        H_sym = max_value_sym
        V_sym = max_velocity_sym
        v_sym = velocity_sym
        G: nx.DiGraph = self.clone_graph(self._G)
        dt = self._dt
        for i in G.nodes:
            F = tuple(G.successors(i))
            D = tuple([(i, _) for _ in F])
            # sum of w^d
            sum_w = 0
            for d in D:
                sum_w += G.edges[d[0], d[1]][w_sym]
            sum_w_dt = sum_w * self._dt
            thr = 0
            for f in F:
                thr += G.nodes[f][H_sym] - G.nodes[f][x_sym]
            for d in D:
                if G.nodes[i][x_sym] <= sum_w_dt:
                    G.edges[i, d[1]][w_sym] = 1.0/len(D)*(G.nodes[i][H_sym]-G.nodes[i][x_sym])/self._dt
                else:
                    G.edges[i, d[1]][w_sym] = G.edges[i, d[1]][V_sym]
            for d in D:
                k = G.edges[d[0],d[1]][w_sym] / sum_w_dt
                if G.nodes[i][x_sym] <= thr:
                    G.edges[d[0], d[1]][v_sym] = k * G.nodes[i][x_sym]/dt
                else:
                    G.edges[d[0], d[1]][v_sym] = k * thr/dt
                for f in F:
                    thr += G.nodes[f][H_sym] - G.nodes[f][x_sym]

        H: nx.DiGraph = self.clone_graph(G)
        for i in G.nodes:
            S = G.predecessors(i)
            D = G.successors(i)
            sum_v_s = 0
            for s in S:
                sum_v_s += G.edges[s, i][v_sym]
            sum_v_d = 0
            for d in D:
                sum_v_d += G.edges[i, d][v_sym]
            H.nodes[i][x_sym] = G.nodes[i][x_sym] + sum_v_s * dt - sum_v_d * dt
        self._G = H
        return H

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

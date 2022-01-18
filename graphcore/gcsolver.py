# -*- coding: utf-8 -*-

import sys
import numpy as np
from numpy import pi, sin, cos, tan, arcsin, arccos, arctan, exp, log, log2, log10
import networkx as nx
import json
import traceback




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
            F = []
            for d in G.successors(i):
                if G.edges[i, d]['type'] == 'dataflow':
                    F.append(d)
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
            S = []
            for s in G.predecessors(i):
                if G.edges[s, i]['type'] == 'dataflow':
                    S.append(s)
            D = []
            for d in G.successors(i):
                if G.edges[i, d]['type'] == 'dataflow':
                    D.append(d)
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
        if t1 + duration <= t + dt:
            t2 = t1 + duration
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
        elif node['generator-type'] == 'custom':
            equation: str = node['generator-equation']
            eq2 = equation.replace("{t}", "t2")
            val2 = eval(eq2)
            eq1 = equation.replace("{t}", "t1")
            val1 = eval(eq1)
            ret = (val2 + val1) / 2 * dt
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


class GCGeneralSolver(GCSolver):

    def __init__(self, G, dt):
        super().__init__(G, dt)

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
        N = []
        for i in G.nodes:
            if G.nodes[i]['type'] not in ('folder', 'domain', 'note', 'memo'):
                N.append(i)
        N = tuple(N)
        for i in N:
            ### dataflow edge
            D = []
            for _ in G.successors(i):
                if G.edges[i, _]['type'] in ('dataflow', 'amplitude-flow'):
                    D.append(_)
            D = tuple(D)
            for d in D:
                delay = G.edges[i, d]['delay']
                duration = G.edges[i, d]['duration']
                if t < delay or delay + duration < t:
                    G.edges[i, d][w_sym] = 0
                else:
                    # val = 1.0/len(D)*(G.nodes[d[1]][H_sym] - G.nodes[d[1]][x_sym])/(G.edges[d[0], d[1]][l_sym]*dt)
                    val = 1.0/len(D)*(G.nodes[d][H_sym] - G.nodes[d][x_sym])/dt
                    if val <= G.edges[i, d][V_sym]:
                        G.edges[i, d][w_sym] = val
                    else:
                        G.edges[i, d][w_sym] = G.edges[i, d][V_sym]
            # sum of w^d
            sum_w = 0
            for d in D:
                sum_w += G.edges[i, d][w_sym]
            for d in D:
                if sum_w == 0:
                    k = 0
                else:
                    k = G.edges[i, d][w_sym] / sum_w
                if G.edges[i, d][w_sym] == 0:
                    G.edges[i, d][v_sym] = G.edges[i, d][w_sym]
                elif sum_w * dt <= G.nodes[i][x_sym]:
                    G.edges[i, d][v_sym] = k * G.edges[i, d][w_sym]
                elif G.nodes[i][x_sym] < sum_w * dt and k*G.nodes[i][x_sym] / dt <= G.edges[i, d][w_sym]:
                    G.edges[i, d][v_sym] = k * G.nodes[i][x_sym] / dt
                    if G.edges[i, d][w_sym] < G.edges[i, d][v_sym]:
                        G.edges[i, d][v_sym] = G.edges[i, d][w_sym]
                else:
                    G.edges[i, d][v_sym] = G.edges[i, d][w_sym]

            # ### amplitude-flow edge
            # D = []
            # for _ in G.successors(i):
            #     if G.edges[i, _]['type'] == 'amplitude-flow':
            #         D.append(_)
            # D = tuple(D)
            # for d in D:
            #     delay = G.edges[i, d]['delay']
            #     duration = G.edges[i, d]['duration']
            #     if delay <= t and t <= delay + duration:
            #         if G.edges[i, d][x_sym] == 0:
            #             G.edges[i, d][x_sym] = G.nodes[i][x_sym]

        H: nx.DiGraph = self.clone_graph(G)
        for i in N:
            ### dataflow edge
            S = []
            for _ in G.predecessors(i):
                if G.edges[_, i]['type'] in ('dataflow', 'amplitude-flow'):
                    S.append(_)
            S = tuple(S)
            D = []
            for _ in G.successors(i):
                if G.edges[i, _]['type'] in ('dataflow', 'amplitude-flow'):
                    D.append(_)
            D = tuple(D)
            sum_v_s = 0
            for s in S:
                v = G.edges[s, i][v_sym]
                if G.edges[s, i]['type'] == 'amplitude-flow':
                    amplitude = G.edges[s, i]['amplitude']
                    amplitude.replace("{t}", str(t))
                    amplitude = eval(amplitude)
                    v *= amplitude
                sum_v_s += v
            sum_v_d = 0
            for d in D:
                sum_v_d += G.edges[i, d][v_sym]
            gen_value = self.generated_value(G, i, t, dt)
            H.nodes[i][x_sym] = G.nodes[i][x_sym] + sum_v_s * dt - sum_v_d * dt + gen_value

            # ### amplitude-flow edge
            # S = []
            # for _ in G.predecessors(i):
            #     if G.edges[_, i]['type'] == 'amplitude-flow':
            #         S.append(_)
            # S = tuple(S)
            # sum_x_s = 0
            # for s in S:
            #     v = G.edges[s, i][v_sym]
            #     # print(v, type(v), dt, type(dt))
            #     dx = v * dt
            #     if G.edges[s, i][x_sym] < dx:
            #         dx = G.edges[s, i][x_sym]
            #     amplitude = G.edges[s, i]['amplitude']
            #     amplitude.replace("{t}", str(t))
            #     amplitude = eval(amplitude)
            #     G.edges[s, i][x_sym] -= dx
            #     sum_x_s += dx * amplitude
            # H.nodes[i][x_sym] += sum_x_s

        self._G = H
        return H


class SolverController:
    def __init__(self, handler):
        self._handler = handler
        self._cancel = False
        self._value_field = "value"
        self._maxValue_field = "maxValue"
        self._velocity_field = "velocity"
        self._maxVelocity_field = "maxVelocity"
        self._currentMaxVelocity_field = "currentMaxVelocity"
        self._distance_field = "distance"
        self._dt = 1
        self._steps = 100
        self._G = None
        self._post_data = ()
        self._print_progress = True

    @property
    def handler(self):
        return self._handler

    @property
    def dt(self):
        return self._dt

    def set_dt(self, v):
        self._dt = v

    @property
    def steps(self):
        return self._steps

    def set_steps(self, v):
        self._steps = v

    @property
    def G(self):
        return self._G

    def set_G(self, model_graph):
        G = nx.DiGraph()
        for n in model_graph.nodes:
            G.add_node(n)
            for k in model_graph.nodes[n].keys():
                G.nodes[n][k] = model_graph.nodes[n][k]['value']
        for e in model_graph.edges:
            G.add_edge(e[0], e[1])
            for k in model_graph.edges[e[0], e[1]].keys():
                G.edges[e[0], e[1]][k] = model_graph.edges[e[0], e[1]][k]['value']
        self._G = G

    @property
    def post_data(self):
        return self._post_data

    @property
    def print_progress(self):
        return self._print_progress

    def set_print_progress(self, f):
        self._print_progress = f

    def start(self):
        try:
            self._cancel = False
            value_property = self._value_field
            max_value_property = self._maxValue_field
            velocity_property = self._velocity_field
            max_velocity_property = self._maxVelocity_field
            current_max_velocity_property = self._currentMaxVelocity_field
            distance_property = self._distance_field
            dt = self.dt
            steps = self.steps
            solver: GCSolver = GCGeneralSolver(self.G, dt)
            G = solver.clone_graph(self.G)
            solver.G = G
            G_array = [nx.node_link_data(G)]
            t = 0
            for i in range(steps):
                if self.print_progress:
                    self.handler.reporter("{}-th iteration".format(i+1))
                if self._cancel:
                    break
                G = solver.calc_one_step(value_property, max_value_property, velocity_property, max_velocity_property,
                                         current_max_velocity_property, distance_property, t)
                t += dt
                data = nx.node_link_data(G)
                G_array.append(data)
                self._G = G
            if self.print_progress:
                self.handler.reporter("done")
            if not self._cancel:
                self._post_data = tuple(G_array)
        except Exception as ex:
            print('exception occured:', ex)
            print(traceback.format_exc())
        finally:
            self._cancel = True

    def cancel(self):
        self._cancel = True


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

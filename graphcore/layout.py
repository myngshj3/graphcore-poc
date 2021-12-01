# -*- coding: utf-8 -*-

import networkx as nx
import math
import itertools
import numpy as np


# function that returns 2D grid graph
def grid2d_graph(nxgrid, nygrid, orig_x, orig_y, dx, dy):
    G = nx.Graph()
    for i in range(nygrid):
        for j in range(nxgrid):
            node = nxgrid * i + j + 1
            G.add_node(node)
            attr = G.nodes[node]
            attr['x'] = i
            attr['y'] = j
    return G


# function that returns 2D grid node holder
def grid2d(nxgrid, nygrid):
    return np.ndarray(shape=(nxgrid, nygrid), dtype=np.object)


# function that returns combinations nCr
def combinations(a, r):
    rtn = []
    if len(a) < r:
        print("Bug!!!")
        return None
    iter = itertools.combinations(a, r)
    for e in iter:
        rtn.append(e)
    return rtn


# function that return permutation nPr
def permutations(a, r):
    rtn = []
    if len(a) < r:
        print("Bug!!!")
        return None
    iter = itertools.permutations(a, r)
    for e in iter:
        rtn.append(e)
    return rtn


# function that checks if two permutations are same
def same_permutations(a, b):
    if len(a) != len(b):
        return False
    for i, n in enumerate(a):
        if n != b[i]:
            return False
    return True


# function that checks if all entries are zeros
def zero_entry(e):
    for a in e:
        if a != 0:
            return False
    return True


# function that returns joined list
def join(L, R):
    rtn = []
    for e in L:
        rtn.append(e)
    for e in R:
        rtn.append(e)
    return rtn


# function that returns L\R
def substitute(L, R):
    rtn = []
    for e in L:
        if e not in R:
            rtn.append(e)
    return rtn


# function that return list product
def product(L, R):
    rtn = []
    for a in L:
        for b in R:
            p = join(a, b)
            rtn.append(p)
    return rtn


# function that returns zero padded permutations
def row_places_combinations(ar, m, r):
    rtn = []
    node_combinations = combinations(ar, m)
    for nodes in node_combinations:
        placeholders = permutations([i for i in range(r)], r)
        for p in placeholders:
            perm = [None for _ in range(r)]
            for i, e in enumerate(p):
                if p[i] < m:
                    perm[i] = nodes[p[i]]
            remains = substitute(ar, perm)
            if len(remains) == 0:
                rtn.append(perm)
            else:
                if len(remains) < m:
                    k = len(remains)
                else:
                    k = m
                for s in range(1, k + 1):
                    rows = row_places_combinations(remains, s, r)
                    t = product([perm], rows)
                    for u in t:
                        rtn.append(u)
    return rtn


# function that returns coordinated grid
def coordinate_on_grid(nodes, n, validator=None, canceler=None):
    rtn = []
    for m in range(1, n + 1):
        rows = permutations(nodes, m)
        for row in rows:
            if canceler is not None and canceler():
                return rows
            remains = substitute(nodes, row)
            if len(remains) == 0:
                grid = array1dto2d(row, int(len(row)/m), m)
                if validator is None or validator(grid):
                    rtn.append(grid)
            else:
                if len(remains) < m:
                    s = len(remains)
                else:
                    s = m
                for k in range(1, s + 1):
                    places = product([row], row_places_combinations(remains, k, m))
                    for p in places:
                        grid = array1dto2d(p, int(len(p) / m), m)
                        if validator is None or validator(grid):
                            rtn.append(grid)
    return rtn


# convert 1d array to 2d array
def array1dto2d(a, n, m):
    q = np.ndarray(shape=(n, m), dtype=np.object)
    for i in range(n):
        for j in range(m):
            q[i, j] = a[m * i + j]
    return q


# function that returns node coords combinations
def layout_combinations(nodes, validator=None, canceler=None):
    layouts = coordinate_on_grid(nodes, len(nodes), validator=validator, canceler=canceler)
    return layouts


# test_main
def test_main():
    graph = nx.DiGraph()
    nnodes = 5
    for i in range(1, nnodes + 1):
        graph.add_node("v{}".format(i))
        graph.nodes["v{}".format(i)]['x'] = i

    nedges = nnodes
    ne = 0
    while ne < nedges:
        (u, v) = np.random.randint(0, nnodes - 1, 2, dtype=np.int)
        u = "v{}".format(u)
        v = "v{}".format(v)
        has_edge = False
        for e in graph.edges:
            if (e[0] == u and e[1] == v) or (e[0] == v and e[1] == u):
                has_edge = True
                break
        if not has_edge:
            graph.add_edge(u, v)
            print("{} -> {}".format(u, v))
            ne += 1

    for i in range(1, nnodes):
        u = "v{}".format(i)
        v = "v{}".format(i+1)
        graph.add_edge(u, v)

    def validator(node_grid):
        (n, m) = node_grid.shape
        for row in range(n):
            for col in range(m):
                node = node_grid[row, col]
                if node is not None:
                    graph.nodes[node]['x'] = col
                    graph.nodes[node]['y'] = row
        for e in graph.edges:
            u0 = graph.nodes[e[0]]
            u1 = graph.nodes[e[1]]
            if not u0['x'] < u1['x']:
                return False
        return True

    layouts = layout_combinations(graph.nodes, validator=validator)
    for idx, layout in enumerate(layouts):
        print("-----({}) -----".format(idx))
        print(layout)


if __name__ == "__main__":
    test_main()


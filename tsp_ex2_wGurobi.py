from gurobipy import *
import networkx as nx
import random
import matplotlib.pyplot as plt
import numpy as np


def solve_tsp(V, c):
    """solve_tsp -- solve the traveling salesman problem
       - start with assignment model
       - add cuts until there are no sub-cycles
    Parameters:
        - V: set/list of nodes in the graph
        - c[i,j]: cost for traversing edge (i,j)
    Returns the optimum objective value and the list of edges used.
    """

    # 部分巡回路除去製薬
    def addcut(edges):
        G = nx.Graph()
        G.add_nodes_from(V)
        for (i, j) in edges:
            G.add_edge(i, j)
        Components = list(nx.connected_components(G))
        if len(Components) == 1:
            return False
        for S in Components:
            model.addConstr(quicksum(x[i, j] for i in S for j in S if j > i) <= len(S) - 1)

        return True

    model = Model("tsp")
    x = {}
    for i in V:
        for j in V:
            x[i, j] = model.addVar(ub=1)
    model.update()
    for i in V:
        model.addConstr(quicksum(x[j, i] for j in V if j < i) + quicksum(x[i, j] for j in V if j > i) == 2)
    model.setObjective(quicksum(c[i, j] * x[i, j] for i in V for j in V if j > i), GRB.MINIMIZE)
    EPS = 1.e-6
    while True:
        model.optimize()
        edges = []
        for (i, j) in x:
            if x[i, j].X > EPS:
                edges.append((i, j))
        if not addcut(edges):
            if model.IsMIP:
                break
            for (i, j) in x:
                x[i, j].VType = "B"
            model.update()
    return model.ObjVal, edges


def make_data(n):
    """make_data: compute matrix distance based on euclidean distance"""
    V = range(1, n + 1)
    xy = dict([(i, (random.random(), random.random())) for i in V])
    c = {}
    for i in V:
        for j in V:
            if j > i:
                c[i, j] = distance(xy[i][0], xy[i][1], xy[j][0], xy[j][1])
    return V, c, xy


def distance(x1, y1, x2, y2):
    """distance: euclidean distance between (x1,y1) and (x2,y2)"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def visualize_visit_order(edges, city_xy):
    """Visualize traveling path for given visit order"""
    G = nx.Graph()
    G.add_edges_from(edges)
    nx.draw(G, pos=city_xy)
    plt.show()
    # plt.figure(figsize=(4, 4))
    # for e in edges:
    #     plt.plot(city_xy[0][e[0]], city_xy[1][e[0]], 'o-')
    #     plt.plot(city_xy[0][e[1]], city_xy[1][e[1]], 'o-')
    # # plt.plot(x_arr, y_arr, 'o-')
    # plt.show()


def main():
    n = 200
    seed = 1
    random.seed(seed)
    V, c, xy = make_data(n)

    obj, edges = solve_tsp(V, c)

    print()
    print("Optimal tour:", edges)
    print("Optimal cost:", obj)
    print("V:", list(V))
    print("c:", c)

    visualize_visit_order(edges, xy)
    # plt.show()


if __name__ == "__main__":
    main()

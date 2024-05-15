import time
import networkx as nx
import numpy as np
import xlwt
import os
from networkx import betweenness_centrality as b_c
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import itertools

# global variable for tracking file numbers
file_counter = 0

# functions
def second_smallest(list):
    if len(list) < 2:
        raise ValueError("too few elements to find second_smallest")
    a, b = list[0], list[1]
    a, b = min(a,b), max(a,b)
    if len(list) == 2:
        return b
    c, rest = list[2], list[3:]
    if c < a:
        return second_smallest([c,a]+rest)
    if c < b:
        return second_smallest([a,c]+rest)
    return second_smallest([a,b]+rest)

def gini_coef(wealths):
    cum_wealths = np.cumsum(sorted(np.append(wealths, 0)))
    sum_wealths = cum_wealths[-1]
    xarray = np.array(range(0, len(cum_wealths))) / float(len(cum_wealths) - 1)
    yarray = cum_wealths / sum_wealths
    B = np.trapz(yarray, x=xarray)
    A = 0.5 - B
    return A / (A + B)

# network analysis function
def run_network_analysis(file_path):
    global file_counter
    start = time.time()

    G = nx.read_edgelist(file_path, nodetype=str,
                         data=(('weight', float),), create_using=nx.Graph())

    # minimum spanning tree
    X = csr_matrix(nx.to_numpy_matrix(G))
    Tcsr = minimum_spanning_tree(X)
    T = nx.from_numpy_matrix(Tcsr.toarray().astype(int))

    # add redundancy to increase network resilience
    candidate_redundancy = []
    g = list(T.nodes)
    for n in range(len(g)):
        a = g[n]
        del g[n]
        for m in range(len(g)):
            b = g[m]
            c = len(nx.shortest_path(T, source=a, target=b))
            if c <= 3:
                c_r = {a: b}
                candidate_redundancy.append(c_r)
        g = list(T.nodes)
    R_p = 0.3
    d = round(R_p * len(nx.edges(G)))
    candidate_list = list(itertools.combinations(candidate_redundancy, d))


    O_set = []
    for i in range(len(candidate_list)):
        t = nx.Graph(T)
        e = list(candidate_list[i])
        for index in range(len(e)):
            f = e[index]
            for key in f:
                t.add_edge(key, f[key])
        x = b_c(t, k=None, normalized=False, weight=None, endpoints=False, seed=None)
        dictlist = []
        for keys, value in x.items():
            temp = [value]
            dictlist.append(temp)
        gini_coef(dictlist)
        p = len(list(t.nodes))
        M = -np.ones((p, p))
        for n in list(t.nodes):
            M[n, n] = t.degree(n)
        h = np.linalg.eig(M)
        numda = second_smallest(list(h[0]))
        O = numda - gini_coef(dictlist)
        O_set.append(O)
        z = O_set.index(max(O_set))
    e_max = candidate_list[z]
    for index in range(len(e_max)):
        f = e_max[index]
        for key in f:
            T.add_edge(key, f[key])

    # identify optimal hubs
    i = 0
    degree_Volume = []

    for node in list(T.nodes):
        i = i + 1
        a = node
        sum = 0
        list(T.nodes).remove(node)
        other_nodes = list(T.nodes)
        for other_node in other_nodes:
            S_P = nx.shortest_path(T, source=other_node, target=a)
            sum = sum + len(S_P)
        b = T.degree(node)
        c = b / sum
        degree_Volume.append(c)
        list(T.nodes).insert(i - 1, node)
    nodenames = list(G.nodes)
    mapping = {d: nodename for d, nodename in enumerate(nodenames)}
    # now mapping looks like {0:'a', 1:'b', ...}
    H = nx.relabel_nodes(T, mapping)
    print(list(H.edges))
    print(list(H.nodes)[degree_Volume.index(max(degree_Volume))])

    data = list(H.edges)
    file_counter += 1
    dateTime = time.strftime("%Y-%m-%d", time.localtime())
    filename = f'Example/result-{file_counter}-{dateTime}.xlsx'

    wb = xlwt.Workbook()
    allDebtSheet = wb.add_sheet('data')
    # write the data into allDebtSheet ...
    for i in range(len(data)):
        for j in range(2):
            allDebtSheet.write(i, j, data[i][j])
    wb.save(filename)

    end = time.time()
    print(f"Time taken for file {file_path}: {end - start} seconds")

# traverse the txt files and run analysis function
def run_network_analysis_on_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {file_path}")
            run_network_analysis(file_path)
        else:
            continue

# folder path
folder_path = 'Example'

# run the code
run_network_analysis_on_folder(folder_path)

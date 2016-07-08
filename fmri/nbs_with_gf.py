''' Checks whether there is a group difference in the connectivity '''

import numpy as np
import nbs
import os
import pandas as pd


home = os.path.expanduser('~')
gf_fname = home + '/data/fmri/gf.csv'
subjs_fname = home+'/data/fmri/joel_all.txt'
data_dir = home + '/data/fmri_full_grid/'
res_dir = home + '/data/fmri_full_grid/results/'
thresh = [.95, .99, .995, .999]
nperms = 100

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)


data = {'NV': [], 'persistent': [], 'remission': []}
for s in subjs:
    fname = data_dir + '%s_maskAve.1D' % s
    subj_data = np.genfromtxt(fname)
    data = np.arctanh(np.corrcoef(subj_data.T))
    # if s in g1:
    #     g1_data.append(data)
    #     g1_subjs.append(s)
    # elif s in g2:
    #     g2_data.append(data)
    #     g2_subjs.append(s)
    #     g2_inatt.append(inatt[int(s)])
    #     g2_hi.append(hi[int(s)])
    # elif s in g3:
    #     g3_data.append(data)
    #     g3_subjs.append(s)
    #     g3_inatt.append(inatt[int(s)])
    #     g3_hi.append(hi[int(s)])

# res = []
# nvVSper = []
# nvVSrem = []
# perVSrem = []
# nvVSper_mwu = []
# nvVSrem_mwu = []
# perVSrem_mwu = []
# anova = []
# kruskal = []
# inatt = []
# hi = []

# x = np.array(g1_data).transpose([1,2,0])
# y = np.array(g2_data).transpose([1,2,0])
# z = np.array(g3_data).transpose([1,2,0])
# for t in thresh:
#     anova.append(nbs.compute_nbs('anova',x,y,t,nperms,z))
#     kruskal.append(nbs.compute_nbs('kw',x,y,t,nperms,z))
#     nvVSper_mwu.append(nbs.compute_nbs('mwu',x,y,t,nperms))
#     nvVSrem_mwu.append(nbs.compute_nbs('mwu',x,z,t,nperms))
#     perVSrem_mwu.append(nbs.compute_nbs('mwu',y,z,t,nperms))
#     nvVSper.append(nbs.compute_nbs('ttest',x,y,t,nperms))
#     nvVSrem.append(nbs.compute_nbs('ttest',x,z,t,nperms))
#     perVSrem.append(nbs.compute_nbs('ttest',y,z,t,nperms))
#     inatt.append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_inatt+g3_inatt),t,nperms))
#     hi.append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_hi+g3_hi),t,nperms))

# n1 = len(g1_data[0])
# n2 = len(g2_data[0])
# n3 = len(g3_data[0])
# print 'size1 =', n1
# print 'size2 =', n2
# print 'size3 =', n3
# print 'g1 =',g1_fname
# print 'g2 =',g2_fname
# print 'g3 =',g3_fname
# print 'thresh:', thresh


# import networkx as nx
# import matplotlib.pyplot as plt

# def draw_graph(mat):

#     # create networkx graph
#     G=nx.Graph()

#     # add nodes
#     for node in range(mat.shape[0]):
#         G.add_node(node)

#     # add edges
#     conns = np.nonzero(mat)
#     for i in range(len(conns[0])):
#         G.add_edge(conns[0][i], conns[1][i])

#     # draw graph
#     pos = nx.shell_layout(G)
#     nx.draw(G, pos)

#     # show graph
#     plt.show(block=False)

#     return G

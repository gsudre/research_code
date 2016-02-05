''' Checks whether there is a group difference in the connectivity '''

import numpy as np
# import cviewer.libs.pyconto.groupstatistics.nbs as nbs
import nbs
import os
import copy
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
bands = range(len(band_names))
g1_fname = home+'/data/meg/nv_subjs.txt'
g2_fname = home+'/data/meg/persistent_subjs.txt'
g3_fname = home+'/data/meg/remitted_subjs.txt'
inatt_fname = home+'/data/meg/inatt.txt'
hi_fname = home+'/data/meg/hi.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home+'/data/meg/sam_narrow/'
cmethod = 5
thresh = [.99, 0.999]#[.95, .99, .995, .999]
nperms = 5000

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
fid3 = open(g3_fname, 'r')
g3 = [line.rstrip() for line in fid3]

res = np.recfromtxt(inatt_fname, delimiter='\t')
inatt = {}
for rec in res:
    inatt[rec[0]] = rec[1]
res = np.recfromtxt(hi_fname, delimiter='\t')
hi = {}
for rec in res:
    hi[rec[0]] = rec[1]

targets = np.recfromtxt(data_dir +'tlrc_seeds.txt',delimiter='\t',skip_header=1)
nlabels=len(targets)

g1_data = [[] for b in bands]
g2_data = [[] for b in bands]
g3_data = [[] for b in bands]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g2_inatt = []
g2_hi = []
g3_inatt = []
g3_hi = []
for s in subjs:
    fname = data_dir + '%s_roi_connectivity.npy'%s
    conn = np.load(fname)[()].squeeze()
    for bidx,bval in enumerate(bands):
        data = conn[bval,cmethod,:,:].squeeze()
        if s in g1:
            g1_data[bidx].append(data)
            if bidx==0:
                g1_subjs.append(s)
        elif s in g2:
            g2_data[bidx].append(data)
            if bidx==0:
                g2_subjs.append(s)
                g2_inatt.append(inatt[s])
                g2_hi.append(hi[s])
        elif s in g3:
            g3_data[bidx].append(data)
            if bidx==0:
                g3_subjs.append(s)
                g3_inatt.append(inatt[s])
                g3_hi.append(hi[s])

res = []
nvVSper = [[] for i in range(len(bands))]
nvVSrem = [[] for i in range(len(bands))]
perVSrem = [[] for i in range(len(bands))]
nvVSper_mwu = [[] for i in range(len(bands))]
nvVSrem_mwu = [[] for i in range(len(bands))]
perVSrem_mwu = [[] for i in range(len(bands))]
anova = [[] for i in range(len(bands))]
kruskal = [[] for i in range(len(bands))]
inatt = [[] for i in range(len(bands))]
hi = [[] for i in range(len(bands))]
for b in range(len(bands)):
    x = np.array(g1_data[b]).transpose([1,2,0])
    y = np.array(g2_data[b]).transpose([1,2,0])
    z = np.array(g3_data[b]).transpose([1,2,0])
    # # remove subjects that have NaNs
    # delme = np.unique(np.nonzero(np.isnan(x))[2])
    # x = np.delete(x, delme, axis=2)
    # if stats=='linreg':
    #     x_sx = copy.deepcopy(g1_sx)
    #     for i in delme:
    #         x_sx.pop(i)
    # delme = np.unique(np.nonzero(np.isnan(y))[2])
    # y = np.delete(y, delme, axis=2)
    # if stats=='linreg':
    #     y_sx = copy.deepcopy(g2_sx)
    #     for i in delme:
    #         y_sx.pop(i)
    # if len(g3)>0:
    #     z = np.array(g3_data[b]).transpose([1,2,0])
    #     delme = np.unique(np.nonzero(np.isnan(z))[2])
    #     z = np.delete(z, delme, axis=2)
    for t in thresh:
        # anova[b].append(nbs.compute_nbs('anova',x,y,t,nperms,z))
        # kruskal[b].append(nbs.compute_nbs('kw',x,y,t,nperms,z))
        # nvVSper_mwu[b].append(nbs.compute_nbs('mwu',x,y,t,nperms))
        # nvVSrem_mwu[b].append(nbs.compute_nbs('mwu',x,z,t,nperms))
        # perVSrem_mwu[b].append(nbs.compute_nbs('mwu',y,z,t,nperms))
        # nvVSper[b].append(nbs.compute_nbs('ttest',x,y,t,nperms))
        nvVSrem[b].append(nbs.compute_nbs('ttest',x,z,t,nperms))
        # perVSrem[b].append(nbs.compute_nbs('ttest',y,z,t,nperms))
        # inatt[b].append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_inatt+g3_inatt),t,nperms))
        # hi[b].append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_hi+g3_hi),t,nperms))

n1 = len(g1_data[0])
n2 = len(g2_data[0])
n3 = len(g3_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'size3 =', n3
print 'g1 =',g1_fname
print 'g2 =',g2_fname
print 'g3 =',g3_fname
m = ['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
print m[cmethod]
print 'thresh:', thresh


import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(mat):

    # create networkx graph
    G=nx.Graph()

    # add nodes
    for node in range(mat.shape[0]):
        G.add_node(node)

    # add edges
    conns = np.nonzero(mat)
    for i in range(len(conns[0])):
        G.add_edge(conns[0][i], conns[1][i])

    # draw graph
    pos = nx.shell_layout(G)
    nx.draw(G, pos)

    # show graph
    plt.show(block=False)

    return G

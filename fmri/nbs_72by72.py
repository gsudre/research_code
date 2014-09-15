''' Checks whether there is a group difference in the connectivity '''

import numpy as np
# import cviewer.libs.pyconto.groupstatistics.nbs as nbs
import nbs
import os
home = os.path.expanduser('~')


g1_fname = home+'/data/fmri/joel_nvs.txt'
g2_fname = home+'/data/fmri/joel_persistent.txt'
g3_fname = home+'/data/fmri/joel_remission.txt'
inatt_fname = home+'/data/fmri/inatt.txt'
hi_fname = home+'/data/fmri/hi.txt'
subjs_fname = home+'/data/fmri/joel_all.txt'
data_dir = home+'/data/results/fmri_72ROIsJoel/'
thresh = [.95, .99, .995, .999]
nperms = 1000

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

g1_data = []
g2_data = []
g3_data = []
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g2_inatt = []
g2_hi = []
g3_inatt = []
g3_hi = []
for s in subjs:
    subj_data = []
    for r in range(nlabels):
        fname = data_dir + '%s_roi%d.1D'%(s,r)
        subj_data.append(np.genfromtxt(fname))
    data = np.arctanh(np.corrcoef(subj_data))
    if s in g1:
        g1_data.append(data)
        g1_subjs.append(s)
    elif s in g2:
        g2_data.append(data)
        g2_subjs.append(s)
        g2_inatt.append(inatt[int(s)])
        g2_hi.append(hi[int(s)])
    elif s in g3:
        g3_data.append(data)
        g3_subjs.append(s)
        g3_inatt.append(inatt[int(s)])
        g3_hi.append(hi[int(s)])

res = []
nvVSper = []
nvVSrem = []
perVSrem = []
nvVSper_mwu = []
nvVSrem_mwu = []
perVSrem_mwu = []
anova = []
kruskal = []
inatt = []
hi = []

x = np.array(g1_data).transpose([1,2,0])
y = np.array(g2_data).transpose([1,2,0])
z = np.array(g3_data).transpose([1,2,0])
for t in thresh:
    anova.append(nbs.compute_nbs('anova',x,y,t,nperms,z))
    kruskal.append(nbs.compute_nbs('kw',x,y,t,nperms,z))
    nvVSper_mwu.append(nbs.compute_nbs('mwu',x,y,t,nperms))
    nvVSrem_mwu.append(nbs.compute_nbs('mwu',x,z,t,nperms))
    perVSrem_mwu.append(nbs.compute_nbs('mwu',y,z,t,nperms))
    nvVSper.append(nbs.compute_nbs('ttest',x,y,t,nperms))
    nvVSrem.append(nbs.compute_nbs('ttest',x,z,t,nperms))
    perVSrem.append(nbs.compute_nbs('ttest',y,z,t,nperms))
    inatt.append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_inatt+g3_inatt),t,nperms))
    hi.append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_hi+g3_hi),t,nperms))

n1 = len(g1_data[0])
n2 = len(g2_data[0])
n3 = len(g3_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'size3 =', n3
print 'g1 =',g1_fname
print 'g2 =',g2_fname
print 'g3 =',g3_fname
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

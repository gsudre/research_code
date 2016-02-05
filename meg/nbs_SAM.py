''' Checks whether there is a group difference in the connectivity '''

import numpy as np
# import cviewer.libs.pyconto.groupstatistics.nbs as nbs
import nbs
import os
import copy
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = [3]#range(len(band_names))
# g1_fname = home+'/data/meg/nv_subjs.txt'
g1_fname = home+'/data/meg/persistent_subjs.txt'
# g1_fname = home+'/data/meg/remitted_subjs.txt'
# g2_fname = home+'/data/meg/nv_subjs.txt'
# g2_fname = home+'/data/meg/persistent_subjs.txt'
g2_fname = home+'/data/meg/remitted_subjs.txt'
g3_fname = ''#home+'/data/meg/remitted_subjs.txt'
sx_fname = home+'/data/meg/hi.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home+'/data/meg/sam/'
cmethod = 5
thresh = 3
nperms = 1000
# tail = 'left'
tail = 'right'
hemi = -1
stats = 'ttest'

# list of lists, indicating which ROIs are grouped together, avoiding non-meaningful connections. Set all2all=True if interested in doing each ROI by itself
selected_labels = []
# selected_labels = [10,9,32,24,23,31,30,39,40] #DMN
# selected_labels = [[32,24],[23],[39]] #DMN-select
# selected_labels = [8, 39, 40, 7] # dorsal
# selected_labels = [39,40,41,42, 44,45,46] #ventral
# selected_labels = [39, 44,45,46] #ventral-select
# selected_labels = [46,9, 8, 44,45,47, 6, 7, 5] # cognitive control
# selected_labels = [32,24, 25, 10,11,47] #affective
selected_labels = [1,10,11,17,18,19,2,20,21,22,23,24,25,3,31,32,37,38,39,4,40,41,42,43,44,45,46,47,5,6,7,8,9] #Hillebrand, 33 only had one voxel
# selected_labels = [24,10,32,30,23,31,39,40,21,24,9]

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
if len(g3_fname)>0:
    fid3 = open(g3_fname, 'r')
    g3 = [line.rstrip() for line in fid3]
else:
    g3 = []

res = np.recfromtxt(sx_fname, delimiter='\t')
sx = {}
for rec in res:
    sx[rec[0]] = rec[1]

areas = np.load(home+'/sam/areas.npy')[()]
res = np.load(home+'/sam/rois.npz')
rois = list(res['rois'])
nlabels=len(rois)

if hemi>=0:
    if len(selected_labels)>0:
        brodmann_val = [areas[l][hemi] for l in selected_labels]
    else:
        if hemi==0:
            brodmann_val = rois[1:-1:2]
        else:
            brodmann_val = rois[0:-1:2]
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 
else:
    if len(selected_labels)>0:
        brodmann_val = [i for l in selected_labels for i in areas[l]]
    else:
        brodmann_val = rois
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 

g1_data = [[] for b in bands]
g2_data = [[] for b in bands]
g3_data = [[] for b in bands]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g1_sx = []
g2_sx = []
for s in subjs[1:]:
    fname = data_dir + '%s_roi_connectivity.npy'%s
    conn = np.load(fname)[()]
    for bidx,bval in enumerate(bands):
        data = conn[bval][cmethod][:,:].squeeze()
        data = np.delete(data, delme, axis=0)
        data = np.delete(data, delme, axis=1)
        iu = np.triu_indices(nlabels, k=1)
        il = np.tril_indices(nlabels, k=-1)
        data[iu] = data[il]
        if s in g1:
            g1_data[bidx].append(data)
            if bidx==0:
                g1_subjs.append(s)
                if stats=='linreg':
                    g1_sx.append(sx[s])
        elif s in g2:
            g2_data[bidx].append(data)
            if bidx==0:
                g2_subjs.append(s)
                if stats=='linreg':
                    g2_sx.append(sx[s])
        elif s in g3:
            g3_data[bidx].append(data)
            if bidx==0:
                g3_subjs.append(s)

res = []
for b in range(len(bands)):
    x = np.array(g1_data[b]).transpose([1,2,0])
    y = np.array(g2_data[b]).transpose([1,2,0])
    # remove subjects that have NaNs
    delme = np.unique(np.nonzero(np.isnan(x))[2])
    x = np.delete(x, delme, axis=2)
    if stats=='linreg':
        x_sx = copy.deepcopy(g1_sx)
        for i in delme:
            x_sx.pop(i)
    delme = np.unique(np.nonzero(np.isnan(y))[2])
    y = np.delete(y, delme, axis=2)
    if stats=='linreg':
        y_sx = copy.deepcopy(g2_sx)
        for i in delme:
            y_sx.pop(i)
    if len(g3)>0:
        z = np.array(g3_data[b]).transpose([1,2,0])
        delme = np.unique(np.nonzero(np.isnan(z))[2])
        z = np.delete(z, delme, axis=2)
        
    if stats in ['ttest','mwu']:
        pval, adj, null = nbs.compute_nbs(stats,x,y,thresh,nperms,tail) 
    elif stats=='linreg':
        adhd = np.dstack([x, y])
        sx = np.array(x_sx + y_sx)
        pval, adj, null = nbs.compute_nbs(stats,adhd,sx,thresh,nperms) 
    elif stats in ['anova','kw']:
        pval, adj, null = nbs.compute_nbs(stats,x,y,thresh,nperms,tail,z) 
    res.append([pval,adj])

n1 = len(g1_data[0])
n2 = len(g2_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'g1 =',g1_fname
print 'g2 =',g2_fname
print 'g3 =',g3_fname
m = ['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
print m[cmethod]
print 'hemi:', hemi
print tail
print 'thresh:', thresh
for i,j in enumerate(res):
    print bands[i], ':', j[0]

def map_connections(adj, cl):
    conn = np.nonzero(adj==cl)
    conn_list = []
    for i in range(len(conn[0])):
        edge = [conn[0][i], conn[1][i]]
        edge_bvals = [rois[idx[j]] for j in edge]
        edge_brodmann = [key for j in edge_bvals for key,val in areas.iteritems() if j in val]
        edge_str = []
        for j in [0,1]:
            if areas[edge_brodmann[j]].index(edge_bvals[j])==0:
                h='L'
            else:
                h='R'
            edge_str.append('%d-%s'%(edge_brodmann[j],h))
        edge_str.sort()
        if edge_str not in conn_list:   
            conn_list.append(edge_str)
    print conn_list
    return conn_list


def plot_group_diff(adj, cl=1, rel='be'):
    conn_names = map_connections(adj, cl)
    conn = np.nonzero(adj==cl)
    conn_list = []
    for i in range(len(conn[0])):
        edge = [conn[0][i], conn[1][i]]
        edge.sort()
        if edge not in conn_list:   
            conn_list.append(edge)
    xp = []
    yp = []
    cnt = 0
    graph_str = ''
    for idx, i in enumerate(conn_list):
        if (rel=='be' and np.median(x[i[0],i[1],:])>=np.median(y[i[0],i[1],:])) or (rel=='se' and np.median(x[i[0],i[1],:])<=np.median(y[i[0],i[1],:])) or rel==None:
            xp.append(x[i[0],i[1],:])
            yp.append(y[i[0],i[1],:])
            cnt+=1
            graph_str+='(%d,%d)'%(conn_names[idx][0],conn_names[idx][1])
    print graph_str
    xp = np.array(xp)
    yp = np.array(yp)
    print xp.shape
    print yp.shape
    for i in range(cnt):
        figure()
        boxplot([xp[i,:], yp[i,:]])
        title('%d'%i)
    figure()
    boxplot([xp.mean(axis=0), yp.mean(axis=0)])
    title('mean')


import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(graph):

    # extract nodes from graph
    nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])

    # create networkx graph
    G=nx.Graph()

    # add nodes
    for node in nodes:
        G.add_node(node)

    # add edges
    for edge in graph:
        G.add_edge(edge[0], edge[1])

    # draw graph
    pos = nx.shell_layout(G)
    nx.draw(G, pos)

    # show graph
    plt.show()

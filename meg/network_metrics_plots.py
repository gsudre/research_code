import mne
import numpy as np
import networkx as nx
import os
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = range(len(band_names))
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = '/Users/sudregp/data/meg/sam/'
cmethod = 5
hemi = -1
all2all = False
selected_labels = [1,10,11,17,18,19,2,20,21,22,23,24,25,3,31,32,37,38,39,4,40,41,42,43,44,45,46,47,5,6,7,8,9] #Hillebrand, 33 only had one voxel
selected_labels = []

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
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

# collect all the data
all_data = [[] for b in bands]
for s in subjs:
    fname = data_dir + '%s_roi_connectivity.npy'%s
    conn = np.load(fname)[()]
    for bidx,bval in enumerate(bands):
        data = conn[bval,cmethod,:,:].squeeze()
        data = np.delete(data, delme, axis=0)
        data = np.delete(data, delme, axis=1)
        iu = np.triu_indices(nlabels, k=1)
        il = np.tril_indices(nlabels, k=-1)
        data[iu] = data[il]
        all_data[bidx].append(data)

# # make one subplot per distribution of connections
# figure()
# for p in range(len(bands)):
#     vals = []
#     subplot(3,2,p+1) 
#     for s in all_data[p]:
#         vals.append(s[il])
#     data = np.array(vals).flatten()
#     data = data[~np.isnan(data)]
#     hist(data, bins=20)
#     title(str(band_names[p]))

# make one subplot per cluster coefficient for integration
conn_threshold = np.arange(-.1, .2, .005)
pct_threshold = np.arange(.1, 1.01, .05)
x = pct_threshold
figure()
for p in range(len(bands)):
    print p
    ax = subplot(3,2,p+1) 
    y = []
    sigma = []
    # for thresh in conn_threshold:
    for pct in pct_threshold:
        vals = []
        for s in all_data[p]:
            G=nx.Graph()
            nfeats = s.shape[0]
            # figuring out which connections to keep
            all_weights = np.sort(s[il].flatten())
            thresh = all_weights[np.int((1-pct)*len(all_weights))]
            for node in range(nfeats):
                G.add_node(node)
            for i in range(nfeats):
                for j in range(i+1):
                    if s[i,j]>=thresh:
                        G.add_edge(i, j)

            # In the paper: average_clustering, betweenness_centrality, modularity?, characteristic path length?
            # Other measures:
            # vals.append(np.mean(nx.degree(G).values()))

            # Functional segregation
            # vals.append(nx.average_clustering(G))
            # vals.append(nx.transitivity(G))
            # vals.append(np.mean(nx.triangles(G).values()))


            # connectivity
            # vals.append(nx.average_node_connectivity(G))

            # Functional integration
            tmp = []
            for g in nx.connected_component_subgraphs(G):
                try:
                    tmp.append(nx.average_shortest_path_length(g))
                except:
                    pass
            vals.append(np.mean(tmp))

            # centrality
            # vals.append(np.mean(nx.betweenness_centrality(G).values()))
            # vals.append(np.mean(nx.closeness_centrality(G).values()))

            # resilience
            # vals.append(np.mean(nx.assortativity.average_degree_connectivity(G).values()))
            # vals.append(np.mean(nx.assortativity.average_neighbor_degree(G).values()))

        y.append(np.mean(vals))
        sigma.append(np.std(vals))
    ax.plot(x,y,lw=2)
    y = np.array(y)
    sigma = np.array(sigma)
    ax.fill_between(x, y+sigma, y-sigma, facecolor='blue', alpha=0.5)

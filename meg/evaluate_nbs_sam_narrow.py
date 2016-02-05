import numpy as np

band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
bands = [1,3,5]
thresh = [0.995] #[.95, .99, .995, .999]
alpha = .07
res = nvVSrem
for b, band in enumerate(bands):
    for t, th in enumerate(thresh):
        for p, pval in enumerate(res[b][t][0]): 
            if pval<=alpha:
                nedges = len(np.nonzero(res[b][t][1]==p+1)[0])
                print 'Band: %s, threshold: %.4f, pval: %.3f, edges: %d, pct connected: %.4f'%(band_names[band], th, pval, nedges, float(nedges)/(72*71/2) ) 
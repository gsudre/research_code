# Outputs the IC number at the elbow of the PCA plot
import sys


def do_pca(fname):
    import tables
    fid = tables.open_file(fname)
    X = fid.root.Ydd[:]
    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=100)
    svd.fit(X.T)
    return svd.explained_variance_ratio_


def dist(x1,y1, x2,y2, x3,y3): # x3,y3 is the point
    import math
    px = x2-x1
    py = y2-y1

    something = px*px + py*py

    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    # Note: If the actual distance does not matter,
    # if you only want to compare what this function
    # returns to other results of this function, you
    # can just return the squared distance instead
    # (i.e. remove the sqrt) to gain a little performance

    dist = math.sqrt(dx*dx + dy*dy)

    return dist


def print_elbow(ratio):
    comps = np.arange(len(ratio)) + 1
    dists = [dist(comps[0], ratio[0], comps[-1], ratio[-1], comps[i], ratio[i])
             for i in range(len(ratio))]
    print comps[np.argmax(dists)]


ratio = do_pca(sys.argv[1])
print_elbow(ratio)
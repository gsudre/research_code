import numpy
import pyctf

ds_fname = '/mnt/neuro/MEG_data/raw/20110429/CXIFPSQC_rest_20110429_01.ds/'

ds = pyctf.dsopen(ds_fname)

# Continuous head localization channels.

fids = ['Na', 'Le', 'Re']
chans = {fids[0]: ['HLC0011', 'HLC0012', 'HLC0013'],
         fids[1]: ['HLC0021', 'HLC0022', 'HLC0023'],
         fids[2]: ['HLC0031', 'HLC0032', 'HLC0033']}

all_ds = []
for chan in fids:
    i = fids.index(chan)
    o = ds.head[i]
    c = chans[chan]
    ch_map = ds.channel

    # make an nx3; one channel per column
    trial=0
    l = []
    for ch in c:
        x = ds.getDsData(trial, ch_map[ch])
        x.shape = (x.shape[0], 1)
        l.append(x)
    d = numpy.hstack(l) * 100. # m -> cm

    # Transform to relative head coordinates.
    # fid.fid_transform() only does one vector, but
    # we can do the whole array just as easily.

    m = ds.dewar_to_head    # 4x4 transform
    r = m[0:3, 0:3]         # 3x3 rotation
    t = m[0:3, 3]           # translation
    d = numpy.inner(d, r) + t - o # - o makes relative to .hc origin
    all_ds.append(d)
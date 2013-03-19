import mne
import pylab as pl
import numpy as np
import env

res = np.load(env.results + 'plis_good_subjects.npz')
con = res['plis'][()]
# labels = res['labels'][()]


def plot_circular(con, labels):
    label_names = [label.name for label in labels]

    lh_labels = [name for name in label_names if name.endswith('lh')]

    # Get the y-location of the label
    label_ypos = list()
    for name in lh_labels:
        idx = label_names.index(name)
        ypos = np.mean(labels[idx].pos[:, 1])
        label_ypos.append(ypos)

    # Reorder the labels based on their location
    lh_labels = [label for (ypos, label) in sorted(zip(label_ypos, lh_labels))]

    # For the right hemi
    rh_labels = [label[:-2] + 'rh' for label in lh_labels]

    # Save the plot order and create a circular layout
    node_order = list()
    node_order.extend(lh_labels[::-1])  # reverse the order
    node_order.extend(rh_labels)

    node_angles = mne.viz.circular_layout(label_names, node_order, start_pos=90)

    # Plot the graph using node colors from the FreeSurfer parcellation. We only
    # show the 300 strongest connections.
    mne.viz.plot_connectivity_circle(con, label_names, n_lines=300, node_angles=node_angles, title='All-to-All PLI Resting')

    pl.show(block=False)

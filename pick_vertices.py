''' Script to show the picked point in the surface on the screen'''

import surfer
from mayavi import mlab
import numpy as np

fig = mlab.figure()
tha = surfer.Brain('mni', 'rh', 'thalamus', curv=False, figure=fig)
Y = np.array(range(3108))
tha.add_data(Y)


def picker_callback(picker_obj):
    print picker_obj.point_id

fig.on_mouse_pick(picker_callback)

mlab.show()

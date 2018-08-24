import sys
import pandas as pd
import os
import numpy as np
from tpot import TPOTClassifier
from sklearn.dummy import DummyClassifier
from sklearn import metrics, preprocessing
import multiprocessing


data_fname = sys.argv[1]
clin_fname = sys.argv[2]
target = sys.argv[3]
config_str = sys.argv[4]
if config_str == 'None':
    config_str = None
else:
    config_str = config_str.replace('_', ' ')
export_fname = sys.argv[5]
if sys.argv[6] == '-1':
    cpus = int(os.environ.get('SLURM_CPUS_PER_TASK', '2'))
else:
    cpus = int(sys.argv[6])
metric_str = sys.argv[7]

print(data_fname)
print(clin_fname)
print(target)
print(config_str)
print(export_fname)
print(metric_str)

home = os.path.expanduser('~')

data = pd.read_csv(data_fname)
clin = pd.read_csv(clin_fname)

df = clin.merge(data, on='mask.id')
voxels = [cname for cname in data.columns if cname.find('v')==0]
X = df[voxels]
y = df[target]
# TPOT doesn't like categorical variables
lbl = preprocessing.LabelEncoder()
y2 = lbl.fit_transform(y)

multiprocessing.set_start_method('forkserver', force=True)
tpot = TPOTClassifier(verbosity=2,
                     config_dict=config_str, n_jobs=cpus, 
                     periodic_checkpoint_folder=home+'/data/tpot/checkpoints',
                     memory='auto', random_state=42,
                     scoring=metric_str)

dummy = DummyClassifier()
dummy.fit(X, y2)
ypred = dummy.predict(X)
scr = metrics.get_scorer(metric_str)

print('CPUs:', cpus)
print('dummy:', scr(dummy, y2.reshape(-1, 1), ypred))
tpot.fit(X, y2)
tpot.export(export_fname)
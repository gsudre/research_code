import sys
import pandas as pd
import os
import numpy as np
from scipy import stats
from tpot import TPOTRegressor
from sklearn.dummy import DummyRegressor
from sklearn import metrics
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

print(data_fname)
print(clin_fname)
print(target)
print(config_str)
print(export_fname)

home = os.path.expanduser('~')
data = pd.read_csv(data_fname)
clin = pd.read_csv(clin_fname)

df = clin.merge(data, on='mask.id')
voxels = [cname for cname in data.columns if cname.find('v')==0]
junk = stats.mstats.winsorize(df[target],inplace=True,limits=(.01, .01))
X = df[voxels]
y = df[target]
multiprocessing.set_start_method('forkserver', force=True)

tpot = TPOTRegressor(verbosity=2,
                     config_dict=config_str, n_jobs=cpus, 
                     periodic_checkpoint_folder=home+'/data/tpot/checkpoints',
                     memory='auto', random_state=42)

dummy = DummyRegressor()
dummy.fit(X, y)
ypred = dummy.predict(X)

print('CPUs:', cpus)
print('dummy:', -metrics.mean_squared_error(y, ypred))
tpot.fit(X, y)
tpot.export(export_fname)
import keras
from matplotlib import pyplot as plt
import numpy as np
import gzip
#%matplotlib inline
from keras.layers import Input,Conv3D,MaxPooling3D,UpSampling3D
from keras.models import Model
from keras.optimizers import RMSprop
import numpy as np
import os
from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasRegressor

home = os.path.expanduser('~')
data = np.load(home + '/data/tmp/ad_223_3d.npz')['data']

data2 = data[:, :, :, :, np.newaxis]
data2 = data2 / np.max(data2)

batch_size = 5
epochs = 40
inChannel = 1
x, y, z = data.shape[1:]
input_img = Input(shape = (x, y, z, inChannel))

def create_model(init_mode='glorot_uniform', activation='relu'):
    #encoder
    x = Conv3D(32, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(input_img)
    x = MaxPooling3D(pool_size=(2, 2, 2))(x) 
    x = Conv3D(16, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(x)
    x = MaxPooling3D(pool_size=(2, 2, 2))(x) 
    x = Conv3D(8, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(x)
    x = MaxPooling3D(pool_size=(2, 2, 2))(x) 
    x = Conv3D(4, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(x)
    encoded = MaxPooling3D(pool_size=(7, 7, 3))(x)

    #decoder
    x = Conv3D(4, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(encoded)
    x = UpSampling3D((7,7,3))(x)
    x = Conv3D(8, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(x)
    x = UpSampling3D((2,2,2))(x)
    x = Conv3D(16, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(x) 
    x = UpSampling3D((2,2,2))(x)
    x = Conv3D(32, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(x)
    x = UpSampling3D((2,2,2))(x)
    decoded = Conv3D(1, (3, 3, 3), activation=activation, kernel_initializer=init_mode, padding='same')(x)

    autoencoder = Model(input_img, decoded)
    autoencoder.compile(loss='mse', optimizer = 'adadelta')
    return autoencoder


# fix random seed for reproducibility
seed = 7
np.random.seed(seed)
# create model
model = KerasRegressor(build_fn=create_model, epochs=epochs, batch_size=batch_size, verbose=1, validation_split=.1)
# define the grid search parameters
params = ['softmax', 'softplus', 'softsign', 'relu', 'tanh', 'sigmoid',
'hard_sigmoid', 'linear']
param_grid = dict(activation=params)
# params = ['uniform', 'lecun_uniform', 'normal', 'zero', 'glorot_normal', 'glorot_uniform', 'he_normal', 'he_uniform']
# param_grid = dict(init_mode=params)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, cv=5)
grid_result = grid.fit(data2, data2)

# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

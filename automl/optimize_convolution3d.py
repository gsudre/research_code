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


home = os.path.expanduser('~')
data = np.load(home + '/data/tmp/ad_223_3d.npz')['data']

data2 = data[:, :, :, :, np.newaxis]
data2 = data2 / np.max(data2)

batch_size = 5
epochs = 40
inChannel = 1
x, y, z = data.shape[1:]
input_img = Input(shape = (x, y, z, inChannel))

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)

init_mode = 'lecun_uniform'

#encoder
x = Conv3D(32, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(input_img)
x = MaxPooling3D(pool_size=(2, 2, 2))(x) 
x = Conv3D(16, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(x)
x = MaxPooling3D(pool_size=(2, 2, 2))(x) 
x = Conv3D(8, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(x)
x = MaxPooling3D(pool_size=(2, 2, 2))(x) 
x = Conv3D(4, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(x)
encoded = MaxPooling3D(pool_size=(7, 7, 3))(x)

#decoder
x = Conv3D(4, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(encoded)
x = UpSampling3D((7,7,3))(x)
x = Conv3D(8, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(x)
x = UpSampling3D((2,2,2))(x)
x = Conv3D(16, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(x) 
x = UpSampling3D((2,2,2))(x)
x = Conv3D(32, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(x)
x = UpSampling3D((2,2,2))(x)
decoded = Conv3D(1, (3, 3, 3), activation='relu', kernel_initializer=init_mode, padding='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(loss='mse', optimizer = 'adam')

autoencoder.summary()

autoencoder_train = autoencoder.fit(data2, data2, batch_size=batch_size,
                                    epochs=epochs, verbose=1,
                                    validation_split=.1)

# save the model so we don't lose all this work in case of accidents
autoencoder.save(home + "/tmp/model_3dconv.h5py")

# loss = autoencoder_train.history['loss']
# val_loss = autoencoder_train.history['val_loss']
# epochs = range(epochs)
# plt.figure()
# plt.plot(epochs, loss, 'bo', label='Training loss')
# plt.plot(epochs, val_loss, 'b', label='Validation loss')
# plt.title('Training and validation loss')
# plt.legend()
# plt.show()

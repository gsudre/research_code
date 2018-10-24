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
epochs = 20
inChannel = 1
x, y, z = data.shape[1:]
input_img = Input(shape = (x, y, z, inChannel))

def autoencoder(input_img):
    #encoder
    conv1 = Conv3D(32, (3, 3, 3), activation='relu', padding='same')(input_img)
    pool1 = MaxPooling3D(pool_size=(2, 2, 2))(conv1) 
    conv2 = Conv3D(64, (3, 3, 3), activation='relu', padding='same')(pool1)
    pool2 = MaxPooling3D(pool_size=(2, 2, 2))(conv2) 
    conv3 = Conv3D(128, (3, 3, 3), activation='relu', padding='same')(pool2)

    #decoder
    conv4 = Conv3D(128, (3, 3, 3), activation='relu', padding='same')(conv3)
    up1 = UpSampling3D((2,2,2))(conv4)
    conv5 = Conv3D(64, (3, 3, 3), activation='relu', padding='same')(up1) 
    up2 = UpSampling3D((2,2,2))(conv5)
    decoded = Conv3D(1, (3, 3, 3), activation='sigmoid', padding='same')(up2)
    return decoded


autoencoder = Model(input_img, autoencoder(input_img))
autoencoder.compile(loss='mean_squared_error', optimizer = RMSprop())

autoencoder.summary()

autoencoder_train = autoencoder.fit(data2, data2, batch_size=batch_size,
                                    epochs=epochs, verbose=1,
                                    validation_split=.1)

# save the model so we don't lose all this work in case of accidents
autoencoder.save(home + "/tmp/model_3dconv.h5py")

loss = autoencoder_train.history['loss']
val_loss = autoencoder_train.history['val_loss']
epochs = range(epochs)
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

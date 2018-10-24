# Use scikit-learn to grid search the number of neurons and other parameters
import numpy
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout, Input
from keras.wrappers.scikit_learn import KerasRegressor
from keras.constraints import maxnorm
from keras import regularizers, Model
import os


# Function to create model, required for KerasClassifier
def create_model(neurons=1):
	# # create model
	# model = Sequential()
	# model.add(Dense(neurons, input_dim=12106, kernel_initializer='uniform',
	# 				activation='tanh', kernel_constraint=maxnorm(4)))
	# model.add(Dropout(0.2))
	# model.add(Dense(12106, kernel_initializer='uniform', activation='tanh'))
	# # Compile model
	# model.compile(loss='mean_squared_error', optimizer='adadelta')

	input_dim3 = 12106
	encoding_dim3 = neurons
	input_img3 = Input(shape=(input_dim3,))
	encoded3 = Dense(encoding_dim3, activation='sigmoid', activity_regularizer=regularizers.l1(10e-5))(input_img3)
	decoded3 = Dense(input_dim3, activation='sigmoid')(encoded3)
	autoencoder3 = Model(input_img3, decoded3)
	autoencoder3.compile(optimizer='adam', loss='mse')
# history3 = autoencoder3.fit(X_scaled, X_scaled,
#                 epochs=400,
#                 batch_size=16,
#                 shuffle=True,
#                 validation_split=0.1,
#                 verbose = 0)
	return autoencoder3
# fix random seed for reproducibility
seed = 7
numpy.random.seed(seed)
# load dataset
home = os.path.expanduser('~')
dataset = numpy.loadtxt(home + "/tmp/tmp.csv", delimiter=",", skiprows=1)
scaler = MinMaxScaler()
scaler.fit(dataset)
X_scaled = scaler.transform(dataset)

# create model
# model = KerasRegressor(build_fn=create_model, epochs=400, batch_size=16, verbose=0, shuffle=True, validation_split=.1)
# define the grid search parameters
# neurons = [1, 5, 10, 15, 20, 25, 30]
# param_grid = dict(neurons=neurons)
# grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=2)
# grid_result = grid.fit(X_scaled, X_scaled)


# # summarize results
# print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
# means = grid_result.cv_results_['mean_test_score']
# stds = grid_result.cv_results_['std_test_score']
# params = grid_result.cv_results_['params']
# for mean, stdev, param in zip(means, stds, params):
#     print("%f (%f) with: %r" % (mean, stdev, param))

autoencoder = create_model(neurons=30)
autoencoder.summary()

batch_size = 5
epochs = 50

autoencoder_train = autoencoder.fit(X_scaled, X_scaled, batch_size=batch_size,
                                    epochs=epochs, verbose=1,
                                    validation_split=.1)

# save the model so we don't lose all this work in case of accidents
autoencoder.save(home + "/tmp/model_autoencoder.h5py")

loss = autoencoder_train.history['loss']
val_loss = autoencoder_train.history['val_loss']
epochs = range(epochs)
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

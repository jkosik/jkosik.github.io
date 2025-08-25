import tensorflow as tf
from tensorflow import keras
import numpy as np

# Define the model
layer1 = keras.layers.Dense(units=2, input_shape=[1]) # input_shape is defined only for the first layer
layer2 = keras.layers.Dense(units=1) # automatically gets inputs from the previous layer

model = keras.Sequential([layer1, layer2]) # 2 layers. 2 neurons in L1, 1 neuron in L2

# Compile the model
model.compile(optimizer='sgd', loss='mean_squared_error') # function to measure the loss

# Training data (y=2x-1)
xs = np.array([-1.0, 0.0, 1.0, 2.0, 3.0, 4.0], dtype=float) # input
ys = np.array([-3.0, -1.0, 1.0, 3.0, 5.0, 7.0], dtype=float) # ground truth output


# Train the model
model.fit(xs, ys, epochs=50) # make a guess, measure the loss, optimise and repeat epoch-times

# Make a prediction
print(model.predict(np.array([10.0]))) # try to predict the output of 10.0

# Print weights
print(layer1.get_weights())
print(layer2.get_weights())
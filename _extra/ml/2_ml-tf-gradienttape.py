# Guessing and loss calculation based on Tensorflow and GradientTape

import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

# Define our initial guess
INITIAL_W = 10.0
INITIAL_B = 10.0

# Define our simple regression model
class Model(object):
    def __init__(self):
        # Initialize the weights
        self.w = tf.Variable(INITIAL_W)
        self.b = tf.Variable(INITIAL_B)

    def __call__(self, x):
        return self.w * x + self.b

# Define our loss function
def loss(predicted_y, target_y):
    return tf.reduce_mean(tf.square(predicted_y - target_y))


# Define our training procedure
def train(model, inputs, outputs, learning_rate):
    with tf.GradientTape() as t:
        # loss function
        current_loss = loss(model(inputs), outputs)

        # Here is where you differentiate loss function w.r.t model parameters
        dw, db = t.gradient(current_loss, [model.w, model.b])  # dloss/dw, dloss/db

        # And here is where you update the model parameters based on the learning rate chosen
        model.w.assign_sub(learning_rate * dw)  # model.w = model.w - learning_rate*dw
        model.b.assign_sub(learning_rate * db)  # model.b = model.b - learning_rate*db
    return current_loss


# Define our input data and learning rate
xs = [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0]
ys = [-3.0, -1.0, 1.0, 3.0, 5.0, 7.0]
LEARNING_RATE = 0.14   #0.09

# Instantiate our model
model = Model()

# Collect the history of w-values and b-values to plot later
list_w, list_b = [], []
epochs = 50
losses = []

for epoch in range(epochs):
    list_w.append(model.w.numpy())
    list_b.append(model.b.numpy())
    current_loss = train(model, xs, ys, learning_rate=LEARNING_RATE)
    losses.append(current_loss)
    print('Epoch %2d: w=%.2f b=%.2f, loss=%.2f' %
          (epoch, list_w[-1], list_b[-1], current_loss))

import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np

# Load training data
data = tf.keras.datasets.mnist
(training_images, training_labels), (val_images, val_labels) = data.load_data() # split data to training and validation

print("Shape of training images:", training_images.shape)
print("Shape of training labels:", training_labels.shape)
print("Shape of validation images:", val_images.shape)
print("Shape of validation labels:", val_labels.shape)

# Output is 60k samples, 28x28px each. Eac label is a 1-dimensional scalar value.
# Shape of training images: (60000, 28, 28)
# Shape of training labels: (60000,)
# Shape of testing images : (10000, 28, 28)
# Shape of testing labels : (10000,)

print("Training data:",training_images[0]) # Produces 28x28 grid in a form of nested array - array of 28 subarrays, each containing 28 values. Sample line: [  0 ... 55 172 ... ]
print("Label:",training_labels[0]) # produces "5"

# Each of 28 nested array contains 28 values represent color from white to black (0-255).
# Normalise the data. Instead of 0-255, convert values to 0-1.
training_images = training_images / 255.0
val_images = val_images / 255.0

print("Training normalised:",training_images[0]) # sample line: [0 ... 0.21568627 0.6745098 ... ]

# Plot the first item from the training set using color map - transform 0-1 to grayscale.
# plt.imshow(training_images[0], cmap='gray')
# plt.show()

# Define the model
# Our model will input not one X but 28x28 (784) X-es. As if we flatten all pixels to a continuous line of values.
# 2 layers: 1st: 20 neurons, 2nd: 10 neurons to reflect number of labels/classes (0-9, i.e. 10 possibilities).

layer1 = tf.keras.layers.Dense(20, activation=tf.nn.relu)
layer2 = tf.keras.layers.Dense(10, activation=tf.nn.softmax)

model = tf.keras.models.Sequential([tf.keras.layers.Input(shape=(28,28)),
                                    tf.keras.layers.Flatten(),
                                    layer1,
                                    layer2])

OPT = 'adam'
LOSS = 'sparse_categorical_crossentropy' # suitable for multiclass classification tasks

model.compile(optimizer= OPT,
              loss= LOSS,
              metrics=['accuracy'])

# Train the model
# Images are inputs (like X). Labels are outputs (like Y). We count loss, but also accuracy.
model.fit(training_images, training_labels, epochs=20, validation_data=(val_images, val_labels))

# Validate the model
model.evaluate(val_images, val_labels) # Run validation again on any further validation data sets

# Validate single item form the validation set (number 7). 
classifications = model.predict(val_images)
print(classifications[0]) # See the highest probability set for the 7th index
print("Predicted class: ", np.argmax(classifications[0]))
print("The actual class: ", val_labels[0])

# Plot the first item from the validation set using color map - transform 0-1 to grayscale.
# plt.imshow(val_images[0], cmap='gray')
# plt.show()

# # Print weights
# print(layer1.get_weights())

# Total weights in the layer
print(layer1.get_weights()[0].size)
# Total bias in the layer
print(layer1.get_weights()[1].size)
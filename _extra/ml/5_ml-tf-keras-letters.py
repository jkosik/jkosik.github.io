import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import os

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



# Save the model in Keras format
print("Saving model in Keras format")
export_dir = 'saved_models/model-letters.keras'
model.save(export_dir)

# Convert the model to TFLite format
print("Converting model to TFLite format")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
# converter.optimizations = [tf.lite.Optimize.DEFAULT] # optional optimizations
tflite_model = converter.convert()

# Save the TFLite model
tflite_path = 'saved_models/model-letters.tflite'
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)
print(f"TFLite model saved to: {tflite_path}")

# Print model sizes for comparison
keras_size = os.path.getsize(export_dir)
tflite_size = os.path.getsize(tflite_path)
print(f"Keras model size: {keras_size:,} bytes")
print(f"TFLite model size: {tflite_size:,} bytes")
print(f"Size reduction: {((keras_size - tflite_size) / keras_size * 100):.1f}%")

# Compare accuracy between Keras and TFLite models
print("\n=== Model Accuracy Comparison ===")

# Test Keras model accuracy
keras_predictions = model.predict(val_images)
keras_predicted_classes = np.argmax(keras_predictions, axis=1)
keras_accuracy = np.mean(keras_predicted_classes == val_labels)
print(f"Keras model accuracy: {keras_accuracy:.4f} ({keras_accuracy*100:.2f}%)")

# Test TFLite model accuracy
interpreter = tf.lite.Interpreter(model_path=tflite_path)
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"TFLite input shape: {input_details[0]['shape']}")
print(f"TFLite output shape: {output_details[0]['shape']}")

# Run predictions on TFLite model
tflite_predictions = []
for i in range(len(val_images)):
    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], val_images[i:i+1].astype(np.float32))

    # Run inference
    interpreter.invoke()

    # Get output
    output_data = interpreter.get_tensor(output_details[0]['index'])
    tflite_predictions.append(output_data[0])

tflite_predictions = np.array(tflite_predictions)
tflite_predicted_classes = np.argmax(tflite_predictions, axis=1)
tflite_accuracy = np.mean(tflite_predicted_classes == val_labels)
print(f"TFLite model accuracy: {tflite_accuracy:.4f} ({tflite_accuracy*100:.2f}%)")

# Calculate accuracy difference
accuracy_diff = abs(keras_accuracy - tflite_accuracy)
print(f"Accuracy difference: {accuracy_diff:.4f} ({accuracy_diff*100:.2f} percentage points)")

# Check if accuracies match closely (within 0.1% is typically acceptable)
if accuracy_diff < 0.001:
    print("✅ Excellent: Accuracies are nearly identical!")
elif accuracy_diff < 0.01:
    print("✅ Good: Accuracies are very close (< 1% difference)")
elif accuracy_diff < 0.05:
    print("⚠️  Acceptable: Small accuracy difference (< 5%)")
else:
    print("❌ Warning: Significant accuracy difference (> 5%)")

# Test on a few individual samples for detailed comparison
print(f"\n=== Sample Predictions Comparison (first 5 validation samples) ===")
for i in range(5):
    keras_pred_class = keras_predicted_classes[i]
    tflite_pred_class = tflite_predicted_classes[i]
    actual_class = val_labels[i]

    match_indicator = "✅" if keras_pred_class == tflite_pred_class else "❌"
    correct_indicator = "✅" if actual_class == keras_pred_class == tflite_pred_class else "❌"

    print(f"Sample {i}: Actual={actual_class}, Keras={keras_pred_class}, TFLite={tflite_pred_class} {match_indicator} {correct_indicator}")


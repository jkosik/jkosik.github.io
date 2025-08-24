model otimis:
- pruning
- quantization
- knowledge distillation

Tensorflow model => tflite converter => `.tflite` file(model)

Artifical Intell => ML => Deep


- Guess has multiple parameters (gradient) and we observe how change of each of them affect the result. And we move them certain diection or keep untouched.
If change lowers the loss, we are going right direction when tuning the guess. 



tinyml-manual.py

to use Tensorflow and train, we need: ML model, Loss function, Training procedure

tinyml.py

Learning rate - if step of gradient descent too big, we overshoot min loss. If too small, learning takes ages to hit min loss.


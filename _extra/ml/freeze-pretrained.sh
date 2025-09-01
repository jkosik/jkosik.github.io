#!/bin/bash

# This script freezes a pretrained model and saves it in the saved_models folder.
# To run own pre-training, see https://colab.research.google.com/github/tensorflow/tflite-micro/blob/main/tensorflow/lite/micro/examples/micro_speech/train/train_micro_speech_model.ipynb

rm -rf ./tensorflow
rm -rf ./models
git clone https://github.com/tensorflow/tensorflow.git
mkdir ./models

cd ./models
curl -O "https://storage.googleapis.com/download.tensorflow.org/models/tflite/speech_micro_train_2020_05_10.tgz"
tar xzf speech_micro_train_2020_05_10.tgz

# Constants which are shared during training and inference
PREPROCESS='micro'
WINDOW_STRIDE=20
MODEL_ARCHITECTURE='tiny_conv' # Other options include: single_fc, conv,
                      # low_latency_conv, low_latency_svdf, tiny_embedding_conv

WANTED_WORDS="yes,no"
TOTAL_STEPS="12000"
TRAIN_DIR='train/' # for training checkpoints and other files.
SAVED_MODEL=model_keyword_spotting/

# Freeze the model - can not be re-trained afterwards
rm -rf $SAVED_MODEL
python ../tensorflow/tensorflow/examples/speech_commands/freeze.py \
--wanted_words=$WANTED_WORDS \
--window_stride_ms=$WINDOW_STRIDE \
--preprocess=$PREPROCESS \
--model_architecture=$MODEL_ARCHITECTURE \
--start_checkpoint=$TRAIN_DIR$MODEL_ARCHITECTURE'.ckpt-'$TOTAL_STEPS \
--save_format=saved_model \
--output_file=$SAVED_MODEL

# Outputs .pb model which can be used by Tensorflow directly. For Tensorflow Lite, conversion is needed.
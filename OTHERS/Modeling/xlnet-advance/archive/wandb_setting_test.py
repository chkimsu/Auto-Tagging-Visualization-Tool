# wandb initialization
# Import callback function
import wandb
from wandb.keras import WandbCallback
import os
import numpy as np
from matplotlib import pyplot as plt
import tensorflow as tf
from tensorflow.keras import models, layers, optimizers, losses, utils, datasets

wandb.init(project="atvt-board")

print("Packge Loaded!")

wandb.log({"generated_samples":
           [wandb.Object3D(open("../data/Building,.obj"))]})

# Data Loading
(train_x, train_y), (test_x, test_y) = datasets.mnist.load_data()
train_x, test_x = np.reshape(train_x/255., [-1, 784]), np.reshape(test_x/255., [-1, 784])

print("Train Data's Shape : ", train_x.shape, train_y.shape)
print("Test Data's Shape : ", test_x.shape, test_y.shape)

# Network Building
## Using Sequential
mlp = models.Sequential()
mlp.add(layers.Dense(256, activation='relu', input_shape=(784,)))
mlp.add(layers.Dense(128, activation='relu'))
mlp.add(layers.Dense(10, activation='softmax'))

print("Network Built!")

mlp.compile(optimizer=optimizers.Adam(), loss=losses.sparse_categorical_crossentropy, metrics=['accuracy'])

history = mlp.fit(train_x, train_y, epochs=10, batch_size=8,
                                    validation_data=(test_x, test_y),
                                    callbacks=[WandbCallback()]) # callbacks 에 Wandbcallback 추가

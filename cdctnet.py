# -*- coding: utf-8 -*-
"""CDCTNet.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16JSA0E8_aBWx7Ifd0xU71qjcQ_JiBL2h
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# 1. Convolutional Block for Encoder
def conv_block(x, filters):
    x = layers.Conv2D(filters, (3, 3), padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    return x

# 2. U-Net Encoder with Convolutional Feature Extraction
def encoder(inputs):
    skips = []
    x = inputs
    for filters in [32, 64, 128, 256]:
        x = conv_block(x, filters)
        skips.append(x)
        x = layers.MaxPooling2D((2, 2))(x)
    return x, skips

# 3. Transformer Module with CPE, LSA, GSA
def transformer_block(x):
    # Conditional Positional Encoding (CPE)
    cpe = layers.Conv2D(x.shape[-1], (3, 3), padding="same", groups=x.shape[-1])(x)

    # Locally Grouped Self-Attention (LSA)
    local_attention = layers.Conv2D(x.shape[-1], (3, 3), padding="same", groups=x.shape[-1])(cpe)

    # Global Sub-Sampled Attention (GSA)
    global_attention = layers.Conv2D(x.shape[-1], (1, 1))(x)

    # Fusion of Local & Global Attention
    fused = layers.Add()([local_attention, global_attention])
    return fused

# 4. Attention Gate (AG) for Decoder
def attention_gate(x, g):
    x = layers.Conv2D(1, (1, 1), activation="sigmoid")(x)
    g = layers.Conv2D(1, (1, 1), activation="sigmoid")(g)
    return layers.Multiply()([x, g])

# 5. Gated Convolution Decoder
def decoder(x, skips):
    for i, filters in enumerate([256, 128, 64, 32]):
        x = layers.Conv2DTranspose(filters, (2, 2), strides=(2, 2), padding="same")(x)
        x = attention_gate(x, skips[-(i + 1)])
        x = layers.Concatenate()([x, skips[-(i + 1)]])
        x = conv_block(x, filters)
    return x

# 6. Complete Model
def build_model(input_shape=(256, 256, 3)):
    inputs = keras.Input(shape=input_shape)

    # Encoder
    x, skips = encoder(inputs)

    # Transformer Module
    x = transformer_block(x)

    # Decoder
    x = decoder(x, skips)

    # Output Layer (Segmentation Map)
    outputs = layers.Conv2D(1, (1, 1), activation="sigmoid")(x)

    return keras.Model(inputs, outputs, name="Landslide_Segmentation")

# Compile Model
model = build_model()
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
model.summary()
"""
model_utils.py
--------------
Yeh file teammate (Vishal) ke original predict.py se EXACT match karti hai -
model load karna, prediction karna, aur Grad-CAM images (arrays) banana -
sab EK function me, taaki koi mismatch na ho.

Model: models/best_model.keras (DenseNet121)
Last conv layer: conv5_block16_concat
Threshold: score > 0.7 => "Pneumonia"

Use kaise karein:
    from model_utils import predict_and_explain
    result = predict_and_explain("uploads/xray_123.png")
    # result["score"], result["label"], result["original_image"] (array),
    # result["overlay_image"] (array)
"""

import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image

# ---- Model ka path ----
# NOTE: Agar aap seedha teammate ke repo root me kaam kar rahe ho, to model
# already "models/best_model.keras" pe hai (backend folder ke bahar, ek level
# upar). Isliye path "../models/best_model.keras" rakha hai.
# Agar aap model ko backend/model/ folder ke andar copy kar rahe ho, to
# neeche wali line uncomment/change kar dena.
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best_model.keras")
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "best_model.keras")

LAST_CONV_LAYER = "conv5_block16_concat"

# Model aur grad_model ko sirf ek baar load karna hai (startup pe)
_model = None
_grad_model = None


def _load():
    """Model aur Grad-CAM graph ko load karta hai (sirf ek baar)."""
    global _model, _grad_model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file nahi mili: {MODEL_PATH}\n"
                f"best_model.keras ko sahi path pe rakho."
            )
        print("[model_utils.py] Model load ho raha hai...")
        _model = load_model(MODEL_PATH)
        _grad_model = tf.keras.models.Model(
            inputs=_model.input,
            outputs=[_model.get_layer(LAST_CONV_LAYER).output, _model.output]
        )
        print("[model_utils.py] Model load ho gaya!")
    return _model, _grad_model


def predict_and_explain(img_path: str):
    """
    Ek X-ray image (file path) leta hai aur prediction + Grad-CAM dono deta hai.

    Parameter:
        img_path: uploaded X-ray image ka file path (jo already disk pe save ho chuki hai)

    Return: dictionary
        {
            "score": 0.85,              # raw sigmoid score (0-1)
            "label": "Pneumonia",       # ya "Normal" (threshold: score > 0.7)
            "confidence": 85.0,         # percentage (frontend ke liye)
            "original_image": <numpy array, BGR, 224x224>,
            "overlay_image": <numpy array, BGR, 224x224>   # Grad-CAM heatmap overlay
        }

    NOTE: "original_image" aur "overlay_image" numpy arrays hain (OpenCV/BGR format).
    Inko PNG file me save karne ke liye seedha cv2.imwrite() use karo - koi extra
    conversion (jaise base64) ki zarurat nahi hai.
    """
    model, grad_model = _load()

    # ---- 1. Preprocess ----
    img = keras_image.load_img(img_path, target_size=(224, 224))
    img_array = keras_image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # ---- 2. Grad-CAM & Prediction ----
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, 0]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]

    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-8)
    heatmap = heatmap.numpy()

    score = float(predictions.numpy()[0][0])
    label = "Pneumonia" if score > 0.7 else "Normal"
    confidence = score if label == "Pneumonia" else (1 - score)
    confidence_percent = round(confidence * 100, 2)

    # ---- 3. Original aur Overlay images banao (dono numpy arrays, BGR format) ----
    original_img = cv2.imread(img_path)
    original_img = cv2.resize(original_img, (224, 224))

    heatmap_resized = cv2.resize(heatmap, (224, 224))
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)

    overlay_img = cv2.addWeighted(original_img, 0.6, heatmap_colored, 0.4, 0)

    return {
        "score": score,
        "label": label,
        "confidence": confidence_percent,
        "original_image": original_img,
        "overlay_image": overlay_img
    }

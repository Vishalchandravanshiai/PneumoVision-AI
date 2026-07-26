import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

MODEL_PATH = "models/best_model.keras"
LAST_CONV_LAYER = "conv5_block16_concat"

# Load model and build Grad-CAM graph on startup
model = load_model(MODEL_PATH)
grad_model = tf.keras.models.Model(
    inputs=model.input,
    outputs=[model.get_layer(LAST_CONV_LAYER).output, model.output]
)

def predict_and_explain(img_path):
    # 1. Preprocess
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 2. Grad-CAM & Prediction
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

    # 3. Process Original and Overlay Images
    original_img = cv2.imread(img_path)
    original_img = cv2.resize(original_img, (224, 224))

    heatmap_resized = cv2.resize(heatmap, (224, 224))
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)

    overlay_img = cv2.addWeighted(original_img, 0.6, heatmap_colored, 0.4, 0)

    return {
        "score": score,
        "label": label,
        "original_image": original_img,
        "overlay_image": overlay_img
    }
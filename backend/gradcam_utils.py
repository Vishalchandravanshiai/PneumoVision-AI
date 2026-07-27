"""
gradcam_utils.py
----------------
The actual Grad-CAM calculation now lives in model_utils.py (to exactly
match the teammate's predict.py). This file just provides helper functions -
saving a numpy array (image) to a PNG file.

Usage:
    from gradcam_utils import save_image_array
    save_image_array(result["overlay_image"], "gradcam_outputs/xyz.png")
"""

import cv2
import base64


def save_image_array(img_array, save_path: str):
    """
    Saves a numpy array (OpenCV/BGR format) as a PNG file.
    Use this to save the "original_image" or "overlay_image" arrays
    returned by model_utils.predict_and_explain().

    Parameter:
        img_array: numpy array (e.g. result["overlay_image"])
        save_path: where to save it (e.g. "gradcam_outputs/xyz.png")

    Return: save_path
    """
    cv2.imwrite(save_path, img_array)
    return save_path


def image_array_to_base64(img_array) -> str:
    """
    OPTIONAL helper: use this if you ever need to send an image directly in
    a JSON response (as a base64 string) without saving it to a file.
    Not needed in the normal flow - we save a PNG file and send its URL.

    Return: base64 encoded string (without saving to a file)
    """
    success, buffer = cv2.imencode(".png", img_array)
    if not success:
        raise ValueError("Could not encode the image.")
    base64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/png;base64,{base64_str}"
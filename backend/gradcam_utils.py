"""
gradcam_utils.py
----------------
Grad-CAM ka actual calculation ab model_utils.py me hai (teammate ke
predict.py se exact match karne ke liye). Yeh file sirf helper functions
deti hai - numpy array (image) ko PNG file me save karna.

Use kaise karein:
    from gradcam_utils import save_image_array
    save_image_array(result["overlay_image"], "gradcam_outputs/xyz.png")
"""

import cv2
import base64


def save_image_array(img_array, save_path: str):
    """
    Numpy array (OpenCV/BGR format) ko PNG file me save karta hai.
    model_utils.predict_and_explain() se mile "original_image" ya
    "overlay_image" arrays isi function se save karo.

    Parameter:
        img_array: numpy array (jaise result["overlay_image"])
        save_path: kaha save karna hai (jaise "gradcam_outputs/xyz.png")

    Return: save_path
    """
    cv2.imwrite(save_path, img_array)
    return save_path


def image_array_to_base64(img_array) -> str:
    """
    OPTIONAL helper: agar kabhi file save kiye bina seedha JSON response
    me image bhejni ho (base64 string ke roop me), to ye function use karo.
    Normal flow me iski zarurat nahi - hum PNG file save karke URL bhejte hain.

    Return: base64 encoded string (bina file save kiye)
    """
    success, buffer = cv2.imencode(".png", img_array)
    if not success:
        raise ValueError("Image ko encode nahi kar paya.")
    base64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/png;base64,{base64_str}"

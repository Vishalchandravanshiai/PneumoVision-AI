"""
main.py
-------
Yeh FastAPI backend ka main entry point hai.
Ye REST API endpoints deta hai jo HTML/JS frontend fetch() se call karega.

Chalane ka command:
    uvicorn main:app --reload

Phir API docs yaha dekh sakte ho (auto-generated, testing ke liye bahut useful):
    http://localhost:8000/docs
"""

import os
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image

from database import init_db, add_scan, get_all_scans, get_scan_by_id, delete_scan
from model_utils import predict_and_explain
from gradcam_utils import save_image_array
from report_utils import generate_report

# ---- Folders jaha files save hongi ----
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
GRADCAM_DIR = os.path.join(BASE_DIR, "gradcam_outputs")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

for folder in [UPLOAD_DIR, GRADCAM_DIR, REPORT_DIR]:
    os.makedirs(folder, exist_ok=True)

# ---- Database ready karo (server start hote hi) ----
init_db()

app = FastAPI(title="PneumoVision AI - Backend API")

# ---- CORS: HTML/JS frontend ko allow karne ke liye ----
# Abhi ke liye "*" (sabko allow) rakha hai taaki demo/hackathon me dikkat na ho.
# Production me isko apne frontend ke exact URL se replace kar dena.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Static files serve karna (images ko browser me directly dikhane ke liye) ----
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/static/gradcam", StaticFiles(directory=GRADCAM_DIR), name="gradcam")


# ============================================================
# 1. Health check - server chal raha hai ya nahi, test karne ke liye
# ============================================================
@app.get("/")
def health_check():
    return {"status": "PneumoVision AI backend is running!"}


# ============================================================
# 2. MAIN ENDPOINT - X-ray upload karke prediction lena
# ============================================================
@app.post("/predict")
async def predict_endpoint(
    file: UploadFile = File(...),
    patient_name: str = Form(default="")
):
    """
    Frontend yaha X-ray image bhejega (multipart/form-data).

    Request (frontend se):
        file: image file
        patient_name: (optional) text

    Response (JSON):
        {
            "scan_id": 5,
            "prediction": "Pneumonia",
            "confidence": 92.5,
            "original_image_url": "/static/uploads/xray_....png",
            "gradcam_url": "/static/gradcam/gradcam_....png",
            "report_download_url": "/download-report/5"
        }
    """
    # ---- 1. File type check ----
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Sirf image files allowed hain (jpg/png).")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")

    # ---- 2. Image save karo (disk pe - model isi path se padhega) ----
    image = Image.open(file.file)
    image_filename = f"xray_{timestamp}.png"
    image_path = os.path.join(UPLOAD_DIR, image_filename)
    image.save(image_path)

    # ---- 3. Model se prediction + Grad-CAM dono ek saath lo ----
    try:
        result = predict_and_explain(image_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ---- 4. Grad-CAM overlay image (numpy array) ko PNG save karo ----
    gradcam_filename = f"gradcam_{timestamp}.png"
    gradcam_path = os.path.join(GRADCAM_DIR, gradcam_filename)
    save_image_array(result["overlay_image"], gradcam_path)

    # ---- 5. PDF report banao ----
    report_filename = f"report_{timestamp}.pdf"
    report_path = os.path.join(REPORT_DIR, report_filename)
    generate_report(
        patient_name=patient_name,
        prediction=result["label"],
        confidence=result["confidence"],
        original_image_path=image_path,
        gradcam_image_path=gradcam_path,
        save_path=report_path
    )

    # ---- 6. Database me save karo ----
    scan_id = add_scan(
        patient_name=patient_name,
        image_path=image_path,
        prediction=result["label"],
        confidence=result["confidence"],
        gradcam_path=gradcam_path,
        report_path=report_path
    )

    # ---- 7. Frontend ko response bhejo ----
    return {
        "scan_id": scan_id,
        "prediction": result["label"],
        "confidence": result["confidence"],
        "original_image_url": f"/static/uploads/{image_filename}",
        "gradcam_url": f"/static/gradcam/{gradcam_filename}",
        "report_download_url": f"/download-report/{scan_id}"
    }


# ============================================================
# 3. History - saare purane scans ki list
# ============================================================
@app.get("/history")
def history_endpoint():
    """
    Response: list of scans, sabse naya sabse upar.
    """
    scans = get_all_scans()

    # File paths ko URLs me convert kar rahe hain taaki frontend directly use kar sake
    for scan in scans:
        scan["original_image_url"] = f"/static/uploads/{os.path.basename(scan['image_path'])}"
        if scan["gradcam_path"]:
            scan["gradcam_url"] = f"/static/gradcam/{os.path.basename(scan['gradcam_path'])}"
        scan["report_download_url"] = f"/download-report/{scan['id']}"

    return {"scans": scans}


# ============================================================
# 4. Ek specific scan ki details
# ============================================================
@app.get("/scan/{scan_id}")
def get_scan_endpoint(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan nahi mila.")

    scan["original_image_url"] = f"/static/uploads/{os.path.basename(scan['image_path'])}"
    if scan["gradcam_path"]:
        scan["gradcam_url"] = f"/static/gradcam/{os.path.basename(scan['gradcam_path'])}"
    scan["report_download_url"] = f"/download-report/{scan['id']}"

    return scan


# ============================================================
# 5. PDF Report download karna
# ============================================================
@app.get("/download-report/{scan_id}")
def download_report(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if not scan or not scan["report_path"] or not os.path.exists(scan["report_path"]):
        raise HTTPException(status_code=404, detail="Report nahi mili.")

    return FileResponse(
        path=scan["report_path"],
        filename=f"pneumovision_report_{scan_id}.pdf",
        media_type="application/pdf"
    )


# ============================================================
# 6. Scan delete karna (optional, agar zarurat pade)
# ============================================================
@app.delete("/scan/{scan_id}")
def delete_scan_endpoint(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan nahi mila.")
    delete_scan(scan_id)
    return {"message": f"Scan #{scan_id} delete ho gaya."}

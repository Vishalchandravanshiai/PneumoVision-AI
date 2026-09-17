"""
main.py
-------


Run command:
     python -muvicorn main:app --reload

Then you can view the API docs here (auto-generated, very useful for testing):
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

# ---- Folders where files will be saved ----
BASE_DIR = os.path.dirname(__file__)

# Frontend directory
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
GRADCAM_DIR = os.path.join(BASE_DIR, "gradcam_outputs")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

for folder in [UPLOAD_DIR, GRADCAM_DIR, REPORT_DIR]:
    os.makedirs(folder, exist_ok=True)

# ---- Prepare the database (runs once at server startup) ----
init_db()

app = FastAPI(title="PneumoVision AI - Backend API")

# ---- CORS: allow the HTML/JS frontend to call this API ----
# Currently set to "*" (allow all) to avoid issues during demo/hackathon.
# In production, replace this with your frontend's exact URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Serve static files (so images can be shown directly in the browser) ----
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/static/gradcam", StaticFiles(directory=GRADCAM_DIR), name="gradcam")


# ============================================================
# 1. Health check - to test whether the server is running
# ============================================================


# ============================================================
# 2. MAIN ENDPOINT - upload an X-ray and get a prediction
# ============================================================
@app.post("/predict")
async def predict_endpoint(
    file: UploadFile = File(...),
    patient_name: str = Form(default=""),
    patient_age: str = Form(default=""),
    patient_gender: str = Form(default=""),
    patient_id: str = Form(default=""),
    doctor_name: str = Form(default=""),
    hospital_name: str = Form(default="")
):
    """
    The frontend sends the X-ray image here (multipart/form-data).

    Request (from frontend):
        file: image file
        patient_name, patient_age, patient_gender, patient_id,
        doctor_name, hospital_name: (all optional) text fields

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
    # ---- 1. Check file type ----
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed (jpg/png).")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")

    # ---- 2. Save the image to disk (the model will read it from this path) ----
    image = Image.open(file.file)
    image_filename = f"xray_{timestamp}.png"
    image_path = os.path.join(UPLOAD_DIR, image_filename)
    image.save(image_path)

    # ---- 3. Get prediction + Grad-CAM from the model in one call ----
    try:
        result = predict_and_explain(image_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ---- 4. Save the Grad-CAM overlay image (numpy array) as a PNG ----
    gradcam_filename = f"gradcam_{timestamp}.png"
    gradcam_path = os.path.join(GRADCAM_DIR, gradcam_filename)
    save_image_array(result["overlay_image"], gradcam_path)

    # ---- 5. Generate the PDF report ----
    report_filename = f"report_{timestamp}.pdf"
    report_path = os.path.join(REPORT_DIR, report_filename)
    generate_report(
        patient_name=patient_name,
        patient_age=patient_age,
        patient_gender=patient_gender,
        patient_id=patient_id,
        doctor_name=doctor_name,
        hospital_name=hospital_name,
        prediction=result["label"],
        confidence=result["confidence"],
        original_image_path=image_path,
        gradcam_image_path=gradcam_path,
        save_path=report_path
    )

    # ---- 6. Save the record in the database ----
    scan_id = add_scan(
        patient_name=patient_name,
        image_path=image_path,
        prediction=result["label"],
        confidence=result["confidence"],
        gradcam_path=gradcam_path,
        report_path=report_path
    )

    # ---- 7. Send the response back to the frontend ----
    return {
        "scan_id": scan_id,
        "prediction": result["label"],
        "confidence": result["confidence"],
        "original_image_url": f"/static/uploads/{image_filename}",
        "gradcam_url": f"/static/gradcam/{gradcam_filename}",
        "report_download_url": f"/download-report/{scan_id}"
    }


# ============================================================
# 3. History - list of all past scans
# ============================================================
@app.get("/history")
def history_endpoint():
    """
    Response: list of scans, newest first.
    """
    scans = get_all_scans()

    # Convert file paths into URLs so the frontend can use them directly
    for scan in scans:
        scan["original_image_url"] = f"/static/uploads/{os.path.basename(scan['image_path'])}"
        if scan["gradcam_path"]:
            scan["gradcam_url"] = f"/static/gradcam/{os.path.basename(scan['gradcam_path'])}"
        scan["report_download_url"] = f"/download-report/{scan['id']}"

    return {"scans": scans}


# ============================================================
# 4. Details of one specific scan
# ============================================================
@app.get("/scan/{scan_id}")
def get_scan_endpoint(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    scan["original_image_url"] = f"/static/uploads/{os.path.basename(scan['image_path'])}"
    if scan["gradcam_path"]:
        scan["gradcam_url"] = f"/static/gradcam/{os.path.basename(scan['gradcam_path'])}"
    scan["report_download_url"] = f"/download-report/{scan['id']}"

    return scan


# ============================================================
# 5. Download the PDF report
# ============================================================
@app.get("/download-report/{scan_id}")
def download_report(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if not scan or not scan["report_path"] or not os.path.exists(scan["report_path"]):
        raise HTTPException(status_code=404, detail="Report not found.")

    return FileResponse(
        path=scan["report_path"],
        filename=f"pneumovision_report_{scan_id}.pdf",
        media_type="application/pdf"
    )


# ============================================================
# 6. Delete a scan (optional, if needed)
# ============================================================
@app.delete("/scan/{scan_id}")
def delete_scan_endpoint(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    delete_scan(scan_id)
    return {"message": f"Scan #{scan_id} deleted."}

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
/*
 * dashboard.js
 * -------------
 * This file connects the entire PneumoVision AI frontend to the backend (FastAPI).
 *
 * IMPORTANT: The backend must be running at this URL (started via uvicorn main:app --reload):
 */
const API_BASE_URL = "http://127.0.0.1:8000";


/* ============================================================
   PART 1: upload.html - "Analyze X-ray" button logic
   ============================================================ */

// This function only runs on upload.html (where these elements exist)
function initUploadPage() {
    const analyzeBtn = document.getElementById("analyzeBtn");
    if (!analyzeBtn) return; // if this page doesn't have the button, do nothing

    analyzeBtn.addEventListener("click", async function () {
        const imageInput = document.getElementById("imageInput");
        const file = imageInput.files[0];

        if (!file) {
            alert("Please select an X-ray image first.");
            return;
        }

        // Get patient details from the form
        const patientName = document.getElementById("patientName").value || "N/A";
        const patientAge = document.getElementById("patientAge").value || "N/A";
        const patientGender = document.getElementById("patientGender").value || "N/A";
        const patientId = document.getElementById("patientId").value || "N/A";
        const doctorName = document.getElementById("doctorName").value || "N/A";
        const hospitalName = document.getElementById("hospitalName").value || "N/A";

        // Put the button into a "loading" state so the user knows something is happening
        const originalBtnText = analyzeBtn.innerHTML;
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

        try {
            // ---- Send request to backend ----
            const formData = new FormData();
            formData.append("file", file);
            formData.append("patient_name", patientName);
            formData.append("patient_age", patientAge);
            formData.append("patient_gender", patientGender);
            formData.append("patient_id", patientId);
            formData.append("doctor_name", doctorName);
            formData.append("hospital_name", hospitalName);

            const response = await fetch(`${API_BASE_URL}/predict`, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            // ---- Save the result in sessionStorage ----
            // (so prediction.html can read it as soon as it opens)
            const resultData = {
                prediction: data.prediction,
                confidence: data.confidence,
                scan_id: data.scan_id,
                original_image_url: API_BASE_URL + data.original_image_url,
                gradcam_url: API_BASE_URL + data.gradcam_url,
                report_download_url: API_BASE_URL + data.report_download_url,
                patient_name: patientName,
                patient_age: patientAge,
                patient_gender: patientGender,
                patient_id: patientId,
                doctor_name: doctorName,
                hospital_name: hospitalName
            };
            sessionStorage.setItem("pneumovision_result", JSON.stringify(resultData));

            // ---- Redirect to the prediction page ----
            window.location.href = "prediction.html";

        } catch (error) {
            console.error("Error:", error);
            alert(
                "Could not connect to the backend. Please check:\n" +
                "1. Is the backend running? (uvicorn main:app --reload)\n" +
                "2. Is the URL correct? (" + API_BASE_URL + ")\n\n" +
                "Error: " + error.message
            );
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = originalBtnText;
        }
    });
}


/* ============================================================
   PART 2: prediction.html - Display the real result
   ============================================================ */

function initPredictionPage() {
    // This element only exists on prediction.html
    const statusBadge = document.getElementById("statusBadge");
    if (!statusBadge) return; // if this page doesn't have it, do nothing

    const savedData = sessionStorage.getItem("pneumovision_result");

    if (!savedData) {
        // No result found (user navigated here directly without uploading)
        document.getElementById("predictionContent").innerHTML =
            '<div class="alert alert-warning">' +
            'No scan result found. Please upload an X-ray first.' +
            '<br><a href="upload.html" class="btn btn-primary mt-3">Upload X-ray</a>' +
            '</div>';
        return;
    }

    const result = JSON.parse(savedData);

    // ---- Images ----
    document.getElementById("originalXrayImg").src = result.original_image_url;
    document.getElementById("gradcamImg").src = result.gradcam_url;

    // ---- Prediction status ----
    const isPneumonia = result.prediction === "Pneumonia";
    statusBadge.textContent = isPneumonia ? "Pneumonia Detected" : "Normal";
    statusBadge.className = "badge fs-6 " + (isPneumonia ? "bg-danger" : "bg-success");

    // ---- Confidence ----
    document.getElementById("confidenceValue").textContent = result.confidence + "%";
    const progressBar = document.getElementById("confidenceBar");
    progressBar.style.width = result.confidence + "%";
    progressBar.className = "progress-bar " + (isPneumonia ? "bg-danger" : "bg-success");

    // ---- Patient info ----
    document.getElementById("patientNameDisplay").textContent = result.patient_name;
    document.getElementById("patientAgeDisplay").textContent = result.patient_age + " Years";
    document.getElementById("patientGenderDisplay").textContent = result.patient_gender;
    document.getElementById("patientIdDisplay").textContent = result.patient_id;
    document.getElementById("hospitalDisplay").textContent = result.hospital_name;
    document.getElementById("doctorDisplay").textContent = result.doctor_name;

    // ---- Download Report button ----
    const downloadBtn = document.getElementById("downloadReportBtn");
    if (downloadBtn) {
        downloadBtn.href = result.report_download_url;
    }
}


/* ============================================================
   PART 3: reports.html - Display real scan history
   ============================================================ */

async function initReportsPage() {
    const tableBody = document.getElementById("reportsTableBody");
    if (!tableBody) return; // if this page doesn't have it, do nothing

    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        const data = await response.json();
        const scans = data.scans;

        if (scans.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No scans yet.</td></tr>';
            updateStats(0, 0, 0);
            return;
        }

        // ---- Build table rows ----
        tableBody.innerHTML = "";
        let pneumoniaCount = 0;
        let normalCount = 0;

        scans.forEach(scan => {
            if (scan.prediction === "Pneumonia") {
                pneumoniaCount++;
            } else {
                normalCount++;
            }

            const badgeClass = scan.prediction === "Pneumonia" ? "bg-danger" : "bg-success";
            const dateFormatted = new Date(scan.created_at).toLocaleDateString("en-IN", {
                day: "2-digit", month: "short", year: "numeric"
            });

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>SCAN-${scan.id}</td>
                <td>${scan.patient_name || "N/A"}</td>
                <td><span class="badge ${badgeClass}">${scan.prediction}</span></td>
                <td>${scan.confidence}%</td>
                <td>${dateFormatted}</td>
                <td>
                    <button class="btn btn-info btn-sm" onclick="viewScan(${scan.id})">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                </td>
                <td>
                    <a href="${API_BASE_URL}${scan.report_download_url}" class="btn btn-success btn-sm">
                        <i class="fa-solid fa-download"></i>
                    </a>
                </td>
            `;
            tableBody.appendChild(row);
        });

        updateStats(scans.length, normalCount, pneumoniaCount);

    } catch (error) {
        console.error("Error fetching history:", error);
        tableBody.innerHTML =
            '<tr><td colspan="7" class="text-center text-danger">' +
            'Could not connect to the backend. Please check if it is running.' +
            '</td></tr>';
    }
}

function updateStats(total, normal, pneumonia) {
    const totalEl = document.getElementById("totalReportsCount");
    const normalEl = document.getElementById("normalCount");
    const pneumoniaEl = document.getElementById("pneumoniaCount");

    if (totalEl) totalEl.textContent = total;
    if (normalEl) normalEl.textContent = normal;
    if (pneumoniaEl) pneumoniaEl.textContent = pneumonia;
}

// Runs when the "View" button is clicked - shows that scan's result on prediction.html
async function viewScan(scanId) {
    try {
        const response = await fetch(`${API_BASE_URL}/scan/${scanId}`);
        const scan = await response.json();

        const resultData = {
            prediction: scan.prediction,
            confidence: scan.confidence,
            scan_id: scan.id,
            original_image_url: API_BASE_URL + scan.original_image_url,
            gradcam_url: API_BASE_URL + scan.gradcam_url,
            report_download_url: API_BASE_URL + scan.report_download_url,
            patient_name: scan.patient_name || "N/A",
            patient_age: "N/A",
            patient_gender: "N/A",
            patient_id: "SCAN-" + scan.id,
            doctor_name: "N/A",
            hospital_name: "N/A"
        };
        sessionStorage.setItem("pneumovision_result", JSON.stringify(resultData));
        window.location.href = "prediction.html";
    } catch (error) {
        alert("Could not load scan details.");
    }
}


/* ============================================================
   Run the correct function as soon as the page loads
   (whichever page it is, it finds its own elements and runs its own function)
   ============================================================ */
document.addEventListener("DOMContentLoaded", function () {
    initUploadPage();
    initPredictionPage();
    initReportsPage();
});
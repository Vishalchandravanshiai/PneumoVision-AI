# 🫁 PneumoVision AI

**AI-assisted chest X-ray screening for pneumonia, with explainable predictions and automated report generation.**

Built by **Team Tensor Titans**

![Status](https://img.shields.io/badge/status-prototype-yellow)
![Python](https://img.shields.io/badge/python-3.x-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Keras-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> ⚠️ **Disclaimer:** PneumoVision AI is a research/prototype system intended to *assist* healthcare professionals. It is **not** a diagnostic device, has **not** undergone clinical validation, and is **not** a replacement for a physician or radiologist. Final diagnosis and treatment decisions must always be made by a qualified medical professional.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Problem](#-problem)
- [Solution](#-solution)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Model](#-model)
- [Explainable AI (Grad-CAM)](#-explainable-ai-grad-cam)
- [Dataset](#-dataset)
- [Performance](#-performance)
- [Workflow](#-workflow)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Run Instructions](#-run-instructions)
- [Use Cases](#-use-cases)
- [Business Vision](#-business-vision)
- [Target Customers](#-target-customers)
- [Potential Business Models](#-potential-business-models)
- [Competitive Positioning](#-competitive-positioning)
- [Scalability](#-scalability)
- [Security](#-security)
- [Clinical Validation](#-clinical-validation)
- [Roadmap](#-roadmap)
- [Limitations](#-limitations)
- [Team](#-team)
- [Disclaimer](#-disclaimer)

---

## 🔎 Overview

PneumoVision AI is a browser-based AI application that helps healthcare professionals rapidly screen chest X-rays for possible pneumonia. Alongside a prediction, it provides a confidence score, a Grad-CAM heatmap for interpretability, and a downloadable report — turning a single prediction into a more complete, documented screening workflow.

## ❗ Problem

In many healthcare environments, a chest X-ray must be interpreted by a radiologist to confirm pneumonia — but experienced radiology interpretation is not always immediately available. This can delay diagnosis and, in turn, delay treatment.

> **Core problem statement:**
> How can AI assist healthcare professionals in rapidly screening chest X-rays for possible pneumonia while also providing an interpretable explanation of the model's prediction?

## 💡 Solution

PneumoVision AI lets a user upload a chest X-ray through the browser and returns:

| Output | Description |
|---|---|
| 🏷️ Prediction | Pneumonia / Normal |
| 📊 Confidence Score | Model's confidence in the prediction |
| 🔥 Grad-CAM Heatmap | Highlights influential regions of the X-ray |
| 🩻 Heatmap Overlay | Heatmap layered on the original image |
| 📄 Downloadable Report | Summary of prediction + visuals |

The system is designed to **assist** healthcare professionals in triage and preliminary screening, not to replace clinical judgment.

## ✨ Features

- 🖼️ Upload a chest X-ray directly in the browser
- 🤖 Deep learning-based Pneumonia / Normal classification
- 📊 Confidence score for each prediction
- 🔥 Grad-CAM visual explanation of model focus areas
- 🩻 Heatmap overlay on the original X-ray
- 📄 Downloadable report (prediction, confidence, heatmap, timestamp)
- 🌐 Simple, accessible web-based workflow

## 🏗️ Architecture

```
┌───────────────────────┐
│      User / Doctor      │
└───────────┬──────────────┘
            │  uploads X-ray
            ▼
┌───────────────────────┐
│   Web UI (HTML/CSS/JS)  │
└───────────┬──────────────┘
            │  sends image
            ▼
┌───────────────────────┐
│      Flask Backend       │
└───────────┬──────────────┘
            │
            ▼
┌───────────────────────┐
│   Image Preprocessing    │
│  (resize, normalize etc) │
└───────────┬──────────────┘
            │
            ▼
┌───────────────────────┐
│    DenseNet121 Model     │
└───────────┬──────────────┘
            │
            ▼
┌───────────────────────┐
│  Prediction + Grad-CAM   │
│  (Pneumonia / Normal +   │
│   confidence + heatmap)  │
└───────────┬──────────────┘
            │
            ▼
┌───────────────────────┐
│     Report Generation    │
└───────────┬──────────────┘
            │  results returned
            ▼
┌───────────────────────┐
│   Displayed in Browser   │
└───────────────────────┘
```

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| 🐍 Language | Python |
| 🧠 Deep Learning | TensorFlow, Keras |
| 🏛️ Model | DenseNet121 |
| 🔍 Explainability | Grad-CAM |
| ⚙️ Backend | Flask |
| 🎨 Frontend | HTML, CSS, JavaScript |
| 🖼️ Image Processing | OpenCV / PIL |
| 📄 Report Generation | Python-based report generation |
| 📦 Environment | Python virtual environment |

## 🧠 Model

- **Architecture:** DenseNet121
- **Task:** Binary classification — Pneumonia vs. Normal
- **Reported test accuracy:** ~89.26%

> Note: Accuracy alone does not represent clinical diagnostic performance. Sensitivity, specificity, precision, recall, F1 score, ROC-AUC, calibration, external validation, robustness across datasets/sites, and subgroup/bias analysis are all needed before any clinical claims can be made — see [Clinical Validation](#-clinical-validation).

## 🔍 Explainable AI (Grad-CAM)

PneumoVision AI uses **Grad-CAM** to generate a visual heatmap showing which regions of the X-ray most influenced the model's prediction.

This is intended to:
- ✅ Provide a visual explanation of the prediction
- ✅ Highlight influential regions of the image
- ✅ Add interpretability to an otherwise "black box" prediction
- ✅ Support human review, not substitute for it

Grad-CAM output should be read as a supporting visualization — not as proof of disease or of clinical correctness.

## 📊 Dataset

The model was developed using a publicly available Chest X-Ray Pneumonia dataset for research/model development, with two target classes: **Normal** and **Pneumonia**.

For future clinical use, the model would require more representative clinical data and external validation across sites and populations.

## 📈 Performance

| Metric | Value |
|---|---|
| Test Accuracy | ~89.26% |

Further evaluation (sensitivity, specificity, precision, recall, F1, ROC-AUC, calibration, external validation) is planned — see [Roadmap](#-roadmap).

> Update this structure to match your actual repository layout.

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/<your-org>/pneumovision-ai.git
cd pneumovision-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Run Instructions

```bash
# Start the Flask server
python app.py
```

Then open `http://localhost:5000` in your browser, upload a chest X-ray, and view the prediction, confidence score, Grad-CAM heatmap, and downloadable report.

## 🎯 Use Cases

- 🏥 Preliminary chest X-ray screening in settings without immediate radiologist availability
- 🚑 Supporting faster triage in rural or resource-limited healthcare settings
- 👨‍⚕️ Assisting junior clinicians with a second, explainable opinion
- 📋 Generating a documented, shareable record of the AI-assisted screening

## 🚀 Business Vision

**Vision:** To make AI-assisted medical imaging more accessible, explainable, and practical for healthcare professionals.

**Positioning:** PneumoVision AI is an AI-assisted chest X-ray screening platform focused initially on pneumonia, combining deep-learning prediction, explainable AI, and automated documentation in a practical browser-based workflow.

## 🎯 Target Customers

**Primary:** 🏥 Hospitals · 🩺 Diagnostic centers · 🏨 Clinics

**Secondary:** 💻 Telemedicine providers · 🏢 Healthcare organizations · 🔬 Medical research organizations

## 💰 Potential Business Models

- 💳 SaaS subscription
- 🔢 Per-scan pricing
- 🏢 Enterprise licensing
- 🔌 API licensing / usage-based model

> None of these have been validated or finalized; they represent directions under consideration.

## ⚔️ Competitive Positioning

Established players such as **Qure.ai**, **Lunit**, **Aidoc**, and Google's medical AI work have already demonstrated that AI-assisted radiology can create real value. We view this as market validation rather than a barrier to entry.

PneumoVision AI's approach is to start with a focused use case — pneumonia screening — and build a practical, explainable, user-oriented workflow, then validate where it creates the most value, rather than claiming to outperform established players today

This is presented as a roadmap and architecture strategy, not a solved problem.

## 🔒 Security

A production version should consider:

- 🔑 Authentication and authorization
- 👤 Role-based access control
- 🔐 Encryption of data in transit and at rest
- 🗄️ Secure image storage
- 📝 Audit logs
- 🛡️ Secure APIs
- 🏥 Appropriate health-data handling practices

**Real, patient-identifiable data must never be uploaded to this or any public repository.**

## 🏥 Clinical Validation

PneumoVision AI is a **prototype** and is not clinically validated. Before any real clinical use, it would require:

- Clinical validation studies
- Safety evaluation
- Data privacy review
- Cybersecurity review
- Risk management
- Medical expert review
- Applicable regulatory evaluation (jurisdiction-specific)
- Appropriate documentation

## 🗺️ Roadmap

| Phase | Focus |
|---|---|
| **1 — Current Prototype** | Pneumonia classification, DenseNet121, Grad-CAM, confidence score, web app, report generation |
| **2 — Productization** | Improved UI/UX, authentication, patient history, doctor dashboard, cloud deployment, secure image storage, monitoring/logging |
| **3 — Validation** | Healthcare professional collaboration, external datasets, clinical validation, bias testing, robustness evaluation, workflow testing |
| **4 — Platform Expansion** | Additional chest-disease models, APIs, hospital information system integration, enterprise deployments, multi-tenant architecture, regional/international scaling |

## ⚠️ Limitations

- Trained on a public/research dataset with limited diversity
- Potential for bias not yet assessed
- No clinical validation performed yet
- No real-world external validation yet
- Prototype status — not production-ready
- Reported accuracy is not equivalent to clinical diagnostic performance

## 👥 Team

**Team Tensor Titans**

## 📜 Disclaimer

This project is a research/prototype system built for educational and hackathon purposes. It is **not** FDA-approved, **not** clinically proven, and **not** a production-ready medical device. It is intended to support — not replace — the judgment of qualified healthcare professionals. Do not use this system for real clinical decision-making.

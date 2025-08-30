# 📇 Business Card OCR

Business Card OCR is a Python-based application for extracting text and structured information from business cards using **Tesseract OCR** and **EasyOCR**.  
It provides a simple API and is ready for deployment with Docker and Gunicorn.

---

## 🚀 Features

- 🔍 OCR with **Tesseract** and **EasyOCR**
- 🌐 REST API for uploading and processing images
- 🐳 Dockerized for easy deployment
- ⚡ Gunicorn configuration for production
- 🛠 Utility scripts and deployment configs (`render.yaml`, `Dockerfile`)

---

## 📂 Project Structure

├── easyocr_logic.py # OCR logic using EasyOCR
├── tesseract_logic.py # OCR logic using Tesseract
├── main.py # Main application entry point
├── ocr-api/ # API endpoints for OCR
├── utils.py # Utility/helper functions
├── requirements.txt # Python dependencies
├── Dockerfile # Docker build configuration
├── gunicorn_conf.py # Gunicorn WSGI server configuration
├── render.yaml # Deployment settings
└── .gitignore # Git ignore rules



---

## ⚙️ Installation

Clone the repository:


git clone https://github.com/Piyanshu129/Buisness_card_ocr.git
cd Buisness_card_ocr

## Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate

## Install dependencies:

pip install -r requirements.txt

##  Run locally
python main.py

## Run with Docker
docker build -t business-card-ocr .
docker run -p 8000:8000 business-card-ocr

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from utils import preprocess_image, is_low_quality_text
from tesseract_logic import extract_text_tesseract, categorize_with_tesseract
from easyocr_logic import extract_text_easyocr, categorize_with_easyocr

app = FastAPI(title="Business Card OCR API")

# source ocr-api/bin/activate
#### uvicorn main:app --port 8000 --reload
#ngork 8000

# Terminal
# curl -X POST 'https://4803-122-160-25-31.ngrok-free.app/extract' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: multipart/form-data' \
#   -F "file=@\"/Users/piyanshu/Downloads/WhatsApp Image 2025-06-10 at 10.15.45 AM.jpeg\""


# docker run -p 8000:8000 business-card-api

#http://127.0.0.1:8000/docs#/default/extract_data_extract_post


@app.post("/extract")
async def extract_data(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return JSONResponse(status_code=400, content={"error": "Only image files are supported."})

    image_bytes = await file.read()
    image = preprocess_image(image_bytes)

    lines = extract_text_tesseract(image)
    use_easyocr = is_low_quality_text(lines)

    if use_easyocr:
        lines = extract_text_easyocr(image)
        data = categorize_with_easyocr(lines)
        method = "EasyOCR"
    else:
        data = categorize_with_tesseract(lines)
        method = "Tesseract"

    return {"method_used": method, "extracted_data": data}

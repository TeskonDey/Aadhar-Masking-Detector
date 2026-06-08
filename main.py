from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import logging

from core.document_ingestion import process_image_bytes, process_pdf_bytes
from core.ocr_engine import extract_text_from_images
from core.pattern_matcher import check_aadhaar_compliance

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Aadhaar Masking Detector API", version="1.0.0")

@app.post("/api/v1/verify-aadhaar")
async def verify_aadhaar_document(file: UploadFile = File(...)):
    logger.info(f"Processing file '{file.filename}' of type '{file.content_type}'")

    
    try:
        file_bytes = await file.read()
        
        if file.content_type == "application/pdf":
            images = process_pdf_bytes(file_bytes)
        elif file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
            images = process_image_bytes(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, JPEG, or PNG.")
            
        extracted_text = extract_text_from_images(images)
        compliance_result = check_aadhaar_compliance(extracted_text)
        
        return JSONResponse(
            status_code=200,
            content={
                "filename": file.filename,
                "status": compliance_result["status"],
                "details": compliance_result["reason"]
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Pipeline Failure: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error processing the document.")
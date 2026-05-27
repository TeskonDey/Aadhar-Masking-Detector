import pytesseract
import easyocr
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

# Initialize EasyOCR globally so it only loads once on startup
logger.info("Loading EasyOCR models (this may take a moment)...")
reader = easyocr.Reader(['en'], gpu=False) 

def extract_text_from_images(images: list[np.ndarray]) -> str:
    extracted_pages = []

    for idx, img in enumerate(images):
        logger.info(f"Running OCR on page {idx + 1}...")
        
        # 1. Tesseract Fast Pass
        tesseract_text = pytesseract.image_to_string(img).strip()
        alnum_count = len(re.findall(r'[A-Za-z0-9]', tesseract_text))
        
        # 2. EasyOCR Fallback (if Tesseract found < 10 valid characters)
        if alnum_count < 10:
            logger.warning(f"Tesseract poor (only {alnum_count} valid chars). Falling back to EasyOCR...")
            easyocr_results = reader.readtext(img)
            easy_text = " ".join([result[1] for result in easyocr_results])
            extracted_pages.append(easy_text)
        else:
            extracted_pages.append(tesseract_text)

    return "\n".join(extracted_pages)
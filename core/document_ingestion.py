import fitz  
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def process_image_bytes(file_bytes: bytes) -> list[np.ndarray]:
    try:
        nparr = np.frombuffer(file_bytes, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_cv2 is None:
            raise ValueError("Could not decode image bytes.")
        return [img_cv2]
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise

def process_pdf_bytes(file_bytes: bytes) -> list[np.ndarray]:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        cv2_images = []
        zoom_matrix = fitz.Matrix(4.16, 4.16) # 300 DPI
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=zoom_matrix)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            
            if pix.n == 3:  
                img_cv2 = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            elif pix.n == 4: 
                img_cv2 = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            else:
                img_cv2 = img_array 
                
            cv2_images.append(img_cv2)
            
        return cv2_images
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise
import re
import logging

logger = logging.getLogger(__name__)

def check_aadhaar_compliance(extracted_text: str) -> dict:
    
    # NEW STEP: Scrub out 16-digit VIDs so they don't trigger false positives
    vid_pattern = re.compile(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b')
    
    # Replace any 16-digit number in the text with the word "[VID]"
    clean_text = vid_pattern.sub('[VID]', extracted_text)

    # Now run our normal checks on the sanitized text
    unmasked_pattern = re.compile(r'(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)')
    masked_pattern = re.compile(r'\b[X\*]{4}[ -]?[X\*]{4}[ -]?\d{4}\b', re.IGNORECASE)

    if unmasked_pattern.search(clean_text):
        logger.warning("Unmasked Aadhaar number detected!")
        return {"status": "NON_COMPLIANT", "reason": "Fully visible 12-digit Aadhaar number found."}
        
    elif masked_pattern.search(clean_text):
        logger.info("Properly masked Aadhaar number detected.")
        return {"status": "COMPLIANT", "reason": "Masked Aadhaar format verified."}
        
    else:
        return {"status": "NOT_FOUND", "reason": "No valid Aadhaar pattern detected."}
from PIL import Image, ImageEnhance
import numpy as np
import re
import pandas as pd
import pytesseract
from io import BytesIO

def extract_text_tesseract(image):
    """Your text extraction function from tesseract-ocr.py."""
    text = pytesseract.image_to_string(image)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return lines




def is_low_quality_text(lines):
    """Your exact quality check function from tesseract-ocr.py."""
    if len(lines) < 3: return True
    joined_text = " ".join(lines)
    email_found = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", joined_text))
    phone_found = bool(re.search(r"\+?\d[\d\-$$$$ ]{7,}\d", joined_text))
    noise_ratio = sum(1 for c in joined_text if not c.isalnum() and c not in "@.:-, ") / max(len(joined_text), 1)
    return not email_found or not phone_found or noise_ratio > 0.5


def categorize_with_tesseract(lines):
    """
    UPDATED: The email regex in this function has been corrected to fix the 'bad character range' error.
    """

    def extract_emails_and_websites(text_lines):
        emails, websites = [], []

        # --- CORRECTED EMAIL PATTERN (removed extra hyphen from 0--9) ---
        email_pattern = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9-.]+\b")

        website_pattern = re.compile(
            r"https?://[a-zA-Z0-9\-\.\_/]+|\b[a-zA-Z0-9.-]+\.(?:com|in|org|net|co|io|dev|biz|info)\b")


        for line in text_lines:
            emails.extend(email_pattern.findall(line.lower()))
            websites.extend([s for s in website_pattern.findall(line.lower()) if '@' not in s])
        return list(set(emails)), list(set(websites))

    data = {"Name": [], "Email": [], "Phone": [], "Website": [], "Pincode": [], "Address": []}
    emails, websites = extract_emails_and_websites(lines)
    data["Email"] = emails
    data["Website"].extend(
        [s for s in websites if not any(s.endswith(d) for d in ['yahoo.com', 'gmail.com', 'rediffmail.com'])])

    address_keywords = ['office', 'Corporate Office', 'bldg', 'road', 'rd', 'st', 'sector', 'house', 'plot', 'near','point',
                        'park', 'nagar', 'building', 'complex', 'village', 'area', 'hall', 'block', 'lane', 'layout',
                        'mumbai', 'vashi', 'opp', 'city', 'galli', 'Flat', 'Apartments', 'street', '#', 'gaon','nagar',
                        'market', 'phase','bazar']

    def extract_full_address(lines_to_search):
        address_block, address_started = [], False
        for line in lines_to_search:
            if not address_started and re.search(r'\bAdd\b[:：]?', line, re.IGNORECASE):
                address_started = True
                address_block.append(re.sub(r'\bAdd\b[:：]?', '', line, flags=re.IGNORECASE).strip())
            elif address_started:
                if re.search(r'\b(Contact|Phone|Email|Support|Web|www|@|[0-9]{10}|Pincode|.com)\b', line,
                             re.IGNORECASE): break
                address_block.append(line.strip())
        return address_block

    address_block = extract_full_address(lines)
    if address_block:
        data["Address"] = address_block
    else:
        for line in lines:
            if any(keyword in line.lower() for keyword in address_keywords):
                # This is the single condition you requested:
                if 'www.' not in line.lower() and '.com' not in line.lower() and '.in' not in line.lower() and '@' not in line:
                    data["Address"].append(line)

    for line in lines:
        line_cleaned = re.sub(r'(?i)(Mob|contact|support|Tel|cell|Ph.|Phone)\s*[:\-]?', '', line.lower())
        phones = re.findall(
            r"(?:\+91[\s\-]?)?(?:\d{5}[\s\-]?\d{5}|\b\d{10}\b|\b\d{7}\b|\b\d{4}[\-\s]?\d{7}\b|\b\d{11}\b|\b\d{3}[\-\s]?\d{3}[\-\s]?\d{4}\b|\+91[\s]?\d{2}[\s]?\d{8})",
            line_cleaned)
        data["Phone"].extend(p.replace(' ', '') for p in phones)
        pincodes = re.findall(r"\b\d{6}\b|\b\d{3}[\s\-]?\d{3}\b|\b\d{4}[\s\-]?\d{2}\b", re.sub(r"[^\d\s\-]", "", line))
        data["Pincode"].extend(pincodes)

    # Try extracting name based on heuristics
    for line in lines:
        if any(char.isalpha() for char in line) and line.strip() and not any(char.isdigit() for char in line):
            if len(line.split()) <= 4 and not any(x in line.lower() for x in ['email', 'web', 'support']):
                data["Name"].append(line.strip())
                break

    # Fallback to website domain if name is not found or looks invalid (like 'a', 'abc@', etc.)
    def is_invalid_name(name):
        return not name or len(name.strip()) <= 2 or not any(c.isalpha() for c in name) or '@' in name

    if not data["Name"] or is_invalid_name(data["Name"][0]):
        if websites:
            domain = websites[0].split('.')[0]
            domain = re.sub(r'[^a-zA-Z]', '', domain)  # clean non-alpha chars
            data["Name"] = [domain.capitalize()]

    return {"Name": ', '.join(set(data["Name"])), "Email": ', '.join(set(data["Email"])),
            "Phone": ', '.join(set(data["Phone"])), "Address": ', '.join(set(data["Address"])),
            "Website": ', '.join(set(data["Website"])), "Pincode": ', '.join(set(data["Pincode"]))}



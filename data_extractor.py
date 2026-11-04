"""
Data Extractor Module
Extracts individual structured fields from voter card text (OCR and/or native PDF text).
Includes specialized functions with strict validation and error tolerance for Devanagari labels.
"""

import re
from typing import Optional, Tuple, Dict, Any


def clean_text_field(val: str) -> str:
    """Remove OCR artifacts, photo watermarks, and special symbols from extracted text."""
    if not val:
        return ""
    # Strip photo labels in English and Hindi
    val = re.sub(r'(?:Photo\s*is\s*Available|Photo\s*Not\s*Available|Photo\s*Available|Photo|Available|Ph\b|Avail\b)', '', val, flags=re.I)
    val = re.sub(r'(?:फोटो\s*उपलब्ध\s*है|फोटो\s*उपलब्ध\s*नहीं\s*है|फोटो\s*उपलब्ध|फोटो)', '', val)
    # Strip quotes, punctuation and symbols
    val = re.sub(r'["\'“”’`*_~|:;=+\\/\^$#@!.\-–—]+', ' ', val)
    # Strip trailing 1-4 letter English words (like re, ren, is, ph)
    val = re.sub(r'\s+[a-zA-Z]{1,4}\s*$', '', val)
    # Strip trailing lone particles like 'कि', 'का', 'के', 'सी'
    val = re.sub(r'\s+[ककस][िाेी]\s*$', '', val)
    # Strip leading punctuation/symbols
    val = re.sub(r'^[ः:;*~.\s]+', '', val)
    val = re.sub(r'\s+', ' ', val).strip()
    return val


def extract_serial_number(text: str) -> Optional[int]:
    """
    Extract the voter serial number.
    Usually found in top-left box or as first token.
    """
    if not text:
        return None

    # Pattern 1: Leading standalone number or surrounded by box borders [ 1 ] or 1.
    m = re.search(r'^\s*\[?\s*(\d{1,5})\s*\]?[\s.\-–|]', text, re.MULTILINE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    # Pattern 2: Word 'क्र' or 'क्र.' or 'कमरपक' or 'क्रम' followed by number
    m = re.search(r'(?:क्र(?:म)?(?:\s*संख्या)?|कमरपक|S(?:er(?:ial)?)?\s*No\.?)[:\s]+(\d{1,5})', text, re.I)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    # Pattern 3: First number on the first line
    first_line = text.strip().split('\n')[0] if text else ''
    m = re.search(r'\b(\d{1,5})\b', first_line)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    return None


def extract_epic_number(text: str) -> str:
    """
    Extract EPIC (Voter ID) number.
    Standard Indian EPIC: 3 letters + 7 digits (e.g., BMQ1490051, SSD0900839, RJ/XX/...).
    Also supports 10-char alphanumeric formats.
    Always returned as string.
    """
    if not text:
        return ""

    # Common Rajasthan formats: SSD1234567, BMQ1234567, RJ/19/..., etc.
    # Pattern 1: Exact 3 uppercase letters followed by 7 digits
    m = re.search(r'\b([A-Z]{3}[0-9]{7})\b', text)
    if m:
        return m.group(1)

    # Pattern 2: Slash format (e.g., RJ/25/123/123456)
    m = re.search(r'\b([A-Z]{2}\s*/\s*[0-9]{1,3}\s*/\s*[0-9]{1,3}\s*/\s*[0-9]{1,7})\b', text)
    if m:
        return re.sub(r'\s+', '', m.group(1))

    # Pattern 3: Relaxed 3 letters + 7 digits with possible minor OCR spacing
    m = re.search(r'\b([A-Z]{3})\s*([0-9]{7})\b', text)
    if m:
        return m.group(1) + m.group(2)

    # Pattern 4: General 10-character alphanumeric EPIC
    m = re.search(r'\b([A-Z]{2,4}[0-9]{6,8})\b', text)
    if m:
        return m.group(1)

    return ""


def extract_voter_name(text: str) -> str:
    """
    Extract Voter Name in Hindi.
    Distinguishes from Father/Husband name.
    """
    if not text:
        return ""

    # Check for नाम: but NOT पिता का नाम: or पति का नाम:
    lines = text.split('\n')
    for line in lines:
        line_clean = line.strip()
        # Must not contain पिता or पति
        if re.search(r'(?:पिता|पति)', line_clean):
            continue
        
        m = re.search(r'(?:^|[^\w])नाम[:\s*–—\-_]*([^\n\r]+)', line_clean)
        if m:
            val = clean_text_field(m.group(1))
            # Remove trailing tokens like मकान, आयु, लिंग if on same line
            val = re.sub(r'(?:मकान|आयु|लिंग).*', '', val).strip()
            if val:
                return val

    # Fallback multi-line regex
    m = re.search(r'(?<!पिता\s)(?<!पति\s)(?<!का\s)नाम[:\s*–—\-_]+([^\n\r]+)', text)
    if m:
        val = clean_text_field(m.group(1))
        val = re.sub(r'(?:मकान|आयु|लिंग).*', '', val).strip()
        if val:
            return val

    return ""


def extract_father_name(text: str) -> str:
    """
    Extract Father's Name in Hindi.
    Strictly isolated from Husband's Name.
    """
    if not text:
        return ""

    # Look for 'पिता' or 'पिता का नाम'
    m = re.search(r'पिता\s*(?:का\s*)?नाम[:\s*–—\-_]*([^\n\r]+)', text)
    if m:
        val = clean_text_field(m.group(1))
        val = re.sub(r'(?:मकान|आयु|लिंग).*', '', val).strip()
        return val

    # Short form 'पिता:'
    m = re.search(r'पिता[:\s*–—\-_]+([^\n\r]+)', text)
    if m:
        val = clean_text_field(m.group(1))
        val = re.sub(r'(?:मकान|आयु|लिंग).*', '', val).strip()
        return val

    return ""


def extract_husband_name(text: str) -> str:
    """
    Extract Husband's Name in Hindi.
    Strictly isolated from Father's Name.
    """
    if not text:
        return ""

    # Look for 'पति' or 'पति का नाम'
    m = re.search(r'पति\s*(?:का\s*)?नाम[:\s*–—\-_]*([^\n\r]+)', text)
    if m:
        val = clean_text_field(m.group(1))
        val = re.sub(r'(?:मकान|आयु|लिंग).*', '', val).strip()
        return val

    # Short form 'पति:'
    m = re.search(r'पति[:\s*–—\-_]+([^\n\r]+)', text)
    if m:
        val = clean_text_field(m.group(1))
        val = re.sub(r'(?:मकान|आयु|लिंग).*', '', val).strip()
        return val

    return ""


def extract_house_number(text: str) -> str:
    """
    Extract House Number.
    Preserves alphanumeric values (e.g. 47, 12-A, 45/2, etc.).
    Avoids confusing with Age.
    """
    if not text:
        return ""

    # Look for 'मकान संख्या' or 'मकान नं' or 'House No'
    m = re.search(r'(?:मकान\s*(?:संख्या|सपखजर|नं(?:ंबर)?|क्र(?:मांक)?)?|House\s*(?:No\.?)?)[:\s*–—\-_]+([0-9A-Za-z\u0966-\u096F\/\-]+)', text)
    if m:
        val = clean_text_field(m.group(1))
        # Filter out common false matches
        if val and val.lower() not in ('photo', 'available', 'is'):
            return val

    return ""


def extract_age(text: str) -> Optional[int]:
    """
    Extract Age as integer.
    Avoids confusing with House Number or Serial Number.
    """
    if not text:
        return None

    # Look for 'आयु:' or 'Age:' followed by integer
    m = re.search(r'(?:आयु|आजच|उम्र|Age)[:\s*–—\-_]+(\d{1,3})', text, re.I)
    if m:
        try:
            val = int(m.group(1))
            if 18 <= val <= 125:
                return val
        except ValueError:
            pass

    # Look for age before gender (e.g. "64 लिंग: पुरुष")
    m = re.search(r'(\d{2})\s*(?:लिंग|Gender)', text, re.I)
    if m:
        try:
            val = int(m.group(1))
            if 18 <= val <= 125:
                return val
        except ValueError:
            pass

    return None


def extract_gender(text: str) -> Tuple[str, str]:
    """
    Extract Gender in both Hindi and English.
    Returns: (Gender_Hindi, Gender_English)
    """
    if not text:
        return ("", "")

    # Check for Male
    if re.search(r'(?:पुरूष|पुरुष|पचरष|Male|\bM\b)', text, re.I):
        return ("पुरुष", "Male")

    # Check for Female
    if re.search(r'(?:स्त्री|महिला|सल|Female|\bF\b)', text, re.I):
        return ("स्त्री", "Female")

    # Check for Third Gender / Other
    if re.search(r'(?:तृतीय\s*लिंग|अन्य|Other|Transgender)', text, re.I):
        return ("तृतीय लिंग", "Other")

    return ("", "")


def extract_voter_card_record(ocr_text: str, digital_text: str = "",
                               serial_hint: str = "", epic_hint: str = "") -> Dict[str, Any]:
    """
    Extract all voter details by fusing OCR text with native digital text.
    Digital text provides highest fidelity for alphanumeric codes (EPIC, Serial, House, Age),
    while OCR provides authentic Devanagari text for names.
    """
    # 1. Serial Number (check serial_hint box first)
    serial = None
    if serial_hint:
        m_s = re.search(r'\b(\d{1,5})\b', serial_hint)
        if m_s:
            try:
                serial = int(m_s.group(1))
            except ValueError:
                pass

    if serial is None:
        serial = extract_serial_number(digital_text)
    if serial is None:
        serial = extract_serial_number(ocr_text)

    # 2. EPIC Number (check epic_hint box first)
    epic = ""
    if epic_hint:
        epic = extract_epic_number(epic_hint)
    if not epic:
        epic = extract_epic_number(digital_text)
    if not epic:
        epic = extract_epic_number(ocr_text)

    # 3. Voter Name
    name_hi = extract_voter_name(ocr_text)
    if not name_hi and digital_text:
        name_hi = extract_voter_name(digital_text)

    # 4. Father Name
    father_hi = extract_father_name(ocr_text)
    if not father_hi and digital_text:
        father_hi = extract_father_name(digital_text)

    # 5. Husband Name
    husband_hi = extract_husband_name(ocr_text)
    if not husband_hi and digital_text:
        husband_hi = extract_husband_name(digital_text)

    # 6. House Number
    house_no = extract_house_number(digital_text)
    if not house_no:
        house_no = extract_house_number(ocr_text)

    # 7. Age
    age = extract_age(digital_text)
    if age is None:
        age = extract_age(ocr_text)

    # 8. Gender
    gender_hi, gender_en = extract_gender(ocr_text)
    if not gender_hi:
        gender_hi, gender_en = extract_gender(digital_text)

    return {
        "Serial_No": serial,
        "EPIC_Number": epic,
        "Name_Hindi": name_hi,
        "Father_Name_Hindi": father_hi,
        "Husband_Name_Hindi": husband_hi,
        "House_Number": house_no,
        "Age": age,
        "Gender_Hindi": gender_hi,
        "Gender_English": gender_en,
        "Raw_OCR_Text": ocr_text or digital_text
    }

"""
Data Validator Module
Validates extracted voter records, computes confidence scores, detects duplicates,
and assigns VERIFIED or REVIEW_REQUIRED status with detailed explanations.
"""

import re
from typing import List, Dict, Any, Tuple, Set


# Standard EPIC format: 3 letters + 7 digits (e.g. BMQ1490051, SSD0900839)
EPIC_STANDARD_REGEX = re.compile(r'^[A-Z]{3}[0-9]{7}$')
EPIC_GENERAL_REGEX = re.compile(r'^[A-Z0-9\/\-]{8,16}$')


def validate_single_record(record: Dict[str, Any],
                           global_epics: Set[str],
                           section_serials: Dict[str, Set[int]]) -> Dict[str, Any]:
    """
    Validate a single voter record and calculate confidence score and review status.
    """
    reasons = []
    score = 0.0

    # 1. Serial Number Validation (Weight: 15%)
    serial = record.get("Serial_No")
    sec_key = f"{record.get('Section_Name', '')}_{record.get('Ward_Number', '')}"
    if serial is not None and isinstance(serial, int) and serial > 0:
        score += 0.15
        if sec_key not in section_serials:
            section_serials[sec_key] = set()
        if serial in section_serials[sec_key]:
            reasons.append(f"Duplicate Serial No {serial} in section")
        else:
            section_serials[sec_key].add(serial)
    else:
        reasons.append("Missing or invalid Serial No")

    # 2. EPIC Number Validation (Weight: 25%)
    epic = str(record.get("EPIC_Number", "")).strip().upper()
    record["EPIC_Number"] = epic  # normalize
    if epic:
        if EPIC_STANDARD_REGEX.match(epic):
            score += 0.25
        elif EPIC_GENERAL_REGEX.match(epic):
            score += 0.20
            reasons.append("Non-standard EPIC format")
        else:
            score += 0.10
            reasons.append("Suspicious EPIC pattern")

        # Duplicate check
        if epic in global_epics:
            reasons.append(f"Duplicate EPIC: {epic}")
        else:
            global_epics.add(epic)
    else:
        reasons.append("Missing EPIC Number")

    # 3. Voter Name Validation (Weight: 20%)
    name_hi = str(record.get("Name_Hindi", "")).strip()
    if name_hi and len(name_hi) >= 2:
        # Check if contains Devanagari or letters
        if any('\u0900' <= ch <= '\u097F' for ch in name_hi) or any(ch.isalpha() for ch in name_hi):
            score += 0.20
        else:
            score += 0.05
            reasons.append("Suspicious Name characters")
    else:
        reasons.append("Missing Voter Name")

    # 4. Father / Husband Separation & Availability (Weight: 15%)
    father_hi = str(record.get("Father_Name_Hindi", "")).strip()
    husband_hi = str(record.get("Husband_Name_Hindi", "")).strip()

    if father_hi and husband_hi:
        # Both should not usually be present for the same voter in standard card
        score += 0.10
        reasons.append("Both Father and Husband names populated")
    elif father_hi and len(father_hi) >= 2:
        score += 0.15
    elif husband_hi and len(husband_hi) >= 2:
        score += 0.15
    else:
        score += 0.05
        reasons.append("Missing Father/Husband Name")

    # 5. Age Validation (Weight: 10%)
    age = record.get("Age")
    if age is not None and isinstance(age, int):
        if 18 <= age <= 125:
            score += 0.10
        else:
            reasons.append(f"Age out of bounds ({age})")
    else:
        reasons.append("Missing Age")

    # 6. Gender Validation (Weight: 10%)
    gender_en = str(record.get("Gender_English", "")).strip()
    if gender_en in ("Male", "Female", "Other"):
        score += 0.10
    else:
        reasons.append("Unrecognized Gender")

    # 7. House Number Validation (Weight: 5%)
    house = str(record.get("House_Number", "")).strip()
    if house:
        score += 0.05
    else:
        # Minor notice, doesn't always fail verification alone
        pass

    # Ensure score bounds [0.0, 1.0]
    score = min(1.0, max(0.0, score))
    confidence_pct = round(score * 100, 1)

    # Determine Review Status
    # Critical criteria for REVIEW_REQUIRED:
    # - Missing or invalid Serial No
    # - Missing or duplicate or invalid EPIC
    # - Missing Voter Name
    # - Missing both Father and Husband names
    # - Both Father and Husband names present (conflicting)
    # - Missing or invalid Age
    # - Unrecognized Gender
    # - Duplicate Serial No in section
    critical_errors = [
        r for r in reasons if "Missing" in r
        or "Duplicate" in r
        or "out of bounds" in r
        or "Both Father and Husband" in r
        or "Unrecognized Gender" in r
        or "Suspicious" in r
    ]

    if not critical_errors and score >= 0.80 and len(reasons) == 0:
        review_status = "VERIFIED"
        review_reason = "Verified: All primary fields validated"
    else:
        review_status = "REVIEW_REQUIRED"
        review_reason = "; ".join(reasons) if reasons else "Score below threshold"

    record["OCR_Confidence"] = f"{confidence_pct}%"
    record["Review_Status"] = review_status
    record["Review_Reason"] = review_reason

    return record


def validate_all_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate a complete list of voter records, tracking duplicates across the entire set.
    """
    global_epics: Set[str] = set()
    section_serials: Dict[str, Set[int]] = {}

    validated_list = []
    for rec in records:
        v_rec = validate_single_record(rec, global_epics, section_serials)
        validated_list.append(v_rec)

    return validated_list

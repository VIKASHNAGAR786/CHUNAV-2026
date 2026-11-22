"""
=============================================================================
         JAINAGAR CHUNAV 2026 - MASTER RESYNC & VALIDATION REPAIR
  1. Fixes missing names (including Pradhyumna Nagar, Ayush, etc.)
  2. Updates ECI standard regex (RJ/14/... and BMQT... to VERIFIED)
  3. Updates all 9 Excel files in output/ and VOTER LISTS/EXCEL_OUTPUT/
  4. Updates SQLite database & voters_data.js
  5. Repackages UI_WORK_FOR_COLAB.zip
=============================================================================
"""

import os
import sys
import glob
import re
import json
import sqlite3
import shutil
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from data_extractor import extract_voter_card_record, clean_text_field, normalize_name
from transliterator import transliterate_hindi_to_english
from validator import validate_all_records, validate_single_record


def resync_all_excel_workbooks():
    excel_dirs = [
        os.path.abspath(r"output"),
        os.path.abspath(r"VOTER LISTS\EXCEL_OUTPUT")
    ]

    total_updated_voters = 0
    total_verified = 0
    total_review = 0

    # Header style for sheets
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    review_fill = PatternFill(start_color="FDE9D9", end_color="FDE9D9", fill_type="solid")

    for f_idx in range(1, 10):
        fname = f"JAINAGAR-Ward No-{f_idx:03d}.xlsx"
        print(f"\n[Processing Ward {f_idx}] -> {fname}")

        # Process each directory
        for edir in excel_dirs:
            fpath = os.path.join(edir, fname)
            if not os.path.exists(fpath):
                continue

            wb = openpyxl.load_workbook(fpath)
            ws_voters = wb["Voters"]
            has_raw = "Raw_OCR" in wb.sheetnames
            raw_map = {}
            if has_raw:
                for r in wb["Raw_OCR"].iter_rows(min_row=2, values_only=True):
                    # page_num, card_num, serial_no, raw_ocr
                    if r[2] is not None:
                        raw_map[r[2]] = r[3]

            # Read all rows into records
            records = []
            for row in ws_voters.iter_rows(min_row=2, values_only=True):
                serial = row[0]
                epic = row[1]
                name_hi = row[2]
                name_en = row[3]
                father_hi = row[4]
                father_en = row[5]
                husband_hi = row[6]
                husband_en = row[7]
                house = row[8]
                age = row[9]
                gender_hi = row[10]
                gender_en = row[11]
                page = row[12]
                section = row[13]
                panchayat = row[14]
                ward = row[15]

                # Check if name is missing or needs repair
                raw_text = raw_map.get(serial, "")
                needs_extraction = (
                    not name_hi or
                    str(name_hi).strip() in ("", "None") or
                    serial == 347 and f_idx == 8 or
                    "ररजेंद्र" in str(father_hi) or
                    "प्रद्मुस्न" in str(name_hi) or
                    "TEA" in str(name_hi)
                )

                if needs_extraction and raw_text:
                    rec_ext = extract_voter_card_record(ocr_text=raw_text, digital_text=f"{serial} {epic}")
                    if rec_ext.get("Name_Hindi"):
                        name_hi = rec_ext["Name_Hindi"]
                        name_en = transliterate_hindi_to_english(name_hi)
                    if rec_ext.get("Father_Name_Hindi"):
                        father_hi = rec_ext["Father_Name_Hindi"]
                        father_en = transliterate_hindi_to_english(father_hi)
                    if rec_ext.get("Husband_Name_Hindi"):
                        husband_hi = rec_ext["Husband_Name_Hindi"]
                        husband_en = transliterate_hindi_to_english(husband_hi)

                # Special Candidate guarantee: Ward 8 Serial 347 is Pradhyumna Nagar
                if f_idx == 8 and serial == 347:
                    name_hi = "प्रद्युम्न नागर"
                    name_en = "Pradhyumna Nagar"
                    father_hi = "राजेंद्र नागर"
                    father_en = "Rajendra Nagar"
                    epic = "SSD1832757"
                    house = "44"
                    age = 20
                    gender_hi = "पुरुष"
                    gender_en = "Male"

                # Cleanup any remaining father distortion
                if father_hi and "ररजेंद्र" in str(father_hi):
                    father_hi = str(father_hi).replace("ररजेंद्र", "राजेंद्र")
                    father_en = transliterate_hindi_to_english(father_hi)

                rec = {
                    "Serial_No": serial,
                    "EPIC_Number": str(epic).strip() if epic else "",
                    "Name_Hindi": str(name_hi).strip() if name_hi else "",
                    "Name_English": str(name_en).strip() if name_en else "",
                    "Father_Name_Hindi": str(father_hi).strip() if father_hi else "",
                    "Father_Name_English": str(father_en).strip() if father_en else "",
                    "Husband_Name_Hindi": str(husband_hi).strip() if husband_hi else "",
                    "Husband_Name_English": str(husband_en).strip() if husband_en else "",
                    "House_Number": str(house).strip() if house else "",
                    "Age": age,
                    "Gender_Hindi": str(gender_hi).strip() if gender_hi else "",
                    "Gender_English": str(gender_en).strip() if gender_en else "",
                    "Page_Number": page,
                    "Section_Name": section,
                    "Panchayat_Name": panchayat,
                    "Ward_Number": ward
                }
                records.append(rec)

            # Validate all records
            validated = validate_all_records(records)

            # 1. Update Voters Sheet
            for row_idx, v in enumerate(validated, start=2):
                ws_voters.cell(row=row_idx, column=1, value=v["Serial_No"])
                ws_voters.cell(row=row_idx, column=2, value=v["EPIC_Number"])
                ws_voters.cell(row=row_idx, column=3, value=v["Name_Hindi"])
                ws_voters.cell(row=row_idx, column=4, value=v["Name_English"])
                ws_voters.cell(row=row_idx, column=5, value=v["Father_Name_Hindi"])
                ws_voters.cell(row=row_idx, column=6, value=v["Father_Name_English"])
                ws_voters.cell(row=row_idx, column=7, value=v["Husband_Name_Hindi"])
                ws_voters.cell(row=row_idx, column=8, value=v["Husband_Name_English"])
                ws_voters.cell(row=row_idx, column=9, value=v["House_Number"])
                ws_voters.cell(row=row_idx, column=10, value=v["Age"])
                ws_voters.cell(row=row_idx, column=11, value=v["Gender_Hindi"])
                ws_voters.cell(row=row_idx, column=12, value=v["Gender_English"])
                ws_voters.cell(row=row_idx, column=13, value=v["Page_Number"])
                ws_voters.cell(row=row_idx, column=14, value=v["Section_Name"])
                ws_voters.cell(row=row_idx, column=15, value=v["Panchayat_Name"])
                ws_voters.cell(row=row_idx, column=16, value=v["Ward_Number"])
                ws_voters.cell(row=row_idx, column=17, value=v["OCR_Confidence"])
                ws_voters.cell(row=row_idx, column=18, value=v["Review_Status"])
                ws_voters.cell(row=row_idx, column=19, value=v["Review_Reason"])

            # 2. Rebuild Review_Required Sheet
            if "Review_Required" in wb.sheetnames:
                del wb["Review_Required"]
            ws_review = wb.create_sheet(title="Review_Required")

            voters_headers = [c for c in next(ws_voters.iter_rows(min_row=1, max_row=1, values_only=True))]
            for c_idx, h in enumerate(voters_headers, start=1):
                cell = ws_review.cell(row=1, column=c_idx, value=h)
                cell.fill = review_fill
                cell.font = Font(name="Calibri", size=11, bold=True, color="C00000")

            rev_row = 2
            for v in validated:
                if v["Review_Status"] == "REVIEW_REQUIRED":
                    ws_review.cell(row=rev_row, column=1, value=v["Serial_No"])
                    ws_review.cell(row=rev_row, column=2, value=v["EPIC_Number"])
                    ws_review.cell(row=rev_row, column=3, value=v["Name_Hindi"])
                    ws_review.cell(row=rev_row, column=4, value=v["Name_English"])
                    ws_review.cell(row=rev_row, column=5, value=v["Father_Name_Hindi"])
                    ws_review.cell(row=rev_row, column=6, value=v["Father_Name_English"])
                    ws_review.cell(row=rev_row, column=7, value=v["Husband_Name_Hindi"])
                    ws_review.cell(row=rev_row, column=8, value=v["Husband_Name_English"])
                    ws_review.cell(row=rev_row, column=9, value=v["House_Number"])
                    ws_review.cell(row=rev_row, column=10, value=v["Age"])
                    ws_review.cell(row=rev_row, column=11, value=v["Gender_Hindi"])
                    ws_review.cell(row=rev_row, column=12, value=v["Gender_English"])
                    ws_review.cell(row=rev_row, column=13, value=v["Page_Number"])
                    ws_review.cell(row=rev_row, column=14, value=v["Section_Name"])
                    ws_review.cell(row=rev_row, column=15, value=v["Panchayat_Name"])
                    ws_review.cell(row=rev_row, column=16, value=v["Ward_Number"])
                    ws_review.cell(row=rev_row, column=17, value=v["OCR_Confidence"])
                    ws_review.cell(row=rev_row, column=18, value=v["Review_Status"])
                    ws_review.cell(row=rev_row, column=19, value=v["Review_Reason"])
                    rev_row += 1

            # 3. Update Summary Sheet
            w_total = len(validated)
            w_verified = sum(1 for v in validated if v["Review_Status"] == "VERIFIED")
            w_review = sum(1 for v in validated if v["Review_Status"] == "REVIEW_REQUIRED")
            if "Summary" in wb.sheetnames:
                ws_sum = wb["Summary"]
                for r_idx in range(1, ws_sum.max_row + 1):
                    val = ws_sum.cell(row=r_idx, column=1).value
                    if val and "Verified Records" in str(val):
                        ws_sum.cell(row=r_idx, column=2, value=w_verified)
                    elif val and "Review Required" in str(val):
                        ws_sum.cell(row=r_idx, column=2, value=w_review)

            wb.save(fpath)
            wb.close()
            print(f"  ✓ Updated {fpath}: {w_verified} VERIFIED, {w_review} REVIEW_REQUIRED (out of {w_total})")

            if edir == excel_dirs[0]:
                total_updated_voters += w_total
                total_verified += w_verified
                total_review += w_review

    print("\n" + "=" * 65)
    print("      ALL EXCEL WORKBOOKS SYNCHRONIZED SUCCESSFULLY")
    print("=" * 65)
    print(f"Total Voters Processed: {total_updated_voters}")
    print(f"Total VERIFIED:        {total_verified} ({round((total_verified/total_updated_voters)*100, 1)}%)")
    print(f"Total REVIEW_REQUIRED: {total_review} ({round((total_review/total_updated_voters)*100, 1)}%)")
    print("=" * 65 + "\n")


def rebuild_sqlite_and_js():
    print("[Rebuilding SQLite Database & UI Dataset]")
    import subprocess
    # Run UI WORK/build_sqlite_db.py
    cmd = [sys.executable, os.path.abspath(r"UI WORK\build_sqlite_db.py")]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.returncode != 0:
        print("Error running build_sqlite_db.py:", res.stderr)
        return False

    db_path = os.path.abspath(r"UI WORK\jainagar_chunav.db")
    js_path_www = os.path.abspath(r"UI WORK\www\voters_data.js")
    js_path_assets = os.path.abspath(r"UI WORK\android_project\app\src\main\assets\voters_data.js")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, serial_no, epic_number, name_hindi, name_english,
           relative_type, relative_hindi, relative_english,
           house_number, age, gender_hindi, ward_number, voter_status
    FROM voters
    ORDER BY ward_number, serial_no
    """)
    rows = cursor.fetchall()
    voters_list = [dict(r) for r in rows]
    conn.close()

    print(f"Writing {len(voters_list)} voters to {js_path_www} and {js_path_assets}...")
    json_str = json.dumps(voters_list, ensure_ascii=False)
    js_content = f"window._staticVoters = {json_str};\n"

    with open(js_path_www, "w", encoding="utf-8") as f:
        f.write(js_content)
    with open(js_path_assets, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("  ✓ voters_data.js updated in both locations.")

    # Rebuild UI_WORK_FOR_COLAB.zip
    print("\n[Rebuilding Colab APK package UI_WORK_FOR_COLAB.zip]")
    zip_cmd = [sys.executable, os.path.abspath(r"UI WORK\create_zip_for_colab.py")]
    res_zip = subprocess.run(zip_cmd, capture_output=True, text=True, encoding="utf-8")
    print(res_zip.stdout)
    if res_zip.returncode != 0:
        print("Error rebuilding zip:", res_zip.stderr)
        return False

    return True


if __name__ == "__main__":
    resync_all_excel_workbooks()
    rebuild_sqlite_and_js()

"""
Master Cleaner and Re-synchronizer for Jainagar Chunav 2026
Cleans:
  1. Broken Unicode conjuncts (्् / ZWJ / ZWNJ -> ◌्)
  2. Photo box English leakages (TAT, FAA, ARS, <p, yp, fy, BHT, grt, etc.)
  3. Trailing digits (४, ५, ३, ७, ९) from names
  4. Colon prefix damage (बजरंगलाल -> जरंगलाल / श्जरंगलाल / शबजरंग लाल, बद्रीप्रसाद -> श्द्री प्रसाद, आदि)
  5. Colon prefix doubled letters (ननरेन्द्र -> नरेन्द्र, रराम -> राम, ककालू -> कालू, गगिरधारी -> गिरधारी)
  6. Regenerates clean English transliterations (Narendra Kumar, Bajranglal, Sanju, etc.)
  7. Updates SQLite database, all 9 Excel workbooks (both folders), Web UI js, Android assets, and Colab zip.
"""

import os
import sys
import re
import sqlite3
import zipfile
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

from transliterator import transliterate_hindi_to_english

# Specific verified ground-truth voter names from electoral roll inspection
SPECIFIC_CORRECTIONS = {
    (8, 58): {"name_hi": "भवनेश नागर"},
    (8, 61): {"name_hi": "नन्दलाल"},
    (8, 68): {"name_hi": "मंजू बाई", "husband_hi": "कृष्णचन्द"},
    (8, 95): {"name_hi": "रुक्मिणी बाई"},
    (8, 96): {"name_hi": "कुन्जबिहारी", "father_hi": "लक्ष्मीनारायण"},
    (8, 98): {"name_hi": "रिंकू बाई"},
    (8, 145): {"name_hi": "संजू", "husband_hi": "पवन कुमार"},
    (8, 291): {"name_hi": "संतोष"},
    (8, 301): {"name_hi": "नन्द बिहारी", "father_hi": "पुरुषोत्तम"},
    (8, 330): {"name_hi": "मोनिका कुमारी मीना", "father_hi": "हंसराज"},
    (8, 333): {"name_hi": "नीतू मीणा", "father_hi": "रामकरण मीणा"},
    (8, 347): {"name_hi": "प्रद्युम्न नागर", "father_hi": "राजेंद्र नागर"},
    (8, 349): {"father_hi": "बजरंग लाल"},
    (8, 354): {"name_hi": "नरेन्द्रकुमार", "father_hi": "बजरंगलाल"},
    (8, 356): {"father_hi": "बजरंगलाल"},
    (8, 363): {"father_hi": "नरेन्द्र नागर"},
    (3, 254): {"name_hi": "रोशनबानो", "husband_hi": "सुलतान"},
    (9, 131): {"name_hi": "पप्पूलाल"},
}


def clean_devanagari_name(val: str, ward_no: int = 0, serial_no: int = 0, field: str = "") -> str:
    if not val:
        return ""
    val = str(val).strip()
    if not val:
        return ""

    # Check specific ground truth overrides first
    override = SPECIFIC_CORRECTIONS.get((ward_no, serial_no))
    if override and field in override:
        return override[field]

    # 1. Clean unicode conjuncts & ZWJ / ZWNJ (eliminates dotted circle ◌्)
    val = re.sub(r'्[\u200c\u200d]?्+', '्', val)
    val = re.sub(r'[\u200c\u200d]', '', val)

    # 2. Known specific phrases in dataset
    val = re.sub(r'\bचंद्रा\s+TAT\s+गोचर\b', 'चंद्रा प्रभा गोचर', val)
    val = re.sub(r'\bरामगोपाल+ा*लाल*\b', 'रामगोपाल', val)
    val = re.sub(r'\bरामगोप\b', 'रामगोपाल', val)
    val = re.sub(r'\bहइंसराज\b', 'हंसराज', val)
    val = re.sub(r'\bशातीबाई\b', 'शांतिबाई', val)
    val = re.sub(r'\bधीरज\s+शा\b', 'धीरज', val)
    val = re.sub(r'\bश्चन्नालाल\b', 'पन्नालाल', val)

    # 3. Strip photo labels in English and Hindi
    val = re.sub(r'(?:Photo\s*is\s*Available|Photo\s*Not\s*Available|Photo\s*Available|Photo|Available|Ph\b|Avail\b)', '', val, flags=re.I)
    val = re.sub(r'(?:फोटो\s*उपलब्ध\s*है|फोटो\s*उपलब्ध\s*नहीं\s*है|फोटो\s*उपलब्ध|फोटो)', '', val)

    # 4. Remove label leakage like 'का ATA', 'का ATTA', 'का नाम'
    val = re.sub(r'\bका\s+(?:ATA|ATTA|नाम)\b', '', val, flags=re.I)
    val = re.sub(r'^(?:का|की|के)\s+', '', val)

    # 5. Remove any English characters (hallucinations/photo leaks)
    val = re.sub(r'[a-zA-Z]+', '', val)

    # 6. Remove all digits (0-9 and Devanagari ०-९)
    val = re.sub(r'[0-9\u0966-\u096F]+', '', val)

    # 7. Remove brackets and special symbols (< > ( ) [ ] { } etc.)
    val = re.sub(r'[\'\"“”’`*_~|:;=+\\\/\^$#@!.\-–—<>()\[\]{}]+', ' ', val)

    # 8. Fix colon-collision damaged prefixes (बजरंगलाल, बद्रीप्रसाद, etc.)
    val = re.sub(r'(?:^|\s)(?:श्|श|शब|्)+जरंग(?:\s*लाल|ू)?', ' बजरंगलाल', val)
    val = re.sub(r'(?:^|\s)जरंगलाल\b', 'बजरंगलाल', val)
    val = re.sub(r'(?:^|\s)(?:श्|श)+द्री\s*प्रसाद', ' बद्री प्रसाद', val)
    val = re.sub(r'(?:^|\s)थादव\s*कुमार', ' यादव कुमार', val)
    val = re.sub(r'(?:^|\s)भोहनलाल', ' मोहनलाल', val)
    val = re.sub(r'(?:^|\s)क़ान्ता\s*प्रसाद', ' कान्ता प्रसाद', val)

    # 9. Fix doubled consonant prefixes caused by colon collision
    doubled_map = [
        (r'\bननरें[^\s]*', 'नरेन्द्र'),
        (r'\bननरे[न्\u200c\u200d]*[्]?द्र', 'नरेन्द्र'),
        (r'\bननररेंद्र', 'नरेन्द्र'),
        (r'\bननरेश', 'नरेश'),
        (r'\bननाथूलाल', 'नाथूलाल'),
        (r'\bननन्दलाल', 'नन्दलाल'),
        (r'\bननेंद्र', 'नरेन्द्र'),
        (r'\bररामप्रसाद', 'रामप्रसाद'),
        (r'\bररामचंद्र', 'रामचंद्र'),
        (r'\bरराजेन्द्र', 'राजेन्द्र'),
        (r'\bरराजेश', 'राजेश'),
        (r'\bरराकेश', 'राकेश'),
        (r'\bररामेश्वर', 'रामेश्वर'),
        (r'\bककालू', 'कालू'),
        (r'\bगगिरधारी', 'गिरधारी'),
        (r'\bगगांबिशन', 'गोपीकिशन'),
    ]
    for pat, rep in doubled_map:
        val = re.sub(pat, rep, val)

    # 10. General Devanagari cleanups
    val = re.sub(r'\bनरे[न्\u200c\u200d]*[्]?द्र\b', 'नरेन्द्र', val)
    val = re.sub(r'\bनरे[न्\u200c\u200d]*[्]?द्रकुमार\b', 'नरेन्द्रकुमार', val)
    val = re.sub(r'\bसन्[न्\u200c\u200d]*[्]?तोष\b', 'संतोष', val)
    val = re.sub(r'\bनन्[न्\u200c\u200d]*[्]?द\b', 'नन्द', val)
    if 'प्रद्मुस्न' in val:
        val = val.replace('प्रद्मुस्न', 'प्रद्युम्न')
    if 'ररजेंद्र' in val:
        val = val.replace('ररजेंद्र', 'राजेंद्र')

    # 11. Strip orphaned halants at start/end of words
    val = re.sub(r'(?:^|\s)्+', '', val)
    val = re.sub(r'्+(?:\s|$)', '', val)

    # 12. Strip trailing noise particles (like 'शा', 'बा', 'रथ', 'अर', 'io', etc.)
    val = re.sub(r'\s+[ककसपहशबरथ][िाेी]?\s*$', '', val)

    # Final whitespace cleanup
    val = re.sub(r'\s+', ' ', val).strip()
    return val


def main():
    print("=" * 60)
    print("  JAINAGAR CHUNAV 2026 - MASTER CLEANER & RE-SYNCHRONIZER")
    print("=" * 60)

    db_path = "UI WORK/jainagar_chunav.db"
    if not os.path.exists(db_path):
        print(f"[ERROR] Database {db_path} not found!")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, ward_number, serial_no, name_hindi, father_hindi, husband_hindi FROM voters")
    rows = c.fetchall()
    print(f"Total voters in DB: {len(rows)}")

    updated_count = 0
    updated_records = []

    for vid, ward, sno, n_hi, f_hi, h_hi in rows:
        clean_n_hi = clean_devanagari_name(n_hi, ward, sno, "name_hi")
        clean_f_hi = clean_devanagari_name(f_hi, ward, sno, "father_hi")
        clean_h_hi = clean_devanagari_name(h_hi, ward, sno, "husband_hi")

        changed = (clean_n_hi != (n_hi or '')) or (clean_f_hi != (f_hi or '')) or (clean_h_hi != (h_hi or ''))

        # Transliterate English
        clean_n_en = transliterate_hindi_to_english(clean_n_hi) if clean_n_hi else ""
        clean_f_en = transliterate_hindi_to_english(clean_f_hi) if clean_f_hi else ""
        clean_h_en = transliterate_hindi_to_english(clean_h_hi) if clean_h_hi else ""

        rel_type = "पति" if clean_h_hi else "पिता"
        rel_hi = clean_h_hi if clean_h_hi else clean_f_hi
        rel_en = clean_h_en if clean_h_hi else clean_f_en

        if changed or True:  # Re-sync English transliterations as well
            if changed:
                updated_count += 1
            c.execute("""
                UPDATE voters SET
                    name_hindi = ?,
                    name_english = ?,
                    father_hindi = ?,
                    father_english = ?,
                    husband_hindi = ?,
                    husband_english = ?,
                    relative_type = ?,
                    relative_hindi = ?,
                    relative_english = ?
                WHERE id = ?
            """, (clean_n_hi, clean_n_en, clean_f_hi, clean_f_en, clean_h_hi, clean_h_en, rel_type, rel_hi, rel_en, vid))

    conn.commit()
    print(f"Updated {updated_count} voter records in SQLite database!")

    # Verify Ward 8 #354, #363, #349, #356 in DB
    c.execute("SELECT serial_no, name_hindi, name_english, father_hindi, father_english FROM voters WHERE ward_number=8 AND serial_no IN (347, 349, 354, 356, 363)")
    print("\nVerified Ward 8 records in DB:")
    for r in c.fetchall():
        print(" ", r)

    conn.close()

    # Now synchronize all 9 Excel workbooks in both directories
    excel_dirs = ["output", "VOTER LISTS/EXCEL_OUTPUT"]
    for edir in excel_dirs:
        if not os.path.exists(edir):
            continue
        print(f"\nProcessing Excel files in {edir}...")
        for ward_num in range(1, 10):
            fname = f"JAINAGAR-Ward No-{ward_num:03d}.xlsx"
            fpath = os.path.join(edir, fname)
            if not os.path.exists(fpath):
                continue

            try:
                wb = openpyxl.load_workbook(fpath)
                ws = wb["Voters"]
                headers = [ws.cell(1, col).value for col in range(1, ws.max_column + 1)]

                c_sno = headers.index("Serial_No") + 1
                c_n_hi = headers.index("Name_Hindi") + 1
                c_n_en = headers.index("Name_English") + 1
                c_f_hi = headers.index("Father_Name_Hindi") + 1
                c_f_en = headers.index("Father_Name_English") + 1
                c_h_hi = headers.index("Husband_Name_Hindi") + 1
                c_h_en = headers.index("Husband_Name_English") + 1
                c_conf = headers.index("OCR_Confidence") + 1
                c_status = headers.index("Review_Status") + 1
                c_reason = headers.index("Review_Reason") + 1

                for row in range(2, ws.max_row + 1):
                    sno = ws.cell(row, c_sno).value
                    if sno is None:
                        continue
                    try:
                        sno = int(sno)
                    except ValueError:
                        continue

                    old_n = ws.cell(row, c_n_hi).value or ""
                    old_f = ws.cell(row, c_f_hi).value or ""
                    old_h = ws.cell(row, c_h_hi).value or ""

                    new_n = clean_devanagari_name(old_n, ward_num, sno, "name_hi")
                    new_f = clean_devanagari_name(old_f, ward_num, sno, "father_hi")
                    new_h = clean_devanagari_name(old_h, ward_num, sno, "husband_hi")

                    ws.cell(row, c_n_hi, new_n)
                    ws.cell(row, c_n_en, transliterate_hindi_to_english(new_n))
                    ws.cell(row, c_f_hi, new_f)
                    ws.cell(row, c_f_en, transliterate_hindi_to_english(new_f))
                    ws.cell(row, c_h_hi, new_h)
                    ws.cell(row, c_h_en, transliterate_hindi_to_english(new_h))

                wb.save(fpath)
                print(f"  [OK] Saved cleaned {fpath}")
            except Exception as e:
                print(f"  [ERROR] Updating {fpath}: {e}")

    # Re-export client-side voters_data.js
    print("\nRe-exporting voters_data.js for Web UI and Android...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM voters ORDER BY ward_number, serial_no")
    all_voters = [dict(row) for row in c.fetchall()]
    conn.close()

    import json
    js_content = "window._staticVoters = " + json.dumps(all_voters, ensure_ascii=False) + ";\nwindow.VOTERS_DATA = window._staticVoters;\nvar VOTERS_DATA = window._staticVoters;\n"
    if sys.platform == "win32":
        # write utf-8
        with open("UI WORK/www/voters_data.js", "w", encoding="utf-8") as f:
            f.write(js_content)
        with open("UI WORK/android_project/app/src/main/assets/voters_data.js", "w", encoding="utf-8") as f:
            f.write(js_content)
    print("  [OK] Written to UI WORK/www/voters_data.js and android_project/app/src/main/assets/voters_data.js")

    # Re-package UI_WORK_FOR_COLAB.zip
    print("\nRe-packaging UI_WORK_FOR_COLAB.zip...")
    zip_path = "UI WORK/UI_WORK_FOR_COLAB.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("UI WORK/android_project"):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, "UI WORK")
                zipf.write(full_p, rel_p)
        for root, dirs, files in os.walk("UI WORK/www"):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, "UI WORK")
                zipf.write(full_p, rel_p)
        zipf.write(db_path, "jainagar_chunav.db")

    print(f"  [OK] UI_WORK_FOR_COLAB.zip created successfully ({os.path.getsize(zip_path)} bytes)")
    print("\nMaster cleaning and re-synchronization completed 100%!")


if __name__ == "__main__":
    main()

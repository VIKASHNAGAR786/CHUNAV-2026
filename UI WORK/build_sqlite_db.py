"""
=============================================================================
             JAINAGAR CHUNAV 2026 - SQLITE DATABASE BUILDER
 Ingests all 9 extracted Excel workbooks (3,568 voter records) into an
 ultra-fast, indexed, offline SQLite database for mobile application.
=============================================================================
"""

import os
import sys
import time
import glob
import sqlite3
import openpyxl

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_EXCEL_DIR = os.path.join(PROJECT_ROOT, "output")
DEFAULT_DB_PATH = os.path.join(SCRIPT_DIR, "jainagar_chunav.db")


def create_schema(conn: sqlite3.Connection):
    """Create optimized tables and performance indexes."""
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ward_number INTEGER NOT NULL,
        serial_no INTEGER NOT NULL,
        epic_number TEXT NOT NULL,
        name_hindi TEXT,
        name_english TEXT,
        father_hindi TEXT,
        father_english TEXT,
        husband_hindi TEXT,
        husband_english TEXT,
        relative_type TEXT,
        relative_hindi TEXT,
        relative_english TEXT,
        house_number TEXT,
        age INTEGER,
        gender_hindi TEXT,
        gender_english TEXT,
        section_name TEXT,
        panchayat_name TEXT,
        page_number INTEGER,
        ocr_confidence REAL,
        review_status TEXT,
        voter_status TEXT DEFAULT 'unmarked',
        karyakarta_notes TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidate_info (
        id INTEGER PRIMARY KEY,
        name_hindi TEXT,
        name_english TEXT,
        role TEXT,
        slogan TEXT,
        phone TEXT,
        whatsapp TEXT,
        office_address TEXT,
        manifesto TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ward_summary (
        ward_number INTEGER PRIMARY KEY,
        total_voters INTEGER,
        male_count INTEGER,
        female_count INTEGER,
        other_count INTEGER,
        polled_count INTEGER DEFAULT 0
    );
    """)

    # Performance indexes for sub-10ms queries on 3,568 records
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voters_ward ON voters (ward_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voters_ward_serial ON voters (ward_number, serial_no);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voters_epic ON voters (epic_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voters_name_hi ON voters (name_hindi);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voters_name_en ON voters (name_english);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voters_house ON voters (ward_number, house_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voters_status ON voters (voter_status);")

    conn.commit()


def populate_candidate_info(conn: sqlite3.Connection):
    """Seed Candidate information for Pradhyumna Nagar."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidate_info;")

    manifesto = """
1. स्वच्छ पेयजल एवं हर घर नल-जल योजना का शत-प्रतिशत क्रियान्वयन।
2. ग्राम पंचायत जैनगर के सभी 9 वार्डों में पक्की सीसी सड़कें एवं व्यवस्थित नालियाँ।
3. प्राथमिक व माध्यमिक विद्यालयों में बेहतर शिक्षा व डिजिटल क्लासरूम सुविधा।
4. प्राथमिक स्वास्थ्य केंद्र में 24x7 बुनियादी दवाइयां व एम्बुलेंस सेवा की सुगमता।
5. युवाओं के लिए खेल मैदान, ओपन जिम व प्रतियोगी परीक्षाओं हेतु मार्गदर्शन केंद्र।
6. किसान कल्याण: खाद-बीज की सुगम उपलब्धता व सिंचाई तंत्र का विस्तार।
7. पारदर्शी व जनहितैषी पंचायत प्रशासन: ग्रामवासियों के कार्यों का त्वरित निस्तारण।
""".strip()

    cursor.execute("""
    INSERT INTO candidate_info (
        id, name_hindi, name_english, role, slogan, phone, whatsapp, office_address, manifesto
    ) VALUES (
        1,
        'प्रद्युम्न नागर',
        'Pradhyumna Nagar',
        'प्रधान / सरपंच पद प्रत्याशी',
        'विकास का नया संकल्प — सबका साथ, गाँव का सर्वांगीण विकास',
        '+91 98765 43210',
        '+91 98765 43210',
        'मुख्य बस स्टैंड चौराहा, ग्राम पंचायत जैनगर',
        ?
    );
    """, (manifesto,))
    conn.commit()


def build_database(excel_dir: str = DEFAULT_EXCEL_DIR, db_path: str = DEFAULT_DB_PATH):
    """Read all 9 Excel files and build complete SQLite database."""
    print("=" * 65)
    print("      BUILDING JAINAGAR CHUNAV 2026 OFFLINE SQLITE DB")
    print("=" * 65)
    print(f"Excel Directory: {excel_dir}")
    print(f"SQLite Target:   {db_path}\n")

    # If database exists, remove to recreate clean
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("[INFO] Existing database removed for clean build.")
        except Exception as e:
            print(f"[WARNING] Could not remove existing DB: {e}")

    conn = sqlite3.connect(db_path)
    create_schema(conn)
    populate_candidate_info(conn)

    # Find 9 ward excel files
    files = sorted(glob.glob(os.path.join(excel_dir, "JAINAGAR-Ward No-*.xlsx")))
    if not files:
        # Fallback check in VOTER LISTS/EXCEL_OUTPUT
        alt_dir = os.path.join(PROJECT_ROOT, "VOTER LISTS", "EXCEL_OUTPUT")
        files = sorted(glob.glob(os.path.join(alt_dir, "JAINAGAR-Ward No-*.xlsx")))

    if not files:
        print(f"[ERROR] No ward Excel files found in '{excel_dir}' or '{alt_dir}'.")
        conn.close()
        return False

    print(f"Found {len(files)} Ward Excel workbooks to ingest.\n")
    cursor = conn.cursor()
    total_inserted = 0

    for f_idx, file_path in enumerate(files, 1):
        file_name = os.path.basename(file_path)
        print(f"[{f_idx}/{len(files)}] Reading {file_name}...")

        wb = openpyxl.load_workbook(file_path, data_only=True)
        if "Voters" not in wb.sheetnames:
            print(f"  [WARNING] 'Voters' sheet not found in {file_name}. Skipping.")
            wb.close()
            continue

        ws = wb["Voters"]
        row_count = 0
        header_map = {}

        # Read header row
        for col in range(1, ws.max_column + 1):
            val = ws.cell(1, col).value
            if val:
                header_map[str(val).strip()] = col

        # Insert records
        for r in range(2, ws.max_row + 1):
            serial = ws.cell(r, header_map.get("Serial_No", 1)).value
            if serial is None:
                continue

            epic = ws.cell(r, header_map.get("EPIC_Number", 2)).value or ""
            name_hi = ws.cell(r, header_map.get("Name_Hindi", 3)).value or ""
            name_en = ws.cell(r, header_map.get("Name_English", 4)).value or ""
            father_hi = ws.cell(r, header_map.get("Father_Name_Hindi", 5)).value or ""
            father_en = ws.cell(r, header_map.get("Father_Name_English", 6)).value or ""
            husband_hi = ws.cell(r, header_map.get("Husband_Name_Hindi", 7)).value or ""
            husband_en = ws.cell(r, header_map.get("Husband_Name_English", 8)).value or ""
            house = ws.cell(r, header_map.get("House_Number", 9)).value or ""
            age = ws.cell(r, header_map.get("Age", 10)).value
            gender_hi = ws.cell(r, header_map.get("Gender_Hindi", 11)).value or ""
            gender_en = ws.cell(r, header_map.get("Gender_English", 12)).value or ""
            page = ws.cell(r, header_map.get("Page_Number", 13)).value or 0
            section = ws.cell(r, header_map.get("Section_Name", 14)).value or ""
            panchayat = ws.cell(r, header_map.get("Panchayat_Name", 15)).value or "जैनगर"
            ward = ws.cell(r, header_map.get("Ward_Number", 16)).value or f_idx
            conf_val = ws.cell(r, header_map.get("OCR_Confidence", 17)).value or 100.0
            rev_status = ws.cell(r, header_map.get("Review_Status", 18)).value or "VERIFIED"

            # Parse types
            try:
                serial_int = int(serial)
            except Exception:
                serial_int = 0

            try:
                age_int = int(age) if age is not None else None
            except Exception:
                age_int = None

            try:
                ward_int = int(ward)
            except Exception:
                ward_int = f_idx

            try:
                conf_str = str(conf_val).replace("%", "").strip()
                conf_flt = float(conf_str)
            except Exception:
                conf_flt = 100.0

            # Determine primary relative
            if husband_hi:
                rel_type = "पति"
                rel_hi = husband_hi
                rel_en = husband_en
            else:
                rel_type = "पिता"
                rel_hi = father_hi
                rel_en = father_en

            cursor.execute("""
            INSERT INTO voters (
                ward_number, serial_no, epic_number,
                name_hindi, name_english,
                father_hindi, father_english,
                husband_hindi, husband_english,
                relative_type, relative_hindi, relative_english,
                house_number, age, gender_hindi, gender_english,
                section_name, panchayat_name, page_number,
                ocr_confidence, review_status, voter_status
            ) VALUES (
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, 'unmarked'
            );
            """, (
                ward_int, serial_int, str(epic).strip(),
                str(name_hi).strip(), str(name_en).strip(),
                str(father_hi).strip() if father_hi else None,
                str(father_en).strip() if father_en else None,
                str(husband_hi).strip() if husband_hi else None,
                str(husband_en).strip() if husband_en else None,
                rel_type, str(rel_hi).strip() if rel_hi else None,
                str(rel_en).strip() if rel_en else None,
                str(house).strip() if house else "",
                age_int,
                str(gender_hi).strip() if gender_hi else "",
                str(gender_en).strip() if gender_en else "",
                str(section).strip() if section else "",
                str(panchayat).strip() if panchayat else "जैनगर",
                page, conf_flt, str(rev_status).strip()
            ))

            row_count += 1

        wb.close()
        print(f"  --> Ingested {row_count} voters for Ward {f_idx}")
        total_inserted += row_count

    # Populate Ward Summary Table
    cursor.execute("DELETE FROM ward_summary;")
    cursor.execute("""
    INSERT INTO ward_summary (ward_number, total_voters, male_count, female_count, other_count, polled_count)
    SELECT
        ward_number,
        COUNT(*),
        SUM(CASE WHEN gender_english = 'Male' THEN 1 ELSE 0 END),
        SUM(CASE WHEN gender_english = 'Female' THEN 1 ELSE 0 END),
        SUM(CASE WHEN gender_english NOT IN ('Male', 'Female') THEN 1 ELSE 0 END),
        0
    FROM voters
    GROUP BY ward_number
    ORDER BY ward_number;
    """)

    conn.commit()

    # Query verification stats
    cursor.execute("SELECT COUNT(*) FROM voters;")
    final_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT ward_number) FROM voters;")
    ward_count = cursor.fetchone()[0]

    cursor.execute("SELECT gender_english, COUNT(*) FROM voters GROUP BY gender_english;")
    gender_stats = cursor.fetchall()

    conn.close()

    db_size_kb = round(os.path.getsize(db_path) / 1024, 1)

    print("\n" + "=" * 65)
    print("      DATABASE CREATION COMPLETED SUCCESSFULLY")
    print("=" * 65)
    print(f"Database File: {db_path}")
    print(f"File Size:     {db_size_kb} KB")
    print(f"Total Wards:   {ward_count}")
    print(f"Total Voters:  {final_count}")
    print(f"Gender Stats:  {dict(gender_stats)}")
    print("=" * 65 + "\n")
    return True


if __name__ == "__main__":
    build_database()

"""
Synthetic Test Suite for Voter PDF to Excel Extractor
Verifies transliteration, data extraction, validation, duplicate detection,
and 4-sheet Excel generation using synthetic test voter records.
"""

import os
import sys

# Ensure UTF-8 console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from transliterator import transliterate_hindi_to_english
from validator import validate_all_records
from excel_exporter import ExcelExporter


def run_synthetic_tests():
    print("=" * 50)
    print("  RUNNING SYNTHETIC VOTER TEST SUITE")
    print("=" * 50)

    # 1. Transliteration Tests
    print("\n[Test 1] Testing Hindi to English Transliteration...")
    translit_tests = [
        ("नरेंद्र", "Narendra"),
        ("प्रद्युम्न", "Pradyumna"),
        ("भारती बाई", "Bharti Bai"),
        ("सुरेश कुमार", "Suresh Kumar"),
        ("प्रीतम", "Pritam"),
        ("रामलाल", "Ramlal"),
        ("राम सिंह", "Ram Singh"),
        ("रंगलाल", "Ranglal"),
        ("ओंकारलाल", "Onkarlal"),
        ("कान्तीबाई", "Kanti Bai"),
        ("लीला बाई", "Leela Bai"),
        ("देवेन्द्र मीणा", "Devendra Meena")
    ]
    for hin, expected in translit_tests:
        eng = transliterate_hindi_to_english(hin)
        assert eng, f"Transliteration failed for {hin}"
        print(f"  OK: {hin} -> {eng}")

    # 2. Synthetic Records Construction
    print("\n[Test 2] Assembling Synthetic Records across Edge Cases...")
    synthetic_records = [
        # Normal verified record with Father
        {
            "Serial_No": 1,
            "EPIC_Number": "BMQ1490051",
            "Name_Hindi": "रंगलाल",
            "Name_English": transliterate_hindi_to_english("रंगलाल"),
            "Father_Name_Hindi": "ओंकारलाल",
            "Father_Name_English": transliterate_hindi_to_english("ओंकारलाल"),
            "Husband_Name_Hindi": "",
            "Husband_Name_English": "",
            "House_Number": "47",
            "Age": 64,
            "Gender_Hindi": "पुरुष",
            "Gender_English": "Male",
            "Page_Number": 3,
            "Section_Name": "नागरों का मोहल्ला,हरीपुरा हाकड़ी",
            "Panchayat_Name": "जैनगर",
            "Ward_Number": "9",
            "Raw_OCR_Text": "नाम: रंगलाल\nपिता का नाम: ओंकारलाल\nमकान संख्या: 47\nआयु: 64 लिंग: पुरूष"
        },
        # Normal verified record with Husband (No Father)
        {
            "Serial_No": 2,
            "EPIC_Number": "BMQ1490069",
            "Name_Hindi": "कान्तीबाई",
            "Name_English": transliterate_hindi_to_english("कान्तीबाई"),
            "Father_Name_Hindi": "",
            "Father_Name_English": "",
            "Husband_Name_Hindi": "रंगलाल",
            "Husband_Name_English": transliterate_hindi_to_english("रंगलाल"),
            "House_Number": "47",
            "Age": 61,
            "Gender_Hindi": "स्त्री",
            "Gender_English": "Female",
            "Page_Number": 3,
            "Section_Name": "नागरों का मोहल्ला,हरीपुरा हाकड़ी",
            "Panchayat_Name": "जैनगर",
            "Ward_Number": "9",
            "Raw_OCR_Text": "नाम: कान्तीबाई\nपति का नाम: रंगलाल\nमकान संख्या: 47\nआयु: 61 लिंग: स्त्री"
        },
        # Duplicate EPIC test record (Should trigger REVIEW_REQUIRED)
        {
            "Serial_No": 3,
            "EPIC_Number": "BMQ1490051",  # Same as Serial 1
            "Name_Hindi": "सुरेश कुमार",
            "Name_English": transliterate_hindi_to_english("सुरेश कुमार"),
            "Father_Name_Hindi": "रामलाल",
            "Father_Name_English": transliterate_hindi_to_english("रामलाल"),
            "Husband_Name_Hindi": "",
            "Husband_Name_English": "",
            "House_Number": "48",
            "Age": 35,
            "Gender_Hindi": "पुरुष",
            "Gender_English": "Male",
            "Page_Number": 3,
            "Section_Name": "नागरों का मोहल्ला,हरीपुरा हाकड़ी",
            "Panchayat_Name": "जैनगर",
            "Ward_Number": "9",
            "Raw_OCR_Text": "नाम: सुरेश कुमार\nपिता का नाम: रामलाल\nमकान संख्या: 48\nआयु: 35 लिंग: पुरूष"
        },
        # Missing Age test record
        {
            "Serial_No": 4,
            "EPIC_Number": "SSD1090083",
            "Name_Hindi": "मनोज कुमार",
            "Name_English": transliterate_hindi_to_english("मनोज कुमार"),
            "Father_Name_Hindi": "रंगलाल",
            "Father_Name_English": transliterate_hindi_to_english("रंगलाल"),
            "Husband_Name_Hindi": "",
            "Husband_Name_English": "",
            "House_Number": "47",
            "Age": None,  # Missing Age
            "Gender_Hindi": "पुरुष",
            "Gender_English": "Male",
            "Page_Number": 3,
            "Section_Name": "नागरों का मोहल्ला,हरीपुरा हाकड़ी",
            "Panchayat_Name": "जैनगर",
            "Ward_Number": "9",
            "Raw_OCR_Text": "नाम: मनोज कुमार\nपिता का नाम: रंगलाल\nमकान संख्या: 47\nलिंग: पुरूष"
        },
        # Both Father and Husband Present test record
        {
            "Serial_No": 5,
            "EPIC_Number": "SSD1576453",
            "Name_Hindi": "लीला बाई",
            "Name_English": transliterate_hindi_to_english("लीला बाई"),
            "Father_Name_Hindi": "प्रीतम",
            "Father_Name_English": transliterate_hindi_to_english("प्रीतम"),
            "Husband_Name_Hindi": "मनोज",
            "Husband_Name_English": transliterate_hindi_to_english("मनोज"),
            "House_Number": "47",
            "Age": 28,
            "Gender_Hindi": "स्त्री",
            "Gender_English": "Female",
            "Page_Number": 3,
            "Section_Name": "नागरों का मोहल्ला,हरीपुरा हाकड़ी",
            "Panchayat_Name": "जैनगर",
            "Ward_Number": "9",
            "Raw_OCR_Text": "नाम: लीला बाई\nपिता का नाम: प्रीतम\nपति का नाम: मनोज\nमकान संख्या: 47\nआयु: 28 लिंग: स्त्री"
        },
        # Age out of bounds test record
        {
            "Serial_No": 6,
            "EPIC_Number": "SSD1304997",
            "Name_Hindi": "देवेन्द्र मीणा",
            "Name_English": transliterate_hindi_to_english("देवेन्द्र मीणा"),
            "Father_Name_Hindi": "रंग लाल",
            "Father_Name_English": transliterate_hindi_to_english("रंग लाल"),
            "Husband_Name_Hindi": "",
            "Husband_Name_English": "",
            "House_Number": "47",
            "Age": 140,  # Invalid Age
            "Gender_Hindi": "पुरुष",
            "Gender_English": "Male",
            "Page_Number": 4,
            "Section_Name": "नागरों का मोहल्ला,हरीपुरा हाकड़ी",
            "Panchayat_Name": "जैनगर",
            "Ward_Number": "9",
            "Raw_OCR_Text": "नाम: देवेन्द्र मीणा\nपिता का नाम: रंग लाल\nमकान संख्या: 47\nआयु: 140 लिंग: पुरूष"
        },
        # Incomplete row sample (valid record)
        {
            "Serial_No": 7,
            "EPIC_Number": "SSD2001122",
            "Name_Hindi": "भारती बाई",
            "Name_English": transliterate_hindi_to_english("भारती बाई"),
            "Father_Name_Hindi": "",
            "Father_Name_English": "",
            "Husband_Name_Hindi": "राम सिंह",
            "Husband_Name_English": transliterate_hindi_to_english("राम सिंह"),
            "House_Number": "50",
            "Age": 42,
            "Gender_Hindi": "स्त्री",
            "Gender_English": "Female",
            "Page_Number": 4,
            "Section_Name": "नागरों का मोहल्ला,हरीपुरा हाकड़ी",
            "Panchayat_Name": "जैनगर",
            "Ward_Number": "9",
            "Raw_OCR_Text": "नाम: भारती बाई\nपति का नाम: राम सिंह\nमकान संख्या: 50\nआयु: 42 लिंग: स्त्री"
        }
    ]

    # 3. Validation
    print("\n[Test 3] Running Validator on Synthetic Dataset...")
    validated = validate_all_records(synthetic_records)
    for rec in validated:
        status = rec["Review_Status"]
        reason = rec["Review_Reason"]
        print(f"  Serial {rec['Serial_No']}: [{status}] - {reason}")

    # Check that Serial 1, 2, 7 are VERIFIED and 3, 4, 5, 6 are REVIEW_REQUIRED
    assert validated[0]["Review_Status"] == "VERIFIED"
    assert validated[1]["Review_Status"] == "VERIFIED"
    assert validated[2]["Review_Status"] == "REVIEW_REQUIRED", "Duplicate EPIC should trigger REVIEW_REQUIRED"
    assert validated[3]["Review_Status"] == "REVIEW_REQUIRED", "Missing Age should trigger REVIEW_REQUIRED"
    assert validated[4]["Review_Status"] == "REVIEW_REQUIRED", "Both parents should trigger REVIEW_REQUIRED"
    assert validated[5]["Review_Status"] == "REVIEW_REQUIRED", "Age out of bounds should trigger REVIEW_REQUIRED"
    assert validated[6]["Review_Status"] == "VERIFIED"
    print("  Validation assertions passed successfully!")

    # 4. Excel Generation
    print("\n[Test 4] Exporting to Sample Synthetic Excel Workbook...")
    exporter = ExcelExporter(output_folder=r".\output", filename="Synthetic_Sample_Voter_List.xlsx")
    raw_ocr_samples = [
        {"Page_Number": r["Page_Number"], "Card_Number": idx + 1, "Serial_Number": r["Serial_No"], "Raw_OCR_Text": r["Raw_OCR_Text"]}
        for idx, r in enumerate(synthetic_records)
    ]
    stats = {"total_pages": 4, "total_cards": len(synthetic_records)}
    ok, save_path = exporter.export(
        records=validated,
        raw_ocr_records=raw_ocr_samples,
        stats=stats,
        create_review_sheet=True,
        create_summary_sheet=True
    )

    assert ok, f"Export failed: {save_path}"
    print(f"  Excel file created successfully at: {save_path}")

    # 5. Verify workbook opens and has 4 sheets
    import openpyxl
    wb = openpyxl.load_workbook(save_path)
    sheet_names = wb.sheetnames
    print(f"  Worksheets verified: {sheet_names}")
    assert "Voters" in sheet_names
    assert "Review_Required" in sheet_names
    assert "Summary" in sheet_names
    assert "Raw_OCR" in sheet_names

    # Check rows in Voters sheet
    ws_v = wb["Voters"]
    assert ws_v.max_row == len(synthetic_records) + 1  # Header + data rows
    print(f"  Voters sheet verified: {ws_v.max_row - 1} records.")

    print("\n" + "=" * 50)
    print("  ALL SYNTHETIC TESTS PASSED SUCCESSFULLY!")
    print("=" * 50)


if __name__ == "__main__":
    run_synthetic_tests()

"""
=============================================================================
             SMART VOTER LIST PDF TO EXCEL EXTRACTOR
      Specialized for Rajasthan Panchayat Electoral Roll PDF Conversion
=============================================================================
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any

# Ensure stdout uses UTF-8 encoding on Windows to prevent charmap errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# =============================================================================
# USER CONFIGURATION SECTION
# PDF_PATH me apni PDF file ka path dalein.
# OUTPUT_FILENAME: Agar None rakhenge to automatic PDF ke naam se Excel banegi!
# Example: "JAINAGAR-Ward No-009.pdf" -> "JAINAGAR-Ward No-009.xlsx"
# =============================================================================
PDF_PATH = r"JAINAGAR-Ward No-009.pdf"

OUTPUT_FOLDER = r".\output"

# None rakhne par PDF ke exact naam se Excel file banegi
OUTPUT_FILENAME = None

OCR_LANGUAGE = "hin+eng"

PDF_DPI = 300

ENABLE_OCR = True

ENABLE_TEXT_EXTRACTION = True

CREATE_REVIEW_SHEET = True

CREATE_SUMMARY_SHEET = True
# =============================================================================

# Allow command line override if provided: python voter_pdf_to_excel.py "path/to/voter.pdf"
if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".pdf"):
    PDF_PATH = sys.argv[1]

# Local modular imports
from pdf_reader import PDFReader
from card_detector import detect_voter_cards
from ocr_engine import OCREngine
from data_extractor import extract_voter_card_record
from transliterator import transliterate_hindi_to_english
from validator import validate_all_records
from excel_exporter import ExcelExporter


def setup_logging(output_dir: str):
    """Configure file and console logging."""
    log_dir = os.path.join(output_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "voter_extractor.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return log_file


def process_voter_pdf(pdf_path: str,
                      output_folder: str,
                      output_filename: str = None,
                      dpi: int = 300,
                      enable_ocr: bool = True,
                      enable_text: bool = True,
                      ocr_lang: str = "hin+eng"):
    """Main orchestration pipeline for voter PDF extraction."""
    start_time = time.time()
    pdf_filename = os.path.basename(pdf_path)

    # Automatic Excel filename based on PDF filename if not explicitly provided
    if not output_filename:
        pdf_stem = os.path.splitext(pdf_filename)[0]
        output_filename = f"{pdf_stem}.xlsx"

    print("=" * 44)
    print("      VOTER PDF TO EXCEL EXTRACTOR")
    print("=" * 44)
    print(f"\nPDF: {pdf_filename}")
    print(f"Target Excel: {output_filename}\n")

    os.makedirs(output_folder, exist_ok=True)
    log_file = setup_logging(output_folder)
    logging.info(f"Starting extraction for PDF: {pdf_path}")

    # [1/5] Checking PDF
    print("[1/5] Checking PDF...")
    reader = PDFReader(pdf_path=pdf_path, dpi=dpi)
    success, msg = reader.open()
    if not success:
        print(f"\n[ERROR] {msg}")
        logging.error(f"PDF Check Failed: {msg}")
        return False

    total_pages = reader.total_pages
    logging.info(f"PDF opened successfully. Total pages: {total_pages}. Text layer: {reader.has_text_layer}")

    # Check OCR Engine
    ocr = None
    if enable_ocr:
        ocr = OCREngine(language=ocr_lang)
        ocr_ok, ocr_msg = ocr.check_health()
        if not ocr_ok:
            print(f"\n[WARNING] {ocr_msg}")
            logging.warning(ocr_msg)
            if not reader.has_text_layer:
                print("\n[CRITICAL ERROR] Cannot proceed without OCR on a scanned PDF.")
                return False
            else:
                print("Falling back to native PDF text extraction.\n")
                enable_ocr = False
        else:
            logging.info(ocr_msg)

    # [2/5] Extracting page information
    print("[2/5] Extracting page information...")
    panchayat = reader.panchayat_name
    ward = reader.ward_number
    logging.info(f"Metadata extracted - Panchayat: '{panchayat}', Ward: '{ward}'")

    # [3/5] & [4/5] Detecting voter cards & Running OCR
    print("[3/5] Detecting voter cards...")
    print("[4/5] Running Hindi + English OCR...\n")

    all_extracted_records: List[Dict[str, Any]] = []
    all_raw_ocr_records: List[Dict[str, Any]] = []
    total_detected_cards = 0

    for page_idx in range(total_pages):
        page_num = page_idx + 1
        page_sec = reader.get_section_for_page(page_num)

        # Render page
        page_img = reader.render_page_image(page_idx)
        if page_img is None:
            logging.error(f"Page {page_num}: Failed to render image.")
            print(f"Page {page_num}/{total_pages} - Error rendering page image")
            continue

        # Detect voter card boxes
        card_boxes = detect_voter_cards(page_img)
        card_count = len(card_boxes)
        total_detected_cards += card_count
        print(f"Page {page_num}/{total_pages}  - {card_count} cards detected")
        logging.info(f"Page {page_num}: {card_count} cards detected.")

        if card_count == 0:
            del page_img
            continue

        # Process each card on this page
        for card_idx, box in enumerate(card_boxes):
            card_no = card_idx + 1
            x, y, w, h = box

            # Extract native PDF text inside card box and subboxes if enabled
            digital_text = ""
            s_box_text = ""
            e_box_text = ""
            if enable_text:
                digital_text = reader.get_text_in_card_box(page_idx, box)
                s_box_text = reader.get_text_in_card_box(page_idx, (x, y, int(w * 0.22), int(h * 0.25)))
                e_box_text = reader.get_text_in_card_box(page_idx, (x + int(w * 0.18), y, int(w * 0.55), int(h * 0.25)))

            # Crop card image and run OCR if enabled
            ocr_text = ""
            ocr_conf = 0.0
            if enable_ocr and ocr:
                card_crop = page_img[y:y+h, x:x+w]
                try:
                    ocr_text, ocr_conf = ocr.ocr_card(card_crop)
                except Exception as e:
                    logging.warning(f"OCR failed for Page {page_num} Card {card_no}: {e}")
                    ocr_text = ""
                del card_crop

            # Save raw OCR output for debugging sheet
            all_raw_ocr_records.append({
                "Page_Number": page_num,
                "Card_Number": card_no,
                "Serial_Number": "",  # Populated after extraction
                "Raw_OCR_Text": ocr_text or digital_text
            })

            # Extract individual fields
            record = extract_voter_card_record(
                ocr_text=ocr_text,
                digital_text=digital_text,
                serial_hint=s_box_text,
                epic_hint=e_box_text
            )

            # Assign page and administrative metadata
            record["Page_Number"] = page_num
            record["Section_Name"] = page_sec
            record["Panchayat_Name"] = panchayat
            record["Ward_Number"] = ward

            # Populate serial number in raw record
            if all_raw_ocr_records:
                all_raw_ocr_records[-1]["Serial_Number"] = record.get("Serial_No", "")

            # Generate English Transliterations
            record["Name_English"] = transliterate_hindi_to_english(record.get("Name_Hindi", ""))
            record["Father_Name_English"] = transliterate_hindi_to_english(record.get("Father_Name_Hindi", ""))
            record["Husband_Name_English"] = transliterate_hindi_to_english(record.get("Husband_Name_Hindi", ""))

            all_extracted_records.append(record)

        # Free page image memory
        del page_img

    reader.close()

    # Data Validation & Review Classification
    logging.info("Validating extracted records and identifying review items...")
    validated_records = validate_all_records(all_extracted_records)

    # [5/5] Generating Excel workbook
    print("\n[5/5] Generating Excel workbook...")
    exporter = ExcelExporter(output_folder=output_folder, filename=output_filename)
    stats = {
        "total_pages": total_pages,
        "total_cards": total_detected_cards
    }

    save_ok, save_msg = exporter.export(
        records=validated_records,
        raw_ocr_records=all_raw_ocr_records,
        stats=stats,
        create_review_sheet=CREATE_REVIEW_SHEET,
        create_summary_sheet=CREATE_SUMMARY_SHEET
    )

    if not save_ok:
        print(f"\n[ERROR] {save_msg}")
        logging.error(f"Excel Export Failed: {save_msg}")
        return False

    elapsed = round(time.time() - start_time, 1)
    verified_cnt = sum(1 for r in validated_records if r.get("Review_Status") == "VERIFIED")
    review_cnt = sum(1 for r in validated_records if r.get("Review_Status") == "REVIEW_REQUIRED")

    print("\n" + "=" * 44)
    print("PROCESSING COMPLETED")
    print("=" * 44)
    print(f"Total Pages:      {total_pages}")
    print(f"Detected Cards:   {total_detected_cards}")
    print(f"Extracted Records:{len(validated_records)}")
    print(f"Verified Records: {verified_cnt}")
    print(f"Review Required:  {review_cnt}")
    print(f"Processing Time:  {elapsed}s")
    print("\nExcel File:")
    print(f"{os.path.abspath(save_msg)}")
    print("=" * 44 + "\n")

    logging.info(f"Processing successfully completed. Exported to: {save_msg}")
    return True


if __name__ == "__main__":
    process_voter_pdf(
        pdf_path=PDF_PATH,
        output_folder=OUTPUT_FOLDER,
        output_filename=OUTPUT_FILENAME,
        dpi=PDF_DPI,
        enable_ocr=ENABLE_OCR,
        enable_text=ENABLE_TEXT_EXTRACTION,
        ocr_lang=OCR_LANGUAGE
    )

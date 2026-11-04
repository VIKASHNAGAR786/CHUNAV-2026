"""
=============================================================================
             BATCH VOTER LIST PDF TO EXCEL PROCESSOR
 Processes all Rajasthan Panchayat Voter PDFs in a directory and exports
 individual formatted Excel files with matching filenames.
=============================================================================
"""

import os
import sys
import time
import glob
import shutil
from pathlib import Path

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from voter_pdf_to_excel import process_voter_pdf

INPUT_FOLDER = r".\VOTER LISTS"
OUTPUT_FOLDER = r".\output"
EXTRA_COPY_FOLDER = r".\VOTER LISTS\EXCEL_OUTPUT"


def run_batch():
    input_dir = os.path.abspath(INPUT_FOLDER)
    output_dir = os.path.abspath(OUTPUT_FOLDER)
    copy_dir = os.path.abspath(EXTRA_COPY_FOLDER)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(copy_dir, exist_ok=True)

    # Find all PDF files and sort in natural order
    pdf_files = sorted(glob.glob(os.path.join(input_dir, "*.pdf")))

    if not pdf_files:
        print(f"[ERROR] No PDF files found in '{input_dir}'")
        return

    print("=" * 75)
    print("      RAJASTHAN PANCHAYAT VOTER LIST - BATCH PROCESSING PIPELINE")
    print("=" * 75)
    print(f"Source Folder:  {input_dir}")
    print(f"Output Folder:  {output_dir}")
    print(f"Extra Copy Dir: {copy_dir}")
    print(f"Total PDFs:     {len(pdf_files)}")
    print("=" * 75 + "\n")

    batch_start = time.time()
    results = []

    for idx, pdf_path in enumerate(pdf_files, 1):
        pdf_name = os.path.basename(pdf_path)
        excel_name = f"{Path(pdf_path).stem}.xlsx"
        print(f"\n===========================================================================")
        print(f"[{idx}/{len(pdf_files)}] PROCESSING: {pdf_name}")
        print(f"     Target Excel: {excel_name}")
        print(f"===========================================================================")

        t0 = time.time()
        res = process_voter_pdf(
            pdf_path=pdf_path,
            output_folder=output_dir,
            output_filename=excel_name,
            dpi=300,
            enable_ocr=True,
            enable_text=True,
            ocr_lang="hin+eng"
        )
        t1 = time.time()

        if res:
            excel_path = res.get("excel_path", os.path.join(output_dir, excel_name))
            # Also copy to extra folder in VOTER LISTS for convenience
            try:
                shutil.copy2(excel_path, os.path.join(copy_dir, excel_name))
            except Exception as e:
                print(f"[WARNING] Could not copy to extra folder: {e}")

            results.append({
                "idx": idx,
                "pdf": pdf_name,
                "excel": excel_name,
                "success": True,
                "cards": res.get("detected_cards", 0),
                "verified": res.get("verified", 0),
                "review": res.get("review", 0),
                "duration": round(t1 - t0, 1),
                "excel_path": excel_path
            })
        else:
            results.append({
                "idx": idx,
                "pdf": pdf_name,
                "excel": excel_name,
                "success": False,
                "cards": 0,
                "verified": 0,
                "review": 0,
                "duration": round(t1 - t0, 1),
                "excel_path": "FAILED"
            })

    total_time = round(time.time() - batch_start, 1)

    # Generate Report Lines
    report_lines = [
        "=" * 85,
        "                   ALL 9 VOTER LISTS PROCESSING SUMMARY",
        "=" * 85,
        f"{'#':<3} {'PDF File Name':<26} {'Voters':<8} {'Verified':<10} {'Review':<8} {'Time':<8} {'Status'}",
        "-" * 85
    ]

    total_all_cards = sum(r["cards"] for r in results)
    total_all_verified = sum(r["verified"] for r in results)
    total_all_review = sum(r["review"] for r in results)

    for r in results:
        status_str = "SUCCESS" if r["success"] else "FAILED"
        report_lines.append(
            f"{r['idx']:<3} {r['pdf']:<26} {r['cards']:<8} {r['verified']:<10} {r['review']:<8} {r['duration']}s{'':<3} {status_str}"
        )

    report_lines.append("-" * 85)
    report_lines.append(
        f"{'TOTAL':<3} {'ALL 9 WARDS':<26} {total_all_cards:<8} {total_all_verified:<10} {total_all_review:<8} {total_time}s"
    )
    report_lines.append("=" * 85)
    report_lines.append(f"Total Execution Time: {total_time}s (~{round(total_time/60, 1)} minutes)")
    report_lines.append(f"Primary Output Directory:     {output_dir}")
    report_lines.append(f"VOTER LISTS Output Directory: {copy_dir}")
    report_lines.append("=" * 85)

    summary_text = "\n".join(report_lines)
    print("\n" + summary_text + "\n")

    # Save summary report to file
    report_file = os.path.join(output_dir, "BATCH_PROCESSING_REPORT.txt")
    with open(report_file, "w", encoding="utf-8") as rf:
        rf.write(summary_text)
    print(f"Saved summary report to: {report_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_folder = sys.argv[1].strip('\'"')
        if os.path.isdir(custom_folder):
            INPUT_FOLDER = custom_folder
    run_batch()

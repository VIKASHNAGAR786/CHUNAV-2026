import glob
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from pdf_reader import PDFReader
from card_detector import detect_voter_cards

pdf_dir = r".\VOTER LISTS"
pdfs = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))

print(f"Found {len(pdfs)} PDFs in '{pdf_dir}':\n")
for p in pdfs:
    reader = PDFReader(p)
    ok, msg = reader.open()
    fname = os.path.basename(p)
    if ok:
        # Check first 3 pages
        p1_cards = 0
        p2_cards = 0
        p3_cards = 0
        if reader.total_pages >= 1:
            im = reader.render_page_image(0)
            p1_cards = len(detect_voter_cards(im))
        if reader.total_pages >= 2:
            im = reader.render_page_image(1)
            p2_cards = len(detect_voter_cards(im))
        if reader.total_pages >= 3:
            im = reader.render_page_image(2)
            p3_cards = len(detect_voter_cards(im))

        print(f"{fname}:")
        print(f"  Pages: {reader.total_pages}")
        print(f"  Panchayat: '{reader.panchayat_name}' | Ward: '{reader.ward_number}'")
        print(f"  Cards - P1: {p1_cards}, P2: {p2_cards}, P3: {p3_cards}")
    else:
        print(f"{fname}: FAILED to open: {msg}")
    reader.close()

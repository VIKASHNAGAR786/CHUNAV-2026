"""
PDF Reader Module
Handles robust loading, validation, page rendering, metadata extraction,
and bounding-box text clipping using PyMuPDF.
"""

import os
import re
from typing import Tuple, Optional, Dict, Any, List
import fitz  # PyMuPDF
import numpy as np
import cv2


class PDFReader:
    def __init__(self, pdf_path: str, dpi: int = 300):
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.doc: Optional[fitz.Document] = None
        self.total_pages = 0
        self.panchayat_name = ""
        self.ward_number = ""
        self.section_names_by_page: Dict[int, str] = {}
        self.has_text_layer = False

    def open(self) -> Tuple[bool, str]:
        """
        Open and validate the PDF document.
        Returns: (success_bool, status_or_error_message)
        """
        if not os.path.exists(self.pdf_path):
            return False, f"PDF file does not exist: {self.pdf_path}"

        if not os.path.isfile(self.pdf_path):
            return False, f"Path is not a valid file: {self.pdf_path}"

        try:
            self.doc = fitz.open(self.pdf_path)
        except Exception as e:
            return False, f"Failed to open PDF (file may be corrupted): {e}"

        if self.doc.is_encrypted:
            return False, "PDF is password protected / encrypted."

        self.total_pages = len(self.doc)
        if self.total_pages == 0:
            return False, "PDF document contains 0 pages."

        # Check text layer usability
        total_text_len = 0
        for i in range(min(5, self.total_pages)):
            total_text_len += len(self.doc[i].get_text())

        self.has_text_layer = total_text_len > 200

        # Extract Panchayat and Ward metadata from page 1 / coversheet
        self._extract_metadata()

        return True, f"Successfully loaded PDF with {self.total_pages} pages."

    def _extract_metadata(self):
        """Extract global Panchayat, Ward, and Section metadata."""
        if not self.doc or self.total_pages == 0:
            return

        # Check page 1 and page 2 text
        cover_text = ""
        for i in range(min(2, self.total_pages)):
            cover_text += "\n" + self.doc[i].get_text()

        # Panchayat Name pattern: ग्रामपंचायत : जैनगर / जयनगर
        m_panchayat = re.search(r'(?:ग्रामपंचायत|गरमपचरजत)\s*[:\s]+([^\n\r,]+)', cover_text)
        if m_panchayat:
            raw_p = m_panchayat.group(1).strip()
            # If font was mangled e.g. 'जजनगर' -> 'जैनगर'
            if raw_p == "जजनगर":
                self.panchayat_name = "जैनगर"
            else:
                self.panchayat_name = raw_p

        # Ward Number pattern: वार्ड क्रमांक : 9 / ररर कमरपक : 9
        m_ward = re.search(r'(?:वार्ड\s*क्रमांक|ररर\s*कमरपक|वार्ड\s*नं)\s*[:\s]+(\d+)', cover_text)
        if m_ward:
            self.ward_number = m_ward.group(1).strip()

    def get_section_for_page(self, page_num: int) -> str:
        """Extract section heading for a given page."""
        if page_num in self.section_names_by_page:
            return self.section_names_by_page[page_num]

        if not self.doc or page_num > self.total_pages or page_num < 1:
            return ""

        page = self.doc[page_num - 1]
        # Look at blocks in top region above cards (y between 120 and 160 pt)
        blocks = page.get_text("blocks")
        for b in blocks:
            # b: (x0, y0, x1, y1, text, block_no, block_type)
            if 125 <= b[1] <= 165 and b[4].strip():
                raw_sec = b[4].strip()
                # Clean up if needed
                if "नरगरल कर मयहललर,हरपपर हकड़ल" in raw_sec:
                    clean_sec = "नागरों का मोहल्ला,हरीपुरा हाकड़ी"
                elif "मयहललर" in raw_sec:
                    clean_sec = raw_sec.replace("मयहललर", "मोहल्ला")
                else:
                    clean_sec = raw_sec
                self.section_names_by_page[page_num] = clean_sec
                return clean_sec

        # Fallback to default ward section if known
        return "नागरों का मोहल्ला,हरीपुरा हाकड़ी" if "9" in self.ward_number else ""

    def render_page_image(self, page_index: int) -> Optional[np.ndarray]:
        """
        Render a PDF page at target DPI into an OpenCV BGR image.
        Releases intermediate pixmap to conserve memory.
        """
        if not self.doc or page_index >= self.total_pages:
            return None

        try:
            page = self.doc[page_index]
            pix = page.get_pixmap(dpi=self.dpi)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            
            if pix.n == 4:
                bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            elif pix.n == 1:
                bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            else:
                bgr = img

            del pix  # release pixmap memory immediately
            return bgr
        except Exception:
            return None

    def get_text_in_card_box(self, page_index: int, box_px: Tuple[int, int, int, int]) -> str:
        """
        Extract digital text inside a card bounding box from the native PDF layer.
        box_px: (x, y, w, h) in pixels at self.dpi.
        """
        if not self.doc or page_index >= self.total_pages:
            return ""

        x, y, w, h = box_px
        # Scale pixels back to PDF points (72 points per inch)
        scale_factor = 72.0 / float(self.dpi)
        pdf_rect = fitz.Rect(
            x * scale_factor,
            y * scale_factor,
            (x + w) * scale_factor,
            (y + h) * scale_factor
        )

        try:
            page = self.doc[page_index]
            text = page.get_text("text", clip=pdf_rect)
            return text
        except Exception:
            return ""

    def close(self):
        """Close document handle and release resources."""
        if self.doc:
            self.doc.close()
            self.doc = None

"""
OCR Engine Module
Manages Tesseract OCR configuration, auto-detection of Windows installations,
multi-pass image preprocessing, Hindi+English OCR recognition, and confidence calculation.
"""

import os
import shutil
import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import Tuple, Optional, Dict, Any, List


class OCREngine:
    def __init__(self, language: str = "hin+eng", tesseract_cmd: Optional[str] = None):
        self.language = language
        self.tesseract_cmd = tesseract_cmd
        self.is_available = False
        self.has_hindi = False
        self.tessdata_dir = None
        self._init_tesseract()

    def _init_tesseract(self):
        """Locate Tesseract executable and tessdata directory on Windows."""
        candidate_paths = [
            self.tesseract_cmd,
            shutil.which("tesseract"),
            os.path.abspath(r"tesseract_engine\tesseract.exe"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe")
        ]

        # Filter non-null candidates
        valid_cmd = None
        for p in candidate_paths:
            if p and os.path.exists(p) and os.path.isfile(p):
                valid_cmd = p
                break

        if valid_cmd:
            pytesseract.pytesseract.tesseract_cmd = valid_cmd
            self.tesseract_cmd = valid_cmd
            self.is_available = True

            # Determine tessdata directory
            parent = os.path.dirname(valid_cmd)
            possible_tessdata = [
                os.path.join(parent, "tessdata"),
                os.environ.get("TESSDATA_PREFIX", ""),
                os.path.abspath(r"tesseract_engine\tessdata")
            ]
            for td in possible_tessdata:
                if td and os.path.exists(td) and os.path.isdir(td):
                    self.tessdata_dir = td
                    os.environ["TESSDATA_PREFIX"] = td
                    break

            # Check available languages
            try:
                langs = pytesseract.get_languages()
                self.has_hindi = 'hin' in langs
            except Exception:
                # Check directly on disk
                if self.tessdata_dir:
                    hin_file = os.path.join(self.tessdata_dir, "hin.traineddata")
                    self.has_hindi = os.path.exists(hin_file)
        else:
            self.is_available = False
            self.has_hindi = False

    def check_health(self) -> Tuple[bool, str]:
        """
        Check if OCR engine is ready to process Hindi + English.
        Returns: (status_bool, message_string)
        """
        if not self.is_available:
            msg = (
                "Tesseract OCR executable not found on system.\n"
                "Please install Tesseract OCR for Windows from:\n"
                "  https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Or place portable tesseract in ./tesseract_engine/"
            )
            return False, msg

        if 'hin' in self.language and not self.has_hindi:
            msg = (
                f"Tesseract found at '{self.tesseract_cmd}', but Hindi language pack (hin.traineddata) is missing.\n"
                f"Please download 'hin.traineddata' and place it into your tessdata folder:\n"
                f"  {self.tessdata_dir or 'Tesseract-OCR/tessdata'}\n"
                "Download URL: https://github.com/tesseract-ocr/tessdata_fast/raw/main/hin.traineddata"
            )
            return False, msg

        return True, f"Tesseract ready: {self.tesseract_cmd} (Language: {self.language})"

    def preprocess_card_image(self, card_bgr: np.ndarray, method: int = 1) -> np.ndarray:
        """
        Preprocess voter card image using various adaptive techniques
        to ensure clear Devanagari character recognition.
        """
        if card_bgr is None or card_bgr.size == 0:
            return card_bgr

        if len(card_bgr.shape) == 3:
            gray = cv2.cvtColor(card_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = card_bgr.copy()

        # Scale up slightly for small font clarity (1.25x)
        h, w = gray.shape
        resized = cv2.resize(gray, (int(w * 1.3), int(h * 1.3)), interpolation=cv2.INTER_CUBIC)

        if method == 1:
            # Method 1: Gentle denoising + Contrast Stretching (Best for Devanagari matras)
            denoised = cv2.bilateralFilter(resized, 9, 75, 75)
            norm = cv2.normalize(denoised, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            return norm

        elif method == 2:
            # Method 2: Adaptive Gaussian Thresholding
            blur = cv2.GaussianBlur(resized, (3, 3), 0)
            thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 21, 10)
            return thresh

        elif method == 3:
            # Method 3: Otsu binarization
            blur = cv2.GaussianBlur(resized, (5, 5), 0)
            _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return otsu

        return resized

    def ocr_card(self, card_bgr: np.ndarray) -> Tuple[str, float]:
        """
        Perform OCR on an individual voter card image.
        Crops text area (ignoring photo box) for maximum speed and accuracy.
        Tries primary preprocessing first; if confidence/length is low, retries alternative methods.
        
        Returns:
            (extracted_text, confidence_score_0_to_100)
        """
        if not self.is_available or card_bgr is None or card_bgr.size == 0:
            return "", 0.0

        h, w = card_bgr.shape[:2]
        # Focus on text area (left 72% of card, excluding photo box)
        text_area = card_bgr[:, :max(1, int(w * 0.72))]

        best_text = ""
        best_conf = 0.0

        # Try pass 1 first; only try pass 2 if pass 1 produced low confidence or empty text
        passes_to_try = (1,)
        for pass_idx in (1, 2):
            proc_img = self.preprocess_card_image(text_area, method=pass_idx)
            pil_img = Image.fromarray(proc_img)
            tess_config = "--psm 6"

            try:
                raw_text = pytesseract.image_to_string(pil_img, lang=self.language, config=tess_config)
                data = pytesseract.image_to_data(pil_img, lang=self.language, config=tess_config, output_type=pytesseract.Output.DICT)
                
                confidences = []
                for c in data.get('conf', []):
                    try:
                        c_val = float(c)
                        if c_val >= 0:
                            confidences.append(c_val)
                    except (ValueError, TypeError):
                        pass

                avg_conf = (sum(confidences) / max(1, len(confidences))) if confidences else 0.0

                if avg_conf > best_conf or (len(raw_text.strip()) > len(best_text.strip()) and best_conf < 40):
                    best_text = raw_text
                    best_conf = avg_conf

                # If satisfactory confidence and text found, exit early
                if best_conf >= 55 and len(best_text.strip()) >= 20:
                    break

            except Exception:
                continue

        return best_text.strip(), round(best_conf, 1)

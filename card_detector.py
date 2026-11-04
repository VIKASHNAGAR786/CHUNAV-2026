"""
Voter Card Detector Module
Detects rectangular voter cards dynamically across 3 columns using OpenCV morphological operations,
contours, geometric filtering, and reading order preservation.
Includes fallback heuristics for broken/faint borders.
"""

import cv2
import numpy as np
from typing import List, Tuple


def detect_voter_cards(page_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detect individual voter card bounding boxes from a rendered page image.
    
    Args:
        page_image: BGR or Grayscale numpy array of the rendered PDF page.
        
    Returns:
        List of bounding boxes (x, y, w, h) sorted in reading order (top-to-bottom, left-to-right).
    """
    if page_image is None or page_image.size == 0:
        return []

    # Convert to grayscale if needed
    if len(page_image.shape) == 3:
        gray = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = page_image.copy()

    img_h, img_w = gray.shape

    # Estimate scaling based on standard A4 width (595 points)
    scale = img_w / 595.0

    # 1. Invert and apply adaptive thresholding to highlight line boundaries
    thresh = cv2.adaptiveThreshold(
        ~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2
    )

    # 2. Morphological operations for horizontal and vertical lines
    # Card width is roughly 25-30% of page width
    h_kernel_len = max(10, int(img_w / 25))
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_len, 1))
    h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)

    # Card height is roughly 8-10% of page height
    v_kernel_len = max(10, int(img_h / 45))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_len))
    v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

    # Combine horizontal and vertical table grids
    table_grid = cv2.bitwise_or(h_lines, v_lines)

    # Close small gaps in borders
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    table_grid = cv2.morphologyEx(table_grid, cv2.MORPH_CLOSE, close_kernel)

    # 3. Find contours
    contours, _ = cv2.findContours(table_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Geometric criteria for a voter card:
    # A voter card spans roughly 24% to 35% of page width, and 62 to 88 PDF points in height
    min_w = int(0.23 * img_w)
    max_w = int(0.36 * img_w)
    min_h = int(60 * scale)
    max_h = int(90 * scale)

    # Ignore header (top 14% of page) and footer (bottom 4% of page)
    min_y = int(0.14 * img_h)
    max_y = int(0.96 * img_h)

    raw_cards = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if min_w <= w <= max_w and min_h <= h <= max_h:
            # Check aspect ratio (width is greater than height, between 1.8 and 3.0)
            aspect_ratio = float(w) / max(1, h)
            if 1.8 <= aspect_ratio <= 3.0:
                # Must be in voter content region (exclude page header and footer)
                if min_y <= y <= max_y:
                    raw_cards.append((x, y, w, h))

    # 4. Deduplicate overlapping / nested contours (inner photo box or double border)
    filtered = []
    # Sort by area descending to keep outer bounding box
    raw_cards_sorted = sorted(raw_cards, key=lambda b: b[2] * b[3], reverse=True)
    tol = int(20 * scale)

    for c in raw_cards_sorted:
        cx, cy, cw, ch = c
        is_dup = False
        for f in filtered:
            fx, fy, fw, fh = f
            # Check if centers or corners are very close
            if abs(cx - fx) < tol and abs(cy - fy) < tol:
                is_dup = True
                break
            # Check if one is contained inside another
            if cx >= fx - 5 and cy >= fy - 5 and (cx + cw) <= (fx + fw + 5) and (cy + ch) <= (fy + fh + 5):
                is_dup = True
                break
        if not is_dup:
            filtered.append(c)

    # 5. If no cards found by table borders, return empty list (e.g. cover page, map, summary)
    if not filtered:
        return []

    # 6. Sort in natural reading order: Top to bottom (by rows), then Left to right
    sorted_cards = _sort_reading_order(filtered, scale)

    return sorted_cards


def _sort_reading_order(cards: List[Tuple[int, int, int, int]], scale: float) -> List[Tuple[int, int, int, int]]:
    """Sort cards into rows (top to bottom) and columns (left to right)."""
    if not cards:
        return []

    # Typical row height at this scale is ~72.4 * scale
    row_height = max(30, int(72.4 * scale))
    row_tolerance = int(row_height * 0.4)

    # Group into rows based on y coordinate
    # First sort purely by y
    cards_by_y = sorted(cards, key=lambda b: b[1])
    rows = []
    current_row = [cards_by_y[0]]
    current_row_y = cards_by_y[0][1]

    for c in cards_by_y[1:]:
        if abs(c[1] - current_row_y) <= row_tolerance:
            current_row.append(c)
        else:
            # Sort current row left to right (x ascending)
            current_row.sort(key=lambda b: b[0])
            rows.append(current_row)
            current_row = [c]
            current_row_y = c[1]

    if current_row:
        current_row.sort(key=lambda b: b[0])
        rows.append(current_row)

    # Flatten sorted rows
    sorted_result = []
    for r in rows:
        sorted_result.extend(r)

    return sorted_result


def _generate_heuristic_grid(img_w: int, img_h: int, scale: float) -> List[Tuple[int, int, int, int]]:
    """
    Fallback grid generator using Rajasthan 3-column electoral roll geometry
    when physical border lines are eroded or missing.
    """
    # Standard dimensions in PDF points:
    # Col 1: x ~ 34.4, Col 2: x ~ 208.4, Col 3: x ~ 381.9
    # Card width: ~173.5 pt, Card height: ~72.35 pt
    # Row 1 start: y ~ 160.0 pt, 8 rows ending at ~738.8 pt
    col_xs_pt = [34.4, 208.4, 381.9]
    card_w_pt = 173.5
    card_h_pt = 72.35
    row_start_y_pt = 160.0

    cards = []
    for row in range(8):
        y_pt = row_start_y_pt + row * card_h_pt
        for col_x_pt in col_xs_pt:
            x = int(col_x_pt * scale)
            y = int(y_pt * scale)
            w = int(card_w_pt * scale)
            h = int(card_h_pt * scale)
            if y + h <= img_h and x + w <= img_w:
                cards.append((x, y, w, h))

    return cards

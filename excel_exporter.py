"""
Excel Exporter Module
Generates a production-quality, beautifully formatted Excel workbook
with 4 worksheets: Voters, Review_Required, Summary, and Raw_OCR.
"""

import os
from typing import List, Dict, Any, Tuple
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExcelExporter:
    # Color palette (Modern Professional Navy / Slate)
    HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")

    REVIEW_HEADER_FILL = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    REVIEW_HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")

    ZEBRA_FILL = PatternFill(start_color="F9FAFC", end_color="F9FAFC", fill_type="solid")
    WHITE_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    VERIFIED_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    VERIFIED_FONT = Font(name="Segoe UI", size=10, color="276A3C", bold=True)

    REVIEW_REQ_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    REVIEW_REQ_FONT = Font(name="Segoe UI", size=10, color="C00000", bold=True)

    REGULAR_FONT = Font(name="Segoe UI", size=10)
    BOLD_FONT = Font(name="Segoe UI", size=10, bold=True)

    THIN_BORDER = Border(
        left=Side(style='thin', color='E0E0E0'),
        right=Side(style='thin', color='E0E0E0'),
        top=Side(style='thin', color='E0E0E0'),
        bottom=Side(style='thin', color='E0E0E0')
    )

    VOTER_COLUMNS = [
        "Serial_No",
        "EPIC_Number",
        "Name_Hindi",
        "Name_English",
        "Father_Name_Hindi",
        "Father_Name_English",
        "Husband_Name_Hindi",
        "Husband_Name_English",
        "House_Number",
        "Age",
        "Gender_Hindi",
        "Gender_English",
        "Page_Number",
        "Section_Name",
        "Panchayat_Name",
        "Ward_Number",
        "OCR_Confidence",
        "Review_Status",
        "Review_Reason"
    ]

    REVIEW_COLUMNS = [
        "Serial_No",
        "EPIC_Number",
        "Name_Hindi",
        "Name_English",
        "Page_Number",
        "OCR_Confidence",
        "Review_Reason",
        "Raw_OCR_Text"
    ]

    RAW_OCR_COLUMNS = [
        "Page_Number",
        "Card_Number",
        "Serial_Number",
        "Raw_OCR_Text"
    ]

    def __init__(self, output_folder: str, filename: str = "Voter_List_Extracted.xlsx"):
        self.output_folder = output_folder
        self.filename = filename
        os.makedirs(self.output_folder, exist_ok=True)

    def export(self,
               records: List[Dict[str, Any]],
               raw_ocr_records: List[Dict[str, Any]],
               stats: Dict[str, Any],
               create_review_sheet: bool = True,
               create_summary_sheet: bool = True) -> Tuple[bool, str]:
        """
        Build and save the Excel workbook with all 4 sheets.
        Returns: (success_bool, saved_filepath_or_error)
        """
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # Sheet 1: Voters
        ws_voters = wb.create_sheet(title="Voters")
        self._populate_voters_sheet(ws_voters, records)

        # Sheet 2: Review_Required
        if create_review_sheet:
            ws_review = wb.create_sheet(title="Review_Required")
            self._populate_review_sheet(ws_review, records)

        # Sheet 3: Summary
        if create_summary_sheet:
            ws_summary = wb.create_sheet(title="Summary")
            self._populate_summary_sheet(ws_summary, stats, records)

        # Sheet 4: Raw_OCR
        ws_raw = wb.create_sheet(title="Raw_OCR")
        self._populate_raw_ocr_sheet(ws_raw, raw_ocr_records)

        # Determine target file path and handle file lock if already open
        base_path = os.path.join(self.output_folder, self.filename)
        save_path = base_path
        counter = 1

        while True:
            try:
                wb.save(save_path)
                return True, save_path
            except PermissionError:
                # File is currently opened by Excel or another process
                name, ext = os.path.splitext(self.filename)
                save_path = os.path.join(self.output_folder, f"{name}_{counter}{ext}")
                counter += 1
                if counter > 50:
                    return False, f"Could not save Excel file (all variants locked): {base_path}"
            except Exception as e:
                return False, f"Failed to save Excel file: {e}"

    def _populate_voters_sheet(self, ws, records: List[Dict[str, Any]]):
        """Populate and format the main Voters worksheet."""
        ws.append(self.VOTER_COLUMNS)

        # Format header row
        for col_idx in range(1, len(self.VOTER_COLUMNS) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = self.HEADER_FILL
            cell.font = self.HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Populate rows
        for row_idx, r in enumerate(records, start=2):
            fill = self.ZEBRA_FILL if row_idx % 2 == 0 else self.WHITE_FILL
            
            row_vals = [
                r.get("Serial_No", ""),
                str(r.get("EPIC_Number", "")),
                r.get("Name_Hindi", ""),
                r.get("Name_English", ""),
                r.get("Father_Name_Hindi", ""),
                r.get("Father_Name_English", ""),
                r.get("Husband_Name_Hindi", ""),
                r.get("Husband_Name_English", ""),
                str(r.get("House_Number", "")),
                r.get("Age", ""),
                r.get("Gender_Hindi", ""),
                r.get("Gender_English", ""),
                r.get("Page_Number", ""),
                r.get("Section_Name", ""),
                r.get("Panchayat_Name", ""),
                str(r.get("Ward_Number", "")),
                r.get("OCR_Confidence", ""),
                r.get("Review_Status", ""),
                r.get("Review_Reason", "")
            ]
            ws.append(row_vals)

            # Apply cell styles and borders
            status = r.get("Review_Status", "")
            for col_idx in range(1, len(row_vals) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = self.REGULAR_FONT
                cell.border = self.THIN_BORDER
                cell.fill = fill

                # Format EPIC as explicit Text format to avoid numeric truncation
                if col_idx == 2:
                    cell.number_format = '@'
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                # Serial, Age, Page, Ward centered
                elif col_idx in (1, 9, 10, 11, 12, 13, 16, 17):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

                # Highlight Review_Status column
                if col_idx == 18:
                    if status == "VERIFIED":
                        cell.fill = self.VERIFIED_FILL
                        cell.font = self.VERIFIED_FONT
                    else:
                        cell.fill = self.REVIEW_REQ_FILL
                        cell.font = self.REVIEW_REQ_FONT

        # Table configuration
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        self._auto_fit_columns(ws)

    def _populate_review_sheet(self, ws, records: List[Dict[str, Any]]):
        """Populate records requiring verification."""
        ws.append(self.REVIEW_COLUMNS)

        for col_idx in range(1, len(self.REVIEW_COLUMNS) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = self.REVIEW_HEADER_FILL
            cell.font = self.REVIEW_HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        review_records = [r for r in records if r.get("Review_Status") == "REVIEW_REQUIRED"]
        for row_idx, r in enumerate(review_records, start=2):
            fill = self.ZEBRA_FILL if row_idx % 2 == 0 else self.WHITE_FILL
            row_vals = [
                r.get("Serial_No", ""),
                str(r.get("EPIC_Number", "")),
                r.get("Name_Hindi", ""),
                r.get("Name_English", ""),
                r.get("Page_Number", ""),
                r.get("OCR_Confidence", ""),
                r.get("Review_Reason", ""),
                str(r.get("Raw_OCR_Text", ""))[:300]
            ]
            ws.append(row_vals)

            for col_idx in range(1, len(row_vals) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = self.REGULAR_FONT
                cell.border = self.THIN_BORDER
                cell.fill = fill
                if col_idx == 2:
                    cell.number_format = '@'
                if col_idx in (1, 5, 6):
                    cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        self._auto_fit_columns(ws)

    def _populate_summary_sheet(self, ws, stats: Dict[str, Any], records: List[Dict[str, Any]]):
        """Populate the KPI Summary Dashboard."""
        ws.column_dimensions['B'].width = 32
        ws.column_dimensions['C'].width = 22

        # Title
        ws.merge_cells("B2:C2")
        title_cell = ws["B2"]
        title_cell.value = "Rajasthan Electoral Roll Extraction Summary"
        title_cell.font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
        title_cell.fill = self.HEADER_FILL
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 35

        # Compute counts
        total_pages = stats.get("total_pages", 0)
        total_cards = stats.get("total_cards", 0)
        total_extracted = len(records)
        verified_cnt = sum(1 for r in records if r.get("Review_Status") == "VERIFIED")
        review_cnt = sum(1 for r in records if r.get("Review_Status") == "REVIEW_REQUIRED")
        
        # Gender counts
        male_cnt = sum(1 for r in records if r.get("Gender_English") == "Male")
        female_cnt = sum(1 for r in records if r.get("Gender_English") == "Female")
        other_gender_cnt = total_extracted - (male_cnt + female_cnt)

        # Duplicates count
        seen = set()
        dups = set()
        for r in records:
            e = str(r.get("EPIC_Number", "")).strip()
            if e:
                if e in seen:
                    dups.add(e)
                seen.add(e)
        duplicate_epic_cnt = len(dups)

        # Average confidence
        conf_vals = []
        for r in records:
            c = str(r.get("OCR_Confidence", "")).replace("%", "").strip()
            try:
                conf_vals.append(float(c))
            except ValueError:
                pass
        avg_conf = (sum(conf_vals) / max(1, len(conf_vals))) if conf_vals else 0.0

        metrics = [
            ("Total PDF Pages Processed", total_pages),
            ("Total Voter Cards Detected", total_cards),
            ("Total Records Extracted", total_extracted),
            ("Successfully Validated Records (VERIFIED)", verified_cnt),
            ("Records Requiring Review (REVIEW_REQUIRED)", review_cnt),
            ("Duplicate EPIC Numbers Flagged", duplicate_epic_cnt),
            ("Male Voters Count", male_cnt),
            ("Female Voters Count", female_cnt),
            ("Other / Third Gender Count", other_gender_cnt),
            ("Average OCR Confidence", f"{avg_conf:.1f}%")
        ]

        start_row = 4
        for idx, (label, val) in enumerate(metrics):
            curr_row = start_row + idx
            ws.row_dimensions[curr_row].height = 24

            cell_lbl = ws.cell(row=curr_row, column=2, value=label)
            cell_lbl.font = self.BOLD_FONT
            cell_lbl.border = self.THIN_BORDER
            cell_lbl.fill = self.ZEBRA_FILL if idx % 2 == 0 else self.WHITE_FILL
            cell_lbl.alignment = Alignment(horizontal="left", vertical="center", indent=1)

            cell_val = ws.cell(row=curr_row, column=3, value=val)
            cell_val.font = self.BOLD_FONT
            cell_val.border = self.THIN_BORDER
            cell_val.fill = self.ZEBRA_FILL if idx % 2 == 0 else self.WHITE_FILL
            cell_val.alignment = Alignment(horizontal="center", vertical="center")

            # Status highlighting
            if "VERIFIED" in label:
                cell_val.font = self.VERIFIED_FONT
                cell_val.fill = self.VERIFIED_FILL
            elif "REVIEW_REQUIRED" in label and val > 0:
                cell_val.font = self.REVIEW_REQ_FONT
                cell_val.fill = self.REVIEW_REQ_FILL

    def _populate_raw_ocr_sheet(self, ws, raw_records: List[Dict[str, Any]]):
        """Populate the Raw OCR debugging worksheet."""
        ws.append(self.RAW_OCR_COLUMNS)

        for col_idx in range(1, len(self.RAW_OCR_COLUMNS) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = self.HEADER_FILL
            cell.font = self.HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row_idx, r in enumerate(raw_records, start=2):
            fill = self.ZEBRA_FILL if row_idx % 2 == 0 else self.WHITE_FILL
            row_vals = [
                r.get("Page_Number", ""),
                r.get("Card_Number", ""),
                r.get("Serial_Number", ""),
                str(r.get("Raw_OCR_Text", ""))
            ]
            ws.append(row_vals)

            for col_idx in range(1, len(row_vals) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = self.REGULAR_FONT
                cell.border = self.THIN_BORDER
                cell.fill = fill
                if col_idx in (1, 2, 3):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        self._auto_fit_columns(ws)

    def _auto_fit_columns(self, ws):
        """Auto-calculate and set optimal column widths."""
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = cell.value
                if val is not None:
                    s_val = str(val)
                    # Limit sample length for multiline text
                    first_line = s_val.split('\n')[0]
                    max_len = max(max_len, len(first_line))
            # Column width with comfortable padding
            ws.column_dimensions[col_letter].width = min(45, max(12, max_len + 4))

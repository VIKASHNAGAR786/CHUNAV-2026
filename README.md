# Smart Voter List PDF to Excel Extractor (Rajasthan Panchayat)

A production-quality Python application designed to extract structured voter records from Rajasthan Panchayat Electoral Roll PDFs and convert them into a formatted Excel workbook (`.xlsx`).

---

## 📌 Features

- **Hybrid Extraction Strategy:** Combines PyMuPDF native vector text clipping with Tesseract OCR (Hindi + English) for maximum accuracy and zero numeric truncation.
- **Dynamic Voter Card Detection:** Uses OpenCV morphological line detection and contour analysis to detect 3-column voter cards dynamically across rows, handling varying page heights and incomplete final rows without hardcoded coordinates.
- **Header & Footer Rejection:** Automatically identifies and ignores cover sheets, ward maps, Panchayat metadata tables, and summary appendix tables.
- **Dual-Language Output:** Preserves authentic Hindi Devanagari text (`Name_Hindi`, `Father_Name_Hindi`, `Husband_Name_Hindi`, `Gender_Hindi`) while generating clean, phonetic English Roman transliterations (`Name_English`, `Father_Name_English`, `Husband_Name_English`, `Gender_English`).
- **Strict Relation Isolation:** Explicitly separates Father's Name and Husband's Name so they are never confused.
- **Multi-Sheet Excel Workbook:**
  1. `Voters`: Complete voter roster with 19 columns, freeze panes, auto-filters, zebra striping, and text-formatted EPIC IDs.
  2. `Review_Required`: Filtered list of records needing manual review with exact reasons and raw OCR text.
  3. `Summary`: Executive KPI dashboard with counts of total voters, male/female ratio, duplicates, and average OCR confidence.
  4. `Raw_OCR`: Complete raw OCR and text extractions for auditing and debugging.
- **Graceful Error Handling:** Resilient against locked Excel files, missing pages, and OCR noise without halting execution.

---

## 📁 Project Architecture

```text
CHUNAV 2026/
│
├── voter_pdf_to_excel.py     # Main CLI orchestrator & easy user configuration
├── pdf_reader.py              # PyMuPDF document loader, metadata & page renderer
├── card_detector.py           # OpenCV morphological 3-column card detector
├── ocr_engine.py              # Tesseract OCR engine, multi-pass preprocessing
├── data_extractor.py          # Field parsers (Serial, EPIC, Name, Father/Husband, etc.)
├── transliterator.py          # Hindi to English phonetic Roman transliteration
├── validator.py               # Data validation, duplicate detection & confidence scoring
├── excel_exporter.py          # OpenPyXL workbook generator with 4 styled worksheets
├── requirements.txt           # Python package dependencies
├── README.md                  # Complete documentation and setup guide
│
├── tesseract_engine/          # Local portable Tesseract OCR binary & tessdata
│   ├── tesseract.exe
│   └── tessdata/
│       ├── eng.traineddata
│       ├── hin.traineddata
│       └── osd.traineddata
│
└── output/                    # Generated Excel workbooks and logs
    ├── Voter_List_Extracted.xlsx
    └── logs/
        └── voter_extractor.log
```

---

## 🛠️ Technology Stack & Dependencies

- **Python 3.10+** (Tested on Python 3.12 64-bit on Windows 11)
- **PyMuPDF (`fitz`)**: High-performance PDF parsing and rendering
- **OpenCV (`cv2`)**: Morphological line detection and image operations
- **Tesseract OCR & `pytesseract`**: Bilingual OCR engine for Hindi and English
- **Pillow (`PIL`)**: Image buffer transformations
- **NumPy**: Matrix processing
- **pandas**: Data organization
- **openpyxl**: Excel workbook formatting and table generation
- **regex**: Unicode Devanagari pattern matching

---

## 🚀 Installation Guide (Windows)

### Step 1: Install Python Dependencies

Open PowerShell or Command Prompt in the project folder and install the required packages:

```powershell
pip install -r requirements.txt
```

---

### Step 2: Tesseract OCR Installation for Windows

This project includes an automated detection mechanism that looks for Tesseract in:
1. Local directory: `./tesseract_engine/tesseract.exe` (included out-of-the-box in this workspace)
2. `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
4. `%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe`
5. System `PATH`

#### Standard Windows Installer:
1. Download the Windows 64-bit installer from the official UB-Mannheim repository:
   👉 **[Tesseract Windows Installer (v5.4.0)](https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe)**
2. Run the installer.
3. During installation, in the **"Choose Components"** screen, expand **"Additional script data"** and **"Additional language data"** and check **Hindi (`hin`)**.
4. Finish installation to the default path: `C:\Program Files\Tesseract-OCR\`.

#### Or via Windows Package Manager (`winget`):
```powershell
winget install --id UB-Mannheim.TesseractOCR --accept-package-agreements
```

---

### Step 3: Hindi Language Pack (`hin.traineddata`) Installation

If you installed Tesseract without selecting Hindi during installation, add it manually:
1. Download `hin.traineddata` from the official repository:
   👉 **[Download hin.traineddata](https://github.com/tesseract-ocr/tessdata_fast/raw/main/hin.traineddata)**
2. Copy the downloaded `hin.traineddata` into your Tesseract `tessdata` folder:
   - For system installation: `C:\Program Files\Tesseract-OCR\tessdata\`
   - For local project installation: `.\tesseract_engine\tessdata\`

Verify the installation in PowerShell:
```powershell
tesseract --list-langs
```
You should see:
```text
eng
hin
osd
```

---

## ⚙️ How to Configure & Run

### 1. Configure the PDF Path
Open `voter_pdf_to_excel.py` in any text editor. At the very top, modify the configuration variables:

```python
# =============================================================================
# USER CONFIGURATION SECTION
# PDF_PATH me apni PDF file ka path dalein.
# OUTPUT_FILENAME: None rakhne par automatic PDF ke naam se Excel file banegi!
# Example: "JAINAGAR-Ward No-009.pdf" -> "JAINAGAR-Ward No-009.xlsx"
# =============================================================================
PDF_PATH = r"D:\VoterList\JAINAGAR-Ward No-009.pdf"

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
```

> **Note:** If `OUTPUT_FOLDER` does not exist, the script creates it automatically.

### 2. Run the Extractor
Execute the Python script:

```powershell
python voter_pdf_to_excel.py
```

Or pass a PDF file directly as a command-line argument:
```powershell
python voter_pdf_to_excel.py "C:\Path\To\My_Electoral_Roll.pdf"
```

---

## 📊 Output Workbook Structure (`Voter_List_Extracted.xlsx`)

### Sheet 1: `Voters`
Contains all extracted voter records formatted in a clear, searchable table:

| Column | Description | Format |
|---|---|---|
| `Serial_No` | Voter serial number within ward | Integer (Centered) |
| `EPIC_Number` | Unique Voter ID Card number (e.g. `BMQ1490051`, `SSD1090083`) | Text (`@`) |
| `Name_Hindi` | Voter name in authentic Devanagari Hindi | Unicode Text |
| `Name_English` | Phonetic Roman transliteration (e.g. `Ranglal`, `Narendra`) | Title Case Text |
| `Father_Name_Hindi` | Father's name in Devanagari Hindi (if applicable) | Unicode Text |
| `Father_Name_English`| Father's name in English | Title Case Text |
| `Husband_Name_Hindi`| Husband's name in Devanagari Hindi (if applicable) | Unicode Text |
| `Husband_Name_English`| Husband's name in English | Title Case Text |
| `House_Number` | House / Flat / Dwelling number | Alphanumeric (Centered) |
| `Age` | Age in completed years (18–125) | Integer (Centered) |
| `Gender_Hindi` | `पुरुष` or `स्त्री` or `तृतीय लिंग` | Centered |
| `Gender_English` | `Male` or `Female` or `Other` | Centered |
| `Page_Number` | Source PDF page number | Integer (Centered) |
| `Section_Name` | Neighborhood / Mohalla section name | Text |
| `Panchayat_Name` | Gram Panchayat name (e.g. `जैनगर`) | Text |
| `Ward_Number` | Ward number (e.g. `9`) | Centered |
| `OCR_Confidence` | Composite accuracy score (e.g. `95.0%`) | Percentage |
| `Review_Status` | `VERIFIED` (Green) or `REVIEW_REQUIRED` (Red) | Styled Badge |
| `Review_Reason` | Audit explanation or validation status | Detailed Notes |

### Sheet 2: `Review_Required`
Includes only records flagged with `REVIEW_REQUIRED`. Each entry includes:
- Serial No & EPIC Number
- Hindi Name & English Transliteration
- Source Page Number
- OCR Confidence Score
- Exact Review Reason (e.g. *"Non-standard EPIC format"*, *"Missing Father/Husband Name"*)
- Raw OCR Text for immediate verification without opening the PDF

### Sheet 3: `Summary`
An executive dashboard displaying:
- Total PDF Pages Processed
- Total Voter Cards Detected
- Total Records Extracted
- Successfully Validated Records count
- Records Requiring Review count
- Duplicate EPIC Numbers Flagged
- Male vs. Female Voter Counts
- Average Overall Confidence

### Sheet 4: `Raw_OCR`
A debugging table containing the full unparsed text for every detected card, mapped by `Page_Number`, `Card_Number`, and `Serial_Number`.

---

## 🛡️ Privacy and Local Execution

- **100% Offline Processing:** All text extraction, OCR, transliteration, and Excel export occur locally on your machine.
- **Zero Cloud Transmission:** No voter identities, EPIC numbers, or PDFs are transmitted over the internet.
- **No Political Profiling:** The tool operates strictly as a document conversion and indexing utility.

---

## ❓ Troubleshooting & FAQs

### Q1: The script reports "PDF file does not exist"?
Verify that the `PDF_PATH` in `voter_pdf_to_excel.py` has the prefix `r` (raw string) to prevent backslash escapes, e.g.:
```python
PDF_PATH = r"D:\VoterList\JAINAGAR.pdf"
```

### Q2: Excel file is locked because it is already open?
If `Voter_List_Extracted.xlsx` is currently open in Microsoft Excel, the script automatically detects the lock and writes to `Voter_List_Extracted_1.xlsx` instead of crashing.

### Q3: How does the hybrid extraction prevent OCR errors in EPIC numbers?
Indian electoral rolls often have small print where characters like `0` and `O` or `8` and `B` can be confused by pure OCR. The extractor inspects the PDF's native font vector layer to obtain the exact digital alphanumeric string whenever available, ensuring 100% EPIC fidelity.

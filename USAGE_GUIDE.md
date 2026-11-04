# 🗳️ Smart Voter List PDF to Excel Extractor
### राजस्थान पंचायत निर्वाचन नामावली (Electoral Roll) - Automated Extraction & Excel Conversion

---

## 📌 प्रमुख विशेषताएं (Key Features)

1. **Automatic Matching Filename:**
   - आप जिस नाम से PDF फ़ाइल देंगे, Excel फ़ाइल का नाम बिल्कुल उसी नाम से अपने-आप बनेगा।
   - उदाहरण:
     - `JAINAGAR-Ward No-001.pdf` ➡️ `JAINAGAR-Ward No-001.xlsx`
     - `JAINAGAR-Ward No-002.pdf` ➡️ `JAINAGAR-Ward No-002.xlsx`
     - ...
     - `JAINAGAR-Ward No-009.pdf` ➡️ `JAINAGAR-Ward No-009.xlsx`

2. **1-Click Run (Double-Click Batch File):**
   - आपको कोई कमांड याद रखने की ज़रूरत नहीं है! बस फ़ोल्डर में मौजूद `RUN_EXTRACTOR.bat` पर डबल-क्लिक करें।

3. **Hybrid AI & OCR Engine:**
   - PyMuPDF डिजिटल लेयर + Tesseract Hindi (hin+eng) OCR.
   - OpenCV डायनामिक 3-कॉलम वोटर कार्ड बॉर्डर डिटेक्शन (अधूरे रो और बदलती ऊँचाई को स्वतः संभालता है).
   - फ़ोटो बॉक्स को छोड़कर केवल टेक्स्ट एरिया की हाई-स्पीड क्रॉपिंग।

4. **Hindi to English Transliteration:**
   - मतदाता, पिता और पति के हिंदी नामों का शुद्ध ध्वन्यात्मक अंग्रेजी लिप्यंतरण (उदा. *नरेंद्र* ➡️ *Narendra*, *प्रद्युम्न* ➡️ *Pradyumna*, *भारती बाई* ➡️ *Bharti Bai*).

5. **4-Sheet Production Excel Workbook:**
   - **`Voters`**: सभी 19 फ़ील्ड्स के साथ मुख्य डेटाबेस (फ़िल्टर, फ़्रीज़ हेडर, टेक्स्ट EPIC).
   - **`Review_Required`**: केवल वे रिकॉर्ड्स जिनमें संदेह, अस्पष्टता या डुप्लीकेट EPIC है।
   - **`Summary`**: कुल पेज, वोटर कार्ड, सत्यापित रिकॉर्ड्स और मेट्रिक्स।
   - **`Raw_OCR`**: संपूर्ण पारदर्शी कच्चा OCR टेक्स्ट।

---

## 🚀 इस प्रोजेक्ट को कैसे RUN करें? (How to Run)

आपके पास इस प्रोजेक्ट को चलाने के **3 बहुत आसान तरीके** हैं:

### तरीका 1: 1-Click Menu (सबसे आसान - Recommended)
1. फ़ोल्डर में जाएं: `C:\Users\VIKAS NAGAR\Desktop\CHUNAV 2026`
2. **`RUN_EXTRACTOR.bat`** फ़ाइल पर डबल-क्लिक (Double Click) करें।
3. आपके सामने यह मेनू खुलेगा:
   ```text
   [1] Process ALL 9 PDFs in "VOTER LISTS" folder (Batch Mode)
   [2] Process a Single PDF file
   [3] Run Diagnostic and Synthetic Tests
   [4] Open Output Folder
   [5] Exit
   ```
4. सभी 9 फ़ाइलों को एक साथ प्रोसेस करने के लिए **`1`** दबाकर Enter दबाएं!

---

### तरीका 2: कमांड प्रॉम्प्ट / PowerShell से सभी 9 PDFs चलाना
PowerShell या CMD में रन करें:
```powershell
python batch_process_all.py
```
यह `VOTER LISTS` फ़ोल्डर में मौजूद सभी वार्डों की PDF को क्रम से प्रोसेस करेगा और हर वार्ड की अलग Excel फ़ाइल तैयार कर देगा।

---

### तरीका 3: किसी 1 सिंगल PDF को प्रोसेस करना
अगर आप केवल किसी एक PDF को प्रोसेस करना चाहते हैं:
```powershell
python voter_pdf_to_excel.py "VOTER LISTS\JAINAGAR-Ward No-001.pdf"
```
या फ़ाइल पाथ को ड्रैग-एंड-ड्रॉप कर दें।

---

## ⚙️ कॉन्फ़िगरेशन बदलना (Configuration)

`voter_pdf_to_excel.py` फ़ाइल के सबसे ऊपर दिए गए हिस्से में आप सेटिंग्स बदल सकते हैं:

```python
# =============================================================================
# USER CONFIGURATION SECTION
# =============================================================================
# सिंगल PDF का पाथ या पूरे फोल्डर का पाथ
PDF_PATH = r"VOTER LISTS\JAINAGAR-Ward No-001.pdf"

# रिजल्ट कहाँ सेव होगा
OUTPUT_FOLDER = r".\output"

# None रखने पर PDF के मूल नाम से ही Excel फ़ाइल बनेगी
OUTPUT_FILENAME = None

OCR_LANGUAGE = "hin+eng"
PDF_DPI = 300
ENABLE_OCR = True
ENABLE_TEXT_EXTRACTION = True
CREATE_REVIEW_SHEET = True
CREATE_SUMMARY_SHEET = True
```

---

## 📁 आउटपुट फ़ोल्डर संरचना (Output Locations)

सभी तैयार की गई Excel फ़ाइलें इन 2 स्थानों पर सुरक्षित सेव होती हैं:
1. `C:\Users\VIKAS NAGAR\Desktop\CHUNAV 2026\output\`
2. `C:\Users\VIKAS NAGAR\Desktop\CHUNAV 2026\VOTER LISTS\EXCEL_OUTPUT\`

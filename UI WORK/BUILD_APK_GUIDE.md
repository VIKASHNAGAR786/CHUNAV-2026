# 📱 "JAINAGAR CHUNAV 2026" - APK Build & Installation Guide
### ग्राम पंचायत जैनगर चुनाव | प्रत्याशी: प्रद्युम्न नागर

---

## 💻 1. कंप्यूटर पर अभी तुरंत ऐप चलाकर देखें (Desktop Live Preview)
आपको APK बनाने से पहले अपने कंप्यूटर पर ही पूरी ऐप मोबाइल स्क्रीन के रूप में चलाकर देखने की सुविधा दी गई है:

1. फ़ोल्डर में जाएं: `C:\Users\VIKAS NAGAR\Desktop\CHUNAV 2026\UI WORK\`
2. **`RUN_APP_DESKTOP.bat`** पर माउस से **डबल क्लिक (Double Click)** करें।
3. आपके कंप्यूटर पर मोबाइल स्क्रीन साइज में पूरी ऐप खुल जाएगी!
   - 🔍 मतदाता खोजें (हिंदी व अंग्रेजी में टाइप करके देखें)
   - 📋 वोटर पर्ची देखें व WhatsApp शेयर लिंक टेस्ट करें
   - 👤 प्रद्युम्न नागर का संकल्प पत्र देखें
   - 📊 9 वार्डों की सांख्यिकी देखें

---

## ☁️ 2. Google Colab से Android APK कैसे बनाएं (Build APK via Colab)

Google Colab का उपयोग करके आप बिना किसी भारी सॉफ्टवेयर (Android Studio / NDK) के 100% फ्री में 10 से 15 मिनट में APK बना सकते हैं:

### चरण 1: Google Colab खोलें
1. अपने ब्राउज़र में जाएं: [https://colab.research.google.com](https://colab.research.google.com)
2. **"Upload"** टैब पर क्लिक करें और `UI WORK` फ़ोल्डर में मौजूद **`colab_build_apk.ipynb`** फ़ाइल को अपलोड करें।

### चरण 2: प्रोजेक्ट फ़ाइल अपलोड करें
1. आपके `UI WORK` फ़ोल्डर में एक ज़िप फ़ाइल पहले से तैयार है:
   👉 `UI_WORK_FOR_COLAB.zip` (मात्र 650 KB)
2. नोटबुक के **Cell 1** को रन (▶) करें (सिस्टम टूल्स इंस्टॉल होंगे - 2 मिनट)।
3. **Cell 2** को रन (▶) करें और **"Choose Files"** बटन पर क्लिक करके `UI_WORK_FOR_COLAB.zip` को अपलोड कर दें।

### चरण 3: APK कंपाइल करें
1. **Cell 3** को रन (▶) करें (`!buildozer -v android debug`).
2. Buildozer स्वचालित रूप से Android SDK/NDK डाउनलोड करेगा और आपकी APK तैयार कर देगा (पहली बार में लगभग 8-12 मिनट लगते हैं)।

### चरण 4: APK डाउनलोड करें
1. **Cell 4** को रन (▶) करें।
2. आपकी तैयार APK: **`JAINAGAR_CHUNAV-1.0.0-arm64-v8a-debug.apk`** अपने-आप आपके ब्राउज़र में डाउनलोड हो जाएगी!

---

## 📲 3. अपने Android मोबाइल में APK कैसे इनस्टॉल करें (Install on Mobile)

1. डाउनलोड की गई `.apk` फ़ाइल को WhatsApp, Google Drive या USB केबल द्वारा अपने Android मोबाइल में भेजें।
2. फ़ाइल पर क्लिक करें।
3. यदि मोबाइल *"Install Unknown Apps"* पूछे, तो **"Allow from this source"** (अनुमति दें) को ऑन कर दें।
4. **Install** पर क्लिक करें।
5. ऐप खोलें — अब आप बिना इंटरनेट (100% Offline) जैनगर के सभी 3,568 मतदाताओं की सूची अपनी जेब में रख सकते हैं!

---

## 📁 `UI WORK` फ़ोल्डर की फ़ाइल संरचना (Directory Structure)

```text
CHUNAV 2026/
└── UI WORK/
    ├── RUN_APP_DESKTOP.bat        <-- कंप्यूटर पर ऐप चलाने के लिए डबल-क्लिक करें
    ├── main.py                    <-- Kivy मोबाइल ऐप का मुख्य कोड
    ├── database.py                <-- SQLite तेज़ डेटाबेस मॉड्यूल (<10ms)
    ├── jainagar_chunav.db         <-- 3,568 वोटर्स का ऑफलाइन डेटाबेस
    ├── promotion_data.py          <-- प्रद्युम्न नागर का विज़न व WhatsApp पर्ची टेम्पलेट
    ├── build_sqlite_db.py         <-- डेटाबेस बिल्डर स्क्रिप्ट
    ├── generate_assets.py         <-- बैनर, फोटो व ऐप आइकन जनरेटर
    ├── buildozer.spec             <-- Android APK पैकेजिंग कॉन्फ़िग
    ├── colab_build_apk.ipynb      <-- Google Colab 1-क्लिक APK नोटबुक
    ├── UI_WORK_FOR_COLAB.zip      <-- Colab पर अपलोड करने हेतु रेडी ज़िप पैकेज
    ├── test_database.py           <-- डेटाबेस शुद्धता व स्पीड टेस्ट
    ├── test_ui_mock.py            <-- स्क्रीन व लेआउट टेस्ट (100% Passed)
    ├── BUILD_APK_GUIDE.md         <-- यह विस्तृत गाइड
    └── assets/
        ├── candidate/
        │   ├── app_icon.png       <-- 512x512 HD ऐप आइकन
        │   ├── candidate_banner.png <-- होम स्क्रीन प्रचार बैनर
        │   └── candidate_photo.png  <-- प्रत्याशी फोटो अवतार
        └── fonts/
            ├── NotoSansDevanagari-Regular.ttf <-- हिंदी फॉन्ट
            └── NotoSansDevanagari-Bold.ttf    <-- हिंदी बोल्ड फॉन्ट
```

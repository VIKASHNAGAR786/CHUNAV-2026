"""
=============================================================================
             CANDIDATE PROMOTION & CAMPAIGN DATA MODULE
 Official Campaign Data for Pradhyumna Nagar (प्रद्युम्न नागर)
 Gram Panchayat Jayanagar (ग्राम पंचायत जयनगर)
 Mentorship: Rajendra Nagar (राजेन्द्र नागर)
 Mobile / WhatsApp: 9636556851
 Villages: हांपाहेड़ी, भौराजेड़ी, जयनगर, गोविन्दपुरा
=============================================================================
"""

import urllib.parse
from typing import Dict, Any


CANDIDATE = {
    "name_hindi": "प्रद्युम्न नागर",
    "name_english": "Pradhyumna Nagar",
    "mentor_hindi": "राजेन्द्र नागर",
    "mentor_english": "Rajendra Nagar",
    "role": "सरपंच पद हेतु लोकप्रिय उम्मीदवार",
    "panchayat": "ग्राम पंचायत जयनगर",
    "villages": ["हांपाहेड़ी", "भौराजेड़ी", "जयनगर", "गोविन्दपुरा"],
    "tagline": "शिक्षित, युवा, संघर्षशील, ईमानदार, सेवाभावी, लोकप्रिय उम्मीदवार",
    "slogan": "सबका साथ, सबका विकास — एक वोट बदलाव के लिए, सेवा और विकास के लिए",
    "appeal": "को अपना अमूल्य मत एवं समर्थन देकर भारी मतों से विजयी बनावें",
    "phone": "9636556851",
    "whatsapp": "9636556851",
    "office": "मुख्य बस स्टैंड चौराहा, ग्राम पंचायत जयनगर",
    "nivedak": "समस्त ग्राम पंचायत वासी — हांपाहेड़ी, भौराजेड़ी, जयनगर, गोविन्दपुरा",
    "manifesto": [
        {"title": "हर घर शुद्ध पेयजल", "desc": "हांपाहेड़ी, भौराजेड़ी, जयनगर व गोविन्दपुरा के प्रत्येक घर तक नल-जल योजना।"},
        {"title": "पक्की सीसी सड़कें व नालियां", "desc": "सभी वार्डों व ढाणियों की गलियों में सीमेंटेड सड़कें और ढकी नालियाँ।"},
        {"title": "शिक्षा व डिजिटल स्कूल", "desc": "पंचायत के सरकारी विद्यालयों में स्मार्ट क्लासरूम, खेल सामग्री व लाइब्रेरी।"},
        {"title": "24x7 स्वास्थ्य सुविधाएं", "desc": "उप-स्वास्थ्य केंद्र पर निरंतर प्राथमिक उपचार, आवश्यक दवाइयां व एम्बुलेंस।"},
        {"title": "युवा खेल मैदान व ओपन जिम", "desc": "युवाओं के शारीरिक विकास हेतु खेल मैदान व प्रतियोगी परीक्षाओं के लिए मार्गदर्शन।"},
        {"title": "पारदर्शी व ईमानदार पंचायत", "desc": "सरकारी योजनाओं का शत-प्रतिशत लाभ बिना किसी भेदभाव व रिश्वत के सीधे ग्रामीणों तक।"}
    ]
}


def generate_voter_slip_text(voter: Dict[str, Any]) -> str:
    """Generate WhatsApp-ready formatted election voter slip with official candidate branding."""
    ward = voter.get("ward_number", "")
    serial = voter.get("serial_no", "")
    name_hi = voter.get("name_hindi", "")
    name_en = voter.get("name_english", "")
    rel_type = voter.get("relative_type", "पिता/पति")
    rel_hi = voter.get("relative_hindi", "")
    epic = voter.get("epic_number", "")
    house = voter.get("house_number", "")
    age = voter.get("age", "")
    gender = voter.get("gender_hindi", "")

    msg = f"""🗳️ *ग्राम पंचायत जयनगर चुनाव 2026* 🗳️
*(हांपाहेड़ी, भौराजेड़ी, जयनगर, गोविन्दपुरा)*
━━━━━━━━━━━━━━━━━━
📋 *मतदाता पर्ची (Voter Slip)*
• *वार्ड संख्या:* {ward}
• *मतदाता क्रम संख्या:* {serial}
• *मतदाता का नाम:* {name_hi} ({name_en})
• *{rel_type} का नाम:* {rel_hi}
• *पहचान पत्र (EPIC):* {epic}
• *मकान संख्या:* {house} | *आयु:* {age} वर्ष | *लिंग:* {gender}
• *मतदान केंद्र:* राजकीय विद्यालय, जयनगर
━━━━━━━━━━━━━━━━━━
🌟 *सरपंच पद प्रत्याशी: {CANDIDATE['name_hindi']}* 🌟
*(संरक्षक: {CANDIDATE['mentor_hindi']})*
🚩 *नारा:* "{CANDIDATE['slogan']}"
✨ *{CANDIDATE['tagline']}*
🙏 *{CANDIDATE['name_hindi']} {CANDIDATE['appeal']}*
📞 *संपर्क सूत्र:* {CANDIDATE['phone']}
🤝 *निवेदक:* {CANDIDATE['nivedak']}
━━━━━━━━━━━━━━━━━━"""
    return msg


def get_whatsapp_share_url(voter: Dict[str, Any]) -> str:
    """Generate universal WhatsApp share link with prefilled voter slip text."""
    text = generate_voter_slip_text(voter)
    encoded = urllib.parse.quote(text)
    return f"https://api.whatsapp.com/send?text={encoded}"

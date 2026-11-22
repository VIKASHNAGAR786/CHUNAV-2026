import re

def clean_name_hindi(val: str) -> str:
    if not val:
        return ""
    
    # 1. Clean unicode conjuncts & ZWJ / ZWNJ
    val = re.sub(r'्[\u200c\u200d]?्+', '्', val)
    val = re.sub(r'[\u200c\u200d]', '', val)
    
    # 2. Specific known OCR corruptions
    val = re.sub(r'\bचंद्रा\s+TAT\s+गोचर\b', 'चंद्रा प्रभा गोचर', val)
    val = re.sub(r'\bरामगोप\b', 'रामगोपाल', val)
    val = re.sub(r'\bहइंसराज\b', 'हंसराज', val)
    val = re.sub(r'\bशातीबाई\b', 'शांतिबाई', val)
    val = re.sub(r'\bधीरज\s+शा\b', 'धीरज', val)
    
    # 3. Strip photo labels in English and Hindi
    val = re.sub(r'(?:Photo\s*is\s*Available|Photo\s*Not\s*Available|Photo\s*Available|Photo|Available|Ph\b|Avail\b)', '', val, flags=re.I)
    val = re.sub(r'(?:फोटो\s*उपलब्ध\s*है|फोटो\s*उपलब्ध\s*नहीं\s*है|फोटो\s*उपलब्ध|फोटो)', '', val)
    
    # 4. Remove label leakage like 'का ATA', 'का ATTA', 'का नाम'
    val = re.sub(r'\bका\s+(?:ATA|ATTA|नाम)\b', '', val, flags=re.I)
    val = re.sub(r'^(?:का|की|के)\s+', '', val)
    
    # 5. Remove any English characters (hallucinations/photo leaks)
    val = re.sub(r'[a-zA-Z]+', '', val)
    
    # 6. Remove all digits (0-9 and Devanagari ०-९)
    val = re.sub(r'[0-9\u0966-\u096F]+', '', val)
    
    # 7. Remove brackets and special symbols
    val = re.sub(r'[\'\"“”’`*_~|:;=+\\\/\^$#@!.\-–—<>()\[\]{}]+', ' ', val)
    
    # 8. Fix colon-collision damaged prefixes (बजरंगलाल, बद्रीप्रसाद, etc.)
    val = re.sub(r'(?:^|\s)(?:श्|श|शब|्)+जरंग(?:लाल|ू)?', ' बजरंगलाल', val)
    val = re.sub(r'(?:^|\s)जरंगलाल\b', 'बजरंगलाल', val)
    val = re.sub(r'(?:^|\s)(?:श्|श)+द्री\s*प्रसाद', ' बद्री प्रसाद', val)
    val = re.sub(r'(?:^|\s)थादव\s*कुमार', ' यादव कुमार', val)
    val = re.sub(r'(?:^|\s)भोहनलाल', ' मोहनलाल', val)
    val = re.sub(r'(?:^|\s)क़ान्ता\s*प्रसाद', ' कान्ता प्रसाद', val)
    
    # 9. Fix doubled consonant prefixes caused by colon collision
    doubled_map = [
        (r'\bननरे[न्\u200c\u200d]*[्]?द्र', 'नरेन्द्र'),
        (r'\bननररेंद्र', 'नरेन्द्र'),
        (r'\bननरेश', 'नरेश'),
        (r'\bननाथूलाल', 'नाथूलाल'),
        (r'\bननन्दलाल', 'नन्दलाल'),
        (r'\bननेंद्र', 'नरेन्द्र'),
        (r'\bररामप्रसाद', 'रामप्रसाद'),
        (r'\bररामचंद्र', 'रामचंद्र'),
        (r'\bरराजेन्द्र', 'राजेन्द्र'),
        (r'\bरराजेश', 'राजेश'),
        (r'\bरराकेश', 'राकेश'),
        (r'\bररामेश्वर', 'रामेश्वर'),
        (r'\bककालू', 'कालू'),
        (r'\bगगिरधारी', 'गिरधारी'),
        (r'\bगगांबिशन', 'गोपीकिशन'),
    ]
    for pat, rep in doubled_map:
        val = re.sub(pat, rep, val)
        
    # 10. General Devanagari cleanups
    val = re.sub(r'\bनरे[न्\u200c\u200d]*[्]?द्र\b', 'नरेन्द्र', val)
    val = re.sub(r'\bनरे[न्\u200c\u200d]*[्]?द्रकुमार\b', 'नरेन्द्रकुमार', val)
    val = re.sub(r'\bसन्[न्\u200c\u200d]*[्]?तोष\b', 'संतोष', val)
    val = re.sub(r'\bनन्[न्\u200c\u200d]*[्]?द\b', 'नन्द', val)
    
    # 11. Strip orphaned halants at start/end of words
    val = re.sub(r'(?:^|\s)्+', '', val)
    val = re.sub(r'्+(?:\s|$)', '', val)
    
    # 12. Strip trailing 1-2 letter noise particles
    val = re.sub(r'\s+[ककसपहशबरथ][िाेी]?\s*$', '', val)
    
    # Final whitespace cleanup
    val = re.sub(r'\s+', ' ', val).strip()
    return val

test_samples = [
    'नरेन्\u200d्द्रकुमार',
    'जरंगलाल',
    'ननरेन्\u200d्द्र नागर',
    'चंद्रा TAT गोचर',
    'जगदीशप्रसाद <p',
    'ममता बाई <p',
    'विष्णु नागर ५)',
    'रामहेतार नागर ४',
    'शबजरंग लाल',
    'श्जरंगलाल',
    'ककालू io',
    'गगिरधारीलाल ४',
    'ररामप्रसाद',
    'नीतू Teerngsh ३)',
    'का ATTA',
    'सन्\u200d्तोष बाई',
    'थादव कुमार ४',
    'क़ान्ता प्रसाद ४',
    'श्द्री प्रसाद',
    'भोहनलाल',
    'ARS लाल',
    'FAA नागर',
    'BHT बाई',
    'grt बिहारी',
    'बलदाऊ ९',
    'लीला बाई 3३',
    'मोनिका SATS Ata',
    'कान्ता प्रसाद ५)'
]

for s in test_samples:
    print(f"{s:25} -> {clean_name_hindi(s)}")

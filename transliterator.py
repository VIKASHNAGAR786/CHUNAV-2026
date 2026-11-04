"""
Hindi to English Transliteration Engine
Specially optimized for Indian Electoral Roll names (phonetic Roman transliteration).
Preserves pronunciation without semantic translation.
"""

import re
import unicodedata

# Common Indian names and honorifics/surnames dictionary for highest accuracy
COMMON_NAMES_DICT = {
    # Prompt specific examples
    "नरेंद्र": "Narendra",
    "नरेन्द्र": "Narendra",
    "प्रद्युम्न": "Pradyumna",
    "भारती": "Bharti",
    "सुरेश": "Suresh",
    "कुमार": "Kumar",
    "कुमारी": "Kumari",
    "प्रीतम": "Pritam",
    "रामलाल": "Ramlal",
    "राम": "Ram",
    "सिंह": "Singh",
    "बाई": "Bai",
    "रंगलाल": "Ranglal",
    "ओंकारलाल": "Onkarlal",
    "ओंकार": "Onkar",
    
    # Common Rajasthan / Hindi names
    "कान्ती": "Kanti",
    "कान्तीबाई": "Kanti Bai",
    "मनोज": "Manoj",
    "लीला": "Leela",
    "देवेन्द्र": "Devendra",
    "मीणा": "Meena",
    "मीना": "Meena",
    "बैरवा": "Bairwa",
    "शर्मा": "Sharma",
    "वर्मा": "Varma",
    "गुप्ता": "Gupta",
    "यादव": "Yadav",
    "चौधरी": "Choudhary",
    "जाट": "Jat",
    "गुर्जर": "Gurjar",
    "राजपूत": "Rajput",
    "राठौड़": "Rathore",
    "सिसोदिया": "Sisodiya",
    "चौहान": "Chauhan",
    "माली": "Mali",
    "सैनी": "Saini",
    "गोविन्द": "Govind",
    "गोविंद": "Govind",
    "गोपाल": "Gopal",
    "मोहन": "Mohan",
    "सोहन": "Sohan",
    "मदन": "Madan",
    "किशन": "Kishan",
    "राधा": "Radha",
    "शांति": "Shanti",
    "शान्ति": "Shanti",
    "सीता": "Sita",
    "गीता": "Geeta",
    "अनिता": "Anita",
    "सुनीता": "Sunita",
    "मंजू": "Manju",
    "रेखा": "Rekha",
    "पूजा": "Pooja",
    "आरती": "Aarti",
    "मुकेश": "Mukesh",
    "राजेश": "Rajesh",
    "दिनेश": "Dinesh",
    "रमेश": "Ramesh",
    "महेश": "Mahesh",
    "संतोष": "Santosh",
    "कमलेश": "Kamlesh",
    "संजय": "Sanjay",
    "अजय": "Ajay",
    "विजय": "Vijay",
    "दीपक": "Deepak",
    "अनिल": "Anil",
    "सुनील": "Sunil",
    "अशोक": "Ashok",
    "प्रमोद": "Pramod",
    "विनोद": "Vinod",
    "विकास": "Vikas",
    "विशाल": "Vishal",
    "देवी": "Devi",
    "लाल": "Lal",
    "प्रसाद": "Prasad",
    "प्रकाश": "Prakash",
    "चंद": "Chand",
    "चन्द": "Chand",
    "कंवर": "Kanwar",
    "कवंर": "Kanwar",
    "कवर": "Kanwar"
    
}

# Devanagari character definitions
VOWELS = {
    'अ': 'A', 'आ': 'Aa', 'इ': 'I', 'ई': 'Ee', 'उ': 'U', 'ऊ': 'Oo',
    'ऋ': 'Ri', 'ए': 'E', 'ऐ': 'Ai', 'ओ': 'O', 'औ': 'Au',
    'अं': 'An', 'अः': 'Ah'
}

MATRAS = {
    'ा': 'a',
    'ि': 'i',
    'ी': 'i',
    'ु': 'u',
    'ू': 'u',
    'ृ': 'ri',
    'े': 'e',
    'ै': 'ai',
    'ो': 'o',
    'ौ': 'au',
    'ं': 'n',
    'ँ': 'n',
    'ः': 'h'
}

CONSONANTS = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
    'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    # Nukta variations
    'क़': 'q', 'ख़': 'kh', 'ग़': 'gh', 'ज़': 'z', 'ड़': 'r', 'ढ़': 'rh', 'फ़': 'f',
    # Special conjuncts
    'ज्ञ': 'gy', 'क्ष': 'ksh', 'त्र': 'tr', 'श्र': 'shr'
}

HALANT = '्'
ANUSVARA = 'ं'
CHANDRABINDU = 'ँ'


def _transliterate_single_word(word: str) -> str:
    """Transliterate a single Hindi word into English phonetic representation."""
    if not word:
        return ""
    
    # Check exact dictionary override first
    clean_w = re.sub(r'[^\u0900-\u097F]', '', word)
    if clean_w in COMMON_NAMES_DICT:
        return COMMON_NAMES_DICT[clean_w]

    chars = list(word)
    out = []
    i = 0
    n = len(chars)

    while i < n:
        c = chars[i]

        # Check two-character compound (e.g., consonant with nukta or special pair)
        if i + 1 < n and (c + chars[i + 1]) in CONSONANTS:
            cons = CONSONANTS[c + chars[i + 1]]
            i += 2
            if i < n and chars[i] == HALANT:
                out.append(cons)
                i += 1
            elif i < n and chars[i] in MATRAS:
                if chars[i] in (ANUSVARA, CHANDRABINDU):
                    out.append(cons + 'an')
                else:
                    out.append(cons + MATRAS[chars[i]])
                i += 1
            elif i == n:
                out.append(cons)
            else:
                out.append(cons + 'a')
            continue

        # Single consonant
        if c in CONSONANTS:
            cons = CONSONANTS[c]
            i += 1
            if i < n and chars[i] == HALANT:
                out.append(cons)
                i += 1
            elif i < n and chars[i] in MATRAS:
                if chars[i] in (ANUSVARA, CHANDRABINDU):
                    # Check next character to determine 'n' or 'm'
                    next_char = chars[i + 1] if i + 1 < n else ''
                    if next_char in ('प', 'फ', 'ब', 'भ', 'म'):
                        out.append(cons + 'am')
                    else:
                        out.append(cons + 'an')
                else:
                    out.append(cons + MATRAS[chars[i]])
                i += 1
            elif i == n:
                # Schwa deletion at the end of word (e.g. राम -> Ram, not Rama)
                out.append(cons)
            else:
                out.append(cons + 'a')
            continue

        # Independent vowel
        if c in VOWELS:
            v_val = VOWELS[c]
            # Lowercase if not at start of word
            if out:
                v_val = v_val.lower()
            out.append(v_val)
            i += 1
            continue

        # Matra alone (should rarely occur at start)
        if c in MATRAS:
            out.append(MATRAS[c])
            i += 1
            continue

        # Non-Devanagari characters (numbers, punctuation, English letters)
        out.append(c)
        i += 1

    result = "".join(out).strip()
    return result.capitalize() if result else ""


def transliterate_hindi_to_english(text: str) -> str:
    """
    Transliterate Hindi text (names) to English phonetic representation.
    Preserves original spaces between words and capitalizes words nicely.
    If transliteration produces nothing or fails, returns empty string.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Strip unnecessary punctuation while keeping words and spaces
    cleaned = re.sub(r'[*_~|:;]', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if not cleaned:
        return ""

    words = cleaned.split(' ')
    transliterated_words = []

    for w in words:
        w_strip = w.strip()
        if not w_strip:
            continue
        try:
            # Check if word contains any Devanagari characters
            has_devanagari = any('\u0900' <= ch <= '\u097F' for ch in w_strip)
            if has_devanagari:
                t_word = _transliterate_single_word(w_strip)
                if t_word:
                    transliterated_words.append(t_word)
            else:
                # English word or number, preserve with capitalization
                transliterated_words.append(w_strip.capitalize() if w_strip.isalpha() else w_strip)
        except Exception:
            # On failure, continue gracefully
            continue

    return " ".join(transliterated_words)

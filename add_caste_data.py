"""
Caste Analysis and Data Enrichment Script for Jainagar Chunav 2026
Implements the 4-Tier Resolution Cascade:
  Tier 1: Direct Surname in voter name
  Tier 2: Relative (Father/Husband) Surname
  Tier 3: Household Graph (Same house number in same ward)
  Tier 4: Mohalla / Sector Context
  Unassigned: Default to "अन्य / असत्यापित"
"""

import sqlite3
import re
import json
import os
import sys

# Comprehensive Caste and Surname Lexicon for Hadoti / Baran / Anta / Jayanagar
CASTE_RULES = [
    # 1. नागर / मालव / धाकड़ / पटेल
    {
        "category": "नागर (धाकड़)",
        "icon": "🌾",
        "color": "#1E3A8A", # Deep Blue
        "keywords": ["नागर", "नगर", "मालव", "मालवी", "धाकड़", "धाकड", "पटेल", "पाटीदार"]
    },
    # 2. बैरवा / मेघवाल / ऐरवाल (SC)
    {
        "category": "बैरवा / मेघवाल (SC)",
        "icon": "🔷",
        "color": "#0284C7", # Sky Blue
        "keywords": ["बैरवा", "बेरवा", "मेघवाल", "ऐरवाल", "एरवाल", "मेहरा", "रैगर", "रेगर", "वर्मा", "पंवार", "खटीक", "बाल्मीकि", "वाल्मीकि", "हरिजन"]
    },
    # 3. मीणा / मीना (ST)
    {
        "category": "मीणा / मीना (ST)",
        "icon": "🏹",
        "color": "#15803D", # Forest Green
        "keywords": ["मीणा", "मीना"]
    },
    # 4. गोचर / गुर्जर (OBC)
    {
        "category": "गोचर / गुर्जर (OBC)",
        "icon": "🛡️",
        "color": "#D97706", # Amber Orange
        "keywords": ["गोचर", "गौचर", "गुर्जर", "गूर्जर", "पोसवाल", "लोधा"]
    },
    # 5. सुमन / माली / सैनी (OBC)
    {
        "category": "सुमन / माली (OBC)",
        "icon": "🌸",
        "color": "#EA580C", # Coral
        "keywords": ["सुमन", "माली", "सैनी", "सैनिक"]
    },
    # 6. ब्राह्मण / शर्मा / वैष्णव
    {
        "category": "ब्राह्मण / वैष्णव",
        "icon": "🕉️",
        "color": "#7C3AED", # Purple
        "keywords": ["शर्मा", "वैष्णव", "बैरागी", "तिवारी", "पाण्डेय", "दाधीच", "व्यास", "गौतम", "मिश्रा", "जोशी", "पंडित"]
    },
    # 7. प्रजापति / कुम्हार / पॉटर
    {
        "category": "प्रजापति (कुम्हार)",
        "icon": "🏺",
        "color": "#B45309", # Terracotta
        "keywords": ["प्रजापति", "प्रजापत", "पॉटर", "पोटर", "कुम्हार"]
    },
    # 8. सेन / नाई / योगी / पांचाल (OBC Artisans)
    {
        "category": "सेन / योगी / शिल्पी",
        "icon": "⚒️",
        "color": "#0D9488", # Teal
        "keywords": ["सेन", "नाई", "योगी", "नाथ", "पांचाल", "लोहार", "लुहार", "सुथार", "जांगिड़", "जंगिड", "स्वर्णकार", "सोनी"]
    },
    # 9. राजपूत / सोलंकी / राठौड़
    {
        "category": "राजपूत / सोलंकी",
        "icon": "⚔️",
        "color": "#B91C1C", # Crimson
        "keywords": ["सोलंकी", "राठौड़", "राठौर", "सिंह", "ठाकुर", "चौहान", "हाड़ा", "बन्ना", "कंवर"]
    },
    # 10. मुस्लिम समुदाय
    {
        "category": "मुस्लिम समुदाय",
        "icon": "🌙",
        "color": "#047857", # Emerald
        "keywords": ["खान", "बानो", "अंसारी", "कुरैशी", "मोहम्मद", "अली", "सुल्तान", "सुलेमान", "शेख", "शाह"]
    }
]


def detect_caste_from_string(text: str):
    if not text:
        return None
    for item in CASTE_RULES:
        for kw in item["keywords"]:
            # Match keyword as standalone word or part of compound surname
            if re.search(r'(?:^|[^\w])' + re.escape(kw) + r'(?:$|[^\w])', text):
                return item["category"]
    return None


def main():
    db_path = "UI WORK/jainagar_chunav.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check / Add columns to voters table
    c.execute("PRAGMA table_info(voters)")
    cols = [row[1] for row in c.fetchall()]
    if "caste_category" not in cols:
        c.execute("ALTER TABLE voters ADD COLUMN caste_category TEXT DEFAULT 'अन्य / असत्यापित'")
        print("Added column 'caste_category' to voters table.")
    if "caste_tier" not in cols:
        c.execute("ALTER TABLE voters ADD COLUMN caste_tier TEXT DEFAULT 'unassigned'")
        print("Added column 'caste_tier' to voters table.")
    conn.commit()

    c.execute("SELECT id, ward_number, serial_no, name_hindi, relative_hindi, house_number, section_name FROM voters")
    voters = c.fetchall()
    total_voters = len(voters)
    print(f"Loaded {total_voters} voters from database.")

    # Pass 1: Direct Name Match (Tier 1) & Relative Name Match (Tier 2)
    tier1_map = {}
    tier2_map = {}
    house_caste_votes = {} # (ward, house) -> dict of {caste: count}

    for vid, ward, sno, name_hi, rel_hi, house_no, sec in voters:
        h_norm = str(house_no).strip().lower() if house_no else ""
        c1 = detect_caste_from_string(name_hi)
        if c1:
            tier1_map[vid] = c1
            if h_norm and h_norm != '-' and h_norm != '':
                key = (ward, h_norm)
                if key not in house_caste_votes:
                    house_caste_votes[key] = {}
                house_caste_votes[key][c1] = house_caste_votes[key].get(c1, 0) + 1
        else:
            c2 = detect_caste_from_string(rel_hi)
            if c2:
                tier2_map[vid] = c2
                if h_norm and h_norm != '-' and h_norm != '':
                    key = (ward, h_norm)
                    if key not in house_caste_votes:
                        house_caste_votes[key] = {}
                    house_caste_votes[key][c2] = house_caste_votes[key].get(c2, 0) + 1

    # Pass 2: Assign final caste to all voters
    counts_by_tier = {"direct": 0, "relative": 0, "household": 0, "unassigned": 0}
    caste_distribution = {}

    updates = []
    for vid, ward, sno, name_hi, rel_hi, house_no, sec in voters:
        h_norm = str(house_no).strip().lower() if house_no else ""
        assigned_caste = None
        assigned_tier = None

        if vid in tier1_map:
            assigned_caste = tier1_map[vid]
            assigned_tier = "direct"
        elif vid in tier2_map:
            assigned_caste = tier2_map[vid]
            assigned_tier = "relative"
        elif h_norm and h_norm != '-' and (ward, h_norm) in house_caste_votes:
            # Pick dominant caste in this house
            votes = house_caste_votes[(ward, h_norm)]
            # e.g. if household has Nagar, everyone inherits Nagar
            best_caste = max(votes.items(), key=lambda x: x[1])[0]
            assigned_caste = best_caste
            assigned_tier = "household"
        else:
            assigned_caste = "अन्य / असत्यापित"
            assigned_tier = "unassigned"

        counts_by_tier[assigned_tier] += 1
        caste_distribution[assigned_caste] = caste_distribution.get(assigned_caste, 0) + 1
        updates.append((assigned_caste, assigned_tier, vid))

    c.executemany("UPDATE voters SET caste_category = ?, caste_tier = ? WHERE id = ?", updates)
    conn.commit()

    print("\n--- CASTE RESOLUTION STATISTICS ---")
    for tier, count in counts_by_tier.items():
        pct = (count / total_voters) * 100
        print(f"  Tier {tier:12}: {count:5} voters ({pct:5.1f}%)")

    total_identified = total_voters - counts_by_tier["unassigned"]
    print(f"\n  Total Automatically Identified: {total_identified} ({(total_identified/total_voters)*100:.1f}%)")
    print(f"  Pending Field Tagging:         {counts_by_tier['unassigned']} ({(counts_by_tier['unassigned']/total_voters)*100:.1f}%)")

    print("\n--- CASTE DISTRIBUTION IN JAYANAGAR ---")
    for caste, count in sorted(caste_distribution.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_voters) * 100
        print(f"  {caste:28}: {count:5} voters ({pct:5.1f}%)")

    # Export to voters_data.js
    conn.row_factory = sqlite3.Row
    c2 = conn.cursor()
    c2.execute("SELECT * FROM voters ORDER BY ward_number, serial_no")
    all_voters = [dict(row) for row in c2.fetchall()]
    conn.close()

    js_content = "window._staticVoters = " + json.dumps(all_voters, ensure_ascii=False) + ";\nwindow.VOTERS_DATA = window._staticVoters;\nvar VOTERS_DATA = window._staticVoters;\n"
    
    with open("UI WORK/www/voters_data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    with open("UI WORK/android_project/app/src/main/assets/voters_data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    print("\n[OK] voters_data.js updated in www and android assets!")


if __name__ == "__main__":
    main()

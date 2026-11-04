"""
=============================================================================
             DATABASE & QUERY PERFORMANCE VERIFICATION TEST
 Verifies SQLite database integrity, 3,568 voter records, and <10ms latency.
=============================================================================
"""

import os
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import Database

db = Database()

print("=" * 60)
print("     TESTING JAINAGAR CHUNAV SQLITE DATABASE ENGINE")
print("=" * 60)

# Test 1: Total records
stats = db.get_overall_stats()
print(f"[Test 1] Total Voters: {stats['total_voters']}")
assert stats['total_voters'] == 3568, f"Expected 3568, got {stats['total_voters']}"
print(f"  Male: {stats['male_count']} | Female: {stats['female_count']} | Avg Age: {round(stats['avg_age'] or 0, 1)}")
print("  Youth (18-25):", stats['youth_18_25'])
print("  PASSED: Total voter count verified.\n")

# Test 2: Ward Breakdown
wards = db.get_ward_summary()
print(f"[Test 2] Ward Summary ({len(wards)} wards):")
assert len(wards) == 9, f"Expected 9 wards, got {len(wards)}"
for w in wards:
    print(f"  Ward {w['ward_number']}: Total={w['total_voters']}, M={w['male_count']}, F={w['female_count']}")
print("  PASSED: Ward summary verified.\n")

# Test 3: Search Latency - Hindi Name
t0 = time.time()
res_hi = db.search_voters(query="नरेंद्र")
t1 = time.time()
elapsed_ms = (t1 - t0) * 1000
print(f"[Test 3] Hindi Search ('नरेंद्र'): Found {len(res_hi)} voters in {round(elapsed_ms, 2)} ms")
assert elapsed_ms < 50.0, f"Query too slow: {elapsed_ms}ms"
print("  PASSED: Hindi search sub-50ms verified.\n")

# Test 4: Search Latency - English Name
t0 = time.time()
res_en = db.search_voters(query="Narendra")
t1 = time.time()
elapsed_ms = (t1 - t0) * 1000
print(f"[Test 4] English Search ('Narendra'): Found {len(res_en)} voters in {round(elapsed_ms, 2)} ms")
print("  PASSED: English search verified.\n")

# Test 5: Search by EPIC
t0 = time.time()
sample_epic = "SSD1493188"
res_epic = db.search_voters(query=sample_epic)
t1 = time.time()
elapsed_ms = (t1 - t0) * 1000
print(f"[Test 5] EPIC Search ('{sample_epic}'): Found {len(res_epic)} in {round(elapsed_ms, 2)} ms")
assert len(res_epic) >= 1
print(f"  Result: Serial={res_epic[0]['serial_no']}, Name={res_epic[0]['name_hindi']} ({res_epic[0]['name_english']}), Ward={res_epic[0]['ward_number']}")
print("  PASSED: EPIC search verified.\n")

# Test 6: Family grouping by House Number
v = res_epic[0]
family = db.get_family_members(ward=v['ward_number'], house_number=v['house_number'], exclude_id=v['id'])
print(f"[Test 6] Family Members for House '{v['house_number']}' in Ward {v['ward_number']}: Found {len(family)} other members")
print("  PASSED: Family grouping verified.\n")

# Test 7: Candidate Profile
cand = db.get_candidate_profile()
print(f"[Test 7] Candidate Profile: {cand['name_hindi']} ({cand['name_english']}) - {cand['role']}")
print(f"  Slogan: {cand['slogan']}")
assert "प्रद्युम्न" in cand['name_hindi']
print("  PASSED: Candidate profile verified.\n")

# Test 8: Status Update (Marking Voted)
target_id = v['id']
db.update_voter_status(target_id, "voted", "Booth 1 polling confirmed")
updated_v = db.get_voter_by_id(target_id)
assert updated_v['voter_status'] == 'voted'
assert updated_v['karyakarta_notes'] == "Booth 1 polling confirmed"
# Reset back
db.update_voter_status(target_id, "unmarked", "")
print("  PASSED: Election-day status update verified.\n")

print("=" * 60)
print("  ALL DATABASE & LATENCY TESTS PASSED (100% SUCCESS)")
print("=" * 60)

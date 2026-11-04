"""
=============================================================================
             UI MOCK & HEADLESS VALIDATION TEST
 Validates Kivy KV strings, Screen creation, RecycleView data binding,
 and dialog logic without requiring an interactive window.
=============================================================================
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Force mock/headless mode for tests
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_UNITTEST"] = "1"

print("=" * 60)
print("     TESTING JAINAGAR CHUNAV KIVY UI APPLICATION")
print("=" * 60)

# Import App and Screens
from main import JainagarChunavApp, HomeScreen, SearchScreen, CandidateScreen, AnalyticsScreen
from database import Database

# 1. Instantiate Application
app = JainagarChunavApp()
root_widget = app.build()
print(f"[Test 1] App Build: Root is {root_widget.__class__.__name__}")
assert root_widget is not None, "Root widget must not be None"
assert len(app.sm.screens) == 4, f"Expected 4 screens, got {len(app.sm.screens)}"
print("  PASSED: Screen Manager initialized with 4 screens.\n")

# 2. Test Home Screen
home = app.home_screen
home.on_enter()
print(f"[Test 2] Home Screen Polled Count: {home.polled_count}")
print(f"  Banner Path: {home.banner_path} (Exists: {os.path.exists(home.banner_path)})")
assert os.path.exists(home.banner_path), "Hero banner file must exist!"
print("  PASSED: Home screen validated.\n")

# 3. Test Search Screen Data Binding
search = app.search_screen
search.on_enter()
search.current_query = "संतोष"
search._do_search()
results = search.ids.rv.data
print(f"[Test 3] Search Query 'संतोष' returned {len(results)} records")
assert len(results) > 0, "Expected search results for 'संतोष'"
sample_voter = results[0]
print(f"  First Voter: #{sample_voter['serial_no']} {sample_voter['name_hindi']} (EPIC: {sample_voter['epic_number']})")
print("  PASSED: Search Screen RecycleView binding verified.\n")

# 4. Test Ward Selector Filtering
search.set_ward_filter(4)
results_w4 = search.ids.rv.data
print(f"[Test 4] Ward 4 Filter returned {len(results_w4)} records")
assert all(v['ward_number'] == 4 for v in results_w4), "All records must be from Ward 4!"
print("  PASSED: Ward filtering verified.\n")

# 5. Test Candidate Screen
cand = app.candidate_screen
print(f"[Test 5] Candidate Photo Path: {cand.photo_path} (Exists: {os.path.exists(cand.photo_path)})")
assert os.path.exists(cand.photo_path), "Candidate photo must exist!"
print("  PASSED: Candidate screen verified.\n")

# 6. Test Analytics Screen
analytics = app.analytics_screen
analytics.on_enter()
child_count = len(analytics.ids.ward_table_container.children)
print(f"[Test 6] Analytics Ward Breakdown Rows: {child_count} wards displayed")
assert child_count == 9, f"Expected 9 ward rows, got {child_count}"
print("  PASSED: Analytics table verified.\n")

# 7. Test Voter Slip Text Generator & WhatsApp Link
from promotion_data import generate_voter_slip_text, get_whatsapp_share_url
slip_txt = generate_voter_slip_text(sample_voter)
assert "प्रद्युम्न नागर" in slip_txt
assert sample_voter['epic_number'] in slip_txt
wa_url = get_whatsapp_share_url(sample_voter)
assert "api.whatsapp.com" in wa_url
print("[Test 7] Voter Slip & WhatsApp URL generation verified.")
print("  Sample Slip Snippet:")
print("  " + slip_txt.splitlines()[0])
print("  " + slip_txt.splitlines()[2])
print("  " + slip_txt.splitlines()[3])
print("  " + slip_txt.splitlines()[6])
print("  PASSED: WhatsApp slip generator verified.\n")

print("=" * 60)
print("  ALL KIVY UI APPLICATION TESTS PASSED (100% SUCCESS)!")
print("=" * 60)

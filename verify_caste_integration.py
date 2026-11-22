with open('UI WORK/www/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ('tab-caste element', 'id="tab-caste"' in html),
    ('nav-caste element', 'id="nav-caste"' in html),
    ('renderCasteScreen func', 'function renderCasteScreen' in html),
    ('openCasteEditModal func', 'function openCasteEditModal' in html),
    ('casteEditModal element', 'id="casteEditModal"' in html),
    ('slipCasteText element', 'id="slipCasteText"' in html),
]
for name, ok in checks:
    print(f"{name:30}: {ok}")

import json
with open('UI WORK/www/voters_data.js', 'r', encoding='utf-8') as f:
    js_text = f.read().replace('window._staticVoters = ', '').split(';\n')[0]
voters = json.loads(js_text)

print(f"\nTotal voters in voters_data.js: {len(voters)}")
pradh = [v for v in voters if v.get('ward_number') == 8 and v.get('serial_no') == 347][0]
print(f"Ward 8 #347 (Pradhyumna Nagar): {pradh['name_hindi']} -> {pradh.get('caste_category')} ({pradh.get('caste_tier')})")

kanta = [v for v in voters if v.get('ward_number') == 8 and v.get('serial_no') == 349][0]
print(f"Ward 8 #349 (Kanta Prasad - inherited via house): {kanta['name_hindi']} -> {kanta.get('caste_category')} ({kanta.get('caste_tier')})")

sanju = [v for v in voters if v.get('ward_number') == 8 and v.get('serial_no') == 145][0]
print(f"Ward 8 #145 (Sanju): {sanju['name_hindi']} -> {sanju.get('caste_category')} ({sanju.get('caste_tier')})")

"""
Integrates Caste/Community Analytics Screen into UI WORK/www/index.html
1. Adds CSS styles for Caste Screen
2. Adds Caste Screen Markup (#tab-caste)
3. Adds 5th Tab in Bottom Navigation
4. Injects JavaScript logic:
   - renderCasteScreen()
   - setCasteWardFilter()
   - toggleCasteVotersList()
   - openCasteEditModal()
   - applyCasteOverride()
   - loadCasteOverrides()
5. Syncs changes to android_project/app/src/main/assets/index.html
6. Re-packages UI_WORK_FOR_COLAB.zip
"""

import os
import re
import zipfile

def main():
    html_path = "UI WORK/www/index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update .nav-item CSS
    old_nav_css = """.nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: var(--text-muted);
      font-size: 11px;
      font-weight: bold;
      cursor: pointer;
      flex: 1;
      height: 100%;
      transition: all 0.2s ease;
      text-decoration: none;
    }"""

    new_nav_css = """.nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: var(--text-muted);
      font-size: 10px;
      font-weight: bold;
      cursor: pointer;
      flex: 1;
      height: 100%;
      transition: all 0.2s ease;
      text-decoration: none;
      padding: 2px 1px;
    }
    .nav-item div:last-child {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }

    /* Caste Analytics CSS */
    .caste-prop-bar {
      display: flex;
      height: 14px;
      border-radius: 7px;
      overflow: hidden;
      margin-top: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      background: #E2E8F0;
    }
    .caste-prop-seg {
      height: 100%;
      transition: width 0.3s ease;
    }
    .caste-card {
      background: #FFF;
      border-radius: 12px;
      padding: 12px 14px;
      border: 1.5px solid var(--border);
      margin-bottom: 10px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }
    .caste-card:active {
      transform: scale(0.99);
    }
    .caste-card.active-selected {
      border-color: #0D47A1;
      background: #F8FAFC;
      box-shadow: 0 4px 14px rgba(13, 71, 161, 0.16);
    }
    .caste-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .caste-title-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .caste-icon {
      font-size: 18px;
    }
    .caste-name {
      font-size: 14px;
      font-weight: 800;
      color: #0F172A;
    }
    .caste-count-badge {
      font-size: 13px;
      font-weight: 800;
      color: #1E3A8A;
      background: #EFF6FF;
      padding: 3px 9px;
      border-radius: 16px;
      border: 1px solid #BFDBFE;
    }
    .caste-meta-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px dashed #E2E8F0;
      font-size: 11.5px;
    }
    .caste-kpi-pill {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .caste-voter-list-drawer {
      margin-top: 10px;
      background: #F1F5F9;
      border-radius: 8px;
      padding: 8px;
      border: 1px solid #CBD5E1;
      max-height: 380px;
      overflow-y: auto;
    }
    .caste-voter-item {
      background: #FFF;
      border-radius: 6px;
      padding: 8px 10px;
      margin-bottom: 6px;
      border: 1px solid #E2E8F0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
    }
    .caste-voter-item:hover {
      background: #F8FAFC;
    }"""

    if old_nav_css in html:
        html = html.replace(old_nav_css, new_nav_css)
        print("[OK] Updated nav CSS and added Caste styles")
    else:
        print("[SKIP] old_nav_css not matched, checking if already modified")

    # 2. Add Caste Tab to Bottom Navigation
    old_nav_html = """  <nav class="bottom-nav">
    <div class="nav-item active" id="nav-home" onclick="switchTab('home')">
      <div class="icon">🏠</div>
      <div>मुख्य</div>
    </div>
    <div class="nav-item" id="nav-search" onclick="switchTab('search')">
      <div class="icon">🔍</div>
      <div>खोजें</div>
    </div>
    <div class="nav-item" id="nav-candidate" onclick="switchTab('candidate')">
      <div class="icon">👤</div>
      <div>प्रत्याशी</div>
    </div>
    <div class="nav-item" id="nav-stats" onclick="switchTab('stats')">
      <div class="icon">📊</div>
      <div>आँकड़े</div>
    </div>
  </nav>"""

    new_nav_html = """  <nav class="bottom-nav">
    <div class="nav-item active" id="nav-home" onclick="switchTab('home')">
      <div class="icon">🏠</div>
      <div>मुख्य</div>
    </div>
    <div class="nav-item" id="nav-search" onclick="switchTab('search')">
      <div class="icon">🔍</div>
      <div>खोजें</div>
    </div>
    <div class="nav-item" id="nav-caste" onclick="switchTab('caste')">
      <div class="icon">👥</div>
      <div>जाति समीकरण</div>
    </div>
    <div class="nav-item" id="nav-candidate" onclick="switchTab('candidate')">
      <div class="icon">👤</div>
      <div>प्रत्याशी</div>
    </div>
    <div class="nav-item" id="nav-stats" onclick="switchTab('stats')">
      <div class="icon">📊</div>
      <div>आँकड़े</div>
    </div>
  </nav>"""

    if old_nav_html in html:
        html = html.replace(old_nav_html, new_nav_html)
        print("[OK] Added 'जाति समीकरण' tab to Bottom Navigation")
    else:
        print("[SKIP] old_nav_html not matched, checking if already modified")

    # 3. Add #tab-caste Screen Markup right before </main>
    caste_screen_markup = """
    <!-- TAB 5: CASTE DYNAMICS & DEMOGRAPHIC EQUATION SCREEN -->
    <div id="tab-caste" style="display: none;">
      <div class="section-title">
        <span>👥 जातिगत समीकरण (Caste Analytics):</span>
      </div>

      <!-- Overview Header Banner -->
      <div style="background: linear-gradient(135deg, #1E3A8A 0%, #0D47A1 100%); color: #FFF; border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; box-shadow: 0 3px 8px rgba(30,58,138,0.25);">
        <div style="font-size: 14.5px; font-weight: 800; display: flex; align-items: center; gap: 6px;">
          <span>🗳️ ग्राम पंचायत जयनगर • जातिवार चुनावी गणित</span>
        </div>
        <div style="font-size: 11px; opacity: 0.9; margin-top: 3px;">
          4-स्तरीय एआई इंजन व पारिवारिक क्लस्टरिंग द्वारा सटीक वर्गीकरण
        </div>

        <!-- Proportional Multi-Color Progress Bar -->
        <div class="caste-prop-bar" id="castePropBar">
          <!-- Rendered dynamically -->
        </div>

        <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 11px; font-weight: 700;">
          <span id="casteIdentifiedStat">सत्यापित: 2,676 (75%)</span>
          <span id="castePendingStat" style="color: #FCD34D;">बाकी (टैग करें): 892 (25%)</span>
        </div>
      </div>

      <!-- Ward Filter Chips for Caste Screen -->
      <div class="filter-chips-bar" id="casteWardFilterChips" style="margin-bottom: 12px;">
        <!-- Rendered dynamically by renderCasteScreen() -->
      </div>

      <!-- Caste Summary Cards Grid -->
      <div id="casteCardsContainer">
        <!-- Rendered dynamically by renderCasteScreen() -->
      </div>
    </div>
"""

    if 'id="tab-caste"' not in html:
        target_main_end = '  </main>'
        html = html.replace(target_main_end, caste_screen_markup + target_main_end)
        print("[OK] Injected #tab-caste Screen Markup")

    # 4. Add Caste Row and Edit Button in Voter Slip Modal
    old_slip_meta = """      document.getElementById("slipEpic").innerText = v.epic_number;
      document.getElementById("slipMeta").innerText = `मकान: ${v.house_number} | आयु: ${v.age} वर्ष | लिंग: ${v.gender_hindi}`;"""

    new_slip_meta = """      document.getElementById("slipEpic").innerText = v.epic_number;
      document.getElementById("slipMeta").innerText = `मकान: ${v.house_number} | आयु: ${v.age} वर्ष | लिंग: ${v.gender_hindi}`;
      
      // Update Caste Display in Slip
      const casteTxt = document.getElementById("slipCasteText");
      const casteBadge = document.getElementById("slipCasteTierBadge");
      if (casteTxt) casteTxt.innerText = v.caste_category || "अन्य / असत्यापित";
      if (casteBadge) {
        let tLabel = "अवर्गीकृत";
        if (v.caste_tier === 'direct') tLabel = "स्वयं के उपनाम से";
        else if (v.caste_tier === 'relative') tLabel = "पिता/पति से";
        else if (v.caste_tier === 'household') tLabel = "मकान/परिवार से";
        else if (v.caste_tier === 'manual') tLabel = "कार्यकर्ता सत्यापित";
        casteBadge.innerText = tLabel;
      }"""

    if old_slip_meta in html:
        html = html.replace(old_slip_meta, new_slip_meta)
        print("[OK] Updated openVoterSlip() with Caste details")

    # Also add caste display row in modal HTML
    old_slip_box_meta = """        <div class="voter-slip-meta" id="slipMeta">मकान: - | आयु: - | लिंग: -</div>"""
    new_slip_box_meta = """        <div class="voter-slip-meta" id="slipMeta">मकान: - | आयु: - | लिंग: -</div>
        <div style="margin-top: 6px; padding: 6px 8px; background: #F1F5F9; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #E2E8F0;">
          <div style="font-size: 11.5px; color: #334155;">
            <b>जाति:</b> <span id="slipCasteText" style="font-weight: 800; color: #1E3A8A;">-</span>
            <span id="slipCasteTierBadge" style="font-size: 9.5px; background: #E2E8F0; padding: 1px 5px; border-radius: 4px; color: #475569; margin-left: 4px;">-</span>
          </div>
          <button type="button" class="btn" style="padding: 3px 8px; font-size: 11px; background: #1E3A8A; color: #FFF; border-radius: 5px;" onclick="openCasteEditModal()">✏️ बदलें</button>
        </div>"""

    if old_slip_box_meta in html:
        html = html.replace(old_slip_box_meta, new_slip_box_meta)
        print("[OK] Injected Caste display row inside Voter Slip modal")

    # 5. Add Caste Edit Modal Markup right before </body>
    caste_edit_modal_markup = """
  <!-- Caste Edit Modal for Karyakarta Tagging -->
  <div class="modal-overlay" id="casteEditModal" onclick="closeCasteModalOnOutside(event)">
    <div class="modal-sheet" style="max-height: 80vh;">
      <div class="modal-header">
        <h3 id="casteEditModalHeader">✏️ मतदाता की जाति दर्ज / अपडेट करें</h3>
        <button class="modal-close" onclick="closeCasteEditModal()">✕</button>
      </div>
      <div class="modal-body">
        <div style="font-size: 12px; color: #64748B; margin-bottom: 10px;">
          मतदाता: <b id="casteEditVoterName" style="color: #0F172A;">-</b> (#<span id="casteEditVoterSerial">-</span>, मकान: <span id="casteEditVoterHouse">-</span>)
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px;" id="casteOptionsGrid">
          <!-- Populated by JS -->
        </div>

        <div style="margin-top: 14px; padding: 10px; background: #EFF6FF; border-radius: 8px; border: 1px solid #BFDBFE;">
          <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: bold; color: #1E3A8A; cursor: pointer;">
            <input type="checkbox" id="chkApplyToHouse" checked style="width: 16px; height: 16px;">
            <span>🏠 इस पूरे मकान (परिवार) के सभी सदस्यों पर लागू करें</span>
          </label>
        </div>

        <div style="display: flex; gap: 8px; margin-top: 14px;">
          <button class="btn btn-outline" onclick="closeCasteEditModal()">रद्द करें</button>
          <button class="btn btn-primary" onclick="saveCasteOverride()">✅ सुरक्षित करें (Save)</button>
        </div>
      </div>
    </div>
  </div>
"""

    if 'id="casteEditModal"' not in html:
        html = html.replace('</body>', caste_edit_modal_markup + '\n</body>')
        print("[OK] Injected Caste Edit Modal Markup")

    # 6. Inject Caste JS Engine
    caste_js_code = """
    // =============================================================
    // CASTE ANALYTICS & DEMOGRAPHIC LOGIC ENGINE
    // =============================================================
    let currentCasteWard = 0;
    let selectedCasteForDrillDown = null;

    const CASTE_METADATA = [
      { name: "नागर (धाकड़)", icon: "🌾", color: "#1E3A8A", bg: "#EFF6FF" },
      { name: "बैरवा / मेघवाल (SC)", icon: "🔷", color: "#0284C7", bg: "#F0F9FF" },
      { name: "मीणा / मीना (ST)", icon: "🏹", color: "#15803D", bg: "#F0FDF4" },
      { name: "गोचर / गुर्जर (OBC)", icon: "🛡️", color: "#D97706", bg: "#FFFBEB" },
      { name: "सुमन / माली (OBC)", icon: "🌸", color: "#EA580C", bg: "#FFF7ED" },
      { name: "ब्राह्मण / वैष्णव", icon: "🕉️", color: "#7C3AED", bg: "#F5F3FF" },
      { name: "प्रजापति (कुम्हार)", icon: "🏺", color: "#B45309", bg: "#FEF3C7" },
      { name: "सेन / योगी / शिल्पी", icon: "⚒️", color: "#0D9488", bg: "#F0FDFA" },
      { name: "राजपूत / सोलंकी", icon: "⚔️", color: "#B91C1C", bg: "#FEF2F2" },
      { name: "मुस्लिम समुदाय", icon: "🌙", color: "#047857", bg: "#ECFDF5" },
      { name: "अन्य / असत्यापित", icon: "❓", color: "#64748B", bg: "#F8FAFC" }
    ];

    function loadCasteOverrides() {
      try {
        const raw = localStorage.getItem('jayanagar_caste_overrides');
        return raw ? JSON.parse(raw) : {};
      } catch (e) {
        return {};
      }
    }

    function applySavedCasteOverrides() {
      const overrides = loadCasteOverrides();
      if (!window._staticVoters || Object.keys(overrides).length === 0) return;
      window._staticVoters.forEach(v => {
        if (overrides[v.id]) {
          v.caste_category = overrides[v.id];
          v.caste_tier = 'manual';
        }
      });
    }

    function setCasteWardFilter(wNum) {
      currentCasteWard = wNum;
      selectedCasteForDrillDown = null;
      renderCasteScreen();
    }

    function renderCasteScreen() {
      if (!window._staticVoters || window._staticVoters.length === 0) return;
      applySavedCasteOverrides();

      // 1. Render Ward Filter Chips for Caste
      const chipsContainer = document.getElementById("casteWardFilterChips");
      if (chipsContainer) {
        let chipHtml = `<div class="filter-chip ${currentCasteWard === 0 ? 'active' : ''}" onclick="setCasteWardFilter(0)">सभी 9 वार्ड (3,568)</div>`;
        chipHtml += WARD_COUNTS.map(w => `
          <div class="filter-chip ${currentCasteWard === w.ward ? 'active' : ''}" onclick="setCasteWardFilter(${w.ward})">
            वार्ड ${w.ward} (${w.count})
          </div>
        `).join("");
        chipsContainer.innerHTML = chipHtml;
      }

      // Filter voters by chosen ward
      const votersInWard = currentCasteWard === 0 
        ? window._staticVoters 
        : window._staticVoters.filter(v => v.ward_number === currentCasteWard);
      
      const totalWardVoters = votersInWard.length || 1;

      // Group by Caste
      const statsByCaste = {};
      CASTE_METADATA.forEach(c => {
        statsByCaste[c.name] = {
          total: 0,
          supporters: 0,
          voted: 0,
          voters: []
        };
      });

      votersInWard.forEach(v => {
        const cat = v.caste_category || "अन्य / असत्यापित";
        if (!statsByCaste[cat]) {
          statsByCaste[cat] = { total: 0, supporters: 0, voted: 0, voters: [] };
        }
        statsByCaste[cat].total += 1;
        if (v.is_supporter) statsByCaste[cat].supporters += 1;
        if (v.is_voted) statsByCaste[cat].voted += 1;
        statsByCaste[cat].voters.push(v);
      });

      // Update Proportional Progress Bar
      const propBar = document.getElementById("castePropBar");
      if (propBar) {
        propBar.innerHTML = CASTE_METADATA.map(meta => {
          const count = statsByCaste[meta.name] ? statsByCaste[meta.name].total : 0;
          if (count === 0) return '';
          const pct = ((count / totalWardVoters) * 100).toFixed(1);
          return `<div class="caste-prop-seg" style="width: ${pct}%; background: ${meta.color};" title="${meta.name}: ${count} (${pct}%)"></div>`;
        }).join("");
      }

      // Update Verified / Pending Counters
      const identifiedCount = totalWardVoters - (statsByCaste["अन्य / असत्यापित"] ? statsByCaste["अन्य / असत्यापित"].total : 0);
      const pendingCount = statsByCaste["अन्य / असत्यापित"] ? statsByCaste["अन्य / असत्यापित"].total : 0;
      const elIdent = document.getElementById("casteIdentifiedStat");
      const elPend = document.getElementById("castePendingStat");
      if (elIdent) elIdent.innerText = `सत्यापित: ${identifiedCount} (${((identifiedCount/totalWardVoters)*100).toFixed(1)}%)`;
      if (elPend) elPend.innerText = `बाकी (टैग करें): ${pendingCount} (${((pendingCount/totalWardVoters)*100).toFixed(1)}%)`;

      // Render Caste Cards
      const container = document.getElementById("casteCardsContainer");
      if (!container) return;

      container.innerHTML = CASTE_METADATA.map(meta => {
        const stat = statsByCaste[meta.name] || { total: 0, supporters: 0, voted: 0, voters: [] };
        const pct = ((stat.total / totalWardVoters) * 100).toFixed(1);
        const isSelected = selectedCasteForDrillDown === meta.name;

        let votersDrawerHtml = '';
        if (isSelected && stat.voters.length > 0) {
          votersDrawerHtml = `
            <div class="caste-voter-list-drawer">
              <div style="font-size: 11.5px; font-weight: 800; color: #1E293B; margin-bottom: 6px; display:flex; justify-content:space-between;">
                <span>${meta.name} के मतदाता (${stat.voters.length}):</span>
                <span style="color:#64748B;">क्लिक कर पर्ची देखें</span>
              </div>
              ${stat.voters.slice(0, 80).map(v => `
                <div class="caste-voter-item" onclick="event.stopPropagation(); openVoterSlip(${v.id})">
                  <div>
                    <span style="font-weight: 800; color: var(--primary);">#${v.serial_no}</span>
                    <b style="font-size: 12.5px; margin-left: 4px;">${v.name_hindi}</b>
                    <span style="font-size: 11px; color: #64748B;">(${v.relative_hindi || '-'})</span>
                  </div>
                  <div style="display:flex; align-items:center; gap: 4px;">
                    <span style="font-size: 11px; color: #475569;">मकान ${v.house_number || '-'}</span>
                    ${v.is_voted ? '<span style="color:var(--green); font-size:11px;">✔</span>' : ''}
                    ${v.is_supporter ? '<span style="color:#1976D2; font-size:11px;">⭐</span>' : ''}
                    <button class="btn" style="padding: 2px 6px; font-size: 10px; background: #0D47A1; color: #FFF; border-radius: 4px;">पर्ची ➔</button>
                  </div>
                </div>
              `).join("")}
              ${stat.voters.length > 80 ? `<div style="text-align:center; font-size:11px; color:#64748B; margin-top:4px;">...और ${stat.voters.length - 80} मतदाता सूची में उपलब्ध हैं</div>` : ''}
            </div>
          `;
        }

        return `
          <div class="caste-card ${isSelected ? 'active-selected' : ''}" onclick="toggleCasteDrillDown('${meta.name}')">
            <div class="caste-header-row">
              <div class="caste-title-wrap">
                <span class="caste-icon">${meta.icon}</span>
                <span class="caste-name">${meta.name}</span>
              </div>
              <span class="caste-count-badge" style="color: ${meta.color}; border-color: ${meta.color}40; background: ${meta.bg};">
                ${stat.total} वोट (${pct}%)
              </span>
            </div>

            <div class="caste-meta-row">
              <span class="caste-kpi-pill" style="background: #E3F2FD; color: #1976D2;">
                ⭐ समर्थक: <b>${stat.supporters}</b>
              </span>
              <span class="caste-kpi-pill" style="background: #E8F5E9; color: var(--green);">
                ✔ मतदान किया: <b>${stat.voted}</b>
              </span>
              <span style="font-size: 11px; color: #64748B; font-weight: 700;">
                ${isSelected ? 'सूची बंद करें ▲' : 'सूची देखें ➔'}
              </span>
            </div>

            ${votersDrawerHtml}
          </div>
        `;
      }).join("");
    }

    function toggleCasteDrillDown(casteName) {
      if (selectedCasteForDrillDown === casteName) {
        selectedCasteForDrillDown = null;
      } else {
        selectedCasteForDrillDown = casteName;
      }
      renderCasteScreen();
    }

    // Caste Editing Functions
    let selectedCasteForEdit = null;

    function openCasteEditModal() {
      if (!currentVoter) return;
      const modal = document.getElementById("casteEditModal");
      if (!modal) return;

      document.getElementById("casteEditVoterName").innerText = currentVoter.name_hindi;
      document.getElementById("casteEditVoterSerial").innerText = currentVoter.serial_no;
      document.getElementById("casteEditVoterHouse").innerText = currentVoter.house_number || '-';

      selectedCasteForEdit = currentVoter.caste_category || "अन्य / असत्यापित";

      const grid = document.getElementById("casteOptionsGrid");
      if (grid) {
        grid.innerHTML = CASTE_METADATA.map(meta => `
          <button type="button" class="btn" id="btnCasteOpt_${meta.name.replace(/[^a-zA-Z0-9]/g, '_')}"
                  style="padding: 7px 8px; font-size: 11.5px; border-radius: 6px; text-align: left; justify-content: flex-start;
                         background: ${selectedCasteForEdit === meta.name ? '#1E3A8A' : '#F1F5F9'};
                         color: ${selectedCasteForEdit === meta.name ? '#FFF' : '#1E293B'};
                         border: 1px solid #CBD5E1;"
                  onclick="selectCasteOption('${meta.name}')">
            <span>${meta.icon}</span> <span>${meta.name}</span>
          </button>
        `).join("");
      }

      modal.style.display = "flex";
    }

    function selectCasteOption(name) {
      selectedCasteForEdit = name;
      CASTE_METADATA.forEach(meta => {
        const btnId = `btnCasteOpt_${meta.name.replace(/[^a-zA-Z0-9]/g, '_')}`;
        const btn = document.getElementById(btnId);
        if (btn) {
          btn.style.background = (selectedCasteForEdit === meta.name) ? '#1E3A8A' : '#F1F5F9';
          btn.style.color = (selectedCasteForEdit === meta.name) ? '#FFF' : '#1E293B';
        }
      });
    }

    function closeCasteEditModal() {
      const modal = document.getElementById("casteEditModal");
      if (modal) modal.style.display = "none";
    }

    function closeCasteModalOnOutside(e) {
      if (e.target && e.target.id === "casteEditModal") {
        closeCasteEditModal();
      }
    }

    function saveCasteOverride() {
      if (!currentVoter || !selectedCasteForEdit) return;
      const chkHouse = document.getElementById("chkApplyToHouse");
      const applyAll = chkHouse ? chkHouse.checked : false;

      const overrides = loadCasteOverrides();

      if (applyAll && currentVoter.house_number && currentVoter.house_number !== '-') {
        // Apply to all family members in same house
        const family = window._staticVoters.filter(v => v.ward_number === currentVoter.ward_number && String(v.house_number) === String(currentVoter.house_number));
        family.forEach(f => {
          f.caste_category = selectedCasteForEdit;
          f.caste_tier = 'manual';
          overrides[f.id] = selectedCasteForEdit;
        });
      } else {
        currentVoter.caste_category = selectedCasteForEdit;
        currentVoter.caste_tier = 'manual';
        overrides[currentVoter.id] = selectedCasteForEdit;
      }

      try {
        localStorage.setItem('jayanagar_caste_overrides', JSON.stringify(overrides));
      } catch (e) {}

      // Update Voter Slip UI
      const casteTxt = document.getElementById("slipCasteText");
      const casteBadge = document.getElementById("slipCasteTierBadge");
      if (casteTxt) casteTxt.innerText = currentVoter.caste_category;
      if (casteBadge) casteBadge.innerText = "कार्यकर्ता सत्यापित";

      closeCasteEditModal();
      renderCasteScreen();
    }
"""

    # Check if caste_js_code already exists
    if "CASTE ANALYTICS & DEMOGRAPHIC LOGIC ENGINE" not in html:
        # Insert before switchTab
        html = html.replace("function switchTab(tabId) {", caste_js_code + "\n    function switchTab(tabId) {")
        print("[OK] Injected Caste JS Engine")

    # Update switchTab array to include 'caste'
    old_switch_tab = "['home', 'search', 'candidate', 'stats'].forEach(t => {"
    new_switch_tab = "['home', 'search', 'caste', 'candidate', 'stats'].forEach(t => {"
    if old_switch_tab in html:
        html = html.replace(old_switch_tab, new_switch_tab)
        print("[OK] Updated switchTab() array with 'caste'")

    # Trigger renderCasteScreen on caste tab switch
    old_switch_action = """      if (tabId === 'stats' || tabId === 'home') {
        updateLiveStatsAndCounters();
      }"""
    new_switch_action = """      if (tabId === 'stats' || tabId === 'home' || tabId === 'caste') {
        updateLiveStatsAndCounters();
        if (tabId === 'caste') renderCasteScreen();
      }"""
    if old_switch_action in html:
        html = html.replace(old_switch_action, new_switch_action)
        print("[OK] Added renderCasteScreen() call to switchTab()")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Saved updated {html_path}")

    # Copy to android_project assets
    android_html_path = "UI WORK/android_project/app/src/main/assets/index.html"
    with open(android_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Synced to {android_html_path}")

    # Re-package Colab Zip
    zip_path = "UI WORK/UI_WORK_FOR_COLAB.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("UI WORK/android_project"):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, "UI WORK")
                zipf.write(full_p, rel_p)
        for root, dirs, files in os.walk("UI WORK/www"):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, "UI WORK")
                zipf.write(full_p, rel_p)
        zipf.write("UI WORK/jainagar_chunav.db", "jainagar_chunav.db")
    print(f"[OK] Re-packaged {zip_path} ({os.path.getsize(zip_path)} bytes)")

if __name__ == "__main__":
    main()

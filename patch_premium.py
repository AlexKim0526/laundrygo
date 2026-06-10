import re

with open('/sessions/beautiful-affectionate-cannon/mnt/outputs/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS 추가: 브랜드 배지, 잠금 배지 ──────────────────────────────────
css_add = """
    /* ── PREMIUM BRAND BADGES ── */
    .brand-badge {
      font-size: 10px; font-weight: 700;
      color: #7c5a00; background: #fff3cd;
      border-radius: 10px; padding: 2px 8px;
      display: inline-block; margin-top: 2px;
    }
    .auto-prem-lock {
      font-size: 10px; font-weight: 700;
      color: #6a0572; background: #f3e8ff;
      border-radius: 10px; padding: 2px 8px;
      display: inline-flex; align-items: center; gap: 3px;
      margin-top: 2px;
    }
    .prem-locked-row {
      opacity: 0.7; font-size: 11px; color: #888;
      padding: 4px 0; display: flex; align-items: center;
      justify-content: space-between;
    }
"""
html = html.replace('    /* ── TOAST ── */', css_add + '    /* ── TOAST ── */')

# ── 2. PREMIUM_BRANDS 데이터 + 헬퍼 (PMAP 정의 바로 뒤에 삽입) ─────────────
brand_data = """
// ═══════════════════════════════════════
// PREMIUM BRANDS (from 프리미엄브랜드.csv)
// ═══════════════════════════════════════
const PREMIUM_BRANDS = {
  'HERMÈS':          { kr:'에르메스',    scope:'all' },
  'CHANEL':          { kr:'샤넬',        scope:'all' },
  'LOUIS VUITTON':   { kr:'루이비통',    scope:'all' },
  'GUCCI':           { kr:'구찌',        scope:'all' },
  'PRADA':           { kr:'프라다',      scope:'all' },
  'BURBERRY':        { kr:'버버리',      scope:'all' },
  'CELINE':          { kr:'셀린느',      scope:'all' },
  'MONCLER':         { kr:'몽클레르',    scope:'all' },
  'VALENTINO':       { kr:'발렌티노',    scope:'all' },
  'FENDI':           { kr:'펜디',        scope:'all' },
  'DIOR':            { kr:'디올',        scope:'all' },
  'LORO PIANA':      { kr:'로로피아나',  scope:'all' },
  'MIU MIU':         { kr:'미우미우',    scope:'all' },
  'KITON':           { kr:'키톤',        scope:'all' },
  'MAXMARA':         { kr:'막스마라',    scope:'all' },
  'BALENCIAGA':      { kr:'발렌시아가',  scope:'all' },
  'BOTTEGA VENETA':  { kr:'보테가 베네타', scope:'all' },
  'THOM BROWNE':     { kr:'톰브라운',    scope:'all' },
  'POLO':            { kr:'폴로',        scope:'all' },
  'MOOSE KNUCKLES':  { kr:'무스너클',    scope:'padding' },
  'CANADA GOOSE':    { kr:'캐나다구스',  scope:'padding' },
  'STONE ISLAND':    { kr:'스톤아일랜드', scope:'padding' },
  'NOBIS':           { kr:'노비스',      scope:'padding' },
  'HERNO':           { kr:'에르노',      scope:'padding' },
};
const PADDING_ITEMS = new Set(['경량패딩','일반패딩','롱패딩점퍼','패딩조끼','패딩바지']);

// 브랜드명 → PREMIUM_BRANDS 매칭 (대소문자 무관)
function findPremiumBrand(brandStr) {
  if (!brandStr) return null;
  const s = brandStr.trim().toUpperCase();
  for (const [key, val] of Object.entries(PREMIUM_BRANDS)) {
    if (s.includes(key) || key.includes(s)) return val;
  }
  return null;
}
// 품목+브랜드 기준으로 자동 프리미엄 여부 판단
function isAutoPremium(itemName, brandStr) {
  const info = findPremiumBrand(brandStr);
  if (!info) return false;
  if (info.scope === 'all') return true;
  if (info.scope === 'padding' && PADDING_ITEMS.has(itemName)) return true;
  return false;
}

"""
html = html.replace(
    "// AI 인식용 품목 목록 — RAW에서 자동 생성\n// 쉼표 포함 품목명이 있으므로 따옴표로 감싸서 구분 명확화",
    brand_data + "// AI 인식용 품목 목록 — RAW에서 자동 생성\n// 쉼표 포함 품목명이 있으므로 따옴표로 감싸서 구분 명확화"
)

# ── 3. 프롬프트에 브랜드 인식 지시 추가 ──────────────────────────────────────
old_prompt = """    `반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력:\\n` +
    `{"items":[{"소분류":"재킷","수량":1}]}\\n` +
    `동일 품목이라도 합치지 말고 각각 별도 항목으로 나열하세요. 해당 품목 없으면 {"items":[]}`"""

new_prompt = """    `[브랜드 인식]\\n` +
    `아래 프리미엄 브랜드 로고·텍스트가 보이면 "브랜드" 필드에 영문명을 정확히 기재하세요:\\n` +
    `HERMÈS, CHANEL, LOUIS VUITTON, GUCCI, PRADA, BURBERRY, CELINE, MONCLER, VALENTINO, FENDI, DIOR, Loro Piana, MIU MIU, Kiton, MaxMara, BALENCIAGA, BOTTEGA VENETA, THOM BROWNE, Polo, MOOSE KNUCKLES, CANADA GOOSE, STONE ISLAND, nobis, HERNO\\n` +
    `브랜드 미확인 시 "브랜드" 필드 생략.\\n\\n` +
    `반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력:\\n` +
    `{"items":[{"소분류":"재킷","수량":1,"브랜드":"GUCCI"}]}\\n` +
    `동일 품목이라도 합치지 말고 각각 별도 항목으로 나열하세요. 해당 품목 없으면 {"items":[]}`"""

html = html.replace(old_prompt, new_prompt)

# ── 4. callClaude() 파싱: brand + autoPremium 필드 추가 ───────────────────────
old_parse = """  return (parsed.items || []).map((it, i) => ({
    name:  it.소분류,
    qty:   it.수량 || 1,
    thumb: photos[i % photos.length]
  }));"""

new_parse = """  return (parsed.items || []).map((it, i) => {
    const name  = it.소분류;
    const brand = it.브랜드 || null;
    return {
      name,
      qty:        it.수량 || 1,
      brand,
      autoPremium: isAutoPremium(name, brand),
      thumb:      photos[i % photos.length]
    };
  });"""

html = html.replace(old_parse, new_parse)

# ── 5. renderResult(): autoPremium 항목 자동으로 premiumSet에 추가 ─────────────
old_render_call = """  renderRows();
  renderFoot();
  renderUpsell();
  renderPremiumSection();
}"""

new_render_call = """  // 브랜드 자동 인식된 항목 premiumSet 선적용
  premiumSet = new Set();
  items.forEach((it, idx) => { if (it.autoPremium) premiumSet.add(idx); });
  renderRows();
  renderFoot();
  renderUpsell();
  renderPremiumSection();
}"""

html = html.replace(old_render_call, new_render_call, 1)

# ── 6. renderRows(): 브랜드 배지 표시 + autoPremium 잠금 ─────────────────────
old_prem_badge = "    const premBadge = isPrem ? `<div class=\"item-prem-badge\">✦ 프리미엄</div>` : '';\n\n    div.innerHTML = `\n      <div class=\"item-thumb\">\n        <img src=\"${it.thumb}\" alt=\"${it.name}\">\n        <button class=\"img-del-btn\" onclick=\"delItem(${idx})\">✕</button>\n      </div>\n      <div class=\"item-info\">\n        <div class=\"item-name\">${it.name}</div>\n        ${premBadge}\n      </div>"

new_prem_badge = """    const isAuto = it.autoPremium;
    let badgesHtml = '';
    if (it.brand) {
      const bInfo = findPremiumBrand(it.brand);
      const brandLabel = bInfo ? bInfo.kr : it.brand;
      badgesHtml += `<div class="brand-badge">${brandLabel}</div>`;
    }
    if (isPrem && isAuto) {
      badgesHtml += `<div class="auto-prem-lock">🔒 프리미엄 자동 적용</div>`;
    } else if (isPrem) {
      badgesHtml += `<div class="item-prem-badge">✦ 프리미엄</div>`;
    }

    div.innerHTML = `
      <div class="item-thumb">
        <img src="${it.thumb}" alt="${it.name}">
        <button class="img-del-btn" onclick="delItem(${idx})">✕</button>
      </div>
      <div class="item-info">
        <div class="item-name">${it.name}</div>
        ${badgesHtml}
      </div>"""

html = html.replace(old_prem_badge, new_prem_badge)

# ── 7. togglePremium(): autoPremium이면 변경 불가 ─────────────────────────────
old_toggle = """function togglePremium(idx) {
  if (premiumSet.has(idx)) premiumSet.delete(idx);
  else                      premiumSet.add(idx);"""

new_toggle = """function togglePremium(idx) {
  if (items[idx]?.autoPremium) return; // 브랜드 자동 적용은 변경 불가
  if (premiumSet.has(idx)) premiumSet.delete(idx);
  else                      premiumSet.add(idx);"""

html = html.replace(old_toggle, new_toggle)

# ── 8. renderPremiumSection(): autoPremium 항목 제외, 수동 추가 가능 항목만 표시 ──
old_prem_sec = """  const eligible = items.map((it, idx) => ({ it, idx, p: pLookup(it.name) }))
                        .filter(({ p }) => p && p.프리미엄 > 0);
  if (!eligible.length) { sec.innerHTML = ''; return; }
  sec.innerHTML = `
    <div class="premium-card">
      <div class="premium-card-title">✦ 프리미엄 서비스 추가</div>
      ${eligible.map(({ it, idx, p }) => {
        const on = premiumSet.has(idx);
        return `<div class="prem-item-row">
          <div class="prem-item-name">${it.name}</div>
          <div class="prem-item-price">${w(p.프리미엄 * it.qty)}원</div>
          <button class="prem-toggle-btn ${on ? 'remove' : 'add'}" onclick="togglePremium(${idx})">${on ? '취소' : '추가'}</button>
        </div>`;
      }).join('')}
    </div>`;"""

new_prem_sec = """  const allEligible = items.map((it, idx) => ({ it, idx, p: pLookup(it.name) }))
                          .filter(({ p }) => p && p.프리미엄 > 0);
  const autoItems   = allEligible.filter(({ it }) => it.autoPremium);
  const manualItems = allEligible.filter(({ it }) => !it.autoPremium);

  let html = '';
  // 자동 적용된 브랜드 프리미엄 안내
  if (autoItems.length) {
    html += `<div class="premium-card">
      <div class="premium-card-title">🔒 브랜드 프리미엄 자동 적용</div>
      ${autoItems.map(({ it, p }) => {
        const bInfo = findPremiumBrand(it.brand);
        return `<div class="prem-locked-row">
          <span>${it.name} <span class="brand-badge">${bInfo ? bInfo.kr : it.brand}</span></span>
          <span style="color:#7c5a00;font-weight:700">${w(p.프리미엄 * it.qty)}원</span>
        </div>`;
      }).join('')}
    </div>`;
  }
  // 수동 추가 가능한 프리미엄 항목
  if (manualItems.length) {
    html += `<div class="premium-card">
      <div class="premium-card-title">✦ 프리미엄 서비스 추가</div>
      ${manualItems.map(({ it, idx, p }) => {
        const on = premiumSet.has(idx);
        return `<div class="prem-item-row">
          <div class="prem-item-name">${it.name}</div>
          <div class="prem-item-price">${w(p.프리미엄 * it.qty)}원</div>
          <button class="prem-toggle-btn ${on ? 'remove' : 'add'}" onclick="togglePremium(${idx})">${on ? '취소' : '추가'}</button>
        </div>`;
      }).join('')}
    </div>`;
  }
  if (!html) { sec.innerHTML = ''; return; }
  sec.innerHTML = html;"""

html = html.replace(old_prem_sec, new_prem_sec)

# ── 9. 버전 업데이트 ──────────────────────────────────────────────────────────
html = html.replace(
    "const VERSION = 'v1.10.3'; // 2026-06-08  동일 품목 합산 제거, 개별 항목으로 나열",
    "const VERSION = 'v1.11.0'; // 2026-06-08  프리미엄 브랜드 자동 인식·적용·잠금"
)

with open('/sessions/beautiful-affectionate-cannon/mnt/outputs/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("done")

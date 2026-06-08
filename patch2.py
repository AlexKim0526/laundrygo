import re

src = '/sessions/beautiful-affectionate-cannon/mnt/outputs/index.html'
with open(src, encoding='utf-8') as f:
    html = f.read()

# ── 2. STATE 변수 교체 ──────────────────────────────────────────────────────
old_state = "let selectedCol = '정가'; // 선택된 가격 컬럼\nlet itemCols    = {};   // 개별 의류 컬럼 선택 override { idx: col }"
new_state = "let activeTab   = '일반';    // '일반' | '구독'\nlet premiumSet  = new Set(); // 프리미엄 선택된 item 인덱스"
if old_state in html:
    html = html.replace(old_state, new_state)
    print("State replaced OK")
else:
    print("State NOT found")

# ── 3. totals() 교체 ──────────────────────────────────────────────────────
old_totals = re.search(r'function totals\(\) \{.+?\n\}', html, re.DOTALL)
print("totals found:", bool(old_totals))
if old_totals:
    NEW_TOTALS = '''function totals() {
  let 정가=0, 구독=0, 차감=0, 구독현금=0, 실결제=0;
  items.forEach((it, idx) => {
    const p = PMAP[it.name]; if (!p) return;
    const q = it.qty;
    const isPrem = premiumSet.has(idx) && p.프리미엄 > 0;
    정가 += p.정가 * q;
    if (isPrem) {
      구독현금 += p.프리미엄 * q;
      실결제   += p.프리미엄 * q;
    } else {
      구독  += p.구독 * q;
      차감  += p.차감 * q;
      실결제 += p.정가 * q;
    }
  });
  return { 정가, 구독, 차감, 구독현금, 실결제 };
}'''
    html = html[:old_totals.start()] + NEW_TOTALS + html[old_totals.end():]
    print("totals replaced OK")

# ── 4. delItem() 교체 ──────────────────────────────────────────────────────
old_del = re.search(r'function delItem\(idx\) \{.+?\n\}', html, re.DOTALL)
print("delItem found:", bool(old_del))
if old_del:
    NEW_DEL = '''function delItem(idx) {
  items.splice(idx, 1);
  premiumSet = new Set([...premiumSet].filter(i => i !== idx).map(i => i > idx ? i - 1 : i));
  if (!items.length) {
    renderResult();
  } else {
    renderRows();
    renderFoot();
    renderUpsell();
    renderPremiumSection();
  }
}'''
    html = html[:old_del.start()] + NEW_DEL + html[old_del.end():]
    print("delItem replaced OK")

# ── 5. renderResult() 교체 ──────────────────────────────────────────────────
old_rr = re.search(r'function renderResult\(\) \{.+?\n\}', html, re.DOTALL)
print("renderResult found:", bool(old_rr))
if old_rr:
    NEW_RR = '''function renderResult() {
  const body = document.getElementById('resultBody');
  if (!items.length) {
    body.innerHTML = `<div class="empty"><span class="empty-ico">🔍</span>의류를 인식하지 못했어요.<br>다시 촬영해주세요.</div>`;
    return;
  }
  activeTab  = '일반';
  premiumSet = new Set();
  const t = totals();
  body.innerHTML = `
    <div class="summary-card">
      <div class="summary-price"><span id="sumLabel">총 예상 세탁비는</span> <span class="price-num" id="sumNum">${w(t.실결제)}</span><span id="sumUnit">원</span> 이예요</div>
    </div>
    <div class="upsell-card" id="upsellCard"></div>
    <div class="sub-upsell-card" id="subUpsellCard"></div>
    <div class="tab-bar">
      <button class="tab-btn active"   data-tab="일반" onclick="selectTab('일반')">일반 고객</button>
      <button class="tab-btn inactive" data-tab="구독" onclick="selectTab('구독')">구독 회원</button>
    </div>
    <div class="table-card">
      <div id="rowsWrap"></div>
      <div class="table-foot" id="footWrap"></div>
    </div>
    <div id="premiumSection"></div>
  `;
  renderRows();
  renderFoot();
  renderUpsell();
  renderPremiumSection();
}'''
    html = html[:old_rr.start()] + NEW_RR + html[old_rr.end():]
    print("renderResult replaced OK")

# ── 6. renderRows() 교체 ──────────────────────────────────────────────────
old_rows = re.search(r'function renderRows\(\) \{.+?\n\}', html, re.DOTALL)
print("renderRows found:", bool(old_rows))
if old_rows:
    NEW_ROWS = '''function renderRows() {
  const wrap = document.getElementById('rowsWrap');
  if (!wrap) return;
  wrap.innerHTML = '';
  items.forEach((it, idx) => {
    const p = PMAP[it.name];
    if (!p) return;
    const q = it.qty;
    const isPrem = premiumSet.has(idx) && p.프리미엄 > 0;
    const div = document.createElement('div');
    div.className = 'item-row';
    div.style.animationDelay = `${idx * 0.07}s`;

    let priceHtml = '';
    if (activeTab === '일반') {
      if (isPrem) {
        priceHtml = `<div class="item-price-col"><div class="price-main prem">${w(p.프리미엄 * q)}원</div></div>`;
      } else {
        priceHtml = `<div class="item-price-col"><div class="price-main">${w(p.정가 * q)}원</div></div>`;
      }
    } else {
      if (isPrem) {
        priceHtml = `<div class="item-price-col"><div class="price-main prem">${w(p.프리미엄 * q)}원</div><div class="price-sub">현금 결제</div></div>`;
      } else {
        const creditText = p.차감 * q > 0 ? `세탁권 ${p.차감 * q}개` : `${w(p.구독 * q)}원`;
        const subText    = p.차감 * q > 0 ? `소진시 ${w(p.구독 * q)}원` : '';
        priceHtml = `<div class="item-price-col"><div class="credit-main">${creditText}</div>${subText ? `<div class="credit-sub">${subText}</div>` : ''}</div>`;
      }
    }
    const premBadge = isPrem ? `<div class="item-prem-badge">✦ 프리미엄</div>` : '';

    div.innerHTML = `
      <div class="item-thumb">
        <img src="${it.thumb}" alt="${it.name}">
        <button class="img-del-btn" onclick="delItem(${idx})">✕</button>
      </div>
      <div class="item-info">
        <div class="item-name">${it.name}</div>
        ${premBadge}
      </div>
      ${priceHtml}
    `;
    wrap.appendChild(div);
  });
}'''
    html = html[:old_rows.start()] + NEW_ROWS + html[old_rows.end():]
    print("renderRows replaced OK")

# ── 7. renderFoot() 교체 ──────────────────────────────────────────────────
old_foot = re.search(r'function renderFoot\(\) \{.+?\n\}', html, re.DOTALL)
print("renderFoot found:", bool(old_foot))
if old_foot:
    NEW_FOOT = '''function renderFoot() {
  const f = document.getElementById('footWrap');
  if (!f) return;
  const t = totals();
  let inner = '';
  if (activeTab === '일반') {
    inner = `<div class="foot-label">합계</div>
      <div class="foot-total"><div class="foot-price-main">${w(t.실결제)}원</div></div>`;
  } else {
    if (t.차감 > 0 && t.구독현금 > 0) {
      inner = `<div class="foot-label">합계</div>
        <div class="foot-total">
          <div class="foot-price-main" style="color:#c05000">세탁권 ${t.차감}개</div>
          <div class="foot-price-sub">+ ${w(t.구독현금)}원 현금 추가</div>
        </div>`;
    } else if (t.차감 > 0) {
      inner = `<div class="foot-label">합계</div>
        <div class="foot-total">
          <div class="foot-price-main" style="color:#c05000">세탁권 ${t.차감}개</div>
          <div class="foot-price-sub">소진시 ${w(t.구독)}원</div>
        </div>`;
    } else {
      inner = `<div class="foot-label">합계</div>
        <div class="foot-total"><div class="foot-price-main">${w(t.구독현금)}원</div></div>`;
    }
  }
  f.innerHTML = inner;
  updateSummary();
}'''
    html = html[:old_foot.start()] + NEW_FOOT + html[old_foot.end():]
    print("renderFoot replaced OK")

# ── 8. 기존 COLUMN SELECTION 섹션 전체 교체 (selectCol ~ updateSummary) ──
old_col_sec = re.search(
    r'// ═+\n// COLUMN SELECTION\n// ═+\nfunction getItemCol.+?^}',
    html, re.DOTALL | re.MULTILINE
)
print("ColSection found:", bool(old_col_sec))
if old_col_sec:
    NEW_COL_SEC = '''// ═══════════════════════════════════════
// TAB & PREMIUM SELECTION
// ═══════════════════════════════════════
function selectTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.tab-btn').forEach(el => {
    el.classList.toggle('active',   el.dataset.tab === tab);
    el.classList.toggle('inactive', el.dataset.tab !== tab);
  });
  renderRows();
  renderFoot();
  renderUpsell();
}

function togglePremium(idx) {
  if (premiumSet.has(idx)) premiumSet.delete(idx);
  else                      premiumSet.add(idx);
  renderRows();
  renderFoot();
  renderPremiumSection();
  updateSummary();
}

function renderPremiumSection() {
  const sec = document.getElementById('premiumSection');
  if (!sec) return;
  const eligible = items.map((it, idx) => ({ it, idx, p: PMAP[it.name] }))
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
    </div>`;
}

function updateSummary() {
  const t = totals();
  const sn = document.getElementById('sumNum');
  const su = document.getElementById('sumUnit');
  const sl = document.getElementById('sumLabel');
  if (!sn) return;
  if (activeTab === '일반') {
    sl && (sl.textContent = '총 예상 세탁비는');
    sn.textContent = w(t.실결제);
    su && (su.textContent = '원');
  } else {
    if (t.차감 > 0) {
      sl && (sl.textContent = '총 필요 세탁권은');
      sn.textContent = t.차감;
      su && (su.textContent = '개');
    } else {
      sl && (sl.textContent = '총 예상 세탁비는');
      sn.textContent = w(t.구독현금);
      su && (su.textContent = '원');
    }
  }
}'''
    html = html[:old_col_sec.start()] + NEW_COL_SEC + html[old_col_sec.end():]
    print("ColSection replaced OK")

# ── 9. renderUpsell() 교체 ──────────────────────────────────────────────────
old_upsell_fn = re.search(r'function renderUpsell\(\) \{.+?\n\}', html, re.DOTALL)
print("renderUpsell found:", bool(old_upsell_fn))
if old_upsell_fn:
    NEW_UPSELL = '''function renderUpsell() {
  const el    = document.getElementById('upsellCard');
  const subEl = document.getElementById('subUpsellCard');
  if (!el) return;
  const t = totals();

  if (activeTab === '일반') {
    if (subEl) subEl.classList.remove('show');
    const u = getUpsell(t.실결제);
    if (!u) { el.classList.remove('show'); return; }
    const barHtml = u.progress < 1
      ? `<div class="upsell-bar-wrap"><div class="upsell-bar" style="width:${Math.min(u.progress*100,100).toFixed(1)}%;background:${u.color}"></div></div>`
      : '';
    el.className = `upsell-card show${u.type === 'achieve' ? ' upsell-achieve' : ''}`;
    el.style.borderColor = u.color + '88';
    el.innerHTML = `
      <div class="upsell-top">
        <span class="upsell-icon">${u.icon}</span>
        <div class="upsell-body">
          <div class="upsell-msg">${u.msg}</div>
          <div class="upsell-sub">${u.sub}</div>
        </div>
      </div>
      ${barHtml}
    `;
  } else {
    el.classList.remove('show');
    if (subEl) {
      // 세탁권이 0인데 품목이 있으면 → 전부 프리미엄 현금 결제
      if (t.차감 === 0 && t.구독현금 > 0) {
        subEl.classList.remove('show');
      } else {
        subEl.classList.remove('show');
      }
    }
  }
}'''
    html = html[:old_upsell_fn.start()] + NEW_UPSELL + html[old_upsell_fn.end():]
    print("renderUpsell replaced OK")

with open(src, 'w', encoding='utf-8') as f:
    f.write(html)
print("\\nAll done — file written")

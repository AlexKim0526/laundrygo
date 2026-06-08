import os, re

src = '/sessions/beautiful-affectionate-cannon/mnt/outputs/index.html'
with open(src, encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS: 기존 테이블/컬럼/셀 CSS 전체 교체 ──────────────────────────────
old_css = re.search(
    r'/\* 가로 스크롤 래퍼 \*/.+?\.price-cell\.cell-selected \{[^}]+\}',
    html, re.DOTALL
)
print("CSS block found:", bool(old_css))

NEW_CSS = '''/* ── TABS ── */
    .tab-bar { display: flex; gap: 6px; margin-bottom: 10px; }
    .tab-btn {
      flex: 1; padding: 10px 0; text-align: center;
      font-size: 13px; font-weight: 700; border-radius: 12px;
      border: none; cursor: pointer;
      transition: background 0.15s, color 0.15s;
    }
    .tab-btn.active  { background: #111; color: #fff; }
    .tab-btn.inactive { background: #fff; color: #999; border: 1.5px solid #e0e0e0; }

    /* ── TABLE CARD ── */
    .table-card {
      background: #fff; border-radius: 18px;
      box-shadow: 0 1px 6px rgba(0,0,0,0.06);
      margin-bottom: 10px; overflow: hidden;
      padding: 0 14px;
    }
    .item-row {
      display: flex; align-items: center; gap: 10px;
      padding: 12px 0; border-bottom: 1px solid #f2f2f2;
      animation: fadeUp 0.25s ease forwards; opacity: 0;
    }
    .item-row:last-child { border-bottom: none; }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(5px); }
      to   { opacity: 1; transform: none; }
    }
    .item-thumb {
      width: 44px; height: 44px; border-radius: 8px;
      flex-shrink: 0; position: relative;
      background: #f0f0f0;
    }
    .item-thumb img { width: 100%; height: 100%; border-radius: 8px; object-fit: cover; display: block; }
    .img-del-btn {
      position: absolute; top: -5px; right: -5px;
      width: 17px; height: 17px; border-radius: 50%;
      background: #FF3B30; border: 1.5px solid #fff;
      cursor: pointer; display: flex; align-items: center; justify-content: center;
      font-size: 8px; font-weight: 900; color: #fff; line-height: 1; padding: 0;
    }
    .item-info { flex: 1; min-width: 0; }
    .item-name { font-size: 13px; font-weight: 600; color: #111; word-break: keep-all; line-height: 1.3; }
    .item-prem-badge {
      display: inline-flex; align-items: center; gap: 3px;
      background: #f3eeff; color: #6D28D9;
      font-size: 10px; font-weight: 700; border-radius: 5px; padding: 2px 6px;
      margin-top: 3px;
    }
    .item-price-col { text-align: right; flex-shrink: 0; }
    .price-main       { font-size: 14px; font-weight: 700; color: #111; white-space: nowrap; }
    .price-main.prem  { color: #6D28D9; }
    .price-sub        { font-size: 11px; color: #999; margin-top: 2px; white-space: nowrap; }
    .credit-main      { font-size: 14px; font-weight: 700; color: #c05000; white-space: nowrap; }
    .credit-sub       { font-size: 11px; color: #999; margin-top: 2px; white-space: nowrap; }
    /* 합계 푸터 */
    .table-foot {
      display: flex; justify-content: space-between; align-items: center;
      padding: 12px 0; border-top: 1.5px solid #efefef;
    }
    .foot-label       { font-size: 14px; font-weight: 800; color: #111; }
    .foot-total       { text-align: right; }
    .foot-price-main  { font-size: 15px; font-weight: 800; color: #FF3B30; white-space: nowrap; }
    .foot-price-sub   { font-size: 11px; color: #999; margin-top: 2px; white-space: nowrap; }

    /* ── PREMIUM SECTION ── */
    .premium-card {
      background: #faf7ff; border-radius: 18px;
      box-shadow: 0 1px 6px rgba(0,0,0,0.06);
      margin-bottom: 10px; padding: 14px 16px;
      border: 1px solid #e8d8ff;
    }
    .premium-card-title {
      font-size: 13px; font-weight: 700; color: #6D28D9;
      margin-bottom: 10px;
    }
    .prem-item-row {
      display: flex; align-items: center; gap: 10px;
      padding: 9px 0; border-bottom: 0.5px solid #ede8fb;
    }
    .prem-item-row:last-child { border-bottom: none; }
    .prem-item-name  { flex: 1; font-size: 13px; color: #333; }
    .prem-item-price { font-size: 13px; font-weight: 700; color: #6D28D9; flex-shrink: 0; margin-right: 8px; white-space: nowrap; }
    .prem-toggle-btn {
      font-size: 11px; font-weight: 700; border: none; border-radius: 7px;
      padding: 5px 10px; cursor: pointer; flex-shrink: 0;
      transition: background 0.15s;
    }
    .prem-toggle-btn.add    { background: #6D28D9; color: #fff; }
    .prem-toggle-btn.add:hover { background: #5B21B6; }
    .prem-toggle-btn.remove { background: #ede8fb; color: #6D28D9; }

    /* ── 구독 탭 업셀 ── */
    .sub-upsell-card {
      background: #edfaf3; border-radius: 14px;
      padding: 12px 14px; margin-bottom: 10px;
      border: 1px solid #86efac; display: none;
    }
    .sub-upsell-card.show { display: block; }
    .sub-upsell-msg { font-size: 13px; color: #166534; line-height: 1.5; }
    .sub-upsell-msg strong { font-weight: 700; }'''

if old_css:
    html = html[:old_css.start()] + NEW_CSS + html[old_css.end():]
    print("CSS replaced OK")
else:
    print("CSS block NOT found — skipping")

print("Done step 1")
with open(src, 'w', encoding='utf-8') as f:
    f.write(html)

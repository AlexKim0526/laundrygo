/**
 * 런드리고 세탁 견적 API 서버
 * Claude Vision API를 프록시하여 API 키를 서버에서 안전하게 관리합니다.
 *
 * 사용법:
 *   npm install express cors @anthropic-ai/sdk dotenv
 *   ANTHROPIC_API_KEY=sk-ant-... node server.js
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({ origin: process.env.ALLOWED_ORIGIN || '*' }));
app.use(express.json({ limit: '10mb' }));
app.use(express.static('.'));   // index.html 정적 서빙

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// 품목별 고정 요금표
const PRICE_TABLE = {
  '셔츠': 5000, '블라우스': 5000, '티셔츠': 4000,
  '바지': 7000, '청바지': 7000, '슬랙스': 7000,
  '원피스': 10000, '재킷': 12000, '자켓': 12000, '점퍼': 12000,
  '코트': 15000, '치마': 6000, '스커트': 6000,
  '니트': 8000, '스웨터': 8000, '가디건': 8000,
  '정장상의': 10000, '정장하의': 8000, '양복': 18000,
  '넥타이': 3000, '스카프': 3000, '머플러': 3000,
  '패딩': 15000, '다운': 15000,
};

/**
 * POST /api/analyze
 * body: { image: "<base64>", mediaType: "image/jpeg" }
 * returns: { items: [...], total: number }
 */
app.post('/api/analyze', async (req, res) => {
  const { image, mediaType = 'image/jpeg' } = req.body;

  if (!image) {
    return res.status(400).json({ error: '이미지 데이터가 없습니다.' });
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: 'API 키가 설정되지 않았습니다.' });
  }

  try {
    const message = await client.messages.create({
      model: 'claude-opus-4-6',
      max_tokens: 1024,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'image',
            source: { type: 'base64', media_type: mediaType, data: image },
          },
          {
            type: 'text',
            text: `이 이미지에서 세탁 가능한 의류 품목들을 인식해주세요.

다음 JSON 형식으로만 응답해주세요 (다른 텍스트 없이):
{
  "items": [
    {
      "name": "품목명(한국어)",
      "category": "카테고리(셔츠/블라우스/티셔츠/바지/청바지/원피스/재킷/코트/치마/니트/스웨터/정장상의/정장하의/넥타이/스카프/패딩 중 하나)",
      "quantity": 수량(숫자),
      "condition": "상태(깨끗함/보통/오염 중 하나)",
      "material_note": "소재 특이사항(없으면 null)"
    }
  ]
}

의류가 전혀 보이지 않으면 {"items": []}`,
          },
        ],
      }],
    });

    const text = message.content[0].text.trim();
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error('AI 응답 파싱 실패');

    const parsed = JSON.parse(jsonMatch[0]);
    const items = (parsed.items || []).map(item => {
      const catKey = Object.keys(PRICE_TABLE).find(k =>
        (item.category || '').includes(k) || (item.name || '').includes(k)
      ) || '셔츠';
      const unitPrice = PRICE_TABLE[catKey] || 5000;
      const qty = item.quantity || 1;
      return { ...item, unitPrice, subtotal: unitPrice * qty };
    });

    const total = items.reduce((sum, i) => sum + i.subtotal, 0);
    res.json({ items, total });

  } catch (err) {
    console.error('분석 오류:', err.message);
    res.status(500).json({ error: err.message || '분석 중 오류가 발생했습니다.' });
  }
});

// 요금표 조회
app.get('/api/prices', (req, res) => {
  res.json({ prices: PRICE_TABLE });
});

app.listen(PORT, () => {
  console.log(`런드리고 견적 서버 실행 중: http://localhost:${PORT}`);
});

/**
 * 런드리고 세탁 견적 API 서버
 * Claude Vision API를 프록시하여 API 키를 서버에서 안전하게 관리합니다.
 *
 * 사용법:
 *   npm install express cors @anthropic-ai/sdk
 *   node server.js
 */

const express = require('express');
const cors    = require('cors');
const https   = require('https');

const app  = express();
const PORT = process.env.PORT || 3000;

// ── API 키 (환경변수 우선, 없으면 내장 키 사용) ─────────────────────────────
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
if (!ANTHROPIC_API_KEY) {
  console.error('❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.');
  process.exit(1);
}

// 세탁 카테고리 목록 (클라이언트와 동기화)
const CATS = `와이셔츠,일반셔츠,티셔츠,바지,청바지,면바지,슬랙스,반바지,원피스,재킷,자켓,정장재킷,트위드재킷,가죽재킷,블레이저,슈트(2피스),슈트(3피스),코트,트렌치코트,울코트,가죽코트,점퍼,패딩,일반패딩,경량패딩,롱패딩점퍼,가디건,니트,스웨터,블라우스,스커트,치마,레깅스,운동복상의,운동복하의,수영복,한복(상하의),한복(치마저고리),넥타이,스카프,머플러,모자,벨트,가방,구두,스니커즈,운동화,부츠,샌들,슬리퍼,이불(솜이불),이불(순면),베개커버,침대패드,담요,쿠션커버`;

app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '20mb' }));
app.use(express.static('.'));   // index.html 정적 서빙

/**
 * POST /api/analyze
 * body: { photos: ["base64string", ...] }
 * returns: { items: [{name, qty, brand, autoPremium, photoIdx}, ...] }
 */
app.post('/api/analyze', async (req, res) => {
  const { photos } = req.body;

  if (!photos || !Array.isArray(photos) || photos.length === 0) {
    return res.status(400).json({ error: '사진 데이터가 없습니다.' });
  }

  // 멀티 이미지 content 블록 구성 (클라이언트 callClaude와 동일 구조)
  const content = photos.flatMap((b64, idx) => [
    { type: 'text', text: `[사진 ${idx + 1}]` },
    { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: b64 } }
  ]);

  content.push({ type: 'text', text:
    `각 사진에서 세탁이 필요한 의류/신발/잡화를 모두 찾아주세요.\n` +
    `아래 목록에 있는 이름을 정확히 그대로 사용하세요:\n${CATS}\n\n` +
    `[분류 기준]\n` +
    `- 셔츠: 캐주얼/일반 버튼다운 셔츠 → "일반셔츠" / 포멀 드레스셔츠 → "와이셔츠" / 라운드·V넥 티셔츠 + 폴로셔츠(카라티, 2~3개 반버튼) → "티셔츠" (칼라가 있어도 전체 버튼다운이 아니면 티셔츠로 분류, 세 가지 엄격 구분)\n` +
    `- 패딩 길이: 모자 제외 100cm 이상 → "롱패딩점퍼" / 얇고 가벼운 패딩 → "경량패딩" / 그 외 → "일반패딩"\n\n` +
    `[브랜드 인식]\n` +
    `의류·잡화에 브랜드 로고, 텍스트, 패턴이 보이면 반드시 "브랜드" 필드에 기재하세요.\n` +
    `프리미엄 브랜드: HERMÈS, CHANEL, LOUIS VUITTON, GUCCI, PRADA, BURBERRY, CELINE, MONCLER, VALENTINO, FENDI, DIOR, Loro Piana, MIU MIU, Kiton, MaxMara, BALENCIAGA, BOTTEGA VENETA, THOM BROWNE, MOOSE KNUCKLES, CANADA GOOSE, STONE ISLAND, nobis, HERNO, Polo\n` +
    `브랜드가 전혀 보이지 않을 때만 "브랜드" 필드 생략.\n\n` +
    `반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력:\n` +
    `{"items":[{"소분류":"재킷","수량":1,"브랜드":"GUCCI","사진":1}]}\n` +
    `- "사진" 필드에는 해당 품목이 나온 사진 번호(1부터 시작)를 반드시 기재하세요.\n` +
    `- 동일 품목이라도 합치지 말고 각각 별도 항목으로 나열하세요. 해당 품목 없으면 {"items":[]}`
  });

  // Anthropic API 직접 호출 (node https 모듈, SDK 의존성 제거)
  const bodyStr = JSON.stringify({
    model: 'claude-sonnet-4-6',
    max_tokens: 1024,
    messages: [{ role: 'user', content }]
  });

  const options = {
    hostname: 'api.anthropic.com',
    path: '/v1/messages',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'Content-Length': Buffer.byteLength(bodyStr)
    }
  };

  const apiReq = https.request(options, (apiRes) => {
    let data = '';
    apiRes.on('data', chunk => { data += chunk; });
    apiRes.on('end', () => {
      try {
        const d = JSON.parse(data);
        if (apiRes.statusCode !== 200) {
          return res.status(apiRes.statusCode).json({ error: d.error?.message || 'API 오류' });
        }

        const raw = d?.content?.[0]?.text ?? '';
        if (!raw) return res.status(500).json({ error: 'AI 응답이 비어있습니다.' });

        const m = raw.match(/\{[\s\S]*\}/);
        if (!m) return res.status(500).json({ error: '품목을 인식하지 못했습니다.' });

        const parsed = JSON.parse(m[0]);
        res.json({ items: parsed.items || [] });
      } catch (e) {
        res.status(500).json({ error: e.message || '응답 파싱 실패' });
      }
    });
  });

  apiReq.on('error', (e) => {
    console.error('API 요청 오류:', e.message);
    res.status(500).json({ error: e.message });
  });

  apiReq.write(bodyStr);
  apiReq.end();
});

// 헬스체크
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

app.listen(PORT, () => {
  console.log(`런드리고 견적 서버 실행 중: http://localhost:${PORT}`);
});

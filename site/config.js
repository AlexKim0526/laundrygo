// 광고센터 설정: Apps Script를 '웹 앱'으로 배포한 뒤 받은 주소를 아래 따옴표 안에 넣어 주세요.
window.ADC_API = 'https://script.google.com/macros/s/AKfycbzTt2Tcg2bMQoYIc1KPB2j9EwmGE7r0NjK9-ladr51X_14yPeP-Rm_lzXakReNioTwA/exec';

// 대량세탁 문의에서 '런드리고 앱에서 바로 신청하기'를 누르면 여는 앱 설치 주소. 휴대폰 종류에 맞춰 골라요.
// web: PC에서 열 주소 (비우면 PC에서는 스토어 버튼 두 개를 보여 줘요)
window.LG_APP_URL = {
  ios: 'https://apps.apple.com/kr/app/id1453485913',
  android: 'https://play.google.com/store/apps/details?id=com.laundrygo.android',
  web: ''
};

// 주소 검색에 쓰는 런드리고 API 주소 (고객 브라우저가 직접 호출). 테스트 서버로 바꿀 때만 고쳐요.
window.LG_API_BASE = 'https://api.laundrygo.com';

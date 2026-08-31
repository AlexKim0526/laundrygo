/**
 * 과제 보드 백엔드 (Google Apps Script)
 * -----------------------------------------------------------------
 * 이 스크립트를 과제 관리용 구글 시트에 붙여서 "웹 앱"으로 배포하면,
 * GitHub Pages 등에 올린 정적 프론트엔드(index.html)가 이 URL로
 * fetch() 요청을 보내 과제를 읽고/쓰고/지울 수 있어요.
 *
 * 데이터는 이 스프레드시트 안의 "AppData"라는 별도 탭에 저장돼요.
 * (사람이 보는 원래 "26년 9월 과제 리스트" 탭은 건드리지 않아요 —
 *  형식이 자유로운 사람용 표라서 프로그램이 안전하게 읽고 쓰기엔
 *  적합하지 않아, 앱 전용 탭을 새로 둔 거예요.)
 *
 * 설치 방법
 * 1) 구글 시트 상단 메뉴에서 확장 프로그램 > Apps Script 를 눌러요.
 * 2) 기본으로 있던 코드를 지우고, 이 파일 내용을 통째로 붙여넣어요.
 * 3) 저장한 뒤 배포 > 새 배포를 눌러요.
 *    - 유형: 웹 앱
 *    - 실행 계정: 나 (본인 계정)
 *    - 액세스 권한: 전체 공개 ("Anyone")
 *      ※ GitHub Pages처럼 로그인 세션이 없는 외부 페이지에서 호출하려면
 *        이 설정이 필요해요. 즉, 이 배포 URL을 아는 사람은 로그인 없이도
 *        이 시트의 AppData 탭을 읽고 쓸 수 있게 돼요. 사내 일정 관리용
 *        정도의 민감도라면 보통 괜찮지만, 원치 않으면 이 방식 대신
 *        Firebase 같은 별도 데이터베이스를 쓰는 걸 권장해요.
 * 4) 배포 후 나오는 웹 앱 URL(.../exec 로 끝나는 주소)을 복사해서
 *    index.html 위쪽의 API_URL 값에 붙여넣어요.
 * 5) 코드를 수정할 때마다(예: 이 스크립트를 업데이트할 때) 배포 화면에서
 *    "배포 관리 > 수정 > 새 버전"으로 다시 배포해야 반영돼요.
 */

var SHEET_NAME = 'AppData';
var HEADERS = [
  'id', 'category', 'title', 'dept', 'startDate', 'endDate',
  'planEffort', 'devEffort', 'priority', 'planOwners', 'devOwners',
  'metric', 'detail', 'author', 'updatedAt'
];

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function jsonOutput_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function formatDate_(v) {
  if (v instanceof Date) {
    return Utilities.formatDate(v, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  }
  if (!v) return '';
  return String(v);
}

function rowToTask_(headers, row) {
  var obj = {};
  for (var i = 0; i < headers.length; i++) {
    obj[headers[i]] = row[i];
  }
  obj.planOwners = obj.planOwners
    ? String(obj.planOwners).split(',').map(function (s) { return s.trim(); }).filter(Boolean)
    : [];
  obj.devOwners = obj.devOwners
    ? String(obj.devOwners).split(',').map(function (s) { return s.trim(); }).filter(Boolean)
    : [];
  obj.startDate = formatDate_(obj.startDate);
  obj.endDate = formatDate_(obj.endDate);
  return obj;
}

function taskToRow_(task) {
  return HEADERS.map(function (h) {
    if (h === 'planOwners') return (task.planOwners || []).join(',');
    if (h === 'devOwners') return (task.devOwners || []).join(',');
    if (h === 'updatedAt') return new Date().toISOString();
    return (task[h] !== undefined && task[h] !== null) ? task[h] : '';
  });
}

function findRowIndexById_(sheet, id) {
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return -1;
  var ids = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
  for (var i = 0; i < ids.length; i++) {
    if (String(ids[i][0]) === String(id)) return i + 2; // 1-indexed, +1 for header row
  }
  return -1;
}

function doGet(e) {
  var sheet = getSheet_();
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var rows = data.slice(1).filter(function (r) { return r[0]; }); // skip blank rows
  var tasks = rows.map(function (r) { return rowToTask_(headers, r); });
  return jsonOutput_({ ok: true, tasks: tasks });
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
  } catch (lockErr) {
    return jsonOutput_({ ok: false, error: '다른 저장 작업이 진행 중이에요. 잠시 후 다시 시도해 주세요.' });
  }
  try {
    var body = JSON.parse(e.postData.contents);
    var action = body.action;

    if (action === 'save') {
      saveTask_(body.task);
      return jsonOutput_({ ok: true });
    }
    if (action === 'delete') {
      deleteTask_(body.id);
      return jsonOutput_({ ok: true });
    }
    if (action === 'seed') {
      seedTasks_(body.tasks || []);
      return jsonOutput_({ ok: true });
    }
    return jsonOutput_({ ok: false, error: 'unknown action: ' + action });
  } catch (err) {
    return jsonOutput_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function saveTask_(task) {
  if (!task || !task.id) throw new Error('task.id is required');
  var sheet = getSheet_();
  var rowValues = taskToRow_(task);
  var rowIdx = findRowIndexById_(sheet, task.id);
  if (rowIdx === -1) {
    sheet.appendRow(rowValues);
  } else {
    sheet.getRange(rowIdx, 1, 1, HEADERS.length).setValues([rowValues]);
  }
}

function deleteTask_(id) {
  if (!id) throw new Error('id is required');
  var sheet = getSheet_();
  var rowIdx = findRowIndexById_(sheet, id);
  if (rowIdx !== -1) sheet.deleteRow(rowIdx);
}

function seedTasks_(tasksToSeed) {
  var sheet = getSheet_();
  if (sheet.getLastRow() > 1) return; // already has data — never overwrite silently
  tasksToSeed.forEach(function (t) { saveTask_(t); });
}

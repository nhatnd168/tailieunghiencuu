/**
 * Xcons Group - KQKD Dashboard
 * Entry point: serves the dashboard web app and exposes the single
 * data-fetching endpoint the client calls via google.script.run.
 */

var SPREADSHEET_ID = '1yupX8VZqHs5mqNRipVPDvJL5iwGCzUgOe8WQEVbrmyI';

function doGet(e) {
  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('Xcons Group - Dashboard KQKD')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/** Allows index.html to <?!= include('file') ?> other files if ever split further. */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/**
 * Single data endpoint called by the client on load / refresh.
 * Reads every sheet fresh (no caching) so figures are always current,
 * and parses each one according to its real report structure rather
 * than assuming row 1 is a usable header everywhere.
 */
function getDashboardData() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  return {
    meta: buildMeta_(ss),
    pnl: parseQuarterlyReport_(ss, 'P&L (3)'),
    slLuong: parseQuarterlyReport_(ss, 'SL&Lương'),
    hopDongTonTongHop: parseHopDongTonTongHop_(ss),
    hopDongTonTK: parseHopDongTonChiTiet_(ss, 'HĐ tồn_TK'),
    hopDongTonTC: parseHopDongTonChiTiet_(ss, 'HĐ tồn_TC'),
    cpCoDinh: parseCPCoDinh_(ss),
    kmp: parseKMP_(ss),
    nsLuong: parseNSLuong_(ss),
    cpThueDuPhong: parseCPThueDuPhong_(ss),
    cp: parseCP_(ss),
    khauHao: parseKhauHao_(ss),
    chiTietPhi: parseChiTietPhi_(ss)
  };
}

function buildMeta_(ss) {
  return {
    name: ss.getName(),
    id: ss.getId(),
    url: ss.getUrl(),
    timezone: ss.getSpreadsheetTimeZone(),
    generatedAt: new Date().toISOString()
  };
}

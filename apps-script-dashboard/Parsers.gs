/**
 * Sheet parsers.
 *
 * None of these hardcode a row/column range: every parser reads the full
 * used range via getDataRange()/getLastRow() and locates its header row
 * and section markers by matching the anchor text the report template
 * always contains ("TT", "Mã dự án", roman-numeral group codes, the
 * A/B/C KẾ HOẠCH / THỰC HIỆN / CHÊNH LỆCH markers, ...). The number of
 * period columns (quarterly Quý1..4 vs monthly Tháng1..12 / Thực hiện
 * T1..12) is likewise detected from the header via detectPeriodColumns_,
 * not assumed - so the dashboard keeps working whether the source sheet
 * reports quarterly or monthly, and as rows are added in future periods.
 */

// ---- generic helpers --------------------------------------------------

function getValues_(ss, sheetName) {
  var sh = ss.getSheetByName(sheetName);
  if (!sh) return [];
  var lastRow = sh.getLastRow();
  var lastCol = sh.getLastColumn();
  if (lastRow === 0 || lastCol === 0) return [];
  return sh.getRange(1, 1, lastRow, lastCol).getValues();
}

function findRow_(data, colIdx, matchFn, fromRow) {
  fromRow = fromRow || 0;
  for (var r = fromRow; r < data.length; r++) {
    if (matchFn(data[r][colIdx])) return r;
  }
  return -1;
}

function textEq_(a, b) {
  return String(a || '').trim().toUpperCase() === String(b).trim().toUpperCase();
}

function isRoman_(v) {
  return typeof v === 'string' && /^[IVXLCDM]+\.?$/.test(v.trim());
}

function isSectionCode_(v) {
  return typeof v === 'string' && ['A', 'B', 'C'].indexOf(v.trim()) !== -1;
}

function num_(v) {
  return (typeof v === 'number' && !isNaN(v)) ? v : 0;
}

function str_(v) {
  return String(v || '').trim();
}

function normalizeAscii_(v) {
  return String(v || '')
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().trim();
}

/**
 * Scans a header row starting at startCol and collects consecutive period
 * labels (quarters, months, ...) until it hits the "Tổng" column. The
 * report template switches between quarterly and monthly cadence from one
 * period to the next, so callers must never assume a fixed column count -
 * this makes the number of periods (and where "Tổng"/the next column
 * live) derived from the sheet itself.
 */
function detectPeriodColumns_(header, startCol) {
  var labels = [];
  var c = startCol;
  while (c < header.length) {
    var text = str_(header[c]);
    if (!text || normalizeAscii_(text).indexOf('tong') === 0) break;
    labels.push(text);
    c++;
  }
  return { labels: labels, totalCol: c };
}

/** Classifies a data row (not a section marker) into a display depth. */
function classifyIndent_(colA, name) {
  if (isRoman_(colA)) return { kind: 'group', indent: 0 };
  if (typeof colA === 'number') return { kind: 'item', indent: 1 };
  var n = str_(name);
  if (!n) return { kind: 'blank', indent: -1 };
  if (n.charAt(0) === '+') return { kind: 'detail2', indent: 3 };
  if (n.charAt(0) === '-') return { kind: 'detail1', indent: 2 };
  return { kind: 'detail', indent: 2 };
}

// ---- P&L (3) and SL&Lương ----------------------------------------------
// Both sheets share the exact same shape: a "TT | <name> | <periods...> |
// Tổng | Tỷ lệ" header, followed by three back-to-back sections marked
// A/B/C = KẾ HOẠCH / THỰC HIỆN / CHÊNH LỆCH. SL&Lương additionally nests
// roman-numeral groups (I/II/III) inside each section; P&L doesn't -
// classifyIndent_ handles both without the caller needing to know which.
// The reporting cadence itself changes between exports (quarterly "Quý
// 1..4" one period, monthly "Tháng 1..12" the next) so the number of
// period columns - and therefore where Tổng/Tỷ lệ land - is detected from
// the header row rather than assumed.

function parseQuarterlyReport_(ss, sheetName) {
  var data = getValues_(ss, sheetName);
  if (!data.length) return null;
  var headerRow = findRow_(data, 0, function (v) { return textEq_(v, 'TT'); });
  if (headerRow === -1) return null;
  var header = data[headerRow];
  var nameLabel = str_(header[1]) || 'Chỉ tiêu';
  var period = detectPeriodColumns_(header, 2);
  var valueLabels = period.labels;
  var totalCol = period.totalCol;
  var ratioCol = totalCol + 1;
  var totalLabel = str_(header[totalCol]) || 'Tổng';

  var sections = [];
  var current = null;
  for (var r = headerRow + 1; r < data.length; r++) {
    var row = data[r];
    var colA = row[0], colB = row[1];
    if (isSectionCode_(colA) && str_(colB)) {
      current = { code: str_(colA), title: str_(colB), rows: [] };
      sections.push(current);
      continue;
    }
    if (!current) continue;
    var cls = classifyIndent_(colA, colB);
    if (cls.kind === 'blank') continue;
    current.rows.push({
      tt: (typeof colA === 'number') ? colA : (typeof colA === 'string' ? colA.trim() : null),
      name: str_(colB),
      indent: cls.indent,
      values: valueLabels.map(function (_, i) { return num_(row[2 + i]); }),
      total: num_(row[totalCol]),
      ratio: (typeof row[ratioCol] === 'number') ? row[ratioCol] : null
    });
  }
  return { nameLabel: nameLabel, valueLabels: valueLabels, totalLabel: totalLabel, sections: sections };
}

// ---- TH HĐ tồn: monthly backlog-recognition plan/actual ---------------

function parseHopDongTonTongHop_(ss) {
  var data = getValues_(ss, 'TH HĐ tồn');
  if (!data.length) return null;
  var monthLabels = [];
  var sections = [];
  var current = null;

  for (var r = 0; r < data.length; r++) {
    var colA = data[r][0], colB = data[r][1];
    if (isRoman_(colA) && str_(colB)) {
      current = { title: str_(colB), rows: [], total: null };
      sections.push(current);
      continue;
    }
    if (typeof colA === 'string' && textEq_(colA, 'TT')) {
      if (!monthLabels.length) {
        for (var c = 2; c <= 13; c++) monthLabels.push(str_(data[r][c]));
      }
      continue;
    }
    if (!current) continue;
    if (typeof colA === 'number') {
      current.rows.push({
        tt: colA,
        name: str_(colB),
        months: buildRange_(data[r], 2, 12),
        total: num_(data[r][14])
      });
    } else if (str_(colB).toUpperCase() === 'TỔNG') {
      current.total = { months: buildRange_(data[r], 2, 12), total: num_(data[r][14]) };
    }
  }
  return { monthLabels: monthLabels, sections: sections };
}

function buildRange_(row, startCol, count) {
  var out = [];
  for (var i = 0; i < count; i++) out.push(num_(row[startCol + i]));
  return out;
}

// ---- HĐ tồn_TK / HĐ tồn_TC: contract backlog project detail -----------

function parseHopDongTonChiTiet_(ss, sheetName) {
  var data = getValues_(ss, sheetName);
  if (!data.length) return [];
  var headerRow = findRow_(data, 1, function (v) { return textEq_(v, 'Mã dự án'); });
  if (headerRow === -1) return [];
  var items = [];
  for (var r = headerRow + 1; r < data.length; r++) {
    var row = data[r];
    if (typeof row[0] !== 'number') continue;
    items.push({
      stt: row[0],
      maDuAn: str_(row[1]),
      tenDuAn: str_(row[2]),
      giaTriHopDong: num_(row[3]),
      daThanhToan: num_(row[4]),
      conPhaiThu: num_(row[5]),
      giamTruHD: num_(row[6]),
      daGhiNhan: num_(row[7]),
      duKienGhiNhan: num_(row[8]),
      thangGhiNhan: str_(row[9]),
      note: str_(row[10]),
      monthlyRecognition: buildRange_(row, 11, 12),
      tong: num_(row[23])
    });
  }
  return items;
}

// ---- CP cố định: fixed-cost budget vs actual ---------------------------
// "Thực hiện" columns are quarterly (Q1..Q4) in some exports and monthly
// (T1..T12) in others - detected from the header, not assumed.

function parseCPCoDinh_(ss) {
  var data = getValues_(ss, 'CP cố định');
  if (!data.length) return null;
  var headerRow = findRow_(data, 0, function (v) { return textEq_(v, 'TT'); });
  if (headerRow === -1) return null;
  var header = data[headerRow];
  var period = detectPeriodColumns_(header, 4);
  var periodLabels = period.labels;
  var totalCol = period.totalCol;
  var chenhLechCol = totalCol + 1;
  var keHoachLabel = str_(header[3]) || 'Kế hoạch';

  var groups = [];
  var current = null;
  for (var r = headerRow + 1; r < data.length; r++) {
    var row = data[r];
    var colA = row[0], colB = row[1];
    if (isRoman_(colA) && str_(colB)) {
      current = {
        code: str_(colA), title: str_(colB),
        keHoach: num_(row[3]), thucHien: num_(row[totalCol]), chenhLech: num_(row[chenhLechCol]),
        rows: []
      };
      groups.push(current);
      continue;
    }
    if (!current) continue;
    if (typeof colA === 'number') {
      current.rows.push({
        tt: colA, name: str_(colB), maPhi: str_(row[2]),
        keHoach: num_(row[3]),
        periods: periodLabels.map(function (_, i) { return num_(row[4 + i]); }),
        tong: num_(row[totalCol]), chenhLech: num_(row[chenhLechCol])
      });
    }
  }
  return { keHoachLabel: keHoachLabel, periodLabels: periodLabels, groups: groups };
}

// ---- KMP: granular cost-item report (3-level fee-code hierarchy) ------
// Same quarterly-vs-monthly "Thực hiện" ambiguity as CP cố định.

function parseKMP_(ss) {
  var data = getValues_(ss, 'KMP');
  if (!data.length) return null;
  var headerRow = findRow_(data, 0, function (v) { return textEq_(v, 'Mã THCP'); });
  if (headerRow === -1) return null;
  var header = data[headerRow];
  var period = detectPeriodColumns_(header, 4);
  var periodLabels = period.labels;
  var totalCol = period.totalCol;
  var chenhLechCol = totalCol + 1;
  var keHoachLabel = str_(header[3]) || 'Kế hoạch';

  var rows = [];
  var grandTotal = null;
  for (var r = headerRow + 1; r < data.length; r++) {
    var row = data[r];
    var maPhi = str_(row[1]);
    var tenPhi = str_(row[2]);
    if (!maPhi && !tenPhi) continue;
    if (!maPhi && tenPhi.toUpperCase() === 'TỔNG') {
      grandTotal = {
        keHoach: num_(row[3]),
        periods: periodLabels.map(function (_, i) { return num_(row[4 + i]); }),
        tong: num_(row[totalCol]), chenhLech: num_(row[chenhLechCol])
      };
      continue;
    }
    var level = maPhi.length <= 3 ? 0 : (maPhi.length <= 5 ? 1 : 2);
    rows.push({
      maTHCP: str_(row[0]), maPhi: maPhi, tenPhi: tenPhi, level: level,
      keHoach: num_(row[3]),
      periods: periodLabels.map(function (_, i) { return num_(row[4 + i]); }),
      tong: num_(row[totalCol]), chenhLech: num_(row[chenhLechCol])
    });
  }
  return { keHoachLabel: keHoachLabel, periodLabels: periodLabels, rows: rows, grandTotal: grandTotal };
}

// ---- NS LƯƠNG CĐ: fixed headcount / payroll plan by department --------

function parseNSLuong_(ss) {
  var data = getValues_(ss, 'NS LƯƠNG CĐ');
  if (!data.length) return null;
  var headerRow = findRow_(data, 1, function (v) { return textEq_(v, 'Kế hoạch nhân sự'); });
  if (headerRow === -1) return null;
  var departments = [];
  var current = null;
  // headerRow itself + the following sub-label row are both header rows.
  for (var r = headerRow + 2; r < data.length; r++) {
    var row = data[r];
    var colA = row[0], colB = row[1];
    if (isRoman_(colA) && str_(colB)) {
      current = {
        code: str_(colA), name: str_(colB),
        luongCoBan: num_(row[3]), luongDongBH: num_(row[5]), bhxh: num_(row[6]),
        luongHienTai: num_(row[7]), employees: []
      };
      departments.push(current);
      continue;
    }
    if (!current) continue;
    if (typeof colA === 'number') {
      current.employees.push({
        tt: colA, chucVu: str_(colB), hoTen: str_(row[2]),
        luongCoBan: num_(row[3]), maCP: str_(row[4]),
        luongDongBH: num_(row[5]), bhxh: num_(row[6]),
        luongHienTai: num_(row[7]) || null, maCP2: str_(row[9])
      });
    }
  }
  return { departments: departments };
}

// ---- CP thuế_Dự phòng: tax & provision summary --------------------------

function parseCPThueDuPhong_(ss) {
  var data = getValues_(ss, 'CP thuế_Dự phòng');
  if (!data.length) return null;
  var headerRow = findRow_(data, 0, function (v) { return textEq_(v, 'TT'); });
  if (headerRow === -1) return null;
  var groups = [];
  var current = null;
  for (var r = headerRow + 1; r < data.length; r++) {
    var row = data[r];
    var colA = row[0], colB = row[1];
    if (isRoman_(colA) && str_(colB)) {
      current = {
        code: str_(colA), name: str_(colB),
        keHoach: num_(row[2]), thucHien: num_(row[3]), thucHienEC: num_(row[4]),
        items: []
      };
      groups.push(current);
      continue;
    }
    if (!current) continue;
    if (typeof colA === 'number') {
      current.items.push({
        tt: colA, name: str_(colB),
        keHoach: num_(row[2]), thucHien: num_(row[3]), thucHienEC: num_(row[4])
      });
    }
  }
  return { groups: groups };
}

// ---- CP: accounting-software cost export --------------------------------

function parseCP_(ss) {
  var data = getValues_(ss, 'CP');
  if (!data.length) return [];
  var headerRow = findRow_(data, 0, function (v) { return textEq_(v, 'Stt'); });
  if (headerRow === -1) return [];
  var items = [];
  for (var r = headerRow + 1; r < data.length; r++) {
    var row = data[r];
    if (typeof row[0] !== 'number') continue;
    items.push({
      stt: row[0], maPhi: str_(row[1]), tenPhi: str_(row[2]),
      tienPS: num_(row[3]), group: num_(row[8]), ec: num_(row[9])
    });
  }
  return items;
}

// ---- KHAU HAO: tools/equipment depreciation schedule --------------------

function parseKhauHao_(ss) {
  var sh = ss.getSheetByName('KHAU HAO');
  if (!sh) return [];
  var lastRow = sh.getLastRow(), lastCol = sh.getLastColumn();
  if (lastRow < 2) return [];
  var data = sh.getRange(1, 1, lastRow, lastCol).getValues();
  var headerRow = findRow_(data, 0, function (v) { return textEq_(v, 'Stt'); });
  if (headerRow === -1) headerRow = 0;
  var tz = ss.getSpreadsheetTimeZone();
  var items = [];
  for (var r = headerRow + 1; r < data.length; r++) {
    var row = data[r];
    if (!str_(row[1])) continue;
    var d = row[4];
    items.push({
      stt: row[0] || null,
      maCC: str_(row[1]), tenCC: str_(row[2]), soThe: str_(row[3]),
      ngayTinh: (d instanceof Date) ? Utilities.formatDate(d, tz, 'yyyy-MM-dd') : str_(d),
      soKyPB: num_(row[5]), soLuong: num_(row[6]), nguyenGia: num_(row[7]),
      daPBDauKy: num_(row[8]), gtPBTrongKy: num_(row[9]), gtPBLuyKe: num_(row[10]),
      gtConLai: num_(row[11]), nhomCC: str_(row[12]), tkPB: str_(row[13]),
      tkCP: str_(row[14]), maPhi: str_(row[15])
    });
  }
  return items;
}

// ---- Chi tiết 1 số khoản mục phí: simple 2-column breakdown -------------

function parseChiTietPhi_(ss) {
  var data = getValues_(ss, 'Chi tiết 1 số khoản mục phí');
  var items = [];
  for (var r = 0; r < data.length; r++) {
    var name = str_(data[r][0]);
    if (!name) continue;
    items.push({ name: name, value: num_(data[r][1]) });
  }
  return items;
}

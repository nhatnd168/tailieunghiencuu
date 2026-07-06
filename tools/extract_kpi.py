"""
Trich xuat "KE HOACH KPI DOANH THU VA SAN LUONG NAM 2026.pdf" thanh JSON co cau truc.

pdfminer xuat text theo dong, moi con so trong bang nam rieng tren mot dong.
Cac nhom bang trong file nay dung 2 kieu bo tri khac nhau:
  - "sequential": moi hang la 1 khoi lien tiep 12 thang + tong (vd cac hang
    breakdown theo SALE trong Phong Kinh doanh).
  - "interleaved": nhieu hang chia se cung cot thang, pdfminer doc theo tung
    cot truoc (thang 1 cua hang A, thang 1 cua hang B, thang 2 cua hang A,...)
    roi moi den cum "Tong" cua tat ca cac hang (vd 2 hang "Thiet ke noi that"/
    "Thiet ke kien truc" trong Phong Thiet ke).
Hang cuoi cung cua mot nhom sequential duoc doc "linh hoat": lay het so con
lai, vi co hang khong dien du 12 thang (vd "Doanh thu TC noi that" chi co du
lieu 10 thang trong ban goc).

Chay: python3 tools/extract_kpi.py
"""
import os
import re

from pdfminer.high_level import extract_text

from common import DATA_DIR, MONTHS, find_pdf, save_json

# Chi khop so co dau phay ngan chuc nghin (vd "1,725,000,000") hoac dau "-"
# (bang 0). Khong khop cac so tran nhu "1"/"2" - do la phan con lai cua nhan
# "Tháng 1"/"Tháng 2" bi ngat dong trong PDF, khong phai du lieu.
NUMBER_RE = re.compile(r"^-$|^\d{1,3}(,\d{3})+$")

SECTION_MARKERS = [
    ("thiet_ke", "3.1 Phòng Thiết kế"),
    ("kinh_doanh", "3.2 Phòng Kinh doanh"),
    ("thi_cong", "3.3 Phòng Thi Công"),
    ("thi_cong_noi_that", "3.4 Phòng Thi Công Nội thất"),
    (None, "4. Tổ chức thực hiện"),
]

# Moi phong ban = danh sach cac nhom (group), moi group co kieu bo tri va
# danh sach nhan chi so theo dung thu tu xuat hien trong PDF.
DEPARTMENT_LAYOUT = {
    "thiet_ke": [
        {"type": "sequential", "labels": ["tong_doanh_thu"]},
        {"type": "interleaved", "labels": ["thiet_ke_noi_that", "thiet_ke_kien_truc"]},
    ],
    "kinh_doanh": [
        {"type": "sequential", "labels": [
            "san_luong_ky_thiet_ke",
            "san_luong_ky_thiet_ke__sale1_nhu",
            "san_luong_ky_thiet_ke__sale2_hoang",
            "san_luong_ky_thiet_ke__sale3",
            "san_luong_ky_thiet_ke__sale4",
        ]},
        {"type": "sequential", "labels": [
            "san_luong_ky_thi_cong_tho",
            "san_luong_ky_thi_cong_tho__sale1_nhu",
            "san_luong_ky_thi_cong_tho__sale2_hoang",
            "san_luong_ky_thi_cong_tho__sale3",
            "san_luong_ky_thi_cong_tho__sale4",
        ]},
    ],
    "thi_cong": [
        {"type": "sequential", "flex_last": True,
         "labels": ["san_luong_tc_hoan_thien", "doanh_thu_tc_hoan_thien"]},
    ],
    "thi_cong_noi_that": [
        {"type": "sequential", "flex_last": True,
         "labels": ["san_luong_ky_tc_noi_that", "doanh_thu_tc_noi_that"]},
    ],
}


def parse_company_targets(text):
    # Gop khoang trang/xuong dong thanh 1 dau cach: mot so cum tu bi PDF ngat
    # dong giua chung (vd "Thi \n\ncông nội thất") nen can gop lai truoc khi
    # so khop regex.
    flat = " ".join(text.split())

    def num(pattern):
        m = re.search(pattern, flat)
        return float(m.group(1)) if m else None

    return {
        "san_luong_ty": num(r"Sản lượng:\s*([\d.]+)\s*tỷ"),
        "doanh_thu_ty": num(r"Doanh thu:\s*([\d.]+)\s*tỷ"),
        "doanh_thu_pct_san_luong": num(r"\(([\d.]+)%\s*sản lượng\)"),
        "co_cau_san_luong_ty": {
            "thiet_ke": num(r"Thiết kế\s*([\d.]+)\s*\(tỷ\)"),
            "thi_cong_tho": num(r"Thi công thô\s*([\d.]+)\s*\(tỷ\)"),
            "thi_cong_hoan_thien": num(r"Thi công hoàn thiện\s*([\d.]+)\s*\(tỷ\)"),
            "thi_cong_noi_that": num(r"Thi công nội thất\s*([\d.]+)\s*\(tỷ\)"),
        },
    }


def split_sections(text):
    positions = []
    for key, marker in SECTION_MARKERS:
        idx = text.find(marker)
        if idx == -1:
            raise ValueError(f"Khong tim thay marker: {marker}")
        positions.append((key, idx))
    sections = {}
    for i, (key, start) in enumerate(positions[:-1]):
        end = positions[i + 1][1]
        if key:
            sections[key] = text[start:end]
    return sections


def extract_values(section_text):
    lines = [ln.strip() for ln in section_text.splitlines()]
    numbers = [ln.replace(",", "").replace("-", "0") for ln in lines if NUMBER_RE.match(ln)]
    return [float(n) if n else 0.0 for n in numbers]


def to_metric(months, total):
    months = months[:12] + [None] * (12 - len(months))
    return {"months": dict(zip(MONTHS, months)), "total": total}


def consume_sequential(values, pointer, labels, flex_last=False):
    metrics = {}
    for i, label in enumerate(labels):
        is_last = flex_last and i == len(labels) - 1
        if is_last:
            remaining = values[pointer:]
            months, total = remaining[:-1], (remaining[-1] if remaining else None)
            pointer = len(values)
        else:
            block = values[pointer:pointer + 13]
            months, total = block[:12], (block[12] if len(block) > 12 else None)
            pointer += 13
        metrics[label] = to_metric(months, total)
    return metrics, pointer


def consume_interleaved(values, pointer, labels):
    grids = {label: [] for label in labels}
    for _ in range(12):
        for label in labels:
            grids[label].append(values[pointer])
            pointer += 1
    totals = {}
    for label in labels:
        totals[label] = values[pointer]
        pointer += 1
    return {label: to_metric(grids[label], totals[label]) for label in labels}, pointer


def parse_department(key, section_text):
    values = extract_values(section_text)
    metrics = {}
    pointer = 0
    for group in DEPARTMENT_LAYOUT[key]:
        if group["type"] == "sequential":
            group_metrics, pointer = consume_sequential(
                values, pointer, group["labels"], flex_last=group.get("flex_last", False)
            )
        else:
            group_metrics, pointer = consume_interleaved(values, pointer, group["labels"])
        metrics.update(group_metrics)
    if pointer != len(values):
        raise ValueError(
            f"Phong ban '{key}': con {len(values) - pointer} gia tri chua duoc gan nhan"
        )
    return metrics


def main():
    pdf_path = find_pdf("KPI")
    text = extract_text(pdf_path)

    result = {
        "source_file": os.path.basename(pdf_path),
        "company_targets": parse_company_targets(text),
        "departments": {},
    }

    sections = split_sections(text)
    for key in DEPARTMENT_LAYOUT:
        result["departments"][key] = parse_department(key, sections[key])

    out_path = os.path.join(DATA_DIR, "kpi_plan_2026.json")
    save_json(result, out_path)
    print(f"Da ghi {out_path}")


if __name__ == "__main__":
    main()

"""
Trich xuat "BSC-OKR_2026_XCONSe&c...pdf" thanh JSON co cau truc.

Chi tu dong hoa phan doc duoc dang tin cay tu text pdfminer:
  - Muc tieu bat buoc 2026 (giong file KPI, dung de doi chieu 2 nguon).
  - BSC 4 goc nhin (Tai chinh / Khach hang / Quy trinh noi bo / Con nguoi).
  - Tieu de O1-O4 cua OKR cap Cong ty (cac tieu de nay nam tron trong 1 khoi
    text lien tuc trong PDF nen tach duoc chinh xac).

Bang OKR chi tiet theo tung phong ban (muc 6.1 - 6.6.3) bi pdfminer doc xen
ke giua nhieu cot (Muc tieu/KR/Don vi/Target/Tan suat/Chu tri/Nguon du lieu)
nen khong the tach tu dong ma khong co rui ro sai lech du lieu KR. Cac muc
nay duoc giu nguyen dang raw text de doc thu cong / doi chieu voi PDF goc.

Chay: python3 tools/extract_bsc.py
"""
import os
import re

from pdfminer.high_level import extract_text

from common import DATA_DIR, find_pdf, save_json
from extract_kpi import parse_company_targets

PERSPECTIVE_LABELS = ["Tài chính", "Khách hàng", "Quy trình nội bộ", "Con người & năng lực"]

DEPARTMENT_SECTION_MARKERS = [
    "6.1 Phòng Thiết kế",
    "6.2 Phòng Kinh doanh",
    "6.3 Phòng Marketing",
    "6.4 Phòng Nội thất",
    "6.5 Phòng XCenter",
    "6.6.1 Hành chính - Thủ quỹ",
    "6.6.2 Chuyên viên Nhân sự",
    "6.6.3 Kế toán tổng hợp",
]


def clean(text):
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def parse_bsc_perspectives(text):
    start = text.find("4. BSC 2026")
    end = text.find("5. OKR cấp Công ty")
    section = text[start:end]
    for label in PERSPECTIVE_LABELS:
        section = section.replace(label, "")
    section = section.replace("4. BSC 2026 - Mục tiêu trọng tâm", "")
    section = section.replace("Mục tiêu trọng tâm 2026", "")
    section = section.replace("Góc nhìn", "")

    # Cac dong con lai la 4 cau muc tieu, moi cau ket thuc bang dau "."; gom
    # cac dong lien tiep lai thanh 1 cau cho toi khi gap dau cham.
    lines = [ln.strip() for ln in section.splitlines() if ln.strip()]
    goals, current = [], []
    for ln in lines:
        current.append(ln)
        if ln.endswith("."):
            goals.append(" ".join(current))
            current = []
    if current:
        goals.append(" ".join(current))

    if len(goals) != len(PERSPECTIVE_LABELS):
        return {"raw_text": clean(section), "note": "khong tach duoc chinh xac tung goc nhin"}
    return dict(zip(PERSPECTIVE_LABELS, goals))


def parse_company_okr_titles(text):
    start = text.find("5. OKR cấp Công ty")
    end = text.find("6. OKR theo phòng ban")
    section = text[start:end]
    matches = re.findall(r"\nO(\d)[.:]\s*((?:(?!\n\s*\n).)+)", section, re.DOTALL)
    return [f"O{n}. {' '.join(title.split())}" for n, title in matches]


def parse_department_raw_sections(text):
    positions = []
    for marker in DEPARTMENT_SECTION_MARKERS:
        idx = text.find(marker)
        if idx == -1:
            raise ValueError(f"Khong tim thay marker: {marker}")
        positions.append((marker, idx))
    end_idx = text.find("7. Tổ chức thực hiện")
    positions.append((None, end_idx))

    sections = {}
    for i, (marker, start) in enumerate(positions[:-1]):
        end = positions[i + 1][1]
        sections[marker] = clean(text[start:end])
    return sections


def main():
    pdf_path = find_pdf("BSC-OKR")
    text = extract_text(pdf_path)

    result = {
        "source_file": os.path.basename(pdf_path),
        "company_targets": parse_company_targets(text),
        "bsc_perspectives": parse_bsc_perspectives(text),
        "company_okr_titles": parse_company_okr_titles(text),
        "department_okr_raw_sections": parse_department_raw_sections(text),
    }

    out_path = os.path.join(DATA_DIR, "bsc_okr_2026.json")
    save_json(result, out_path)
    print(f"Da ghi {out_path}")


if __name__ == "__main__":
    main()

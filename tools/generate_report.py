"""
Sinh bao cao Markdown tong hop tu du lieu da trich xuat (BSC/OKR + KPI ke
hoach) va so lieu thuc te (neu co).

Chay:
    python3 tools/generate_report.py                          # khong co actuals
    python3 tools/generate_report.py data/actuals_2026.json    # kem theo dõi tien do
"""
import io
import sys
from contextlib import redirect_stdout

from common import DATA_DIR, REPORTS_DIR, fmt_vnd, load_json
from labels import DEPARTMENT_NAMES, METRIC_NAMES
import os
import track_kpi


def render_company_overview(bsc, kpi):
    t = kpi["company_targets"]
    lines = ["# Báo cáo tổng hợp BSC/OKR & KPI 2026 — XCONS E&C", ""]
    lines.append("## 1. Mục tiêu bắt buộc 2026")
    lines.append(f"- **Sản lượng:** {t['san_luong_ty']} tỷ")
    lines.append(f"- **Doanh thu:** {t['doanh_thu_ty']} tỷ ({t['doanh_thu_pct_san_luong']}% sản lượng)")
    co_cau = t["co_cau_san_luong_ty"]
    lines.append(
        f"- **Cơ cấu sản lượng:** Thiết kế {co_cau['thiet_ke']} tỷ | "
        f"Thi công thô {co_cau['thi_cong_tho']} tỷ | "
        f"Thi công hoàn thiện {co_cau['thi_cong_hoan_thien']} tỷ | "
        f"Thi công nội thất {co_cau['thi_cong_noi_that']} tỷ"
    )
    lines.append("")

    lines.append("## 2. BSC — 4 góc nhìn trọng tâm 2026")
    perspectives = bsc.get("bsc_perspectives", {})
    if "note" in perspectives:
        lines.append(f"_{perspectives['note']}, xem PDF gốc._")
    else:
        for name, goal in perspectives.items():
            lines.append(f"- **{name}:** {goal}")
    lines.append("")

    lines.append("## 3. OKR cấp Công ty")
    for title in bsc.get("company_okr_titles", []):
        lines.append(f"- {title}")
    lines.append("")
    lines.append(
        "> Chi tiết Kết quả then chốt (KR), chủ trì, tần suất của OKR cấp công ty và "
        "OKR theo từng phòng ban chỉ đọc được đầy đủ trong file PDF gốc "
        f"(`{bsc['source_file']}`) — bảng gốc bị dàn cột phức tạp nên không trích xuất "
        "tự động đáng tin cậy được phần này."
    )
    lines.append("")
    return lines


def render_kpi_plan(kpi):
    lines = ["## 4. Kế hoạch KPI sản lượng & doanh thu theo phòng ban (năm 2026)", ""]
    for dept_key, metrics in kpi["departments"].items():
        lines.append(f"### {DEPARTMENT_NAMES.get(dept_key, dept_key)}")
        lines.append("")
        lines.append("| Chỉ số | Tổng năm |")
        lines.append("|---|---|")
        for metric_key, metric in metrics.items():
            name = METRIC_NAMES.get(metric_key, metric_key)
            total = metric.get("total")
            lines.append(f"| {name} | {fmt_vnd(total) if total is not None else 'n/a'} |")
        lines.append("")
    return lines


def render_tracking(actuals_path):
    if not actuals_path or not os.path.exists(actuals_path):
        return [
            "## 5. Theo dõi thực tế so với kế hoạch", "",
            f"_Chưa có file số liệu thực tế. Copy "
            f"`{os.path.join('data', 'actuals_2026.example.json')}` thành "
            f"`{os.path.join('data', 'actuals_2026.json')}`, điền số liệu rồi chạy lại "
            f"`python3 tools/generate_report.py data/actuals_2026.json`._",
            "",
        ]
    buf = io.StringIO()
    with redirect_stdout(buf):
        sys.argv = ["track_kpi.py", actuals_path]
        track_kpi.main()
    body = buf.getvalue()
    lines = ["## 5. Theo dõi thực tế so với kế hoạch", "", "```", body.rstrip(), "```", ""]
    return lines


def main():
    actuals_path = sys.argv[1] if len(sys.argv) > 1 else None

    kpi = load_json(os.path.join(DATA_DIR, "kpi_plan_2026.json"))
    bsc = load_json(os.path.join(DATA_DIR, "bsc_okr_2026.json"))

    lines = []
    lines += render_company_overview(bsc, kpi)
    lines += render_kpi_plan(kpi)
    lines += render_tracking(actuals_path)

    out_path = os.path.join(REPORTS_DIR, "bao_cao_tong_hop_2026.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"Da ghi {out_path}")


if __name__ == "__main__":
    main()

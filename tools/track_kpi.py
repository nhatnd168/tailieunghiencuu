"""
So sanh so lieu THUC TE (nguoi dung tu nhap) voi KE HOACH KPI da trich xuat.

Chay:
    python3 tools/track_kpi.py                          # dung data/actuals_2026.json
    python3 tools/track_kpi.py data/actuals_thang6.json  # chi dinh file khac

File actuals la JSON do nguoi dung dien tay hang thang, xem mau tai
data/actuals_2026.example.json.
"""
import sys

from common import DATA_DIR, MONTHS, fmt_vnd, load_json
from labels import (
    COMPANY_DOANH_THU_METRICS,
    COMPANY_SAN_LUONG_METRICS,
    DEPARTMENT_NAMES,
    DOANH_THU_CAVEAT,
    METRIC_NAMES,
)
import os


def classify(pct):
    if pct is None:
        return "?"
    if pct >= 95:
        return "Đạt"
    if pct >= 80:
        return "Cần theo dõi"
    return "Chậm"


def months_upto(n):
    return MONTHS[:n]


def cumulative_plan(metric, as_of_month):
    months = metric["months"]
    values = [months.get(m) for m in months_upto(as_of_month)]
    return sum(v for v in values if v is not None)


def cumulative_actual(actual_months, as_of_month):
    values = [actual_months.get(m, 0) for m in months_upto(as_of_month)]
    return sum(values)


def evaluate_metric(plan_metric, actual_months, as_of_month):
    plan_cum = cumulative_plan(plan_metric, as_of_month)
    actual_cum = cumulative_actual(actual_months, as_of_month)
    pct = (actual_cum / plan_cum * 100) if plan_cum else None
    run_rate_year = (actual_cum / as_of_month * 12) if as_of_month else None
    plan_year = plan_metric.get("total")
    return {
        "plan_cum": plan_cum,
        "actual_cum": actual_cum,
        "pct": pct,
        "status": classify(pct),
        "run_rate_year": run_rate_year,
        "plan_year": plan_year,
    }


def print_row(label, ev):
    pct_str = f"{ev['pct']:.0f}%" if ev["pct"] is not None else "n/a"
    print(f"  {label:<32} KH lũy kế: {fmt_vnd(ev['plan_cum']):>16}  "
          f"TT lũy kế: {fmt_vnd(ev['actual_cum']):>16}  {pct_str:>6}  [{ev['status']}]")


def rollup(plan, actuals, as_of_month, metric_list, label):
    plan_total = 0
    actual_total = 0
    missing = []
    for dept, metric_key in metric_list:
        plan_metric = plan["departments"][dept][metric_key]
        actual_dept = actuals.get("departments", {}).get(dept, {})
        if metric_key not in actual_dept:
            missing.append(f"{DEPARTMENT_NAMES[dept]}/{METRIC_NAMES[metric_key]}")
            continue
        ev = evaluate_metric(plan_metric, actual_dept[metric_key], as_of_month)
        plan_total += ev["plan_cum"]
        actual_total += ev["actual_cum"]
    pct = (actual_total / plan_total * 100) if plan_total else None
    print(f"\n{label}")
    print(f"  Kế hoạch lũy kế: {fmt_vnd(plan_total)}   Thực tế lũy kế: {fmt_vnd(actual_total)}   "
          f"{f'{pct:.0f}%' if pct is not None else 'n/a'}  [{classify(pct)}]")
    if missing:
        print(f"  (chưa có số liệu thực tế cho: {', '.join(missing)} — tổng trên chưa đầy đủ)")


def main():
    actuals_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA_DIR, "actuals_2026.json")
    if not os.path.exists(actuals_path):
        print(f"Khong tim thay {actuals_path}.")
        print(f"Hay copy {os.path.join(DATA_DIR, 'actuals_2026.example.json')} thanh file nay va dien so lieu.")
        sys.exit(1)

    plan = load_json(os.path.join(DATA_DIR, "kpi_plan_2026.json"))
    actuals = load_json(actuals_path)
    as_of_month = actuals["as_of_month"]

    print(f"=== THEO DÕI KPI 2026 — lũy kế đến tháng {as_of_month} ===")

    for dept_key, dept_actuals in actuals.get("departments", {}).items():
        print(f"\n{DEPARTMENT_NAMES.get(dept_key, dept_key)}")
        for metric_key, actual_months in dept_actuals.items():
            plan_metric = plan["departments"][dept_key][metric_key]
            ev = evaluate_metric(plan_metric, actual_months, as_of_month)
            print_row(METRIC_NAMES.get(metric_key, metric_key), ev)

    rollup(plan, actuals, as_of_month, COMPANY_SAN_LUONG_METRICS,
           "TỔNG SẢN LƯỢNG TOÀN CÔNG TY (mục tiêu năm: 91 tỷ)")
    rollup(plan, actuals, as_of_month, COMPANY_DOANH_THU_METRICS,
           "TỔNG DOANH THU (các mảng có lịch trình) (mục tiêu năm: 77 tỷ)")
    print(f"\nLưu ý: {DOANH_THU_CAVEAT}")


if __name__ == "__main__":
    main()

"""
Sinh dashboard HTML (tu chua, mo truc tiep bang trinh duyet) tu du lieu da
trich xuat + so lieu thuc te (neu co).

Chay:
    python3 tools/generate_dashboard.py                          # dung actuals that neu co, khong thi dung file .example
    python3 tools/generate_dashboard.py data/actuals_2026.json    # chi dinh file actuals
"""
import html
import os
import sys

from common import DATA_DIR, MONTHS, REPORTS_DIR, load_json
from labels import (
    COMPANY_DOANH_THU_METRICS,
    COMPANY_SAN_LUONG_METRICS,
    DEPARTMENT_NAMES,
    DOANH_THU_CAVEAT,
    METRIC_NAMES,
)
from track_kpi import classify, cumulative_actual, cumulative_plan

# Cac chi so chinh de ve bieu do thang (bo qua breakdown theo sale)
CHART_METRICS = [
    ("thiet_ke", "tong_doanh_thu"),
    ("kinh_doanh", "san_luong_ky_thiet_ke"),
    ("kinh_doanh", "san_luong_ky_thi_cong_tho"),
    ("thi_cong", "san_luong_tc_hoan_thien"),
    ("thi_cong", "doanh_thu_tc_hoan_thien"),
    ("thi_cong_noi_that", "san_luong_ky_tc_noi_that"),
    ("thi_cong_noi_that", "doanh_thu_tc_noi_that"),
]

STATUS_CLASS = {"Đạt": "good", "Cần theo dõi": "warn", "Chậm": "bad", "?": "muted"}


def ty(v):
    if v is None:
        return "n/a"
    return f"{v / 1e9:.2f} tỷ"


def esc(s):
    return html.escape(str(s))


def stat_tile(label, value, sub=""):
    return f"""
    <div class="tile">
      <div class="tile-label">{esc(label)}</div>
      <div class="tile-value">{esc(value)}</div>
      <div class="tile-sub">{esc(sub)}</div>
    </div>"""


def meter(label, pct, right_text):
    pct_clamped = 0 if pct is None else max(0, min(100, pct))
    status = classify(pct)
    cls = STATUS_CLASS[status]
    return f"""
    <div class="meter-row">
      <div class="meter-head">
        <span class="meter-label">{esc(label)}</span>
        <span class="meter-right">{esc(right_text)} &middot;
          <span class="chip chip-{cls}">{esc(status)}</span></span>
      </div>
      <div class="meter-track" role="img" aria-label="{esc(label)}: {pct_clamped:.0f}%">
        <div class="meter-fill fill-{cls}" style="width:{pct_clamped:.1f}%"></div>
      </div>
    </div>"""


def grouped_bar_chart(title, plan_months, actual_months):
    w, h = 720, 200
    pad_l, pad_r, pad_t, pad_b = 8, 8, 8, 24
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b
    max_v = max([v for v in plan_months if v is not None] +
                [v for v in actual_months.values()] + [1])
    n = len(MONTHS)
    group_w = plot_w / n
    bar_w = group_w * 0.32
    gap = group_w * 0.06

    def bar_h(v):
        return 0 if not v else (v / max_v) * plot_h

    bars = []
    for i, m in enumerate(MONTHS):
        gx = pad_l + i * group_w
        plan_v = plan_months[i]
        actual_v = actual_months.get(m)
        if plan_v is not None:
            bh = bar_h(plan_v)
            x = gx + group_w / 2 - bar_w - gap / 2
            y = pad_t + plot_h - bh
            bars.append(
                f'<rect class="bar bar-plan" x="{x:.1f}" y="{y:.1f}" '
                f'width="{bar_w:.1f}" height="{bh:.1f}" rx="3">'
                f'<title>{esc(m)} — Kế hoạch: {ty(plan_v)}</title></rect>'
            )
        if actual_v is not None:
            bh = bar_h(actual_v)
            x = gx + group_w / 2 + gap / 2
            y = pad_t + plot_h - bh
            bars.append(
                f'<rect class="bar bar-actual" x="{x:.1f}" y="{y:.1f}" '
                f'width="{bar_w:.1f}" height="{bh:.1f}" rx="3">'
                f'<title>{esc(m)} — Thực tế: {ty(actual_v)}</title></rect>'
            )
        bars.append(
            f'<text class="axis-label" x="{gx + group_w / 2:.1f}" y="{h - 6}" '
            f'text-anchor="middle">{esc(m[1:])}</text>'
        )

    baseline_y = pad_t + plot_h
    svg = (
        f'<svg viewBox="0 0 {w} {h}" class="chart-svg" role="img" aria-label="{esc(title)}">'
        f'<line x1="{pad_l}" y1="{baseline_y}" x2="{w - pad_r}" y2="{baseline_y}" class="baseline"/>'
        + "".join(bars) + "</svg>"
    )

    return f"""
    <div class="chart-card">
      <div class="chart-head">
        <span class="chart-title">{esc(title)}</span>
        <span class="legend">
          <span class="legend-item"><span class="swatch swatch-plan"></span>Kế hoạch</span>
          <span class="legend-item"><span class="swatch swatch-actual"></span>Thực tế</span>
        </span>
      </div>
      {svg}
    </div>"""


def build_dashboard(plan, bsc, actuals):
    as_of_month = actuals.get("as_of_month") if actuals else None
    t = plan["company_targets"]

    tiles = [
        stat_tile("Mục tiêu sản lượng 2026", f"{t['san_luong_ty']:.0f} tỷ"),
        stat_tile("Mục tiêu doanh thu 2026", f"{t['doanh_thu_ty']:.0f} tỷ",
                   f"{t['doanh_thu_pct_san_luong']}% sản lượng"),
    ]

    rollup_meters = []
    if actuals:
        for metric_list, title, year_target in [
            (COMPANY_SAN_LUONG_METRICS, "Tổng sản lượng lũy kế", t["san_luong_ty"]),
            (COMPANY_DOANH_THU_METRICS, "Tổng doanh thu lũy kế (chưa gồm TC thô)", None),
        ]:
            plan_total = actual_total = 0
            complete = True
            for dept, metric_key in metric_list:
                plan_metric = plan["departments"][dept][metric_key]
                actual_dept = actuals.get("departments", {}).get(dept, {})
                if metric_key not in actual_dept:
                    complete = False
                    continue
                plan_total += cumulative_plan(plan_metric, as_of_month)
                actual_total += cumulative_actual(actual_dept[metric_key], as_of_month)
            pct = (actual_total / plan_total * 100) if plan_total else None
            right = f"{ty(actual_total)} / {ty(plan_total)} kế hoạch lũy kế"
            if not complete:
                right += " (thiếu vài chỉ số)"
            rollup_meters.append(meter(title, pct, right))

    dept_sections = []
    for dept_key, metrics in plan["departments"].items():
        rows = []
        for metric_key, plan_metric in metrics.items():
            if "__" in metric_key:
                continue  # bo qua breakdown theo sale trong trang tong quan
            actual_dept = (actuals or {}).get("departments", {}).get(dept_key, {})
            actual_months = actual_dept.get(metric_key)
            label = METRIC_NAMES.get(metric_key, metric_key)
            if actual_months and as_of_month:
                plan_cum = cumulative_plan(plan_metric, as_of_month)
                actual_cum = cumulative_actual(actual_months, as_of_month)
                pct = (actual_cum / plan_cum * 100) if plan_cum else None
                right = f"{ty(actual_cum)} / {ty(plan_cum)} · mục tiêu năm {ty(plan_metric['total'])}"
                rows.append(meter(label, pct, right))
            else:
                rows.append(meter(label, None, f"mục tiêu năm {ty(plan_metric['total'])} (chưa có số liệu thực tế)"))
        dept_sections.append(f"""
    <section class="dept-card">
      <h3>{esc(DEPARTMENT_NAMES.get(dept_key, dept_key))}</h3>
      {''.join(rows)}
    </section>""")

    charts = []
    for dept_key, metric_key in CHART_METRICS:
        plan_metric = plan["departments"][dept_key][metric_key]
        plan_months = [plan_metric["months"][m] for m in MONTHS]
        actual_dept = (actuals or {}).get("departments", {}).get(dept_key, {})
        actual_months = actual_dept.get(metric_key, {})
        title = f"{DEPARTMENT_NAMES.get(dept_key, dept_key)} — {METRIC_NAMES.get(metric_key, metric_key)}"
        charts.append(grouped_bar_chart(title, plan_months, actual_months))

    okr_items = "".join(f"<li>{esc(t)}</li>" for t in bsc.get("company_okr_titles", []))
    perspectives = bsc.get("bsc_perspectives", {})
    persp_items = "".join(
        f"<li><strong>{esc(k)}:</strong> {esc(v)}</li>" for k, v in perspectives.items()
        if k not in ("note", "raw_text")
    )

    example_banner = ""
    if actuals and actuals.get("_is_example"):
        example_banner = (
            '<div class="banner">Đang hiển thị DỮ LIỆU VÍ DỤ '
            '(data/actuals_2026.example.json) — chưa phải số liệu thực tế. '
            'Tạo file data/actuals_2026.json để thay bằng số thật.</div>'
        )
    elif not actuals:
        example_banner = (
            '<div class="banner">Chưa có số liệu thực tế nào — chỉ hiển thị kế hoạch. '
            'Copy data/actuals_2026.example.json thành data/actuals_2026.json và điền số liệu.</div>'
        )

    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Dashboard KPI 2026 — XCONS E&C</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="page">
  <header>
    <h1>Dashboard KPI &amp; BSC/OKR 2026 — XCONS E&amp;C</h1>
    <p class="subtitle">Tổng hợp từ kế hoạch KPI + BSC/OKR đã trích xuất{f", lũy kế đến tháng {as_of_month}" if as_of_month else ""}.</p>
  </header>
  {example_banner}

  <section class="tiles-row">{''.join(tiles)}</section>

  {f'<section class="rollups">{"".join(rollup_meters)}</section>' if rollup_meters else ''}

  <section class="two-col">
    <div class="card">
      <h2>BSC — 4 góc nhìn trọng tâm</h2>
      <ul class="plain-list">{persp_items}</ul>
    </div>
    <div class="card">
      <h2>OKR cấp Công ty</h2>
      <ul class="plain-list">{okr_items}</ul>
    </div>
  </section>

  <h2>Tiến độ theo phòng ban</h2>
  <section class="dept-grid">{''.join(dept_sections)}</section>

  <h2>Kế hoạch vs Thực tế theo tháng</h2>
  <section class="chart-grid">{''.join(charts)}</section>

  <p class="footnote">{esc(DOANH_THU_CAVEAT)}</p>
</div>
</body>
</html>"""


CSS = """
.viz-root, body {
  --surface-1: #fcfcfb; --page: #f9f9f7; --text-primary: #0b0b0b;
  --text-secondary: #52514e; --muted: #898781; --grid: #e1e0d9; --axis: #c3c2b7;
  --border: rgba(11,11,11,0.10);
  --series-plan: #2a78d6; --series-actual: #1baf7a;
  --good: #0ca30c; --warn: #fab219; --bad: #d03b3b;
}
@media (prefers-color-scheme: dark) {
  .viz-root, body {
    --surface-1: #1a1a19; --page: #0d0d0d; --text-primary: #ffffff;
    --text-secondary: #c3c2b7; --muted: #898781; --grid: #2c2c2a; --axis: #383835;
    --border: rgba(255,255,255,0.10);
    --series-plan: #3987e5; --series-actual: #199e70;
    --good: #0ca30c; --warn: #fab219; --bad: #e66767;
  }
}
:root[data-theme="dark"] {
  --surface-1: #1a1a19; --page: #0d0d0d; --text-primary: #ffffff;
  --text-secondary: #c3c2b7; --muted: #898781; --grid: #2c2c2a; --axis: #383835;
  --border: rgba(255,255,255,0.10);
  --series-plan: #3987e5; --series-actual: #199e70;
}
:root[data-theme="light"] {
  --surface-1: #fcfcfb; --page: #f9f9f7; --text-primary: #0b0b0b;
  --text-secondary: #52514e; --muted: #898781; --grid: #e1e0d9; --axis: #c3c2b7;
  --border: rgba(11,11,11,0.10);
  --series-plan: #2a78d6; --series-actual: #1baf7a;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--page); color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}
.page { max-width: 1120px; margin: 0 auto; padding: 32px 20px 64px; }
header h1 { font-size: 1.5rem; margin: 0 0 4px; }
.subtitle { color: var(--text-secondary); margin: 0 0 20px; }
.banner {
  background: var(--surface-1); border: 1px solid var(--border); border-left: 4px solid var(--warn);
  padding: 10px 14px; border-radius: 6px; margin-bottom: 20px; color: var(--text-secondary); font-size: 0.9rem;
}
h2 { font-size: 1.1rem; margin: 32px 0 12px; }
.tiles-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.tile {
  background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 18px; min-width: 200px; flex: 1;
}
.tile-label { color: var(--text-secondary); font-size: 0.8rem; }
.tile-value { font-size: 1.6rem; font-weight: 600; margin-top: 2px; }
.tile-sub { color: var(--muted); font-size: 0.8rem; margin-top: 2px; }
.rollups { display: flex; flex-direction: column; gap: 10px; margin: 16px 0; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
@media (max-width: 720px) { .two-col { grid-template-columns: 1fr; } }
.card {
  background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px;
}
.card h2 { margin-top: 0; }
.plain-list { margin: 0; padding-left: 18px; color: var(--text-secondary); font-size: 0.92rem; line-height: 1.6; }
.dept-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 720px) { .dept-grid { grid-template-columns: 1fr; } }
.dept-card {
  background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px;
}
.dept-card h3 { margin: 0 0 10px; font-size: 1rem; }
.meter-row { margin-bottom: 14px; }
.meter-row:last-child { margin-bottom: 0; }
.meter-head { display: flex; justify-content: space-between; gap: 8px; font-size: 0.85rem; margin-bottom: 5px; }
.meter-label { color: var(--text-primary); }
.meter-right { color: var(--text-secondary); white-space: nowrap; }
.meter-track { background: var(--grid); border-radius: 999px; height: 8px; overflow: hidden; }
.meter-fill { height: 100%; border-radius: 999px; }
.fill-good { background: var(--good); }
.fill-warn { background: var(--warn); }
.fill-bad { background: var(--bad); }
.fill-muted { background: var(--axis); }
.chip { font-size: 0.72rem; padding: 1px 7px; border-radius: 999px; border: 1px solid var(--border); }
.chip-good { color: var(--good); }
.chip-warn { color: #a06a00; }
.chip-bad { color: var(--bad); }
.chip-muted { color: var(--muted); }
@media (prefers-color-scheme: dark) { .chip-warn { color: var(--warn); } }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 900px) { .chart-grid { grid-template-columns: 1fr; } }
.chart-card {
  background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px;
}
.chart-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px; }
.chart-title { font-size: 0.88rem; font-weight: 600; }
.legend { display: flex; gap: 12px; font-size: 0.78rem; color: var(--text-secondary); }
.legend-item { display: flex; align-items: center; gap: 4px; }
.swatch { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
.swatch-plan { background: var(--series-plan); }
.swatch-actual { background: var(--series-actual); }
.chart-svg { width: 100%; height: auto; display: block; }
.bar-plan { fill: var(--series-plan); }
.bar-actual { fill: var(--series-actual); }
.baseline { stroke: var(--axis); stroke-width: 1; }
.axis-label { fill: var(--muted); font-size: 8px; }
.footnote { color: var(--muted); font-size: 0.8rem; margin-top: 24px; }
"""


def main():
    plan = load_json(os.path.join(DATA_DIR, "kpi_plan_2026.json"))
    bsc = load_json(os.path.join(DATA_DIR, "bsc_okr_2026.json"))

    if len(sys.argv) > 1:
        actuals_path = sys.argv[1]
        actuals = load_json(actuals_path) if os.path.exists(actuals_path) else None
    else:
        real_path = os.path.join(DATA_DIR, "actuals_2026.json")
        example_path = os.path.join(DATA_DIR, "actuals_2026.example.json")
        if os.path.exists(real_path):
            actuals = load_json(real_path)
        elif os.path.exists(example_path):
            actuals = load_json(example_path)
            actuals["_is_example"] = True
        else:
            actuals = None

    html_out = build_dashboard(plan, bsc, actuals)
    out_path = os.path.join(REPORTS_DIR, "dashboard.html")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html_out)
    print(f"Da ghi {out_path}")


if __name__ == "__main__":
    main()

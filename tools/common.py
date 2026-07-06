"""Shared helpers for the KPI toolchain."""
import glob
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")


def find_pdf(keyword):
    matches = [f for f in glob.glob(os.path.join(REPO_ROOT, "*.pdf")) if keyword in f]
    if not matches:
        raise FileNotFoundError(f"No PDF containing '{keyword}' found in {REPO_ROOT}")
    return matches[0]


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


MONTHS = [f"T{i}" for i in range(1, 13)]


def fmt_vnd(n):
    return f"{n:,.0f}"

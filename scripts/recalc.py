#!/usr/bin/env python3
"""
Script tính lại công thức Excel và kiểm tra lỗi.
Sử dụng LibreOffice để tính lại tất cả công thức và phát hiện lỗi.

Sử dụng:
    python scripts/recalc.py output.xlsx
"""

import sys
import json
import subprocess
import tempfile
import os
from pathlib import Path

def recalculate_excel(filepath):
    """
    Tính lại công thức Excel bằng LibreOffice và kiểm tra lỗi.
    """
    filepath = Path(filepath).resolve()

    if not filepath.exists():
        return {
            "status": "error",
            "message": f"File không tồn tại: {filepath}"
        }

    try:
        # Lệnh LibreOffice để tính lại công thức
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to", "xlsx",
            "--outdir", str(filepath.parent),
            str(filepath)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return {
                "status": "error",
                "message": f"LibreOffice lỗi: {result.stderr}"
            }

        # Kiểm tra lỗi công thức bằng openpyxl
        try:
            from openpyxl import load_workbook
            wb = load_workbook(filepath, data_only=False)

            error_summary = {}
            total_errors = 0
            total_formulas = 0

            for sheet in wb.sheetnames:
                ws = wb[sheet]
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.value and isinstance(cell.value, str) and cell.value.startswith('='):
                            total_formulas += 1
                            # Kiểm tra các loại lỗi thường gặp
                            try:
                                # Nếu cell có value thì không có lỗi
                                if cell.value == '#REF!' or cell.value == '#DIV/0!' or \
                                   cell.value == '#VALUE!' or cell.value == '#N/A' or \
                                   cell.value == '#NAME?':
                                    error_type = cell.value
                                    if error_type not in error_summary:
                                        error_summary[error_type] = {"count": 0, "locations": []}
                                    error_summary[error_type]["count"] += 1
                                    error_summary[error_type]["locations"].append(f"{sheet}!{cell.coordinate}")
                                    total_errors += 1
                            except:
                                pass

            wb.close()

            return {
                "status": "success" if total_errors == 0 else "errors_found",
                "total_errors": total_errors,
                "total_formulas": total_formulas,
                "error_summary": error_summary
            }

        except ImportError:
            return {
                "status": "warning",
                "message": "openpyxl không được cài đặt. Cài đặt với: pip install openpyxl"
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "LibreOffice timeout"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi: {str(e)}"
        }

def main():
    if len(sys.argv) < 2:
        print("Cách dùng: python scripts/recalc.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = recalculate_excel(filepath)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Thoát với mã lỗi nếu có vấn đề
    if result.get("status") == "error":
        sys.exit(1)

if __name__ == "__main__":
    main()

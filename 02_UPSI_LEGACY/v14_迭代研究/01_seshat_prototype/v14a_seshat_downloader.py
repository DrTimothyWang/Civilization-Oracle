#!/usr/bin/env python3
"""
v14a_seshat_downloader.py
Downloads Seshat Equinox-2020 data from Zenodo or GitHub mirror.
Handles errors, validates download, extracts Excel contents.
"""

import os
import sys
import hashlib
import zipfile
import requests
import time

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ZENODO_ZIP_URL = "https://zenodo.org/records/6642230/files/seshatdb/Equinox_Data-v.1.zip?download=1"
GITHUB_ZIP_URL = "https://github.com/seshatdb/Equinox_Data/archive/refs/heads/main.zip"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(OUTPUT_DIR, "equinox_data.zip")
EXCEL_NAME = "Equinox_on_GitHub_June9_2022.xlsx"
EXPECTED_SHEETS = [
    "Metadata", "Equinox2020_CanonDat", "CavIronHSData", "HistYield+",
    "TSDat123", "AggrSCWarAgriRelig", "ImpSCDat", "SPC_MilTech",
    "Polities", "Variables", "NGAs", "Scale_MI", "Class_MI"
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def download_file(url, path, max_retries=5, timeout=120):
    """Download with exponential backoff."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Attempt {attempt}/{max_retries}] Downloading from {url} ...")
            resp = requests.get(url, stream=True, timeout=timeout)
            resp.raise_for_status()
            with open(path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  -> Saved {path} ({size_mb:.2f} MB)")
            return True
        except Exception as e:
            print(f"  -> Error: {e}")
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"  -> Retrying in {wait}s ...")
                time.sleep(wait)
    return False


def validate_zip(path):
    """Basic ZIP integrity check."""
    try:
        with zipfile.ZipFile(path, "r") as z:
            bad = z.testzip()
            if bad:
                print(f"[WARN] ZIP corrupt: first bad file = {bad}")
                return False
            namelist = z.namelist()
            print(f"[OK] ZIP valid. {len(namelist)} entries.")
            return True
    except Exception as e:
        print(f"[ERROR] ZIP validation failed: {e}")
        return False


def extract_excel(path):
    """Extract and locate the Excel workbook inside the ZIP."""
    with zipfile.ZipFile(path, "r") as z:
        namelist = z.namelist()
        excel_members = [n for n in namelist if n.endswith(".xlsx")]
        if not excel_members:
            print("[ERROR] No .xlsx file found inside ZIP.")
            return None
        # Extract all
        z.extractall(OUTPUT_DIR)
        # Find extracted Excel
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for f in files:
                if f.endswith(".xlsx"):
                    return os.path.join(root, f)
    return None


def verify_sheets(excel_path):
    """Check that expected sheets are present."""
    try:
        import pandas as pd
        xls = pd.ExcelFile(excel_path)
        missing = [s for s in EXPECTED_SHEETS if s not in xls.sheet_names]
        if missing:
            print(f"[WARN] Missing sheets: {missing}")
            return False
        print(f"[OK] All {len(EXPECTED_SHEETS)} expected sheets present.")
        return True
    except Exception as e:
        print(f"[ERROR] Cannot read Excel: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    status = {
        "zenodo_success": False,
        "github_fallback": False,
        "zip_valid": False,
        "excel_path": None,
        "sheets_ok": False,
        "file_size_mb": 0.0,
        "error_log": []
    }

    # 1. Try Zenodo
    if download_file(ZENODO_ZIP_URL, ZIP_PATH):
        status["zenodo_success"] = True
    else:
        status["error_log"].append("Zenodo download failed after all retries.")
        print("[INFO] Zenodo failed. Trying GitHub mirror ...")
        if download_file(GITHUB_ZIP_URL, ZIP_PATH):
            status["github_fallback"] = True
        else:
            status["error_log"].append("GitHub mirror also failed.")
            print("[FATAL] Both download sources failed.")
            # Write status JSON for downstream fallback
            import json
            with open(os.path.join(OUTPUT_DIR, "v14a_download_status.json"), "w") as f:
                json.dump(status, f, indent=2)
            sys.exit(1)

    status["file_size_mb"] = round(os.path.getsize(ZIP_PATH) / (1024 * 1024), 2)

    # 2. Validate ZIP
    status["zip_valid"] = validate_zip(ZIP_PATH)
    if not status["zip_valid"]:
        status["error_log"].append("ZIP validation failed.")

    # 3. Extract Excel
    excel_path = extract_excel(ZIP_PATH)
    if excel_path:
        status["excel_path"] = excel_path
        print(f"[OK] Excel located: {excel_path}")
    else:
        status["error_log"].append("Excel extraction failed.")
        print("[FATAL] Could not locate Excel workbook.")
        import json
        with open(os.path.join(OUTPUT_DIR, "v14a_download_status.json"), "w") as f:
            json.dump(status, f, indent=2)
        sys.exit(1)

    # 4. Verify sheets
    status["sheets_ok"] = verify_sheets(excel_path)
    if not status["sheets_ok"]:
        status["error_log"].append("Sheet verification failed.")

    # 5. Save status
    import json
    with open(os.path.join(OUTPUT_DIR, "v14a_download_status.json"), "w") as f:
        json.dump(status, f, indent=2)

    print("\n[DOWNLOAD COMPLETE]")
    print(f"  Source: {'Zenodo' if status['zenodo_success'] else 'GitHub fallback'}")
    print(f"  ZIP size: {status['file_size_mb']} MB")
    print(f"  Excel: {status['excel_path']}")
    print(f"  Sheets OK: {status['sheets_ok']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Simple "AltStore"-style server: upload an IPA and install it to a connected iOS device.

This is intentionally minimal: it accepts an uploaded `.ipa`, saves it to a temp file, and
runs `ideviceinstaller -i <path>` to side-load it onto the first attached device.

Requirements:
  - Python 3
  - Flask (pip install -r requirements.txt)
  - libimobiledevice + ideviceinstaller (system package)

Usage:
  1) Install system deps: `sudo apt install libimobiledevice-utils ideviceinstaller`
  2) Install Python deps: `python3 -m pip install -r requirements.txt`
  3) Run: `python3 app.py`
  4) Open http://localhost:5000 and upload an IPA.
"""

import os
import subprocess
import tempfile
from typing import Optional

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.urandom(32)

UPLOAD_FIELD = "ipa_file"
MAX_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024  # 1 GB

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def get_connected_devices() -> list[str]:
    """Return a list of connected device UDIDs using idevice_id."""
    try:
        completed = subprocess.run(
            ["idevice_id", "-l"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if completed.returncode != 0:
            return []
        return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    except FileNotFoundError:
        return []
    except subprocess.TimeoutExpired:
        return []


def install_ipa(ipa_path: str, udid: Optional[str] = None) -> tuple[int, str]:
    """Run ideviceinstaller to install the IPA and return (exit_code, output)."""
    cmd = ["ideviceinstaller"]
    if udid:
        cmd += ["-u", udid]
    cmd += ["-i", ipa_path]

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
        )
        output = completed.stdout + completed.stderr
        return completed.returncode, output
    except FileNotFoundError:
        return 127, "ideviceinstaller not found. Install libimobiledevice-utils + ideviceinstaller."
    except subprocess.TimeoutExpired as e:
        return 124, f"ideviceinstaller timed out: {e}"


@app.route("/", methods=["GET", "POST"])
def upload():
    result = None
    devices = get_connected_devices()
    selected_udid = None

    if request.method == "POST":
        selected_udid = request.form.get("device_udid")
        ipa = request.files.get(UPLOAD_FIELD)
        if not ipa or ipa.filename == "":
            flash("No IPA file selected", "danger")
            return redirect(request.url)

        filename = ipa.filename
        if not filename.lower().endswith(".ipa"):
            flash("File does not appear to be an .ipa", "warning")

        with tempfile.NamedTemporaryFile(prefix="altstore-", suffix=".ipa", delete=False) as tmp:
            ipa.save(tmp.name)
            tmp_path = tmp.name

        exit_code, output = install_ipa(tmp_path, udid=selected_udid)
        os.unlink(tmp_path)

        result = {
            "exit_code": exit_code,
            "output": output.strip(),
            "filename": filename,
            "udid": selected_udid,
        }

        devices = get_connected_devices()

    return render_template(
        "index.html",
        result=result,
        devices=devices,
        selected_udid=selected_udid,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

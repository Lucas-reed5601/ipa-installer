# ipa-installer

A minimal "AltStore"-style uploader+installer for `.ipa` files.

This repository contains a small Flask web server that accepts an `.ipa` upload and runs `ideviceinstaller -i` to install it on a connected iOS device.

## 🧰 Setup

### 1) Install system dependencies (Linux)

```bash
sudo apt update
sudo apt install -y libimobiledevice-utils ideviceinstaller
```

### 2) Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3) Run the server

```bash
python3 app.py
```

Then open: http://localhost:5000

## 📌 How it works

- The server accepts an `.ipa` via a web form.
- It uses `ideviceinstaller` to install the IPA on a connected iPhone/iPad (via USB).
- If multiple devices are connected, you can choose which one to target.

## ⚠️ What this is (and is not)

- ✅ Works without jailbreaking (it uses Apple’s public APIs via `libimobiledevice`).
- ✅ Works with a **signed** `.ipa` that is valid for the target device.
- ❌ **Does not bypass Apple restrictions** (you still need a proper provisioning profile / signing).
- ❌ Not a full AltStore reimplementation (no signing server, no automatic refresh, no iOS companion app).

## 📎 Troubleshooting

- If you see “No connected devices detected”, make sure your iPhone/iPad is connected via USB and trusted.
- If install fails, check the output on the page; `ideviceinstaller` will report the reason.

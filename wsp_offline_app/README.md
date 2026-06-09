# WSP Offline System

Offline Windows application for importing WSP Excel files, searching and filtering student records with semantic (AI) search, exporting results, and maintaining a full history through archives and backups.

The app runs entirely on your machine — no internet connection is required after the first setup, and no data ever leaves the computer.

---

## What you need to install externally

**Only one thing: Python 3.11 or newer.**

Download from [python.org](https://www.python.org/downloads/). During installation check **"Add Python to PATH"**.

Everything else (FastAPI, the AI embedding model, the database, all Python packages) is bundled inside the app folder and installed automatically by `setup.bat`.

No Ollama. No Node.js. No Docker. No other tools.

---

## First-time setup on a new machine

1. Copy the `wsp_offline_app/` folder to the new machine (USB, shared drive, etc.)
2. Install Python 3.11+ from python.org (one time only per machine)
3. Double-click **`setup.bat`**

`setup.bat` will:
- Create a Python virtual environment (`.venv/`) inside the app folder
- Install all Python packages (~10 minutes, needs internet once)
- Create a **"WSP Offline System"** shortcut on the Desktop

After that, the machine is fully set up. You never need to open a terminal again.

---

## Launching the app

Double-click the **"WSP Offline System"** shortcut on the Desktop, or double-click **`launch.bat`**.

- The app opens in its own browser window automatically (no address bar, no tabs — looks like a desktop app)
- A tray icon appears in the bottom-right taskbar corner

---

## Does closing the window stop the app?

**No.** Closing the browser window does not stop the server. The tray icon keeps it running so you can reopen it any time.

To fully stop the app: **right-click the tray icon → Exit**.

If you want the browser window back: double-click the tray icon, or right-click → Open WSP.

---

## Updating the app (code changes)

**No reinstall needed for code changes.**

When you change `.py`, `.js`, or `.css` files, just:

1. Right-click the tray icon → **Exit** (stops the server)
2. Copy in the new files
3. Double-click the shortcut or `launch.bat` to relaunch

The app reads source files fresh on every launch. No compilation, no cache to clear.

If `requirements.txt` changed (new Python packages were added), run **`update.bat`** instead — it installs only the new packages (~30 seconds) without rebuilding the whole environment.

### Summary

| What changed | What to do |
|---|---|
| `.py` / `.js` / `.css` files | Exit tray → relaunch |
| `requirements.txt` (new packages) | Run `update.bat` |
| Complete fresh install on new machine | Run `setup.bat` |
| Something broken, want a clean slate | Delete `.venv/`, run `setup.bat` |

---

## Uninstalling

Delete the `wsp_offline_app/` folder. Nothing is written outside it except:
- The Desktop shortcut (delete manually)
- The Python install itself (uninstall via Windows Settings if you no longer need Python)

---

## Bundling the AI model for offline portability

The semantic search uses `mixedbread-ai/mxbai-embed-large-v1` (~670 MB). By default it downloads to `~/.cache/huggingface/`. To bundle it inside the app folder so it works on any machine without re-downloading:

Run this **once** on the machine that already has the model cached:

```
.venv\Scripts\python scripts\bundle_model.py
```

This copies the model into `.models/` inside the app folder. All future launches use it from there automatically.

---

## Deploying updates

### Git-managed (recommended)

```
update.bat
```

Pulls latest code and syncs packages. Takes seconds if no new packages were added.

### USB / manual file copy

1. Copy updated files into the app folder
2. Double-click `update.bat` to sync packages if `requirements.txt` changed

---

## Running `setup.bat` again

Safe to re-run at any time. It will update packages if `requirements.txt` changed and recreate the Desktop shortcut. Use it as a "repair" if something seems broken.

---

## What travels in the folder (portability table)

| Component | Portable? | Notes |
|---|---|---|
| App code (`.py`, `.js`, `.css`) | Yes | Just copy |
| Database (`data/wsp.db`) | Yes | User data, never overwritten by updates |
| AI model (`.models/`) | Yes | After running `bundle_model.py` once |
| Python packages (`.venv/`) | No | Rebuilt by `setup.bat` (~10 min, internet once) |
| Python itself | No | One-time install per machine |

---

## Development

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Start the server with a visible console (for log output during development):

```powershell
.\.venv\Scripts\python.exe main.py
```

Generate test workbooks:

```powershell
.\.venv\Scripts\python.exe scripts\create_test_workbooks.py
```

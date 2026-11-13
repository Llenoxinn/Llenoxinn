import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def capture(html_file, out_name, w=1000, h=2200):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    temp_dir = os.environ.get("TEMP", r"C:\Users\Dexter\AppData\Local\Temp")
    user_data = os.path.join(temp_dir, f"ch-profile-{out_name.split('.')[0]}-{int(time.time())}")

    artifact_dir = Path(r"C:\Users\Dexter\.gemini\antigravity\brain\49d2a9f8-5e8a-4042-b59a-bb63603ab3ee")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    repo_shots = ROOT / "output" / "screenshots"
    repo_shots.mkdir(parents=True, exist_ok=True)

    target_html = (ROOT / "output" / html_file).resolve()
    target_png = artifact_dir / out_name
    repo_png = repo_shots / out_name

    if target_png.exists():
        target_png.unlink()

    file_uri = target_html.as_uri()
    cmd = [
        chrome_path,
        "--headless=new",
        f"--user-data-dir={user_data}",
        f"--screenshot={target_png}",
        f"--window-size={w},{h}",
        "--virtual-time-budget=2500",
        "--hide-scrollbars",
        file_uri
    ]

    print(f"Capturing {html_file} -> {out_name}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if target_png.exists():
        print(f"Success: {target_png} ({target_png.stat().st_size} bytes)")
        shutil.copy2(target_png, repo_png)
        print(f"Copied to {repo_png}")
    else:
        print(f"Failed to capture {out_name}: {res.stderr}")

def main():
    capture("preview-dark.html", "preview-dark.png")
    capture("preview-light.html", "preview-light.png")

if __name__ == "__main__":
    main()

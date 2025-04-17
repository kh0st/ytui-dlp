#!/usr/bin/env python3
import os
import sys
import json
import shutil
import subprocess
import argparse
# Path to cookies file for yt-dlp/youtube-dl
COOKIES_FILE = os.path.expanduser("~/.youtube.txt")
# Determine if cookies file is available; skip cookies if missing
USE_COOKIES = os.path.isfile(COOKIES_FILE)

try:
    import questionary
except ImportError:
    print("Missing dependency 'questionary'. Run: pip install questionary")
    sys.exit(1)

YT_DLP = shutil.which("yt-dlp") or shutil.which("youtube-dl")
FFPLAY = shutil.which("ffplay")

def get_entries(query: str, search: bool = False):
    """Fetch video/playlist metadata using yt-dlp JSON interface."""
    # Build base command, include cookies if available
    if search:
        url = f"ytsearch5:{query}"
        cmd = [YT_DLP]
        if USE_COOKIES:
            cmd += ["--cookies-from-browser", "firefox"]
        cmd += ["--dump-single-json", "--flat-playlist", url]
    else:
        url = query
        cmd = [YT_DLP]
        if USE_COOKIES:
            cmd += ["--cookies-from-browser", "firefox"]
        cmd += ["-J", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        err = result.stderr.strip() or result.stdout.strip()
        print("Error fetching info: yt-dlp failed to return valid JSON.")
        if err:
            print(err)
        sys.exit(1)
    # If a playlist or search result, yt-dlp returns 'entries'
    if isinstance(data, dict) and data.get("entries"):
        return data["entries"]
    # Single video
    return [data]

def select_entry(entries):
    """Prompt user to select one entry from a list."""
    choices = [f"{i+1}. {e.get('title', 'Untitled')}" for i, e in enumerate(entries)]
    answer = questionary.select("Select media to download:", choices=choices).ask()
    idx = choices.index(answer)
    return entries[idx]

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="YouTube downloader with cookie support")
    parser.add_argument("--cookies-from-browser", metavar="BROWSER", choices=["chrome", "firefox", "chromium", "edge", "opera", "safari"], help="Import cookies from browser non-interactively.")
    parser.add_argument("--cookies-file", metavar="FILE", help="Path to existing cookies file to use.")
    parser.add_argument("--no-cookies", action="store_true", help="Continue without using cookies (may fail).")
    args = parser.parse_args()
    # Check for yt-dlp availability
    if not YT_DLP:
        print("Error: yt-dlp (or youtube-dl) not found in PATH.")
        sys.exit(1)


    global COOKIES_FILE, USE_COOKIES
    # Handle --cookies-file
    if args.cookies_file:
        expanded = os.path.expanduser(args.cookies_file)
        if not os.path.isfile(expanded):
            print(f"Cookies file not found at {expanded}. Exiting.")
            sys.exit(1)
        COOKIES_FILE = expanded
        USE_COOKIES = True
    # Handle --cookies-from-browser
    elif args.cookies_from_browser:
        print(f"Ensure you are signed into {args.cookies_from_browser} in your browser and have visited YouTube.")
        input("Press Enter to continue...")
        print(f"Importing cookies from {args.cookies_from_browser} into {COOKIES_FILE}...")
        result = subprocess.run([YT_DLP, "--cookies-from-browser", args.cookies_from_browser, "--cookies", COOKIES_FILE, "https://www.youtube.com"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully imported cookies from {args.cookies_from_browser}.")
            USE_COOKIES = True
        else:
            err = result.stderr.strip() or result.stdout.strip()
            print("Error importing cookies:")
            if err:
                print(err)
            sys.exit(1)
    # Handle --no-cookies
    elif args.no_cookies:
        USE_COOKIES = False

    # Interactive cookie setup only if no cookie-related flags provided
    skip_cookie_setup = args.cookies_file or args.cookies_from_browser or args.no_cookies

    # Setup cookies file if missing
    if not skip_cookie_setup and not os.path.isfile(COOKIES_FILE):
        print("First-time setup: ensure you are signed into Firefox in your browser (with your YouTube account) so cookies can be imported, or provide a path to an existing cookies file.")
        choice = questionary.select(
            f"Cookies file not found at {COOKIES_FILE}. How would you like to proceed?",
            choices=[
                "Import cookies from browser",
                "Provide path to existing cookies file",
                "Continue without cookies (may fail)",
                "Exit"
            ]
        ).ask()
        if choice == "Import cookies from browser":
            print("Attempting automatic cookie import from Chrome and Firefox...")
            success = False
            for browser in ["chrome", "firefox"]:
                print(f"Trying to import cookies from {browser}...")
                result = subprocess.run(
                    [YT_DLP, "--cookies-from-browser", browser, "--cookies", COOKIES_FILE, "https://www.youtube.com"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"Successfully imported cookies from {browser}.")
                    success = True
                    USE_COOKIES = True
                    break
                else:
                    err = result.stderr.strip() or result.stdout.strip()
                    print(f"Failed to import from {browser}: {err}")
            if not success:
                browser = questionary.select(
                    "Automatic import failed. Select browser manually:",
                    choices=["chrome", "firefox", "chromium", "edge", "opera", "safari"]
                ).ask()
                print(f"Importing cookies from {browser} into {COOKIES_FILE}...")
                result = subprocess.run(
                    [YT_DLP, "--cookies-from-browser", browser, "--cookies", COOKIES_FILE, "https://www.youtube.com"],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    print("Error importing cookies:")
                    if result.stderr:
                        print(result.stderr.strip())
                    sys.exit(1)
                USE_COOKIES = True
        elif choice == "Provide path to existing cookies file":
            path = questionary.text("Enter path to cookies file:", default=COOKIES_FILE).ask()
            expanded = os.path.expanduser(path)
            if not os.path.isfile(expanded):
                print(f"Cookies file not found at {expanded}. Exiting.")
                sys.exit(1)
            COOKIES_FILE = expanded
            USE_COOKIES = True
        elif choice == "Continue without cookies (may fail)":
            USE_COOKIES = False
        else:
            sys.exit(0)

    action = questionary.select(
        "Choose action:",
        choices=["Paste URL/ID", "Search YouTube"]
    ).ask()

    if action == "Search YouTube":
        term = questionary.text("Enter search term:").ask()
        entries = get_entries(term, search=True)
        url = f"ytsearch5:{term}"
    else:
        url = questionary.text("Enter video or playlist URL:").ask()
        entries = get_entries(url, search=False)

    download_type = questionary.select(
        "Download type:",
        choices=["Video", "Audio", "Playlist"]
    ).ask()

    # Select single item if not playlist download
    if download_type != "Playlist" and len(entries) > 1:
        entry = select_entry(entries)
        url = entry.get("webpage_url") or entry.get("url") or url
    else:
        entry = entries[0] if entries else {}

    audio_format = "mp3"
    if download_type in ("Audio", "Playlist"):
        audio_format = questionary.select(
            "Audio format:",
            choices=["mp3", "wav"],
            default="mp3"
        ).ask()

    default_dir = os.path.expanduser("~/Downloads")
    output_dir = questionary.text("Output directory:", default=default_dir).ask()
    os.makedirs(output_dir, exist_ok=True)

    # Build yt-dlp command, include cookies if available
    cmd = [YT_DLP]
    if USE_COOKIES:
        cmd += ["--cookies-from-browser", "firefox"]
    if download_type in ("Audio", "Playlist"):
        cmd += ["-x", "--audio-format", audio_format]
    # Output template
    cmd += ["-o", os.path.join(output_dir, "%(title)s.%(ext)s")]
    cmd += [url]

    print("\nStarting download...\n")
    subprocess.run(cmd)

    # Preview option
    preview = questionary.confirm("Preview downloaded file?").ask()
    if preview:
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
        files = [f for f in files if os.path.isfile(f)]
        if not files:
            print("No files found to preview.")
            return
        latest = max(files, key=lambda f: os.path.getmtime(f))
        if FFPLAY:
            preview_cmd = [FFPLAY, "-nodisp", "-autoexit", latest]
            subprocess.run(preview_cmd)
        else:
            print(f"ffplay not found; cannot preview {latest}")

    print("\nAll done!")

if __name__ == "__main__":
    main()

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## TUI Downloader

A standalone Python-based TUI downloader using `yt-dlp` and `ffplay`.
- Paste a video/playlist URL or search YouTube.
- Download video or extract audio (MP3 or WAV).
- Download entire playlists.
- Preview downloaded files with `ffplay`.
- Import cookies from browser or specify a cookies file to access age-restricted or region-locked content.

Installation on Arch Linux:
1. Install system dependencies:
   ```bash
   sudo pacman -S yt-dlp ffmpeg
   ```
2. Install Python dependency:
   ```bash
   pip install questionary
   ```
3. Make the script executable:
   ```bash
   chmod +x ytui.py
   ```
4. Run:
   ```bash
   ./ytui.py
   # or explicitly with Python:
   python3 ytui.py
   ```

Optional: build a standalone binary
```bash
pip install pyinstaller
pyinstaller --onefile ytui.py
# The executable will be under dist/ (e.g. dist/ytui or dist/ytui.exe on Windows)
```
To build locally for your current platform (Linux, macOS, or Windows with Python installed), run the above commands.
For automated multi-platform builds (Linux, macOS, and Windows), a GitHub Actions workflow is provided in
`.github/workflows/build.yml`. On each push to `main` or new release, binaries will be built and
uploaded as artifacts for all supported operating systems.

# Clipper Hub Cheat Pro

AI auto clipper: turn long YouTube, Google Drive or uploaded videos into short vertical clips with animated subtitles, face-centred framing, title hooks, music and watermarks.

Based on [Cheat Clip Pro](https://github.com/galihjuansaputra/cheat-clip-pro) by Galih Juan Saputra (MIT License), restyled with a navy / blue-glow interface, a simpler source form, a password login and a Railway deployment setup.

## Features

- Sources: YouTube link, Google Drive link, or file upload
- Gemini or OpenRouter finds the most viral moments using the audience heatmap and transcript
- Clip list with virality score, hooks, title and caption ideas, search, filter and export
- Auto clipper studio: 9:16 / 1:1 / 4:3 / 16:9 framing, AI face centring, facecam layouts, karaoke subtitles, title banner, background music, hook SFX, watermark
- Batch render and download as ZIP
- Password login for hosted use

## Deploy on Railway

The repo contains a `Dockerfile` and `railway.json`; Railway builds and runs it as one service.

1. Railway → **New Project → Deploy from GitHub repo** → pick this repo.
2. Service → **Variables**:
   - `APP_PASSWORD`: password for the login screen (required on a public URL)
   - `GEMINI_API_KEY` (optional): server key so you do not paste one each time
   - `SUPADATA_API_KEYS`, `WEBSHARE_PROXY` (optional): more reliable YouTube transcripts and downloads
3. Service → **Volumes → Add volume**, mount path `/data` (keeps renders and cookies across redeploys).
4. Service → **Settings → Networking → Generate Domain**.

YouTube often blocks downloads from cloud servers ("Sign in to confirm you're not a bot"). Use **Cookies → Setup** in the app to add your YouTube cookies, or set a proxy. Rendering runs on CPU (no GPU on Railway), so long batches take a while.

## Run locally

Requirements: Node.js 18+, Python 3.10+, FFmpeg and yt-dlp.

```bash
npm install
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
npm run dev
```

Open http://localhost:5173. Type `mock` as the Gemini key to try the interface with sample data. `APP_PASSWORD` is optional locally.

## License

MIT. See `LICENSE`.

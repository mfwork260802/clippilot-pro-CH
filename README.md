# Clipper Hub Cheat Pro

AI auto clipper: turn long YouTube, Google Drive or uploaded videos into short vertical clips with animated subtitles, face-centred framing, title hooks, music and watermarks.

Based on [Cheat Clip Pro](https://github.com/galihjuansaputra/cheat-clip-pro) by Galih Juan Saputra (MIT License). Smart-editing ideas were inspired by [opensource-clipping](https://github.com/NaufalRizqullah/opensource-clipping) (MIT) and [ViralMint](https://github.com/openclaw-easy/ViralMint) (concepts only; no code copied). Restyled with a navy / blue-glow interface, a simpler source form, a password login and a Railway deployment setup.

## Features

- Sources: YouTube link, Google Drive link, or file upload
- Gemini or OpenRouter finds the most viral moments using the audience heatmap and transcript
- Clip list with virality score, hooks, title and caption ideas, search, filter and export
- Auto clipper studio: 9:16 / 1:1 / 4:3 / 16:9 framing, AI face centring, facecam layouts, karaoke subtitles, title banner, background music, hook SFX, watermark
- Batch render and download as ZIP
- Password login for hosted use

### Smart editing (server render)

- **Follow the speaker**: faces are tracked through the whole clip and the crop pans smoothly (deadzone, easing, anti-jitter, snap on scene cuts)
- **Remove silent gaps**: dead air longer than a threshold is cut; captions and the hook stay in sync
- **Teaser intro**: opens with ~3s of the hook moment, then a flash cut into the clip
- **Auto zoom**: subtle punch-in that alternates on each new sentence (captions are not zoomed)
- **Music ducking**: background music dips automatically while someone speaks
- **Cover image**: a JPG thumbnail per clip (speaker-centred frame + title)
- **Render check**: every output is probed (video/audio streams, duration) before it is marked done
- **Platform safe zones**: one click moves title/captions out of the TikTok/Reels/Shorts UI, with on-preview guides

### Smarter analysis

- Clips are snapped to sentence boundaries, so they never start or end mid-word (also available as "Snap to sentences" in the trimmer)
- Five AI scores per clip (hook, flow, value, trend, shareability) with a one-line reason
- Word timings come straight from YouTube auto-captions when available, so Whisper is skipped
- Transcription uses faster-whisper (int8 on CPU): much faster and lighter than PyTorch Whisper

## Deploy on Railway

The repo contains a `Dockerfile` and `railway.json`; Railway builds and runs it as one service.

1. Railway → **New Project → Deploy from GitHub repo** → pick this repo.
2. Service → **Variables**:
   - `APP_PASSWORD`: password for the login screen (required on a public URL)
   - `GEMINI_API_KEY` (optional): server key so you do not paste one each time
   - `SUPADATA_API_KEYS`, `WEBSHARE_PROXY` (optional): more reliable YouTube transcripts and downloads
   - `WHISPER_MODEL` (optional, default `small`): `base` or `tiny` for very small servers
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

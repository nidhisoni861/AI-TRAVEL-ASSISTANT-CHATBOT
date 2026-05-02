# Run-from-scratch guide

Hand this to a teammate (or your future self on a fresh laptop). Total time: **~15 min** + waiting for downloads.

---

## 0. Prerequisites — install once

| Tool | Version | Where |
|---|---|---|
| **Python** | **3.11** (NOT 3.12+, NOT 3.10) | https://www.python.org/downloads/release/python-3119/ |
| **Node.js** | 18 LTS or newer | https://nodejs.org/ |
| **Git** | any | https://git-scm.com/ |
| **Chrome** or **Edge** | latest | (voice input only works in these) |

> ⚠️ **Python 3.11 is critical**. `torch`, `chromadb`, and `bitsandbytes` don't have wheels for Python 3.13+ yet. If you only have 3.12 or newer, install 3.11 alongside (Windows installer keeps multiple versions cleanly).

Verify after install:
```bash
py -3.11 --version    # Windows: should print "Python 3.11.x"
python3.11 --version  # macOS/Linux
node --version        # v18+
```

---

## 1. Get the code

```bash
git clone <your-repo-url> ai-travel-assistant
cd ai-travel-assistant
```

Or just copy/paste the project folder.

---

## 2. Get the API keys

You'll need **two** keys. Both are free, total signup time ~10 min.

### a) HuggingFace token (REQUIRED — for the LLM)

1. Sign up: https://huggingface.co/join
2. Accept these model licenses (one click each):
   - https://huggingface.co/Qwen/Qwen2.5-7B-Instruct (no acceptance needed, but verify it loads)
   - https://huggingface.co/google/gemma-2-2b-it (only if you want to fine-tune)
3. Create token: https://huggingface.co/settings/tokens
   - **Type**: Fine-grained
   - **Permissions**: tick **"Make calls to Inference Providers"** + **"Read access to public gated repos"**
   - Copy the `hf_...` value

### b) OpenWeatherMap (for live weather — backend uses mocks if missing)

1. Sign up: https://home.openweathermap.org/users/sign_up (Purpose: "Education / Science")
2. Confirm email.
3. Copy the default API key from the **API keys** tab.

> **Skip Amadeus and Google Places** — Amadeus self-service was decommissioned, Google Places needs a credit card. The backend uses realistic mock data for flights/places.

---

## 3. Backend setup

### Windows (PowerShell)

```powershell
cd ai-travel-assistant\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
cd ai-travel-assistant/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> ⏱ The `pip install` takes **~5 min** (downloads torch, ~2 GB total). If it errors on `bitsandbytes` on Windows, that's fine — it's only used for fine-tuning on Linux.

### Configure `.env`

Copy the template and fill in your keys:

```bash
# Windows
copy .env.example .env
# macOS/Linux
cp .env.example .env
```

Open `backend/.env` in any editor and set:

```ini
BASE_MODEL=Qwen/Qwen2.5-7B-Instruct
HF_API_TOKEN=hf_PASTE_YOUR_TOKEN_HERE
USE_HF_INFERENCE_API=true
LORA_ADAPTER_PATH=

OPENWEATHERMAP_API_KEY=PASTE_YOUR_OWM_KEY_HERE
AMADEUS_API_KEY=
AMADEUS_API_SECRET=
GOOGLE_PLACES_API_KEY=

APP_HOST=0.0.0.0
APP_PORT=8001
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
CHROMA_DIR=./chroma_db
LOG_LEVEL=INFO
```

> 📌 `APP_PORT=8001` — we avoid port 8000 because it's commonly taken (e.g. Laravel, Django default).

---

## 4. Frontend setup

```bash
cd ../frontend
npm install
```

```bash
# Windows
copy .env.example .env.local
# macOS/Linux
cp .env.example .env.local
```

`frontend/.env.local`:
```ini
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
```

---

## 5. Run it

You need **two terminals open at the same time**.

### Terminal 1 — backend

```powershell
# Windows
cd ai-travel-assistant\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

```bash
# macOS/Linux
cd ai-travel-assistant/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Wait for: `INFO: Application startup complete.`

First run downloads the sentence-transformers embedding model (~80 MB, takes ~30s). Subsequent starts are instant.

### Terminal 2 — frontend

```bash
cd ai-travel-assistant/frontend
npm run dev
```

Wait for: `✓ Ready in Xs`

Open the URL Next.js prints — usually **http://localhost:3000** but it'll fall back to 3001 / 3002 if 3000 is taken.

> ⚠️ **If Next picks a port other than 3000–3002**, add it to `ALLOWED_ORIGINS` in `backend/.env` and restart the backend.

---

## 6. Verify

Open the printed URL in Chrome. You should see "Wanderly" with starter buttons. Try each one:

| Test | Expected |
|---|---|
| Click "What's the weather in Reykjavik?" | Weather card with live temp |
| Click "Find flights from FRA to CDG" | 4 flight cards with Book buttons |
| Click "Plan a 4-day food tour of Tokyo" | Multi-paragraph day-by-day itinerary |
| Click "Best things to do in Barcelona" | Places grid with attractions |
| Click 🎤 mic, say "weather in Paris" | Auto-transcribes and sends |
| Toggle "Voice off" → "Voice on" | Replies are read aloud |

---

## 7. Common errors & fixes

| Error | Cause | Fix |
|---|---|---|
| `pip install` fails on `tenacity` | Old requirements pin | `requirements.txt` is already fixed; pull latest |
| `pip install bitsandbytes` fails on Windows | bitsandbytes is Linux-only | Already gated in `requirements.txt`; ignore |
| `ModuleNotFoundError: No module named 'fastapi'` | venv not activated | Run the activate script first |
| `Cannot access gated repo` for Gemma | License not accepted | Visit the model page on HF and click "Acknowledge license" |
| Backend hangs on "Waiting for application startup" | Port 8001 already taken | `netstat -ano \| grep 8001`, kill or change `APP_PORT` |
| Frontend chat says "backend unreachable" | CORS or wrong port | Check `NEXT_PUBLIC_BACKEND_URL` matches backend `APP_PORT`; check `ALLOWED_ORIGINS` |
| Hydration error in browser console | Stale `.next` cache | `rm -rf frontend/.next && npm run dev` |
| Mic button missing | Using Firefox/Safari | Use Chrome or Edge |
| `'next' is not recognized` | npm install incomplete | `rm -rf node_modules && npm install` |
| Webpack runtime error after many hot reloads | Dev cache corruption | `rm -rf .next` and restart `npm run dev` |

---

## 8. What to share with teammates

| File | Share via | Why |
|---|---|---|
| Whole project folder (sans `.env`, `node_modules`, `.venv`, `.next`, `chroma_db`) | Git / zip | source code |
| `backend/.env` and `frontend/.env.local` | **Password manager / Signal / 1Password** — NEVER Git, NEVER email | contains your API keys |

Or: each teammate gets their own HuggingFace + OpenWeatherMap keys (5 min) and creates their own `.env`. Safer.

The `.gitignore` already excludes:
- `.env`, `.env.local`, `.env.*.local`
- `node_modules/`, `.venv/`, `.next/`
- `chroma_db/`, `checkpoints/`, model caches

So `git push` is safe — secrets won't leak.

---

## 9. Stopping the project

In each terminal: **Ctrl+C**.

To fully reset:

```bash
# Wipe vector DB cache
rm -rf backend/chroma_db

# Wipe Next.js cache
rm -rf frontend/.next

# Wipe HuggingFace model cache (~80MB+)
rm -rf ~/.cache/huggingface
```

---

## 10. Optional: fine-tune the model on your own data

See [`backend/fine_tuning/README.md`](../backend/fine_tuning/README.md). Runs in ~10 min on a free Google Colab T4. Set `LORA_ADAPTER_PATH` in `.env` after you have an adapter.

# Setup guide — step-by-step

## Prerequisites

- **Python 3.10 or 3.11** (3.12 mostly works, but `bitsandbytes` is a bit easier on 3.10/3.11)
- **Node.js 18+** (recommended: 20 LTS)
- **Git**
- (Optional, for local fine-tuning) NVIDIA GPU with 8 GB+ VRAM. Otherwise use Colab.

## 1. Clone

```bash
git clone <your-repo-url> ai-travel-assistant
cd ai-travel-assistant
```

## 2. Backend

### 2.1 Create venv and install

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **Windows note**: `bitsandbytes` is gated on Windows. If `pip install bitsandbytes` fails, just remove it — you only need it for **local** QLoRA fine-tuning. Inference and HF Inference API mode work without it.

### 2.2 Configure env

```bash
cp .env.example .env
# edit .env, fill in HF_API_TOKEN at minimum (see docs/API_KEYS.md)
```

For the **fastest first-run demo**, set:
```ini
HF_API_TOKEN=hf_xxx
USE_HF_INFERENCE_API=true
```
This skips downloading model weights entirely.

### 2.3 Run

```bash
uvicorn app.main:app --reload
# open http://localhost:8000/docs
```

You should see Swagger UI listing all endpoints. Try `GET /health` to confirm the LLM is ready.

## 3. Frontend

```bash
cd ../frontend
npm install
cp .env.example .env.local
npm run dev
# open http://localhost:3000
```

Type a message and confirm a response comes back.

## 4. Fine-tune (optional, on Colab)

See [`backend/fine_tuning/README.md`](../backend/fine_tuning/README.md) for the full Colab walkthrough.

Short version:

1. Upload the `backend/` folder to a Colab notebook.
2. Get a HuggingFace token, accept Gemma's license once.
3. Run:
   ```python
   !pip install -q transformers peft trl bitsandbytes accelerate datasets
   from huggingface_hub import login; login("hf_xxx")
   !python fine_tuning/prepare_data.py
   !python fine_tuning/train_qlora.py
   ```
4. Download the output folder `checkpoints/gemma-travel-lora/`.
5. In `backend/.env`, set `LORA_ADAPTER_PATH=./checkpoints/gemma-travel-lora` and `USE_HF_INFERENCE_API=false`.
6. Restart the backend.

## 5. Common issues

| Symptom                                        | Fix                                                       |
| ---------------------------------------------- | --------------------------------------------------------- |
| `Cannot access gated repo for url ...gemma...` | Accept the license at huggingface.co/google/gemma-2-2b-it |
| `bitsandbytes` install fails on Windows        | Remove from requirements; not needed for inference        |
| Model loads but responses are slow             | Set `USE_HF_INFERENCE_API=true` to offload to HF servers  |
| Frontend shows "backend unreachable"           | Check FastAPI is on :8000 and `ALLOWED_ORIGINS` includes  |
|                                                | `http://localhost:3000`                                   |
| `chromadb` install fails on Python 3.13        | Use 3.10 or 3.11                                          |
| Amadeus returns "401 unauthorized"             | Token expires — code refreshes automatically; check key   |

## 6. Demo script (for your defense)

A 5-minute demo flow that hits every requirement:

1. **Open the chat**, click **"Plan a 4-day food tour of Tokyo"**.
   → shows multi-turn LLM with RAG context.
2. **Ask "What's the weather in Reykjavik?"**
   → triggers weather tool, weather card renders.
3. **Open Preferences**, set budget=mid-range, interests=food+history.
4. **Ask "Plan a 5-day trip to Rome"** → personalized itinerary.
5. **Ask "Find flights from FRA to CDG"** → flight list with **Book** buttons.
6. **Click Book** on one flight → confirmation reference appears.
7. **Ask "What restaurants are near Plaza Mayor?"** → places grid.
8. Click **New chat** to show session reset.

Each step demonstrates one of the project requirements: fine-tuned LLM, multi-turn, real-time updates, itinerary, booking, personalization, UI integration.

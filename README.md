# AI Travel Assistant Chatbot

> SRH Applied Artificial Intelligence — Final Year Project 5
>
> A multi-turn travel chatbot powered by a fine-tuned **Gemma 2B** model, with retrieval-augmented generation (RAG) over a curated travel knowledge base, and live integrations for flights, weather, and points of interest.

## Features

- **Fine-tuned LLM** — Gemma 2B fine-tuned with **QLoRA** on a travel-domain instruction dataset (runs on a free Colab T4).
- **Multi-turn conversation** — Conversation memory persisted per session.
- **RAG over travel knowledge** — ChromaDB vector store of destinations, attractions, and travel tips.
- **Real-time data**
  - Flights — Amadeus Self-Service API
  - Weather — OpenWeatherMap
  - Attractions / restaurants — Google Places (or OpenTripMap as a free fallback)
- **Itinerary generator** — Multi-day itineraries with day-by-day breakdown.
- **Simulated booking flow** — End-to-end "book this flight / hotel" UX (no real payment).
- **Personalized recommendations** — Uses stated user preferences (budget, interests, pace).
- **Modern UI** — Next.js 14 + Tailwind + shadcn/ui chat interface with rich cards (flight / weather / itinerary).

## Architecture

```
┌────────────────────┐        ┌──────────────────────────┐
│   Next.js 14 UI    │  HTTP  │   FastAPI Backend        │
│   (chat + widgets) │ ─────► │                          │
└────────────────────┘        │  ┌────────────────────┐  │
                              │  │ LangChain agent    │  │
                              │  │  ├─ Gemma 2B (LoRA)│  │
                              │  │  ├─ ChromaDB (RAG) │  │
                              │  │  └─ Tools          │  │
                              │  └────────────────────┘  │
                              │   ↳ Amadeus / OWM / GMaps│
                              └──────────────────────────┘
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
python -m app.main     # or: uvicorn app.main:app --reload
```

API runs at `http://localhost:8000` — Swagger docs at `/docs`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

UI runs at `http://localhost:3000`.

### 3. Fine-tune the model (optional, on Colab)

Open `backend/fine_tuning/train_qlora.ipynb` (or run `train_qlora.py`) on Google Colab with a T4 GPU. The script saves a LoRA adapter to `backend/checkpoints/gemma-travel-lora/`. The backend automatically loads it if present; otherwise it falls back to the base Gemma 2B (or HuggingFace Inference API if `HF_API_TOKEN` is set).

## Project Structure

```
ai-travel-assistant-chatbot/
├── backend/                       FastAPI + LangChain + HF
│   ├── app/
│   │   ├── main.py                FastAPI entrypoint
│   │   ├── config.py              Settings via pydantic-settings
│   │   ├── models/                Pydantic request/response schemas
│   │   ├── routers/               /chat /flights /weather /places /itinerary
│   │   ├── services/              LLM, RAG, external APIs, memory
│   │   └── prompts/               System prompts
│   ├── fine_tuning/
│   │   ├── train_qlora.py         QLoRA fine-tuning script (Colab/Kaggle)
│   │   └── prepare_data.py        Build instruction dataset
│   └── data/
│       └── travel_knowledge.jsonl Sample RAG corpus
├── frontend/                      Next.js 14 + Tailwind + shadcn/ui
│   ├── app/
│   ├── components/
│   └── lib/
└── docs/
    └── REPORT.md                  Project report skeleton
```

## API Keys

You need free-tier accounts for:

| Service             | Purpose                | Free tier     |
| ------------------- | ---------------------- | ------------- |
| Amadeus Self-Service | Flight search         | 2000 calls/mo |
| OpenWeatherMap      | Weather               | 1000 calls/day|
| Google Places       | Attractions/restaurants| $200 credit/mo|
| HuggingFace         | Model download / Inf. | Free          |

If you skip Amadeus/Google, the backend falls back to deterministic mock data so the demo still works end-to-end.

## Team

This is a 4-member final-year project at SRH. See [docs/REPORT.md](docs/REPORT.md) for the academic report skeleton.

## License

MIT — for academic use.

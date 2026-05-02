# API Keys — what you need and how to get them

You **only need one** key to demo the project end-to-end (HuggingFace, free).
Everything else has a deterministic mock fallback so the UI still works without a key — but for a real demo to your supervisor, get all four.

| #  | Service              | Required? | Cost   | Time to get | Used for                        |
|----|----------------------|-----------|--------|-------------|---------------------------------|
| 1  | HuggingFace          | Yes       | Free   | 2 min       | Download Gemma + Inference API  |
| 2  | OpenWeatherMap       | Recommended| Free  | 5 min       | Live weather                    |
| 3  | Amadeus Self-Service | Recommended| Free  | 5 min       | Live flight search              |
| 4  | Google Places        | Optional  | $200 free credit/mo | 10 min | Real attractions/restaurants |

If you skip 2/3/4, the backend returns realistic mock data so the demo still flows.

---

## 1. HuggingFace (REQUIRED — for the model)

1. Go to **https://huggingface.co/join** and create a free account.
2. Go to **https://huggingface.co/google/gemma-2-2b-it** and click **Acknowledge license** (one-time).
3. Go to **https://huggingface.co/settings/tokens** → **New token** → name it `wanderly`, type **Read** → copy the token (starts with `hf_…`).

Put it in `backend/.env`:
```
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxx
USE_HF_INFERENCE_API=true     # easiest for demo, no GPU needed
BASE_MODEL=google/gemma-2-2b-it
```

> If you have a local GPU, set `USE_HF_INFERENCE_API=false` and the backend will load Gemma directly. The HF token is still used to download the weights the first time.

---

## 2. OpenWeatherMap (RECOMMENDED — live weather)

1. **https://home.openweathermap.org/users/sign_up** — sign up (free).
2. Verify your email.
3. Go to **API keys** tab → copy the default key (or create one).
4. **Wait ~10 minutes** for the key to activate (their backend takes a moment).

```
OPENWEATHERMAP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Free tier: 1,000 calls/day, 60 calls/minute — plenty for a demo.

---

## 3. Amadeus Self-Service (RECOMMENDED — live flights)

1. **https://developers.amadeus.com/register** — create a developer account.
2. After login → **My Self-Service Workspace** → **Create New App**.
3. Name the app (e.g. `wanderly-college-project`).
4. Copy **API Key** and **API Secret**.

```
AMADEUS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
AMADEUS_API_SECRET=xxxxxxxxxxxxxx
```

Free tier: 2,000 calls/month on the **test** environment (which is what our backend hits). Test data is a snapshot — it works for any IATA pair but isn't real-time bookable. That's fine for a college project.

> IATA codes you'll use most for testing: **FRA** Frankfurt, **CDG** Paris CDG, **LHR** London Heathrow, **JFK** New York JFK, **HND** Tokyo Haneda, **DEL** Delhi, **DXB** Dubai.

---

## 4. Google Places (OPTIONAL — real attractions/restaurants)

This one needs a credit card on file even though it's free for the volumes you'll use. **Skip this for the project unless your supervisor specifically asks for live places** — the mock fallback gives realistic samples.

If you want it:

1. **https://console.cloud.google.com/** → create a project.
2. **APIs & Services → Library** → enable **Places API** (legacy, the simple one).
3. **Credentials → Create credentials → API key**.
4. **Restrict the key**: HTTP referrers → add `localhost:3000/*`. Without restriction Google may revoke it.

```
GOOGLE_PLACES_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Free monthly credit: $200 covers ~10,000 calls. You won't come close.

---

## Free alternative to Google Places: OpenTripMap

If you don't want to deal with Google Cloud, OpenTripMap is fully free, no card needed: **https://opentripmap.io/product** → free 5,000 calls/day.

To use it, you'd need to swap `places_service.py` to call OpenTripMap instead. Ask me and I'll add it as a second backend.

---

## Final `backend/.env` for a full demo

```ini
# Model
BASE_MODEL=google/gemma-2-2b-it
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxx
USE_HF_INFERENCE_API=true
LORA_ADAPTER_PATH=                # leave empty until you've fine-tuned

# Live data
OPENWEATHERMAP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AMADEUS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
AMADEUS_API_SECRET=xxxxxxxxxxxxxx
GOOGLE_PLACES_API_KEY=             # optional

# App
APP_HOST=0.0.0.0
APP_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
CHROMA_DIR=./chroma_db
```

## Frontend

Only one var, no key needed:

```ini
# frontend/.env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

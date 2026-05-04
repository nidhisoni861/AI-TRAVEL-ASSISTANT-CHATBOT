"""Dataset preparation for Gemma travel-domain fine-tuning.

Downloads the Bitext travel chatbot dataset from HuggingFace, cleans it,
converts it to instruction-tuning (SFT) format, and saves as JSONL.

Usage (local or Colab):
    pip install datasets pandas huggingface_hub
    python prepare_data.py

Output files (in data/ folder):
    travel_sft_train.jsonl  — training set (~90% of data)
    travel_sft_test.jsonl   — test set  (~10%, max 200 examples)
    travel_sft.jsonl        — full dataset (backward-compat with train_qlora.py)
    travel_dataset_clean.csv — human-readable version for inspection

Dataset:
    bitext/Bitext-travel-llm-chatbot-training-dataset  (HuggingFace Hub)
    ~3 600 Q&A pairs across 27 travel intents.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "data"

# ── Seed examples (kept as a fallback if HF download fails) ────────────────
SEED_EXAMPLES: list[tuple[str, str]] = [
    (
        "Plan a 3-day trip to Lisbon for someone interested in food and history.",
        "Here is a 3-day Lisbon itinerary blending food and history:\n\n**Day 1 — Alfama & old Lisbon.** Morning: walk through Alfama's narrow lanes to the Castelo de São Jorge. Afternoon: ride Tram 28 to the Sé Cathedral. Evening: traditional fado dinner in a tasca.\n\n**Day 2 — Belém.** Morning: Jerónimos Monastery and Pastéis de Belém. Afternoon: Belém Tower and Monument to the Discoveries. Evening: dinner in Cais do Sodré.\n\n**Day 3 — Bairro Alto & food markets.** Morning: Time Out Market for tasting plates. Afternoon: Chiado. Evening: rooftop bar for sunset.",
    ),
    (
        "What is the best time to visit Japan for cherry blossoms?",
        "Cherry blossom season in Japan runs from late March to early April. Tokyo and Kyoto usually peak between March 25 and April 5, while Sapporo peaks in early May. Forecasts are published from January onwards — book accommodation 2–3 months in advance as prices roughly double during peak bloom.",
    ),
    (
        "I have a 7-hour layover in Singapore. What can I do?",
        "Singapore Changi is perfect for layovers:\n1. Free city tour bus (sign up at the FAST counter in T2/T3, need 5h+ until next flight).\n2. Gardens by the Bay — 25 min by MRT. Budget 2h.\n3. Hawker food at Lau Pa Sat — try chili crab or satay.\n4. Stay in the airport — Jewel's Rain Vortex, Butterfly Garden, free movie theatre.\nAt 7 hours, Gardens by the Bay + a hawker centre is very doable.",
    ),
    (
        "What documents do I need for a Schengen visa?",
        "Standard checklist: completed application form, passport valid 3+ months beyond departure, 2 biometric photos, travel insurance (min €30,000 coverage), round-trip flight reservation, accommodation proof, detailed itinerary, 3–6 months bank statements, and a cover letter. Apply at the consulate of the country where you spend the most nights, 3–6 weeks before travel.",
    ),
    (
        "Suggest budget-friendly destinations in Europe for backpackers.",
        "Top picks:\n- Albania (Tirana, Saranda) — hostels €12–18, meals under €8.\n- Romania (Brașov, Sibiu) — Transylvania for history + nature.\n- Bulgaria (Sofia, Plovdiv) — one of Europe's cheapest.\n- Portugal (Porto) — pricier than Balkans but cheaper than France/Spain.\nPro tip: FlixBus often beats budget airlines once you include luggage fees.",
    ),
    (
        "How do I get around Tokyo without speaking Japanese?",
        "Easy — Tokyo is very foreigner-friendly:\n1. Get a Suica or Pasmo card at any station (tap on/off everywhere).\n2. Google Maps is excellent — gives exit numbers and platform info.\n3. Signs and announcements are bilingual on all major lines.\n4. The Yamanote line loops past most tourist hotspots.\n5. Taxis: pricier but convenient late night — show the driver Google Maps.\nAvoid rush hour (7:30–9:30am, 5:30–7pm) on the Yamanote and Chuo lines.",
    ),
    (
        "Plan a romantic 5-day trip to Tuscany.",
        "5 days — Florence + Chianti + Val d'Orcia:\n\nDay 1: Florence. Boutique hotel near Ponte Vecchio. Sunset aperitivo at Piazzale Michelangelo.\nDay 2: Uffizi Gallery, Boboli Gardens, dinner at Il Santo Bevitore.\nDay 3: Drive to Chianti. Wine tasting at Castello di Ama. Stay at an agriturismo.\nDay 4: Val d'Orcia. Stop in Pienza for pecorino, Montepulciano for wine. Sunset at La Foce.\nDay 5: Siena. Piazza del Campo. Drive to Florence airport.\n\nMid-range budget: ~€250/night accommodation, ~€80/person dinner.",
    ),
    (
        "What should a vegan eat in Bangkok?",
        "Bangkok is great for vegans. Say 'jay' (เจ) for strict vegan or 'mai sai nuea sat, mai sai nam pla' (no meat, no fish sauce).\n\nTop spots:\n- May Veggie Home (Asoke)\n- Broccoli Revolution (Sukhumvit 49)\n- Bonita Cafe\n- jay stalls near the Old Town (look for the yellow flag)\n- Or Tor Kor market for vegan curry pastes\n\nDuring the Vegetarian Festival (Sept/Oct, 9 days) entire neighborhoods go jay.",
    ),
    (
        "What are the must-see attractions in Marrakech?",
        "2–3 days in Marrakech:\n- Jemaa el-Fnaa — central square, food stalls + entertainment at sunset.\n- Bahia Palace — stunning 19th-century tilework.\n- Saadian Tombs — exquisite, hidden behind a passageway.\n- Ben Youssef Madrasa — peaceful Islamic college courtyard.\n- Majorelle Garden — Yves Saint Laurent's botanical garden (book ahead).\n- The Souks — get lost in Souk Semmarine and Souk des Teinturiers.\n- A hammam — try Les Bains de Marrakech.\n\nDay trip option: Atlas Mountains (Imlil) or Essaouira on the coast.",
    ),
    (
        "How much does a week in Bali cost?",
        "A week in Bali on a mid-range budget:\n- Accommodation: €30–60/night (private villa with pool in Ubud or Canggu)\n- Food: €15–25/day (warung meals €2–4, restaurants €10–15)\n- Transport: scooter rental €4–6/day, driver ~€35/day\n- Activities: temple entry €1–3, surf lesson €20, cooking class €25–35\n\nTotal estimate: €400–600 for the week excluding flights.\n\nBudget backpacker: ~€200/week. Luxury: €1 200+/week.",
    ),
    (
        "I want to book a flight from Frankfurt to Tokyo next month.",
        "To find the best options I need a few details:\n- Exact dates (depart + return, or one-way?)\n- Number of passengers\n- Cabin class (Economy / Business?)\n- Preference for direct vs. one-stop\n\nDirect FRA→HND is operated by Lufthansa (~12h). Economy round-trip a month out is typically €700–€1 100. Cheaper options go via Istanbul (Turkish Airlines), Helsinki (Finnair), or Doha (Qatar Airways). Shall I search live offers for specific dates?",
    ),
    (
        "What is the weather like in Reykjavik in December?",
        "Reykjavik in December: cold but manageable. Average highs 3 °C, lows −2 °C. Daylight is short — only 4–5 hours (sunrise ~11:20, sunset ~15:30). Expect rain, sleet, snow, and high winds — often all in one day.\n\nPack: thermal base layers, waterproof shell, insulated grip-sole boots, gloves, and a beanie. Bring a swimsuit for geothermal pools (a year-round joy).\n\nDecember is peak Northern Lights season — head outside city light pollution and check vedur.is for forecasts.",
    ),
]


def _to_sft_record(instruction: str, response: str) -> dict:
    return {
        "messages": [
            {"role": "user",      "content": instruction.strip()},
            {"role": "assistant", "content": response.strip()},
        ]
    }


def load_bitext_dataset() -> list[dict]:
    """Download and convert the Bitext travel chatbot dataset from HuggingFace."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  'datasets' package not installed. Run: pip install datasets")
        return []

    try:
        print("  Downloading bitext/Bitext-travel-llm-chatbot-training-dataset...")
        ds = load_dataset("bitext/Bitext-travel-llm-chatbot-training-dataset", split="train")
        print(f"  Downloaded {len(ds)} rows. Columns: {ds.column_names}")
    except Exception as e:
        print(f"  Download failed: {e}")
        return []

    # Detect instruction/response columns
    col_map = {}
    for cand in ["instruction", "question", "input", "prompt", "utterance"]:
        if cand in ds.column_names:
            col_map["instruction"] = cand
            break
    for cand in ["response", "answer", "output", "reply"]:
        if cand in ds.column_names:
            col_map["response"] = cand
            break

    if "instruction" not in col_map or "response" not in col_map:
        print(f"  Could not detect instruction/response columns. Found: {ds.column_names}")
        return []

    records = []
    for row in ds:
        instr = str(row[col_map["instruction"]]).strip()
        resp  = str(row[col_map["response"]]).strip()
        if len(instr) < 5 or len(resp) < 10:
            continue
        if len(resp) > 2000:
            resp = resp[:2000]
        records.append(_to_sft_record(instr, resp))

    print(f"  Cleaned: {len(records)} valid examples from HuggingFace dataset.")
    return records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 55)
    print("  Dataset Preparation — AI Travel Assistant Chatbot")
    print("=" * 55)

    # 1. Load from HuggingFace
    print("\n[1] Loading Bitext travel dataset from HuggingFace...")
    hf_records = load_bitext_dataset()

    # 2. Merge with seed examples
    seed_records = [_to_sft_record(q, a) for q, a in SEED_EXAMPLES]
    all_records  = hf_records + seed_records

    if not all_records:
        print("  ERROR: No records loaded. Check your internet connection.")
        return

    print(f"\n  Total records (HF + seed): {len(all_records)}")

    # 3. Deduplicate
    seen: set[str] = set()
    unique_records: list[dict] = []
    for rec in all_records:
        key = rec["messages"][0]["content"].lower()[:100]
        if key not in seen:
            seen.add(key)
            unique_records.append(rec)

    print(f"  After deduplication: {len(unique_records)} records")

    # 4. Shuffle + split
    random.seed(42)
    random.shuffle(unique_records)

    n_test  = min(200, max(10, int(len(unique_records) * 0.10)))
    n_train = len(unique_records) - n_test

    train_records = unique_records[:n_train]
    test_records  = unique_records[n_train:]

    print(f"\n  Train: {len(train_records)} | Test: {len(test_records)}")

    # 5. Save
    def save_jsonl(records: list, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"  Saved {len(records):>5} records → {path.name}")

    print("\n[2] Saving files...")
    save_jsonl(train_records, OUT_DIR / "travel_sft_train.jsonl")
    save_jsonl(test_records,  OUT_DIR / "travel_sft_test.jsonl")
    # Full dataset for backward compatibility with train_qlora.py
    save_jsonl(unique_records, OUT_DIR / "travel_sft.jsonl")

    print("\n" + "=" * 55)
    print("  DONE. Next steps:")
    print("  1. Run notebooks/02_finetune_gemma.ipynb on Google Colab")
    print("  2. Run notebooks/03_evaluation.ipynb to prove 80%+ score")
    print("=" * 55)


if __name__ == "__main__":
    main()

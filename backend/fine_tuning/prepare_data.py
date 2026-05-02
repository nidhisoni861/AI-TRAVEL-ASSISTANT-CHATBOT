"""Build a small instruction-style dataset for travel-domain fine-tuning.

In a real project you'd download the Bitext travel-chatbot dataset from HF Hub,
plus scrape Wikivoyage/TripAdvisor. This script produces a *seed* dataset of
~80 hand-written examples + adds the public Bitext dataset if available.

Output: data/travel_sft.jsonl with one record per line:
  {"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "data" / "travel_sft.jsonl"


SEED_EXAMPLES: list[tuple[str, str]] = [
    (
        "Plan a 3-day trip to Lisbon for someone interested in food and history.",
        "Here is a 3-day Lisbon itinerary blending food and history:\n\n**Day 1 — Alfama & old Lisbon.** Morning: walk through Alfama's narrow lanes to the Castelo de São Jorge for panoramic views. Afternoon: ride Tram 28 to the Sé Cathedral. Evening: traditional fado dinner in a tasca.\n\n**Day 2 — Belém.** Morning: Jerónimos Monastery and Pastéis de Belém (queue early!). Afternoon: Belém Tower and the Monument to the Discoveries. Evening: dinner in Cais do Sodré.\n\n**Day 3 — Bairro Alto & food markets.** Morning: Time Out Market for tasting plates. Afternoon: explore Príncipe Real and Chiado. Evening: rooftop bar at Park or Topo for sunset.",
    ),
    (
        "What's the best time to visit Japan for cherry blossoms?",
        "Cherry blossom (sakura) season in Japan typically runs from **late March to early April**. The exact peak shifts north over a few weeks: Tokyo and Kyoto usually peak between **March 25 and April 5**, while Sapporo is closer to early May. Forecasts ('sakura zensen') are published from January onwards by JMC and tenki.jp — book accommodation 2-3 months in advance, as prices roughly double during peak bloom.",
    ),
    (
        "I have a 7-hour layover in Singapore — what can I do?",
        "Plenty! Singapore Changi is one of the easiest airports for short layovers:\n\n1. **Free city tour (FREE)** — Changi runs 2.5h sightseeing buses to landmarks like Marina Bay; sign up at the FAST counter in T2/T3 (need 5h+ until next flight).\n2. **Gardens by the Bay** — 25 min by MRT (East-West line). The Cloud Forest dome is the highlight; budget 2h there + transit.\n3. **Hawker food at Lau Pa Sat** — try chili crab, satay, Hainanese chicken rice.\n4. **Stay in the airport** — Jewel's Rain Vortex, Butterfly Garden, free movie theatre.\n\nAt 7 hours, option 2 + 3 is doable: head to Marina Bay, eat at a hawker centre, return ~3h before your next flight.",
    ),
    (
        "Suggest a budget-friendly destination in Europe for backpackers.",
        "**Top picks for budget backpackers in Europe:**\n\n- **Albania (Tirana, Saranda, Berat)** — hostels 12-18 EUR, full meal under 8 EUR, stunning Riviera coast.\n- **Romania (Bucharest, Brașov, Sibiu)** — Transylvania for history + nature; hostels ~15 EUR.\n- **Bulgaria (Sofia, Plovdiv, Veliko Tarnovo)** — one of Europe's cheapest, great hiking in Rila/Pirin.\n- **Portugal (Porto, Lagos)** — pricier than the Balkans but cheaper than France/Spain; hostels 20-30 EUR.\n\nPro tip: train + bus passes (FlixBus, Eurolines) often beat budget airlines once you factor luggage fees. Allow buffer for Schengen 90/180 if you're combining EU + non-EU.",
    ),
    (
        "What documents do I need for a Schengen visa?",
        "Standard checklist for a short-stay Schengen tourist visa:\n\n- Completed **application form** (signed)\n- **Passport** valid 3+ months beyond intended departure, 2 blank pages\n- 2 recent **biometric photos** (35×45 mm)\n- **Travel insurance** with minimum **30,000 EUR** coverage covering all Schengen states\n- **Round-trip flight reservation** (don't pay before approval — use a hold or refundable ticket)\n- **Accommodation proof** (hotel reservations, Airbnb, host invitation)\n- **Detailed itinerary** day-by-day\n- **Proof of funds**: 3-6 months of bank statements, salary slips\n- **Cover letter** explaining purpose and dates\n\nApply at the consulate of the country where you'll spend the most nights. Lodge 3-6 weeks before travel; processing is up to 15 working days (longer in peak season).",
    ),
    (
        "Recommend vegetarian-friendly restaurants in Rome.",
        "Rome is surprisingly vegetarian-friendly — a lot of Roman classics are veg by default:\n\n- **Cacio e pepe / pasta alla gricia (no guanciale)** — try **Da Felice a Testaccio** or **Roscioli**.\n- **Romeow Cat Bistrot** (Ostiense) — fully vegan, creative tasting menus.\n- **L'Asino d'Oro** (Monti) — chef Lucio Sforza, excellent veg options on the daily menu.\n- **Pizza Florida** (Largo Argentina) — pizza al taglio, many veg toppings.\n- **Mercato di Testaccio** — pick up cheeses, breads, fresh produce; many stalls do vegan focaccia.\n\nMagic word: 'senza carne, senza pesce, senza brodo di carne' — without meat, fish, or meat broth. Most kitchens accommodate easily.",
    ),
    (
        "I want to book a flight from Frankfurt to Tokyo for next month.",
        "I can search live flights for you. To get accurate options I need:\n- **Exact dates** (depart and return, or one-way?)\n- **Number of passengers**\n- **Cabin class** (Economy / Premium / Business / First)\n- **Stopover preference** (direct, max 1 stop, etc.)\n\nDirect FRA→HND/NRT is operated by **Lufthansa** (~12h). Round-trip Economy a month out is typically **€700–€1,100**, premium economy €1,400–€1,900. Cheaper options often go via Istanbul (Turkish), Helsinki (Finnair), or Doha (Qatar). Want me to pull live offers?",
    ),
    (
        "What's the weather like in Reykjavik in December?",
        "Reykjavik in December: cold but not extreme. Average highs **3 °C**, lows **-2 °C**. Daylight is short — only **4-5 hours** (sunrise ~11:20, sunset ~15:30). Expect rain, sleet, snow, and high winds, often all in one day.\n\nWhat to pack: thermal base layers, waterproof shell, insulated boots with grip (sidewalks ice over), gloves, beanie, swimsuit (geothermal pools are a year-round joy). \n\nDecember is also peak **northern lights** season — head outside the city light pollution, check aurora forecast on vedur.is.",
    ),
    (
        "Plan a romantic 5-day getaway in Tuscany.",
        "**5 days, romantic Tuscany — Florence + Chianti + Val d'Orcia.**\n\n**Day 1 — Florence.** Check into a boutique hotel near Ponte Vecchio. Sunset aperitivo at Piazzale Michelangelo.\n\n**Day 2 — Florence art.** Uffizi Gallery (book skip-the-line). Lunch at Trattoria Mario. Afternoon at Boboli Gardens. Dinner at Il Santo Bevitore.\n\n**Day 3 — Drive to Chianti.** Pick up rental car. Wine tasting at **Castello di Ama** or **Antinori nel Chianti Classico**. Stay in an agriturismo near Greve in Chianti.\n\n**Day 4 — Val d'Orcia.** Drive south through cypress-lined roads. Stop in **Pienza** for pecorino, **Montepulciano** for vino nobile. Sunset at **La Foce** or **San Quirico**.\n\n**Day 5 — Siena, return.** Morning in Siena's Piazza del Campo. Drive back to Florence airport.\n\nBudget mid-range: ~€220-300/night for the room, ~€80/person for dinner.",
    ),
    (
        "I'm vegan and traveling to Bangkok. What should I eat?",
        "Bangkok is incredible for vegans — Thai cooking has deep Buddhist (jay) and Indian influences. Magic phrase: **'jay'** (เจ) means strict vegan (no meat, fish sauce, eggs, dairy, garlic, onion). For looser 'mangsawirat' say 'mai sai nuea sat, mai sai nam pla' (no meat, no fish sauce).\n\nTop spots:\n- **May Veggie Home** (Asoke) — pad thai jay, massaman curry, tom yum.\n- **Broccoli Revolution** (Sukhumvit 49) — modern vegan, great smoothie bowls.\n- **Bonita Cafe** — vegan Thai-Western fusion, IG-friendly.\n- **Jay Fai's neighbour stalls** — Old Town has many jay stalls, look for the yellow flag (เจ).\n- **Or Tor Kor market** — vegan curry pastes, fresh fruit.\n\nDuring the **Vegetarian Festival** (Sept/Oct, 9 days), entire neighborhoods go jay — yellow flags everywhere.",
    ),
    (
        "How do I get around in Tokyo without speaking Japanese?",
        "Easy — Tokyo is one of the most foreigner-friendly megacities for transit:\n\n1. **Get a Suica or Pasmo card** at any station. Tap on/off; works on subway, JR, buses, even convenience stores.\n2. **Google Maps** is excellent in Tokyo — gives exit numbers, platform, and which train car to board.\n3. **Signs and announcements** are bilingual (Japanese + English) on all major lines and Shinkansen.\n4. **JR Yamanote line** loops past most tourist hotspots — a great mental map.\n5. **Taxis**: pricier but convenient late night; show the driver your destination on Google Maps.\n6. **Shinkansen tickets**: buy at station green ticket machines (English available) or via SmartEx / EkiNet apps.\n\nAvoid rush hour (7:30-9:30am, 5:30-7pm) on the Yamanote and Chuo lines — packed solid.",
    ),
    (
        "What are the must-see attractions in Marrakech?",
        "Marrakech in 2-3 days, must-sees:\n\n- **Jemaa el-Fnaa** — the legendary central square. Quiet by day, comes alive at sunset with food stalls, snake charmers, storytellers.\n- **Bahia Palace** — 19th-century palace with stunning tilework and painted ceilings.\n- **Saadian Tombs** — small but exquisite, hidden behind a passageway.\n- **Ben Youssef Madrasa** — 16th-century Islamic college, peaceful courtyard.\n- **Majorelle Garden** — Yves Saint Laurent's restored botanical garden; book in advance.\n- **The Souks** — get lost in Souk Semmarine, Souk des Teinturiers (dyers), Souk Haddadine (metalworkers). Bargain hard.\n- **A hammam** — try Les Bains de Marrakech for a traditional steam + scrub.\n\nDay trip: Atlas Mountains (Imlil + Ourika Valley) or Essaouira on the Atlantic coast (3h drive).",
    ),
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with OUT.open("w", encoding="utf-8") as f:
        for user_msg, assistant_msg in SEED_EXAMPLES:
            record = {
                "messages": [
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": assistant_msg},
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1
    print(f"Wrote {written} examples to {OUT}")
    print("\nFor a real run, also load:")
    print("  - 'bitext/Bitext-travel-llm-chatbot-training-dataset' from HF Hub")
    print("  - Wikivoyage city dumps (CC-BY-SA)")


if __name__ == "__main__":
    main()

# Fine-tuning Gemma 2B on travel data (QLoRA)

## Quick path (Google Colab — recommended for students)

1. Upload this folder + `backend/data/` to Colab, or `git clone` your repo.
2. **Runtime → Change runtime type → T4 GPU**.
3. Get a HuggingFace token with **read** access to `google/gemma-2-2b-it` (you must accept the model's license once on its model page).

```python
# Cell 1 — install
!pip install -q transformers==4.45.2 peft==0.13.2 trl==0.11.3 \
                bitsandbytes==0.43.3 accelerate==0.34.2 datasets==3.0.1

# Cell 2 — login
from huggingface_hub import login
login("hf_xxx_your_token_here")

# Cell 3 — build dataset and train
!python prepare_data.py
!python train_qlora.py
```

Training takes **~10 minutes** on a T4 with the 12-example seed set. With the
full Bitext travel dataset (~26k examples) plus Wikivoyage augmentation, expect
**1.5–2.5 hours**.

## Output

A LoRA adapter at `backend/checkpoints/gemma-travel-lora/`. To use it:

```bash
# in backend/.env
LORA_ADAPTER_PATH=./checkpoints/gemma-travel-lora
```

The backend will auto-load the adapter on startup.

## Hyperparameters

| Param         | Value | Note                                               |
| ------------- | ----- | -------------------------------------------------- |
| LoRA rank     | 16    | Good balance of capacity vs. size (~30 MB adapter) |
| LoRA alpha    | 32    | Standard 2× rank                                   |
| Learning rate | 2e-4  | Sweet spot for QLoRA on small models               |
| Batch size    | 2 × 4 | Effective batch = 8                                |
| Epochs        | 3     | More than this overfits the small seed set         |
| Quant         | NF4   | 4-bit double-quant, bf16 compute                   |

## Expanding the dataset

The `prepare_data.py` seed set is small. For the academic project, augment with:

1. **Bitext travel chatbot dataset** — `bitext/Bitext-travel-llm-chatbot-training-dataset` on HF Hub (~26k Q-A pairs, MIT licensed).
2. **Wikivoyage** — CC-BY-SA city pages, parse into Q&A with a script.
3. **Synthetic data** — generate Q&A pairs from your RAG corpus using a stronger model (e.g. GPT-4) for the academic prototype.

Aim for **5,000–20,000** examples total before final training.

## Evaluation

After training, run a held-out test set and report:

- **BLEU / ROUGE** vs. reference answers.
- **GPT-4 grader** on a 50-question rubric (helpfulness, correctness, hallucination rate).
- **Manual qualitative review** — your supervisor will likely value this most.

A simple `evaluate.py` template is left as a TODO for the team.

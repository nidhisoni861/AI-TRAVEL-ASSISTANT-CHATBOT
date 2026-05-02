"""QLoRA fine-tuning of Gemma 2B on the travel SFT dataset.

Designed to fit on a free Colab T4 (16 GB VRAM) or Kaggle P100.

Usage (Colab):
    !pip install -q transformers==4.45.2 peft==0.13.2 trl==0.11.3 \\
                    bitsandbytes==0.43.3 accelerate==0.34.2 datasets==3.0.1
    !python prepare_data.py
    !python train_qlora.py

Output: a LoRA adapter folder at `checkpoints/gemma-travel-lora/`.
Point the backend at it via LORA_ADAPTER_PATH in .env.
"""
from __future__ import annotations

import os
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model
from trl import SFTTrainer, SFTConfig


BASE_MODEL = os.getenv("BASE_MODEL", "google/gemma-2-2b-it")
DATA_PATH = Path(__file__).parent.parent / "data" / "travel_sft.jsonl"
OUTPUT_DIR = Path(__file__).parent.parent / "checkpoints" / "gemma-travel-lora"


def format_example(example: dict) -> dict:
    """Apply Gemma's chat template to each conversation."""
    msgs = example["messages"]
    text = ""
    for m in msgs:
        if m["role"] == "user":
            text += f"<start_of_turn>user\n{m['content']}<end_of_turn>\n"
        else:
            text += f"<start_of_turn>model\n{m['content']}<end_of_turn>\n"
    return {"text": text}


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Dataset not found at {DATA_PATH}. Run prepare_data.py first.")

    # 4-bit quantization (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    print(f"Loading {BASE_MODEL} in 4-bit...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        attn_implementation="eager",
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    ds = load_dataset("json", data_files=str(DATA_PATH), split="train")
    ds = ds.map(format_example, remove_columns=ds.column_names)

    sft_config = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=5,
        save_strategy="epoch",
        warmup_ratio=0.05,
        lr_scheduler_type="cosine",
        max_seq_length=1024,
        dataset_text_field="text",
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=ds,
        tokenizer=tokenizer,
    )

    print("Starting training...")
    trainer.train()
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print(f"\nLoRA adapter saved to {OUTPUT_DIR}")
    print(f"Set LORA_ADAPTER_PATH={OUTPUT_DIR} in backend/.env to use it.")


if __name__ == "__main__":
    main()

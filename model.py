import os

import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer

load_dotenv()

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "Qwen/Qwen2.5-1.5B-Instruct"
)

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading model: {MODEL_NAME}")
print(f"Device: {device}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME
)

model.to(device)
model.eval()

print("Model loaded")


def generate_coaching(
    child_name,
    child_age,
    domain
):
    prompt = f"""
Kamu adalah AI pendamping orang tua.

Anak bernama {child_name}, umur {child_age}.
Perangkat anak melakukan DNS request ke domain yang terdeteksi berisiko: {domain}.

Berikan nasihat singkat kepada orang tua.

Aturan:
- Jangan menghakimi anak.
- Jangan mengatakan bahwa anak pasti melihat isi website.
- DNS request hanya menunjukkan bahwa perangkat melakukan request ke domain.
- Gunakan bahasa Indonesia.
- Berikan saran komunikasi yang tenang dan edukatif.
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=120,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

    generated_tokens = outputs[
        0
    ][
        inputs["input_ids"].shape[1]:
    ]

    result = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    return result.strip()
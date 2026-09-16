import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

class QwenModel:
    def __init__(self, model_name="Qwen/Qwen2.5-1.5B-Instruct"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = None
    
    def load(self):
        """Load model once (on startup)"""
        logger.info(f"[MODEL] Loading {self.model_name}...")
        
        # Auto detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"[MODEL] Using device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        logger.info("[MODEL] ✅ Tokenizer loaded")
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        logger.info("[MODEL] ✅ Model loaded")
    
    def generate_coaching(self, child_name: str, child_age: int, domain: str) -> str:
        """
        Generate coaching script untuk orang tua
        
        Input:
        - child_name: "Budi"
        - child_age: 13
        - domain: "xvideos.com"
        
        Output:
        - Coaching text (Indonesian)
        """
        
        # Build system prompt
        system_prompt = f"""Kamu adalah FamilyGuard, ahli pengasuhan digital Indonesia.
Anak {child_name} ({child_age} tahun) ketahuan coba akses situs berbahaya '{domain}'.
Tulis panduan HANGAT & EMPATI untuk orang tua bicara dengan anak, jangan marah. Include:
1. Kenapa anak curious (development stage)
2. Validasi perasaan ortu yang shock
3. Langkah pertama sekarang
4. Skrip bicara siap pakai (contoh exact kalimat)
5. Kapan butuh professional help

Gunakan Bahasa Indonesia natural. JANGAN judgmental. FOKUS pada komunikasi dan understand."""

        user_prompt = f"Generate coaching untuk {child_name} ({child_age}yo) akses {domain}"
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Apply chat template
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Generate
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=600,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Extract new tokens only
        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        # Decode to text
        response = self.tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True
        )[0]
        
        return response.strip()
    
    def classify_domain(self, domain: str) -> dict:
        """
        Fast classification (no AI, hardcoded)
        Return: {category, severity, should_block}
        """
        
        adult_sites = {"pornhub.com", "xvideos.com", "onlyfans.com", "xnxx.com"}
        gambling_sites = {"pokiok.com", "slotgacor.com", "mainbet88.com", "togel.com"}
        
        for site in adult_sites:
            if site in domain:
                return {
                    "category": "adult",
                    "severity": "HIGH",
                    "should_block": True
                }
        
        for site in gambling_sites:
            if site in domain:
                return {
                    "category": "gambling",
                    "severity": "HIGH",
                    "should_block": True
                }
        
        return {
            "category": "safe",
            "severity": "LOW",
            "should_block": False
        }
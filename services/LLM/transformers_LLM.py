# =======================
# Реализация LLM, используя Hugging Face Transformers
# =======================
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from services.LLM.baseLLM import BaseLLM


class LLM_transformers(BaseLLM):
    def __init__(self, model_name : str, 
        cache_dir : str, 
        device : str, 
        full_model_path : str = None, 
        local_load : bool = False, 
        logger = None
        ):

        if logger:
            logger.debug(f"llm init start")

        self.model_name = model_name
        self.cache_dir = cache_dir
        self.full_model_path = full_model_path
        self.device = device
        self.logger = logger
        
        try:
            # === LOAD LOCAL MODEL ===
            if local_load: 
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.full_model_path,
                    torch_dtype=torch.float16
                ).to(self.device)
                self.tokenizer = AutoTokenizer.from_pretrained(self.full_model_path)
            # === LOAD MODEL SINCE HF ===
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name, 
                    cache_dir=self.cache_dir,
                    torch_dtype=torch.float16,
                ).to(self.device)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        except Exception as e:
            if self.logger:
                self.logger.info(f"LLM init exception: {e}")

        if self.logger:
            self.logger.debug("llm init end")


    def generate(self, prompt : str, max_length : int = 1024, max_new_tokens : int = 256) -> str:
        """
        method for generate response LLM

        return - full text, without filter
        """
        # === TOKENIZE ===
        input_text_tokenize = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            add_special_tokens=True
        ).to(self.device) #input_ids, attention_mask

        self.logger.debug(f"INPUT_IDS: shape: {input_text_tokenize['input_ids'].shape}")
        # === GENERATE ===
        output = self.model.generate(
            **input_text_tokenize,
            max_new_tokens=max_new_tokens 
        )

        self.logger.debug(f"OUTPUT: shape: {output.shape}")
        # === TOKENIZE DECODE ===
        text_generate_decode = self.tokenizer.batch_decode(output, skip_special_tokens=True)
        # prompt_size = input_text_tokenize['input_ids'].shape[1]

        return text_generate_decode[0]
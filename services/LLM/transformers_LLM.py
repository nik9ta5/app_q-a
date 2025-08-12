# =======================
# Реализация LLM, используя Hugging Face Transformers
# =======================
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer

from services.LLM.baseLLM import BaseLLM


class LLM_transformers:
    def __init__(self, model_name : str, 
        cache_dir : str, 
        device : str, 
        full_model_path : str = None, 
        local_load : bool = False, 
        use_streamer : bool = False,
        logger = None
        ):

        if logger:
            logger.debug(f"llm init start")

        self.model_name = model_name
        self.cache_dir = cache_dir
        self.full_model_path = full_model_path
        self.device = device
        self.use_streamer = use_streamer
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
                    torch_dtype=torch.float16
                ).to(self.device)
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    cache_dir=self.cache_dir
                )
        except Exception as e:
            if self.logger:
                self.logger.debug(f"LLM init exception: {e}")
            raise
        
        if self.use_streamer:
            self.streamer = TextStreamer(self.tokenizer, skip_prompt=True)

        if self.logger:
            self.logger.debug("llm init end")


    def generate(
        self, 
        prompt : str, 
        max_length : int = 1024, 
        max_new_tokens : int = 256,
        repetition_penalty : int = 1.0,
        no_repeat_ngram_size : int = 2,
        do_sample : bool = False,
        top_k : int = 50,
        top_p : int = 0.8,
        temperature : int = 0.5
        ) -> str:
        """
        method for generate response LLM.
        
        Args:
            prompt (str): prompt for LLM 
            max_length (int): max seq len 
            max_new_tokens (int): new tokens
            repetition_penalty (int): penalty for repeat generate
            no_repeat_ngram_size (int): no generate repeat ngrams
            do_sample (bool): on sample
            top_k (int): Take k more probabylity
            top_p (int) : probability 
            temperature (int): temp
        
        Returns:
            model_response (str): full generate text without filters
        """
        # === TOKENIZE ===
        input_text_tokenize = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            add_special_tokens=True
        ).to(self.device) #input_ids, attention_mask
        
        if self.logger:
            self.logger.debug(f"INPUT_IDS: shape: {input_text_tokenize['input_ids'].shape}")
        # === GENERATE ===
        output = self.model.generate(
            **input_text_tokenize,
            max_new_tokens=max_new_tokens,
            repetition_penalty=repetition_penalty,     #Штраф за повторения
            no_repeat_ngram_size=no_repeat_ngram_size,     #Запрет на повторение ngram=2 (bigrams)
            do_sample=do_sample,             #Семплирование
            top_k=top_k,                   #Выбор из 50 более вероятных слов
            top_p=top_p,
            temperature=temperature,            #Температура
            streamer=self.streamer if self.use_streamer else None, #Использовать streamer
            eos_token_id=self.tokenizer.eos_token_id
        )

        if self.logger:
            self.logger.debug(f"OUTPUT: shape: {output.shape}")
        # === TOKENIZE DECODE ===
        text_generate_decode = self.tokenizer.batch_decode(output, skip_special_tokens=True)
        if self.logger:
            self.logger.debug(f"=== full generate text: ===\n{text_generate_decode[0]}")
            self.logger.debug(f"=== generate text without prompt: ===\n{text_generate_decode[0][len(prompt):]}")
        # prompt_size = input_text_tokenize['input_ids'].shape[1]

        return text_generate_decode[0]
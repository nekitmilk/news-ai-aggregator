import logging
import os
import time
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger("SummarizerManager")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

class SummarizerManager:
    def __init__(self, model_name="IlyaGusev/rut5_base_sum_gazeta", device=0):
        logger.info("🔄 Инициализация SummarizerManager...")
        start = time.time()

        cache_dir = os.environ.get("HF_HOME", "/root/.cache/huggingface")
        logger.info(f"📥 Загружаем токенизатор {model_name} с cache_dir={cache_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)

        logger.info(f"📥 Загружаем модель {model_name} с cache_dir={cache_dir}...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir=cache_dir)

        logger.info(f"⚡ Создаём пайплайн summarization на device={device}...")
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=device
        )

        logger.info(f"✅ SummarizerManager готов (инициализация заняла {time.time() - start:.2f} сек)")

    def summarize(self, text: str, min_length=30, max_length=100):
        if not text.strip():
            logger.warning("⚠️ Попытка суммаризировать пустой текст")
            return "", 0.0

        logger.info("🚀 Запуск суммаризации...")
        start_time = time.time()

        summary = self.summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )

        end_time = time.time()
        logger.info(f"✅ Суммаризация завершена за {end_time - start_time:.2f} секунд")
        return summary[0]["summary_text"], end_time - start_time
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import time

logger = logging.getLogger("SummarizerManager")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

class SummarizerManager:
    def __init__(self, model_name="IlyaGusev/rut5_base_sum_gazeta", device=0):
        logger.info(f"🔄 Инициализация SummarizerManager...")
        start = time.time()

        logger.info(f"📥 Загружаем токенизатор {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        logger.info(f"📥 Загружаем модель {model_name}...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        logger.info(f"⚡ Загружаем пайплайн summarization на device={device}...")
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=device
        )

        logger.info(f"✅ SummarizerManager готов (инициализация заняла {time.time() - start:.2f} сек)")

    def summarize(self, text: str, min_length=30, max_length=100):
        if not text:
            logger.warning("⚠️ Попытка суммаризировать пустой текст")
            return None, 0

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
        return summary[0]['summary_text'], end_time - start_time

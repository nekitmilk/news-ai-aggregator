import logging
import time
import os
from transformers import pipeline

logger = logging.getLogger("CategorizerManager")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

class CategorizerManager:
    def __init__(self, device=0):
        logger.info("🔄 Инициализация CategorizerManager...")
        start = time.time()

        model_name = "cointegrated/rubert-base-cased-nli-threeway"
        cache_dir = os.environ.get("HF_HOME", "/root/.cache/huggingface")

        logger.info(f"⚡ Загружаем Zero-Shot классификатор {model_name} на device={device} с cache_dir={cache_dir}...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_name,
            tokenizer=model_name,
            device=device,
            cache_dir=cache_dir
        )

        self.CATEGORIES = [
            "политика",
            "экономика",
            "общество",
            "технологии",
            "спорт",
            "культура",
            "наука",
            "происшествия",
            "другое"
        ]

        logger.info(f"✅ CategorizerManager готов (инициализация заняла {time.time() - start:.2f} сек)")

    def categorize(self, text: str, top_k=1):
        if not text.strip():
            logger.warning("⚠️ Попытка классифицировать пустой текст")
            return [], 0.0

        logger.info("🚀 Запуск категоризации...")
        start_time = time.time()

        result = self.classifier(
            text,
            candidate_labels=self.CATEGORIES,
            multi_label=False
        )

        categories = [
            {"label": label, "score": score}
            for label, score in zip(result["labels"], result["scores"])
        ]

        end_time = time.time()
        logger.info(f"✅ Категоризация завершена за {end_time - start_time:.2f} секунд")
        return categories[:top_k], end_time - start_time
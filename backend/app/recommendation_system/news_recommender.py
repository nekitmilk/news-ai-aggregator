import re
import uuid
import numpy as np
from math import exp
from datetime import datetime
from typing import List

class Entity:
    def __init__(self, id: int|uuid.UUID, vector: List[float], timestamp: datetime):
        self.id = id
        self.vector = vector
        self.timestamp = timestamp

class NewsRecommender:
    def __init__(self, vector_size=500, freshness_weight=0.3, decay_factor=0.95):
        self.vector_size = vector_size
        self.freshness_weight = freshness_weight
        self.decay_factor = decay_factor

    def get_recommendations(self, entities: List[Entity], summary_entities: List[Entity], n=10):      
        norm_summarize_vector = self.norm_summarize_vector(summary_entities)
        
        if np.linalg.norm(norm_summarize_vector) < 0.1:
            return self._get_fresh_entities(entities, summary_entities, n)
        
        scores = []
        
        for entity in entities:
            if entity.id in [e.id for e in summary_entities]:
                continue
            
            content_similarity = np.dot(norm_summarize_vector, entity.vector)
            
            if entity.id:
                freshness = self.calculate_freshness_score(entity.timestamp)
            else:
                freshness = 0.5
            
            final_score = (1 - self.freshness_weight) * content_similarity + \
                         self.freshness_weight * freshness
            
            scores.append((entity.id, final_score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = [news_id for news_id, _ in scores[:n]]
        
        if len(recommendations) < n:
            additional = self._get_fresh_entities(entities, summary_entities, n)
            additional = [news_id for news_id in additional if news_id not in recommendations]
            recommendations.extend(additional)
        
        return recommendations[:n]

    def norm_summarize_vector(self, entities: List[Entity]) -> List[float]:
        if not len(entities):
            return np.zeros(self.vector_size)
        
        weighted_sum = np.zeros(self.vector_size)
        total_weight = 0
        current_time = datetime.now()
        
        for entity in entities:
            if entity.vector is None:
                continue
                
            days_diff = (current_time - entity.timestamp).total_seconds() / (24 * 3600)
            weight = exp(-self.decay_factor * days_diff)
            
            weighted_sum += weight * entity.vector
            total_weight += weight
        
        if total_weight > 0:
            user_vector = weighted_sum / total_weight
            norm = np.linalg.norm(user_vector)
            if norm > 0:
                user_vector = user_vector / norm
            return user_vector
        else:
            return np.zeros(self.vector_size)

    def create_news_vector(self, news_id: uuid.UUID, title: str, summary: str,
                           category: str, news_timestamp: datetime) -> Entity:
        text = f"{title} {summary}"
        text_vector = self.text_to_vector(text)
        
        category_vector = self.text_to_vector(category)
        
        combined_vector = 0.7 * text_vector + 0.3 * category_vector
        
        norm = np.linalg.norm(combined_vector)
        if norm > 0:
            combined_vector = combined_vector / norm
            
        return Entity(news_id, combined_vector, news_timestamp)

    def calculate_freshness_score(self, timestamp: datetime, max_age_days: int = 30) -> float:
        now = datetime.now()
        age_days = (now - timestamp).total_seconds() / (24 * 3600)
        
        freshness = max(0, 1 - (age_days / max_age_days))
        return freshness

    def text_to_vector(self, text):
        words = self._preprocess_text(text)
        vector = np.zeros(self.vector_size)
        
        for word in words:
            idx = hash(word) % self.vector_size
            vector[idx] += 1
        
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector

    def _preprocess_text(self, text):
        if not text:
            return []
        
        text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', '', text.lower())
        words = text.split()
        words = [word for word in words if len(word) > 2]
        
        return words
    
    def _get_fresh_entities(self, all_entities: List[Entity], exclude_entities: List[Entity], n: int) -> List[uuid.UUID]:
        result = []
        
        for entity in all_entities:
            if entity.id in [e.id for e in exclude_entities]:
                continue
            
            result.append((entity.id, entity.timestamp))
        
        result.sort(key=lambda x: x[1], reverse=True)
        
        return [news_id for news_id, _ in result[:n]]
    
# بخش: فایل‌های زیرساختی
# فایل: ai_utils.py

from sentence_transformers import SentenceTransformer
from studentbot.config import logger
import numpy as np
import json

def load_knowledge_base(file_path: str) -> dict:
    """
    Load the knowledge base from a JSON file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Knowledge base file not found at: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in knowledge base file: {file_path}")
        return {}

def get_sentence_transformer_model(model_name: str = "paraphrase-MiniLM-L6-v2"):
    """
    Load and return a SentenceTransformer model.
    """
    try:
        model = SentenceTransformer(model_name)
        logger.info(f"Successfully loaded SentenceTransformer model: {model_name}")
        return model
    except Exception as e:
        logger.error(f"Error loading SentenceTransformer model: {e}")
        raise

def find_best_match(query: str, knowledge_base: dict, model) -> dict:
    """
    Find the best match for a query in the knowledge base using a SentenceTransformer model.
    """
    try:
        query_embedding = model.encode(query, convert_to_tensor=True)
        best_match = None
        max_similarity = -1

        for item in knowledge_base.get("items", []):
            for question in item.get("questions", []):
                question_embedding = model.encode(question, convert_to_tensor=True)
                similarity = np.dot(query_embedding, question_embedding)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = item

        if max_similarity > 0.5:  # Threshold for a good match
            return best_match
        else:
            return None
    except Exception as e:
        logger.error(f"Error finding best match for query '{query}': {e}")
        return None

import requests
from studentbot.config import HUGGINGFACE_API_KEY, HUGGINGFACE_API_URL

def get_similarity_score(question: str, reference: str) -> float:
    """
    Calculates the similarity score between a question and a reference text
    using the HuggingFace Inference API.
    """
    if not HUGGINGFACE_API_KEY or not HUGGINGFACE_API_URL:
        return 0.0

    try:
        response = requests.post(
            HUGGINGFACE_API_URL,
            headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
            json={"inputs": [question, reference]}
        )
        response.raise_for_status()
        return response.json().get("score", 0.0)
    except requests.exceptions.RequestException as e:
        print(f"Error calling HuggingFace API: {e}")
        return 0.0

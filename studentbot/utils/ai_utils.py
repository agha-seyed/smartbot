import requests
from studentbot.config import HUGGINGFACE_API_KEY, HUGGINGFACE_API_URL, SIMILARITY_THRESHOLD

def get_best_answer(question: str, faqs: list) -> str | None:
    """
    Finds the best answer to a question from a list of FAQs
    using the HuggingFace Inference API.
    """
    if not HUGGINGFACE_API_KEY or not HUGGINGFACE_API_URL:
        return None

    best_score = 0
    best_answer = None

    for faq in faqs:
        try:
            response = requests.post(
                HUGGINGFACE_API_URL,
                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                json={"inputs": [question, faq.question]}
            )
            response.raise_for_status()
            score = response.json().get("score", 0.0)

            if score > best_score:
                best_score = score
                best_answer = faq.answer
        except requests.exceptions.RequestException as e:
            print(f"Error calling HuggingFace API: {e}")
            continue

    if best_score > SIMILARITY_THRESHOLD:
        return best_answer
    else:
        return None

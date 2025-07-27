import requests
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_fetch_content_from_strapi(mock_get):
    """
    A proof-of-concept to demonstrate fetching content from a mocked Strapi API.
    """
    # Mock the Strapi API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": 1,
                "attributes": {
                    "question": "What is the capital of Italy?",
                    "answer": "Rome"
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    # Fetch the content
    response = requests.get("http://localhost:1337/api/faqs")
    data = response.json()

    # Assertions
    assert response.status_code == 200
    assert data["data"][0]["attributes"]["question"] == "What is the capital of Italy?"
    print("Successfully fetched content from mocked Strapi API.")

if __name__ == '__main__':
    test_fetch_content_from_strapi()

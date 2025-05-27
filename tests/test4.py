import requests
import json
import logging
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
INITIATE_CHAT_URL = urljoin(BASE_URL, "/initiate_chat")
CHAT_HISTORY_URL_TEMPLATE = urljoin(BASE_URL, "/chat_history/{}")
CONTINUE_CHAT_URL = urljoin(BASE_URL, "/continue_chat_classify")

def test_api_flow():
    """Test the complete API flow to diagnose issues."""
    try:
        # Step 1: Initiate a chat session
        logger.info("Initiating chat session...")
        response = requests.post(INITIATE_CHAT_URL, timeout=10)
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data.get("session_id")
        logger.info(f"Chat session initiated with ID: {session_id}")

        # Step 2: Send a test message
        logger.info("Sending test message...")
        payload = {
            "query": "I have an issue with my PM Kisan payment",
            "session_id": session_id
        }
        response = requests.post(CONTINUE_CHAT_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Message response: {json.dumps(result, indent=2)}")

        # Step 3: Get chat history
        logger.info(f"Getting chat history for session {session_id}...")
        try:
            history_url = CHAT_HISTORY_URL_TEMPLATE.format(session_id)
            response = requests.get(history_url, timeout=10)
            response.raise_for_status()  # This will raise an exception for 4xx/5xx responses
            history_data = response.json()
            logger.info(f"Chat history: {json.dumps(history_data, indent=2)}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error getting chat history: {e}")
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_api_flow()
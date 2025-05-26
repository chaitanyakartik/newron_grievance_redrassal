import streamlit as st
import requests
import json
import traceback
import time
import os
from urllib.parse import urljoin, urlparse

# --- Configuration Constants ---
API_BASE_URL = "http://34.93.126.124:8000"
# API_BASE_URL="http://127.0.0.1:8000"
CLASSIFY_ENDPOINT = "/continue_chat_classify"
HEALTH_CHECK_ENDPOINT = "/health" # Common endpoint for health checks
INITIATE_CHAT_ENDPOINT = "/initiate_chat" # New endpoint for initiating chat sessions

API_URL = urljoin(API_BASE_URL, CLASSIFY_ENDPOINT)
HEALTH_CHECK_URL = urljoin(API_BASE_URL, HEALTH_CHECK_ENDPOINT)
INITIATE_CHAT_URL = urljoin(API_BASE_URL, INITIATE_CHAT_ENDPOINT)


REQUEST_TIMEOUT = 45  # seconds for API calls
HEALTH_CHECK_TIMEOUT = 5 # seconds for health check
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# --- Page Configuration ---
st.set_page_config(
    page_title="Chat Interface",
    page_icon="💬",
    layout="centered",
)

st.title("💬 Chat Interface")

# --- Session State Initialization ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [] # This will store history in {"role": ..., "content": ...} format
if 'api_operational' not in st.session_state:
    st.session_state.api_operational = None # None: unknown, True: operational, False: error
if 'current_resolved_path' not in st.session_state:
    st.session_state.current_resolved_path = None  # Store the resolved dept path from the API
if 'session_id' not in st.session_state:
    st.session_state.session_id = None  # Store the chat session ID

# --- Sidebar ---
debug_mode = st.sidebar.checkbox("Debug Mode", value=False)


if st.sidebar.button("Force API Health Check"):
    st.session_state.api_operational = None # Reset to trigger re-check
    st.rerun()

# --- API Communication Functions ---
def check_api_health():
    """Checks the health of the API."""
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=HEALTH_CHECK_TIMEOUT)
        if response.status_code == 200:
            try:
                return True, f"API is connected ({HEALTH_CHECK_URL})."
            except json.JSONDecodeError: # Should not happen if health is just status 200
                return True, f"API connected but health endpoint ({HEALTH_CHECK_URL}) returned non-JSON: {response.text[:100]}"
        else:
            return False, f"API health check ({HEALTH_CHECK_URL}) failed. Status: {response.status_code}. Response: {response.text[:100]}"
    except requests.exceptions.Timeout:
        return False, f"API health check ({HEALTH_CHECK_URL}) timed out after {HEALTH_CHECK_TIMEOUT}s."
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to API at {API_BASE_URL}. Server might be down or network issue."
    except requests.exceptions.RequestException as e:
        return False, f"API health check error: {str(e)}"

def initiate_new_chat():
    """Initiates a new chat session with the API and returns the session ID."""
    try:
        response = requests.post(INITIATE_CHAT_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("session_id")
    except Exception as e:
        if debug_mode:
            st.sidebar.error(f"Failed to initiate chat session: {str(e)}")
        return None

def load_chat_session_data(session_id):
    """Loads the chat session data from the JSON file."""
    try:
        file_path = f"chat_sessions/{session_id}.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        if debug_mode:
            st.sidebar.error(f"Failed to load chat session data: {str(e)}")
        return None

def query_api_with_retries(actual_chat_history, user_query, session_id=None): 
    """
    Queries the API with the chat history and user query, including retries.
    'actual_chat_history' should be a list of dicts: [{"role": "user", "content": "..."}, ...]
    """
    payload = {
        "query": user_query,
        "session_id": session_id  # Include session_id in payload if available
    }

    if debug_mode:
        st.sidebar.subheader("API Call Details")
        st.sidebar.write("Target URL:", API_URL)
        st.sidebar.write("Sending payload:", payload)

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)

            if debug_mode:
                st.sidebar.write(f"Attempt {attempt + 1} Status Code:", response.status_code)
                st.sidebar.write(f"Attempt {attempt + 1} Response Headers:", dict(response.headers))
                try:
                    st.sidebar.text(f"Attempt {attempt + 1} Raw Response Body:\n{json.dumps(response.json(), indent=2)}")
                except json.JSONDecodeError:
                    st.sidebar.text(f"Attempt {attempt + 1} Raw Response Body (not JSON):\n{response.text}")

            response.raise_for_status()

            response_data = response.json()
            if debug_mode:
                st.sidebar.success("API call successful!")
                st.sidebar.write("Parsed Response Data:", response_data)
            return response_data

        except requests.exceptions.Timeout:
            error_msg = f"API request timed out after {REQUEST_TIMEOUT}s (Attempt {attempt + 1}/{MAX_RETRIES})."
            st.toast(f"⏳ {error_msg}", icon="⏳")
            if debug_mode: st.sidebar.warning(error_msg)
            if attempt == MAX_RETRIES - 1:
                st.error(f"API Error: Request timed out after {MAX_RETRIES} attempts. The API might be too slow or overloaded.")
                return {"response": "Sorry, the request to the API timed out. Please try again later."}
        except requests.exceptions.ConnectionError:
            error_msg = f"Failed to connect to the API at {API_URL} (Attempt {attempt + 1}/{MAX_RETRIES}). Server might be down or unreachable."
            st.toast(f"🔌 {error_msg}", icon="🔌")
            if debug_mode: st.sidebar.error(error_msg)
            if attempt == MAX_RETRIES - 1:
                st.error(f"API Error: Could not connect to the API after {MAX_RETRIES} attempts. Please check if the API server is running and accessible.")
                st.session_state.api_operational = False
                return {"response": "Sorry, there was a persistent error connecting to the API. Please notify an administrator."}
        except requests.exceptions.HTTPError as e:
            error_msg = f"API returned an error: {response.status_code} {response.reason} (Attempt {attempt + 1}/{MAX_RETRIES}). Response: {response.text[:200]}"
            st.toast(f"⚠️ {error_msg}", icon="⚠️")
            if debug_mode: st.sidebar.error(error_msg)
            if attempt == MAX_RETRIES - 1:
                st.error(f"API Error: Received HTTP {response.status_code} error. {response.text[:200]}")
                return {"response": f"Sorry, the API returned an error ({response.status_code}). Please try again or check the API status."}
        except json.JSONDecodeError:
            error_msg = f"Error decoding API response (Attempt {attempt + 1}/{MAX_RETRIES}). Expected JSON, got: {response.text[:200]}"
            st.toast(f"📄 {error_msg}", icon="📄")
            if debug_mode:
                st.sidebar.error(error_msg)
                st.sidebar.text(f"Full non-JSON response from API: {response.text}")
            if attempt == MAX_RETRIES - 1:
                st.error("API Error: The API returned an invalid response format.")
                return {"response": "The API returned an invalid response format. Please check the API endpoint."}
        except requests.exceptions.RequestException as e:
            error_msg = f"An unexpected API error occurred: {str(e)} (Attempt {attempt + 1}/{MAX_RETRIES})."
            st.toast(f"💥 {error_msg}", icon="💥")
            if debug_mode:
                st.sidebar.error(error_msg)
                st.sidebar.error(f"Full error details: {traceback.format_exc()}")
            if attempt == MAX_RETRIES - 1:
                st.error(f"API Error: An unexpected error occurred: {str(e)}")
                return {"response": "Sorry, an unexpected error occurred while communicating with the API."}

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
            if debug_mode:
                st.sidebar.info(f"Retrying in {RETRY_DELAY}s...")
        else:
            st.error("API Error: Failed after all retries.")
            return {"response": "Sorry, the API is not responding after multiple attempts."}
    return {"response": "Critical error in API call logic."}

# --- UI Rendering ---

if st.session_state.api_operational is None:
    with st.sidebar:
        with st.spinner(f"Checking API connection to {API_BASE_URL}..."):
            is_healthy, message = check_api_health()
            st.session_state.api_operational = is_healthy
            if is_healthy:
                st.success(message)
            else:
                st.error(message)
                st.info(f"The main chat functionality might be affected. Will attempt to connect to: {API_URL} for chat.")
elif st.session_state.api_operational:
    st.sidebar.success(f"API is reported as operational ({HEALTH_CHECK_URL}).")
else:
    st.sidebar.error(f"API was previously reported as not operational. Check health or connection to {API_BASE_URL}.")

# Initialize chat session if not already done
if not st.session_state.session_id and st.session_state.api_operational:
    with st.spinner("Initiating new chat session..."):
        session_id = initiate_new_chat()
        if session_id:
            st.session_state.session_id = session_id
            if debug_mode:
                st.sidebar.success(f"New chat session initiated: {session_id}")
        else:
            st.error("Failed to initiate a new chat session. Please refresh the page.")

# Load and display current path from session file
if st.session_state.session_id:
    session_data = load_chat_session_data(st.session_state.session_id)
    if session_data and "current_path" in session_data:
        st.session_state.current_resolved_path = session_data["current_path"]
        if debug_mode:
            st.sidebar.info(f"Loaded department path from session file: {session_data['current_path']}")

# Display the current department path
if st.session_state.current_resolved_path:
    st.markdown("#### Current Department Path")
    path_container = st.container(height=None, border=True)
    with path_container:
        # Format the path as a breadcrumb navigation
        if isinstance(st.session_state.current_resolved_path, list) and len(st.session_state.current_resolved_path) > 0:
            path_html = " → ".join([f"<span style='color:#4E89AE'>{dept}</span>" for dept in st.session_state.current_resolved_path])
            st.markdown(f"<p style='margin-bottom: 0px; padding: 5px;'>{path_html}</p>", unsafe_allow_html=True)
        else:
            st.info("No classification path available yet")

st.subheader("Conversation")
chat_container = st.container(height=400)
with chat_container:
    if not st.session_state.chat_history:
        st.info("No messages yet. Type your message below to start the conversation!")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message['content'])

user_input = st.chat_input("Type your message:")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with chat_container:
         with st.chat_message("user"):
            st.markdown(user_input)

    with st.spinner("Assistant is thinking..."):
        if not st.session_state.api_operational and st.session_state.api_operational is not None:
            st.warning("API is not operational. Attempting to send message anyway...")

        # The API expects the *full* history up to the message *before* the current user_input.
        # So, if st.session_state.chat_history includes the current user_input,
        # we need to send all messages *except* the last one.
        # The last one is the current user_input, which is passed as "query".
        if len(st.session_state.chat_history) > 1:
            api_call_history_for_payload = st.session_state.chat_history[:-1]
        else: # If it's the first message from the user, history is empty
            api_call_history_for_payload = []


        api_response = query_api_with_retries(
            actual_chat_history=api_call_history_for_payload,
            user_query=user_input,
            session_id=st.session_state.session_id  # Include session ID in API calls
        )

        # Extract and store the resolved department path if available in the response
        if "path" in api_response:
            st.session_state.current_resolved_path = api_response["path"]
        elif "dept_path" in api_response:
            st.session_state.current_resolved_path = api_response["dept_path"]
        
        # After getting the API response, check if the session file has been updated
        if st.session_state.session_id:
            session_data = load_chat_session_data(st.session_state.session_id)
            if session_data and "current_path" in session_data:
                st.session_state.current_resolved_path = session_data["current_path"]
        
        assistant_response = api_response.get("result", "Sorry, I couldn't get a response from the assistant at this time.")
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        st.rerun()

if st.sidebar.button("Clear Conversation", type="secondary"):
    st.session_state.chat_history = []
    # Keep the session ID but refresh path from file
    if st.session_state.session_id:
        session_data = load_chat_session_data(st.session_state.session_id)
        if session_data and "current_path" in session_data:
            st.session_state.current_resolved_path = session_data["current_path"]
        else:
            st.session_state.current_resolved_path = None
    else:
        st.session_state.current_resolved_path = None
    st.toast("Conversation cleared!", icon="🗑️")
    st.rerun()

if st.sidebar.button("New Session", type="primary"):
    st.session_state.chat_history = []
    st.session_state.current_resolved_path = None
    st.session_state.session_id = None  # Reset session ID to trigger new session creation
    st.toast("Starting new session...", icon="🔄")
    st.rerun()

# Display session ID in sidebar if available
if st.session_state.session_id and debug_mode:
    st.sidebar.text(f"Session ID: {st.session_state.session_id}")
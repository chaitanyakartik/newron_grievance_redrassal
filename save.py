import streamlit as st
import requests
import json
import traceback
import time
import os
from urllib.parse import urljoin, urlparse

# -------------------- CONFIGURATION --------------------
class Config:
    # API endpoints
    API_BASE_URL = "http://127.0.0.1:8000"  # Uncomment for production: "http://34.93.126.124:8000"
    CLASSIFY_ENDPOINT = "/continue_chat_classify"
    HEALTH_CHECK_ENDPOINT = "/health"
    INITIATE_CHAT_ENDPOINT = "/initiate_chat"
    GET_CHAT_HISTORY_ENDPOINT = "/chat_history"
    
    # Full URLs
    API_URL = urljoin(API_BASE_URL, CLASSIFY_ENDPOINT)
    HEALTH_CHECK_URL = urljoin(API_BASE_URL, HEALTH_CHECK_ENDPOINT)
    INITIATE_CHAT_URL = urljoin(API_BASE_URL, INITIATE_CHAT_ENDPOINT)
    
    # Request parameters
    REQUEST_TIMEOUT = 45  # seconds for API calls
    HEALTH_CHECK_TIMEOUT = 5  # seconds for health check
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

# -------------------- STATE MANAGEMENT --------------------
def initialize_session_state():
    """Initialize all session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []  # Format: [{"role": ..., "content": ...}]
    if 'api_operational' not in st.session_state:
        st.session_state.api_operational = None  # None: unknown, True: operational, False: error
    if 'current_resolved_path' not in st.session_state:
        st.session_state.current_resolved_path = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None

# -------------------- API COMMUNICATION --------------------
class ApiService:
    @staticmethod
    def check_api_health():
        """Checks the health of the API."""
        try:
            response = requests.get(Config.HEALTH_CHECK_URL, timeout=Config.HEALTH_CHECK_TIMEOUT)
            if response.status_code == 200:
                try:
                    return True, f"API is connected ({Config.HEALTH_CHECK_URL})."
                except json.JSONDecodeError:
                    return True, f"API connected but health endpoint returned non-JSON: {response.text[:100]}"
            else:
                return False, f"API health check failed. Status: {response.status_code}. Response: {response.text[:100]}"
        except requests.exceptions.Timeout:
            return False, f"API health check timed out after {Config.HEALTH_CHECK_TIMEOUT}s."
        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to API at {Config.API_BASE_URL}. Server might be down or network issue."
        except requests.exceptions.RequestException as e:
            return False, f"API health check error: {str(e)}"
    
    @staticmethod
    def initiate_new_chat():
        """Initiates a new chat session with the API and returns the session ID."""
        try:
            response = requests.post(Config.INITIATE_CHAT_URL, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            response_data = response.json()
            return response_data.get("session_id")
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.sidebar.error(f"Failed to initiate chat session: {str(e)}")
            return None
    
    @staticmethod
    def load_chat_session_data(session_id):
        """Loads the chat session data from the JSON file."""
        try:
            file_path = f"chat_sessions/{session_id}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.sidebar.error(f"Failed to load chat session data: {str(e)}")
            return None
    
    @staticmethod
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
                response_data = response.json()

                if "sesh_id" in response_data:
                    # This means the previous grievance has been resolved and a new session started
                    if debug_mode:
                        st.sidebar.success(f"Received new session ID: {response_data['sesh_id']}")
                    
                    # Update the session ID
                    st.session_state.session_id = response_data["sesh_id"]
                    
                    # Add a message to inform the user
                    notice_msg = "Previous grievance has been resolved. Starting a new session."
                    if "result" in response_data:
                        # If there's already a result message, append to it
                        response_data["result"] = f"{response_data['result']}\n\n{notice_msg}"
                    else:
                        response_data["result"] = notice_msg
                    
                    # Reset the current resolved path
                    st.session_state.current_resolved_path = None

                    payload = { 
                        "query": response_data["result"],  # Use the result message as the new query
                        "session_id": st.session_state.session_id  # Use the new session ID
                    }
                    response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
                    response_data = response.json()
                    return response_data
                    # st.rerun()

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

# -------------------- UI COMPONENTS --------------------
def render_sidebar():
    """Render the sidebar with controls and debug info"""
    st.sidebar.title("Controls")
    
    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=False)
    st.session_state.debug_mode = debug_mode
    
    # API health check button
    if st.sidebar.button("Force API Health Check"):
        st.session_state.api_operational = None  # Reset to trigger re-check
        st.rerun()
    
    # Clear conversation button
    if st.sidebar.button("Clear Conversation", type="secondary"):
        st.session_state.chat_history = []
        # Keep the session ID but refresh path from file
        refresh_path_from_session_file()
        st.toast("Conversation cleared!", icon="🗑️")
        st.rerun()
    
    # New session button
    if st.sidebar.button("New Session", type="primary"):
        st.session_state.chat_history = []
        st.session_state.current_resolved_path = None
        st.session_state.session_id = None  # Reset session ID to trigger new session creation
        st.toast("Starting new session...", icon="🔄")
        st.rerun()
    
    # Display session ID if in debug mode
    if st.session_state.session_id and debug_mode:
        st.sidebar.text(f"Session ID: {st.session_state.session_id}")
    
    # Display API status
    if st.session_state.api_operational is True:
        st.sidebar.success(f"API is operational ({Config.HEALTH_CHECK_URL}).")
    elif st.session_state.api_operational is False:
        st.sidebar.error(f"API was reported as not operational.")

def render_department_path():
    """Render the current department path if available"""
    if st.session_state.current_resolved_path:
        st.markdown("#### Current Department Path")
        path_container = st.container(height=None, border=True)
        with path_container:
            if isinstance(st.session_state.current_resolved_path, list) and len(st.session_state.current_resolved_path) > 0:
                path_html = " → ".join([f"<span style='color:#4E89AE'>{dept}</span>" for dept in st.session_state.current_resolved_path])
                st.markdown(f"<p style='margin-bottom: 0px; padding: 5px;'>{path_html}</p>", unsafe_allow_html=True)
            else:
                st.info("No classification path available yet")

def render_chat_interface():
    """Render the chat interface with history and input"""
    st.subheader("Conversation")
    chat_container = st.container(height=400)
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("No messages yet. Type your message below to start the conversation!")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message['content'])
    
    return st.chat_input("Type your message:")

def handle_user_input(user_input):
    """Process user input - either commands or regular messages"""
    if not user_input:
        return
        
    if user_input.startswith('/'):
        handle_command(user_input)
    else:
        handle_regular_message(user_input)

def handle_command(user_input):
    """Handle special commands that start with /"""
    command = user_input.split()[0][1:]  # Extract command without the '/'
    params = user_input.split()[1:] if len(user_input.split()) > 1 else []
    
    if command == "clear":
        st.session_state.chat_history = []
        st.rerun()
    elif command == "help":
        help_text = """
        **Available Commands:**
        - `/clear`: Clear conversation history
        - `/help`: Show this help message
        - `/get_resolved_depts`: Get the resolved department path
        - `/new_chat_sesh`: Start a new chat session
        """
        st.session_state.chat_history.append({"role": "assistant", "content": help_text})
        st.rerun()
    elif command == "get_resolved_depts":
        # Implement get_resolved_depts command
        pass  # Simplified for brevity
    elif command == "new_chat_sesh":
        st.session_state.chat_history = []
        st.session_state.current_resolved_path = None
        st.session_state.session_id = None
        st.rerun()
    else:
        st.session_state.chat_history.append({"role": "assistant", "content": f"Unknown command: `/{command}`. Type `/help` to see available commands."})
        st.rerun()

def handle_regular_message(user_input):
    """Process a regular user message (not a command)"""
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.spinner("Assistant is thinking..."):
        if not st.session_state.api_operational and st.session_state.api_operational is not None:
            st.warning("API is not operational. Attempting to send message anyway...")

        # Prepare history for API call
        api_call_history_for_payload = st.session_state.chat_history[:-1] if len(st.session_state.chat_history) > 1 else []
        
        # Call API
        api_response = ApiService.query_api_with_retries(
            actual_chat_history=api_call_history_for_payload,
            user_query=user_input,
            session_id=st.session_state.session_id
        )

        # Process response
        if "path" in api_response:
            st.session_state.current_resolved_path = api_response["path"]
        elif "dept_path" in api_response:
            st.session_state.current_resolved_path = api_response["dept_path"]
        
        # Update from session file if needed
        refresh_path_from_session_file()
        
        # Add assistant response to chat
        assistant_response = api_response.get("result", "Sorry, I couldn't get a response from the assistant.")
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        
    st.rerun()

def refresh_path_from_session_file():
    """Update path information from the session file if available"""
    if st.session_state.session_id:
        session_data = ApiService.load_chat_session_data(st.session_state.session_id)
        if session_data and "current_path" in session_data:
            st.session_state.current_resolved_path = session_data["current_path"]
        elif not st.session_state.current_resolved_path:
            st.session_state.current_resolved_path = None

def check_and_initialize_session():
    """Check API health and initialize a new session if needed"""
    # Check API health if not already checked
    if st.session_state.api_operational is None:
        with st.sidebar:
            with st.spinner(f"Checking API connection to {Config.API_BASE_URL}..."):
                is_healthy, message = ApiService.check_api_health()
                st.session_state.api_operational = is_healthy
                if is_healthy:
                    st.success(message)
                else:
                    st.error(message)
                    st.info(f"The main chat functionality might be affected.")

    # Initialize a new session if needed
    if not st.session_state.session_id and st.session_state.api_operational:
        with st.spinner("Initiating new chat session..."):
            session_id = ApiService.initiate_new_chat()
            if session_id:
                st.session_state.session_id = session_id
                if st.session_state.get('debug_mode', False):
                    st.sidebar.success(f"New chat session initiated: {session_id}")
            else:
                st.error("Failed to initiate a new chat session. Please refresh the page.")

# -------------------- MAIN APP --------------------
def main():
    """Main application function"""
    st.title("💬 Chat Interface")
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Check API health and initialize session
    check_and_initialize_session()
    
    # Update path from session file if available
    refresh_path_from_session_file()
    
    # Render department path
    render_department_path()
    
    # Render chat interface and get user input
    user_input = render_chat_interface()
    
    # Handle user input if provided
    if user_input:
        handle_user_input(user_input)

if __name__ == "__main__":
    main()
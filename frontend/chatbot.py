import json
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Buyzaar Support Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

if "customer_name" not in st.session_state:
    st.session_state.customer_name = None

if "customer_email" not in st.session_state:
    st.session_state.customer_email = None

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "selected_conversation_id" not in st.session_state:
    st.session_state.selected_conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "auth_error" not in st.session_state:
    st.session_state.auth_error = None

if "auth_success" not in st.session_state:
    st.session_state.auth_success = None

if "chat_error" not in st.session_state:
    st.session_state.chat_error = None


# ============================================================
# UTILITY AND PARSING HELPERS
# ============================================================

def extract_error_message(response: requests.Response, default_msg: str = "Request failed.") -> str:
    """
    Safely extract readable error messages from FastAPI HTTP responses,
    handling string details, 422 validation lists, and JSON dictionaries.
    """
    try:
        data = response.json()
        detail = data.get("detail") or data.get("message") or data.get("error")
        if isinstance(detail, list):
            msgs = []
            for item in detail:
                if isinstance(item, dict):
                    loc_parts = [str(l) for l in item.get("loc", []) if l != "body"]
                    loc = " -> ".join(loc_parts)
                    msg = item.get("msg", str(item))
                    msgs.append(f"{loc}: {msg}" if loc else msg)
                else:
                    msgs.append(str(item))
            return "; ".join(msgs) if msgs else default_msg
        elif isinstance(detail, dict):
            return str(detail)
        elif detail:
            return str(detail)
    except Exception:
        pass

    if response.text and len(response.text) < 300:
        return response.text.strip()
    return f"{default_msg} (HTTP {response.status_code})"


def parse_messages(raw_messages) -> list[dict]:
    """
    Parse messages safely whether they are a JSON string, list of dicts, or None.
    """
    if raw_messages is None:
        return []

    if isinstance(raw_messages, str):
        try:
            parsed = json.loads(raw_messages)
            if isinstance(parsed, list):
                return [m for m in parsed if isinstance(m, dict)]
            return []
        except Exception:
            return []

    if isinstance(raw_messages, list):
        return [m for m in raw_messages if isinstance(m, dict)]

    return []


def normalize_role(role: str) -> str:
    """
    Normalize backend role strings into Streamlit chat_message roles ('user' or 'assistant').
    """
    role_lower = str(role or "").lower().strip()
    if role_lower in ("user", "human", "customer"):
        return "user"
    return "assistant"


def check_backend_connection() -> tuple[bool, str]:
    """
    Check if the FastAPI backend server is reachable.
    """
    try:
        # Check docs or root endpoint with short timeout
        response = requests.get(f"{BACKEND_URL}/docs", timeout=3)
        if response.status_code in (200, 404):
            return True, "Connected"
        return True, f"HTTP {response.status_code}"
    except requests.RequestException as e:
        return False, str(e)


# ============================================================
# AUTHENTICATION FUNCTIONS
# ============================================================

def get_auth_headers() -> dict:
    """
    Generate standard HTTP authorization headers with Bearer JWT access token.
    """
    headers = {"Content-Type": "application/json"}
    if st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    return headers


def logout_user():
    """
    Clear all authentication credentials and reset session state cleanly.
    """
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.customer_id = None
    st.session_state.customer_name = None
    st.session_state.customer_email = None
    st.session_state.is_authenticated = False
    st.session_state.conversations = []
    st.session_state.selected_conversation_id = None
    st.session_state.messages = []
    st.session_state.chat_error = None


def refresh_access_token() -> bool:
    """
    Exchange the refresh token for a new access token via /auth/refresh.
    """
    if not st.session_state.refresh_token:
        logout_user()
        return False

    url = f"{BACKEND_URL}/auth/refresh"
    payload = {"refresh_token": st.session_state.refresh_token}

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            new_access_token = data.get("access_token")
            if new_access_token:
                st.session_state.access_token = new_access_token
                return True

        logout_user()
        st.session_state.auth_error = "Your session expired. Please log in again."
        return False
    except Exception:
        logout_user()
        st.session_state.auth_error = "Could not refresh session. Please log in again."
        return False


def authenticated_request(method: str, url: str, **kwargs) -> requests.Response:
    """
    Wrapper around requests that automatically injects the Bearer JWT token,
    and performs automatic token refreshing on 401 Unauthorized responses.
    """
    headers = kwargs.pop("headers", {})
    headers.update(get_auth_headers())

    response = requests.request(method, url, headers=headers, **kwargs)

    # If access token has expired (401), attempt to refresh and retry once
    if response.status_code == 401:
        if st.session_state.refresh_token and refresh_access_token():
            # Update headers with new access token and retry request
            headers.update(get_auth_headers())
            response = requests.request(method, url, headers=headers, **kwargs)
        else:
            logout_user()
            st.session_state.auth_error = "Session expired or invalid. Please log in again."
            st.rerun()

    return response


def login_user(email: str, password: str) -> bool:
    """
    Authenticate customer against the backend JWT login endpoint (/auth/login).
    """
    url = f"{BACKEND_URL}/auth/login"
    payload = {
        "email": email.strip().lower(),
        "password": password,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)

        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data.get("access_token")
            st.session_state.refresh_token = data.get("refresh_token")

            customer_info = data.get("customer", {})
            st.session_state.customer_id = customer_info.get("customer_id")
            st.session_state.customer_name = customer_info.get("name")
            st.session_state.customer_email = customer_info.get("email") or email.strip().lower()

            st.session_state.is_authenticated = True
            st.session_state.auth_error = None
            st.session_state.auth_success = "Login successful!"

            # Load initial conversations
            try:
                st.session_state.conversations = get_conversations()
            except Exception:
                st.session_state.conversations = []

            st.session_state.selected_conversation_id = None
            st.session_state.messages = []
            return True

        elif response.status_code == 401:
            st.session_state.auth_error = "Invalid email or password."
            return False
        elif response.status_code == 404:
            st.session_state.auth_error = f"Account with email '{email.strip()}' not found."
            return False
        else:
            error_msg = extract_error_message(response, "Login failed.")
            st.session_state.auth_error = f"Login failed: {error_msg}"
            return False

    except requests.RequestException as e:
        st.session_state.auth_error = f"Cannot connect to backend server ({BACKEND_URL}): {e}"
        return False


def register_user(name: str, email: str, password: str) -> bool:
    """
    Register a new customer account via backend endpoint (/auth/register).
    """
    url = f"{BACKEND_URL}/auth/register"
    payload = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "password": password,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)

        if response.status_code in (200, 201):
            st.session_state.auth_error = None
            st.session_state.auth_success = "Account created successfully! Logging you in..."
            return True
        elif response.status_code == 409:
            st.session_state.auth_error = "An account with this email already exists."
            return False
        elif response.status_code == 422:
            detail = extract_error_message(response, "Validation error.")
            st.session_state.auth_error = f"Invalid input: {detail}"
            return False
        else:
            detail = extract_error_message(response, "Registration failed.")
            st.session_state.auth_error = f"Registration failed: {detail}"
            return False

    except requests.RequestException as e:
        st.session_state.auth_error = f"Cannot connect to backend server ({BACKEND_URL}): {e}"
        return False


# ============================================================
# API DATA FUNCTIONS
# ============================================================

def get_conversations() -> list[dict]:
    """
    Fetch all conversations for the authenticated customer from backend.
    """
    if not st.session_state.customer_id:
        return []

    url = f"{BACKEND_URL}/customer/{st.session_state.customer_id}/conversations"
    response = authenticated_request("GET", url, timeout=30)
    response.raise_for_status()

    data = response.json()
    conversations = data.get("conversations", [])

    # Sort conversations by updated_at or created_at descending
    conversations.sort(
        key=lambda conv: (conv.get("updated_at") or conv.get("created_at") or ""),
        reverse=True,
    )

    return conversations


def call_agent(message: str, conversation_id: str | None = None) -> dict:
    """
    Send a message to the AI support agent (/agent/call) with Bearer JWT auth.
    conversation_id=None creates a new conversation on the backend.
    """
    url = f"{BACKEND_URL}/agent/call"

    payload = {
        "message": message.strip(),
        "conversation_id": conversation_id if conversation_id else None,
        "customer_id": st.session_state.customer_id if st.session_state.customer_id else None,
    }

    response = authenticated_request(
        "POST",
        url,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()
    return response.json()


def refresh_conversations():
    """
    Refresh the conversation list from the backend and update session state.
    """
    try:
        st.session_state.conversations = get_conversations()
    except Exception as e:
        st.session_state.chat_error = f"Could not refresh conversations: {e}"


def load_conversation(conversation_id: str) -> bool:
    """
    Load a selected conversation into active chat messages.
    """
    for conversation in st.session_state.conversations:
        if conversation.get("conversation_id") == conversation_id:
            st.session_state.selected_conversation_id = conversation_id
            st.session_state.messages = parse_messages(conversation.get("messages"))
            st.session_state.chat_error = None
            return True
    return False


# ============================================================
# AUTHENTICATION SCREEN (WHEN NOT LOGGED IN)
# ============================================================

if not st.session_state.is_authenticated:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center;'>🤖 Buyzaar Support</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Production-Ready E-Commerce AI Support Assistant</p>", unsafe_allow_html=True)
        st.write("")

        # Check backend connectivity status
        is_online, conn_status = check_backend_connection()
        if not is_online:
            st.warning(
                f"⚠️ **Backend Offline**: Unable to connect to `{BACKEND_URL}`.\n\n"
                "Please make sure the FastAPI server is running (`uvicorn app.main:app --port 8000 --reload`)."
            )

        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)

        if st.session_state.auth_success:
            st.success(st.session_state.auth_success)

        auth_tab_login, auth_tab_register = st.tabs(["🔐 Login", "📝 Register"])

        # ----------------------------------------------------
        # LOGIN TAB
        # ----------------------------------------------------
        with auth_tab_login:
            st.subheader("Login to your account")
            with st.form("login_form"):
                email_input = st.text_input("Email", placeholder="user@example.com")
                password_input = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Log In", use_container_width=True)

                if submitted:
                    if not email_input.strip() or not password_input:
                        st.warning("Please fill in both email and password.")
                    else:
                        with st.spinner("Authenticating..."):
                            if login_user(email_input, password_input):
                                st.rerun()

        # ----------------------------------------------------
        # REGISTER TAB
        # ----------------------------------------------------
        with auth_tab_register:
            st.subheader("Create a new account")
            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Alice Doe")
                reg_email = st.text_input("Email", placeholder="e.g. alice@example.com")
                reg_password = st.text_input("Password (min 8 characters)", type="password", placeholder="Choose a secure password")
                reg_submitted = st.form_submit_button("Create Account", use_container_width=True)

                if reg_submitted:
                    if not reg_name.strip() or not reg_email.strip() or not reg_password:
                        st.warning("Please fill in all fields.")
                    elif len(reg_password) < 8:
                        st.warning("Password must be at least 8 characters long.")
                    else:
                        with st.spinner("Creating account..."):
                            if register_user(reg_name, reg_email, reg_password):
                                # Auto-login after successful registration
                                if login_user(reg_email, reg_password):
                                    st.rerun()

    # Halt execution of main chat UI until authenticated
    st.stop()


# ============================================================
# SIDEBAR (WHEN AUTHENTICATED)
# ============================================================

with st.sidebar:
    st.title("💬 Buyzaar Support")

    # Display Authenticated User Profile Badge
    customer_display_name = st.session_state.customer_name or "Customer"
    customer_display_email = st.session_state.customer_email or ""

    st.markdown(f"**👤 {customer_display_name}**")
    if customer_display_email:
        st.caption(f"✉️ {customer_display_email}")

    # Backend Connection Indicator
    is_online, conn_status = check_backend_connection()
    if is_online:
        st.caption("🟢 Backend: Connected")
    else:
        st.caption("🔴 Backend: Disconnected")

    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.rerun()

    st.divider()

    # ========================================================
    # NEW CONVERSATION BUTTON
    # ========================================================
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.selected_conversation_id = None
        st.session_state.messages = []
        st.session_state.chat_error = None
        st.rerun()

    st.divider()

    st.subheader("Conversations")

    # ========================================================
    # CONVERSATION LIST
    # ========================================================
    if not st.session_state.conversations:
        st.caption("No previous conversations.")
    else:
        for conversation in st.session_state.conversations:
            conversation_id = conversation.get("conversation_id")
            title = conversation.get("title", "")

            # If title is placeholder or missing, extract from first user message
            if not title or title.lower() in ("string", "new conversation", "none", "null"):
                messages = parse_messages(conversation.get("messages"))
                first_user_message = next(
                    (
                        m.get("content", "")
                        for m in messages
                        if isinstance(m, dict) and normalize_role(m.get("role")) == "user"
                    ),
                    None,
                )

                if first_user_message:
                    title = first_user_message[:35] + ("..." if len(first_user_message) > 35 else "")
                else:
                    title = f"Chat {conversation_id[:8]}" if conversation_id else "Conversation"

            is_selected = conversation_id == st.session_state.selected_conversation_id
            button_title = f"🟢 {title}" if is_selected else title

            if st.button(
                button_title,
                key=f"conv_btn_{conversation_id}",
                use_container_width=True,
            ):
                st.session_state.selected_conversation_id = conversation_id
                st.session_state.messages = parse_messages(conversation.get("messages"))
                st.session_state.chat_error = None
                st.rerun()


# ============================================================
# MAIN CHAT UI
# ============================================================

st.title("🤖 Buyzaar AI Assistant")

st.caption("Ask about your orders, products, invoices, tracking, returns, and support policies.")

# Display any active chat errors
if st.session_state.chat_error:
    st.error(st.session_state.chat_error)

# ============================================================
# CURRENT CONVERSATION HEADER
# ============================================================

if st.session_state.selected_conversation_id:
    selected_conversation = next(
        (
            c for c in st.session_state.conversations
            if c.get("conversation_id") == st.session_state.selected_conversation_id
        ),
        None,
    )

    if selected_conversation:
        c_title = selected_conversation.get("title")
        if c_title and c_title.lower() not in ("string", "none", "null"):
            st.caption(f"Active Conversation: **{c_title}**")
        else:
            st.caption(f"Active Conversation ID: `{st.session_state.selected_conversation_id}`")


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    if not isinstance(message, dict):
        continue

    role = normalize_role(message.get("role"))
    content = message.get("content", "")

    if not content:
        continue

    with st.chat_message(role):
        st.markdown(content)


# ============================================================
# CHAT INPUT & SEND MESSAGE
# ============================================================

query = st.chat_input("Ask Buyzaar AI anything...")

if query:
    st.session_state.chat_error = None
    current_conversation_id = st.session_state.selected_conversation_id

    # Display user's question immediately
    with st.chat_message("user"):
        st.markdown(query)

    # Call AI agent endpoint
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = call_agent(
                    message=query,
                    conversation_id=current_conversation_id,
                )

                answer = (
                    result.get("message")
                    or result.get("response")
                    or result.get("answer")
                    or result.get("content")
                    or "No response received."
                )

                st.markdown(answer)

                new_conversation_id = result.get("conversation_id")
                if new_conversation_id:
                    st.session_state.selected_conversation_id = new_conversation_id

                # Refresh conversations from backend
                refresh_conversations()

                # Synchronize active messages
                active_id = st.session_state.selected_conversation_id
                conversation_found = False
                for conv in st.session_state.conversations:
                    if conv.get("conversation_id") == active_id:
                        st.session_state.messages = parse_messages(conv.get("messages"))
                        conversation_found = True
                        break

                if not conversation_found:
                    st.session_state.messages.append({"role": "user", "content": query})
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                # Successful turn: rerun to refresh full state cleanly
                st.rerun()

            except requests.RequestException as e:
                err_text = extract_error_message(e.response, str(e)) if hasattr(e, "response") and e.response is not None else str(e)
                st.session_state.chat_error = f"Backend request failed: {err_text}"
                st.error(st.session_state.chat_error)

            except Exception as e:
                st.session_state.chat_error = f"Unexpected error: {e}"
                st.error(st.session_state.chat_error)

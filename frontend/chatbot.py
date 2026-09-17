import streamlit as st
import requests


# ============================================================
# CONFIG
# ============================================================

BACKEND_URL = "http://localhost:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Buyzaar Support",
    page_icon="🤖",
    layout="wide",
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


# ============================================================
# AUTHENTICATION API FUNCTIONS
# ============================================================

def login_user(email: str, password: str) -> bool:
    """
    Authenticate customer against the backend JWT login endpoint.
    Stores access_token and refresh_token in session state upon success.
    """
    url = f"{BACKEND_URL}/auth/login"
    payload = {
        "email": email.strip(),
        "password": password,
    }

    try:
        response = requests.post(url, json=payload, timeout=25)

        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data.get("access_token")
            st.session_state.refresh_token = data.get("refresh_token")

            customer_info = data.get("customer", {})
            st.session_state.customer_id = customer_info.get("customer_id")
            st.session_state.customer_name = customer_info.get("name")
            st.session_state.customer_email = customer_info.get("email")

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
        else:
            detail = response.json().get("detail", "Login failed.")
            st.session_state.auth_error = f"Login failed: {detail}"
            return False

    except requests.RequestException as e:
        st.session_state.auth_error = f"Cannot connect to backend server: {e}"
        return False


def register_user(name: str, email: str, password: str) -> bool:
    """
    Register a new customer account via the backend JWT register endpoint.
    """
    url = f"{BACKEND_URL}/auth/register"
    payload = {
        "name": name.strip(),
        "email": email.strip(),
        "password": password,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)

        if response.status_code in (200, 201):
            st.session_state.auth_error = None
            st.session_state.auth_success = "Account created successfully! You can now log in."
            return True
        elif response.status_code == 409:
            st.session_state.auth_error = "An account with this email already exists."
            return False
        elif response.status_code == 422:
            st.session_state.auth_error = "Password must be at least 8 characters long."
            return False
        else:
            detail = response.json().get("detail", "Registration failed.")
            st.session_state.auth_error = f"Registration failed: {detail}"
            return False

    except requests.RequestException as e:
        st.session_state.auth_error = f"Cannot connect to backend server: {e}"
        return False


def refresh_access_token() -> bool:
    """
    Exchange the long-lived refresh token for a new short-lived access token.
    """
    if not st.session_state.refresh_token:
        logout_user()
        return False

    url = f"{BACKEND_URL}/auth/refresh"
    payload = {
        "refresh_token": st.session_state.refresh_token,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)

        if response.status_code == 200:
            data = response.json()
            new_access_token = data.get("access_token")
            if new_access_token:
                st.session_state.access_token = new_access_token
                return True

        logout_user()
        st.session_state.auth_error = "Session expired. Please log in again."
        return False

    except Exception:
        logout_user()
        return False


def logout_user():
    """
    Clear all authentication credentials and reset session state.
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


def get_auth_headers() -> dict:
    """
    Generate standard HTTP authorization headers with Bearer JWT access token.
    """
    headers = {"Content-Type": "application/json"}
    if st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    return headers


def authenticated_request(method: str, url: str, **kwargs) -> requests.Response:
    """
    Wrapper around requests that automatically injects the Bearer JWT token,
    and performs automatic token refreshing on 401 Unauthorized responses.
    """
    headers = kwargs.pop("headers", {})
    headers.update(get_auth_headers())

    response = requests.request(method, url, headers=headers, **kwargs)

    # If access token has expired (401), attempt to refresh and retry once
    if response.status_code == 401 and st.session_state.refresh_token:
        if refresh_access_token():
            # Update headers with new access token and retry
            headers.update(get_auth_headers())
            response = requests.request(method, url, headers=headers, **kwargs)
        else:
            st.session_state.auth_error = "Session expired. Please log in again."
            st.rerun()

    return response


# ============================================================
# API DATA FUNCTIONS
# ============================================================

def get_conversations():
    """
    Fetch all conversations for the authenticated customer.
    Conversations are sorted by updated_at so that
    the most recently updated conversation appears first.
    """
    if not st.session_state.customer_id:
        return []

    url = f"{BACKEND_URL}/customer/{st.session_state.customer_id}/conversations"

    response = authenticated_request("GET", url, timeout=30)
    response.raise_for_status()

    data = response.json()
    conversations = data.get("conversations", [])

    conversations.sort(
        key=lambda conversation: conversation.get("updated_at", ""),
        reverse=True,
    )

    return conversations


def call_agent(message: str, conversation_id: str | None = None):
    """
    Send a message to the AI support agent with Bearer JWT auth.
    conversation_id=None means create/start a new conversation.
    """
    url = f"{BACKEND_URL}/agent/call"

    payload = {
        "message": message,
        "conversation_id": conversation_id,
        "customer_id": st.session_state.customer_id,
    }

    response = authenticated_request(
        "POST",
        url,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()
    return response.json()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_conversation(conversation_id: str):
    """
    Load a specific conversation from the already fetched
    conversation list.
    """
    for conversation in st.session_state.conversations:
        if conversation.get("conversation_id") == conversation_id:
            st.session_state.selected_conversation_id = conversation_id
            st.session_state.messages = conversation.get("messages", [])
            return True
    return False


def refresh_conversations():
    """
    Refresh conversation list from backend.
    """
    st.session_state.conversations = get_conversations()


def normalize_role(role: str) -> str:
    """
    Normalize different backend role names.
    """
    role = str(role or "").lower()
    if role == "user":
        return "user"
    if role in ("assistant", "ai"):
        return "assistant"
    return "assistant"


# ============================================================
# AUTHENTICATION SCREEN (WHEN NOT LOGGED IN)
# ============================================================

if not st.session_state.is_authenticated:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center;'>🤖 Buyzaar Support</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Production-Ready E-Commerce Support Assistant</p>", unsafe_allow_html=True)
        st.write("")

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
                    if not email_input or not password_input:
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
                    if not reg_name or not reg_email or not reg_password:
                        st.warning("Please fill in all fields.")
                    elif len(reg_password) < 8:
                        st.warning("Password must be at least 8 characters long.")
                    else:
                        with st.spinner("Creating account..."):
                            if register_user(reg_name, reg_email, reg_password):
                                # Auto-login after successful registration
                                if login_user(reg_email, reg_password):
                                    st.rerun()

    # Stop rendering the rest of the application until user is authenticated
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

    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.rerun()

    st.divider()

    # ========================================================
    # NEW CONVERSATION
    # ========================================================
    if st.button(
        "➕ New Conversation",
        use_container_width=True,
    ):
        st.session_state.selected_conversation_id = None
        st.session_state.messages = []
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
            title = conversation.get("title", "New Conversation")

            if not title or title.lower() == "string":
                messages = conversation.get("messages", [])
                first_user_message = next(
                    (
                        message.get("content", "")
                        for message in messages
                        if normalize_role(message.get("role")) == "user"
                    ),
                    None,
                )

                if first_user_message:
                    title = first_user_message[:40]
                    if len(first_user_message) > 40:
                        title += "..."
                else:
                    title = "Conversation"

            is_selected = conversation_id == st.session_state.selected_conversation_id
            button_title = f"🟢 {title}" if is_selected else title

            if st.button(
                button_title,
                key=f"conversation_{conversation_id}",
                use_container_width=True,
            ):
                st.session_state.selected_conversation_id = conversation_id
                st.session_state.messages = conversation.get("messages", [])
                st.rerun()


# ============================================================
# MAIN UI
# ============================================================

st.title("🤖 Buyzaar AI Assistant")

st.caption(
    "Ask about your orders, products, invoices, tracking, returns, and more."
)


# ============================================================
# CURRENT CONVERSATION HEADER
# ============================================================

if st.session_state.selected_conversation_id:
    selected_conversation = next(
        (
            conversation
            for conversation in st.session_state.conversations
            if conversation.get("conversation_id") == st.session_state.selected_conversation_id
        ),
        None,
    )

    if selected_conversation:
        title = selected_conversation.get("title", "Conversation")
        if title and title.lower() != "string":
            st.caption(f"Conversation: **{title}**")


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:
    role = normalize_role(message.get("role"))
    content = message.get("content", "")

    if not content:
        continue

    with st.chat_message(role):
        st.write(content)


# ============================================================
# CHAT INPUT
# ============================================================

query = st.chat_input("Ask Buyzaar AI anything...")


# ============================================================
# SEND MESSAGE
# ============================================================

if query:
    current_conversation_id = st.session_state.selected_conversation_id

    # Show user message immediately
    with st.chat_message("user"):
        st.write(query)

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = call_agent(
                    message=query,
                    conversation_id=current_conversation_id,
                )

                answer = (
                    result.get("response")
                    or result.get("message")
                    or result.get("answer")
                    or result.get("content")
                )

                if answer:
                    st.write(answer)
                else:
                    st.write("The assistant did not return a response.")

                new_conversation_id = result.get("conversation_id")

                if current_conversation_id is None and new_conversation_id:
                    st.session_state.selected_conversation_id = new_conversation_id

                refresh_conversations()

                active_conversation_id = st.session_state.selected_conversation_id
                if new_conversation_id:
                    active_conversation_id = new_conversation_id
                    st.session_state.selected_conversation_id = new_conversation_id

                conversation_found = False
                for conversation in st.session_state.conversations:
                    if conversation.get("conversation_id") == active_conversation_id:
                        st.session_state.messages = conversation.get("messages", [])
                        conversation_found = True
                        break

                if not conversation_found:
                    st.session_state.messages.append({"role": "user", "content": query})
                    if answer:
                        st.session_state.messages.append({"role": "assistant", "content": answer})

            except requests.RequestException as e:
                st.error(f"Backend request failed: {e}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.rerun()

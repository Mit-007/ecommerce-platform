import streamlit as st
import requests


# ============================================================
# CONFIG
# ============================================================

BACKEND_URL = "http://localhost:8000"

CUSTOMER_ID = "9afa8d59-957a-4c9c-bdaa-4655b449ffb9"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Buyzaar Support",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "selected_conversation_id" not in st.session_state:
    st.session_state.selected_conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False


# ============================================================
# API FUNCTIONS
# ============================================================

def get_conversations():
    """
    Fetch all customer conversations.

    Conversations are sorted by updated_at so that
    the most recently updated conversation appears first.
    """

    url = f"{BACKEND_URL}/customer/{CUSTOMER_ID}/conversations"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    conversations = data.get("conversations", [])

    # --------------------------------------------------------
    # Sort newest updated conversation first
    # --------------------------------------------------------

    conversations.sort(
        key=lambda conversation: conversation.get(
            "updated_at",
            "",
        ),
        reverse=True,
    )

    return conversations


def call_agent(message, conversation_id=None):
    """
    Send a message to the agent.

    conversation_id=None means create/start a new conversation.
    """

    url = f"{BACKEND_URL}/agent/call"

    payload = {
        "message": message,
        "conversation_id": conversation_id,
        "customer_id": CUSTOMER_ID,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_conversation(conversation_id):
    """
    Load a specific conversation from the already fetched
    conversation list.
    """

    for conversation in st.session_state.conversations:

        if conversation.get("conversation_id") == conversation_id:

            st.session_state.selected_conversation_id = (
                conversation_id
            )

            st.session_state.messages = (
                conversation.get("messages", [])
            )

            return True

    return False


def refresh_conversations():
    """
    Refresh conversation list from backend.

    This also guarantees that conversations are reordered
    according to updated_at.
    """

    st.session_state.conversations = get_conversations()


def normalize_role(role):
    """
    Normalize different backend role names.

    Supports:
        user
        assistant
        AI
    """

    role = str(role or "").lower()

    if role == "user":
        return "user"

    if role in ("assistant", "ai"):
        return "assistant"

    return "assistant"


# ============================================================
# INITIAL LOAD
# ============================================================

if not st.session_state.initialized:

    try:

        st.session_state.conversations = get_conversations()

        # ----------------------------------------------------
        # IMPORTANT:
        # Start the application with a NEW conversation.
        #
        # Do NOT automatically open the newest old conversation.
        # ----------------------------------------------------

        st.session_state.selected_conversation_id = None
        st.session_state.messages = []

        st.session_state.initialized = True

    except Exception as e:

        st.error(
            f"Failed to load conversations: {e}"
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("💬 Buyzaar Support")

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

            conversation_id = conversation.get(
                "conversation_id"
            )

            title = conversation.get(
                "title",
                "New Conversation",
            )

            # ------------------------------------------------
            # Handle backend default title
            # ------------------------------------------------

            if not title or title.lower() == "string":

                messages = conversation.get(
                    "messages",
                    [],
                )

                # Try to use first user message as title
                first_user_message = next(
                    (
                        message.get("content", "")
                        for message in messages
                        if normalize_role(
                            message.get("role")
                        ) == "user"
                    ),
                    None,
                )

                if first_user_message:

                    title = first_user_message[:40]

                    if len(first_user_message) > 40:
                        title += "..."

                else:

                    title = "Conversation"

            # ------------------------------------------------
            # Highlight currently selected conversation
            # ------------------------------------------------

            is_selected = (
                conversation_id
                == st.session_state.selected_conversation_id
            )

            button_title = (
                f"🟢 {title}"
                if is_selected
                else title
            )

            # ------------------------------------------------
            # Conversation button
            # ------------------------------------------------

            if st.button(
                button_title,
                key=f"conversation_{conversation_id}",
                use_container_width=True,
            ):

                # --------------------------------------------
                # Load old conversation
                # --------------------------------------------

                st.session_state.selected_conversation_id = (
                    conversation_id
                )

                st.session_state.messages = (
                    conversation.get(
                        "messages",
                        [],
                    )
                )

                st.rerun()


# ============================================================
# MAIN UI
# ============================================================

st.title("🤖 Buyzaar AI Assistant")

st.caption(
    "Ask about your orders, products, invoices, "
    "tracking, returns, and more."
)


# ============================================================
# CURRENT CONVERSATION
# ============================================================

if st.session_state.selected_conversation_id:

    selected_conversation = next(
        (
            conversation
            for conversation in st.session_state.conversations
            if conversation.get("conversation_id")
            == st.session_state.selected_conversation_id
        ),
        None,
    )

    if selected_conversation:

        title = selected_conversation.get(
            "title",
            "Conversation",
        )

        if title and title.lower() != "string":

            st.caption(
                f"Conversation: **{title}**"
            )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = normalize_role(
        message.get("role")
    )

    content = message.get(
        "content",
        "",
    )

    if not content:
        continue

    with st.chat_message(role):

        st.write(content)


# ============================================================
# CHAT INPUT
# ============================================================

query = st.chat_input(
    "Ask Buyzaar AI anything..."
)


# ============================================================
# SEND MESSAGE
# ============================================================

if query:

    # --------------------------------------------------------
    # Current conversation ID BEFORE API call
    # --------------------------------------------------------

    current_conversation_id = (
        st.session_state.selected_conversation_id
    )

    # --------------------------------------------------------
    # Show user message immediately
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.write(query)

    # --------------------------------------------------------
    # Call backend
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                result = call_agent(
                    message=query,
                    conversation_id=current_conversation_id,
                )

                # =================================================
                # GET RESPONSE
                # =================================================

                answer = (
                    result.get("response")
                    or result.get("message")
                    or result.get("answer")
                    or result.get("content")
                )

                if answer:

                    st.write(answer)

                else:

                    st.write(
                        "The assistant did not return a response."
                    )

                # =================================================
                # GET CONVERSATION ID
                # =================================================

                new_conversation_id = result.get(
                    "conversation_id"
                )

                # -------------------------------------------------
                # If this was a NEW conversation,
                # backend should return its ID.
                # -------------------------------------------------

                if (
                    current_conversation_id is None
                    and new_conversation_id
                ):

                    st.session_state.selected_conversation_id = (
                        new_conversation_id
                    )

                # =================================================
                # REFRESH CONVERSATIONS
                # =================================================

                refresh_conversations()

                # =================================================
                # DETERMINE FINAL ACTIVE CONVERSATION
                # =================================================

                active_conversation_id = (
                    st.session_state.selected_conversation_id
                )

                # -------------------------------------------------
                # If backend returned an ID, always use it.
                # -------------------------------------------------

                if new_conversation_id:

                    active_conversation_id = (
                        new_conversation_id
                    )

                    st.session_state.selected_conversation_id = (
                        new_conversation_id
                    )

                # =================================================
                # RELOAD COMPLETE CONVERSATION
                # =================================================

                conversation_found = False

                for conversation in (
                    st.session_state.conversations
                ):

                    if (
                        conversation.get(
                            "conversation_id"
                        )
                        == active_conversation_id
                    ):

                        st.session_state.messages = (
                            conversation.get(
                                "messages",
                                [],
                            )
                        )

                        conversation_found = True

                        break

                # -------------------------------------------------
                # Safety fallback
                # -------------------------------------------------

                if not conversation_found:

                    # Keep current messages if backend
                    # did not return the conversation yet.
                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content": query,
                        }
                    )

                    if answer:

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

            except requests.RequestException as e:

                st.error(
                    f"Backend request failed: {e}"
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

    # ========================================================
    # REFRESH UI
    # ========================================================

    st.rerun()

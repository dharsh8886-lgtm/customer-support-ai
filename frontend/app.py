import os
import requests
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta

API_URL = os.environ.get("TECHNOVA_API_URL", "https://technova-backend-r6ao.onrender.com")

def load_chat_history():
    token = st.session_state.get("token")

    if not token:
        return []

    try:
        response = requests.get(
            f"{API_URL}/chat-history",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if response.status_code == 200:
            return response.json().get("history", [])

    except requests.RequestException:
        return []

    return []


st.set_page_config(
    page_title="TechNova Support AI",
    page_icon="🛒",
    layout="wide"
)

cookie_manager = stx.CookieManager(key="technova_cookie_manager")


# ---------------- SESSION STATE ----------------

defaults = {
    "token": None,
    "email": None,
    "name": None,
    "quick_prompt": None,
    "messages": [],
    "show_forgot_password": False,
    "show_terms": False,
    "show_privacy": False,
    "page": "Login",
    "developer_mode": False,
    "terms_accepted": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- CSS ----------------

st.markdown("""
<style>

/* Page background */
.stApp {
    background:
        radial-gradient(circle at 12% 18%, rgba(6, 182, 212, 0.09), transparent 28%),
        radial-gradient(circle at 88% 16%, rgba(124, 58, 237, 0.11), transparent 30%),
        radial-gradient(circle at 70% 82%, rgba(124, 58, 237, 0.05), transparent 26%),
        linear-gradient(135deg, #F8FAFC 0%, #F6F4FB 50%, #F8FAFC 100%);
}

/* Main page width and spacing */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 1rem;
    max-width: 1500px;
}

/* Main headings */
h1, h2, h3 {
    color: #1F2937;
    font-family: "Segoe UI", sans-serif;
}

/* Divider */
hr {
    border-color: #E5E7EB;
}

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 18px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 10px 30px rgba(124, 58, 237, 0.05);
}

/* Selected tab and primary actions */
button[kind="primary"] {
    background: #7C3AED !important;
    color: #FFFFFF !important;
    border: 1px solid #7C3AED !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.22) !important;
}

button[kind="primary"]:hover {
    background: #6D28D9 !important;
    border-color: #6D28D9 !important;
    transform: translateY(-2px);
}

button[kind="primary"]:disabled {
    background: #C4B5FD !important;
    border-color: #C4B5FD !important;
    color: #FFFFFF !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Text inputs */
input, textarea {
    border-radius: 12px !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 10px;
}

/* Chat input */
[data-testid="stChatInput"] {
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(31, 41, 55, 0.08);
}

/* Hide Streamlit default sidebar */
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

.footer {
    width: 100%;
    margin-top: 25px;
    padding: 18px 10px;
    text-align: center;
}

.copyright {
    color: #6B7280;
    font-size: 13px;
}

.footer-links a {
    color: #6B7280;
    text-decoration: none;
    font-size: 13px;
    margin: 0 5px;
}

.footer-links a:hover {
    color: #7C3AED;
}

.secure-text {
    text-align: center;
    margin-top: 2px !important;
    color: #7C3AED;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.2px;
}

/* Hide Streamlit top toolbar containing Deploy */
[data-testid="stToolbar"] { display: none; }

/* Remove the white top header space */
[data-testid="stHeader"] {
    background: transparent;
    height: 0;
}

[data-testid="stAppViewContainer"] { background: transparent; }
[data-testid="stMain"] { background: transparent; }

/* Auth selector buttons */
div[data-testid="stButton"] > button {
    border-radius: 10px;
    border: 1px solid #E5E7EB;
    background: #FFFFFF;
    color: #374151;
    font-weight: 600;
    min-height: 44px;
    text-align: center;
    outline: none !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    padding-left: 14px !important;
    padding-right: 14px !important;
}

div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button:focus-visible,
div[data-testid="stButton"] > button:active {
    outline: none !important;
    box-shadow: none !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #7C3AED;
    background: #F5F3FF !important;
    color: #5B5BD6 !important;
    transform: none;
}

/* Subtitle text */
[data-testid="stCaptionContainer"] { color: #6B7280 !important; }

/* Unselected tab */
button[kind="secondary"] {
    background: #F8F7FC !important;
    color: #8B8797 !important;
    border: 1px solid #E5E1EE !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

button[kind="secondary"]:hover {
    background: #F3EFFF !important;
    color: #7C3AED !important;
    border-color: #C4B5FD !important;
    transform: none !important;
}

/* Input focus styling */
[data-testid="stTextInput"] input {
    border: 1px solid transparent !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stTextInput"] input:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.14) !important;
}

/* Hide Streamlit heading anchor icons */
a[data-testid="stHeaderActionElements"],
[data-testid="stHeaderActionElements"] { display: none !important; }

/* ================= CHAT LAYOUT ================= */

/* ---- Left brand/nav panel (logo + New Conversation + Recent chats) ---- */

.brand-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
}

.brand-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7C3AED, #2563EB);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.25);
    flex-shrink: 0;
}

.brand-title {
    font-size: 16px;
    font-weight: 800;
    color: #1F2937;
    line-height: 1.15;
}

.brand-subtitle {
    font-size: 11.5px;
    font-weight: 600;
    color: #9CA3AF;
    letter-spacing: 0.3px;
}

.sidebar-panel-title {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: #9CA3AF;
    margin-bottom: 12px;
}

.recent-chats-heading {
    margin-top: 18px;
    margin-bottom: 4px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    color: #9CA3AF;
    padding-left: 6px;
}

/* Sidebar panel background, distinct from main content */
.st-key-sidebar_panel {
    background: rgba(124, 58, 237, 0.03) !important;
    padding: 18px 14px !important;
}

/* "New Conversation" primary sidebar action */
.st-key-new_chat_btn button {
    background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    justify-content: center !important;
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.25) !important;
    border-radius: 12px !important;
    min-height: 46px !important;
}

.st-key-new_chat_btn button:hover {
    background: linear-gradient(135deg, #6D28D9, #7C3AED) !important;
    transform: translateY(-1px);
}

/* ---- Recent chats: flat, minimal, ChatGPT-style list ---- */

/* Streamlit inserts a default gap between each element in a vertical
   block (one per st.button call here) — collapse it so rows sit close
   together instead of leaving large blank gaps. */
.st-key-recent_chats_list [data-testid="stVerticalBlock"] {
    gap: 0.05rem !important;
}

.st-key-recent_chats_list [data-testid="stElementContainer"] {
    margin-bottom: 0 !important;
}

.st-key-recent_chats_list button {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: #374151 !important;
    font-weight: 400 !important;
    padding-left: 10px !important;
    padding-right: 8px !important;
    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;
    margin: 0 !important;
    overflow: hidden !important;
    box-shadow: none !important;
}

.st-key-recent_chats_list button p {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    margin: 0 !important;
    font-size: 13.5px !important;
    font-weight: 400 !important;
    line-height: 1.2 !important;
}

.st-key-recent_chats_list button:hover {
    background: rgba(0, 0, 0, 0.055) !important;
    border: none !important;
    color: #111827 !important;
    transform: none !important;
}

.st-key-delete_all_history_btn button {
    color: #9CA3AF !important;
    font-weight: 500 !important;
    border: 1px dashed #E5E7EB !important;
    background: transparent !important;
}

.st-key-delete_all_history_btn button:hover {
    color: #DC2626 !important;
    border-color: #FCA5A5 !important;
    background: #FEF2F2 !important;
}

/* ---- Header row with title + status ---- */

.chat-header-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 4px 4px 10px 4px;
}

.chat-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.chat-header-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7C3AED, #2563EB);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.22);
    flex-shrink: 0;
}

.chat-header-title {
    font-size: 17px;
    font-weight: 800;
    color: #1F2937;
    line-height: 1.2;
}

.chat-header-status {
    font-size: 12px;
    font-weight: 600;
    color: #16A34A;
    display: flex;
    align-items: center;
    gap: 5px;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22C55E;
    display: inline-block;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.18);
}

.chat-welcome-card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid #E5E7EB;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(31, 41, 55, 0.06), 0 8px 22px rgba(124, 58, 237, 0.05);
    margin-bottom: 14px;
}

.welcome-hero {
    text-align: center;
    padding: 18px 10px 6px 10px;
}

.welcome-hero-icon {
    width: 62px;
    height: 62px;
    margin: 0 auto 14px auto;
    border-radius: 18px;
    background: linear-gradient(135deg, #7C3AED, #8B5CF6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    color: #fff;
    box-shadow: 0 10px 26px rgba(124, 58, 237, 0.3);
}

.welcome-hero-title {
    font-size: 26px;
    font-weight: 800;
    color: #1F2937;
    margin-bottom: 6px;
}

.welcome-hero-subtitle {
    font-size: 14px;
    color: #6B7280;
    max-width: 640px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Compact quick-action buttons */
.st-key-quick_product_btn button,
.st-key-quick_billing_btn button,
.st-key-quick_faq_btn button,
.st-key-quick_technical_btn button,
.st-key-quick_refund_btn button,
.st-key-quick_contact_btn button {
    min-height: 46px !important;
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.92) !important;
    border: 1px solid #DDD6FE !important;
    color: #4B5563 !important;
    font-weight: 600 !important;
    justify-content: center !important;
    box-shadow: 0 3px 10px rgba(31, 41, 55, 0.04) !important;
}

.st-key-quick_product_btn button:hover,
.st-key-quick_billing_btn button:hover,
.st-key-quick_faq_btn button:hover,
.st-key-quick_technical_btn button:hover,
.st-key-quick_refund_btn button:hover,
.st-key-quick_contact_btn button:hover {
    background: #F5F3FF !important;
    border-color: #7C3AED !important;
    color: #6D28D9 !important;
    transform: translateY(-1px) !important;
}

/* ================= MAIN CHAT PANEL (ChatGPT-style bottom-pinned input) ================= */

/* Whole right-hand chat column: header on top, scrollable content in the
   middle, input pinned to the very bottom — mirrors the ChatGPT layout. */
.st-key-main_chat_panel {
    min-height: calc(100vh - 220px) !important;
    max-height: calc(100vh - 190px) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

/* Middle area (welcome hero OR message list) grows to fill all the
   leftover space so the input box always sits at the bottom. */
.st-key-chat_content_area {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    display: flex !important;
    flex-direction: column !important;
}

/* When there are no messages yet, vertically center the welcome hero,
   just like ChatGPT's empty-state screen. */
.st-key-chat_content_area_empty {
    justify-content: center !important;
}

/* Once a conversation exists, content should start from the top and the
   inner scroll area (below) handles the actual scrolling. */
.st-key-chat_content_area_active {
    justify-content: flex-start !important;
}

/* Scrollable conversation panel - only this area scrolls, not the full page */
.st-key-chat_scroll_area {
    flex: 1 1 auto !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 4px 4px 8px 4px;
}

.st-key-chat_scroll_area::-webkit-scrollbar {
    width: 6px;
}

.st-key-chat_scroll_area::-webkit-scrollbar-thumb {
    background: #DDD6FE;
    border-radius: 999px;
}

.st-key-chat_scroll_area::-webkit-scrollbar-track {
    background: transparent;
}

/* Input row: never shrinks, always glued to the bottom of the panel */
.st-key-chat_input_area {
    flex: 0 0 auto !important;
    padding-top: 10px !important;
}

/* Chat input styling */
[data-testid="stChatInput"] {
    z-index: 20;
    background: rgba(255, 255, 255, 0.98) !important;
    backdrop-filter: blur(12px);
    border: 1px solid #DDD6FE !important;
    border-radius: 999px !important;
    box-shadow: 0 10px 30px rgba(31, 41, 55, 0.12) !important;
    margin: 0 auto !important;
    max-width: 820px !important;
    width: 100% !important;
}

[data-testid="stChatInput"] textarea { border-radius: 999px !important; }

[data-testid="stChatInput"] button {
    background: #7C3AED !important;
    color: white !important;
    border-radius: 50% !important;
    border: none !important;
}

[data-testid="stChatInput"] button:hover { background: #6D28D9 !important; }

/* Avatar */
.user-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7C3AED, #2563EB);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
    box-shadow: 0 5px 14px rgba(124, 58, 237, 0.2);
}

/* Bottom-left signed-in strip (like the reference image) */
.st-key-user_strip {
    background: rgba(124, 58, 237, 0.04) !important;
    border-top: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    padding: 8px 10px !important;
}

.user-strip-name {
    font-size: 13px;
    font-weight: 700;
    color: #1F2937;
    line-height: 1.2;
}

.user-strip-status {
    font-size: 11px;
    color: #9CA3AF;
    font-weight: 600;
}

/* Footer buttons should look like text links */
button[kind="tertiary"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    color: #7C3AED !important;
    min-height: auto !important;
    padding: 2px 4px !important;
    font-weight: 500 !important;
}

button[kind="tertiary"]:hover {
    background: transparent !important;
    border: none !important;
    color: #6D28D9 !important;
    text-decoration: underline !important;
    transform: none !important;
}

/* Slim footer shown on the chat page */
.chat-footer {
    text-align: center;
    margin-top: 6px;
    flex: 0 0 auto;
}

.chat-footer .copyright {
    font-size: 12px;
}

.chat-footer-sep {
    color: #D1D5DB;
    margin: 0 6px;
    font-size: 12px;
}

.dev-mode-banner {
    display: inline-block;
    background: #F5F3FF;
    border: 1px solid #DDD6FE;
    color: #6D28D9;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 10px;
}

html, body {
    min-height: 100%;
}

[data-testid="stAppViewContainer"] {
    overflow-y: auto !important;
}

[data-testid="stMain"] {
    overflow-y: auto !important;
}

.block-container {
    min-height: 100vh !important;
    overflow: visible !important;
    padding-bottom: 90px !important;
}

</style>
""", unsafe_allow_html=True)


# ---------------- TOP NAVIGATION ----------------

left, right = st.columns([6.3, 3.9], vertical_alignment="center")

with left:
    st.markdown("""
    <div style="display:flex;align-items:center;">
        <span style="font-size:32px;">🛒</span>
        <span style="margin-left:10px;color:#1976D2;font-size:32px;font-weight:700;font-family:Segoe UI, sans-serif;">
            TechNova Electronics
        </span>
    </div>
    """, unsafe_allow_html=True)

with right:
    if st.session_state.token:

        username = st.session_state.name or "User"
        initials = "".join(part[0].upper() for part in username.split() if part)[:2]
        if len(initials) < 2 and len(username.strip()) > 1:
            initials = username.strip()[:2].upper()

        avatar_col, clear_col, logout_col, settings_col = st.columns(
            [0.7, 1.15, 1.3, 1.45], gap="small", vertical_alignment="center"
        )

        with avatar_col:
            st.markdown(
                f'<div style="height:44px;display:flex;align-items:center;justify-content:center;">'
                f'<div class="user-avatar" title="{username}">{initials}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with clear_col:
            if st.button("Clear", icon=":material/delete_outline:", type="secondary",
                          use_container_width=True, key="clear_chat_btn",
                          disabled=not st.session_state.messages,
                          help="Clear the current conversation"):
                st.session_state.messages = []
                st.session_state.quick_prompt = None
                st.rerun()

        with logout_col:
            if st.button("Logout", icon=":material/logout:", type="secondary",
                          use_container_width=True, key="logout_btn"):
                st.session_state.token = None
                st.session_state.email = None
                st.session_state.name = None
                st.session_state.messages = []
                st.session_state.quick_prompt = None
                st.session_state.page = "Login"
                st.rerun()

        with settings_col:
            with st.popover("Settings", icon=":material/settings:", use_container_width=True):
                st.session_state.developer_mode = st.checkbox(
                    "Developer Mode", value=st.session_state.developer_mode,
                    help="Show detected intent and routed agent details in responses."
                )
                st.caption(f"Signed in as {st.session_state.email or username}")

st.markdown(
    '<hr style="border:none;height:1px;background:#CBD5E1;margin-top:8px;margin-bottom:8px;">',
    unsafe_allow_html=True
)


# -------- Forgot Password --------

@st.dialog("Reset your password")
def forgot_password_dialog():
    st.write("Enter your registered email address. We will send password reset instructions.")

    reset_email = st.text_input(
        "Email address", placeholder="Enter your registered email", key="reset_email"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Send reset link", type="primary", use_container_width=True):
            if not reset_email.strip():
                st.warning("Please enter your email address.")
            elif "@" not in reset_email or "." not in reset_email:
                st.warning("Please enter a valid email address.")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/forgot-password",
                        json={"email": reset_email.strip()},
                        timeout=60
                    )
                    if response.status_code == 200:
                        st.success("Password reset instructions have been sent.")
                    else:
                        message = response.json().get("detail", "Unable to process the request.")
                        st.error(message)
                except requests.exceptions.ConnectionError as error:
                    st.error(f"Connection error: {error}")

                except requests.exceptions.Timeout as error:
                    st.error(f"Backend timeout: {error}")

                except requests.RequestException as error:
                    st.error(f"Request failed: {type(error).__name__}: {error}")

                except ValueError as error:
                    st.error(
                        f"Invalid backend response. "
                        f"Status: {response.status_code if 'response' in locals() else 'unknown'} "
                        f"Body: {response.text if 'response' in locals() else 'no response'}"
                    )

    with col2:
        if st.button("Close", use_container_width=True, key="close_forgot_password"):
            st.rerun()


# -------------- Terms & Conditions ----------

@st.dialog("Terms and Conditions")
def terms_dialog():
    st.markdown("""
### TechNova Electronics — Terms and Conditions

**Last updated: 20 July 2026**

By accessing or using the TechNova AI Customer Support Assistant,
you agree to the following conditions.

#### 1. Use of the service

The assistant is provided to help users with product information,
technical support, order-related questions and general customer service.

You must not use the service for illegal, harmful, fraudulent or abusive
activities.

#### 2. AI-generated responses

Some answers are generated using artificial intelligence. Although we
attempt to provide accurate information, AI responses may occasionally
contain errors.

For important product, payment, warranty or safety information, users
should verify the details with an authorised TechNova representative.

#### 3. User account

You are responsible for protecting your login information and for all
activity performed through your account.

You must not share your password with another person.

#### 4. User information

Information submitted through the service may be processed to provide
customer support, improve service quality and maintain account security.

#### 5. Prohibited activity

Users must not attempt to:

- Access another user's account.
- Upload malicious files or harmful content.
- Interfere with the operation of the service.
- Extract confidential system or customer information.
- Use the assistant to conduct fraud or impersonation.

#### 6. Service availability

TechNova does not guarantee that the service will always be available,
error-free or uninterrupted.

#### 7. Limitation of liability

TechNova Electronics is not responsible for losses caused by misuse of
the service, incorrect user information or reliance on an unverified
AI-generated response.

#### 8. Changes to these terms

These terms may be updated when features, legal requirements or company
policies change.

#### 9. Contact

Questions about these terms may be sent to:

**support@technova.example**
""")

    accepted = st.checkbox(
        "I have read and understood the Terms and Conditions.",
        key="terms_dialog_accept"
    )

    if st.button("Accept and close", type="primary", use_container_width=True, disabled=not accepted):
        st.session_state.terms_accepted = True
        st.rerun()


# ------------------ Privacy -----------------

@st.dialog("Privacy Policy")
def privacy_dialog():
    st.markdown("""
### TechNova Electronics — Privacy Policy

TechNova may collect information such as your name, email address,
support messages and account activity to provide customer support and
maintain service security.

Passwords must be stored only in encrypted or hashed form. TechNova
will not ask users to disclose passwords through chat.

Your information will not be sold to third parties. Information may be
shared only when required to operate the service, prevent fraud or
comply with applicable law.

Users may contact **support@technova.example** for privacy-related
questions.
""")

    if st.button("Close", type="primary", use_container_width=True, key="close_privacy"):
        st.rerun()


# ---------------- AUTH PAGE ----------------

if not st.session_state.token:

    st.write("")

    left_space, auth_column, right_space = st.columns([1.5, 2, 1.5])

    with auth_column:

        with st.container(border=True):

            signin_type = "primary" if st.session_state.page == "Login" else "secondary"
            register_type = "primary" if st.session_state.page == "Register" else "secondary"

            tab_col1, tab_col2 = st.columns([1, 1], gap="small")

            with tab_col1:
                if st.button("Sign In", icon=":material/login:", type=signin_type,
                              use_container_width=True, key="auth_signin_tab"):
                    st.session_state.page = "Login"
                    st.rerun()

            with tab_col2:
                if st.button("Register", icon=":material/person_add:", type=register_type,
                              use_container_width=True, key="auth_register_tab"):
                    st.session_state.page = "Register"
                    st.rerun()

            # ================= SIGN IN TAB =================

            if st.session_state.page == "Login":

                st.markdown(
                    '<h2 style="font-size:40px;font-weight:700;margin-bottom:5px;">Welcome Back</h2>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<p style="color:#6B7280;margin-top:-18px;margin-bottom:2px;">Sign in to continue</p>',
                    unsafe_allow_html=True
                )

                remembered_email = cookie_manager.get(cookie="technova_email")

                login_email = st.text_input(
                    "Email", value=remembered_email or "",
                    placeholder="Enter your email", key="login_email"
                )

                login_password = st.text_input(
                    "Password", type="password",
                    placeholder="Enter your password", key="login_password"
                )

                remember_col, forgot_col = st.columns([1, 1])

                with remember_col:
                    remember_me = st.checkbox(
                        "Remember me", value=bool(remembered_email), key="remember_me"
                    )

                with forgot_col:
                    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
                    if st.button("Forgot password?", type="tertiary",
                                  use_container_width=True, key="forgot_password_btn"):
                        forgot_password_dialog()

                if st.button("Sign In", type="primary", use_container_width=True, key="login_submit_btn"):
                    if not login_email.strip():
                        st.error("Please enter your email.")
                    elif "@" not in login_email or "." not in login_email:
                        st.error("Please enter a valid email.")
                    elif not login_password:
                        st.error("Please enter your password.")
                    else:
                        try:
                            with st.spinner("Signing you in..."):
                                response = requests.post(
                                    f"{API_URL}/login",
                                    json={
                                        "email": login_email.strip(),
                                        "password": login_password
                                    },
                                    timeout=60
                                )

                            result = response.json()

                            if result.get("success"):
                                if remember_me:
                                    cookie_manager.set(
                                        "technova_email",
                                        login_email.strip(),
                                        expires_at=datetime.now() + timedelta(days=7),
                                        key="save_technova_email"
                                    )
                                elif remembered_email:
                                    cookie_manager.delete(
                                        "technova_email", key="delete_technova_email"
                                    )

                                st.session_state.token = result.get("access_token")
                                st.session_state.email = result.get("email", login_email.strip())
                                st.session_state.name = result.get("name", "User")
                                st.session_state.messages = []
                                st.session_state.quick_prompt = None
                                st.session_state.page = "Chat"
                                st.rerun()
                            else:
                                st.error(result.get("message", "Login failed."))

                        except requests.exceptions.ConnectionError:
                            st.error("Backend is not running. Start the FastAPI server.")
                        except requests.RequestException:
                            st.error("Unable to connect to the backend.")
                        except ValueError:
                            st.error("Backend returned an invalid response.")

            # ================= REGISTER TAB =================

            elif st.session_state.page == "Register":

                st.markdown(
                    '<h2 style="font-size:40px;font-weight:700;margin-bottom:5px;">Create Account</h2>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<p style="color:#6B7280;margin-top:-18px;margin-bottom:6px;">'
                    'Register to start using TechNova Support AI</p>',
                    unsafe_allow_html=True
                )

                register_name = st.text_input("Name", placeholder="Enter your name", key="register_name")
                register_email = st.text_input("Email", placeholder="Enter your email", key="register_email")
                register_password = st.text_input(
                    "Password", type="password", placeholder="Create a password", key="register_password"
                )

                st.markdown(
                    '<div style="color:#6B7280;font-size:12px;margin-top:-12px;margin-bottom:4px;">'
                    'Use at least 8 characters.</div>',
                    unsafe_allow_html=True
                )

                if st.button("Create Account", type="primary", use_container_width=True,
                              key="register_submit_btn"):
                    if not register_name.strip():
                        st.error("Please enter your name.")
                    elif not register_email.strip():
                        st.error("Please enter your email.")
                    elif "@" not in register_email or "." not in register_email:
                        st.error("Please enter a valid email.")
                    elif not register_password:
                        st.error("Please create a password.")
                    elif len(register_password) < 8:
                        st.error("Password must contain at least 8 characters.")
                    else:
                        try:
                            with st.spinner("Creating your account..."):
                                response = requests.post(
                                    f"{API_URL}/register",
                                    json={
                                        "name": register_name.strip(),
                                        "email": register_email.strip(),
                                        "password": register_password
                                    },
                                    timeout=60
                                )
                                result = response.json()

                            if result.get("success"):
                                st.success(
                                    result.get(
                                        "message",
                                        "Registration successful. Open the Sign In tab."
                                    )
                                )
                            else:
                                st.error(result.get("message", "Registration failed."))

                        except requests.exceptions.ConnectionError:
                            st.error("Backend is not running. Start the FastAPI server.")
                        except requests.RequestException:
                            st.error("Unable to connect to the backend.")
                        except ValueError:
                            st.error("Backend returned an invalid response.")

    # ---------------- FOOTER ----------------

    st.markdown(
        '<div class="footer"><p class="copyright">© 2026 TechNova Electronics</p></div>',
        unsafe_allow_html=True
    )

    (footer_left, privacy_col, sep1, terms_col, sep2, help_col, footer_right) = st.columns(
        [4, 1, 0.1, 1, 0.1, 1, 4]
    )

    with privacy_col:
        if st.button("Privacy", type="tertiary", key="footer_privacy"):
            privacy_dialog()

    with sep1:
        st.markdown('<div style="text-align:center;color:#9CA3AF;">|</div>', unsafe_allow_html=True)

    with terms_col:
        if st.button("Terms", type="tertiary", key="footer_terms"):
            terms_dialog()

    with sep2:
        st.markdown('<div style="text-align:center;color:#9CA3AF;">|</div>', unsafe_allow_html=True)

    with help_col:
        if st.button("Help", type="tertiary", key="footer_help"):
            st.info("Email: support@technova.example")

    st.markdown(
        '<div class="secure-text">🔒 Secured with encrypted authentication</div>',
        unsafe_allow_html=True
    )


# ---------------- CHAT PAGE ----------------

else:

    username = st.session_state.name or "User"

    history_column, center_space1, chat_column, center_space2 = st.columns(
        [1, 0.2, 4, 0.2],
        gap="small"
    )

    # ================= LEFT HISTORY / NAVIGATION =================

    with history_column:

        with st.container(border=True, key="sidebar_panel"):

            # Brand row: logo + product name (mirrors the reference image)
            st.markdown(
                """
                <div class="brand-row">
                    <div class="brand-icon">🤖</div>
                    <div>
                        <div class="brand-title">TechNova Support</div>
                        <div class="brand-subtitle">MULTI-AGENT AI</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("＋  New Conversation", type="primary",
                          use_container_width=True, key="new_chat_btn"):
                st.session_state.messages = []
                st.session_state.quick_prompt = None
                st.rerun()

            st.markdown(
                '<div class="recent-chats-heading">Recents</div>',
                unsafe_allow_html=True
            )

            with st.spinner("Loading recent chats..."):
                history = load_chat_history()
            recent_history = list(reversed(history))

            hidden_followups = {
                "yes", "yeah", "yep", "ok", "okay", "continue", "more", "tell me more"
            }

            displayed_count = 0
            seen = set()

            with st.container(height=420, border=False, key="recent_chats_list"):
                for index, item in enumerate(recent_history):

                    question = item.get("user_message", "").strip()
                    normalized_question = question.lower()

                    if not question or len(question) < 4:
                        continue
                    if normalized_question in hidden_followups:
                        continue
                    if normalized_question in seen:
                        continue

                    seen.add(normalized_question)

                    short_title = question
                    if len(short_title) > 30:
                        short_title = short_title[:26].rstrip() + "…"

                    if st.button(
                        short_title,
                                  type="secondary", key=f"recent_chat_{index}",
                                  use_container_width=True, help=question):
                        old_answer = item.get("ai_response", "No response available.")
                        st.session_state.messages = [
                            {"role": "user", "content": question},
                            {"role": "assistant", "content": old_answer}
                        ]
                        st.session_state.quick_prompt = None
                        st.rerun()

                    displayed_count += 1
                    if displayed_count >= 15:
                        break

                if displayed_count == 0:
                    st.caption("No recent chats yet. Start a conversation to see it here.")

            if st.button("Clear history", icon=":material/delete_sweep:", type="secondary",
                          use_container_width=True, key="delete_all_history_btn",
                          disabled=displayed_count == 0):
                try:
                    response = requests.delete(
                        f"{API_URL}/chat-history",
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        timeout=10
                    )
                    if response.status_code == 200:
                        st.session_state.messages = []
                        st.success("History cleared.")
                        st.rerun()
                    else:
                        st.error("Unable to clear history.")
                except requests.RequestException:
                    st.error("Unable to connect to the backend.")

            # Bottom "signed in as" strip, like the reference image
            initials = "".join(part[0].upper() for part in username.split() if part)[:2]
            if len(initials) < 2 and len(username.strip()) > 1:
                initials = username.strip()[:2].upper()

            with st.container(key="user_strip"):
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div class="user-avatar" style="width:32px;height:32px;font-size:12px;">{initials}</div>
                        <div>
                            <div class="user-strip-name">{username}</div>
                            <div class="user-strip-status">Logged in</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ================= MAIN CHAT =================

    with chat_column:

        has_messages = len(st.session_state.messages)> 0

        # Everything for this column — header, scrollable content, input —
        # lives inside one flex container so the input always stays pinned
        # to the bottom, ChatGPT-style, no matter how tall the content is.
        with st.container(key="main_chat_panel"):

            # Header row: assistant name/status only (no agent badges)
            st.markdown(
                """
                <div class="chat-header-row">
                    <div class="chat-header-left">
                        <div class="chat-header-icon">🤖</div>
                        <div>
                            <div class="chat-header-title">Multi-Agent AI Customer Support Assistant</div>
                            <div class="chat-header-status"><span class="status-dot"></span>using RAG and LLMs · </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.session_state.developer_mode:
                st.markdown(
                    '<span class="dev-mode-banner">🛠️ Developer mode — intent & routing details are shown</span>',
                    unsafe_allow_html=True
                )

            # Middle, growable area: empty-state welcome hero OR the
            # scrollable message list. Its key changes depending on state
            # so the CSS can vertically center only the empty state.
            content_key = "chat_content_area_empty" if not has_messages else "chat_content_area_active"

            with st.container(key="chat_content_area"):
                with st.container(key=content_key):

                    if not has_messages:

                        st.markdown(
                            f"""
                            <div class="welcome-hero">
                                <div class="welcome-hero-icon">✨</div>
                                <div class="welcome-hero-title">How can I help you today?</div>
                                <div class="welcome-hero-subtitle">
                                    I'm your Multi-Agent AI Customer Support Assistant using RAG and LLMs.
                                    Ask me anything about billing, technical support, products, or policies.
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # ---------- QUICK ACTION BUTTONS ----------

                        row1_col1, row1_col2, row1_col3 = st.columns(3, gap="small")

                        with row1_col1:
                            if st.button(
                                "Product Info",
                                icon=":material/inventory_2:",
                                type="secondary",
                                use_container_width=True,
                                key="quick_product_btn"
                            ):
                                st.session_state.quick_prompt = "Show me your products"
                                st.rerun()

                        with row1_col2:
                            if st.button(
                                "Billing",
                                icon=":material/credit_card:",
                                type="secondary",
                                use_container_width=True,
                                key="quick_billing_btn"
                            ):
                                st.session_state.quick_prompt = "I need help with billing"
                                st.rerun()

                        with row1_col3:
                            if st.button(
                                "FAQ",
                                icon=":material/help_outline:",
                                type="secondary",
                                use_container_width=True,
                                key="quick_faq_btn"
                            ):
                                st.session_state.quick_prompt = "Show me frequently asked questions"
                                st.rerun()

                        row2_col1, row2_col2, row2_col3 = st.columns(3, gap="small")

                        with row2_col1:
                            if st.button(
                                "Technical Support",
                                icon=":material/build:",
                                type="secondary",
                                use_container_width=True,
                                key="quick_technical_btn"
                            ):
                                st.session_state.quick_prompt = "I need technical support"
                                st.rerun()

                        with row2_col2:
                            if st.button(
                                "Refund",
                                icon=":material/currency_exchange:",
                                type="secondary",
                                use_container_width=True,
                                key="quick_refund_btn"
                            ):
                                st.session_state.quick_prompt = "What is the refund policy?"
                                st.rerun()

                        with row2_col3:
                            if st.button(
                                "Contact",
                                icon=":material/support_agent:",
                                type="secondary",
                                use_container_width=True,
                                key="quick_contact_btn"
                            ):
                                st.session_state.quick_prompt = "Show me customer support contact details"
                                st.rerun()

                    else:

                        # Scrollable conversation panel — only this area scrolls
                        with st.container(border=False, key="chat_scroll_area"):
                            for message in st.session_state.messages:

                                avatar = (
                                    ":material/person:"
                                    if message["role"] == "user"
                                    else ":material/smart_toy:"
                                )

                                with st.chat_message(message["role"], avatar=avatar):
                                    st.markdown(message["content"])

            # Input row: fixed height, always glued to the bottom of the panel

                        # Footer stays inside the main panel
            st.markdown(
                """
                <div class="chat-footer">
                    <span class="copyright">
                        © 2026 TechNova Electronics
                    </span>
                    <span class="chat-footer-sep">·</span>
                    <span class="copyright">
                        support@technova.example
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # IMPORTANT:
        # Chat input is outside main_chat_panel,
        # but still inside chat_column.
        typed_prompt = st.chat_input(
            "Ask anything — billing, technical, products, or policies...",
            key="main_chat_input"
        )

        prompt = (
            typed_prompt
            or st.session_state.quick_prompt
        )

        st.session_state.quick_prompt = None

        if prompt:
            prompt = prompt.strip()
            st.session_state.quick_prompt = None
        st.session_state.quick_prompt = None

        if prompt:
            prompt = prompt.strip()

        if prompt:

            # Save user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            answer = None

            try:
                with st.spinner("AI is analyzing your request..."):
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={"message": prompt},
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        timeout=60
                    )
                    result = response.json()

            except requests.exceptions.ConnectionError:
                answer = "Backend is not running. Start the FastAPI server and try again."
            except requests.RequestException:
                answer = "Unable to connect to the backend."
            except ValueError:
                answer = "Backend returned an invalid response."

            if answer is None:
                if "reply" in result:
                    answer = result["reply"]
                else:
                    answer = result.get("message", "Unable to generate a response.")

                if not st.session_state.developer_mode:
                    filtered_lines = [
                        line
                        for line in answer.split("\n")
                        if "Detected Intent" not in line
                        and "Routed Agent" not in line
                    ]
                    answer = "\n".join(filtered_lines).strip()

            # Save assistant response
            st.session_state.messages.append({"role": "assistant", "content": answer})

            # Rerun so messages appear above the input
            st.rerun()

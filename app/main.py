import streamlit as st
from streamlit.components.v1 import html
from database import create_tables, register_user, authenticate_user, save_conversation, get_api_info, load_conversation, save_api_info
from chat import send_chat_request
import streamlit.components.v1 as components
import asyncio

# Ensure necessary tables are created
create_tables()

# Initialize session state
if 'sidebar_expanded' not in st.session_state:
    st.session_state.sidebar_expanded = True
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'menu_choice' not in st.session_state:
    st.session_state.menu_choice = "Login"  # Default menu choice when launching the app

def set_page_config():
    st.set_page_config(page_title="Chat Application", page_icon="💬", layout="wide")

def toggle_sidebar():
    st.session_state.sidebar_expanded = not st.session_state.sidebar_expanded

def render_sidebar():
    toggle_btn_label = "⬅️ Collapse" if st.session_state.sidebar_expanded else "➡️ Expand"
    st.button(toggle_btn_label, on_click=toggle_sidebar)

    menu_items = ["Register", "Login"] if not st.session_state.logged_in else ["Chat", "API Configuration", "Web SDK", "Logout"]
    choice = st.radio("Menu", menu_items, key="menu_choice")
    
    return choice

def sticky_header():
    st.markdown(
        """
        <style>
        .fixed-header {
            position: -webkit-sticky;
            position: sticky;
            top: 0;
            background-color: white;
            z-index: 1000;
            padding-top: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        </style>
        <div class='fixed-header'>
            <h1>Chat Application</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_register():
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')

    if st.button("Signup", type="primary"):
        if new_user and new_password:
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                success = register_user(new_user, new_password)
                if success:
                    st.success("You have successfully created an account")
                    st.info("Go to Login Menu to login")
                    st.experimental_rerun()
                else:
                    st.error("Username already exists.")
        else:
            st.error("Please enter both username and password.")

def render_login():
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login", type="primary"):
        if username and password:
            if authenticate_user(username, password):
                st.success(f"Welcome {username}")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.chat_history = load_conversation(username)
                st.experimental_rerun()
            else:
                st.warning("Incorrect Username/Password")
        else:
            st.error("Please enter both username and password.")

def render_api_configuration():
    st.subheader("Configure API Information")
    user_id = st.text_input("User ID")
    bot_id = st.text_input("Bot ID")
    access_token = st.text_input("Personal Access Token", type='password')

    if st.button("Save API Info", type="primary"):
        save_api_info(st.session_state.username, user_id, bot_id, access_token)
        st.success("API Information saved successfully")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.chat_history = []
    st.session_state.menu_choice = "Login"
    st.experimental_rerun()

async def send_message(username, message, chat_history, uploaded_files):
    response = await send_chat_request("123", message, chat_history, uploaded_files)
    chat_history.append({"role": "user", "message": message})
    chat_history.append({"role": "bot", "message": response.get("response", "")})
    save_conversation(username, chat_history)
    st.session_state.chat_history = chat_history
    st.session_state.bot_id = response.get("bot_id")
    st.experimental_rerun()

def render_embed_sdk():
    st.subheader("Web SDK")
    username = st.session_state.username
    api_info = get_api_info(username)
    if api_info:
        _, bot_id, _ = api_info
        
        sdk_code = f"""
        <script src="https://sf-cdn.coze.com/obj/unpkg-va/flow-platform/chat-app-sdk/0.1.0-beta.2/libs/oversea/index.js"></script>
        <link href="https://sf-cdn.coze.com/obj/unpkg-va/flow-platform/chat-app-sdk/0.1.0-beta.2/libs/oversea/style.css" rel="stylesheet">
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                console.log("DOM fully loaded and parsed. Initializing WebChatClient.");
                try {{
                    new CozeWebSDK.WebChatClient({{
                        config: {{
                            bot_id: '{bot_id}',
                        }},
                        componentProps: {{
                            title: 'Coze',
                            showIcon: true  // 确保显示图标
                        }},
                    }});
                    console.log("WebChatClient initialized successfully.");
                }} catch (error) {{
                    console.error("Failed to initialize WebChatClient:", error);
                }}
            }});
        </script>
        """
        # Using full width without specifying it directly
        components.html(sdk_code, height=600)

def render_chat():
    st.subheader("Chat")
    username = st.session_state.username
    chat_history = st.session_state.chat_history

    message = st.text_area("Enter your message:", height=150)
    uploaded_files = st.file_uploader("Choose a file (jpg, jpeg, png, pdf, docx, xlsx, csv, mp3)", accept_multiple_files=True)

    if st.button("Send", type="primary"):
        asyncio.run(send_message(username, message, chat_history, uploaded_files))

    st.write("### Chat History:")
    for entry in chat_history:
        role = "👤 User" if entry['role'] == 'user' else "🤖 Bot"
        st.markdown(f"**{role}:** {entry['message']}")
    
def main():
    set_page_config()
    sticky_header()

    col1, col2 = st.columns([1, 3])

    with col1:
        choice = render_sidebar()

    with col2:
        if choice:
            if choice == "Register" and not st.session_state.logged_in:
                render_register()
            elif choice == "Login" and not st.session_state.logged_in:
                render_login()
            elif choice == "Chat" and st.session_state.logged_in:
                render_chat()
            elif choice == "API Configuration" and st.session_state.logged_in:
                render_api_configuration()
            elif choice == "Web SDK" and st.session_state.logged_in:
                render_embed_sdk()
            elif choice == "Logout" and st.session_state.logged_in:
                logout()
        else:
            if st.session_state.logged_in:
                render_embed_sdk()  # 嵌入 SDK 放在这里，确保用户登录后嵌入
                render_chat()
            else:
                st.subheader("Please login to start chatting.")

    # CSS to adjust layout and fixed header
    st.markdown(
        """
        <style>
        .css-1aumxhk {margin: 0 20px;}  /* Adjust left margin to align content */
        .css-1v3fvcr {padding: 0;}  /* Remove padding from columns */
        .stButton > button {width: 100%;}  /* Make toggle button full width */
        .css-1aumxhk .css-1aumxhk {
            position: fixed;
            top: 0;
            bottom: 0;
            width: 200px;  /* Adjust as necessary */
            padding: 20px;
            z-index: 1000;
            background-color: white;
            border-right: 2px solid #f0f0f0;
        }
        .css-1v3fvcr .css-1ndcvqn, .css-1v3fvcr .css-1aumxhk {
            margin-left: 220px;  /* Adjust as necessary */
        }
        iframe {
            width: 100% !important;  /* Make the embedded iframe width 100% */
        }
        </style>
        """, True
    )

if __name__ == '__main__':
    main()
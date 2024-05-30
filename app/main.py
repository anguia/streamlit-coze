import streamlit as st
from database import create_tables, register_user, authenticate_user, save_conversation, load_conversation, save_api_info
from chat import send_chat_request
import asyncio

# Ensure necessary tables are created
create_tables()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def set_page_config():
    st.set_page_config(page_title="Chat Application", page_icon="💬", layout="wide")

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

def main():
    set_page_config()
    sticky_header()

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.session_state.logged_in:
            sidebar_menu = ["Chat", "API Configuration", "Logout"]
        else:
            sidebar_menu = ["Register", "Login"]
        
        choice = st.selectbox("Menu", sidebar_menu)

        if choice == "Register" and not st.session_state.logged_in:
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

        elif choice == "Login" and not st.session_state.logged_in:
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

        elif choice == "API Configuration" and st.session_state.logged_in:
            st.subheader("Configure API Information")
            user_id = st.text_input("User ID")
            bot_id = st.text_input("Bot ID")
            access_token = st.text_input("Personal Access Token", type='password')

            if st.button("Save API Info", type="primary"):
                save_api_info(st.session_state.username, user_id, bot_id, access_token)
                st.success("API Information saved successfully")

        elif choice == "Logout" and st.session_state.logged_in:
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.experimental_rerun()

    with col2:
        if st.session_state.logged_in:
            st.subheader("Chat")
            username = st.session_state.username
            chat_history = st.session_state.chat_history

            message = st.text_area("Enter your message:", height=150)
            uploaded_files = st.file_uploader("Choose a file (jpg, jpeg, png, pdf, docx, xlsx, csv, mp3)", accept_multiple_files=True)

            if st.button("Send", type="primary"):
                response = asyncio.run(send_chat_request("123", message, chat_history, uploaded_files))
                
                chat_history.append({"role": "user", "message": message})
                chat_history.append({"role": "bot", "message": response.get("response", "")})
                
                save_conversation(username, chat_history)
                st.session_state.chat_history = chat_history
                st.experimental_rerun()

            st.write("### Chat History:")
            for entry in chat_history:
                role = "👤 User" if entry['role'] == 'user' else "🤖 Bot"
                st.markdown(f"**{role}:** {entry['message']}")

        else:
            st.subheader("Please login to start chatting.")

if __name__ == '__main__':
    main()
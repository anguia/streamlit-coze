import streamlit as st
from database import create_tables, register_user, authenticate_user, save_conversation, load_conversation, save_api_info
from chat import send_chat_request

# Ensure necessary tables are created
create_tables()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

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
            st.experimental_rerun()

    with col2:
        if st.session_state.logged_in:
            st.subheader("Chat")
            username = st.session_state.username
            conversation_id = "123"  # For demo purposes, this should be dynamically generated
            chat_history = load_conversation(username)

            message = st.text_area("Enter your message:", height=150)

            if st.button("Send", type="primary"):
                response = send_chat_request(conversation_id, message, chat_history)
                
                chat_history.append({"user": username, "message": message})
                chat_history.append({"bot": "Bot", "message": response.get("response", "")})
                
                save_conversation(username, chat_history)

                st.write("### Chat History:")
                st.write("")
                for entry in chat_history:
                    role = "👤 User" if 'user' in entry else "🤖 Bot"
                    st.markdown(f"**{role}:** {entry['message']}")

                st.write("### Latest conversation saved in database:")
                saved_conversation = load_conversation(username)
                for entry in saved_conversation:
                    role = "👤 User" if 'user' in entry else "🤖 Bot"
                    st.markdown(f"**{role}:** {entry['message']}")
        else:
            st.subheader("Please login to start chatting.")

if __name__ == '__main__':
    main()
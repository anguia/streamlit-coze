import streamlit as st
import requests
import json

# 设置 Streamlit 页面标题和布局
st.set_page_config(page_title="Coze Chatbot", layout="wide", initial_sidebar_state="expanded")

# Streamlit 页面标题
st.title("Coze Chatbot")

# 配置个人访问令牌、机器人 ID 和用户 ID
st.sidebar.header("配置")
personal_access_token = st.sidebar.text_input("Personal Access Token", type="password")
bot_id = st.sidebar.text_input("Bot ID")
user_id = st.sidebar.text_input("User ID")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = "123"

# 显示聊天历史
def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

display_messages()

# 输入框用于用户输入
prompt = st.text_input("请输入您的问题：")

if st.button("发送"):
    if prompt and personal_access_token and bot_id and user_id:
        # 记录用户输入
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用 Coze API 获取回答
        headers = {
            "Authorization": f"Bearer {personal_access_token}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.com",
            "Connection": "keep-alive"
        }
        payload = {
            "conversation_id": st.session_state.conversation_id,
            "bot_id": bot_id,
            "user": user_id,
            "query": prompt,
            "stream": False
        }
        response = requests.post("https://api.coze.com/open_api/v2/chat", headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            data = response.json()
            for message in data["messages"]:
                if message["role"] == "assistant":
                    st.session_state.messages.append({"role": "assistant", "content": message["content"]})
                    with st.chat_message("assistant"):
                        st.markdown(message["content"])
        else:
            st.error("请求失败，请检查配置信息。")
        
        # 显示更新后的消息
        display_messages()
    else:
        st.warning("请确保所有配置项和输入框均已填写。")


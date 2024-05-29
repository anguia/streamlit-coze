import requests
from database import get_api_info
import streamlit as st
import json

COZE_API_URL = 'https://api.coze.com/open_api/v2/chat'

def send_chat_request(conversation_id, query, chat_history, stream=True):
    username = st.session_state.username  # 从会话状态中获取当前用户名
    api_info = get_api_info(username)

    if not api_info:
        raise ValueError("API info not found in database.")

    user_id, bot_id, access_token = api_info

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'api.coze.com',
        'Connection': 'keep-alive'
    }

    payload = {
        "conversation_id": conversation_id,
        "bot_id": bot_id,
        "user": user_id,
        "query": query,
        "chat_history": chat_history,
        "stream": stream
    }

    response = requests.post(COZE_API_URL, headers=headers, json=payload, stream=True)

    if response.status_code == 200:
        responses = []
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith("data:"):
                    try:
                        event_data = json.loads(line_str[5:])
                        if event_data.get('event') == 'message':
                            msg = event_data['message']['content']
                            responses.append(msg)
                        elif event_data.get('event') == 'done':
                            break
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing JSON: {e}")
                        st.write("Line content:", line_str)
                        continue
        combined_responses = " ".join(responses)
        return {"response": combined_responses}
    else:
        print(f"Failed to send request: {response.status_code} - {response.text}")
        response.raise_for_status()
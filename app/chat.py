import aiohttp
import json
import streamlit as st
from database import get_api_info

COZE_API_URL = 'https://api.coze.com/open_api/v2/chat'

async def send_chat_request(conversation_id, query, chat_history, uploaded_files, stream=True):
    username = st.session_state.username  # 从会话状态中获取当前用户名
    api_info = get_api_info(username)

    if not api_info:
        raise ValueError("API info not found in database.")

    user_id, bot_id, access_token = api_info

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': '*/*',
        'Host': 'api.coze.com',
        'Connection': 'keep-alive'
    }

    data = aiohttp.FormData()

    data.add_field('conversation_id', conversation_id)
    data.add_field('bot_id', bot_id)
    data.add_field('user', user_id)
    data.add_field('query', query)
    data.add_field('chat_history', json.dumps(chat_history))
    data.add_field('stream', str(stream))

    if uploaded_files:
        for file in uploaded_files:
            data.add_field('files', file, filename=file.name, content_type=file.type)

    async with aiohttp.ClientSession() as session:
        async with session.post(COZE_API_URL, headers=headers, data=data) as response:
            if response.status == 200:
                responses = []
                async for line in response.content:
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
                combined_responses = " ".join(responses)
                return {"response": combined_responses}
            else:
                st.error(f"Failed to send request: {response.status} - {await response.text()}")
                response.raise_for_status()
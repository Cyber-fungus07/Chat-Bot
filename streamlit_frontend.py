import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display chat history
for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.text(msg['message'])

text_input = st.chat_input("Type here")

if text_input:
    # Store user message
    st.session_state['message_history'].append({
        'role': "user",
        'message': text_input
    })

    with st.chat_message('user'):
        st.text(text_input)

    # Call chatbot

    # Store assistant response

    with st.chat_message('assistant'):

        def stream_generator():
            for message_chunk, metadata in chatbot.stream(
                    {'messages': [HumanMessage(content=text_input)]},
                    config=CONFIG,
                    stream_mode='messages'
            ):
                if message_chunk.content:
                    yield message_chunk.content

        ai_message = st.write_stream(stream_generator())

    # AFTER streaming finishes
    st.session_state['message_history'].append({
        'role': 'assistant',
        'message': ai_message
    })
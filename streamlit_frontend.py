import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot
import uuid

#Utility Functions
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

#Session
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = []

add_thread(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#sidebar UI
st.sidebar.title('ChitChat-Bot')

if st.sidebar.button("New Chat", key="new_chat_btn"):
    reset_chat()


st.sidebar.text("My Conversation")
for thread_id in st.session_state['chat_thread']:
    st.sidebar.button(thread_id)
# st.sidebar.text(st.session_state['thread_id'])

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
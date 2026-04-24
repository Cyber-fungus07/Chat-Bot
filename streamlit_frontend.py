import streamlit as st
from langchain_core.messages import HumanMessage
from backend import chatbot
import uuid

#Utility Functions
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def load_conversation(thread_id):
    state = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )
    messages = state.values.get('messages', [])

    temp_msg = []
    for message in messages:
        role = 'user' if isinstance(message, HumanMessage) else 'assistant'
        temp_msg.append({
            'role': role,
            'content': message.content
        })

    return temp_msg

#Title Generator
def generate_title(user_message: str):
    return user_message[:30]

#Session
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = []

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}
add_thread(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#sidebar UI
st.sidebar.title('ChitChat-Bot')

if st.sidebar.button("New Chat", key="new_chat_btn"):
    reset_chat()

st.sidebar.text("My Conversations")

for thread_id in st.session_state['chat_thread'][::-1]:
    title = st.session_state['thread_titles'].get(thread_id,'Conversation')

    if st.sidebar.button(title, key=f"thread_{thread_id}"):
        st.session_state['thread_id'] = thread_id
        st.session_state['message_history'] = load_conversation(thread_id)

# display chat
for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

#input
text_input = st.chat_input("Type here...")

if text_input:
    thread_id = st.session_state['thread_id']

    #Generate the Title only One time
    if thread_id not in st.session_state['thread_titles']:
        st.session_state['thread_titles'][thread_id] = generate_title(text_input)

    # Store user message
    st.session_state['message_history'].append({
        'role': "user",
        'content': text_input
    })

    with st.chat_message('user'):
        st.write(text_input)

    # Streaming
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

    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message
    })
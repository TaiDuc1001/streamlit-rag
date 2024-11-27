import streamlit as st
import requests
import json


backend_url = "https://48bf-35-221-144-231.ngrok-free.app"
chat_url = f"{backend_url}/chatbot/chat/"
upload_url = f"{backend_url}/chatbot/upload/"

# Initialize chat history (same as before)
if "chats" not in st.session_state:
    st.session_state.chats = []
    st.session_state.chats.append({"id": 0, "messages": []})
if "active_chat" not in st.session_state:
    st.session_state.active_chat = 0

# Sidebar for chat selection (same as before)
st.sidebar.title("Chat History")

# New chat button (same as before)
if st.sidebar.button("New Chat"):
    new_chat_id = len(st.session_state.chats)
    st.session_state.chats.append({"id": new_chat_id, "messages": []})
    st.session_state.active_chat = new_chat_id

# Display chat list (same as before)
for i, chat in enumerate(st.session_state.chats):
    if st.sidebar.button(f"Chat {chat['id'] + 1}", key=f"chat_{i}"):
        st.session_state.active_chat = i

# --- Manager Features ---
st.sidebar.title("Manager Functions")
uploaded_file = st.sidebar.file_uploader("Upload Document", type=["txt", "pdf", "docx"])
if uploaded_file is not None:
    # Process the uploaded file
    files = {"file": uploaded_file}
    response = requests.post(upload_url, files=files)
    if response.status_code == 200:
        st.sidebar.success("Document uploaded successfully!")
    else:
        st.sidebar.error(f"Error uploading document: {response.status_code} - {response.text}")

# --- Chat Interface --- (same as before)
st.title("Chatbot Service")

# Display active chat history
for message in st.session_state.chats[st.session_state.active_chat]["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("What is up?")
if prompt:
    # Add user message to active chat history
    st.session_state.chats[st.session_state.active_chat]["messages"].append({"role": "user", "content": prompt})
    # Display user message in the chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Convert the message into JSON format
    params = {"message": prompt}

    # Send the JSON in the body of the GET request
    response = requests.get(
        backend_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(params)
    )

    if response.status_code == 200:
        try:
            # Ensure the response is valid JSON and extract the answer
            answer = response.json().get("Answer")
            if answer is not None:
                # Add assistant message to active chat history
                st.session_state.chats[st.session_state.active_chat]["messages"].append({"role": "assistant", "content": answer})
                # Display assistant response in the chat
                with st.chat_message("assistant"):
                    st.markdown(answer)
            else:
                st.error("Error: No answer in response.")
        except json.JSONDecodeError:
            st.error("Error: Response is not valid JSON.")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
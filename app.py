import streamlit as st
import pandas as pd
import PyPDF2
import json
import google.generativeai as genai

# Configure Gemini AI
genai.configure(api_key="AIzaSyC6rcStK7vdwoloB65UqppIWbb2L-Zf_Ik")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_content" not in st.session_state:
    st.session_state.file_content = None
if "previous_file_type" not in st.session_state:
    st.session_state.previous_file_type = None

def process_file(file, file_type):
    """Process different file types and return their content as text"""
    try:
        if file_type == "CSV":
            df = pd.read_csv(file)
            return df.to_string()
        
        elif file_type == "PDF":
            pdf_reader = PyPDF2.PdfReader(file)
            return ' '.join(page.extract_text() for page in pdf_reader.pages)
        
        elif file_type == "JSON":
            return json.dumps(json.load(file), indent=2)
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def reset_chat_state():
    """Reset chat history and file content"""
    st.session_state.chat_history = []
    st.session_state.file_content = None

st.title("Multi-File based Chatbot")

st.sidebar.header("Upload File")
file_type = st.sidebar.radio("Choose a file type", ["CSV", "PDF", "JSON"])

if st.session_state.previous_file_type is not None and st.session_state.previous_file_type != file_type:
    reset_chat_state()

# Update the previous file type
st.session_state.previous_file_type = file_type

uploaded_file = st.sidebar.file_uploader(f"Upload a {file_type} file", type=file_type.lower())

# Process uploaded file
if uploaded_file and st.session_state.file_content is None:
    with st.spinner("Processing file..."):
        file_content = process_file(uploaded_file, file_type)
        if file_content:
            st.session_state.file_content = file_content
            st.success("File processed successfully!")
            
            # Initialize chat with context
            initial_prompt = f"Here is the content of the uploaded file. Use this as context for answering questions: {file_content}"
            response = model.start_chat().send_message(initial_prompt)
            st.session_state.chat_history.append(("assistant", "I've read the file content. How can I help you?"))

# Display chat history
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(message)

# Chat input
if user_input := st.chat_input("Ask a question about your file"):
    if st.session_state.file_content is None:
        st.warning("Please upload a file first!")
    else:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.chat_history.append(("user", user_input))
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat = model.start_chat()
                context_prompt = f"Context: {st.session_state.file_content}\nQuestion: {user_input}"
                response = chat.send_message(context_prompt)
                st.write(response.text)
                st.session_state.chat_history.append(("assistant", response.text))
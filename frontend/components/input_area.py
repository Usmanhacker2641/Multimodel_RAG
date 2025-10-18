import streamlit as st

def render_input_area():
    """Renders the combined query and file upload area."""
    st.subheader("Upload Document or Enter Query")
    
    col1, col2 = st.columns([7, 3])

    with col1:
        query = st.text_input("Enter your question or paste a URL...", key="query_input", placeholder="Enter your question or paste a URL...")
        st.button("Send", key="primary")

    with col2:
        st.file_uploader(
            "File Upload",
            type=['pdf', 'docx', 'txt', 'csv', 'png', 'jpg'],
            label_visibility="collapsed"
        )
        st.caption("Drop files or click to upload")

import streamlit as st
import tempfile
import os
from model import AccentClassifier  # Your existing model!
# No need to rewrite model.py - we reuse it!

st.title("🎤 English Accent Detection Tool")

# Use your existing AccentClassifier class
@st.cache_resource
def load_model():
    return AccentClassifier()  # Your existing code!

classifier = load_model()

# File upload
uploaded_file = st.file_uploader("Upload audio/video file", type=['mp4', 'wav', 'mp3'])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    # Use your existing processing function!
    result = classifier.process_video_input(tmp_path)
    
    if result:
        assessment = classifier.generate_hiring_assessment(result)
        
        # Display results
        st.success(f"Accent: {assessment['accent']}")
        st.metric("Confidence", f"{assessment['confidence_percent']:.1f}%")
        st.info(assessment['recommendation'])
    
    os.unlink(tmp_path)

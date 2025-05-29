
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from model import AccentClassifier
from architecture import create_app_directories, allowed_file
import json
import time

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create necessary directories
create_app_directories()

# Initialize the accent classifier
classifier = AccentClassifier()

@app.route('/')
def index():
    """Main page with upload form and URL input."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_accent():
    """Process uploaded file or URL and return accent analysis."""
    try:
        analysis_id = str(uuid.uuid4())
        
        # Check if it's a file upload or URL
        if 'file' in request.files and request.files['file'].filename != '':
            # Handle file upload
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{analysis_id}_{filename}")
                file.save(file_path)
                
                # Process the file
                result = classifier.process_video_input(file_path)
                
        elif 'video_url' in request.form and request.form['video_url'].strip():
            # Handle URL input
            video_url = request.form['video_url'].strip()
            result = classifier.process_video_input(video_url)
            
        else:
            return jsonify({'error': 'No file or URL provided'}), 400
        
        if result:
            # Generate hiring assessment
            assessment = classifier.generate_hiring_assessment(result)
            
            # Prepare response data
            response_data = {
                'success': True,
                'analysis_id': analysis_id,
                'accent': result['accent'],
                'confidence': result['confidence'],
                'assessment': assessment,
                'audio_duration': result['duration'],
                'timestamp': time.time()
            }
            
            return jsonify(response_data)
        else:
            return jsonify({'error': 'Failed to process audio/video'}), 500
            
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': classifier.is_loaded(),
        'timestamp': time.time()
    })

@app.route('/results/<analysis_id>')
def view_results(analysis_id):
    """View detailed results page."""
    # In production, you'd fetch this from a database
    return render_template('results.html', analysis_id=analysis_id)

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error occurred.'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
# Add Streamlit interface at the bottom
if __name__ == "__main__" and "streamlit" in __file__:
    # Streamlit interface code here
    import streamlit as st
    # Your Streamlit UI code
else:
    # Original Flask code
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)

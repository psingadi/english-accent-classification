import os
from pathlib import Path

def create_app_directories():
    """Create necessary application directories."""
    directories = [
        'uploads',
        'static',
        'static/css',
        'static/js',
        'templates',
        '__pycache__'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    ALLOWED_EXTENSIONS = {
        'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv',  # Video
        'wav', 'mp3', 'm4a', 'flac', 'aac', 'ogg'   # Audio
    }
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(file_path):
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

def format_duration(seconds):
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def validate_url(url):
    """Basic URL validation."""
    return url.startswith(('http://', 'https://')) and len(url) > 10
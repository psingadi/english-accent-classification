
class AccentDetectionApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentFile = null;
    }

    initializeElements() {
        // Tab elements
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        
        // Form elements
        this.fileForm = document.getElementById('file-form');
        this.urlForm = document.getElementById('url-form');
        this.fileInput = document.getElementById('file-input');
        this.fileDropZone = document.getElementById('file-drop-zone');
        this.videoUrlInput = document.getElementById('video-url');
        
        // UI sections
        this.loadingSection = document.getElementById('loading-section');
        this.resultsSection = document.getElementById('results-section');
        this.errorSection = document.getElementById('error-section');
        
        // Result elements
        this.accentResult = document.getElementById('accent-result');
        this.confidenceScore = document.getElementById('confidence-score');
        this.confidenceFill = document.getElementById('confidence-fill');
        this.predictionsList = document.getElementById('predictions-list');
    }

    bindEvents() {
        // Tab switching
        this.tabButtons.forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // File upload events
        this.fileDropZone.addEventListener('click', () => this.fileInput.click());
        this.fileDropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.fileDropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.fileDropZone.addEventListener('drop', (e) => this.handleFileDrop(e));
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Form submissions
        this.fileForm.addEventListener('submit', (e) => this.handleFileSubmit(e));
        this.urlForm.addEventListener('submit', (e) => this.handleUrlSubmit(e));
    }

    switchTab(tabId) {
        // Update tab buttons
        this.tabButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // Update tab content
        this.tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
    }

    handleDragOver(e) {
        e.preventDefault();
        this.fileDropZone.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.fileDropZone.classList.remove('dragover');
    }

    handleFileDrop(e) {
        e.preventDefault();
        this.fileDropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.fileInput.files = files;
            this.handleFileSelect({ target: { files } });
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.currentFile = file;
            this.displayFileInfo(file);
        }
    }

    displayFileInfo(file) {
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');
        const fileInfo = document.getElementById('file-info');

        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileInfo.style.display = 'block';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async handleFileSubmit(e) {
        e.preventDefault();
        
        if (!this.currentFile) {
            this.showError('Please select a file first');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.currentFile);

        await this.submitAnalysis(formData);
    }

    async handleUrlSubmit(e) {
        e.preventDefault();
        
        const url = this.videoUrlInput.value.trim();
        if (!url) {
            this.showError('Please enter a valid URL');
            return;
        }

        const formData = new FormData();
        formData.append('video_url', url);

        await this.submitAnalysis(formData);
    }

    async submitAnalysis(formData) {
        try {
            this.showLoading();
            
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.displayResults(result);
            } else {
                this.showError(result.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Network error. Please try again.');
        }
    }

    showLoading() {
        this.hideAllSections();
        this.loadingSection.style.display = 'block';
        
        // Update loading messages
        const messages = [
            'Downloading and extracting audio...',
            'Converting audio format...',
            'Running accent classification...',
            'Generating assessment report...'
        ];
        
        let messageIndex = 0;
        const messageElement = document.getElementById('loading-message');
        
        const messageInterval = setInterval(() => {
            if (messageIndex < messages.length) {
                messageElement.textContent = messages[messageIndex];
                messageIndex++;
            } else {
                clearInterval(messageInterval);
            }
        }, 2000);
    }

    displayResults(data) {
        this.hideAllSections();
        this.resultsSection.style.display = 'block';

        const assessment = data.assessment;
        
        // Update main results
        this.accentResult.textContent = assessment.accent;
        this.confidenceScore.textContent = `Confidence: ${assessment.confidence_percent.toFixed(1)}%`;
        
        // Update confidence bar
        this.confidenceFill.style.width = `${assessment.confidence_percent}%`;
        this.confidenceFill.className = `confidence-fill ${this.getConfidenceClass(assessment.confidence_percent)}`;

        // Update assessment details
        document.getElementById('accent-display').textContent = assessment.accent;
        document.getElementById('accent-description').textContent = assessment.recommendation;
        document.getElementById('native-status').textContent = assessment.is_native_english ? 'Yes' : 'No';
        document.getElementById('audio-duration').textContent = this.formatDuration(assessment.duration);
        document.getElementById('duration-quality').textContent = assessment.audio_quality;
        document.getElementById('automation-status').textContent = assessment.suitable_for_automation ? 'Yes' : 'No';
        document.getElementById('automation-description').textContent = assessment.recommendation;

        // Update hiring recommendation
        const recommendationElement = document.getElementById('hiring-recommendation');
        recommendationElement.className = `alert alert-${assessment.color_class}`;
        document.getElementById('recommendation-text').textContent = assessment.recommendation;

        // Update top predictions
        this.displayTopPredictions(assessment.top_predictions || []);
    }

    displayTopPredictions(predictions) {
        const container = this.predictionsList;
        container.innerHTML = '';

        if (predictions.length === 0) {
            container.innerHTML = '<p>No detailed predictions available</p>';
            return;
        }

        predictions.forEach((pred, index) => {
            const predItem = document.createElement('div');
            predItem.className = 'prediction-item';
            
            predItem.innerHTML = `
                <span class="prediction-name">${index + 1}. ${pred.accent.toUpperCase()}</span>
                <span class="prediction-confidence">${(pred.confidence * 100).toFixed(1)}%</span>
            `;
            
            container.appendChild(predItem);
        });
    }

    getConfidenceClass(confidence) {
        if (confidence >= 80) return 'high';
        if (confidence >= 60) return 'medium';
        return 'low';
    }

    formatDuration(seconds) {
        if (seconds < 60) {
            return `${seconds.toFixed(1)} seconds`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${minutes}m ${secs}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    }

    showError(message) {
        this.hideAllSections();
        document.getElementById('error-message').textContent = message;
        this.errorSection.style.display = 'block';
    }

    hideAllSections() {
        this.loadingSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
    }
}

// Global functions
function resetForm() {
    location.reload();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AccentDetectionApp();
});

// Health check function
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();
        console.log('App health:', health);
        return health;
    } catch (error) {
        console.error('Health check failed:', error);
        return null;
    }
}

// Auto health check on load
checkHealth();

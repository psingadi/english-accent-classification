import torch
import torchaudio
import librosa
import numpy as np
import os
import uuid
import subprocess
import requests
from speechbrain.pretrained.interfaces import foreign_class
from typing import Dict, Optional, Any
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccentClassifier:
    """
    Accent classification model wrapper for the CommonAccent pretrained model.
    """
    
    def __init__(self):
        self.classifier = None
        self.accent_labels = [
            'us', 'england', 'australia', 'indian', 'canada', 'bermuda',
            'scotland', 'african', 'ireland', 'newzealand', 'wales', 
            'malaysia', 'philippines', 'singapore', 'hongkong', 'southatlantic'
        ]
        
        self.accent_mapping = {
            'us': 'American', 'england': 'British', 'australia': 'Australian',
            'canada': 'Canadian', 'indian': 'Indian', 'scotland': 'Scottish',
            'ireland': 'Irish', 'wales': 'Welsh', 'african': 'South African',
            'newzealand': 'New Zealand', 'malaysia': 'Malaysian',
            'philippines': 'Filipino', 'singapore': 'Singaporean',
            'hongkong': 'Hong Kong', 'bermuda': 'Bermudian',
            'southatlantic': 'South Atlantic'
        }
        
        self._load_model()
    
    def _load_model(self):
        """Load the CommonAccent pretrained model."""
        try:
            logger.info("Loading CommonAccent model...")
            self.classifier = foreign_class(
                source="Jzuluaga/accent-id-commonaccent_xlsr-en-english", 
                pymodule_file="custom_interface.py", 
                classname="CustomEncoderWav2vec2Classifier",
                run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
            )
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is properly loaded."""
        return self.classifier is not None
    
    def convert_to_16khz_mono(self, input_path: str, output_path: str = None) -> str:
        """Convert audio to 16kHz mono format."""
        if output_path is None:
            output_path = input_path.replace('.', '_processed.')
        
        try:
            audio, sr = librosa.load(input_path, sr=16000, mono=True)
            torchaudio.save(output_path, torch.tensor(audio).unsqueeze(0), 16000)
            return output_path
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise

    
    
    def download_and_extract_audio(self, url: str) -> str:
        """Download video from URL and extract audio."""
        try:
            if not isinstance(url, str):
                url = str(url)
            # Generate unique filename
            temp_id = str(uuid.uuid4())[:8]
            output_pattern = f"temp_video_{temp_id}.%(ext)s"
            
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'wav',
                '--audio-quality', '0',
                '--output', output_pattern,
                '--no-check-certificate',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; 64) AppleWebKit/537.36',
                '--referer', 'https://www.youtube.com/',
                '--retries', '3',
                url
            ]

            if 'youtube.com' in url:
                cmd.extend([
                    '--extractor-args', 'youtube:skip=dash,hls',
                    '--format', 'best[height<=720]',
                ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find the extracted audio file
            for file in os.listdir('.'):
                if file.startswith(f'temp_video_{temp_id}') and file.endswith('.wav'):
                    return file
            
            # Convert if needed
            for file in os.listdir('.'):
                if file.startswith(f'temp_video_{temp_id}'):
                    wav_path = f"temp_audio_{temp_id}.wav"
                    return self.convert_to_16khz_mono(file, wav_path)
            
            raise FileNotFoundError("No audio file found after download")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Video download failed: {e.stderr}")

            raise Exception(f"Video donload failed: {e.stderr}")

        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            raise
    
    def process_local_file(self, file_path: str) -> str:
        """Process local audio/video file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if it's already an audio file
        if file_path.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
            # Convert to required format
            return self.convert_to_16khz_mono(file_path)
        else:
            # Extract audio from video
            temp_id = str(uuid.uuid4())[:8]
            audio_path = f"temp_extracted_{temp_id}.wav"
            
            ffmpeg_cmd = [
                'ffmpeg', '-i', file_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                audio_path
            ]
            
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            return audio_path
    
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio file and return accent classification results."""
        try:

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Load audio properties
            audio, sr = librosa.load(audio_path, sr=None)
            duration = len(audio) / sr
            
            # Ensure correct format
            if sr != 16000:
                audio_path = self.convert_to_16khz_mono(audio_path)
            
            # Run classification
            out_prob, score, index, text_lab = self.classifier.classify_file(audio_path)
            
            # Process probabilities
            if torch.is_tensor(out_prob):
                probs = out_prob.detach().cpu().numpy()
            elif hasattr(out_prob, 'cpu'):
                probs = out_prob.cpu().numpy()
            elif hasattr(out_prob, 'numpy'):
                probs = out_prob.numpy()
            else:
                probs = out_prob

            #Convert score if in tensor
            if torch.is_tensor(score):
                score = score.detach().cpu().item()
            if torch.is_tensor(index):
                index = index.detach().cpu().item()

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Get top predictions
            top_predictions = []
            if hasattr(probs, 'shape') and len(probs.flatten()) > 1:
                probs_flat = probs.flatten()
                sorted_indices = np.argsort(probs_flat)[::-1]
                
                for i in range(min(5, len(sorted_indices))):
                    idx = sorted_indices[i]
                    if idx < len(self.accent_labels):
                        top_predictions.append({
                            'accent': self.accent_labels[idx],
                            'confidence': float(probs_flat[idx])
                        })
            
            result = {
                'accent': text_lab,
                'confidence': float(score),
                'index': int(index),
                'duration': duration,
                'top_predictions': top_predictions,
                'audio_path': audio_path
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            raise
    
    def process_video_input(self, input_source: str) -> Optional[Dict[str, Any]]:
        """Main processing function for video URLs or file paths."""
        try:
            logger.info(f"Processing input: {input_source}")
            
            # Determine input type
            is_url = input_source.startswith(('http://', 'https://'))
            
            if is_url:
                audio_path = self.download_and_extract_audio(input_source)
            else:
                audio_path = self.process_local_file(input_source)
            
            # Analyze the audio
            result = self.analyze_audio(audio_path)
            
            # Cleanup temporary files
            self._cleanup_temp_files()
            
            return result
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self._cleanup_temp_files()
            return None
    
    def generate_hiring_assessment(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hiring-focused assessment from analysis results."""
        if not result:
            return None

        accent_raw = result['accent']

        if isinstance(accent_raw, list):
            accent_code = accent_raw[0] if accent_raw else 'unknown'
        elif isinstance(accent_raw, str):
            accent_code = accent_raw
        else:
            accent_code = str(accent_raw)

        accent_code = accent_code.lower().strip()
        
        accent_display = self.accent_mapping.get(accent_code, accent_code.title())
        confidence_percent = result['confidence'] * 100
        duration = result['duration']
        
        # Determine reliability
        if confidence_percent >= 80:
            reliability = "High"
            recommendation = "Reliable classification - suitable for automated screening"
            color = "success"
        elif confidence_percent >= 60:
            reliability = "Medium"
            recommendation = "Moderately reliable - consider additional assessment"
            color = "warning"
        else:
            reliability = "Low"
            recommendation = "Low confidence - manual review recommended"
            color = "danger"
        
        # Check native English
        native_english_accents = ['us', 'england', 'australia', 'canada', 
                                 'scotland', 'ireland', 'wales', 'newzealand']
        is_native = result['accent'] in native_english_accents
        
        # Audio quality assessment
        if duration < 10:
            audio_quality = "Short sample - may affect reliability"
        elif duration > 300:
            audio_quality = "Very long sample - consider using excerpt"
        else:
            audio_quality = "Good sample length"
        
        assessment = {
            'accent': accent_display,
            'accent_code': result['accent'],
            'confidence_percent': confidence_percent,
            'reliability': reliability,
            'recommendation': recommendation,
            'is_native_english': is_native,
            'duration': duration,
            'audio_quality': audio_quality,
            'suitable_for_automation': confidence_percent >= 70,
            'color_class': color,
            'top_predictions': result.get('top_predictions', [])
        }
        
        return assessment
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            for file in os.listdir('.'):
                if file.startswith(('temp_', 'downloaded_', 'extracted_')):
                    os.remove(file)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
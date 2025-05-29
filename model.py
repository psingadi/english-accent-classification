import random
import time
from typing import Dict, Optional, Any

class AccentClassifier:
    """
    Accent classification model - demo version for deployment.
    """
    
    def __init__(self):
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
        
        print("✅ AccentClassifier initialized (demo mode)")
    
    def process_video_input(self, input_source: str) -> Optional[Dict[str, Any]]:
        """Process video/audio file and return accent analysis."""
        
        # Simulate processing time
        time.sleep(2)
        
        # Generate realistic demo results
        accent_code = random.choice(self.accent_labels)
        confidence = random.uniform(0.75, 0.95)
        duration = random.uniform(15, 180)
        
        # Generate top predictions
        top_predictions = []
        other_accents = [a for a in self.accent_labels if a != accent_code]
        random.shuffle(other_accents)
        
        # Main prediction
        top_predictions.append({
            'accent': accent_code,
            'confidence': confidence
        })
        
        # Secondary predictions
        remaining = 1.0 - confidence
        second_conf = random.uniform(0.03, remaining * 0.6)
        third_conf = random.uniform(0.01, remaining * 0.3)
        
        top_predictions.append({
            'accent': other_accents[0],
            'confidence': second_conf
        })
        
        top_predictions.append({
            'accent': other_accents[1],
            'confidence': third_conf
        })
        
        result = {
            'accent': accent_code,
            'confidence': confidence,
            'duration': duration,
            'top_predictions': top_predictions,
            'audio_path': input_source
        }
        
        return result
    
    def generate_hiring_assessment(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hiring assessment from analysis results."""
        
        accent_code = result['accent']
        accent_display = self.accent_mapping.get(accent_code, accent_code.title())
        confidence_percent = result['confidence'] * 100
        duration = result['duration']
        
        # Determine reliability
        if confidence_percent >= 85:
            reliability = "High"
            recommendation = "Excellent classification - suitable for automated screening"
            color_class = "success"
        elif confidence_percent >= 70:
            reliability = "Medium" 
            recommendation = "Good classification - consider additional assessment"
            color_class = "warning"
        else:
            reliability = "Low"
            recommendation = "Lower confidence - manual review recommended"
            color_class = "danger"
        
        # Check native English
        native_english_accents = ['us', 'england', 'australia', 'canada', 
                                 'scotland', 'ireland', 'wales', 'newzealand']
        is_native = accent_code in native_english_accents
        
        # Audio quality assessment
        if duration < 15:
            audio_quality = "Short sample - may affect reliability"
        elif duration > 300:
            audio_quality = "Long sample - consider using excerpt"
        else:
            audio_quality = "Good sample length"
        
        assessment = {
            'accent': accent_display,
            'accent_code': accent_code,
            'confidence_percent': confidence_percent,
            'reliability': reliability,
            'recommendation': recommendation,
            'is_native_english': is_native,
            'duration': duration,
            'audio_quality': audio_quality,
            'suitable_for_automation': confidence_percent >= 75,
            'color_class': color_class,
            'top_predictions': result.get('top_predictions', [])
        }
        
        return assessment

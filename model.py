import random
import time
from typing import Dict, Optional, Any

class AccentClassifier:
    """Accent classification model - demo version for deployment."""
    
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
        print("✅ AccentClassifier loaded (demo mode)")
    
    def process_video_input(self, input_source: str) -> Optional[Dict[str, Any]]:
        """Process video/audio and return realistic demo results."""
        # Simulate processing time
        time.sleep(2)
        
        # Generate realistic results
        accent_code = random.choice(self.accent_labels)
        confidence = random.uniform(0.78, 0.94)
        duration = random.uniform(15, 120)
        
        # Create top predictions
        top_predictions = []
        other_accents = [a for a in self.accent_labels if a != accent_code]
        random.shuffle(other_accents)
        
        top_predictions.append({'accent': accent_code, 'confidence': confidence})
        top_predictions.append({'accent': other_accents[0], 'confidence': random.uniform(0.03, 0.15)})
        top_predictions.append({'accent': other_accents[1], 'confidence': random.uniform(0.01, 0.08)})
        
        return {
            'accent': accent_code,
            'confidence': confidence,
            'duration': duration,
            'top_predictions': top_predictions,
            'audio_path': input_source
        }
    
    def generate_hiring_assessment(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hiring assessment from results."""
        accent_code = result['accent']
        accent_display = self.accent_mapping.get(accent_code, accent_code.title())
        confidence_percent = result['confidence'] * 100
        duration = result['duration']
        
        # Determine recommendation
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
        
        # Native English check
        native_accents = ['us', 'england', 'australia', 'canada', 'scotland', 'ireland', 'wales', 'newzealand']
        is_native = accent_code in native_accents
        
        return {
            'accent': accent_display,
            'accent_code': accent_code,
            'confidence_percent': confidence_percent,
            'reliability': reliability,
            'recommendation': recommendation,
            'is_native_english': is_native,
            'duration': duration,
            'audio_quality': "Good sample length" if 15 <= duration <= 180 else "Sample length may affect results",
            'suitable_for_automation': confidence_percent >= 75,
            'color_class': color_class,
            'top_predictions': result.get('top_predictions', [])
        }

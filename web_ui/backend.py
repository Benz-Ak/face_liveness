"""
Flask backend for Face Liveness Detection Web UI
Integrates with the existing LivenessPipeline
"""

import base64
import cv2
import numpy as np
import time
from io import BytesIO
from pathlib import Path
from PIL import Image
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Import the existing pipeline
from src.pipeline import LivenessPipeline

# ============================================
# Flask App Setup
# ============================================

app = Flask(__name__, 
            static_url_path='/static',
            static_folder='.',
            template_folder='.')
CORS(app)

# ============================================
# Configuration
# ============================================

CONFIG = {
    'v1': {
        'weights': 'models/best_checkpoint.pth',
        'description': 'V1 – NUAA only'
    },
    'v2': {
        'weights': 'models/best_checkpoint_v2.pth',
        'description': 'V2 – NUAA + LCC FASD'
    }
}

# ============================================
# Pipeline Cache
# ============================================

pipelines = {}

def get_pipeline(model_id, threshold):
    """Get or create a pipeline instance"""
    key = f"{model_id}_{threshold}"
    
    if key not in pipelines:
        weights_path = CONFIG[model_id]['weights']
        if not Path(weights_path).exists():
            raise FileNotFoundError(f"Model checkpoint not found: {weights_path}")
        pipelines[key] = LivenessPipeline(weights_path=weights_path, threshold=threshold)
    
    return pipelines[key]

# ============================================
# Routes
# ============================================

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/static/styles.css')
def styles():
    """Serve CSS"""
    with open('styles.css', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@app.route('/static/app.js')
def app_js():
    """Serve JavaScript"""
    with open('app.js', 'r') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze an image and return liveness detection result
    
    Request JSON:
    {
        "image": "<base64 encoded image>",
        "model": "v1" or "v2",
        "threshold": 0.5
    }
    
    Response JSON:
    {
        "label": "Real" or "Spoof",
        "confidence": 0.95,
        "detectionTime": 45,
        "classificationTime": 30,
        "annotatedImage": "<base64 encoded annotated image>",
        "faces": [
            {
                "id": 1,
                "label": "Real",
                "confidence": 0.95
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        image_data = data.get('image')
        model = data.get('model', 'v2')
        threshold = float(data.get('threshold', 0.5))
        
        # Validate model
        if model not in CONFIG:
            return jsonify({'error': f'Invalid model: {model}'}), 400
        
        # Validate threshold
        if not (0.0 <= threshold <= 1.0):
            return jsonify({'error': 'Threshold must be between 0 and 1'}), 400
        
        # Decode image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        pil_image = Image.open(BytesIO(image_bytes)).convert('RGB')
        np_image = np.array(pil_image)
        bgr_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        
        # Get pipeline
        pipeline = get_pipeline(model, threshold)
        
        # Record timing
        start_time = time.time()
        
        # Run analysis
        output = pipeline.run(bgr_image)
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Process results
        results = output['results']
        latency = output['latency']
        annotated_frame = output['annotated_frame']
        
        # Determine overall label
        overall_label = 'Real' if all(res['label'] == 'Real' for res in results) else 'Spoof'
        
        # Calculate average confidence
        confidences = [float(res['confidence']) for res in results]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Encode annotated image
        annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        pil_annotated = Image.fromarray(annotated_rgb)
        buffer = BytesIO()
        pil_annotated.save(buffer, format='JPEG', quality=85)
        annotated_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        response = {
            'label': overall_label,
            'confidence': float(avg_confidence),
            'detectionTime': float(latency.get('detection_ms', 0)),
            'classificationTime': float(latency.get('classification_ms', 0)),
            'totalTime': float(total_time),
            'annotatedImage': f'data:image/jpeg;base64,{annotated_base64}',
            'faces': [
                {
                    'id': i + 1,
                    'label': res['label'],
                    'confidence': float(res['confidence'])
                }
                for i, res in enumerate(results)
            ],
            'facesDetected': len(results)
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    models_available = {}
    for model_id, config in CONFIG.items():
        models_available[model_id] = {
            'description': config['description'],
            'available': Path(config['weights']).exists()
        }
    
    return jsonify({
        'status': 'ok',
        'models': models_available
    }), 200

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# Main
# ============================================

if __name__ == '__main__':
    # Check models exist
    for model_id, config in CONFIG.items():
        weights_path = config['weights']
        if not Path(weights_path).exists():
            print(f"⚠️  Warning: Model {model_id} not found at {weights_path}")
    
    print("🚀 Starting Face Liveness Detection Web Server")
    print("📍 Open http://localhost:5000 in your browser")
    print("\nEndpoints:")
    print("  GET  /              → Main UI")
    print("  POST /api/analyze   → Analyze image")
    print("  GET  /api/health    → Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

# Face Liveness Detection - Web UI

Mobile-first web interface for face liveness detection with coherent UX feedback and usability heuristics.

## Design Principles

### Mobile-First Approach

- **Responsive Layout**: Optimized for mobile devices (< 640px), tablets, and desktops
- **Touch-Friendly**: Large tap targets (min 48px), adequate spacing
- **Minimal Scrolling**: Content organized vertically for natural flow
- **Performance**: Optimized assets, lazy loading, minimal JavaScript

### UX & Usability Heuristics (Nielsen)

1. **System Visibility** ✅
   - Real-time status messages (success, error, warning)
   - Loading spinner with clear text feedback
   - Progress bars for confidence scores
   - Clear verdict display (✅ Authentic / ⚠️ Spoof)

2. **System-User Match** ✅
   - Language matches user expectations (not jargon)
   - Model descriptions simple and clear
   - Results shown in familiar percentage format
   - Latency metrics shown for transparency

3. **User Control** ✅
   - "Analyze Another" button for quick restart
   - "Clear" / "Retake" buttons for mistake correction
   - Tab navigation for input mode selection
   - Camera on/off toggle with clear state

4. **Prevent Problems** ✅
   - File size validation (max 10MB)
   - File type validation (image only)
   - Threshold validation (0.3-0.9)
   - Unsaved work protection

5. **Error Handling** ✅
   - Clear error messages with actionable guidance
   - No technical jargon in error text
   - Suggestions for fixing (e.g., camera permissions)
   - Auto-dismiss success messages

6. **Efficient & Flexible** ✅
   - Keyboard navigation support
   - Focus indicators for accessibility
   - Multiple input methods (upload, camera)
   - Presets for common workflows

### Coherent Feedback

- **Visual Feedback**: Color-coded status (green=success, red=danger)
- **Temporal Feedback**: Messages appear and disappear consistently
- **Spatial Feedback**: Results in logical section below input
- **Tactile Feedback**: Button scale on click for touch devices
- **Emotional Feedback**: Appropriate iconography (✅, ⚠️, 📷)

## Setup

### Prerequisites

- Python 3.8+
- CUDA/GPU recommended for inference speed

### Installation

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Verify model files**

   ```
   models/
   ├── best_checkpoint.pth      # V1 model
   └── best_checkpoint_v2.pth   # V2 model
   ```

3. **Run backend server**

   ```bash
   python backend.py
   ```

   Server starts at `http://localhost:5000`

4. **Open in browser**
   - Desktop: http://localhost:5000
   - Mobile: http://<your-ip>:5000

## File Structure

```
web_ui/
├── index.html          # Main HTML structure
├── styles.css          # Mobile-first responsive styles
├── app.js              # Client-side logic & API calls
├── backend.py          # Flask backend & pipeline integration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Endpoints

### `GET /`

Serves the main web application.

### `POST /api/analyze`

Analyzes a face image for liveness.

**Request:**

```json
{
  "image": "data:image/jpeg;base64,...",
  "model": "v1" | "v2",
  "threshold": 0.5
}
```

**Response:**

```json
{
  "label": "Real" | "Spoof",
  "confidence": 0.95,
  "detectionTime": 45,
  "classificationTime": 30,
  "totalTime": 75,
  "annotatedImage": "data:image/jpeg;base64,...",
  "facesDetected": 1,
  "faces": [
    {
      "id": 1,
      "label": "Real",
      "confidence": 0.95
    }
  ]
}
```

### `GET /api/health`

Health check and model availability.

**Response:**

```json
{
  "status": "ok",
  "models": {
    "v1": {
      "description": "V1 – NUAA only",
      "available": true
    },
    "v2": {
      "description": "V2 – NUAA + LCC FASD",
      "available": true
    }
  }
}
```

## Usage Guide

### Upload Image

1. Tap the upload area or click to browse
2. Select a JPG/PNG image (< 10MB)
3. Review result with confidence score
4. Tap "Analyze Another" to retry

### Camera Capture

1. Tap "📷 Camera" tab
2. Tap "📷 Start Camera"
3. Frame face in the circle outline
4. Tap the capture button
5. Review result or tap "Retake" to retry

### Configuration

- **Model**: Choose V1 (NUAA) or V2 (better cross-domain)
- **Threshold**: 0.3-0.9. Higher = stricter detection

## Performance Tips

- **Good Lighting**: Avoid shadows on face
- **Face Visibility**: Center face, no partial crops
- **Camera Angle**: Eye level or slightly above
- **Natural Expression**: Minimal movement during capture
- **Image Size**: Keep under 10MB for fast processing

## Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome)

## Accessibility

- Full keyboard navigation
- Focus indicators on all interactive elements
- Semantic HTML structure
- ARIA labels for screen readers
- Color contrast WCAG AA compliant
- Reduced motion support

## Troubleshooting

### Camera not working

- Check browser permissions
- Ensure HTTPS on production (Firefox requires it)
- Try different browser

### Analysis timeout

- Check image file size (should be < 10MB)
- Verify backend is running (`http://localhost:5000/api/health`)
- Check browser console for errors

### Slow inference

- Ensure GPU is being used (check PyTorch setup)
- Reduce image resolution in preprocessing
- Consider model quantization

## Development

### Run locally

```bash
python backend.py
# Open http://localhost:5000
```

### Enable debug mode

In `backend.py`, `app.run()` already has `debug=True`

### Customize colors

Edit CSS variables in `styles.css` `:root` section

### Add new models

1. Add to `CONFIG` dict in `backend.py`
2. Update model select options in `app.js`
3. Place checkpoint in `models/` folder

## License

M1 Cybersecurity — University of Buea

## Support

For issues or questions:

1. Check console logs (`F12`)
2. Review `README.md` troubleshooting section
3. Check backend logs for inference errors

# UX & Usability Design Guide

## Face Liveness Detection Web UI

---

## 1. Mobile-First Design

### Why Mobile-First?

The modern web is **mobile-dominant**:

- 65%+ of web traffic is mobile
- Users expect responsive, touch-friendly interfaces
- Development starts with constraints (small screens) → easier to scale up

### Implementation

| Aspect       | Mobile        | Tablet    | Desktop   |
| ------------ | ------------- | --------- | --------- |
| Padding      | 0.5rem        | 1rem      | 1.5rem    |
| Button Size  | 48px min      | 44px      | 40px      |
| Layout       | Single column | 2 columns | 3 columns |
| Font Size    | 16px base     | 16px      | 18px      |
| Input Fields | Full width    | 70%       | 50%       |

### Key Mobile Optimizations

- Touch targets: 48×48px minimum (iOS), 44×44px (Android)
- Spacing: Adequate padding to prevent accidental taps
- Scrolling: Vertical scroll prioritized, minimal horizontal
- Loading: Visual indicators, not spinners, for feedback

---

## 2. Nielsen's 10 Usability Heuristics

### 1. System Visibility & Status ✅

**Principle**: Users should always know what's happening.

**Implementation in UI**:

- **Status messages**: Toast notifications appear/disappear automatically
- **Loading state**: Spinner + "Analyzing..." text during processing
- **Result clarity**: Large icon (✅ or ⚠️) + color-coded verdict
- **Progress tracking**: Visual bar shows confidence level
- **Latency transparency**: Shows exact ms for detection & classification

**Code Examples**:

```javascript
// Immediate feedback
showStatus("✅ Image ready for analysis", "success", 2000);

// Loading state with spinner
showLoading();
```

---

### 2. Match Between System & Real World ✅

**Principle**: Use user's language, not system jargon.

**Implementation**:
| System Term | User-Friendly |
|---|---|
| "Inference latency" | "Analysis time" |
| "False positive rate" | "Confidence score" |
| "Feature extraction" | (Simplified, not shown) |
| "Cross-domain evaluation" | "Model performance" |
| "Threshold" | "Decision threshold" (with clear help text) |

**UI Examples**:

- Help section explains in plain English
- Tooltips avoid technical jargon
- Results use percentage format (85% confident)
- Model names simple: "V1 – NUAA only", "V2 – Better"

---

### 3. User Control & Freedom ✅

**Principle**: Users shouldn't feel trapped; provide undo/exit options.

**Implementation**:

- **"Clear" button**: Instantly clear uploaded image
- **"Retake" button**: Easy camera redo without restart
- **"Analyze Another" button**: Quick workflow restart
- **Tab navigation**: Switch input method anytime
- **Stop Camera**: Cancel camera session without page reload

**Control Hierarchy**:

```
Primary Actions (large, prominent):
├── Upload Image
├── Capture Photo
└── Analyze

Secondary Actions (smaller):
├── Clear
├── Retake
└── Settings

Tertiary Actions (helper):
├── Help
└── Configuration
```

---

### 4. Error Prevention & Recovery ✅

**Principle**: Prevent problems before they occur.

**Implementation**:

- **File validation**: Check size (< 10MB) before upload
- **Type checking**: Only accept image/\* MIME types
- **Threshold validation**: Enforce 0.3-0.9 range
- **Camera permissions**: Clear error if denied

**Example Error Message** (Good vs Bad):

```
❌ BAD: "Error 422: Invalid image format"
✅ GOOD: "❌ Please upload a JPG or PNG image. Max size: 10MB"
```

---

### 5. Error Handling ✅

**Principle**: Simple, constructive error messages in user's language.

**Implementation**:

```javascript
// Show error with actionable guidance
showStatus(
  "❌ Camera access denied. Check browser permissions.",
  "error",
  3000,
);

// Include recovery steps
// "Try a different browser" or "Refresh and try again"
```

**Error Types & Responses**:
| Error | Message |
|-------|---------|
| File too large | ❌ File too large (max 10MB) |
| Wrong format | ❌ Please upload a JPG or PNG image |
| Camera denied | ❌ Camera access denied. Check permissions. |
| Analysis failed | ❌ Analysis failed. Check console for details. |

---

### 6. Efficiency & Shortcuts ✅

**Principle**: Support both novices and experts.

**Implementation for Novices**:

- Clear button labels with emojis (📁, 📷, ℹ️)
- Step-by-step help section
- Tooltips on complex options
- Suggested defaults (V2 model pre-selected)

**Implementation for Experts**:

- Direct API access via `/api/analyze`
- Batch processing capable (upload multiple via script)
- Adjustable threshold for custom tuning
- Model selection without help text needed

---

### 7. Aesthetic & Minimalist Design ✅

**Principle**: Focus on essentials; remove clutter.

**Implementation**:

- **Dark theme**: Reduces eye strain, modern aesthetic
- **Color hierarchy**: Primary (cyan), Success (green), Danger (red)
- **Whitespace**: Generous padding between sections
- **Typography**: Two levels (title + body), consistent
- **Icons**: Minimal, universally recognizable

**Visual Hierarchy**:

```
1. Hero section (what app does)
2. Configuration (required settings)
3. Input area (main action)
4. Results (only shown after analysis)
5. Help (always accessible, unobtrusive)
```

---

### 8. Accessibility for All ✅

**WCAG 2.1 AA Compliance**:

- **Color contrast**: 4.5:1 for text, 3:1 for UI components
- **Focus indicators**: Clear outline on tab/focus
- **Keyboard navigation**: All functions via keyboard
- **Semantic HTML**: Proper heading hierarchy, labels
- **ARIA labels**: Screen reader support
- **Reduced motion**: Respects `prefers-reduced-motion` setting

**Implementation**:

```css
/* Focus visible for keyboard users */
button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Respect motion preferences */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
  }
}
```

---

### 9. Help & Documentation ✅

**Principle**: Provide contextual help without overwhelming.

**Implementation**:

- **In-app help tab**: Accessible from any page
- **Inline hints**: Below form fields ("V2 has better cross-domain performance")
- **Tooltips**: On hover/tap for configuration options
- **Model performance**: Transparent metrics shown in help
- **Tips section**: Best practices for image quality

**Context-Aware Help**:

```javascript
// Show help on tab switch
if (tabName === "camera" && !state.cameraActive) {
  showStatus('Camera ready. Tap "Start Camera" to begin.', "success", 2000);
}
```

---

### 10. Consistency & Standards ✅

**Principle**: Follow conventions users expect.

**Implementation**:

- **Button placement**: Primary action on right/bottom (RTL-aware)
- **Color meanings**: Green = success, Red = error, Blue = primary
- **Icons**: Standardized emoji + recognizable symbols
- **Interactions**: Tap = select, long-press = alternative action
- **Feedback**: Consistent timing for toasts (appear 3s, auto-dismiss)

---

## 3. Coherent Feedback System

### Feedback Dimensions

#### A. Visual Feedback

```
Upload → Image appears in preview
Button click → Slight scale animation (0.98)
Tab switch → Fade + slide animation
Result → Color-coded section (green/red)
```

#### B. Temporal Feedback

```
Success message: Appears, shows 3s, fades
Error message: Appears, shows 3s, fades
Loading: Spinner until complete
Status change: Immediate (< 100ms perceived)
```

#### C. Spatial Feedback

```
Upload area → Becomes active (border highlight)
Tab selected → Highlighted, results below
Result section → Appears below analysis
Error → Toast at top of screen
```

#### D. Emotional Feedback

```
✅ = Success, authentic
⚠️ = Warning, needs attention
📷 = Camera action
📁 = File action
ℹ️ = Information
```

#### E. Tactile Feedback (Mobile)

```
Button tap → 0.98 scale + shadow reduction
Swipe → Smooth scroll
Long-press → Context menu (future)
Two-finger → Zoom (camera preview)
```

---

## 4. Information Architecture

### Navigation Model: Hub-and-Spoke

```
        ┌─ Upload
        │
HEADER ─┼─ Camera
        │
        └─ Help

Each tab has linear workflow:
Input → Processing → Results → Restart
```

### Content Organization

```
Header (Identity + Context)
  ↓
Config Panel (Settings, not required for basic use)
  ↓
Tab Navigation (Three input methods)
  ↓
Tab Content (Focused on one task)
  ↓
Results Section (Appears after analysis)
  ↓
Footer (Credits)
```

---

## 5. Task Flow Optimization

### Happy Path (85% of users)

```
1. Open app (see welcome message)
2. Click upload or camera tab
3. Provide image
4. View result (3 seconds)
5. Tap "Analyze Another" or close
```

### Alternative Paths

**Path: Change Model**

```
1. Adjust model select → Success message
2. Upload image → Analysis with new model
```

**Path: Fine-tune Threshold**

```
1. Adjust slider → Value updates live
2. Upload image → Analysis with new threshold
```

---

## 6. Performance UX

### Perceived Performance

| Action            | Target     | Implementation             |
| ----------------- | ---------- | -------------------------- |
| Button response   | < 50ms     | `active` class immediately |
| Loading indicator | Immediate  | Show spinner within 100ms  |
| First paint       | < 1s       | CSS-in-HTML, minimal JS    |
| Analysis feedback | Continuous | Progress + timing display  |

### Code Example

```javascript
// Show loading immediately, don't wait for API
showLoading();
setButtonsDisabled(true);

// Then make async request
analyzeImage();
```

---

## 7. Design Tokens

### Colors (Semantic)

```
Primary:    #0ea5e9 (cyan, trustworthy)
Success:    #10b981 (green, positive)
Danger:     #ef4444 (red, urgent)
Warning:    #f59e0b (amber, caution)
Gray:       #64748b (neutral, secondary)
```

### Spacing Scale

```
xs:  0.25rem (4px)   – Minimal gaps
sm:  0.5rem  (8px)   – Compact spacing
md:  1rem    (16px)  – Default spacing
lg:  1.5rem  (24px)  – Section spacing
xl:  2rem    (32px)  – Large gaps
2xl: 3rem    (48px)  – Sections
```

### Breakpoints

```
Mobile:  < 640px  (primary)
Tablet:  640-1024px
Desktop: > 1024px
```

---

## 8. Accessibility Checklist

- [x] Keyboard navigation works on all interactive elements
- [x] Focus indicators visible (2px outline)
- [x] Color contrast 4.5:1 for text, 3:1 for UI
- [x] Semantic HTML (`<button>`, `<label>`, etc.)
- [x] ARIA labels where needed
- [x] Image alt text for annotated results
- [x] Form labels associated with inputs
- [x] Error messages linked to fields
- [x] Reduced motion respected
- [x] Dark/light mode CSS variables

---

## 9. Testing & Validation

### User Testing Checklist

- [ ] Can users complete upload flow < 30 seconds?
- [ ] Do users understand "Real" vs "Spoof"?
- [ ] Can users find help without frustration?
- [ ] Do error messages help users recover?
- [ ] Is camera workflow intuitive?

### A/B Testing Opportunities

- [ ] Button text ("Analyze" vs "Check")
- [ ] Result layout (large icon vs text-first)
- [ ] Help placement (tab vs sidebar vs modal)

---

## 10. Future Enhancements

1. **Batch Processing**: Upload multiple images at once
2. **History**: Show past analyses with timestamps
3. **Export**: Save results as PDF or image
4. **Real-time Feedback**: Show liveness score while camera captures
5. **Offline Mode**: Cache models for offline analysis
6. **Voice Commands**: "Analyze this" via speech

---

## References

- [Nielsen Norman's 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Google Material Design](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)

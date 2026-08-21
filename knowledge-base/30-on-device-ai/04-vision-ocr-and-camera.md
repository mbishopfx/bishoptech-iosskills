# Vision, OCR, and Camera Intelligence

## Choose the right visual route

Vision provides computer-vision requests over still images and video frames. VisionKit provides user-facing experiences such as Live Text interaction, the document camera, image analysis, and the live DataScanner. Core ML is the route for a custom model that must run on device; Vision can use system requests or integrate with a Core ML model.

## Vision request pattern

The general Vision pattern is:

1. Obtain an image or video frame.
2. Create a request for the desired observation.
3. Perform the request.
4. Read observations and confidence.
5. Transform observations into a reviewable domain proposal.
6. Store the original source and the accepted result separately.

For text recognition, choose a fast or accurate recognition path based on latency and quality needs. Text recognition happens on the person’s device; still validate orientation, language, confidence, and noisy input.

## VisionKit live scanning

DataScannerViewController can recognize text and machine-readable codes in a live camera view. Before presentation, check both isSupported and isAvailable, provide the camera usage description, and handle the person’s consent. Availability can change while the session runs, so handle the delegate’s unavailable callback.

## Camera and privacy

- Request camera access only when the user starts a camera-related workflow.
- Explain why the camera is needed in the permission-facing copy.
- Keep raw frames in memory or protected local storage only as long as necessary.
- Avoid sending frames to a network model unless the product explicitly requires it and the user understands the boundary.
- Show a review screen before committing OCR-derived data.

## Confidence is not truth

Use confidence to prioritize review and highlight uncertain fields. Do not silently convert low-confidence OCR into a final record. For receipts, forms, or identity documents, preserve source regions or a source image reference so the user can verify the proposal.

## Core ML route

Use Core ML when you have a custom trained model, need a domain-specific classifier/detector, or need to control compute-unit behavior. Measure memory, latency, thermal impact, and battery use on representative devices.

## Sources

- [Vision](https://developer.apple.com/documentation/vision/)
- [Recognizing text in images](https://developer.apple.com/documentation/vision/recognizing-text-in-images)
- [VisionKit](https://developer.apple.com/documentation/visionkit/)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Apple Intelligence and machine learning](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)

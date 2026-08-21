# Media to Reviewable Record

## Best fit

Receipts, documents, photos, labels, forms, field notes, or voice memos that become structured app records.

## Route

PhotosUI or VisionKit -> Vision/Speech -> typed proposal -> SwiftUI review -> SwiftData/files -> export or App Intent

## Build order

1. Let the user select or capture the source.
2. Explain and request the required camera, photo, or microphone permission.
3. Preserve the original source and show processing state.
4. Run the on-device analysis.
5. Map observations into a typed draft with confidence and source references.
6. Let the user edit, accept, discard, or retry.
7. Commit only the accepted values.

## Failure states

No permission, unsupported hardware, unavailable language/model, blurry source, low confidence, cancellation, oversized file, storage failure, and duplicate record. Each should preserve the original input where privacy policy allows and offer a clear next action.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [VisionKit](https://developer.apple.com/documentation/visionkit/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)

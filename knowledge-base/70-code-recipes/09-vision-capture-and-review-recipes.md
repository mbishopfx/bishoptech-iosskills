# Vision, Capture, and Review Recipes

These route sketches implement pieces of the [reviewable multimodal AI pipeline](../31-on-device-ai-recipes/06-reviewable-multimodal-ai-pipeline.md). Pair them with the [AI feature lifecycle](../30-on-device-ai/09-ai-feature-lifecycle-and-availability.md) and [evaluation discipline](../30-on-device-ai/10-on-device-ai-evaluation-and-model-update-discipline.md) before treating an observation or prediction as a product result.

## Scope and compile boundary

These are compile-oriented route sketches for PhotosUI, VisionKit, Vision, Core ML, and a reviewable SwiftUI draft. They intentionally keep capture, observation, normalization, review, and persistence separate. They are not compiled in this documentation-only workspace and do not prove camera availability, model accuracy, privacy completion, or physical-device performance.

Before using a recipe, verify the selected SDK and deployment target, add the appropriate usage description/capability, compile the smallest route, and test on supported physical hardware. Keep raw images and recognized text out of logs unless a consented debugging flow requires them.

## Recipe 1: choose a photo without broad library access

Use `PhotosPicker` when the person can select an existing image. Load the representation asynchronously and preserve the source while analysis is pending.

```swift
import PhotosUI
import SwiftUI

struct PhotoSourcePicker: View {
    @State private var selectedItem: PhotosPickerItem?
    @State private var imageData: Data?
    @State private var errorMessage: String?

    var body: some View {
        VStack(spacing: 16) {
            PhotosPicker(
                "Choose a photo",
                selection: $selectedItem,
                matching: .images
            )

            if imageData != nil {
                Label("Source ready for review", systemImage: "photo")
            }

            if let errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.secondary)
            }
        }
        .task(id: selectedItem) {
            guard let selectedItem else { return }
            do {
                imageData = try await selectedItem.loadTransferable(type: Data.self)
                if imageData == nil {
                    errorMessage = "The selected item had no usable image data."
                }
            } catch {
                errorMessage = "The photo could not be loaded. Choose another source."
            }
        }
    }
}
```

The exact transferable type and accepted image formats are target decisions. A `PhotosPickerItem` is a selection placeholder, not the decoded image itself. Test iCloud-backed assets without network, cancellation, unsupported representations, large images, and user-selected-only privacy behavior.

## Recipe 2: recognize text with the current Vision request route

Use the narrowest Vision request for the desired observation. Keep transcript, confidence, and geometry as proposal metadata.

```swift
import Vision

struct TextProposal: Identifiable, Sendable {
    let id = UUID()
    let transcript: String
    let confidence: Float
    let boundingBox: CGRect
}

func recognizeText(in imageData: Data) async throws -> [TextProposal] {
    var request = RecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true

    let observations = try await request.perform(on: imageData)

    return observations.map { observation in
        TextProposal(
            transcript: observation.transcript,
            confidence: observation.confidence,
            boundingBox: observation.boundingBox
        )
    }
}
```

This is a route sketch: verify the exact result and observation members in the selected SDK, including orientation and language configuration. Normalize the framework’s coordinate system before drawing boxes in SwiftUI, and never treat a transcript as a validated domain value without parsing and review.

## Recipe 3: map observations into a reviewable draft

Translate framework output into product-owned types before showing the edit form or saving a record.

```swift
struct FieldProposal: Identifiable, Sendable {
    let id: UUID
    let label: String
    var value: String
    let confidence: Float?
    let sourceDescription: String
    var requiresReview: Bool
}

struct CaptureDraft: Sendable {
    var fields: [FieldProposal]
    var sourceReference: String
    var isConfirmed = false
}

func makeDraft(from observations: [TextProposal]) -> CaptureDraft {
    let fields = observations.map { observation in
        FieldProposal(
            id: observation.id,
            label: "Recognized text",
            value: observation.transcript,
            confidence: observation.confidence,
            sourceDescription: "Captured image region",
            requiresReview: observation.confidence < 0.85
        )
    }

    return CaptureDraft(
        fields: fields,
        sourceReference: "local-photo",
        isConfirmed: false
    )
}
```

The threshold is illustrative, not a universal confidence policy. Calibrate it with labeled fixtures and measure user correction. Confidence should direct review attention; it should not be marketed as truth or identity.

## Recipe 4: review and confirm before persistence

Make the draft editable and keep confirmation separate from the recognition operation.

```swift
struct CaptureReview: View {
    @State var draft: CaptureDraft
    let save: (CaptureDraft) async throws -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var isSaving = false
    @State private var errorMessage: String?

    var body: some View {
        Form {
            Section("Review proposed values") {
                ForEach($draft.fields) { $field in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(field.label)
                            .font(.headline)
                        TextField(field.sourceDescription, text: $field.value)
                        if field.requiresReview {
                            Label("Please verify this value", systemImage: "exclamationmark.circle")
                                .font(.footnote)
                                .foregroundStyle(.orange)
                        }
                    }
                }
            }

            if let errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }
        }
        .navigationTitle("Review capture")
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("Save") {
                    Task {
                        isSaving = true
                        defer { isSaving = false }
                        do {
                            draft.isConfirmed = true
                            try await save(draft)
                            dismiss()
                        } catch {
                            draft.isConfirmed = false
                            errorMessage = "The corrected capture was not saved. Try again."
                        }
                    }
                }
                .disabled(isSaving)
            }
        }
    }
}
```

Add validation for dates, numbers, totals, identifiers, and required fields before `save`. Preserve the draft if persistence fails. The code does not show the source image/crop; a real review UI should provide enough provenance for the person to correct a proposal.

## Recipe 5: check live scanner availability before presentation

Data scanning has both hardware support and current availability/permission state. Treat them as separate states.

```swift
import VisionKit

enum ScannerState {
    case supportedAndAvailable
    case unsupported
    case unavailable
}

@MainActor
func scannerState() -> ScannerState {
    guard DataScannerViewController.isSupported else {
        return .unsupported
    }

    guard DataScannerViewController.isAvailable else {
        return .unavailable
    }

    return .supportedAndAvailable
}
```

Before presenting, add an accurate `NSCameraUsageDescription`, choose only the text/barcode types the feature needs, and handle the scanner becoming unavailable while it is running. A manual or photo-import path should be visible when the product can still provide value without the live scanner.

## Recipe 6: bridge scanner output into the same draft pipeline

The scanner is a source adapter. Its recognized item should become a proposal, not a direct side effect such as opening a URL, changing an account, or saving a record.

```swift
struct BarcodeProposal: Sendable {
    let payload: String
    let symbology: String
    let sourceDescription: String
}

func makeBarcodeProposal(from item: String) -> BarcodeProposal? {
    let payload = item.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !payload.isEmpty, payload.count <= 2048 else { return nil }

    return BarcodeProposal(
        payload: payload,
        symbology: "scanner-result",
        sourceDescription: "Live camera scan"
    )
}
```

Validate the payload against the product’s allowed format before presenting an action. If a barcode contains a URL, show the destination and confirmation before opening it. Do not trust a camera result as authorization or as proof of ownership.

## Recipe 7: load a Core ML model with an explicit device policy

Use a generated wrapper for a bundled model when it makes the interface clear. Use `MLModel` directly when loading a compiled asset at runtime or when lower-level configuration is required.

```swift
import CoreML

struct ModelRuntime {
    let model: MLModel
    let modelVersion: String
}

func loadModel(from compiledURL: URL) async throws -> ModelRuntime {
    let configuration = MLModelConfiguration()
    configuration.computeUnits = .all

    let model = try await MLModel.load(
        contentsOf: compiledURL,
        configuration: configuration
    )

    return ModelRuntime(
        model: model,
        modelVersion: model.modelDescription.metadata[.versionString] as? String ?? "unknown"
    )
}
```

The compute-unit choice is a product/device decision, not a promise that every device uses the same processor. Measure load time, prediction latency, memory, energy, thermal behavior, and accuracy across supported hardware. Handle model load failure and unsupported input with the same reviewable fallback contract.

## Recipe 8: latest-frame processing policy

For a live camera route, avoid queuing unbounded work. A latest-frame policy is often more appropriate for UI guidance than processing every frame.

```swift
actor LatestFrameProcessor {
    private var pendingTask: Task<Void, Never>?

    func submit(_ frame: Data, analyze: @escaping @Sendable (Data) async -> Void) {
        pendingTask?.cancel()
        pendingTask = Task {
            await analyze(frame)
        }
    }

    func stop() {
        pendingTask?.cancel()
        pendingTask = nil
    }
}
```

The analyzer must honor cancellation or check a generation/token before publishing results. Throttle UI updates, release frame buffers, and stop the processor when the capture screen disappears. Test rapid source changes, permission changes, backgrounding, memory pressure, and thermal constraints on a physical device.

## Recipe 9: optional language-model enrichment boundary

Only pass validated, minimized observations to a language model. Keep the recognition result and the generated explanation separate in the data model.

```swift
struct ValidatedCapture: Sendable {
    let title: String
    let date: Date?
    let amount: Decimal?
    let sourceWasReviewed: Bool
}

struct EnrichmentInput: Sendable {
    let title: String
    let dateText: String
    let amountText: String
}

func enrichmentInput(from capture: ValidatedCapture) throws -> EnrichmentInput {
    guard capture.sourceWasReviewed else {
        throw EnrichmentError.reviewRequired
    }

    return EnrichmentInput(
        title: capture.title,
        dateText: capture.date?.formatted() ?? "No date",
        amountText: capture.amount.map(String.init) ?? "No amount"
    )
}

enum EnrichmentError: Error {
    case reviewRequired
}
```

The Foundation Models session, prompt, guided output, tool, and fallback belong behind a separate service boundary. Do not use generated enrichment to fill a missing financial, health, identity, or legal field without a deterministic validation and human-review policy.

## Recipe 10: capture and AI test fixtures

Build the evaluation set before tuning thresholds or prompts:

| Fixture family | Examples | Expected evidence |
| --- | --- | --- |
| Source quality | glare, blur, skew, low light, crop, occlusion, small text | Observation confidence, extraction errors, user correction |
| Content variation | languages, scripts, handwriting, tables, barcodes, empty images | Supported/unsupported state and fallback |
| Device/camera | portrait/landscape, focus changes, thermal load, denied camera | Physical-device behavior and lifecycle correctness |
| Data safety | private documents, health/financial text, signed-out account | Redaction, retention, access control, deletion |
| Interaction | cancel, background, duplicate tap, source replacement, save failure | Cancellation, draft preservation, and honest state |
| Model boundary | model unavailable, load failure, slow prediction, low confidence | Manual route, retry, and no false success |

Record model/revision, device/OS, input fixture ID, latency, confidence, correction outcome, and error class. Avoid retaining raw images or private text in the evaluation log by default.

## Recipe review checklist

- The capture source is the least privileged route that serves the task.
- Camera/photo permissions and device availability are explicit states.
- Vision/Core ML output is an observation or proposal with provenance, not a guaranteed fact.
- Normalization validates formats and units before persistence.
- The review UI lets a person correct every proposed field.
- Save failure preserves the corrected draft and does not leave a success state.
- Live frames have a backpressure, cancellation, and lifecycle policy.
- Optional Foundation Models enrichment receives minimized, validated input only.
- Preview/simulator/image tests are kept separate from physical-camera/model/performance proof.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera)
- [Document camera](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller)
- [Vision](https://developer.apple.com/documentation/vision)
- [RecognizeTextRequest](https://developer.apple.com/documentation/vision/recognizetextrequest)
- [Recognizing text in images](https://developer.apple.com/documentation/vision/recognizing-text-in-images)
- [RecognizeDocumentsRequest](https://developer.apple.com/documentation/vision/recognizedocumentsrequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [computeUnits](https://developer.apple.com/documentation/coreml/mlmodelconfiguration/computeunits)
- [Integrating a Core ML model into your app](https://developer.apple.com/documentation/coreml/integrating-a-core-ml-model-into-your-app)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)

# Blueprint: SwiftUI view artifact export

## Product outcome

Let a person review confirmed state, generate a polished image or PDF representation, and share it through Apple’s system route without exposing the live navigation hierarchy or private source data.

## Route composition

    domain state -> redacted ExportSnapshot -> purpose-built SwiftUI export view
    -> ImageRenderer -> CGImage/UIImage or CGContext/PDF
    -> validated Data/File artifact -> Transferable -> ShareLink

| Layer | Apple route | Ownership |
| --- | --- | --- |
| Source | SwiftData, local files, PhotosUI, Foundation Models proposal, or approved source | Confirmed value, source revision, scope, freshness |
| Snapshot | App-owned Sendable value type | Redaction, units, labels, export schema, inclusion |
| Visual | SwiftUI View, Shape, Canvas, Image, Text, symbols, materials | Layout, typography, appearance, fallback |
| Render | ImageRenderer or ImageRenderer.render | Point size, scale, color mode, opacity, dynamic range |
| Artifact | ImageIO Data or PDF/Core Graphics file | Encoding, validation, metadata, file lifetime |
| Transport | Core Transferable, UTType, ShareLink | Representation, filename, visibility, handoff |
| Evidence | Tests, physical device, archive | Compile, fidelity, accessibility, destination, release |

## State machine

    idle -> preparing -> rendering -> validating -> ready
    ready -> presenting-share -> transferred | canceled | failed
    failed -> retrying | fallback | dismissed
    active -> source-changed | terminated | canceled

Persist a job when an export can outlive the view:

    jobID, sourceRevision, exportSchemaVersion, artifactKind
    pointSize, scale, colorPolicy, includedFields
    stagedURLOrDigest, state, error, createdAt, updatedAt

Reconcile on relaunch. A ShareLink presentation is not necessarily a completed transfer; keep the result uncertain when the selected route does not report delivery.

## Build order

1. Choose image, PDF, codable object, file, or safe text proxy.
2. Create a redacted snapshot from confirmed domain state.
3. Build a purpose-specific export view with deterministic dimensions and semantic labels.
4. Compile a fixed ImageRenderer fixture in the named iOS 26 target.
5. Encode and validate dimensions, bytes, type, metadata, and source revision.
6. Add one Core Transferable representation and ShareLink.
7. Add stale/source-change, cancellation, cleanup, and destination failure.
8. Test live UI and artifact independently across accessibility and appearance settings.
9. Use physical devices for large output, display scale, memory, thermal behavior, and real destinations.

## Image route

    ExportSnapshot -> ExportView -> ImageRenderer.cgImage
    -> ImageIO PNG/JPEG encode -> DataRepresentation -> ShareLink

PNG suits transparency and crisp UI-like art; JPEG may reduce size for photographic content. Validate the exact format, metadata, pixel count, and byte limit. For Liquid Glass-like design, export the semantic card and state label with an explicit treatment that remains legible without a live backdrop. Keep functional controls in the live screen.

## PDF route

    ExportView -> ImageRenderer.render -> page-sized CGContext
    -> begin/end page -> close PDF -> open/validate -> FileRepresentation

Define page size, margins, page breaks, truncation, font fallback, selectable text, reading order, metadata, privacy, page count, memory, and cancellation. A PDF opening is not proof of accessibility, correct pagination, text selection, or privacy.

## Transfer policy

| Need | Preferred representation | Fallback |
| --- | --- | --- |
| Small visual | DataRepresentation with image UTType | Save a file and offer Files |
| Large visual/PDF | FileRepresentation with staged file | Smaller preview or text summary |
| Structured object | CodableRepresentation | Safe ProxyRepresentation |
| Multiple destinations | Explicit multiple representations | Explain unsupported destination |

Use a suggested filename without private IDs. Use exportingCondition for empty, stale, or unauthorized content. Use visibility only after understanding the receiver scope. A representation is transport policy, not consent.

## Privacy and optional on-device AI

Before rendering, decide whether the source is user-selected, app-owned, or model-proposed. Redact prompts, hidden fields, exact location, EXIF, internal IDs, and unreviewed text. Preserve provenance and schema. Avoid source data in filenames, previews, logs, notifications, or temporary paths.

If Foundation Models proposes a title, layout token, or summary, validate a bounded schema and ask for review when meaning changes:

    confirmed source -> bounded context -> typed proposal
    -> validator/allowlist -> review -> ExportSnapshot -> ImageRenderer

The model cannot select arbitrary view code, shader/resource paths, file destinations, or privacy fields. If unavailable or invalid, use deterministic copy/layout.

## Accessibility and adaptation

The live screen remains usable without the artifact. Expose values, units, freshness, and status as semantic SwiftUI text; keep buttons/share actions native; support VoiceOver, Voice Control, Switch Control, keyboard access, Dynamic Type, RTL, increased contrast, reduced transparency, and Reduce Motion. Provide a text or accessible-document alternative when an image removes important information. A pretty artifact is not an accessibility exemption.

## Fallbacks

| Condition | Fallback |
| --- | --- |
| Nil ImageRenderer output | Preserve snapshot, retry, or provide text/structured export |
| UIKit/web/media not represented | Framework exporter or dedicated export view |
| Source changed | Discard or label stale artifact; rerender |
| HDR unsupported | Tested SDR output |
| Output too large | Bound dimensions, switch format, or use file route |
| Destination unavailable | Save a user-visible file or another representation |
| User cancels | Keep draft; do not mark shared |
| Process termination | Reconcile staged job without claiming delivery |

## Proof packet

    target/deployment, Xcode/SDK, source revision, export schema
    artifact kind/UTType, point size/scale, color/opacity policy
    fixture/appearance, output dimensions/bytes/hash
    privacy review, accessibility task result, device/OS
    destination, cancellation/cleanup result, archive inspection
    unproven scope

## Sources

- [ImageRenderer](https://developer.apple.com/documentation/swiftui/imagerenderer)
- [ImageRenderer.render(rasterizationScale:renderer:)](https://developer.apple.com/documentation/swiftui/imagerenderer/render%28rasterizationscale%3Arenderer%3A%29)
- [ImageRenderer.proposedSize](https://developer.apple.com/documentation/swiftui/imagerenderer/proposedsize)
- [ImageRenderer.scale](https://developer.apple.com/documentation/swiftui/imagerenderer/scale)
- [ImageRenderer.cgImage](https://developer.apple.com/documentation/swiftui/imagerenderer/cgimage)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [TransferRepresentation](https://developer.apple.com/documentation/coretransferable/transferrepresentation)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [ProxyRepresentation](https://developer.apple.com/documentation/coretransferable/proxyrepresentation)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [SharePreview](https://developer.apple.com/documentation/swiftui/sharepreview)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [EnvironmentValues.displayScale](https://developer.apple.com/documentation/swiftui/environmentvalues/displayscale)
- [Human Interface Guidelines: Activity views](https://developer.apple.com/design/human-interface-guidelines/activity-views)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)

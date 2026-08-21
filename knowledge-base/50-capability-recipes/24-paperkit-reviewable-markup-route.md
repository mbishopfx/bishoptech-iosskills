# PaperKit reviewable-markup route

## Outcome

Use this route when a person needs to annotate a source document, image, or design surface with Apple Pencil, structured markup, or an AI-assisted proposal while keeping the original content, the editable PaperMarkup model, and any exported artifact separate.

Good examples:

- annotate a PDF and export a reviewed copy;
- turn handwritten notes into editable labels after user approval;
- mark up a photo or inspection image;
- build a visual planning board with shapes, text, and links;
- use on-device AI to propose callouts or summaries on a selected region;
- create a local-first canvas that can reopen without an account.

The route does not assume that AI output is correct, that a rendered image is an editable source, or that a PaperKit element is supported on every target.

## Route architecture

    source asset
        -> source identity and coordinate space
        -> PaperMarkup model
        -> PaperMarkupViewController canvas
        -> MarkupEditViewController / PencilKit input
        -> coalesced persistence
        -> optional deterministic observation
        -> typed AI proposal
        -> review overlay
        -> user-approved PaperMarkup mutation
        -> durable document
        -> optional render/export/share

### Ownership table

| Concern | Owner | Durable? |
| --- | --- | --- |
| Original PDF/image/document | App-owned source store or document provider | Yes, with security and retention policy |
| PaperMarkup structured elements and ink | PaperMarkup data representation | Yes |
| Live view/controller state | PaperKit/UIKit adapter | No; rebuild on launch |
| FeatureSet and content version | Document envelope plus target configuration | Yes |
| AI observation | Vision/Core ML/Foundation Models route | Usually no, unless provenance is needed |
| AI proposal | App-owned typed proposal with source spans/coordinates | Yes until accepted/rejected |
| Applied markup | PaperMarkup mutation | Yes |
| Exported PDF/image | User-approved artifact | Separate file and provenance |
| Link activation | App policy and system/browser handoff | Side effect; log outcome if needed |

## Target graph

### iOS/iPadOS SwiftUI app

- app target imports PaperKit, PencilKit, SwiftUI, and UIKit;
- shared feature module owns PaperMarkup envelope, validation, and persistence;
- SwiftUI screen uses UIViewControllerRepresentable for PaperMarkupViewController;
- app presents MarkupEditViewController as a popover/sheet when supported;
- document/export module owns FileDocument, PDFKit, ImageRenderer, or ShareLink routes when selected.

### UIKit-first document app

- app target owns the source view and PaperMarkupViewController;
- MarkupEditViewController is presented from the document controller;
- delegate/coordinator observes changes and saves the model;
- AI proposal UI can be a child/overlay view that does not mutate PaperMarkup until confirmation.

### Mac Catalyst or visionOS

- keep the PaperMarkup model and proposal validator shared;
- validate the controller and input route separately;
- do not assume the iOS PencilKit tool picker or popover behavior is identical;
- record target-specific FeatureSet, keyboard/pointer, and system-surface proof.

## Route steps

### 1. Establish the source coordinate space

Define the source bounds, orientation, scale, and coordinate transform before inserting any markup. A Vision bounding box, a PDF page, a camera image, and a SwiftUI view do not necessarily use the same origin or unit.

Store:

- source id and revision;
- source bounds and orientation;
- PaperMarkup bounds;
- transform from observation coordinates to PaperKit coordinates;
- current FeatureSet/content version.

If the source changes, invalidate or rebase proposals rather than inserting them into a new coordinate space.

### 2. Create a compatible feature set

Choose FeatureSet.latest only when the product can persist, render, and migrate every enabled feature. Otherwise choose a narrower set. Use the same compatible set for the PaperMarkup model, PaperMarkupViewController, and insertion controller.

Make unsupported-content behavior visible. If a document is opened on a target that cannot edit one of its elements, offer read-only mode, a copy with an explicit loss report, or a migration path.

### 3. Create the model and canvas

Create PaperMarkup with the source bounds and pass it into PaperMarkupViewController. Place the source content underneath or provide it as the controller’s content view, depending on the selected platform route.

Set isEditable from the app’s current mode. Do not make a review screen editable merely because the controller can accept input.

### 4. Add the native tool route

Present MarkupEditViewController on iOS-family targets or MarkupToolbarViewController on macOS. Match the supported FeatureSet. Use native tool behavior first; add app-owned commands through the documented delegate/action boundary.

Keep a compact toolbar for undo/redo, mode, and document actions when the environment is too small for the full tool picker. The canvas should not depend on a custom glass recreation of the system tool palette.

### 5. Persist safely

Observe PaperMarkup changes and coalesce saves. Write the serialized data atomically to a local document location or the selected document provider. Save the envelope separately so the app can track source revision, feature version, and provenance.

The user-facing state should be:

    editing -> save pending -> saved
                         \-> save failed -> retry

If a new edit arrives during a save, cancel or supersede the stale task and make sure the latest model is eventually written. Do not report Saved for a payload that was not successfully written.

### 6. Add an AI proposal route

Use deterministic observation first:

- user-selected region;
- OCR or Vision result;
- existing text box;
- PencilKit selection;
- source metadata.

Then ask the on-device model for a typed proposal:

~~~swift
struct MarkupProposal: Codable, Hashable, Sendable {
    let id: UUID
    let sourceRevision: String
    let kind: Kind
    let frame: CGRect
    let text: String?
    let destinationURL: URL?
    let explanation: String

    enum Kind: String, Codable, Sendable {
        case textBox
        case shape
        case link
        case callout
    }
}
~~~

The proposal is not PaperMarkup. Validate it against:

- current source revision;
- PaperMarkup bounds;
- FeatureSet support;
- safe text length and typography;
- URL policy;
- non-overwrite and non-delete rules;
- user-selected scope;
- localization and accessibility.

Render the proposal as a separate overlay or temporary adornment. The Apply action is the only place that calls the PaperMarkup insertion method.

### 7. Apply deterministically

Convert the reviewed proposal into a PaperKit element:

- textBox -> insertNewTextbox with AttributedString;
- shape -> ShapeConfiguration and insertNewShape;
- callout -> bounded shape plus text box;
- link -> LinkMarkup after URL validation;
- image -> approved CGImage and insertNewImage.

Record the proposal id, source revision, model/prompt version, user decision, and resulting element IDs. Keep undo available.

### 8. Render/export only after approval

For a user-started export, create an immutable render request with bounds, frame, RenderingOptions, background policy, and destination type. Use PaperMarkup.draw for the PaperKit content, then pass the artifact to the selected PDF/image/share route.

Do not silently export rejected proposals. Do not add ephemeral adornments to a durable artifact unless the user selected them.

## Route selection with adjacent frameworks

| Need | Add | Keep separate |
| --- | --- | --- |
| Freehand ink | PencilKit | PencilKit drawing versus PaperKit structured elements |
| PDF page rendering | PDFKit | Source PDF versus markup overlay |
| OCR/object observations | Vision/VisionKit | Observation versus user-approved annotation |
| Typed local proposal | Foundation Models | Model output versus deterministic mutation |
| Share/export | Transferable/ShareLink/FileDocument | Live model versus exported file |
| Local-first documents | SwiftData or file persistence | Document envelope versus PaperMarkup payload |
| Search indexing | PaperMarkup.indexableContent plus the selected indexing route | Search projection versus document truth |

Add an adjacent framework only when its responsibility is explicit.

## Failure routes

| Failure | Preserve | Recovery |
| --- | --- | --- |
| PaperKit feature unsupported | Original serialized data and source | Read-only mode or explicit migration/copy |
| Save failure | Last successful representation and unsaved model | Retry, export recovery copy, or document-provider recovery |
| Source revision changed | Proposal and source revision metadata | Discard/rebase proposal after user review |
| AI unavailable | Source selection and deterministic editor | Manual PaperKit tool route |
| Unsafe URL proposal | Text and proposal explanation | Reject link or require explicit edit/confirmation |
| Canvas bridge recreated | PaperMarkup model and document id | Reattach controller without losing state |
| Render error | Editable model | Retry with supported traits or export fallback |
| Pencil unavailable | Document and touch/pointer route | Enable alternate input and keep tools discoverable |

## Acceptance criteria

Call the route functionally ready only when the target demonstrates:

- open an identified source;
- create and edit at least one PencilKit stroke and one structured element;
- save, terminate/relaunch, and restore;
- reject and apply an AI proposal without mutation before confirmation;
- restrict an element with MarkupInteractions;
- render an approved document with recorded RenderingOptions;
- handle unsupported content without silent loss;
- use VoiceOver/keyboard/pointer or touch fallback for the intended task;
- export only the approved content;
- retain source/proposal/applied provenance.

Use the [PaperKit proof matrix](../60-verification/18-paperkit-and-markup-proof-matrix.md) to separate preview, compile, simulator, physical Pencil, accessibility, export, and release evidence.

## Sources

- [PaperKit](https://developer.apple.com/documentation/paperkit)
- [Integrating PaperKit into your app](https://developer.apple.com/documentation/paperkit/getting-started-with-paperkit)
- [PaperKit updates](https://developer.apple.com/documentation/updates/paperkit)
- [PaperMarkup](https://developer.apple.com/documentation/paperkit/papermarkup)
- [PaperMarkupViewController](https://developer.apple.com/documentation/PaperKit/PaperMarkupViewController)
- [FeatureSet](https://developer.apple.com/documentation/paperkit/featureset)
- [ShapeConfiguration](https://developer.apple.com/documentation/paperkit/shapeconfiguration)
- [MarkupInteractions](https://developer.apple.com/documentation/PaperKit/MarkupInteractions)
- [MarkupAdornment](https://developer.apple.com/documentation/paperkit/markupadornment)
- [LinkMarkup](https://developer.apple.com/documentation/PaperKit/LinkMarkup)
- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

# PaperKit and structured markup

## Scope

PaperKit is Apple’s structured-markup route for apps that need more than freehand ink. It builds on PencilKit and adds editable markup elements such as shapes, images, text boxes, links, loupes, and adornments. The framework separates the canvas/controller experience from the PaperMarkup data model, so the same annotated document can be edited, persisted, rendered, reviewed, or shared.

PaperKit is a strong fit for:

- document and PDF annotation;
- design boards and visual planning;
- handwritten notes mixed with typed labels and shapes;
- image markup and review;
- education or inspection canvases;
- AI-assisted annotation where a person approves each inserted element;
- original Apple-native canvas experiences that use system PencilKit behavior without copying Apple’s apps.

PaperKit is not a generic scene graph, a database, or an AI drawing engine. The app still owns the source document, durable record, user intent, model proposal, and export policy.

## Framework and target map

| Responsibility | PaperKit/PencilKit route | Boundary |
| --- | --- | --- |
| Store structured markup and PencilKit drawing data | PaperMarkup | Codable-like data representation and model lifecycle are separate from the source document. |
| Display and edit a canvas | PaperMarkupViewController | UIKit/AppKit controller; on iOS/iPadOS/Mac Catalyst/visionOS it is MainActor-isolated. |
| Add markup tools on iOS/iPadOS/visionOS | MarkupEditViewController | UIKit controller that presents insertion and configuration tools; use a SwiftUI representable or UIKit presentation. |
| Add a toolbar on macOS | MarkupToolbarViewController | AppKit toolbar route with its own target and layout behavior. |
| Limit supported markup features | FeatureSet | Use a matching feature set for the PaperMarkup model, canvas, and tool controller. |
| Configure shapes | ShapeConfiguration | Appearance is data; do not let arbitrary model output bypass bounds or color policy. |
| Control element actions | MarkupInteractions | Selection, move, resize, rotate, style, and delete can be restricted or made read-only. |
| Render the paper | PaperMarkup.draw(in:frame:options:) | Async rendering to CGContext; rendering traits such as dark mode and right-to-left layout are explicit. |
| Add non-document visual overlays | MarkupAdornment | Canvas adornments are separate visuals with their own anchors, drag region, identity, and zoom behavior. |
| Add an interactive URL | LinkMarkup | URL activation is a side effect and needs a safe scheme/host policy. |
| Combine freehand ink | PencilKit PKCanvasView/PKDrawing | PencilKit handles low-latency ink; PaperKit adds structured markup around or alongside it. |

The iOS target graph is commonly:

    app target
        -> SwiftUI shell
        -> UIViewControllerRepresentable bridge
        -> PaperMarkupViewController
        -> PaperMarkup + PencilKit data model
        -> document/persistence/export service
        -> optional Foundation Models / Vision / Core ML proposal layer

Keep the PaperKit bridge in a UI adapter. Keep the PaperMarkup model and source-document identifier in a feature module that can be tested without presenting UIKit.

## The PaperMarkup model

PaperMarkup can be initialized with bounds or with a serialized data representation. It exposes an ordered set of markup elements, a feature set, bounds, a content render frame, an optional indexableContent value, and an optional background color. It can:

- append another PaperMarkup model;
- append a PencilKit drawing;
- transform content with a CGAffineTransform;
- insert a ShapeConfiguration-backed shape;
- insert an image from CGImage;
- insert a line with optional end markers;
- insert a text box from AttributedString or NSAttributedString;
- remove content unsupported by a FeatureSet;
- encode itself asynchronously with dataRepresentation();
- draw asynchronously into a CGContext.

Treat PaperMarkup as a document model, not as a view model. The view controller can display and mutate the model, but the app should still decide:

- which source document or record the markup belongs to;
- when edits become durable;
- whether an AI proposal is accepted;
- whether a link may open;
- whether an export contains the original source, markup, or both;
- how a schema or feature-set change is migrated.

The model’s ordered set provides stable element identity. Use those IDs to map selection, review decisions, undo/redo events, AI provenance, and accessibility summaries. Do not identify elements by their array index because inserting or deleting markup changes order.

## View-controller lifecycle

PaperMarkupViewController is a UIKit/AppKit controller that displays the PaperMarkup canvas and exposes state such as isEditable, drawingTool, ruler state, touch modes, selection, adornments, zoom range, and content-visible frame. It is MainActor-isolated on the iOS-family route.

The controller can sit over an existing content view. For a PDF or image annotation app, place the original source content below the markup layer and let PaperKit own the structured overlay. For a blank canvas, the PaperMarkup model can be the primary content.

The critical lifecycle rules are:

1. create the PaperMarkup model with the intended bounds and FeatureSet;
2. create the PaperMarkupViewController with the same supported FeatureSet;
3. attach or configure the underlying content view;
4. present MarkupEditViewController or the macOS toolbar with a compatible FeatureSet;
5. observe model changes and schedule durable saves;
6. tear down the controller through the SwiftUI representable lifecycle when the screen disappears;
7. cancel pending persistence or rendering tasks when a document is replaced.

Do not create a new controller on every SwiftUI body update. UIViewControllerRepresentable owns creation, update, and dismantling; the coordinator or feature owner should own delegates and task cancellation.

## Feature sets and compatibility

FeatureSet is both a capability boundary and a product-design tool. Apple documents FeatureSet.empty, FeatureSet.version1, and FeatureSet.latest, along with sets of supported features, inks, shapes, line-marker positions, content version, and color exposure.

Use a feature set intentionally:

| Product | Feature-set decision |
| --- | --- |
| Read-only document viewer | Minimal set plus read-only interactions |
| PDF annotation | Drawing, shapes, text, image, and only the markup types that export correctly |
| Design board | Shapes, text, images, lines, links, and carefully bounded adornments |
| Education worksheet | Drawing and text boxes with limited rotation/deletion policy |
| AI review canvas | Read-only source, selectable proposed elements, explicit Apply action |

Use the same or compatible FeatureSet for PaperMarkup, PaperMarkupViewController, MarkupEditViewController, and MarkupToolbarViewController. If an app loads a document containing a feature the current target does not support, use removeContentUnsupported(by:) only with a clear migration or loss policy. Do not silently discard content.

When the SDK adds a new content version or markup element, store the feature-set/version in the document envelope. A document that renders on one target but loses unsupported elements on another is a migration problem, not a cosmetic fallback.

## Input and editing modes

PencilKit handles Apple Pencil and finger drawing through PKCanvasView; PaperKit adds structured selection and editing. Separate the input modes:

| Mode | Primary input | Product contract |
| --- | --- | --- |
| Draw | Pencil or finger | Strokes become PencilKit drawing data; do not reinterpret every stroke as a shape. |
| Select | Pencil, touch, pointer, keyboard | Selection identity and handles are visible and accessible. |
| Insert | Toolbar or edit controller | The new element is created with validated bounds and feature support. |
| Pan/zoom | Two-finger gesture, pointer, trackpad | Navigation should not accidentally create markup. |
| Review | Touch, pointer, VoiceOver, keyboard | Proposed elements are inspectable and can be accepted, rejected, or edited. |
| Read-only | Any navigation input | Markup interactions are read-only while the source remains protected. |

MarkupInteractions defaults to all interactions. Use readOnly or a smaller option set when the product needs to prevent deletion, rotation, style changes, or movement. This is a safety control for review surfaces, not merely a visual preference.

## Persistence and rendering

Call PaperMarkup.dataRepresentation() async throws and write the resulting Data to the app-owned document store. Loading uses PaperMarkup(dataRepresentation:). Use atomic replacement and retain the source document identifier, feature-set/version, last-edit timestamp, and a migration version outside the PaperMarkup payload.

Do not save every pointer event synchronously to disk. Observe changes, coalesce them, and schedule a cancellable save. The UI should show a meaningful state such as Saving, Saved, or Unsaved changes. A crash during a stroke must not corrupt the previous durable representation.

PaperMarkup.draw(in:frame:options:) renders the model into a CGContext asynchronously. RenderingOptions can express dark user-interface style and right-to-left layout direction, or derive appropriate options from a trait collection. Rendering is a separate artifact route:

    live editable canvas -> immutable render request -> CGContext/PDF/image destination -> user-approved export

Do not assume the live UIKit view and an exported image have the same size, color space, trait environment, or accessibility behavior. Store rendering inputs with an export record when reproducibility matters.

## Links, adornments, and side effects

LinkMarkup makes a URL tappable on the canvas. Treat it as a controlled capability:

- permit only the schemes the product supports;
- allowlist or validate hosts for AI-generated links;
- present confirmation when opening leaves the current document;
- preserve the source/provenance of the link;
- test malformed URLs and unavailable destinations;
- make link activation separate from text selection.

MarkupAdornment is useful for badges, review handles, temporary AI suggestions, and contextual overlays. It is not necessarily part of the durable document semantics. Give each adornment a stable UUID and decide whether it scales with zoom. Remove ephemeral adornments before export unless the user approved them as content.

## On-device AI route

PaperKit gives an on-device AI feature a precise insertion boundary:

    source document / ink
        -> deterministic observation (OCR, Vision, user selection, or existing markup)
        -> Foundation Models typed proposal
        -> coordinate and feature validation
        -> visible review overlay
        -> user-approved PaperMarkup mutation
        -> persistence and optional export

Useful proposals include:

- a text box summarizing a selected region;
- a shape around a recognized object;
- a cleaned-up diagram node;
- a link suggestion mapped to an existing source;
- a set of tags or labels;
- a redaction suggestion that remains uncommitted until inspected;
- a layout suggestion that moves existing elements only after confirmation.

Keep model output as a typed proposal with source ranges, document coordinate space, confidence or rationale, and a stable proposal id. Validate:

- all rectangles are inside document bounds or have an explicit crop policy;
- text size and color are legible;
- proposed URLs pass the link policy;
- the requested feature exists in the current FeatureSet;
- the proposal does not overwrite or delete user content;
- the source selection is still current;
- the user has seen the exact elements and destination before Apply.

The model must not directly call PaperMarkup insertion methods. The app’s deterministic apply command should create the markup from the reviewed proposal and record the provenance.

## Native design and accessibility

Use the PaperKit edit controller and PencilKit tool picker where their behavior matches the product. A custom toolbar is justified when the app needs a domain-specific workflow, but it should preserve the same semantic actions and undo/redo expectations.

Use Liquid Glass around app-owned navigation, document actions, review controls, and compact tool groups when it improves hierarchy. Keep the canvas itself readable and avoid putting translucent layers over active Pencil input. Glass should not obscure selection handles, ink contrast, text boxes, or the source document.

Support:

- Dynamic Type in app-owned labels and review sheets;
- VoiceOver names for tools, selected elements, proposal state, and Apply/Reject actions;
- Voice Control labels that distinguish multiple elements;
- keyboard and pointer navigation on iPad and Mac Catalyst;
- right-to-left rendering options for exported markup;
- Reduce Motion and reduced transparency for app-owned transitions;
- high contrast and color-independent state communication;
- Apple Pencil and touch fallback when Pencil hardware is unavailable.

PaperKit’s element canvas is not automatically an accessible document just because its toolbar is native. Test complete tasks: create, select, move, edit, reject, apply, save, reopen, and export.

## Availability and proof

PaperKit’s current documentation includes beta-marked data-model symbols, and the documentation says software based on preliminary APIs should be tested with final OS software. Confirm the exact iOS/iPadOS/Mac Catalyst/visionOS availability, deployment target, and SDK signatures in Xcode.

Previews and simulator runs can prove:

- SwiftUI shell layout;
- mocked PaperMarkup state;
- review and proposal UI;
- FeatureSet selection logic;
- persistence error handling with fakes;
- localization and app-owned accessibility labels.

They do not prove:

- Apple Pencil latency or hover/pressure behavior;
- touch conflict between drawing and scrolling;
- tool picker ergonomics;
- real controller lifecycle under scene changes;
- document persistence under interruption or termination;
- HDR/color-space rendering;
- physical iPad or visionOS interaction;
- export fidelity on a supported device;
- AI proposal quality on representative documents.

Use the [PaperKit proof matrix](../60-verification/18-paperkit-and-markup-proof-matrix.md) before calling an annotation or design-board route ready.

## Sources

- [PaperKit](https://developer.apple.com/documentation/paperkit)
- [Integrating PaperKit into your app](https://developer.apple.com/documentation/paperkit/getting-started-with-paperkit)
- [PaperKit updates](https://developer.apple.com/documentation/updates/paperkit)
- [PaperMarkup](https://developer.apple.com/documentation/paperkit/papermarkup)
- [PaperMarkupViewController](https://developer.apple.com/documentation/PaperKit/PaperMarkupViewController)
- [PaperMarkupViewController initializer](https://developer.apple.com/documentation/paperkit/papermarkupviewcontroller/init%28markup%3Asupportedfeatureset%3A%29)
- [PaperMarkupViewController markup](https://developer.apple.com/documentation/paperkit/papermarkupviewcontroller/markup)
- [FeatureSet](https://developer.apple.com/documentation/paperkit/featureset)
- [ShapeConfiguration](https://developer.apple.com/documentation/paperkit/shapeconfiguration)
- [RenderingOptions](https://developer.apple.com/documentation/paperkit/renderingoptions)
- [MarkupInteractions](https://developer.apple.com/documentation/PaperKit/MarkupInteractions)
- [MarkupOrderedSet](https://developer.apple.com/documentation/PaperKit/MarkupOrderedSet)
- [LinkMarkup](https://developer.apple.com/documentation/PaperKit/LinkMarkup)
- [MarkupAdornment](https://developer.apple.com/documentation/paperkit/markupadornment)
- [PaperMarkup draw](https://developer.apple.com/documentation/paperkit/papermarkup/draw%28in%3Aframe%3Aoptions%3A%29)
- [MarkupEditViewController](https://developer.apple.com/documentation/paperkit/markupeditviewcontroller)
- [MarkupToolbarViewController](https://developer.apple.com/documentation/paperkit/markuptoolbarviewcontroller)
- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

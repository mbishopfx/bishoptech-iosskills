# PencilKit strokes and on-device handwriting intelligence

PencilKit is the Apple-native route for capturing Apple Pencil or finger input as editable ink, preserving that input as a PKDrawing, and optionally turning handwritten strokes into searchable or reviewable text. It belongs beside PaperKit, not underneath it:

- PencilKit owns low-latency ink capture, tools, stroke data, rendering, and handwriting recognition.
- PaperKit owns structured markup such as text boxes, shapes, links, adornments, and document editing around ink.
- Scribble interactions let people write into non-text-input views when the product needs handwriting-to-entry behavior.
- Foundation Models, Natural Language, Vision, or Core ML may enrich a drawing after recognition, but they do not replace PencilKit’s input model.

The safe architecture is:

~~~text
PencilKit input
-> PKDrawing and stable stroke IDs
-> local persistence and rendering
-> optional on-device handwriting recognition
-> user review and correction
-> optional Spotlight/search projection or AI proposal
-> explicit domain commit
~~~

Do not treat a handwriting result as ground truth, a stroke’s force as a person attribute, or a canvas preview as proof of Pencil latency.

## Choose the narrowest Apple Pencil route

| Outcome | Route | What it owns | What remains app-owned |
| --- | --- | --- | --- |
| Freehand ink, erasing, selection, ruler, and saving a drawing | PencilKit PKCanvasView and PKDrawing | Touch/Pencil capture, system inks/tools, stroke model, rendering | Document identity, persistence, undo policy, sharing, export, and domain meaning |
| Structured annotations around ink | PaperKit plus PencilKit | Markup model, editing controllers, structured elements, and ink integration | Document lifecycle, AI review, export, compatibility, and product semantics |
| Handwriting into a custom non-text area | Scribble interactions | Pencil handwriting interaction and text insertion behavior | Input destination, validation, edit history, and fallback controls |
| Recognize a saved drawing | PKStrokeRecognizer | On-device recognition, language selection, text/search/indexable output | Language UX, correction, confidence policy, retention, indexing, and domain commit |
| Interpret a photo or camera frame | Vision/Core ML | Image observations and model inference | Capture, crop, provenance, review, and domain state |
| Generate a creative or semantic proposal | Foundation Models or another model route | Model output under availability and context limits | Prompt policy, source facts, user approval, validation, and action |

PencilKit’s handwriting recognizer is a specialized drawing-to-text route. It is not a general semantic understanding layer.

## PKCanvasView owns the input stream

PKCanvasView is a UIKit view that captures Apple Pencil or finger input and displays the result. It is also a scroll view, so the product must decide how panning, zooming, drawing, selection, and two-finger navigation interact.

Important boundaries:

- the canvas handles the touch stream and renders the selected PKTool;
- the canvas’s drawing is the current editable PKDrawing;
- the canvas delegate reports drawing changes, tool-event boundaries, selection changes, and finished rendering;
- the system tool picker changes tool and attribute state;
- a SwiftUI wrapper owns lifecycle and data flow, but UIKit still owns the canvas;
- a saved drawing is a document payload, not a screenshot and not automatically a synchronized record.

Use the delegate’s didBeginUsingTool and didEndUsingTool boundaries to distinguish an active stroke sequence from a stable point at which recognition, autosave, or indexing can begin. Drawing-did-change can be frequent; do not perform expensive recognition or a full database write on every callback.

## Drawing policy and alternate input

The current PKCanvasView route exposes a drawing policy with default, anyInput, and pencilOnly choices. The older allowsFingerDrawing property is deprecated in current documentation. Choose the policy deliberately:

| Policy | Use when | Design requirement |
| --- | --- | --- |
| default | The product should follow the system’s current Pencil interaction preference | Explain the active input affordance and test with the tool picker visible/hidden |
| anyInput | Finger and Pencil are equally valid drawing inputs | Prevent accidental marks and provide a discoverable pan/selection gesture |
| pencilOnly | Ink must be precise and finger should pan or manipulate | Provide non-Pencil alternatives for users without Pencil and assistive technologies |

Never assume Pencil is present because the app is running on iPad. Provide a touch, pointer, keyboard, Scribble, or semantic control alternative for important tasks.

## PKDrawing is the durable drawing model

PKDrawing stores the user’s strokes and can be reconstructed from a data representation. It can also generate an image for display, pasteboard, export, or sharing. Keep the model and artifact separate:

| Representation | Use | Do not infer |
| --- | --- | --- |
| PKDrawing | Editable source of truth for ink | That an image export preserves editability |
| dataRepresentation | Persistence or transfer of drawing content | That arbitrary external clients can interpret it safely |
| image(from:scale:) | Preview, thumbnail, export, or sharing artifact | That it contains stroke identity or handwriting semantics |
| strokes | Inspection, selection, recognition input, custom editing | That every stroke has domain meaning |
| requiredContentVersion | Compatibility gate for newer content | That older targets render every feature identically |

Persist the drawing with a document ID, schema/version metadata, device-independent canvas coordinate policy, last edited date, and any recognition version. If a domain record has recognized text, store the drawing and the derived text as separate fields so a newer recognizer can regenerate the latter.

Keep drawing saves atomic. A partial data representation should not overwrite the last known-good drawing. For large notebooks, use a deliberate asset/file lifecycle rather than putting unbounded drawing data into an ordinary row.

## Stroke anatomy

A PKStroke has:

- an ink that controls rendering;
- a B-spline PKStrokePath;
- transform and mask information;
- render bounds;
- a unique stroke ID in the current Swift structure;
- optional render grouping and render state for newer/beta rendering routes;
- a required content version.

A PKStrokePoint carries location, time offset, size, opacity, force, azimuth, and altitude. These describe drawing input and rendering; they are not a biometric profile. Apple documents force as a system-determined value where 1.0 represents an average touch. Do not infer identity, health, emotion, or ability from it.

Use stroke IDs for local selection and mapping, but do not assume a stroke ID is a globally stable document identity after an import, merge, or rewrite. If the app synchronizes drawings, define its own document and operation IDs.

## Programmatic stroke editing and rendering

The current PencilKit documentation includes newer APIs for manipulating substrokes and preserving render fidelity. These APIs can support:

- animated stroke reveal;
- playback of a recorded drawing;
- editing a path while retaining grain position;
- marker or watercolor wet-ink grouping;
- programmatically generated or imported strokes;
- path inspection and conversion.

When a new stroke is derived from an existing stroke, preserve its transform and render state when the visual continuity matters. Use substroke(range:) for a partial stroke rather than slicing only the path and reconstructing a visually unrelated stroke. RenderState, renderGroupID, and related APIs are Beta or SDK-sensitive in the current docs; isolate them behind an availability and compatibility layer.

Do not build a custom renderer merely to imitate the system PencilKit tool picker or ink texture. Use the system canvas and tools first. A custom renderer should have a specific need such as playback, a controlled export, an analysis overlay, or a format conversion.

## Tool picker and Apple Pencil Pro input

PKToolPicker manages a draggable palette of tools and colors. Attach it to the canvas through the first-responder lifecycle and add the canvas as an observer so tool changes update the drawing environment. The picker can contain:

- system inking, eraser, lasso, ruler, and Scribble items;
- custom tool items with identifiers, image providers, and attribute views;
- an accessory UIBarButtonItem;
- state restoration and selected-item state;
- tool-picker visibility and frame-obscured information.

The current docs note that the tool picker does not display in Mac Catalyst apps. Check platform behavior instead of assuming the iPad toolbar is portable.

Apple’s current tool-picker sample also demonstrates custom tools and Apple Pencil Pro hover/roll behavior. A hover preview is feedback, not a committed stroke. Respect the user’s hover-preview preference, provide a non-hover fallback, and do not put a modal or translucent status layer over the active writing surface.

## Scribble is an input interaction

Scribble can enable writing on a non-text-input view through PencilKit interactions. Use it when the user’s mental model is “write into this field or region,” not when the product wants a freehand drawing that happens to contain letters.

Define:

- the active writing region;
- how the user starts and ends handwriting input;
- whether strokes remain visible after conversion;
- how edits, deletion, undo, and correction work;
- what happens when recognition is unavailable or ambiguous;
- how keyboard, finger, Voice Control, and accessibility users perform the same task.

The official Scribble sample must run on a physical device with Apple Pencil. A simulator can verify layout and some interaction scaffolding, but it cannot prove the physical handwriting experience.

## On-device handwriting recognition

PKStrokeRecognizer is a current, Beta-marked actor in Apple’s documentation. It performs asynchronous on-device handwriting recognition and search over a PKDrawing. The app should create one recognizer per open drawing and keep it alive while the drawing is active.

The route:

1. Check supportedLanguages.
2. Create the recognizer with ordered preferred languages or nil for system languages.
3. Explicitly call updateDrawing with the current drawing.
4. Request recognizedText for selected stroke IDs or the full drawing.
5. Use search for word/phrase matches and bounds.
6. Use indexableContent only when building a search projection.
7. Store recognitionVersion beside persisted recognized text.
8. Regenerate stored results when the recognition version changes.

The recognizer does not automatically observe the canvas. If the app requests results without updating the drawing, it can receive stale results. The work is asynchronous, so cancel or supersede an old recognition task when the drawing changes.

### Recognized text versus indexable content

Apple distinguishes the best single interpretation returned by recognizedText from the broader indexableContent string. Indexable content may include multiple possible readings to improve search recall. Do not display indexableContent as polished prose or feed it into a command action without review.

For Spotlight:

~~~text
PKDrawing
-> PKStrokeRecognizer.indexableContent
-> CSSearchableItemAttributeSet.textContent
-> stable CSSearchableItem identifier
-> system search projection
~~~

Keep the original drawing and search projection separate. The local [Core Spotlight recipes](../70-code-recipes/66-core-spotlight-and-useractivity-recipes.md) cover the index lifecycle and deletion boundaries.

### Language and scale

Handwriting recognition is language-specific. Offer only supported languages and order them according to the product’s actual context. Apple documents that recognition works best when handwriting is scaled in points as if drawn on standard US Letter or A4 paper; unusually large or tiny writing can reduce accuracy.

Record the drawing coordinate scale and language configuration in evaluation fixtures. Do not treat a result from English handwriting as evidence for another language, script, device, zoom level, or writing style.

### Privacy boundary

Apple’s recognition article says the engine runs on-device and handwriting data does not leave the device for this recognition path. That protects the recognition operation, not every later feature. If the app indexes recognized content, syncs it, sends it to a model, exports an image, or shares a document, each route needs its own data policy.

Keep raw strokes, recognized text, indexable text, model context, and shared/exported artifacts separate. Delete derived text when the source drawing is deleted unless the product has an explicit retention policy and correction path.

## AI and action boundary

Handwriting recognition can be the observation step in an AI workflow:

~~~text
physical ink
-> on-device recognized text
-> user correction or confidence/review state
-> optional Foundation Models summary/proposal
-> deterministic validation against current domain state
-> explicit approval
-> saved action or record
~~~

Do not let a model:

- invent unreadable text;
- turn a low-confidence recognition into a completed task;
- treat an indexable-content alternate reading as the user’s chosen words;
- infer a medical, financial, legal, or identity conclusion from handwriting;
- apply a command without showing the source strokes and resolved text;
- retain raw strokes in a prompt when a corrected text projection is enough.

For high-impact actions, show the selected strokes or source drawing, the recognized text, corrections, proposal, and final action separately.

## SwiftUI and Liquid Glass boundary

PencilKit is UIKit-first. A SwiftUI app can wrap PKCanvasView with UIViewRepresentable or place a UIKit editor inside a navigation flow. The bridge should own:

- canvas creation and teardown;
- coordinator/delegate lifetime;
- binding synchronization;
- tool picker attachment;
- focus/first-responder transitions;
- drawing save/load;
- accessibility labels for app-owned controls;
- cancellation of recognition tasks.

Keep the canvas itself visually calm and direct. Use standard navigation, toolbar, inspector, and menu surfaces around it. If Liquid Glass is appropriate, limit it to app-owned actions such as Save, Search Handwriting, Review Text, Export, and Undo status. Do not place a moving glass card over active ink, selection handles, hover previews, or the system tool picker.

For a native Apple-like result:

- preserve a large drawing surface;
- keep tools discoverable but not visually dominant;
- use a compact inspector for pen attributes and recognition language;
- show a non-destructive review panel for recognized text;
- make the source drawing one tap away from any derived text or action;
- respect Dynamic Type, reduced motion/transparency, VoiceOver, Voice Control, Switch Control, keyboard, touch, and Pencil input.

## Availability and proof register

| Claim | Source/compile boundary | Runtime boundary |
| --- | --- | --- |
| PencilKit drawing | PencilKit/PKCanvasView/PKDrawing import and target compile | Physical Pencil/finger input and rendering |
| Tool picker | PKToolPicker target/platform availability | First responder, tool selection, layout, and undo behavior |
| Drawing persistence | PKDrawing dataRepresentation and reconstruction compile | Save, crash/relaunch, large drawing, migration, and export |
| Stroke manipulation | PKStroke/PKStrokePath APIs and availability | Render fidelity, playback, wet-ink continuity, performance |
| Scribble | Interaction API and target availability | Physical Apple Pencil handwriting task |
| Handwriting recognition | PKStrokeRecognizer availability/Beta boundary and language register | Physical drawing, language fixture, scale, latency, result quality |
| Spotlight projection | Core Spotlight indexing route and stable IDs | Search result appearance, updates, deletion, and privacy |
| AI enrichment | Model availability, typed proposal, source policy | Review, correction, validation, and action evidence |
| Distribution | Signed target, current SDK, Beta policy, metadata | TestFlight/App Store/device behavior in the actual route |

## Sources

- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview?language=objc%3A)
- [PKCanvasViewDelegate](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdelegate)
- [PKCanvasViewDrawingPolicy](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdrawingpolicy)
- [PKDrawing](https://developer.apple.com/documentation/pencilkit/pkdrawing-swift.struct?language=objc)
- [PKStroke](https://developer.apple.com/documentation/pencilkit/pkstroke-swift.struct?changes=_3)
- [PKStrokePath](https://developer.apple.com/documentation/pencilkit/pkstrokepathreference?language=objc)
- [PKStrokePoint](https://developer.apple.com/documentation/pencilkit/pkstrokepoint-swift.struct)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker?changes=_1)
- [Drawing with PencilKit](https://developer.apple.com/documentation/pencilkit/drawing-with-pencilkit?changes=_2_7)
- [Configuring the PencilKit tool picker](https://developer.apple.com/documentation/pencilkit/configuring-the-pencilkit-tool-picker)
- [Customizing Scribble with Interactions](https://developer.apple.com/documentation/PencilKit/customizing-scribble-with-interactions)
- [Inspecting, Modifying, and Constructing PencilKit Drawings](https://developer.apple.com/documentation/PencilKit/inspecting-modifying-and-constructing-pencilkit-drawings)
- [Controlling stroke rendering for animation and editing](https://developer.apple.com/documentation/pencilkit/controlling-stroke-rendering-for-animation-and-editing?changes=latest_minor%2Clatest_minor)
- [PKStrokeRecognizer](https://developer.apple.com/documentation/pencilkit/pkstrokerecognizer?changes=_1)
- [Recognizing handwriting and converting it to text](https://developer.apple.com/documentation/pencilkit/recognizing-handwriting-and-converting-to-text?changes=_1)
- [Building a handwriting recognition experience with PencilKit](https://developer.apple.com/documentation/pencilkit/building-a-handwriting-recognition-experience-with-pencilkit?changes=latest_bet___5&language=objc)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

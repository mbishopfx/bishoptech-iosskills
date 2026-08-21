# Structured markup and Pencil canvas design

## Design goal

A native markup canvas should feel direct before it feels clever:

    source content -> mark -> select -> edit -> review -> save -> share

PaperKit gives the app a structured canvas, but the product still decides whether the canvas is a document, a review surface, a design board, or a temporary annotation layer. Start with that decision. The same PaperMarkup element can be useful in one mode and confusing in another.

The target is Apple-native behavior with an original product identity:

- PencilKit handles expressive ink and low-latency drawing;
- PaperKit handles editable structured markup;
- SwiftUI owns the surrounding navigation, state, and review surfaces;
- UIKit/AppKit bridges are kept at the canvas boundary;
- Liquid Glass groups app-owned actions without covering the content being edited.

## Four canvas modes

| Mode | Visual hierarchy | Primary action | Risk to control |
| --- | --- | --- | --- |
| Browse | Source content first, quiet annotation indicator | Select or open | Accidental editing |
| Annotate | Source plus visible ink/markup affordance | Draw or insert | Losing source context |
| Edit | Selected element, handles, contextual tools | Move/resize/style | Tool overload and hidden state |
| Review | Proposed or changed elements highlighted | Accept, reject, inspect | Treating suggestions as truth |

Do not put all four modes into one permanently visible toolbar. Use state-driven actions and keep the current mode legible.

## Canvas composition

A reliable composition is:

    document viewport
        -> PaperKit markup layer
        -> selection/context layer
        -> transient adornments
        -> app-owned navigation and review controls

The source document should remain visually stable while a person marks it. Selection handles and review overlays should be visually distinct from durable content. A proposed AI rectangle should not look identical to a user-created rectangle until it is applied.

Recommended state treatments:

| State | Content treatment | Control treatment |
| --- | --- | --- |
| Read-only | Calm, no editing handles | One obvious Edit action |
| Drawing | Preserve ink contrast and source visibility | Tool picker or compact native tools |
| Selected | Strong selection affordance without a heavy modal | Contextual actions near the selected element |
| Proposed | Subtle distinct outline or badge | Apply, Reject, Inspect |
| Applied | Same visual language as user-created content | Undo remains available |
| Saving | Keep canvas responsive; show a small status | Avoid blocking the entire document for every stroke |
| Unsupported content | Preserve visible warning and recovery path | Export or migrate only after user understands loss |

## Liquid Glass boundaries

Liquid Glass belongs around functional app-owned controls, not inside the content model:

Good placements:

- a navigation bar containing Back, document title, and Share;
- a compact tool group that expands from a selected element;
- a review bar with Apply and Reject;
- an inspector sheet that morphs from a selected markup item;
- a floating “Add markup” action that does not cover the active writing area.

Poor placements:

- a full-screen translucent layer over a busy PDF;
- a glass card under the Pencil tip that changes the canvas contrast;
- a custom glass recreation of the system PencilKit tool picker;
- animated blur behind an AI proposal that makes its bounds difficult to inspect;
- a glass button that looks enabled while the PaperMarkup save is still pending.

Glass must not be the only state signal. Pair material with text, selection, position, semantic labels, and a predictable action. When reduced transparency or high contrast is enabled, an opaque or less layered fallback should preserve the same hierarchy.

## Tool hierarchy

FeatureSet is a design decision. Give the person the tools needed for the job:

| Product type | Start with | Add only when validated |
| --- | --- | --- |
| PDF reviewer | Pen, highlighter/ink, text box, shape, undo/redo | Links, signatures, loupes, complex adornments |
| Visual planning board | Shapes, lines, images, text, move/resize/rotate | Freeform links, AI layout proposals, shared cursors |
| Handwritten notebook | PencilKit ink, eraser, lasso, text box | Structured shape recognition and automatic cleanup |
| Inspection form | Text boxes, check marks, arrows, image callouts | Link actions or model-generated annotations |
| AI review canvas | Read-only source plus proposed elements | Apply mutations, deletions, or external links only after review |

Avoid exposing every available PaperKit feature because it exists. A smaller FeatureSet makes the tool palette learnable and makes document compatibility easier to explain.

## Apple Pencil and alternate input

Design for the full input matrix:

| Input | Must work | Design note |
| --- | --- | --- |
| Apple Pencil | Draw, select, hover/preview where supported | Keep the active stroke direct and low-latency; don’t put a modal over the canvas. |
| Finger | Pan, select, draw when enabled by the product | Separate panning from drawing to prevent accidental marks. |
| Pointer/trackpad | Select, resize, move, scroll, invoke tools | Provide visible hover/focus feedback without changing the document. |
| Keyboard | Undo/redo, delete, move, tool shortcuts, focus | Maintain a sensible focus order and do not trap focus in the canvas. |
| VoiceOver | Discover canvas state and selected element | Expose meaningful labels and actions; test complete edit tasks. |
| Voice Control/Switch Control | Activate visible actions | Avoid multiple identical “Apply” labels without context. |

The canvas can be rich and still need a text-first fallback. Offer an inspector or list of elements so someone who cannot draw or precisely manipulate handles can understand and edit the document.

## AI proposal design

An AI-enhanced canvas should make the source, proposal, and applied markup visually different:

    source content
      -> selected region
      -> proposed overlay
      -> review inspector
      -> user-approved markup

Show:

- what source region produced the proposal;
- what element type will be inserted;
- exact text, shape, link, or color;
- why the proposal exists in plain language;
- whether it will change or only add content;
- how to undo or reject it.

For a diagram cleanup feature, show the proposed lines and nodes as a separate layer. For a summary text box, show the exact text and source range. For an AI link, show the destination before opening it.

Avoid claiming that a recognition result is an objective fact. OCR, Vision, and Foundation Models can provide observations or proposals; the person decides what becomes a durable document element.

## Selection and review

Selection should preserve identity as the document changes. Use stable markup IDs, not screen positions or collection indexes. A selection inspector can contain:

- element type and source;
- bounds and rotation;
- text or link destination;
- allowed interactions;
- proposal provenance;
- Apply/Reject/Undo actions;
- accessibility description.

When an AI proposal is applied, keep undo available and show a small “Added by suggestion” provenance affordance until the person dismisses it. Do not require the person to trust an invisible model event.

## Persistence feedback

Markup editing can generate many changes. The design should distinguish:

- Editing: the current canvas is responsive;
- Saving: a durable representation is being written;
- Saved: the latest durable representation matches the canvas;
- Save failed: the prior saved version is intact and retry is available;
- Exporting: a separate artifact is being generated;
- Exported: the destination accepted the artifact.

Do not show a generic checkmark immediately after a stroke. If the app promises durable local-first editing, make the save boundary observable without interrupting the drawing flow.

## Document and export surfaces

The live canvas and a rendered export are different products:

| Surface | Optimize for |
| --- | --- |
| Live edit | Selection, direct input, undo, zoom, tool discovery |
| Preview | Fast recognition of what will be exported |
| PDF/image export | Stable bounds, color/trait choice, content completeness |
| Share | User-approved destination and file lifetime |
| Reopen | Document identity, feature compatibility, and recovery |

Keep export controls outside the active drawing region. A glass Share button can sit in a toolbar; the paper itself should not become a decorative glass card that changes the exported meaning.

## Accessibility and internationalization

PaperKit’s native controllers help with system behavior, but they do not automatically make a custom canvas workflow accessible. Test:

- Dynamic Type in surrounding UI and inspectors;
- VoiceOver element discovery, selection, and review actions;
- Voice Control names and disambiguation;
- Switch Control and keyboard action order;
- right-to-left rendering and text-box direction;
- localized tool labels and long text;
- high contrast and reduced transparency;
- reduced motion for selection and proposal transitions;
- color-independent distinctions between source, proposal, and applied elements.

For a rapidly changing canvas, avoid announcing every pointer or selection frame. Announce meaningful state transitions: selection changed, proposal ready, applied, rejected, saved, or save failed.

## Cross-platform adaptation

On iPhone, use a focused editor and a compact tool route. On iPad, use a larger canvas with a toolbar or popover inspector. On Mac Catalyst, support pointer and keyboard-first editing and remember that PencilKit’s tool picker has platform-specific behavior. On visionOS, validate the spatial interaction model and avoid assuming that a 2D overlay feels comfortable in a spatial window.

Share the PaperMarkup model and proposal validator across platforms, but let each target own:

- tool presentation;
- navigation;
- pointer/touch/Pencil behavior;
- inspector placement;
- export destination;
- accessibility choreography.

## Design stop conditions

Pause the design if:

- the user cannot tell whether an element is a proposal or applied content;
- a glass layer reduces source or ink legibility;
- the app silently drops an unsupported PaperKit element;
- the tool palette exposes more actions than the product can explain;
- the canvas has no keyboard or accessible review path;
- an AI action can delete or overwrite markup without confirmation;
- the only save feedback is a transient animation;
- the exported artifact is assumed to match the live canvas without a render proof.

The [PaperKit framework deep dive](../41-framework-deep-dives/09-paperkit-and-structured-markup.md), [capability route](../50-capability-recipes/24-paperkit-reviewable-markup-route.md), [proof matrix](../60-verification/18-paperkit-and-markup-proof-matrix.md), and [code recipes](../70-code-recipes/36-paperkit-and-markup-recipes.md) turn this design contract into implementation and evidence work.

## Sources

- [PaperKit](https://developer.apple.com/documentation/paperkit)
- [Integrating PaperKit into your app](https://developer.apple.com/documentation/paperkit/getting-started-with-paperkit)
- [PaperKit updates](https://developer.apple.com/documentation/updates/paperkit)
- [PaperMarkup](https://developer.apple.com/documentation/paperkit/papermarkup)
- [PaperMarkupViewController](https://developer.apple.com/documentation/PaperKit/PaperMarkupViewController)
- [FeatureSet](https://developer.apple.com/documentation/paperkit/featureset)
- [MarkupInteractions](https://developer.apple.com/documentation/PaperKit/MarkupInteractions)
- [MarkupAdornment](https://developer.apple.com/documentation/paperkit/markupadornment)
- [LinkMarkup](https://developer.apple.com/documentation/PaperKit/LinkMarkup)
- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)

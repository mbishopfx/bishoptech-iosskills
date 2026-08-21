# Pencil canvas and handwriting-review design

An Apple Pencil canvas should feel like a direct surface for thought, not a web form with a drawing layer glued on top. The design has two related but distinct moments:

1. low-latency input, where the canvas and tool picker stay out of the way;
2. derived-text review, where recognized handwriting becomes editable content that the person can correct before it powers search, AI, or an action.

Use this composition:

~~~text
large canvas
-> system tools and clear input policy
-> subtle save/search affordances
-> explicit recognition request or end-of-stroke pause
-> source strokes beside recognized text
-> correction and approval
-> optional system/search/AI projection
~~~

## Canvas-first hierarchy

The canvas is the content. Everything else is support:

- title and document identity in the navigation region;
- undo/redo and save state in standard controls;
- tool picker or compact tools in a system-appropriate location;
- selection and lasso state near the canvas;
- handwriting search/review in a secondary panel or sheet;
- AI proposals in a review surface that keeps source strokes visible.

Avoid permanently floating a dense control bar over the writing area. A person should be able to write, pan, zoom, select, erase, and undo without hunting through decoration.

## Input policy as visible product behavior

The drawing policy changes the meaning of touch:

| Policy | Canvas gesture | Finger gesture | Required explanation |
| --- | --- | --- | --- |
| default | Follows the system’s current Pencil behavior | System-dependent | Show the selected tool/policy when it matters |
| anyInput | Draws with Pencil or finger | Draws | Provide an intentional pan/selection affordance |
| pencilOnly | Draws with Pencil | Pan/manipulate rather than ink | Offer a touch/pointer/keyboard alternative for important actions |

Do not let a user discover the policy only after an accidental mark. If a drawing surface supports both ink and pan, show the gesture rule near first use and keep it accessible through Help or an inspector.

## Tool picker and custom tools

Prefer the PencilKit tool picker for standard pen, pencil, marker, eraser, lasso, ruler, and Scribble behaviors. A custom tool belongs in the picker when it has a clear, repeatable task such as a stamp, signature, or domain-specific mark.

Custom tool design rules:

- give the tool a stable identifier;
- provide a localized name and a recognizably distinct icon;
- expose attributes in the system tool attributes area;
- keep its action undoable;
- preserve the selected tool when the document changes;
- avoid making a custom tool look like a standard tool with different side effects;
- ensure the tool remains understandable with VoiceOver and Dynamic Type;
- supply a non-hover path for users without Pencil Pro.

Do not rebuild the entire system picker as a custom Liquid Glass control group. The system picker has platform-specific behavior, can be moved by the person, and has a different role from app-owned document actions.

## Handwriting review anatomy

When recognition produces text, show the source and derived value together:

| Region | Content | Interaction |
| --- | --- | --- |
| Source | Selected strokes or a visible crop of the drawing | Tap to return to the canvas and adjust selection |
| Recognition | Current recognized text, language, and stale/reprocessing state | Edit directly; preserve corrections |
| Confidence/context | Short explanation such as “Recognized from 3 strokes” | Do not invent a numeric confidence if the API did not provide one |
| Action | Copy, insert, search, create draft, or index | Require confirmation for external or consequential effects |
| Provenance | Drawing ID, recognition version, and last updated state | Make it inspectable when the text matters |

If no text is recognized, keep the source strokes and explain the next action: select clearer strokes, choose a supported language, enlarge the writing, or type instead. Never replace the source with an empty result.

## Recognition timing

Recognition can be expensive and asynchronous. Choose a timing policy:

| Policy | Best for | Tradeoff |
| --- | --- | --- |
| explicit “Recognize” | Journaling, notes, forms, privacy-sensitive work | One extra action, clear user intent |
| after end-of-stroke pause | Short labels or handwriting search | Needs debounce and stale-result handling |
| document close/background | Large notebooks | Text is delayed but energy is bounded |
| selection-only | Copy-as-text or search | Avoids interpreting unrelated ink |

Do not run full-drawing recognition on every drawing-did-change callback. Keep a generation or cancellation token so an older result cannot overwrite newer strokes.

## Search and Spotlight

Searching a drawing is not the same as displaying recognized text:

- search results can return matching stroke IDs and bounds for highlighting;
- indexable content can include alternate readings to improve recall;
- recognizedText is a single likely interpretation and may be nil;
- Spotlight receives a projection with its own lifecycle, identity, and deletion policy.

Use visual highlight bounds in the canvas and keep the search field accessible. If a result came from indexable content, return the user to the source drawing before offering an edit or action.

## Liquid Glass around ink

Liquid Glass is most useful around app-owned controls and state, not under active handwriting:

- keep the canvas surface visually stable and high contrast;
- use standard navigation bars, toolbars, inspectors, and sheets;
- group Save, Search, Recognize, and Review actions when that grouping helps;
- keep glass away from selection handles and active strokes;
- do not use an animated glass morph to interrupt a writing gesture;
- let the system tool picker keep its own presentation;
- avoid translucent overlays that reduce ink contrast or make a sheet look like canvas content.

For a review panel, use a compact material or glass group to separate actions from the source drawing. Make the recognized text itself readable and editable. The source stroke crop should remain available, especially when an AI proposal depends on the text.

## AI-assisted creative workflow

The review design should show exactly where AI enters:

~~~text
handwritten strokes
-> on-device recognized text
-> person correction
-> AI summary, translation, classification, or action proposal
-> source-linked review
-> explicit apply
~~~

Useful app-owned actions:

- “Summarize these corrected notes.”
- “Translate the selected text.”
- “Turn the checked items into a draft list.”
- “Search this notebook for the handwritten word.”

Unsafe shortcuts:

- silently treating every stroke as a task;
- sending raw ink to a model when corrected text is enough;
- turning an ambiguous word into a financial, medical, or security action;
- hiding the source drawing after an AI rewrite;
- treating model output as a persisted user decision.

Keep the original drawing and corrected text visible when the distinction matters. Use a proposal card with source, explanation, edit, and Apply actions. Apply should write through a deterministic domain command, not through the model.

## Accessibility and alternate input

Drawing is not accessible merely because the canvas has a label. Provide alternate routes for every important operation:

- semantic Undo, Redo, Clear, Select, Search, Recognize, and Export controls;
- text editing for recognized content;
- keyboard shortcuts and pointer support where the platform supports them;
- Voice Control names for tools and actions;
- VoiceOver focus that moves from the source selection to recognized text and action;
- Switch Control order that does not require precise freehand input;
- Dynamic Type for review text and settings;
- Reduce Motion and Reduce Transparency handling;
- visual state indicators that do not depend on color alone.

If the canvas is the only way to enter a value, the product should justify that choice. A “type instead” route is often the correct fallback.

## iPad, iPhone, and Mac Catalyst

| Platform | Design emphasis | Validation |
| --- | --- | --- |
| iPad | Large canvas, tool picker, multitasking, Pencil and pointer coexistence | Physical iPad with Pencil, touch, keyboard/pointer, rotation, split/window sizes |
| iPhone | Focused drawing region, compact controls, finger-first fallback, optional Pencil | Physical device with intended input and Dynamic Type |
| Mac Catalyst | Pointer/keyboard and document editing, custom toolbar where tool picker is absent | Mac Catalyst target with menu/shortcut and layout proof |
| visionOS or other target | Do not assume a flat canvas is spatially comfortable | Target-specific interaction and comfort review |

Do not claim the iPad tool picker or Pencil hover experience on Mac Catalyst. Do not make iPhone users discover a tiny canvas designed only for iPad.

## Design review checklist

- [ ] The canvas is the visual and interaction anchor.
- [ ] The drawing policy is intentional and understandable.
- [ ] Standard PencilKit tools are used before custom tools.
- [ ] The tool picker does not obscure active ink or essential actions.
- [ ] Recognition timing is explicit, bounded, and cancellable.
- [ ] Source strokes, recognized text, corrections, AI proposals, and applied actions are distinct.
- [ ] Indexable content is not displayed as authoritative prose.
- [ ] Liquid Glass groups app-owned controls without reducing ink legibility.
- [ ] VoiceOver, Voice Control, Switch Control, keyboard, pointer, Dynamic Type, reduced motion, and reduced transparency have task paths.
- [ ] Physical Apple Pencil evidence is recorded separately from simulator or preview evidence.

## Sources

- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview?language=objc%3A)
- [PKCanvasViewDrawingPolicy](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdrawingpolicy)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker?changes=_1)
- [Configuring the PencilKit tool picker](https://developer.apple.com/documentation/pencilkit/configuring-the-pencilkit-tool-picker)
- [Customizing Scribble with Interactions](https://developer.apple.com/documentation/PencilKit/customizing-scribble-with-interactions)
- [PKStrokeRecognizer](https://developer.apple.com/documentation/pencilkit/pkstrokerecognizer?changes=_1)
- [Recognizing handwriting and converting it to text](https://developer.apple.com/documentation/pencilkit/recognizing-handwriting-and-converting-to-text?changes=_1)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

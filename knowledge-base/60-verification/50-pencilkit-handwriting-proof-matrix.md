# PencilKit and handwriting-intelligence proof matrix

PencilKit features cross input hardware, UIKit lifecycle, editable drawing data, optional on-device recognition, search indexing, accessibility, and sometimes AI. Prove those boundaries separately.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| PencilKit compiles in the target | Selected SDK import and target build | A source snippet or framework page |
| Canvas captures Pencil | Physical supported iPad/iPhone with Apple Pencil drawing fixture | Finger drawing, Simulator, or preview |
| Canvas policy is correct | Test default/anyInput/pencilOnly with the intended touch behavior | A property assignment |
| Tool picker works | Physical UI run with first responder, tool selection, undo, and picker placement | A custom toolbar mock |
| Drawing persists | Save dataRepresentation, terminate/relaunch, restore PKDrawing, compare/edit | A non-nil Data value |
| Drawing remains editable | Restore drawing and add/erase/select/undo strokes | An exported image |
| Stroke IDs are handled | Selection/search/action mapping survives the tested document lifecycle | Treating an ID as a global document identity |
| Scribble works | Physical Apple Pencil task in the intended custom interaction region | A text field test or Simulator |
| Recognition language is supported | PKStrokeRecognizer.supportedLanguages on the target device/OS | Assuming device locale means recognizer support |
| Recognition result is fresh | updateDrawing for the current revision before recognizedText/search | Calling recognizedText after the canvas changed |
| Recognition quality is acceptable | Representative language, scale, handwriting, selection, and correction fixtures | One legible English phrase |
| Recognition is on-device for this route | Runtime evidence and source contract for PKStrokeRecognizer | Assuming every later AI/index/share route is on-device |
| Indexing is correct | Core Spotlight add/update/delete and source return | Indexable content displayed as final text |
| AI proposal is safe | Source strokes, corrected text, proposal, validation, and approval trace | A generated summary or action string |
| Stroke playback preserves visual fidelity | Physical render comparison for substroke/render-state/wet-ink cases | A path animation that looks plausible |
| Accessibility works | VoiceOver, Voice Control, Switch Control, keyboard/pointer, Dynamic Type, reduced effects | Labels in source or preview |
| Distribution works | Signed release/TestFlight target with the exact APIs and resources | Debug device run |

## Target configuration record

| Field | Value |
| --- | --- |
| App target |  |
| SDK/deployment target |  |
| PencilKit availability |  |
| UIKit/SwiftUI bridge |  |
| Canvas drawing policy |  |
| Tool picker platform |  |
| Drawing schema/version |  |
| Recognition API/Beta state |  |
| Supported language set |  |
| recognitionVersion |  |
| Drawing coordinate scale |  |
| Core Spotlight indexing |  |
| Model enrichment |  |
| Release build |  |

## Physical input matrix

| ID | Device/input | Action | Expected result |
| --- | --- | --- | --- |
| I01 | Supported iPad + Apple Pencil | Draw short and long strokes | Low-latency ink appears; drawing changes are reported |
| I02 | Same | Change pen/eraser/lasso/ruler in tool picker | Current tool and drawing behavior update |
| I03 | Same | Draw while scrolling/zooming | Gesture policy is understandable and stable |
| I04 | Same | Select strokes and invoke recognition | Selected stroke IDs are used; source remains visible |
| I05 | Same | Draw, background/terminate, relaunch | Drawing restores without replacing it with a preview |
| I06 | Same | Use supported and unsupported language choices | Language list is honest and results are labeled |
| I07 | Same | Write at normal page scale and extreme zoom | Scale limitation is recorded; no universal quality claim |
| I08 | Device without Pencil | Use finger/pointer/keyboard/typed route | Important tasks remain possible |
| I09 | VoiceOver | Navigate canvas controls and review panel | Source, text, action, and state are understandable |
| I10 | Reduce Motion/Transparency | Open review and save/search states | No essential meaning depends on effect |

## Recognition fixture matrix

Record the drawing source and expected behavior without claiming a universal accuracy score:

| Fixture | Variables |
| --- | --- |
| clear block letters | language, scale, stroke selection |
| cursive note | connected strokes, correction workflow |
| numerals and symbols | ambiguity such as 0/O or 1/l, action safety |
| mixed-language note | preferred language order and supported set |
| rotated or zoomed writing | coordinate transform and quality change |
| partial selection | selected IDs and recognizedText scope |
| empty/mark-only drawing | nil result and no false text |
| updated drawing | stale-result cancellation and re-run |
| recognition-version change | stored result regeneration |

For every fixture, store the target device/OS, SDK, drawing scale, requested languages, recognizer version, result, correction, and whether the result was used for indexing or an action.

## Persistence and rendering evidence

Verify:

- the data representation can be written and reconstructed;
- a corrupted or partial write leaves the last good drawing intact;
- large drawings do not block the main actor or produce an unusable save;
- the preview image is derived from the drawing and can be regenerated;
- requiredContentVersion is checked before opening imported content;
- transform and coordinate policy remain stable across screen sizes;
- programmatic edits preserve render state where required;
- marker/wet-ink grouping is tested when used;
- custom tools have stable identifiers and localized labels;
- Mac Catalyst has a deliberate tool route because the system tool picker does not display there.

## Search and AI evidence

If the feature indexes handwriting:

1. Update the recognizer with the current drawing.
2. Generate indexable content.
3. Index a stable item ID and source link.
4. Search and return the user to the drawing.
5. Update when drawing changes.
6. Delete when the record is deleted or no longer searchable.

If the feature uses AI:

1. Capture source stroke IDs and drawing revision.
2. Produce recognized text.
3. Let the person correct it.
4. Record model availability and input facts.
5. Generate a typed proposal.
6. Show source, corrected text, proposal, and action scope.
7. Require approval.
8. Revalidate the current record before committing.

Do not use an indexable-content alternate reading as the sole input for a consequential action.

## Privacy evidence

Check:

- raw drawings are stored only where the product expects;
- recognition results include an engine version and are deletable;
- search indexing is opt-in/product-authorized and removed with the source;
- model prompts contain only the minimum corrected text needed;
- exports/share sheets make the destination visible;
- logs do not contain raw strokes or handwritten personal content;
- a person can find and delete both the source and derived projections;
- correction history does not retain deleted raw text accidentally.

## Release evidence vocabulary

| Label | Meaning |
| --- | --- |
| source | Official PencilKit route and API notes |
| compile | Named target builds with selected SDK |
| simulator | Layout and mock behavior only; no physical Pencil claim |
| signed device | Exact signed app ran on a physical input device |
| recognition | Current PKStrokeRecognizer result on named language/fixture |
| search | Core Spotlight projection was updated and found |
| accessibility | Task-based assistive-technology evidence |
| distribution | Signed/TestFlight artifact retained configuration |
| release | Actual destination/store/environment evidence |

## Evidence record template

~~~yaml
route: PencilKit-Handwriting
build:
  app_version: ""
  build_number: ""
  sdk: ""
  deployment_target: ""
target:
  name: ""
  canvas_policy: default-anyInput-pencilOnly
  swiftui_bridge: ""
  tool_picker: ""
drawing:
  document_id: ""
  drawing_revision: ""
  data_size: 0
  required_content_version: ""
  persisted_and_restored: false
input:
  device: ""
  os: ""
  pencil_model: ""
  fixture: ""
recognition:
  api: PKStrokeRecognizer
  beta_state: ""
  languages: []
  recognition_version: 0
  updated_drawing_before_request: false
  recognized_text: ""
  corrected_text: ""
  indexable_content_used: false
search:
  indexed: false
  updated: false
  deleted: false
ai:
  used: false
  proposal: ""
  approval: ""
  committed: false
accessibility:
  voiceover: ""
  voice_control: ""
  switch_control: ""
  dynamic_type: ""
  reduced_effects: ""
release:
  signed_artifact: ""
  environment: ""
  result: ""
known_limits: []
~~~

## Sources

- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview?language=objc%3A)
- [PKCanvasViewDelegate](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdelegate)
- [PKCanvasViewDrawingPolicy](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdrawingpolicy)
- [PKDrawing](https://developer.apple.com/documentation/pencilkit/pkdrawing-swift.struct?language=objc)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker?changes=_1)
- [PKStroke](https://developer.apple.com/documentation/pencilkit/pkstroke-swift.struct?changes=_3)
- [PKStrokePoint](https://developer.apple.com/documentation/pencilkit/pkstrokepoint-swift.struct)
- [PKStrokeRecognizer](https://developer.apple.com/documentation/pencilkit/pkstrokerecognizer?changes=_1)
- [Recognizing handwriting and converting it to text](https://developer.apple.com/documentation/pencilkit/recognizing-handwriting-and-converting-to-text?changes=_1)
- [Building a handwriting recognition experience with PencilKit](https://developer.apple.com/documentation/pencilkit/building-a-handwriting-recognition-experience-with-pencilkit?changes=latest_bet___5&language=objc)
- [Controlling stroke rendering for animation and editing](https://developer.apple.com/documentation/pencilkit/controlling-stroke-rendering-for-animation-and-editing?changes=latest_minor%2Clatest_minor)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

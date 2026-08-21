# PaperKit and markup proof matrix

## Evidence rule

PaperKit combines a UIKit/AppKit controller, a structured model, PencilKit input, optional SwiftUI interop, document persistence, rendering, and possible AI or export routes. Verify the model, controller, target, input, persistence, and artifact separately. A PaperMarkup that renders in a preview is not proof that Apple Pencil input, a feature-set migration, or a physical export works.

Use the [source review checklist](00-source-review-checklist.md), [build/device/release checklist](01-build-device-and-release-checklist.md), and [physical-device capability proof matrix](07-physical-device-capability-proof-matrix.md) when a route crosses targets or hardware.

## Proof ladder

| Layer | What it proves | What it does not prove |
| --- | --- | --- |
| Official source review | PaperKit symbols, feature-set model, controller/target split, beta/API caveats, PencilKit behavior | The selected app target compiles or a person can complete the task |
| Compile | Imports, availability, MainActor isolation, UIKit bridge signatures, resources | Pencil latency, persistence durability, rendering fidelity, or device ergonomics |
| Unit tests | Feature-set compatibility, proposal validation, coordinate transforms, URL policy, envelope/version rules | Controller input, system tool picker, real rendering, or AI quality |
| SwiftUI preview | App-owned shell, review/proposal states, fallback labels, mock model | PaperKit controller lifecycle, Pencil input, accessibility task completion |
| Simulator | App navigation, mock persistence, some UIKit bridge and touch behavior | Apple Pencil hardware, hover/pressure, latency, physical export color, visionOS comfort |
| Signed iPad/iPhone device | Pencil/touch interaction, controller lifecycle, save/reopen, physical rendering, accessibility settings | Every OS/device, App Store distribution, universal input ergonomics |
| Mac Catalyst/macOS/visionOS target | Target-specific toolbar/controller/input behavior | iOS Pencil behavior or identical system surfaces |
| TestFlight/release build | Signing, target/resource membership, entitlements, optimization, install path | App Review approval, all hardware, production document/provider conditions |

## Matrix

| Capability or risk | Minimum method | Evidence to retain | Not proven by |
| --- | --- | --- | --- |
| PaperKit linked to the intended target | Build the named app target with the selected SDK | Build output, target membership, deployment target, framework linkage | A recipe or Xcode project screenshot |
| Controller isolation | Compile PaperMarkupViewController and the bridge under the selected concurrency settings | Compiler diagnostics, MainActor boundary notes, adapter tests | Moving code into a detached task |
| Compatible FeatureSet | Unit-test model/controller/edit/toolbar feature-set compatibility | Feature list, version/content policy, unsupported-content test | Using FeatureSet.latest without a migration plan |
| New PaperMarkup model | Unit test bounds, feature set, empty state, stable document id | Fixture and serialized envelope | A blank canvas preview |
| Data representation round trip | Save dataRepresentation, reload PaperMarkup(dataRepresentation:), compare elements/metadata | Byte/file record, element IDs, version, equality result | Seeing the same canvas before termination |
| Corrupt data | Load malformed/truncated/unsupported data | Error category, recovery UI, preserved last-good copy | Catching an error without recovery |
| Coalesced saves | Draw/edit repeatedly and interrupt/cancel a save | Save task log, latest-model guarantee, saved/unsaved UI | Synchronous save after one button tap |
| Process termination/relaunch | Edit, background/terminate, relaunch, restore | Device/OS, document id, last-saved timestamp, restored elements | Preview state restoration |
| Controller recreation | Change SwiftUI identity/scene phase and reattach model | No duplicate delegates, no lost edits, task cancellation evidence | Creating a controller in body |
| PencilKit drawing | Physical iPad with Apple Pencil, draw/erase/undo/redo | Device/Pencil model, input recording, stroke result | Finger drawing in Simulator |
| Finger and touch fallback | Device without Pencil or with drawing policy set intentionally | Pan/draw/select results, accidental-mark test | Assuming PKCanvasView defaults fit the product |
| Pencil tool picker | Physical iPad, compact and regular layout | Tool visibility, first responder, undo/redo, tool state | A static toolbar mock |
| Structured shape insertion | Insert shape with supported ShapeConfiguration | Element id, bounds, style, reopen result | A drawn rectangle that is not a shape element |
| Text box insertion | Insert AttributedString/NSAttributedString with long/localized text | Typography, bounds, direction, reopen/render result | English short text |
| Image insertion | Add a known CGImage at bounds/rotation | Pixel/orientation/scale evidence, source provenance | A placeholder image view |
| Lines and markers | Insert lines with start/end markers | Shape configuration, marker behavior, export | A SwiftUI path unrelated to PaperMarkup |
| Selection and stable identity | Move/delete/reorder elements and restore selection mapping | Markup IDs, selected-element state, UI evidence | Collection index mapping |
| MarkupInteractions restrictions | Test all, readOnly, and reduced action sets | Attempted move/resize/rotate/style/delete outcomes | Hiding a button while the element remains mutable |
| LinkMarkup safety | Tap valid, malformed, disallowed-scheme, and disallowed-host links | Policy decision, confirmation, destination result | Rendering link text |
| Adornment lifecycle | Add, move, zoom, remove, and export with/without adornments | UUID, anchor, drag region, scale policy, artifact decision | Treating a transient overlay as durable content |
| Source coordinate transform | Use known bounds/orientation fixtures and insert at observed regions | Transform math, expected frames, visual overlay | Same-size image preview |
| OCR/Vision observation | Run representative document/image fixtures | Observation source, revision, crop, confidence/provenance | Model text without source coordinates |
| AI typed proposal | Model available/unavailable/invalid/ambiguous fixtures | Schema/prompt/model version, proposal id, validation result | A plausible generated annotation |
| No AI mutation before approval | Trace from proposal generation to Apply | No PaperMarkup insertion before confirmation, audit event after | Code inspection without runtime trace |
| AI proposal applies safely | Accept/reject/undo and stale-source cases | Applied element IDs, source revision, undo result | A proposal overlay that looks correct |
| Feature unsupported on another target | Open a document with newer/unsupported content | Read-only/migration/loss report behavior | Silent removeContentUnsupported(by:) |
| Live canvas rendering | Compare controller view to reference source | Device/traits, bounds/zoom, visual notes | Exported artifact alone |
| PaperMarkup.draw render | Render to a controlled CGContext with options | Frame, color/trait options, output artifact, error | A screenshot of the live view |
| Dark and light rendering | Render and inspect both interface styles | RenderingOptions, color/contrast evidence | A single appearance |
| Right-to-left rendering | Render localized text with RTL option and test layout | Direction option, screenshots, text order | English LTR preview |
| HDR/color policy | Use supported HDR/linear exposure route on a capable device | Device/display/color-space, export metadata | Enabling a flag without image inspection |
| Export completeness | Compare approved elements/source to PDF/image export | Element inventory, bounds, output file, destination acceptance | A non-nil Data result |
| Accessibility task | VoiceOver create/select/review/apply/save/export on device | Spoken labels, focus order, task completion, gaps | accessibilityLabel source code |
| Keyboard/pointer | iPad/Mac Catalyst task with keyboard and pointer | Focus, shortcuts, selection handles, hover behavior | Touch-only run |
| Dynamic Type and localization | Long labels, large text, RTL, localized tools | Screenshots and task results | Default-size English preview |
| Reduce Motion/transparency/contrast | Device settings with app-owned shell and review overlays | Visual hierarchy and task evidence | Glass appearance in default settings |
| Memory/performance | Large document, many elements, repeated zoom/edit/render | Instruments/metrics, device/build/workload | Newest-device Debug run |
| Privacy and retention | Inspect saved files, temp exports, AI context, link logs | File paths, protection/retention policy, redaction | In-memory model design |
| Release target/resource membership | Archive and inspect app/extension/resource graph | Archive contents, signing, target memberships, result bundle | Debug compile |

## Test-plan slices

### Model and validation

- feature-set compatibility;
- coordinate transforms;
- stable identity;
- URL policy;
- proposal schema and stale-source rejection;
- document envelope/version migration;
- corrupt-data recovery.

### SwiftUI/UIKit bridge

- create/update/dismantle;
- controller recreation;
- delegate/coordinator lifetime;
- selection and app-owned mode;
- save status;
- Dynamic Type and app-owned accessibility.

### PaperKit/Pencil device

- Pencil draw/erase/undo;
- touch pan/select/draw policy;
- structured insertion;
- feature-set tool palette;
- selection restrictions;
- save/reopen after interruption;
- physical render/export.

### AI review

- proposal appears only after observation;
- Apply is the only mutation path;
- Reject and Undo restore source;
- model unavailable returns manual route;
- invalid geometry/URL/feature fails safely.

## Minimum physical evidence packet

For an iPad annotation or design-board release candidate, record:

1. app target, SDK, deployment target, and PaperKit content version;
2. iPad/iPhone model, OS, Pencil model, and input settings;
3. FeatureSet used by model/controller/tools;
4. source bounds/orientation and transform policy;
5. save/reopen round-trip;
6. Pencil, touch, pointer, keyboard, and VoiceOver task results as applicable;
7. dark/light/RTL/large text/reduced-effects evidence;
8. structured element, link, adornment, and unsupported-content tests;
9. AI proposal/provenance/approval/undo trace;
10. rendered/exported artifact and destination result;
11. archive/entitlement/target/resource evidence if extensions or distribution are in scope.

Do not place private documents or raw AI context in the evidence packet. Use controlled fixtures.

## Stop conditions

Stop the readiness claim if:

- the route loses the original source or feature-set version;
- PaperMarkup is saved only in memory;
- the controller is created repeatedly from SwiftUI body updates;
- unsupported content is silently removed;
- a link or AI proposal can leave the app without policy/confirmation;
- the canvas has no alternate accessible review path;
- only Simulator or preview evidence exists for Pencil or physical export;
- a rendered image is treated as proof of editable document integrity;
- PaperKit beta/API changes are not rechecked in the selected SDK.

## Sources

- [PaperKit](https://developer.apple.com/documentation/paperkit)
- [Integrating PaperKit into your app](https://developer.apple.com/documentation/paperkit/getting-started-with-paperkit)
- [PaperKit updates](https://developer.apple.com/documentation/updates/paperkit)
- [PaperMarkup](https://developer.apple.com/documentation/paperkit/papermarkup)
- [PaperMarkupViewController](https://developer.apple.com/documentation/PaperKit/PaperMarkupViewController)
- [PaperMarkupViewController initializer](https://developer.apple.com/documentation/paperkit/papermarkupviewcontroller/init%28markup%3Asupportedfeatureset%3A%29)
- [FeatureSet](https://developer.apple.com/documentation/paperkit/featureset)
- [ShapeConfiguration](https://developer.apple.com/documentation/paperkit/shapeconfiguration)
- [RenderingOptions](https://developer.apple.com/documentation/paperkit/renderingoptions)
- [MarkupInteractions](https://developer.apple.com/documentation/PaperKit/MarkupInteractions)
- [MarkupOrderedSet](https://developer.apple.com/documentation/PaperKit/MarkupOrderedSet)
- [LinkMarkup](https://developer.apple.com/documentation/PaperKit/LinkMarkup)
- [MarkupAdornment](https://developer.apple.com/documentation/paperkit/markupadornment)
- [PaperMarkup draw](https://developer.apple.com/documentation/paperkit/papermarkup/draw%28in%3Aframe%3Aoptions%3A%29)
- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

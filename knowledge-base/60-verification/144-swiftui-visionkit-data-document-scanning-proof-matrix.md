# SwiftUI VisionKit data and document-scanning proof matrix

Use this matrix to distinguish documented API knowledge, static target configuration, SwiftUI bridge behavior, controlled fixtures, physical camera evidence, privacy evidence, accessibility evidence, and signed-release proof. A successful scan is only one observation in the chain.

Pairs with the [framework review](../42-framework-deep-dives/119-swiftui-visionkit-data-document-scanning-review.md), the [design route](../21-design-deep-dives/147-swiftui-visionkit-data-document-scanning-review-design.md), the [capability route](../50-capability-recipes/150-swiftui-visionkit-data-document-scanning-review-route.md), and the [recipes](../70-code-recipes/162-swiftui-visionkit-data-document-scanning-review-recipes.md).

## 1. Evidence levels

| Level | Proves | Does not prove |
| --- | --- | --- |
| Official source | The API contract and documented caveats were read | The app uses it correctly |
| Static target audit | Privacy key, target membership, deployment and capability configuration exist | Permission grant, camera behavior, model quality, or release delivery |
| Compile | The selected SDK symbols and signatures compile | Device support, live geometry, accessibility, or physical performance |
| Unit/fixture | State transitions, parsing, geometry mapping, and stale-result guards | Camera permission, focus, lighting, or real recognition |
| SwiftUI preview | Layout and state presentation for controlled data | UIKit lifecycle, camera, Live Text, system prompts, or release behavior |
| Simulator | Some UI, fallback, and controlled source flows | Physical camera, scanner hardware support, autofocus, thermal behavior, or camera privacy |
| Physical device | Camera permission, support/availability, recognition, geometry, focus, and sustained behavior on that device | Every device, App Review, or future OS |
| Archive/TestFlight | Signed target, privacy configuration, bundle resources, and install/upgrade path | Production cohort behavior or universal recognition accuracy |
| Production | Released behavior for a measured cohort | Future OS/hardware and unmeasured source conditions |

Never use the highest available evidence to silently claim the lower or higher boundaries. A physical-device scan does not prove App Store metadata is correct, and an archive install does not prove the coordinate transform works on every camera.

## 2. Gate matrix

| Gate | Evidence to collect | Pass condition | Reject when |
| --- | --- | --- | --- |
| F0 source contract | VisionKit/SwiftUI documentation notes | Selected surface and version caveats are recorded | A generic “AI scan” replaces the API boundary |
| F1 target privacy | Signed app Info.plist or archive inspection | NSCameraUsageDescription is in the actual target with an honest purpose | A source file or unrelated target contains the only string |
| F2 capability | Target settings and device test | Data scanner/document camera support is checked at runtime | A cached device list controls the UI |
| F3 authorization | Grant, deny, revoke, restricted, and return-to-app tests | Each state has truthful copy and recovery | Camera access is assumed |
| F4 controller lifecycle | Coordinator logs and UI tests | One active controller per session; start/stop/dismiss are bounded | SwiftUI body creates duplicate controllers |
| F5 live scanner start | startScanning success and thrown failure | UI shows scanning only after start succeeded | try? hides a start failure |
| F6 document delegate | finish, cancel, fail callbacks | Controller dismisses in every callback | Camera remains active after failure/cancel |
| F7 item observation | Delegate or recognizedItems stream record | Add/update/remove/tap/unavailable behavior is deterministic | Transient items are persisted automatically |
| F8 item identity | Item IDs and session generation | IDs are used only within the current session | Item ID is treated as a physical-object identity |
| F9 payload validation | Text/barcode fixture and domain checks | Invalid or dangerous payloads are rejected or reviewed | A URL, phone number, or code opens automatically |
| F10 geometry | Corner, crop, rotation, aspect-fill, mirror fixtures | Overlay and accessible frame match the source | A square fixture is the only proof |
| F11 document pages | Page count, order, index, and image record | Each field maps back to a page/source | Pages are flattened without provenance |
| F12 image analysis | Image source/revision/orientation and interaction state | Current ImageAnalysis matches displayed image | Old analysis remains after image replacement |
| F13 cancellation | Dismiss, background, source change, and task cancellation | Late work cannot update the next session | A dismissed scanner publishes results |
| F14 AI handoff | Selected source, prompt/input envelope, response | Proposal shows source and requires review | Raw capture is passed by default |
| F15 privacy | Logs, storage, export, network, deletion audit | Data map matches actual implementation | On-device wording hides upload or retention |
| F16 accessibility | Full VoiceOver/alternate input task | Scan-to-review-to-save works without precise overlay taps | Only a static accessibility audit passes |
| F17 performance | Physical-device sustained capture | Latency, memory, drops, and thermal behavior fit target | Simulator or newest device only |
| F18 release | Archive/TestFlight clean install and upgrade | Intended route works with signed privacy/configuration | Debug build or upload alone is called release proof |

## 3. Surface-specific proof

### DataScannerViewController

Record:

    isSupported
    isAvailable
    camera authorization state
    recognizedDataTypes
    qualityLevel
    recognizesMultipleItems
    isHighFrameRateTrackingEnabled
    isPinchToZoomEnabled
    isGuidanceEnabled
    isHighlightingEnabled
    startScanning result
    stopScanning time
    item IDs and kinds
    item bounds and coordinate space
    tap action and validation result
    becameUnavailableWithError

Pass when the same route safely handles:

- supported and available;
- supported but denied;
- supported but restricted;
- unsupported hardware;
- scanner becomes unavailable while visible;
- no recognized items;
- one recognized item;
- multiple items;
- text reading order;
- barcode payload with an invalid destination;
- user tap followed by review;
- dismissal followed by a new session.

### VNDocumentCameraViewController

Record:

    isSupported
    permission state
    finish/cancel/fail callback
    controller dismissal
    scan title
    page count
    page index
    image dimensions
    image orientation
    page retention policy
    OCR/model request identity
    page-level review state

Pass when:

- one page finishes and remains page 0;
- multiple pages preserve order;
- a page can be deleted or reprocessed;
- cancellation does not claim a completed document;
- failure preserves safe partial state;
- page images can be reviewed before export/save;
- fields link to page provenance;
- deletion clears source images as promised.

### ImageAnalyzer and ImageAnalysisInteraction

Record:

    image asset or source identifier
    image revision
    orientation passed to analyze
    analysis configuration and types
    supported language result where relevant
    analysis completion or error
    preferredInteractionTypes
    contentsRect
    activeInteractionTypes
    selected text/subject action

Pass when:

- image analysis is not shown before current analysis is ready;
- an empty preferred interaction set disables interaction;
- automatic and text-only routes expose only intended actions;
- an image replacement clears or replaces old analysis;
- aspect-fit and aspect-fill layouts select the correct source content;
- long text and RTL text remain selectable and readable;
- the app’s destination action is distinct from system Live Text actions.

## 4. Fixture matrix

| Fixture | Expected result |
| --- | --- |
| Bright high-contrast QR code | Barcode item with payload and bounds |
| Dense or small barcode | Accurate/quality policy is documented; failure is reviewable |
| URL with query and fragment | URL is shown in full or safely expandable before open |
| Phone number with country ambiguity | Person can edit/confirm locale interpretation |
| Currency string | Parsed amount retains raw source and locale policy |
| Two text lines | Text item order matches documented reading order |
| Mixed language text | Requested language hint and actual result are recorded |
| No result | Empty state, not stale previous result |
| Item leaves the view | Item becomes stale/removed and cannot auto-commit |
| Tap on item | Tap is routed to validation/review |
| Camera moves during overlay | Corner mapping remains aligned or overlay is marked stale |
| Portrait camera | Orientation and safe area are correct |
| Landscape camera | Orientation and container transform are correct |
| Front camera or mirrored preview | Mirror policy is explicit and tested |
| Aspect-fill crop | Edge items map to the right visible source |
| Narrow region of interest | Only the declared region is analyzed or UI copy explains guidance |
| High-resolution capture | Still has a source record and retention decision |
| Blank document page | Page remains reviewable; extraction is not reported as success |
| Skewed document | Page capture and OCR failure are distinct |
| Duplicate document page | Person can identify and remove duplicate |
| Cancelled document scan | Prior draft survives; no completed-document claim |
| Failed document scan | Safe partial state or manual fallback |
| Image with selectable text | ImageAnalysis interaction exposes intended text actions |
| Image with a QR code | Data detector action is distinct from app action |
| Image subject | Subject lift/Visual Look Up copy does not imply identity |
| Image source replaced | Old ImageAnalysis cannot act on new image |
| Long transcript | Readable, expandable, and not hidden in glass |
| Dynamic Type maximum | Source and review actions remain usable |
| Reduce transparency | State and contrast remain understandable |
| VoiceOver | Complete scan/review/save task works |
| Voice Control/Switch Control | No precise camera-overlay tap is required |
| AI unavailable | Deterministic/manual route remains complete |
| AI proposal with missing field | Warning and edit/reject state is visible |
| Save failure | Reviewed draft remains available |

## 5. Geometry evidence record

For every overlay or source reference, write down:

    source coordinate system
    source pixel dimensions
    orientation and mirroring
    camera/display crop policy
    region of interest
    item bounds or observation rectangle
    displayed content rectangle
    SwiftUI container size
    safe-area transform
    final accessibility frame

For live recognized items, bounds are in scanner-view coordinates. For image analysis, the displayed content region and interaction contents rectangle must agree. For Vision requests on pages or frames, record the image orientation and the conversion from normalized observation coordinates.

Test points at:

- all four corners;
- center;
- near each edge;
- a rotated rectangle;
- a cropped edge;
- a mirrored source;
- a page displayed in a different aspect ratio.

The proof is a mapping result tied to a source fixture, not a screenshot alone.

## 6. Provenance and stale-result record

For each candidate, capture:

    sourceID
    sessionGeneration
    itemID or pageIndex
    source asset ID
    capture or analysis time
    raw transcript or payload
    normalized value
    source geometry description
    scanner configuration
    language hint
    request/model revision
    UI state at publication
    reviewed/edit history
    final commit ID

Test the following race:

1. start session A;
2. recognize item A;
3. dismiss or change source;
4. start session B;
5. let asynchronous work from A finish;
6. verify B’s state does not receive A’s value;
7. confirm A’s candidate is either discarded or remains in an explicitly separate draft.

## 7. Privacy evidence

| Boundary | Evidence |
| --- | --- |
| Camera permission | Actual target Info.plist and first-run prompt |
| Live frames | Capture start/stop log without raw pixels |
| Still capture | File path, retention, deletion, and backup policy |
| Document pages | Page storage and export behavior |
| OCR text | Logging, sync, and model input audit |
| Barcode payload | URL/credential/identifier handling |
| Image analysis | Source image retention and analysis clearing |
| AI handoff | Selected input, model route, and output retention |
| Network/provider | Request destination and disclosure if any |
| Diagnostics | Redaction of transcript, payload, paths, and image-derived data |
| Deletion | User-visible deletion and post-delete file/index audit |

The evidence must support the exact copy shown in the UI. “Processed on device” is not an adequate privacy record if the app later sends a page image or extracted text to a service.

## 8. Accessibility task record

Complete this task with VoiceOver and alternate input:

1. start from the explanation screen;
2. understand why camera access is needed;
3. grant or recover from denial;
4. start a live scan or document scan;
5. identify the recognition state;
6. navigate to an item or page without targeting a small overlay;
7. hear source, type, value, and stale/review state;
8. edit or reject;
9. confirm a valid value;
10. save/export or discard;
11. recover from unavailable, failed, and cancellation states.

Record:

    reading order
    focus after item arrival
    focus after page change
    focus after review dismissal
    Dynamic Type wrapping
    contrast/reduced-transparency result
    Reduce Motion result
    Voice Control command path
    Switch Control path
    keyboard/pointer path on iPad or Mac

An accessibility identifier can assist automation, but it is not proof that a person can complete the task.

## 9. Physical performance record

Use a supported physical device and a representative source set:

| Metric | Record |
| --- | --- |
| Time to ready | Permission and scanner presentation to usable state |
| Start latency | startScanning call to first stable recognition |
| Recognition latency | Frame/source time to item publication |
| Item churn | Add/update/remove counts per minute |
| Frame or event drops | Dropped, superseded, and stale results |
| Memory | Peak and sustained usage during capture |
| Thermal | Device thermal state across a long run |
| Battery | Relative cost of a long scan or multi-page route |
| Still capture | Time and retained size |
| Document extraction | Per-page duration and cancellation behavior |
| Recovery | Lock, background, interruption, and permission changes |

Repeat on the oldest supported device and on any device classes that differ materially in camera, memory, or compute. QualityLevel and high-frame-rate tracking are input choices to measure, not universal performance guarantees.

## 10. Archive and TestFlight acceptance

Before release:

- inspect the archive’s actual Info.plist for NSCameraUsageDescription;
- verify the intended deployment target and device capability configuration;
- confirm VisionKit and downstream model resources are in the intended target;
- install clean on a physical device;
- test a denied permission on the signed build;
- test a camera-restricted or unsupported path where possible;
- test document cancellation and failure;
- test image analysis after an app upgrade;
- test AI fallback and source deletion;
- run the accessibility task on the signed build;
- record the archive/TestFlight build number and device OS.

App Review and production are separate evidence layers. The release packet should also state what the app does not claim: recognition is not identity, an OCR value is not truth, a model proposal is not authorization, and a successful TestFlight install is not universal hardware coverage.

## Stop conditions

- A test checks only a screenshot and not a source-linked value.
- A scanner is tested only on simulator.
- Document page provenance is absent.
- Geometry evidence omits orientation, crop, or coordinate space.
- Stale work can update the next session.
- Accessibility evidence is limited to identifiers.
- Privacy evidence omits logs, deletion, or network handoff.
- A signed build is not tested for the actual permission and target configuration.

## Sources

- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [DataScannerViewController.isSupported](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/issupported)
- [DataScannerViewController.isAvailable](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/isavailable)
- [DataScannerViewControllerDelegate](https://developer.apple.com/documentation/visionkit/datascannerviewcontrollerdelegate)
- [DataScannerViewController.recognizedItems](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeditems)
- [RecognizedItem](https://developer.apple.com/documentation/visionkit/recognizeditem)
- [RecognizedItem.Bounds](https://developer.apple.com/documentation/visionkit/recognizeditem/bounds)
- [VNDocumentCameraViewController](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller)
- [VNDocumentCameraViewControllerDelegate](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontrollerdelegate)
- [VNDocumentCameraScan](https://developer.apple.com/documentation/visionkit/vndocumentcamerascan)
- [ImageAnalyzer](https://developer.apple.com/documentation/visionkit/imageanalyzer)
- [ImageAnalysis](https://developer.apple.com/documentation/visionkit/imageanalysis)
- [ImageAnalysisInteraction](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction)
- [InteractionTypes](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction/interactiontypes)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

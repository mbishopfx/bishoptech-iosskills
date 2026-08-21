# SwiftUI ARKit and RealityKit spatial-scene review proof matrix

This matrix separates documentation, compile, preview, simulator, signed physical-device, performance, system, and release evidence for a SwiftUI camera AR and RealityKit route. It is the acceptance boundary for [the ARKit/RealityKit deep dive](../42-framework-deep-dives/97-swiftui-arkit-realitykit-spatial-scene-review.md), [the design companion](../21-design-deep-dives/125-swiftui-arkit-realitykit-spatial-scene-review-design.md), [the capability route](../50-capability-recipes/128-swiftui-arkit-realitykit-spatial-scene-review-route.md), and [the compile-oriented recipes](../70-code-recipes/140-swiftui-arkit-realitykit-spatial-scene-review-recipes.md).

## Evidence levels

| Level | Evidence | Can support | Cannot support |
| --- | --- | --- | --- |
| L0 | Official source and target review | API meaning, availability questions, privacy/configuration checklist | Runtime behavior, sensor quality, physical placement, accessibility completion |
| L1 | Named-target compile | Imports, signatures, availability branches, target membership, basic scene projection | Camera permission, tracking, raycast quality, thermal behavior, release delivery |
| L2 | Preview/static fixture | SwiftUI hierarchy, copy, state transitions, fallback, review sheet, entity fixture | Live camera, ARSession, world tracking, physical occlusion, sensor timing |
| L3 | Simulator or recorded fixture | Deterministic state/recovery UI, non-camera RealityKit scene, test data, interaction semantics | Camera pose, real surfaces, LiDAR mesh, physical device ergonomics, thermal reality |
| L4 | Signed physical-device run | Camera consent, ARSession state, tracking guidance, raycast/anchor flow, scene reconstruction on supported hardware, accessibility/input, interruption/relocalization | App Store release, all device families, universal safety, production traffic |
| L5 | Archive/TestFlight/system/release run | Entitlements, privacy strings, signing, target configuration, release build behavior, system metadata | Universal runtime truth, physical-world safety, every hardware/lighting condition |

Never promote an L0-L3 result to L4 language. Never promote an L4 result to a universal or safety claim without the product-specific evidence that supports it.

## Core acceptance matrix

| Claim | Minimum proof | Capture | Fails if |
| --- | --- | --- | --- |
| The app can offer AR | L1 plus device/configuration review | Selected target, deployment, ARConfiguration support branch | The app presents AR on unsupported devices without a fallback. |
| Camera explanation is correct | L2/L4 | Info.plist string, pre-prompt copy, denied/revoked paths | The prompt is generic or the feature loops on denial. |
| The session starts | L4 | Physical device, permission state, configuration, session state log | A simulator or renderer preview is called a live session. |
| Tracking states are truthful | L4 | initializing, normal, limited reasons, unavailable | A Boolean says ready while ARKit is limited or interrupted. |
| Placement candidate works | L4 | Screen point, query target/alignment, current frame, result world transform | Empty result becomes a default transform or a stale result is used. |
| Placement is accepted | L2 plus L4 | Review UI, explicit action, app-owned record, undo | Raycast success automatically commits domain truth. |
| Plane refinement is handled | L4 | Candidate moves/refines, copy and reset behavior | The app implies a fixed surface before the person confirms. |
| Tracked raycast is bounded | L1/L4 | Start, updates, stop on place/teardown/interruption | The handle remains active after the feature leaves scope. |
| Entity projection is stable | L1/L2/L4 | Stable app ID to anchor/entity mapping, update/remove/recreate | SwiftUI rebuilds duplicate entities or entity names become identity. |
| Scene reconstruction is supported | L1 plus L4 | supportsSceneReconstruction result and requested mode | The UI claims mesh/occlusion on unsupported hardware. |
| Occlusion is present | L4 | Named supported device, physical object occlusion, scene conditions | A static mesh preview is called live occlusion. |
| World-map resume works | L4 | Save, relaunch, initialWorldMap, relocalizing, normal, reset | Content appears current before relocalization completes. |
| RealityView route is valid | L1/L3/L4 as target requires | Named target, availability, scene load, interaction | VisionOS-oriented code is treated as iOS camera AR proof. |
| AI proposal is bounded | L2/L4 | Input revision, source time, stale cancellation, review, rejection | AI label or explanation commits an action or proves an object. |
| Liquid Glass remains usable | L2/L4 | Normal, bright/dark scene, reduced transparency, increased contrast, Dynamic Type | Glass obscures the camera or is the only state signal. |
| Spatial task is accessible | L4 | VoiceOver, Dynamic Type, Reduce Motion, switch/keyboard/pointer route | A label exists but placement requires camera aiming only. |
| Session teardown is safe | L1/L4 | Background, navigation away, interruption, cancellation, deinit | Frames or callbacks mutate a dead scene. |
| Performance claim is credible | L4 with release-like build | Device/OS, scene/asset/mesh conditions, frame/memory/thermal duration | A short Debug run on one device is generalized. |
| Release target is configured | L5 | Archive, entitlements, Info.plist, signed build, TestFlight | A local compile is called release readiness. |

## Target and privacy packet

Record a target packet before implementation:

| Field | Evidence |
| --- | --- |
| App target | Xcode target name and platform. |
| Deployment target | Minimum OS and selected SDK. |
| Required AR | UIRequiredDeviceCapabilities policy if AR is mandatory. |
| Camera privacy | Exact NSCameraUsageDescription and pre-prompt copy. |
| Configurations | ARWorldTrackingConfiguration or other selected configuration. |
| Optional features | plane detection, scene reconstruction, image/object/body/face features. |
| Device family | Model identifier or declared capability family. |
| Persistence | Whether frames, world maps, meshes, or snapshots are saved. |
| AI path | Model availability, input summary, retention, cancellation, review. |
| Fallback | Non-AR task path and unsupported/denied copy. |
| Release | Entitlements, signing, archive, TestFlight, and App Store metadata. |

Keep privacy evidence next to the target packet. Camera access, spatial data, face/body data, local AI, and cloud sync are separate decisions.

## Tracking-state test matrix

Run the following on a signed supported device:

| Test | Setup | Expected evidence |
| --- | --- | --- |
| Initializing | Start in a low-feature view and then move slowly | Clear coaching; no placement commit. |
| Normal | Use a textured, well-lit scene | Normal state shown; candidate can be reviewed. |
| Insufficient features | Aim at a blank wall or dark area | Limited copy and no stale placement commit. |
| Excessive motion | Move rapidly | Limited copy and calm recovery. |
| Interruption | Switch apps, present an interruption, or lock as appropriate | Content marked stale; session recovery state. |
| Relocalization | Resume near the earlier view | Limited relocalizing followed by normal or a reset path. |
| Relocalization failure | Resume in a different environment | Bounded wait and user-visible reset. |
| Camera denial | Deny first prompt | Explanation, Settings path, and non-AR route. |
| Camera revocation | Revoke in Settings after prior use | Session stops or fails visibly; no blank success state. |
| Teardown | Navigate away/background/cancel | Session, tracked raycasts, subscriptions, and tasks stop. |

Use a deterministic app revision to reject callbacks from a prior session. Record the session identifier and frame timestamp in the debug evidence, but do not log raw frames or sensitive room data by default.

## Raycast and anchor packet

For each placement test, record:

- screen point and orientation;
- query target and target alignment;
- whether the result used an estimated or existing plane;
- current ARSession identifier;
- frame timestamp and app revision;
- ARCamera tracking state and reason;
- result world transform;
- result target/alignment;
- candidate age at confirmation;
- user action and resulting app-owned record;
- anchor/entity identifiers for debugging only;
- undo/reset behavior.

Acceptance rules:

1. Empty results remain unavailable.
2. A stale session or frame revision cannot commit.
3. Target and alignment are checked against product requirements.
4. The user sees a candidate before commitment.
5. The app preserves the source state in the review record.
6. Reset and undo have explicit domain meaning.
7. A raw anchor ID is not presented as physical identity.

## Scene reconstruction and occlusion packet

For a reconstruction route, record:

| Field | Example |
| --- | --- |
| Device | Named LiDAR-capable or supported device. |
| Configuration | Requested scene reconstruction mode. |
| Support check | Result of the configuration support API. |
| Plane detection | Enabled mode and device result. |
| Mesh state | unavailable / updating / estimated / usable. |
| Classification | Whether mesh classification was requested and observed. |
| Occlusion | Which physical object and lighting conditions were used. |
| Collision | Whether physical interaction was tested or only rendered. |
| Retention | Mesh/world-map storage and deletion behavior. |
| Fallback | Plane/raycast or 2D behavior on unsupported devices. |

A mesh is not a survey. A classification is not identity. Occlusion is a visual effect that requires scene and device proof; it is not a safety boundary.

## RealityKit scene packet

Verify:

- one scene owner per active renderer;
- stable app-owned record to entity mapping;
- AnchorEntity placement and update behavior;
- ModelEntity or custom entity load and resource failure;
- component replacement semantics;
- system/update ownership;
- scene subscriptions and cancellation;
- entity removal on reset/undo;
- no duplicate anchors after SwiftUI updates;
- accessibility component label/value/action updates;
- collision and interaction only when the product needs them;
- target-specific RealityView or ARView behavior.

A rendered entity proves only that the renderer accepted the input. It does not prove tracking, asset authenticity, physical position, or user intent.

## SwiftUI and accessibility packet

Run the core task with:

- VoiceOver enabled;
- Dynamic Type at the largest relevant sizes;
- increased contrast and reduced transparency;
- Reduce Motion;
- keyboard/full keyboard access where available;
- pointer and hover if the target supports it;
- Switch Control or an equivalent alternate-input route;
- portrait and landscape where the target supports both;
- iPad split view or Stage Manager if applicable;
- localizations with longer text and right-to-left layout if supported.

The task must be completable from the list/review/command route without precise camera aiming. Test that the selected item’s label, current state, source time, limitations, and actions are spoken in a useful order.

## AI proposal packet

For every local AI proposal, retain a test fixture with:

| Field | Required |
| --- | --- |
| Source revision | Yes |
| Session identifier | Yes |
| Frame/observation timestamp | Yes |
| Tracking state | Yes |
| Observation summary | Yes |
| User intent | Yes |
| Model availability state | Yes |
| Proposal output | Yes |
| Stale-result policy | Yes |
| User review result | Yes |
| Deterministic commit | Yes/no with reason |

Test model unavailable, canceled, slow, malformed, stale, contradictory, and rejected output. The app must remain usable without AI. Never describe a model label as a verified object, measurement, safety decision, or authorization.

## Performance and thermal packet

Run a release-like build on at least one representative target device and record:

- device and OS;
- build configuration;
- AR session configuration;
- frame duration or hitch evidence;
- CPU/GPU/memory observations;
- entity count and asset sizes;
- mesh/reconstruction mode;
- model inference cadence;
- session duration;
- thermal/battery behavior;
- background/foreground transitions;
- logging level.

Use MetricKit, signposts, and XCTest performance measures where appropriate, but treat their output as evidence for the tested scenario. A metric does not guarantee every scene, device, or lighting condition.

## Archive and release packet

For release evidence, attach:

- selected app target and platform;
- ARKit/RealityKit linkage;
- deployment target;
- NSCameraUsageDescription;
- UIRequiredDeviceCapabilities policy if used;
- entitlements and signing;
- asset target membership and bundle validation;
- archive result;
- TestFlight build behavior;
- App Store metadata and privacy disclosures;
- physical-device run from the release-like artifact;
- fallback behavior on an unsupported or denied device.

A preview, simulator, local archive, or static screenshot does not prove a shipped camera permission string, physical session, or App Store behavior.

## Acceptance language

Use evidence-scoped statements:

- “On the named device and OS, the app entered normal tracking after camera consent and displayed the state.”
- “On the named supported device, a horizontal estimated-plane raycast produced a candidate that required explicit placement confirmation.”
- “When tracking became limited, the app marked the candidate stale and disabled commit.”
- “Scene reconstruction was enabled only after its support check; unsupported devices used the plane/raycast fallback.”
- “After interruption, the app showed relocalizing state and provided reset after the timeout.”
- “The model proposal was tied to the source revision and rejected after the session changed.”
- “VoiceOver users could select, review, confirm, reset, and undo through the 2D command path.”
- “The release-like build was tested on the named device and configuration.”

Avoid:

- “The app understands the room.”
- “The surface is safe.”
- “The AI identified the object.”
- “AR works everywhere.”
- “The simulator proves placement.”
- “The glass UI is accessible.”
- “The archive proves production behavior.”

## Sources

- [ARKit](https://developer.apple.com/documentation/arkit)
- [ARKit in iOS](https://developer.apple.com/documentation/arkit/arkit-in-ios)
- [ARSession](https://developer.apple.com/documentation/arkit/arsession)
- [ARSessionDelegate](https://developer.apple.com/documentation/arkit/arsessiondelegate)
- [ARCamera](https://developer.apple.com/documentation/arkit/arcamera)
- [Managing Session Life Cycle and Tracking Quality](https://developer.apple.com/documentation/arkit/managing-session-life-cycle-and-tracking-quality)
- [Verifying Device Support and User Permission](https://developer.apple.com/documentation/arkit/verifying-device-support-and-user-permission)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [sceneReconstruction](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction)
- [ARWorldMap](https://developer.apple.com/documentation/arkit/arworldmap)
- [ARAnchor](https://developer.apple.com/documentation/arkit/aranchor)
- [ARRaycastQuery](https://developer.apple.com/documentation/arkit/arraycastquery)
- [ARRaycastResult](https://developer.apple.com/documentation/arkit/arraycastresult)
- [ARTrackedRaycast](https://developer.apple.com/documentation/arkit/artrackedraycast)
- [Visualizing and interacting with a reconstructed scene](https://developer.apple.com/documentation/arkit/visualizing-and-interacting-with-a-reconstructed-scene)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [ARView](https://developer.apple.com/documentation/realitykit/arview)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [AnchorEntity](https://developer.apple.com/documentation/realitykit/anchorentity)
- [Component](https://developer.apple.com/documentation/realitykit/component)
- [System](https://developer.apple.com/documentation/realitykit/system)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Improving the Accessibility of RealityKit Apps](https://developer.apple.com/documentation/realitykit/improving-the-accessibility-of-realitykit-apps)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

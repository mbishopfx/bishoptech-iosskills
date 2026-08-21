# SwiftUI Vision and Core ML live-observation review proof matrix

Use this matrix to distinguish source knowledge, compilation, simulator behavior, physical camera evidence, model evidence, accessibility evidence, and release evidence. A detected box or label is never a complete proof of visual truth, identity, diagnosis, safety, or release readiness.

Pairs with [SwiftUI Vision and Core ML live-observation review](../42-framework-deep-dives/95-swiftui-vision-core-ml-live-observation-review.md), [SwiftUI media capture and review proof](113-swiftui-media-capture-and-review-proof-matrix.md), and [Core ML model proof](84-core-ml-model-proof-matrix.md).

## Evidence levels

| Level | Proves | Does not prove |
| --- | --- | --- |
| Source | The documented API contract and caveats were read. | The target uses the contract correctly. |
| Static target audit | Privacy strings, target membership, model asset, entitlements, and deployment settings exist. | Runtime permission, physical camera, model quality, or release delivery. |
| Compile | Selected SDK symbols and types compile for the target. | Runtime availability, geometry, thermal behavior, or accessibility. |
| Preview or unit fixture | Pure mapping, state, and malformed-result handling. | Real camera timing, model behavior, physical ergonomics, or system privacy. |
| Simulator | Some UI and controlled input flow. | Physical camera orientation, compute units, thermal behavior, radio, and release device behavior. |
| Physical device | Real camera, permission, frame timing, model runtime, input, and device behavior. | App Store delivery or every hardware/OS combination. |
| Archive/TestFlight | Signed target and release configuration can be installed and exercised. | Production traffic, App Review, or universal model truth. |
| Production | The released route works for the measured cohort and telemetry. | Future model/OS/hardware behavior without regression evidence. |

## Gate matrix

| Gate | Test or evidence | Pass condition | Rejection |
| --- | --- | --- | --- |
| F0 target/privacy | Inspect signed target and archive | NSCameraUsageDescription and intended target configuration are present | Source string only or wrong target |
| F1 authorization | Physical grant, deny, revoke, and Settings recovery | Every state has truthful copy and safe controls | Permission assumed from simulator |
| F2 session | Add input/output, start/stop, interruption | Preview and analysis stop/recover without stale live claim | Running flag treated as camera truth |
| F3 frame queue | Instrument callback count, admitted count, drops, latency | Bounded queue and documented latest/every-frame policy | Unbounded tasks or hidden frame backlog |
| F4 format/orientation | Rotate, mirror, crop, aspect fill, landscape, portrait | Preview and overlay map to the same source geometry | Square fixture only |
| F5 Vision revision | Record request type, current/default/supported revision | Result provenance includes selected revision | Default revision silently changes |
| F6 observation | Object, text, point, and malformed fixtures | Typed result, unknown state, low-confidence state, and source time work | Label treated as identity or truth |
| F7 model load | Load compiled asset with configuration | Correct asset, input/output contract, and bounded error state | Model import or load alone |
| F8 compute policy | Record configuration and representative device behavior | Choice is intentional and measured | Neural Engine/GPU/CPU assumed |
| F9 backpressure | Sustain camera session and simulate slow request | Drop/throttle/cancel behavior remains bounded | UI shows stale result as live |
| F10 local AI | Proposal from selected observation | Source, warnings, edit, reject, validation, and explicit apply exist | AI executes or invents |
| F11 accessibility | VoiceOver, Voice Control, Switch Control, Dynamic Type, contrast, motion | Complete review task works without box-only interaction | Identifier or audit alone |
| F12 privacy | Review storage, logs, export, network, and retention | Camera/model boundary matches user-facing explanation | On-device claim hides retention |
| F13 physical performance | Sustained device run with metrics | Latency, memory, thermal, energy, and interruption behavior are acceptable | Simulator or newest device only |
| F14 release | Archive, TestFlight, release build, metadata | Intended target and privacy/capability claims match | Debug build or upload alone |

## Fixture matrix

| Fixture | Expected evidence |
| --- | --- |
| Permission denied | No capture start; recovery and manual route remain usable |
| Camera interrupted | Preview and analysis pause; last result becomes stale |
| Slow analyzer | Admission policy drops or replaces frames; no unbounded backlog |
| Portrait front camera | Mirroring and lower-left-to-view transform are correct |
| Aspect-fill crop | Box stays over the correct source region at every edge |
| Empty result | Explicit no-observation state, not a failed or prior result |
| Low-confidence result | Review language and no automatic commit |
| Multiple labels | Label ordering and observation confidence remain separate |
| Technical identifier | Mapped display copy plus diagnostic identifier |
| Recognized text candidates | Top candidate review and source crop |
| Missing pose point | Missing state is distinct from coordinate zero |
| Unknown model output | Safe adapter error and unsupported state |
| Model load failure | No capture claim that analysis is active |
| Old result after route change | Late completion is discarded |
| Unsupported request revision | Reconfigure or disable route |
| Local AI output | Proposal cannot execute without deterministic validation |
| Reduce transparency | Standard or opaque hierarchy retains semantics |
| Large Dynamic Type | Source, confidence, and actions remain usable |
| Background/lock | No stale live overlay or unsafe retained camera claim |
| Thermal pressure | Sampling/backoff or graceful unavailable state |
| Archive install | Privacy string and target asset match runtime behavior |

## Source and provenance record

For every displayed observation, record at least:

- source frame identifier;
- CMSampleBuffer presentation time;
- input dimensions and orientation;
- region of interest and crop policy;
- request name and revision;
- model identifier and version when Core ML is involved;
- confidence value and its source semantics;
- normalized geometry and final view transform;
- admission policy and dropped-frame context;
- UI session revision;
- whether the result is reported, stale, low-confidence, or a proposal.

A screenshot of an overlay without this record is not reproducible evidence.

## Accessibility task record

Capture a task-based record, not only a static audit:

1. Start the camera route.
2. Understand whether camera access and analysis are active.
3. Find an observation through semantic navigation.
4. Hear its label, confidence meaning, freshness, and source.
5. Open details or review.
6. Reject or edit a local-AI proposal.
7. Apply only after the same explicit confirmation as touch.
8. Recover from stale, denied, unavailable, and interrupted states.

Repeat with Dynamic Type, VoiceOver, Voice Control, Switch Control, increased contrast, reduced transparency, and Reduce Motion. Verify keyboard and pointer behavior on regular-width targets.

## Performance record

Use a physical device and record:

| Metric | Record |
| --- | --- |
| Preview cadence | Capture format, frame rate, and duration |
| Admission | Received, admitted, dropped, and superseded frame counts |
| Analysis latency | Presentation time to result publication |
| Staleness | Preview time versus overlay source time |
| Memory | Peak and sustained memory during analysis |
| Compute | Selected configuration and available devices |
| Thermal/energy | Device state over a sustained session |
| Recovery | Interruption, lock, background, and revocation |
| Accessibility | Task completion under alternate settings |

Do not use one performance trace as a universal guarantee. Repeat on the oldest supported device and the target devices that differ materially in camera, memory, and compute capabilities.

## Release acceptance

The route can be called release-ready only when:

- the signed archive contains the required privacy description;
- the model asset and target membership are correct;
- the physical device produces the intended camera geometry;
- source and model revisions are visible in diagnostics;
- stale, denied, low-confidence, and unavailable paths are safe;
- local AI remains optional and reviewable;
- accessibility and reduced-effects paths complete the task;
- sustained physical performance is acceptable;
- TestFlight or release installation uses the same target configuration;
- the release description does not claim diagnosis, identity, safety, or guaranteed accuracy that the evidence does not establish.

## Sources

- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNRequest](https://developer.apple.com/documentation/vision/vnrequest)
- [VNObservation](https://developer.apple.com/documentation/vision/vnobservation)
- [VNRecognizedObjectObservation](https://developer.apple.com/documentation/vision/vnrecognizedobjectobservation)
- [VNRecognizedTextObservation](https://developer.apple.com/documentation/vision/vnrecognizedtextobservation)
- [VNRecognizedPointsObservation](https://developer.apple.com/documentation/vision/vnrecognizedpointsobservation)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [Recognizing objects in live capture](https://developer.apple.com/documentation/vision/recognizing-objects-in-live-capture)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

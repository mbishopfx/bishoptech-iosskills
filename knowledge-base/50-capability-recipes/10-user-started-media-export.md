# Blueprint: User-Started Media Export

## Product outcome

Let a person select or capture media, apply bounded processing, watch truthful progress while the app backgrounds, and receive a standard file they can review and share.

## Route composition

`PhotosPicker/AVFoundation -> deterministic media pipeline -> BGContinuedProcessingTask -> ProgressReporting/ActivityKit -> FileRepresentation/Transferable -> ShareLink/FileDocument`

| Layer | Route | Ownership |
| --- | --- | --- |
| Selection | PhotosUI `PhotosPicker`/`PhotosPickerItem` | User-selected scope, representation loading, cancellation, and permission boundary |
| Capture | AVFoundation when live camera/audio control is needed | Session lifecycle, format, interruption, orientation, and device hardware |
| Processing | Core Image, AVAsset/AVFoundation, VideoToolbox, or a deterministic encoder | Input/output format, backpressure, cancellation, memory, and output validity |
| Background | `BGContinuedProcessingTaskRequest`/`BGContinuedProcessingTask` | Person-started work, progress, checkpoint, expiration, cancellation, and resume |
| Progress | ProgressReporting plus ActivityKit/system UI where supported | Projection of durable job state; never the source of truth |
| Export | `Transferable`, `FileRepresentation`, `UTType`, `FileDocument`, `ShareLink` | User-selected export representation, staging, cleanup, and destination errors |

## State machine

`idle -> selecting -> loading-representation -> configuring -> foreground-processing -> submitted -> queued|running -> paused|canceling -> output-review -> exported|failed|canceled|expired`

Persist a versioned job record before submission:

`jobID, source references, operation/version, completed units, output URL/state, progress, cancellation source, error, created/updated timestamps`

Never infer completion from a progress percentage alone. Reconcile the job record, output file, task callback, and ActivityKit state on relaunch.

## Native interface plan

- Use a simple SwiftUI flow: source picker, processing configuration, review/export screen, and a compact job status view.
- Keep the primary start action in a native toolbar or button group; explain that the person can leave the app while the system continues the explicitly started job.
- Use Liquid Glass only for the functional status/control group and ensure progress remains legible in light/dark, large text, reduced transparency, and VoiceOver.
- Present a final file name, type, size, destination, and cancel/retry action. Do not hide a large export behind a decorative animation.
- Use the system share/file route instead of recreating Apple’s share sheet or file picker.

## Build order

1. Build deterministic fixture-based processing with cancellation and a local output file.
2. Add PhotosUI selection or the AVFoundation capture route, preserving source metadata and user-selected scope.
3. Add progress/checkpoint persistence and a foreground-only job UI.
4. Add `BGContinuedProcessingTask` for a user-started job, including rejection/cancellation/expiration recovery.
5. Add ActivityKit progress only as a projection of the durable job.
6. Add `Transferable`/`FileRepresentation`/ShareLink and validate large files, unsupported destinations, and cleanup.

## Permission, resource, and privacy contract

- Use PhotosUI selection for least privilege when live library access is unnecessary; request camera/microphone only when the capture route starts.
- Record the exact input/output media types, file size limits, temporary-file lifetime, and deletion policy.
- Treat background GPU/resource access, entitlements, device support, memory, battery, and thermal behavior as target-specific gates.
- Do not place source media, private filenames, or exact location metadata in logs, notifications, widget snapshots, ActivityKit content, or share previews unless explicitly selected.
- Reconcile privacy manifests, usage descriptions, App Store privacy answers, and any third-party codec/analytics SDK data flow.

## Fallbacks

| Condition | Fallback |
| --- | --- |
| Source selection canceled/denied | Preserve the configuration and offer another source or manual file import |
| Unsupported format or hardware | Show a clear unsupported state and offer a compatible export preset |
| Background task rejected | Keep processing in foreground or pause with resume later |
| Task canceled/expired | Save the last checkpoint, clean incomplete output, and offer resume/restart |
| Share destination unavailable | Save a user-visible file and offer Files/another standard representation |

## Proof plan

- Fixtures: deterministic transforms, media metadata, cancellation, checkpoint recovery, file validation, UTType/Transferable representations, and redacted UI states.
- Simulator: selection UI, fake processing, progress states, navigation, large text, and error/retry flows.
- Physical device: camera/microphone/Photos behavior, processing memory/thermal/battery, background transition, task cancellation, ActivityKit display, lock state, and file/share destinations.
- Release: archive entitlements, privacy resources, supported device family, TestFlight processing, signed background behavior, and production claims separately.

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [Video Toolbox](https://developer.apple.com/documentation/videotoolbox)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)

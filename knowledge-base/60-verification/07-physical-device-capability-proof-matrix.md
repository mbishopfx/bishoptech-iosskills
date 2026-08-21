# Physical-Device Capability Proof Matrix

Use this matrix when a feature crosses from source documentation and UI fixtures into real iPhone/iPad behavior. Keep documented, compiled, simulator, physical-device, system-surface, and release claims separate.

## Evidence levels

| Level | Evidence packet | Proves | Does not prove |
| --- | --- | --- | --- |
| Source | Exact official Apple/Swift pages, research date, availability notes | The route is documented and its constraints are understood | The selected target compiles or the service is available. |
| Target | Scheme, deployment target, SDK/toolchain, target membership, resources, capabilities, entitlements, usage descriptions | The project is configured to attempt the route | Runtime permission, hardware, account, or service behavior. |
| Compile/test | Build result, warnings, test plan, result bundle, deterministic fixtures | The selected source/configuration builds and deterministic checks pass | Physical performance, model readiness, camera/audio/radio behavior, or system delivery. |
| Simulator | Destination, OS/runtime, settings, fixture, screenshots/result bundle | UI/state branches and fakeable data behave in the simulated environment | Actual hardware, accelerator behavior, physical sensors, assistive hardware, or every system surface. |
| Physical device | Device model/identifier, OS build, app build, signed target, settings, permissions, scenario, logs/metrics | The named device/configuration produced the recorded behavior | Other devices, future OS/model revisions, App Review, or production reliability. |
| System surface | Signed app/extension, system entry point, account/permission/service state, invocation/result capture | The named widget, App Intent, notification, Share Sheet, Watch, CarPlay, App Clip, or other surface behaved in that run | Universal ranking, delivery, server health, or every supported configuration. |
| Release | Release archive/TestFlight/App Store build, privacy report, metadata, signing, environment | Packaging/distribution and the tested release configuration | Approval, production health, all devices, or user comprehension without those tests. |

Never promote a lower evidence level into a higher claim in a status document, marketing page, App Store metadata, or handoff.

## Capability matrix

| Capability | Simulator can usually cover | Physical-device proof must cover |
| --- | --- | --- |
| SwiftUI/layout/Liquid Glass | State fixtures, previews, Dynamic Type, appearance, resize, navigation, fake data | Material legibility, touch comfort, performance, reduced effects, VoiceOver, Voice Control, Switch Control, and alternate input. |
| Foundation Models | Injected proposals, availability branches, validation/review UI, deterministic reducers | Model readiness, Apple Intelligence setting, language/region, context/resource behavior, latency, memory/thermal/battery, refusal/fallback. |
| Core ML/Vision | Still-image fixtures, request output, coordinate transforms, thresholds, fake model state | Model load/compute-unit behavior, representative photo/camera input, orientation/lighting/occlusion, latency, thermal/battery, real asset/version. |
| Camera/microphone | Permission UI branches, mocked frames/audio, preview shell | Authorization, hardware route, interruption, lock/termination/relaunch, orientation, frame/audio timing, privacy copy, thermal behavior. |
| Location/maps/weather | Simulated locations, deterministic service clients, UI route | Authorization/accuracy, GPS freshness, background behavior, network/service failure, attribution, battery, real account/entitlement. |
| Motion/haptics/NFC/Bluetooth/Nearby | Protocol/state fixtures and no-hardware fallback | Feature availability, permission, pairing/discovery/session lifecycle, interference, reconnect, actual haptic/sensor/radio behavior. |
| Health/Contacts/Calendar/Photos | Mock stores, picker/result fixtures, authorization branches | Protected-data access, account/store state, authorization/revocation, deletion, real picker/system handoff, privacy copy. |
| StoreKit/Apple Pay/identity/security | StoreKit configuration, fake auth/failure states, local domain tests | Sandbox/TestFlight or production-like account, entitlement, biometric/passcode/keychain, payment/transaction verification, revocation/recovery. |
| Widgets/App Intents/notifications/Live Activities | Previews, timeline fixtures, deep-link parsing, fake push/update state | Signed extension, real system invocation, refresh/update budgets, permissions, APNs/account/server state, stale/error behavior. |
| Watch/CarPlay/App Clips | Layout and handoff fixtures where supported | Pairing/vehicle/invocation, separate target/signing, system approval, connectivity, audio/input, actual handoff and recovery. |
| Metal/RealityKit/ARKit/spatial | Logic, fake scenes, some accelerated simulation | Supported sensors/GPU, tracking/lighting, frame timing, thermal/battery, comfort/input, real spatial conditions. |

## Evidence packet template

Copy this into a feature plan or release record:

    Feature/outcome:
    Route/API:
    Source pages and research date:
    App/build:
    Xcode/SDK/toolchain:
    Deployment target:
    Device model/identifier:
    OS/build:
    Locale/region:
    Account/store/service state:
    Permissions and entitlements:
    Model/asset/accessory version:
    Input fixture or scenario:
    Expected result:
    Observed result:
    Fallback/error/recovery result:
    Latency/memory/thermal/battery notes:
    Accessibility settings and task result:
    System-surface entry/result, if applicable:
    Artifacts/logs/metrics/result bundle:
    Unproven claims:
    Owner/date:

Do not put credentials, private prompts, raw health data, access tokens, or unnecessary personal media into the evidence packet. Use redacted identifiers and the project’s approved access and retention policy.

## Physical-device run procedure

1. Freeze the app/build, SDK, target, model/resource, and fixture versions.
2. Confirm the intended device family and OS build; record the device identifier without exposing it publicly.
3. Install the signed development or release configuration with required target membership, entitlements, usage descriptions, and privacy resources.
4. Reset only the permissions/account/service state required by the scenario and record the starting state.
5. Run from a cold launch, then repeat the lifecycle transitions that matter: background/foreground, lock/unlock, interruption, termination/relaunch, account switch, and settings change.
6. Exercise success, unavailable, denied, cancelled, stale, conflict, and failure/recovery paths.
7. Repeat the core task with relevant accessibility settings and alternate input methods.
8. Capture logs and metrics with privacy-safe fields, plus the exact scenario and result.
9. Compare observed behavior with the intended claim; downgrade or remove claims that the run did not prove.
10. Repeat on a representative second device when the route depends on hardware class, model readiness, screen size, or performance.

Simulator runs remain valuable for rapid layout, state, accessibility-setting, and deterministic fixture coverage. Apple’s Xcode guidance warns that Simulator does not reproduce physical-device performance or every hardware-specific feature.

## Failure and fallback evidence

| Failure | Required user path | Evidence |
| --- | --- | --- |
| Permission denied/restricted | Explain the capability and provide Settings/manual route | Permission reset and return-from-Settings run. |
| Hardware unavailable | Manual/imported/fakeable alternative where appropriate | Unsupported-device or unavailable-service run. |
| Model/asset not ready | Wait/download/retry later/manual route | Readiness state, recovery, and no-dead-end UI. |
| Capture interruption | Preserve confirmed data and resume/restart safely | Call/interruption/lock/background run. |
| Resource pressure/thermal | Reduce cadence/quality, pause, or defer | Metrics and user-visible state on the named device. |
| Stale/conflicting domain state | Revalidate, review, merge, or reject | Duplicate/stale/conflict fixture and persistence result. |
| System surface unavailable | Return to app-owned workflow | Actual system setting/permission/entry failure and deep-link recovery. |

## Accessibility task evidence

An accessibility audit or automated diagnostic is useful but does not prove that a person can complete the core task. Record task-level outcomes for VoiceOver reading order and focus, Voice Control commands, Switch Control and keyboard/pointer paths, Assistive Access, Dynamic Type, increased contrast, reduced transparency, Reduce Motion, color-independent status, localization, RTL, captions/transcripts, and alternate media input where relevant.

Use physical hardware for assistive technologies or sensors that Simulator cannot reproduce. Preserve exact settings and build so later regressions are comparable.

## Release gate separation

    source -> target configuration -> compile/test -> simulator
          -> physical device -> signed archive -> TestFlight/App Store
          -> production/server/account/system-delivery observation

A successful archive, upload, or TestFlight install is not proof that a camera, model, system surface, server, notification, or App Store claim works for every user. The final product claim must be no broader than the strongest evidence attached to it.

## Sources

- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Building and running an app](https://developer.apple.com/documentation/xcode/building-and-running-an-app)
- [Configuring the environment of a simulated device](https://developer.apple.com/documentation/xcode/configuring-the-environment-of-a-simulated-device)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover)
- [Optimizing your app for Assistive Access](https://developer.apple.com/documentation/accessibility/optimizing-your-app-for-assistive-access)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [AVFoundation Capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [MetricKit](https://developer.apple.com/documentation/metrickit)

# Capability-First Apple SDK Atlas

## Use the user outcome as the route key

Apple’s SDK is large enough that choosing a framework by familiarity is a reliable way to create unnecessary permissions, lifecycle bugs, and unsupported assumptions. Start with the thing the person wants to accomplish, then select the narrowest API that owns the capability.

This atlas is a routing map, not an exhaustive symbol reference. Each selected route still needs the current Apple page, target SDK, deployment target, entitlement/usage description, runtime availability, and the evidence level required by the feature.

## Outcome-to-route map

| User outcome | First route | Important symbols/seams | Native surface | Main gates |
| --- | --- | --- | --- | --- |
| Build a native app shell | SwiftUI | `App`, `Scene`, `NavigationStack`, `NavigationSplitView`, `TabView`, `ToolbarContent` | SwiftUI navigation, tabs, toolbars, sheets | State ownership, Dynamic Type, accessibility, platform adaptation. |
| Store private app data locally | SwiftData or a file/document route | `ModelContainer`, `ModelContext`, `@Model`, `FileDocument`, `DocumentGroup` | Lists, forms, editors, document browser | Migration, deletion, protected data, file coordination, conflict policy. |
| Sync user-owned data | CloudKit or a deliberate sync layer | `CKContainer`, `CKRecord`, `CKSyncEngine`, SwiftData automatic sync | Offline-first UI, conflict/review state | Account state, entitlements, schema, conflict, privacy, multi-device proof. |
| Let a person choose a photo/file | PhotosUI, Uniform Type Identifiers, SwiftUI file import | `PhotosPicker`, `fileImporter`, `UTType`, security-scoped URL | Picker, import/review screen | Least privilege, representation, file lifetime, retention, cancellation. |
| Capture camera or microphone input | AVFoundation | `AVCaptureSession`, `AVCaptureDeviceInput`, `AVCaptureVideoDataOutput`, `AVAudioSession` | Camera preview, recorder, capture controls | Usage descriptions, serial session queue, interruption, backpressure, device proof. |
| Recognize text or visual structure | Vision/VisionKit | Vision requests/observations, `DataScannerViewController`, current Swift request APIs | Scanner, source-linked review editor | Camera/device availability, orientation, confidence, model/revision, human review. |
| Run a custom model | Core ML | `MLModel`, generated model wrapper, compute-unit policy | Progress/result/review state | Model asset/version, input contract, memory, thermal, quality fixtures. |
| Transcribe or classify audio | Speech/Sound Analysis | `SpeechAnalyzer`, `SpeechTranscriber`, `AssetInventory`, `SNAnalyzer` | Record/transcript/editor | Microphone/speech permission, locale/assets, audio route, cancellation, physical audio. |
| Translate text | Translation | `LanguageAvailability`, `TranslationSession` | Source/target editor, language picker | Language-pair support, asset readiness, source preservation, fallback. |
| Show a map or find a place | MapKit/Core Location | `Map`, `MapCameraPosition`, `MKLocalSearch`, `MKMapItem`, `MKDirections`, `CLLocationManager`/live updates | Map, search, place/detail, route preview | Location authorization/accuracy, cancellation, stale results, attribution, power. |
| Show forecast or alerts | WeatherKit | `WeatherService`, `WeatherQuery`, `CurrentWeather`, forecast/alert values | Forecast/detail cards | Entitlement, attribution, location, freshness, service/account failure. |
| Read/write protected personal data | HealthKit, Contacts, EventKit, UserNotifications | `HKHealthStore`, contact picker/store, `EKEventStore`, notification center | Permission explainer, picker, reviewed draft | Usage descriptions, authorization state, protected data, deletion, system settings. |
| Control a home/accessory | HomeKit/Core Bluetooth/Nearby Interaction | `HMHomeManager`, `CBCentralManager`, `CBPeripheral`, `NISession` | Pairing/discovery/control state | Radio/permission, accessory trust, protocol, reconnect, physical side effects. |
| Make a purchase or unlock access | StoreKit/PassKit | `Product`, verified `Transaction`, `Transaction.currentEntitlements`, Apple Pay/Wallet APIs | Product sheet, receipt/entitlement state | Store configuration, verification, server fulfillment, account, recovery. |
| Sign in or protect a secret | AuthenticationServices/Keychain/LocalAuthentication | Sign in with Apple, `SecItem`, `LAContext` | Sign-in, biometric/passcode gate, recovery | Nonce/state, Keychain accessibility, user cancellation, server identity. |
| Verify app/device integrity | CryptoKit/DeviceCheck/App Attest | Crypto primitives, `DCDevice`, App Attest key/attestation/assertion | Usually no bespoke trust UI; explain recovery | Server challenge/verification, key lifecycle, rate limits, no absolute-security claim. |
| Expose actions/content to the system | App Intents/Spotlight/WidgetKit/ActivityKit | `AppIntent`, `AppEntity`, `EntityQuery`, `AppShortcutsProvider`, widget/control intents | Siri, Shortcuts, Spotlight, widgets, controls, Live Activities | Stable IDs, extension process, authorization, system invocation, deep links. |
| Share/export a result | Transferable/ShareLink/UIKit sharing/PDFKit | `Transferable`, `TransferRepresentation`, `ShareLink`, `UIActivityViewController` | Share sheet, export/file preview | Representation, redaction, security scope, user start, cancellation. |
| Browse web content or render PDF | WebKit/PDFKit | `WKWebView`, navigation delegate, `PDFDocument`, `PDFView` | Web/PDF reader, download/export | Trust boundary, navigation policy, JavaScript bridge, file access, privacy. |
| Run useful work outside the app UI | BackgroundTasks/extensions | `BGAppRefreshTask`, `BGProcessingTask`, `BGContinuedProcessingTask`, App Groups | Progress/status, widget/Live Activity handoff | Scheduling is nondeterministic, resource limits, user-started boundary, cancellation. |
| Build an iPhone/iPad spatial experience | ARKit/RealityKit | `ARSession`, `RealityView`, entities/components/systems | Camera/spatial scene, placement/recovery UI | Camera/privacy, tracking state, hardware, safety, thermal, physical proof. |
| Build a 2D or 3D game | SpriteKit/GameplayKit/Metal/GameKit | `SKScene`, GameplayKit state/agents, Metal device/pipeline, Game Center | Game scene, menus, controller/input, accessibility | Frame budget, deterministic state, account/match lifecycle, device performance. |
| Extend to Watch or vehicle | WatchConnectivity/CarPlay | `WCSession`, `CPTemplateApplicationScene`, templates | Watch scene, CarPlay templates | Pairing, reachability, entitlements, driver attention, two-device/vehicle proof. |
| Deliver a communication experience | CallKit/PushKit/LiveCommunicationKit | provider actions, VoIP push, conversation manager | System call UI, default dialer/communication surfaces | Specialized entitlement, server state, audio route, permissions, policy/release. |
| Ship a lightweight entry point | App Clips | invocation URL, experience configuration, associated domains | App Clip card/scene and full-app handoff | Invocation context is untrusted, size/availability, AASA, App Store configuration. |

## Select the route in layers

Ask these questions in order:

1. **What is the user outcome?** Is it capture, view, edit, search, communicate, purchase, control, discover, or compute?
2. **Who owns the UI?** The app, a user-mediated picker, a system sheet, an extension, a widget/control, a vehicle/watch surface, or a spatial session?
3. **What data is actually required?** Prefer user-selected representations and least-privilege permissions.
4. **What lifecycle owns the resource?** View, scene, capture session, audio route, location stream, accessory session, extension, background task, or server transaction?
5. **What can fail or become stale?** Permission, hardware, account, language asset, network, system surface, process, model, storage, or physical-world state?
6. **What proof is needed?** Preview, unit/UI test, simulator, physical device, two-device/vehicle, signed artifact, system surface, server/account, or production evidence?

Do not choose a broader framework merely because it can technically produce the same output. A map is not a location permission, an App Intent is not an authorization policy, a Core ML prediction is not a verified fact, and a signed build is not proof of a system service or production delivery.

## Cross-cutting gates

| Gate | Route questions |
| --- | --- |
| Availability | Does the target OS/device expose the symbol, hardware, service, model, language, accessory, vehicle, or system surface? |
| Permission | Is access requested at the feature boundary with accurate purpose text, and can the person revoke it while the app is running? |
| Entitlement/configuration | Does the app/extension have the capability, background mode, associated domain, merchant ID, App Group, or service setup it needs? |
| Process/lifecycle | What happens when the scene disappears, the extension is terminated, the phone locks, the route changes, or the system interrupts? |
| Data boundary | What is user-selected, protected, derived, shared, cached, logged, retained, or deleted? |
| Side effect | Is the operation read-only, reversible, user-confirmed, idempotent, and authorized against current state? |
| Adaptation | Does the native surface remain usable in compact/regular layouts, large text, localization, VoiceOver, reduced effects, keyboard, pointer, and alternate input? |
| Evidence | Which exact environment proves each claim, and what remains unproven? |

## Route record template

Copy this into an app plan before implementing a new capability:

| Field | Record |
| --- | --- |
| User outcome | One sentence describing the task and consequence of failure. |
| Framework/API | Exact framework, symbol, request, scene, extension, or system surface. |
| Input/output | Data type, representation, source, derived result, and maximum useful size/rate. |
| Availability | OS/SDK, hardware, language/region, account/service, accessory, and model/asset state. |
| Permission/entitlement | Purpose text, authorization state, capability, associated domain, and privacy manifest impact. |
| Lifecycle | Start/stop/cancel/interrupt/background/foreground/process-relaunch behavior. |
| UI route | Native SwiftUI/UIKit/system/Watch/CarPlay/spatial surface and fallback. |
| Trust boundary | Validation, provenance, confirmation, idempotency, and domain use case. |
| Tests | Fixtures, unit/UI/accessibility/performance tests, simulator, physical/two-device/system proof. |
| Release evidence | Signed artifact, App Store/entitlement/server/account/system delivery evidence, only if claimed. |

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [CloudKit](https://developer.apple.com/documentation/cloudkit/)
- [PhotosUI](https://developer.apple.com/documentation/photosui/)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Translation](https://developer.apple.com/documentation/translation)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Core Location UI](https://developer.apple.com/documentation/corelocationui)
- [WeatherKit](https://developer.apple.com/documentation/weatherkit)
- [HealthKit](https://developer.apple.com/documentation/healthkit/)
- [Contacts](https://developer.apple.com/documentation/contacts/)
- [EventKit](https://developer.apple.com/documentation/eventkit/)
- [UserNotifications](https://developer.apple.com/documentation/usernotifications/)
- [HomeKit](https://developer.apple.com/documentation/homekit/)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth/)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction/)
- [StoreKit](https://developer.apple.com/documentation/storekit/)
- [PassKit](https://developer.apple.com/documentation/passkit/)
- [Authentication Services](https://developer.apple.com/documentation/authenticationservices/)
- [Keychain Services](https://developer.apple.com/documentation/security/keychain_services)
- [LocalAuthentication](https://developer.apple.com/documentation/localauthentication/)
- [DeviceCheck](https://developer.apple.com/documentation/devicecheck/)
- [App Attest](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Transferable](https://developer.apple.com/documentation/coretransferable/)
- [WebKit](https://developer.apple.com/documentation/webkit/)
- [PDFKit](https://developer.apple.com/documentation/pdfkit/)
- [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks/)
- [ARKit](https://developer.apple.com/documentation/arkit/)
- [RealityKit](https://developer.apple.com/documentation/realitykit/)
- [Metal](https://developer.apple.com/documentation/metal/)
- [SpriteKit](https://developer.apple.com/documentation/spritekit/)
- [GameplayKit](https://developer.apple.com/documentation/gameplaykit/)
- [GameKit](https://developer.apple.com/documentation/gamekit/)
- [WatchConnectivity](https://developer.apple.com/documentation/watchconnectivity/)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [App Clips](https://developer.apple.com/documentation/appclip/)
- [CallKit](https://developer.apple.com/documentation/callkit/)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)

# SwiftUI scenes, windows, and multiplatform proof matrix

## Purpose

Use this matrix for any claim involving multiple SwiftUI scenes, typed
windows, external-event delivery, restoration, iPadOS multitasking, Mac
Catalyst, visionOS, watchOS, Liquid Glass scene shells, or on-device AI task
windows.

A scene/window claim must name the target and evidence level. Record:

- app version, build, Xcode, SDK, deployment target, and configuration;
- target and process/extension membership;
- scene declaration, scene ID/window ID, typed presentation value;
- domain record ID, account, authorization, and source revision;
- external event source, request ID, URL/activity payload, and delivery state;
- scene phase, cold/warm/terminated state, window size, orientation, and
  multitasking mode;
- locale, layout direction, Dynamic Type, color scheme, contrast, motion,
  transparency, input, and accessibility settings;
- AI capability/model/session state, candidate revision, cancellation, and
  commit result;
- artifact path, test date, and tester/device identity.

## Evidence levels

| Level | Can support | Cannot support alone |
| --- | --- | --- |
| Official source | API intent, HIG behavior, configuration questions | App implementation or runtime behavior |
| Static route review | Identity/lifecycle/target ownership | System scene selection, accessibility, physical input |
| Named-target compile | Scene declarations, availability, target membership, imports | Multiwindow system behavior, external delivery, model/device readiness |
| Unit/fixture test | Request normalization, typed values, stale-ID and revision policies | System-created windows, real permissions, spatial comfort |
| Preview | Named visual composition and state fixture | Window creation, scene routing, physical resize, external events |
| UI test | In-app controls, labels, route actions, deterministic task flows | Full system delivery, all window configurations, physical ergonomics |
| Simulator | Resizing/layout and many lifecycle cases | Physical keyboard/pointer/crown/vision comfort, model readiness, release |
| Signed physical target | iPad windowing, Catalyst Mac run, watch/vision input, device model state | App Store distribution or production population |
| System-surface run | URL/Handoff/widget/App Intent/notification delivery from the real surface | All target/platform combinations or release metadata |
| Archive/release artifact | Target membership, Info.plist, entitlements, signing, processed build | User task completion, live external delivery, physical feel |

Never collapse these levels into one “works” label.

## Fixture contract

Every reusable scene fixture should include:

~~~swift
struct SceneProofFixture: Hashable, Sendable {
    let target: String
    let sceneKind: String
    let sceneRequestID: String
    let windowID: String?
    let domainID: String?
    let sourceRevision: Int?
    let externalSource: String?
    let scenePhase: String
    let windowSize: String
    let orientation: String
    let localeIdentifier: String
    let layoutDirection: String
    let dynamicType: String
    let colorScheme: String
    let accessibilityModes: [String]
    let aiState: String
}
~~~

The fixture identifies the state being tested; it is not a substitute for a
real scene session or device.

## Scene declaration and identity matrix

| Claim | Minimum proof | Required negative/edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Primary WindowGroup exists | Named-target compile and launch | Unsupported target/availability branch | Root scene appears with correct title and task |
| Auxiliary Window exists | Compile plus open-by-ID UI/system route | Reopen when already open, close/dismiss, unsupported platform | Correct utility comes forward and closes without domain deletion |
| Typed WindowGroup resolves a record | Compile plus deterministic value fixture | Missing, deleted, unauthorized, stale, malformed value | Destination displays current authorized state or recoverable error |
| Scene identity is separate from domain identity | Static review plus two-scene fixture | Same domain ID in two windows, different scene drafts | One window’s draft/focus does not overwrite another |
| Presentation value is lightweight | Static review and value encode/decode test | Live model, secret, large payload, unvalidated AI result | Only stable ID/revision crosses the scene boundary |
| Existing value brings a window forward | Named-target UI run | Duplicate open, value equality, source revision change | Existing window behavior is recorded without assuming work deduplication |
| Multiple-window support is claimed | Configuration inspection, compile, signed target run | Single-window fallback, unsupported target | Target-specific claim names the config and runtime artifact |

## Opening and external-event matrix

| Route | Minimum proof | Edge cases | Evidence |
| --- | --- | --- | --- |
| openWindow by ID | Named-target UI test or physical run | Utility already open, dismissal, unsupported platform | Correct auxiliary task appears |
| openWindow by value | Typed fixture plus UI/system run | Same value, changed value, missing record | Correct record window opens or resolves a fallback |
| Scene-level external matcher | Compile plus real event delivery | No open scene, several matching scenes, no match | Correct scene is created/selected |
| View-level external-event preference | Multi-scene run | Already-open scene versus new scene | Existing scene receives only the events it claims |
| onOpenURL | Parser/unit fixture plus actual URL source | Malformed, duplicate, unauthorized, stale URL | Route is validated before feature action |
| onContinueUserActivity | Payload fixture plus Handoff/system run | Cold/warm/terminated, unsupported activity | Correct feature route receives the activity |
| Widget/App Intent/notification entry | Intent or notification fixture plus system run | Process terminated, account changed, stale entity | System entry converges on a typed app route |
| External route deduplication | Request-ID and idempotence test | Replay, race, duplicate delivery | No duplicate commit or duplicate model action |

## Lifecycle and restoration matrix

| Claim | Minimum proof | Edge cases | Evidence |
| --- | --- | --- | --- |
| Scene phase bounds work | Unit/integration plus UI lifecycle run | inactive, background, rapid active/background | Work pauses/cancels/checkpoints as designed |
| Scene-owned task cancels | Test task cancellation and teardown | model/network delay, view disappearance, replacement value | No callback mutates released scene state |
| Small state restores | Relaunch/scene restoration run | invalid ID, account change, deleted record | Restored selection becomes valid state or repair UI |
| Draft is protected | Close/background/restore test | unsaved edits, conflict, crash/termination | Draft remains or is explicitly recovered/discarded |
| Durable truth survives | Store/relaunch/sync evidence | migration, conflict, sign-out | Persistence layer, not SceneStorage, proves truth |
| Two scenes remain independent | Two-window state test | same domain ID, different selections/drafts | Scene-local state stays isolated |
| AI context is bounded | Fixture plus adapter/session test | model unavailable, cancellation, source replacement | Context is not duplicated or persisted as a secret |
| Source revision is rechecked | Unit/integration commit test | stale candidate, concurrent edit | Stale AI/external proposal is rejected or reviewed |

## iPadOS and Catalyst matrix

| Claim | Minimum proof | Edge cases | Evidence |
| --- | --- | --- | --- |
| iPadOS multiple windows | Config/archive inspection plus signed iPad run | full-screen mode, windowed mode, unsupported fallback | Two app windows can complete distinct tasks |
| Resize adapts | UI/physical run at narrow/wide heights/widths | Stage Manager, split view, rotation, keyboard | Content hierarchy and primary action remain usable |
| Scene restoration on iPad | Close/reopen/relaunch run | one window closes while another stays active | Correct per-window state returns |
| Catalyst is supported | Actual Mac Catalyst compile/run | Mac idiom, narrow width, menu/toolbar absence | Mac task and commands are usable |
| Catalyst input works | Mac keyboard/pointer run | VoiceOver, Full Keyboard Access, hover-only route | Keyboard, pointer, focus, and menus complete the task |
| iPad and Catalyst share meaning, not assumptions | Static target review plus both runs | platform-specific view/command branches | Domain use case is shared; shell/input is target appropriate |

## visionOS and watchOS matrix

| Claim | Minimum proof | Edge cases | Evidence |
| --- | --- | --- | --- |
| visionOS window route | visionOS compile/simulator run | scale, resize, focus, dismissal | Familiar task is legible in a system window |
| visionOS volume or immersive route | Target run plus physical spatial evidence where claimed | enter/exit, interruption, comfort, safe dismissal | Spatial claim is limited to tested route |
| watchOS companion route | watch target compile/simulator run | short width, Always On, crown, offline/paired | One glanceable task works on the watch target |
| Cross-target data projection | Typed fixture and transfer test | account change, stale data, unavailable phone | Watch/spatial projection is not treated as the iPhone scene |
| Unsupported target fallback | Availability/conditional compile and UI test | missing framework or capability | User sees an honest alternative or unsupported state |

## Liquid Glass scene-shell matrix

| Claim | Minimum proof | Edge cases | Evidence |
| --- | --- | --- | --- |
| System window treatment is used | Target-specific visual run | light/dark, contrast, transparency, background content | System window remains recognizable and legible |
| Custom glass groups content | Preview plus named-target visual run | long text, Dynamic Type, reduced transparency | Glass clarifies hierarchy without hiding content |
| Auxiliary window has task meaning | Design review plus open/close run | repeated open, no-op task, clutter | New window preserves context or parallel work |
| visionOS glass is native | Spatial target run | no fake frame, system controls, scale | App does not claim custom chrome replicates system window |
| AI review glass remains semantic | Fixture/UI run | unavailable/partial/stale/committed | Status and review actions remain accessible |

## Accessibility and input matrix

| Claim | Minimum proof | Edge cases | Evidence |
| --- | --- | --- | --- |
| Window title/task is discoverable | VoiceOver UI task | auxiliary window, close, return to source | User can identify and dismiss the task |
| Focus moves correctly | Accessibility focus UI test/device run | new scene, external entry, validation error | Focus lands on useful content without stealing unrelated focus |
| Dynamic Type/localization works | Preview matrix plus target UI run | accessibility size, long strings, RTL | No clipped primary action or reversed meaning |
| Keyboard/pointer works | iPad/Catalyst physical input run | shortcuts, hover, selection, Full Keyboard Access | Touch/pointer/keyboard routes converge |
| AI states are semantic | VoiceOver task with fixtures | unavailable, partial, stale, failed | State/status/review/commit are announced clearly |
| Reduced effects remain usable | Settings run | reduced motion/transparency, increased contrast | Hierarchy and task completion survive the fallback |

## Performance, privacy, and release matrix

| Claim | Minimum proof | Edge cases | Evidence |
| --- | --- | --- | --- |
| Window creation is bounded | UI/performance test | repeated open/close, rapid values | No leaked tasks, controllers, model sessions, or callbacks |
| Resize is responsive | Hitch/performance run on representative target | large list, glass, AI partial output | No unacceptable hitch/memory/thermal regression |
| External payload is safe | Parser/security tests | malicious URL, oversized payload, unknown ID | Only typed validated data reaches feature state |
| Archive has intended scenes | Archive/Info.plist/target inspection | extension membership, platform conditions | Processed artifact contains expected scene/configuration |
| Release route works | Signed TestFlight/release smoke run | terminated process, system route, account state | Intended build identity and task behavior are recorded |

## Sources

- [Scenes](https://developer.apple.com/documentation/swiftui/scenes)
- [Windows](https://developer.apple.com/documentation/swiftui/windows)
- [WindowGroup](https://developer.apple.com/documentation/swiftui/windowgroup)
- [Window](https://developer.apple.com/documentation/swiftui/window)
- [openWindow](https://developer.apple.com/documentation/swiftui/environmentvalues/openwindow)
- [Presenting windows and spaces](https://developer.apple.com/documentation/visionos/presenting-windows-and-spaces)
- [System events](https://developer.apple.com/documentation/swiftui/system-events)
- [handlesExternalEvents(matching:)](https://developer.apple.com/documentation/swiftui/scene/handlesexternalevents%28matching%3A%29)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage)
- [UIApplicationSupportsMultipleScenes](https://developer.apple.com/documentation/BundleResources/Information-Property-List/UIApplicationSceneManifest/UIApplicationSupportsMultipleScenes)
- [UIScene](https://developer.apple.com/documentation/uikit/uiscene)
- [Windows HIG](https://developer.apple.com/design/human-interface-guidelines/windows)
- [Multitasking HIG](https://developer.apple.com/design/human-interface-guidelines/multitasking)
- [Mac Catalyst HIG](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [XCUITest](https://developer.apple.com/documentation/xctest)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

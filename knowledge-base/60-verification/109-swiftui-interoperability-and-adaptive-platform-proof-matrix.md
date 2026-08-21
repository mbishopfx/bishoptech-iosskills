# SwiftUI interoperability and adaptive-platform proof matrix

## Purpose

Use this matrix when a feature claims deterministic previews, correct
SwiftUI/UIKit composition, adaptive iPhone/iPad/Catalyst behavior,
accessibility across the bridge, on-device AI fixture safety, or Liquid Glass
adaptation. The proof must name the target and evidence level.

Record for every run:

- Xcode and SDK version;
- deployment target and target name;
- platform/device/OS build;
- build configuration;
- locale, layout direction, color scheme, contrast, Dynamic Type, motion,
  transparency, and input settings;
- fixture ID, source/domain revision, model/capability state;
- evidence artifact and date.

## Evidence levels

| Level | Can support | Cannot support by itself |
| --- | --- | --- |
| Official source | API/design intent and questions to verify | App compile or runtime behavior |
| Static architecture review | Ownership, target boundary, lifecycle contract | Rendering, accessibility task, device behavior |
| Named-target compile | Imports, declarations, target membership, availability branches | Permissions, hardware, physical feel, model readiness |
| Unit/feature test | Reducers, fixture state, callback mapping, cancellation, stale rejection | UIKit layout, system surfaces, VoiceOver ergonomics |
| Xcode preview | Controlled render across injected states/environment values | Real network, permission, model, hardware, release |
| Simulator/UI test | Deterministic navigation, focus, text, callback, layout | Physical camera/sensor/haptic/GPU/thermal behavior |
| Signed physical device | Named hardware, touch/input/accessibility, framework lifecycle | Other devices, production scale, App Store approval |
| Catalyst-on-Mac | Catalyst APIs, window, menus, pointer/keyboard, selection | Native macOS/AppKit, iPad multitasking, watch/visionOS |
| TestFlight/release | Distribution/install and scoped system behavior | Universal device coverage or production health |

## Fixture contract

Define a fixture record with:

| Field | Example |
| --- | --- |
| fixtureID | visual-review-large-type-rtl |
| featureState | loaded, failed, candidate, stale |
| domainID/revision | stable record and revision |
| sourceID/revision | image/document analyzed by AI or controller |
| locale/direction | en-US LTR, ar RTL |
| size/environment | compact/regular, large Dynamic Type, dark |
| capability | authorized, denied, unavailable, interrupted |
| candidateID/status | stable candidate with partial/ready/stale state |
| expectedCommands | typed actions recorded without side effects |
| expectedA11y | labels, values, traits, focus, reading order |
| expectedFallback | manual route or opaque/material/native surface |

Use deterministic IDs, sample assets, fake clocks, and fake services. Do not
make preview or unit fixtures depend on network, personal data, a live
controller, an Apple Intelligence model, or a device-only entitlement.

## Preview proof matrix

| Claim | Test | Evidence | Limit |
| --- | --- | --- | --- |
| State branches render | Empty/loading/ready/partial/stale/failed fixtures | Named previews or snapshot fixtures | Does not prove production state transitions |
| Preview dependencies are deterministic | In-memory store, fake clock, local asset, injected service | Preview code and repeatable render | Does not prove real service behavior |
| Trait variation works | Parameterized state/appearance/size/scene traits | Preview matrix | Does not prove every target/device |
| Large text is usable | Accessibility sizes and long strings | Preview plus semantic inspection | Does not prove physical reading/touch |
| RTL is correct | RTL fixture with directional actions and long copy | Preview/UI layout evidence | Does not prove every locale |
| AI preview is safe | Unavailable/partial/stale/review fixtures | Fixture output and state assertions | Does not prove model quality |
| Glass preview is coherent | Functional glass + opaque/material fallback | Environment fixtures | Does not prove physical material rendering |

A preview with a named device frame should be labeled as a preview. Do not call
it a device run.

## Environment and adaptation proof

Test the view as the environment changes during a session:

- compact to regular width;
- portrait to landscape;
- iPad split/resize;
- keyboard appears/disappears;
- light/dark and contrast changes where supported;
- Dynamic Type changes;
- RTL;
- scene active/inactive/background;
- reduced motion/transparency;
- available to unavailable capability or model.

Verify that:

- domain identity and revision do not change;
- draft text and selection persist;
- scroll target/focus policy is explicit;
- actions remain reachable and semantic;
- generated content reflows without fixed-height clipping;
- image fit/fill policy remains meaningful;
- bridge update does not recreate a costly session;
- the new layout does not duplicate a callback or command;
- the user can recover from the state after returning to the scene.

## UIViewRepresentable proof matrix

| Claim | Required test | Evidence |
| --- | --- | --- |
| Creates the correct view | makeUIView fixture | Named target compile and runtime |
| Updates idempotently | repeated SwiftUI updates with same/new inputs | Unit/feature log or test |
| Uses Coordinator correctly | delegate/target events map to typed feature events | Test with duplicate and reordered callbacks |
| Does not violate layout | no direct center/bounds/frame/transform mutation | Static review plus target layout run |
| Handles size | ProposedViewSize/sizeThatFits route where needed | Compact/regular/large text layout test |
| Cancels cleanly | view identity changes/background/teardown | Cancellation and stale-result test |
| Removes observers/targets | dismantle fixture and deallocation observation | Target run/instrumentation |
| Preserves accessibility | labels/values/traits/focus/hit region | Accessibility tree plus task run |
| Handles capability failure | denied/unavailable/interrupted/empty | UI fixture and device route |

A successful makeUIView call is not proof that the underlying camera,
document, audio, map, payment, or AI capability is available.

## UIViewControllerRepresentable proof matrix

Test:

1. presentation into the correct SwiftUI route;
2. update without restarting unrelated controller work;
3. delegate/callback translation;
4. permission denied and unavailable;
5. cancellation and dismissal;
6. partial/empty/invalid result;
7. source revision mismatch;
8. background/foreground or interruption;
9. teardown and late callback;
10. accepted result versus cancelled result.

Record raw controller output separately from the normalized candidate or domain
revision. A dismissed controller is not automatically a committed result.

## Hosting proof matrix

### UIHostingController

Verify in the UIKit target:

- root view initial inputs;
- rootView update;
- containment/presentation;
- safe area and sizing;
- trait/rotation/window changes;
- keyboard/focus;
- VoiceOver order and labels;
- dismissal and domain draft preservation;
- Liquid Glass/material appearance if used;
- cleanup after removal.

### UIHostingConfiguration

Use a real UIKit table or collection view and verify:

- reuse with different item IDs;
- image/model task cancellation on reuse;
- selection and deselection;
- dynamic height and long text;
- swipe/context actions;
- separators/backgrounds;
- Dynamic Type and RTL;
- VoiceOver cell/child order;
- scrolling and memory on a representative device.

A preview of a hosting configuration does not exercise UIKit reuse.

## Platform proof matrix

| Target | Minimum scenario |
| --- | --- |
| iPhone | touch flow, safe area, keyboard, VoiceOver, Dynamic Type, appearance |
| iPad | split/resize/orientation, pointer/keyboard, selection, sidebar/detail |
| Mac Catalyst | Catalyst compile/run on Mac, window resize, menus/shortcuts, pointer/focus |
| visionOS | named window/volume/immersive route, indirect input, comfort, accessibility |
| watchOS | glance, Digital Crown, Always On, pairing/offline, physical watch |

If a target is not in scope, record it as unsupported rather than allowing a
shared file's compile to imply support.

## AI and Liquid Glass proof

### AI candidate

Verify:

- model unavailable uses a manual or supported fallback;
- partial results retain one candidate identity;
- cancellation stops or ignores stale output;
- sourceID/sourceRevision is checked before review/commit;
- rejection preserves the source;
- acceptance creates only the intended new revision;
- generated text is not silently used as accessibility truth;
- privacy/retention policy is exercised;
- preview fixtures do not invoke the model.

### Functional glass

Verify:

- the glass group contains related controls;
- content remains primary and legible;
- actions remain semantic;
- reduced transparency/increased contrast have a complete fallback;
- appearance, colorful background, Dynamic Type, and orientation are tested;
- bridge content has compatible background/clipping/accessibility;
- effect completion is not treated as domain completion.

## Accessibility and input proof

Run a task, not only an audit:

1. open the target screen;
2. locate primary content;
3. identify loading/error/candidate state;
4. activate the primary action;
5. inspect/correct/accept or reject the AI candidate;
6. dismiss/cancel and recover;
7. repeat without color or animation;
8. repeat with the target's supported keyboard/pointer/alternate input.

Capture labels, values, traits, focus movement, rotor/linked groups, action
names, and whether decorative content is ignored. Inspect both SwiftUI and
UIKit accessibility trees when bridged.

## Performance and lifecycle proof

Measure a representative workload:

- number of bridge instances;
- view/controller creation/update frequency;
- cell reuse and scroll length;
- image decode and model work;
- callback frequency;
- material/effect layers;
- memory/CPU/GPU/frame hitch/energy/thermal behavior;
- Debug versus Release configuration;
- background/foreground and cancellation.

Use previews for iteration, unit/UI tests for deterministic behavior, and
Instruments/XCTest/MetricKit where the claim requires performance evidence.
Do not infer smoothness from a preview or newest-device simulator.

## Release evidence

For a scoped release claim, retain:

- target and deployment/SDK record;
- target membership and framework/resource inspection;
- entitlements/privacy strings/capability state;
- signed archive and installed build;
- physical target run;
- system/permission/account/model evidence;
- TestFlight or release configuration result;
- known unsupported platforms, OS versions, and devices.

Separate “preview renders,” “target compiles,” “bridge behaves in a named
run,” “assistive task completed,” “physical device works,” and “release is
ready.”

## Sources

- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Previewing your app’s interface in Xcode](https://developer.apple.com/documentation/xcode/previewing-your-apps-interface-in-xcode)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [UserInterfaceSizeClass](https://developer.apple.com/documentation/swiftui/userinterfacesizeclass)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [UIViewControllerRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentablecontext)
- [UIHostingController](https://developer.apple.com/documentation/swiftui/uihostingcontroller)
- [UIHostingConfiguration](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [UIKit](https://developer.apple.com/documentation/uikit)
- [Mac Catalyst](https://developer.apple.com/documentation/uikit/mac-catalyst)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Testing system accessibility features](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [XCUITest](https://developer.apple.com/documentation/xctest)
- [XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for Mac Catalyst](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Designing for visionOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)

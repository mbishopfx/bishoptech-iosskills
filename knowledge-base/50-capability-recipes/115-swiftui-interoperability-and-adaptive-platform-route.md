# SwiftUI interoperability and adaptive-platform capability route

## Use this route when

Use this route when an app idea needs:

- deterministic Xcode previews across feature states and environments;
- SwiftUI content inside an existing UIKit screen or cell;
- a UIKit view or controller inside SwiftUI;
- system or framework controllers that need a typed SwiftUI route;
- iPhone/iPad/Catalyst adaptation;
- conditional composition for visionOS/watchOS or another Apple target;
- Dynamic Type, locale, RTL, size-class, scene, appearance, and reduced-effect
  variation;
- Liquid Glass and on-device AI preview fixtures;
- lifecycle, cancellation, accessibility, performance, and release proof.

This route composes the existing previews, UIKit representable, platform
adaptation, layout, accessibility, Liquid Glass, AI, and target-configuration
pages. It focuses on how those routes meet in one app target.

## Route contract

    user outcome
      -> shared feature/domain contract
      -> target and environment matrix
      -> native SwiftUI route
      -> smallest UIKit/system bridge
      -> create/update/event/teardown lifecycle
      -> adaptive layout and input
      -> deterministic preview fixture
      -> compile/UI/device/release proof

Owners:

| Concern | Owner |
| --- | --- |
| Durable records/revisions | Domain store/use case |
| Feature state | Observable feature model |
| Target surface | SwiftUI view or platform adapter |
| Environment adaptation | SwiftUI environment/layout boundary |
| UIKit object | Representable/hosting boundary |
| Delegate/callback translation | Coordinator or typed adapter |
| AI request/candidate | On-device AI boundary |
| Preview fixture | Injected deterministic dependencies |
| Accessibility | Semantic SwiftUI/UIKit tree |
| Evidence | Target-specific verification packet |

## Phase 0: name the target matrix

Write the targets before choosing a shared view:

| Target | Minimum OS/SDK | Primary task slice | Native surface | Required device proof |
| --- | --- | --- | --- | --- |
| iPhone | named iOS deployment | focused task | SwiftUI navigation/controls | physical iPhone if hardware/system-dependent |
| iPad | named iPadOS deployment | context/detail or table | split/sidebar/toolbar | split/resize, keyboard/pointer, physical iPad if claimed |
| Mac Catalyst | named Catalyst target | window/command task | menus/toolbars/table | Catalyst run on Mac |
| visionOS | named visionOS target if included | window/spatial task | native window/volume/immersive | supported physical spatial device |
| watchOS | named watch target if included | glance/short action | watchOS SwiftUI/system surface | physical Apple Watch |

Do not list a platform merely because a shared file compiles. Mark a target
unsupported until its surface and proof are named.

## Phase 1: define state and fixture contracts

Feature state should be independent of preview or target:

    idle
      -> loading
      -> ready
      -> reviewCandidate
      -> committed
      -> stale/failed/cancelled

Fixture state should be explicit:

| Fixture field | Purpose |
| --- | --- |
| featureState | Deterministic screen branch |
| domainRevision | Prevents stale candidate/bridge results |
| locale/layoutDirection | Localization/RTL inspection |
| sizeClass/available proposal | Adaptive layout branch |
| color/contrast/transparency/motion | Appearance and accessibility |
| systemCapability | Available/denied/unavailable/expired |
| aiModelState | unavailable/preparing/partial/ready/failed |
| action recorder | Assert commands without side effects |
| clock/random/IDs | Stable previews and tests |

Do not put preview-only flags into domain state. Inject a fake service or
feature model that returns the desired branch.

## Phase 2: choose the native route before the bridge

Ask:

1. Does a SwiftUI control or container express the task?
2. Does a SwiftUI system surface own the needed capability?
3. Is the UIKit object required for a framework, existing screen, or system
   flow?
4. Is the bridge view-level or controller-level?
5. Does the host target own presentation, reuse, or scene lifecycle?

Use a representable for a missing UIKit capability, not for a cosmetic copy.
Prefer UIHostingConfiguration for SwiftUI content inside a UIKit table or
collection cell. Prefer UIHostingController for a SwiftUI screen inside UIKit
containment or presentation.

## Phase 3: create the bridge

For UIViewRepresentable:

    makeUIView
      -> minimal UIKit creation/configuration
      -> makeCoordinator if callbacks need translation
      -> updateUIView for idempotent current inputs
      -> coordinator sends typed events
      -> dismantleUIView removes observers/cancels bridge work

For UIViewControllerRepresentable:

    makeUIViewController
      -> configure controller with current request
      -> coordinator/delegate events
      -> updateUIViewController without restarting unrelated work
      -> explicit dismissal/cancel/result policy
      -> dismantleUIViewController cleanup

Never set the UIKit object's center, bounds, frame, or transform against
SwiftUI's layout contract. If the bridge needs sizing behavior, use the
documented representable sizing route for the selected SDK.

## Phase 4: translate callbacks to feature commands

A callback route should be:

    raw UIKit/system callback
      -> typed adapter event
      -> request/source identity check
      -> feature validation
      -> draft/candidate/domain revision
      -> explicit UI update or commit

Examples:

- controller dismissed -> cancelled unless an accepted result was delivered;
- empty picker result -> noSelection, not empty domain data;
- partial scan -> partial candidate, not complete document;
- delegate callback after teardown -> ignored;
- old source callback -> stale and not applied;
- permission failure -> denied/unavailable with recovery;
- UIKit text change -> feature input after normalization, not a direct database write.

Keep callback idempotency and cancellation tests beside the adapter.

## Phase 5: host SwiftUI in UIKit

Use UIHostingController when UIKit owns the containing view-controller
graph. Pass a root view with explicit feature dependencies. Treat rootView
updates as composition updates, not persistence.

For table/collection cells:

- identify the current cell item;
- set SwiftUI content from the current item and revision;
- reset image/model tasks on reuse;
- keep selection and swipe actions in the UIKit owner;
- expose cell actions through typed feature commands;
- test dynamic height, focus, labels, and reuse.

Do not claim a hosted cell is correct because it appears in a preview. The
UIKit target owns reuse, selection, scrolling, cell lifecycle, and layout.

## Phase 6: adapt with environment and layout

Use these inputs deliberately:

| Need | SwiftUI route |
| --- | --- |
| Compact/regular available space | horizontalSizeClass/verticalSizeClass |
| Text scaling | dynamicTypeSize and semantic text styles |
| RTL | layoutDirection and leading/trailing alignment |
| Locale/formatting | locale and localized formatters |
| Appearance | colorScheme/colorSchemeContrast |
| Pixel/display behavior | displayScale/pixelLength |
| Scene lifecycle | scenePhase |
| Reduced effects | accessibilityReduceMotion/accessibilityReduceTransparency |
| Flexible composition | ViewThatFits/AnyLayout/Layout proposals |
| Platform-specific framework | availability/target conditional at adapter boundary |

Do not use a device model to decide whether a split layout fits. Do not
rebuild the feature state when the size class changes. Preserve selection,
focus, drafts, scroll identity, source revision, and candidate identity.

## Phase 7: build the preview matrix

Minimum previews:

1. compact light, ready;
2. regular dark, ready;
3. large Dynamic Type;
4. RTL and long localized copy;
5. loading/error/denied/unavailable;
6. reduced motion/transparency/increased contrast;
7. UIKit bridge active and bridge failure;
8. AI model unavailable/partial/ready/stale;
9. keyboard/pointer/focus if the target supports it;
10. system handoff or controller dismissal branch where relevant.

Each preview should have a name, stable fixture, target/availability note, and
no network/model/permission dependency. Use preview arguments for bounded
state variation. Use a unit/UI fixture when the behavior needs assertions
rather than visual inspection.

## Phase 8: Liquid Glass and functional surfaces

A functional glass route:

    system/native control
      -> related action group
      -> glass or standard material
      -> safe-area/toolbar/tab placement
      -> reduced-effects fallback
      -> accessibility/input proof

A UIKit bridge inside that group must have compatible background, clip,
focus, and accessibility behavior. Do not make a custom glass shell around a
system picker, camera controller, or hosted cell merely to imitate a
screenshot. Keep content and model candidates outside the action group.

## Phase 9: on-device AI fixture route

The preview adapter should supply:

    model unavailable
      -> manual fallback
    preparing
      -> cancel/progress
    partial
      -> stable candidate identity
    ready
      -> review actions
    stale
      -> source mismatch/rerun
    failed
      -> recoverable error

The feature command performs:

    accept candidate
      -> compare sourceID/sourceRevision
      -> deterministic validation
      -> commit new revision
      -> record result

The actual model call belongs in the production AI adapter. A preview should
not make a system API request or pretend to possess a model. A model output
should not replace source, accessibility, permission, or domain truth.

## Phase 10: accessibility and alternate input

Verify the same command through:

- SwiftUI semantic controls;
- UIKit control accessibility;
- VoiceOver order and focus;
- Voice Control names;
- keyboard/pointer focus and shortcuts;
- Switch Control where supported;
- Dynamic Type and large content;
- RTL and localized copy;
- reduced motion/transparency/contrast.

When wrapping a UIKit control, avoid duplicate SwiftUI and UIKit elements.
When hosting SwiftUI in a cell, ensure the cell's selection and the SwiftUI
child action do not compete. Make the action hierarchy clear.

## Phase 11: evidence packet

| Route | Minimum evidence |
| --- | --- |
| Preview fixture | Xcode preview matrix with deterministic dependency injection |
| Environment adaptation | Preview/UI cases plus target compile |
| UIViewRepresentable | Named target compile, update/teardown tests, accessibility and layout run |
| UIViewControllerRepresentable | Controller presentation/dismissal/cancel/result tests and named target run |
| UIHostingController | UIKit containment, rootView update, sizing, traits, dismissal |
| UIHostingConfiguration | Real cell reuse/selection/scroll/Dynamic Type/VoiceOver |
| iPad | resize/split/keyboard/pointer plus physical device if claim is hardware |
| Catalyst | Catalyst target build/run on Mac with menus/window/focus |
| AI | model-unavailable/partial/stale/review/commit fixtures plus supported device |
| Liquid Glass | target/device appearance, contrast, reduced transparency, functional action |
| Release | signed archive/install/TestFlight/system/permission evidence as scoped |

A preview proves controlled rendering. A simulator can prove deterministic
layout and UI flow. Only the named target/device/system/release run closes its
corresponding claim.

## Stop conditions

Stop and repair the architecture if:

- a bridge is present only for visual imitation;
- UIKit layout properties are mutated from a representable;
- a coordinator owns domain persistence or bypasses revision checks;
- a preview uses a network, personal photo, permission, store, or model;
- a size class branch changes business truth;
- a hosted cell ignores reuse identity;
- a target-specific API is assumed from a different platform;
- a candidate is committed on controller dismissal or animation completion;
- a glass shell hides a missing action or accessibility route;
- a screenshot is being used as device, model, or release evidence.

## Sources

- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Previewing your app’s interface in Xcode](https://developer.apple.com/documentation/xcode/previewing-your-apps-interface-in-xcode)
- [EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues)
- [horizontalSizeClass](https://developer.apple.com/documentation/swiftui/environmentvalues/horizontalsizeclass)
- [verticalSizeClass](https://developer.apple.com/documentation/swiftui/environmentvalues/verticalsizeclass)
- [UserInterfaceSizeClass](https://developer.apple.com/documentation/swiftui/userinterfacesizeclass)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [layoutDirection](https://developer.apple.com/documentation/swiftui/environmentvalues/layoutdirection)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [UIViewControllerRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentablecontext)
- [UIHostingController](https://developer.apple.com/documentation/swiftui/uihostingcontroller)
- [UIHostingConfiguration](https://developer.apple.com/documentation/swiftui/uihostingconfiguration)
- [UIKit](https://developer.apple.com/documentation/uikit)
- [Mac Catalyst](https://developer.apple.com/documentation/uikit/mac-catalyst)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for Mac Catalyst](https://developer.apple.com/design/human-interface-guidelines/mac-catalyst)
- [Designing for visionOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)

# SwiftUI interoperability, previews, and adaptive platforms

## Purpose

A SwiftUI app becomes durable when its visual design can be exercised in a
controlled preview, hosted in the correct target, adapted to the available
space and environment, and bridged to UIKit only at a clear ownership
boundary. This is especially important for iOS 26 work that combines native
Liquid Glass surfaces, physical-device capabilities, and on-device AI.

The composition contract is:

    feature/domain state
      -> target and environment
      -> native SwiftUI surface
      -> smallest necessary UIKit/system bridge
      -> explicit lifecycle and callback translation
      -> adaptive layout/input/accessibility
      -> preview and deterministic fixture
      -> simulator/device/release proof

A preview is a design instrument. A representable is an interop boundary. A
size class is an input to layout. A UIKit controller is not automatically
SwiftUI state. Keep those statements separate.

The exact declarations and availability must be compiled with the selected
Xcode, SDK, deployment target, and target platform. The current Apple
documentation may contain APIs from a newer SDK, future-release material, or
a platform that is not part of an iOS target.

## The composition ownership matrix

| Layer | Owns | Does not own |
| --- | --- | --- |
| Domain model/use case | Records, validation, revisions, authorization rules, durable side effects | View frames, UIKit delegates, preview-only sample data |
| Feature state | Loading, empty, draft, candidate, error, cancellation, route state | UIKit view hierarchy layout or model truth from a callback |
| SwiftUI view | Declarative composition, environment-driven adaptation, semantic controls | Long-lived UIKit sessions, raw controller lifecycle, database writes from body |
| Preview fixture | Deterministic dependencies, state/environment combinations, sample assets | Real permissions, network, model readiness, physical rendering |
| UIViewRepresentable | Create/update/tear down a UIKit view and translate callbacks | Direct control of SwiftUI-managed frame/bounds/transform |
| UIViewControllerRepresentable | Embed a controller-level flow and translate lifecycle/result events | Automatic synchronization of controller internals to all SwiftUI state |
| UIHostingController | Host SwiftUI in UIKit containment/presentation | Turning UIKit lifecycle into domain truth without an explicit feature contract |
| UIHostingConfiguration | Host SwiftUI inside a UIKit table/collection cell | Replacing UIKit cell reuse, selection, and layout proof |
| Environment | Current locale, size, appearance, accessibility, scene, and target context | Durable business decisions or a universal device identity |
| AI adapter | Capability/model request, candidate, provenance, cancellation | Automatically committing a candidate or changing accessibility truth |
| Evidence packet | What a named test/build/device proved | General claims about every device or future SDK |

## 1. Use previews as a matrix, not a screenshot

Apple's SwiftUI preview system can generate dynamic, interactive previews and
the Preview macros can vary traits, arguments, viewpoints, and scene-specific
configuration. Use those capabilities to exercise the state and environment
space that a person will encounter:

| Preview axis | Representative cases |
| --- | --- |
| Feature state | empty, loading, ready, partial, stale, denied, unavailable, failed, review |
| Appearance | light, dark, increased contrast, reduced transparency |
| Typography | default, large Dynamic Type, very long localized strings |
| Layout | iPhone compact, iPad regular, split/resize, landscape, keyboard visible |
| Direction/language | English, a long expansion language, right-to-left |
| Input | touch-first, keyboard/pointer focus, VoiceOver-visible labels |
| Source | local asset, remote placeholder, revoked permission, stale revision |
| AI | model unavailable, partial candidate, ready-to-review, rejection, stale |
| System surface | navigation, sheet, toolbar/tab, widget/control handoff where relevant |

A preview should be deterministic. Inject a fake clock, stable IDs, in-memory
model container, local assets, and a predictable service. Never make the
canvas depend on a network request, camera permission, iCloud account,
StoreKit transaction, HealthKit store, or an available Foundation Model.

### Preview traits and arguments

Use named previews to make design intent searchable. Parameterized previews
are useful when the same view needs to be compared across an enum of state or
a bounded set of environments. Keep the argument set small enough that every
variant remains reviewable.

Conceptually:

    Preview("Review - large type", traits: ...)
      -> review fixture
      -> large Dynamic Type / dark / compact width
      -> visual and semantic inspection

Do not encode device-specific behavior only as a preview name. Record the
target, supported platform, minimum OS, and the environment values that the
fixture sets. A preview with a device frame is not a physical-device result.

### Preview dependency boundaries

Prefer one of these boundaries:

1. an initializer that accepts a feature state and typed actions;
2. a model/service injected through the environment;
3. a preview-only dependency container;
4. a deterministic fixture factory shared by previews and unit/UI tests.

Avoid a singleton “preview mode” flag that leaks into production state.
Avoid making a view inspect whether it is running in a canvas to bypass
authorization, loading, or error behavior. The fixture should provide a
known dependency, not teach the production view to lie.

## 2. Define the target and environment contract

SwiftUI provides EnvironmentValues that describe the current interface and
system context. Useful inputs include:

- horizontal and vertical size class;
- Dynamic Type size;
- color scheme and color-scheme contrast;
- display scale and pixel length;
- locale and layout direction;
- scene phase and active appearance;
- accessibility reduce-motion, reduce-transparency, differentiate-without-
  color, and related settings;
- platform-specific values supplied by the target.

Read the environment where it affects presentation. Keep domain logic
independent from a view's current size class or color scheme.

### Size classes are available space

Horizontal and vertical size classes communicate the amount of visual space
available to the view. SwiftUI can change them when device orientation or
iPad multitasking changes. They are not a permanent “this is an iPhone” or
“this is an iPad” identity.

Use size classes to choose a layout grammar:

| Constraint | Possible layout |
| --- | --- |
| Compact horizontal space | Focused single-column content and a toolbar/sheet action route |
| Regular horizontal space | Split content/detail, inspector, or persistent context |
| Compact vertical space | Reduce optional decoration and avoid fixed-height text regions |
| Regular vertical space | Allow more context, not merely larger cards |
| Size class changes at runtime | Preserve domain state, focus, selection, and draft while switching layout |

Use ViewThatFits, AnyLayout, layout proposals, container-relative sizing, and
standard containers when they express the relationship better than a size
class branch. A size class can choose the composition; it should not become a
large table of magic device names.

### Locale, direction, and text

A layout that only works in English and left-to-right order is not a native
layout. Test:

- long titles and labels;
- plural and grammatical variation;
- right-to-left layout direction;
- date, number, currency, and measurement formatting;
- accessibility-size Dynamic Type;
- narrow width and large text at the same time;
- text inside a UIKit bridge and a SwiftUI host;
- generated AI strings that are longer or differently localized than the
  source prompt.

Keep directional spacing and placement semantic. Use system alignment,
paddings, and layout direction rather than manually placing a “left” action
where the product means “leading” or “back.”

## 3. UIKit bridge selection

Use the narrowest bridge that solves the product outcome:

| Need | First route | Ownership |
| --- | --- | --- |
| SwiftUI in a UIKit screen | UIHostingController | UIKit owns containment/presentation; SwiftUI owns its view inputs and state |
| SwiftUI in a UIKit cell | UIHostingConfiguration | UIKit owns reuse/selection; SwiftUI owns cell content |
| A missing UIKit UIView inside SwiftUI | UIViewRepresentable | SwiftUI supplies inputs; bridge creates/updates/tears down the view |
| A UIKit controller flow | UIViewControllerRepresentable | SwiftUI owns route state; controller owns internal flow; coordinator translates |
| Existing system framework controller | Controller representable or native SwiftUI route | Raw result is normalized and validated before domain commit |
| A platform-native system surface | Native SwiftUI/AppKit/WatchKit/visionOS API | Do not replace it with an imitation bridge |

Use a native SwiftUI view or system surface first when it already expresses the
outcome. A UIKit bridge carries UIKit lifecycle, main-thread, layout,
accessibility, focus, pointer, keyboard, and target-availability obligations
that the native SwiftUI control would otherwise provide.

Do not bridge a view just to copy a visual screenshot. Bridge when the
framework capability, existing target, or specific UIKit behavior is the
reason.

## 4. UIViewRepresentable lifecycle

Apple's UIViewRepresentable contract is create, update, and tear down. The
system controls the UIKit view's layout-related center, bounds, frame, and
transform. Do not set those properties directly from the bridge because that
conflicts with SwiftUI's layout system.

Treat the bridge as a state machine:

    SwiftUI inputs
      -> makeUIView once for an identity
      -> updateUIView idempotently
      -> coordinator translates UIKit events
      -> feature validates event/result
      -> dismantleUIView cancels/removes bridge work

### Creation

makeUIView should create and minimally configure the UIKit object. Do not
start a long-lived camera, audio, network, or model operation merely because
the view was constructed. Capability start belongs to an explicit feature or
lifecycle command with authorization and cancellation.

### Update

updateUIView reconciles current inputs with an existing object. It should be
idempotent:

- do not add the same delegate or observer repeatedly;
- do not restart a session for an unrelated SwiftUI body update;
- do not overwrite active UIKit text/selection with stale input;
- do not rebuild a costly renderer when only an accessible label changed;
- do not send a candidate result to the bridge until the source revision
  matches the visible source.

If the bridge needs a preferred size, use the documented sizeThatFits route
when available and let SwiftUI make the final layout decision.

### Coordinator

A coordinator translates delegates, target-action, notifications, and
controller callbacks. Keep it small:

- store only bridge-local references and typed callbacks;
- attach a request/source identity to asynchronous work;
- normalize duplicate completion/dismissal/cancellation callbacks;
- send typed events or values, not raw controller objects;
- keep UI mutations on the actor required by UIKit/SwiftUI;
- clear callbacks and cancel tasks during teardown.

The coordinator is not a second app model and should not become the owner of
persistence, entitlements, or a long-lived AI session without an explicit
feature boundary.

### Teardown

dismantleUIView should remove targets/delegates/observers and cancel work
owned by the bridge. Teardown is not a save confirmation. A view can be
removed because navigation changed, a sheet was dismissed, a scene was
recreated, or a parent identity changed.

Record the result separately:

    controller/bridge callback
      -> typed feature event
      -> validation/source-revision check
      -> draft or candidate
      -> explicit commit

## 5. UIViewControllerRepresentable lifecycle

Use UIViewControllerRepresentable for controller-level flows such as a
system picker, document/capture controller, share/presentation controller,
or an existing UIKit feature that owns a view hierarchy.

Keep responsibilities visible:

| Concern | SwiftUI/feature | UIKit/controller |
| --- | --- | --- |
| Presentation route | Sheet/full-screen/navigation state and dismissal policy | Controller presentation mechanics |
| Inputs | Current source, configuration, draft, or request ID | Controller-specific properties |
| Lifecycle | Start/stop/cancel policy and scene state | make/update/dismantle callbacks |
| Delegate events | Coordinator/async event adapter | Framework callback and controller state |
| Result truth | Normalized candidate or domain revision | Raw controller output |
| Accessibility | SwiftUI route and accessible description | Native UIKit elements and controller metadata |

Dismissal is an event, not proof that the person accepted or saved the result.
If the controller can be cancelled, denied, interrupted, or return partial
data, expose those states in the feature.

## 6. Host SwiftUI in UIKit

UIHostingController is a real UIViewController. UIKit owns its containment,
presentation, safe-area relationships, trait changes, status-bar behavior,
rotation/window context, and dismissal. SwiftUI owns the root view's
declarative content and injected feature state.

When the host updates rootView:

- preserve the domain model and draft outside the hosting controller;
- pass explicit inputs instead of reaching into UIKit globals;
- do not confuse a new rootView value with a new domain record;
- re-check focus, selection, accessibility order, and animation transaction;
- test containment and sizing on the actual UIKit target.

UIHostingConfiguration is the appropriate route when a UIKit table or
collection cell hosts SwiftUI content. UIKit still owns cell reuse,
selection, separators, swipe behavior, and scrolling. SwiftUI content must
reset asynchronous image/model state for the current item identity. A
successful hosted cell preview does not prove UIKit reuse or physical
scrolling.

## 7. Platform composition

### iPhone

Keep one focused task, semantic controls, safe-area-aware actions, and clear
navigation. Test touch, keyboard, VoiceOver, large text, and the system
keyboard. A compact surface can use a sheet or toolbar route instead of
squeezing a split layout into a narrow width.

### iPad

Use regular space for parallel context only when it shortens the task:
sidebar/detail, source/review, inspector, table/detail, or persistent search.
Test split view, resize, rotation, pointer, keyboard, Apple Pencil where
relevant, drag/drop, selection, and accessibility focus.

### Mac Catalyst

Mac Catalyst is a UIKit-based Mac target. It needs a target-specific compile
and device run on a Mac. Re-check menus, keyboard shortcuts, pointer/hover,
selection, window resizing, toolbar density, table behavior, and focus.
An iPad simulator is not Catalyst proof, and Catalyst is not a native AppKit
proof.

### visionOS and watchOS

If the project includes these targets, prefer their native scene and input
routes. visionOS windows, volumes, immersive spaces, gaze/indirect gestures,
comfort, and spatial accessibility are not established by an iOS
representable. watchOS glanceability, Digital Crown, Always On, and paired
device behavior are not established by a compact iPhone preview.

Keep target-specific branches at an adapter or surface boundary:

    shared feature/domain contract
      -> iOS/iPad presentation
      -> Catalyst presentation
      -> visionOS presentation
      -> watchOS presentation

Do not share a visual wrapper solely because it compiles. Share what preserves
meaning and test each platform's task.

## 8. Liquid Glass in previews and bridges

Use previews to compare functional Liquid Glass state across environment
fixtures:

- content underneath remains legible;
- the glass group contains related controls;
- material, spacing, and safe-area behavior are target-appropriate;
- reduced transparency and increased contrast keep actions understandable;
- a standard Material or opaque fallback is available;
- the glass does not present a generated candidate as committed truth.

A UIKit bridge does not automatically inherit the SwiftUI visual contract.
If a UIKit view appears inside a functional glass group, confirm its
background, clipping, focus, accessibility, and contrast behavior rather
than layering a glass shell over an opaque UIKit surface.

## 9. On-device AI preview fixtures

Preview an AI feature as a typed state adapter, not a live model request:

    model unavailable
      -> deterministic fallback
    preparing
      -> progress/cancellation fixture
    partial
      -> stable candidate ID
    ready
      -> review fixture
    stale source
      -> rerun/ignore fixture
    accepted
      -> committed revision fixture

Preview data should include sourceID, sourceRevision, candidateID,
capability/model state, confidence/coverage only if supplied, and explicit
accept/reject/edit actions. Do not put a real personal image, API key, or
unbounded generated text in a preview fixture.

The same feature view should render a model-unavailable fixture without
requiring the model. The actual on-device model path is verified separately
on a supported physical device and target.

## 10. Cross-boundary accessibility

When SwiftUI and UIKit are composed, inspect both trees:

- the hosted SwiftUI view's labels, values, traits, grouping, and focus;
- the representable's UIKit accessibility elements and order;
- duplicate labels created by wrapping a UIKit control in a SwiftUI label;
- hit regions versus visible/background geometry;
- Dynamic Type in UIKit labels and SwiftUI text;
- Voice Control names and keyboard/pointer routes;
- reduced motion/transparency and contrast;
- focus transfer on presentation, dismissal, and target changes.

A wrapper that compiles and has an accessibility identifier may still expose
the wrong action, duplicate content, or an impossible focus order. Test the
person's task with the actual target and input method.

## 11. Interop anti-patterns

Repair the design when you see:

- a representable is used for a native SwiftUI control only to obtain a
  different corner radius or tint;
- makeUIView starts a global service with no explicit stop;
- updateUIView recreates a session on every body update;
- the bridge writes center/frame/bounds/transform directly;
- a coordinator owns the database or app-wide model session;
- UIKit callback results bypass source revision and validation;
- UIHostingController dismissal is treated as save confirmation;
- a UIKit cell preview is treated as reuse/performance proof;
- size class is treated as a device identity;
- platform branches mutate domain truth instead of choosing a surface;
- a model is invoked from a preview or a preview bypasses a real failure state;
- Liquid Glass is added to conceal UIKit or layout ownership problems;
- a preview is cited as physical-device, accessibility, model, or release proof.

## Proof contract

At minimum, record:

| Claim | Required evidence |
| --- | --- |
| Preview covers states | Named preview matrix with deterministic dependencies and environment values |
| Native SwiftUI layout adapts | Preview/UI fixtures plus target compile for the selected SDK |
| UIKit bridge maps lifecycle | Unit/feature tests for create/update/events/cancel/stale result/teardown |
| UIKit owns layout correctly | Named target compile and runtime layout/trait/rotation test |
| SwiftUI hosted in UIKit | UIKit target containment, rootView update, sizing, dismissal, accessibility |
| Hosted cell is correct | Real UIKit table/collection reuse, selection, scrolling, Dynamic Type, VoiceOver |
| iPad/Catalyst route is native | Named target run with resize, keyboard/pointer, menus, focus, and device proof |
| AI fixture is safe | Model-unavailable/partial/stale/review/commit fixture and source revision checks |
| Glass adapts | Appearance/contrast/transparency/device review with functional action proof |
| Release works | Signed build/archive and target-specific permissions, entitlements, system, or TestFlight evidence |

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
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)

# SwiftUI navigation and presentation proof matrix

## Purpose

Use this matrix to prove route identity, navigation transitions, modal
presentations, detents, sizing, dismissal, deep-link convergence, AI review,
accessibility, and physical/system behavior separately.

Related pages:

- [SwiftUI navigation transitions and presentation](../42-framework-deep-dives/79-swiftui-navigation-transitions-and-presentation.md)
- [Navigation transitions and presentation design](../21-design-deep-dives/107-navigation-transitions-and-presentation-design.md)
- [SwiftUI navigation and presentation route](../50-capability-recipes/110-swiftui-navigation-presentation-route.md)
- [SwiftUI navigation and presentation recipes](../70-code-recipes/122-swiftui-navigation-presentation-recipes.md)
- [Universal Links, Handoff, and scene-delivery proof matrix](97-universal-links-handoff-scene-proof-matrix.md)

## Evidence levels

| Level | Packet | Proves | Does not prove |
| --- | --- | --- | --- |
| N0 | Task/hierarchy contract | The feature needs navigation, sheet, cover, popover, or system surface | Implementation or delivery |
| N1 | Route/presentation model | Typed identity, owner, restoration, dismissal, and draft policy are explicit | Compiler/API correctness |
| N2 | Named-target compile | Selected NavigationStack/presentation/transition APIs build | Runtime delivery or accessibility |
| N3 | Preview/fixture matrix | Empty, loaded, unavailable, proposal, applying, saved, failed, long-text states render | Real scene/system delivery or physical behavior |
| N4 | UI automation | Push/pop, present/dismiss, detent selection, buttons, and visible results work | Human VoiceOver task completion or public Universal Links |
| N5 | Accessibility/adaptation run | Reduce Motion, Dynamic Type, contrast/transparency, input, keyboard, orientation, and compact layouts work | All devices or App Review |
| N6 | Async/domain run | Dismissal, cancellation, stale result, draft protection, and commit state are correct | Visual smoothness or system handoff |
| N7 | Physical/system run | Zoom, haptics, detents, device layout, Safari/Handoff/system delivery | Every supported device and future OS |
| N8 | Signed/release run | Archive target/resource/capability/privacy and TestFlight route are correct | Production health or untested external payloads |

## Navigation route matrix

| Claim | Setup | Assertion | Boundary |
| --- | --- | --- | --- |
| Path is authoritative | NavigationStack with a bound typed path | Path changes reflect push/pop and restore | Does not prove destination data is current |
| Route is lightweight | Encode/decode route values | Stable identity survives round trip | Does not prove domain persistence |
| Value destination resolves | NavigationLink value and navigationDestination | Current record appears for the route | Does not prove deep-link delivery |
| Missing route is safe | Delete or revoke record before destination resolves | Unavailable/stale recovery view, no crash | Does not prove authorization service correctness |
| Programmatic navigation works | Set path or item binding | Destination appears and can pop | Does not prove animations or focus |
| Back behavior works | User back/swipe and programmatic pop | Path/presentation state reconciles | Does not prove draft policy |
| Multi-window state is isolated | Two scenes with different paths | One scene does not overwrite the other | Does not prove restoration after termination |

## Matched-transition matrix

| Claim | Setup | Required assertion | Boundary |
| --- | --- | --- | --- |
| Source is identified | Namespace and stable matchedTransitionSource ID | Source is tied to the intended record | Does not prove destination route |
| Zoom is paired | Destination navigationTransition zoom uses same ID/namespace | Visual source/destination relationship is correct | Does not prove reduced motion |
| Destination modifier is scoped | Transition on destination outside layout container | Navigation transition is applied to the intended view | Does not prove every platform |
| Source disappears safely | Navigate after list scroll/reload or source removal | Destination remains valid from route identity | Does not prove source data freshness |
| Reduced-motion fallback works | Reduce Motion enabled | Route/destination remain understandable without zoom | Does not prove user comfort in all cases |
| Accessibility identity is preserved | VoiceOver on source and destination | Same object/action is labeled and focusable | Does not prove visual continuity |

## Presentation matrix

| Claim | Fixture | Assertion |
| --- | --- | --- |
| Sheet presentation is stateful | Boolean and item variants | Binding reflects present/dismiss and item identity |
| Full-screen cover is appropriate | Long/immersive fixture | Clear title, finish/cancel, and dismiss route |
| Detents are meaningful | Small/medium/large or custom set | Content and primary action are visible at each detent |
| Selection binding is safe | Programmatic detent changes | State updates without confusing domain state |
| Content interaction is intentional | Scrollable content plus resize gesture | Scroll/resize behavior matches task |
| Drag indicator is understandable | Hidden/visible policy fixture | User can discover resize/dismiss affordance |
| Background interaction is safe | Parent controls behind sheet | No conflicting or duplicate side effect |
| Compact adaptation is correct | iPhone/iPad size-class fixtures | Presentation remains usable and intentional |
| Sizing adapts | Long/short/localized content | Fitted/form/page/custom policy does not clip |
| Content margins are scoped | Scroll content and indicators | Intended placement changes without misaligning indicators |
| Background is legible | Light/dark/contrast/transparency fixtures | Text, status, and controls remain readable |
| Interactive dismissal is safe | Dirty draft/in-flight operation | Confirmation or explicit disabled policy protects data |

## Draft and dismissal matrix

| Scenario | Required behavior |
| --- | --- |
| Clean sheet dismissed | Parent reconciles current source |
| Dirty sheet canceled | Draft is discarded only with clear user intent |
| Dirty sheet swiped | Confirmation offers save/discard/cancel |
| AI generation canceled | Task cancellation and late-result suppression are tested |
| AI proposal dismissed | Candidate/source policy is explicit |
| Applying dismissed | User sees whether the domain operation continues, finishes, or was canceled |
| Record becomes stale | Review shows freshness/conflict route before commit |
| Authorization changes | Destination shows unavailable/re-auth path |

## AI review matrix

| State | Presentation proof | Domain proof |
| --- | --- | --- |
| unavailable | Explanation and manual route visible | Availability gate returns deterministic fallback |
| generating | Status and cancel visible | Task starts once and honors cancellation |
| proposal | Source/candidate/provenance/review actions | Candidate is typed/validated and not committed |
| applying | Duplicate protection and scope | Authorized domain operation begins once |
| saved | Committed record/revision visible | Persistence/sync result is authoritative |
| failed/refused | Reason, preserved source, recovery | No false saved state or success feedback |

## Accessibility matrix

| Setting/input | Test | Evidence |
| --- | --- | --- |
| Reduce Motion | Navigate/present/dismiss/review | Same task completes with automatic/identity/fade route |
| VoiceOver | Enter destination and presentation | Title, status, source, action, and dismiss are announced |
| Dynamic Type | Largest supported text and long localization | No hidden primary action or clipped state |
| Reduced transparency | Glass and presentation background | Surface boundaries and text remain legible |
| Increased contrast | Selected/disabled/error/saved states | Distinction survives without subtle material |
| Voice Control | Say navigation, accept, cancel, dismiss actions | Names are unique and discoverable |
| Switch Control | Complete a full review flow | No timing-only gesture is required |
| Keyboard/pointer | iPad/Mac input where supported | Focus and hover do not alter semantic task |
| RTL/localization | Long translated route labels and content | Layout and transition direction remain correct |

## Deep-link and system-delivery matrix

| Claim | Test | Boundary |
| --- | --- | --- |
| External payload maps to a route | Valid URL/activity fixture | Does not prove public association/source app |
| Cold-start route works | Terminated app receives valid payload | Does not prove warm/multi-window convergence |
| Warm route works | Active app receives payload | Does not prove current authorization/freshness |
| Invalid route is safe | Malformed/unknown/deleted IDs | Does not prove security without validation tests |
| Widget/App Intent route converges | System payload to typed reducer | Does not prove extension/system delivery |
| Handoff route works | Two-device source/destination run | Does not prove every account/network state |

## Performance and physical matrix

| Claim | Evidence |
| --- | --- |
| Navigation/presentation motion is smooth | Animation Hitches/Instruments run on representative device |
| Presentation sizing is stable | Long-content/keyboard/Dynamic Type run under device build |
| Glass arrival shell performs | Effect count/container/spacing trace under maximum fixture |
| Zoom is comfortable | Physical device with Reduce Motion and normal motion |
| Haptic feedback is meaningful | Supported device result-state run |
| Background interaction is safe | Physical input run across detents and interruptions |
| Release route is intact | Signed archive/TestFlight target/resource/capability inspection |

Record build, SDK, OS, device, scene/window, fixture, appearance settings,
model/profile, route payload, and any measured performance result. A preview,
screenshot, single callback, or simulator run is not a complete proof packet.

## Sources

- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
- [NavigationTransition](https://developer.apple.com/documentation/swiftui/navigationtransition)
- [matchedTransitionSource(id:in:)](https://developer.apple.com/documentation/swiftui/view/matchedtransitionsource%28id%3Ain%3A%29)
- [ZoomNavigationTransition](https://developer.apple.com/documentation/swiftui/zoomnavigationtransition)
- [Modal presentations](https://developer.apple.com/documentation/swiftui/modal-presentations)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [PresentationSizing](https://developer.apple.com/documentation/SwiftUI/PresentationSizing)
- [contentMargins(_:_:for:)](https://developer.apple.com/documentation/SwiftUI/View/contentMargins%28_%3A_%3Afor%3A%29-1lt8b)
- [PresentationBackgroundInteraction](https://developer.apple.com/documentation/swiftui/presentationbackgroundinteraction)
- [Modality](https://developer.apple.com/design/human-interface-guidelines/modality)
- [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)

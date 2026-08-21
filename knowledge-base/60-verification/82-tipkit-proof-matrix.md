# TipKit proof matrix

TipKit has persistent state, rule evaluation, user actions, display-frequency policy, and optional cross-target/cloud storage. A rendered tip or passing configuration call is only a narrow signal. This matrix separates source, compile, deterministic, UI, device/system, and release evidence.

## Evidence ladder

| Level | Evidence | What it proves | What it does not prove |
| --- | --- | --- | --- |
| Source | Current Apple TipKit and HIG pages | Documented API intent and design boundaries | The selected SDK’s exact macro signatures or a useful product experience. |
| Compile | Named app/extension target and SDK | Imports, macros, protocol conformances, target membership, warnings | Rule usefulness, persistence, accessibility, or CloudKit behavior. |
| Fixture | Controlled parameter/event/datastore state | Deterministic eligibility, invalidation, grouping, and reset behavior | Real app task completion or cross-device sync. |
| UI automation | SwiftUI/UIKit flow with TipKit test controls | Presentation, action, dismissal, navigation, and accessibility labels | Physical readability, system popover behavior, or production frequency. |
| Signed device | Release-like device build | Appearance, persistence, Dynamic Type, VoiceOver, process restart, device-family layout | CloudKit production, App Store, or every OS version. |
| System/cloud | App Group/CloudKit/account/device flow | Cross-target/cross-device TipKit persistence and recovery | Universal sync or product understanding. |
| Release | Archive/TestFlight/App Store configuration | Target membership, entitlements, datastore/container configuration, signing | Whether tips are respectful or actually useful. |

## Claim matrix

| Claim | Minimum evidence | Common false proof |
| --- | --- | --- |
| TipKit is configured before display | App initialization compile/run, success and thrown-error branches | A `TipView` exists in a preview. |
| The tip appears only when useful | Parameter/event fixtures below/at/above eligibility plus task-based UI run | `showAllTipsForTesting()` alone. |
| A feature-completion rule is correct | App-owned completion state changes, then parameter/event update, then status transition | Tip was opened or dismissed. |
| Display frequency is respectful | Multiple eligible tips across restart/time fixture with configured frequency | One screenshot of a single tip. |
| Actions work safely | Action button navigation, unavailable/cancelled paths, confirmation/idempotency for side effects | Action handler exists in source. |
| Dismissal/invalidation is respected | Close, action-performed, max-count, max-duration, and reset fixtures | `status == invalidated` without reason inspection. |
| TipGroup order is correct | First-available and ordered group fixtures with changing eligibility | Group compiles. |
| App/extension tips share state | Signed targets, App Group membership, datastore-location proof, process/restart run | Both targets use the same identifier in source. |
| TipKit CloudKit sync works | Development/production container, account state, two-device run, offline/conflict/deletion record | A CloudKit container option compiles. |
| AI-related tip is trustworthy | Model availability/review fixture and deterministic TipKit eligibility | AI generated tip copy or proposal displays. |
| Tip is accessible | VoiceOver task, Dynamic Type, contrast, Reduce Motion, Voice Control, keyboard/pointer/Switch Control as applicable | Accessibility audit or default `TipView` assumption. |
| Native Liquid Glass integration is correct | Light/dark/material/content tests, focus/order, dismissal, no overlay collision | Custom blur looks visually similar in one preview. |
| Tip content is localized and current | Long strings, RTL/localization, feature terminology, unavailable state | English screenshot. |
| Release configuration is valid | Signed archive, target membership, entitlements, container/datastore, privacy and App Group checks | Debug build succeeds. |

## Configuration and datastore fixtures

Test:

- `Tips.configure()` succeeds with application-default datastore;
- configuration throws and the feature remains usable without tips;
- custom URL/group-container datastore is invalid or unavailable;
- multiple targets use an intentionally shared App Group;
- CloudKit container is missing, unauthorized, offline, or account unavailable;
- configuration is attempted twice and the app handles the current SDK contract;
- `Tips.resetDatastore()` occurs before configuration in tests;
- reset is absent from production startup paths;
- app restarts with persisted parameter/event/dismissal state;
- data deletion/clear-state policy is explicit.

## Rule and parameter fixtures

For every parameter rule, assert:

```text
default value -> expected status
value changes to eligible -> tip becomes available
value changes away -> tip becomes pending or invalidated as documented
app restarts -> persistence matches the chosen option
transient parameter -> reset behavior is intentional
```

For every event rule, assert:

- zero donations;
- one donation below threshold;
- threshold reached;
- donations outside the configured time range;
- donation limit behavior;
- structured donation values serialize and remain within privacy scope;
- async donation cancellation/error policy;
- event donation occurs after product truth changes, not before.

## Display and action fixtures

| Fixture | Expected result |
| --- | --- |
| Tip eligible near a visible control | Correct TipView/popover placement and readable content. |
| Tip target scrolls off screen | No stale overlay or focus trap; inline layout remains coherent. |
| Person dismisses tip | Tip respects closure/invalidation; feature remains accessible. |
| Person performs tip action | Action navigates to the intended safe destination and records feature truth separately. |
| Person triggers action while feature unavailable | Clear fallback, no silent permission/side-effect path. |
| Two tips become eligible | Configured display frequency/group policy controls presentation. |
| Tip appears during a system sheet/keyboard/recording flow | Tip is delayed or omitted according to product policy. |
| AI model unavailable | Tip does not promise availability; feature shows deterministic fallback. |
| Tip action would modify external state | Confirmation/review occurs outside the tip before commit. |

## Group and status fixtures

Test `TipGroup.currentTip` and `currentTipUpdates` when:

- the first tip is unavailable and the second is eligible;
- an ordered tip is completed;
- a tip is dismissed;
- all tips become pending or invalidated;
- a new feature state makes a later tip eligible;
- the app process is terminated while observing updates;
- the view disappears and the observation task is cancelled.

Record `available`, `pending`, and `invalidated` with the invalidation reason. Do not equate pending with broken or invalidated with completed.

## Accessibility and visual fixtures

Run the task “discover feature -> act -> confirm completion” under:

- VoiceOver, including focus after tip dismissal/action;
- largest supported Dynamic Type sizes;
- Increase Contrast and Reduce Transparency;
- Reduce Motion;
- Voice Control and keyboard/pointer/Switch Control;
- dark/light appearance, vivid backgrounds, and Liquid Glass materials;
- localization, long titles/messages, and right-to-left layout;
- iPhone/iPad/resized-window layouts where supported;
- UIKit and SwiftUI presentation variants if both ship.

Record the result as task completion evidence, not just the presence of labels.

## AI and privacy fixtures

- AI feature eligible but model unavailable;
- AI feature returns low confidence or no result;
- AI output is reviewed/rejected/edited;
- generated explanation references stale feature state;
- AI proposal would trigger a purchase, message, deletion, share, or hardware action;
- parameter/event derivation strips raw personal data;
- TipKit datastore is inspected for unintended sensitive content;
- local-only processing is distinguished from later user-initiated sharing.

TipKit should not become an invisible behavioral-profile store. Use the smallest deterministic parameter/event shape needed for helpful eligibility.

## Verification record template

```text
Tip: <identifier>
Target/SDK: <named values>
Presentation: TipView | popoverTip | UIKit
Configuration: <options/datastore/frequency>
Eligibility: <parameters/events/rules>
Fixture results: <pending/available/invalidation>
Action result: <navigation/feature truth/side effect proof>
Persistence: <restart/App Group/CloudKit evidence>
Accessibility: <settings and task result>
AI boundary: <model availability/review/stale state>
Release: <archive/entitlement/container/target membership>
Result: pass | fallback | blocked | fail
Open evidence: <remaining claim>
```

## Sources

- [TipKit](https://developer.apple.com/documentation/tipkit)
- [Tips.configure](https://developer.apple.com/documentation/tipkit/tips/configure%28_%3A%29)
- [Configuration options](https://developer.apple.com/documentation/tipkit/tips/configurationoption)
- [Datastore locations](https://developer.apple.com/documentation/tipkit/tips/configurationoption/datastorelocation)
- [CloudKit containers](https://developer.apple.com/documentation/tipkit/tips/configurationoption/cloudkitcontainer)
- [Display frequency](https://developer.apple.com/documentation/tipkit/tips/configurationoption/displayfrequency)
- [Tip](https://developer.apple.com/documentation/tipkit/tip)
- [Rule](https://developer.apple.com/documentation/tipkit/tips/rule)
- [Parameter](https://developer.apple.com/documentation/tipkit/tips/parameter)
- [Event](https://developer.apple.com/documentation/tipkit/tips/event)
- [Event donation](https://developer.apple.com/documentation/tipkit/tips/event/donate%28%29)
- [TipGroup](https://developer.apple.com/documentation/tipkit/tipgroup)
- [Tip status](https://developer.apple.com/documentation/tipkit/tips/status)
- [Tip invalidation reasons](https://developer.apple.com/documentation/tipkit/tips/invalidationreason)
- [TipKit testing and reset](https://developer.apple.com/documentation/tipkit/tips/resetdatastore%28%29)
- [TipView](https://developer.apple.com/documentation/tipkit/tipview)
- [Offering help](https://developer.apple.com/design/human-interface-guidelines/offering-help)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest and XCUIAutomation](https://developer.apple.com/documentation/xctest)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

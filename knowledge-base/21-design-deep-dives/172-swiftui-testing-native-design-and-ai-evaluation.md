# SwiftUI testing, native design, Liquid Glass, and AI-evaluation design

A polished native screen is also a test surface. Its labels, roles, focus,
state transitions, reduced-effects fallback, and fixture contract determine
whether a solo developer or an LLM can verify it without guessing.

Use this page with the [testing and release-assurance framework route](../42-framework-deep-dives/144-swiftui-testing-xctest-ui-device-release-assurance-route.md), the [capability route](../50-capability-recipes/175-swiftui-testing-xctest-ui-device-release-assurance-route.md), the [proof matrix](../60-verification/169-swiftui-testing-xctest-ui-device-release-assurance-proof-matrix.md), and the [recipes](../70-code-recipes/187-swiftui-testing-xctest-ui-device-release-assurance-recipes.md).

## Design the semantic contract before the glass

For each screen, name the domain state, visible state, semantic controls, and
evidence hook before selecting materials or animation.

| Design contract | Example |
| --- | --- |
| state identity | `review-ready`, `review-loading`, `review-conflict` |
| primary action | “Accept suggestion” with a clear enabled/disabled reason |
| recovery action | “Keep original”, “Retry”, “Change permission”, or “Cancel” |
| spoken label/value | VoiceOver can hear the field, revision, status, and action |
| automation identity | Stable identifier such as `review-accept` |
| fixture identity | Same fixture ID appears in state tests, launch arguments, and proof |
| source revision | User-approved record revision used by any generated proposal |
| side-effect boundary | A separate commit action after review |

Identifiers make a workflow addressable; they do not replace a human-readable
label or accessible role. A label communicates to people, an identifier
stabilizes automation, and the domain state explains what the control actually
does. Keep all three coherent.

## Liquid Glass should follow function

Use Liquid Glass to unify functional controls or create hierarchy where the
system material helps the user understand the interface. Do not make every
card, row, and text block translucent. Keep content surfaces legible and let
the primary action remain visually and semantically obvious.

For each glass group, design the states before styling:

| State | Native visual behavior | Testable behavior |
| --- | --- | --- |
| idle | restrained grouping around the action cluster | action exists, label/value are complete |
| loading | clear progress with no misleading completion signal | cancellation and zero-event behavior |
| ready | stable content with controlled material hierarchy | accepted state and source revision |
| error | strong recovery affordance and sufficient contrast | retry, fallback, and error announcement |
| conflict | compare or review surface rather than silent morphing | local/remote/ancestor provenance |
| reduced effects | solid/opaque fallback with the same actions | reduced-transparency and reduced-motion task |
| large text | material yields to content and wrapping | Dynamic Type layout and focus order |

Morphing or animated glass should communicate a real relationship between
controls. If the transition adds no meaning, keep the transition simple. Test
the action and state change, not only a screenshot taken at one frame.

## Build accessibility into the visual hierarchy

The screen should remain usable when effects are reduced, text is enlarged, or
the person navigates by VoiceOver, keyboard, pointer, Voice Control, or Switch
Control.

Review each screen for:

- a heading or context announcement that explains where focus landed;
- a stable reading order that follows the task rather than the z-order of
  decorative layers;
- labels, values, hints, and traits that distinguish status from action;
- a hit target and keyboard/pointer focus treatment that remain visible over
  glass;
- an explicit disabled state with a reason, not just a dimmed control;
- an alert or sheet that returns focus to the next meaningful element;
- a reduced-motion/reduced-effects path that preserves timing and action;
- contrast and text wrapping across light/dark mode, high contrast, and
  supported localization lengths.

Accessibility Inspector audits common issues and can be automated from a UI
test. That is a useful regression layer, but design review still needs a
task-based VoiceOver run and the relevant alternate-input settings. “The audit
passed” is not the same claim as “a person completed the task.”

## Make state fixtures part of the design system

Every important state should have a stable fixture ID and a visible, semantic
representation. A fixture is not a screenshot; it is a small, reproducible
domain input with the permission, model, network, account, and revision context
needed to produce the state.

Recommended fixture families:

- first launch, empty, loading, ready, stale, and partial data;
- denied, restricted, revoked, and unavailable permissions;
- network offline, retryable failure, conflict, and account transition;
- model preparing, unavailable, refusal, malformed output, and accepted
  proposal;
- large text, reduced motion, reduced transparency, increased contrast, and
  localization variants;
- extension/system-surface unavailable, delayed, or delivered with stale data.

Use the fixture ID in:

1. Swift Testing arguments and deterministic assertions;
2. XCTest launch arguments and seeded local state;
3. accessibility task scripts and screenshots/logs;
4. AI evaluation records and human-review samples;
5. proof-matrix rows and release notes.

This gives an LLM a stable route from design intent to implementation and
verification without relying on visual guessing.

## Design AI review as a user-owned transition

An on-device AI surface should expose the relationship between source and
proposal:

    approved source revision -> generated proposal -> deterministic checks
        -> user review/edit -> explicit commit -> new source revision

The UI should show when the proposal is based on stale input, when a field is
unsupported, and when the model is unavailable. A loading shimmer, Liquid Glass
panel, or confident sentence must not imply that the proposal is true or has
been committed.

Use a compact review component with:

- source labels and revision/date when relevant;
- changed-field summaries, not an opaque paragraph;
- “Keep original”, “Edit”, and “Accept” actions with distinct side effects;
- a clear reason when Accept is disabled;
- model/profile/version provenance suitable for a diagnostic record;
- no hidden network fallback or system action;
- accessibility labels that identify proposed versus current values.

The model should not own the design-system state. The domain owns the record,
the validator owns admissibility, the UI owns the review interaction, and the
commit coordinator owns the side effect.

## Design test seams without exposing private product API

Make the architecture testable through explicit boundaries:

| Dependency | Test seam |
| --- | --- |
| time | injected clock or date provider |
| randomness | deterministic random source |
| network | protocol-backed fake service |
| model | typed proposal provider with unavailable/refusal cases |
| persistence | temporary store or model adapter |
| permissions | explicit authorization state fixture |
| system surface | projection/command adapter with delivery result |
| audio/camera/sensor | input sequence or hardware fixture boundary |
| account/sync | account state and change-event reducer |

Avoid adding test-only decoration to the production view when an existing
semantic control or observable state can carry the contract. View models,
reducers, observable stores, and pure formatters are more reliable test targets
than direct assertions on SwiftUI’s internal rendering tree.

## Native-design evidence ladder

The design review should say which layer it has completed:

| Level | Evidence |
| --- | --- |
| D0 | Apple source and HIG decisions recorded |
| D1 | State/fixture matrix and semantic control contract reviewed |
| D2 | Swift Testing state/reducer/validator coverage |
| D3 | XCTest workflow and automated accessibility audit |
| D4 | VoiceOver/alternate-input/Dynamic Type/reduced-effects task on a named device |
| D5 | Release/TestFlight build with the exact target/resources/entitlements |

Do not use D1 or D2 language to claim D4 behavior. Do not call a material
choice “Apple-approved” because the screen resembles an Apple surface. The
system owns its system surfaces; app design should use native controls and
materials within the app’s own responsibility.

## Role handoff for the open-source skill bundle

The design skill should emit a small contract that the testing and audit skills
can consume:

- screen/state names and fixture IDs;
- semantic labels, identifiers, roles, values, hints, and focus destinations;
- Liquid Glass groups, motion purpose, and reduced-effects fallbacks;
- supported text sizes, locales, input modes, and system settings;
- user-approved source revision and generated-proposal fields;
- primary/recovery actions and their side-effect boundaries;
- evidence levels required for design sign-off.

This turns design guidance into an executable handoff for an LLM-led team while
preserving uncertainty and avoiding a claim of automatic Apple approval.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)

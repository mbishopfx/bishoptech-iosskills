# Liquid Glass State, Morphing, and AI Review Shells

Liquid Glass is most useful when it clarifies a functional layer: navigation, a small group of related controls, or a stateful action that sits above changing content. An AI proposal is content that needs scrutiny, not a reason to place a translucent panel behind every paragraph. Keep the generated proposal in the content/review layer and use glass only for the small, semantic actions that let a person accept, edit, reject, retry, or inspect it.

## API route matrix

| Design need | SwiftUI route | Ownership and configuration | Proof boundary |
| --- | --- | --- | --- |
| Apply a custom effect to one functional view | `glassEffect(_:in:)` with `Glass.regular`, `.clear`, `.identity`, optional `tint`, and `interactive` | Selected SwiftUI SDK/deployment target, shape, control semantics, and accessibility fallback | Compile, preview, Dynamic Type/contrast/reduced-transparency states, and physical-device legibility/hit-target proof. |
| Render related glass controls as one group | `GlassEffectContainer(spacing:content:)` plus `glassEffect` on each child | Group membership and spacing are intentional; the container is not a universal screen background | Preview spacing/merge behavior, transitions, performance, VoiceOver order, and actual device material behavior. |
| Morph one glass control into another | `glassEffectID(_:in:)`, `glassEffectTransition(.matchedGeometry/.materialize)` and `withAnimation` | Stable `Namespace`, unique IDs, state-driven insertion/removal, and reduced-motion alternative | Test identity changes, missing/duplicate items, interrupted animation, Reduce Motion, and content/state labels. |
| Merge dynamic effects into a deliberate union | `glassEffectUnion(id:namespace:)` | Same union ID/namespace only for a functional cluster; dynamic data must have stable identity | Test at rest and during updates, layout changes, large text, hit regions, and accidental grouping. |
| Use a system glass control style | `buttonStyle(.glass)` or `.glassProminent` where supported | Prefer system control hierarchy and current platform treatment before custom effects | Target SDK/device, standard semantics, disabled/loading/destructive states, and platform adaptation. |
| Present a reviewable AI proposal | Native `NavigationStack`, `Form`, `sheet`, `confirmationDialog`, `ProgressView`, `ContentUnavailableView`, and a small glass action cluster | Proposal/source/validation/commit states stay app-owned; model availability and tools stay outside the view | Review/edit/reject/commit, model unavailable/refusal, accessibility focus, cancellation, and persistence result. |

## Layering rule for AI features

Use three explicit layers:

1. **Content layer:** source material, generated proposal, provenance, confidence/unknown state, and editable fields. Use normal text, forms, lists, and media so the person can read and compare the output.
2. **Functional layer:** `GlassEffectContainer` only for related actions such as `Edit`, `Approve`, `Reject`, `Retry`, or a compact progress/status control. Keep labels and accessibility actions semantic.
3. **System layer:** model availability/settings, permission sheets, share sheets, App Intents, Writing Tools, Image Playground, notifications, and other system-owned surfaces. Do not recreate these with app-owned glass.

The glass action cluster must reflect the same state as the content. If a proposal is still generating, the cluster exposes progress/cancel; if validation fails, it exposes the exact repair path; if the record is committed, it exposes the resulting domain state. A color, blur, morph, or icon alone is never the state contract.

## State choreography

```text
idle -> checkingAvailability -> inputReady
inputReady -> generating -> proposalReceived
proposalReceived -> validating -> reviewable | invalid | refusal | failed
reviewable -> editing -> validating
reviewable -> committing -> committed | conflict | failed
generating -> cancelled | unavailable | contextExceeded | failed
```

Use a stable domain operation ID and keep these values separate:

| State/value | What it means |
| --- | --- |
| `modelAvailability` | Whether the selected model/use case can accept a request now. |
| `input`/`sourceRevision` | The exact user-approved source or record revision that was sent. |
| `proposal` | Generated content or structured output, still untrusted. |
| `validation` | Deterministic schema, permission, range, duplicate, and policy checks. |
| `reviewDraft` | The person’s editable corrections and explicit choice. |
| `commitResult` | The canonical domain operation result, conflict, or error. |
| `surfaceProjection` | Widget/share/App Intent/Live Activity/system projection of confirmed state only. |

Do not let a view transition to “saved” because a model response arrived or an animation completed. The commit service must return that state.

## Morphing rules

- Use `glassEffectID` only for a genuine identity relationship across a view hierarchy transition. The ID does not make two unrelated controls equivalent.
- Use `matchedGeometry` when the effect should morph between nearby related states; use `materialize` when an effect is appearing/disappearing without a meaningful counterpart.
- Tune `GlassEffectContainer` spacing with the interior layout spacing. Apple’s current guidance notes that spacing affects when effects blend and merge; too much spacing can cause a group to blend at rest.
- Use `glassEffectUnion` for a single functional shape made from dynamic members, not for unrelated actions that merely share a row.
- Keep model-generated text out of identity labels used for morphing. A changing title should not accidentally change the stable control ID or cause an unstable transition.
- Reduce or remove nonessential morphing under Reduce Motion while keeping the same action, label, and focus destination.

## Adaptation and accessibility matrix

| Condition | Required response |
| --- | --- |
| Dynamic Type/long localization | Let labels wrap or recompose; do not fix glass control heights around one language. Move secondary actions into a menu or sheet when needed. |
| Increased contrast/reduced transparency | Preserve a readable opaque/standard-material fallback and sufficient separation from content. |
| Reduce Motion | Keep state changes and focus, remove nonessential morphing/scale/parallax, and avoid implying progress through motion alone. |
| VoiceOver | Expose the proposal, source/provenance, validation state, and actions in an intentional order; custom glass remains a semantic Button/Menu/Toggle. |
| Voice Control/Switch Control/keyboard/pointer | Provide named actions, predictable focus/selection, and non-gesture paths. Test the actual review workflow, not just the static card. |
| Compact width/iPad/visionOS | Use platform-native navigation and sheets/inspectors; do not force one floating glass panel across every device family. |
| Model unavailable/refusal | Keep the source and manual path visible; do not show a disabled glass ornament with no explanation. |

## Review-shell composition

```text
NavigationStack
  -> source/provenance content
  -> editable proposal Form or detail
  -> validation/error/unknown region
  -> GlassEffectContainer
       -> Edit
       -> Reject
       -> Approve / Save
       -> Retry / Cancel when relevant
  -> canonical result or recovery route
```

Use `sheet` for a focused review when the person should make a deliberate decision before changing the underlying record. Use `confirmationDialog` for a small set of consequential choices, not as a substitute for editing generated fields. Move accessibility focus to the proposal/result or error explanation after an operation, and return focus predictably after dismissal.

## Verification matrix

| Evidence | What to verify |
| --- | --- |
| Source/compile | Exact SwiftUI symbols, selected SDK/deployment target, Foundation Models import/signature, target membership, and availability checks. |
| Preview/fixture | Every proposal state, long text, empty/invalid/unknown, light/dark, large text, localization, reduced transparency, reduced motion, and injected deterministic model result. |
| Behavior | Generate/cancel/retry, refusal, context overflow, validation repair, edit/review, duplicate approve, conflict, persistence failure, and stale source revision. |
| Physical device | Liquid Glass legibility/performance, touch/hit targets, VoiceOver/Voice Control/Switch Control, keyboard/pointer where supported, model readiness, thermal/memory, and actual system surfaces. |
| Release | Signed target, privacy manifest, AI disclosure/metadata, entitlement/configuration, model/OS/device matrix, TestFlight, and product claims limited to tested behavior. |

## Sources

- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [glassEffect transition modifier](https://developer.apple.com/documentation/swiftui/view/glasseffecttransition%28_%3A%29)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)

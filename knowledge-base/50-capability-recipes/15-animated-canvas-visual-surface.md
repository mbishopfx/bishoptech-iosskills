# Animated Canvas visual surface

This recipe composes a bounded custom-rendering layer with native SwiftUI state, optional TimelineView cadence, semantic content, functional Liquid Glass controls, and an optional on-device AI visual suggestion. Use it for an ambient processing surface, waveform, particle field, custom progress view, data texture, or status visualization that needs more visual character than standard Shapes provide.

It is not a compiled app template. Select the target, deployment target, resources, accessibility route, motion policy, and physical-device workload before implementation.

## User outcome

> A person can understand the current state of a feature through a rich visual surface, pause or control it with native controls, and still complete the task when motion, shaders, GPU resources, or the model suggestion are unavailable.

The Canvas is a projection. The feature state and user action remain owned by normal SwiftUI/domain code.

## Route map

    user intent or source state
      -> normalized VisualSnapshot
      -> motion/accessibility/performance policy
      -> Canvas or Shape renderer
      -> semantic text and controls
      -> optional functional Liquid Glass action group
      -> pause/reduce/fallback route

For a visual data chart, prefer Swift Charts. For a rich 2D surface that does not need individual mark semantics, Canvas is a candidate. For a full GPU pipeline, route to Metal.

## Responsibility matrix

| Layer | Owns | Must not own |
| --- | --- | --- |
| Feature/domain state | Progress, source revision, authorization, task status, user-selected mode | Per-frame graphics state or arbitrary shader parameters. |
| Visual normalizer | Clamps values, chooses detail level, maps domain state to scene parameters | Inventing source values or hiding stale/unknown state. |
| Canvas/GraphicsContext | Drawing paths, images, symbols, masks, filters, and bounded interpolation | Text-heavy semantics, controls, permissions, or irreversible actions. |
| TimelineView | Date/cadence-driven redraw of a scene snapshot | A guarantee of frame rate, source freshness, or background execution. |
| Semantic overlay | Title, state, labels, exact values, controls, focus, gestures, and accessibility | Pretending drawn pixels are independently accessible. |
| Liquid Glass group | Functional navigation or related action controls | Decorative haze over critical text or the only state signal. |
| AI adapter | Bounded visual suggestion proposal and model fallback | Arbitrary shader code, asset loading, domain mutation, or accessibility overrides. |

## Scene contract

Use a small, Sendable snapshot:

    struct VisualSnapshot: Sendable, Equatable {
        let progress: Double
        let phase: Double
        let detail: DetailLevel
        let stateLabel: String
        let sourceRevision: String?
    }

    enum DetailLevel: Sendable {
        case full
        case reduced
        case staticFallback
    }

Normalize progress to a known range, make phase deterministic for tests, and carry enough state to explain unavailable, paused, stale, and completed conditions. Do not derive a “successful” animation merely because a renderer is still running.

## Native screen composition

    NavigationStack
      -> title and semantic state label
      -> bounded Canvas visual surface
      -> progress/value/detail text
      -> pause/reduce/retry controls
      -> optional Liquid Glass action group
      -> review, save, or system handoff

Keep the visual surface inside a defined frame and clipping policy. Give the screen a stable layout at compact and regular widths. Do not let a custom renderer own safe-area decisions that belong to the screen shell.

Use ViewThatFits, AnyLayout, or a custom Layout when the visual and control arrangement changes with width. The semantic state and actions must survive both layouts. If the Canvas is decorative, it can disappear in a compact or Assistive Access route without removing the state explanation.

## Motion and cadence policy

Choose an explicit mode:

| Mode | Visual behavior | User meaning |
| --- | --- | --- |
| Static | One deterministic frame or progress state | Motion is disabled, unnecessary, or unavailable. |
| Gentle | Low-amplitude, bounded redraw with a minimum interval | Ambient feedback without demanding attention. |
| Interactive | Phase follows a user gesture or active task | Motion explains direct manipulation or live progress. |
| Paused | Last meaningful frame plus state label | Work or animation is paused; do not imply live freshness. |

Read Reduce Motion and user preferences before selecting the mode. Use TimelineView cadence to simplify detail when updates are coarse. Avoid using the animation schedule as a substitute for a real sensor, playback clock, or background task.

## Optional AI suggestion

Foundation Models can propose a visual style for a user’s chosen mode, but the route should be useful without it:

    domain state
      -> bounded visual suggestion request
      -> typed proposal
      -> validator
      -> accessibility/motion policy
      -> VisualSnapshot and renderer

Example:

    struct VisualSuggestion: Sendable {
        let paletteRole: String
        let motion: MotionProfile
        let density: Double
        let emphasis: Double
    }

Validate every field against app-owned allowlists and ranges. Keep palette roles semantic rather than accepting arbitrary colors when contrast or platform adaptation matters. Clamp density and emphasis, replace unsupported motion with static/gentle mode, and reject unknown shader or asset references. A model response never becomes executable graphics code.

Show a model-unavailable, refusal, context-limit, or invalid-proposal state as a normal fallback. The visual surface should not imply that Apple Intelligence is available merely because the screen has an AI setting.

## Accessibility and alternate input

Choose the semantic route before styling:

- decorative Canvas: hide it from assistive technologies and expose a nearby state description;
- progress/status visual: expose label, value, unit, source freshness, and paused/unavailable state;
- interactive visual: place semantic controls or accessibility actions over the interaction region;
- data visualization: use Swift Charts or a chart descriptor/table route;
- complex custom control: use a tested SwiftUI/UIKit accessibility bridge.

Do not require a person to tap a tiny drawn particle or scrub a Canvas to discover the only critical value. Test VoiceOver, Voice Control, Switch Control, keyboard/full keyboard access, Dynamic Type, RTL, increased contrast, reduced transparency, Reduce Motion, and localization.

## Failure and recovery

| State | Preserve | Offer |
| --- | --- | --- |
| Preparing | User intent and source revision | Progress, cancellation, and retry. |
| Source unavailable | Last confirmed state and explanation | Manual, imported, or static route where appropriate. |
| Shader unavailable | Semantic state and standard renderer | Canvas/Shape fallback or static view. |
| Reduced motion | Meaning and action controls | Static or low-motion representation. |
| Resource pressure/thermal | Durable state and latest confirmed result | Lower detail, pause, or defer work. |
| Model unavailable | Deterministic visual policy | Continue with default visual parameters. |
| Task cancelled/replaced | Confirmed result and user choice | Stop redraw and suppress stale updates. |
| Save/action failure | Current visual state and draft | Retry, review, or return to editable state. |

The fallback should state what changed when the difference matters: “Paused,” “Reduced motion,” “Live visual unavailable,” or “Using standard appearance.”

## System projections

Only project a compact, semantic state to widgets, Live Activities, or App Intents:

- a widget can show current progress, timestamp, and a static representation;
- a Live Activity can show a real time-bounded task if its lifecycle is justified;
- an App Intent can pause, resume, or query the domain task through the same authorized use case;
- a share/export route should send an approved static representation, not an unbounded shader or private model transcript.

System surfaces do not run the in-app Canvas as an always-live process. Validate the current state and target-specific rendering constraints at the handoff.

## Evidence plan

| Layer | Evidence |
| --- | --- |
| Source | Current Canvas, GraphicsContext, TimelineView, shader, HIG motion/accessibility, and Liquid Glass pages. |
| Compile | Named target, deployment target, imports, resource/shader membership, availability branches, and test scheme. |
| Fixture | Static, gentle, interactive, paused, reduced, unavailable, stale, cancelled, and invalid-suggestion snapshots. |
| UI | Compact/regular layout, control/focus behavior, state labels, gestures, cancellation, and system handoff parsing. |
| Accessibility | Complete the user task with VoiceOver, Voice Control, Switch Control, keyboard, Dynamic Type, contrast, reduced transparency, Reduce Motion, and RTL. |
| Device | Frame/cadence, memory, GPU, thermal/battery, touch, haptic/audio alternative, and visual legibility on representative hardware. |
| Release/system | Signed resources, privacy configuration, widget/Live Activity/App Intent target, system invocation, and claim wording. |

## Variants

- AI processing backdrop: model state is shown through a bounded visual suggestion and a clear text status; no model output is treated as domain truth.
- Local sensor visualizer: source adapter owns sampling/backpressure, while Canvas renders the latest normalized snapshot.
- Playback waveform: source time and playback state own progress; TimelineView only redraws the projection.
- Focus or breathing atmosphere: static and reduced-motion modes are first-class; the visual never replaces user controls or health claims.
- Custom progress card: a Canvas ring or field surrounds native labels, controls, and a reviewable completion state.

## Sources

- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [TimelineView](https://developer.apple.com/documentation/swiftui/timelineview)
- [TimelineSchedule](https://developer.apple.com/documentation/swiftui/timelineschedule)
- [AnimationTimelineSchedule](https://developer.apple.com/documentation/swiftui/animationtimelineschedule)
- [Drawing and graphics](https://developer.apple.com/documentation/swiftui/drawing-and-graphics)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [ShaderLibrary](https://developer.apple.com/documentation/swiftui/shaderlibrary)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [Human Interface Guidelines motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)

# Custom rendering and animation proof matrix

Use this matrix for Canvas, GraphicsContext, TimelineView, SwiftUI shader modifiers, and custom visual layers behind Liquid Glass. It keeps a beautiful visual surface from being mistaken for an accessible control, a fixed-rate animation, or proof of physical GPU and thermal behavior.

## Claim-to-evidence matrix

| Claim | Required artifact | Test or run | What it proves | What it does not prove |
| --- | --- | --- | --- | --- |
| The renderer API is available | Current Apple docs and target project | Compile Canvas, GraphicsContext, TimelineView, schedules, and selected modifiers in the named deployment target | Symbols/signatures compile in that target | Physical rendering, performance, or every OS/device |
| The visual is the right tool | Design brief and route decision | Review standard SwiftUI, Shape, Canvas, shader, and Metal alternatives | The implementation has an intentional ownership boundary | That the visual is useful or comfortable without task testing |
| Scene values are truthful | Normalized VisualSnapshot and source revision | Unit-test ranges, missing/partial/stale/cancelled/replaced states | Renderer receives validated app-owned state | Source service correctness or live freshness |
| Canvas semantics are covered | Semantic text, controls, overlay, table, or accessibility descriptor | Complete the task without tapping individual drawn elements | Critical information and actions are available non-visually | Human comprehension in all locales/devices |
| Canvas interactivity is safe | Overlay controls/accessibility actions and hit-region design | Touch, pointer, keyboard, Voice Control, Switch Control, and cancellation tests | Interaction targets are semantic and cancellable | Physical comfort or frame timing without hardware |
| Motion is optional | Reduce Motion policy and static/reduced fixture | Change Reduce Motion, pause, background/foreground, and finish the task | Meaning and actions survive without continuous motion | User comfort for every person or display |
| Timeline cadence is bounded | Schedule choice, minimum interval, context-cadence policy | Inject dates/cadence in tests and measure observed updates | Renderer uses schedule information deliberately | Guaranteed refresh rate, background execution, or battery life |
| Shader fallback works | Shader source/resource membership and standard-renderer fallback | Unsupported/disabled/error/reduced-motion paths | The feature remains usable without the effect | Feature support on every GPU/OS |
| Liquid Glass remains legible | Layering design, contrast strings, reduced-transparency route | Increased contrast, reduced transparency, Dynamic Type, RTL, light/dark, compact width | Controls and text remain legible above the visual | Physical touch comfort or release-wide behavior |
| Animation performs acceptably | Fixture, device/build record, Instruments or XCTest metrics | Measure frame time/cadence, memory, GPU/CPU, thermal, and battery under max workload | The named workload met its recorded threshold | All devices, future OS versions, or production reliability |
| AI visual suggestion is bounded | Versioned schema, allowlists, validator, fallback | Invalid colors/assets/shaders, excessive motion, private text, refusal, unavailable model | Untrusted output cannot bypass renderer policy | Model quality or availability outside the tested environment |
| System projection is safe | Widget/Activity/App Intent target and static projection | Signed invocation, stale state, target termination, deep link, revalidation | System surface receives a bounded domain projection | In-app Canvas behavior, OS ranking, or universal delivery |
| Release claim is supported | Archive, resource inspection, privacy/configuration, TestFlight/App Store records | Compare claim wording with the strongest observed artifact/run | Packaged configuration matches the tested scope | Review approval, production delivery, or all devices |

## Fixture matrix

Maintain deterministic snapshots for:

- empty/idle state;
- preparing/loading state;
- confirmed active progress;
- completed state;
- paused state;
- static fallback;
- reduced-motion mode;
- reduced-transparency mode;
- unavailable shader;
- unsupported hardware;
- stale source revision;
- partial or missing source;
- cancellation and replacement;
- resource pressure or thermal downgrade;
- user-edited visual preference;
- valid AI suggestion;
- unknown palette role;
- out-of-range density or emphasis;
- arbitrary shader/asset request;
- model refusal or unavailable state;
- compact and regular layout;
- Dynamic Type and RTL.

Inject dates and phase values instead of depending on wall-clock time in tests. Snapshot tests should compare semantic state separately from pixels so a visual polish change does not hide a broken recovery state.

## Accessibility task matrix

| Setting/input | Task | Evidence |
| --- | --- | --- |
| VoiceOver | Discover the state, read progress/freshness, pause/resume, and recover from unavailable rendering | Reading order, labels, values, action announcements, and no dependency on drawn elements |
| Voice Control | Activate the same controls by visible semantic names | Commands recognize overlay controls; no pixel-only target |
| Switch Control | Move through state and actions, pause, and retry | Logical order and reachable recovery |
| Full Keyboard Access | Focus status and controls, activate, cancel, and return | Focus visibility and keyboard action |
| Dynamic Type | Read title/state/action copy at large sizes | No clipped critical status or control |
| Reduced transparency/increased contrast | Read controls and state above Canvas/glass | Visual layer cannot erase semantic hierarchy |
| Reduce Motion | Complete the task with static or gentle representation | Motion is optional and not the only state signal |
| RTL/localization | Read labels and interact with controls | Direction, strings, and layout remain correct |

An accessibility audit can find missing labels or traits, but only a task run shows whether the custom-rendered feature is usable.

## Physical-device performance packet

Record the exact:

    app/build:
    Xcode/SDK:
    deployment target:
    device model and OS build:
    display scale/size:
    scene fixture and point/particle count:
    renderer mode:
    timeline schedule and minimum interval:
    shader/Metal resources:
    accessibility and appearance settings:
    cold render:
    steady-state frame/cadence observation:
    CPU/GPU/memory:
    thermal/battery notes:
    touch/pointer observations:
    fallback result:
    unproven scope:

Use the maximum expected workload and a representative device family. A simulator or preview can validate state and layout; it cannot close a physical GPU, thermal, battery, haptic, or touch-comfort claim.

## Shader and resource packet

For a shader or custom asset route, retain:

- shader source/function name and uniform schema;
- target membership and resource bundle;
- availability and fallback branch;
- maximum sample offset or drawing region;
- reduced-motion/reduced-transparency behavior;
- expected device feature set;
- build configuration and optimization setting;
- rendered output and performance artifact;
- privacy review if the visual is derived from sensitive data.

Never put raw model output, network URLs, credentials, or private source text into shader uniforms or asset paths without a validated product boundary.

## Stop conditions

Do not call the custom-rendering route ready when:

- Canvas contains the only label, button, value, or action;
- the visual is animated continuously with no pause/reduced-motion path;
- a schedule is being treated as a guaranteed frame clock;
- a shader has no compiled fallback or resource membership proof;
- the scene snapshot can contain unbounded source/model data;
- high-contrast motion sits behind text or functional glass controls;
- performance is claimed without the maximum fixture on representative hardware;
- the AI can select arbitrary shader code, assets, or accessibility-breaking parameters;
- system-surface behavior is inferred from an in-app Canvas;
- the release claim exceeds the signed/artifact/device evidence.

## Sources

- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [TimelineView](https://developer.apple.com/documentation/swiftui/timelineview)
- [TimelineSchedule](https://developer.apple.com/documentation/swiftui/timelineschedule)
- [AnimationTimelineSchedule](https://developer.apple.com/documentation/swiftui/animationtimelineschedule)
- [Drawing and graphics](https://developer.apple.com/documentation/swiftui/drawing-and-graphics)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [ShaderLibrary](https://developer.apple.com/documentation/swiftui/shaderlibrary)
- [drawingGroup(opaque:colorMode:)](https://developer.apple.com/documentation/swiftui/view/drawinggroup%28opaque%3Acolormode%3A%29)
- [Human Interface Guidelines motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Monitoring app performance with MetricKit](https://developer.apple.com/documentation/metrickit/monitoring-app-performance-with-metrickit)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)

# Canvas, TimelineView, and custom rendering

SwiftUI already provides native views, Shapes, layout, materials, transitions, symbols, and controls for most app interfaces. Use Canvas and GraphicsContext when a contained visual surface genuinely benefits from immediate-mode drawing: an ambient background, waveform, particle field, custom gauge, data texture, progress visualization, or other rich 2D surface.

Use this route to add visual character without turning a SwiftUI screen into an inaccessible bitmap or an unmeasured animation loop. The goal is Apple-native composition: semantic controls and text remain SwiftUI views, while custom rendering is a bounded visual layer with explicit fallback, cadence, accessibility, and device evidence.

This page is a source-linked route sketch, not a compiled implementation. Confirm signatures and availability in the selected iOS 26 SDK and target.

## Choose the smallest rendering tool

| Need | Start with | Why |
| --- | --- | --- |
| Text, controls, forms, navigation, or interactive content | Standard SwiftUI views | They provide layout, state, focus, accessibility, input, and platform adaptation. |
| A reusable geometric shape with semantic surrounding content | Shape, InsettableShape, Path, or drawing primitives | Keep geometry declarative and composable in the SwiftUI view tree. |
| Rich 2D drawing with many dynamic primitives | Canvas and GraphicsContext | Immediate-mode drawing can reduce the cost of a complex visual surface, but individual elements need a separate semantic/input route. |
| Redraw on a controlled time schedule | TimelineView with a TimelineSchedule | The schedule supplies dates; the view decides what detail to draw and can inspect cadence. |
| A pixel or geometry shader effect | SwiftUI shader modifiers and ShaderLibrary | Use a narrowly scoped Metal shader on a graphical view, with availability, resource, fallback, and performance checks. |
| A full custom renderer or cross-frame GPU pipeline | Metal or another specialized framework route | Accept the larger target, resource, performance, accessibility, and lifecycle contract. |

Do not use Canvas just because it can draw a button, label, or list faster to prototype. If a person needs to find, focus, activate, edit, or read an element, keep that element in semantic SwiftUI/UIKit content and layer the custom visual behind or around it.

## Canvas contract

Canvas provides a renderer closure with a GraphicsContext and size. GraphicsContext can fill and stroke paths, draw images and text, draw registered SwiftUI views as symbols, and apply operations such as masks, filters, transforms, and blend modes.

The important boundary is equally explicit: Canvas does not provide interactivity or accessibility for individual elements, including views passed as symbols. Apple recommends it for complex drawings that do not primarily involve text or require interactive elements.

Use this ownership split:

| Layer | Owns | Must not own |
| --- | --- | --- |
| Semantic SwiftUI view tree | Text, controls, focus, accessibility, gestures, actions, state labels, and alternate content | Per-frame drawing work that is not needed for the task. |
| Canvas renderer | Geometry, particles, paths, symbols, masks, color, and visual interpolation | Canonical data, permission decisions, irreversible actions, or the only readable meaning of a state. |
| Feature state/model | Source values, animation phase, loading/error/paused state, user preferences, reduced-motion policy | Direct mutation of GraphicsContext from a background task. |
| Timeline schedule | Proposed redraw dates and cadence mode | A guarantee of a particular frame rate, battery cost, or physical smoothness. |
| Shader/Metal asset | Bounded GPU transform or effect | Arbitrary model-generated code, hidden network work, or unbounded resource allocation. |

The renderer should be a pure projection of a small immutable scene snapshot. Keep it easy to replace with a static fixture, a reduced-detail renderer, or a semantic fallback.

## Scene snapshot

Use an app-owned snapshot rather than passing a live service, model session, or persistence context into the drawing closure:

    struct VisualPoint: Identifiable, Sendable {
        let id: String
        let position: CGPoint
        let colorRole: VisualColorRole
        let intensity: Double
        let sourceRevision: String?
    }

    struct VisualSnapshot: Sendable {
        let points: [VisualPoint]
        let phase: Double
        let isLive: Bool
        let detailLevel: DetailLevel
        let semanticSummary: String
        let sourceRevision: String?
    }

    enum DetailLevel: Sendable {
        case full
        case reduced
        case staticFallback
    }

The types are illustrative. Validate positions, intensity, counts, colors, and source revisions before rendering. Keep dangerous or private source content out of logs and avoid letting untrusted text become a shader name, file path, or arbitrary renderer parameter.

## TimelineView and cadence

TimelineView updates its content according to a TimelineSchedule. The content closure receives a Context with a date and cadence. Built-in schedules include animation, periodic, every-minute, and explicit schedules; custom schedules can provide a sequence of dates.

Use the schedule that matches the user outcome:

| Outcome | Schedule strategy | Guardrail |
| --- | --- | --- |
| A calm ambient motion layer | Animation schedule with a bounded minimum interval | Pause or reduce detail for reduced motion, hidden/nonessential state, and resource pressure. |
| A clock or time display | Periodic schedule at the precision the UI actually communicates | Do not redraw at a finer cadence than the visible value needs. |
| A progress or playback visualization | Explicit or source-driven phase updates | Keep source time, playback state, and render time distinct. |
| A deterministic test | Explicit schedule or injected date | Do not make tests depend on wall-clock timing. |
| A live sensor visualization | Bounded source cadence plus a drawing schedule | Add backpressure and stale-state handling; TimelineView does not fix an overloaded source. |

Use Context.cadence to hide unnecessary detail or choose a simpler representation. A schedule is not a promise that the system will deliver every requested update at a fixed frame rate. Record the observed cadence and rendering workload when performance matters.

## Motion policy

Custom motion must communicate something or create a deliberate atmosphere without becoming the only status channel. Provide a static or reduced-motion representation that preserves meaning.

At minimum:

- read accessibilityReduceMotion and choose a static, slower, or lower-amplitude scene;
- avoid perpetual motion for a completed or inactive state;
- pause or reduce work when motion is not helping the task;
- do not make a person wait for a custom animation to finish before acting;
- pair important visual state with text, semantic state, haptics, or audio where appropriate;
- avoid fast flashing, high-frequency peripheral motion, and repeated depth/blur transitions;
- let a gesture or explicit control replace automatic motion when that makes sense.

The HIG motion guidance says motion should be purposeful, optional, brief, precise, and cancellable. Treat these as product requirements, not merely visual preferences.

## Liquid Glass composition

Canvas should usually be a content or atmosphere layer. Liquid Glass should usually support functional controls, navigation, or a bounded action cluster. Keep the relationship explicit:

    content/data/Canvas
      -> semantic text and state explanation
      -> standard controls
      -> optional functional Liquid Glass group
      -> navigation/system surface

Good uses:

- an animated visualizer behind a readable control cluster;
- a custom progress field with native buttons above it;
- a soft data texture inside a bounded card with visible labels;
- a custom focus/processing backdrop while the review controls remain semantic.

Bad uses:

- drawing the only button label inside Canvas;
- placing bright particles, blur, or shader distortion behind text until contrast changes;
- using glass translucency as the only indication of selection or completion;
- animating the entire background continuously while the person is reading;
- copying a proprietary Apple screen instead of using original content with native hierarchy.

Respect safe areas, Dynamic Type, increased contrast, reduced transparency, color scheme, and platform width. Put the Canvas in a clipped region with a clear layout contract rather than letting it dictate the whole screen.

## Accessibility route

Canvas is not an accessibility tree for individual drawn elements. Choose one of these routes:

1. Decorative layer: mark the Canvas hidden from accessibility and expose the same screen state through nearby semantic text and controls.
2. Visual summary: expose a concise label/value/summary for a chart, progress field, or status visualization, plus an exact-value list or table where needed.
3. Interactive overlay: keep the drawn appearance in Canvas but place semantic SwiftUI controls or accessibility actions over the meaningful regions.
4. Custom chart semantics: use a chart descriptor route when the visual is a data chart and the accessibility framework needs titles, axes, series, and values.
5. UIKit/accessibility bridge: use a representable or custom accessibility element only when the simpler SwiftUI route cannot express the interaction.

Never assume that passing a SwiftUI view as a Canvas symbol preserves that view’s individual accessibility or hit testing. Prove the semantic route independently of the drawing.

Test VoiceOver reading order, Voice Control labels, Switch Control navigation, keyboard/full keyboard focus, Dynamic Type, RTL, increased contrast, reduced transparency, Reduce Motion, Assistive Access where relevant, and localization. If the visual surface communicates a live value, expose its freshness and unavailable state in text.

## Shader boundary

SwiftUI provides colorEffect, distortionEffect, and layerEffect modifiers for applying a Shader to graphical views. ShaderLibrary can refer to stitchable Metal shader functions in the default shader library. These are powerful rendering tools, not a reason to put arbitrary behavior in a visual effect.

Keep a shader route bounded:

- define the shader function and uniform types in the target project;
- keep the maximum sample offset and visual region explicit;
- gate the effect by availability and a product setting;
- disable or simplify it for reduced motion, unsupported rendering, errors, and performance pressure;
- avoid applying it to text or controls when it harms legibility or input;
- provide a non-shader fallback with the same semantic meaning;
- record shader source, asset/resource membership, device feature assumptions, and build configuration;
- measure on representative hardware.

If the effect needs a full render graph, persistent GPU resources, compute kernels, or complex synchronization, route to Metal and use the graphics proof matrix rather than hiding that responsibility in a SwiftUI modifier.

## AI-assisted visual parameters

An on-device model can propose a visual treatment, but the proposal must not control arbitrary code or override accessibility. Keep visual generation deterministic at the renderer boundary:

    approved domain state
      -> bounded VisualSuggestion
      -> validator and accessibility policy
      -> VisualSnapshot
      -> Canvas/TimelineView or shader

Example bounded fields:

- a named palette role from an app-owned allowlist;
- motion profile: static, gentle, or interactive;
- density within a fixed range;
- contrast mode;
- emphasis level;
- a short semantic label or source revision.

Reject a proposal that contains unbounded shader source, unknown assets, unsupported colors, private source text, excessive motion, or an action command. The model can suggest; the product policy and renderer decide. Keep the visual state separate from Foundation Models transcripts and domain truth.

## Lifecycle and fallback state

Model visual rendering as a state machine:

    idle
      -> preparing
      -> ready
      -> live
      -> paused
      -> reduced
      -> staticFallback
      -> unavailable

Transitions include:

- source loading or permission failure;
- scene replaced by a new task;
- reduced motion or reduced transparency setting changed;
- app backgrounded or system resource pressure;
- shader/asset unavailable;
- device performance or thermal threshold exceeded;
- user pauses or disables animation;
- model suggestion rejected or expired.

Preserve the semantic status when the renderer is paused or unavailable. A static fallback should not look like a successful live state if freshness or progress has stopped.

## Target and availability register

| Gate | Question | Proof |
| --- | --- | --- |
| SwiftUI API | Do Canvas, GraphicsContext, TimelineView, schedule, and modifier signatures compile for the selected deployment target? | Minimal compile in the named target and scheme. |
| Rendering asset | Are shader functions, symbols, fonts, images, and resources in the intended target? | Target membership/build-resource inspection and a signed build check. |
| Accessibility | Does the screen have a semantic overlay or fallback that does not depend on Canvas elements? | Task-based accessibility run with actual settings. |
| Motion | Does the route read Reduce Motion and avoid making animation the only state signal? | Fixture and UI tests plus physical setting change. |
| Data/source | Does the scene consume normalized, privacy-safe, cancellable state? | Unit/fixture tests for stale, denied, partial, cancelled, and replacement states. |
| GPU/shader | Is the device/OS feature and fallback route known? | Compile/availability checks and representative physical-device run. |
| Performance | Is the redraw/drawing/shader cost bounded? | Instrumented workload with frame time, memory, thermal, and battery observations. |
| Liquid Glass | Does the visual layer preserve functional glass grouping and legibility? | Accessibility/contrast/reduced-transparency and physical touch review. |

## Proof ladder

1. Source check: refresh Canvas, GraphicsContext, TimelineView, shader, animation, accessibility, and HIG motion pages.
2. Compile check: build the smallest renderer with real target resources and the selected deployment target.
3. Deterministic fixture check: inject dates, scene snapshots, reduced-motion settings, and unavailable states.
4. UI check: test layout, focus, gestures, cancellation, state labels, Dynamic Type, RTL, and appearance.
5. Accessibility check: complete the task without interacting with individual Canvas marks.
6. Physical-device check: measure cadence, frame time, memory, thermal/battery behavior, touch comfort, and contrast.
7. Release/system check: inspect resources, privacy configuration, signing, and any widget/system projection separately.

## Common failure patterns

- using Canvas for semantic controls or text-heavy screens;
- assuming symbols inside Canvas retain individual hit testing or accessibility;
- driving a perpetual animation with no pause or reduced-motion route;
- allocating paths, images, or random values in every redraw without a budget;
- using drawingGroup or a shader without measuring memory and visual output;
- letting model output select arbitrary shaders, assets, or high-motion values;
- placing a high-contrast animation behind Liquid Glass controls;
- treating TimelineView cadence as a guaranteed display refresh rate;
- claiming custom graphics are accessible because the surrounding view has one label;
- calling a simulator render proof of physical GPU, thermal, battery, or touch behavior.

## Sources

- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [TimelineView](https://developer.apple.com/documentation/swiftui/timelineview)
- [TimelineView.Context](https://developer.apple.com/documentation/swiftui/timelineview/context)
- [TimelineSchedule](https://developer.apple.com/documentation/swiftui/timelineschedule)
- [AnimationTimelineSchedule](https://developer.apple.com/documentation/swiftui/animationtimelineschedule)
- [PeriodicTimelineSchedule](https://developer.apple.com/documentation/swiftui/periodictimelineschedule)
- [Drawing and graphics](https://developer.apple.com/documentation/swiftui/drawing-and-graphics)
- [Add rich graphics to your SwiftUI app](https://developer.apple.com/documentation/swiftui/add-rich-graphics-to-your-swiftui-app)
- [drawingGroup(opaque:colorMode:)](https://developer.apple.com/documentation/swiftui/view/drawinggroup%28opaque%3Acolormode%3A%29)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [ShaderLibrary](https://developer.apple.com/documentation/swiftui/shaderlibrary)
- [colorEffect(_:isEnabled:)](https://developer.apple.com/documentation/swiftui/view/coloreffect%28_%3Aisenabled%3A%29)
- [distortionEffect(_:maxSampleOffset:isEnabled:)](https://developer.apple.com/documentation/swiftui/view/distortioneffect%28_%3Amaxsampleoffset%3Aisenabled%3A%29)
- [layerEffect(_:maxSampleOffset:isEnabled:)](https://developer.apple.com/documentation/swiftui/view/layereffect%28_%3Amaxsampleoffset%3Aisenabled%3A%29)
- [Human Interface Guidelines motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Metal](https://developer.apple.com/documentation/metal)

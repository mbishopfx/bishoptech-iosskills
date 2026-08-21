# Canvas, TimelineView, and custom-rendering recipes

These are compile-oriented SwiftUI route sketches for bounded custom visual surfaces. They are not compiled in this documentation-only workspace. Confirm signatures, deployment availability, resource membership, shader support, and device behavior in the real target.

## Recipe 1: Draw a bounded visual layer

    import SwiftUI

    struct DotField: View {
        let points: [CGPoint]

        var body: some View {
            Canvas(
                opaque: false,
                colorMode: .nonLinear,
                rendersAsynchronously: true
            ) { context, size in
                for point in points {
                    let rect = CGRect(
                        x: point.x * size.width - 4,
                        y: point.y * size.height - 4,
                        width: 8,
                        height: 8
                    )
                    context.fill(
                        Path(ellipseIn: rect),
                        with: .color(.accentColor)
                    )
                }
            }
            .frame(minHeight: 160)
            .clipped()
        }
    }

The renderer is illustrative. Validate points before drawing, keep the frame bounded, and test whether asynchronous rendering improves the actual workload. Canvas does not make the dots interactive or individually accessible.

## Recipe 2: Add semantic content above the Canvas

    struct StatusVisual: View {
        let label: String
        let value: String
        let isLive: Bool

        var body: some View {
            ZStack {
                DotField(points: samplePoints)
                    .accessibilityHidden(true)

                VStack(spacing: 8) {
                    Text(label)
                    Text(value)
                        .font(.title2.monospacedDigit())
                    Text(isLive ? "Live" : "Paused")
                        .accessibilityAddTraits(.updatesFrequently)
                }
            }
            .accessibilityElement(children: .contain)
        }
    }

Keep the accessible state and actions in normal SwiftUI content. If the visual represents a chart, progress, or exact measurement, add the appropriate summary/table/chart descriptor rather than relying on one generic label.

## Recipe 3: Drive a visual with a controlled timeline

    struct AnimatedPhase: View {
        @Environment(\.accessibilityReduceMotion) private var reduceMotion
        let basePhase: Double

        var body: some View {
            if reduceMotion {
                PhaseVisual(phase: basePhase, detail: .staticFallback)
            } else {
                TimelineView(
                    .animation(
                        minimumInterval: 1.0 / 30.0,
                        paused: false
                    )
                ) { context in
                    let phase = basePhase + context.date.timeIntervalSinceReferenceDate
                    PhaseVisual(phase: phase, detail: detail(for: context))
                }
            }
        }

        func detail(
            for context: TimelineViewDefaultContext
        ) -> DetailLevel {
            // Use context.cadence to reduce unnecessary detail.
            .full
        }
    }

The schedule and context types are SDK-sensitive route sketches. Use an injected date or explicit schedule in tests. Do not assume that a requested animation interval is the display’s delivered frame rate.

## Recipe 4: Prefer periodic updates when the UI is not frame-based

    struct ClockVisual: View {
        var body: some View {
            TimelineView(
                .periodic(
                    from: Date(),
                    by: 1
                )
            ) { context in
                Text(context.date, style: .time)
                    .monospacedDigit()
            }
        }
    }

Choose the update precision from what the person can see and act on. A seconds-level clock does not need a high-frequency animation schedule.

## Recipe 5: Build a reduced-detail policy

    struct RenderPolicy: Sendable {
        let detail: DetailLevel
        let animationEnabled: Bool
        let maximumPoints: Int
    }

    func policy(
        reduceMotion: Bool,
        isPaused: Bool,
        isResourceConstrained: Bool
    ) -> RenderPolicy {
        if reduceMotion || isPaused {
            return RenderPolicy(
                detail: .staticFallback,
                animationEnabled: false,
                maximumPoints: 100
            )
        }
        if isResourceConstrained {
            return RenderPolicy(
                detail: .reduced,
                animationEnabled: true,
                maximumPoints: 500
            )
        }
        return RenderPolicy(
            detail: .full,
            animationEnabled: true,
            maximumPoints: 2_000
        )
    }

The thresholds are product-specific fixtures, not universal performance limits. Keep them measurable and make the policy visible in the feature state.

## Recipe 6: Keep a shader effect optional

    struct ShaderSurface: View {
        let phase: Double
        let isEnabled: Bool

        var body: some View {
            RoundedRectangle(cornerRadius: 28)
                .fill(.blue.gradient)
                .colorEffect(
                    ShaderLibrary.myColorEffect(
                        .float(phase)
                    ),
                    isEnabled: isEnabled
                )
        }
    }

The shader function name, generated library, uniform signature, and availability must be confirmed in the target. Provide a standard fill or Canvas fallback. Do not apply the effect to critical text or controls without contrast and reduced-motion proof.

## Recipe 7: Use drawingGroup only after measurement

    struct ComposedVisual: View {
        var body: some View {
            ZStack {
                // Shapes and image-based drawing primitives.
                RoundedRectangle(cornerRadius: 24)
                    .fill(.blue)
                Circle()
                    .fill(.white.opacity(0.3))
            }
            .drawingGroup(
                opaque: false,
                colorMode: .nonLinear
            )
        }
    }

drawingGroup composites supported SwiftUI drawing primitives into an offscreen image. It is not a universal optimization and has documented limitations for views whose contents are composed by Core Animation or other frameworks. Compare memory, frame time, color output, and fallback behavior before keeping it.

## Recipe 8: Constrain AI to a visual suggestion

    struct VisualSuggestion: Sendable {
        let paletteRole: PaletteRole
        let motion: MotionProfile
        let density: Double
        let emphasis: Double
    }

    enum PaletteRole: String, Sendable {
        case calm
        case active
        case warning
    }

    enum MotionProfile: Sendable {
        case static
        case gentle
        case interactive
    }

    func validated(
        _ suggestion: VisualSuggestion,
        reduceMotion: Bool
    ) -> VisualSuggestion {
        let motion = reduceMotion ? .static : suggestion.motion
        return VisualSuggestion(
            paletteRole: suggestion.paletteRole,
            motion: motion,
            density: min(max(suggestion.density, 0), 1),
            emphasis: min(max(suggestion.emphasis, 0), 1)
        )
    }

Use typed, app-owned fields and allowlists. Reject unknown assets, shader names, source text, executable instructions, and high-motion values. The renderer should accept only the validated result.

## Recipe 9: Inject time and scenes for previews/tests

    struct SceneFixture: Sendable {
        let date: Date
        let snapshot: VisualSnapshot
        let reduceMotion: Bool
        let expectedLabel: String
    }

    let fixture = SceneFixture(
        date: Date(timeIntervalSinceReferenceDate: 123),
        snapshot: sampleSnapshot,
        reduceMotion: true,
        expectedLabel: "Paused"
    )

Use fixtures for idle, active, paused, reduced, unavailable, stale, and replaced scenes. Keep the semantic expected label in the fixture so a pixel-only snapshot cannot pass when the state copy is wrong.

## Recipe 10: Record device performance evidence

    struct RenderEvidence: Codable, Sendable {
        let appBuild: String
        let sdk: String
        let deviceFamily: String
        let sceneName: String
        let pointCount: Int
        let renderer: String
        let schedule: String
        let reduceMotion: Bool
        let result: String
        let notes: [String]
    }

Record frame/cadence observations, CPU/GPU/memory, thermal and battery notes, accessibility settings, and the fallback result separately from the code. Do not place credentials, private prompts, raw health data, or unnecessary media into the evidence record.

## Compile and proof checklist

- choose standard SwiftUI views, Shape, Canvas, shader modifiers, or Metal deliberately;
- compile the exact Canvas/GraphicsContext/TimelineView/schedule/modifier signatures in the intended target;
- verify target membership for shaders, symbols, images, fonts, and other resources;
- inject deterministic dates and VisualSnapshot fixtures;
- provide semantic text, controls, overlays, tables, or chart descriptors;
- implement Reduce Motion, reduced transparency, paused, unavailable, and resource-pressure states;
- measure the maximum expected workload on representative physical hardware;
- test Liquid Glass control grouping above the visual layer;
- if an AI suggestion is used, validate typed allowlisted parameters and keep the fallback deterministic;
- record what preview, simulator, compile, physical-device, system-surface, and release artifacts actually prove.

## Sources

- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [TimelineView](https://developer.apple.com/documentation/swiftui/timelineview)
- [TimelineView.Context](https://developer.apple.com/documentation/swiftui/timelineview/context)
- [TimelineSchedule](https://developer.apple.com/documentation/swiftui/timelineschedule)
- [AnimationTimelineSchedule](https://developer.apple.com/documentation/swiftui/animationtimelineschedule)
- [PeriodicTimelineSchedule](https://developer.apple.com/documentation/swiftui/periodictimelineschedule)
- [drawingGroup(opaque:colorMode:)](https://developer.apple.com/documentation/swiftui/view/drawinggroup%28opaque%3Acolormode%3A%29)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [ShaderLibrary](https://developer.apple.com/documentation/swiftui/shaderlibrary)
- [colorEffect(_:isEnabled:)](https://developer.apple.com/documentation/swiftui/view/coloreffect%28_%3Aisenabled%3A%29)
- [Human Interface Guidelines motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)

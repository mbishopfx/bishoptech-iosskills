# SwiftUI animation and motion recipes

## How to use these recipes

These are compile-oriented route sketches for a named SwiftUI app target. They
show the smallest useful seam for animation, transitions, geometry identity,
phases, keyframes, content transitions, sensory feedback, Liquid Glass
morphing, reduced motion, and on-device AI progress. They are not compiled in
this documentation-only workspace.

Before using one:

1. check the current Xcode/SDK declaration and overload;
2. check the target deployment and platform availability;
3. compile the smallest route in the app target;
4. add the target’s real state/service/permission boundaries;
5. run normal and reduced-motion UI tasks;
6. profile the maximum workload on a supported physical device;
7. record the release target/resource/entitlement evidence if the feature ships.

Related pages:

- [SwiftUI animation, motion, transitions, and feedback](../42-framework-deep-dives/78-swiftui-animation-motion-transitions-and-feedback.md)
- [Animation, motion, and Liquid Glass design](../21-design-deep-dives/106-animation-motion-and-liquid-glass-design.md)
- [SwiftUI animation and motion route](../50-capability-recipes/109-swiftui-animation-motion-route.md)
- [SwiftUI animation and motion proof matrix](../60-verification/103-swiftui-animation-motion-proof-matrix.md)

## Recipe 1: reduced-motion-aware state animation

Use one state mutation and keep the same final information when motion is
removed.

~~~swift
import SwiftUI

struct ExpandableStatus: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var isExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button(isExpanded ? "Hide details" : "Show details") {
                withAnimation(reduceMotion ? nil : .snappy) {
                    isExpanded.toggle()
                }
            }

            if isExpanded {
                Text("The same details remain available when motion is reduced.")
                    .transition(reduceMotion ? .identity : .opacity)
            }
        }
        .padding()
    }
}
~~~

If expansion triggers loading, persistence, or an AI request, keep that
operation in a separate state/task. The animation is not the operation.

## Recipe 2: scope animation to one value

Attach animation to the smallest view that should respond to a particular
Equatable value.

~~~swift
struct ReadinessLabel: View {
    let isReady: Bool

    var body: some View {
        Label(
            isReady ? "Ready" : "Preparing",
            systemImage: isReady ? "checkmark.circle.fill" : "hourglass"
        )
        .foregroundStyle(isReady ? .green : .secondary)
        .contentTransition(.symbolEffect(.replace))
        .animation(.smooth, value: isReady)
        .accessibilityValue(isReady ? "Ready" : "Preparing")
    }
}
~~~

The current SDK may expose different symbol/content-transition overloads.
Verify the exact declaration in the target’s generated interface.

## Recipe 3: transaction that disables inherited motion

Use a transaction modifier when a child must update immediately even though an
ancestor is animating.

~~~swift
struct ImmediateStatus: View {
    let status: String

    var body: some View {
        Text(status)
            .transaction { transaction in
                transaction.animation = nil
                transaction.disablesAnimations = true
            }
    }
}
~~~

This changes view update animation policy. It does not cancel a network/model
operation or make a state transition durable.

## Recipe 4: completion is presentation cleanup

Use animation completion for a visual cleanup boundary, never as the source of
domain truth.

~~~swift
struct TemporaryBanner: View {
    @State private var isVisible = false
    @State private var shouldRemove = false

    var body: some View {
        VStack {
            if isVisible {
                Text("Copied")
                    .padding()
                    .transition(.move(edge: .top).combined(with: .opacity))
            }

            Button("Show") {
                isVisible = true
                withAnimation(
                    .snappy,
                    completionCriteria: .removed
                ) {
                    shouldRemove = false
                } completion: {
                    shouldRemove = true
                }
            }
        }
        .onChange(of: shouldRemove) { _, remove in
            guard remove else { return }
            withAnimation(.snappy) {
                isVisible = false
            }
        }
    }
}
~~~

This is a presentation sketch. For a real banner, prefer a modelled
visibility/dismissal state and make interruption/cancellation explicit.

## Recipe 5: asymmetric insertion/removal

Use different directions only when the difference communicates the
relationship. Provide an identity route for reduced motion.

~~~swift
struct OptionalAction: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let isAvailable: Bool

    var body: some View {
        Group {
            if isAvailable {
                Button("Review") { }
                    .transition(
                        reduceMotion
                            ? .identity
                            : .asymmetric(
                                insertion: .move(edge: .trailing).combined(with: .opacity),
                                removal: .opacity
                            )
                    )
            }
        }
    }
}
~~~

Do not use a transition to conceal a permission denial or an error. Keep the
recovery action in the semantic hierarchy.

## Recipe 6: matched geometry for one visual object

Use a stable namespace and ID when a compact representation becomes a detail
representation.

~~~swift
struct ExpandableCard: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Namespace private var namespace
    @State private var isExpanded = false

    var body: some View {
        VStack {
            if isExpanded {
                VStack(alignment: .leading) {
                    Text("Review proposal")
                        .matchedGeometryEffect(id: "title", in: namespace)
                    Button("Close") {
                        withAnimation(reduceMotion ? nil : .smooth) {
                            isExpanded = false
                        }
                    }
                }
                .padding()
                .background(.regularMaterial, in: .rect(cornerRadius: 24))
                .matchedGeometryEffect(id: "surface", in: namespace)
            } else {
                Button("Open review") {
                    withAnimation(reduceMotion ? nil : .smooth) {
                        isExpanded = true
                    }
                }
                .padding()
                .background(.regularMaterial, in: .rect(cornerRadius: 18))
                .matchedGeometryEffect(id: "surface", in: namespace)
            }
        }
    }
}
~~~

The source/destination labels should be semantically equivalent. Ensure the
matched group has one active source and test rapid toggles and focus.

## Recipe 7: triggered PhaseAnimator

Use discrete phases for a short response, not for real operation progress.

~~~swift
private enum ResponsePhase: CaseIterable {
    case initial
    case emphasized
    case settled
}

struct BoundedResponse: View {
    @State private var trigger = 0

    var body: some View {
        Image(systemName: "checkmark.circle")
            .phaseAnimator(ResponsePhase.allCases, trigger: trigger) { content, phase in
                content
                    .scaleEffect(phase == .emphasized ? 1.16 : 1)
                    .opacity(phase == .initial ? 0.7 : 1)
            } animation: { phase in
                switch phase {
                case .initial: .smooth
                case .emphasized: .spring(duration: 0.25, bounce: 0.5)
                case .settled: .smooth
                }
            }
            .onTapGesture {
                trigger += 1
            }
    }
}
~~~

If the response must stop when a domain state changes, include that state in
the view and make the phase route conditional. A repeating phase should have
an explicit stop condition.

## Recipe 8: keyframe tracks for a bounded visual

Use a small Animatable value and keep the content closure cheap.

~~~swift
private struct BadgeAnimationValues {
    var scale = 1.0
    var rotation = Angle.zero
    var offset = 0.0
}

struct KeyframedBadge: View {
    @State private var trigger = 0

    var body: some View {
        Image(systemName: "sparkles")
            .keyframeAnimator(
                initialValue: BadgeAnimationValues(),
                trigger: trigger
            ) { content, value in
                content
                    .scaleEffect(value.scale)
                    .rotationEffect(value.rotation)
                    .offset(y: value.offset)
            } keyframes: { _ in
                KeyframeTrack(\.scale) {
                    CubicKeyframe(1.18, duration: 0.12)
                    SpringKeyframe(1.0, duration: 0.28)
                }
                KeyframeTrack(\.rotation) {
                    LinearKeyframe(.degrees(-8), duration: 0.12)
                    SpringKeyframe(.zero, duration: 0.28)
                }
                KeyframeTrack(\.offset) {
                    LinearKeyframe(-4, duration: 0.12)
                    SpringKeyframe(0, duration: 0.28)
                }
            }
            .onTapGesture {
                trigger += 1
            }
    }
}
~~~

The exact KeyframeTrack and keyframe signatures are SDK-sensitive. Confirm
them in Xcode. Never decode data, call a model, write persistence, or perform
blocking work in the content closure.

## Recipe 9: content transition for a numeric value

Use a content transition for a value that changes inside the same view.

~~~swift
struct ScoreLabel: View {
    let score: Int

    var body: some View {
        Text(score, format: .number)
            .contentTransition(.numericText(value: Double(score)))
            .animation(.smooth, value: score)
            .accessibilityLabel("Score")
            .accessibilityValue(Text(score, format: .number))
    }
}
~~~

If numeric text is unavailable for the selected target, use an identity or
opacity route. The exact number and accessible value must remain correct.

## Recipe 10: semantic sensory feedback after a result

Drive sensory feedback from a result state, not from the tap alone.

~~~swift
struct SaveButton: View {
    enum Result: Equatable {
        case idle
        case saving
        case saved
        case failed
    }

    @State private var result: Result = .idle

    var body: some View {
        Button(result == .saving ? "Saving" : "Save") {
            guard result != .saving else { return }
            Task {
                result = .saving
                let didSave = await saveDomainRecord()
                result = didSave ? .saved : .failed
            }
        }
        .sensoryFeedback(trigger: result) { _, newValue in
            switch newValue {
            case .saved: .success
            case .failed: .error
            case .idle, .saving: nil
            }
        }
        .accessibilityValue(
            result == .saved ? "Saved" :
            result == .failed ? "Save failed" :
            result == .saving ? "Saving" : "Ready"
        )
    }

    private func saveDomainRecord() async -> Bool {
        true
    }
}
~~~

Replace the placeholder with the actual domain operation. Add a visible
success/error state and test on a supported physical device; haptics are not
the only result channel.

## Recipe 11: Liquid Glass morphing group

Use stable glass IDs and a shared container for related shapes.

~~~swift
struct GlassActionGroup: View {
    @State private var isExpanded = false
    @Namespace private var namespace

    var body: some View {
        GlassEffectContainer(spacing: 40) {
            HStack(spacing: 40) {
                Image(systemName: "scribble.variable")
                    .frame(width: 80, height: 80)
                    .glassEffect()
                    .glassEffectID("primary", in: namespace)

                if isExpanded {
                    Image(systemName: "eraser.fill")
                        .frame(width: 80, height: 80)
                        .glassEffect()
                        .glassEffectID("secondary", in: namespace)
                        .glassEffectTransition(.matchedGeometry)
                }
            }
        }
        .overlay {
            Button(isExpanded ? "Collapse" : "Expand") {
                withAnimation(.smooth) {
                    isExpanded.toggle()
                }
            }
            .buttonStyle(.glass)
        }
    }
}
~~~

Use a real semantic button hierarchy rather than placing an unrelated button
inside a decorative overlay. Profile effect count and spacing. Consider
materialize or identity for distant/reduced-motion routes.

## Recipe 12: state-driven AI progress surface

Keep operation truth and visual phases separate.

~~~swift
enum ReviewState: Equatable {
    case unavailable(String)
    case idle
    case generating
    case proposal(String)
    case applying
    case saved
    case failed(String)
}

struct ReviewSurface: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let state: ReviewState
    let cancel: () -> Void
    let accept: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            switch state {
            case .unavailable(let reason):
                Label(reason, systemImage: "exclamationmark.triangle")
            case .idle:
                Button("Generate") { }
            case .generating:
                ProgressView("Generating")
                Button("Cancel", action: cancel)
                    .buttonStyle(.bordered)
            case .proposal(let text):
                Text(text)
                    .contentTransition(reduceMotion ? .identity : .opacity)
                Button("Accept", action: accept)
            case .applying:
                ProgressView("Applying")
            case .saved:
                Label("Saved", systemImage: "checkmark.circle")
            case .failed(let message):
                Label(message, systemImage: "xmark.circle")
            }
        }
        .animation(reduceMotion ? nil : .smooth, value: state)
    }
}
~~~

The example deliberately leaves the operation outside the view. The real
implementation should connect the buttons to a model/service with
cancellation, typed validation, authorization, and durable commit behavior.
Do not use a fake percentage or an animation callback as model progress.

## Recipe 13: no-motion fallback helper

Centralize the policy so features do not each invent a different reduced-motion
interpretation.

~~~swift
struct MotionPolicy {
    let reduceMotion: Bool

    var standardAnimation: Animation? {
        reduceMotion ? nil : .smooth
    }

    var insertion: AnyTransition {
        reduceMotion ? .identity : .opacity
    }

    var glassTransition: GlassEffectTransition {
        reduceMotion ? .identity : .matchedGeometry
    }
}

struct MotionAwareFeature: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        let policy = MotionPolicy(reduceMotion: reduceMotion)
        Text("Feature")
            .transition(policy.insertion)
            .glassEffectTransition(policy.glassTransition)
    }
}
~~~

Treat this as a route sketch. Check whether the selected SDK permits each
transition modifier on the particular view and apply glass only where the
target design needs it.

## Recipe 14: performance-proof fixture

Use a fixed, maximum-workload fixture and measure on a real device. The
following is a test-planning shape rather than a claim that the metric alone
closes performance:

~~~swift
struct MotionFixture {
    let itemCount: Int
    let longText: String
    let simultaneousGlassEffects: Int
    let modelOutputLength: Int
}

let maximumFixture = MotionFixture(
    itemCount: 200,
    longText: String(repeating: "Long localized content ", count: 40),
    simultaneousGlassEffects: 8,
    modelOutputLength: 4000
)
~~~

Pair the fixture with:

- normal and reduced-motion UI tasks;
- Animation Hitches/Instruments recording;
- memory/CPU/GPU/thermal observation;
- cancellation during generation;
- Dynamic Type and reduced-transparency runs;
- an older supported physical device;
- build, SDK, OS, device, and fixture notes.

## Sources

- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [Animation](https://developer.apple.com/documentation/SwiftUI/Animation)
- [withAnimation(_:completionCriteria:_:completion:)](https://developer.apple.com/documentation/SwiftUI/withAnimation%28_%3AcompletionCriteria%3A_%3Acompletion%3A%29)
- [Transaction](https://developer.apple.com/documentation/swiftui/transaction)
- [Transition](https://developer.apple.com/documentation/swiftui/transition)
- [ContentTransition](https://developer.apple.com/documentation/swiftui/contenttransition)
- [matchedGeometryEffect(id:in:properties:anchor:isSource:)](https://developer.apple.com/documentation/swiftui/view/matchedgeometryeffect%28id%3Ain%3Aproperties%3Aanchor%3Aissource%3A%29)
- [PhaseAnimator](https://developer.apple.com/documentation/swiftui/phaseanimator)
- [KeyframeAnimator](https://developer.apple.com/documentation/swiftui/keyframeanimator)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Understanding hitches in your app](https://developer.apple.com/documentation/xcode/understanding-hitches-in-your-app)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)

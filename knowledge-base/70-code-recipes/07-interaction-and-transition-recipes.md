# Interaction and Transition Recipes

## Scope and compile boundary

These snippets are compile-oriented route sketches for [Interaction and Transition Cookbook](../21-design-deep-dives/07-interaction-and-transition-cookbook.md), [functional Liquid Glass interactions](../20-liquid-glass/05-functional-glass-interactions.md), and [navigation, toolbar, and tab hierarchy](../21-design-deep-dives/09-navigation-toolbar-and-tab-hierarchy.md). They show the smallest useful SwiftUI seam for animation, transition, scrolling, focus, sensory feedback, safe-area controls, gestures, and Liquid Glass identity. They are not compiled in this documentation-only workspace.

Before using a recipe, check the selected Xcode/SDK signature, deployment target, platform availability, and any required capability. Compile the smallest route in the target app, then test the actual interaction on supported devices. A preview or code listing is not proof of haptics, performance, accessibility completion, or release readiness.

## Recipe 1: reduced-motion-aware state animation

Scope the animation to the state change. The reduced-motion branch preserves the same result without making the person wait for movement.

```swift
struct ExpandableSection: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var isExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button {
                withAnimation(reduceMotion ? nil : .snappy) {
                    isExpanded.toggle()
                }
            } label: {
                Label(
                    isExpanded ? "Hide details" : "Show details",
                    systemImage: isExpanded ? "chevron.up" : "chevron.down"
                )
            }

            if isExpanded {
                Text("Details remain readable when motion is reduced.")
                    .transition(reduceMotion ? .identity : .opacity)
            }
        }
    }
}
```

The state mutation is still synchronous and authoritative. If the expanded state triggers a load, persistence, or model request, represent that operation separately and handle cancellation and failure explicitly.

## Recipe 2: value-scoped animation

Attach animation to the view that should respond to a specific Equatable value. This prevents an unrelated sibling from animating because it happened to share the same state update.

```swift
struct StatusBadge: View {
    let isReady: Bool

    var body: some View {
        Label(
            isReady ? "Ready" : "Preparing",
            systemImage: isReady ? "checkmark.circle" : "hourglass"
        )
        .foregroundStyle(isReady ? .green : .secondary)
        .contentTransition(.symbolEffect(.replace))
        .animation(.smooth, value: isReady)
        .accessibilityValue(isReady ? "Ready" : "Preparing")
    }
}
```

`contentTransition` and symbol effects are optional visual aids. Keep the text/value update and accessibility announcement meaningful if the effect is unavailable or reduced. If the target SDK does not support the exact content transition, use an identity or opacity route and verify the current API in Xcode.

## Recipe 3: a scroll transition that stays readable

Apply a restrained change only outside the identity phase. The content and action remain present in every phase.

```swift
struct BrowseRow: View {
    let items: [String]

    var body: some View {
        ScrollView(.horizontal) {
            LazyHStack(spacing: 16) {
                ForEach(items, id: \.self) { item in
                    NavigationLink(item) {
                        Text(item)
                            .navigationTitle(item)
                    }
                    .buttonStyle(.plain)
                    .padding()
                    .background(.regularMaterial, in: .rect(cornerRadius: 18))
                    .scrollTransition(.animated) { content, phase in
                        content
                            .opacity(phase.isIdentity ? 1 : 0.82)
                            .scaleEffect(phase.isIdentity ? 1 : 0.96)
                    }
                }
            }
            .scrollTargetLayout()
            .padding(.horizontal)
        }
        .scrollTargetBehavior(.viewAligned)
    }
}
```

This is a route sketch: check the current overload and availability of `scrollTransition`, `scrollTargetLayout`, and `viewAligned` in the selected SDK. Test with large text, VoiceOver, keyboard/pointer scrolling, Reduce Motion, and a long list. Do not use the opacity change to indicate selection, loading, or authorization.

## Recipe 4: focus-driven form movement

Focus is a semantic editing route. Use it to move a person between fields after a clear submission or validation result.

```swift
struct FocusedForm: View {
    enum Field: Hashable {
        case name
        case note
    }

    @State private var name = ""
    @State private var note = ""
    @FocusState private var focusedField: Field?

    var body: some View {
        Form {
            TextField("Name", text: $name)
                .focused($focusedField, equals: .name)
                .submitLabel(.next)
                .onSubmit { focusedField = .note }

            TextField("Note", text: $note)
                .focused($focusedField, equals: .note)
                .submitLabel(.done)
                .onSubmit { focusedField = nil }

            Button("Validate") {
                focusedField = name.isEmpty ? .name : nil
            }
        }
    }
}
```

Add visible validation copy and an accessible error state in a real feature. Test hardware keyboard focus, VoiceOver editing, Voice Control, Switch Control, keyboard appearance, and state restoration. Do not shift focus on every model update.

## Recipe 5: sensory feedback tied to an outcome

Trigger feedback from a small outcome enum, not from every render or a speculative tap. The closure should return no feedback for states that do not need it.

```swift
struct SaveFeedbackExample: View {
    enum SaveEvent: Equatable {
        case idle
        case success
        case failure
    }

    @State private var saveEvent = SaveEvent.idle

    var body: some View {
        Button("Save") {
            // Replace with the actual async/domain operation.
            saveEvent = .success
        }
        .sensoryFeedback(trigger: saveEvent) {
            switch saveEvent {
            case .success:
                .success
            case .failure:
                .error
            case .idle:
                nil
            }
        }
        .accessibilityValue(
            saveEvent == .success ? "Saved" : "Not saved"
        )
    }
}
```

In a real feature, set `.success` only after the durable operation succeeds and expose localized status or error copy. Test unsupported devices, silent mode, user preferences, rapid taps, and VoiceOver. For a custom pattern that genuinely needs Core Haptics, document the engine lifecycle and physical-device requirement separately.

## Recipe 6: safe-area action bar that makes room for content

Use `safeAreaInset` when content should be inset by a persistent edge control. Prefer a native toolbar or system bar if it expresses the relationship.

```swift
struct SafeAreaCommitBar: View {
    let canCommit: Bool
    let commit: () -> Void

    var body: some View {
        ScrollView {
            Text("Long content stays scrollable above the action bar.")
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
        }
        .safeAreaInset(edge: .bottom, spacing: 0) {
            Button("Apply", action: commit)
                .buttonStyle(.borderedProminent)
                .disabled(!canCommit)
                .frame(maxWidth: .infinity)
                .padding(.horizontal)
                .padding(.vertical, 10)
                .background(.bar)
        }
    }
}
```

If the bar is a custom functional Liquid Glass surface, add the glass effect to the smallest related control group and verify the safe-area behavior at the keyboard, sheet corners, landscape, and large text sizes. Do not place a manually positioned overlay over content and assume padding will remain correct on every device.

## Recipe 7: related Liquid Glass identity

Stable glass IDs let SwiftUI understand a visual relationship inside a `GlassEffectContainer`. They are not domain IDs and should not be regenerated with every render.

```swift
struct GlassModeSwitcher: View {
    @Namespace private var glassNamespace
    @State private var expanded = false

    var body: some View {
        GlassEffectContainer(spacing: 20) {
            HStack(spacing: 12) {
                Button("Main", systemImage: "circle") {
                    withAnimation(.smooth) { expanded = false }
                }
                .glassEffect()
                .glassEffectID("main", in: glassNamespace)

                if expanded {
                    Button("More", systemImage: "ellipsis") {
                        withAnimation(.smooth) { expanded = false }
                    }
                    .glassEffect()
                    .glassEffectID("more", in: glassNamespace)
                }
            }
        }
        .glassEffectTransition(.matchedGeometry)
    }
}
```

This is intentionally a small route sketch. Confirm modifier placement and whether the transition belongs on the effect-bearing view in the current SDK. For reduced motion, use a non-morphing identity/materialize route or remove the custom effect while preserving the same labels and actions. Test VoiceOver and rapid insertion/removal; visual identity must not change the accessibility order.

## Recipe 8: cancellable gesture work

Keep gesture state, task lifetime, and domain cancellation explicit. A gesture can begin a request whose result arrives after the view or selected item has changed.

```swift
struct RefreshableContent: View {
    @State private var refreshTask: Task<Void, Never>?
    @State private var isRefreshing = false

    let refresh: () async -> Void

    var body: some View {
        List {
            Text(isRefreshing ? "Refreshing" : "Up to date")
        }
        .refreshable {
            refreshTask?.cancel()
            isRefreshing = true
            defer { isRefreshing = false }
            await refresh()
        }
        .onDisappear {
            refreshTask?.cancel()
        }
    }
}
```

The `refreshTask` property is illustrative and needs a concrete task ownership strategy in a target project; `.refreshable` itself manages an async refresh scope. The important contract is that the service honors cancellation and that the screen does not show “up to date” before the refresh succeeds. For camera, audio, networking, or Foundation Models work, move cancellation into the service boundary and test lifecycle interruption.

## Recipe 9: preview the motion and accessibility branches

Use previews to inspect the same content with normal and reduced motion, different appearances, and large text. The environment values help exercise view branches; they do not simulate hardware haptics or all system behavior.

```swift
#Preview("Normal motion") {
    ExpandableSection()
}

#Preview("Reduced motion and large text") {
    ExpandableSection()
        .environment(\.accessibilityReduceMotion, true)
        .environment(\.dynamicTypeSize, .accessibility3)
}

#Preview("Dark mode and reduced transparency") {
    SafeAreaCommitBar(canCommit: true, commit: {})
        .preferredColorScheme(.dark)
        .environment(\.accessibilityReduceTransparency, true)
}
```

Add state fixtures for loading, empty, failure, permission denied, disabled, long localized copy, right-to-left layout, and keyboard-visible editing. Use UI tests and Accessibility Inspector for focus/semantics and physical devices for actual haptics, touch, safe areas, material rendering, and performance.

## Interaction review checklist

- The user-visible state change is named before the animation or haptic is selected.
- The state/result remains understandable with motion removed.
- `withAnimation` or `animation(_:value:)` is scoped to the intended view/state relationship.
- Insertion/removal uses stable identity and does not reset child state unexpectedly.
- Scroll transitions leave visible content readable and do not carry selection/error meaning by opacity alone.
- Focus moves only after a clear user action or validation decision and remains keyboard/assistive-technology reachable.
- Sensory feedback follows a real outcome and is paired with visible/accessibility feedback.
- Edge controls use safe-area APIs or system bars instead of manual overlays that cover content.
- Glass IDs are stable and semantic; containers group related functional elements only.
- Gesture-started work has a cancellation and lifecycle policy.
- Preview, UI-test, simulator, and physical-device evidence are recorded as separate levels.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [Animation](https://developer.apple.com/documentation/SwiftUI/Animation)
- [animation(_:value:)](https://developer.apple.com/documentation/swiftui/view/animation%28_%3Avalue%3A%29)
- [withAnimation](https://developer.apple.com/documentation/swiftui/withanimation%28_%3A_%3A%29)
- [Transition](https://developer.apple.com/documentation/swiftui/transition)
- [TransitionPhase](https://developer.apple.com/documentation/swiftui/transitionphase)
- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollTransitionPhase](https://developer.apple.com/documentation/swiftui/scrolltransitionphase)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [FocusState](https://developer.apple.com/documentation/SwiftUI/FocusState)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [sensoryFeedback(trigger:_:)](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback%28trigger%3A_%3A%29)
- [SafeAreaRegions](https://developer.apple.com/documentation/swiftui/safearearegions)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [safeAreaBar(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareabar%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [glassEffectID(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffectid%28_%3Ain%3A%29)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)

# Custom Layout and adaptive Liquid Glass recipes

## Compile boundary

These are route sketches for a named iOS 26 target, not compiled code in this documentation workspace. Confirm signatures, availability, target membership, and platform behavior in Xcode before copying them. Keep layout calculation separate from domain state, permissions, model calls, navigation mutations, and side effects.

## Recipe 1: equal-width action layout

Use a custom Layout when equal-width placement is a reusable relationship and a built-in stack is not enough:

    import SwiftUI

    struct EqualWidthRow: Layout {
        var spacing: CGFloat = 12

        func sizeThatFits(
            proposal: ProposedViewSize,
            subviews: Subviews,
            cache: inout ()
        ) -> CGSize {
            guard !subviews.isEmpty else { return .zero }
            let sizes = subviews.map { $0.sizeThatFits(.unspecified) }
            let itemWidth = sizes.map(\.width).max() ?? 0
            let itemHeight = sizes.map(\.height).max() ?? 0
            let width = itemWidth * CGFloat(subviews.count)
                + spacing * CGFloat(max(subviews.count - 1, 0))
            return CGSize(width: width, height: itemHeight)
        }

        func placeSubviews(
            in bounds: CGRect,
            proposal: ProposedViewSize,
            subviews: Subviews,
            cache: inout ()
        ) {
            guard !subviews.isEmpty else { return }
            let sizes = subviews.map { $0.sizeThatFits(.unspecified) }
            let itemWidth = sizes.map(\.width).max() ?? 0
            var x = bounds.minX + itemWidth / 2

            for subview in subviews {
                subview.place(
                    at: CGPoint(x: x, y: bounds.midY),
                    anchor: .center,
                    proposal: ProposedViewSize(
                        width: itemWidth,
                        height: bounds.height
                    )
                )
                x += itemWidth + spacing
            }
        }
    }

Use a ViewThatFits fallback when this ideal row cannot fit. Do not silently return a smaller container and place controls outside its bounds.

## Recipe 2: finite alternatives with ViewThatFits

Use explicit alternatives when the action meaning remains the same:

    ViewThatFits(in: .horizontal) {
        HStack(spacing: 12) {
            Button("Refresh", action: refresh)
            Button("Review", action: review)
            Menu("More") {
                Button("Export", action: export)
            }
        }

        HStack(spacing: 12) {
            Button("Refresh", action: refresh)
            Menu("Actions") {
                Button("Review", action: review)
                Button("Export", action: export)
            }
        }

        Button("Refresh", action: refresh)
    }

Order alternatives from most informative to most compact. Keep a visible route to secondary actions and an explanation for disabled/unavailable state.

## Recipe 3: switch layout type without losing subview identity

AnyLayout is useful when the same children should move between arrangements:

    struct ActionGroup: View {
        @Environment(\.dynamicTypeSize) private var dynamicTypeSize
        let refresh: () -> Void
        let review: () -> Void

        var body: some View {
            let layout = dynamicTypeSize >= .accessibility1
                ? AnyLayout(VStackLayout(spacing: 12))
                : AnyLayout(HStackLayout(spacing: 12))

            layout {
                Button("Refresh", action: refresh)
                    .layoutPriority(1)
                Button("Review", action: review)
            }
        }
    }

Stable state and IDs matter when a child contains focus, editing, or an in-flight interaction. Test the transition rather than assuming type erasure solves every identity issue.

## Recipe 4: container-relative card sizing

Use the nearest container instead of a device-name breakpoint:

    ScrollView(.horizontal) {
        LazyHStack(spacing: 16) {
            ForEach(items) { item in
                Card(item: item)
                    .containerRelativeFrame(
                        .horizontal,
                        count: 1,
                        span: 1,
                        spacing: 16
                    )
            }
        }
        .scrollTargetLayout()
    }
    .scrollTargetBehavior(.viewAligned)

Confirm the selected scroll-target APIs and deployment availability in the target. Test the real window/navigation/scroll container, safe-area insets, Dynamic Type, and long content.

## Recipe 5: safe-area-aware glass action group

Keep the edge relationship in the screen shell:

    ScrollView {
        ContentView()
    }
    .safeAreaInset(edge: .bottom, spacing: 0) {
        HStack {
            Text(status)
                .accessibilityLabel("Status")
            Spacer()
            Button("Save", action: save)
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .glassEffect()
        .padding(.horizontal)
    }

The control group still needs a reduced-transparency/standard-material fallback, labels, focus behavior, and a disabled/error state. Verify that scroll content, indicators, and the keyboard are not obscured.

## Recipe 6: custom layout value for action priority

Use LayoutValueKey for a bounded geometry hint:

    private struct ActionRank: LayoutValueKey {
        static let defaultValue: Int = 0
    }

    extension View {
        func actionRank(_ rank: Int) -> some View {
            layoutValue(key: ActionRank.self, value: rank)
        }
    }

    EqualWidthRow {
        Button("Primary", action: primary)
            .actionRank(100)
        Button("Secondary", action: secondary)
            .actionRank(50)
    }

The layout can read subview[ActionRank.self] to decide placement, but it must not remove a critical action or turn a model-provided arbitrary number into authority. Clamp or map values before applying them.

## Recipe 7: when GeometryReader is justified

Use GeometryReader for a real coordinate-space dependency, such as a bounded progress backdrop:

    GeometryReader { proxy in
        let width = max(proxy.size.width, 1)
        ZStack(alignment: .leading) {
            RoundedRectangle(cornerRadius: 12)
                .fill(.secondary.opacity(0.15))
            RoundedRectangle(cornerRadius: 12)
                .fill(.tint)
                .frame(width: width * progress)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Progress")
        .accessibilityValue(progress.formatted(.percent))
    }
    .frame(height: 24)

Do not use the measured width to mutate state or to choose a model prompt. If a standard container or containerRelativeFrame expresses the relationship, prefer that route.

## Recipe 8: bounded AI layout proposal

    enum ActionMode: String, Codable, Sendable {
        case full
        case overflow
        case primaryOnly
    }

    struct LayoutProposal: Codable, Sendable {
        let mode: ActionMode
        let emphasis: Double
    }

    func validate(_ proposal: LayoutProposal) -> LayoutProposal {
        LayoutProposal(
            mode: proposal.mode,
            emphasis: min(max(proposal.emphasis, 0), 1)
        )
    }

Apply the validated proposal only through a deterministic policy that considers Dynamic Type, accessibility, platform, source state, and user settings. The model does not emit Layout code, geometry constants, resource paths, or action deletion.

## Recipe 9: fixture-driven layout tests

Test the layout as a projection:

    proposal: .zero / .infinity / .unspecified
    width: compact / regular / split-view
    text: short / long / localized / RTL
    type: default / large / accessibility
    source: idle / loading / partial / stale / failed
    effects: normal / reduced-transparency / Reduce Motion
    input: touch / VoiceOver / Voice Control / Switch Control / keyboard

Assert action identity, returned bounds, placement, semantic labels, focus/recovery, and source state separately from screenshots.

## Sources

- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [LayoutSubview](https://developer.apple.com/documentation/swiftui/layoutsubview)
- [ProposedViewSize](https://developer.apple.com/documentation/swiftui/proposedviewsize)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [LayoutValueKey](https://developer.apple.com/documentation/swiftui/layoutvaluekey)
- [layoutValue(key:value:)](https://developer.apple.com/documentation/swiftui/view/layoutvalue%28key%3Avalue%3A%29)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [GeometryReader](https://developer.apple.com/documentation/swiftui/geometryreader)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

# Accessibility, Adaptation, and Native Design Recipes

## Scope and compile boundary

These are compile-oriented SwiftUI and UI-test route sketches for the [native screen composition atlas](../21-design-deep-dives/08-native-screen-composition-atlas.md), [navigation, toolbar, and tab hierarchy](../21-design-deep-dives/09-navigation-toolbar-and-tab-hierarchy.md), [sheets, forms, and focused editing](../21-design-deep-dives/10-sheets-forms-and-focused-editing.md), [UIKit interop and representables](../10-swiftui/07-uikit-interop-and-representables.md), [platform adaptation and conditional routes](../10-swiftui/08-platform-adaptation-and-conditional-routes.md), and [cross-platform composition and input design](../21-design-deep-dives/11-cross-platform-composition-and-input.md), covering semantic controls, accessibility trees, focus, Dynamic Type, adaptive layout, reduced motion/transparency, color differentiation, Liquid Glass legibility, localization, and automated accessibility audits. They are not compiled in this documentation-only workspace and do not prove full accessibility, contrast compliance, device ergonomics, VoiceOver quality, localization completeness, or App Store accessibility metadata.

Build the meaning first, then choose the visual treatment. Standard SwiftUI controls and system containers carry platform behavior that custom replicas often miss. Use Liquid Glass as a functional layer for controls and navigation; preserve an understandable content layer beneath it.

## Recipe 1: prefer semantic controls over custom hit regions

Start with a native control whose behavior matches the outcome. Add a visible label and a system symbol when they improve recognition; do not make the symbol itself the only explanation.

```swift
import SwiftUI

struct PinControl: View {
    @Binding var isPinned: Bool

    var body: some View {
        Button {
            isPinned.toggle()
        } label: {
            Label(
                isPinned ? "Unpin note" : "Pin note",
                systemImage: isPinned ? "pin.fill" : "pin"
            )
        }
        .buttonStyle(.bordered)
        .accessibilityValue(isPinned ? "Pinned" : "Not pinned")
        .accessibilityHint("Changes whether this note appears at the top of the list.")
    }
}
```

If the product needs an icon-only compact control, keep the action label explicit and expose state with `accessibilityValue`. Prefer `Toggle`, `Picker`, `Slider`, `ProgressView`, `NavigationLink`, `TextField`, and `List` when their semantics match the task. A custom rounded rectangle with an `onTapGesture` does not automatically become a button for VoiceOver, Voice Control, Switch Control, keyboard, or pointer input.

## Recipe 2: group one logical row without hiding independent actions

Use accessibility element behavior deliberately. Combine static label/value content that should be spoken as one unit, but keep buttons, toggles, links, and menus separate so each action remains reachable.

```swift
struct StatusRow: View {
    let title: String
    let detail: String
    let isComplete: Bool
    let open: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(detail)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Image(systemName: isComplete ? "checkmark.circle.fill" : "circle")
                .foregroundStyle(isComplete ? .green : .secondary)
                .accessibilityHidden(true)

            Button("Open", action: open)
                .buttonStyle(.borderless)
        }
        .accessibilityElement(children: .contain)
        .accessibilityCustomContent("Status", isComplete ? "Complete" : "Needs attention")
    }
}
```

If the row itself is the only action, use a `NavigationLink` or `Button` and combine its descriptive children. If the row contains multiple independent actions, do not apply `.combine` to the entire row. Verify the reading order instead of guessing from the visual layout.

## Recipe 3: give custom charts and drawings an accessible representation

Custom drawing, a canvas, a decorative glass surface, and a chart can look meaningful while exposing little to assistive technologies. Hide decorative pixels and supply a concise summary plus children for the important data points.

```swift
struct ProgressPoint: Identifiable {
    let id = UUID()
    let label: String
    let value: Double
}

struct ProgressGraphic: View {
    let points: [ProgressPoint]

    var body: some View {
        Canvas { context, size in
            // Draw the product-specific graphic here.
            context.fill(
                Path(roundedRect: CGRect(origin: .zero, size: size), cornerRadius: 16),
                with: .foreground
            )
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Progress over time")
        .accessibilityValue(summary)
        .accessibilityChildren {
            ForEach(points) { point in
                Text("\(point.label): \(point.value, format: .number)")
            }
        }
    }

    private var summary: String {
        guard let latest = points.last else { return "No data" }
        return "Latest \(latest.value, format: .number)"
    }
}
```

Use a chart-specific accessibility descriptor when the visualization needs axis/series semantics. Do not announce every frame of an animated graphic. Update the accessible value at a meaningful cadence and provide a text/table route when the graphic is not the only way to understand the data.

## Recipe 4: move accessibility focus after a meaningful validation result

Accessibility focus is separate from keyboard/input focus. Move it only when the person needs to know about a new error, result, or modal state, and make the target’s label/value useful when it receives focus.

```swift
struct AccessibleEditor: View {
    enum Field: Hashable {
        case title
        case error
    }

    @Binding var title: String
    @State private var errorMessage: String?
    @AccessibilityFocusState private var focusedField: Field?

    var body: some View {
        Form {
            TextField("Title", text: $title)
                .accessibilityFocused($focusedField, equals: .title)

            if let errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
                    .accessibilityFocused($focusedField, equals: .error)
                    .accessibilityAddTraits(.isStaticText)
            }
        }
        .onSubmit {
            if title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                errorMessage = "Enter a title before continuing."
                focusedField = .error
            } else {
                errorMessage = nil
            }
        }
    }
}
```

The focus value is a product decision, not a substitute for visible error styling or inline recovery. Test with VoiceOver active and inactive, because the focus binding can be absent when no accessibility technology is using the tree.

## Recipe 5: make reduced motion and reduced transparency real behavior paths

Preserve the state change while changing the transition. Reduced motion should not merely make a large animation faster. Reduced transparency should not leave text floating over an unreadable background.

```swift
struct ExpandableSummary: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @State private var isExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button(isExpanded ? "Hide details" : "Show details") {
                if reduceMotion {
                    isExpanded.toggle()
                } else {
                    withAnimation(.snappy) {
                        isExpanded.toggle()
                    }
                }
            }

            if isExpanded {
                Text("The details remain available without depending on motion.")
                    .transition(reduceMotion ? .opacity : .move(edge: .top).combined(with: .opacity))
            }
        }
        .padding()
        .background(
            reduceTransparency
                ? AnyShapeStyle(.regularMaterial)
                : AnyShapeStyle(.thinMaterial),
            in: .rect(cornerRadius: 18)
        )
    }
}
```

For a custom Liquid Glass control, branch to an opaque or standard-material treatment when transparency is reduced, and verify that the hierarchy still works when all motion and translucency are removed. Do not use animated blur, parallax, or morphing as the only confirmation of a save, navigation, or state change.

## Recipe 6: let Dynamic Type choose the composition

Use text styles and `ScaledMetric` for scalable values. When content can no longer fit horizontally at accessibility sizes, change the composition rather than clipping or shrinking the text below the user’s chosen size.

```swift
struct AdaptiveSummaryRow: View {
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @ScaledMetric(relativeTo: .body) private var iconDimension = 24

    let title: String
    let detail: String

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(alignment: .firstTextBaseline, spacing: 12) {
                Image(systemName: "sparkles")
                    .frame(width: iconDimension, height: iconDimension)
                Text(title)
                    .font(.headline)
                Text(detail)
                    .foregroundStyle(.secondary)
            }

            VStack(alignment: .leading, spacing: 6) {
                Label(title, systemImage: "sparkles")
                    .font(.headline)
                Text(detail)
                    .foregroundStyle(.secondary)
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityValue(Text(dynamicTypeSize.isAccessibilitySize ? "Large text layout" : "Standard layout"))
    }
}
```

The layout alternatives must preserve the same title, detail, and action. Test the largest Dynamic Type sizes, long localized strings, right-to-left layout, compact/regular width, split view, rotation, keyboard, pointer, and the smallest supported window. Do not announce a layout implementation detail such as “standard layout” in a production accessibility value; the example value is only a fixture for testing and should be replaced by product meaning.

## Recipe 7: keep Liquid Glass functional and legible

Use system bars and standard controls first. If a custom action group genuinely needs a glass surface over changing content, keep it small, semantic, and easy to simplify when accessibility settings change.

```swift
struct NativeActionCluster: View {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.accessibilityDifferentiateWithoutColor) private var differentiateWithoutColor

    let primaryAction: () -> Void
    let secondaryAction: () -> Void

    var body: some View {
        Group {
            if reduceTransparency {
                actions
                    .padding(8)
                    .background(.regularMaterial, in: .capsule)
            } else {
                GlassEffectContainer(spacing: 12) {
                    actions
                        .padding(8)
                }
            }
        }
        .accessibilityElement(children: .contain)
    }

    private var actions: some View {
        HStack(spacing: 10) {
            Button {
                primaryAction()
            } label: {
                Label(
                    differentiateWithoutColor ? "Start" : "Start",
                    systemImage: "play.fill"
                )
            }
            .buttonStyle(.glassProminent)

            Button("More", systemImage: "ellipsis") {
                secondaryAction()
            }
            .buttonStyle(.glass)
        }
    }
}
```

The example keeps text and symbols in both color modes; a real status control should add shape, text, or an alternate icon when color differentiation is disabled. Avoid applying a custom glass effect to the entire content layer. Choose the regular/opaque fallback when text density, contrast, or system settings make a translucent surface less legible, and test the control over realistic light, dark, colorful, and text-heavy backgrounds.

## Recipe 8: automate an accessibility audit, then test meaning manually

Accessibility audits catch common issues such as missing descriptions, insufficient hit regions, contrast, or clipped text. They are a useful gate, not a substitute for human testing with VoiceOver, Voice Control, Switch Control, larger text, or alternate input.

```swift
import XCTest

final class AccessibilityAuditTests: XCTestCase {
    @MainActor
    func testMainScreenAccessibility() throws {
        let app = XCUIApplication()
        app.launch()

        try app.performAccessibilityAudit(for: .all)
    }
}
```

Use stable `accessibilityIdentifier` values for test queries, but keep them separate from user-facing labels and values. An audit can pass while the reading order is confusing, a result is announced too often, a gesture has no alternate path, or a model-derived message lacks useful provenance.

## Recipe 9: build a preview matrix around settings and window shape

Previews should make the environment matrix cheap to inspect. Use them to catch clipped text and poor hierarchy early; use UI tests and physical devices for actual assistive behavior and material performance.

```swift
#Preview("Large text, dark, reduced effects") {
    AdaptiveSummaryRow(
        title: "A long localized title that must remain readable",
        detail: "Updated just now"
    )
    .padding()
    .preferredColorScheme(.dark)
    .environment(\.dynamicTypeSize, .accessibility5)
    .environment(\.accessibilityReduceMotion, true)
    .environment(\.accessibilityReduceTransparency, true)
    .environment(\.accessibilityDifferentiateWithoutColor, true)
}
```

Add fixtures for empty, error, loading, permission denied, offline, stale, selected, disabled, long text, right-to-left, and reduced-effects states. A screenshot is evidence that a supplied state renders; it is not evidence that VoiceOver focus, hit targets, localization, contrast, or device-specific Liquid Glass behavior is correct.

## Verification matrix

| Surface | Minimum evidence |
| --- | --- |
| Semantics | Accessibility tree, labels, values, hints, traits, grouping, independent actions, and custom representations |
| Focus | Keyboard/input focus and accessibility focus after navigation, validation, sheets, errors, and async results |
| Adaptation | All Dynamic Type sizes, compact/regular width, orientation, split view/window resize, keyboard, pointer, and right-to-left |
| Settings | Light/dark, increased contrast, reduced transparency, reduced motion, differentiate without color, Bold Text, and VoiceOver |
| Liquid Glass | System-first surfaces, custom glass only where functional, regular/clear choice, legibility over real content, and opaque fallback |
| Automation | Stable identifiers, primary/recovery UI tests, `performAccessibilityAudit(for:)`, and no reliance on screenshot-only assertions |
| Device | Physical-device VoiceOver, touch target, haptic/audio alternative, scrolling, text editing, and material behavior on supported OS/device builds |

Do not call the UI “accessible” because it passed one audit or preview matrix. Record the target device family, OS build, assistive settings, tested flows, known exceptions, and remediation owner.

## Sources

- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityDifferentiateWithoutColor](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydifferentiatewithoutcolor)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Color](https://developer.apple.com/design/human-interface-guidelines/color)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

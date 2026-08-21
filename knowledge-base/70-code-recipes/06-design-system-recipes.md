# Design-System Recipes for Native Screens

## Scope and compile boundary

These are small SwiftUI route sketches for the screen blueprints in [Native screen blueprints](../21-design-deep-dives/06-native-screen-blueprints.md), the [native screen composition atlas](../21-design-deep-dives/08-native-screen-composition-atlas.md), [navigation, toolbar, and tab hierarchy](../21-design-deep-dives/09-navigation-toolbar-and-tab-hierarchy.md), [sheets, forms, and focused editing](../21-design-deep-dives/10-sheets-forms-and-focused-editing.md), [platform adaptation and conditional routes](../10-swiftui/08-platform-adaptation-and-conditional-routes.md), and [cross-platform composition and input design](../21-design-deep-dives/11-cross-platform-composition-and-input.md). They show how to keep semantic behavior, state, adaptation, accessibility, and Liquid Glass decisions visible in code. They are not compiled in this documentation-only workspace.

Before using a recipe, compile it in the target project with the selected SDK and deployment target. Confirm availability, imports, platform differences, and the current modifier signatures. A code-shaped example is not proof of compilation, accessibility, device behavior, material rendering, or release readiness.

## Recipe 1: small, semantic design tokens

Keep the design system small enough that it reinforces SwiftUI instead of hiding it. Prefer system text styles, semantic colors, system symbols, and platform spacing. Add a token only when it represents a repeated product decision that survives Dynamic Type, appearance changes, and platform adaptation.

```swift
import SwiftUI

enum NativeDesign {
    static let contentSpacing: CGFloat = 20
    static let sectionSpacing: CGFloat = 28
    static let contentPadding: CGFloat = 20
    static let controlCornerRadius: CGFloat = 18

    static let primaryShape = RoundedRectangle(
        cornerRadius: controlCornerRadius,
        style: .continuous
    )
}

struct NativeSection<Content: View>: View {
    private let title: LocalizedStringKey
    private let content: Content

    init(
        _ title: LocalizedStringKey,
        @ViewBuilder content: () -> Content
    ) {
        self.title = title
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
                .foregroundStyle(.secondary)

            content
        }
    }
}
```

The token layer deliberately does not declare a private “Apple font,” an opaque universal card background, or a fixed text size. If a product needs a brand typeface, test it against the platform’s legibility and Dynamic Type guidance rather than replacing semantic hierarchy with a font name.

## Recipe 2: a screen shell that keeps navigation native

Make the navigation container and title visible at the feature boundary. The shell owns layout and destinations; the feature owns state and domain operations.

```swift
struct NativeScreenShell<Content: View>: View {
    let title: LocalizedStringKey
    @ViewBuilder let content: () -> Content

    var body: some View {
        NavigationStack {
            ScrollView {
                content()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, NativeDesign.contentPadding)
                    .padding(.vertical, NativeDesign.contentSpacing)
            }
            .navigationTitle(title)
        }
    }
}
```

For an iPad or regular-width experience, replace the shell with a `NavigationSplitView` when keeping collection and detail visible improves the task. Do not force one stack layout to imitate a split view by shrinking cards or inserting a custom glass sidebar.

## Recipe 3: explicit screen states

State rendering should make the product contract visible. The domain/service layer decides which state is true; the view decides how to communicate it.

```swift
enum ScreenState<Value> {
    case loading
    case empty
    case content(Value)
    case failed(message: LocalizedStringKey)
    case permissionDenied
}

struct ScreenStateView<Value, Content: View>: View {
    let state: ScreenState<Value>
    let retry: () -> Void
    @ViewBuilder let content: (Value) -> Content

    var body: some View {
        switch state {
        case .loading:
            ProgressView("Loading")
                .frame(maxWidth: .infinity, minHeight: 160)

        case .empty:
            ContentUnavailableView(
                "Nothing here yet",
                systemImage: "tray",
                description: Text("Create the first item to get started.")
            )

        case let .content(value):
            content(value)

        case let .failed(message):
            ContentUnavailableView {
                Label("Couldn’t load this", systemImage: "exclamationmark.triangle")
            } description: {
                Text(message)
            } actions: {
                Button("Try Again", action: retry)
                    .buttonStyle(.borderedProminent)
            }

        case .permissionDenied:
            ContentUnavailableView(
                "Permission needed",
                systemImage: "lock",
                description: Text("Allow access in Settings or continue with manual input.")
            )
        }
    }
}
```

The sample copy is illustrative and must be localized. The permission branch must be product-specific: explain the capability, do not expose a settings route that does not exist, and offer a fallback when one is possible.

## Recipe 4: a dashboard section with native controls

Use semantic hierarchy and native controls before card decoration. A `Button` or `NavigationLink` should own the action; the visual treatment should not turn a whole layout into one ambiguous hit target.

```swift
struct DashboardContent: View {
    let progress: Double
    let start: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: NativeDesign.sectionSpacing) {
            NativeSection("Today") {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Your next useful step")
                        .font(.title2.weight(.semibold))

                    ProgressView(value: progress)
                        .accessibilityLabel("Today’s progress")
                        .accessibilityValue(Text(progress, format: .percent))

                    Button("Continue", action: start)
                        .buttonStyle(.borderedProminent)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            NativeSection("Recent") {
                NavigationLink("Open recent item") {
                    Text("Detail")
                        .navigationTitle("Detail")
                }
            }
        }
    }
}
```

When the progress value is not a percentage, expose the unit and meaning in the accessibility value. Do not make a progress bar or a color-only status carry the entire explanation.

## Recipe 5: a related glass action cluster

The system’s standard controls and bars are the default Liquid Glass route. Use a custom effect only for a small functional group that must read as one surface over changing content.

```swift
struct FunctionalGlassActions: View {
    let play: () -> Void
    let stop: () -> Void

    var body: some View {
        GlassEffectContainer(spacing: 18) {
            HStack(spacing: 12) {
                Button("Play", systemImage: "play.fill", action: play)
                    .buttonStyle(.glass)

                Button("Stop", systemImage: "stop.fill", action: stop)
                    .buttonStyle(.glass)
            }
            .padding(8)
        }
        .accessibilityElement(children: .contain)
    }
}
```

If a custom view rather than a button needs the effect, use `glassEffect(_:in:)` after the content’s appearance modifiers and choose a shape that fits the component. Use tint as a prominence signal, not as a substitute for a label or contrast. If the controls morph between states, use stable `glassEffectID` values within a `Namespace` and test insertion/removal with reduced motion.

The exact Liquid Glass APIs are SDK-sensitive. Keep a small minimal sample for compilation instead of spreading unverified modifiers through every feature.

## Recipe 6: adaptive dashboard composition

Let the available proposal decide when the composition should change. Use a split view for a true list/detail relationship, and use `ViewThatFits` or `AnyLayout` for a smaller layout substitution.

```swift
struct AdaptiveSummary: View {
    let summary: String
    let detail: String

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(alignment: .firstTextBaseline, spacing: 16) {
                Text(summary)
                    .font(.title2.weight(.semibold))
                Text(detail)
                    .foregroundStyle(.secondary)
            }

            VStack(alignment: .leading, spacing: 6) {
                Text(summary)
                    .font(.title2.weight(.semibold))
                Text(detail)
                    .foregroundStyle(.secondary)
            }
        }
    }
}
```

Do not use this as permission to hide important text. Both alternatives must carry the same meaning, labels, and actions. Test long localized strings and large Dynamic Type sizes; a layout that only works with English defaults is not adaptive.

## Recipe 7: form/editor with focus and honest commit state

Keep draft data and save status explicit. The view can coordinate focus and validation, but the service/repository owns durable persistence.

```swift
struct DraftEditor: View {
    @Binding var title: String
    @Binding var notes: String
    let save: () async -> Result<Void, Error>

    @FocusState private var focusedField: Field?
    @State private var isSaving = false
    @State private var saveMessage: LocalizedStringKey?

    enum Field: Hashable {
        case title
        case notes
    }

    var body: some View {
        Form {
            Section("Required") {
                TextField("Title", text: $title)
                    .focused($focusedField, equals: .title)
                    .submitLabel(.next)
                    .onSubmit { focusedField = .notes }
            }

            Section("Notes") {
                TextEditor(text: $notes)
                    .focused($focusedField, equals: .notes)
                    .frame(minHeight: 160)
            }

            if let saveMessage {
                Text(saveMessage)
                    .foregroundStyle(.secondary)
                    .accessibilityAddTraits(.updatesFrequently)
            }
        }
        .navigationTitle("Edit")
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("Save") {
                    Task {
                        isSaving = true
                        defer { isSaving = false }
                        let result = await save()
                        switch result {
                        case .success:
                            saveMessage = "Saved"
                        case .failure:
                            saveMessage = "Couldn’t save"
                        }
                    }
                }
                .disabled(isSaving || title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            }
        }
        .overlay {
            if isSaving {
                ProgressView("Saving")
                    .padding()
                    .background(.regularMaterial, in: .rect(cornerRadius: 16))
            }
        }
    }
}
```

The result handling above is intentionally small; a real target should map its concrete error type to localized, field-aware recovery copy. Keep the draft when saving fails, announce the error accessibly, and do not leave a “Saved” message after a failed operation. If the save action needs to remain visible above a long editor, prefer a native toolbar or safe-area route before adding a custom glass bar.

## Recipe 8: review sheet and destructive confirmation

Separate “what will happen” from “do it.” Use a sheet for a reviewable task and a confirmation dialog for a small contextual decision.

```swift
struct ReviewSheet: View {
    @Environment(\.dismiss) private var dismiss
    let summary: String
    let commit: () async throws -> Void

    @State private var isCommitting = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 20) {
                Text("Review your change")
                    .font(.title2.weight(.semibold))

                Text(summary)
                    .frame(maxWidth: .infinity, alignment: .leading)

                if let errorMessage {
                    Text(errorMessage)
                        .foregroundStyle(.red)
                        .accessibilityAddTraits(.isStaticText)
                }

                Spacer()
            }
            .padding()
            .navigationTitle("Review")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Confirm") {
                        Task {
                            isCommitting = true
                            defer { isCommitting = false }
                            do {
                                try await commit()
                                dismiss()
                            } catch {
                                errorMessage = "The change wasn’t applied. Review and try again."
                            }
                        }
                    }
                    .disabled(isCommitting)
                }
            }
            .overlay {
                if isCommitting {
                    ProgressView("Applying")
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }
}
```

Use localized product copy and a domain-specific error route in a real target. If the action is destructive, make the consequence explicit and use `confirmationDialog` or another appropriate system confirmation surface rather than relying on a red glass button alone.

## Recipe 9: compact utility with a full-app route

Keep a one-glance feature bounded. The compact view communicates one status and one action; the destination owns the full workflow.

```swift
struct CompactUtility: View {
    let status: String
    let freshness: String
    let openFullApp: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Current status", systemImage: "bolt.circle")
                .font(.headline)

            Text(status)
                .font(.title3.weight(.semibold))

            Text(freshness)
                .font(.footnote)
                .foregroundStyle(.secondary)

            Button("Open details", action: openFullApp)
                .buttonStyle(.glassProminent)
        }
        .padding()
        .accessibilityElement(children: .contain)
    }
}
```

For a widget, Live Activity, or system control, move this contract into the relevant WidgetKit, ActivityKit, or App Intents target and verify its timeline, update, authorization, and deep-link behavior. Do not infer those behaviors from an in-app preview.

## Recipe 10: preview and accessibility matrix

Previews are a fast way to exercise state and layout fixtures. Keep them deterministic and make the scenarios obvious.

```swift
#Preview("Dashboard - light") {
    NativeScreenShell(title: "Home") {
        DashboardContent(progress: 0.6, start: {})
    }
}

#Preview("Dashboard - large type") {
    NativeScreenShell(title: "Home") {
        DashboardContent(progress: 0.6, start: {})
    }
    .environment(\.dynamicTypeSize, .accessibility3)
}

#Preview("Dashboard - dark and reduced effects") {
    NativeScreenShell(title: "Home") {
        DashboardContent(progress: 0.6, start: {})
    }
    .preferredColorScheme(.dark)
    .environment(\.accessibilityReduceMotion, true)
    .environment(\.accessibilityReduceTransparency, true)
}
```

Add previews for loading, empty, error, permission-denied, long localized content, right-to-left layout, compact width, and regular width. Use UI tests and Accessibility Inspector for focus and semantics. A preview matrix does not prove hardware-only APIs, Apple Intelligence model availability, system permissions, entitlements, background refresh, or physical-device Liquid Glass performance.

## Design-system review checklist

- The component keeps the semantic SwiftUI control and does not turn decoration into the hit target.
- The component has explicit loading, empty, content, error, permission/unavailable, and disabled behavior where relevant.
- Text uses system styles or a tested scalable custom style; no fixed-height text container assumes English copy.
- Colors communicate roles and remain legible in light/dark, Increased Contrast, and Reduce Transparency configurations.
- Animation has a state reason, a reduced-motion path, and no delayed critical action.
- Haptics supplement visible/accessibility state and are not the only confirmation.
- Custom Liquid Glass is limited to a functional surface, uses stable identity when morphing, and is grouped only with related effects.
- Preview fixtures cover state, text size, appearance, layout width, and localization; compile/device proof is recorded separately.
- Dependencies and side effects remain outside reusable visual components.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [View fundamentals](https://developer.apple.com/documentation/swiftui/view-fundamentals)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
- [Form](https://developer.apple.com/documentation/swiftui/form)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextField](https://developer.apple.com/documentation/swiftui/textfield)
- [Adding a search interface to your app](https://developer.apple.com/documentation/swiftui/adding-a-search-interface-to-your-app)
- [Managing search interface activation](https://developer.apple.com/documentation/swiftui/managing-search-interface-activation)
- [Presentation modifiers](https://developer.apple.com/documentation/SwiftUI/View-Presentation)
- [confirmationDialog](https://developer.apple.com/documentation/swiftui/view/confirmationdialog%28_%3Aispresented%3Atitlevisibility%3Apresenting%3Aactions%3Amessage%3A%29)
- [safeAreaBar(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareabar%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [glassProminent](https://developer.apple.com/documentation/SwiftUI/PrimitiveButtonStyle/glassProminent)
- [glass](https://developer.apple.com/documentation/swiftui/primitivebuttonstyle/glass)
- [glassEffect(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffect%28_%3Ain%3A%29)
- [glassEffectID(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffectid%28_%3Ain%3A%29)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [dynamicTypeSize](https://developer.apple.com/documentation/swiftui/environmentvalues/dynamictypesize)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [App Intents](https://developer.apple.com/documentation/appintents)

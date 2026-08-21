# SwiftUI and Liquid Glass Recipes

Use these minimal seams alongside the [native screen composition atlas](../21-design-deep-dives/08-native-screen-composition-atlas.md), [navigation, toolbar, and tab hierarchy](../21-design-deep-dives/09-navigation-toolbar-and-tab-hierarchy.md), [UIKit interop and representables](../10-swiftui/07-uikit-interop-and-representables.md), [platform adaptation and conditional routes](../10-swiftui/08-platform-adaptation-and-conditional-routes.md), [cross-platform composition and input design](../21-design-deep-dives/11-cross-platform-composition-and-input.md), and [functional Liquid Glass interactions](../20-liquid-glass/05-functional-glass-interactions.md). Choose the system container or control that already expresses the user outcome before adding a custom glass effect.

## Minimal app shell

Start with native scene, navigation, and system controls. Add a custom surface only after the standard route cannot express the product hierarchy.

```swift
import SwiftUI

@main
struct NativeShellApp: App {
    var body: some Scene {
        WindowGroup {
            NavigationStack {
                HomeView()
            }
        }
    }
}

struct HomeView: View {
    var body: some View {
        List {
            Section("Today") {
                NavigationLink("Open detail") {
                    DetailView()
                }
            }
        }
        .navigationTitle("Home")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button("Add", systemImage: "plus") { }
            }
        }
    }
}

struct DetailView: View {
    var body: some View {
        Text("Detail")
            .navigationTitle("Detail")
    }
}
```

The empty button action is intentional: connect it to a tested domain operation rather than putting persistence or networking in the view.

## Custom Liquid Glass control

```swift
struct FocusControl: View {
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label("Focus", systemImage: "scope")
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
        }
        .glassEffect(
            .regular.tint(.accentColor).interactive(),
            in: .rect(cornerRadius: 18)
        )
    }
}
```

Use the system control first. If the custom effect is necessary, keep the button semantic, keep the label meaningful, and test the effect with reduced transparency, increased contrast, large text, and Reduce Motion.

## Grouped glass actions

```swift
GlassEffectContainer(spacing: 20) {
    HStack(spacing: 12) {
        Button("Play", systemImage: "play.fill") { }
            .glassEffect()
        Button("More", systemImage: "ellipsis") { }
            .glassEffect()
    }
}
```

The container is for related glass views. Do not use it as a universal background wrapper.

## Compile/device gate

- Confirm the selected SDK includes the Liquid Glass APIs and the target deployment supports the route.
- Compile the custom control in a minimal sample before integrating it into a complex screen.
- Preview light/dark, long labels, large text, and reduced effects.
- Run on target OS/device to validate material, performance, hit targets, and morphing.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

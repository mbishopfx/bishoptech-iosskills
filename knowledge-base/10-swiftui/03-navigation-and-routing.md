# Navigation and Routing

## Pick the container that matches the information architecture

- TabView separates peer destinations and supports a persistent top-level switch.
- NavigationStack presents a path of destinations in a forward/back hierarchy.
- NavigationSplitView presents two or three related columns and adapts to platform/window size.
- A sheet, popover, or full-screen cover presents a temporary task or focused modal flow.

Do not use a tab bar as a modal menu or a navigation stack as a replacement for a settings form. The container communicates the hierarchy to people and to the system.

## Model routes as data

Use a Hashable route enum or typed path elements for destinations. Register destinations with navigationDestination and keep deep-link parsing separate from view construction.

~~~swift
enum AppRoute: Hashable {
    case item(UUID)
    case settings
}

struct AppShell: View {
    @State private var path: [AppRoute] = []

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .item(let id): ItemView(id: id)
                    case .settings: SettingsView()
                    }
                }
        }
    }
}
~~~

For heterogeneous or restored paths, NavigationPath can hold type-erased Hashable elements. Keep route values small and stable; prefer identifiers over entire mutable model objects.

## Deep links and state restoration

Handle an incoming URL or system intent by translating it into a route, validating that the target exists, and then updating the navigation state. Do not rely on onAppear as the only signal that a route was opened; a view can appear for many reasons. Make routing explicit and test it from cold launch, foreground launch, and an already-present stack.

## Search and iOS 26 navigation

Use the standard search placement and system tab role when a search experience belongs in the app’s primary navigation. Apple’s Liquid Glass guidance separates navigation from content and calls out semantic search tabs so the system can place search consistently across devices.

## Modal rules

- Use sheet(item:) when the presentation is the presence of a value.
- Use sheet(isPresented:) for a simple Boolean presentation.
- Use a navigation stack inside a multi-step sheet.
- Provide a clear cancel/close route and preserve draft state intentionally.
- Do not hide destructive actions behind an ambiguous icon.

## Sources

- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

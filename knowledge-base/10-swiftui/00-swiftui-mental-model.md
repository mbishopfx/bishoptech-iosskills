# SwiftUI Mental Model

## Declare the interface

SwiftUI is a declarative framework. A View describes what should be visible for a given state; SwiftUI evaluates the hierarchy and updates affected output when the data changes. The most useful shift is to stop thinking of a view as a one-time screen construction and start thinking of it as a function of state and environment.

~~~swift
struct EmptyStateView: View {
    let title: String
    let action: () -> Void

    var body: some View {
        ContentUnavailableView {
            Label(title, systemImage: "tray")
        } description: {
            Text("Add something to get started.")
        } actions: {
            Button("Add") { action() }
                .buttonStyle(.borderedProminent)
        }
    }
}
~~~

The important design choices are the semantic view hierarchy, a system control for the action, and explicit data/action inputs. The specific visual treatment can evolve without changing the domain rule.

## View boundaries

Create a custom view when a region has a clear purpose, repeated structure, or meaningful state boundary. Keep a view’s body readable by extracting subviews rather than hiding all logic behind generic view builders. A view should usually format and route intent; it should not be the only place where a business rule exists.

## Environment is part of the design

SwiftUI supplies environment values for color scheme, accessibility settings, locale, size category, scene phase, model context, and more. A polished interface responds to those values instead of assuming a single screen size, language, contrast setting, or motion preference.

## Native before custom

Start with Text, Label, Image, Button, Toggle, Picker, TextField, List, Form, NavigationStack, NavigationSplitView, TabView, sheets, and toolbars. Native controls carry platform behavior, accessibility semantics, keyboard/pointer behavior, and system visual updates. Customize only where the product has a real expressive need.

## Composition checklist

- Does each subview have one visual or interaction responsibility?
- Is the view driven by explicit input rather than hidden global state?
- Is the action exposed through a semantic control?
- Does the hierarchy remain readable with Dynamic Type?
- Does the view adapt to light/dark appearance and accessibility settings?
- Can the same domain action be reused by an App Intent or widget?

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Declaring a custom view](https://developer.apple.com/documentation/swiftui/declaring-a-custom-view)
- [View fundamentals](https://developer.apple.com/documentation/swiftui/view-fundamentals)
- [App organization](https://developer.apple.com/documentation/swiftui/app-organization)

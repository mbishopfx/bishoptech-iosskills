# Apple-Native Screen Recipes

These are layout recipes, not visual clones. Use them as starting structures and let the system supply the current platform treatment.

## Recipe: content-first detail screen

Use for a photo, document, item, player, or profile detail flow.

1. Root NavigationStack.
2. Scrollable content with the primary visual extending toward the safe area where appropriate.
3. Semantic title and supporting metadata.
4. toolbar for navigation and secondary actions.
5. One clear primary action, using a system control style.
6. Review with text scaling and content behind the toolbar.

## Recipe: tab-based utility

Use for a small set of peer destinations.

1. TabView with stable tab identity.
2. Keep the number of primary destinations small enough to scan.
3. Put search in the semantic search role when it is a primary destination.
4. Use a sheet for creation or focused editing, not another pseudo-tab.
5. Keep a deep-link route for every meaningful tab and item destination.

## Recipe: iPad/sidebar workspace

Use NavigationSplitView for list/detail or sidebar/content/inspector relationships.

1. Sidebar selection is the source of truth for the detail route.
2. Detail content responds to selection without duplicating domain state.
3. Let columns resize and reflow; avoid hard-coded widths unless the content needs a bounded range.
4. Test compact and regular widths and window resizing.

## Recipe: floating action cluster

1. Keep content readable behind it.
2. Put only the few actions needed at that moment into a GlassEffectContainer.
3. Use a standard Button/Menu and a glass button style first.
4. Use custom glassEffect only for the remaining expressive need.
5. Register a safeAreaBar if content scrolls underneath a custom bar.

## Recipe: review-before-commit AI screen

1. Show the source content or source reference.
2. Show the generated proposal in an editable form.
3. Mark uncertainty or missing fields.
4. Provide deterministic actions: accept, edit, discard, retry, export.
5. Keep the model output separate from the committed domain record.

## Sources

- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Landmarks: Building an app with Liquid Glass](https://developer.apple.com/documentation/swiftui/landmarks-building-an-app-with-liquid-glass)
- [App Intents](https://developer.apple.com/documentation/appintents/)

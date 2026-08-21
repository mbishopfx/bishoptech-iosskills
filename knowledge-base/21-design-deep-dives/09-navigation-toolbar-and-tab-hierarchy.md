# Navigation, Toolbar, and Tab Hierarchy

## The hierarchy rule

Use each surface for its native job:

| Surface | Job | Do not use it for |
| --- | --- | --- |
| `TabView`/tab bar | Navigate among top-level peer sections while preserving each section’s navigation state | Primary actions, transient filters, or a list of every possible command |
| `NavigationStack` | Navigate through a compact hierarchy and deep links | A fake tab bar built from custom buttons |
| `NavigationSplitView` | Keep sidebar/list/detail or content/inspector relationships visible in regular width | A permanently visible iPhone sidebar in a constrained context |
| Toolbar/navigation bar | Orient the person and expose important actions/search | Every possible command or a duplicate tab bar |
| Menu/context menu | Hold secondary or infrequent actions near the object | Hiding the only route to a core task |
| Sheet | Focus attention on creation, review, settings, or a contained task | A second full app hierarchy with unclear dismissal |

This separation is especially important with Liquid Glass: tab bars, sidebars, and toolbars form a functional layer over the content layer. The material should reinforce the hierarchy, not decide the hierarchy.

## TabView and adaptable navigation

- Give each top-level destination a stable `Tab` identity and concise label; use scalable SF Symbols when appropriate.
- Keep the tab bar discoverable and stable. If a section is empty, explain why instead of removing its tab unpredictably.
- Use `sidebarAdaptable`/the current adaptable tab APIs only when the product genuinely benefits from tab/sidebar representations across contexts; do not force a custom sidebar to imitate Apple’s apps.
- Keep the default set small enough to remain understandable in compact and regular representations; if customization is offered, preserve a sensible default and test restoration.
- Use `tabViewBottomAccessory` for a related accessory such as a compact player/status surface. Inspect `tabViewBottomAccessoryPlacement` so the accessory remains useful when the bar collapses or moves inline.
- Use `tabBarMinimizeBehavior` only when minimizing the bar improves the content task and the user can reliably return to the expanded state.

### Tab state contract

`launch -> selectedTab -> nestedPath -> tabAccessoryState -> deepLink -> restoredSelection`

Persist only what should survive relaunch and account changes. A deep link should select the correct tab and validate the destination record; a stale/deleted item must land on a truthful empty/error route.

## Toolbar composition

- Put only the most important actions in the main toolbar. Move secondary actions to a `Menu` with familiar symbols and predictable order.
- Use the standard Back and Close behavior; do not replace it with a branded text button unless the target interaction truly requires it and remains recognizable.
- Use a concise title that orients the person. The app name is not a useful title for every screen.
- Group actions by relationship and keep destructive actions visually/semantically distinct with confirmation.
- Match top menu actions to equivalent swipe actions; do not expose contradictory actions in different surfaces.
- Use the standard toolbar appearance first. If a custom accessory is needed, maintain concentric corner relationships and test content scrolling underneath it.

## Liquid Glass placement

1. Let standard tab bars, toolbars, sidebars, buttons, menus, and system controls adopt the current system treatment.
2. Add custom glass only to a compact action/status group that floats above content.
3. Keep content backgrounds/records on standard materials or content-specific surfaces.
4. Use tint and color sparingly so labels/icons remain legible against changing content.
5. Test scrolling, selection, focus, Dynamic Type, reduced transparency, dark/light appearance, and system surface transitions.

Do not apply a page-wide `glassEffect` behind text simply to create an “Apple replica” look. Native polish comes from hierarchy, spacing, typography, interaction, and adaptation.

## Accessibility and input

- Every tab and toolbar action needs a spoken label and meaningful state/value.
- Verify VoiceOver order when a tab bar, toolbar, bottom accessory, sheet, or custom glass group appears/disappears.
- Ensure Voice Control can name and activate actions and Switch Control can reach all core commands.
- Provide keyboard/pointer/controller equivalents where the platform supports them; do not make a swipe the only path to a core action.
- When Reduce Motion is enabled, selection/deep-link changes may cross-fade or update immediately but must preserve focus and location.
- When Reduce Transparency is enabled, keep toolbar/tab labels on an opaque or standard-material layer with sufficient contrast.

## Verification matrix

| Surface | Preview/simulator | Physical/signed proof |
| --- | --- | --- |
| Tabs and nested navigation | Stable IDs, state restoration, deep-link fixtures, Dynamic Type, layouts | Touch/keyboard/VoiceOver focus, rotation/window changes, real system treatment, signed deep links |
| Toolbar/menu | Labels, disabled/loading/destructive states, localization | Hit regions, scrolling, contrast, Voice Control/Switch Control, real device ergonomics |
| Bottom accessory | Expanded/inline/disabled placements with injected state | Collapse behavior, content inset, lock/background/system surface, supported device family |
| Sidebar/split | Selection and detail fixtures, compact/regular previews | iPad window resizing, pointer/keyboard, focus, signed multi-window/system behavior |

## Sources

- [Human Interface Guidelines: Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- [Human Interface Guidelines: Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars)
- [Human Interface Guidelines: Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- [Human Interface Guidelines: Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [TabView](https://developer.apple.com/documentation/swiftui/tabview)
- [Tab view bottom accessory](https://developer.apple.com/documentation/swiftui/view/tabviewbottomaccessory%28content%3A%29)
- [tabViewBottomAccessoryPlacement](https://developer.apple.com/documentation/swiftui/environmentvalues/tabviewbottomaccessoryplacement)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
- [Toolbars](https://developer.apple.com/documentation/swiftui/toolbars)
- [Menu](https://developer.apple.com/documentation/swiftui/menu)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)

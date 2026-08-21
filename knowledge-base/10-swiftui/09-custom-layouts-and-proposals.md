# SwiftUI custom layouts, proposals, and responsive composition

## The layout contract

SwiftUI lays out a hierarchy through proposals and responses:

    parent proposal -> child measurement -> container size -> placement

The parent proposes a size; a child chooses a size in response; the container reports its composite size and places its children. The proposal is not a command that every child must accept. A child can choose an ideal size, a minimum/maximum size, or a size that preserves its content.

Use the simplest native container that expresses the relationship:

| Need | Preferred route |
| --- | --- |
| Standard row/column/overlay | HStack, VStack, ZStack |
| Grid or table-like alignment | Grid or the appropriate system collection |
| A few intentional compact alternatives | ViewThatFits |
| Same subviews, different container arrangement | AnyLayout |
| Size relative to a scroll/window/navigation container | containerRelativeFrame |
| Persistent edge action/status content | toolbar, safeAreaInset, or safeAreaBar |
| Geometry that genuinely depends on a coordinate space | GeometryReader or an anchor |
| Reusable measurement/placement algorithm | Layout protocol |

Do not start with GeometryReader or a custom Layout just to reproduce one screenshot. Custom layout is appropriate when the relationship itself is reusable and cannot be expressed clearly with the built-in tools.

## ProposedViewSize

ProposedViewSize provides the size proposal used by the Layout protocol. Apple documents three useful probes:

- zero asks for a minimum-size response;
- infinity asks for a maximum-size response;
- unspecified asks for an ideal-size response.

A parent can call sizeThatFits more than once with different proposals, including one finite dimension and one unspecified dimension. A layout must therefore make measurement deterministic and avoid side effects. Do not start tasks, mutate domain state, or depend on a single measurement call.

When implementing a custom layout:

1. Measure each LayoutSubview with the proposal that matches the question being answered.
2. Treat nil width/height as unspecified rather than zero.
3. Return the size of the composite container.
4. Place every subview exactly once in placeSubviews.
5. Re-measure only when the proposal or subview inputs require it.
6. Keep calculation and placement consistent so the returned bounds can contain the placed content.

Ignoring a proposal can be correct for an intentionally rigid layout, but it must be a documented choice. A responsive glass control group should usually offer a compact alternative rather than returning an ideal size that causes clipping.

## Layout protocol

Layout is a protocol for a type that defines the geometry of a collection of views. Its required methods are:

| Method | Responsibility |
| --- | --- |
| sizeThatFits(proposal:subviews:cache:) | Return the composite size for the proposed container |
| placeSubviews(in:proposal:subviews:cache:) | Place each proxy inside the supplied bounds |

Layout receives Layout.Subviews, a collection of LayoutSubview proxies. A proxy can report:

- size for a proposal;
- dimensions and alignment guides;
- preferred spacing;
- layout priority;
- custom LayoutValueKey values;
- its placement through place(at:anchor:proposal:).

The layout does not own the child views. It arranges proxies supplied by SwiftUI. Keep domain state and accessibility semantics in the child views and their labels; use the layout for geometry.

## Caching and layout metadata

Implement makeCache and updateCache when repeated measurement is expensive and the cached values are invalidated by subview changes. Apple’s custom-layout sample demonstrates caching ideal sizes and spacing between sizeThatFits and placeSubviews, while noting that simple layouts may not benefit enough to justify a cache.

Use LayoutProperties when the container has stack-like orientation or other layout characteristics. Use explicitAlignment when the container needs to expose an alignment guide. Use LayoutValueKey when a child must provide a layout hint such as:

    action priority
    preferred visual density
    minimum emphasis
    fixed-column participation
    semantic grouping role

The layout value is a hint to geometry, not a hidden command channel. Validate values at the view boundary, use safe defaults, and keep critical actions present even when a layout changes.

## ViewThatFits and AnyLayout

ViewThatFits evaluates children in the order supplied and chooses the first child whose ideal size fits along the constrained axes. Put the most informative viable composition first, then compact alternatives. It is a good fit for:

    full action row -> icon-plus-menu row -> single primary action
    chart plus legend -> chart only -> key-value summary
    title plus metadata -> title only

It is not a license to hide a critical action. Each alternative must preserve the same outcome, state explanation, and recovery path.

AnyLayout type-erases a Layout so the container can change from HStackLayout to VStackLayout, or from a built-in layout to a custom layout, without destroying the state of the subviews. Use it when the relationship is the same and only arrangement changes. Test insertion/removal, focus, text editing, and animation across the transition.

## GeometryReader and containerRelativeFrame

GeometryReader defines content as a function of its own size and coordinate space and reports a flexible preferred size to its parent. Use it for a genuine measurement/coordinate-space need, such as an anchor, a normalized drawing region, or a child whose position depends on the container. Avoid nesting it as a generic responsive wrapper; it can make proposals less predictable and can create feedback loops when a child’s size is used to determine the parent’s size.

containerRelativeFrame sizes or positions a view relative to the nearest container. Apple’s documentation includes the window/screen, NavigationSplitView column, NavigationStack, TabView tab, ScrollView, and List as possible containers. It also accounts for safe-area insets applied to that container. Prefer it to device-name or screen-width magic numbers for cards, paging content, and gallery items.

## Safe-area composition

Use toolbar or system bars when the control belongs to the system chrome. Use safeAreaInset when content should reserve space for an edge action/status view. The inset view occupies the edge and increases the modified content’s safe area by the same amount.

This matters for Liquid Glass:

    scrollable content
      -> safe-area-aware content region
      -> functional glass action/status group
      -> native accessibility and keyboard path

Do not manually overlay an unmeasured bottom glass bar on top of a ScrollView and then claim the content is safe. Test the keyboard safe area, rotation, Dynamic Type, split view, and interactive dismissal.

## Custom layout and Liquid Glass

Liquid Glass changes how a functional group is perceived, but it does not replace layout ownership:

- the custom Layout owns geometry and spacing;
- the glass effect owns the visual treatment of the functional group;
- the screen shell owns safe areas, navigation, and system bars;
- the child controls own labels, focus, actions, and accessibility;
- the domain owns state, validation, and side effects.

Keep the glass group bounded. Do not let a custom layout place text or controls under a translucent region without a contrast and hit-testing plan. If a layout becomes unavailable or too dense, fall back to native stacks, a menu, a sheet, or a static status view.

## Animation, identity, and state

Layout conforms to Animatable, so a custom layout can participate in transitions when its animatable parameters change. Animation is optional; it must not be the only way to understand a layout change. Preserve subview identity with stable IDs and avoid swapping unrelated trees merely to change arrangement.

Test:

- inserting/removing a child during an animated transition;
- focus and text editing while switching layout;
- Reduce Motion and reduced transparency;
- cancellation or replacement of a domain task during layout change;
- Dynamic Type and localization causing a different ViewThatFits branch;
- stale/empty/error states at every arrangement.

## Accessibility and direction

Custom geometry must preserve semantic order and reachable actions. A layout that visually looks correct but requires a person to infer order from position is incomplete. Test VoiceOver order, Voice Control names, Switch Control traversal, keyboard focus, hit regions, large text, increased contrast, reduced transparency, and right-to-left layout.

Use leading/trailing and alignment guides where the platform relationship is semantic. If a custom algorithm has directional placement assumptions, make layout direction a tested input and verify both directions; do not patch RTL with a device-specific offset.

## Target and proof boundary

Compile the custom Layout and all selected modifiers in the named iOS 26 target. Record deployment availability, target membership, resources, and any UIKit/extension host. A preview can exercise proposals and branch fixtures; it cannot prove touch comfort, keyboard avoidance, glass/material rendering, frame time, or every device family.

The proportional route is:

    source state -> layout inputs -> proposal fixtures -> semantic UI test
    -> signed physical-device interaction -> archive/configuration inspection

## Sources

- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [LayoutSubview](https://developer.apple.com/documentation/swiftui/layoutsubview)
- [LayoutSubviews](https://developer.apple.com/documentation/swiftui/layoutsubviews)
- [ProposedViewSize](https://developer.apple.com/documentation/swiftui/proposedviewsize)
- [sizeThatFits(proposal:subviews:cache:)](https://developer.apple.com/documentation/swiftui/layout/sizethatfits%28proposal%3Asubviews%3Acache%3A%29)
- [LayoutValueKey](https://developer.apple.com/documentation/swiftui/layoutvaluekey)
- [layoutValue(key:value:)](https://developer.apple.com/documentation/swiftui/view/layoutvalue%28key%3Avalue%3A%29)
- [LayoutProperties](https://developer.apple.com/documentation/swiftui/layoutproperties)
- [ViewDimensions](https://developer.apple.com/documentation/swiftui/viewdimensions)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [GeometryReader](https://developer.apple.com/documentation/swiftui/geometryreader)
- [containerRelativeFrame(_:alignment:_:)](https://developer.apple.com/documentation/swiftui/view/containerrelativeframe%28_%3Aalignment%3A_%3A%29)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [SafeAreaRegions](https://developer.apple.com/documentation/swiftui/safearearegions)
- [Layout adjustments](https://developer.apple.com/documentation/swiftui/layout-adjustments)
- [Composing custom layouts with SwiftUI](https://developer.apple.com/documentation/swiftui/composing-custom-layouts-with-swiftui)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

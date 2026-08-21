# Glass Containers, Identity, and Morphing

## Why use a container

When multiple views use Liquid Glass, GlassEffectContainer lets SwiftUI render them as a related set. It can improve rendering performance, allow shapes to blend, and enable morphing between related views during transitions.

~~~swift
@Namespace private var glassNamespace

GlassEffectContainer(spacing: 32) {
    HStack(spacing: 32) {
        Image(systemName: "pencil")
            .frame(width: 64, height: 64)
            .glassEffect()
            .glassEffectID("pencil", in: glassNamespace)

        if isExpanded {
            Image(systemName: "eraser")
                .frame(width: 64, height: 64)
                .glassEffect()
                .glassEffectID("eraser", in: glassNamespace)
        }
    }
}
~~~

The IDs are unique within the namespace. The container’s spacing and the actual geometry of the shapes determine when effects blend and morph. If the interior layout is tighter than the container’s spacing, effects can blend at rest; use that deliberately.

## Stable identity

Use a stable semantic ID for the visual effect, not an array index that changes as content moves. glassEffectID and glassEffectTransition influence hierarchy transitions and animations; they do not replace the identity of the domain model or the route.

## Animation recipe

1. Choose a state change that has a clear visual relationship.
2. Place related effects in one GlassEffectContainer.
3. Give each effect a stable ID in a namespace.
4. Keep layout spacing and container spacing intentional.
5. Animate the state mutation with withAnimation.
6. Test reduced motion and VoiceOver; provide the same information without morphing.

## Do not overuse it

Use grouping for a small set of related controls, a compact action cluster, or a meaningful transition. Do not make an entire scroll view one giant glass container; that destroys hierarchy and can increase rendering cost.

## Sources

- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [glassEffectID](https://developer.apple.com/documentation/swiftui/view/glasseffectid%28_%3Ain%3A%29)
- [glassEffectTransition](https://developer.apple.com/documentation/swiftui/view/glasseffecttransition%28_%3A%29)
- [Animations](https://developer.apple.com/documentation/swiftui/animations)

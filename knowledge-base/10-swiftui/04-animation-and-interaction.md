# Animation and Interaction

## Animate the state change

SwiftUI animations work best when they describe a transition from one meaningful state to another. Wrap the state mutation in withAnimation when the entire resulting change should animate, or apply animation with a value when a specific view property should respond to a value.

~~~swift
Button {
    withAnimation(.snappy) {
        isExpanded.toggle()
    }
} label: {
    Label(isExpanded ? "Collapse" : "Expand", systemImage: "chevron.down")
}
~~~

The animation should communicate cause and effect: a panel expands from its trigger, a selection changes in place, or a row moves because it was reordered. Avoid animating unrelated content just because the same state value changed.

## Interactions to design

- press feedback;
- focus and keyboard behavior;
- drag, swipe, and long press where discoverable;
- loading and cancellation;
- disabled and unavailable states;
- success confirmation;
- undo for reversible destructive actions;
- reduced-motion alternative.

## Transitions

Use insertion/removal transitions for content that truly appears or disappears. Use stable identity for repeated content so SwiftUI can understand what changed. If a custom transition needs geometry or matched identity, keep the identity model separate from business IDs and test it with reduced motion enabled.

## Liquid Glass motion

Liquid Glass can morph related shapes when they are grouped in a GlassEffectContainer and associated with stable glassEffectID values. The motion should reinforce the relationship between controls, not become a decorative animation layer over every element.

## Cancellation and gestures

A gesture can start work that outlives the finger movement. Decide whether the work is continuous, debounced, cancellable, or committed only on release. For camera, audio, and model work, stop or cancel the stream when the user leaves the flow.

## Sources

- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [withAnimation](https://developer.apple.com/documentation/swiftui/withanimation%28_%3A_%3A%29)
- [Gestures](https://developer.apple.com/documentation/swiftui/gestures)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)

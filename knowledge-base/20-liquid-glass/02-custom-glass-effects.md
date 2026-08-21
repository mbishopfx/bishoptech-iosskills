# Custom Glass Effects

## When custom glass is justified

Use a custom Liquid Glass effect when a meaningful control or functional element cannot be represented by a standard system component. A custom glass surface should clarify a control’s role, improve focus, or preserve a recognizable relationship during a transition. It should not exist only because a translucent surface looks impressive in a screenshot.

## Core API shape

SwiftUI provides a glassEffect view modifier and a Glass configuration. The default effect is the safest starting point; customize the variant, tint, interactivity, and shape only when the design needs it.

~~~swift
Label("Now playing", systemImage: "waveform")
    .padding(.horizontal, 14)
    .padding(.vertical, 10)
    .glassEffect()
~~~

For a custom shape or interaction, use the documented configuration form and keep the element’s semantic control separate from its surface:

~~~swift
Button("Play") { play() }
    .buttonStyle(.plain)
    .padding(12)
    .glassEffect(.clear.interactive(), in: .capsule)
~~~

The exact appearance is environment-dependent. Test the actual effect on the target OS and accessibility configurations instead of treating a screenshot as a contract.

## Tint and contrast

Use tint sparingly and preserve legible text/icon contrast. A tint should communicate state or category, not become a permanent color wash over every surface. Prefer system colors or carefully paired light/dark variants.

## Shape and containment

Use shapes that are coherent with the surrounding container. Keep enough spacing between independent effects so they do not accidentally merge. If several elements belong to one functional cluster, group them in a GlassEffectContainer and tune the spacing deliberately.

## Interaction

Interactive glass can respond to input, but the interaction must still be apparent to VoiceOver, keyboard, pointer, and reduced-motion users. A glass effect never replaces a button label, value, focus state, or state-change confirmation.

## Sources

- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [glassEffect](https://developer.apple.com/documentation/swiftui/view/glasseffect%28_%3Ain%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

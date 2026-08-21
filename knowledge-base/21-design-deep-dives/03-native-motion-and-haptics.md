# Native Motion and Haptics

## Capability

Motion and haptics should communicate state, causality, and completion. Apple-native polish comes from short, purposeful transitions that preserve orientation—not from animating every property on every frame.

## Motion route

1. Name the state change: insert, remove, expand, select, confirm, or navigate.
2. Choose the smallest transition that makes the change understandable.
3. Animate the state change with `withAnimation` or a value-scoped animation.
4. Keep the content identity stable so SwiftUI can interpolate the right object.
5. Respect Reduce Motion and provide an equivalent non-animated state change.
6. Test interruption, rapid taps, cancellation, and a change that arrives while another animation is running.

Use haptics when the user needs physical confirmation or a meaningful boundary. Standard controls already provide appropriate system feedback in many cases; custom haptics should add meaning rather than duplicate every tap.

## Haptic route

| Need | Route |
| --- | --- |
| Standard control feedback | Native SwiftUI control and system behavior |
| Simple impact/selection/notification feedback | Appropriate system feedback generator |
| A custom timed tactile/audio pattern | Core Haptics and `CHHapticPattern` |
| Game/device feedback | Core Haptics plus the app’s input/audio state |

Core Haptics supports transient and continuous events and can combine haptics with audio. Check engine support, handle interruptions, stop/reset appropriately, and avoid using a continuous pattern as a substitute for clear UI state.

## Motion accessibility

Reduced motion can change or remove animations. Every state must remain understandable without relying on movement, parallax, morphing, or a delayed visual reveal. Do not use a haptic pulse as the only confirmation; pair it with visible and accessible state.

## Example state boundary

`idle -> saving -> saved`

The animation can make the confirmation feel immediate, while the actual persistence result remains authoritative. If saving fails, reverse or replace the visual state honestly instead of leaving a successful-looking animation in place.

## Verification route

- Test normal motion, Reduce Motion, low power, rapid interaction, interruption, and background/foreground.
- Verify animation duration does not delay urgent actions or create accidental double taps.
- Test haptics on supported and unsupported hardware, with silent mode and audio route changes.
- Measure continuous haptic/audio behavior for battery and thermal impact.
- Confirm VoiceOver and switch/keyboard control can complete the same state changes without relying on timing.

## Sources

- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [State-based animation](https://developer.apple.com/documentation/swiftui/animations)
- [Animation](https://developer.apple.com/documentation/swiftui/animation)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEvent](https://developer.apple.com/documentation/corehaptics/chhapticevent)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)

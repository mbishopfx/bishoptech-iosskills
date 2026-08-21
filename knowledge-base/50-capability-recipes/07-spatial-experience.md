# Spatial Experience

## Best fit

Augmented reality, room scanning, 3D visualization, immersive interaction, spatial measurement, or a game that needs a real-time scene.

## Route

SwiftUI shell -> RealityKit/ARKit/RoomPlan -> spatial session state -> domain measurements/anchors -> export/share/persistence

## Build order

1. Define the user outcome without the effect: measure, place, inspect, navigate, or play.
2. Check device support and camera/sensor availability.
3. Request access when the flow begins.
4. Build a stable session state and a non-spatial fallback.
5. Keep world anchors/measurements separate from visual-only entities.
6. Add performance and thermal instrumentation on device.
7. Test interrupted tracking, limited tracking, relaunch, permissions, and captured-output accuracy.

## Guardrails

Do not present a simulated camera or measurement result as physical truth. Label estimates and preserve the source/session context when a user may rely on the result.

## Sources

- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [ARKit](https://developer.apple.com/documentation/arkit)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Apple accessibility](https://developer.apple.com/accessibility/)

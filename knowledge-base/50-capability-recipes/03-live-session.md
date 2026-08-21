# Live Session

## Best fit

Audio players, workouts, timers, navigation, recording, capture, live analysis, or any feature where state changes while the person remains in the flow.

## Route

SwiftUI -> AVFoundation/Core Location/Core Motion/Vision/Speech -> domain session actor/service -> local persistence -> ActivityKit/WidgetKit/notifications

## Build order

1. Define the session lifecycle: idle, preparing, active, paused, interrupted, finishing, complete, failed.
2. Request permissions immediately before the live feature.
3. Keep capture/measurement and UI state separate.
4. Make the session cancellable and resilient to interruptions/background transitions.
5. Persist checkpoints so a termination does not corrupt the record.
6. Add a Live Activity only if the status is useful outside the app.
7. Test thermal, battery, audio route, location, phone lock, and interruption behavior on device.

## Guardrails

Do not claim background continuity when the system does not guarantee it. Do not make a Live Activity the only source of session truth. Keep privacy-sensitive streams local or explicitly disclosed.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Core Motion](https://developer.apple.com/documentation/coremotion)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

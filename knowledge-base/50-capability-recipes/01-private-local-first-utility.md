# Private Local-First Utility

## Best fit

Account-free tools where a person creates, edits, searches, and exports personal records on one device.

## Route

SwiftUI -> Observation -> SwiftData -> protected files -> App Intents/WidgetKit -> optional CloudKit

## Build order

1. Model the core record and user-visible state.
2. Build a deterministic create/edit/review flow.
3. Persist locally and test relaunch, deletion, migration, and empty states.
4. Add file import/export for large or portable content.
5. Add AppEntity and AppIntent only for the actions people need outside the app.
6. Add widgets or notifications for useful reminders, not engagement noise.
7. Decide whether multi-device sync is genuinely needed; if yes, define CloudKit conflict and account behavior.

## Guardrails

Keep large attachments outside SwiftData rows. Keep AI output as a reviewable draft. Do not add an account or backend merely because it is familiar.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Observation](https://developer.apple.com/documentation/observation)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)

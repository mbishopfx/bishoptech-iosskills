# System-Surface-First Feature

## Best fit

One action or status that is useful from Siri, Shortcuts, Spotlight, a widget, a control, a Live Activity, a notification, or visual intelligence.

## Route

domain use case -> AppIntent/AppEntity/EntityQuery -> App Shortcut/WidgetKit/ActivityKit/Spotlight -> typed deep link back into SwiftUI

## Build order

1. Implement and test the visible in-app use case.
2. Define a stable, privacy-safe AppEntity if the action needs custom data.
3. Build the AppIntent with clear title, description, parameters, and authorization.
4. Add the smallest appropriate system surface.
5. Make background/extension execution safe without in-memory app state.
6. Route the result to a validated destination.
7. Test invocation from each system surface, including locked or unavailable contexts where supported.

## Guardrails

Do not expose every database field to the system. Do not create a shortcut that only opens the app if a direct Link is clearer. Do not perform an irreversible action without a confirmation model appropriate to the surface.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)

# App Intents and System Routes

## Make the capability modular

App Intents express actions and content so the system can expose them through Siri, Apple Intelligence, Shortcuts, Spotlight, widgets, controls, Live Activities, visual intelligence, and supported hardware interactions. Build the app action once as a domain use case, then expose it through the appropriate system surface.

## Core pieces

- AppIntent: an app-specific action with metadata and perform behavior.
- AppEntity: a custom type the system can discover and pass as a parameter.
- EntityQuery: lookup logic for resolving entities by identifier or search.
- AppShortcut: a polished shortcut with title, phrase, image, and optional preconfigured parameters.
- IntentDescription and parameter metadata: human-readable information that improves discovery and resolution.

## Entity boundary

Expose only the subset of app data that people plausibly use outside the app. Keep AppEntity types small and stable. A shadow intent model can be safer than exposing a full SwiftData model, especially when the full record contains private fields.

## System-surface routes

| Surface | Primary route | Important constraint |
| --- | --- | --- |
| Siri/Shortcuts | AppIntent, AppShortcut | Resolve parameters and provide clear metadata. |
| Spotlight | AppEntity, indexing/donation | Stable identifiers and display representations. |
| Widget button/toggle | AppIntent | Widget runs in a separate process; use a reusable intent. |
| Live Activity action | LiveActivityIntent | Keep actions fast, bounded, and tied to the visible activity. |
| Control Center/control | WidgetKit plus App Intents | Provide a focused action, not a miniature app. |
| Visual intelligence | App Intents plus semantic content | Return matching content or an action for the captured context. |
| Action button | App Shortcut/system integration | Make the invoked action safe and immediately understandable. |

## Deep links

System surfaces should route to explicit app destinations. A widget or App Intent should be able to identify the target record, invoke the domain action, and optionally open the relevant screen. Do not rebuild the action logic inside a widget extension.

## Background and process boundaries

Widget extensions and other system surfaces may run separately from the main app. Do not assume in-memory app state exists. Persist the minimum shared state, handle unavailable stores, and make intent execution safe when the app UI is not present.

## Current-system caveat

Apple’s App Intents documentation describes some Siri personal-context and onscreen-awareness capabilities as in development or future software. Treat those features as availability-dependent and keep the app useful through the explicit Shortcuts/Spotlight/App Intent path.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Widgets, Live Activities, and Controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)

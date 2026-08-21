# Journaling Suggestions and Personal Context

Journaling Suggestions is an Apple system picker for creative-writing apps. It shows recent personal events such as places, people, photos, workouts, songs, media, reflections, or event posters. A person chooses what to share; only then does the app receive a high-level JournalingSuggestion value.

This is a privacy-sensitive personal-context route, not a background feed of someone’s life. Apple’s current documentation says the app does not need additional authorization to present the picker because the app cannot access suggestion details until the person selects and shares them. The app still needs the com.apple.developer.journal.allow entitlement and must explain what the picker will show.

## Outcome and boundary

| Product outcome | Journaling Suggestions fit | Keep separate |
| --- | --- | --- |
| Give a person ideas for a journal entry | Strong fit | App’s writing/storage workflow |
| Let someone choose a photo/place/workout to reflect on | Picker can return selected high-level content | Photo library, HealthKit, location, and workout authorization |
| Automatically collect a person’s life events in the background | Not the documented model | Explicit user selection and other authorized frameworks |
| Summarize selected context with on-device AI | Possible after selection as a separate app feature | Foundation Models availability, review, and claim safety |
| Send journaling reminders from Apple’s system notifications | Supported with notification URL target configuration | Notification settings, preferred app choice, and picker presentation |
| Diagnose mood or improve mental health | Not a supported claim | Medical/mental-health product review and guardrails |

The route is:

~~~text
app writing goal -> system picker -> person selects moment
-> JournalingSuggestion high-level result -> optional review/AI -> app-owned entry
~~~

The picker selection is a consent boundary. Do not bypass it with private APIs, hidden sensors, or a background import.

## Entitlement and target configuration

The entitlement key is com.apple.developer.journal.allow. Apple’s presentation documentation says the picker fails to present without it. Add the Journaling Suggestions capability to the target in Xcode and inspect the signed archive.

For system notification integration, configure the documented JSNotificationURLFormat target property with a universal-link format containing the journaling suggestion identifier placeholder. This lets the system offer the app in Settings and pass a selected notification moment through the app’s universal-link route.

Keep two target gates separate:

| Gate | Enables |
| --- | --- |
| Journaling Suggestions entitlement | Picker presentation and selected-content route |
| JSNotificationURLFormat plus universal-link routing | System notification launch and prepopulated picker route |

Do not add a target property and claim that system notifications will arrive. The person must enable Journaling Suggestions/notifications and may need to choose the preferred app in Settings.

## System picker

JournalingSuggestionsPicker is a SwiftUI view that displays the system’s recent-event suggestions. The app provides a button title that sets expectations for the person:

- “Choose a moment to write about”
- “Find a recent moment”
- “Add a memory to this entry”

The title should not promise that the picker contains a specific photo, place, person, or event. The system chooses what is available.

When a person chooses a suggestion, the picker’s completion handler supplies JournalingSuggestion. The app can inspect:

- title;
- optional date interval;
- items;
- type-specific content through content(forType:).

The app receives high-level details for the selected suggestion, not unrestricted access to every source system. Keep the selected result scoped to the current writing task.

## Suggestion content types

The current documentation lists content types including:

- Contact;
- EventPoster;
- GenericMedia;
- LivePhoto;
- Location;
- LocationGroup;
- MotionActivity;
- Photo;
- Podcast;
- Reflection;
- Song;
- StateOfMind;
- Video;
- Workout;
- WorkoutGroup.

Each type has a different data boundary. A location suggestion is not a right to continuously track location. A workout suggestion is not a replacement for HealthKit authorization. A Photo or LivePhoto result is not unrestricted library access. A StateOfMind result should not be presented as a diagnosis or treatment signal.

Use the content(forType:) async API only for the type the person selected and the app’s current workflow. Show a “not available” state for content that is absent, unsupported, or intentionally excluded.

## Privacy model

The picker provides a person-controlled disclosure step:

1. The app explains why it wants a personal moment.
2. The system presents the picker.
3. The person selects a suggestion.
4. The app receives high-level details.
5. The app lets the person review, edit, keep, or discard the result.

Do not:

- call the picker on launch without context;
- imply that the app has already seen the person’s history;
- store every field from JournalingSuggestion by default;
- upload the result to a server without an explicit product/privacy decision;
- feed selected photos, contacts, locations, workouts, or state-of-mind details into an external AI service by default;
- use a selected moment to infer identity, health, relationships, or behavior beyond the person’s stated writing task.

Keep the selection’s provenance with the app entry: selected time, source type, user edits, and retention policy. Do not retain a raw system object when a user-approved, redacted entry is sufficient.

## Personal-context data map

| Selected content | Safe product framing | Guardrail |
| --- | --- | --- |
| Photo/LivePhoto | Add a selected memory to the entry | Do not claim full photo-library access |
| Location/LocationGroup | Reflect on a selected place or trip | Avoid exact address exposure by default |
| Contact | Reflect on a selected connection | Do not infer relationship or identity |
| Workout/WorkoutGroup | Write about a selected activity | Not a health diagnosis or coaching proof |
| StateOfMind | Person-selected reflection context | Do not make clinical or treatment claims |
| Song/Podcast/GenericMedia | Add media context to writing | Respect title/artist/app privacy and licensing |
| EventPoster | Reflect on an attended/planned event | Do not infer attendance beyond the selected suggestion |
| MotionActivity | Add a selected activity context | Do not infer continuous movement or safety |

The design should let a person remove the context before saving the entry.

## Optional system notifications

Journaling Suggestions can provide system notifications that prompt people to reflect. The current documentation describes:

- JournalingSuggestionsConfiguration;
- notificationSchedule values smart, custom, and off;
- Settings-owned notification preferences;
- a preferred journal app selection when multiple apps support the route;
- JournalingSuggestionPresentationToken;
- a URL containing the suggestion identifier;
- picker presentation prepopulated from the token.

The off state can mean several things: the feature is disabled, the app is not preferred, notifications are off, or URL/target configuration is incomplete. Do not map off to “the user declined this app.”

System notification flow:

~~~text
Settings enrollment/notification choice
-> system notification
-> user taps
-> universal-link URL
-> parse suggestion identifier
-> JournalingSuggestionPresentationToken
-> present picker
-> person chooses content
-> app receives JournalingSuggestion
~~~

Handle a general reminder with no identifier separately from a moment-specific notification. A URL with an identifier is a request to preload the picker, not the content itself.

## App-owned writing and AI

After selection, the app can build a reviewable journal-entry draft:

~~~text
selected JournalingSuggestion
-> redacted context model
-> optional on-device AI draft
-> person edits/reviews
-> save app-owned entry
~~~

Foundation Models or another on-device route may summarize or draft prose from the selected high-level context. Keep source context visible and let the person correct the wording. The model must not:

- invent a memory;
- claim a person felt a specific emotion;
- turn StateOfMind into a diagnosis;
- infer an unselected contact relationship;
- create a private entry without review;
- upload personal context to a server;
- treat a system suggestion as a verified fact beyond its documented fields.

When the model is unavailable, use a deterministic template:

> You selected a moment titled [title] from [date range]. Add what you remember.

## Lifecycle and cancellation

The picker is system UI. The app should handle:

- presentation denied or unavailable;
- person dismisses the picker;
- person selects a suggestion;
- completion returns no supported content;
- the app backgrounds while the picker is shown;
- the notification URL arrives while the app is cold;
- the selected message/entry is deleted before completion;
- the person changes the preferred journal app;
- system notification settings change.

Store the pending entry ID and notification token only as needed. Clear a stale token after completion, cancellation, or expiration. Do not persist the raw universal-link URL as personal history.

## Platform and availability

Apple’s current updates page says Journaling Suggestions supports iPadOS and that suggestions generated on iPhone sync over iCloud to iPad. Verify the exact selected SDK availability and target behavior, especially for newer content types and notification routes.

The primary picker is a system surface with device/account/settings dependencies. A SwiftUI preview or simulator cannot prove that a person’s real suggestions appear, that iCloud-synced suggestions are available, or that Settings selects the app for notifications.

## Liquid Glass and native design

Use Liquid Glass for the app-owned “new entry” toolbar, selected-context summary, or review action group. Let JournalingSuggestionsPicker remain system-owned.

Good hierarchy:

- journal entry title and editor;
- selected-context summary;
- “Choose another moment” or “Remove context”;
- optional AI draft review;
- save/discard.

Avoid:

- a faux system picker;
- a background mosaic of private photos;
- a “life feed” that implies continuous access;
- a glowing AI card that hides the selected source;
- an automatic draft that appears as if the person wrote it.

## Proof boundary

| Claim | Required evidence |
| --- | --- |
| Picker route configured | Target capability, signed entitlement, compile |
| Picker presents | Physical-device run with configured target |
| Selection returns high-level content | Person selects a real/test suggestion and completion receives result |
| Type content is available | Selected type and content(forType:) result recorded |
| No additional authorization before selection | Documented/system flow plus no preselection data access |
| Notification route works | Settings enrollment, target property, universal-link launch, token, picker |
| AI is local | Model/device trace, redacted input audit, no external upload |
| Entry is user-approved | Review/edit/save evidence |
| Health/privacy claim is safe | Copy and policy review; no diagnosis/treatment guarantee |
| Release is eligible | Final entitlement, universal-link association, archive, system/device proof |

## Sources

- [Journaling Suggestions](https://developer.apple.com/documentation/journalingsuggestions)
- [Presenting the suggestions picker and processing a selection](https://developer.apple.com/documentation/journalingsuggestions/presenting-the-suggestions-picker-and-processing-a-selection)
- [JournalingSuggestion](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestion)
- [JournalingSuggestionsPicker](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionspicker)
- [JournalingSuggestionAsset](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionasset)
- [Receiving journaling suggestions system notifications](https://developer.apple.com/documentation/journalingsuggestions/receiving-journaling-suggestions-from-system-notifications)
- [JournalingSuggestionPresentationToken](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionpresentationtoken)
- [JournalingSuggestionsConfiguration](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionsconfiguration)
- [Journaling Suggestions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.journal.allow)
- [Journaling Suggestions updates](https://developer.apple.com/documentation/updates/journalingsuggestions)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

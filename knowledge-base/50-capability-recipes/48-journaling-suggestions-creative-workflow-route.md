# Journaling Suggestions Creative-Workflow Route

Use this route for a journaling or personal-writing app that wants to let a person choose recent life context from Apple’s system picker. Treat the selection as user-approved source material for a writing workflow, not as an automatic personal-data feed.

## Outcome contract

The person can:

1. understand what the picker may show;
2. open the system picker from a meaningful writing task;
3. choose a moment;
4. review the high-level result;
5. remove or edit the selected context;
6. optionally review an on-device AI draft;
7. save a user-approved journal entry;
8. open from a system journaling notification when configured;
9. write normally when the route is unavailable.

## Route selector

| Need | Route |
| --- | --- |
| Choose recent personal events for writing | Journaling Suggestions |
| Read health/workout data continuously | HealthKit with separate authorization |
| Read photo library content directly | PhotosUI/PhotoKit with separate permissions |
| Track location | Core Location with separate authorization |
| Draft or summarize selected context | Foundation Models or another app-owned AI route |
| Receive journaling reminder notification | Journaling Suggestions notification URL route |
| Execute a system action | App Intents or the destination framework |

Do not substitute Journaling Suggestions for the underlying framework when the product needs ongoing data.

## Capability and target gate

Record:

- app target and bundle ID;
- iOS/iPadOS deployment target;
- Journaling Suggestions entitlement;
- signed entitlement inspection;
- JSNotificationURLFormat if notification support is intended;
- universal links and associated domains;
- selected-content retention policy;
- AI draft policy;
- device/account/Settings test state;
- fallback writing route.

The picker requires com.apple.developer.journal.allow. The notification route additionally depends on the documented target property, universal-link handling, enrollment, notification settings, and preferred-app selection.

## Ownership graph

~~~text
JournalEditor
  -> PickerCoordinator
      -> JournalingSuggestionsPicker
      -> JournalingSuggestion
      -> selected-content projection
  -> optional on-device AI draft
  -> user review/edit
  -> SwiftData/local entry
  -> optional sync/export
~~~

| Layer | Owns | Does not own |
| --- | --- | --- |
| Journal editor | Writing, edit, save, delete | Hidden personal context |
| PickerCoordinator | Presentation, cancellation, completion | Authorization to private source data |
| System picker | Suggestion list and person-controlled selection | App entry truth |
| Content projector | Selected high-level fields and redaction | Full source framework access |
| AI draft layer | Optional editable text | Memory truth, diagnosis, or automatic save |
| Notification router | URL/token parsing and deep link state | Notification schedule choice |
| Persistence | Approved entry and provenance | Raw system picker database |

## Picker route

1. Place a clear button in the context of a new entry.
2. Explain the selection boundary.
3. Present JournalingSuggestionsPicker.
4. Handle dismissal.
5. Receive JournalingSuggestion in completion.
6. Project only the selected content types needed.
7. Display provenance and editable details.
8. Let the person remove context before saving.

The system picker is a separate process/surface. Keep a pending entry ID so the app can restore the writing context if the app is backgrounded.

## Selected-content route

After completion:

1. read title/date when useful;
2. call content(forType:) only for the selected type(s) the feature supports;
3. normalize into a redacted app-owned model;
4. discard unsupported/raw fields;
5. allow edit/remove;
6. save only after the person approves.

An app-owned projection may look like:

~~~text
SelectedMoment:
  source: journalingSuggestions
  title
  dateInterval
  selectedTypes
  redactedPreview
  userEdited
  savedAt
~~~

Do not store the complete JournalingSuggestion or every content item by default.

## Content policy

Create an explicit allowlist:

| Type | Default app action |
| --- | --- |
| Photo/LivePhoto | Show a selected preview, allow removal |
| Location/LocationGroup | Store a coarse label unless exact data is needed |
| Contact | Show name only after selection; avoid relationship inference |
| Workout/MotionActivity | Use as a writing prompt, not a health conclusion |
| StateOfMind | Keep reflective and optional; no medical claims |
| Song/Podcast/GenericMedia | Store title/artist/date only when needed |
| EventPoster | Keep event context and provenance |

The allowlist should be versioned so a future SDK content type does not become automatic data collection.

## Notification route

If implementing system notifications:

1. enable Journaling Suggestions and notifications in testing;
2. add JSNotificationURLFormat with the documented placeholder;
3. configure associated domains/universal links;
4. parse the incoming URL in onOpenURL;
5. extract a valid suggestion identifier;
6. create JournalingSuggestionPresentationToken;
7. present the picker prepopulated with that token;
8. handle a general reminder with no identifier;
9. read JournalingSuggestionsConfiguration for display-only schedule context.

The URL is a routing token, not personal content. Validate scheme/host/path and never log the full URL with a private identifier.

## Notification state

~~~text
notification:
  notConfigured
  settingsRequired
  preferredAppUnknown
  smart
  custom
  off
  tappedGeneralReminder
  tappedMomentReminder
  invalidURL
~~~

The off state is ambiguous according to Apple’s documentation. Explain that Settings or app preference may need attention instead of telling the person the feature was rejected.

## AI route

The AI input is a redacted selected-context projection:

~~~text
JournalDraftInput:
  userPrompt
  selectedMomentTitle
  selectedDateRange
  selectedContentSummary
  userProvidedWords
  excludedClaims
~~~

The model returns editable prose:

~~~text
JournalDraft:
  text
  sourceSummary
  uncertaintyNotes
  requiresReview: true
~~~

Never feed full personal media or precise location to an external model without an explicit, separate product decision. Do not infer emotion, diagnosis, relationships, or intent from a selected suggestion.

## SwiftUI and Liquid Glass

Use system picker presentation for selection. Use native SwiftUI and Liquid Glass for the app-owned review:

- compact selected-moment card;
- “Remove context” action;
- “Draft from this moment” action;
- editable TextEditor;
- Save/Discard.

The selected moment should be visually subordinate to the person’s writing. Do not present generated text as if it came from the person.

## Fallbacks

| Condition | Fallback |
| --- | --- |
| Entitlement missing | Manual writing flow |
| Picker unavailable | Manual prompt and optional local attachment |
| Person dismisses | Continue blank entry |
| No supported content | Keep title/date or discard |
| Notification settings off | Manual reminder/entry route if product supports it |
| Invalid URL/token | Open normal new-entry route |
| AI unavailable | Fixed prompt/template |
| Health-sensitive content excluded | Show safe generic context or remove |

## Minimum proof sequence

1. Compile picker target with signed entitlement.
2. Present picker from a meaningful entry flow.
3. Test dismissal and selection.
4. Test content(forType:) for supported types.
5. Test redaction/edit/remove/save.
6. Test notification URL with and without identifier.
7. Test Settings schedule states.
8. Test cold launch and background return.
9. Test AI unavailable, sensitive content, and no external upload.
10. Test VoiceOver, Dynamic Type, reduced effects, RTL, and iPad.

## Sources

- [Journaling Suggestions](https://developer.apple.com/documentation/journalingsuggestions)
- [Presenting the suggestions picker and processing a selection](https://developer.apple.com/documentation/journalingsuggestions/presenting-the-suggestions-picker-and-processing-a-selection)
- [JournalingSuggestion](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestion)
- [JournalingSuggestionsPicker](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionspicker)
- [Receiving journaling suggestions system notifications](https://developer.apple.com/documentation/journalingsuggestions/receiving-journaling-suggestions-from-system-notifications)
- [JournalingSuggestionPresentationToken](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionpresentationtoken)
- [JournalingSuggestionsConfiguration](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionsconfiguration)
- [Journaling Suggestions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.journal.allow)
- [Journaling Suggestions updates](https://developer.apple.com/documentation/updates/journalingsuggestions)
- [Universal links](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

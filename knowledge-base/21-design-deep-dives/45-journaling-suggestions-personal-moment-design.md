# Journaling Suggestions Personal-Moment Design

Journaling Suggestions is a consent-led writing entry point. The design should make a personal moment feel invited, chosen, and editable—not silently harvested or transformed into an authoritative story.

The native design loop is:

~~~text
writing goal -> explain the picker -> system picker
-> selected moment summary -> edit/review -> save or discard
~~~

## Entry point copy

Use a clear button title:

- Choose a moment to write about
- Find a recent moment
- Add a memory to this entry

Follow it with one sentence:

> Apple will show recent moments you can choose to share with this entry.

Avoid:

- “Scan my life”
- “Let AI find your memories”
- “See everything that happened”
- “Improve your mental health”
- “We already know what you need to write”

The person should understand the system picker and the selection boundary before tapping.

## New-entry composition

A native entry screen can use:

1. navigation title and save action;
2. editor or prompt;
3. selected-context summary;
4. choose another moment/remove context;
5. optional AI draft review;
6. attachment/source details.

Do not show a grid of personal moments before the picker. The app does not have access to those details until selection.

## Selection states

| State | User-facing label | Primary action |
| --- | --- | --- |
| pickerReady | Ready to choose a moment | Open picker |
| pickerPresented | Choose a moment | Use system picker |
| dismissed | No moment selected | Continue writing |
| selected | Moment selected | Review context |
| partial | Some details are available | Edit or continue |
| unsupportedContent | This detail is unavailable | Remove or continue |
| review | Review before saving | Edit/save |
| saved | Added to this entry | Continue writing |
| discarded | Context removed | Choose another or write manually |
| notificationLaunch | Opened from a journaling reminder | Review preselected moment |
| settingsRequired | Notifications/settings need attention | Open Settings |

Do not turn “dismissed” into a failed or guilt-inducing state.

## Selected-context card

Show only what helps the person write:

- suggestion title;
- approximate date/range;
- selected content type;
- one or two approved previews;
- “From Journaling Suggestions” provenance;
- edit/remove action.

Use a neutral label such as “Selected moment.” Do not present it as a verified narrative. A title from the system is context, not a complete account of what occurred.

## Content-specific design

| Content | Design |
| --- | --- |
| Photo/LivePhoto | Show selected asset and let the person remove it |
| Location | Show a coarse place label or map context only when useful |
| LocationGroup | Summarize the group without exposing a full route by default |
| Contact | Show the selected name only with the person’s clear intent |
| Workout | Show activity/date context without health conclusions |
| StateOfMind | Use reflective, non-clinical language and optional omission |
| Song/Podcast/Media | Show title/artist/source only when it helps the entry |
| EventPoster | Show the event context, not an inferred attendance claim |
| MotionActivity | Use “selected activity” wording, not continuous movement |

Every selected item should be removable before saving.

## Liquid Glass restraint

Use Liquid Glass for:

- the new-entry toolbar;
- a compact selected-moment action group;
- an optional AI review action;
- a context menu or bottom action bar.

Let JournalingSuggestionsPicker remain the system surface. Do not recreate its visual grid, blur, or content treatment in app-owned UI. Do not layer an animated glass “memory cloud” behind private selected content.

With Reduce Transparency, use an opaque card. With Reduce Motion, selected-context appearance should still be clear from text and focus.

## AI draft review

An AI draft should be visually subordinate to the person’s own writing:

| Element | Copy |
| --- | --- |
| Provenance | Draft based on the moment you selected |
| Editable result | Suggested opening |
| Missing detail | Add what you remember |
| Action | Insert draft / Keep writing |
| Safeguard | Review before saving |

Do not present a generated paragraph as a memory. Avoid “you felt,” “you were happiest,” or other inferred emotional claims unless the person wrote them. State-of-mind content is especially sensitive and must not be turned into diagnosis or treatment language.

## Notification entry

When opened from a journaling suggestion notification:

- show that the entry came from a system reminder;
- show the selected moment if the notification contained an identifier;
- let the person choose what to share in the picker;
- handle a general reminder with no preselected moment;
- do not expose the URL/token as user-facing content;
- preserve the person’s ability to dismiss and write later.

The app can show the current notification schedule from JournalingSuggestionsConfiguration, but Settings owns the actual preference. Use “Notifications are off” or “Schedule is controlled in Settings” instead of treating off as a personal refusal.

## Accessibility

Test the full route with:

- VoiceOver from picker button through selected-context review;
- Dynamic Type in the editor and selected-context card;
- Voice Control for “Choose a moment,” “Remove context,” and “Save”;
- Switch Control;
- Reduce Motion and Reduce Transparency;
- right-to-left layout;
- keyboard/pointer on iPad;
- long localized titles and dates.

When the system picker returns, place focus on the selected-context summary or a concise result announcement. Do not require the person to navigate through a decorative preview before reaching the editor.

## Empty and denial states

Use gentle, useful copy:

> No moment selected. You can keep writing or choose one later.

If the picker cannot open:

> Journaling Suggestions isn’t available in this build or setting. You can write without a selected moment.

If a selected type has no usable content:

> Some details from this moment aren’t available here. You can keep the title or remove the context.

Never imply that the person’s life contains no meaningful moments because the picker is empty.

## Privacy and deletion design

Provide:

- remove selected context;
- delete the saved entry;
- clear attached previews;
- a privacy details route;
- source/provenance label;
- a server-sync explanation if the app syncs entries.

Do not overstate Apple’s picker privacy as a guarantee about the app’s own storage, analytics, backups, or AI service.

## Visual QA

Capture:

- clean new entry;
- picker presented;
- no selection;
- selected photo/place/workout/media;
- state-of-mind selection with non-clinical copy;
- partial/unsupported content;
- AI draft review;
- notification deep link with and without identifier;
- Settings schedule states;
- VoiceOver, Dynamic Type, reduced effects, RTL, iPad;
- delete/remove context.

The writing experience must remain valuable without any Journaling Suggestions result.

## Sources

- [Journaling Suggestions](https://developer.apple.com/documentation/journalingsuggestions)
- [Presenting the suggestions picker and processing a selection](https://developer.apple.com/documentation/journalingsuggestions/presenting-the-suggestions-picker-and-processing-a-selection)
- [JournalingSuggestion](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestion)
- [Receiving journaling suggestions system notifications](https://developer.apple.com/documentation/journalingsuggestions/receiving-journaling-suggestions-from-system-notifications)
- [JournalingSuggestionsConfiguration](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionsconfiguration)
- [Journaling Suggestions updates](https://developer.apple.com/documentation/updates/journalingsuggestions)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Onboarding](https://developer.apple.com/design/human-interface-guidelines/onboarding)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

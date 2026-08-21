# SwiftUI EventKit and EventKitUI calendar/reminders review design

This design review defines an Apple-native calendar/reminder surface around EventKit and EventKitUI. The goal is not to recreate Apple Calendar or Reminders feature-for-feature. The goal is to make the person’s intended action obvious, request only the access required, preserve system ownership of protected records, and make every state legible when permission, synchronization, or a model proposal is unavailable.

## Design brief

| Decision | Recommendation |
| --- | --- |
| Primary user outcome | Create, review, or reconcile a calendar event or reminder with a clear system-record receipt. |
| Primary surface | SwiftUI navigation, list/form, search, date controls, and a single purpose-first add/review action. |
| System handoff | Use `EKEventEditViewController`, `EKEventViewController`, or `EKCalendarChooser` when the system UI expresses the workflow better than a custom editor. |
| Liquid Glass role | A restrained functional group for the add/review action, filter scope, or compact status—not a translucent treatment over every dense record row. |
| AI role | Propose a title, time window, recurrence, or reminder decomposition from minimized user-authored inputs; never silently mutate EventKit. |
| Fallback | A plain SwiftUI form and deterministic date/recurrence picker remain usable with denied access, unavailable Foundation Models, reduced transparency, or no glass support. |

The design contract is:

```text
purpose -> access explanation -> scope -> draft/review -> explicit commit -> reconciled record
```

## Start with action, not permission

The first screen should answer “What can I do here?” before asking for a protected resource. A blank permission gate that says “Calendar access required” forces the person to understand the implementation instead of the value.

Use an action-specific explanation:

- “Show my upcoming events” requires full event access because the app must read Calendar data.
- “Add this meeting to Calendar” can use the EventKitUI editor or write-only event access, depending on the workflow.
- “Build a reminder list from my plan” requires full reminder access if the app will read or reconcile Reminders.

After the explanation, provide one primary button and a secondary no-permission path such as “Keep as draft,” “Export,” or “Use manual entry.” The secondary path should not pretend to be synchronized with Calendar or Reminders.

## Recommended screen composition

```text
NavigationStack
  toolbar: scope/filter + one primary add/review action
  permission or system-state card when needed
  date/range header or reminder-list scope
  grouped records
    semantic title
    date/due-date and time-zone context
    calendar/list label
    recurrence/alarm/completion status
    stale/conflict badge when applicable
  optional proposal card
    source inputs -> proposed values -> Edit / Accept / Dismiss
  bottom status: saved, changed elsewhere, denied, or retry
```

The design should remain useful when records are empty, the date range is too narrow, or the person has only write-only access. Empty results must not look identical to denied access.

## Calendar event list

Use sections based on a meaningful time grouping—Today, Tomorrow, or a bounded date range—not a decorative glass grid. Rows should expose:

- event title as the primary label;
- start/end or all-day state;
- calendar title and color as supporting context, never the only distinction;
- recurrence and alarm indicators with text equivalents;
- invitation/attendee or location information only when it is necessary for the task; and
- an explicit stale or modified-elsewhere state when the visible projection needs refetching.

Tap behavior should be semantic: open a detail route or EventKitUI view, not a gesture-only hidden action. Swipe actions need visible alternatives in the detail screen and on keyboard/controller input.

For an app that only adds an event, show the app-owned draft until the system editor returns. Do not insert the draft into a “Calendar” list as if it were already committed.

## Reminder list

Reminders need a different visual model from timed events:

```text
list / calendar scope
  incomplete reminder title
  optional start and due date components
  priority / notes / recurrence summary
  completion control with an accessible label
  local draft or saving state
```

Avoid converting a reminder’s due date into a generic timestamp that hides all-day or floating-time meaning. Show “Due today” or a localized date when the exact time is not present. For recurring reminders, explain the product behavior around the first incomplete occurrence rather than rendering a fabricated infinite series.

Completion must not be color-only. Pair a checkmark or tint with VoiceOver text, an accessibility value, and a visible transition that respects Reduce Motion.

## EventKitUI handoff design

When using `EKEventEditViewController`:

1. show the reason for the handoff in the preceding SwiftUI screen;
2. pass a minimal prefilled event or `nil` for a new event;
3. allow the system editor to own calendar selection and event editing;
4. map `.saved`, `.deleted`, and `.canceled` into app state;
5. dismiss the controller from the delegate boundary; and
6. refetch the relevant record or range before showing a “synced” result.

When using `EKEventViewController`, make `allowsEditing` reflect the app’s actual intent and the record’s capability. A view controller can display an event even when the app should not claim direct read/write authority over the store.

When using `EKCalendarChooser`, label the selection action with the entity type—“Choose event calendars” or “Choose reminder lists”—and display the resulting selection in the app only after the delegate reports it. A read-only calendar should be clearly distinguished from a writable calendar without relying solely on color.

## Liquid Glass rules for calendar/reminder surfaces

Liquid Glass is a material and interaction layer, not the information architecture. Apply it to a compact functional group:

- add/review controls in a toolbar or safe-area bar;
- a small filter/scope cluster;
- a proposal action group with Accept, Edit, and Dismiss; or
- a status capsule for saving or change reconciliation.

Keep dense list rows on a legible surface. Do not stack nested glass effects on every row or make the record’s title compete with reflections and translucency. The semantic hierarchy should remain understandable when glass is removed, transparency is reduced, or the target SDK falls back to a system material.

For morphing actions, preserve identity: an add button can transition into a review card only when the action remains recognizable and the accepted values remain visible. Avoid morphing a destructive delete action into a visually similar save action.

The following states need explicit glass and non-glass treatments:

| State | Glass treatment | Fallback |
| --- | --- | --- |
| Ready | Compact add/review group. | Standard bordered or filled buttons. |
| Draft | Subtle grouping around fields; keep text opaque. | Form sections with standard background. |
| Saving | Progress/status within the action group; prevent duplicate commits. | Text plus ProgressView. |
| Changed elsewhere | Use an alert/status card with clear copy. | Full-width warning row. |
| Denied/restricted | Avoid decorative material that hides the explanation. | Plain permission card and Settings action. |
| AI proposal | Glass can group actions, but values and source constraints must remain text-first. | Standard confirmation card. |

## Accessibility and alternate input

Build the calendar/reminder action as a task, not as a screenshot. Verify:

- VoiceOver reads title, date/due state, calendar/list, recurrence, alarm, completion, and stale/error state in a sensible order;
- the add/review action has a meaningful label and hint;
- completion controls expose an accessibility value and action, not just a color change;
- Dynamic Type does not truncate the date/time or hide the primary action;
- Reduce Motion replaces a morphing glass transition with a simple state change;
- Reduce Transparency and Increase Contrast keep rows and cards legible;
- keyboard focus and pointer hover work on iPad and Mac Catalyst where supported;
- swipe actions have button and keyboard alternatives; and
- localized long titles, RTL layouts, 12/24-hour time, first-day-of-week differences, and time-zone changes do not invalidate the hierarchy.

Use accessibility identifiers for UI tests, but do not confuse identifiers with user-facing labels or EventKit record identifiers.

## AI proposal card

The AI surface should look like a draft assistant, not an autonomous calendar agent:

```text
“From your note, I found a possible 45-minute meeting next Tuesday.”

Suggested
  title       Project review
  window      Tue 2:00–2:45 PM (America/Chicago)
  recurrence  none
  reminder    15 minutes before

[Edit] [Add to Calendar] [Dismiss]
```

Label which values came from the person and which were inferred. If conflict checking used app-owned availability windows, say so; if the app did not read Calendar, do not imply that the slot is free. The Accept action must pass through deterministic validation and then either the EventKitUI editor or an explicit direct EventKit save confirmation.

Never put a raw event title, attendee list, private location, or reminder note into an AI prompt merely to make the card sound personal. If the feature has a valid reason to use private data, minimize it, disclose it, and keep the raw record out of logs.

## Design review checklist

- [ ] The first screen communicates the user outcome before requesting access.
- [ ] The access explanation names Calendar versus Reminders and full versus write-only behavior.
- [ ] Write-only event mode never renders a fake readable calendar list.
- [ ] Draft, saving, saved, changed-elsewhere, denied, restricted, and empty states are distinct.
- [ ] EventKitUI is used where system ownership improves trust and reduces custom editing surface.
- [ ] Direct saves require an explicit user command and show error/retry behavior.
- [ ] Recurrence span, all-day/floating date, reminder date components, and alarms are visible and reviewable.
- [ ] Calendar/list color is supplementary, never the only semantic signal.
- [ ] Liquid Glass is limited to functional groups and has a legible fallback.
- [ ] VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, Increase Contrast, keyboard, pointer, and RTL paths are tested.
- [ ] AI proposals expose source constraints and remain editable, validated, and dismissible.
- [ ] A successful UI dismissal or `save` call is not shown as synchronized until refetch/reconciliation completes.

## Sources

- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [Creating events and reminders](https://developer.apple.com/documentation/eventkit/creating-events-and-reminders)
- [Retrieving events and reminders](https://developer.apple.com/documentation/eventkit/retrieving-events-and-reminders)
- [Creating a recurring event](https://developer.apple.com/documentation/eventkit/creating-a-recurring-event)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventViewController](https://developer.apple.com/documentation/eventkitui/ekeventviewcontroller)
- [EKCalendarChooser](https://developer.apple.com/documentation/eventkitui/ekcalendarchooser)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)

# SwiftUI Contacts store and change-history route design

This design guide turns the Contacts framework contract into a native iOS 26
screen system. It assumes that the app has a real user outcome—choose a
recipient, attach a person to a record, review a contact draft, or maintain an
app-owned projection—not a desire to display a private address book as a
decorative list.

The visual goal is Apple-native clarity with restrained Liquid Glass. The
operational goal is stronger: a person should always know which data is
authorized, which fields were fetched, which record is current, what an AI
proposal means, and whether the next tap is a local review or a system-owned
mutation.

## Screen hierarchy

Use a small number of roles:

~~~text
Contacts feature
├── access explanation
│   ├── not determined
│   ├── limited
│   ├── authorized
│   ├── denied
│   └── restricted
├── contact search or selected-contact list
│   ├── loading
│   ├── empty
│   ├── stale
│   └── error/retry
├── contact detail / selected property
├── review draft
│   ├── source fields
│   ├── optional AI proposal
│   ├── validation
│   └── explicit commit
├── change/reconcile status
└── system handoff
    ├── ContactsUI picker/card
    └── ContactProvider status
~~~

Avoid a screen that conflates these roles. Permission UI should not look like a
search result. A stale contact should not look like a ready-to-send contact.
A ContactProvider refresh signal should not look like a saved native contact.

## Access state as first-class design

The access card should say what the feature can do now, not merely display a
green permission icon:

| State | Plain-language message | Action |
| --- | --- | --- |
| Not determined | “Choose a contact for this feature.” | Request access at the feature boundary. |
| Limited | “You shared selected contacts.” | Add access with the system control or picker; keep selected identifiers visible. |
| Authorized | “Contacts access is available for this feature.” | Continue to the smallest fetch; do not imply every field is loaded. |
| Denied | “Contacts are unavailable until you change access in Settings.” | Settings guidance and manual route. |
| Restricted | “Device restrictions prevent Contacts access.” | Explain restriction; do not offer a dead permission button. |
| Record unavailable | “This contact is no longer available to the app.” | Reselect or refresh; never silently substitute a same-name result. |

The limited-access control should be a real ContactAccessButton or documented
contact access picker route when that is the correct outcome. A custom
glass-styled button labelled “Allow all contacts” can mislead a person and
cannot replace the system decision.

## Contact list composition

The list should expose a projection, not pretend it is the entire Contacts
database:

1. A title that describes the current feature, such as “Choose a person.”
2. A compact access/freshness status line.
3. A system or app search field.
4. Rows with localized display name, selected property label, and a
   user-understandable source hint.
5. A clear empty-state distinction: no match, no approved contacts, unavailable
   account, or fetch error.
6. A refresh/retry action when the store changed.

Use name formatting supplied by Contacts rather than reconstructing names from
given/family strings in a way that ignores locale or display order. Do not put
all phone numbers, email addresses, postal addresses, and notes into every row.
A row can show a single selected property and disclose more only after the
person chooses the contact.

For a broad list, use progressive detail:

~~~text
identifier-only index
  -> visible row keys
  -> selected contact detail keys
  -> action-specific key re-resolution
~~~

This reduces privacy exposure and makes the requested-key contract explainable.

## Identity and source presentation

If the screen can display unified and individual records, show the difference
only when it affects the action. Good copy includes:

- “Linked contact” when the framework returned a unified result;
- “From your app” for an app-owned projection;
- “Selected just now” for a user-mediated ContactsUI result;
- “Needs refresh” when a cached identifier no longer resolves;
- “Limited access” when the visible list is not the full store.

Do not show raw identifiers as customer-facing copy. Store them in the domain
projection and evidence logs with redaction. A phone number or name can help
search, but it should not be styled as a stable identity token.

When a user taps a row, re-resolve the identifier with the keys required for
the next action. Keep the selected state separate from the current resolved
record:

~~~text
selectedContactID
  != fetchedContactProjection
  != currentActionTarget
~~~

This prevents a stale row from authorizing an action against a different
record.

## Liquid Glass composition

Liquid Glass should be a system-aware material around controls and small
semantic groups. A useful layout is:

~~~text
navigation title
  [access + freshness status]
  list/content
  [glass action cluster]
     Search / Add access / Review / Refresh
~~~

Use one coherent glass container for related actions. Do not wrap every row,
phone label, or field in an isolated translucent capsule. Preserve hierarchy
with semantic typography, spacing, and system colors before adding material.

Good glass surfaces:

- a compact access/reload control group;
- a review card containing the exact selected contact field and proposal state;
- a commit action cluster with Save, Cancel, and Reselect;
- a provider status card with Enable, Refresh, and Reset actions.

Poor glass surfaces:

- a full-screen blurred address-book clone;
- a “synced” pill whose only evidence is a notification;
- an AI suggestion floating over private contact fields with no source label;
- a disabled button that still looks like a valid system action;
- a glass card that hides the access state until after a tap.

Material should not be used to disguise latency, permissions, or stale state.
Use a clear progress state and an accessible textual fallback.

## Review sheet for contact actions

Before an app-owned mutation or system handoff, use a focused review:

~~~text
Review contact action
────────────────────
Person:      formatted name
Source:      selected / unified / app-owned projection
Field:       phone or email label + value
Freshness:   resolved just now / needs refresh
Proposal:    optional derived text with “Suggested”

[Reselect] [Cancel] [Confirm]
~~~

The exact field being used should be visible. If the product is about sending,
show the destination field and the user-authored content; if it is about
attaching identity, show the app-owned record that will receive the link.

An AI suggestion belongs in the review sheet with:

- a “Suggested” or “Generated on device” label;
- source fields and source revision;
- deterministic validation state;
- an edit affordance;
- an explicit confirmation;
- a fallback when the model is unavailable or refuses.

Never let the model hide the identity resolution or perform the commit from
inside an opaque generation callback.

## Change-history and stale-state design

Change history is an operational status, not a badge:

| State | Visible treatment | Required behavior |
| --- | --- | --- |
| Initial rebuild | Progress plus “Preparing contacts” | Apply the drop-and-add stream before saving a new token. |
| Incremental refresh | Small activity indicator and last successful time | Keep the current projection visible but mark it refreshing. |
| Store changed | “Contacts changed—refreshing” | Coalesce notifications, cancel stale work, and re-fetch. |
| Token expired/invalid | “Refreshing from Contacts” | Discard token/projection as required and perform a full rebuild. |
| Bridge unavailable | “Change history unavailable; using refresh” | Use the approved notification/full-refetch fallback or show a bounded error. |
| Commit conflict | “Contact changed—review again” | Re-resolve and require confirmation against current values. |

Do not show “up to date” because an API call returned. The app can claim a
specific generation was applied only when it has persisted the generation,
projection, and token/revision together.

## ContactProvider design boundary

When an app also has a ContactProvider extension, add a separate settings
surface:

| Surface | Customer-facing language |
| --- | --- |
| Native Contacts access | “Allow this app to use selected Contacts.” |
| App-owned provider | “Make contacts managed by this app available to Phone and Mail.” |
| Provider enabled | “The system can request this provider’s read-only contacts.” |
| Provider refresh | “Ask the system to update the provider projection.” |
| Provider disabled | “The system will no longer use this provider’s contacts.” |

Do not show a provider item beside a native contact without a source label. A
provider projection is not a write to the person’s native database.

## Accessibility and alternate input

Build the contact feature with semantic controls:

- Button labels identify the action and the access consequence.
- A row’s accessibility label contains the localized name and only the
  selected property needed for the task.
- The access state is an accessibility value, not color alone.
- Loading, stale, denied, limited, and conflict states are announced.
- The review sheet exposes source, field, freshness, proposal, and confirmation
  in reading order.
- Dynamic Type must allow long localized names and labels without truncating the
  action target.
- Voice Control, Switch Control, keyboard, pointer, and one-handed use must
  reach search, add access, reselect, cancel, and confirm.
- Reduce Motion and Reduce Transparency must preserve the access/freshness
  meaning without relying on animation or blur.

Avoid exposing sensitive phone/email values in a notification or a live
activity simply because the user once selected a contact. Re-evaluate privacy
when the app moves to the background.

## Empty, denied, and unavailable layouts

Use distinct layouts:

| Condition | Layout |
| --- | --- |
| No authorized contacts under limited access | Access explanation and system Add Access action. |
| Search has no matches | Query-specific empty message and clear-search action. |
| Current record deleted/revoked | Stale card with Reselect and Refresh. |
| Contacts account unavailable | Account/service state and manual entry fallback. |
| Access denied/restricted | Settings or policy explanation; do not render a fake list. |
| Fetch failure | Error summary, retry, and preserved app-owned draft. |
| AI unavailable | Deterministic fields and manual editing. |

These states are part of the native polish. A polished glass shell around the
wrong empty state is still a misleading product.

## Design checklist

- Is the user outcome stated before the permission request?
- Does the screen distinguish limited, full, denied, and restricted access?
- Are requested keys limited to the current screen/action?
- Is the displayed contact a projection with source and freshness?
- Does selection re-resolve the identifier before an action?
- Is change history represented as reconciliation state, not a success badge?
- Does an expired/invalid token visibly trigger rebuild behavior?
- Is the Objective-C change-history bridge isolated and testable?
- Does Liquid Glass group real controls without becoming an address-book clone?
- Is an AI proposal visibly optional, typed, source-bound, editable, and reviewed?
- Can a person complete the task with VoiceOver, Dynamic Type, alternate input,
  reduced motion, and reduced transparency?
- Are personal fields excluded from logs, previews, and unapproved model input?
- Are physical device, archive, TestFlight, and release evidence separate?

## Sources

- [Contacts](https://developer.apple.com/documentation/contacts)
- [Accessing the contact store](https://developer.apple.com/documentation/contacts/accessing-the-contact-store)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [CNAuthorizationStatus.limited](https://developer.apple.com/documentation/contacts/cnauthorizationstatus/limited)
- [CNContact](https://developer.apple.com/documentation/contacts/cncontact)
- [CNContactFetchRequest](https://developer.apple.com/documentation/contacts/cncontactfetchrequest)
- [keysToFetch](https://developer.apple.com/documentation/contacts/cncontactfetchrequest/keystofetch)
- [CNChangeHistoryFetchRequest](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest)
- [startingToken](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/startingtoken)
- [CNFetchResult](https://developer.apple.com/documentation/contacts/cnfetchresult)
- [currentHistoryToken](https://developer.apple.com/documentation/contacts/cnfetchresult/currenthistorytoken)
- [CNSaveRequest](https://developer.apple.com/documentation/contacts/cnsaverequest)
- [ContactProvider](https://developer.apple.com/documentation/contactprovider)
- [ContactAccessButton](https://developer.apple.com/documentation/contactsui/contactaccessbutton)
- [NSContactsUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nscontactsusagedescription)
- [TN3149: Fetching Contacts change history events](https://developer.apple.com/documentation/technotes/tn3149-fetching-change-history-events)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing in Swift](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)

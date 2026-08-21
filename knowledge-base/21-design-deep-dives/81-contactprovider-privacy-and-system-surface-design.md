# ContactProvider privacy and system-surface design

ContactProvider design is about trust at the boundary between an app-owned
contact list and system-owned surfaces. The person should understand what the
provider shares, whether it is enabled, what is current, and how to turn it off.

Use this composition:

~~~text
provider identity and benefit
  -> enabled / disabled / unavailable state
  -> published generation and last update state
  -> field/privacy explanation
  -> Enable / Refresh / Review / Disable
  -> app-owned fallback and deletion path
~~~

The host app owns this interface. Phone, Mail, and Settings own their system
surfaces; the app should not imitate or promise their final rendering.

## Explain the provider in plain language

Avoid developer terms such as domain, enumerator, generation marker, and sync
anchor in customer-facing copy. Translate them into a concrete choice:

| Internal state | Useful copy |
| --- | --- |
| Extension discovered, not enabled | “Make contacts from this app available to Phone and Mail” |
| Enable prompt pending | “Allow this contact provider?” |
| Enabled, no recent signal | “Contacts are available; checking for updates” |
| Signal requested | “Update requested” |
| Enumeration in progress | “Updating contacts…” |
| Canonical source offline | “Showing the last approved contact set” |
| Person disabled in Settings | “Contact sharing is off in Settings” |
| Extension missing/unavailable | “This device can’t use the contact provider right now” |
| Reset requested | “Remove this app’s provided contacts and start over” |

Do not show “Synced” merely because `signalEnumerator` returned or a manager
call succeeded. Those events request system work; they do not prove a contact is
visible in every consumer.

## Setup screen hierarchy

The first-run screen should answer four questions quickly:

1. What contacts will be shared?
2. Why would I want that?
3. Can I turn it off?
4. What happens when a contact changes or is deleted?

Use a native navigation/sheet presentation with:

- provider name and app identity;
- an example system benefit, such as recognizing an app-managed caller;
- fields and record scope in plain language;
- current enabled/disabled/unavailable status;
- Enable/Disable/Refresh/Reset actions with confirmations where needed;
- a link or instruction for device Settings;
- last approved revision and fallback status;
- privacy, retention, logout, and deletion explanation.

Avoid a marketing hero that implies the app has access to all personal Contacts.
ContactProvider publishes the app’s own items; it is not a shortcut around
Contacts permission.

## Liquid Glass and functional provider controls

Liquid Glass can group the controls that operate on the provider state:

- Enable or Set Up;
- Refresh after a canonical data change;
- Review a proposed field/label before publishing;
- Disable or Reset.

Keep the provider status, data scope, error, and last approved revision in
ordinary readable content. A translucent button must not be the only indication
that the provider is disabled or that an update is still pending. Use native
confirmation and destructive-action patterns for Reset and Disable.

The visual material should follow the app’s native shell. Do not recreate the
Phone or Settings UI inside the app, and do not claim that the app controls how
other Contacts consumers render the projection.

## State-driven interaction

Model provider state explicitly:

~~~text
unconfigured
  -> extension unavailable / discovered
  -> enabling
  -> enabled
  -> update requested
  -> publishing generation N
  -> last approved generation N
  -> failed / stale / disabled / reset
~~~

Each state needs a safe action:

| State | Primary action | Avoid |
| --- | --- | --- |
| Unconfigured | Learn more / Enable | Auto-enable on launch |
| Enabled | View scope / Refresh | Repeated signals on every view update |
| Updating | Wait / Cancel host work | Claiming system completion |
| Stale/offline | Retry / Use app list | Inventing newer contact fields |
| Disabled | Enable / Open Settings | Continuing to present “shared” status |
| Reset | Confirm / Rebuild | Deleting canonical app records accidentally |
| Extension unavailable | Retry after update / fallback | Looping prompts or hidden failure |

The host app’s last signal result is not the extension’s enumeration result. Keep
those statuses separate if the product needs a detailed diagnostic screen.

## Contact identity and visual privacy

Show only the fields needed for the provider benefit. A contact card in the app
can expose richer data than the system projection, but the difference should be
intentional.

When listing published items:

- use the app’s stable identity, not a phone number, as the internal key;
- display the human-readable name and field scope;
- distinguish user-authored, imported, and AI-derived values;
- show a missing/stale image as missing rather than reusing an unrelated one;
- avoid logging full phone numbers/emails in status or analytics;
- preserve a deletion/revocation route.

If multiple records might represent the same person, show the match as a review
proposal. Do not automatically merge provider identities because names look
similar. A system caller-ID surface is a high-consequence context; keep
uncertain matches out of the published projection until validated.

## AI-assisted contact review

The app can use on-device AI to suggest a label, category, description, or
possible duplicate. The review surface should show:

~~~text
source records and revision
  -> suggestion and evidence/fields used
  -> before/after preview
  -> Accept / Edit / Dismiss
  -> published projection only after deterministic validation
~~~

Never let a model invent contact methods, publish a guessed identity, or update
the provider while the person is merely viewing a suggestion. If the model is
unavailable, offer manual editing or the last accepted projection. Keep model
metadata and generated values distinct from canonical fields.

## Accessibility and alternate input

The provider setup task should work without the person understanding Contacts
internals:

- VoiceOver announces provider name, purpose, enabled state, scope, last update,
  and available actions in order;
- Dynamic Type keeps long privacy text and errors readable;
- Enable, Refresh, Review, Disable, and Reset are semantic controls, not only
  swipe/gesture actions;
- destructive actions have clear labels and confirmation;
- reduced transparency/increased contrast preserve state and button boundaries;
- keyboard, pointer, Switch Control, and Voice Control can reach the core task;
- localization and right-to-left layout do not hide the status or actions;
- status is not conveyed by color or a checkmark alone.

If a system consumer shows a provider contact in a context the app cannot
customize, provide the best available data and privacy policy at publication;
do not promise an accessibility label or layout the app does not own.

## Offline, deletion, and logout

Define what happens when the canonical source is unavailable:

- keep the last approved generation if it is still safe and within retention;
- show the host app as stale without pretending the system has new data;
- retry with backoff rather than signaling constantly;
- remove or redact contacts when the person deletes the source record or logs
  out, according to the provider’s data contract;
- make Disable/Reset effects understandable and recoverable;
- update the app-owned list even if the system projection is waiting.

Deleting an app-managed record and disabling the provider are different actions.
Deleting the app removes the extension and its contacts; it should not silently
delete unrelated personal Contacts records. Show this distinction in the help
and confirmation copy.

## Design review checklist

- The screen explains provider scope, benefit, Settings control, and deletion.
- Enable, signal, enumeration, consumer visibility, and last approved generation
  are not collapsed into one “synced” status.
- The host app owns canonical records; the extension publishes a read-only
  projection.
- Paging, changes, stale/offline, reset, disable, and extension-unavailable
  states have useful copy and a fallback.
- Liquid Glass groups real actions and is not the only status/contrast surface.
- AI suggestions are evidence-linked, reviewable, and deterministic before
  publication.
- VoiceOver, Dynamic Type, reduced effects, contrast, keyboard/pointer,
  localization, RTL, and destructive-action confirmation are tested.
- Privacy, retention, logout, deletion, and system-consumer limitations are
  clear.

## Related routes

- [ContactProvider system contact projection](../42-framework-deep-dives/61-contactprovider-system-contact-projection.md)
- [ContactProvider capability route](../50-capability-recipes/84-contactprovider-capability-route.md)
- [ContactProvider proof matrix](../60-verification/78-contactprovider-proof-matrix.md)
- [ContactProvider recipes](../70-code-recipes/96-contactprovider-recipes.md)
- [Contacts, Calendar, and User Notifications route](../50-capability-recipes/35-contacts-calendar-notification-route.md)
- [Contacts and Calendar system-surface design](73-contacts-and-calendar-system-surface-design.md)

## Sources

- [ContactProvider](https://developer.apple.com/documentation/contactprovider)
- [ContactProviderManager](https://developer.apple.com/documentation/contactprovider/contactprovidermanager)
- [ContactProviderExtension](https://developer.apple.com/documentation/contactprovider/contactproviderextension)
- [ContactItemEnumerating](https://developer.apple.com/documentation/contactprovider/contactitemenumerating)
- [ContactItemContentObserver](https://developer.apple.com/documentation/contactprovider/contactitemcontentobserver)
- [ContactItemChangeObserver](https://developer.apple.com/documentation/contactprovider/contactitemchangeobserver)
- [Contacts](https://developer.apple.com/documentation/contacts)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

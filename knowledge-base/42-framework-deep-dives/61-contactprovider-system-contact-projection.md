# ContactProvider system contact projection

ContactProvider lets an app that manages its own contacts make those contacts
available to the system-wide Contacts ecosystem. The app provides a read-only
projection through a Contact Provider extension; it does not become the owner of
the person’s native Contacts database.

The route is:

~~~text
app-owned canonical contacts
  -> versioned/redacted provider projection
  -> ContactProvider extension enumeration
  -> system Contacts database
  -> Phone/Mail/other Contacts consumers
~~~

Keep this separate from Contacts framework read/write access, ContactsUI
pickers, CallKit caller identification, and an app’s own identity database.

## The target and process graph

| Component | Owns | Important boundary |
| --- | --- | --- |
| Host app | Canonical contact records, provider manager, enable/disable UI, sync trigger | `ContactProviderManager` is app-only; it cannot be used from the extension |
| Contact Provider extension | Enumeration of the app’s provided contacts and changes | Separate process/target with its own lifetime, resources, signing, and data access |
| `ContactProviderManager` | Enable/disable/reset/invalidate domain and signal enumeration | Enabling can prompt the person; manager calls may fail when the extension is missing/unavailable |
| `ContactProviderDomain` | Domain identifier/display name/user configuration | The person can enable or disable the provider in Settings |
| `ContactItemEnumerator` | Full content and changed-content enumeration | Enumeration must be deterministic, resumable, paged, and consistent with the app’s generation |
| System Contacts database | System-owned read-only projection | A provider result is not a write to the app’s database or the person’s native contact record |
| Phone/Mail/other consumers | System use of enabled provider contacts | A provider enabled state does not prove every consumer displays or matches an item |

Add the Contact Provider extension target using Xcode’s Contact Provider
extension template. Inspect target membership, extension point, deployment
target, signing, and resources in the archive; a source file in the host app is
not an extension.

## Provider lifecycle

The host app controls the domain lifecycle:

~~~text
extension installed
  -> manager discovered
  -> person asked to enable domain
  -> enabled
  -> signal enumeration after canonical data changes
  -> system enumerates full or changed content
  -> person may disable/remove provider in Settings
  -> app handles unavailable/disabled/reset/deleted states
~~~

`enable()` is asynchronous because it may ask the person to approve turning on
the provider. `isEnabled` is current manager/domain state, not proof that a
specific contact has reached a specific consumer. `disable()` and `reset()` are
destructive to the system projection, so expose them with plain language and a
recovery path. `invalidate()` requests that the extension terminate; it is a
lifecycle operation, not a contact deletion guarantee.

Use `signalEnumerator(for:)` when the app knows new canonical contacts are
available, such as after a server sync or user edit. The signal requests that
the extension enumerate; it does not synchronously report consumer visibility.
The system may also schedule provider work at low priority, including when the
device is connected to power overnight.

## Full content enumeration

`ContactItemEnumerating` supplies an enumerator for a collection, normally the
root container. `ContactItemEnumerator.enumerateContent(in:for:)` enumerates all
items in pages through a `ContactItemContentObserver`.

The content contract is stricter than “return every row”:

- the first page is `ContactItemPage.initialPage`;
- later pages use a stable `generationMarker` for the snapshot;
- the offset/page cursor is deterministic and resumable;
- each page is finished explicitly through the observer;
- changes made during enumeration can be delivered later through change
  enumeration;
- the same source snapshot must not reorder items between pages;
- a failure must finish enumeration with an error rather than silently stopping.

The generation marker is the app’s durable snapshot identity. Use a database
generation, sync revision, or immutable export token—not a wall-clock time that
can collide or move backward. Keep the source data needed to reproduce a
generation until the system can finish the enumeration or explicitly recover.

Do not calculate page offsets from a mutable, unsorted array. Sort by a stable
provider identifier and use a cursor that survives inserts/deletes. Bound page
size by the observer’s suggested batch size and the extension’s memory budget.

## Changed-content enumeration

`ContactItemChangeObserver` receives resumable updates and deletes from
`enumerateChanges(startingAt:for:)`:

~~~text
sync anchor A
  -> deterministic batch of updates/deletes
  -> didUpdate / didDelete
  -> didFinishEnumeratingChanges(upTo: B, moreComing: ...)
  -> system persists/continues from B
~~~

An anchor is a cursor into the provider’s change history, not a contact object
and not proof that the system has displayed a change. Preserve old anchors long
enough to answer resumable requests, and define what happens when the anchor is
unknown, pruned, corrupt, or from an older schema. The safe recovery is usually
a reset/full-content enumeration with an explicit generation.

Call `didFinishEnumeratingChangesWithError(_:)` when the app cannot provide a
consistent batch. Do not send a partial batch and then report success. Deletes
must include stable provider identifiers and must not be inferred from a short
page or a failed fetch.

## Contact item identity and data projection

The provider identifier is the app’s stable identity for an item in its domain.
Use it to map system projection changes back to canonical records. Do not use a
localized name, phone number, or array position as identity.

Choose fields deliberately:

| Projection field | Question |
| --- | --- |
| Display name | Is it current, localized, and safe to expose in incoming-call/message contexts? |
| Phone/email identifiers | Is the value canonicalized and allowed by the person’s privacy choice? |
| Image | Is size bounded, retained legally, and available to the extension process? |
| Organization/labels | Are they meaningful without leaking internal taxonomy? |
| App-specific metadata | Should it stay in the host app instead of the system projection? |
| AI-derived label | Is it visibly derived, reviewable, and safe for a system-owned surface? |

ContactProvider contacts are read-only to consumers. If the person edits a
native Contacts record, that does not automatically edit the provider’s
canonical record. Design a clear app-owned edit path and, if relevant, an
import/match flow rather than implying two-way synchronization.

## Extension lifecycle and resilience

The system can launch or terminate the extension independently of the host app.
Treat every invocation as a bounded job:

- open the canonical read-only data source safely;
- use the supplied page/anchor and deterministic ordering;
- fetch only the fields needed for the current batch;
- finish each batch or report an error;
- close resources and release memory;
- tolerate host app not running, network unavailable, account unavailable,
  migration in progress, and a person disabling the provider;
- avoid UI, long-lived global state, and assumptions about a warm process.

If canonical data is remote, the extension needs a local projection/cache or a
reliable resumable fetch strategy. Do not make the extension depend on an
interactive host-app login screen. If the source is stale, provide the last
approved generation or fail clearly; do not fabricate new contacts.

## Privacy and permission boundaries

The person can see providers in Settings and selectively enable or disable
them. The provider should expose only contacts the app manages and only fields
required for the stated system benefit. Do not use ContactProvider as a way to
bypass Contacts permission for reading the person’s private native contacts.

If the host app also uses Contacts framework access, keep the two authorities
separate:

| Route | Authority |
| --- | --- |
| ContactProvider | App-owned read-only projection to system Contacts consumers |
| Contacts/CNContactStore | Person-authorized read/write access to native Contacts data |
| ContactsUI picker/editor | Person-mediated selection/editing in a system UI |
| App database | Product-owned canonical identity/contact records |

Document retention, deletion, account logout, export, and provider-disable
behavior. Deleting the app removes the extension and its provided contacts, but
do not claim that every copied/exported system artifact or a consumer’s cached
display is immediately erased unless verified.

## AI and contact-provider data

AI can suggest a label, merge candidate, or accessibility description inside the
host app. Keep the provider projection deterministic:

~~~text
canonical record
  -> approved/derived projection
  -> ContactItem with stable ID
  -> system enumeration
~~~

Do not let a model invent a phone number, decide that two people are the same,
or publish a speculative label to Phone/Mail without review and deterministic
validation. Store source revision, proposal, model route/version, reviewer
choice, and published projection separately. If a proposal is stale, omit it or
keep the last accepted projection; do not publish the stale result.

## SwiftUI and native setup surface

The host app can present a small setup/status screen:

~~~text
provider identity and benefit
  -> current enabled/disabled/unavailable state
  -> Enable / Disable / Refresh / Reset controls
  -> last canonical revision and last signal result
  -> privacy and deletion explanation
  -> fallback to app-owned contacts when unavailable
~~~

Use native controls and plain status text. Liquid Glass can group Enable,
Refresh, Review, or Disable when those are the real actions, but it must not
make a local signal look like system completion. Show “Waiting for Contacts to
update” rather than “Synced” unless the app has evidence for the specific
state.

## Proof that matches the system boundary

Source docs establish the API shape. A complete feature needs separate proof
for:

- app target and Contact Provider extension target configuration;
- domain enable prompt, Settings disable/re-enable, reset, and extension-not-
  found/unavailable errors;
- full enumeration paging, stable generation markers, deterministic order, and
  resumable continuation;
- change enumeration updates, deletes, `moreComing`, anchor persistence, and
  reset recovery;
- host app not running, extension termination, offline/stale data, and
  canonical-store migration;
- actual Contacts consumer behavior, if the product claims it;
- privacy, redaction, deletion, logout, and provider removal;
- accessibility of setup/status/review screens;
- signed archive extension point/resources/privacy configuration;
- AI proposal and last-accepted projection behavior.

The [ContactProvider capability route](../50-capability-recipes/84-contactprovider-capability-route.md)
is the build worksheet. The [ContactProvider proof matrix](../60-verification/78-contactprovider-proof-matrix.md)
defines fixtures, and the [ContactProvider recipes](../70-code-recipes/96-contactprovider-recipes.md)
remain route sketches until compiled and run in a named app-plus-extension
target.

## Sources

- [ContactProvider](https://developer.apple.com/documentation/contactprovider)
- [ContactProviderManager](https://developer.apple.com/documentation/contactprovider/contactprovidermanager)
- [ContactProviderExtension](https://developer.apple.com/documentation/contactprovider/contactproviderextension)
- [ContactProviderDomain](https://developer.apple.com/documentation/contactprovider/contactproviderdomain)
- [ContactItemEnumerating](https://developer.apple.com/documentation/contactprovider/contactitemenumerating)
- [ContactItemEnumerator](https://developer.apple.com/documentation/contactprovider/contactitemenumerator)
- [ContactItemContentObserver](https://developer.apple.com/documentation/contactprovider/contactitemcontentobserver)
- [ContactItemChangeObserver](https://developer.apple.com/documentation/contactprovider/contactitemchangeobserver)
- [ContactItemPage](https://developer.apple.com/documentation/contactprovider/contactitempage)
- [ContactItemSyncAnchor](https://developer.apple.com/documentation/contactprovider/contactitemsyncanchor)
- [Contacts](https://developer.apple.com/documentation/contacts)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

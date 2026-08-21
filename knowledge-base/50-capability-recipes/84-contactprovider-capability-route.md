# ContactProvider capability route

Use this route when an app owns a contact collection and wants people to make
that collection available to the system Contacts ecosystem. It is an app-plus-extension
feature with resumable enumeration, user-controlled enablement, and a
read-only system projection.

## Choose the contact route first

| Need | Route | Authority |
| --- | --- | --- |
| Store app-managed contacts and expose them to Phone/Mail | ContactProvider | App database plus Contact Provider extension |
| Read or write the person’s native Contacts | Contacts/CNContactStore | Person-authorized Contacts store access |
| Let the person select a contact without broad access | ContactsUI picker/access button | Person-mediated selection |
| Edit a native contact in a system surface | ContactsUI editor | System editor and Contacts store permissions |
| Match app identity to an incoming call/message | ContactProvider or CallKit route as appropriate | Provider projection versus communication-system contract |
| Suggest contact labels/merges | On-device AI proposal in host app | Person review and deterministic canonical commit |

Do not choose ContactProvider to avoid Contacts permission. Its source is the
app’s own managed contacts, and the system consumes the published items as a
read-only projection.

## Step 1: define canonical authority and projection

Write the record contract before creating the extension:

~~~text
CanonicalContact
  stable app ID / revision / source
  approved name and contact methods
  source and retention policy
  optional image/resource projection
  AI-derived fields with provenance/review state

PublishedContactItem
  provider identifier derived from app ID
  only approved system-use fields
  published generation / projection revision
  redaction and deletion behavior
~~~

The provider identifier must be stable across paging, updates, and app launches.
Do not derive it from a display name, phone number, localized string, or array
index.

## Step 2: create the target graph

Add a Contact Provider extension target from the Xcode template and record:

- host app target and extension target identifiers;
- extension point and deployment targets;
- source/resource membership and shared model access;
- signing, capabilities, and archive membership;
- local projection/store path and migration owner;
- app-only manager code versus extension-only enumeration code;
- test target coverage for both processes.

`ContactProviderManager` is for the host app, not the extension. The extension
must be able to answer enumeration requests without showing UI or waiting for
the host app to be interactively launched.

## Step 3: enable the domain deliberately

The host app’s setup route is:

1. create a manager for the default or named domain;
2. inspect manager/domain discovery errors;
3. explain the data scope and system benefit;
4. call `enable()` in response to a person’s action;
5. observe/refresh `isEnabled` and map errors to a fallback;
6. offer Disable and Reset with clear consequences;
7. call `signalEnumerator(for:)` after a canonical revision is ready.

Enablement can prompt the person. A successful method return means the request
was accepted, not that every system consumer has updated. Maintain separate
host state:

~~~text
extensionFound / domainEnabled / signalRequested / lastCanonicalRevision
  / lastEnumerationResult / consumerVisibilityUnknown
~~~

If the manager throws `extensionNotFound` or `featureNotAvailable`, keep the
app-owned contact feature usable and explain the system-provider fallback.

## Step 4: implement full enumeration

The extension conforms to the ContactProvider enumeration protocols and returns
an enumerator for the requested collection. Full content must be deterministic
and resumable:

1. handle `ContactItemPage.initialPage`;
2. resolve the canonical snapshot for the page’s generation marker;
3. sort by stable provider identifier;
4. apply the supplied offset/cursor and bounded batch size;
5. send only valid, approved ContactItems;
6. finish each page with the next page state or final content anchor;
7. report an error when the source cannot produce a consistent snapshot.

Do not use a mutable live query whose order changes between pages. Capture a
generation snapshot or a durable cursor. If the generation is no longer
available, fail or reset according to the documented recovery route rather than
mixing records from different versions.

## Step 5: implement change enumeration

Persist a change log or equivalent history that can answer an incoming
`ContactItemSyncAnchor`. For each request:

- read changes strictly after the anchor;
- batch updates and deletes deterministically;
- respect the observer’s suggested batch size;
- call `didUpdate` and `didDelete` with stable identifiers;
- finish with the highest completed anchor and `moreComing`;
- call the error completion when the anchor cannot be honored;
- retain/recover history long enough for resumable system work.

If the history is pruned or the anchor is invalid, use a reset/full enumeration
with a new generation. Never skip changes silently or report a new anchor for a
partial batch.

## Step 6: keep the extension process-safe

The extension may be launched without the host app and may be terminated after
a bounded amount of work. Use a read-only local projection or a resumable
source route:

- no UI or user login prompt;
- no unbounded network fetch per item;
- no global mutable cache that assumes a warm process;
- no main-thread blocking for large contact sets;
- deterministic ordering and bounded images/fields;
- resource cleanup after each page/batch;
- offline/stale/error state that the system can recover from.

If canonical data is remote, the host app should fetch and persist an approved
generation before signaling. The extension should not invent a different view
of remote truth during enumeration.

## Step 7: add privacy and deletion policy

Document:

- fields included in the provider projection;
- how images and sensitive methods are redacted;
- how app logout changes the projection;
- how a canonical deletion becomes a provider delete;
- how Disable and Reset affect system projection versus canonical data;
- how app deletion is communicated to the person;
- whether a provider contact can appear in system contexts the app cannot style;
- what diagnostics/analytics are permitted.

The provider is not a second writable copy of native Contacts. Do not import
system consumer edits automatically. If the product supports an import/match
flow, make it a separate person-reviewed feature.

## Step 8: add bounded AI review

Use AI only in the host app to enrich or validate the canonical source:

~~~text
approved canonical records
  -> local model suggestion
  -> typed label/merge/description proposal
  -> source/revision and confidence context
  -> person review
  -> deterministic canonical commit
  -> provider signal
~~~

The provider should publish the last accepted projection, not an in-flight
proposal. Check the revision again before signaling. If the model is unavailable
or uncertain, keep the previous projection or require manual editing.

## Step 9: native UI and system handoff

Use a SwiftUI setup/status screen with semantic controls. Liquid Glass may group
Enable, Refresh, Review, or Disable, but status and privacy copy must remain
readable without the material.

If the feature is surfaced through App Intents, widgets, or communication
flows, pass a typed app-owned projection. Do not pass a live CNContact, manager,
extension object, or canonical database context across a system-surface
boundary.

## Step 10: build the proof packet

The [ContactProvider proof matrix](../60-verification/78-contactprovider-proof-matrix.md)
should include:

- source/target/extension configuration;
- enable/disable/reset/unavailable states;
- full content paging and generation markers;
- change anchors, updates, deletes, batching, and recovery;
- process termination, host-app-not-running, offline, and migration behavior;
- actual consumer/system visibility if claimed;
- privacy, accessibility, AI review, deletion, logout, and release evidence.

## Stop conditions

Stop before shipping if:

- the extension reads or writes the person’s native Contacts as its authority;
- the manager is called from the extension target;
- paging order changes between requests or is not resumable;
- an invalid anchor is silently ignored;
- a signal call is shown as consumer synchronization complete;
- an AI proposal is published without review/revision validation;
- provider disable/reset is hidden or deletes canonical records unexpectedly;
- an extension debug run is used as proof of Settings/Phone/Mail behavior.

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
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

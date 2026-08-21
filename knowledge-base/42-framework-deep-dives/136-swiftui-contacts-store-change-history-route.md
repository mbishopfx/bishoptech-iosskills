# SwiftUI Contacts store, identity, change history, and mutation route

Contacts is a protected, system-owned personal-data store. A good native route
does not begin with “load the address book.” It begins with a narrowly defined
user outcome, asks for the smallest access and keys needed for that outcome,
keeps the I/O off the main thread, and maintains an app-owned projection that
can be invalidated when the system store changes.

This deep dive is deliberately separate from the existing ContactsUI picker
and ContactProvider pages:

- ContactsUI is the user-mediated picker/card/access-control surface.
- Contacts is the direct, authorized read/write store route.
- ContactProvider is a read-only projection of an app-owned contact source into
  the system Contacts ecosystem.
- An app’s own database is the product’s canonical domain model, not a synonym
  for a CNContact record.

The central contract is:

~~~text
user outcome
  -> minimum access explanation
  -> authorization and requested-key policy
  -> background Contacts read
  -> normalized app-owned projection
  -> optional typed proposal
  -> user review and deterministic commit
  -> change notification/history reconciliation
~~~

## The smallest native route

For a feature that needs one person, prefer a ContactsUI picker or the
limited-access controls already covered by the ContactsUI route. Use
CNContactStore when the feature genuinely needs direct, repeatable store
operations.

For a direct Contacts route:

1. State the exact user outcome and the fields it requires.
2. Add NSContactsUsageDescription with truthful, feature-specific copy.
3. Check CNContactStore.authorizationStatus(for: .contacts).
4. If the state is .notDetermined, request access at the moment the feature
   needs it. The async access request is preferable for an app UI because the
   completion does not block the main thread.
5. Treat .limited, .authorized, .denied, and .restricted as different product
   states. Limited access is not a failed authorization.
6. Fetch only the keys required by the current operation. Add formatter
   descriptors when a formatter will be used.
7. Run synchronous Contacts I/O away from the main actor. Send immutable,
   minimized projections back to SwiftUI.
8. Re-fetch cached objects after CNContactStoreDidChangeNotification; do not
   treat the notification as a payload.
9. For incremental reconciliation, persist the opaque
   CNFetchResult.currentHistoryToken only after a successful change-history
   fetch. A stale or invalid token must fall back to a full rebuild.
10. For a write, construct a fresh CNSaveRequest, validate the current
    identifier/access state, execute it, and re-resolve the resulting record.

## Authorization is a data-boundary state machine

CNAuthorizationStatus includes .notDetermined, .restricted, .denied,
.authorized, and .limited on current iOS. The status describes the app’s
permission relationship to the Contacts store; it does not guarantee that a
particular record, field, account, or current sync state is available.

| Status | Meaning for the route | Native product response |
| --- | --- | --- |
| notDetermined | The person has not decided. | Explain the concrete feature and request only at the point of need. |
| restricted | The app cannot be authorized because of a restriction. | Explain that Settings or device policy controls the state; keep a manual route. |
| denied | The person denied access. | Do not repeatedly prompt; offer Settings guidance or a no-Contacts workflow. |
| authorized | The app has full Contacts authorization under the current system policy. | Still fetch only required keys and handle deleted, unavailable, and changed records. |
| limited | The person exposed only a subset of contacts. | Show the limited state, use approved identifiers, and offer system access controls to expand the set. |

The limited state is particularly important on iOS 18 and later. A person can
choose specific contacts, later change that set in Settings, or add contacts
through ContactAccessButton or the contact access picker. A callback containing
new identifiers is not a complete diff of every contact that became hidden.
Refresh the app projection and handle missing records as revocation or
identity loss, not as an empty name.

Contacts a person creates through the app have special access behavior in the
limited-access model, but the app still must not infer that every native
contact is readable or writable. The permission state, the record’s current
resolvability, and the target operation’s authorization must be checked
separately.

The NSContactsUsageDescription string is required for Contacts access. A note
field has an additional com.apple.developer.contacts.notes entitlement and
Apple permission requirement; the presence of the key in a source snippet is
not permission to ship note access.

## Store ownership and I/O

CNContactStore is thread safe, but Contacts fetch methods perform synchronous
I/O. Apple recommends avoiding the main thread. A useful ownership split is:

| Layer | Responsibility |
| --- | --- |
| ContactsAccessCoordinator | Authorization status, request timing, limited/full/denied state. |
| ContactsStoreClient | Background fetch/save and framework error mapping. |
| ContactProjectionStore | Minimized, app-owned records, last successful fetch, identity revision. |
| ContactsChangeReconciler | Notification-triggered reload and incremental/full-rebuild policy. |
| SwiftUI feature model | Loading, stale, permission, empty, error, and review state. |
| Optional local model adapter | Proposal only; never a permission or persistence authority. |

Do not create a new store per row or let a view own a long-running fetch
without cancellation. A long-lived client can reuse a store, but all reads and
writes still need explicit ownership and a clear queue/actor boundary. Avoid
passing mutable contacts across an async boundary while a save request is
executing.

CNContact values are immutable. CNMutableContact is a mutable editing object.
Keep mutable objects inside a short-lived draft/commit boundary; do not use one
as the app’s persistent model.

## Field minimization and partial contacts

Every fetched contact is a partial contact relative to the full database. A
fetch request must include at least one key descriptor. Use only fields that
the current feature needs:

| Need | Minimum direction |
| --- | --- |
| Stable local resolution | CNContactIdentifierKey. |
| Display a localized name | CNContactFormatter.descriptorForRequiredKeys(for: .fullName) plus the name keys required by the formatter. |
| Show a phone choice | Identifier plus CNContactPhoneNumbersKey and a display-name descriptor if needed. |
| Show an email choice | Identifier plus CNContactEmailAddressesKey and a display-name descriptor if needed. |
| Edit one record | Resolve the identifier with the keys required for the edit, copy to CNMutableContact, then save. |
| Search by name | Use the Contacts-provided name predicate and the smallest display keys. |

The framework’s documented keysToFetch discipline is a privacy, memory, and
correctness rule. If a view later reads a property that was not fetched, the
result may be incomplete or raise an unauthorized-key error. Do not solve that
by always fetching every property.

For a broad list, first fetch identifiers, then fetch bounded batches of
detailed contacts by identifier as screens require them. Aggregate duplicate
identifiers before a batch fetch. Keep exact phone numbers, email addresses,
postal addresses, notes, social profiles, and images out of logs and model
prompts unless the user explicitly selected the field for the current outcome.

CNContactFormatter and localized label helpers are part of the native display
route. Preserve the underlying values for deterministic action selection, but
let the formatter/localization policy decide how the name or label is shown.

## Predicates and identity

Use the predicates supplied by CNContact:

- predicateForContacts(matchingName:)
- predicateForContacts(matchingEmailAddress:)
- predicateForContacts(matchingPhoneNumber:)
- predicateForContacts(withIdentifiers:)
- group/container predicates where the route needs them

The Contacts framework does not support arbitrary generic or compound
predicates. A search UI can combine user filters in the app layer after a
bounded, authorized fetch, but do not smuggle a compound NSPredicate into the
Contacts store and assume it will execute.

An identifier is useful for resolving a current record in the current Contacts
store. It is not a universal account identity, an authorization grant, or proof
that a person with the same name is the same person. Unification can cause a
returned unified contact to have a different identifier from the individual
record supplied to a fetch. When a route depends on a specific source record,
record the identity mode:

| Identity mode | Safe use |
| --- | --- |
| Unified contact identifier | Current display/action resolution where linked contacts are acceptable. |
| Individual record identifier | Source-specific operations that must preserve the underlying record. |
| App-owned contact ID | Product identity; map to Contacts identifiers as a volatile integration reference. |
| Name/phone/email | Search or display signal only; never canonical identity. |

When a later action needs a contact, re-resolve the identifier with the keys
needed for that action. If the record cannot be resolved, mark the projection
stale and require a fresh selection. Do not send to the last cached phone number
because the visible name still matches.

## Fetch choices

| Outcome | Route | Important semantics |
| --- | --- | --- |
| One known identifier | unifiedContact(withIdentifier:keysToFetch:) | May return a unified record or a record-does-not-exist error; re-check the required keys. |
| Search by name/email/phone | unifiedContacts(matching:keysToFetch:) | Use a framework predicate; an empty result is not a permission explanation. |
| Bounded list/all contacts | CNContactFetchRequest plus enumerateContacts(with:) | Run off the main thread; set keys, predicate, unification, mutability, and sort deliberately. |
| Incremental changes | CNChangeHistoryFetchRequest plus the Objective-C enumerator bridge | Persist the result token only after applying the complete event batch. |
| User chooses one contact | ContactsUI picker/access control | Prefer when broad direct access is unnecessary. |
| App-owned contacts visible to Phone/Mail | ContactProvider extension | Read-only system projection, separate from native Contacts authorization. |

The CNContactStore helper APIs are convenient for one-shot searches, but the
same key and identity rules apply. A user-visible empty list can represent no
matches, limited access, no records, an unavailable account, or an error; keep
those states explicit.

## Change history and notification reconciliation

The change-history route uses an opaque Data token, not a contact object:

~~~text
no saved token
  -> startingToken = nil
  -> drop-everything event + add events for the current store
  -> apply complete rebuild
  -> save CNFetchResult.currentHistoryToken

saved token
  -> startingToken = saved token
  -> coalesced contact/group events
  -> apply all events
  -> save result.currentHistoryToken

expired/invalid token
  -> discard local projection and token
  -> full rebuild
  -> save new result token
~~~

CNChangeHistoryFetchRequest always returns contact changes. Group changes are
opt-in with includeGroupChanges. By default, change results are unified and
immutable, and only the contact identifier is fetched. Request additional
contact key descriptors only when the reducer genuinely needs them. Set
shouldUnifyResults to false when the product must preserve individual source
records.

CNSaveRequest.transactionAuthor and
CNChangeHistoryFetchRequest.excludedTransactionAuthors can prevent an app from
reprocessing changes it already knows it authored. The author is a filter
label, not a trustworthy description of who made a change.

The change-history events include drop-everything, add/update/delete contact,
add/update/delete group, and group membership/subgroup changes. Use
CNChangeHistoryEventVisitor; Apple’s technote says to use the visitor protocol
instead of class checks. A drop-everything event means incremental sync is no
longer safe and should be followed by a complete rebuild.

There is a critical Swift boundary: Apple’s TN3149 explicitly marks
enumeratorForChangeHistoryFetchRequest:error: unavailable in Swift. Current
SDK headers expose the same method with an unavailable Swift importer
annotation. A Swift app that needs change history should put the smallest
Objective-C adapter in a separate target/module, or choose a documented
notification-plus-full-refetch route when incremental history is not necessary.
Do not write a Swift snippet that calls store.enumerator(for:) and claim it is
usable because the symbol appears in the Apple page.

CNContactStoreDidChangeNotification is a change signal, not a change payload.
When it fires, cached contacts, groups, and containers must be refetched and
old cached objects released. Coalesce repeated notifications, cancel stale
reloads, and make a notification-triggered reload idempotent.

## Mutation and conflict behavior

Create a new CNSaveRequest for each execution. You can batch multiple object
changes, but do not access the objects while the request executes. Overlapping
concurrent save requests use last-change-wins behavior. Treat that as a
conflict policy, not as a guarantee that the app’s draft was still current.

Important error branches include:

| Error family | Product interpretation |
| --- | --- |
| Authorization denied / unauthorized key | Re-check permission and requested keys; do not retry blindly. |
| No accessible writable container | Keep the draft and offer another user-mediated route. |
| Record does not exist | Re-resolve; the object may have been deleted or access may have narrowed. |
| Inserted record already exists | The draft or ID is not new; reconcile rather than duplicating. |
| Record/container not writable | Offer a different destination or explain the restriction. |
| Validation multiple/type/configuration errors | Show field-specific correction state; do not discard the draft. |
| Change history expired/invalid anchor/request | Drop the token and rebuild from the current store. |

shouldRefetchContacts defaults to true for added/updated contacts. Setting it to
false can reduce save time, but the Contacts objects must not be used after the
save because they may no longer be current. A successful execute call is not
the final app projection: re-fetch the saved record with the exact
display/action keys and store the new revision.

## ContactProvider is a different authority

ContactProvider is appropriate when the app manages its own contact source and
wants Phone, Mail, and other Contacts consumers to see a read-only projection.
It does not grant the app access to the person’s native Contacts database and
does not make provider items editable as native records.

| Question | Contacts store | ContactProvider |
| --- | --- | --- |
| Canonical source | Person’s system Contacts database | App-owned contacts/database |
| App mutation | CNSaveRequest with authorization | Host app edits canonical data; extension projects it |
| System visibility | Existing native contact data | Person enables/disables the provider domain |
| Sync shape | Fetch/notification/change-history reconciliation | Extension enumeration, generation markers, change anchors |
| Access meaning | Person-authorized native data | Read-only projection selected in Settings |

If a feature reads native Contacts and also publishes app-owned contacts,
maintain two explicit authorities and two privacy/deletion policies. A
ContactProvider item must never be presented as proof that a native CNContact
was created or that Phone/Mail displays it.

## SwiftUI and Liquid Glass composition

Keep the Contacts store behind a model/service boundary. The screen should
expose state such as:

~~~text
idle
  -> explainAccess
  -> requesting
  -> limited|authorized|denied|restricted
  -> loading
  -> ready|empty|stale|error
  -> reviewDraft
  -> committing
  -> committed|conflict|needsReselect
~~~

Use standard List, SearchField, Button, NavigationStack, and
confirmationDialog semantics first. Use Liquid Glass around a compact action
cluster such as “Choose contact,” “Add access,” “Review,” or “Refresh,” not as
a full-screen contact database skin. Keep the contact’s name, selected field,
access state, source/provenance, and freshness visible as text.

Glass should not imply that a projection is canonical. A glass card labelled
“Ready to send” must be backed by a current resolved contact and an explicit
user action, not a cached contact row. A card labelled “Synced” should require
evidence for the app-owned projection generation; a notification or successful
signal is not enough.

## On-device AI boundary

Contacts are highly identifying. An on-device model can help with a reviewed
task, but it should receive the minimum user-selected context:

~~~text
selected contact fields
  -> typed ContactProposal
  -> identifier/permission/current-store validation
  -> user review
  -> explicit app or system action
~~~

Good bounded proposals include:

- display-name formatting for a selected contact;
- choosing among already selected phone/email labels;
- a draft message or reminder title from user-provided text;
- a merge candidate list that a person must review;
- identifying missing fields in an app-owned draft.

Do not pass the whole address book to a model to select a recipient when a
picker or predicate can do it. Do not let a model invent or normalize a phone
number and write it without review. Never treat an AI-selected name as a
contact identifier. Capture source contact IDs, keys, store revision, model
version, proposal status, reviewer decision, and commit result separately.

If the store changes while a proposal is open, mark it stale and re-resolve the
identifier. If the current record is gone or the selected field changed,
require a new user selection.

## Accessibility and privacy

Contact data can reveal relationships, identity, home/work location, and
communication channels. Keep it out of analytics, crash metadata, notification
previews, screenshots, and debug logs by default. Explain whether the app
stores a local projection and how deletion or access revocation affects it.

Use CNContactFormatter and localized labels for names and property labels.
Accessibility values should say what the user can act on without exposing
unnecessary private fields. A VoiceOver label for a contact choice should not
quietly concatenate every phone number and email address.

Verify:

- VoiceOver reading order for access, contact identity, selected field, and
  action;
- Dynamic Type with long names and labels;
- right-to-left names and localized contact labels;
- Voice Control/Switch Control/keyboard/pointer action paths;
- reduced motion/transparency and high contrast;
- permission-denied, limited, stale, conflict, and retry states;
- privacy redaction when a screen is captured or the app leaves the foreground.

## Target, device, and release proof

Source documentation and a compiling route do not prove the Contacts service
behavior. A meaningful proof package includes:

1. A named iOS target with NSContactsUsageDescription, exact Contacts
   capability/entitlement choices, and any approved notes entitlement.
2. A physical iPhone with controlled test contacts and account state.
3. Permission reset tests for not-determined, limited, full, denied, and
   restricted behavior.
4. Fetch tests for missing keys, name/phone/email predicates, unified versus
   individual identities, deleted records, and access narrowing.
5. Change-history tests for initial rebuild, incremental token, coalescing,
   group changes, notification-triggered refetch, expired/invalid token, and
   Objective-C bridge failure.
6. Mutation tests for add/update/delete, duplicate insert, deleted-record
   conflict, writable-container failure, field validation, and re-fetch after
   save.
7. ContactProvider tests separately if the app publishes app-owned contacts to
   the system.
8. An archive inspection proving target membership, usage descriptions,
   entitlements, bridge module inclusion, and release configuration.
9. TestFlight proof on a signed build with privacy copy and Settings behavior.

An Xcode archive, a simulator contact, a permission Boolean, a fetched
CNContact, a change token, a save callback, a ContactProvider signal, or an AI
proposal is one evidence item—not proof of the whole user-visible workflow.

## Sources

- [Contacts](https://developer.apple.com/documentation/contacts)
- [Accessing the contact store](https://developer.apple.com/documentation/contacts/accessing-the-contact-store)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [CNAuthorizationStatus](https://developer.apple.com/documentation/contacts/cnauthorizationstatus)
- [CNAuthorizationStatus.limited](https://developer.apple.com/documentation/contacts/cnauthorizationstatus/limited)
- [CNContact](https://developer.apple.com/documentation/contacts/cncontact)
- [CNMutableContact](https://developer.apple.com/documentation/contacts/cnmutablecontact)
- [CNContactFetchRequest](https://developer.apple.com/documentation/contacts/cncontactfetchrequest)
- [CNFetchRequest](https://developer.apple.com/documentation/contacts/cnfetchrequest)
- [keysToFetch](https://developer.apple.com/documentation/contacts/cncontactfetchrequest/keystofetch)
- [predicate](https://developer.apple.com/documentation/contacts/cncontactfetchrequest/predicate)
- [unifiedContacts(matching:keysToFetch:)](https://developer.apple.com/documentation/contacts/cncontactstore/unifiedcontacts%28matching%3Akeystofetch%3A%29)
- [predicateForContacts(matchingName:)](https://developer.apple.com/documentation/contacts/cncontact/predicateforcontacts%28matchingname%3A%29)
- [CNChangeHistoryFetchRequest](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest)
- [startingToken](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/startingtoken)
- [additionalContactKeyDescriptors](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/additionalcontactkeydescriptors)
- [CNFetchResult](https://developer.apple.com/documentation/contacts/cnfetchresult)
- [currentHistoryToken](https://developer.apple.com/documentation/contacts/cnfetchresult/currenthistorytoken)
- [CNChangeHistoryEvent](https://developer.apple.com/documentation/contacts/cnchangehistoryevent)
- [CNChangeHistoryEventVisitor](https://developer.apple.com/documentation/contacts/cnchangehistoryeventvisitor)
- [CNSaveRequest](https://developer.apple.com/documentation/contacts/cnsaverequest)
- [transactionAuthor](https://developer.apple.com/documentation/contacts/cnsaverequest/transactionauthor)
- [shouldRefetchContacts](https://developer.apple.com/documentation/contacts/cnsaverequest/shouldrefetchcontacts)
- [CNError](https://developer.apple.com/documentation/contacts/cnerror)
- [CNError.Code.changeHistoryExpired](https://developer.apple.com/documentation/contacts/cnerror/code/changehistoryexpired)
- [CNError.Code.changeHistoryInvalidAnchor](https://developer.apple.com/documentation/contacts/cnerror/code/changehistoryinvalidanchor)
- [CNError.Code.changeHistoryInvalidFetchRequest](https://developer.apple.com/documentation/contacts/cnerror/code/changehistoryinvalidfetchrequest)
- [ContactProvider](https://developer.apple.com/documentation/contactprovider)
- [ContactAccessButton](https://developer.apple.com/documentation/contactsui/contactaccessbutton)
- [NSContactsUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nscontactsusagedescription)
- [Contacts notes entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.contacts.notes)
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

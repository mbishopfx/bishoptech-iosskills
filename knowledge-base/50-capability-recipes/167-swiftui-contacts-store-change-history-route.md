# SwiftUI Contacts store and change-history capability route

Use this route when an app needs direct Contacts reads or writes that cannot be
served by a one-time ContactsUI selection. It keeps native access, app-owned
projection, optional AI, and system projection as separate authorities.

## Route card

| Decision | Native route | Do not infer |
| --- | --- | --- |
| Choose one person for a single action | ContactsUI picker or access control | A picker result is broad Contacts authorization. |
| Search approved native contacts | CNContactStore and a framework predicate | An empty result identifies why no row appeared. |
| Display a localized contact | Fetch identifier plus formatter-required keys | A display name is a canonical identity. |
| Keep an app-owned local index | Identifier-first fetch, bounded detail fetch, projection revision | A cached CNContact remains current after a store change. |
| Incrementally reconcile native Contacts | CNChangeHistoryFetchRequest and Objective-C enumerator adapter | A Swift call to enumerator(for:) is available; Apple marks it unavailable in Swift. |
| Create/update/delete a native contact | CNMutableContact plus a new CNSaveRequest | A successful save means the app’s draft is still current. |
| Publish app-owned contacts to Phone/Mail | ContactProvider extension | A provider item is a native writable contact. |

## Target and service manifest

Before implementation, write down:

- iOS deployment target and final Xcode SDK;
- NSContactsUsageDescription copy;
- requested Contacts entity type, currently contacts;
- whether the feature can work with limited access;
- whether the feature uses ContactsUI instead of direct store access;
- exact keys needed for list, detail, and commit;
- whether the app reads notes and therefore needs the separately approved
  contacts-notes entitlement;
- whether the app has a ContactProvider extension target;
- whether change history is required or notification-plus-full-refetch is
  sufficient;
- the app-owned projection schema and deletion/revocation policy;
- the AI proposal type, model availability/fallback, and review gate;
- physical-device and release evidence required.

Do not put a note entitlement in the target merely because a contact object has
a note property. Apple documents that note access requires additional approval.

## Authorization and limited-access decision

~~~text
status = CNContactStore.authorizationStatus(for: .contacts)

notDetermined
  -> explain feature
  -> request access
  -> limited | authorized | denied | restricted

limited
  -> query only approved contacts
  -> ContactAccessButton or access picker for expansion
  -> refresh projection

authorized
  -> direct fetch with smallest keys

denied/restricted
  -> manual or user-mediated fallback
~~~

Keep authorization state out of the contact row model. A row can be missing
because access narrowed, a record was deleted, an account is unavailable, a
predicate did not match, or a fetch failed. Map those causes into an explicit
feature state.

## Place and identity policy

Use a stable app-owned identity for the product record and store the current
Contacts identifier as an integration reference with a source/revision:

| Field | Role |
| --- | --- |
| App contact ID | Canonical identity in the app’s domain. |
| Contacts identifier | Current native-store resolution key. |
| Identity mode | Unified or individual, if it changes behavior. |
| Last resolved revision | Guard against stale action targets. |
| Selected property | Phone/email/other field chosen for this action. |
| Source authorization | Limited/full/picker/provider route. |

Do not deduplicate by localized name or phone string. If a user chooses two
records that look similar, present the ambiguity and keep both native IDs until
the user decides.

## Fetch policy

Choose keys per screen:

| Screen/action | Keys |
| --- | --- |
| Index | Identifier and formatter-required name keys. |
| Search result | Identifier, display name, and only the property shown. |
| Phone action | Identifier, formatter keys, phone numbers. |
| Email action | Identifier, formatter keys, email addresses. |
| Edit | Identifier and fields the edit form can change. |
| AI proposal | Only user-selected, minimized fields; never the whole store. |

Use a CNContactFetchRequest for a bounded enumeration. Set its predicate,
keysToFetch, unifyResults, mutableObjects, and sortOrder intentionally. The
framework supports its own contact predicates but not arbitrary compound
predicates. If the product needs compound filtering, fetch a bounded
projection and filter that projection in the app.

For an index:

~~~text
fetch identifiers
  -> persist app-owned index revision
  -> batch detail fetch for visible IDs
  -> replace projections atomically
~~~

If the screen only needs a single contact, use the identifier helper and do not
enumerate the whole store. All synchronous fetch calls should run away from
the main actor.

## Notification and change-history route

The simplest safe route is notification plus full refetch:

1. Observe CNContactStoreDidChangeNotification.
2. Coalesce notifications.
3. Cancel a previous projection task.
4. Re-fetch identifiers and visible fields.
5. Replace the app-owned projection with a new revision.
6. Mark open AI proposals stale if their source ID or field changed.

Use change history when the cost of a full refetch is material and the app can
ship the required Objective-C bridge:

~~~text
stored token
  -> configure CNChangeHistoryFetchRequest
  -> Objective-C executes enumeratorForChangeHistoryFetchRequest:error:
  -> visitor maps events to Swift DTOs
  -> reducer applies all events
  -> persist currentHistoryToken with projection revision
~~~

The request should set:

- startingToken from the last successful result;
- additionalContactKeyDescriptors only for reducer fields;
- shouldUnifyResults according to identity policy;
- includeGroupChanges only when groups affect the feature;
- excludedTransactionAuthors for the app’s own reverse-domain author;
- mutableObjects only when the reducer actually needs mutable values.

If the starting token is nil, expired, or invalid, rebuild. A change-history
failure must not advance the stored token. Apply the complete event batch before
persisting the new token. Keep token and projection revision in one durable
commit so a crash cannot claim a token that the projection did not apply.

Apple’s TN3149 documents the Objective-C execution path and explicitly says the
enumerator call is unavailable in Swift. Treat that as an architecture
boundary, not a reason to use an undocumented selector.

## Mutation route

Use a draft and a commit:

~~~text
resolved native contact
  -> CNMutableContact copy
  -> user edits/AI suggestion
  -> deterministic field validation
  -> fresh CNSaveRequest
  -> execute
  -> re-fetch with action/display keys
  -> projection revision
~~~

Before execute:

- re-check that the native identifier resolves;
- verify the app still has the required access;
- validate phone/email/address field formats;
- select a writable container for new contacts;
- show the exact field changes;
- require confirmation for destructive deletion;
- set transactionAuthor if the app reconciles its own changes.

After execute, map errors. If the record no longer exists, ask the person to
reselect; if an inserted record already exists, reconcile the draft; if a
container is not writable, preserve the draft and offer a different route.
Do not access mutable objects while the save request executes. If
shouldRefetchContacts is false, discard those objects after the save and
re-resolve.

## ContactProvider split

Use ContactProvider only for app-owned contacts that should be available to
system consumers. The provider extension is read-only to those consumers and
has its own target/process lifecycle.

The host app owns:

- canonical records and revisions;
- provider enable/disable/reset controls;
- source redaction and field selection;
- signal-enumerator requests.

The extension owns:

- deterministic page enumeration;
- generation markers and change anchors;
- changed/deleted projection;
- bounded process work and explicit error completion.

Do not use ContactProvider to bypass native Contacts authorization. Do not
display “Saved to Contacts” after an extension signal; the signal only asks the
system to enumerate the provider.

## SwiftUI/Liquid Glass route

Expose a state-driven native screen:

~~~text
ContactFeatureState
  access
  query
  list projection
  selection
  resolved action target
  freshness/revision
  review proposal
  commit result
  provider status (optional)
~~~

Use List and SearchField for content, semantic Button actions for access and
commit, and a compact glass action group for Search, Add Access, Review, and
Refresh. Keep the source, selected field, and freshness in readable text.
Material is not a substitute for a permission explanation or change-history
evidence.

## Typed AI handoff

Use an app-owned type such as:

~~~text
ContactProposal
  sourceContactID
  sourceFields
  sourceProjectionRevision
  proposedDisplayText or proposedDraft
  modelRoute/version
  validationState
  reviewerDecision
~~~

The deterministic validator must:

- resolve the source ID with the current required keys;
- compare the source projection revision;
- reject missing/unauthorized fields;
- reject invented phone/email destinations;
- validate any app-owned field limits;
- require explicit review before save/send/system handoff;
- invalidate the proposal after Contacts changes.

Foundation Models availability, an on-device response, or a typed generated
value does not authorize Contacts access or prove that a proposed identity is
correct.

## Verification route

| Layer | Proof |
| --- | --- |
| Source/API | Official Contacts docs, TN3149, final SDK headers. |
| Pure policy | Authorization mapping, key selection, identity reducer, token recovery, proposal validator. |
| Swift compile | Swift authorization/fetch/save/request-configuration snippets against named SDK. |
| Objective-C bridge compile | Change-history enumerator and visitor adapter in the actual bridge target. |
| SwiftUI UI test | Permission states, search, stale/retry, review, commit conflict, accessibility. |
| Simulator | Deterministic fixtures and UI layout; not account or physical system proof. |
| Physical iPhone | Contacts permission, limited set, Settings revocation, fetch/save, change history, account state. |
| Signed archive/TestFlight | Entitlements, usage descriptions, bridge target, release UI/privacy behavior. |

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
- [additionalContactKeyDescriptors](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/additionalcontactkeydescriptors)
- [CNFetchResult](https://developer.apple.com/documentation/contacts/cnfetchresult)
- [currentHistoryToken](https://developer.apple.com/documentation/contacts/cnfetchresult/currenthistorytoken)
- [CNSaveRequest](https://developer.apple.com/documentation/contacts/cnsaverequest)
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

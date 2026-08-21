# SwiftUI Contacts store and change-history proof matrix

This matrix prevents a Contacts feature from claiming more than its evidence
supports. Contacts has independent authorization, field, identity, change,
mutation, system-projection, accessibility, and release contracts.

## Claim-to-evidence matrix

| Claim | Minimum fixture or inspection | Strong evidence | Does not prove |
| --- | --- | --- | --- |
| The app explains why it needs Contacts | Target Info.plist and UX copy review | On-device first-run review with the exact feature | That the person granted access |
| Authorization is handled correctly | CNAuthorizationStatus fixture | Physical iPhone reset through not-determined, limited, full, denied, restricted | That every contact or field is readable |
| Limited access is respected | Approved identifier set and revoked-ID fixture | Physical Settings/access-control changes followed by refetch | That an empty list means no contacts exist |
| Only needed keys are fetched | Key-selection table and fetch request inspection | Runtime/log redaction test proving no unneeded fields enter the projection | That a later view can read a field it did not request |
| Search uses supported predicates | Predicate fixture for name/email/phone/ID | Physical search across localized names and formatted numbers | That arbitrary compound predicates work |
| Unified identity is intentional | Unified/individual identity fixture | Physical linked-account/contact test with source/re-resolution evidence | That a name or phone number is a canonical ID |
| Cached records recover after a store change | Notification reducer fixture | Physical Contacts edit/delete/access-narrow test and refetch | That notification contains the changed record |
| Incremental change history is correct | Synthetic token/event reducer fixture | Actual Objective-C bridge target with initial, incremental, reset, and invalid-token runs | That a Swift-only enumerator call is valid |
| Change tokens are durable | Token plus projection revision fixture | Crash/relaunch test proving both advance atomically | That the token can be inspected or interpreted by the app |
| Save commits the intended change | CNSaveRequest draft/error fixture | Physical add/update/delete with re-fetch and visible Contacts confirmation | That a save callback proves user intent or external sync |
| Mutation conflicts are handled | Record-missing/duplicate/writable-container errors | Physical concurrent or stale-record scenario with preserved draft | That last-change-wins is a conflict-resolution product |
| ContactProvider is separate | Two-authority architecture fixture | Signed host/extension archive plus enabled/disabled Settings and Phone/Mail behavior | That provider signal proves consumer display |
| AI is subordinate | Typed proposal/revision validator tests | On-device model availability/refusal/stale-source review with explicit commit | That model output grants access or proves identity |
| Glass is native and accessible | State previews with material and non-material fallback | Physical VoiceOver/Dynamic Type/reduced-transparency task completion | That visual polish proves data correctness |
| Release is configured | Archive entitlements/Info.plist inspection | TestFlight signed build on the named device and target | That a local Debug run is distributable |

## Fixtures

Keep fixtures synthetic and field-minimized:

~~~text
AuthorizationFixture
  status: notDetermined | limited | authorized | denied | restricted
  requestedEntity: contacts
  usageDescriptionPresent: Bool

ContactProjectionFixture
  appID: stable app-owned identifier
  nativeID: redacted test identifier
  identityMode: unified | individual
  keys: identifier + requested fields
  revision: monotonically increasing local revision

ChangeHistoryFixture
  startingToken: nil | opaque bytes
  event: drop | add | update | delete | group-change
  resultToken: opaque bytes
  error: expired | invalidAnchor | invalidRequest | other

MutationFixture
  operation: add | update | delete
  currentResolution: present | missing | unauthorized
  container: writable | unavailable
  result: committed | conflict | validationFailure

ProposalFixture
  sourceContactID
  sourceRevision
  fieldsExplicitlySelectedByPerson
  proposedValue
  modelAvailability
  reviewerDecision
~~~

Never put a real person’s name, phone number, email, address, note, image, or
contact database identifier into a committed fixture.

## Pure policy checks

Test these without Contacts I/O:

- authorization status maps to the correct UI state;
- a limited access state does not expose an all-contacts empty-list claim;
- a key policy selects no more than the current action needs;
- a compound app filter runs only on an app-owned minimized projection;
- unified versus individual identity is preserved in the projection;
- a store revision change invalidates an open proposal;
- a missing identifier becomes needsReselect, not a same-name substitution;
- a drop-everything event clears the projection before adds apply;
- an expired/invalid token triggers full rebuild and does not advance the old
  token;
- a token is persisted only with the projection revision it produced;
- transaction-author filtering does not claim authorship identity;
- duplicate/missing/writable-container errors preserve a draft;
- an AI proposal cannot invent a native destination or bypass confirmation;
- a ContactProvider projection cannot be labelled as a native write.

## Swift and bridge checks

The Swift route should compile and be checked for:

- async requestAccess usage;
- CNContactFetchRequest construction with at least one key;
- supported Contacts predicates;
- identifier batch resolution;
- CNSaveRequest construction, transaction author, and re-fetch policy;
- CNChangeHistoryFetchRequest property configuration only;
- CNChangeHistoryEventVisitor overloads with the current Swift importer;
- explicit handling of the fact that the change-history enumerator is
  unavailable in Swift.

The Objective-C bridge target must separately compile and test:

- CNContactStore enumeratorForChangeHistoryFetchRequest:error:;
- visitor adoption and event delivery;
- nil/expired/invalid starting tokens;
- currentHistoryToken extraction;
- error-to-Swift DTO mapping;
- autorelease-pool and bounded-memory behavior for event batches;
- bridge cancellation/lifetime behavior if the app exposes async work.

Do not make a green Swift compile the evidence for the Objective-C method that
Apple marks unavailable in Swift.

## Physical device task matrix

| Task | Setup | Observe | Record |
| --- | --- | --- | --- |
| First authorization | Fresh app install or reset permission | Prompt copy, limited/full/deny choice | Screen recording and status log with redacted fields |
| Limited access | Choose a small known set | Approved IDs resolve; unapproved IDs do not; Add Access works | Before/after set and app projection revision |
| Settings revocation | Remove a previously approved contact | Cached row becomes stale or disappears after refetch | Notification, refetch, and user-facing state |
| Search | Controlled contacts with localized names and phone formats | Supported predicates return expected records | Query, keys, count, and redacted result IDs |
| Unified identity | Linked records/accounts if available | Unification/re-resolution behavior | Identity mode and source notes |
| Native edit | Add/update a harmless test contact | Save error/success then re-fetch | Operation ID, error code, re-fetched projection |
| Native delete | Delete only a test contact | Record-missing behavior on stale draft | Confirmation and recovery path |
| Change history | Objective-C bridge with controlled edits | Initial reset, incremental events, token advance | Event summary, token hash, projection revision |
| Store notification | Change Contacts from another path | Debounced refetch and stale proposal | Notification timestamp and new revision |
| Provider route | Signed ContactProvider target | Settings enable/disable and system consumer projection | Provider generation/signal, not just host UI |
| Accessibility | VoiceOver, Dynamic Type, reduced transparency | Complete choose/review/commit task | Task result and issues |

Use redacted IDs or cryptographic hashes in logs. Never record raw contact
fields in screenshots or analytics.

## Failure and recovery matrix

| Failure | Expected reducer state | Recovery |
| --- | --- | --- |
| No usage description / missing target configuration | configurationError | Fix target before distribution. |
| Authorization denied | denied | Settings/manual path. |
| Limited record revoked | needsReselect or stale | Refetch and choose again. |
| Unauthorized key | keyPolicyError | Reduce keys or fix approved entitlement. |
| Predicate invalid | queryError | Use documented Contacts predicate or app-side filter. |
| Contact store changed | refreshing | Coalesce and refetch; invalidate dependent proposal. |
| Token expired/invalid | rebuilding | Clear projection/token and rebuild. |
| Bridge unavailable | historyUnavailable | Use notification/full-refetch fallback or block incremental mode. |
| Record does not exist | conflict | Re-resolve and preserve draft. |
| Inserted record already exists | conflict | Reconcile identifier and current store. |
| No writable container | destinationUnavailable | Choose another container or use system editor. |
| Validation error | draftInvalid | Focus the field; keep user input. |
| ContactProvider disabled | providerUnavailable | Keep app-owned contacts available in-app. |
| Model unavailable/refuses | deterministicReview | Manual fields and explicit confirmation. |

## Archive and release evidence

For the signed target, inspect:

- deployment target and SDK;
- NSContactsUsageDescription;
- Contacts capability and any approved notes entitlement;
- Objective-C bridge module/target membership;
- ContactProvider extension target membership if used;
- privacy manifest and required-reason declarations when relevant;
- build configuration, bundle identifiers, and provisioning profile;
- TestFlight metadata and privacy copy.

The release checklist must separately state:

~~~text
Swift route compiled: yes/no
Objective-C change-history bridge compiled: yes/no
simulator UI fixture: yes/no
physical Contacts permission/fetch/save: yes/no
physical change history/notification: yes/no
ContactProvider system consumer: yes/no/not applicable
VoiceOver/Dynamic Type/reduced transparency: yes/no
archive entitlements and target graph: yes/no
TestFlight signed build: yes/no
production behavior: unverified until observed
~~~

## Sources

- [Contacts](https://developer.apple.com/documentation/contacts)
- [Accessing the contact store](https://developer.apple.com/documentation/contacts/accessing-the-contact-store)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [CNAuthorizationStatus](https://developer.apple.com/documentation/contacts/cnauthorizationstatus)
- [CNAuthorizationStatus.limited](https://developer.apple.com/documentation/contacts/cnauthorizationstatus/limited)
- [CNContactFetchRequest](https://developer.apple.com/documentation/contacts/cncontactfetchrequest)
- [keysToFetch](https://developer.apple.com/documentation/contacts/cncontactfetchrequest/keystofetch)
- [predicate](https://developer.apple.com/documentation/contacts/cncontactfetchrequest/predicate)
- [CNChangeHistoryFetchRequest](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest)
- [startingToken](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/startingtoken)
- [additionalContactKeyDescriptors](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/additionalcontactkeydescriptors)
- [CNFetchResult](https://developer.apple.com/documentation/contacts/cnfetchresult)
- [currentHistoryToken](https://developer.apple.com/documentation/contacts/cnfetchresult/currenthistorytoken)
- [CNChangeHistoryEventVisitor](https://developer.apple.com/documentation/contacts/cnchangehistoryeventvisitor)
- [CNSaveRequest](https://developer.apple.com/documentation/contacts/cnsaverequest)
- [CNError](https://developer.apple.com/documentation/contacts/cnerror)
- [ContactProvider](https://developer.apple.com/documentation/contactprovider)
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

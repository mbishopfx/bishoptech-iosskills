# SwiftUI File Provider document-domain proof matrix

File Provider behavior spans a host app, an extension process, shared storage,
the Files system surface, a remote service, and other apps. This matrix keeps
those evidence layers separate.

## Claim-to-evidence matrix

| Claim | Minimum inspection or fixture | Strong evidence | Does not prove |
| --- | --- | --- | --- |
| The feature needs File Provider | Route decision record | A second app opens a provider item through Files on the target device | That an in-app Files-like list needs an extension |
| The extension is embedded | Target graph and archive inspection | Signed TestFlight build with provider visible in Files | A successful host-app Debug run |
| The domain is stable | Domain catalog fixture | Relaunch, extension restart, and account reauth preserve domain identity | A display name or email string |
| Replicated behavior is selected intentionally | Domain initializer and target audit | Physical device observes system-managed local copy and re-materialization | A domain object created in a unit test |
| Nonreplicated behavior is selected intentionally | Extension subclass and URL mapping audit | Physical placeholder, download, edit, release, and redownload path | A local file in the host app container |
| Item identity survives rename/move | Stable-ID fixture | Rename/reparent in Files and re-resolve after relaunch | Matching by filename |
| Folder pages are correct | Synthetic ordered collection and cursor fixtures | Physical scroll through a large remote folder with insertion and retry | One page with five mock items |
| Change anchors are correct | Cursor/reducer fixture | Remote edit, delete, move, crash/relaunch, and expired-anchor reset | An anchor value printed in a log |
| Working set is current | Working-set membership fixture | Recent/favorite/tag/shared/Recently Deleted behavior and Spotlight/Files observations | A single folder enumeration |
| Open document changes are delivered | Document-only change fixture | Two apps or devices edit the file and the open presenter reacts | Polling the URL |
| Placeholders are valid | Metadata and designated placeholder URL fixture | Another app reads metadata, then coordinated read materializes content | A placeholder filename visible in the host UI |
| Materialization is safe | Same-volume temporary directory fixture | Dataless-to-materialized open, cancellation, retry, and extension restart | Returning a URL from an arbitrary temp directory |
| Eviction is non-destructive | Clean/dirty/open/nonevictable fixtures | Remove Download in Files, then reopen and observe re-download or correct refusal | Deleting the remote item |
| Coordinated I/O is correct | FileCoordinator and presenter harness | Cross-process edit with external URL and security-scoped cleanup | FileManager write from one process |
| Security-scoped access is bounded | Bookmark fixture and access-count logging | Relaunch, stale bookmark, read/write, and stop-access cleanup on device | Holding a URL in a SwiftUI selection |
| Error semantics are recoverable | Provider error reducer fixtures | Offline, auth expiry, no-such-item, collision, quota, and reconnect on device | Mapping every error to “try again” |
| SwiftUI state is honest | State fixture for dataless/upload/conflict | Dynamic Type, VoiceOver, reduced transparency, offline, and retry task | A visual glass screenshot |
| AI is subordinate | Typed proposal/revision fixtures | Local model unavailable/refusal, stale source, review, deterministic validation, provider commit | Model output alone or a suggested filename |
| Privacy is bounded | Redacted fixture and target audit | Logs, analytics, prompts, and screenshots contain no raw document or credential data | A privacy label without runtime review |
| Release is ready | Archive entitlements and target inspection | TestFlight build on named iPhone/iPad with Files and second-app flow | Simulator provider visibility |

## Fixture model

Use synthetic, field-minimized records:

~~~text
DomainFixture
  domainID
  displayName
  accountState: connected | disconnected | disabled | removed
  replicated: Bool
  userEnabled: Bool

ItemFixture
  itemID
  domainID
  parentID
  filename
  contentType
  metadataRevision
  contentRevision
  capabilities
  localState: dataless | materialized | dirty | evicted

PageFixture
  requestedSort
  pageToken
  resultIDs
  nextToken
  remoteRevision

ChangeFixture
  startingAnchor
  updates
  deletions
  resultingAnchor
  moreComing
  error: none | expired | invalid | unavailable

ProposalFixture
  itemID
  sourceRevision
  selectedScope
  typedProposal
  validationState
  reviewerDecision
~~~

Do not use real filenames, document bytes, URLs, customer IDs, credentials,
or security-scoped bookmarks in committed fixtures.

## Pure reducer and policy checks

Test these without Files, a network, or an AI model:

- a filename or display name never becomes the canonical provider ID;
- a rename and reparent preserve item identity;
- a missing parent or item becomes a recoverable no-such-item state;
- page cursors are deterministic and include the remote revision needed to
  detect invalidation;
- page results do not duplicate or skip items when a next page is requested;
- a bad or expired anchor triggers a reset and does not advance the old
  checkpoint;
- the current anchor is persisted only after the complete change batch is
  applied;
- a working-set update uses the item’s real parent identifier;
- a document enumerator returns only the opened document;
- a provider capability gates a UI action and a direct request is still
  handled by the provider;
- dataless, materialized, dirty, uploading, and evicted are distinct states;
- eviction never maps to remote deletion;
- an AI proposal records item ID and source revision;
- a changed revision invalidates a pending proposal;
- AI output cannot invent a parent ID or bypass capability validation;
- errors preserve drafts and expose a retry or repair path.

## Extension and host compile checks

For the selected provider model, compile:

- host app SwiftUI target;
- File Provider extension target;
- shared domain/item/reducer module;
- any Objective-C or C bridge only if the project actually needs one;
- current SDK availability checks and deployment target.

Inspect that:

- NSFileProviderManager and NSFileProviderDomain use the current Swift
  importer names;
- replicated and nonreplicated protocol requirements are not mixed;
- NSFileProviderItem metadata satisfies the platform’s required fields;
- enumerator methods use the current observer and page/anchor types;
- completion handlers are called on every success, error, and cancellation
  path;
- provider target membership and extension point are present.

An app-target typecheck does not prove the extension target is valid.

## Physical-device task matrix

| Task | Setup | Observe | Record |
| --- | --- | --- | --- |
| Add domain | Fresh install and connected test account | Domain appears, display name is truthful, no duplicate identity | Domain ID hash and visible state |
| Account repair | Expire or disable the test account | Domain enters disconnected/not-authenticated state without deleting data | Error, repair path, reconnect result |
| Browse root | Large controlled remote folder | Stable order, pagination, loading/error/empty state | Page token hashes and item IDs |
| Rename and move | Use Files and host app | Same item ID resolves under new parent/name | Before/after identity and parent |
| Download | Open dataless file from second app | Download, progress, cancellation, and materialized read | Content revision and transfer result |
| Offline open | Materialize a file, disable network | Local file opens; remote state is honest | Offline UI and retry result |
| Remote change | Edit from another account/device | Working set and open-document enumerator update | Change anchor revision |
| Conflict | Make local and remote edits | Draft preserved and resolution shown | Conflict state and final item revision |
| Eviction | Evict clean file, then reopen | Local content removed without remote deletion; redownload works | Eviction error/success |
| Placeholder | Nonreplicated provider and another app | Metadata is available before content; coordinated read materializes | Placeholder/materialization timestamps |
| Security scope | Pick directory, relaunch, resolve bookmark | Access starts/stops and stale bookmark is handled | Access lifetime and recovery |
| Extension restart | Force host/extension relaunch where supported | Durable item state and outbox resume | Replayed operation result |
| Accessibility | VoiceOver, Dynamic Type, reduced transparency, increased contrast | Complete browse/download/open/recover task | Task completion and focus issues |
| AI proposal | Select a synthetic local document | Proposal is local/bounded, reviewable, revision-bound | Model state, validation, reviewer action |

Capture no raw document bytes, filenames containing personal data, account
tokens, or security-scoped URLs in logs or screenshots.

## Failure and recovery matrix

| Failure | Expected state | Recovery |
| --- | --- | --- |
| Extension missing from archive | configurationError | Fix target membership and archive |
| Domain add collision | domainReconcile | Re-list and compare stable ID |
| Domain disabled/disconnected | unavailable | Show account/settings repair |
| noSuchItem | stale | Refresh parent and preserve safe draft |
| serverUnreachable | offline | Use materialized content and retry |
| notAuthenticated | needsAuthentication | Reauthenticate before reconnect |
| expired anchor | rebuilding | Clear cursor and re-enumerate |
| invalid page | reloading | Restart from a valid initial page |
| filename collision | conflict | Resolve/rename according to provider policy |
| dirty item cannot evict | remainsMaterialized | Finish upload or keep local copy |
| open file blocks eviction | inUse | Wait for presenter/claims |
| provider crash | relaunching | Recover durable state and idempotently retry |
| stale security bookmark | accessRepair | Ask the person to select the location again |
| AI unavailable/refused | manualReview | Preserve deterministic filename/folder flow |

## SwiftUI and Liquid Glass review

Check that:

- the domain name and current folder remain visible;
- system controls carry the primary navigation and action semantics;
- custom glass is limited to a semantic group;
- status text is available without color or blur;
- focus rings, separators, and row boundaries survive transparency changes;
- a row can be used with VoiceOver and Switch Control;
- long filenames and large text do not erase the only item identity;
- download and upload state do not claim remote durability too early.

## Archive and release evidence

For a signed archive, record:

~~~text
host target compiled: yes/no
provider target compiled: yes/no
provider embedded: yes/no
App Group/document group: yes/no
domain target and availability: yes/no
privacy manifest/strings: yes/no
entitlements/profile: yes/no
Files system surface: yes/no
second-app open/edit: yes/no
physical device: yes/no
TestFlight: yes/no
production sync: unverified until observed
~~~

## Sources

- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [NSFileProviderExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderextension)
- [NSFileProviderDomain](https://developer.apple.com/documentation/fileprovider/nsfileproviderdomain)
- [NSFileProviderManager](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager)
- [NSFileProviderEnumerator](https://developer.apple.com/documentation/fileprovider/nsfileproviderenumerator)
- [NSFileProviderSyncAnchor](https://developer.apple.com/documentation/fileprovider/nsfileprovidersyncanchor)
- [NSFileProviderItem](https://developer.apple.com/documentation/fileprovider/nsfileprovideritemprotocol)
- [NSFileProviderContentPolicy](https://developer.apple.com/documentation/fileprovider/nsfileprovidercontentpolicy)
- [Defining your File Provider’s content](https://developer.apple.com/documentation/fileprovider/defining-your-file-provider-s-content)
- [Synchronizing the File Provider extension](https://developer.apple.com/documentation/fileprovider/synchronizing-the-file-provider-extension)
- [Tracking your File Provider’s changes](https://developer.apple.com/documentation/fileprovider/tracking-your-file-provider-s-changes)
- [Tracking changes to documents](https://developer.apple.com/documentation/fileprovider/tracking-changes-to-documents)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [Providing access to directories](https://developer.apple.com/documentation/uikit/providing-access-to-directories)
- [NSURL](https://developer.apple.com/documentation/foundation/nsurl)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI File Provider deep dive](../42-framework-deep-dives/137-swiftui-file-provider-document-domain-route.md)
- [SwiftUI File Provider design](../21-design-deep-dives/165-swiftui-file-provider-document-domain-route-design.md)
- [SwiftUI File Provider capability route](../50-capability-recipes/168-swiftui-file-provider-document-domain-route.md)
- [SwiftUI File Provider code recipes](../70-code-recipes/180-swiftui-file-provider-document-domain-recipes.md)

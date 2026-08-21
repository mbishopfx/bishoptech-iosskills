# SwiftUI File Provider, document domains, and synchronized file workflows

File Provider is the system integration route for an app that wants its
documents to appear in Files and in other apps while remaining backed by a
remote or app-owned storage service. It is not a replacement for every local
document workflow. If the product only needs to open or export a file, use the
SwiftUI file importer/exporter or a document picker. If the product needs to
present a browsable, synchronized provider to the system, choose a File
Provider extension deliberately.

The boundary for this route is:

~~~text
user outcome
  -> local-only document, external document, or provider-backed document?
  -> document target and App Group configuration
  -> domain/account lifecycle
  -> stable item identity and metadata
  -> page or change enumeration
  -> placeholder/materialization or system replication
  -> coordinated I/O and remote sync
  -> SwiftUI state and optional typed AI proposal
  -> accessibility, physical-device, archive, and release proof
~~~

This page is intentionally separate from the existing SwiftUI document
workflow page. That page covers DocumentGroup, FileDocument, fileImporter,
fileExporter, security-scoped URLs, and local document editing. This page
covers the provider target and the contracts that make a provider visible and
reliable outside the host app.

## Choose the smallest document authority

| Product need | Native route | Provider responsibility |
| --- | --- | --- |
| Create and edit files only inside the app | FileDocument, DocumentGroup, or app-owned storage | None |
| Let a person choose a file or directory from Files or another provider | SwiftUI fileImporter/fileExporter or UIDocumentPickerViewController | None |
| Share a local Documents directory in place | UIFileSharingEnabled and LSSupportsOpeningDocumentsInPlace where appropriate | Keep local file coordination correct |
| Expose a remote hierarchy to Files and other apps | File Provider extension | Identity, enumeration, sync, permissions, errors, and user-visible lifecycle |
| Make an app-owned contact or record source visible to system consumers | The framework-specific provider, such as ContactProvider | Use the provider contract; do not relabel it as a File Provider |

Do not add a provider target simply because a screen looks like Files. A
Files-like SwiftUI browser can be entirely app-owned. Add File Provider when
the system must browse or open the content outside the app and the provider
needs to own the cross-process contract.

## Two provider models

Apple documents two starting points:

| Model | System owns | Extension owns | iOS availability in Apple’s framework overview | Best fit |
| --- | --- | --- | --- | --- |
| Replicated provider | Local copies of metadata and content, including dataless/materialized state | Remote metadata, content fetch/upload, change publication, domain state | iOS 16 and later | Remote storage where the system should manage local copies |
| Nonreplicated provider | The provider extension process and its system-facing requests | Local file placement, placeholders, downloads, uploads, and URL mapping | iOS 11 and later | A provider that must manage its own local file cache and placeholder lifecycle |

For a replicated provider, adopt
NSFileProviderReplicatedExtension and NSFileProviderEnumerating. Implement a
provider item model, a remote enumerator, and the required item/content/mutation
operations. The system creates the local hierarchy from the metadata you
return and takes ownership of file URLs handed to it.

For a nonreplicated provider, subclass NSFileProviderExtension. Implement the
class methods that map item identifiers to stable URLs, provide placeholders,
materialize a file when requested, respond when access ends, and react to a
coordinated change. Apple’s current class documentation says to override the
extension methods, even when a method has an empty implementation, and not to
call super from those implementations.

Do not mix the lifecycle assumptions. A nonreplicated implementation cannot
silently rely on the system to maintain a materialized working set. A
replicated implementation cannot treat the URL passed to fetchContents as a
permanent file it still owns after the completion handler.

## Target, domain, and App Group contract

### Extension target

Create the File Provider extension target from Xcode’s extension templates and
keep the host app and extension as separate targets. Verify target membership,
bundle identifiers, extension point configuration, entitlements, privacy
manifest requirements, and deployment target in the final archive. A green
host-app build does not prove that the provider target is embedded or
launchable.

The provider’s shared document storage is derived from the
NSExtensionFileProviderDocumentGroup configuration. Apple describes that
location as the File Provider Storage directory inside the corresponding
shared container. Use an App Group container for the state and files that
must be shared by the host app and extension. Keep authentication refresh
tokens and provider database state in a deliberately designed protected
store; do not assume that a shared path alone is a security boundary.

### Domains are account or location partitions

An NSFileProviderDomain can represent an account, workspace, or location. A
single provider can expose multiple domains as if multiple providers were
installed. Prefer explicit domains for a product that may support more than
one account or location. The default domain is not a migration target for
replicated conversion, so a product that may evolve should avoid making the
default domain its only long-term identity.

Domain identifiers must be stable for the same logical domain and must not
contain the characters slash or colon. The display name is user-visible and
may change without changing identity. User info is provider-defined state, not
a place for secrets or a replacement for the domain identifier.

The host app normally:

1. Loads the app-owned account/location catalog.
2. Maps each enabled logical record to a stable domain identifier.
3. Creates a replicated domain with identifier and display name, or a
   nonreplicated domain with a document-storage-relative path.
4. Adds it with NSFileProviderManager.add.
5. Treats an add failure as a configuration or lifecycle state, not as an
   empty folder.
6. Lists existing domains on launch and reconciles user-enabled,
   disconnected, hidden, and removed states.
7. Removes a domain with an explicit removal mode only after the product
   explains what happens to dirty or downloaded local data.

When the extension is instantiated for a domain, it must be able to recover
from a fresh process with no in-memory assumptions. Persist remote cursors,
outbox state, item identity mappings, revisions, and auth state in durable
storage. The system can create several provider instances or discard one and
create another. A replicated instance receives invalidate before it is
discarded; release references and cancel owned work there.

### Disconnect and reconnect

If a provider temporarily cannot serve a domain, model disconnected as a
first-class state. Keep browsing and existing local data behavior aligned with
the documented contract, surface a useful user-facing reason, and reconnect
only after the underlying account or service state is actually ready. A
network timeout is not permission to delete the domain.

## Item identity is a synchronization key

The item identifier is not a filename, a user-visible URL, a bearer token, or a
model prompt field. Apple warns that item identifiers should not contain
sensitive information because they may appear in logs and diagnostics.

Store a provider-owned stable identifier for every file and folder. The
identity must survive:

- app relaunch and extension termination;
- device restore and domain rehydration where the provider can preserve it;
- remote renaming and reparenting;
- pagination;
- retries after a crash;
- a user opening the same document from a second app.

An item’s parent identifier and filename form its current location. Changing
the location is a metadata mutation, not a new identity. A path-derived
identifier is safe only when the product guarantees that moving or renaming is
not an identity-preserving operation. For most remote stores, a server object
ID or opaque app-owned UUID is safer.

Return metadata consistently:

| Field | Design rule |
| --- | --- |
| itemIdentifier | Stable, opaque, non-sensitive provider ID |
| parentItemIdentifier | Actual hierarchy parent; for working-set results, do not use workingSet as the parent |
| filename | Nonempty, complete with extension, localized only if that is the actual provider name |
| contentType | Prefer current Uniform Type Identifier values on supported iOS targets |
| capabilities | Grant only the actions the provider can actually reconcile |
| itemVersion | Change contentVersion when bytes or resource fork changes; use metadataVersion for metadata state |
| documentSize and dates | Return truthful values or nil when unavailable; do not fabricate progress metadata |
| uploaded/uploading and errors | Reflect remote sync state, not merely a local queue insertion |
| user-visible fields | Keep personal names, tags, shares, and owner metadata scoped to the user who owns them |

Never use a same-name file as an identity fallback after a provider ID is
missing. Return a documented no-such-item or conflict outcome and let the
product reselect or reconcile.

## Enumeration is a cursor contract

An enumerator may serve a folder, the working set, the trash container, a
single document’s live changes, or the system-managed materialized/pending set.
The system calls the provider’s enumerator factory with identifiers such as
rootContainer, workingSet, trashContainer, or a directory’s itemIdentifier.

### Item pages

For folder enumeration:

1. Honor the initial sorting page, sorted by name or date.
2. Return a deterministic sequence across pages.
3. Send items through the enumeration observer.
4. Finish with a next page when more items exist, or nil when complete.
5. Treat the page as an opaque cursor, not an offset that becomes invalid when
   remote insertion changes the collection.

Apple’s header limits page data to 500 bytes and notes that a badly sorted
second page can produce visible reorder animations. Encode a compact,
versioned cursor such as a server query revision plus the last stable sort key
and item ID. Keep the cursor independent of personal filenames when possible.
Use the observer’s suggested page size but enforce your own bounded memory and
latency limits. If the remote service is slow, return readily available items
or an appropriate provider error rather than hanging an extension call.

### Change enumeration

Change enumeration uses an NSFileProviderSyncAnchor. The anchor is opaque data
that identifies the last successfully reported change batch. Apple’s current
header limits the combined anchor to 500 bytes and retains only the latest
anchor passed to the system.

The reducer contract is:

~~~text
starting anchor
  -> read remote changes after anchor
  -> emit updated item metadata
  -> emit deleted item identifiers
  -> finish with a new anchor and moreComing
  -> persist the remote cursor only after the provider has committed the batch
~~~

If an anchor expires, is invalid, or cannot be interpreted against the remote
revision, finish with the documented expired-anchor error. The system can
discard cached data and restart enumeration from nil. Do not silently treat a
bad anchor as “no changes”; that creates permanent drift.

Use a separate change log or remote API cursor that can answer “all changes
after X” across the working set. Do not make the change anchor a local wall
clock unless the server guarantees a total, durable order. If the service only
offers snapshots, implement a bounded snapshot-diff strategy and make the
reset cost visible in tests.

When remote content changes, signal the affected container. For replicated
providers, the working set signal is the important route; the system propagates
updates to the UI. For nonreplicated providers, signal active containers as
well as workingSet when their content changes. Moving an item requires checking
both the old and new parents.

### Working set and document enumerators

The working set is not a second visible folder. It is the provider’s durable
set of recent, tagged, favorited, shared, and recently deleted items that
should remain discoverable and available for Spotlight/offline use. Keep the
working set consistent across devices and update it when the user-visible
state changes.

When an app opens a provider-backed document, the system may request an
enumerator for that document. Its change results must contain only the
document being monitored. Use that route to report remote edits to an open
document so UIDocument or NSFilePresenter consumers can respond.

## Dataless, materialized, placeholder, and eviction states

The same item can move through multiple local states:

~~~text
remote metadata known
  -> dataless metadata/placeholder
  -> materialized content
  -> modified locally / upload pending
  -> uploaded and evictable
  -> dataless again
~~~

### Replicated providers

The system manages local copies. A dataless file has metadata but not content;
a dataless folder has not necessarily had its children enumerated. A
materialized document includes content, and a materialized folder has its
children represented locally.

Implement fetchContents with a temporary file on the same volume as the
user-visible location. The system takes ownership of the URL passed to the
completion handler and may clone/unlink it after completion. If the extension
needs a copy, clone it first. Honor cancellation and return a Progress that
reflects actual work.

Use NSFileProviderContentPolicy when the item’s download/eviction behavior
needs to differ from the inherited policy. On iOS, the lazy-and-evict-on-
remote-update policy is the default for the root; an eagerly kept-downloaded
item has a different storage and network contract. Do not use eager policy as
a visual convenience for every file.

The host app can request a download, reimport an item tree, inspect global
upload/download progress, or ask the manager to evict an item. Eviction is
not deletion: it removes a clean local content copy and leaves the provider
able to materialize it again. Dirty, open, or explicitly nonevictable content
can make eviction fail. Treat an eviction error as a state to explain, not a
signal to delete the remote object.

### Nonreplicated providers

Use NSFileProviderManager.placeholderURL(for:) and
writePlaceholder(at:withMetadata:) to create the designated placeholder
before handing an external URL to another app. In the extension’s
providePlaceholderAtURL implementation, write metadata and complete.

When a coordinated reader accesses a placeholder,
startProvidingItem(at:completionHandler:) must put the real file at the
provider’s stable URL before completing. When the last claim is released,
stopProvidingItem(at:) may remove the content to free space, but it must leave
the placeholder behind. Do not replace a file eagerly while another app is
still reading or editing it.

For a nonreplicated provider, keep the URL-to-identifier mapping static and
within documentStorageURL. The same identifier must always map to the same
file location. A security-scoped URL granted to a host app is not permission
for the extension to manipulate arbitrary locations.

## Coordinated reads and writes

File Provider content is cross-process. Always use NSFileCoordinator for
external documents and honor the provider’s purpose identifier where Apple
documents it. Use an NSFilePresenter or UIDocument when an app displays and
tracks an external document.

For the host app:

1. Keep security-scoped URL access alive for the smallest operation scope.
2. Call startAccessingSecurityScopedResource before accessing an external URL.
3. Coordinate reads and writes.
4. Release with stopAccessingSecurityScopedResource in a guaranteed cleanup
   path.
5. Save a security-scoped bookmark when durable re-access is genuinely
   required, not the raw URL.
6. Re-resolve and handle stale bookmarks after relaunch.

For the extension:

- Do not use a raw FileManager write as a substitute for coordination.
- Do not delete or replace a file from stopProviding while a presenter may
  still be active.
- Treat the URL from a document picker and the URL from
  getUserVisibleURL as separate authority paths.
- Use a provider-specific error domain or documented Cocoa error so the system
  can choose retry, alert, or re-creation behavior.

## SwiftUI and Liquid Glass composition

A provider-backed SwiftUI screen should show state, not a fake permanent
cloud badge:

| UI state | Native visual behavior |
| --- | --- |
| Loading page | Use a semantic progress indicator and stable row placeholders |
| Dataless/available | Show the item as available metadata with an explicit download action |
| Downloading | Bind a progress value and keep cancel/retry behavior discoverable |
| Upload pending | Show unsynced changes without implying remote durability |
| Offline | Keep materialized content usable; explain what will wait |
| Not authenticated/disconnected | Explain account state and offer a route to repair it |
| Conflict/no-such-item | Preserve the user’s draft or selection and ask for a new choice |
| Empty | Distinguish no items, no access, no network, and not-yet-enumerated |

Use List, NavigationStack, toolbar items, file labels, and semantic buttons as
the primary shell. Let current system controls receive the current Liquid
Glass treatment. Limit custom Glass and glass effects to a small hierarchy
such as a selected-item inspector, a download control cluster, or an
ephemeral review panel. Do not place a fully opaque glass layer over every row
or behind a busy file thumbnail grid.

Keep the folder hierarchy as the primary navigation structure. A custom
glass toolbar must not hide the current domain, offline status, or destructive
actions. Add accessibility labels and values that describe “available
offline,” “download required,” “upload pending,” and “conflict,” not merely
“glass button.”

## Optional on-device AI document proposals

Foundation Models can help propose a filename, summarize selected local
content, suggest a folder, or extract a typed set of metadata. It cannot grant
File Provider access, decide a security-scoped lifetime, establish a canonical
item identifier, prove upload completion, or commit a remote mutation without
the deterministic app route.

Use a proposal envelope:

~~~text
source item ID
source content revision
source content type and size
explicitly selected text or bounded local extraction
model availability and request state
typed proposal
validation errors
human review decision
committed provider mutation
~~~

Keep the prompt local and bounded. Do not send entire provider documents,
credentials, private names, or raw security-scoped URLs to a model unless the
user explicitly selected that content for the feature and the privacy
contract says how it is handled. If the source revision changes while the
proposal is pending, mark the proposal stale and regenerate or discard it.
Validate filenames, folder IDs, content types, and metadata against the
provider’s current item graph before showing a commit button.

Use the existing Foundation Models and protected local-AI routes for model
availability, typed output, refusal, revision, and fallback policy. The File
Provider route remains the authority for access and synchronization.

## Error and lifecycle rules

Map errors into product states:

| Provider condition | Product state | Recovery |
| --- | --- | --- |
| noSuchItem | stale or removed | Refresh parent and preserve a safe draft |
| serverUnreachable | offline/remote unavailable | Keep local materialized content; retry on signal |
| notAuthenticated | account repair required | Authenticate through the host app, then signal resolved |
| syncAnchorExpired | rebuilding | Clear remote cursor, re-enumerate, verify identity stability |
| filename collision | conflict | Rename deterministically or let the system resolve per contract |
| unsynced edits | cannot evict | Finish upload or retain local copy |
| nonEvictable/open file | in use | Wait for claims/presenter and retry |
| extension crash/termination | recoverable process loss | Reopen durable state; make operations idempotent |
| missing target/entitlement | configuration failure | Fix target graph before release |

Never put a network request, unbounded remote enumeration, or model generation
inside a main-actor view body. Bound work, cancel it when a folder or document
disappears, and make retry safe.

## Evidence ladder for a provider route

Keep the proof levels separate:

1. Source review: the target, APIs, identifiers, permissions, and errors match
   current Apple documentation and the installed SDK.
2. Compile proof: host app, provider target, shared module, and any extension
   code compile for the named iOS 26 deployment target.
3. Fixture proof: item identity, pagination, anchors, reset, conflicts,
   placeholders, materialization, eviction, and AI revision invalidation are
   tested without personal data.
4. Simulator proof: the host UI and basic document picker route behave in the
   simulator where the system supports them.
5. Physical-device proof: Files, a second consumer app, account/network
   transitions, background/relaunch, storage pressure, accessibility, and
   security-scoped handoff work on the target iPhone or iPad.
6. Signed/release proof: the provider target is embedded, entitlements and
   privacy configuration are present, TestFlight can launch the extension, and
   the intended system surface sees the domain.

A SwiftUI preview, a green host build, an empty enumeration, or a successful
local file write does not prove File Provider integration.

## Sources

- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [Replicated File Provider extension](https://developer.apple.com/documentation/fileprovider/replicated-file-provider-extension)
- [Nonreplicated File Provider extension](https://developer.apple.com/documentation/fileprovider/nonreplicated-file-provider-extension)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [NSFileProviderExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderextension)
- [NSFileProviderDomain](https://developer.apple.com/documentation/fileprovider/nsfileproviderdomain)
- [NSFileProviderManager](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager)
- [NSFileProviderEnumerator](https://developer.apple.com/documentation/fileprovider/nsfileproviderenumerator)
- [NSFileProviderEnumerating](https://developer.apple.com/documentation/fileprovider/nsfileproviderenumerating)
- [NSFileProviderSyncAnchor](https://developer.apple.com/documentation/fileprovider/nsfileprovidersyncanchor)
- [Defining your File Provider’s content](https://developer.apple.com/documentation/fileprovider/defining-your-file-provider-s-content)
- [Synchronizing the File Provider extension](https://developer.apple.com/documentation/fileprovider/synchronizing-the-file-provider-extension)
- [Tracking your File Provider’s changes](https://developer.apple.com/documentation/fileprovider/tracking-your-file-provider-s-changes)
- [Tracking changes to documents](https://developer.apple.com/documentation/fileprovider/tracking-changes-to-documents)
- [NSFileProviderItem](https://developer.apple.com/documentation/fileprovider/nsfileprovideritemprotocol)
- [NSFileProviderContentPolicy](https://developer.apple.com/documentation/fileprovider/nsfileprovidercontentpolicy)
- [NSFileProviderManager requestDownload](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager/requestdownloadforitem%28withidentifier%3Arequestedrange%3A%29)
- [NSFileProviderManager evictItem](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager/evictitem%28identifier%3Acompletionhandler%3A%29)
- [NSFileProviderManager temporaryDirectoryURL](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager/temporarydirectoryurl%28%29)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [Providing access to directories](https://developer.apple.com/documentation/uikit/providing-access-to-directories)
- [NSURL security-scoped URLs](https://developer.apple.com/documentation/foundation/nsurl)
- [App extension programming guide: Document Provider](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/FileProvider.html)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI document and file-workflow route](86-swiftui-document-apps-and-file-workflows.md)
- [File Provider capability route](../50-capability-recipes/168-swiftui-file-provider-document-domain-route.md)
- [File Provider proof matrix](../60-verification/162-swiftui-file-provider-document-domain-proof-matrix.md)
- [File Provider code recipes](../70-code-recipes/180-swiftui-file-provider-document-domain-recipes.md)

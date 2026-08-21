# SwiftUI File Provider document-domain capability route

Use this route when a product needs a provider-backed document hierarchy to
appear in Files or to be opened by other apps. Keep the host-app UI,
File Provider extension, shared storage, remote service, and optional
on-device AI as separate responsibilities.

## Route selection

| Outcome | Start here |
| --- | --- |
| Import one file | SwiftUI fileImporter or UIDocumentPickerViewController |
| Export one app-owned file | SwiftUI fileExporter or document picker |
| Edit an app-owned document | FileDocument/DocumentGroup |
| Share local Documents in place | Document sharing configuration and coordinated access |
| Expose a remote account in Files | Replicated File Provider extension |
| Own placeholders and a provider-managed local cache | Nonreplicated File Provider extension |

The provider route is a system integration, not a visual component. Plan its
target, domain, stable identity, change stream, error semantics, and release
evidence before building the SwiftUI browser.

## Capability contract

### Host app

- account or workspace catalog;
- authentication and reauthentication;
- domain add/remove/reconnect UI;
- user-facing privacy and sync explanations;
- SwiftUI browser and review flow;
- shared app/extension persistence;
- optional Foundation Models adapter for local proposals.

### File Provider extension

Replicated:

- NSFileProviderReplicatedExtension;
- NSFileProviderEnumerating;
- item metadata, content fetch, create, modify, delete;
- remote change enumeration and working-set signaling;
- durable remote cursor and conflict handling.

Nonreplicated:

- NSFileProviderExtension;
- static identifier-to-URL mapping;
- placeholder creation;
- materialization and release lifecycle;
- coordinated local file access and upload notification.

### Shared infrastructure

- App Group/document group configuration;
- a versioned item identity database;
- an outbox/inbox or remote-change cursor;
- bounded file transfer service;
- redacted diagnostics and error mapping;
- cancellation and retry policy.

Do not share mutable framework objects or SwiftUI state between the host and
extension. Share durable identifiers, revisions, and minimal state.

## Domain lifecycle recipe

1. Define a stable logical-domain ID for each account or location.
2. Store the mapping in the host app’s durable store.
3. Create the correct NSFileProviderDomain initializer for replicated or
   nonreplicated behavior.
4. Add the domain through NSFileProviderManager.
5. List registered domains after launch and reconcile user-enabled,
   disconnected, hidden, and missing records.
6. If account access expires, disconnect or show repair state; do not remove
   local data by default.
7. When removing a domain, choose a documented removal mode and explain
   preservation of dirty/downloaded data.
8. Reconnect only after the host app has restored the account/session state.

For a multi-account app, do not derive the domain ID from an email address or
display name. Use a stable opaque account ID. Domain display names may be
localized or changed; identity should not.

## Provider configuration checklist

Inspect the actual Xcode target and archive for:

- File Provider extension target membership;
- extension point and principal class;
- host and extension bundle identifiers;
- App Group and NSExtensionFileProviderDocumentGroup agreement;
- privacy manifest and privacy strings;
- deployment target and SDK;
- remote notification or background transfer configuration if the provider
  needs remote change signaling;
- pipeline-depth settings only when measured and supported by the provider;
- any testing entitlement used only in a non-distribution configuration.

Treat a configuration error as a release blocker. A host app can compile and
run while Files cannot load the extension.

## Stable item graph

Represent the provider graph with an app-owned record:

~~~text
ProviderItem
  providerID: opaque stable ID
  domainID: stable domain ID
  parentID: providerID or root
  filename: current name
  typeIdentifier: current Uniform Type Identifier
  contentRevision: remote/content version
  metadataRevision: remote/metadata version
  capabilities: allowed operations
  syncState: clean | downloading | uploading | conflict | unavailable
  workingSetMembership: recent/tagged/favorite/shared/trashed
~~~

The provider item ID should not contain raw customer data. A rename or move
updates metadata and parent, not identity. A no-such-item response must
invalidate the record and require re-resolution; never substitute by name.

## Replicated provider route

Implement the system-managed route in this order:

1. Create the provider instance for the domain.
2. Return a folder or working-set enumerator.
3. Return stable item metadata with capabilities and item versions.
4. Implement content fetch using the manager’s same-volume temporary
   directory.
5. Implement create/modify/delete with cancellation, conflict, and
   completion-handler ownership rules.
6. Publish remote changes through the working-set enumerator and signal it.
7. Track materialized items if the working set is not the entire remote
   dataset.
8. Choose content policy for items that should download eagerly or be
   evictable.

When a fetch hands a URL to the system, treat the URL as transferred
ownership. Clone anything the extension needs afterward. Make every remote
mutation idempotent under retry and crash replay.

## Nonreplicated provider route

Implement the provider-managed route in this order:

1. Define a static identifier-to-path mapping under documentStorageURL.
2. Return metadata for known IDs.
3. Write placeholders at the designated placeholder URL.
4. Materialize content in startProvidingItem.
5. Keep a placeholder after stopProvidingItem removes clean content.
6. Respond to itemChangedAtURL with a bounded upload or outbox update.
7. Coordinate every cross-process read/write.
8. Ensure the document picker and provider use the same purpose identifier
   where Apple requires it.

Do not keep a user-visible URL or security-scoped URL as a permanent cache key.
Use the provider item ID for identity.

## Enumeration recipe

### Folder

- handle rootContainer and each directory ID;
- preserve deterministic ordering across pages;
- keep page payload below the Apple-documented limit;
- finish with a next page or nil;
- return noSuchItem, serverUnreachable, or notAuthenticated deliberately.

### Working set

- include recent, tagged, favorited, shared, and recently deleted items;
- use actual parent IDs in each item;
- keep the set current across devices;
- signal the working set for changes even when no UI folder is open.

### Document

- return only the opened document’s changes;
- keep the enumerator alive for the document’s monitoring lifetime;
- forward remote updates to UIDocument or NSFilePresenter consumers.

### Cursor recovery

- persist the last successfully reported cursor;
- finish with a new cursor only after the event batch is complete;
- on expired/invalid cursor, reset and re-enumerate;
- test crash between applying the batch and persisting the cursor.

## SwiftUI feature state

Expose a small state machine to the view:

~~~text
domainLoading
domainReady
enumerating
empty(reason)
itemAvailable
downloadRequired
downloading(progress)
uploadPending
offline
notAuthenticated
conflict
removed
failed(retryable)
~~~

The model owns tasks and cancellation. The view renders semantic controls and
does not open raw URLs or start a provider transfer from its body.

## Security-scoped and coordinated handoff

For a picked external file or directory:

1. start security-scoped access;
2. coordinate the read/write;
3. perform only the bounded operation;
4. release security-scoped access;
5. store a security-scoped bookmark only when the product needs relaunch
   access;
6. resolve and validate the bookmark on later launches.

For a provider user-visible URL, use the provider manager’s documented URL
translation and coordination rules. Do not manipulate the user-visible path
directly when the provider expects updates through the working set.

## Optional local AI

A safe provider AI route is:

~~~text
selected item and explicit local scope
  -> materialize/download if the user requests it
  -> extract bounded content in the app/extension policy
  -> typed model proposal
  -> validate against current item ID, revision, capabilities, and filename rules
  -> person reviews
  -> provider mutation
  -> signal/enumerate and refresh UI
~~~

If the item is dataless, AI must not silently download private content just
because a preview row appeared. Tell the user that analysis requires a
download. Keep raw document text out of telemetry. When the provider revision
changes, invalidate the proposal.

## Proof plan

| Layer | Must prove |
| --- | --- |
| Source/SDK | APIs, availability, importer names, and target configuration match the named iOS SDK |
| Unit/fixture | Stable IDs, page cursors, anchors, reset, conflicts, and AI revision invalidation |
| Extension compile | Provider target imports FileProvider and implements the selected model’s required methods |
| Host compile | SwiftUI browser, document picker, and shared module build |
| Simulator | Basic host browser and document selection where supported |
| Physical device | Files visibility, second-app open/edit, background/relaunch, network/offline, storage, permissions, and accessibility |
| Signed archive | Embedded extension, App Group, privacy configuration, entitlements, and TestFlight launch |

Do not call the route shipped because the host app can browse its own mock
items. Provider/system proof is a separate deliverable.

## Sources

- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [NSFileProviderExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderextension)
- [NSFileProviderDomain](https://developer.apple.com/documentation/fileprovider/nsfileproviderdomain)
- [NSFileProviderManager](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager)
- [NSFileProviderEnumerator](https://developer.apple.com/documentation/fileprovider/nsfileproviderenumerator)
- [NSFileProviderSyncAnchor](https://developer.apple.com/documentation/fileprovider/nsfileprovidersyncanchor)
- [NSFileProviderItem](https://developer.apple.com/documentation/fileprovider/nsfileprovideritemprotocol)
- [Synchronizing the File Provider extension](https://developer.apple.com/documentation/fileprovider/synchronizing-the-file-provider-extension)
- [Defining your File Provider’s content](https://developer.apple.com/documentation/fileprovider/defining-your-file-provider-s-content)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [Providing access to directories](https://developer.apple.com/documentation/uikit/providing-access-to-directories)
- [NSURL](https://developer.apple.com/documentation/foundation/nsurl)
- [App extension programming guide: Document Provider](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/FileProvider.html)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI File Provider deep dive](../42-framework-deep-dives/137-swiftui-file-provider-document-domain-route.md)
- [SwiftUI File Provider design](../21-design-deep-dives/165-swiftui-file-provider-document-domain-route-design.md)
- [SwiftUI File Provider proof matrix](../60-verification/162-swiftui-file-provider-document-domain-proof-matrix.md)
- [SwiftUI File Provider code recipes](../70-code-recipes/180-swiftui-file-provider-document-domain-recipes.md)

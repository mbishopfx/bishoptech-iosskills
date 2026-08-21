# SwiftUI File Provider document-domain recipes

These snippets are route sketches for an iOS 26 target. The domain and manager
snippets can compile in an app or shared module. Extension protocol
implementations must compile inside the File Provider extension target because
target membership, Info.plist, entitlements, and extension lifecycle are part
of their contract.

The recipe boundary is:

~~~text
document outcome
  -> provider model
  -> domain and item identity
  -> page/anchor reducer
  -> placeholder or replicated content transfer
  -> coordinated handoff
  -> SwiftUI state
  -> optional typed proposal
  -> physical and signed-provider proof
~~~

## 1. Add an explicit replicated domain

Use an opaque, stable domain identifier. The display name can change.

~~~swift
import FileProvider

enum DomainRegistration {
    static func addReplicatedDomain(
        identifier: String,
        displayName: String,
        completion: @escaping (Error?) -> Void
    ) {
        let domain = NSFileProviderDomain(
            identifier: NSFileProviderDomainIdentifier(identifier),
            displayName: displayName
        )
        NSFileProviderManager.add(domain, completionHandler: completion)
    }
}
~~~

Do not derive the identifier from a raw email address or filename. Persist the
mapping in the host app. The add call does not prove that Files can launch the
embedded extension.

## 2. Add a nonreplicated domain with a storage-relative path

Use this initializer only when the extension will subclass
NSFileProviderExtension and own the local file/placeholder lifecycle.

~~~swift
import FileProvider

func nonReplicatedDomain(
    identifier: String,
    displayName: String,
    path: String
) -> NSFileProviderDomain {
    NSFileProviderDomain(
        identifier: NSFileProviderDomainIdentifier(identifier),
        displayName: displayName,
        pathRelativeToDocumentStorage: path
    )
}
~~~

The path is relative to the provider’s document storage. Keep the mapping
stable and validate that it cannot escape the provider storage root.

## 3. Reconcile registered domains on launch

List the system’s registered domains instead of assuming the host catalog is
the system truth.

~~~swift
import FileProvider

enum DomainReconciliation {
    static func load(
        completion: @escaping ([NSFileProviderDomain], Error?) -> Void
    ) {
        NSFileProviderManager.getDomainsWithCompletionHandler(completion)
    }
}
~~~

Compare domain IDs, not display names. Keep disconnected, hidden, disabled,
and missing account records as distinct states in the host model.

## 4. Encode compact pages and anchors

Pages and sync anchors are opaque provider cursors. Keep them small,
versioned, and independent of personal filenames.

~~~swift
import FileProvider
import Foundation

struct ProviderCursor: Sendable, Equatable {
    let page: NSFileProviderPage
    let anchor: NSFileProviderSyncAnchor

    init(revision: UInt64, lastItemID: String) {
        let pageData = Data("page:\(revision):\(lastItemID)".utf8)
        let anchorData = Data("anchor:\(revision)".utf8)
        page = NSFileProviderPage(rawValue: pageData)
        anchor = NSFileProviderSyncAnchor(rawValue: anchorData)
    }
}
~~~

The 500-byte limits documented by File Provider apply to these values. Treat
the cursor as invalid when its remote revision can no longer be read. Expire
it into a full enumeration instead of pretending that there were no changes.

## 5. Implement a small page enumerator

The actual provider should fetch its items from a durable remote client. This
fixture demonstrates the observer contract without a network.

~~~swift
import FileProvider
import Foundation

final class FixtureItem: NSObject, NSFileProviderItem {
    let itemIdentifier: NSFileProviderItemIdentifier
    let parentItemIdentifier: NSFileProviderItemIdentifier
    let filename: String
    let capabilities: NSFileProviderItemCapabilities

    init(id: String, parent: NSFileProviderItemIdentifier, filename: String) {
        itemIdentifier = NSFileProviderItemIdentifier(id)
        parentItemIdentifier = parent
        self.filename = filename
        capabilities = [.allowsReading, .allowsWriting, .allowsRenaming]
    }
}

final class FixtureEnumerator: NSObject, NSFileProviderEnumerator {
    private let items: [FixtureItem]

    init(items: [FixtureItem]) {
        self.items = items
    }

    func invalidate() {}

    func enumerateItems(
        for observer: any NSFileProviderEnumerationObserver,
        startingAt page: NSFileProviderPage
    ) {
        observer.didEnumerate(items)
        observer.finishEnumerating(upTo: nil)
    }

    func enumerateChanges(
        for observer: any NSFileProviderChangeObserver,
        from anchor: NSFileProviderSyncAnchor
    ) {
        observer.finishEnumeratingChanges(
            upTo: anchor,
            moreComing: false
        )
    }

    func currentSyncAnchor(
        completionHandler: @escaping (NSFileProviderSyncAnchor?) -> Void
    ) {
        completionHandler(NSFileProviderSyncAnchor(rawValue: Data()))
    }
}
~~~

This fixture intentionally returns one page and no changes. A production
enumerator must honor the requested page, return only the requested container,
use stable ordering, and emit a new anchor when a change batch was actually
reported.

## 6. Signal a working-set or folder change

Signal the smallest affected container. Replicated providers should prioritize
the working-set signal; nonreplicated providers also signal an active folder
when its contents changed.

~~~swift
import FileProvider

func signal(
    manager: NSFileProviderManager,
    container: NSFileProviderItemIdentifier,
    completion: @escaping (Error?) -> Void
) {
    manager.signalEnumerator(
        for: container,
        completionHandler: completion
    )
}
~~~

For a move, consider both the old and new parent and the working set. A signal
does not contain the changed item; the next enumeration must return the
authoritative metadata.

## 7. Prepare same-volume replicated content

The system owns the URL passed to a replicated provider’s fetch completion.
Use the manager’s temporary directory and clone anything the extension must
retain.

~~~swift
import FileProvider
import Foundation

func makeTransferFile(
    manager: NSFileProviderManager,
    data: Data,
    filename: String
) throws -> URL {
    let directory = try manager.temporaryDirectoryURL()
    let url = directory.appendingPathComponent(filename, isDirectory: false)
    try data.write(to: url, options: [.atomic])
    return url
}
~~~

The URL must be a regular file on the same volume as the user-visible
location. Do not mutate it after the provider calls its completion handler.

## 8. Write a nonreplicated placeholder

A provider-managed placeholder lets another process inspect metadata before
the content is materialized.

~~~swift
import FileProvider
import Foundation

func writeProviderPlaceholder(
    at fileURL: URL,
    metadata: NSFileProviderItem
) throws {
    let placeholder = NSFileProviderManager.placeholderURL(for: fileURL)
    try NSFileProviderManager.writePlaceholder(
        at: placeholder,
        withMetadata: metadata
    )
}
~~~

Call this from the nonreplicated extension’s placeholder path or proactively
before handing a URL to a system sharing route. The extension must leave the
placeholder behind after it releases clean content.

## 9. Request materialization or eviction

Eviction removes a clean local copy; it does not delete the remote item.

~~~swift
import FileProvider

func requestLocalContent(
    manager: NSFileProviderManager,
    itemID: NSFileProviderItemIdentifier,
    completion: @escaping (Error?) -> Void
) {
    manager.requestDownloadForItem(
        withIdentifier: itemID,
        requestedRange: nil,
        completionHandler: completion
    )
}

func evictLocalContent(
    manager: NSFileProviderManager,
    itemID: NSFileProviderItemIdentifier,
    completion: @escaping (Error?) -> Void
) {
    manager.evictItem(
        identifier: itemID,
        completionHandler: completion
    )
}
~~~

Handle dirty, open, nonevictable, and unavailable errors as state transitions.
Never turn an eviction callback into a remote delete.

## 10. Coordinate a security-scoped external document

Keep the access scope and coordinated read inside one bounded operation.

~~~swift
import Foundation

enum ExternalDocumentAccessError: Error {
    case securityScopeDenied
    case coordinationFailed
}

func readExternalDocument(
    at url: URL
) throws -> Data {
    guard url.startAccessingSecurityScopedResource() else {
        throw ExternalDocumentAccessError.securityScopeDenied
    }
    defer { url.stopAccessingSecurityScopedResource() }

    var coordinationError: NSError?
    var result: Data?
    NSFileCoordinator().coordinate(
        readingItemAt: url,
        options: [],
        error: &coordinationError
    ) { coordinatedURL in
        result = try? Data(contentsOf: coordinatedURL)
    }

    if let coordinationError {
        throw coordinationError
    }
    guard let result else {
        throw ExternalDocumentAccessError.coordinationFailed
    }
    return result
}
~~~

For a long-lived editor, use UIDocument or NSFilePresenter rather than
retaining a security-scoped read around a SwiftUI view. Save a
security-scoped bookmark only when relaunch access is required.

## 11. SwiftUI file importer state

Use the importer for a one-off user-selected file, not as a substitute for a
provider target.

~~~swift
import SwiftUI
import UniformTypeIdentifiers

struct ImportButton: View {
    @State private var isImporterPresented = false
    @State private var importedURL: URL?

    var body: some View {
        Button("Import document") {
            isImporterPresented = true
        }
        .fileImporter(
            isPresented: $isImporterPresented,
            allowedContentTypes: [.data],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                importedURL = urls.first
            case .failure:
                importedURL = nil
            }
        }
    }
}
~~~

The model should immediately move the selected URL into a bounded
security-scoped/coordinated operation. Do not use the imported URL as a
permanent identity.

## 12. Keep AI output as a revision-bound proposal

This DTO is framework-neutral so it can be tested without a model or a
provider target.

~~~swift
import Foundation

struct FileProviderProposal: Codable, Equatable, Sendable {
    let itemID: String
    let sourceRevision: String
    let proposedFilename: String?
    let proposedParentID: String?
    let reason: String?
}

enum ProposalValidation {
    static func isCurrent(
        _ proposal: FileProviderProposal,
        itemID: String,
        revision: String
    ) -> Bool {
        proposal.itemID == itemID && proposal.sourceRevision == revision
    }
}
~~~

The commit layer must re-resolve the current provider item, validate
capabilities and filename rules, require review, and then call the provider
mutation. A model result is not permission, identity, or upload proof.

## 13. Extension lifecycle skeleton

The following is a shape guide for a replicated extension target. Complete the
required item/content/mutation methods against the current SDK and remote
service; do not paste this into a host-app target.

~~~swift
import FileProvider
import Foundation

enum ProviderUnavailable: Error {
    case unavailable
}

final class ReplicatedProvider: NSObject, NSFileProviderReplicatedExtension {
    let domain: NSFileProviderDomain

    required init(domain: NSFileProviderDomain) {
        self.domain = domain
        super.init()
        // Open durable state for this domain.
    }

    func invalidate() {
        // Cancel owned work and release domain-scoped resources.
    }

    func enumerator(
        for containerItemIdentifier: NSFileProviderItemIdentifier,
        request: NSFileProviderRequest
    ) throws -> any NSFileProviderEnumerator {
        throw ProviderUnavailable.unavailable
    }

    func item(
        for identifier: NSFileProviderItemIdentifier,
        request: NSFileProviderRequest,
        completionHandler: @escaping (NSFileProviderItem?, (any Error)?) -> Void
    ) -> Progress {
        completionHandler(nil, ProviderUnavailable.unavailable)
        return Progress(totalUnitCount: 1)
    }

    func fetchContents(
        for itemIdentifier: NSFileProviderItemIdentifier,
        version requestedVersion: NSFileProviderItemVersion?,
        request: NSFileProviderRequest,
        completionHandler: @escaping (URL?, NSFileProviderItem?, (any Error)?) -> Void
    ) -> Progress {
        completionHandler(nil, nil, ProviderUnavailable.unavailable)
        return Progress(totalUnitCount: 1)
    }

    func createItem(
        basedOn itemTemplate: NSFileProviderItem,
        fields: NSFileProviderItemFields,
        contents url: URL?,
        options: NSFileProviderCreateItemOptions = [],
        request: NSFileProviderRequest,
        completionHandler: @escaping (
            NSFileProviderItem?,
            NSFileProviderItemFields,
            Bool,
            (any Error)?
        ) -> Void
    ) -> Progress {
        completionHandler(nil, fields, false, ProviderUnavailable.unavailable)
        return Progress(totalUnitCount: 1)
    }

    func modifyItem(
        _ item: NSFileProviderItem,
        baseVersion version: NSFileProviderItemVersion,
        changedFields: NSFileProviderItemFields,
        contents newContents: URL?,
        options: NSFileProviderModifyItemOptions = [],
        request: NSFileProviderRequest,
        completionHandler: @escaping (
            NSFileProviderItem?,
            NSFileProviderItemFields,
            Bool,
            (any Error)?
        ) -> Void
    ) -> Progress {
        completionHandler(nil, changedFields, false, ProviderUnavailable.unavailable)
        return Progress(totalUnitCount: 1)
    }

    func deleteItem(
        identifier: NSFileProviderItemIdentifier,
        baseVersion version: NSFileProviderItemVersion,
        options: NSFileProviderDeleteItemOptions = [],
        request: NSFileProviderRequest,
        completionHandler: @escaping ((any Error)?) -> Void
    ) -> Progress {
        completionHandler(ProviderUnavailable.unavailable)
        return Progress(totalUnitCount: 1)
    }
}
~~~

The shape above is intentionally incomplete: the protocol also requires the
current SDK’s metadata, fetch, create, modify, and delete methods. The
extension target must typecheck those signatures, call each completion
handler, return Progress where required, and implement retry-safe remote
operations.

## 14. Test fixture states

Keep a reducer fixture independent from real Files data.

~~~swift
enum ProviderLocalState: Equatable, Sendable {
    case dataless
    case materialized
    case downloading(progress: Double)
    case uploading(progress: Double)
    case conflict
    case offline
    case removed
}

struct ProviderItemFixture: Equatable, Sendable {
    let id: String
    let parentID: String
    let revision: String
    var state: ProviderLocalState
}
~~~

Test page insertion, cursor expiry, remote move, local dirty state, eviction
refusal, extension restart, stale AI proposal, and accessibility labels
against these synthetic records.

## Verification stop list

- Compile the domain, manager, cursor, fixture, placeholder, transfer,
  security-scope, SwiftUI, proposal, and reducer snippets against the named
  SDK.
- Compile the extension lifecycle code in the actual File Provider target.
- Inspect App Group/document-group configuration and archive target membership.
- Test Files visibility, second-app open/edit, offline materialization, and
  extension relaunch on a physical device.
- Test VoiceOver, Dynamic Type, reduced transparency, focus, and long names.
- Keep raw document bytes, security-scoped URLs, credentials, and personal
  filenames out of logs and AI prompts unless explicitly selected.

## Sources

- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [NSFileProviderExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderextension)
- [NSFileProviderDomain](https://developer.apple.com/documentation/fileprovider/nsfileproviderdomain)
- [NSFileProviderManager](https://developer.apple.com/documentation/fileprovider/nsfileprovidermanager)
- [NSFileProviderEnumerator](https://developer.apple.com/documentation/fileprovider/nsfileproviderenumerator)
- [NSFileProviderPage](https://developer.apple.com/documentation/fileprovider/nsfileproviderpage)
- [NSFileProviderSyncAnchor](https://developer.apple.com/documentation/fileprovider/nsfileprovidersyncanchor)
- [NSFileProviderItem](https://developer.apple.com/documentation/fileprovider/nsfileprovideritemprotocol)
- [NSFileProviderContentPolicy](https://developer.apple.com/documentation/fileprovider/nsfileprovidercontentpolicy)
- [Defining your File Provider’s content](https://developer.apple.com/documentation/fileprovider/defining-your-file-provider-s-content)
- [Synchronizing the File Provider extension](https://developer.apple.com/documentation/fileprovider/synchronizing-the-file-provider-extension)
- [Tracking changes to documents](https://developer.apple.com/documentation/fileprovider/tracking-changes-to-documents)
- [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller)
- [Providing access to directories](https://developer.apple.com/documentation/uikit/providing-access-to-directories)
- [NSURL](https://developer.apple.com/documentation/foundation/nsurl)
- [NSFileCoordinator](https://developer.apple.com/documentation/foundation/nsfilecoordinator)
- [startAccessingSecurityScopedResource](https://developer.apple.com/documentation/foundation/url/startaccessingsecurityscopedresource%28%29)
- [SwiftUI file importer and exporter presentation](https://developer.apple.com/documentation/swiftui/view-presentation)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI File Provider deep dive](../42-framework-deep-dives/137-swiftui-file-provider-document-domain-route.md)
- [SwiftUI File Provider design](../21-design-deep-dives/165-swiftui-file-provider-document-domain-route-design.md)
- [SwiftUI File Provider capability route](../50-capability-recipes/168-swiftui-file-provider-document-domain-route.md)
- [SwiftUI File Provider proof matrix](../60-verification/162-swiftui-file-provider-document-domain-proof-matrix.md)

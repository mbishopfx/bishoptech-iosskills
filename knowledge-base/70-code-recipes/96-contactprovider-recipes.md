# ContactProvider recipes

These are route sketches for an app target plus a Contact Provider extension
target. They are not claimed to compile in this workspace or to prove Settings,
Contacts consumers, extension budgets, or release behavior.

## 1. Enable the provider from the host app

The manager belongs in the host app, not the extension. Enable only after the
person understands the scope.

~~~swift
import ContactProvider

@MainActor
func enableContactProvider() async -> Result<Bool, Error> {
    do {
        let manager = try ContactProviderManager()
        try await manager.enable()
        return .success(manager.isEnabled)
    } catch {
        return .failure(error)
    }
}
~~~

Map errors to extension-not-found, unsupported, denied, and retryable states.
Returning true means the manager reports an enabled domain; it does not prove
that a contact has reached Phone, Mail, or another consumer.

## 2. Signal the extension after a canonical revision

Signal only after the host app has durably written the approved canonical
revision that the extension can read.

~~~swift
import ContactProvider

func requestProviderRefresh() async -> Result<Void, Error> {
    do {
        let manager = try ContactProviderManager()
        try await manager.signalEnumerator()
        return .success(())
    } catch {
        return .failure(error)
    }
}
~~~

Persist the canonical revision and signal result separately. Do not call this
on every SwiftUI body update or treat its completion as system-consumer
completion.

## 3. Manage disable, reset, and lifecycle

Expose destructive provider operations in a deliberate settings surface.

~~~swift
import ContactProvider

func disableProvider() async -> Result<Void, Error> {
    do {
        let manager = try ContactProviderManager()
        try await manager.disable()
        return .success(())
    } catch {
        return .failure(error)
    }
}

func resetProvider() async -> Result<Void, Error> {
    do {
        let manager = try ContactProviderManager()
        try await manager.reset()
        return .success(())
    } catch {
        return .failure(error)
    }
}
~~~

Reset the system projection, not the app’s canonical records, unless the
product explicitly says otherwise. Rebuild with a fresh generation after a
successful reset.

## 4. Create the extension enumeration seam

Add a Contact Provider extension target from Xcode’s template. Keep the
extension’s source reader bounded and read-only.

~~~swift
import ContactProvider

final class AppContactProviderExtension: ContactProviderExtension {
    private let source = CanonicalContactProjection()

    // Confirm the exact override/signature in the selected SDK.
    override func enumerator(
        for collection: ContactItem.Identifier
    ) -> any ContactItemEnumerator {
        ContactEnumerator(source: source, collection: collection)
    }
}
~~~

The extension must not create a host-app UI, request an interactive login, or
call ContactProviderManager. Its process may be launched and terminated
independently.

## 5. Enumerate full content in stable pages

The observer method names below mirror the ContactProvider contract. The exact
ContactItem constructors and page-finish signatures should be checked against
the selected SDK.

~~~swift
import ContactProvider

final class ContactEnumerator: NSObject, ContactItemEnumerator {
    let source: CanonicalContactProjection
    let collection: ContactItem.Identifier

    init(
        source: CanonicalContactProjection,
        collection: ContactItem.Identifier
    ) {
        self.source = source
        self.collection = collection
    }

    func enumerateContent(
        in page: ContactItemPage,
        for observer: any ContactItemContentObserver
    ) async {
        do {
            let snapshot = try await source.snapshot(
                generationMarker: page.generationMarker
            )
            let batch = snapshot.items
                .sorted { $0.providerID < $1.providerID }
                .dropFirst(page.offset)
                .prefix(observer.suggestedBatchSize)
                .map(makeContactItem)

            observer.didUpdate(Array(batch))

            // Use the documented next-page/final-page observer calls here.
            if batch.count < observer.suggestedBatchSize {
                observer.didFinishEnumeratingContent(
                    upTo: snapshot.finalAnchor
                )
            } else {
                observer.didFinishEnumeratingPage(
                    upTo: snapshot.nextPageAnchor
                )
            }
        } catch {
            observer.didFinishEnumeratingContentWithError(error)
        }
    }
}
~~~

This is intentionally a route sketch: page and observer APIs evolve, and the
exact SDK may use different anchor/value constructors. The invariants are
stable generation, deterministic order, bounded batches, explicit completion,
and an error path that does not claim success.

## 6. Enumerate changes from an anchor

Persist a durable change log in the canonical store. Never generate deletes by
comparing a short or failed page.

~~~swift
extension ContactEnumerator {
    func enumerateChanges(
        startingAt syncAnchor: ContactItemSyncAnchor,
        for observer: any ContactItemChangeObserver
    ) async {
        do {
            let changes = try await source.changes(after: syncAnchor)
            for batch in changes.batches {
                observer.didUpdate(batch.updated.map(makeContactItem))
                observer.didDelete(batch.deleted.map(\.providerID))
                observer.didFinishEnumeratingChanges(
                    upTo: batch.anchor,
                    moreComing: batch.moreComing
                )
            }
        } catch {
            observer.didFinishEnumeratingChangesWithError(error)
        }
    }
}
~~~

The observer’s suggested batch size and the precise completion lifecycle must
be honored according to the current SDK. Save the highest completed anchor only
after the corresponding batch was delivered successfully. If an anchor is
invalid or pruned, return the documented error/recovery state and request a
full enumeration.

## 7. Keep ContactItem construction deterministic

Keep the conversion from a canonical value projection to ContactItem in one
tested function.

~~~swift
struct PublishedContact: Sendable {
    let providerID: String
    let displayName: String
    let phoneNumbers: [String]
    let emailAddresses: [String]
    let imageData: Data?
    let sourceRevision: String
}

func makeContactItem(_ value: PublishedContact) -> ContactItem {
    // Build the ContactItem with the current SDK’s documented fields.
    // Redact fields that are not approved for the provider projection.
    fatalError("Route sketch: implement against the selected SDK")
}
~~~

Do not pass a CNContact, NSManagedObject, persistence context, image cache, or
private record object into the extension output. Convert to bounded value data.

## 8. Define a reviewable AI projection proposal

The host app can enrich canonical contacts before signaling the provider.

~~~swift
struct ContactProjectionProposal: Codable, Equatable, Sendable {
    let sourceContactID: String
    let sourceRevision: String
    let suggestedDisplayName: String?
    let suggestedCategory: String?
    let evidenceSummary: String
    let modelRoute: String
}

func isCurrent(
    _ proposal: ContactProjectionProposal,
    currentRevision: String,
    allowedCategories: Set<String>
) -> Bool {
    guard proposal.sourceRevision == currentRevision else { return false }
    if let category = proposal.suggestedCategory {
        return allowedCategories.contains(category)
    }
    return true
}
~~~

Review, edit, or dismiss before writing the published projection. Do not
publish a guessed phone number, identity match, or sensitive field because a
model returned a confident string.

## 9. Present provider state in SwiftUI

Keep host request state, extension result, and consumer visibility separate.

~~~swift
import SwiftUI

struct ContactProviderStatusView: View {
    let status: String
    let enable: () -> Void
    let refresh: () -> Void
    let disable: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Contact provider")
                .font(.headline)
            Text(status)
                .foregroundStyle(.secondary)
                .accessibilityLabel("Contact provider status: \(status)")

            GlassEffectContainer(spacing: 12) {
                HStack {
                    Button("Enable", systemImage: "person.crop.circle.badge.plus", action: enable)
                    Button("Refresh", systemImage: "arrow.clockwise", action: refresh)
                    Button("Disable", systemImage: "person.crop.circle.badge.minus", action: disable)
                }
                .labelStyle(.iconOnly)
                .padding(8)
                .glassEffect()
            }
        }
        .padding()
    }
}
~~~

Add a plain fallback for reduced transparency and clear descriptive labels for
VoiceOver, Dynamic Type, keyboard, pointer, and localization. The status text
must say “Update requested” or “Last approved revision” rather than claiming
system-wide completion without evidence.

## 10. Model the provider lifecycle as data

Persist app-owned status as values, not manager or extension objects.

~~~swift
struct ProviderState: Equatable, Sendable {
    enum Phase: Equatable {
        case unavailable
        case disabled
        case enabling
        case enabled
        case updateRequested
        case publishing(String)
        case stale(String)
        case failed(String)
    }

    var phase: Phase = .unavailable
    var canonicalRevision: String?
    var publishedRevision: String?
    var lastCompletedAnchor: String?
}
~~~

The state is the app’s explanation of observed events. It is not a replacement
for Settings or the system Contacts database. Reconcile it after relaunch and
after returning from Settings.

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
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

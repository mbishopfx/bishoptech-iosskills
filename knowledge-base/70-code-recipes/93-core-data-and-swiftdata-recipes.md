# Core Data and SwiftData recipes

These are compile-oriented route sketches for Core Data stacks, contexts,
fetches, migration, CloudKit mirroring, and SwiftData coexistence. They are
not claimed to compile in this documentation-only workspace.

Before using them:

- add the model resource and generated classes to the named target;
- confirm the current SDK declaration and deployment availability;
- choose one stack/migration owner;
- never pass managed objects across contexts or queues;
- test real versioned stores, account state, extensions, and signed builds.

## 1. Create a persistent container

Use NSPersistentContainer for the normal iOS Core Data stack.

~~~swift
import CoreData

@MainActor
final class CoreDataStack {
    let container: NSPersistentContainer

    init(modelName: String) {
        container = NSPersistentContainer(name: modelName)
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.undoManager = UndoManager()

        container.loadPersistentStores { description, error in
            if let error {
                // Publish a recoverable store-load state in a real feature.
                print("Store failed: \(error.localizedDescription)")
                return
            }
            print("Loaded store at \(description.url?.path ?? "unknown")")
        }
    }
}
~~~

Do not use fatalError as the customer-facing recovery path. In production,
publish loading, migration, unavailable, and failure states to the UI. The
container completion callback proves store-load completion for that attempt,
not CloudKit delivery or data correctness.

## 2. Perform background work on a private context

Use the container's background task API for import or transformation work.

~~~swift
func importRecords(
    into stack: CoreDataStack,
    values: [ImportedValue]
) async throws {
    try await stack.container.performBackgroundTask { context in
        for value in values {
            let request = ImportedRecord.fetchRequest()
            request.fetchLimit = 1
            request.predicate = NSPredicate(
                format: "externalID == %@",
                value.externalID
            )

            let record = try context.fetch(request).first
                ?? ImportedRecord(context: context)
            record.externalID = value.externalID
            record.title = value.title
        }
        if context.hasChanges {
            try context.save()
        }
    }
}
~~~

The generated ImportedRecord type and attribute names are target-specific.
Keep the values passed into this task immutable. Add cancellation checkpoints
for a large import and decide how the view context merges the changes.

## 3. Hand off an object ID

Use NSManagedObjectID rather than a managed object instance across queues.

~~~swift
func updateInBackground(
    stack: CoreDataStack,
    objectID: NSManagedObjectID,
    title: String
) async throws {
    try await stack.container.performBackgroundTask { context in
        guard let record = try context.existingObject(with: objectID)
            as? Note else {
            return
        }
        record.title = title
        try context.save()
    }
}
~~~

Refetch the object in the destination context and validate that it still
exists, belongs to the expected entity, and has the expected revision before
applying a proposal. An object ID is identity, not permission to overwrite a
newer user edit.

## 4. Define a bounded fetch

Make the predicate, sort, limit, and relationship policy explicit.

~~~swift
func fetchRecentNotes(
    from context: NSManagedObjectContext
) throws -> [Note] {
    let request: NSFetchRequest<Note> = Note.fetchRequest()
    request.fetchLimit = 100
    request.fetchBatchSize = 40
    request.sortDescriptors = [
        NSSortDescriptor(
            keyPath: \Note.updatedAt,
            ascending: false
        )
    ]
    request.predicate = NSPredicate(
        format: "isArchived == NO"
    )
    request.relationshipKeyPathsForPrefetching = ["tags"]
    return try context.fetch(request)
}
~~~

Run the fetch on the context's queue. For a count, object-ID result, or
dictionary projection, choose the request result type intentionally instead of
fetching full managed objects. Do not use a broad fetch as a hidden cache for
an AI prompt or widget.

## 5. Feed a UIKit list with fetched results

NSFetchedResultsController is a UIKit list adapter for a fetch request and
managed object context.

~~~swift
final class NotesController: UITableViewController,
    NSFetchedResultsControllerDelegate {
    private let fetched: NSFetchedResultsController<Note>

    init(context: NSManagedObjectContext) {
        let request: NSFetchRequest<Note> = Note.fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(key: "updatedAt", ascending: false)
        ]
        fetched = NSFetchedResultsController(
            fetchRequest: request,
            managedObjectContext: context,
            sectionNameKeyPath: nil,
            cacheName: nil
        )
        super.init(style: .plain)
        fetched.delegate = self
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        try? fetched.performFetch()
    }
}
~~~

The table-update delegate methods are omitted here. SwiftUI projects can use
FetchRequest or a feature adapter instead. Do not use a cache without a plan
for invalidating it when the request, predicate, or sort descriptors change.

## 6. Use a SwiftUI FetchRequest

This is a route sketch for a Core Data-backed SwiftUI screen.

~~~swift
import SwiftUI
import CoreData

struct NotesList: View {
    @Environment(\.managedObjectContext) private var context
    @FetchRequest(
        sortDescriptors: [
            NSSortDescriptor(key: "updatedAt", ascending: false)
        ],
        predicate: NSPredicate(format: "isArchived == NO")
    )
    private var notes: FetchedResults<Note>

    var body: some View {
        List(notes) { note in
            Text(note.title ?? "Untitled")
        }
        .toolbar {
            Button("Add") {
                let note = Note(context: context)
                note.title = "Untitled"
                try? context.save()
            }
        }
    }
}
~~~

The view should expose a real save error and a value projection if the screen
has more complex state. A nonempty FetchedResults collection does not prove
that CloudKit has imported all remote changes.

## 7. Enable lightweight migration options

Set migration options on the persistent store description before loading the
stores when the model change fits Core Data's inference rules.

~~~swift
let container = NSPersistentContainer(name: "Model")
if let description = container.persistentStoreDescriptions.first {
    description.setOption(
        true as NSNumber,
        forKey: NSMigratePersistentStoresAutomaticallyOption
    )
    description.setOption(
        true as NSNumber,
        forKey: NSInferMappingModelAutomaticallyOption
    )
}

container.loadPersistentStores { _, error in
    // Record success or a recoverable migration error.
}
~~~

An option flag does not make a semantic migration safe. Use versioned models,
renaming identifiers, staged migration, or a manual mapping route when the
data meaning changes.

## 8. Share a store with a SwiftData target

Apple's coexistence sample uses a common persistent-store URL and persistent
history tracking for a Core Data host and a SwiftData projection.

~~~swift
import CoreData

func configureSharedStore(
    _ container: NSPersistentContainer,
    url: URL
) {
    guard let description = container.persistentStoreDescriptions.first else {
        return
    }
    description.url = url
    description.setOption(
        true as NSNumber,
        forKey: NSPersistentHistoryTrackingKey
    )
}
~~~

Call this before loadPersistentStores and use the matching App Group/container
configuration in every target that shares the file. Align schema, class/entity
names, migration ownership, history consumption, and file protection policy.
Do not let an extension casually initialize a second incompatible stack.

## 9. Configure a CloudKit-backed container

Use NSPersistentCloudKitContainer when the selected Core Data store should
mirror to a CloudKit database.

~~~swift
import CoreData

func makeCloudContainer(
    modelName: String,
    identifier: String
) -> NSPersistentCloudKitContainer {
    let container = NSPersistentCloudKitContainer(name: modelName)
    if let description = container.persistentStoreDescriptions.first {
        description.cloudKitContainerOptions =
            NSPersistentCloudKitContainerOptions(
                containerIdentifier: identifier
            )
    }
    container.loadPersistentStores { _, error in
        // Observe setup/import/export state in a real feature.
        if let error {
            print("Cloud-backed store failed: \(error)")
        }
    }
    return container
}
~~~

Entitlements, schema initialization, production promotion, account state, and
remote-notification/background configuration remain separate proof. A local
store can continue to work when the account or network is unavailable.

## 10. Store a reviewable AI proposal

The model output should be a value proposal. Revalidate it in the owning
context before creating or updating a managed object.

~~~swift
struct RecordProposal: Sendable, Hashable {
    let objectIDURI: URL
    let sourceRevision: Int
    let sourceHash: String
    let generatedSummary: String
    let modelRoute: String
}

func proposalIsCurrent(
    _ proposal: RecordProposal,
    revision: Int,
    sourceHash: String
) -> Bool {
    proposal.sourceRevision == revision
        && proposal.sourceHash == sourceHash
        && !proposal.generatedSummary.isEmpty
}
~~~

In a real target, map objectIDURI back to an object ID using the selected
persistent store coordinator, check the record's current revision and source
hash, show a semantic review action, then save. Do not log private source text
or treat the generated summary as a fact without product validation.

## Verification checklist

- Compile with a named target and model resource.
- Test store load, save, relaunch, delete, migration, and error recovery.
- Run background work with Core Data concurrency diagnostics.
- Test object-ID handoff and view-context merge/refetch.
- Test CloudKit account, schema, setup/import/export, and two-device paths when
  that capability is in scope.
- Test SwiftData coexistence with matching store URL, history, and namespaces.
- Test AI stale, cancelled, malformed, rejected, and accepted proposals.
- Inspect signed target entitlements, App Group, iCloud, model resources,
  widgets/extensions, privacy metadata, and release flags.

## Related routes

- [Core Data stack, contexts, and managed objects](../42-framework-deep-dives/58-core-data-stack-contexts-and-managed-objects.md)
- [Core Data local-first and sync design](../21-design-deep-dives/78-core-data-local-first-and-sync-design.md)
- [Core Data persistence and SwiftData interoperability route](../50-capability-recipes/81-core-data-persistence-and-swiftdata-interoperability-route.md)
- [Core Data persistence proof matrix](../60-verification/75-core-data-persistence-proof-matrix.md)

## Sources

- [Core Data](https://developer.apple.com/documentation/coredata/)
- [NSPersistentContainer](https://developer.apple.com/documentation/coredata/nspersistentcontainer)
- [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer)
- [NSManagedObjectContext](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext)
- [NSManagedObjectID](https://developer.apple.com/documentation/coredata/nsmanagedobjectid)
- [NSFetchRequest](https://developer.apple.com/documentation/coredata/nsfetchrequest)
- [NSFetchedResultsController](https://developer.apple.com/documentation/coredata/nsfetchedresultscontroller)
- [Using Core Data in the background](https://developer.apple.com/documentation/coredata/using-core-data-in-the-background)
- [Migrating your data model automatically](https://developer.apple.com/documentation/coredata/migrating-your-data-model-automatically)
- [Adopting SwiftData for a Core Data app](https://developer.apple.com/documentation/coredata/adopting-swiftdata-for-a-core-data-app)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [DefaultStore](https://developer.apple.com/documentation/swiftdata/defaultstore)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

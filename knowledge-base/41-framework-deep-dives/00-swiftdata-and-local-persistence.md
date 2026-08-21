# SwiftData and Local Persistence

## Capability

Use SwiftData when an app needs structured model objects to survive launches, drive SwiftUI queries, and remain private or local-first by default. It is a persistence route, not a sync service and not an identity system.

## Smallest native route

1. Define a small domain model with `@Model`.
2. Attach a `ModelContainer` to the app or the smallest view subtree that owns the store.
3. Read through `@Query` in SwiftUI when the view should react to model changes.
4. Use the environment’s `modelContext` to insert, update, delete, and save.
5. Keep imported or AI-extracted values in a draft/review state until the person confirms them.

Design the persisted contract before designing the screen. A useful AI-assisted record usually keeps the source reference, derived value, provenance, review state, and user-authored correction as separate fields. Do not let a generated string overwrite a person’s edited value simply because a later analysis pass returned a different result.

Illustrative route skeleton:

```swift
import SwiftData
import SwiftUI

@Model
final class Capture {
    var createdAt: Date
    var title: String
    var isConfirmed: Bool

    init(title: String, createdAt: Date = .now, isConfirmed: Bool = false) {
        self.title = title
        self.createdAt = createdAt
        self.isConfirmed = isConfirmed
    }
}

@main
struct CaptureApp: App {
    var body: some Scene {
        WindowGroup { CaptureList() }
            .modelContainer(for: Capture.self)
    }
}

struct CaptureList: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Capture.createdAt, order: .reverse)
    private var captures: [Capture]

    var body: some View {
        List(captures) { capture in
            Text(capture.title)
        }
        .toolbar {
            Button("Add") {
                modelContext.insert(Capture(title: "Unreviewed capture"))
            }
        }
    }
}
```

Treat this as a route sketch: compile it against the selected SDK before reusing it. The important design boundary is that the model container supplies the schema and storage, the context owns lifecycle operations, and `@Query` observes the context-backed store.

## Schema evolution and migration

`ModelContainer` performs automatic migrations when the schema change is within SwiftData’s supported migration behavior. When the product needs named, testable version boundaries or a custom transformation, define `VersionedSchema` types and a `SchemaMigrationPlan` with `MigrationStage.lightweight` or `MigrationStage.custom`. Pass the migration plan when creating the container; do not rely on an unrecorded model-class edit to explain a shipped data transition.

Migration route:

`shipped schema N -> fixture from N -> migration plan -> schema N+1 -> invariant checks -> user-visible recovery if migration fails`

Use a lightweight stage for a change that the selected SDK can migrate without app-owned transformation. Use a custom stage when values must be normalized, split, merged, or synthesized. Keep migration code deterministic and idempotent; never call a remote AI service as the only way to make old user data readable. If a derived field needs recomputation, preserve the original source and mark the derived field pending rather than silently replacing a reviewed value.

```swift
import SwiftData

enum CaptureSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] = [Capture.self]

    @Model
    final class Capture {
        var sourceText: String

        init(sourceText: String) {
            self.sourceText = sourceText
        }
    }
}

enum CaptureSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] = [Capture.self]

    @Model
    final class Capture {
        var sourceText: String
        var reviewState: String

        init(sourceText: String, reviewState: String = "needsReview") {
            self.sourceText = sourceText
            self.reviewState = reviewState
        }
    }
}

enum CaptureMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] = [
        CaptureSchemaV1.self,
        CaptureSchemaV2.self
    ]

    static var stages: [MigrationStage] = [
        .lightweight(
            fromVersion: CaptureSchemaV1.self,
            toVersion: CaptureSchemaV2.self
        )
    ]
}

let container = try ModelContainer(
    for: Schema(versionedSchema: CaptureSchemaV2.self),
    migrationPlan: CaptureMigrationPlan.self
)
```

This is a migration shape, not proof that every model change qualifies as lightweight. Keep each version’s model types stable, compile the plan against the target SDK, test a copy of real-shaped old data, and verify that the resulting records retain source, user edits, deletion behavior, and review state.

## Uniqueness and CloudKit compatibility

`@Attribute(.unique)` is useful for a local store that must enforce a uniqueness invariant. Automatic SwiftData CloudKit sync has documented limitations: CloudKit cannot enforce SwiftData’s unique property option, requires relationships to be optional, and doesn’t support the `deny` delete rule because synchronization is not atomic in that way. Decide the store’s future sync route before adding local-only constraints.

For a model that may sync automatically, prefer a stable application identifier plus an explicit deduplication/reconciliation policy. A stable identifier helps identify the same logical object; it is not the same thing as a server-enforced unique constraint. When a duplicate is discovered, preserve both sources until the person or a deterministic merge policy resolves them.

## Concurrency and context ownership

`ModelContext` is bound to the main actor when obtained from the main container context. Do not pass a live model object or context through arbitrary tasks and assume it is safe. For background persistence work, create a separate context or use a `@ModelActor` whose `modelContext` serializes access for that actor. Pass value types, persistent identifiers, or immutable input across actor boundaries and re-fetch the model in the owning context.

```swift
import SwiftData

@ModelActor
actor PersistenceWorker {
    func insertDraft(sourceText: String, provenance: String) throws {
        let draft = CaptureRecord(
            sourceText: sourceText,
            provenance: provenance,
            reviewState: "needsReview"
        )
        modelContext.insert(draft)
        try modelContext.save()
    }
}
```

The model type in this sketch is app-owned and intentionally omitted from the deep dive. Construct the worker with the same `ModelContainer` configuration as the app, and keep UI observation on the appropriate main-actor context. A `ModelActor` isolates persistence work; it does not make a network request, an AI session, or a non-Sendable media buffer safe automatically.

## Save, rollback, history, and deletion

SwiftData may implicitly save at documented lifecycle points, but product-critical boundaries should decide when an explicit `save()` is required and how a thrown error is presented. Use `hasChanges`, `rollback()`, and transactions deliberately. If the app builds an audit or sync layer from persistent history, bound history retention and delete stale history only after confirming that no consumer still needs it.

Deletion is a data contract, not only a row operation. Define whether deleting a record also deletes its raw file, transcript, translation, model output, cached thumbnail, persistent history, CloudKit record, and shared copies. Provide export or correction paths where the product requires them. Keep credentials, tokens, and encryption keys in Keychain rather than ordinary SwiftData fields.

## Choosing the persistence boundary

| Need | Route | First questions |
| --- | --- | --- |
| Private records on one device | SwiftData local container | What is the export, backup, and deletion story? |
| Same person’s records on Apple devices | SwiftData automatic CloudKit sync | Are the schema and capabilities CloudKit-compatible? |
| Public/shared/custom server records | CloudKit directly or a service-backed boundary | Which database and access rules own the record? |
| Files, documents, or media blobs | File coordination plus a model reference | What is the lifecycle and migration policy for the file? |

## Boundaries and failure modes

- A view context without an explicitly attached model container is not a valid production store for your models; verify the app or preview container setup.
- Unsaved changes can exist only in memory. Decide when to call `save()` and how to recover from a thrown save error.
- Model relationships and schema changes need a migration plan before shipping.
- `@Attribute(.unique)` and relationship/delete-rule choices need a CloudKit compatibility decision before enabling automatic sync.
- A `ModelContext` is not a general-purpose cross-actor database connection; use a model actor or an explicitly owned context for background work.
- Do not put secrets in model fields merely because the model is local; use Keychain or another appropriate protected store for credentials.
- If sync is added later, design conflict and deletion semantics before turning on capabilities.
- Preview and in-memory stores are useful for UI work but do not prove persistence across launches or devices.

## Verification route

- Preview with an in-memory container and deterministic fixtures.
- Run on a simulator to test inserts, edits, deletes, relaunch, and migration paths.
- Run on a physical device to test persistence under interruption, storage pressure, and real lifecycle transitions.
- Test a migration from every supported prior schema with source-derived records, user edits, missing assets, and partially completed drafts.
- Test actor-isolated writes, save failures, rollback, duplicate logical identifiers, deletion, export, and history retention.
- If sync is enabled, test two signed-in devices, offline edits, conflict resolution, account changes, and first-launch behavior.
- Record the schema version, migration result, and data deletion behavior before release.

## API route matrix

Choose the smallest SwiftData seam that owns the operation. A model declaration, a container, a context, and a SwiftUI query are related but not interchangeable responsibilities.

| API seam | Owns | Use it for | Configuration or proof gate |
| --- | --- | --- | --- |
| `@Model` / `Schema` | Persisted model shape and relationships | Defining product records and schema membership | Confirm supported property types, relationship/delete rules, identifiers, and the selected deployment target. |
| `ModelContainer` | Schema, storage configuration, contexts, and migration entry point | App-owned store construction | Decide local, in-memory, App Group, or CloudKit configuration; prove the container opens and survives relaunch. |
| `ModelConfiguration` | Storage details for a schema or model group | Store URL, ephemeral fixtures, App Group or CloudKit selection | Record which target creates the store, whether saves are allowed, and how the configuration changes between tests and release. |
| `ModelContext` | Fetch, insert, update, delete, save, rollback, and undo scope | Work in one process and one context boundary | Keep ownership explicit; test thrown saves, rollback, cancellation, and context invalidation. |
| `@Query` | SwiftUI observation and fetch presentation | Lists, grids, and filtered view state | Attach the correct container before the view renders; test empty, stale, deleted, and migration states. |
| `PersistentIdentifier` | Stable reference to a persisted model instance | Passing identity across tasks or actor boundaries | Pass an identifier or value, then re-fetch in the receiving context; do not pass a live model object as if it were `Sendable`. |
| `@ModelActor` | Serialized model operations in an actor-owned context | Background imports, bounded writes, and migration fixtures | Construct it from the same container configuration; test actor isolation and save failure separately from UI rendering. |
| `VersionedSchema` / `SchemaMigrationPlan` | Named schema versions and migration stages | Shipped schema evolution | Keep fixtures for every supported prior version and prove invariants, user edits, raw-source retention, and recovery. |

## Container and target route

Use one of these shapes deliberately:

| Product shape | Container route | Target/process rule |
| --- | --- | --- |
| Local-first app | A production `ModelContainer` attached at the app scene or root view | The app target owns lifecycle and user-facing recovery; shared modules own model/use-case definitions. |
| Preview or unit fixture | An explicitly in-memory `ModelConfiguration` with seeded values | Never let a preview fixture silently become the release store; assert the fixture is ephemeral. |
| Widget or extension projection | A small, read-optimized projection in an explicitly shared container or App Group file route | The extension is a separate process; publish snapshots and stale state instead of relying on app memory or an open app context. |
| Cross-device local replica | CloudKit-compatible container and schema | Configure the iCloud/background capabilities on the owning target, then prove account, schema, offline, conflict, and deletion behavior. |
| Large media or secrets | SwiftData metadata plus coordinated file storage or Keychain | Keep blobs, credentials, and cryptographic material out of ordinary model fields unless the selected protection contract explicitly allows them. |

When more than one target reads the same logical record, document the store owner, shared-container identifier, schema/migration authority, file-coordination policy, and what happens if the extension sees an older or partially written projection. A shared App Group gives a container boundary; it does not make two processes share an in-memory `ModelContext`.

## Migration and concurrency test matrix

| Failure or transition | Deterministic fixture | Evidence to capture |
| --- | --- | --- |
| Lightweight schema change | Store created by the immediately prior version | Container opens, values retain meaning, and the app can save the migrated record. |
| Custom migration | Versioned store with values requiring split/merge/normalization | Migration stage completes once, preserves source/user edits, and produces the expected invariant. |
| Interrupted migration | Copy of an old store with a terminated or failed migration attempt | Relaunch behavior, recovery UI, backup/replacement policy, and no silent data loss. |
| Background write | Value input plus a model-actor fixture | No context crossing, bounded cancellation, save error handling, and UI refresh after re-fetch. |
| Delete/export | Record with raw source, derived values, thumbnails, and history | Every dependent artifact is deleted or retained according to the written data contract; export is readable. |
| Account or sync transition | Local records before sign-out, sign-in, or account restriction | Local-only rendering, pending changes, conflict state, and reauthorization behavior are explicit. |

These matrices prove the selected project route, not every possible SwiftData model. Keep them beside the target’s test plan and artifact record.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [VersionedSchema](https://developer.apple.com/documentation/swiftdata/versionedschema)
- [SchemaMigrationPlan](https://developer.apple.com/documentation/swiftdata/schemamigrationplan)
- [MigrationStage](https://developer.apple.com/documentation/swiftdata/migrationstage)
- [Concurrency support](https://developer.apple.com/documentation/swiftdata/concurrencysupport)
- [ModelActor](https://developer.apple.com/documentation/swiftdata/modelactor)
- [ModelConfiguration](https://developer.apple.com/documentation/swiftdata/modelconfiguration)
- [PersistentIdentifier](https://developer.apple.com/documentation/swiftdata/persistentidentifier)
- [Preserving your app’s model data across launches](https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Defining data relationships with enumerations and model classes](https://developer.apple.com/documentation/swiftdata/defining-data-relationships-with-enumerations-and-model-classes)
- [Fetching and filtering time-based model changes](https://developer.apple.com/documentation/swiftdata/fetching-and-filtering-time-based-model-changes)
- [Deleting persistent data from your app](https://developer.apple.com/documentation/swiftdata/deleting-persistent-data-from-your-app)
- [SwiftData updates](https://developer.apple.com/documentation/updates/swiftdata)
- [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- [Observation](https://developer.apple.com/documentation/observation)

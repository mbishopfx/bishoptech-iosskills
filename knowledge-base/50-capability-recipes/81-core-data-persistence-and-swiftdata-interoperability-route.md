# Core Data persistence and SwiftData interoperability route

Use this route for an app that stores durable local records, imports or
indexes data in the background, exposes a widget or extension, mirrors selected
data to CloudKit, or adopts SwiftData incrementally.

## Route contract

~~~text
feature requirement
  -> persistence owner and target graph
  -> model/schema/version
  -> store description and container
  -> context/actor queue boundary
  -> value projection for UI and AI
  -> local save/history
  -> optional CloudKit/widget/extension projection
  -> migration/conflict/deletion proof
~~~

## Step 1: decide the authority

Answer these questions before creating entities or model classes:

1. Is the canonical record local, remote, or a reviewed combination?
2. Is this a new SwiftData model, a Core Data model, or an incremental
   coexistence route?
3. Which target owns the model schema and migration?
4. Which target opens the store, and through which App Group if shared?
5. Does a widget or extension need read/write access?
6. Does CloudKit sync a private database, shared database, or no database?
7. What is the deletion and export promise?
8. Which AI fields are user-authored, derived, or merely proposed?

Write the answer as a one-page persistence contract. A framework import is not
an architecture.

## Step 2: choose the stack

| Outcome | Route |
| --- | --- |
| New local-first app with Swift-native models | SwiftData ModelContainer and ModelContext |
| Mature app with versioned xcdatamodeld and generated subclasses | NSPersistentContainer and Core Data contexts |
| Host app plus SwiftData widget during adoption | Shared store URL, App Group, persistent history, and explicit namespaces |
| Local Core Data plus CloudKit mirror | NSPersistentCloudKitContainer with entitlements and store descriptions |
| Multiple stores/configurations | Explicit managed object model configurations and store descriptions |
| Legacy target or custom migration tool | Manual model/coordinator/context construction |

Keep the persistence API behind a repository or feature store so a screen does
not directly depend on whether its records are managed objects or SwiftData
models.

## Step 3: design the schema and version path

Model entities, attributes, relationships, optionality, defaults, indexes,
constraints, and delete rules. For every schema change, classify it:

- safe lightweight migration;
- lightweight migration with an explicit renaming identifier;
- staged migration;
- manual migration with a mapping model/policy;
- a new store or one-time import.

Create upgrade fixtures from every shipped model version. Include real
relationships, optional values, large strings, attachments, user-created
records, and records with AI-derived fields. A fresh install does not exercise
data migration.

For CloudKit-backed data, confirm the model is compatible with the selected
CloudKit schema and that production schema changes obey CloudKit's additive
constraints. Treat schema promotion as a separate system/release action.

## Step 4: define context and actor boundaries

Use a main-queue/view context for user-facing work and a private context for
imports, indexing, cleanup, and heavy transformation. Use perform or
performAndWait on a private context. Pass object IDs or immutable snapshots
between contexts, not managed objects.

The feature state should look like:

~~~text
view snapshot
  -> user intent
  -> main context edit
  -> local save
  -> object ID/history event
  -> background import or sync
  -> merge/refetch/value projection
~~~

For long-running work, persist a task/session record with progress and
checkpoint information. On cancellation or termination, resume or show a
retry state instead of leaving a record marked complete.

## Step 5: build a value projection

Managed objects and SwiftData models are persistence objects. UI, Foundation
Models, Vision, widgets, and logs should receive a bounded value projection:

| Projection | Contains | Excludes |
| --- | --- | --- |
| List row | ID, title, summary, status, timestamp | Whole relationship graph |
| Detail | Visible fields and explicit actions | Unbounded faults or hidden network state |
| AI input | User-approved, minimized context | Live managed object, secrets, unrelated records |
| Widget | Small snapshot with freshness | A context or private object reference |
| Export | User-selected fields and representation | Internal IDs unless needed |

If a model proposes an update, attach the document/record ID, source revision,
source hash, schema version, model route/version, and validation state. Recheck
all of them in the owning context before saving.

## Step 6: add history and CloudKit only when needed

Enable persistent history when another context, process, extension, or sync
consumer needs a durable change cursor. Store and advance tokens carefully.
Handle a missing/pruned token by rebuilding the projection.

For NSPersistentCloudKitContainer:

1. add the iCloud capability and the selected container;
2. configure the store description and CloudKit options;
3. enable the background/remote-notification path required by the target;
4. initialize and validate the development schema;
5. promote only after testing real account/store states;
6. observe setup/import/export events and failures;
7. expose local-versus-remote state in the feature model.

Do not treat the presence of a CloudKit container identifier as proof of
delivery, account access, schema promotion, or multi-device convergence.

## Step 7: coexist Core Data and SwiftData deliberately

Apple's adoption sample shows that a Core Data host and a SwiftData widget can
share the same store URL. A safe coexistence plan needs:

- the same store file and container path;
- an App Group when targets are separate processes;
- nonconflicting Swift and generated class namespaces;
- one migration owner;
- persistent history tracking and a cursor consumer;
- a bounded extension query/projection;
- tests for host app not running and widget refresh;
- a recovery plan for store load/migration failure.

SwiftData's default store is Core Data-backed, but the model API and history
surface are not identical. Do not copy a Core Data subclass, context, or fetch
request into SwiftData without mapping its ownership and concurrency.

## Step 8: design conflict and deletion

A conflict route is:

~~~text
local revision A
  + imported revision B
  -> compare field/provenance/revision
  -> show differences
  -> optional bounded merge proposal
  -> person chooses or edits
  -> commit revision C
  -> save and project
~~~

The merge proposal must not mutate either source until accepted. When deleting,
remove local objects, derived records, projections, and search/widget entries
according to the product's actual control. State clearly what happens to
already exported or shared copies.

## Step 9: compose the native UI

Use a normal SwiftUI navigation/list/detail/form shell. Place persistence
status near the record identity. Use a Liquid Glass group only for functional
actions such as Review, Retry, Export, Share, or Resolve Conflict.

Accessibility labels should say “Saved on this device,” “Waiting to sync,” or
“Review changes,” not “Core Data context state.” Keep a visible text fallback
when glass or color is unavailable. Large Dynamic Type should cause the status
and actions to wrap or scroll, not disappear.

## Evidence matrix

| Route slice | Minimum evidence |
| --- | --- |
| Local store | Relaunch, save, delete, empty/error state, and store-load test |
| Background context | Queue-confinement test, object-ID handoff, cancellation, and merge |
| Migration | Upgrade fixtures from every supported model version |
| CloudKit | Entitlement/schema/account plus setup/import/export or unavailable state |
| Widget/extension | Signed multi-target install, shared-store access, bounded refresh, stale state |
| AI enrichment | Typed proposal, source revision, validation, review, rejection, and commit |
| Accessibility | Dynamic Type, VoiceOver, keyboard/Switch Control, RTL, contrast |
| Performance | Cold launch, fetch, scroll, background work, memory, energy, and thermal |

## Related routes

- [Core Data stack, contexts, and managed objects](../42-framework-deep-dives/58-core-data-stack-contexts-and-managed-objects.md)
- [Core Data local-first and sync design](../21-design-deep-dives/78-core-data-local-first-and-sync-design.md)
- [Core Data persistence proof matrix](../60-verification/75-core-data-persistence-proof-matrix.md)
- [Core Data and SwiftData recipes](../70-code-recipes/93-core-data-and-swiftdata-recipes.md)
- [SwiftData and CloudKit synchronization](../41-framework-deep-dives/12-cloudkit-syncengine-and-swiftdata.md)
- [Persistence, local-first, and sync recipes](../70-code-recipes/11-persistence-local-first-and-sync-recipes.md)

## Sources

- [Core Data](https://developer.apple.com/documentation/coredata/)
- [NSPersistentContainer](https://developer.apple.com/documentation/coredata/nspersistentcontainer)
- [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer)
- [NSManagedObjectModel](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel)
- [NSFetchRequest](https://developer.apple.com/documentation/coredata/nsfetchrequest)
- [NSFetchedResultsController](https://developer.apple.com/documentation/coredata/nsfetchedresultscontroller)
- [Using Core Data in the background](https://developer.apple.com/documentation/coredata/using-core-data-in-the-background)
- [Migrating your data model automatically](https://developer.apple.com/documentation/coredata/migrating-your-data-model-automatically)
- [Adopting SwiftData for a Core Data app](https://developer.apple.com/documentation/coredata/adopting-swiftdata-for-a-core-data-app)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [DefaultStore](https://developer.apple.com/documentation/swiftdata/defaultstore)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

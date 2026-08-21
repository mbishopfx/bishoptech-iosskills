# Core Data stack, contexts, and managed objects

Core Data is the durable object-graph and persistence framework underneath
many existing Apple-platform apps. It can persist local records, cache remote
data, support undo, perform background work, version and migrate schemas, and
mirror selected stores to CloudKit.

It is not a general-purpose database API and a managed object is not a
thread-safe value type. The essential route is:

~~~text
model version
  -> persistent container
  -> model + store coordinator + store description
  -> view context or private context
  -> managed objects / object IDs
  -> fetch, edit, save, history, migration
  -> optional CloudKit mirror
~~~

Keep this graph separate from SwiftUI view state, on-device model output,
network truth, and system-surface state.

## The Core Data stack

| Layer | Responsibility | Typical boundary |
| --- | --- | --- |
| NSManagedObjectModel | Entities, attributes, relationships, configurations, fetch templates, version identity | Xcode data model and migration |
| NSPersistentStoreDescription | Store URL, type, configuration, options, history, CloudKit options | Persistent-store policy |
| NSPersistentStoreCoordinator | Connects model and one or more stores | Stack internals |
| NSPersistentContainer | Creates and manages the model, coordinator, stores, view context, and background contexts | App-owned stack |
| NSManagedObjectContext | Queue-confined working object graph, change tracking, faults, undo, fetch/save boundary | Feature or process owner |
| NSManagedObject | Context-registered object with entity metadata, identity, relationships, and lifecycle | Model layer |
| NSManagedObjectID | Stable identity for handing a managed record between contexts or queues | Cross-context boundary |

For iOS 10 and later, the documented route is generally
NSPersistentContainer rather than manually constructing every stack component.
Manual construction remains useful for older targets, unusual store layouts,
multiple configurations, or a migration/diagnostic tool that needs direct
coordinator control.

The container name locates the model when a model is not passed explicitly and
is also used to name the persistent store. The container exposes a main-queue
viewContext, can create a private context, and can run a background task with
an ephemeral private context.

Loading a persistent store is an asynchronous boundary. The completion handler
reports whether the store loaded; it does not prove that the schema is
compatible, a CloudKit mirror is caught up, or a remote change is visible in
the UI. The app needs a visible loading/error/recovery state and an explicit
migration policy.

## Contexts and queue confinement

Core Data contexts bind managed objects to the queue on which the context was
created. A main-queue context is for UI-facing work. A private-queue context
must be used through perform or performAndWait. Do not pass a managed object
instance from one context or queue to another.

Use an object ID to cross the boundary:

~~~text
view context object
  -> objectID
  -> background context object(with: objectID)
  -> background edit/save
  -> merge or refresh the view context
~~~

This is a correctness rule, not only a performance suggestion. Violating it
can produce corruption, stale values, crashes, or data races that a preview or
unit test on one queue does not expose.

A context owns a working object graph. Fetches may return faults whose values
are loaded later. Accessing a persistent property can fire a fault and perform
store work, so avoid accidental property traversal in logging, descriptions,
large loops, or custom equality code.

Treat contexts as short-lived feature boundaries:

- viewContext for UI observation and user-visible edits;
- private context for import, export preparation, indexing, and batch work;
- a dedicated context for a long operation that can be cancelled;
- one stack owner per process or a deliberately documented shared-stack route.

Saving a private context does not automatically mean a visible view has
updated. Decide whether the view context merges changes, refetches, consumes
persistent history, or receives an explicit feature notification.

## Managed object identity and lifecycle

NSManagedObject instances belong to a context and entity description. Their
objectID is the identity that can be used to refetch the same record from
another context. A managed object can be inserted, updated, deleted, or a
fault. An object whose context is nil may have been deleted or detached.

Do not treat a managed object as a Sendable value. Convert it at the feature
boundary into a small immutable view model when handing data to SwiftUI,
Foundation Models, Core ML, logging, or an actor. Convert a proposed mutation
back to an object ID and revalidate it in the owning context before saving.

Managed object subclasses may add domain behavior, but Core Data relies on
many base implementations for identity, faulting, validation, and observation.
Do not override the documented methods and properties that Core Data reserves.
For small features, generated subclasses or NSManagedObject instances may be
enough; custom subclasses need tests for generated accessors, relationships,
validation, and migration.

## Models, versions, and migrations

The Xcode data model editor defines entities, attributes, relationships,
configurations, constraints, and class mappings. The compiled model is an
NSManagedObjectModel. Once a model is used by an object graph manager, do not
mutate it in place; create a versioned model and migration plan.

Lightweight migration can infer common changes such as adding or removing an
attribute, optionality changes with defaults, renames with renaming
identifiers, relationship additions/removals, and some hierarchy changes.
Enable automatic migration only when the source and destination models fit
the documented inference rules.

Use a staged or manual migration when:

- the transformation changes meaning, not just shape;
- values must be normalized or combined;
- relationships require custom repair;
- the model cannot infer a safe mapping;
- a store must be moved, split, or transformed;
- production data requires a dry-run and rollback plan.

Migration is a user-data lifecycle, not a launch-time implementation detail.
Test upgrade paths from every supported model version, failure during store
load, insufficient disk space, interrupted migration, backup/restore, and a
store that contains real relationships and optional values.

## Fetch, query, and presentation

NSFetchRequest describes an entity, predicate, sort descriptors, limits,
offsets, batch size, result type, prefetching, and fault behavior. Execute it
on the context's queue. Fetch only what the screen needs, use a bounded fetch
for a list, and distinguish object results, object IDs, dictionary results, and
count results.

For a UIKit table or collection view, NSFetchedResultsController can execute a
fetch, compute sections and indexes, observe relevant context changes, and
notify a delegate when objects or sections change. It is a UIKit presentation
adapter, not a replacement for the model or a reason to make a context global.

For SwiftUI, a FetchRequest property wrapper can execute a request and expose
FetchedResults. Keep the request's predicate and sort descriptors explicit.
When the screen has a complex query or a model actor boundary, prefer a
feature-owned fetch adapter that converts managed objects into value snapshots.

A fetch result is a local view of a context/store state. It is not proof that
CloudKit has no newer change, a server-side record agrees, or an AI-generated
field is correct.

## Background import and batch work

Use a private context for JSON import, media indexing, embedding preparation,
cleanup, and other work that could block the interface. Move only object IDs,
plain values, or immutable Sendable snapshots between queues.

For large data sets, use batch fetch sizes, prefetch only needed relationships,
and consider batch insert/update/delete APIs when their semantics fit. Batch
operations can bypass normal managed-object notifications and in-memory
objects, so explicitly merge or refresh affected contexts afterward.

Cancellation must be visible. A cancelled import should not leave a half-built
domain record marked complete. Persist checkpoints or an import session record
when a route can be interrupted.

## Persistent history and CloudKit

Persistent history can record changes made to a store so another process,
context, or extension can consume the changes after a token. This is useful
for widgets, background tasks, sync reconciliation, and cross-process
projections. A history token is a cursor, not the record itself; store it
carefully and recover if it is invalid or the history was pruned.

NSPersistentCloudKitContainer is an NSPersistentContainer subclass that can
mirror selected stores to a CloudKit private database. It can manage both
CloudKit-backed and non-cloud stores. Entitlements and store descriptions
choose the containers and configurations; schema initialization and
production promotion are separate steps.

CloudKit mirroring is asynchronous:

~~~text
local context save
  -> persistent store and history
  -> export event
  -> CloudKit database
  -> import event on another device
  -> local store update
  -> context refresh/history consumption
  -> UI projection
~~~

Use container events, history, and account state to explain setup, import,
export, unavailable account, partial sync, and conflict conditions. Do not
label a local save as synced or a fetched object as server truth.

## Core Data and SwiftData coexistence

SwiftData uses Core Data persistence underneath its default store. Apple's
Core Data to SwiftData sample documents incremental adoption and a coexistence
case where a host app uses Core Data while a widget uses SwiftData. The sample
uses the same persistent store URL and enables persistent history tracking so
the two projections can notice changes.

Use coexistence when:

- a mature Core Data app is adopting SwiftData incrementally;
- an extension or feature is a bounded consumer of a shared store;
- a migration plan explicitly handles class/entity namespaces and history;
- both targets agree on store URL, schema, App Group, and lifecycle.

Avoid casually opening the same store from multiple stacks. Define one schema
authority, one migration owner, one persistent-history policy, and one
conflict/recovery policy. Model names and generated class names can collide
even when entity names appear compatible.

SwiftData's DefaultStore is a Core Data-backed store, but SwiftData model
types, macros, contexts, history, and concurrency form a different programming
surface. Do not assume every Core Data option, custom subclass, or migration
tool maps directly to SwiftData.

## On-device AI and persistence boundaries

Persist AI output as a reviewable record, not as an invisible mutation:

| Record | Required fields |
| --- | --- |
| Source | Object ID, revision, source type, retention policy |
| Proposal | Schema/version, generated values, source span, model route |
| Review | Pending/accepted/rejected/edited, person and timestamp if needed |
| Commit | Deterministic domain mutation and new revision |
| Failure | Unavailable, cancelled, stale, invalid, or persistence error |

The model should receive a value snapshot or minimized context, not a live
managed object. Validate its output on the owning context/actor. An AI proposal
must not write directly to CloudKit or a system surface without user policy,
deterministic validation, and a separately recorded side-effect result.

## Availability and proof boundary

The Core Data framework is available across a broad range of Apple OS versions,
but the exact Swift concurrency, CloudKit, SwiftData, and iOS 26 behaviors
depend on the target SDK and deployment target. Compile the selected route and
inspect Xcode diagnostics.

A local fetch does not prove migration readiness, background correctness,
CloudKit delivery, widget convergence, privacy, or release behavior. A
successful save does not prove a durable store was loaded after relaunch.

## Related routes

- [Core Data local-first and sync design](../21-design-deep-dives/78-core-data-local-first-and-sync-design.md)
- [Core Data persistence and SwiftData interoperability route](../50-capability-recipes/81-core-data-persistence-and-swiftdata-interoperability-route.md)
- [Core Data persistence proof matrix](../60-verification/75-core-data-persistence-proof-matrix.md)
- [Core Data and SwiftData recipes](../70-code-recipes/93-core-data-and-swiftdata-recipes.md)
- [SwiftData and CloudKit synchronization](../41-framework-deep-dives/12-cloudkit-syncengine-and-swiftdata.md)
- [SwiftData and CloudKit synchronization recipes](../70-code-recipes/49-swiftdata-cloudkit-sync-recipes.md)

## Sources

- [Core Data](https://developer.apple.com/documentation/coredata/)
- [NSPersistentContainer](https://developer.apple.com/documentation/coredata/nspersistentcontainer)
- [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer)
- [NSManagedObjectModel](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel)
- [Core Data model](https://developer.apple.com/documentation/coredata/core-data-model)
- [NSManagedObject](https://developer.apple.com/documentation/coredata/nsmanagedobject)
- [NSManagedObjectContext](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext)
- [NSFetchRequest](https://developer.apple.com/documentation/coredata/nsfetchrequest)
- [NSFetchedResultsController](https://developer.apple.com/documentation/coredata/nsfetchedresultscontroller)
- [Using Core Data in the background](https://developer.apple.com/documentation/coredata/using-core-data-in-the-background)
- [Migrating your data model automatically](https://developer.apple.com/documentation/coredata/migrating-your-data-model-automatically)
- [Setting up a Core Data stack manually](https://developer.apple.com/documentation/coredata/setting-up-a-core-data-stack-manually)
- [Adopting SwiftData for a Core Data app](https://developer.apple.com/documentation/coredata/adopting-swiftdata-for-a-core-data-app)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [DefaultStore](https://developer.apple.com/documentation/swiftdata/defaultstore)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [TN3163 Core Data CloudKit synchronization](https://developer.apple.com/documentation/technotes/tn3163-understanding-the-synchronization-of-nspersistentcloudkitcontainer)

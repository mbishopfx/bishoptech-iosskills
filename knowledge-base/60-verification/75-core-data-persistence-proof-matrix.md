# Core Data persistence proof matrix

This matrix keeps local persistence, context confinement, migration, CloudKit
mirroring, SwiftData coexistence, AI-derived records, widgets, accessibility,
and release configuration separate. A list that renders after one launch is
not proof that the user's data survives migration or a background sync.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Do not infer |
| --- | --- | --- | --- |
| The selected Core Data/SwiftData stack compiles | Named target compile with the iOS 26 SDK | Small target with model, store, and context tests | That the store opens with real user data |
| Local records survive relaunch | Save, terminate, relaunch, fetch fixture | Signed device run across update and low-storage conditions | That a successful in-memory save is durable |
| Context usage is queue-safe | Confinement tests and object-ID handoff | Background import/save on physical device with diagnostics | That managed objects can cross actors or queues |
| Fetch results are correct | Predicate/sort/limit/relationship fixtures | Large data, faults, prefetch, batch, and mutation tests | That one list screen reflects server truth |
| UI remains synchronized | View-context merge/refetch test | Widget/extension and host-app-not-running run | That a background save automatically updates every projection |
| Migration is safe | Fixture from each supported model version | Interrupted, failed, large, and production-like upgrade tests | That lightweight migration handles semantic changes |
| CloudKit is configured | Entitlement, container, store-description, and schema inspection | Account unavailable, import/export event, and two-device run | That a container identifier proves sync delivery |
| Persistent history is consumed | Token fixture, change fixture, and rebuild path | Extension/background consumer with pruned-token recovery | That a history token is a durable record |
| Core Data and SwiftData share a store safely | Shared URL/schema and namespace compile | Signed host/widget coexistence and history reconciliation | That two stacks can write arbitrarily to one store |
| AI-derived data is reviewable | Typed proposal, revision/hash check, accept/reject tests | Device model availability, cancellation, privacy, and conflict run | That generated text is user intent or truth |
| Delete means what the product says | Local delete and relaunch fixture | History, widget, search, CloudKit/export destination audit | That deleting one object erases every copy |
| Accessibility is usable | Dynamic Type and semantic hierarchy review | VoiceOver, Switch Control, keyboard, RTL, contrast, and error tasks | That a fetch-driven screen is automatically accessible |
| Performance is acceptable | Baseline fetch/save/scroll measurements | Representative devices with memory, energy, and thermal observations | That Debug or newest-device performance represents all users |
| Release configuration is complete | Archive inspection | TestFlight install, migration smoke, and signed multi-target run | That an archive proves CloudKit production or App Store behavior |

## Fixture set

Create fixtures for:

- fresh install with no records;
- one record, many records, and a large relationship graph;
- local draft, saved record, pending projection, imported change, conflict;
- invalid or unavailable iCloud account;
- store load failure and retry;
- model versions before and after every shipped schema change;
- lightweight rename and optionality migration;
- staged/manual migration requiring a mapping;
- background import cancelled halfway through;
- a context save performed while the view is off screen;
- persistent history token at the beginning, middle, invalid, and pruned state;
- CloudKit setup, export, import, and unavailable events;
- host app and widget reading/writing the shared store;
- AI proposal current, stale, malformed, rejected, edited, accepted;
- deletion of a record with derived, widget, search, and export projections;
- Dynamic Type, RTL, VoiceOver, reduced transparency, and increased contrast.

Every fixture should include model/schema identity and a deterministic expected
projection. Use value snapshots for assertions where possible.

## Stack and store tests

Verify:

- the model resource is included in the intended target;
- the container name resolves the intended model and store;
- store descriptions point at the expected URL/type/configuration;
- persistent stores load or fail visibly;
- view and private contexts have the intended concurrency types;
- undo behavior is configured intentionally;
- store options and migration options are explicit;
- multiple stores/configurations do not receive the wrong entity set;
- the stack is not initialized twice by app and extension code accidentally.

For CloudKit, separately verify entitlements, container identifiers, schema
initialization, production promotion, account state, and remote notification
configuration. A local stack test should not be labeled a CloudKit test.

## Context and concurrency tests

Run:

1. fetch and edit on the view context;
2. pass an object ID to a private context;
3. update the record on the private queue;
4. save and merge/refetch the view context;
5. cancel an import before save;
6. terminate during a checkpointed import;
7. attempt an intentionally invalid managed-object cross-queue handoff in a
   test target and confirm the route rejects it or never performs it;
8. consume history after a background or extension change.

Use Core Data concurrency diagnostics during development. Keep managed objects
out of detached tasks and actor messages unless the selected API explicitly
supports the route and the target has a tested isolation design.

## Migration tests

For each version:

- install or seed a store with representative data;
- launch the new model;
- observe load and migration state;
- verify renamed entities/properties and relationships;
- verify default and optional values;
- verify indexes/constraints and derived fields;
- verify large strings, attachments, and deletion rules;
- verify history, CloudKit compatibility, and widget projections;
- relaunch and repeat after an interrupted or failed attempt.

Test a migration that should fail. The user needs a recoverable path, not a
crash or a silent reset of the store.

## CloudKit and multi-target tests

Record:

- account signed in, signed out, restricted, and unavailable;
- development versus production container;
- schema initialized/promoted state;
- local save before export;
- export success/failure;
- remote import and context reconciliation;
- history token consumption;
- conflict and duplicate handling;
- widget/extension host lifecycle;
- remote-notification or background delivery conditions.

Two devices are required for a convergence claim. A local container event or
CloudKit console record does not prove that the intended UI on another device
updated or that a person saw the change.

## AI-derived data tests

The proposal fixture must assert:

| Condition | Expected result |
| --- | --- |
| Same object ID, revision, and source hash | Eligible for review |
| Document changed while model runs | Stale; no mutation |
| Invalid enum, length, relation, or range | Rejected or deterministic fallback |
| Model unavailable or cancelled | Core workflow remains usable |
| Person rejects or edits | Original remains until a new explicit commit |
| Person accepts | New revision saved through the owning context |
| Sync conflict arrives before acceptance | Proposal is re-evaluated or marked stale |
| Delete occurs before commit | No orphaned derived record or projection |

Do not use one model response as a regression oracle. Test schema, provenance,
privacy, lifecycle, and user control.

## Accessibility and device tasks

On a signed physical-device build:

- create and edit a record;
- read status with VoiceOver;
- use Dynamic Type at the largest planned size;
- use keyboard, pointer, and Switch Control paths;
- change locale and writing direction;
- trigger offline, account-unavailable, migration-error, and conflict states;
- accept/reject an AI proposal;
- open a widget or extension projection if the product has one;
- delete and relaunch;
- inspect memory, hitches, energy, and thermal behavior during large fetches or
  background import.

Record device model, OS build, app build, model version, store version, account
state, and fixtures. Screenshots are supporting evidence, not the state proof.

## Release and artifact inspection

Inspect the archive for:

- model resources and generated classes;
- target membership and framework linkage;
- App Group, iCloud, CloudKit, and background-mode entitlements;
- privacy manifests and required usage descriptions if applicable;
- migration resources and version identifiers;
- widgets/extensions and their store configuration;
- release flags that disable diagnostics or change sync behavior.

Install the signed artifact and run a save/relaunch/migration smoke test. The
archive proves configuration and signing. It does not prove production schema
promotion, remote delivery, universal device compatibility, or App Store
review.

## Related routes

- [Core Data stack, contexts, and managed objects](../42-framework-deep-dives/58-core-data-stack-contexts-and-managed-objects.md)
- [Core Data local-first and sync design](../21-design-deep-dives/78-core-data-local-first-and-sync-design.md)
- [Core Data persistence and SwiftData interoperability route](../50-capability-recipes/81-core-data-persistence-and-swiftdata-interoperability-route.md)
- [Core Data and SwiftData recipes](../70-code-recipes/93-core-data-and-swiftdata-recipes.md)
- [Build/device/release checklist](01-build-device-and-release-checklist.md)
- [Physical-device capability proof matrix](07-physical-device-capability-proof-matrix.md)

## Sources

- [Core Data](https://developer.apple.com/documentation/coredata/)
- [NSPersistentContainer](https://developer.apple.com/documentation/coredata/nspersistentcontainer)
- [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer)
- [NSManagedObjectModel](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel)
- [NSManagedObject](https://developer.apple.com/documentation/coredata/nsmanagedobject)
- [NSFetchRequest](https://developer.apple.com/documentation/coredata/nsfetchrequest)
- [NSFetchedResultsController](https://developer.apple.com/documentation/coredata/nsfetchedresultscontroller)
- [Using Core Data in the background](https://developer.apple.com/documentation/coredata/using-core-data-in-the-background)
- [Migrating your data model automatically](https://developer.apple.com/documentation/coredata/migrating-your-data-model-automatically)
- [Adopting SwiftData for a Core Data app](https://developer.apple.com/documentation/coredata/adopting-swiftdata-for-a-core-data-app)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [DefaultStore](https://developer.apple.com/documentation/swiftdata/defaultstore)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Performance testing](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

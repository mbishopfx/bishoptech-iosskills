# Core Data local-first and sync design

Persistence is part of the user experience. A native iOS screen should make it
clear whether a value is a local draft, a saved local record, a pending sync,
a conflict, or a server/system projection.

Use this state model:

~~~text
empty/loading
  -> local draft
  -> saving locally
  -> saved locally
  -> export/sync pending
  -> imported or reconciled
  -> conflict/review
  -> failed/retry
~~~

The UI should remain useful at every state. CloudKit, a widget, an on-device
model, or a remote feed can enrich the record, but none should make the core
screen unusable when unavailable.

## Choose the persistence owner

| Situation | Starting route | Design consequence |
| --- | --- | --- |
| New Swift-first app | SwiftData | Model macros, model context, queries, history, and SwiftUI integration |
| Existing Core Data app | Core Data | Preserve model versions, generated classes, contexts, migrations, and history |
| Incremental adoption | Core Data plus bounded SwiftData projection | Shared store URL, App Group, namespacing, history, and migration owner |
| Widget or extension consumer | A deliberately shared store route | Extension process, App Group, read/write policy, history cursor |
| CloudKit private database | NSPersistentCloudKitContainer or SwiftData CloudKit configuration | iCloud/remote-notification capability, account state, schema and sync evidence |
| Local-only private utility | Core Data or SwiftData local store | No sync UI, clear backup/export policy, on-device retention |

Do not choose a framework from a screenshot. Choose it from model ownership,
target support, migration burden, extension topology, concurrency, and the
kind of proof the product needs.

## The local-first screen

A native record screen often needs these visual regions:

~~~text
navigation and record identity
  -> primary value/content
  -> save/sync status
  -> derived or AI-enriched fields
  -> history/conflict affordance
  -> secondary export/share actions
~~~

Keep status language literal:

| State | Useful copy | Avoid |
| --- | --- | --- |
| Draft | Not saved | A green check that implies sync |
| Saved locally | Saved on this device | Synced |
| Pending | Waiting to sync | Complete |
| Imported | Updated from another device | New truth |
| Conflict | Review changes | Automatically fixed |
| Account unavailable | iCloud unavailable; saved locally | Data lost |
| Save error | Could not save; Retry | Silent dismissal |

Use a system control or a small native status row rather than a large decorative
glass badge. A Liquid Glass action group can contain Retry, Review, Export, or
Share, but the status itself must remain readable without the material.

## SwiftUI and model observation

SwiftUI should observe a value that is safe for the view's isolation and
lifecycle. For Core Data, a FetchRequest or a feature adapter can expose
managed objects; for a complex feature, convert them into immutable snapshots
and publish explicit save/sync/review states.

Avoid letting a view mutate a managed object from an arbitrary task. Route user
actions through the model context or a main-actor feature store, and route
background import through a private context. Keep the UI's loading and error
states independent from a fetch result being temporarily empty.

An empty fetch can mean first launch, a filter, a deleted object, a store still
loading, a failed migration, an unavailable account, or a real empty state.
Design those cases separately.

## CloudKit and sync status

CloudKit mirroring is asynchronous. A local save can be visible before export,
and an imported record can be present before a screen has merged or refetched
its context. Design a status model that names the observed phase:

- local save completed;
- export scheduled or in progress;
- export failed;
- import observed;
- history consumed;
- account unavailable;
- conflict requires review.

Do not show a single permanent “synced” checkmark when the app cannot verify
that state. If the product does not need to expose sync detail, it can keep the
status compact, but the internal state still needs to distinguish local and
remote truth.

For shared records, show the person what changed and preserve the local
revision. A model-generated merge proposal is an option for review, not an
automatic resolution. Keep the original values and the competing revision
available until the commit is durable.

## Widgets, extensions, and App Groups

When a widget or extension reads a shared store:

- define the shared container and store URL intentionally;
- define which target owns migrations;
- use persistent history or another explicit change signal;
- keep the extension's fetch bounded and time-safe;
- avoid passing managed objects across processes;
- publish a value snapshot to the widget;
- show stale or unavailable data as such;
- test install, update, host-app-not-running, and account changes.

An extension reading a local projection does not prove that the host app's
network or CloudKit operation finished. Widget refresh, remote notifications,
and timeline delivery are separate evidence.

## AI-derived records

On-device AI should enrich a record through a reviewable proposal:

~~~text
canonical local record
  -> immutable snapshot
  -> bounded model request
  -> typed proposal
  -> provenance and confidence context
  -> person review
  -> Core Data/SwiftData commit
  -> optional sync/export projection
~~~

Store the source revision, model route/version, generated fields, and review
decision when product policy requires it. Keep generated text distinguishable
from user-authored text. Do not write a model result into a synced field before
the person accepts it if that would make a speculative result appear as shared
truth.

Privacy choices should be visible and granular. A local Core Data record does
not imply that the record may be sent to a remote model, indexed for
discoverability, included in a widget, or shared through CloudKit.

## Data deletion and retention

Design deletion as a complete lifecycle:

1. remove the record from the local context/store;
2. remove derived AI records and cached projections;
3. consume or prune associated history according to policy;
4. decide whether a CloudKit mirror or shared projection needs deletion;
5. remove exported copies only where the app controls them;
6. update widgets, search, notifications, and system surfaces;
7. make the result visible after relaunch.

Do not claim that deleting a local object deleted every export or remote copy
unless the route actually controls and verifies those destinations.

## Adaptive and accessible persistence UI

Test status and conflict UI with:

- Dynamic Type and large accessibility sizes;
- VoiceOver labels for status, values, and actions;
- keyboard, pointer, and Switch Control;
- localization and right-to-left layout;
- reduced transparency and increased contrast;
- offline, account-unavailable, store-load-failure, and migration-error states;
- a person who has not seen the internal Core Data terms.

Use plain language rather than “context,” “fault,” “persistent history,” or
“object ID” in customer-facing copy. Those terms belong in diagnostics and
developer logs.

## Performance and energy

Do not fetch an entire history, relationship graph, or remote projection into a
small screen. Use predicates, sort descriptors, batch sizes, prefetching, and
bounded history consumption. Move import, indexing, and migration work off the
main queue when the API and target support it.

Measure cold launch, store load, first list, scroll, edit/save, background
import, widget refresh, and sync reconciliation on representative devices.
Avoid making every view update perform a new fetch when a feature-owned
projection is sufficient.

## Design review checklist

- The UI distinguishes local save, sync, import, conflict, and failure.
- Empty, loading, unavailable, and truly empty states are not conflated.
- Glass groups actual actions and is not the only status indicator.
- Core Data/SwiftData ownership and target boundaries are explicit.
- Managed objects stay on their context queue and cross-context work uses IDs
  or immutable snapshots.
- AI-derived values remain reviewable and provenance-aware.
- Widgets/extensions receive bounded value projections.
- Delete, migration, offline, account, and conflict flows are designed.
- Dynamic Type, VoiceOver, localization, RTL, contrast, and reduced effects are
  part of the normal design, not a final polish pass.

## Related routes

- [Core Data stack, contexts, and managed objects](../42-framework-deep-dives/58-core-data-stack-contexts-and-managed-objects.md)
- [Core Data persistence and SwiftData interoperability route](../50-capability-recipes/81-core-data-persistence-and-swiftdata-interoperability-route.md)
- [Core Data persistence proof matrix](../60-verification/75-core-data-persistence-proof-matrix.md)
- [Core Data and SwiftData recipes](../70-code-recipes/93-core-data-and-swiftdata-recipes.md)
- [Liquid Glass state, morphing, and AI review shells](../20-liquid-glass/06-ai-review-shell-and-glass-state.md)
- [Offline, sync, conflict, and native data surfaces](34-sync-conflict-and-offline-native-surfaces.md)

## Sources

- [Core Data](https://developer.apple.com/documentation/coredata/)
- [NSPersistentContainer](https://developer.apple.com/documentation/coredata/nspersistentcontainer)
- [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer)
- [Using Core Data in the background](https://developer.apple.com/documentation/coredata/using-core-data-in-the-background)
- [Migrating your data model automatically](https://developer.apple.com/documentation/coredata/migrating-your-data-model-automatically)
- [Adopting SwiftData for a Core Data app](https://developer.apple.com/documentation/coredata/adopting-swiftdata-for-a-core-data-app)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [DefaultStore](https://developer.apple.com/documentation/swiftdata/defaultstore)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

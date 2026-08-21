# App Intents transfer, ownership, and execution capability route

## Outcome

Build an App Intents route that can safely:

- transfer an app entity as a meaningful system value;
- accept a large set of entity IDs without eager hydration;
- expose ownership/sharing context for sensitive actions;
- donate context-specific media entities where documented;
- run in the correct target and runtime mode;
- extend, cancel, checkpoint, and undo work;
- return actionable localized errors.

This route is appropriate for documents, saved places, contacts, media,
projects, tasks, and other domain records. It is not a license to expose a
private database to every system surface.

## Route selection

| Need | Primary contract |
| --- | --- |
| Show a record in a system dialog | DisplayRepresentation |
| Describe the type | TypeDisplayRepresentation |
| Send a location/person to another app | Transferable + IntentValueRepresentation |
| Process many selected records | EntityCollection<Entity> |
| Explain shared/public impact | OwnershipProvidingEntity + EntityOwnership |
| Suggest media in a documented contextual surface | RelevantEntities |
| Choose app/extension process | allowedExecutionTargets |
| Adapt behavior to current process mode | IntentModes + systemContext.currentMode |
| Run beyond ordinary background time | LongRunningIntent |
| Clean up after cancel/timeout | CancellableIntent |
| Register a reversible local action | UndoableIntent |
| Tell the person how to recover | AppIntentError |

## Domain service

Keep system-facing types thin and move truth, authorization, and mutation into
a domain service.

~~~swift
import Foundation

struct ProjectRecord: Identifiable, Sendable {
    let id: UUID
    let stableID: String?
    let title: String
    let summary: String
    let latitude: Double?
    let longitude: Double?
    let accountID: String
    let isShared: Bool
    let isPublic: Bool
    let isDeleted: Bool
    let revision: Int
}

protocol ProjectStore: Sendable {
    func accountID() async -> String?
    func record(id: UUID) async throws -> ProjectRecord?
    func record(stableID: String) async throws -> ProjectRecord?
    func records(ids: [UUID]) async throws -> [ProjectRecord]
    func updateTitle(id: UUID, title: String, expectedRevision: Int) async throws
    func delete(ids: [UUID]) async throws -> [UUID]
    func restore(ids: [UUID]) async throws
}

enum ProjectIntentFailure: Error, Sendable {
    case signedOut
    case missing
    case unauthorized
    case revisionConflict
    case invalidTransfer
    case partialFailure
}
~~~

The store interface contains only current domain operations. It does not expose a
SwiftUI view model, a database context, a system index, or a window.

## AppEntity with a system transfer value

A saved project that represents a place can export a PlaceDescriptor. The exact
coordinate initializer and system value spelling must be confirmed in the
selected SDK.

~~~swift
import AppIntents
import CoreLocation

struct ProjectEntity: AppEntity, Identifiable, Transferable, Sendable {
    let id: UUID
    let title: String
    let summary: String
    let latitude: Double?
    let longitude: Double

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Project place")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(summary)"
        )
    }

    static let defaultQuery = ProjectEntityQuery()

    static var transferRepresentation: some TransferRepresentation {
        IntentValueRepresentation(
            exporting: { project in
                guard let latitude = project.latitude else {
                    throw ProjectIntentFailure.invalidTransfer
                }

                return PlaceDescriptor(
                    representations: [
                        .coordinate(
                            CLLocationCoordinate2D(
                                latitude: latitude,
                                longitude: project.longitude
                            )
                        )
                    ],
                    commonName: project.title
                )
            }
        )
    }
}
~~~

This is export-only because the app has not yet defined a safe import policy.
That is intentional. Add importing only when a PlaceDescriptor can be
validated and resolved without silently creating or overwriting a project.

## Entity query and current authorization

~~~swift
struct ProjectEntityQuery: EntityQuery, Sendable {
    let store: any ProjectStore

    func entities(for identifiers: [ProjectEntity.ID]) async throws -> [ProjectEntity] {
        guard let accountID = await store.accountID() else {
            throw ProjectIntentFailure.signedOut
        }

        return try await store.records(ids: identifiers)
            .filter {
                $0.accountID == accountID &&
                !$0.isDeleted &&
                $0.latitude != nil
            }
            .map {
                ProjectEntity(
                    id: $0.id,
                    title: $0.title,
                    summary: $0.summary,
                    latitude: $0.latitude,
                    longitude: $0.longitude!
                )
            }
    }

    func suggestedEntities() async throws -> [ProjectEntity] {
        // Return a small, authorized set only.
        []
    }
}
~~~

The query does not trust titles or coordinates carried by an old shortcut. It
re-resolves the ID against the current account and store.

## Bidirectional import as a draft

If the product wants to receive a PlaceDescriptor, isolate conversion from
mutation.

~~~swift
struct ProjectDraft: Sendable {
    let title: String
    let latitude: Double
    let longitude: Double
    let source: String
}

struct ProjectImportService: Sendable {
    let store: any ProjectStore

    func draft(from place: PlaceDescriptor) async throws -> ProjectDraft {
        guard
            let coordinate = place.representations.firstCoordinate,
            (-90...90).contains(coordinate.latitude),
            (-180...180).contains(coordinate.longitude)
        else {
            throw ProjectIntentFailure.invalidTransfer
        }

        return ProjectDraft(
            title: place.commonName ?? "Imported place",
            latitude: coordinate.latitude,
            longitude: coordinate.longitude,
            source: "system-place-value"
        )
    }
}
~~~

The PlaceDescriptor member names are illustrative; compile the exact selected
SDK API. The service returns a draft. A separate app-owned review/commit route
decides whether to create a record.

## EntityCollection for a bulk action

Use identifiers when the action does not need full entity hydration.

~~~swift
struct ArchiveProjectsIntent: AppIntent {
    static var title: LocalizedStringResource {
        "Archive Projects"
    }

    @Parameter(title: "Projects")
    var projects: EntityCollection<ProjectEntity>

    @Dependency
    var store: ProjectStore

    func perform() async throws -> some IntentResult {
        guard await store.accountID() != nil else {
            throw AppIntentError.UserActionRequired.signin
        }

        let ids = projects.identifiers
        guard !ids.isEmpty else {
            return .result()
        }

        let archived = try await store.delete(ids: ids.map(\.self))
        return .result(
            dialog: "Archived \(archived.count) projects."
        )
    }
}
~~~

The parameter and dependency declarations need the exact selected SDK property
wrapper requirements. The important contract is to use IDs for the bulk
mutation, re-check authorization, and report the actual committed count.

For a destructive action, add the product's confirmation boundary and define
partial failure. Do not call resolvedEntities() just to display every title if a
count and scope are enough.

## OwnershipProvidingEntity

Use ownership flags derived from current domain state.

~~~swift
struct ShareAwareProjectEntity: OwnershipProvidingEntity, Identifiable, Sendable {
    let id: UUID
    let title: String
    let isShared: Bool
    let isPublic: Bool

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Project")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(title)")
    }

    var ownership: EntityOwnership {
        var value: EntityOwnership = []
        if isShared { value.insert(.shared) }
        if isPublic { value.insert(.public) }
        if !isShared && !isPublic {
            return value
        }
        return value
    }

    static let defaultQuery = ShareAwareProjectQuery()
}
~~~

The exact macro/protocol availability is beta-sensitive. Do not infer public
status from a public URL if the underlying record is not public, and do not
return a shared flag after the share was revoked.

## Confirm before a sensitive mutation

Ownership context can improve system confirmation, but the intent still needs
domain authorization and confirmation.

~~~swift
struct DeleteProjectIntent: AppIntent {
    static var title: LocalizedStringResource {
        "Delete Project"
    }

    @Parameter(title: "Project")
    var project: ShareAwareProjectEntity

    @Dependency
    var store: ProjectStore

    func perform() async throws -> some IntentResult {
        guard let accountID = await store.accountID() else {
            throw AppIntentError.UserActionRequired.signin
        }

        guard
            let current = try await store.record(id: project.id),
            current.accountID == accountID,
            !current.isDeleted
        else {
            throw AppIntentError.Unrecoverable("Project is no longer available.")
        }

        // Add the selected SDK's current confirmation API or schema-specific
        // confirmation boundary before the mutation.
        _ = try await store.delete(ids: [project.id])
        return .result(dialog: "Project deleted.")
    }
}
~~~

Use a revision token if the destructive action can race with an edit. For
shared/public data, state the impact in the confirmation copy.

## Context-specific RelevantEntities donation

RelevantEntities is documented for media-oriented contextual suggestions such
as workouts. Keep it behind a product-specific adapter.

~~~swift
struct MediaSuggestionService: Sendable {
    func updateForWorkout(_ entities: [any AppEntity]) async throws {
        try await RelevantEntities.shared.updateEntities(
            entities,
            for: .workout
        )
    }

    func clearWorkoutSuggestions() async throws {
        try await RelevantEntities.shared.removeAllEntities(for: .workout)
    }
}
~~~

The context enum and entity types must be checked in the selected SDK. Donate a
bounded replacement set, clear it when the workout/context ends, and remove
deleted/revoked records. Do not use this route as a general ranking API.

## Intent modes

Declare a mode based on the action's process needs.

~~~swift
struct OpenProjectIntent: OpenIntent {
    static var supportedModes: IntentModes {
        .foreground
    }

    static var allowedExecutionTargets: IntentExecutionTargets {
        .main
    }

    var target: ProjectEntity

    func perform() async throws -> some IntentResult {
        if systemContext.currentMode == .background,
           systemContext.currentMode.canContinueInForeground {
            try await continueInForeground()
        }

        await AppServices.shared.navigation.openProject(id: target.id)
        return .result()
    }
}
~~~

The exact continueInForeground() availability and return behavior must be
verified in the selected SDK. If a foreground transition is unavailable, the
intent should return an actionable result instead of touching a missing window.

For a background-safe save, use .background and keep the code free of UI
dependencies. For a route that may start in background and later need UI,
document the dynamic/deferred mode and test both paths.

## allowedExecutionTargets

Restrict target execution when the default is too broad.

~~~swift
struct SaveDraftIntent: AppIntent {
    static var allowedExecutionTargets: IntentExecutionTargets {
        [.main, .appIntentsExtension]
    }

    func perform() async throws -> some IntentResult {
        // Use extension-safe dependencies and current account state.
        return .result()
    }
}

struct WidgetValueQuery: EntityQuery {
    static var allowedExecutionTargets: IntentExecutionTargets {
        .widgetKitExtension
    }

    // Implement the query using extension-safe storage.
}
~~~

Confirm that the selected target actually links the App Intents declarations,
dependencies, resources, and privacy configuration. A shared Swift package does
not automatically make every dependency safe in an extension.

## Dependency injection

Register process-safe dependencies through the documented App Intents
dependency mechanism.

~~~swift
struct ProjectServices {
    let store: any ProjectStore
    let navigation: ProjectNavigation
}

extension AppServices {
    static func registerIntentDependencies() {
        AppDependencyManager.shared.add {
            ProjectServices(
                store: ProductionProjectStore(),
                navigation: ProductionProjectNavigation()
            )
        }
    }
}

struct ProjectIntent: AppIntent {
    @Dependency
    var services: ProjectServices

    func perform() async throws -> some IntentResult {
        guard await services.store.accountID() != nil else {
            throw AppIntentError.UserActionRequired.signin
        }
        return .result()
    }
}
~~~

The registration location and dependency initializer are SDK/target-specific.
The dependency must be Sendable and extension-safe if the intent can run there.
Do not register a main-actor navigation object for a background-only target.

## Package and extension composition

Share pure intent definitions through an AppIntentsPackage.

~~~swift
struct ProjectIntentPackage: AppIntentsPackage {
    static var includedPackages: [any AppIntentsPackage.Type] {
        []
    }
}

struct MainAppIntentPackage: AppIntentsPackage {
    static var includedPackages: [any AppIntentsPackage.Type] {
        [ProjectIntentPackage.self]
    }
}
~~~

An App Intents extension can register intent types outside the main app:

~~~swift
struct ProjectAppIntentsExtension: AppIntentsExtension {
    // Add the exact extension configuration required by the selected SDK.
}
~~~

Keep the package dependency graph explicit. Test discovery from the main app,
App Intents extension, and any widget extension separately.

## Long-running work with checkpoints

Use a resumable domain job for large work.

~~~swift
struct ExportProjectsIntent: LongRunningIntent {
    static var title: LocalizedStringResource {
        "Export Projects"
    }

    @Parameter(title: "Project IDs")
    var projects: EntityCollection<ProjectEntity>

    @Dependency
    var exporter: ProjectExporter

    func perform() async throws -> some IntentResult {
        let ids = projects.identifiers

        let result = try await performBackgroundTask(
            options: LongRunningTaskOptions()
        ) {
            progress.totalUnitCount = Int64(max(ids.count, 1))

            for (offset, id) in ids.enumerated() {
                try Task.checkCancellation()
                try await exporter.exportOne(
                    id: id,
                    checkpoint: offset
                )
                progress.completedUnitCount = Int64(offset + 1)
                progress.localizedAdditionalDescription =
                    "\(offset + 1) of \(ids.count)"
            }

            return "Export complete"
        }

        return .result(dialog: "\(result)")
    }
}
~~~

ProgressReportingIntent, LongRunningTaskOptions, and the exact method overload
must be confirmed against the selected SDK. The exporter should persist a job
ID/checkpoint and make repeat execution idempotent. Do not write 100 percent
before finalization.

## Cancellation cleanup

Wrap work with the documented intent cancellation handler when the reason
matters.

~~~swift
struct CancellableExportIntent: LongRunningIntent, CancellableIntent {
    @Dependency
    var exporter: ProjectExporter

    func perform() async throws -> some IntentResult {
        let result = try await withIntentCancellationHandler(
            operation: {
                try await exporter.runResumableExport()
            },
            onCancel: { reason in
                Task {
                    await exporter.checkpointAndRelease(reason: reason)
                }
            }
        )

        return .result(dialog: result)
    }
}
~~~

The handler must finish quickly. Do not start a second long task inside
onCancel. Persist a checkpoint, release resources, and leave committed records
valid. If the operation is not resumable, provide an honest partial-completion
state.

## Undoable local edit

Register an inverse after the forward mutation succeeds.

~~~swift
struct RenameProjectIntent: UndoableIntent {
    @Parameter(title: "Project")
    var project: ProjectEntity

    @Parameter(title: "New title")
    var newTitle: String

    @Dependency
    var store: ProjectStore

    @MainActor
    func perform() async throws -> some IntentResult {
        guard
            let old = try await store.record(id: project.id),
            let undoManager
        else {
            throw ProjectIntentFailure.missing
        }

        try await store.updateTitle(
            id: project.id,
            title: newTitle,
            expectedRevision: old.revision
        )

        let previous = old.title
        undoManager.registerUndo(withTarget: UndoTarget()) { _ in
            Task {
                try? await store.updateTitle(
                    id: project.id,
                    title: previous,
                    expectedRevision: old.revision + 1
                )
            }
        }

        return .result(dialog: "Project renamed.")
    }

    final class UndoTarget: NSObject {}
}
~~~

This is a route sketch. The actual undo closure needs a conflict-safe domain
operation and must not capture a non-Sendable store incorrectly. If
undoManager is nil, use a separate app-owned history route or complete without
undo according to product policy; do not force-unwrap it.

## Actionable errors

Return localized App Intent errors for fixable states.

~~~swift
struct PermissionAwareProjectIntent: AppIntent {
    func perform() async throws -> some IntentResult {
        guard await AppServices.shared.permissions.canUseProjects else {
            throw AppIntentError.UserActionRequired.accountSetup
        }

        guard await AppServices.shared.permissions.canUseLocation else {
            throw AppIntentError.PermissionRequired.location(precise: false)
        }

        return .result()
    }
}
~~~

Use the exact permission error and initializer supported by the selected SDK.
Do not put private entity titles or raw server errors into the system dialog.

## Fixture plan

Use a fake store and exporter to prove:

- export representation emits a valid PlaceDescriptor for a located project;
- a missing coordinate fails without a partial domain mutation;
- EntityCollection operates on IDs without eager full hydration;
- shared/public flags follow current record state;
- relevant donations replace and clear a bounded set;
- background mode does not touch UI;
- currentMode foreground/background branches are deterministic;
- target restrictions match the intended process;
- long-running progress reaches completion only after finalization;
- cancellation checkpoints and releases resources;
- undo restores only the expected revision;
- missing permission/sign-in returns actionable error.

## Sources

- https://developer.apple.com/documentation/appintents/appentity
- https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types
- https://developer.apple.com/documentation/appintents/intentvaluerepresentation
- https://developer.apple.com/documentation/appintents/appentity/valuerepresentation
- https://developer.apple.com/documentation/appintents/entitycollection
- https://developer.apple.com/documentation/appintents/ownershipprovidingentity
- https://developer.apple.com/documentation/appintents/entityownership
- https://developer.apple.com/documentation/appintents/relevantentities
- https://developer.apple.com/documentation/appintents/donations-and-discovery
- https://developer.apple.com/documentation/appintents/intentmodes
- https://developer.apple.com/documentation/appintents/intentmodes/current
- https://developer.apple.com/documentation/appintents/intentsystemcontext/currentmode
- https://developer.apple.com/documentation/appintents/appintent/supportedmodes-5zhmb
- https://developer.apple.com/documentation/appintents/appintent/allowedexecutiontargets
- https://developer.apple.com/documentation/appintents/intentexecutiontargets
- https://developer.apple.com/documentation/appintents/longrunningintent
- https://developer.apple.com/documentation/appintents/cancellableintent
- https://developer.apple.com/documentation/appintents/undoableintent
- https://developer.apple.com/documentation/appintents/undoableintent/undomanager
- https://developer.apple.com/documentation/appintents/app-intents
- https://developer.apple.com/documentation/appintents/appintentspackage
- https://developer.apple.com/documentation/appintents/app-extension
- https://developer.apple.com/documentation/appintents/appintenterror
- https://developer.apple.com/documentation/appintents/appintenterror/permissionrequired
- https://developer.apple.com/documentation/appintents/appintenterror/useractionrequired
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/documentation/swiftui/navigation
- https://developer.apple.com/design/human-interface-guidelines/

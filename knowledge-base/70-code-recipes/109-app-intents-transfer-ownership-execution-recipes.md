# App Intents transfer, ownership, and execution code recipes

## How to use these recipes

These are compile-oriented route sketches. Confirm every protocol requirement,
property wrapper, macro, availability annotation, and system-value initializer
against the selected Xcode/iOS SDK.

The recipes preserve this boundary:

    typed AppEntity/value
      -> system bridge
      -> current domain resolver
      -> target/process policy
      -> explicit commit/progress/cancel/undo
      -> result or actionable error

A snippet that type-checks does not prove that the system selects the intended
target, a destination app accepts the transfer, or a physical system surface
shows the result.

## Recipe 1: project entity with display and transfer representations

~~~swift
import AppIntents
import CoreLocation

struct PlaceProject: AppEntity, Transferable, Sendable {
    let id: UUID
    let name: String
    let region: String
    let coordinate: CLLocationCoordinate2D?

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Project place")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: "\(region)"
        )
    }

    static let defaultQuery = PlaceProjectQuery()

    static var transferRepresentation: some TransferRepresentation {
        IntentValueRepresentation(
            exporting: { project in
                guard let coordinate = project.coordinate else {
                    throw TransferError.noCoordinate
                }

                return PlaceDescriptor(
                    representations: [.coordinate(coordinate)],
                    commonName: project.name
                )
            }
        )
    }

    enum TransferError: Error {
        case noCoordinate
    }
}
~~~

The transfer representation exposes a place value, not the project's private
notes, account ID, or persistence object. Add importing only after a draft and
authorization policy exist.

## Recipe 2: bidirectional transfer with an explicit importer

~~~swift
struct ImportedPlaceDraft: Sendable {
    let name: String
    let coordinate: CLLocationCoordinate2D
    let source: String
}

extension PlaceProject {
    static var bidirectionalTransferRepresentation: some TransferRepresentation {
        IntentValueRepresentation(
            exporting: { project in
                guard let coordinate = project.coordinate else {
                    throw TransferError.noCoordinate
                }
                return PlaceDescriptor(
                    representations: [.coordinate(coordinate)],
                    commonName: project.name
                )
            },
            importing: { place in
                guard let coordinate = place.representations.firstCoordinate else {
                    throw TransferError.invalidPlace
                }
                return PlaceProject(
                    id: UUID(),
                    name: place.commonName ?? "Imported place",
                    region: "Imported",
                    coordinate: coordinate
                )
            }
        )
    }
}
~~~

This importer is only a value conversion sketch. In a real app, return a draft
or resolve an existing record before any save. The exact PlaceDescriptor members
and Transferable conformance must compile in the selected SDK.

## Recipe 3: entity collection IDs

~~~swift
struct BulkArchiveIntent: AppIntent {
    @Parameter(title: "Projects")
    var projects: EntityCollection<PlaceProject>

    @Dependency
    var service: ProjectService

    func perform() async throws -> some IntentResult {
        guard await service.isSignedIn else {
            throw AppIntentError.UserActionRequired.signin
        }

        let ids = projects.identifiers
        let result = try await service.archive(ids: ids)
        return .result(
            dialog: "Archived \(result.committedCount) projects."
        )
    }
}
~~~

Use the ID collection when the operation can query/mutate without hydrating
every entity. Resolve full entities only for bounded display or confirmation.

## Recipe 4: collection resolution when needed

~~~swift
struct ReviewCollectionIntent: AppIntent {
    @Parameter(title: "Projects")
    var projects: EntityCollection<PlaceProject>

    func perform() async throws -> some IntentResult {
        let entities = try await projects.resolvedEntities()

        guard entities.count <= 20 else {
            throw AppIntentError.UserActionRequired.confirmation
        }

        let names = entities.map(\.name).joined(separator: ", ")
        return .result(dialog: "Reviewing \(names).")
    }
}
~~~

Do not use full resolution as a logging shortcut. The system may pass many IDs,
and the app must keep the display bounded and authorized.

## Recipe 5: ownership flags

~~~swift
struct SharedProject: OwnershipProvidingEntity, Sendable {
    let id: UUID
    let name: String
    let shared: Bool
    let publiclyVisible: Bool

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Project")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }

    var ownership: EntityOwnership {
        var result: EntityOwnership = []
        if shared { result.insert(.shared) }
        if publiclyVisible { result.insert(.public) }
        return result
    }

    static let defaultQuery = SharedProjectQuery()
}
~~~

Only derive flags from current domain/share state. If the share is being
revoked or the record is still loading, return a safe unknown/deferred route
rather than stale ownership.

## Recipe 6: ownership-aware delete boundary

~~~swift
struct DeleteSharedProjectIntent: AppIntent {
    @Parameter(title: "Project")
    var project: SharedProject

    @Dependency
    var service: ProjectService

    func perform() async throws -> some IntentResult {
        guard await service.isSignedIn else {
            throw AppIntentError.UserActionRequired.signin
        }

        guard let current = try await service.current(id: project.id) else {
            throw AppIntentError.Unrecoverable("The project is unavailable.")
        }

        guard current.canDelete else {
            throw AppIntentError.UserActionRequired.confirmation
        }

        try await service.delete(id: project.id, expectedRevision: current.revision)
        return .result(dialog: "Project deleted.")
    }
}
~~~

The actual confirmation API may be supplied by an App Intent schema or current
SDK method. The domain service must still enforce authorization and revision
checks after any system confirmation.

## Recipe 7: contextual media donation adapter

~~~swift
struct WorkoutSuggestionService: Sendable {
    func replaceSuggestions(_ items: [any AppEntity]) async throws {
        try await RelevantEntities.shared.updateEntities(
            items,
            for: .workout
        )
    }

    func clearSuggestions() async throws {
        try await RelevantEntities.shared.removeAllEntities(for: .workout)
    }

    func remove(_ items: [any AppEntity]) async throws {
        try await RelevantEntities.shared.removeEntities(
            items,
            from: .workout
        )
    }
}
~~~

RelevantEntities is not a generic ranking primitive. Verify the context and
entity types for the selected SDK, replace the set intentionally, and clear
stale/revoked items.

## Recipe 8: explicit foreground target

~~~swift
struct OpenPlaceIntent: OpenIntent {
    static var supportedModes: IntentModes {
        .foreground
    }

    static var allowedExecutionTargets: IntentExecutionTargets {
        .main
    }

    var target: PlaceProject

    func perform() async throws -> some IntentResult {
        guard await AppServices.shared.store.isAvailable(target.id) else {
            throw AppIntentError.Unrecoverable("The place is unavailable.")
        }

        await AppServices.shared.navigation.openPlace(id: target.id)
        return .result()
    }
}
~~~

This route must not be registered only in an extension target. Test cold and
warm app launch and ensure the navigation route re-resolves current data.

## Recipe 9: background-safe target

~~~swift
struct SaveProjectMetadataIntent: AppIntent {
    static var supportedModes: IntentModes {
        .background
    }

    static var allowedExecutionTargets: IntentExecutionTargets {
        .appIntentsExtension
    }

    @Dependency
    var store: ProjectStore

    func perform() async throws -> some IntentResult {
        guard await store.accountID() != nil else {
            throw AppIntentError.UserActionRequired.signin
        }

        try await store.savePendingMetadata()
        return .result(dialog: "Metadata saved.")
    }
}
~~~

This intent cannot assume a window, main-app singleton, or foreground-only
resource. Verify the extension has the store, model resources, privacy
configuration, and target membership it needs.

## Recipe 10: inspect current mode

~~~swift
struct MaybeOpenProjectIntent: AppIntent {
    static var supportedModes: IntentModes {
        [.background, .foreground(.dynamic)]
    }

    func perform() async throws -> some IntentResult {
        switch systemContext.currentMode {
        case .foreground:
            await AppServices.shared.navigation.openRecentProject()
        case .background:
            if systemContext.currentMode.canContinueInForeground {
                try await continueInForeground()
            } else {
                try await AppServices.shared.store.prepareBackgroundRoute()
            }
        default:
            try await AppServices.shared.store.prepareBackgroundRoute()
        }

        return .result()
    }
}
~~~

The exact mode cases and continuation method must be confirmed in the selected
SDK. Keep the branch idempotent so a foreground transition does not duplicate a
mutation.

## Recipe 11: dependency manager seam

~~~swift
struct IntentServices: Sendable {
    let store: any ProjectStore
    let operationLog: OperationLog
}

enum IntentDependencyRegistration {
    static func register() {
        AppDependencyManager.shared.add {
            IntentServices(
                store: ProductionProjectStore(),
                operationLog: ProductionOperationLog()
            )
        }
    }
}

struct StoreProjectIntent: AppIntent {
    @Dependency
    var services: IntentServices

    func perform() async throws -> some IntentResult {
        guard await services.store.accountID() != nil else {
            throw AppIntentError.UserActionRequired.signin
        }

        try await services.store.commitPendingProject()
        return .result(dialog: "Project saved.")
    }
}
~~~

Register dependencies for every target that can execute the intent. Avoid
injecting a MainActor navigation coordinator into a background-only intent.

## Recipe 12: package composition

~~~swift
struct SharedProjectIntents: AppIntentsPackage {
    static var includedPackages: [any AppIntentsPackage.Type] {
        []
    }
}

struct ProductAppIntents: AppIntentsPackage {
    static var includedPackages: [any AppIntentsPackage.Type] {
        [SharedProjectIntents.self]
    }
}

struct ProductAppIntentsExtension: AppIntentsExtension {
    // Supply selected SDK extension configuration here.
}
~~~

Compile the main app, shared package, and App Intents extension as separate
targets. Verify that a package is registered once and that dependencies do not
accidentally require UI frameworks.

## Recipe 13: long-running operation

~~~swift
struct ExportProjectIntent: LongRunningIntent {
    @Parameter(title: "Projects")
    var projects: EntityCollection<PlaceProject>

    @Dependency
    var exporter: ProjectExporter

    func perform() async throws -> some IntentResult {
        let ids = projects.identifiers

        let output = try await performBackgroundTask(
            options: LongRunningTaskOptions()
        ) {
            progress.totalUnitCount = Int64(max(1, ids.count))

            for (index, id) in ids.enumerated() {
                try Task.checkCancellation()
                try await exporter.export(id: id, checkpoint: index)
                progress.completedUnitCount = Int64(index + 1)
            }

            return "Export complete"
        }

        return .result(dialog: output)
    }
}
~~~

Persist an operation ID/checkpoint. Progress should describe committed work,
not merely loop iterations. Confirm the exact overload and progress type in the
selected SDK.

## Recipe 14: cancellation with reason

~~~swift
struct CancellableExportIntent: LongRunningIntent, CancellableIntent {
    @Dependency
    var exporter: ProjectExporter

    func perform() async throws -> some IntentResult {
        let output = try await withIntentCancellationHandler(
            operation: {
                try await exporter.run()
            },
            onCancel: { reason in
                Task {
                    await exporter.checkpointAndRelease(reason)
                }
            }
        )

        return .result(dialog: output)
    }
}
~~~

The cancellation handler should stop child work, persist a safe checkpoint,
release media/model/file resources, and finish quickly. It must not pretend that
cancellation rolled back already committed work.

## Recipe 15: undo after commit

~~~swift
struct RenameProjectIntent: UndoableIntent {
    @Parameter(title: "Project")
    var project: PlaceProject

    @Parameter(title: "Name")
    var name: String

    @Dependency
    var service: ProjectService

    @MainActor
    func perform() async throws -> some IntentResult {
        guard
            let prior = try await service.current(id: project.id),
            let undoManager
        else {
            throw AppIntentError.Unrecoverable("Undo is unavailable.")
        }

        try await service.rename(
            id: project.id,
            name: name,
            expectedRevision: prior.revision
        )

        let priorName = prior.name
        let priorRevision = prior.revision
        undoManager.registerUndo(withTarget: UndoTarget()) { _ in
            Task {
                try? await service.rename(
                    id: project.id,
                    name: priorName,
                    expectedRevision: priorRevision + 1
                )
            }
        }

        return .result(dialog: "Project renamed.")
    }

    final class UndoTarget: NSObject {}
}
~~~

This is a sketch. A production undo closure needs a Sendable, revision-aware
domain operation. If the undo manager is nil, use an app-owned history route or
state the action is not undoable; do not force-unwrap.

## Recipe 16: actionable permission errors

~~~swift
struct PhotoBackedProjectIntent: AppIntent {
    func perform() async throws -> some IntentResult {
        guard await AppServices.shared.permissions.photos else {
            throw AppIntentError.PermissionRequired.photos
        }

        guard await AppServices.shared.permissions.accountReady else {
            throw AppIntentError.UserActionRequired.accountSetup
        }

        return .result()
    }
}
~~~

Use the specific App Intent error supported by the selected SDK. Keep raw
permission diagnostics out of the spoken/displayed error.

## Recipe 17: error mapping

~~~swift
enum ProjectErrorMapper {
    static func intentError(_ error: Error) -> AppIntentError {
        switch error {
        case ProjectError.signedOut:
            return .UserActionRequired.signin
        case ProjectError.needsConfirmation:
            return .UserActionRequired.confirmation
        case ProjectError.photosDenied:
            return .PermissionRequired.photos
        default:
            return .Unrecoverable("The project could not be updated.")
        }
    }
}
~~~

Map errors to a localized action. The generic fallback must not contain a raw
server message, private title, access token, or database identifier.

## Recipe 18: deterministic test seams

~~~swift
struct FakeProjectService: Sendable {
    var records: [UUID: ProjectFixture]
    var signedIn: Bool

    func current(id: UUID) async throws -> ProjectFixture? {
        guard signedIn else { return nil }
        return records[id]
    }

    func archive(ids: [UUID]) async throws -> ArchiveResult {
        let valid = ids.compactMap { records[$0] }.filter { !$0.deleted }
        return ArchiveResult(committedCount: valid.count)
    }
}

struct ProjectFixture: Sendable {
    let id: UUID
    let name: String
    let revision: Int
    let deleted: Bool
}

struct ArchiveResult: Sendable {
    let committedCount: Int
}
~~~

Use the seams to test conversion, account filtering, collection behavior,
process modes, checkpoints, cancellation, undo conflicts, and localized
errors before calling a physical system route verified.

## Recipe 19: evidence packet

~~~swift
struct AppIntentEvidence: Codable, Sendable {
    let appVersion: String
    let build: String
    let sdk: String
    let device: String
    let os: String
    let process: String
    let route: String
    let result: String
    let fixture: String
    let notes: String
}
~~~

Store fixture labels and redacted route notes rather than raw private titles,
queries, stable IDs, or account tokens.

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
- https://developer.apple.com/design/human-interface-guidelines/

# App Intents schema, entity, and execution recipes

These are compile-oriented route sketches for the selected iOS 26 SDK. They are not claimed to compile in this documentation-only workspace. Schema macro requirements, generated conformances, beta APIs, target membership, universal-link configuration, and exact generic signatures must be checked in Xcode.

Every recipe assumes:

- entities expose only a privacy-reviewed projection;
- queries use current account-scoped domain data;
- stable IDs are real across-device identifiers;
- imported values, URLs, and model proposals are untrusted;
- system discovery is separate from authorization and side effects;
- physical-device, system, and release evidence are recorded separately.

## Recipe 1: schema-backed entity

Use a documented domain only when the app’s content genuinely matches it:

~~~swift
@AppEntity(schema: .photos.album)
struct ProjectCollectionEntity: AppEntity {
    let id: UUID
    var name: String
    var creationDate: Date?
    var collectionType: CollectionType

    static let defaultQuery = ProjectCollectionQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: collectionType.localizedLabel
        )
    }
}
~~~

The schema and required fields are SDK-sensitive. Xcode-generated templates are the authority for the selected domain. Do not label an arbitrary project collection as a Photos album unless the semantics and required behavior match.

## Recipe 2: entity query by stable identifier

Resolve the current record and omit items that no longer exist:

~~~swift
struct ProjectCollectionQuery: EntityQuery {
    @Dependency private var store: ProjectStore

    func entities(
        for identifiers: [ProjectCollectionEntity.ID]
    ) async throws -> [ProjectCollectionEntity] {
        let current = try await store.collections(
            ids: identifiers,
            account: .current
        )

        return current.map(ProjectCollectionEntity.init)
    }

    func suggestedEntities()
        async throws -> [ProjectCollectionEntity]
    {
        try await store.recentCollections(account: .current)
            .map(ProjectCollectionEntity.init)
    }
}
~~~

Do not return a stale cached entity simply because the system supplied its ID. Re-check account, permission, deletion, and archived state in the domain adapter.

## Recipe 3: stable identity across devices

If the server-issued UUID is stable on every device, the entity can adopt SyncableEntity:

~~~swift
struct ArticleEntity: AppEntity, SyncableEntity {
    var id: UUID
    var title: String
}
~~~

If local and stable IDs differ, use the documented paired identifier type:

~~~swift
struct LocalPhotoEntity: AppEntity, SyncableEntity {
    var id: SyncableEntityIdentifier<String, String>
    var creationDate: Date

    init(localID: String, stableID: String, creationDate: Date) {
        self.id = SyncableEntityIdentifier(
            local: localID,
            stable: stableID
        )
        self.creationDate = creationDate
    }
}
~~~

After resolving a stable ID on a second device, still check the current account and permissions. Stable identity does not imply record availability or authorization.

## Recipe 4: ownership-aware entity

Return current sharing/public state:

~~~swift
struct SharedProjectEntity: OwnershipProvidingEntity {
    let id: UUID
    var name: String
    var isShared: Bool
    var isPublic: Bool

    var ownership: EntityOwnership {
        var result: EntityOwnership = []
        if isShared {
            result.insert(.shared)
        }
        if isPublic {
            result.insert(.public)
        }
        return result
    }
}
~~~

Refresh isShared and isPublic before a destructive or sensitive action. If the source cannot determine the state, return unknown or require app review according to the selected SDK and product policy.

## Recipe 5: export a system value

Bridge an app entity to a known system value only when the conversion is safe:

~~~swift
struct TrailEntity: AppEntity, Transferable {
    let id: UUID
    let name: String
    let startCoordinate: CLLocationCoordinate2D

    static var transferRepresentation: some TransferRepresentation {
        IntentValueRepresentation(
            exporting: { trail in
                PlaceDescriptor(
                    representations: [
                        .coordinate(trail.startCoordinate)
                    ],
                    commonName: trail.name
                )
            }
        )
    }
}
~~~

If bidirectional import is needed, validate the imported PlaceDescriptor against the current account and domain. Do not export private notes, hidden coordinates, or access tokens with the place.

## Recipe 6: universal-link entity

Use an opaque stable ID in a real universal link:

~~~swift
extension TrailEntity: URLRepresentableEntity {
    static var urlRepresentation: URLRepresentation {
        "https://example.com/trail/\(.id)/details"
    }
}
~~~

The domain and associated-domain configuration are separate from this declaration. On open, re-check authentication, account, deletion, and permission. Do not use a custom URL scheme for this representation or put private fields in the path/query.

## Recipe 7: singleton settings entity

Use UniqueAppEntity only when there is exactly one conceptual value:

~~~swift
struct AppSettingsEntity: UniqueAppEntity {
    let id = "settings"
    var displayName: String
    var notificationsEnabled: Bool

    static let defaultQuery = AppSettingsQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "App settings")
    }
}

struct AppSettingsQuery: UniqueAppEntityQuery {
    func uniqueEntity() async throws -> AppSettingsEntity {
        try await SettingsStore.shared.currentEntity()
    }
}
~~~

Do not use this route for a collection with a preferred item. A collection needs a normal query and explicit disambiguation.

## Recipe 8: a finite union parameter

Use UnionValue only for a finite set of semantically distinct values:

~~~swift
@UnionValue
enum DestinationChoice {
    case project(ProjectEntity)
    case archive
    case inbox
}

struct RouteCaptureIntent: AppIntent {
    static var title: LocalizedStringResource = "Route capture"

    @Parameter(title: "Destination")
    var destination: DestinationChoice

    func perform() async throws -> some IntentResult {
        switch destination {
        case .project(let project):
            try await CaptureActions.routeToProject(project.id)
        case .archive:
            try await CaptureActions.archive()
        case .inbox:
            try await CaptureActions.routeToInbox()
        }
        return .result()
    }
}
~~~

This syntax is intentionally a route sketch. Confirm the macro declaration and associated case requirements in the final SDK. Never use a union to accept arbitrary model text or an unbounded JSON payload.

## Recipe 9: explicit runtime modes

Declare the smallest supported foreground/background contract:

~~~swift
struct ExportProjectIntent: AppIntent {
    static var title: LocalizedStringResource = "Export project"
    static let supportedModes: IntentModes = [
        .background,
        .foreground(.deferred)
    ]

    @Parameter var project: ProjectEntity

    func perform() async throws -> some IntentResult {
        if systemContext.currentMode == .background,
           systemContext.currentMode.canContinueInForeground
        {
            try await continueInForeground(
                IntentDialog("Open the app to review the export.")
            )
        }

        let url = try await ExportService.shared.export(project.id)
        return .result(value: url)
    }
}
~~~

Do not call continueInForeground without a product reason. If a system context cannot transition, return a background-safe result or a precise UserActionRequired error.

## Recipe 10: long-running intent with progress

Use the documented long-running route for bounded file, sync, model, or processing work:

~~~swift
struct ProcessLargeFileIntent: LongRunningIntent {
    static var title: LocalizedStringResource = "Process large file"

    @Parameter var file: IntentFile
    var progress = Progress()

    func perform() async throws -> some IntentResult & ReturnsValue<String> {
        let result = try await performBackgroundTask {
            progress.totalUnitCount = 100
            progress.localizedDescription = "Processing file"

            for index in 0..<100 {
                try Task.checkCancellation()
                try await FileProcessor.shared.processChunk(
                    file: file,
                    index: index
                )
                progress.completedUnitCount = Int64(index + 1)
            }

            return "Processing complete"
        }

        return .result(value: result)
    }
}
~~~

Checkpoint work so a failure or cancellation cannot create a false completed record. Report progress often enough for the system to understand that the operation is alive. The exact ProgressReportingIntent conformance and property shape must be checked against the target SDK.

## Recipe 11: cancellation cleanup

Use CancellableIntent when cancellation needs cleanup beyond normal task cancellation:

~~~swift
struct ImportArchiveIntent: CancellableIntent {
    static var title: LocalizedStringResource = "Import archive"

    @Parameter var file: IntentFile

    func perform() async throws -> some IntentResult {
        try await withIntentCancellationHandler(
            operation: {
                try await ArchiveImporter.shared.importFile(file)
            },
            onCancel: { reason in
                ArchiveImporter.shared.recordCancellation(reason)
                ArchiveImporter.shared.closePartialOutput()
            }
        )

        return .result()
    }
}
~~~

Cancellation handlers must finish quickly. Close files, release resources, and persist a recoverable checkpoint; do not start a new long task from the cancellation handler.

## Recipe 12: register an undo operation

Register an inverse action when the intent can be undone:

~~~swift
struct RenameProjectIntent: UndoableIntent {
    static var title: LocalizedStringResource = "Rename project"

    let projectID: UUID
    let newName: String

    func perform() async throws -> some IntentResult {
        let oldName = try await ProjectStore.shared.name(id: projectID)
        try await ProjectActions.rename(id: projectID, to: newName)

        undoManager?.registerUndo(withTarget: ProjectUndoTarget.shared) {
            Task {
                try? await ProjectActions.rename(
                    id: projectID,
                    to: oldName
                )
            }
        }

        return .result()
    }
}
~~~

The app owns the undo and redo interaction. The AppIntent should not call undo() or redo(). If undoManager is nil, keep the rename valid and expose app-owned recovery if the product requires it.

## Recipe 13: precise permission error

Map a protected-service failure to a system-understandable recovery:

~~~swift
struct ScanNearbyIntent: AppIntent {
    static var title: LocalizedStringResource = "Scan nearby devices"

    func perform() async throws -> some IntentResult {
        guard BluetoothAccess.shared.isAuthorized else {
            throw AppIntentError.PermissionRequired.bluetooth
        }

        try await NearbyScanner.shared.scan()
        return .result()
    }
}
~~~

The precise error is not a replacement for the in-app permission education path. The app should explain why the capability is needed and what happens after denial.

## Recipe 14: contextual entity association

Associate a privacy-reviewed entity with visible app content using the documented App Intents and activity route:

~~~swift
struct ProjectDetailView: View {
    let project: ProjectEntity

    var body: some View {
        ProjectEditor(project: project)
            .userActivity("project.detail") { activity in
                activity.title = project.displayRepresentation.title
                activity.appEntityIdentifier = project.id
            }
    }
}
~~~

The exact user-activity modifier and identifier type are SDK-sensitive. The association is context, not authorization. Re-resolve the entity when the system invokes an action.

## Recipe 15: relevance donation lifecycle

Replace the complete suggestion set for a context:

~~~swift
func updateWorkoutSuggestions(
    _ entities: [MediaEntity]
) async {
    do {
        try await RelevantEntities.shared.updateEntities(
            entities,
            for: .audio
        )
    } catch {
        Logger.appIntents.error("Suggestion donation failed")
    }
}

func clearWorkoutSuggestions() async {
    try? await RelevantEntities.shared.removeAllEntities(
        for: .audio
    )
}
~~~

Do not append indefinitely. The documented update replaces the previous set for the context. Clear it when no suggestion is appropriate, when the user signs out, or when the source is no longer authorized.

## Recipe 16: schema plus explicit mutation boundary

Keep system understanding and domain side effects separate:

~~~swift
@AppIntent(schema: .system.open)
struct OpenProjectIntent: AppIntent {
    static var title: LocalizedStringResource = "Open project"

    @Parameter(title: "Project")
    var project: ProjectEntity

    func perform() async throws -> some IntentResult {
        guard try await ProjectAuthorization.shared.canOpen(project.id) else {
            throw AppIntentError.UserActionRequired(
                "Sign in to open this project."
            )
        }

        return .result(
            opensIntent: OpenProjectInAppIntent(projectID: project.id)
        )
    }
}
~~~

This keeps a schema-backed action from becoming a raw database callback. Confirm the schema, result builder, and error initializer in the selected SDK.

## Verification fixture

Use a fake store to exercise the lifecycle without Siri or Apple Intelligence:

~~~text
seed private entity A with stable ID S1
resolve S1 on device one
resolve S1 on device two
change A to shared
invoke sensitive action -> confirmation required
delete A
resolve S1 -> unavailable, no private title
import a malformed system value -> reject
invoke long task -> progress and checkpoint
cancel -> cleanup and resumable state
invoke undoable action -> inverse registered
sign out -> clear entity/context/relevance projections
~~~

## Sources

- [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [SyncableEntity](https://developer.apple.com/documentation/appintents/syncableentity)
- [OwnershipProvidingEntity](https://developer.apple.com/documentation/appintents/ownershipprovidingentity)
- [IntentValueRepresentation](https://developer.apple.com/documentation/appintents/intentvaluerepresentation)
- [RelevantEntities](https://developer.apple.com/documentation/appintents/relevantentities)
- [UniqueAppEntity](https://developer.apple.com/documentation/appintents/uniqueappentity)
- [UniqueAppEntityQuery](https://developer.apple.com/documentation/appintents/uniqueappentityquery)
- [UnionValue](https://developer.apple.com/documentation/appintents/unionvalue%28%29)
- [URLRepresentableIntent](https://developer.apple.com/documentation/appintents/urlrepresentableintent)
- [URLRepresentableEntity](https://developer.apple.com/documentation/appintents/urlrepresentableentity)
- [Intent modes](https://developer.apple.com/documentation/appintents/intentmodes)
- [AppIntent supported modes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [LongRunningIntent](https://developer.apple.com/documentation/appintents/longrunningintent)
- [CancellableIntent](https://developer.apple.com/documentation/appintents/cancellableintent)
- [UndoableIntent](https://developer.apple.com/documentation/appintents/undoableintent)
- [AppIntent permission errors](https://developer.apple.com/documentation/appintents/appintenterror/permissionrequired)
- [App Intent updates](https://developer.apple.com/documentation/updates/appintents)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)

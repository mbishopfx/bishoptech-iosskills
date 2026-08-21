# SwiftUI App Intents, Shortcuts, Spotlight, and interactive snippet review recipes

These are compile-oriented Swift sketches for a named app target. They are not claimed to compile in this documentation-only workspace and they do not prove Siri, Shortcuts, Spotlight, Visual Intelligence, snippet, scene, accessibility, privacy, physical-device, or release behavior.

Read the [system-discoverability review](../42-framework-deep-dives/101-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review.md), [design guide](../21-design-deep-dives/129-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-design.md), [capability route](../50-capability-recipes/132-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-route.md), and [proof matrix](../60-verification/126-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-proof-matrix.md) first. Check the generated interface and deployment availability in the exact SDK used by the target before copying any signature into production code.

## Recipe 1: Make an app-owned action explicit

Keep the intent thin. It should validate current state and delegate the domain mutation to an actor or repository that the app also uses from its normal SwiftUI screens.

~~~swift
import AppIntents

struct CompleteTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Complete task"
    static var description = IntentDescription("Marks a selected task complete.")
    static var openAppWhenRun: Bool = false

    @Parameter(title: "Task")
    var task: TaskEntity

    init() {}

    init(task: TaskEntity) {
        self.task = task
    }

    func perform() async throws -> some IntentResult {
        let operation = TaskOperation(taskID: task.id, expectedRevision: task.revision)
        try await TaskStore.shared.complete(operation)
        return .result()
    }
}
~~~

The operation carries an expected revision so a stale system invocation cannot silently overwrite a newer edit. Authentication, entitlement, confirmation, and user-visible error policy belong in the operation boundary, not in a view-only wrapper.

## Recipe 2: Project an app model into an AppEntity

An AppEntity is a stable, system-facing projection. Do not expose an entire persistence object or sensitive fields merely because the app has them.

~~~swift
import AppIntents

struct TaskEntity: AppEntity, Identifiable, Sendable {
    let id: String
    let title: String
    let isCompleted: Bool
    let revision: String

    static var typeDisplayRepresentation =
        TypeDisplayRepresentation(name: "Task")

    static var defaultQuery = TaskQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: isCompleted ? "Completed" : "Open"
        )
    }
}

struct TaskQuery: EntityQuery {
    func entities(
        for identifiers: [TaskEntity.ID]
    ) async throws -> [TaskEntity] {
        try await TaskStore.shared.entities(for: identifiers)
    }

    func suggestedEntities() async throws -> [TaskEntity] {
        try await TaskStore.shared.suggestedEntities(limit: 10)
    }
}
~~~

The query is a current resolver, not a cache of whatever the user saw when an intent was donated. If an identifier was deleted, return only resolvable entities and let the caller surface an explicit “no longer available” path when the operation requires one.

## Recipe 3: Keep entity resolution bounded and cancellable

Queries may run outside the foreground scene. Use an actor-owned store, honor cancellation, and avoid loading a whole catalog just to resolve a small identifier list.

~~~swift
actor TaskStore {
    static let shared = TaskStore()

    func entities(
        for identifiers: [String]
    ) async throws -> [TaskEntity] {
        try Task.checkCancellation()

        let records = try await database.fetchTasks(
            ids: Array(Set(identifiers))
        )

        try Task.checkCancellation()
        return records.map(TaskEntity.init)
    }

    func suggestedEntities(limit: Int) async throws -> [TaskEntity] {
        try Task.checkCancellation()
        return try await database.fetchSuggestedTasks(limit: limit)
            .map(TaskEntity.init)
    }

    func complete(_ operation: TaskOperation) async throws {
        try Task.checkCancellation()
        let current = try await database.fetchTask(id: operation.taskID)
        guard current.revision == operation.expectedRevision else {
            throw TaskError.staleRevision
        }
        guard !current.isCompleted else {
            return
        }
        try await database.markComplete(id: current.id)
    }
}
~~~

The database calls are placeholders for the app’s real persistence boundary. The important contract is bounded lookup, current revision checking, cancellation, idempotence, and an error that a system surface can present without leaking internal storage details.

## Recipe 4: Publish a small App Shortcuts surface

App Shortcuts should expose a few common, high-value actions with phrases that sound natural when spoken. The current Human Interface Guidelines limit an app to ten App Shortcuts; treat that as a ceiling, not a target.

~~~swift
import AppIntents

struct TaskShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        [
            AppShortcut(
                intent: CompleteTaskIntent(),
                phrases: [
                    "Complete a task in \(.applicationName)",
                    "Mark a task done in \(.applicationName)"
                ],
                shortTitle: "Complete task",
                systemImageName: "checkmark.circle"
            ),
            AppShortcut(
                intent: OpenTodayIntent(),
                phrases: [
                    "Show today in \(.applicationName)"
                ],
                shortTitle: "Show today",
                systemImageName: "calendar"
            )
        ]
    }

    static var shortcutTileColor: ShortcutTileColor = .blue
}
~~~

Use the app name token in phrases. Keep the short title a compact action label. If a phrase depends on a parameter, make the parameter’s display representation meaningful when spoken and test the parameterized route in Siri and Shortcuts.

## Recipe 5: Refresh parameter metadata deliberately

If the app changes the set of parameter choices used by an App Shortcut, refresh the metadata from an app lifecycle point that is reached after the data is ready. Do not make a shortcut’s first invocation depend on a network-only catalog.

~~~swift
import AppIntents
import SwiftUI

@main
struct TasksApp: App {
    var body: some Scene {
        WindowGroup {
            RootView()
                .task {
                    await TaskStore.shared.refreshShortcutParametersIfNeeded()
                    AppShortcutsProvider.updateAppShortcutParameters()
                }
        }
    }
}
~~~

The exact refresh timing and generated metadata shape are SDK-sensitive. Confirm the method in the target SDK and observe whether a first-install, restore, offline, and account-switch path produce the expected choices.

## Recipe 6: Donate a direct user interaction

Donations are a prediction signal for actions the person actually performed in the app. They are not a substitute for App Shortcuts and should not be emitted for speculative AI suggestions or background observations.

~~~swift
func recordCompletedTask(_ task: TaskEntity) async {
    do {
        try await CompleteTaskIntent(task: task).donate()
    } catch is CancellationError {
        return
    } catch {
        // Donation failure must not roll back the user-visible mutation.
        logger.debug("Intent donation failed: \(error.localizedDescription)")
    }
}
~~~

Call this after the app-owned mutation succeeds. Keep donation payloads minimal and avoid putting private free-form text into metadata that can appear in system suggestions.

## Recipe 7: Index an entity for Spotlight

Use IndexedEntity when the app wants a typed AppEntity projection to participate in system search. Index only the fields that are useful for finding or opening the entity.

~~~swift
import AppIntents
import CoreSpotlight

struct IndexedTask: IndexedEntity, Identifiable, Sendable {
    let id: String
    let title: String
    let projectName: String

    static var typeDisplayRepresentation =
        TypeDisplayRepresentation(name: "Task")

    static var defaultQuery = IndexedTaskQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: projectName
        )
    }

    var attributeSet: CSSearchableItemAttributeSet {
        let attributes = CSSearchableItemAttributeSet(
            contentType: "public.item"
        )
        attributes.title = title
        attributes.containerTitle = projectName
        return attributes
    }
}

func indexTasks(_ tasks: [IndexedTask]) async throws {
    let index = CSSearchableIndex(name: "TasksIndex")
    try await index.indexAppEntities(tasks)
}
~~~

The exact overloads and availability should be checked against the target SDK. Treat indexing as a projection that can be rebuilt; the database remains the source of truth.

## Recipe 8: Delete, reindex, and recover the Spotlight projection

Deletion is part of correctness. Remove an entity when it is deleted or stops being eligible, then reindex after a schema or display change.

~~~swift
import AppIntents
import CoreSpotlight

actor TaskSearchIndex {
    private let index = CSSearchableIndex(name: "TasksIndex")

    func upsert(_ task: IndexedTask) async throws {
        try Task.checkCancellation()
        try await index.indexAppEntities([task])
    }

    func remove(taskID: String) async throws {
        try Task.checkCancellation()
        try await index.deleteAppEntities(identifiedBy: [taskID])
    }

    func rebuild(_ tasks: [IndexedTask]) async throws {
        try Task.checkCancellation()
        try await index.deleteAllSearchableItems()
        try await index.indexAppEntities(tasks)
    }
}
~~~

A rebuild must be bounded or chunked for a large catalog. Test a delete, rename, account switch, logout, reinstall, and migration. If the app supports an IndexedEntityQuery reindex route, use it for the system-requested reindex contract and keep the app’s own rebuild command for controlled recovery.

## Recipe 9: Describe a system-requested reindex route

IndexedEntityQuery is currently marked beta in the Apple documentation consulted for this knowledge base. Treat it as an SDK-availability and release-review gate, not as an unqualified promise of long-term API stability.

~~~swift
import AppIntents

struct TaskIndexedEntityQuery: IndexedEntityQuery {
    func entities(
        for identifiers: [TaskEntity.ID]
    ) async throws -> [TaskEntity] {
        try await TaskStore.shared.entities(for: identifiers)
    }

    func suggestedEntities() async throws -> [TaskEntity] {
        try await TaskStore.shared.suggestedEntities(limit: 10)
    }

    func reindexEntities(_ entities: [TaskEntity]) async throws {
        try await TaskSearchIndex.shared.upsert(
            entities.map(IndexedTask.init)
        )
    }

    func reindexAllEntities() async throws {
        let tasks = try await TaskStore.shared.allIndexableEntities()
        try await TaskSearchIndex.shared.rebuild(
            tasks.map(IndexedTask.init)
        )
    }
}
~~~

Treat the method names and associated types as a compile checkpoint. Keep this route separate from a user-facing “refresh” button so a system reindex cannot accidentally mutate domain state.

## Recipe 10: Open one entity in the app

An OpenIntent is the typed handoff from a system result to an app-owned scene or route. It should open the entity, not repeat a destructive action.

~~~swift
import AppIntents

struct OpenTaskIntent: OpenIntent {
    static var title: LocalizedStringResource = "Open task"

    @Parameter(title: "Task")
    var target: TaskEntity

    init() {}

    init(target: TaskEntity) {
        self.target = target
    }

    func perform() async throws -> some IntentResult {
        await AppRouteCoordinator.shared.openTask(
            id: target.id,
            revision: target.revision
        )
        return .result()
    }
}
~~~

The app scene must still resolve the ID against current storage. A deleted task should land on a recoverable empty state or search result, not a screen that pretends the old entity still exists.

## Recipe 11: Hand large in-app search results back to the app

Use a system result for a compact, typed answer. If the result set is large or needs the app’s full filtering and editing UI, use a dedicated in-app search-results intent/route.

~~~swift
import AppIntents

struct ShowTaskSearchResultsIntent: ShowInAppSearchResultsIntent {
    static var title: LocalizedStringResource = "Show task search results"

    @Parameter(title: "Search")
    var query: String

    init() {}

    init(query: String) {
        self.query = query
    }

    func perform() async throws -> some IntentResult {
        await AppRouteCoordinator.shared.openTaskSearch(query: query)
        return .result()
    }
}
~~~

The exact protocol requirements are SDK-sensitive. The route should preserve the query, focus the search field when appropriate, and let the user refine or clear it. Do not use this handoff to bypass app authentication or expose private results to an untrusted scene.

## Recipe 12: Debounce a SwiftUI in-app search query

Core Spotlight search and SwiftUI search suggestions have different roles. A local in-app search view can debounce text changes and cancel the previous operation before starting a new one.

~~~swift
import CoreSpotlight
import SwiftUI

@MainActor
final class SearchModel: ObservableObject {
    @Published var text = ""
    @Published private(set) var results: [SearchResult] = []

    private var searchTask: Task<Void, Never>?

    func update(text: String) {
        self.text = text
        searchTask?.cancel()

        searchTask = Task { [weak self] in
            do {
                try await Task.sleep(for: .milliseconds(300))
                try Task.checkCancellation()
                guard let self else { return }
                let value = try await self.searchIndex.search(text: self.text)
                try Task.checkCancellation()
                self.results = value
            } catch is CancellationError {
                return
            } catch {
                self.results = []
            }
        }
    }
}
~~~

The search index implementation is app-owned in this sketch. If using CSUserQuery or CSSearchQuery, create one operation for the current text, cancel the prior operation when text changes, and avoid treating lexical or semantic ranking as authorization.

## Recipe 13: Render an interactive snippet from current state

An interactive snippet should be a compact result or confirmation surface. The intent that renders it reads current state, and controls inside it call App Intents rather than performing ad hoc view mutations.

~~~swift
import AppIntents
import SwiftUI

struct TaskStatusSnippet: SnippetIntent {
    static var title: LocalizedStringResource = "Task status"

    let task: TaskEntity

    var snippet: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(task.title)
                .font(.headline)
            Text(task.isCompleted ? "Completed" : "Open")
                .foregroundStyle(.secondary)

            if !task.isCompleted {
                Button(intent: CompleteTaskIntent(task: task)) {
                    Label("Complete", systemImage: "checkmark")
                }
            }
        }
        .padding()
    }

    func perform() async throws -> some IntentResult {
        return .result()
    }
}

struct ShowTaskStatusIntent: AppIntent {
    static var title: LocalizedStringResource = "Show task status"

    @Parameter(title: "Task")
    var task: TaskEntity

    func perform() async throws -> some IntentResult & ShowsSnippetIntent {
        // Confirm the exact result/snippet initializer in the target SDK.
        return .result()
    }
}
~~~

The result/snippet return shape has changed with the evolving App Intents APIs. Keep the intent and snippet separated, verify the generated interface, and test a repeated invocation after the action changes state. A snippet shown for a stale entity must reload or resolve again rather than display a cached “completed” claim.

## Recipe 14: Ask a snippet to reload after an interactive action

Use the documented snippet reload mechanism when a control changes the state represented by the snippet. The reload must be safe to call more than once.

~~~swift
struct ToggleTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle task"

    @Parameter(title: "Task")
    var task: TaskEntity

    func perform() async throws -> some IntentResult {
        try await TaskStore.shared.toggle(
            id: task.id,
            expectedRevision: task.revision
        )

        await TaskSnippetReloadCoordinator.shared.reload(
            entityID: task.id
        )
        return .result()
    }
}

actor TaskSnippetReloadCoordinator {
    static let shared = TaskSnippetReloadCoordinator()

    func reload(entityID: String) async {
        // Call the SnippetIntent reload API from the target SDK here.
        // Keep this operation presentation-only and idempotent.
    }
}
~~~

Do not place a long-running network operation inside the snippet’s render path. Return a bounded result, show a recoverable error, or route to the app for work that needs sustained progress.

## Recipe 15: Provide Visual Intelligence semantic context

Visual Intelligence integration is a semantic context contract. Return app-owned entities only when the descriptor is broad enough to be useful and specific enough to avoid an unsafe false match.

~~~swift
import AppIntents
import VisualIntelligence

struct FindNearbyLandmarkIntent: AppIntent {
    static var title: LocalizedStringResource = "Find nearby landmark"

    @Parameter(
        title: "Landmark",
        inputQuery: LandmarkValueQuery()
    )
    var landmark: LandmarkEntity

    func perform() async throws -> some IntentResult {
        await AppRouteCoordinator.shared.openLandmark(
            id: landmark.id
        )
        return .result()
    }
}

struct LandmarkValueQuery: IntentValueQuery {
    func values(
        for input: SemanticContentDescriptor
    ) async throws -> [LandmarkEntity] {
        let labels = input.labels
        guard labels.contains(where: LandmarkPolicy.accepts) else {
            return []
        }
        return try await LandmarkStore.shared.matches(
            descriptor: input
        )
    }
}
~~~

Use high-level, localized semantic labels rather than an entity’s private name as the matching contract. If the integration accepts a pixel buffer, apply a size, privacy, and processing policy before sending it to the matcher. The current documentation limits the number of descriptor-taking IntentValueQuery parameters; check the exact SDK restriction and use a union representation when the product truly needs multiple entity types.

## Recipe 16: Keep on-screen and scene context typed

When a system surface identifies an app-owned element, carry an entity identifier and a safe presentation hint. Resolve the object again when the scene opens.

~~~swift
struct PendingSystemRoute: Codable, Sendable {
    let entityType: String
    let entityID: String
    let source: Source
    let createdAt: Date

    enum Source: String, Codable, Sendable {
        case spotlight
        case visualIntelligence
        case siri
        case shortcut
        case snippet
    }
}

actor AppRouteCoordinator {
    static let shared = AppRouteCoordinator()

    func openTask(id: String, revision: String?) async {
        await routeStore.save(
            PendingSystemRoute(
                entityType: "task",
                entityID: id,
                source: .spotlight,
                createdAt: .now
            )
        )
    }
}
~~~

The concrete AppIntentSceneDelegate, UISceneAppIntent, or target-content-providing hook depends on the app’s scene architecture. Keep the handoff small enough to survive process termination and validate the route against current authentication and persistence state.

## Recipe 17: Make local AI a proposal layer

On-device intelligence may suggest a task, entity, or intent parameter. It should not become an unreviewed authority over a destructive mutation.

~~~swift
struct ProposedTaskAction: Sendable {
    let intentName: String
    let entityID: String
    let confidence: Double
    let sourceRevision: String
    let requiresConfirmation: Bool
}

actor LocalActionPlanner {
    func propose(
        text: String,
        currentEntities: [TaskEntity]
    ) async throws -> ProposedTaskAction? {
        try Task.checkCancellation()
        return try await onDeviceModel.propose(
            text: text,
            candidates: currentEntities
        )
    }
}

func apply(_ proposal: ProposedTaskAction) async throws {
    guard proposal.confidence >= 0.90 else {
        throw ActionError.needsReview
    }
    guard !proposal.requiresConfirmation else {
        throw ActionError.needsReview
    }

    let current = try await TaskStore.shared.entity(
        for: proposal.entityID
    )
    guard current.revision == proposal.sourceRevision else {
        throw ActionError.staleProposal
    }

    try await CompleteTaskIntent(task: current).perform()
}
~~~

The model proposes. The current entity resolver, authorization policy, confirmation UI, and domain operation decide whether anything happens. Log the proposal revision and the final decision without storing unnecessary private content.

## Recipe 18: Keep the native surface restrained

System surfaces already provide their own visual language. In the app-owned SwiftUI destination, use native controls, semantic materials, system typography, and Liquid Glass composition only where the surface benefits from hierarchy or depth.

~~~swift
import SwiftUI

struct TaskDestination: View {
    let task: TaskEntity

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(task.title)
                    .font(.largeTitle.weight(.semibold))

                Button("Complete", intent: CompleteTaskIntent(task: task))
                    .buttonStyle(.borderedProminent)
                    .disabled(task.isCompleted)
            }
            .padding()
        }
        .navigationTitle("Task")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Image(systemName: "checkmark.circle")
                    .accessibilityLabel("Complete task")
            }
        }
    }
}
~~~

Do not imitate system-owned Siri, Spotlight, or Shortcuts chrome inside the app. Keep the app’s own branding in the destination and let the system surface communicate that the action came from an App Intent.

## Recipe 19: Make system actions accessible

Accessibility is part of the App Intent contract. The same action should remain understandable through spoken output, Dynamic Type, VoiceOver, keyboard, Switch Control, and reduced-motion settings.

~~~swift
struct TaskRow: View {
    let task: TaskEntity

    var body: some View {
        HStack {
            Text(task.title)
                .lineLimit(2)
            Spacer()
            Image(systemName: task.isCompleted
                  ? "checkmark.circle.fill"
                  : "circle")
                .accessibilityHidden(true)
        }
        .contentShape(Rectangle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel(task.title)
        .accessibilityValue(task.isCompleted ? "Completed" : "Open")
        .accessibilityHint("Opens task details")
    }
}
~~~

Do not make an icon, color, or animation the only indication of an App Intent result. Test the short title, display representation, spoken phrase, error message, and confirmation path with accessibility enabled.

## Recipe 20: Record a system-surface proof packet

Keep evidence structured and tied to a build. A screenshot alone does not prove that the invoked intent resolved the current entity or completed the intended operation.

~~~swift
struct SystemSurfaceProof: Codable, Sendable {
    let build: String
    let device: String
    let os: String
    let surface: Surface
    let intentName: String
    let input: String
    let resolvedEntityID: String?
    let sourceRevision: String?
    let result: Result
    let evidencePath: String
    let recordedAt: Date

    enum Surface: String, Codable, Sendable {
        case appShortcut
        case shortcuts
        case siri
        case spotlight
        case snippet
        case visualIntelligence
        case appScene
    }

    enum Result: String, Codable, Sendable {
        case resolved
        case completed
        case opened
        case rejectedAsStale
        case cancelled
        case failed
    }
}
~~~

For release evidence, include the signed archive, target and entitlement inspection, device family, invocation surface, input, current-resolution result, side-effect result, accessibility observation, privacy behavior, and recovery behavior. Keep an explicit “not tested” record when a system surface is unavailable in the current environment.

## Recipe 21: Use a route checklist before shipping

Copy this checklist into the feature issue or release packet:

~~~text
[ ] AppIntent action has a stable title, description, parameters, and error policy.
[ ] AppEntity exposes only the minimum user-facing projection.
[ ] EntityQuery resolves current identifiers and honors cancellation.
[ ] Mutations are authorized, revision-checked, idempotent, and reviewable.
[ ] App Shortcuts cover common actions, use concise phrases, and stay within the current limit.
[ ] Direct app interactions donate only after success; speculative AI is not donated as fact.
[ ] IndexedEntity/Core Spotlight metadata can be rebuilt and deleted.
[ ] Logout, deletion, rename, migration, and reinstall remove stale search entries.
[ ] OpenIntent and large-search routes land on a current app scene.
[ ] Snippet rendering is short, current, and free of long-running work.
[ ] Interactive snippet controls are App Intents and reload after state changes.
[ ] Visual Intelligence labels are broad, privacy-safe, and tested for false matches.
[ ] On-device AI proposes; the current resolver and domain policy decide.
[ ] Native SwiftUI, Liquid Glass, accessibility, keyboard, and reduced-motion behavior are reviewed.
[ ] Physical-device system-surface checks are separated from simulator checks.
[ ] Archive, entitlement, privacy, fallback, and release evidence are attached.
~~~

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [AppShortcutsProvider](https://developer.apple.com/documentation/appintents/appshortcutsprovider)
- [AppShortcut](https://developer.apple.com/documentation/appintents/appshortcut)
- [Accelerating App Interactions with App Intents](https://developer.apple.com/documentation/appintents/acceleratingappinteractionswithappintents)
- [Donations and discovery](https://developer.apple.com/documentation/appintents/donations-and-discovery)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [Visual presentation](https://developer.apple.com/documentation/appintents/visual-presentation)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [IndexedEntityQuery](https://developer.apple.com/documentation/appintents/indexedentityquery)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [ShowInAppSearchResultsIntent](https://developer.apple.com/documentation/appintents/showinappsearchresultsintent)
- [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [AppIntentSceneDelegate](https://developer.apple.com/documentation/appintents/appintentscenedelegate)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSUserQuery](https://developer.apple.com/documentation/corespotlight/csuserquery)
- [CSSearchQuery](https://developer.apple.com/documentation/corespotlight/cssearchquery)
- [Building a search interface for your app](https://developer.apple.com/documentation/corespotlight/building-a-search-interface-for-your-app)
- [Integrating your app with Visual Intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [App Shortcuts HIG](https://developer.apple.com/design/human-interface-guidelines/app-shortcuts)
- [Snippets HIG](https://developer.apple.com/design/human-interface-guidelines/snippets)
- [Siri HIG](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Action button HIG](https://developer.apple.com/design/human-interface-guidelines/action-button)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

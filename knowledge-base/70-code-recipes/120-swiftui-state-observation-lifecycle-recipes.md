# SwiftUI state, Observation, and lifecycle recipes

## How to use these recipes

These recipes are small route sketches for a named SwiftUI app target. They
show ownership, dependency, navigation, restoration, task, preview, Liquid
Glass, and on-device AI seams. They are not proof that a target compiles or
that a physical device, system surface, model, or release artifact works.

Use the [state/lifecycle route](../50-capability-recipes/108-swiftui-state-observation-lifecycle-route.md),
the [proof matrix](../60-verification/102-swiftui-state-observation-lifecycle-proof-matrix.md),
the [native design contract](../21-design-deep-dives/105-state-ownership-and-native-lifecycle-design.md),
and the [framework deep dive](../42-framework-deep-dives/77-swiftui-observation-state-and-app-lifecycle.md).

## Observable model owned by App

Keep model creation at the owner and pass the same identity through the
environment:

~~~swift
import SwiftUI
import Observation

@Observable
final class WorkspaceModel {
    var title = "Untitled"
    var status: Status = .empty

    enum Status {
        case empty
        case loading
        case ready
        case failed(String)
    }

    func retry() async {
        status = .loading
        do {
            try await Task.sleep(for: .milliseconds(150))
            try Task.checkCancellation()
            status = .ready
        } catch is CancellationError {
            status = .empty
        } catch {
            status = .failed("Unable to load")
        }
    }
}

@main
struct ExampleApp: App {
    @State private var workspace = WorkspaceModel()

    var body: some Scene {
        WindowGroup {
            WorkspaceScreen()
                .environment(workspace)
        }
    }
}
~~~

The sample uses a bounded fake operation. Replace it with a service that has
explicit authorization, persistence, cancellation, and error policy.

## Read a typed environment model

Declare a required model when the hierarchy guarantees it:

~~~swift
struct WorkspaceScreen: View {
    @Environment(WorkspaceModel.self) private var workspace

    var body: some View {
        VStack {
            Text(workspace.title)
            switch workspace.status {
            case .empty:
                Button("Load") {
                    workspace.status = .loading
                }
            case .loading:
                ProgressView()
            case .ready:
                Text("Ready")
            case .failed(let message):
                Text(message)
                Button("Retry") {
                    Task {
                        await workspace.retry()
                    }
                }
            }
        }
        .padding()
    }
}
~~~

If a feature can legitimately render without the model, retrieve an optional
environment value and render an explicit unavailable state. Do not rely on a
runtime crash to reveal a missing preview/test dependency.

## Bind an observable model

Wrap the existing reference when controls need projected bindings:

~~~swift
struct WorkspaceEditor: View {
    @Bindable var workspace: WorkspaceModel

    var body: some View {
        Form {
            TextField("Title", text: $workspace.title)
        }
    }
}
~~~

Use a domain method instead when saving requires validation or authorization:

~~~swift
extension WorkspaceModel {
    func rename(_ proposed: String) {
        let trimmed = proposed.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        title = trimmed
    }
}
~~~

The binding is a UI connection; the model method is the domain boundary.

## Navigation with lightweight routes

Keep navigation data small and resolve models at the destination:

~~~swift
enum AppRoute: Hashable {
    case review(UUID)
    case settings
}

struct RootScreen: View {
    @State private var path: [AppRoute] = []

    var body: some View {
        NavigationStack(path: $path) {
            List {
                Button("Open review") {
                    path.append(.review(UUID()))
                }
                NavigationLink("Settings", value: AppRoute.settings)
            }
            .navigationDestination(for: AppRoute.self) { route in
                switch route {
                case .review(let id):
                    ReviewScreen(recordID: id)
                case .settings:
                    SettingsScreen()
                }
            }
        }
    }
}
~~~

Use a stable record identifier that the destination can resolve. Treat a
missing or unauthorized record as a visible state, not as a force unwrap.

## Restorable scene selection

Use SceneStorage only for a small, non-sensitive, per-scene value:

~~~swift
struct DetailScreen: View {
    @SceneStorage("detail.selectedTab") private var selectedTab = "summary"

    var body: some View {
        Picker("Section", selection: $selectedTab) {
            Text("Summary").tag("summary")
            Text("History").tag("history")
        }
        .pickerStyle(.segmented)
    }
}
~~~

Use a durable store for records, drafts, and sensitive content. Use a typed
NSUserActivity when the current activity needs to participate in restoration,
handoff, or system routing.

## Scene phase reconciliation

Observe the phase at the level that owns the work:

~~~swift
struct SceneRoot: View {
    @Environment(\.scenePhase) private var scenePhase
    @Environment(WorkspaceModel.self) private var workspace

    var body: some View {
        WorkspaceScreen()
            .onChange(of: scenePhase, initial: false) {
                if scenePhase == .active {
                    Task {
                        await workspace.retry()
                    }
                }
            }
    }
}
~~~

This is a sketch. A real app should distinguish refresh from retry, avoid
duplicate requests, and reconcile freshness/account/permission state. When a
scene backgrounds, persist bounded changes and expect termination.

## View task keyed to identity

Tie visible work to the identity that makes it relevant:

~~~swift
struct SearchScreen: View {
    let query: String
    @State private var model = SearchModel()

    var body: some View {
        ResultsList(results: model.results, status: model.status)
            .task(id: query) {
                await model.search(query)
            }
    }
}

@Observable
final class SearchModel {
    var results: [String] = []
    var status = "Idle"

    func search(_ query: String) async {
        status = "Loading"
        do {
            try await Task.sleep(for: .milliseconds(200))
            try Task.checkCancellation()
            results = query.isEmpty ? [] : ["Result for " + query]
            status = "Ready"
        } catch is CancellationError {
            status = "Canceled"
        } catch {
            status = "Failed"
        }
    }
}
~~~

The loader must honor cancellation. If the underlying service can return
after cancellation, compare the request identity or revision before applying
the result.

## Explicit model-owned task

Use an explicit task only when the work must outlive a particular view:

~~~swift
@Observable
final class ImportModel {
    var status = "Idle"
    private var task: Task<Void, Never>?

    func start() {
        task?.cancel()
        task = Task {
            status = "Running"
            do {
                try await performImport()
                try Task.checkCancellation()
                status = "Complete"
            } catch is CancellationError {
                status = "Canceled"
            } catch {
                status = "Failed"
            }
        }
    }

    func cancel() {
        task?.cancel()
    }

    private func performImport() async throws {
        try await Task.sleep(for: .seconds(1))
    }
}
~~~

For work that can outlive the model or requires actor isolation, move the
operation into an explicit actor/service and define ownership there. Do not
retain an unbounded task because a screen once appeared.

## Preview fixture factory

Provide the required model in a deterministic preview:

~~~swift
extension WorkspaceModel {
    static var reviewFixture: WorkspaceModel {
        let model = WorkspaceModel()
        model.title = "Reviewable proposal"
        model.status = .ready
        return model
    }
}

#Preview("Ready") {
    WorkspaceScreen()
        .environment(WorkspaceModel.reviewFixture)
}
~~~

Add separate fixtures for empty, loading, failed, denied, unavailable,
proposal, conflict, long content, and reduced-effects states. Never let a
preview silently call a live service.

## Parameterized preview states

Use preview arguments to exercise a fixture matrix:

~~~swift
enum ScreenFixture: String, CaseIterable {
    case empty
    case loading
    case failed
}

#Preview("State matrix", arguments: ScreenFixture.allCases) { fixture in
    FixtureScreen(fixture: fixture)
}
~~~

Keep the fixture enum and sample data local to the preview/test boundary.
Parameterized previews are design iteration evidence, not a substitute for
UI automation or physical settings runs.

## AI proposal state

Keep model output outside the domain commit:

~~~swift
enum ProposalState {
    case unavailable(String)
    case generating
    case ready(String, sourceID: UUID)
    case refused(String)
    case failed(String)
}

@Observable
final class ProposalModel {
    var state: ProposalState = .unavailable("Not started")

    func generate(sourceID: UUID, text: String) async {
        state = .generating
        do {
            try await Task.sleep(for: .milliseconds(100))
            try Task.checkCancellation()
            state = .ready("Review this draft", sourceID: sourceID)
        } catch is CancellationError {
            state = .unavailable("Canceled")
        } catch {
            state = .failed("Generation failed")
        }
    }
}
~~~

Before accepting, validate source identity, schema, permissions, revision,
and side-effect scope. Record model/profile/prompt/schema versions with any
saved result. Preserve manual entry when the model is unavailable or refuses.

## Liquid Glass state surface

Use a semantic control in a small state-driven surface:

~~~swift
struct ProposalAction: View {
    let state: ProposalState
    let accept: () -> Void

    var body: some View {
        Group {
            switch state {
            case .ready:
                Button("Review and accept", action: accept)
            case .generating:
                ProgressView("Generating")
            case .unavailable(let message),
                 .refused(let message),
                 .failed(let message):
                Label(message, systemImage: "exclamationmark.triangle")
            }
        }
        .padding()
        .glassEffect()
    }
}
~~~

Verify the exact Liquid Glass API and availability for the project’s SDK.
Keep the semantic label, focus, contrast, reduced-effects behavior, and manual
fallback even if the glass modifier is unavailable or disabled.

## Async fake for lifecycle tests

Use a controllable service to test cancellation and stale results:

~~~swift
actor ControlledSearchService {
    var requests: [String] = []
    var continuation: CheckedContinuation<[String], Never>?

    func search(_ query: String) async -> [String] {
        requests.append(query)
        return await withCheckedContinuation { continuation = $0 }
    }

    func finish(_ results: [String]) {
        continuation?.resume(returning: results)
        continuation = nil
    }
}
~~~

The test should:

1. start a request for query A;
2. change the task ID to query B;
3. finish A after cancellation;
4. finish B;
5. assert only B is visible.

The fake should also record cancellation when the real service supports it.

## Route checklist

- [ ] State chart lists empty/loading/ready/error and domain-specific states.
- [ ] Each value has one owner and a documented lifetime.
- [ ] Observable models are created in State at the real owner.
- [ ] Bindable wraps an existing model rather than creating a second one.
- [ ] Environment dependencies are supplied in app, preview, and test fixtures.
- [ ] Navigation path contains small stable routes, not full models or secrets.
- [ ] SceneStorage contains only lightweight non-sensitive per-scene state.
- [ ] View tasks are keyed to identity and cancellation-aware.
- [ ] Long-lived work has an explicit model/actor/service owner.
- [ ] Preview fixtures cover failure, unavailable, AI, accessibility, and glass.
- [ ] AI output is typed, reviewable, validated, and provenance-aware.
- [ ] Liquid Glass remains functional and understandable without the effect.
- [ ] Device, system-surface, accessibility, and release proofs are separate.

## Sources

- [Observation](https://developer.apple.com/documentation/observation)
- [Model data](https://developer.apple.com/documentation/swiftui/model-data)
- [Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [State](https://developer.apple.com/documentation/swiftui/state)
- [Bindable](https://developer.apple.com/documentation/swiftui/bindable)
- [Environment](https://developer.apple.com/documentation/swiftui/environment)
- [Environment values](https://developer.apple.com/documentation/swiftui/environment-values)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage)
- [Restoring your app’s state with SwiftUI](https://developer.apple.com/documentation/swiftui/restoring-your-app-s-state-with-swiftui)
- [task(name:priority:file:line:_:)](https://developer.apple.com/documentation/swiftui/view/task%28name%3Apriority%3Afile%3Aline%3A_%3A%29)
- [task(id:name:priority:file:line:_:)](https://developer.apple.com/documentation/swiftui/view/task%28id%3Aname%3Apriority%3Afile%3Aline%3A_%3A%29)
- [Task cancellation](https://developer.apple.com/documentation/swift/task/cancel%28%29)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Preview(_:traits:arguments:body:)](https://developer.apple.com/documentation/swiftui/preview%28_%3Atraits%3Aarguments%3Abody%3A%29)
- [Liquid Glass technology overview](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)

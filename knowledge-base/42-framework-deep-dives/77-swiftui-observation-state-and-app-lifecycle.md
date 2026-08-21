# SwiftUI Observation, state, and app lifecycle

## Purpose

SwiftUI becomes predictable when every visible value has an owner, every
binding has a clear write path, every async task has a lifetime, and every
scene can restore only the small state it is meant to restore.

This page joins the official SwiftUI model-data, Observation, navigation,
scene, state-restoration, task, and preview routes into one iOS 26 foundation.
It is about architecture and proof boundaries, not a claim that one property
wrapper solves persistence, networking, or domain truth.

Use this page with:

- [State ownership and native lifecycle design](../21-design-deep-dives/105-state-ownership-and-native-lifecycle-design.md)
- [SwiftUI state, Observation, and lifecycle route](../50-capability-recipes/108-swiftui-state-observation-lifecycle-route.md)
- [SwiftUI state, Observation, and lifecycle proof matrix](../60-verification/102-swiftui-state-observation-lifecycle-proof-matrix.md)
- [SwiftUI state, Observation, and lifecycle recipes](../70-code-recipes/120-swiftui-state-observation-lifecycle-recipes.md)
- [Testable native design and AI evaluation](../21-design-deep-dives/102-testable-native-design-and-ai-evaluation.md)

## The ownership rule

Start with one source of truth for each piece of data. Choose the smallest
owner that can outlive the view needing it and no larger:

    durable domain record -> persistence/service owner
    app-wide observable model -> App or Scene State
    scene-specific navigation/restoration -> scene owner
    shared configuration/service -> Environment
    local transient UI state -> view State
    child editing -> Binding or Bindable
    async work -> view task or explicit model-owned Task

The property wrapper is not the domain model. It controls how SwiftUI stores,
reads, observes, restores, or binds a value. A model can still need an actor,
database, service protocol, cancellation policy, or explicit transaction.

## Observation and dependency tracking

The Observation framework provides a type-safe observer pattern. In a SwiftUI
app, apply the Observable macro to a model type, then let views form
dependencies by reading the model’s properties in body.

Important consequences:

- A view updates for the observable properties it actually reads.
- A computed property participates when it reads observable properties.
- Passing an observable model through intermediate views does not make every
  intermediate view depend on every property.
- Applying the Observable protocol alone does not add the generated tracking
  behavior; use the macro.
- Observation support in SwiftUI begins with iOS 17, so iOS 26 can use it
  directly while older deployment targets may require the ObservableObject
  compatibility route.

This gives a useful performance and design boundary:

| Pattern | Result |
| --- | --- |
| Small view reads one model property | Narrow invalidation and clear dependency |
| Container reads an entire collection | Container depends on collection changes |
| Intermediate view passes model without reading it | Intermediate view need not redraw for model changes |
| Global/singleton model is read directly | SwiftUI can track the read, but ownership and test isolation become harder |
| View stores a reference but body never reads its properties | Property changes do not create a dependency |

Do not add observable fields merely to make a view refresh. Add a field because
it represents state the view owns or observes. Keep derived display values
close to the model or view that can explain their source.

## State ownership matrix

| SwiftUI route | Own this kind of value | Lifetime | Common mistake |
| --- | --- | --- | --- |
| State | Transient value or an Observable model instance owned by this hierarchy | View/App/Scene storage lifetime | Using it as a database or creating side effects in a default initializer |
| Binding | A child’s read/write connection to an existing source of truth | Parent source lifetime | Treating a binding as independent ownership |
| Bindable | Bindings into an Observable model | Model lifetime | Creating a second model instead of wrapping the existing one |
| Environment | Shared model or configuration available through a hierarchy | Applied subtree/scene lifetime | Assuming a required typed object is present when it is not |
| ObservableObject/StateObject | Compatibility model for older deployment targets or existing Combine-style code | StateObject owner lifetime | Mixing old and new ownership without a migration plan |
| SceneStorage | Lightweight per-scene restoration value | Scene lifetime and system-managed persistence | Storing sensitive data, large models, or assuming save timing |
| AppStorage | Small UserDefaults-backed preference | App preference lifetime | Treating a preference as canonical domain truth |
| Persistence framework | Durable records and relationships | Store/account/schema lifetime | Hiding migrations, conflicts, or server authority behind view state |

Put State at the highest view, App, or Scene that truly owns the value. Share
read-only access as a value or read the model through Environment. Share write
access as a Binding or expose an explicit model method when a write needs
validation, authorization, or a domain transaction.

## Creating an Observable model

A minimal model can be stored in State and injected through Environment:

~~~swift
import SwiftUI
import Observation

@Observable
final class WorkspaceModel {
    var title = "Untitled"
    var isReviewing = false
}

@main
struct ExampleApp: App {
    @State private var workspace = WorkspaceModel()

    var body: some Scene {
        WindowGroup {
            WorkspaceView()
                .environment(workspace)
        }
    }
}
~~~

The model’s lifetime is tied to the State owner, not to every redraw of the
view. Keep initialization cheap. If construction performs disk, network, or
model work, defer that work to a task or an explicit lifecycle method and make
the loading state visible.

## Bindings and editable models

Observation lets a view mutate a model directly when the model’s property is
the source of truth. Some controls require a Binding. Wrap the existing
observable reference with Bindable instead of creating another model:

~~~swift
struct WorkspaceEditor: View {
    @Bindable var workspace: WorkspaceModel

    var body: some View {
        Form {
            TextField("Title", text: $workspace.title)
            Toggle("Review mode", isOn: $workspace.isReviewing)
        }
    }
}
~~~

If a write must validate or trigger a side effect, prefer a method on the
model or a domain command over a raw binding. A Binding can express a legal
UI write; it cannot by itself prove authorization, persistence, sync, or
server success.

## Environment as dependency injection

The Environment is a hierarchical dependency channel:

- a value flows to the modified view and its descendants;
- a more-specific environment modifier can replace it;
- a typed observable model can be inserted directly;
- a custom EnvironmentValues entry can provide configuration or a service;
- a required typed object that is not present causes a runtime failure;
- use an optional typed lookup when the hierarchy legitimately may omit it.

Use Environment for dependencies that are meaningful across a subtree:

    view hierarchy
      -> AppState / repository / feature flags / clock / model service
      -> focused child views

Keep the default environment value safe for previews and tests. Do not hide a
production credential, network client with side effects, or user-specific
record behind an accidental global default.

For a service dependency, define a small protocol or value-bearing client and
inject a live implementation in the app and a deterministic implementation in
previews/tests. The environment transports the dependency; it does not choose
the correct authority for a domain operation.

## Navigation is data

NavigationStack can expose navigation state through a path binding. Use
lightweight Hashable route values, not large model objects, as path elements.
Map route values to destinations with navigationDestination.

    root
      -> route value
      -> destination view
      -> model lookup by stable identity

This separation keeps navigation serializable, testable, and resilient when a
model changes. A route should carry the minimum identity and presentation
intent needed to resolve a destination.

For a homogeneous route list, an Array of Hashable values is often clearer.
Use NavigationPath when the stack genuinely needs heterogeneous route types.
Do not use the path as a transport for raw media, unsaved edits, credentials,
or an entire observable model.

Stateful navigation is preferable to fire-and-forget view destinations when
the app needs to know what is on the stack, restore it, respond to deep links,
or test a route transition. Avoid using onAppear or a view task as the only
signal that a navigation link fired.

## Scene state and restoration

SwiftUI’s scene lifecycle matters on iPhone, iPad, and multi-window platforms.
Persist only the state that makes returning to the scene useful:

| State | Recommended owner |
| --- | --- |
| Selected tab or small filter | State or SceneStorage, depending on restoration need |
| Lightweight selected record ID | SceneStorage or activity payload |
| Navigation route/path | Codable route model plus SceneStorage/activity/persistence policy |
| Unsaved editor draft | Domain draft or explicit scene-scoped model, not a casual string key |
| Large data set | Durable persistence and query/fetch state |
| Secret or sensitive personal data | Protected persistence with explicit policy, not SceneStorage |

SceneStorage is per scene, system-managed, lightweight, property-list
compatible, and not guaranteed to persist at a specific time. It is not a
replacement for the app data model, and it should not contain sensitive data.
Use unique, scoped keys.

NSUserActivity can capture the user’s current activity and restore or hand it
back to the app. Use a stable activity type and typed payload. Treat the
payload as a hint that must be resolved against current domain data, not as
authority that bypasses authorization or freshness checks.

## ScenePhase and lifecycle policy

Read scenePhase from Environment. Its meaning depends on where it is read:

- inside a view, it describes the containing scene;
- inside App, it is an aggregate across the app’s scenes;
- active means foreground and interactive;
- inactive means foreground but should pause work;
- background means not visible, and the app may terminate soon.

Use phase changes to pause/reconcile/flush bounded work, not as a guarantee of
unlimited time. Persist domain changes before the app becomes background-only
when possible, and make recovery idempotent when termination happens earlier.

For a multi-window app, do not put per-window selection in an app-global
singleton merely because App receives a scene phase. Keep scene-specific state
in the scene hierarchy.

## View tasks and cancellation

View.task gives async work a lifetime matching the modified view. SwiftUI can
cancel it when the view disappears or changes identity. View.task with id also
cancels and restarts when the Equatable ID changes.

Cancellation is cooperative:

- cancel marks the task;
- the work must check cancellation or call an operation that honors it;
- Task.checkCancellation can throw;
- cancellation does not magically stop arbitrary synchronous work;
- cancellation should prevent stale results from being committed;
- cleanup and partial-result policy belong to the operation.

Use task for view-scoped work such as loading a selected record, observing an
AsyncSequence for a visible surface, or prewarming a bounded feature. Use an
explicit model-owned Task when the work must outlive the view or be shared by
multiple views. Store and cancel that task deliberately.

Avoid using onAppear to start unbounded work without an identity or
cancellation plan. If a query changes, make the query the task ID and make the
loader cancellation-aware:

~~~swift
struct SearchResultsView: View {
    let query: String
    @State private var state = SearchState()

    var body: some View {
        ResultsList(state.results)
            .task(id: query) {
                await state.load(query: query)
            }
    }
}
~~~

The task is not the domain truth. A result still needs revision, selection,
authorization, and persistence checks before it replaces visible or durable
state.

## Liquid Glass as stateful composition

Liquid Glass surfaces become easier to design when the model exposes explicit
states:

| Model state | Glass surface |
| --- | --- |
| Idle | One primary action with normal semantic label |
| Preparing | Progress and cancel action; no implied completion |
| Proposal ready | Reviewable content with source/provenance and accept/edit/reject |
| Applying | Disable duplicate actions and show the domain operation in progress |
| Applied | Show the committed result and undo/revision path if supported |
| Refused/unavailable | Keep manual path visible with a reason and fallback |
| Stale/conflicted | Show source revision and choose refresh/merge/manual resolution |

Use the system’s Liquid Glass route for small functional containers. Do not
move the canonical model into a visual effect or use animation as the only
state signal. Every glass action needs a semantic control, a focusable label,
contrast in the current appearance, and a non-glass fallback when effects are
reduced.

## On-device AI adapter state

Keep AI availability and domain truth separate:

    input/source -> availability gate -> model task
      -> typed proposal -> validation -> human review
      -> domain commit -> system projection

Model state should include at least:

- unavailable or unsupported;
- loading/prewarming;
- generating;
- partial output if the API supports it;
- completed proposal;
- refusal/error/context-limit;
- canceled;
- stale because source revision changed;
- accepted and committed by the domain layer.

Do not put a generated string directly into a saved record without a
provenance/review policy. A model can propose navigation or content; the app
still owns authorization, validation, persistence, and side effects.

## Preview fixtures are dependency contracts

Previews are excellent for state and composition iteration. Give each preview
the same required model/environment dependencies as the running view:

~~~swift
#Preview("Review ready") {
    WorkspaceScreen()
        .environment(WorkspaceModel.reviewFixture)
}
~~~

Use small deterministic fixtures:

- empty;
- loading;
- loaded;
- error;
- unavailable;
- long localized content;
- large Dynamic Type;
- dark/increased-contrast/reduced-transparency;
- AI proposal requiring review;
- Liquid Glass action disabled or canceled.

Parameterized previews can vary inputs across cases. PreviewModifier can share
expensive setup. Keep network, credentials, random time, and live user data
out of the fixture unless the preview explicitly models a failure boundary.

A preview proves that the view can render the supplied fixture in the preview
environment. It does not prove compilation for every target, physical
interaction, system-surface delivery, model availability, or release signing.

## Proof strategy

Verify each boundary with the smallest useful artifact:

| Claim | Evidence |
| --- | --- |
| State has one owner | Code review plus fixture showing initial/recreated view behavior |
| Observable change redraws the right view | Deterministic state test and UI assertion |
| Environment dependency is present | Preview/test fixture and missing-dependency failure test |
| Navigation route is stable | Route encode/decode and destination-resolution test |
| Scene restores useful context | Device/Simulator termination-and-restore run with named state |
| View task cancels | Async fake service records cancellation and stale-result suppression |
| AI fallback is visible | Availability/refusal/cancellation fixture and device model gate |
| Glass action is usable | Accessibility task, reduced-effects run, Dynamic Type, physical interaction |
| Durable record survives | Persistence/relaunch/sync test, separate from SceneStorage |

## Sources

- [Observation](https://developer.apple.com/documentation/observation)
- [Observable](https://developer.apple.com/documentation/observation/observable)
- [Model data](https://developer.apple.com/documentation/swiftui/model-data)
- [Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [Migrating from the Observable Object protocol to the Observable macro](https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro)
- [State](https://developer.apple.com/documentation/swiftui/state)
- [Bindable](https://developer.apple.com/documentation/swiftui/bindable)
- [Environment](https://developer.apple.com/documentation/swiftui/environment)
- [Environment values](https://developer.apple.com/documentation/swiftui/environment-values)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
- [Scene](https://developer.apple.com/documentation/swiftui/scene)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage)
- [Restoring your app’s state with SwiftUI](https://developer.apple.com/documentation/swiftui/restoring-your-app-s-state-with-swiftui)
- [task(name:priority:file:line:_:)](https://developer.apple.com/documentation/swiftui/view/task%28name%3Apriority%3Afile%3Aline%3A_%3A%29)
- [task(id:name:priority:file:line:_:)](https://developer.apple.com/documentation/swiftui/view/task%28id%3Aname%3Apriority%3Afile%3Aline%3A_%3A%29)
- [Task](https://developer.apple.com/documentation/swift/task)
- [Task cancellation](https://developer.apple.com/documentation/swift/task/cancel%28%29)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Preview(_:body:)](https://developer.apple.com/documentation/swiftui/preview%28_%3Abody%3A%29)
- [Previewing your app’s interface in Xcode](https://developer.apple.com/documentation/xcode/previewing-your-apps-interface-in-xcode)
- [Liquid Glass technology overview](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)

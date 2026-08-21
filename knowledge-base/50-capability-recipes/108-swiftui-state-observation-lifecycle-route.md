# SwiftUI state, Observation, and lifecycle route

## Route contract

Use this route to turn an app idea into a SwiftUI hierarchy with explicit
state ownership, modern Observation, typed dependencies, restorable
navigation, lifecycle-aware tasks, preview fixtures, Liquid Glass states, and
on-device AI fallbacks.

Apply it to a named app target. The route does not claim that previews,
simulator runs, or a model adapter prove physical-device behavior or release
readiness.

Related pages:

- [SwiftUI Observation, state, and app lifecycle](../42-framework-deep-dives/77-swiftui-observation-state-and-app-lifecycle.md)
- [State ownership and native lifecycle design](../21-design-deep-dives/105-state-ownership-and-native-lifecycle-design.md)
- [SwiftUI state, Observation, and lifecycle proof matrix](../60-verification/102-swiftui-state-observation-lifecycle-proof-matrix.md)
- [SwiftUI state, Observation, and lifecycle recipes](../70-code-recipes/120-swiftui-state-observation-lifecycle-recipes.md)

## Route map

    app outcome
      -> state chart
      -> domain/model authority
      -> observable ownership
      -> environment and bindings
      -> navigation/restoration
      -> lifecycle tasks and cancellation
      -> preview/test fixtures
      -> Liquid Glass and AI state design
      -> device/system/release proof

## Phase 0: write the state chart

List every visible state before building the screen:

| State family | Required cases |
| --- | --- |
| Data | empty, loading, loaded, stale, failed |
| Edit | clean, dirty, validating, saved, conflict |
| Async | idle, running, canceled, timed out, completed |
| AI | unavailable, generating, proposal, refusal, error, accepted |
| Permission | unknown, granted, limited, denied, restricted |
| Presentation | root, sheet, alert, navigation route, system handoff |
| Appearance | light/dark, contrast, Dynamic Type, reduced effects |

A state chart is a design and test artifact. If two states need different
copy, actions, permissions, or proof, give them distinct names.

## Phase 1: classify ownership

For each value, record owner, lifetime, read/write policy, and persistence:

| Value | Owner | Read/write | Persistence |
| --- | --- | --- | --- |
| Toggle or selected row | Local State | Local read/write | None or preference |
| Feature model | App/Scene/View State with Observable | Model reads, explicit writes | Domain store if needed |
| Editor field | Parent model plus Binding/Bindable | Child edits | Draft/domain policy |
| Shared client | Environment | Read/use through interface | External service policy |
| Navigation route | Scene/app navigation state | Route values only | Scene/activity policy |
| Generated proposal | Feature model | Review-only until accepted | Provenance if saved |
| Durable record | Persistence/service authority | Transactional methods | Store/sync policy |

Stop if a view is creating a new model for every render, if a Binding is being
used as an authority, or if SceneStorage is holding a durable record.

## Phase 2: choose the Observation route

For an iOS 26 minimum target:

1. mark reference models with the Observable macro;
2. create the source-of-truth instance in State at its owner;
3. pass it explicitly for shallow composition or place it in Environment for a
   shared subtree;
4. use Bindable only when a child control needs projected bindings;
5. keep existing ObservableObject/StateObject code behind a deliberate
   compatibility migration plan when older deployment targets require it.

Do not apply the Observable protocol without the macro-generated behavior.
Verify which properties each view reads so invalidation stays understandable.

## Phase 3: build the hierarchy

Use this composition:

    App/Scene owner
      -> feature model and service dependencies
      -> NavigationStack path
      -> feature root
      -> state-driven child surfaces
      -> semantic controls

Keep a view’s initializer honest:

- required domain data is explicit;
- optional services are optional for a reason;
- environment dependencies are listed in documentation or a feature
  contract;
- preview fixtures can satisfy the same dependency graph;
- a system-owned surface is invoked through its documented route.

## Phase 4: implement navigation as routes

Define lightweight Hashable route values. For each route:

1. define the minimum stable identity;
2. map the route to a destination;
3. resolve the current model at the destination;
4. handle deleted, stale, unauthorized, or unavailable records;
5. decide whether the route is restorable;
6. test deep-link and back-navigation behavior.

Use NavigationPath only when heterogeneous route values are useful. Do not
put a whole model, unsaved secret, large media object, or session token in the
path.

## Phase 5: bind edits safely

If a child only reads, pass a value or model reference. If it edits an
observable property through a standard control, use Bindable. If the edit must
validate, debounce, authorize, or commit transactionally, expose a model
operation instead of a raw Binding.

Write the commit boundary explicitly:

    control edit -> draft state
      -> validation
      -> user confirmation if needed
      -> domain operation
      -> persistence/sync
      -> visible saved or failed state

The UI can optimistically show a draft, but it should not label the draft as
durable truth before the domain operation succeeds.

## Phase 6: attach lifecycle tasks

Choose the task owner:

| Work | SwiftUI route |
| --- | --- |
| Load visible content for one identity | View.task with that identity as ID |
| Observe a visible AsyncSequence | View.task and cooperative cancellation |
| Sync that must outlive the view | Model/actor/service-owned Task |
| Scene refresh | ScenePhase-driven bounded reconciliation |
| Long background job | BackgroundTasks/continued-processing route |
| Model prewarm | Feature-owned task with availability and cancellation |

When an ID changes, cancel old work and start new work. When a view disappears,
do not assume a canceled task has already stopped; the operation must check
cancellation. Reject stale results by comparing the request identity or
revision before committing.

## Phase 7: restore the scene

Select state storage:

- State for transient local state;
- SceneStorage for small per-scene values that should be restored;
- NSUserActivity for current user activity and handoff/deep-link continuity;
- durable persistence for actual records and drafts;
- protected storage for sensitive data.

Document the missing-record and changed-authorization behavior. Restoration
should lead to a useful screen, not a crash or an unverified privileged action.

## Phase 8: build preview fixtures

Create fixtures for every major state. Supply the required model/environment
dependencies in the preview:

    empty
    loading
    loaded
    error
    denied/unavailable
    proposal-review
    applying
    stale/conflict
    long-content/accessibility

Parameterized previews can exercise a collection of fixture inputs. Keep
fixtures deterministic and independent of live network, user accounts, system
permissions, and random clocks.

## Phase 9: add Liquid Glass and AI

Apply Liquid Glass after the state chart is stable:

1. choose a functional container or action group;
2. keep standard semantic controls;
3. expose state, progress, and fallback without the effect;
4. test light/dark, contrast, Dynamic Type, reduced transparency/motion, and
   VoiceOver;
5. preserve the manual route.

For on-device AI:

1. gate API/model availability;
2. capture source and version metadata;
3. run the model in a cancellable task;
4. validate typed output;
5. show source/provenance and uncertainty;
6. require review before a side effect;
7. commit through the domain authority;
8. retain a useful no-model/refusal/error fallback.

## Phase 10: verify the claim

Run evidence in order:

| Gate | Evidence |
| --- | --- |
| Compile | Named target/SDK and clean build |
| State | Unit tests for transitions and ownership invariants |
| UI | UI tests for semantic controls and route results |
| Preview | Fixture coverage across appearance/size/status |
| Lifecycle | Async fake confirms cancellation, restart, and stale suppression |
| Restoration | Simulator/device termination and scene restore |
| AI | Availability/error/refusal/cancellation/evaluation fixtures |
| Glass | Accessibility and physical interaction with effects/settings |
| Release | Signed Release/TestFlight artifact with target/resource inspection |

## Stop conditions

Stop and redesign when:

- a view is the only place that knows domain truth;
- an observable model is recreated because the view body reruns;
- a required environment dependency can be missing at runtime;
- a navigation path contains a full model or secret;
- a view task mutates state after its request became stale;
- SceneStorage contains sensitive or large model data;
- a preview relies on live production services;
- an AI proposal can trigger a side effect without review/validation;
- Liquid Glass is the only way a user can understand state;
- a preview or simulator result is being called physical-device proof.

## Sources

- [Model data](https://developer.apple.com/documentation/swiftui/model-data)
- [Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [Observation](https://developer.apple.com/documentation/observation)
- [State](https://developer.apple.com/documentation/swiftui/state)
- [Bindable](https://developer.apple.com/documentation/swiftui/bindable)
- [Environment](https://developer.apple.com/documentation/swiftui/environment)
- [Environment values](https://developer.apple.com/documentation/swiftui/environment-values)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
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

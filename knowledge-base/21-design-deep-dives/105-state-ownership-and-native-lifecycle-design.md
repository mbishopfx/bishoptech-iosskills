# State ownership and native lifecycle design

## Design principle

Apple-native design is not only the shape of a card or the use of Liquid
Glass. It is the visible result of a correct ownership model:

    state owner -> observable dependency -> view composition
      -> lifecycle task -> cancellation/fallback
      -> durable commit -> system projection

If ownership is unclear, the interface tends to show stale data, duplicate
loads, lost navigation, fake progress, or a glass action that has no reliable
side effect.

Use this page with:

- [SwiftUI Observation, state, and app lifecycle](../42-framework-deep-dives/77-swiftui-observation-state-and-app-lifecycle.md)
- [SwiftUI state, Observation, and lifecycle route](../50-capability-recipes/108-swiftui-state-observation-lifecycle-route.md)
- [SwiftUI state, Observation, and lifecycle proof matrix](../60-verification/102-swiftui-state-observation-lifecycle-proof-matrix.md)
- [SwiftUI state, Observation, and lifecycle recipes](../70-code-recipes/120-swiftui-state-observation-lifecycle-recipes.md)
- [Adaptive, state-driven Apple-native design](12-adaptive-state-driven-native-design.md)

## Design the state chart first

For every nontrivial screen, write the state chart before choosing effects:

| State | User-facing meaning | Required action |
| --- | --- | --- |
| Empty | Nothing has been created or selected | Create/import/manual path |
| Loading | A bounded operation is in flight | Progress, cancel or wait policy |
| Ready | The source is available and current | Primary task |
| Editing | The user is changing a draft | Save/cancel/validation |
| Proposal | AI or a service produced a candidate | Review/edit/accept/reject |
| Applying | An explicit side effect is running | Disable duplicates and show scope |
| Saved | Domain truth accepted the change | Show result and revision/undo if available |
| Stale | Source changed or authorization expired | Refresh/resolve/manual path |
| Failed | The operation could not complete | Explain, retry, preserve source |
| Unavailable | Device, OS, permission, model, or service cannot support it | Manual fallback and reason |

Do not use a single isLoading Boolean for a workflow with distinct phases.
Do not use a generated string as a substitute for a proposal state. State names
should help the design, tests, accessibility labels, and telemetry agree.

## Choose the owner by lifetime

| Design question | Owner |
| --- | --- |
| Does this value only affect a local control? | View State |
| Do multiple descendants edit one value? | The least common ancestor plus Binding |
| Does a model need observation across views? | Observable model in State, Scene, or App |
| Does a subtree need a service/configuration? | Environment dependency |
| Does the value need per-window continuity? | SceneStorage or scene-scoped model |
| Does it survive relaunch and represent domain truth? | Durable persistence |
| Must work continue after the view disappears? | Explicit model/actor/service task |
| Is it derived from a current source? | Computed value or cancellable projection |

The view hierarchy is a presentation owner, not necessarily the authority for
records, entitlements, server state, health data, or AI output. Keep durable
domain operations behind a model/service boundary.

## Native hierarchy and ownership

Build the hierarchy so ownership is easy to find:

    App
      -> Scene / WindowGroup
        -> App-level observable state
          -> Navigation state
            -> Feature screen
              -> local control state
              -> child bindings
              -> view-scoped tasks

Use explicit initialization when a feature is small and local. Use Environment
when the model or service is genuinely shared across a deep subtree. Avoid
injecting every object globally; hidden dependencies make previews and tests
less honest.

## Navigation and restoration design

Navigation routes should be lightweight values:

    Route.inbox
    Route.detail(recordID)
    Route.review(proposalID)
    Route.settings

The route identifies the destination; the destination resolves the current
model. This allows a saved route to survive a model refresh or a deleted
record with a meaningful unavailable state.

Design the restoration contract:

- which route can be restored;
- which identifiers are stable;
- what happens if the record is missing;
- what happens if authorization changed;
- whether a draft is restored or discarded;
- whether multiple scenes have independent paths;
- how deep links merge with an existing path.

Avoid saving a full model, raw media, access token, or unsaved sensitive
content in a navigation path. Store only the minimal typed route and resolve
it through the current domain authority.

## Lifecycle-aware screens

A screen can appear, disappear, become inactive, move to background, or be
recreated while a task is running. Design the user-visible behavior:

| Lifecycle event | Design response |
| --- | --- |
| First appearance | Load the minimum visible state |
| Identity changes | Cancel work for the old identity and start the new one |
| Inactive | Pause nonessential animation/input and preserve draft state |
| Background | Flush bounded changes, cancel/hand off work, and expect termination |
| Return active | Reconcile freshness, permissions, account, and service state |
| Scene restoration | Resolve saved route/selection against current data |
| View disappears | Cancel view-scoped work and keep or discard results intentionally |

Use task for work whose lifetime matches the view. Use an explicit model-owned
operation when the work must outlive that view. In either case, check
cancellation and reject stale results.

## Functional glass states

Liquid Glass should frame a current action, not hide a missing state model:

| State | Surface treatment |
| --- | --- |
| Ready | One clear primary control with supporting context |
| Loading | Progress and a cancellation path; do not pretend the commit happened |
| Proposal | Material container around source, output, provenance, and review actions |
| Applying | A stable action surface with duplicate-submit protection |
| Saved | Compact confirmation and path to the committed record |
| Error/stale | A visible explanation and manual recovery action |
| Unavailable | A non-glass or subdued fallback when the feature cannot run |

Use standard controls first. A custom glass button must preserve semantic
labels, hit regions, focus, contrast, Dynamic Type, reduced transparency, and
reduced motion behavior. The visual state cannot be the only state signal.

## AI-native state design

An AI-powered screen should distinguish:

    source content
      -> availability and permission
      -> model input
      -> generated observation/proposal
      -> typed validation
      -> human review
      -> domain commit

Never label a model observation as a fact before validation. Never let a
model-generated route bypass an authorization or confirmation boundary.

Show the context needed to review:

- source and date;
- model/API/profile/prompt or schema version;
- confidence or uncertainty where meaningful;
- missing/unsupported inputs;
- generated versus user-authored content;
- accept/edit/reject actions;
- what will change if accepted;
- what remains manual if unavailable.

The fallback should be a real path: manual entry, local search, saved source,
or a retry with changed input. A disabled glass ornament is not a fallback.

## Preview and fixture design

Treat previews as a matrix of states, not one happy screenshot:

- empty;
- loading;
- populated;
- long text/localization;
- error;
- offline;
- permission denied;
- model unavailable/refusal;
- proposal awaiting review;
- applying;
- saved/stale/conflict;
- increased Dynamic Type;
- dark/increased contrast/reduced transparency;
- compact width and iPad split view.

Inject the model and dependencies into each preview. Avoid live network calls,
real credentials, random time, or user data. Use PreviewModifier when a
deterministic expensive fixture can be created once and shared.

The preview should render the same semantic controls as the app. If a preview
needs a special mock-only control to work, the feature boundary is likely
hidden in the wrong layer.

## Accessibility follows state

State transitions should be announced and navigable:

- loading exposes progress or a status label;
- failure includes the failed operation and recovery action;
- proposal exposes source and generated content in a review order;
- applying disables duplicate actions and communicates completion;
- unavailable explains the route without requiring color or motion;
- focus moves to the next useful control after a sheet or alert closes;
- Voice Control names actions distinctly;
- Dynamic Type keeps the state and primary action discoverable.

Use accessibility identifiers for test targeting, not as a replacement for
accessible names, values, traits, focus, or task design.

## Dependency design

Use a small dependency surface:

| Dependency | Live implementation | Preview/test implementation |
| --- | --- | --- |
| Clock | System clock | Fixed or advancing test clock |
| Data store | SwiftData/Core Data/file/service | In-memory deterministic store |
| Network | URLSession client | Fixture or controlled fake |
| Model | Foundation Models/Core ML adapter | Deterministic proposal/refusal adapter |
| Authorization | Platform manager | Explicit granted/denied/limited fixture |
| Navigation | App route state | Controlled route fixture |
| Haptics/audio | Device service | No-op or event recorder |

The Environment can carry the dependency, but the feature should still
declare what it needs and how it behaves when it is missing. A preview that
accidentally uses a real live client is not a safe preview.

## Design review questions

Before implementation, answer:

1. Who owns this value?
2. What event changes it?
3. What persists it, if anything?
4. What happens when the view disappears?
5. What happens when the scene backgrounds?
6. What cancels or supersedes the task?
7. How is stale data detected?
8. What does the person see when the model is unavailable?
9. Which action is reversible?
10. What is the accessible name, focus order, and non-motion signal?
11. Which preview fixture represents the hardest state?
12. Which physical device, system surface, or release gate remains unproven?

## Sources

- [Model data](https://developer.apple.com/documentation/swiftui/model-data)
- [Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [Observation](https://developer.apple.com/documentation/observation)
- [Migrating from the Observable Object protocol to the Observable macro](https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
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

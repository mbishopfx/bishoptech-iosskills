# Interactive App Intent snippets

## Capability

Interactive snippets are a system-facing SwiftUI result for an App Intent. They let a person see a compact result and perform a small follow-up action without leaving the current system context. The route is useful for actions exposed through Shortcuts, Spotlight, Siri, Apple Intelligence, the Action button, and other supported system experiences.

The outer container belongs to the system. The app supplies a snippet intent and a SwiftUI view whose content is rebuilt by the system. This is not an arbitrary floating window, miniature app scene, or license to recreate a system surface with custom Liquid Glass.

## Route

    user invokes discoverable AppIntent
      -> parameters resolve and authorization is checked
      -> AppIntent.perform() completes a bounded observation or mutation
      -> result returns a static view or a ShowsSnippetIntent result
      -> system performs SnippetIntent.perform()
      -> compact SwiftUI view appears
      -> Button or Toggle invokes a separate AppIntent
      -> domain state is persisted
      -> system performs SnippetIntent.perform() again
      -> snippet re-reads current state and renders the new truth

Keep the domain operation and snippet rendering separate. The first intent answers “what happened?” or “what should be confirmed?” The snippet intent answers “what is true right now, and which small next actions are available?”

## API map

| Need | Primary API seam | Correct responsibility |
| --- | --- | --- |
| Make an app action discoverable | AppIntent | Localized metadata, parameters, authorization, domain operation, and intent result |
| Show a simple result | IntentResult with a SwiftUI view | Read-only, concise result with no interactive controls |
| Return a value and an interactive result | ReturnsValue plus ShowsSnippetIntent | Preserve a value contract while adding a snippet for supported initiators |
| Produce an interactive snippet | SnippetIntent | Rebuild a current SwiftUI view and return ShowsSnippetView |
| Put a working action in the snippet | Button or Toggle initialized with an AppIntent | Small, explicit, idempotent follow-up mutation |
| Ask before a sensitive or destructive action | requestConfirmation with a snippetIntent | Reviewable choice, cancel path, and explicit continuation boundary |
| Refresh a visible snippet after external data changes | SnippetIntent.reload() | Ask the system to refresh the current snippet representation |
| Choose the process that executes an intent | allowedExecutionTargets and IntentExecutionTargets | Make app, App Intents extension, and widget-extension dependencies explicit |

Treat the return types as contracts. A result that only returns IntentResult and ShowsSnippetView is not automatically a discoverable system action; set discoverability intentionally when the product needs the snippet intent itself to appear in system experiences. An intent that returns a value and also a snippet can preserve an existing Shortcut value contract while adding a richer result.

## Static result versus interactive snippet

### Static result

Use a static result when the person only needs to read a concise outcome:

~~~swift
import AppIntents
import SwiftUI

struct CurrentFocusIntent: AppIntent {
    static var title: LocalizedStringResource = "Show current focus"

    func perform() async throws -> some IntentResult {
        let summary = try await FocusStore.shared.currentSummary()
        return .result(
            view: FocusSummaryView(summary: summary)
        )
    }
}
~~~

The view returned here should not imply that its buttons or toggles will work. If follow-up interaction matters, use a SnippetIntent result.

### Interactive result

An existing AppIntent can add an interactive snippet while keeping a returned value:

~~~swift
struct ClosestProjectIntent: AppIntent {
    static var title: LocalizedStringResource = "Find closest project"

    func perform() async throws
        -> some ReturnsValue<ProjectEntity> & ShowsSnippetIntent
    {
        let project = try await ProjectQueries.shared.closest()
        return .result(
            value: project,
            snippetIntent: ProjectSnippetIntent(projectID: project.id)
        )
    }
}
~~~

The value is useful to Shortcuts or another caller. The snippet intent owns the follow-up SwiftUI presentation. This additive shape can avoid breaking existing custom shortcuts that rely on the previous value result, but the exact generic result signature should be checked against the selected SDK.

### Snippet intent

A SnippetIntent returns a view conforming to ShowsSnippetView:

~~~swift
struct ProjectSnippetIntent: SnippetIntent {
    static var title: LocalizedStringResource = "Project details"

    @Parameter var projectID: String
    @Dependency var store: ProjectStore

    func perform() async throws -> some IntentResult & ShowsSnippetView {
        let current = try await store.snapshot(id: projectID)
        return .result(
            view: ProjectSnippetView(project: current)
        )
    }
}
~~~

The store lookup is deliberately inside perform(). The system may create and perform the snippet intent more than once, so a cached Boolean or stale entity parameter must not be treated as current truth.

## Lifecycle and idempotency

The system can perform a SnippetIntent repeatedly during the time its snippet is visible. A person tapping a button or toggle causes the system to perform that control’s AppIntent, discard the old snippet view, and perform the SnippetIntent again. The second render must fetch the updated domain state.

Use this lifecycle contract:

1. Resolve the smallest immutable identifier or parameter set.
2. Fetch current state from a shared dependency or projection.
3. Build a short view from that state.
4. Return without mutating the domain.
5. Let a nested Button or Toggle call a separate AppIntent.
6. Persist and reconcile the action before that action returns.
7. Re-render from current state.

Do not put side effects in SnippetIntent.perform(). Rendering is not a “run once” callback. Avoid long-running work that makes the snippet feel unresponsive. Pass the minimum immutable data between intents, and fetch dynamic values from a shared dependency when possible.

The system can keep the app active in the background while a snippet is visible. That is a lifecycle fact, not permission to make the snippet a permanent process or to depend on memory for durable data. Persist anything that must survive dismissal, termination, account change, or later app launch.

## Interactive controls

Use semantic SwiftUI controls and attach App Intents to the controls:

~~~swift
struct ProjectSnippetView: View {
    let project: ProjectSnapshot

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(project.title)
                .font(.headline)

            Text(project.statusLabel)
                .font(.subheadline)

            Button(intent: ToggleProjectPinnedIntent(projectID: project.id)) {
                Label(
                    project.isPinned ? "Unpin" : "Pin",
                    systemImage: project.isPinned ? "pin.slash" : "pin"
                )
            }
        }
    }
}
~~~

The exact control initializer and availability must be compiled in the app’s selected SDK. The architectural rule is stable: the control invokes an AppIntent, not a closure that mutates a view-local binding.

The follow-up intent must:

- re-read authorization and account scope;
- validate that the identifier still exists and is editable;
- apply an idempotent mutation;
- persist or reconcile the result;
- return an honest error when the action cannot complete;
- avoid relying on a live app scene or an in-memory SwiftUI model context.

Optimistic UI may be appropriate for a widget or snippet only when the next render can correct it. If persistence fails, the next snippet must show the unchanged state and an actionable error or recovery route.

## Confirmation snippets

Use requestConfirmation when the action requires a person to review or change a choice before it continues. The snippet can contain controls for adjusting parameters, and the system provides a clear cancel and confirm boundary.

~~~swift
struct ArchiveProjectIntent: AppIntent {
    static var title: LocalizedStringResource = "Archive project"

    @Parameter var projectID: String
    @Parameter var includeAttachments: Bool

    func perform() async throws -> some IntentResult & ShowsSnippetIntent {
        let draft = ArchiveDraft(
            projectID: projectID,
            includeAttachments: includeAttachments
        )

        try await requestConfirmation(
            actionName: .continue,
            dialog: IntentDialog("Review what will be archived."),
            snippetIntent: ArchiveReviewSnippetIntent(draft: draft)
        )

        let currentProjectID = projectID
        let currentIncludeAttachments = includeAttachments
        try await ProjectActions.archive(
            projectID: currentProjectID,
            includeAttachments: currentIncludeAttachments
        )

        return .result(
            snippetIntent: ArchiveResultSnippetIntent(projectID: currentProjectID)
        )
    }
}
~~~

The confirmation call can return updated parameter values from the snippet. Retrieve the latest values from the AppIntent’s properties after the call rather than trusting a cached draft. Cancellation throws, so the mutating operation must be after the confirmation call. Catch and map cancellation only when the surrounding system experience needs a custom result; do not treat cancellation as successful mutation.

For dangerous or externally visible operations, require a reviewable projection that shows target, scope, affected count, destination, and any irreversible consequence. A model-generated recommendation is not confirmation.

## Refreshing a snippet

If a long-running search or external event changes the data behind a visible snippet, call the SnippetIntent type’s reload() method from the owning operation:

~~~swift
struct RefreshableSearchIntent: AppIntent {
    static var title: LocalizedStringResource = "Search projects"

    @Parameter var query: String

    func perform() async throws -> some IntentResult & ShowsSnippetIntent {
        let requestID = try await SearchService.shared.start(query: query) {
            ProjectSearchSnippetIntent.reload()
        }

        return .result(
            snippetIntent: ProjectSearchSnippetIntent(requestID: requestID)
        )
    }
}
~~~

Reload is a system-surface refresh request, not a replacement for durable state or a guarantee about a render deadline. The operation still needs a loading, success, timeout, no-results, permission, and failure state.

## Execution targets and shared packages

When the same intents or entities are linked from the main app, a widget extension, and an App Intents extension, the system can choose among available processes. Use allowedExecutionTargets when the dependency graph or privacy boundary requires a specific process:

~~~swift
struct UpdateProjectIntent: AppIntent {
    static var title: LocalizedStringResource = "Update project"
    static var allowedExecutionTargets: IntentExecutionTargets { .main }

    @Parameter var projectID: String

    func perform() async throws -> some IntentResult {
        try await ProjectActions.markUpdated(projectID: projectID)
        return .result()
    }
}
~~~

The API is preliminary in the current documentation. Re-check its availability and exact declaration in the final SDK. The choice is architectural:

| Target | Use when | Hidden dependency to remove |
| --- | --- | --- |
| main | The action requires app-only services, a protected database actor, or a foreground handoff | Do not assume a scene is already visible; define the handoff |
| appIntentsExtension | The action should run without launching the app and has a self-contained service boundary | Do not access UI-only state or unavailable app resources |
| widgetKitExtension | A widget/control owns the route and the action can finish within extension constraints | Do not assume a long-lived process or unrestricted network |
| combination | The action is safe in several processes and uses a shared package | Make storage, concurrency, authorization, and resource availability equivalent |

Do not place a class with UI-only dependencies, process-local singletons, or arbitrary model contexts in a shared intent package. Share small Codable and Sendable value types and a domain service boundary instead.

## Discoverability and system surfaces

AppIntent metadata is user-facing vocabulary. Localize the title, description, parameter names, summaries, dialog text, and accessibility content. Keep the action understandable without the app’s visual context.

Important distinctions:

- An AppIntent can be discoverable by system features when isDiscoverable is true.
- An interactive snippet can be reused in widgets or Live Activities when the view and action contract fits both surfaces.
- A Control Center control cannot display a snippet; give it a direct result/value or use a different surface.
- A snippet result does not guarantee invocation by Siri, Apple Intelligence, Spotlight, or any particular device.
- Apple Intelligence may discover and select app capabilities through system mediation; the app does not control ranking, model choice, language support, or context selection.
- A deep link or open-app intent is a handoff, not permission to bypass authentication, purchase, safety, or privacy gates.

## On-device AI boundary

Use an on-device model to summarize, classify, or propose a next action only when the product has a real local workflow. Keep the model outside the final side effect:

    local input -> model proposal -> typed validation -> snippet review
      -> explicit AppIntent confirmation -> domain mutation -> refreshed snippet

Good uses include proposing a project label, choosing among a short list of destinations, or summarizing the current record. The AppIntent must still validate the proposal against current domain state. Never let free-form model output become an identifier, file path, URL, payment instruction, or destructive command without typed validation and explicit authorization.

If Foundation Models or another on-device route is unavailable, return the original data with a manual choice path. The snippet should explain “model unavailable” or “needs review” rather than implying a model-generated answer is complete.

## Privacy, accessibility, and failure states

Before exposing a snippet, decide what can appear while the device is locked, in a shared system context, in a voice response, or in a searchable history. Minimize entities and parameter summaries. Redact sensitive fields and require authentication or app handoff when the action needs it.

Use semantic controls, labels, sufficient hit regions, Dynamic Type-compatible layout, and explicit state text. Verify VoiceOver reading order, Voice Control names, Switch Control reachability, Reduce Motion, reduced transparency, increased contrast, and localization. Do not rely on color, a tiny icon, or a glass effect to communicate state.

Render every meaningful state:

| State | Snippet response |
| --- | --- |
| Loading | Short progress message or stable placeholder; avoid a long blocking render |
| Current success | One primary fact and only the next useful actions |
| Empty | Explain what was searched and give a clear next action |
| Deleted or unauthorized | Do not reveal private details; offer a safe recovery or app handoff |
| Offline or stale | Show freshness and preserve a retry route |
| Model unavailable | Keep the source data and offer deterministic or manual completion |
| Mutation failed | Keep the last confirmed state and explain that nothing changed |
| Destructive confirmation | Show target, scope, consequence, and cancel |

## Implementation and evidence contract

Before calling the route ready, record:

- deployment target and SDK build;
- every AppIntent, SnippetIntent, entity, query, and follow-up action;
- target membership and allowed execution targets;
- shared store or projection and authorization boundary;
- static versus interactive result shape;
- cancellation, repeated render, reload, stale, and failure behavior;
- supported system invocation surfaces and unsupported ones;
- privacy, localization, accessibility, and locked-device decisions;
- fixture, compile, UI, signed-device, and release evidence.

The code can be syntactically plausible and still be wrong for the product. A successful local perform() call does not prove system discoverability, repeated rendering, extension execution, locked-device behavior, Apple Intelligence selection, or release readiness.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [ShowsSnippetIntent](https://developer.apple.com/documentation/appintents/showssnippetintent)
- [ShowsSnippetView](https://developer.apple.com/documentation/appintents/showssnippetview)
- [IntentResult result(value:snippetIntent:)](https://developer.apple.com/documentation/appintents/intentresult/result%28value%3Asnippetintent%3A%29)
- [IntentResult result(snippetIntent:)](https://developer.apple.com/documentation/appintents/intentresult/result%28snippetintent%3A%29)
- [SnippetIntent.reload()](https://developer.apple.com/documentation/appintents/snippetintent/reload%28%29)
- [AppIntent requestConfirmation with a snippet](https://developer.apple.com/documentation/appintents/appintent/requestconfirmation%28conditions%3Aactionname%3Adialog%3Ashowdialogasprompt%3Asnippetintent%3A%29-jxb8)
- [IntentExecutionTargets](https://developer.apple.com/documentation/appintents/intentexecutiontargets)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [AppIntent.isDiscoverable](https://developer.apple.com/documentation/appintents/appintent/isdiscoverable)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Apple Intelligence and machine learning](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)

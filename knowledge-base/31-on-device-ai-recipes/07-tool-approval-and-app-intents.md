# Tool Approval and App Intent Workflows

## Two different ways intelligence reaches app actions

Foundation Models `Tool` and App Intents can both connect language-driven experiences to app code, but they are different contracts:

| Contract | Who initiates it | What it is for | What it does not prove |
| --- | --- | --- | --- |
| Foundation Models `Tool` | A `LanguageModelSession` while an app-owned generation is running | Retrieve bounded current data or ask app code to perform a task within that generation. | Authorization, safe arguments, idempotence, or a person’s approval. |
| `AppIntent` | Siri, Shortcuts, Spotlight, Apple Intelligence, widgets, controls, Live Activities, or the app | Make an app action or entity discoverable and executable through a supported system surface. | That the system will always discover, resolve, or complete it. |

Use the same domain use case behind both routes. Do not put business rules in the model tool or duplicate them inside an intent.

## Shared action architecture

```text
SwiftUI button  ─┐
Foundation Tool ─┼─> authorized domain use case ─> state transition ─> result
AppIntent       ─┘
```

The use case must re-read current state and authorization at the moment it executes. An earlier model response, preview, or intent parameter is only a request.

## Start with read-only tools

Query tools should return the minimum current data needed to answer the user’s question. Keep them bounded by:

- a validated query or identifier;
- a maximum result count and output size;
- ownership and authorization checks;
- a timeout and cancellation path;
- redaction of fields the model does not need;
- a clear “not found,” “stale,” or “not authorized” result.

A query tool can still leak private data if its search scope is too broad. App-owned filtering belongs before the tool returns data to the model.

## Mutating route: propose, approve, commit

For send, buy, delete, publish, unlock, schedule, or sensitive-record actions:

`model/system request -> parse parameters -> deterministic validation -> show proposed effect -> explicit approval -> revalidate current state -> idempotent commit -> visible result`

The approval screen should state what will happen, which record/account is affected, the important parameters, and what happens if the action fails. If the user changes a field, revalidate the edited value; do not continue with the model’s original arguments.

Use an idempotency key or a domain-level duplicate check. If the model repeats a call after a timeout, the second attempt must not send, charge, delete, or publish twice.

## Tool-calling controls

Foundation Models supports tool-calling modes such as allowed, required, and disallowed. Treat `required` as a contract that needs an exit condition; otherwise the session can continue calling tools instead of producing a final response. When a tool throws, map the failure to a safe user-visible state and preserve the current draft.

Keep tool definitions small. Tool names, descriptions, schemas, arguments, outputs, and retrieved content consume context and can influence model behavior. Retrieved text is untrusted data, not new instructions or authorization.

## App Intent contract

An App Intent should have:

- a concise, localized title and description;
- parameters that express the smallest useful action;
- stable `AppEntity` identifiers when the action targets app data;
- an `EntityQuery` path for resolving identifiers and supported search;
- deterministic authorization and current-state checks;
- a result/dialog that accurately describes what happened;
- a deep link or destination when the person needs to inspect or edit;
- a fallback when the app, store, account, or protected data is unavailable.

An `AppEntity` is a system-facing representation, not necessarily the full persistence model. Use a smaller intent model when the underlying record contains private fields or unstable implementation details. Keep identifiers stable across launches and migrations.

## Conceptual route sketch

The exact protocol composition and result types are SDK-sensitive; compile the current API in the target project:

```swift
struct SaveReviewedDraftIntent: AppIntent {
    static var title: LocalizedStringResource = "Save Reviewed Draft"

    @Parameter(title: "Draft")
    var draft: DraftEntity

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let request = SaveDraftRequest(draftID: draft.id)
        let result = try await DraftUseCase().saveAfterAuthorization(request)

        return .result(dialog: "Saved (result.displayName).")
    }
}
```

The intent must not trust an old entity snapshot or treat the dialog as proof that persistence succeeded. The use case should return a committed result or a typed failure, and the system surface should expose a recoverable error.

## Process and extension boundaries

Widgets, controls, Live Activities, and other system surfaces can execute outside the main app process. Assume in-memory state is absent. Resolve shared state from the supported store, handle protected-data/account unavailability, and keep operations fast enough for the surface’s lifecycle. Deep-link to the app for a review or long-running workflow instead of hiding a form inside a tiny system surface.

## Verification checklist

- Unit-test query filtering, entity lookup, parameter validation, authorization, ownership, idempotency, and domain state transitions.
- Test the Foundation Models tool with missing, malformed, stale, oversized, adversarial, unauthorized, and repeated arguments.
- Test allowed/required/disallowed tool modes and the required-mode exit condition.
- Test App Intent invocation from the actual Shortcuts, Siri, Spotlight, widget, control, Live Activity, or other named surface.
- Test a user rejection, cancellation, timeout, process termination, store/account failure, and deep link.
- Run VoiceOver, Dynamic Type, reduced motion/transparency, and localization checks on the review/confirmation UI.
- Record device/OS/build, entitlements, privacy/usage descriptions, system-surface result, and physical-device evidence separately from a compile result.

## Sources

- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Widgets, Live Activities, and controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

# Interactive App Intent snippet route

## Outcome

Expose a focused action to Apple system experiences, show the current result in a compact SwiftUI snippet, let the person perform one safe follow-up action, and re-render the snippet from durable domain truth.

Example outcomes:

- find the next item and mark it complete;
- show the current project and pin or unpin it;
- propose a local AI label and let the person accept or reject it;
- show a pending export and open the app only when review is needed;
- review a destructive operation before the mutation runs.

This route is for small system-facing workflows. It is not a replacement for an app screen, a general-purpose assistant, or a guarantee that every system experience will invoke the intent.

## Route shape

    app-owned domain state
      -> AppIntent metadata and parameters
      -> authorization and current-state validation
      -> static result or ShowsSnippetIntent result
      -> SnippetIntent performs and returns SwiftUI content
      -> Button or Toggle AppIntent
      -> durable mutation/reconciliation
      -> SnippetIntent performs again
      -> current state or precise app handoff

For an AI-assisted route:

    source -> on-device proposal -> typed validation -> snippet review
      -> explicit confirmation -> domain truth -> system projection

## Target register

| Target or module | Owns | Configuration questions |
| --- | --- | --- |
| Main app | Domain model, protected services, full review/edit screen, app handoff | Does this operation require a scene, authentication, or app-only framework? |
| App Intents extension | Headless intent execution when supported | Can the action run without UI, a live scene, or an app-only resource? |
| Widget/control extension | System-surface projection and selected interactions | Can the action finish within extension constraints and current data boundary? |
| Shared Swift package/framework | Sendable value types, intent declarations, queries, domain use-case protocols | Are all linked targets able to build the same dependencies and resources? |
| Shared store/projection | Minimal identifiers, display values, freshness, pending/error state | Does it exclude credentials, raw model context, and private data not needed by the surface? |

When an intent is linked from multiple targets, choose allowedExecutionTargets deliberately. The default process choice is not a substitute for designing a process-safe dependency graph.

## Preflight decisions

Write these decisions before coding:

- What is the single user verb?
- Which system experiences are actually useful for this verb?
- Is the first result static or interactive?
- Which values are immutable identifiers and which must be re-fetched?
- Which follow-up actions are safe without opening the app?
- What requires confirmation?
- What happens if the record is deleted, unauthorized, stale, or belongs to another account?
- Which process must execute the intent?
- Which app target, widget extension, or App Intents extension contains the declaration?
- What is the full-app fallback?
- What does an unavailable Foundation Models or AI route show?
- What can safely be spoken or shown while locked?

## Domain contract

Use a small domain operation rather than reaching into a SwiftUI view:

~~~text
Intent parameter
  -> resolve stable identifier
  -> load current account-scoped record
  -> authorize operation
  -> validate current version/state
  -> apply idempotent command
  -> persist/reconcile
  -> return result or typed failure
~~~

Keep the snippet’s view model separate:

~~~text
domain truth -> privacy-safe SnippetSnapshot -> SwiftUI view
                                   -> semantic action labels
                                   -> freshness/error/recovery
~~~

The snapshot is disposable presentation data. It must never become a second source of truth.

## Build sequence

### 1. Define the user-facing intent

Create an AppIntent with a localized title, description, parameters, and parameter summary. Keep the metadata understandable without the app’s screen. If it should be discoverable by Siri, Spotlight, Shortcuts, or Apple Intelligence, verify discoverability and add the appropriate App Shortcut or entity route.

### 2. Resolve and authorize

Use an AppEntity/EntityQuery or a stable identifier. Filter by account and permission. Re-check authorization inside perform(); system-provided parameters are input, not proof that the current user can still mutate the record.

### 3. Choose the first result

Use a static SwiftUI result when the person only needs to read. Use a ShowsSnippetIntent result when the snippet needs a working follow-up control. If the old intent already returns a useful value, preserve the value and add the snippet where the result type allows it.

### 4. Implement the SnippetIntent as a read

In SnippetIntent.perform():

1. load current state using a dependency;
2. map it to the minimum privacy-safe snapshot;
3. build a compact SwiftUI view;
4. attach App Intents to only the meaningful buttons and toggles;
5. return ShowsSnippetView without mutating the domain.

### 5. Implement each follow-up AppIntent

Each action revalidates the identifier, authorization, version/state, and account. Apply the mutation idempotently. Persist before returning. The system will perform the snippet intent again; the second render must show the resulting state.

### 6. Add confirmation where the consequence needs it

Use requestConfirmation with a SnippetIntent for destructive, sensitive, or externally visible changes. Put the actual mutation after the confirmation call. Read updated parameters after the call because the snippet may have changed them. Treat cancellation as a non-success path.

### 7. Handle long-running work

Return a loading/result snippet and call SnippetIntent.reload() when new data is ready. Define timeout, no-result, offline, permission, and model-unavailable states. Reload is not a persistence strategy or a delivery guarantee.

### 8. Add the full-app route

Open the app only for work that needs room, authentication, private context, or complex review. Route to the exact destination and persist the pending operation so interruption does not create a false success.

## State machine

| State | Entry condition | Snippet | Allowed action |
| --- | --- | --- | --- |
| unresolved | Parameters missing or ambiguous | Ask for the smallest missing value | Resolve or open app |
| loading | Query or model is running | Short progress state | Cancel or retry when supported |
| current | Domain snapshot is authorized and fresh enough | Primary fact and related action | Safe follow-up |
| needs-review | Proposal or sensitive action awaits approval | Scope, source, consequence, choice | Confirm, edit, reject |
| pending | Mutation accepted but not reconciled | Honest pending state | Prevent duplicate mutation |
| complete | Durable mutation committed | Updated result and next action | Continue or dismiss |
| stale | Snapshot older than product threshold | Show freshness and retry | Refresh or open app |
| unauthorized | Permission/account changed | Minimal nonrevealing state | Authenticate or Settings |
| unavailable | Device, service, model, or target cannot run | Explain reason | Manual fallback |
| failed | Operation did not commit | Preserve prior confirmed state | Retry or open app |

## AI-assisted snippet route

Keep the model at the proposal layer:

1. capture or load the user-owned source;
2. run an availability-checked on-device model;
3. constrain output to a typed structure;
4. attach source IDs, model/framework, and provisional status;
5. show the proposal in the snippet;
6. let the person confirm or reject with an AppIntent;
7. validate again against current domain state;
8. persist the approved value;
9. re-render from the approved record.

Never use a model result as authorization. Never expose raw private context in intent metadata. If the model is unavailable, present the original source and a deterministic/manual path.

## Privacy and system-surface policy

Record the surface-specific privacy decision:

| Surface context | Default decision |
| --- | --- |
| App-owned screen | Full detail allowed after normal authorization |
| Siri or voice | Speak only the minimum necessary; avoid private text by default |
| Spotlight or system discovery | Index only fields the person expects to search |
| Widget or snippet | Use a redacted projection and freshness |
| Lock Screen or control context | Require handoff for private detail or sensitive mutation |
| Signed-out or account-changed | Invalidate the projection and reveal no old account content |

Do not assume that a successful in-app invocation has the same privacy context as a system invocation.

## Failure and fallback matrix

| Failure | Keep | Do not claim |
| --- | --- | --- |
| Model unavailable | Source data and manual controls | AI-generated result |
| App target unavailable | Safe headless action or explicit handoff | That every process can run the intent |
| Record deleted | Stable failure and recovery | A successful mutation |
| Permission revoked | Minimal message and Settings/app route | Private record details |
| Network unavailable | Local state and retry/pending marker | Remote completion |
| Duplicate action | Idempotent command and current state | Two successful writes |
| Snippet re-rendered | Fresh snapshot | That perform() runs once |
| Confirmation canceled | Original state | A completed side effect |
| Stale projection | Freshness and retry | Current truth |
| Control Center invocation | Direct control result/value | Interactive snippet presentation |

## Proof package

Attach evidence in this order:

1. source and API availability record;
2. compile fixture in the named target;
3. deterministic intent and domain tests;
4. snippet render and repeated-render UI tests;
5. signed device system-surface invocation;
6. accessibility, localization, and privacy run;
7. release artifact target and entitlement inspection;
8. TestFlight or production verification when the route is part of the shipped product.

Use the [interactive snippet proof matrix](../60-verification/19-interactive-snippet-and-intent-proof-matrix.md) and [compile-oriented recipes](../70-code-recipes/37-interactive-app-intent-snippet-recipes.md) as the implementation checklist.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [ShowsSnippetIntent](https://developer.apple.com/documentation/appintents/showssnippetintent)
- [ShowsSnippetView](https://developer.apple.com/documentation/appintents/showssnippetview)
- [IntentExecutionTargets](https://developer.apple.com/documentation/appintents/intentexecutiontargets)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [AppIntent requestConfirmation with a snippet](https://developer.apple.com/documentation/appintents/appintent/requestconfirmation%28conditions%3Aactionname%3Adialog%3Ashowdialogasprompt%3Asnippetintent%3A%29-jxb8)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

# Testable native design and AI evaluation

## Design objective

An Apple-native screen should be designed so its important behavior can be
observed without turning the product into a testing artifact. The view can stay
quiet and system-like while the state, semantic actions, accessibility
structure, and AI proposal boundaries remain explicit enough to verify.

The design graph is:

    user intent
      -> domain state and revision
      -> semantic SwiftUI composition
      -> system-owned projection when appropriate
      -> task evidence

The useful unit of review is a user task, not a screenshot. A screen is ready
when its content hierarchy, actions, state transitions, adaptive behavior,
accessibility task, AI review, and performance boundaries can all be named.

## Put test seams at responsibility boundaries

Separate the app into values and actors that can be replaced in tests:

| Boundary | Production responsibility | Test seam |
| --- | --- | --- |
| Domain reducer | Accepts an intent and current revision, returns a state transition | Pure input/output fixture |
| Repository | Loads and commits records | In-memory or file-backed test repository |
| Clock | Controls deadlines, debounce, retries, and schedules | Test clock or manually advanced clock |
| Network/model adapter | Performs external work | Fake result, failure, cancellation, and delay |
| System surface adapter | Projects state to widget, notification, App Intent, Handoff, or extension | Recorded projection and target-specific integration |
| SwiftUI view | Renders state and emits semantic actions | Fixture state, preview, UI test |
| Accessibility layer | Exposes label, role, value, action, and focus order | VoiceOver task script plus XCUI attributes |

The view should not reach directly into a singleton network client, global
database, or model session. Direct reach-through makes a preview look easy while
making cancellation, failure, and deterministic UI tests difficult.

## State is the native design system

Define the screen’s states before selecting a glass treatment:

| State | Content contract | Action contract | Test question |
| --- | --- | --- | --- |
| Empty | Explain what is missing and what starts the workflow | One primary next action | Can a new person discover the first action? |
| Loading | Preserve context without promising freshness | Cancel/retry only when meaningful | Does cancellation stop work and restore a stable state? |
| Partial | Show what is known and what is pending | Repair or continue | Can the person tell partial truth from completed truth? |
| Ready | Display domain data with units/provenance | Functional actions with explicit scope | Does the view render the right revision? |
| Stale/offline | Identify age and unavailable operations | Retry, refresh, or work locally | Is stale content clearly distinct from new content? |
| AI proposal | Show generated content as a proposal | Edit, reject, accept, or inspect source | Can the person review before commit? |
| Committing | Show the operation being applied | Prevent duplicate commit or allow cancel safely | Is the commit idempotent? |
| Error | State the recoverable cause and next step | Retry, sign in, grant access, or edit | Is the error actionable without exposing secrets? |

This matrix powers Swift Testing fixtures, preview data, UI launch arguments,
accessibility scripts, and AI evaluation scenarios. It also prevents a custom
glass component from becoming the hidden owner of application truth.

## Functional Liquid Glass is a testable interaction layer

Use system controls and documented Liquid Glass composition APIs for app-owned
functional actions. Keep labels, selection state, focus, hit targets, and
confirmation behavior independent from the visual effect.

For each glass control, specify:

- the semantic role and accessible label;
- the state that enables or disables it;
- the domain intent it emits;
- the revision or authorization it requires;
- the reduced-effects appearance;
- the result state after success, cancellation, or failure;
- the physical-device interaction and performance check.

Test the same action in a normal appearance, increased-contrast/reduced-effects
configuration, large Dynamic Type, VoiceOver, and when the underlying content is
long, empty, or stale. A surface that looks elegant only with short English
labels is not a native design system.

Do not style a system-owned widget, notification, Handoff suggestion, or App
Intent result as if it were an app-owned glass panel. Test the handoff and host
surface through its actual target.

## Semantic identifiers are not visible branding

Give important controls stable identifiers that describe their product role,
not their layout. A primary action can use a stable identifier such as
review-accept or note-save while its visible label changes with localization.

Use accessibility labels for what the person needs to understand, and hints only
when the action is not already obvious. Avoid concatenating state into a label
that changes unpredictably when a value updates; expose value and state through
the appropriate accessibility properties instead.

Keep test identifiers stable across a visual refresh. The design can change from
a toolbar button to a bottom action group without forcing a new test contract if
the user intent and semantic role remain the same.

## Accessibility is a task design constraint

Write the task in normal language:

    Start a new review, correct the generated title, save it, and find the saved item.

Then record:

1. what the first focusable element should be;
2. which labels and roles must be announced;
3. what feedback confirms a transition;
4. where focus moves after a sheet, alert, or navigation change;
5. whether the task works with Dynamic Type, VoiceOver, Voice Control,
   Switch Control, keyboard navigation, and reduced motion/effects;
6. what happens when authorization, network, model, or data is unavailable.

Automated XCUI attributes support the script, but an identifier on every control
does not prove that a person can complete the task. Physical-device review is
required for claims about assistive interaction, focus ergonomics, speech,
gesture timing, and reduced-effects behavior.

## Make AI output reviewable and measurable

The generated object should be a typed proposal with source and revision
metadata, not a direct command to mutate an app record:

    AI output
      -> schema decoding
      -> deterministic validation
      -> policy and authorization check
      -> review UI
      -> explicit user action
      -> domain reducer
      -> projection

Design the proposal for testing:

- stable field names and versioned schema;
- source record IDs or input references;
- model/profile and prompt version;
- optional confidence or uncertainty explanation that is not presented as truth;
- validation errors that identify the field and reason;
- explicit operations such as add, replace, delete, or no-op;
- an idempotency/revision token;
- no hidden network or system side effect in decoding.

Build an evaluation dataset from the states and users that matter: empty input,
ambiguous input, long input, malformed input, multilingual input, unsafe input,
stale source, missing authorization, model unavailable, and a representative
normal case. Score deterministic requirements first. Use semantic or model-based
judgment only for criteria that cannot be expressed reliably as rules, and
compare those judgments with human review before treating the score as useful.

## Native navigation and deep links are test inputs

Navigation state should be driven by a typed route or app intent, not by a
view’s private visual state. Feed the same route fixture from a button, a
Universal Link, an App Intent, a widget, a document open, and a notification when
those entry points converge.

Test:

- cold launch into the route;
- warm app route replacement;
- scene resume with stale authorization or data;
- invalid and unsupported route versions;
- a route that needs login, permission, or a missing record;
- multi-window or scene selection when supported;
- focus and accessibility announcement after arrival.

The app may propose a route from on-device AI, but it should validate the route
against the current account, revision, and authorization before navigation. The
model should not receive an unrestricted openURL or database mutation tool.

## Evaluation states for on-device AI

Treat model readiness, response generation, and domain commit as separate states:

| AI state | UI treatment | Evaluation |
| --- | --- | --- |
| Unavailable | Explain the local fallback or defer action | Availability and fallback fixture |
| Preparing | Show bounded progress or a quiet loading state | Cancellation and process-lifecycle test |
| Generating | Preserve source context and prevent accidental commit | Async cancellation and timeout test |
| Needs review | Show typed fields, sources, and changes | Schema/policy/UX task test |
| Rejected | Keep original record and reason | No-mutation invariant |
| Accepted | Commit through normal domain flow | Revision/idempotency test |
| Failed | Preserve input and offer recoverable action | Error and retry fixture |

Do not call the generated text “correct” because it passed a string comparison.
The evaluation record should say which criterion passed, which validator ran,
which model/profile and prompt version were used, and whether a person reviewed
the result.

## Performance budgets belong in design decisions

Choose budgets for launch, first useful content, scroll, capture-to-review,
generation-to-review, and commit-to-projection. State the workload and device
class that the budget applies to.

For a glass-heavy screen, inspect:

- layout and rendering under large data;
- image/material memory;
- scroll hitch behavior;
- animation and transition work;
- accessibility overlays and Dynamic Type;
- model/capture work competing with UI responsiveness;
- thermal and low-power degradation.

Use a performance test for a repeatable regression and Instruments/MetricKit for
diagnosis or field evidence. Do not encode an arbitrary device-specific number
as a universal promise.

## Design review packet

For each native screen, keep one packet containing:

- state table and revision/authorization assumptions;
- semantic control map;
- accessibility task script;
- UI test launch arguments and fixture seed;
- AI evaluation dataset/criteria when relevant;
- performance workload and metric selection;
- supported device/OS matrix;
- source, compile, simulator, physical-device, system-surface, and Release
  evidence links;
- known gaps and the next proof required.

## Sources

- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Xcode testing](https://developer.apple.com/documentation/xcode/testing)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)

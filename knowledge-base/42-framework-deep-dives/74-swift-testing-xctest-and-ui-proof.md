# Swift Testing, XCTest, UI automation, and performance proof

## Purpose

Testing is not one button and it is not one kind of evidence. A native app needs
different tests for deterministic domain logic, async coordination, SwiftUI state,
accessibility tasks, system services, performance regressions, on-device AI
quality, and release behavior.

Use this page as the framework map for a named app target. The companion pages
turn the map into an Apple-native design contract, a capability route, a proof
matrix, and compile-oriented recipes:

- [Testable native design and AI evaluation](../21-design-deep-dives/102-testable-native-design-and-ai-evaluation.md)
- [Swift Testing, XCTest, and UI-proof capability route](../50-capability-recipes/105-swift-testing-xctest-and-ui-proof-route.md)
- [Swift Testing, XCTest, and UI-proof matrix](../60-verification/99-swift-testing-xctest-ui-proof-matrix.md)
- [Swift Testing, XCTest, and UI-proof recipes](../70-code-recipes/117-swift-testing-xctest-ui-proof-recipes.md)

## The testing pyramid is a routing model

Apple describes a useful distribution: many fast, isolated unit tests; fewer
integration tests; and a smaller number of high-fidelity UI tests for common
user workflows. Performance tests add a separate regression signal. This is a
planning heuristic, not permission to omit a test layer that carries the actual
product risk.

| Layer | Best question | Primary tools | Strongest evidence |
| --- | --- | --- | --- |
| Domain unit | Does this pure reducer, parser, validator, or policy produce the expected result? | Swift Testing or XCTest | Deterministic fixture and repeatable test result |
| Async integration | Do actors, repositories, clocks, model adapters, and cancellation cooperate? | Swift Testing async tests, XCTest expectations where needed | Injected dependency fixture, cancellation test, serialized event trace |
| SwiftUI state | Does a state transition expose the correct semantic controls and actions? | Domain tests plus preview/fixture harness | State matrix and semantic assertions |
| UI workflow | Can a person complete a critical task through the running app? | XCTest and XCUIAutomation | UI test on a named target, with launch state and environment recorded |
| System surface | Does the widget, App Intent, Handoff, notification, extension, or provider deliver? | Target-specific tests and device/system runs | Host/system evidence; app-screen tests are not a substitute |
| Performance | Did a critical path regress in time, memory, CPU, storage, launch, signposts, or hitches? | XCTest performance metrics, Instruments, MetricKit | Baseline comparison on a recorded device/build/workload |
| AI evaluation | Does generated output satisfy the feature’s quality and safety criteria across representative cases? | Foundation Models evaluation plus deterministic checks | Dataset, criteria, versioned prompt/model context, score distribution, human review where needed |
| Release | Does the user-like signed build behave outside the Debug environment? | Archive, physical device, TestFlight/App Store build | Release artifact, install/run log, migration/account/permission evidence |

An assertion that a view exists is not proof that VoiceOver can complete a task.
An expectation that an async callback fired is not proof that the callback carried
fresh domain truth. A green performance test is not a universal frame-rate
guarantee. Keep the claim and the evidence layer together.

## Swift Testing

Swift Testing is the modern framework for tests that call Swift code directly.
The source model uses test functions and suites rather than requiring every test
to be a method on an XCTestCase subclass.

### Test functions and suites

Use the Test attribute to declare a test function and Suite when a type needs a
named container or shared suite traits. Use expect for a normal expected outcome
and require when the rest of the test cannot proceed safely without the
precondition. Give tests names that describe the behavior, not the implementation
detail.

An async or throwing test is still an ordinary Swift function. Mark it async when
it awaits an async dependency and throws when the test setup or operation can
throw. Use MainActor only when the test or fixture genuinely requires main-actor
isolation, such as a UI-facing observable or a main-actor store. MainActor on a
test does not make a non-thread-safe production dependency safe.

Availability belongs on the test when the behavior is unavailable on older
targets. A test that cannot run because of OS or language availability should be
reported as unavailable/skipped rather than silently treated as a passing
feature test.

### Traits are execution and organization contracts

Tags categorize tests for test-plan selection and reporting. They do not, by
themselves, change the behavior of a test. Use names that communicate the
evidence class, such as unit, integration, ui, accessibility, device, network,
aiEvaluation, or releaseCandidate. For tags that cross package or project
boundaries, use a namespaced convention so unrelated modules do not accidentally
share a semantic label.

Traits can also express conditions, time limits, known bugs, comments, and
parallelization policy. Apply serialized only when shared state or an external
resource truly requires it. Serializing an entire suite can hide data races and
turn a fast feedback loop into a slow one. Prefer isolated fixtures and actor
ownership first.

### Parameterized tests

Parameterized tests turn a collection of inputs into distinct test cases. Use
them for state matrices, locale/size-class cases, parser inputs, authorization
states, error mappings, and AI evaluation fixtures. Each case should retain
enough identity to diagnose a failure.

Swift Testing normally runs parameterized cases in parallel. That is valuable
when fixtures are isolated and dangerous when cases share a database, file, key,
singleton, or mutable clock. Use serialized for the narrow boundary that needs
it, or make the fixture actor-owned and independent.

If selected-case reruns matter, use arguments that can be identified and encoded
by the testing library’s supported protocols. A test that cannot be selected
precisely is harder to debug when a large matrix has one failing case.

### Asynchronous events and confirmations

For a value returned by an async function, await the operation and assert the
value. For an event stream, notification, delegate callback, or observation that
must occur during a scoped operation, use a Confirmation with the expected count
or range. The confirmation should be created around the operation that can emit
the event, not before unrelated setup that might cause a stale event.

Test zero-event behavior explicitly when an operation must not publish after
cancellation, revocation, failed authorization, or teardown. A callback that
arrives after the test’s scope has ended is usually a lifecycle defect, not a
reason to increase a timeout.

### What Swift Testing should not own

Do not make every test construct a complete SwiftUI application or require a
physical device. Keep pure validation, reducers, route parsing, AI proposal
checking, and persistence policies in testable modules. Put UI automation in a
UI test target and put hardware/service proof in a device/system test packet.

## XCTest and Xcode test targets

XCTest remains the established framework for unit, integration, UI, and
performance tests. Swift Testing and XCTest can coexist in the same test bundle.
Choose the testing system per target and keep the target’s purpose visible.

### Target shape

A practical app project commonly has:

| Target | Responsibilities | Test boundary |
| --- | --- | --- |
| AppTests | Domain, persistence policy, networking adapters, AI validators, view-model/reducer logic | No app launch unless integration is the subject |
| AppUITests | Launch and drive the built app through critical workflows | XCUIApplication, XCUIElement queries, semantic identifiers, seeded launch state |
| FeatureTests | Optional feature-local tests when the feature is a reusable package/module | Direct module tests and package fixtures |
| PerformanceTests | Critical path baselines and metric selection | Controlled workload, fixed data set, recorded device/build |
| ExtensionTests | Extension-specific logic and projections | Extension target constraints and host/system evidence |

Xcode’s project templates can create unit and UI test bundles. Existing projects
can add unit-testing and UI-testing bundle targets. Inspect target membership,
host application, test host, signing, bundle identifiers, and the scheme before
interpreting a green run.

Use testability access intentionally. Internal access through test imports can
help test a module’s contract, but it should not turn private implementation
details into permanent product API. Prefer an explicit test fixture or
dependency-injection seam when a behavior is valuable enough to verify.

### XCTest lifecycle

Keep setup deterministic and teardown complete. A test should own the files,
database, temporary directory, URL protocol stub, clock, model adapter, or
notification observer it creates. Remove observers and cancel tasks before the
fixture disappears.

Async test code must respect actor isolation and cancellation. Do not fulfill an
expectation from a callback after the test has already returned. Do not use
unbounded sleeps to wait for work; await a signal with a bounded timeout and
record whether the timeout means failure, expected unavailability, or a service
that is not in scope.

Use XCTest expectations for legacy delegate/callback APIs or when a specific
XCTest integration requires them. For new Swift-native async code, prefer direct
async tests or Swift Testing confirmations so the lifecycle is expressed by the
structured concurrency scope.

## XCUIAutomation and UI workflow proof

UI tests interact with the app through XCUIApplication and XCUIElement. On iOS,
XCUIElement supports user-like gestures such as tapping, swiping, pinching, and
rotating. It can query existence, enabled/selected state, labels, values, focus,
frames, and accessibility identifiers.

### Query semantic identity

Prefer stable accessibility identifiers for controls and meaningful labels for
what a person hears or sees. Avoid selectors based on a fragile visual hierarchy,
localized text when the test is not a localization test, or an index that changes
when a list is sorted.

A good UI test looks for the product action:

1. Launch with a known fixture or launch argument.
2. Find the semantic control or content element.
3. Wait for the expected state with a bounded timeout.
4. Perform the user action.
5. Assert the next semantic state or domain-visible result.
6. Capture enough context to diagnose failure.

waitForExistence is a synchronization tool, not a proof that the element is
correct. Assert the identifier, role, label, enabled state, or value that
matters. When an action can legitimately be unavailable, assert the unavailable
state and its explanation rather than forcing a tap.

### Launch and environment

Use launch arguments or environment variables to select deterministic fixtures,
disable network calls, choose an account state, seed a local store, and expose
test-only diagnostics. Keep secrets and real personal data out of UI fixtures.
Reset the simulator or test container between scenarios when state leakage would
change the result.

Test the app’s first launch, resumed launch, empty data, partial data, error
state, and deep-link entry when those are product paths. A UI test that starts
only from a fully populated happy-path database can pass while onboarding,
migration, and recovery are broken.

### UI tests and accessibility

XCUIAutomation sees attributes exposed to the accessibility system. That makes
semantic UI construction valuable for both users and tests, but the presence of
an identifier does not prove a usable VoiceOver order or a complete task.

Keep a separate accessibility task script: enable VoiceOver or another assistive
technology, navigate by labels/roles, perform the task, verify focus after
transitions, change Dynamic Type, and test reduced-motion/reduced-effects states.
Record the device, OS, language, orientation, and assistive settings. Automated
UI assertions can support the packet but do not replace task-based physical
accessibility review.

## Test plans and staged feedback

A test plan is an Xcode project document that describes which tests and
configurations a test action runs. A scheme can have more than one plan, and one
plan is the default when a test action does not name one explicitly.

Use plans to give each development stage a deliberate signal:

| Plan | Include | Use |
| --- | --- | --- |
| Fast | Pure unit tests and small package fixtures | Every edit or local iteration |
| Feature | Affected unit/integration tests plus focused UI workflows | Feature branch and review |
| Accessibility | UI workflows with Dynamic Type, VoiceOver, reduced motion, and localization configurations | Native-design review |
| Performance | Metric tests and representative workload | Baseline/regression checks |
| AI evaluation | Versioned prompt/data fixtures and deterministic output criteria | Model/prompt changes |
| Release candidate | Full app, extension, system-surface, migration, and critical UI suites | Signed Release/TestFlight gate |

Use test tags to include or exclude categories. Remember that excluded tests are
not evidence of a passing behavior; they are evidence that the plan did not run
them. Record the plan name, configuration, destination, and result bundle.

From the command line, name the scheme and test plan explicitly when there is
more than one. Discover the available plans before scripting CI. A command that
tests the scheme without the intended plan may produce a green result for the
wrong set of tests.

## Performance and hitch metrics

XCTest performance tests gather repeated measurements and compare them with a
baseline or recorded threshold. Choose metrics that match the user-visible
risk:

| Metric | Useful question |
| --- | --- |
| Clock | Did this operation become slower? |
| CPU | Is the computation using more processor time? |
| Memory | Did a capture, parse, render, or model path increase footprint? |
| Storage | Did a migration/export/cache path write more data? |
| OS signpost | Which named interval regressed? |
| App launch | Did cold or warm launch time change? |
| UI hitch | Did scrolling, animation, or interaction encounter more hitches? |

Set the workload before measuring. A test that creates one tiny record, one
thumbnail, or one short prompt cannot support a claim about a production-sized
dataset. Record device model, OS, build configuration, power/network state,
dataset size, model readiness, and whether the test ran in the simulator or on
hardware.

Use Instruments and MetricKit for investigation and field diagnostics when the
question extends beyond a repeatable XCTest baseline. Keep the metric’s
definition and aggregation separate from a product promise such as “always
smooth” or “instant.”

## Foundation Models evaluation belongs beside tests, not inside snapshots

Generative output is not a deterministic string-returning function. A useful
evaluation begins with a dataset of representative inputs, a versioned prompt
and schema, and concrete quality criteria. Criteria can include:

- deterministic rules for forbidden content, schema validity, ranges, required
  fields, and side-effect permissions;
- comparison with a verified answer or reference set where an answer is known;
- semantic similarity when multiple wordings are valid;
- model-based judgment for nuanced criteria, validated against human judgment;
- human review for high-impact, ambiguous, or safety-sensitive cases.

Run deterministic validators before any model-based score. Store the input
provenance, prompt/schema version, model/device profile, locale, output, failure
reason, and score. Do not make a passing evaluation grant the model authority to
mutate domain state. The model proposes; the app validates, previews, requests
confirmation when appropriate, commits through a domain reducer, and records the
result.

When an OS or model update changes output behavior, compare the new score
distribution with the previous baseline. A single successful prompt run is not a
model-quality result.

## Liquid Glass and native-state coverage

Test the semantic and state contract of a Liquid Glass surface rather than
asserting a screenshot’s pixels. Include:

- normal, pressed, disabled, loading, stale, empty, partial, error, and offline
  states;
- large Dynamic Type and narrow/expanded size classes;
- light/dark appearance, increased contrast, reduced transparency/effects, and
  reduced motion;
- VoiceOver labels, roles, hints, focus movement, and action completion;
- content behind the glass that remains legible and owns the actual meaning;
- a clear distinction between an app-owned functional control and a
  system-owned surface such as a widget, notification, or Handoff suggestion.

If custom glass is used, keep the effect subordinate to content and use the
system API route documented for the selected SDK. Verify on a physical device
for appearance, legibility, touch target, animation, and performance. Previews
and simulator screenshots are useful state fixtures, not final glass proof.

## Evidence levels

Record the lowest evidence level that actually supports the claim:

| Level | Artifact | Does not prove |
| --- | --- | --- |
| L0 | Official source and written contract | Compile or behavior |
| L1 | Package/target compile and deterministic test | UI, hardware, service, or release |
| L2 | Integration test with fake/injected services | Real account, network, model, or system delivery |
| L3 | UI test on a named simulator/device destination | Assistive task completion or all hardware |
| L4 | Physical accessibility/performance/device run | Production delivery or App Review |
| L5 | Signed Release/TestFlight run | Production health or every OS/device |
| L6 | Production observation with logs/metrics and rollback | Universal guarantee |

Every T154 recipe should identify the evidence level it can produce and the
missing boundary that still needs a stronger test.

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/Testing/DefiningTests)
- [Organizing test functions with suite types](https://developer.apple.com/documentation/Testing/OrganizingTests)
- [Implementing parameterized tests](https://developer.apple.com/documentation/Testing/ParameterizedTesting)
- [Testing asynchronous code](https://developer.apple.com/documentation/testing/testing-asynchronous-code)
- [Running tests serially or in parallel](https://developer.apple.com/documentation/Testing/Parallelization)
- [Adding tags to tests](https://developer.apple.com/documentation/Testing/AddingTags)
- [Expectations and confirmations](https://developer.apple.com/documentation/Testing/Expectations)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Xcode testing overview](https://developer.apple.com/documentation/xcode/testing)
- [Adding tests to your Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElement](https://developer.apple.com/documentation/xcuiautomation/xcuielement)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [Improving your app’s performance](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Swift concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)

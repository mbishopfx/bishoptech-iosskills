# Swift Testing, XCTest, and UI-proof capability route

## Use this route when

Use this route when the feature has a meaningful user task, async coordination,
accessibility requirement, performance risk, on-device AI output, or release
boundary. It is especially useful for Liquid Glass screens where a screenshot
can look correct while focus, state, or interaction is wrong.

Read the [testing framework deep dive](../42-framework-deep-dives/74-swift-testing-xctest-and-ui-proof.md)
for API context and the [testable native design contract](../21-design-deep-dives/102-testable-native-design-and-ai-evaluation.md)
for screen-level decisions.

## Route contract

    product outcome
      -> named target and module boundary
      -> deterministic state/reducer tests
      -> async/integration fixture
      -> UI workflow
      -> accessibility task
      -> performance regression
      -> AI evaluation when generated output exists
      -> signed/device/system/release evidence

The route is complete only when each claim has its own evidence level. A unit
test can prove a reducer; it cannot prove that a signed widget target receives
the state or that VoiceOver can complete the task.

## Step 1: name the risk

Write one sentence for the task:

    A person can capture a receipt, review the on-device extraction,
    correct one field, save it, and find it later.

Then classify the risk:

| Risk | First test |
| --- | --- |
| Pure transformation or policy | Swift Testing or XCTest direct test |
| Actor, repository, or async stream | Async test with injected fixture and cancellation |
| View state and semantic actions | State fixture plus focused UI workflow |
| Accessibility | Physical task script with assistive settings |
| Liquid Glass interaction | State matrix, semantic UI test, physical legibility/performance |
| AI generation | Versioned dataset, deterministic validators, quality criteria |
| Camera, network, model, or service | Fake path first, then physical/service evidence |
| Extension or system surface | Target-specific integration and host/system run |
| Performance regression | Repeatable metric test with fixed workload |
| Release behavior | Signed Release/TestFlight run and archive inspection |

## Step 2: choose the test target

Keep test responsibilities visible in the project:

| Target | Put here | Do not infer |
| --- | --- | --- |
| FeatureTests or AppTests | Domain values, reducers, validation, fake adapters, persistence policy | UI or hardware behavior |
| AppUITests | Launch, query, tap, type, swipe, navigation, semantic state | Full accessibility or production data |
| PerformanceTests | Launch, render, parse, import, model/capture handoff, storage | Universal device performance |
| ExtensionTests | Widget/App Intent/provider projection logic | Host-system delivery |
| Device/System test packet | Camera, haptics, model readiness, Handoff, widgets, notifications, account/service | Compile-only or simulator-only proof |

When using Swift packages, keep the package test target close to the domain and
adapter code. The app’s UI test target should exercise the app product and its
real target membership.

## Step 3: create the state and fixture matrix

At minimum, list:

- empty and first-use;
- loading and cancellation;
- ready data with a current revision;
- partial or stale data;
- denied/revoked permission;
- network unavailable or server error;
- model unavailable, preparing, refusal, malformed output, and timeout;
- review with edits;
- commit success, duplicate commit, conflict, and rollback;
- system-surface unavailable or host-delivery delay;
- large Dynamic Type, VoiceOver, reduced motion, increased contrast, and
  localization-sensitive labels.

Each row gets a stable fixture ID. Use the ID in Swift Testing arguments, UI
launch arguments, screenshots/logs, AI evaluation records, and the proof matrix.

## Step 4: write the deterministic core

Test the smallest valuable function first:

1. Decode or construct the input fixture.
2. Apply the reducer, parser, validator, or policy.
3. Assert the state and domain result.
4. Assert that forbidden side effects did not occur.
5. Repeat the test with the same fixture.

For AI, deterministic tests should validate schema, field ranges, source IDs,
revision match, permission, allowed operation, and idempotency. They should not
pretend that generated prose is deterministic.

## Step 5: test async lifecycle

Use async tests for async APIs and a fake dependency for:

- success;
- empty response;
- delayed response;
- cancellation;
- timeout;
- permission loss;
- network path change;
- model unavailable/refusal/context limit;
- process restart or restoration when relevant.

Use a confirmation or an XCTest expectation for event callbacks. Assert event
counts and ordering where the feature depends on them. Cancel child tasks in
teardown and make callbacks unable to outlive their owner.

If a test is flaky, first inspect shared state, actor isolation, uncontrolled
time, unbounded retries, and a dependency that was not replaced. Increasing a
timeout should be the last diagnostic step, not the default fix.

## Step 6: test the running UI

Use a named UI test target and a deterministic launch contract:

| Launch input | Example purpose |
| --- | --- |
| fixture ID | Seed a known state |
| reset store | Avoid data leakage between tests |
| offline | Verify fallback and stale state |
| model unavailable | Verify clear fallback |
| accessibility audit | Enable a known test configuration |
| deep link | Test cold/warm route delivery |
| reduced effects | Test adaptive motion/glass behavior |

Prefer semantic identifiers and element attributes. A workflow should wait for a
meaningful state, act on the intended control, and verify the next state. Keep
the number of UI tests small enough that they remain useful, but cover the
critical path and the common recovery paths.

## Step 7: run accessibility tasks

Write the task in the person’s language. For example:

    Find the pending review, hear which fields changed, reject the suggestion,
    and return to the original record.

Run the task with VoiceOver and at least one non-default text size. Add
Voice Control, Switch Control, keyboard, pointer, reduced motion, and reduced
effects where the product supports those inputs. Record focus after sheets,
alerts, navigation, and asynchronous updates.

Accessibility identifiers help automation find controls. They do not prove that
the labels, roles, values, hints, order, focus, and action feedback are usable.

## Step 8: add performance regression coverage

Pick the metric from the risk:

- application launch for first-use and resumed launch;
- clock/CPU for parsing, migration, or deterministic processing;
- memory for image/capture/model buffers;
- storage for import/export/cache/migration;
- OS signpost for a named feature interval;
- hitch for scroll, animation, or glass-heavy interaction.

Use a fixed dataset and representative workload. Record device, OS, build,
power/network/model state, and baseline. If the feature is sensitive to physical
hardware, run the same scenario on a supported physical device in Release.

## Step 9: evaluate on-device AI

Define:

1. dataset and provenance;
2. prompt/schema/profile version;
3. deterministic safety and schema checks;
4. quality criteria;
5. scoring method;
6. human-review sample;
7. regression threshold;
8. fallback and rollback behavior.

Use rules for objective constraints, ground truth where it exists, semantic
comparison when wording varies, and model-based judgment only with human
calibration. Log failures without retaining sensitive input beyond the approved
retention policy.

The test route ends at a reviewable proposal. The commit path is a separate
domain test and UI/system test. Generated output must not silently call a
network, open a URL, write a record, or trigger a paid/system action.

## Step 10: select staged test plans

Recommended plans:

| Plan | Tiers | Gate |
| --- | --- | --- |
| Fast | Unit and small integration | Local iteration |
| Feature | Affected module plus critical UI | Review |
| NativeDesign | UI, accessibility task, Dynamic Type, reduced effects | Design approval |
| Performance | Metric tests and fixed workloads | Regression decision |
| AIEvaluation | Dataset and criteria | Prompt/model change |
| ReleaseCandidate | Full selected tests, migration, extension/system workflows | Signed Release/TestFlight |

Use tags to select plans. Record exclusions as scope, not as passes. On the
command line, explicitly name the test plan so a green CI result cannot quietly
test the wrong configuration.

## Step 11: assemble the proof packet

The packet should include:

- source links and target SDK/deployment assumptions;
- project target/scheme/test-plan membership;
- fixture IDs and data reset policy;
- deterministic test result bundle;
- async cancellation/lifecycle result;
- UI workflow result and screenshots/logs when useful;
- accessibility task record;
- performance baseline and workload;
- AI dataset/criteria/version/score report;
- physical-device or system-surface record;
- signed Release/TestFlight/archive inspection;
- known exclusions and next required proof.

## Stop conditions

Stop and correct the route when:

- a UI test depends on a localized string or index when a semantic identifier is
  required;
- a test passes only because work is delayed with an unbounded sleep;
- a Swift Testing suite is serialized globally to hide shared-state defects;
- the plan excludes the behavior being claimed;
- a screenshot is used as proof of accessibility or Liquid Glass performance;
- an AI evaluation has no dataset, criteria, or version context;
- a model result can commit without review or deterministic validation;
- a simulator result is presented as physical hardware or release proof;
- a Release archive has not been inspected for the intended targets/resources;
- a production claim has no signed or system evidence.

## Sources

- [Xcode testing](https://developer.apple.com/documentation/xcode/testing)
- [Adding tests to your Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Testing asynchronous code](https://developer.apple.com/documentation/testing/testing-asynchronous-code)
- [Implementing parameterized tests](https://developer.apple.com/documentation/Testing/ParameterizedTesting)
- [Running tests serially or in parallel](https://developer.apple.com/documentation/Testing/Parallelization)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElement](https://developer.apple.com/documentation/xcuiautomation/xcuielement)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

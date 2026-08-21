# Swift Testing, XCTest, UI automation, and AI proof matrix

## Purpose

This matrix separates what a test artifact can establish from what still needs a
running app, physical device, system host, signed build, service, or production
observation. It is used with the [testing framework deep dive](../42-framework-deep-dives/74-swift-testing-xctest-and-ui-proof.md),
the [native design contract](../21-design-deep-dives/102-testable-native-design-and-ai-evaluation.md),
the [capability route](../50-capability-recipes/105-swift-testing-xctest-and-ui-proof-route.md),
and the [recipe page](../70-code-recipes/117-swift-testing-xctest-ui-proof-recipes.md).

## Evidence levels

| Level | Evidence | Supports | Does not support |
| --- | --- | --- | --- |
| L0 | Official source, target contract, and written test intent | Documented route and scope | Compilation or behavior |
| L1 | Named target/package compile and static inspection | Imports, target membership, test discovery, resource inclusion | Runtime, UI, hardware, service, or model quality |
| L2 | Deterministic Swift Testing/XCTest result bundle | Reducer, parser, validator, policy, fake adapter, persistence fixture | Real UI, physical hardware, account, system host, or release |
| L3 | Async integration result with injected dependencies | Cancellation, ordering, actor/repository/model adapter contract | Real network/model/service delivery |
| L4 | UI test on a named simulator/device destination | Launch, query, gesture, semantic state, critical workflow | Complete accessibility task, all devices, or production |
| L5 | Physical accessibility/performance/device or system-host run | Assistive task, haptics/sensors/model readiness, hitch/thermal observation, widget/extension/Handoff delivery | App Store/release distribution or universal behavior |
| L6 | Signed Release/TestFlight/App Store build | User-like build, archive targets/resources, migration/account/permission behavior | Production health or App Review result |
| L7 | Production metrics/logs and rollback record | Observed field behavior for a defined population/build | Universal guarantee |

## Requirement matrix

| Claim | Minimum artifact | Stronger proof | Common false closure |
| --- | --- | --- | --- |
| Reducer returns the right state | Swift Testing/XCTest fixture | Property or parameterized state matrix | UI screenshot |
| Async operation cancels | Async test with cancellation signal and no-commit assertion | Physical process/interruption run | A timeout that happens to pass |
| Event occurs exactly once | Confirmation/expectation with count and event trace | Device/service callback run | A boolean callback flag |
| Test case is included | Test-plan inspection and result bundle | Explicit command-line plan run | A green scheme run with unknown plan |
| Critical UI task works | XCUIApplication/XCUIElement workflow | Signed device/TestFlight task run | Element existence only |
| Control is accessible | Semantic attributes and UI test | VoiceOver/Dynamic Type/reduced-effects task on device | Accessibility identifier alone |
| Liquid Glass remains usable | State/adaptation fixture and semantic assertions | Physical legibility, touch, motion, contrast, and hitch run | Pixel snapshot |
| Performance is stable | Metric test with workload and baseline | Instruments/MetricKit and physical Release run | Debug run on newest simulator |
| AI schema is safe to apply | Typed decoder and deterministic validator | Review UI and domain commit audit | Generated string matches expected text |
| AI quality is acceptable | Versioned dataset and criteria report | Human-calibrated evaluation and device/profile comparison | One good prompt result |
| Model fallback works | Availability/refusal/timeout fixtures | Physical model readiness and offline/release run | Model API compiles |
| Extension projection works | Extension target tests | Host/system surface invocation on signed device | App preview |
| Release build behaves | Archive inspection and Release test | TestFlight/App Store-like user environment | Debug success |

## Swift Testing matrix

| Feature | Fixture | Assertion | Additional gate |
| --- | --- | --- | --- |
| Test/Suite discovery | Named test target | Test appears in selected plan | Result bundle records target and plan |
| Expectation | Valid/invalid values | expect or require reports the intended failure | Failure message identifies fixture |
| Async test | Delayed success/error | Awaited result and cancellation path | No orphan task after teardown |
| Confirmation | 0, 1, and bounded event counts | Expected count/range | Event trace proves ordering and ownership |
| Parameterized test | State/locale/device cases | Each case has diagnosable identity | Selected-case rerun where supported |
| Tags | unit/ui/accessibility/performance/aiEvaluation | Plan includes/excludes intended tags | Exclusions are recorded as scope |
| Parallelization | Isolated and shared fixtures | Isolated cases remain independent | Serialized only at the resource boundary |
| Availability | New API and older deployment | Unsupported case is skipped with reason | Supported target runs the behavior |
| MainActor | Main-actor store/view model | No isolation violation | Tests do not use MainActor to hide unsafe access |

## XCTest and UI matrix

| Surface | What to exercise | Evidence |
| --- | --- | --- |
| App launch | Fresh, seeded, resumed, deep link, interrupted | Launch args, destination, state log |
| Navigation | Push, sheet, tab, back, route replacement | Semantic element sequence and destination state |
| Input | Text, picker, slider, scroll, keyboard/pointer where supported | Element attributes, action result, focus |
| Error recovery | Network/model/permission/data error | Error label/role, retry/cancel, no stale commit |
| Review flow | Generated proposal, edit, reject, accept | Source/changes visible, explicit action, domain result |
| Persistence | Save, relaunch, migration, conflict | Deterministic store plus signed run |
| System entry | Widget/App Intent/Handoff/notification/document | Target/system host evidence |
| Accessibility | VoiceOver, Dynamic Type, reduced motion/effects, contrast | Task record on physical device |

Use identifiers for stable product roles. Use labels and values for human
meaning. Use waitForExistence or an equivalent bounded synchronization only
after the fixture has established the expected state.

## Performance matrix

| Risk | Metric or tool | Workload record | Required comparison |
| --- | --- | --- | --- |
| Cold/warm launch | Application launch metric, Instruments | Fresh/resumed install, device, OS, build | Baseline distribution |
| Parsing/import | Clock, CPU, signpost | Input count/size, format, cache | Previous build/device baseline |
| Image/model memory | Memory metric, Instruments | Pixel dimensions, batch, model profile | Peak and sustained memory |
| Storage/migration | Storage metric, signposts | Store size, schema version, device storage | Write volume and duration |
| Scroll/animation | Hitch metric, Instruments | Content count, glass/effects, size class | Hitch count and interaction state |
| Field behavior | MetricKit diagnostics | Build, device population, workload | Versioned aggregation, not one run |

Do not change the workload, device, or build configuration while declaring a
regression fixed. If the environment must change, record it as a new baseline.

## Accessibility proof matrix

| Task step | Expected semantic result | Automated support | Device evidence |
| --- | --- | --- | --- |
| Find the screen | Correct title/heading and initial focus | Element query/label | VoiceOver navigation |
| Identify primary action | Role, label, enabled state | Identifier/attributes | VoiceOver/Voice Control |
| Change value | New value announced and retained | Value assertion | Dynamic Type and assistive input |
| Open/close sheet | Focus moves and returns predictably | Exists/does-not-exist | Physical focus review |
| Review AI change | Source and changed fields understandable | Text/value checks | Spoken review and edit task |
| Recover from error | Cause and next action clear | Error state assertion | Task completion after retry/cancel |
| Finish task | Confirmation or destination is announced | Final semantic state | Full end-to-end task record |

## AI evaluation matrix

| Criterion | Example check | Test type | Evidence |
| --- | --- | --- | --- |
| Schema | Required fields decode | Deterministic | Fixture result |
| Provenance | Source IDs exist and match revision | Deterministic | Validator log |
| Safety | Forbidden operation/content absent | Deterministic rule | Failure report |
| Ground truth | Known answer or field target | Comparison | Accuracy/error distribution |
| Semantic quality | Meaning preserved across wording | Embedding/semantic comparison | Scored dataset |
| Tone/utility | Helpful, clear, appropriate | Model-based or human judgment | Calibrated sample |
| Privacy | No unapproved retention or transmission | Policy test and inspection | Data-flow record |
| Fallback | No model, refusal, timeout, context limit | Availability/async fixture | UI and no-commit assertion |
| Revision | Stale proposal cannot overwrite newer truth | Domain test | Conflict result |
| Commit | Explicit user action required | UI/domain test | Accepted/rejected trace |

Record prompt, schema, model/profile, OS, language, input fixture, output,
validator versions, criteria scores, and reviewer disposition. Keep sensitive
inputs out of shared result bundles unless the retention policy permits them.

## Test-plan and release matrix

| Gate | Plan contents | Required record |
| --- | --- | --- |
| Local | Fast unit and fixture tests | Command, target, result |
| Review | Affected module plus critical UI | Scheme, plan, destination |
| Native design | Accessibility and adaptive UI tasks | Device settings and task outcome |
| Performance | Metric tests and fixed workload | Baseline and measurement context |
| AI change | Dataset, criteria, validator, human sample | Version comparison |
| Release candidate | Full selected tests, migration, extensions, system surfaces | Archive, signed install, TestFlight/device run |

Inspect that the selected test plan actually contains the targets and tags
needed for the gate. A skipped test is not a passing test.

## Failure states and stop conditions

Stop the proof packet when:

- the test target is not the target that ships;
- the test plan or configuration is not recorded;
- fixtures depend on uncontrolled time, network, account, locale, or model state;
- a shared resource forces broad serialization without an isolation plan;
- UI selectors depend on brittle layout order;
- accessibility is inferred from identifiers or screenshots;
- a performance number has no workload/device/build context;
- an AI score has no dataset, criterion, or version context;
- an AI proposal bypasses validation/review or commits stale state;
- a system surface, physical sensor, or release build is claimed from a simulator;
- a signed archive has not been checked for targets, resources, privacy, and
  entitlements.

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/Testing/DefiningTests)
- [Implementing parameterized tests](https://developer.apple.com/documentation/Testing/ParameterizedTesting)
- [Testing asynchronous code](https://developer.apple.com/documentation/testing/testing-asynchronous-code)
- [Running tests serially or in parallel](https://developer.apple.com/documentation/Testing/Parallelization)
- [Expectations and confirmations](https://developer.apple.com/documentation/Testing/Expectations)
- [Xcode testing](https://developer.apple.com/documentation/xcode/testing)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElement](https://developer.apple.com/documentation/xcuiautomation/xcuielement)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

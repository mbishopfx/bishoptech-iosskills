# Test and evidence matrix

Use this reference to route a claim to the smallest test or audit that can
support it. Preserve the target, SDK, OS, device, configuration, fixture, plan,
and result artifact with the claim.

## Evidence levels

| Level | Evidence | Supports | Does not support alone |
| --- | --- | --- | --- |
| source | Official Apple/Swift docs and HIG | API/design/policy direction | this target’s build or behavior |
| static | target/scheme/entitlement/manifest inspection | intended configuration | valid signing or system delivery |
| compile | SDK typecheck/build | API shape and target compilation | physical behavior, AI quality, accessibility |
| fixture/unit | Swift Testing/XCTest deterministic result | named logic/state behavior | UI/hardware/system behavior |
| simulator/UI | XCUI workflow on named destination | selected running-app workflow | physical sensors, assistive tasks, production |
| physical/system | named device or host surface | observed hardware/accessibility/system behavior | all devices, regions, or future OS versions |
| signed artifact | archive inspection/install/update | packaging and user-like build | App Review or production rollout |
| TestFlight/App Store | exact distributed build | beta/distribution observation | universal production correctness |
| production | live route observation | named production environment | future versions, devices, accounts, or regions |

## Fixture states

Create only the states relevant to the feature, but explicitly decide each row.

| State | Minimum assertion |
| --- | --- |
| firstUse/empty | entry and next action are clear |
| loading | progress is semantic and cancellation is owned |
| ready/current | source revision and domain truth are visible where needed |
| partial/stale | freshness or missing data is not hidden |
| denied/restricted/revoked | permission explanation and manual fallback exist |
| unavailable/notConfigured | target/device/model/service limitation is surfaced |
| offline/retryable | retry is bounded and no duplicate side effect occurs |
| canceled/interrupted | task stops and stale result cannot overwrite state |
| conflict/migration | local, remote, ancestor, or schema revision is explicit |
| malformed AI/refusal/timeout | typed fallback is safe and reviewable |
| committed | actual domain commit is distinguished from proposal/UI state |
| systemDelayed/expired | stale/end behavior remains legible |

Give each fixture a stable ID, source revision, privacy class, and reset policy.
Use the same ID in unit arguments, UI launch arguments, AI evaluation records,
result attachments, screenshots/logs, and release packets.

## Target and plan matrix

| Target/plan | Include | Keep out |
| --- | --- | --- |
| package/module unit | pure values, reducers, validators, fake adapters | UI host, live services, personal data |
| app unit/integration | persistence policy, actors, repositories, cancellation | unbounded live network or shared account |
| UI test target | critical launch/query/action/recovery workflows | fragile implementation hierarchy |
| accessibility plan | UI workflows, audit, Dynamic Type, reduced effects, locales | claim that audit alone proves task success |
| performance plan | fixed workload, Release configuration, metrics/signposts | arbitrary debug-only baseline |
| AI evaluation plan | versioned data, schema/grounding validators, rubric, human sample | one prompt or unversioned prose judgment |
| extension/system target | host invocation, projection, expiration, action result | main-app screen as proxy for host delivery |
| device plan | hardware, permissions, account, accessories, assistive settings | simulator-only claims |
| release candidate | selected full tests, migration, target/artifact audit | hidden exclusions or wrong test plan |

## Swift Testing route

- Prefer structs with independent initialization.
- Use `#require` for a precondition and `#expect` for behavior.
- Use parameterized arguments for state/boundary matrices; keep cases
  identifiable and avoid accidental Cartesian growth.
- Use async tests and `confirmation` around the operation that emits an event.
  Test zero-event cancellation or authorization loss where applicable.
- Use tags for evidence classes and test plans for explicit configuration.
- Use `.serialized` only for a real shared resource; isolate stores and clocks
  first.
- Put `@available` on each test needing a newer OS.
- Bound possible stalls with `.timeLimit(.minutes(...))` and record the reason.
- Attach sanitized diagnostics only when retention/access rules permit it.

Swift Testing does not replace UI testing. Keep XCTest for XCUIAutomation,
accessibility audits, and performance APIs.

## UI and accessibility route

Launch with explicit fixture, reset, offline, account, model, appearance, or
deep-link arguments. Prefer stable identifiers for automation and meaningful
labels/roles/values for people. A query must assert more than existence when
the control’s enabled state, label, value, or selection matters.

For each critical screen:

1. run the automated accessibility audit;
2. test the task with VoiceOver on a named device;
3. test Dynamic Type and localization lengths;
4. test reduced motion and reduced transparency/effects;
5. test contrast and color-independent meaning;
6. test keyboard/pointer/controller/alternate input in scope;
7. record focus after sheets, alerts, navigation, and async updates.

An audit result is a diagnostic artifact. A task record is required for the
claim that a person completed the task with an assistive technology.

## AI and Liquid Glass route

For generated output, retain:

- input/provenance and approved source revision;
- model/profile/prompt/schema version and availability state;
- decoded typed proposal and deterministic validator result;
- quality rubric, representative cases, score distribution, and human sample;
- refusal/malformed/context-limit/timeout/offline fallback;
- accept/edit/reject/commit behavior and stale-revision handling.

For Liquid Glass, retain state/fixture and reduced-effects evidence. Do not use
a screenshot to prove semantic labels, focus, hit targets, contrast, motion,
memory, or system-owned surfaces.

## Performance and device route

Record the fixed workload, warm/cold state, dataset, metric, baseline,
acceptable threshold, device model, OS build, power/network/model state, and
Release/Debug configuration. Use Instruments or signposts when XCTest metrics
cannot explain the behavior. A single run is a measurement, not a universal
performance guarantee.

For camera, microphone, sensors, haptics, GPU, model assets, accessories,
background, Watch, CarPlay, widgets, notifications, or account/system claims,
name the physical device/host, permissions/settings, event/action/result, and
recovery path.

## Minimal proof record

```text
claim:
level:
target:
scheme:
test_plan:
configuration:
sdk:
os:
device_or_host:
fixture_ids:
permissions_account_settings:
command:
result_artifact:
observed_result:
what_this_proves:
what_this_does_not_prove:
next_gate:
```

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/testing/definingtests)
- [Expectations and confirmations](https://developer.apple.com/documentation/testing/expectations)
- [TestScoping](https://developer.apple.com/documentation/testing/testscoping)
- [Attachment](https://developer.apple.com/documentation/testing/attachment)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElementQuery](https://developer.apple.com/documentation/xcuiautomation/xcuielementquery)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Writing and running performance tests](https://developer.apple.com/documentation/xcode/writing-and-running-performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

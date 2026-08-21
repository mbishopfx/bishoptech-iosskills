# SwiftUI testing, XCTest UI, device, and release-assurance proof matrix

Use this matrix to prevent a green test, preview, simulator run, AI response,
archive, or TestFlight upload from being treated as proof of a different claim.
Record the target, SDK, OS, device, configuration, fixture, plan, and result
bundle for every row that matters.

## Evidence levels

| Level | Evidence | Valid claim boundary |
| --- | --- | --- |
| P0 | Official source and availability review | API/design direction is documented |
| P1 | Target/build/typecheck and deterministic fixture | Code shape and pure state behavior |
| P2 | Swift Testing/XCTest result bundle | Tested behavior for the named fixture/configuration |
| P3 | XCUI workflow and automated accessibility audit | Running-app workflow and common audit findings |
| P4 | Physical device or system-surface run | Named hardware/OS/settings behavior |
| P5 | Release archive, install/update, TestFlight run | Signed user-like build evidence |
| P6 | App Review/production observation | External review or live environment result |

Do not raise a row to a higher level without the evidence required by that
level. A test plan can define scope; it cannot create evidence for excluded
tests.

## Claim and artifact matrix

| ID | Claim | Minimum evidence | Artifact to retain | Does not prove |
| --- | --- | --- | --- | --- |
| SRC-01 | API route is appropriate | P0 source/availability review | official URL list, SDK/OS notes | implementation correctness |
| TARGET-01 | Intended target can run the route | P1 target build/typecheck | target, scheme, SDK, deployment, capabilities | entitlement provisioning or device support |
| FIX-01 | Fixture is reproducible | P1 deterministic constructor/reset | fixture ID, inputs, seed/reset policy | production data shape |
| UNIT-01 | Pure reducer/parser/validator works | P2 Swift Testing expectations | test result and source revision | UI/system/hardware behavior |
| UNIT-02 | Invalid and boundary states are handled | P2 parameterized cases | case IDs and failures | untested cases |
| ASYNC-01 | Async success/cancellation/retry works | P2 async test with bounded confirmation | event trace, cancellation result | live service/network availability |
| ASYNC-02 | Shared state is isolated | P2 parallel/actor-safe test | fixture ownership and repeat result | every production race |
| AI-01 | Proposal decodes and is admissible | P2 typed validator | input/output schema, source revision | semantic quality or truth |
| AI-02 | AI quality meets a product criterion | P2 versioned evaluation plus human sample | dataset, model/profile, rubric, scores | future model versions |
| AI-03 | Proposal cannot silently commit | P2 domain/commit test | accept/edit/reject/idempotency result | user intent in production |
| UI-01 | Critical task can be completed | P3 XCTest UI workflow | plan, fixture, destination, result bundle | accessibility task success |
| UI-02 | UI queries use semantic identity | P3 query/identifier review | identifiers, labels, role/value evidence | visual polish |
| A11Y-01 | Common issues are detected | P3 `performAccessibilityAudit` | audit output and screen list | complete accessibility |
| A11Y-02 | Assistive task is usable | P4 VoiceOver/alternate-input task | device/settings/task observations | all assistive technologies |
| GLASS-01 | Liquid Glass states remain functional | P2 state tests + P3 UI workflow | state matrix, semantic actions | physical legibility/performance |
| GLASS-02 | Reduced effects preserve the task | P3 configuration + P4 task | setting, device, focus/action record | every OS/device combination |
| PERF-01 | Critical path has a baseline | P2/XCTest metric with fixed workload | metric, baseline, dataset, configuration | universal performance |
| PERF-02 | Hardware-sensitive path meets device target | P4 Release performance run | device, OS, power, workload, results | unsupported devices |
| PLAN-01 | Intended test set ran | P2 named test plan and `.xcresult` | scheme, plan, configuration, exclusions | behavior not selected |
| SYSTEM-01 | Extension/system surface delivers | P4 target-specific/system run | host, device, event/action/result log | app-screen simulation |
| RELEASE-01 | Release archive has intended contents | P5 archive inspection | UUID, bundle IDs, targets, entitlements, resources | App Review approval |
| RELEASE-02 | Fresh install works | P5 signed install/run | exact build, device, permissions, result | update/migration behavior |
| RELEASE-03 | Update/migration works | P5 prior-build update | prior/current versions, store/account/keychain evidence | every historical version |
| RELEASE-04 | TestFlight build reproduces task | P5 exact uploaded build | TestFlight build ID, device, task log | production-wide behavior |
| RELEASE-05 | App is approved | P6 App Review/production record | external result and date | future versions/regions |

## Swift Testing evidence checks

- [ ] Every test that needs iOS 26 has its availability boundary on the test.
- [ ] Suites use independent fixtures and do not rely on execution order.
- [ ] Parameterized cases are bounded and identifiable; Cartesian growth is
      intentional when two collections are used.
- [ ] `#require` guards meaningful preconditions; `#expect` checks the behavior.
- [ ] Async tests await the work they observe and test cancellation/zero-event
      behavior where applicable.
- [ ] Tags and test plans communicate scope; skipped or known-issue tests are
      not silently counted as passing evidence.
- [ ] Attachments are sanitized and retention-approved.

## XCTest/XCUI and accessibility checks

- [ ] UI tests launch with explicit fixture, reset, network, account, and model
      state.
- [ ] Queries use stable identifiers and assert meaningful labels/values/roles.
- [ ] Waits are bounded and synchronize on semantic state rather than sleep.
- [ ] Accessibility audits cover every critical workflow screen.
- [ ] VoiceOver, Dynamic Type, reduced motion, reduced effects/transparency,
      contrast, keyboard/pointer, and supported alternate inputs are tested as
      tasks on a named device.
- [ ] Audit pass is reported as audit evidence, not as complete accessibility.

## AI evaluation checks

- [ ] Dataset provenance, retention, model/profile, prompt/schema, and source
      revision are recorded.
- [ ] Validators cover decoding, stale revisions, ranges, allowed operations,
      privacy, refusal, timeout, unavailable model, and malformed output.
- [ ] Quality criteria distinguish objective correctness from semantic quality.
- [ ] Human review calibrates any model-based judge and records disagreements.
- [ ] The proposal cannot call a network, mutate a record, or trigger a system
      or paid action without the explicit domain/UI commit path.

## Release and physical-device checks

- [ ] Archive version/build, bundle ID, target families, embedded extensions,
      entitlements, privacy manifests, resources, and signing match the plan.
- [ ] Debugger-disconnected and fresh-install behavior are considered where
      watchdog, suspension, keychain, App Group, or migration behavior matters.
- [ ] Device evidence names model, OS, settings, permissions, account,
      accessory/route, build, and observed result.
- [ ] TestFlight evidence is for the exact uploaded build, not a local debug or
      a different archive.
- [ ] Open exclusions and App Review/production-only claims remain visible.

## Proof record template

```text
claim:
evidence_level:
target:
scheme:
test_plan:
sdk:
os:
device:
configuration:
fixture_ids:
permissions_account_settings:
result_bundle_or_archive:
observed_result:
what_this_proves:
what_this_does_not_prove:
next_required_evidence:
```

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/testing/definingtests)
- [Expectations and confirmations](https://developer.apple.com/documentation/testing/expectations)
- [TestScoping](https://developer.apple.com/documentation/testing/testscoping)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElementQuery](https://developer.apple.com/documentation/xcuiautomation/xcuielementquery)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Writing and running performance tests](https://developer.apple.com/documentation/xcode/writing-and-running-performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)

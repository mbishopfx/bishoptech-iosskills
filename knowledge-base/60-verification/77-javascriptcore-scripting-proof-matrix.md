# JavaScriptCore scripting proof matrix

This matrix keeps “the JavaScript parsed” separate from “the app safely
performed a user-approved action.” JavaScriptCore documentation proves the
framework contract; only a named target and tests prove this app’s bridge,
ownership, privacy, and runtime behavior.

## Evidence ladder

| Claim | Minimum evidence | Does not prove |
| --- | --- | --- |
| API is available | Current Apple source and deployment-target review | That the selected target imports/compiles it |
| Script is valid | Syntax/fixture evaluation with exception capture | That its output matches the product schema |
| Native bridge is narrow | Capability manifest and bridge audit | That hidden object references cannot leak through output |
| Result is deterministic | Repeatable fixture with source/context revision | That a model-generated script generalizes |
| Native side effect is safe | Output validation, authorization, user review, and target-specific operation evidence | That a `true`/returned value means the side effect completed |
| Memory is bounded | Teardown and managed-value tests plus runtime metrics | That one Debug run proves every device |
| Web handoff is safe | WebKit origin/process/message tests | That JavaScriptCore isolates web content |
| Release is configured | Signed artifact/inspector/resource inspection | That development inspector settings are safe in production |

## Fixture pack

Keep a versioned script fixture set with expected typed results:

| Fixture | Expected purpose |
| --- | --- |
| Pure arithmetic/string transform | Primitive conversion and deterministic output |
| Nested dictionary/array | Explicit schema and depth limits |
| `undefined`, `null`, and empty output | Required/optional output semantics |
| Syntax error | Exception handler, redacted diagnostic, edit/retry state |
| Runtime throw | Exception property and failure state |
| Native callback rejection | Native validation sets a failure; no stale commit |
| Unexpected function/object wrapper | Output validator rejects dynamic values |
| Large number/BigInt | Identifier/currency precision policy |
| Oversized source/input/output | Resource budget and readable refusal |
| Stale source revision | Re-run required; proposal not applied |
| Malicious capability attempt | No raw native object, token, or hidden function exposed |
| AI-generated proposal | Model metadata, review, fixture run, accept/edit/dismiss |
| Web page message | Origin/typed message policy separate from local script |

Store fixture source and expected output in test resources, not in production
analytics. Avoid using real private records as the default fixture.

## Context and virtual-machine evidence

Test the ownership rule explicitly:

- context created with a new virtual machine owns its values;
- contexts sharing a virtual machine can use compatible values only when the
  design requires that route;
- a value from another virtual machine is rejected and does not become a
  cross-context domain object;
- the feature runner tears down its context and callbacks on cancellation;
- concurrent work either serializes through one owner or uses separate virtual
  machines with independent state;
- no `JSValue` appears in a `Sendable`, persistence, or long-lived view model.

Record whether the test proves API behavior, app ownership, or performance. A
successful evaluation on one thread is not proof of safe concurrent use.

## Exception and native bridge evidence

| Test | Expected evidence |
| --- | --- |
| Syntax error | `exceptionHandler` receives a diagnostic; UI shows failure; prior output is cleared |
| Runtime error | `context.exception`/handler state maps to a retryable failure |
| Native block receives invalid input | Bridge rejects before touching protected data |
| Exported method throws/rejects | JavaScript sees a defined failure; native side effect is not claimed |
| Unknown function/property | Capability registry refuses access |
| Valid pure call | Typed result passes schema validation and fixture expectation |
| User cancels/revises | Result is discarded or marked stale; no commit |

Do not set the exception handler to `nil` in a production route merely to avoid
an error. Include redaction checks so diagnostics do not leak source, tokens,
health/contact content, or arbitrary arguments.

## Memory and lifecycle evidence

Exercise a long-lived exported object and callback:

- store a `JSManagedValue` rather than a raw `JSValue` in the native owner;
- register/remove the managed reference with the `JSVirtualMachine` as the
  documented ownership chain changes;
- release the feature runner and verify the context can deallocate;
- repeat create/evaluate/teardown cycles;
- exercise view dismissal, backgrounding, cancellation, and source replacement;
- record memory growth and retained-object diagnostics on a representative
  device/configuration.

Use a release build when making memory or performance claims. A test that
passes with one short script does not prove no retain cycle exists.

## Security and privacy evidence

Review the capability manifest as a threat-model fixture:

- no raw persistence context, file manager, network client, keychain, token,
  contact, health sample, camera object, or view controller is exported;
- input is bounded and redacted;
- only selected record IDs or value projections cross the bridge;
- JavaScript cannot invent a native capability name or call an unregistered
  side effect;
- output is validated before any native action;
- authorization is checked again at commit;
- scripts/proposals can be deleted according to product policy;
- remote fallback is explicit and user-mediated;
- WebKit messages have a separate origin/content policy;
- inspector is development-only unless a documented release decision says
  otherwise.

Security review is evidence of a designed boundary, not a proof that all engine
bugs or malicious host code are impossible. Keep the exposed surface small.

## AI proposal evidence

For each model-assisted run, capture:

- model route/version and availability state;
- prompt/context or typed-input policy;
- source/revision and redaction result;
- generated DSL/JSON/script proposal;
- syntax, capability, size, and output validation;
- fixture/dry-run result;
- review task completion;
- stale/cancelled/invalid behavior;
- no-AI/manual fallback;
- final native commit and error state.

Evaluate representative tasks, not only happy-path examples. Do not claim the
model can safely generate arbitrary app code from a few successful fixtures.

## UI, accessibility, and system-surface evidence

Run the script review task with:

- VoiceOver and semantic reading order;
- Dynamic Type and long errors/output;
- reduced motion/transparency and increased contrast;
- keyboard/pointer/Switch Control/Voice Control where supported;
- localization and right-to-left layout;
- empty, loading, stale, invalid, cancelled, and no-AI states;
- App Intent/widget/share/export route if the script is exposed there.

Record whether the person can understand and dismiss a proposal without
reading JavaScript. A screenshot or accessibility tree dump alone is not task
proof.

## Performance evidence

Measure with bounded and representative scripts:

- parse/evaluation duration;
- main-actor blocking/hitches;
- input/output conversion cost;
- memory before/after context and runner teardown;
- repeated-run growth;
- energy/thermal impact if scripts drive media, rendering, sensors, or network;
- UI update cadence and cancellation behavior.

If an app-level execution budget abandons a runner, document what “cancelled”
means and prove that no later completion can commit stale output. Do not claim
hard preemption if the route only stops observing a synchronous call.

## Signed/release evidence

Inspect the archive or installed release build for:

- JavaScriptCore framework linkage and target membership;
- bundled rule/script resources and case-sensitive paths;
- development inspector configuration;
- privacy manifests and permission strings for exposed native capabilities;
- App Intent/widget/extension target boundaries;
- release-only source/resource transformations;
- first-run behavior with no network, no account, denied permissions, and
  deleted/stale scripts.

Test the installed artifact on the intended device family. A development
script runner and a production user-authored script route are different claims.

## Verification record template

~~~text
Feature / target / SDK / build configuration:
JavaScriptCore context/VM owner:
Script source/revision and capability manifest:
Input/output schema:
Fixture results:
Exception/bridge/memory evidence:
Concurrency/actor evidence:
Privacy/security review:
AI proposal/evaluation evidence:
Accessibility/system-surface evidence:
Physical-device/performance evidence:
Signed/release/inspector evidence:
Known limits and fallback:
Conclusion: documented / compiled / tested / device / system / release
~~~

## Sources

- [JavaScriptCore](https://developer.apple.com/documentation/javascriptcore)
- [JSContext](https://developer.apple.com/documentation/javascriptcore/jscontext)
- [JSVirtualMachine](https://developer.apple.com/documentation/javascriptcore/jsvirtualmachine)
- [JSValue](https://developer.apple.com/documentation/javascriptcore/jsvalue)
- [JSManagedValue](https://developer.apple.com/documentation/javascriptcore/jsmanagedvalue)
- [JSExport](https://developer.apple.com/documentation/javascriptcore/jsexport)
- [C JavaScriptCore API](https://developer.apple.com/documentation/javascriptcore/c-javascriptcore-api)
- [JSContext exception](https://developer.apple.com/documentation/javascriptcore/jscontext/exception)
- [JSContext exception handler](https://developer.apple.com/documentation/javascriptcore/jscontext/exceptionhandler)
- [JSContext virtual machine](https://developer.apple.com/documentation/javascriptcore/jscontext/virtualmachine)
- [JSValueRef](https://developer.apple.com/documentation/javascriptcore/jsvalueref)
- [WebKit](https://developer.apple.com/documentation/webkit)
- [WKWebView](https://developer.apple.com/documentation/webkit/wkwebview)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

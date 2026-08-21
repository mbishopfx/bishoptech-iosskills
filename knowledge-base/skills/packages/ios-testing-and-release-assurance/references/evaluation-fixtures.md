# Testing and release-assurance evaluation fixtures

Use these prompts to evaluate whether an LLM routes Apple work precisely. Each
run should record model/version, source revision, target facts, selected route,
files changed, commands, evidence level, and unsupported claims.

## Fixture A: Liquid Glass review screen

**Prompt:** Build a SwiftUI iOS 26 review screen with a chart, a generated
explanation, and accept/edit/reject actions. Make it feel native.

**Accept when the response:**

- chooses standard SwiftUI controls and functional Liquid Glass grouping;
- models idle/loading/ready/error/stale/reduced-effects states;
- gives controls labels, identifiers, focus, Dynamic Type, localization, and
  VoiceOver paths;
- tests state and validators deterministically, then uses XCTest for the
  critical UI workflow;
- records what a preview, simulator, physical device, and release build prove.

**Reject when it:** copies Apple-owned UI, styles every surface as glass, uses a
screenshot as accessibility proof, or calls the model explanation truth.

## Fixture B: typed on-device proposal

**Prompt:** Summarize a private local record on device and propose one next
action without sending the record to a server.

**Accept when the response:**

- checks model/device availability and gives a deterministic fallback;
- minimizes/redacts context and records retention/deletion policy;
- uses typed output, source revision, schema validation, refusal/cancellation,
  review, and explicit commit;
- tests malformed, stale, unavailable, empty, and adversarial outputs;
- separates generated quality from domain correctness and physical proof.

**Reject when it:** adds a remote service by default, lets the model mutate
truth, logs private prompts, or promises accuracy from one example.

## Fixture C: UI and accessibility workflow

**Prompt:** Audit a release candidate for a task that opens a review, rejects a
proposal, and finds the original record later.

**Accept when the response:**

- inspects the actual target, scheme, test plan, and fixture contract;
- uses XCUI semantic identifiers and bounded waits;
- runs automated accessibility audits and a named VoiceOver/Dynamic Type task;
- tests error/retry/offline and fresh-install/update states;
- retains the exact result bundle and names remaining device/release gaps.

**Reject when it:** returns only a generic checklist, uses indices/sleeps, or
calls the audit “complete accessibility.”

## Fixture D: performance and signed release

**Prompt:** Decide whether a glass-heavy dashboard is ready for TestFlight.

**Accept when the response:**

- fixes workload, metric, baseline, Release configuration, device, OS, power,
  and model/network state;
- separates XCTest/Instrument measurements from physical legibility and haptic
  or system evidence;
- inspects archive targets, resources, entitlements, privacy, versions, and
  extensions;
- installs the exact TestFlight build and repeats the critical task;
- reports App Review and production as unresolved external gates.

**Reject when it:** treats one simulator screenshot, archive, or green test as
universal performance or approval.

## Fixture E: maintenance trigger

**Prompt:** The installed SDK changes a Testing or SwiftUI API availability.
Refresh the route and skill bundle.

**Accept when the response:**

- reopens official Apple pages and installed interfaces;
- identifies affected pages, recipes, availability rows, source registry,
  package references, and evaluation fixtures;
- updates stale claims without rewriting unrelated history;
- reruns structural/source/live URL, recipe, package, and archive validation;
- records a concise receipt with the next refresh trigger.

**Reject when it:** patches one snippet from memory, uses a secondary blog as
authority, or leaves stale availability claims in a distributable skill.

## Self-evaluation record

```text
fixture:
model_and_version:
source_revision:
target_sdk_os_device:
selected_roles:
selected_route:
files_changed:
commands:
evidence_levels:
accepted_behaviors:
rejected_behaviors:
unsupported_claims:
next_improvement:
```

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

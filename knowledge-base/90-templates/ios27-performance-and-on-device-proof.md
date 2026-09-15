# iOS 27 Performance and On-Device Proof

Use this template whenever an agent is asked to call a feature “fast,”
“real-time,” “private,” “on-device,” “energy efficient,” or “native.” It keeps
SDK facts, workload measurements, model readiness, privacy boundaries, and
physical-device evidence separate.

## 1. Claim and route

- User-visible operation:
- Consequence if it is slow, stale, wrong, interrupted, or unavailable:
- Claim under review:
- Selected framework/API route:
- Rejected narrower/deterministic alternatives:
- Target(s), device family, minimum OS, deployment target:
- Build SDK, Xcode, Swift, configuration:
- Source and data sensitivity:

### Processing-location classification

Choose the narrowest truthful label for each operation:

| Operation | Glasses/native device | Phone-local | Remote service | Mixed/unknown | What leaves the device |
| --- | --- | --- | --- | --- | --- |
| Capture/preprocessing |  |  |  |  |  |
| Model/inference/analysis |  |  |  |  |  |
| Persistence/sync |  |  |  |  |  |
| User-visible system surface |  |  |  |  |  |

Do not infer processing location from an imported framework, a model name, a
successful compile, a simulator, or a response that feels immediate. Trace
the exact API, asset, network path, device state, and privacy policy.

## 2. Availability and lifecycle

| State | Trigger/owner | User-visible behavior | Cancellation/cleanup | Fallback | Evidence |
| --- | --- | --- | --- | --- | --- |
| Unsupported OS/device |  |  |  |  |  |
| Permission denied/restricted |  |  |  |  |  |
| Model/asset not ready |  |  |  |  |  |
| Preparing |  |  |  |  |  |
| Processing |  |  |  |  |  |
| Partial/proposal |  |  |  |  |  |
| Refusal/validation failure |  |  |  |  |  |
| Cancelled/interrupted |  |  |  |  |  |
| Committed result |  |  |  |  |  |

For AI or learned perception, record model revision, prompt/schema or request
revision, locale, preprocessing, confidence/quality fields, input bounds,
human review, deterministic validation, and side-effect authorization.

## 3. Workload and measurement plan

- Representative fixture/input IDs:
- Cold versus warm state:
- Foreground/background/locked state:
- Network/power/thermal state:
- Device/OS/build:
- Test plan/scheme/configuration:
- Baseline commit/build:
- Acceptable regression threshold:

| Metric | Instrument | Workload | Baseline | Current | Threshold | Evidence/artifact |
| --- | --- | --- | --- | --- | --- | --- |
| Launch/first useful frame |  |  |  |  |  |  |
| Interaction latency |  |  |  |  |  |  |
| Scroll hitch/frame pacing |  |  |  |  |  |  |
| Inference/processing latency |  |  |  |  |  |  |
| Peak/steady memory |  |  |  |  |  |  |
| Energy/thermal impact |  |  |  |  |  |  |
| Dropped frames/inputs |  |  |  |  |  |  |
| Cancellation/teardown |  |  |  |  |  |  |

Use `OSLog`/signposts and XCTest performance tests for controlled workloads.
Record device, OS, build, fixture, power state, and warm/cold conditions. A
single trace is a diagnosis or baseline, not a universal performance claim.

## 4. MetricKit iOS 27 lane

For a target built with the iOS 27 SDK, evaluate the Swift-first
`MetricManager` async sequences. Keep a long-lived manager and consume reports
in owned tasks; do not treat reports as an immediate per-interaction logger:

```swift
let manager = MetricManager()

Task {
    for await report in manager.metricReports {
        process(report)
    }
}

Task {
    for await report in manager.diagnosticReports {
        process(report)
    }
}
```

Record the deployment fallback (`MXMetricManager` subscriber route), the exact
SDK/API availability, report-domain ownership, redaction/retention, and how
simulated payloads differ from reports delivered by a physical device. A
MetricKit API compile or simulated payload is not proof of real-device delivery.

## 5. Privacy and native boundary

- Raw input retained for how long and where:
- Model asset and revision:
- Prompt/instruction/schema version:
- Data sent to a server or Private Cloud Compute, if any:
- Logs/signposts redacted:
- User disclosure and permission:
- Delete/cancel/termination behavior:
- Shared process/device/extension boundary:
- Manual or deterministic fallback:

Keep private prompts, media, health/contact data, credentials, tokens, and
unnecessary identifiers out of logs, fixtures, screenshots, and source control.

## 6. Evidence ledger and claim wording

| Claim | Required evidence | Actual evidence | Safe wording | Open gap |
| --- | --- | --- | --- | --- |
| API is available | Official docs + selected SDK interface/type-check |  | “Documented and type-checked for…” |  |
| Feature compiles | App target/scheme/configuration build |  | “Compiles in…” |  |
| It runs on device | Named physical device/OS/build/task |  | “Observed on…” |  |
| Processing is on-device/private | Traced route + device/model state + network/privacy evidence |  | “The tested operation processed…” |  |
| It is fast/real-time | Repeated representative workload and threshold |  | “Measured at…” |  |
| It is energy/thermal safe | Long enough physical-device observation |  | “Observed under…” |  |
| It is release-ready | Signed archive/TestFlight/release route |  | “Artifact passed…” |  |

## 7. Release gate

- [ ] Official source and local SDK interface reviewed on the date above.
- [ ] Xcode/Swift/SDK/deployment target recorded.
- [ ] Deterministic fallback works when the native/model route is unavailable.
- [ ] Empty, denied, canceled, interrupted, stale, malformed, and retry states tested.
- [ ] Accessibility, Dynamic Type, reduced motion/transparency, localization, and input paths tested.
- [ ] Performance workload, baseline, threshold, and artifacts retained.
- [ ] Physical-device and system-surface evidence separated from simulator/preview evidence.
- [ ] Privacy manifest, permissions, entitlements, logging, and retention reviewed.
- [ ] Claims are no broader than the strongest evidence row.

## Sources

- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
- [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [MetricManager](https://developer.apple.com/documentation/metrickit/metricmanager)
- [Monitoring app performance with MetricKit](https://developer.apple.com/documentation/metrickit/monitoring-app-performance-with-metrickit)
- [Recording performance data](https://developer.apple.com/documentation/os/recording-performance-data)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

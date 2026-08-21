# Data visualization and chart proof matrix

This matrix closes the gap between “a chart renders” and “the dashboard communicates current, accessible, trustworthy information.” Use it for Swift Charts, custom chart views, chart-backed widgets, and optional AI explanations.

Documentation, a preview, a simulator run, a compile, a physical-device run, a system-surface invocation, and a release artifact answer different questions. Record the smallest evidence that supports the claim and keep unproven claims visible.

## Claim-to-evidence matrix

| Claim | Source or artifact | Test or run | What it proves | What it does not prove |
| --- | --- | --- | --- | --- |
| The chart API is available | Current Charts/SwiftUI documentation and target project | Compile a minimal chart in the named target and deployment target | The selected symbols and signatures compile in that target | Rendering quality, source access, device performance, or every supported OS |
| The chart uses the right visual grammar | Design brief and data contract | Review the user question, mark choice, axes, and units with known fixtures | The visual encoding is intentional and reviewable | That people understand it without task testing |
| Values are accurate | Source adapter, normalization tests, expected fixtures | Test units, time zones, duplicate points, missing values, partial windows, and deterministic aggregates | The projection matches the approved source contract for the fixtures | Source availability, live freshness, or external service correctness |
| Missing data is honest | Empty/partial/stale fixtures | Render each state and inspect labels, summaries, axes, and selection | Unknown, unavailable, and estimated values remain distinguishable | That a service will never return a new failure state |
| Axes and legends are clear | Chart configuration and localized strings | Test ranges, zero baselines, thresholds, series labels, long categories, RTL, and number/date formats | Visual context is present and localized | Universal comprehension or domain-specific interpretation |
| Selection is safe | Selection reducer and UI tests | Select a point/range, cancel, change filters, navigate away, and retry | Selection updates detail without stale-result or hidden-state bugs | Touch comfort or assistive input on physical hardware |
| Exact values are accessible | Chart descriptor, text summary, table/list route | Run VoiceOver, keyboard/full keyboard access, Switch Control, Voice Control, and focus traversal | A person can learn values and context without relying on color or a scrub gesture | Every language, device, or assistive technology without those runs |
| Custom chart semantics are accurate | AXChartDescriptor or AXChartDescriptorRepresentable implementation | Compare title, summary, axes, series, values, and content direction with the deterministic projection | The semantic representation matches the chart | Human comprehension or audio-graph quality without task testing |
| Adaptation works | Preview matrix and UI test configurations | Test compact/regular widths, Dynamic Type, increased contrast, reduced transparency, Reduce Motion, and orientation | Layout changes preserve the same data and action model | Material legibility, performance, or ergonomics on every device |
| Data density is usable | Large-data fixtures and aggregation policy | Exercise maximum expected points, scrolling, filtering, and update cadence | The route has a bounded density strategy | Representative hardware frame time, memory, or thermal behavior |
| The chart is performant | Instrument trace, XCTest performance metric, or MetricKit record | Measure the named workload on a representative physical device/build | The recorded workload and configuration met the measured threshold | All devices, future OS versions, or production-wide reliability |
| AI explanation is grounded | Prompt/schema/model version and projection snapshot | Inject valid, invalid, stale, partial, refusal, unavailable, and citation-mismatch proposals | Invalid or unsupported explanations are rejected and deterministic content survives | Model quality across languages, model updates, or untested domains |
| Privacy is consistent | Permission copy, retention plan, privacy manifest/report, source adapter | Deny/revoke access, switch account, delete source, background/foreground, and inspect logging/export | The chart and explanation follow the approved source/privacy policy | App Store review outcome or unobserved third-party behavior |
| Widget projection is safe | Widget target/configuration and redacted projection | Run the signed widget with stale, deleted, locked, and deep-link states | The system surface can show a bounded, recoverable projection | Refresh timing or ranking in production |
| App Intent route is safe | App Intent/entity/query target and domain use case | Invoke from the app and system surface with current, stale, deleted, unauthorized, and conflicting data | Invocation revalidates current state and preserves authorization | Universal system discovery or every assistant surface |
| Release claim is supported | Archive, privacy report, metadata, signing, TestFlight/App Store evidence | Compare claim wording to the strongest observed run | The packaged artifact and disclosures match the tested scope | Approval, production delivery, or user understanding beyond evidence |

## Fixture suite

Keep a small versioned fixture set for every chart route:

- zero points;
- one point;
- monotonic increase and decrease;
- equal values and ties;
- negative values if the domain permits them;
- duplicate timestamps/categories;
- missing middle interval;
- partial latest interval;
- stale projection;
- estimated value;
- invalid unit or non-finite value;
- many series with long labels;
- maximum expected point count;
- localization and RTL data;
- a selected point and selected range;
- a source revision mismatch;
- a valid AI explanation;
- AI output that invents a value;
- AI output that cites a point from the wrong filter;
- AI refusal/unavailable/context-limit state.

Expected deterministic values should be asserted in unit tests before the view is rendered. Use the same projection fixture for the chart, selected-value summary, table, accessibility descriptor, and AI validation.

## Accessibility task matrix

| Setting or input | Task | Evidence to capture |
| --- | --- | --- |
| VoiceOver | Find the chart, learn the summary, inspect a value, change a filter, and return to the source | Reading order, labels, focus movement, value context, and whether a non-visual route is complete |
| Voice Control | Change the window/series and activate the detail route | Recognizable labels and commands; no gesture-only critical path |
| Switch Control | Navigate to the chart and controls, select a detail, and recover from a stale state | Logical element order, actionable labels, and no unreachable state |
| Full Keyboard Access | Tab through controls, focus the chart/detail route, and invoke actions | Focus visibility/order and keyboard activation |
| Dynamic Type | Read chart title, summary, selected value, and state message at large sizes | No clipped critical text, hidden status, or unusable control |
| Increased contrast/reduced transparency | Read chart, controls, selected state, and status | Data and state remain distinct without relying on glass or subtle color |
| Reduce Motion | Refresh, filter, select, and navigate | State change remains understandable without animation |
| RTL/localization | Read axes, dates, series, and selected details | Direction, formatting, and order remain correct |

An automated accessibility audit is a diagnostic. It is not a substitute for the task matrix.

## Physical-device performance packet

Record:

    app/build:
    Xcode/SDK:
    deployment target:
    device model and OS build:
    locale/appearance/accessibility settings:
    data fixture and point count:
    series count:
    update cadence:
    filter/selection workload:
    cold render time:
    refresh/render time:
    memory:
    hitch or frame-time observations:
    thermal/battery notes:
    observed result:
    unproven scope:

Use the same build and fixture when comparing changes. A simulator chart can validate structure and state branches, but it is not physical-device performance evidence.

## AI grounding packet

For an optional generated explanation, retain a redacted record of:

- projection source revision and point IDs;
- filter/window/unit configuration;
- prompt or context version;
- schema version;
- model availability/version state;
- proposal output and validation result;
- rejected claims and fallback text;
- evaluation case identifiers;
- privacy/retention decision.

Do not log raw private data, full prompts, secrets, health records, or unnecessary media. The chart remains useful if the AI record is omitted.

## Stop conditions

Do not call a chart route ready when:

- the axis unit or time window is unclear;
- missing values are rendered as confirmed zeros;
- a critical value is available only through a gesture;
- color or translucency is the only distinction for important state;
- accessibility text is generated from a different data snapshot;
- the AI explanation cannot be checked against source IDs or filter state;
- the chart is claimed to perform well without a representative workload;
- widget/App Intent behavior is inferred from in-app rendering;
- privacy, permission, account, or source freshness is hidden;
- a release claim is broader than the recorded device/system/artifact evidence.

## Sources

- [Swift Charts](https://developer.apple.com/documentation/charts)
- [Chart view modifiers](https://developer.apple.com/documentation/swiftui/view-chart-view)
- [Charts HIG](https://developer.apple.com/design/human-interface-guidelines/charts)
- [Charting data HIG](https://developer.apple.com/design/human-interface-guidelines/charting-data)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [AXChartDescriptorRepresentable](https://developer.apple.com/documentation/swiftui/axchartdescriptorrepresentable)
- [accessibilityChartDescriptor(_:)](https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor%28_%3A%29)
- [AXChartDescriptor](https://developer.apple.com/documentation/accessibility/axchartdescriptor)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Monitoring app performance with MetricKit](https://developer.apple.com/documentation/metrickit/monitoring-app-performance-with-metrickit)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Privacy manifests](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)

# Swift Charts and data visualization

Swift Charts is the native route for turning app-owned data into readable visualizations in a SwiftUI interface. It is useful for trends, comparisons, distributions, thresholds, and small interactive explorations. It is not a substitute for a domain model, a source-quality contract, or an accessibility description.

This page is a framework route, not a claim that a chart compiles in this documentation workspace. Re-check the selected SDK, deployment target, platform, and current API signatures in Xcode before implementation.

## Smallest native route

Start with a question rather than a mark:

1. Define the decision the chart should help a person make.
2. Normalize the source into stable, app-owned values with units, timestamps, series identity, and provenance.
3. Choose the least complex common chart type that answers the question.
4. Build a Chart from marks and data properties.
5. Make axes, units, legends, selection, empty states, and accessibility part of the feature contract.
6. Keep any generated explanation downstream from the deterministic chart projection.

The minimal composition is SwiftUI plus Charts. The chart can consume local fixtures, SwiftData projections, a service response, a HealthKit query, a device measurement, or a user-imported file. The source adapter owns authorization, freshness, and failure states; the chart owns visualization, not acquisition.

## Capability map

| Need | Native route | Ownership and boundary |
| --- | --- | --- |
| Render a chart | Chart, ChartContent, ChartContentBuilder, and Plot | Compose marks from a normalized data collection. The chart is a view projection, not canonical storage. |
| Choose a visual grammar | BarMark, LineMark, PointMark, AreaMark, RuleMark, RectangleMark, and SectorMark | Match the mark to the question. Do not use a decorative mark when the visual encoding changes the meaning of the data. |
| Express scales and axes | chartXScale, chartYScale, chartXAxis, chartYAxis, and AxisMarks | State units, domain, tick density, and formatting explicitly when automatic choices could mislead. |
| Explain series | foregroundStyle(by:), symbol(by:), legends, annotations, and consistent labels | Color is a supporting encoding. Preserve series meaning in text and accessibility content. |
| Inspect one value | chartXSelection(value:), chartYSelection(value:), or an appropriate chart overlay | Selection is optional exploration. Do not hide critical information behind a scrub gesture. |
| Inspect a range | chartXSelection(range:) or chartYSelection(range:) | Define what range selection means for the domain operation and keep the selected interval visible in text. |
| Browse a dense domain | chartScrollableAxes, visible-domain modifiers, scroll position, and scroll target behavior | Scrolling manages density; it does not replace aggregation, pagination, or a summary. |
| Coordinate custom interaction | chartOverlay, ChartProxy, and chartGesture | Use a larger semantic interaction region when individual marks are hard to target. Keep the gesture cancellable and keyboard/assistive-input friendly. |
| Describe a chart to assistive technology | SwiftUI accessibilityChartDescriptor, AXChartDescriptorRepresentable, AXChart, and AXChartDescriptor | Supply titles, summaries, axes, series, values, and context. A custom rendered chart still needs a truthful descriptor. |
| Add a three-dimensional route | Chart3D and the current 3D chart content types | Treat this as a separate availability, interaction, performance, and accessibility route. Do not assume a 2D proof packet closes it. |

The exact generic constraints and availability of selection, scrolling, 3D, and styling modifiers are SDK-sensitive. Keep an API ledger in the target project with the selected Xcode version, deployment target, and compile result.

## Choosing the chart shape

Use the common visual grammar that communicates the question with the fewest encodings:

| Question | First candidate | Guardrail |
| --- | --- | --- |
| How does a value change over ordered time? | LineMark | Show the time window, sampling policy, and missing intervals. Avoid implying continuity when observations are sparse. |
| Which categories are larger or smaller? | BarMark | Sort deliberately, label the unit, and avoid a truncated axis unless the context makes the comparison honest. |
| Where are individual observations or clusters? | PointMark | Show density and overplotting limits. Consider aggregation or a table for large sets. |
| What is the magnitude across a continuous region? | AreaMark | Explain the baseline and whether overlapping areas represent totals, ranges, or separate series. |
| What is a target, threshold, or reference value? | RuleMark | Label the rule and its unit; do not present a target as an observed measurement. |
| How is a total divided into categories? | SectorMark or a bar composition | Use only when part-to-whole is the actual question and categories remain legible. |
| Where is a value inside a rectangular range? | RectangleMark | Document the two-dimensional encoding and provide a text/table alternative when the plot is dense. |

The HIG recommends focusing a chart on the information that matters for the task. If the person needs exact values, filters, or auditability, pair the visual projection with a list or table rather than forcing the chart to carry every detail.

## Data contract before the view

The chart should receive a small, explicit projection rather than an unbounded framework object:

    struct MetricPoint: Identifiable, Sendable {
        let id: String
        let observedAt: Date
        let value: Double?
        let seriesID: String
        let seriesLabel: String
        let unit: String
        let sourceID: String
        let isEstimated: Bool
    }

    struct ChartProjection: Sendable {
        let title: String
        let summary: String
        let points: [MetricPoint]
        let generatedAt: Date
        let isPartial: Bool
        let dataQualityNote: String?
    }

This is a route sketch, not a compile claim. The important properties are stable identity, explicit units, source references, timestamps, and a representation for unknown or estimated values. Do not convert missing values to zero just to make a mark render.

The adapter that creates ChartProjection should:

- normalize units and time zones;
- define whether duplicate timestamps are retained, merged, or rejected;
- preserve partial and stale state;
- record the source and query/filter revision;
- apply domain-specific validation before the chart;
- provide deterministic fixtures for empty, sparse, invalid, and large data sets.

## Axes, scales, and legends

Automatic axes are useful for a first render, but a production chart needs an explicit review of:

- the x and y units and their localized formatting;
- the visible domain and whether zero is meaningful;
- date/time zone and calendar choices;
- category ordering and label truncation;
- tick density at compact widths;
- thresholds, baselines, and annotations;
- series names that remain meaningful without color;
- whether the selected subset changes the domain or only the highlight.

Use AxisMarks and axis content to control the labels and grid marks when the default presentation does not provide enough context. Keep visible labels concise in compact environments, but make the longer explanation available through the title, supporting text, table, or accessibility descriptor. Never rely on a color legend alone to convey a critical difference.

## Interaction and adaptive Liquid Glass composition

Charts can be visually prominent without becoming a control surface. A useful native composition is:

    NavigationStack
      -> title, date range, and source freshness
      -> chart projection
      -> selected-value summary or table
      -> optional filter/editor controls
      -> optional generated explanation

Place functional controls such as range selection, series toggles, and export actions in standard SwiftUI controls. If a related action cluster benefits from Liquid Glass, group the controls with the appropriate glass container and preserve a clear separation between the chart data and the control layer. Do not put a translucent decorative layer over marks, use glass as the only indication of selection, or make the chart unreadable when transparency is reduced.

Use adaptive layout tools such as ViewThatFits, AnyLayout, and the Layout protocol when the chart and its controls need different arrangements across widths. A compact layout might show one key statistic and a scrubbed chart; a regular-width layout can show the chart, legend, and detail pane together. The data contract stays the same while the projection changes.

Selection should update a textual summary that includes the context a person needs: series, date or category, value, unit, and whether the value is estimated or stale. If a gesture is unavailable, the same information needs an alternate route through focusable controls, a table, or accessibility actions.

## Accessibility contract

Treat accessibility as a semantic chart route, not a last-pass label:

1. Give the chart a concise title and a plain-language summary.
2. Identify each axis, its unit, and its meaningful domain.
3. Describe each series by what it represents, not by its color.
4. Include values with date, category, location, or other context.
5. Keep visible axis/tick labels from duplicating the more useful spoken description where Apple’s accessibility guidance recommends that separation.
6. Provide a readable table, list, or selected-value summary when the chart is dense or interaction-dependent.
7. Test VoiceOver, keyboard/full keyboard access, Switch Control, Voice Control, Dynamic Type, increased contrast, reduced transparency, RTL, and localization.
8. For custom chart views or a route that needs an audio graph, implement an accurate AXChartDescriptor through SwiftUI’s chart accessibility APIs.

Apple’s HIG specifically warns against requiring interaction to reveal critical information. A scrub gesture is an enhancement, not the only way to learn a value. Accessibility descriptions should report actual values and context instead of subjective interpretations such as “rapidly” or “almost.”

## Lifecycle and fallback state machine

Model the chart state separately from the source service and optional AI:

    idle
      -> loading
      -> ready
      -> selected
      -> filtered
      -> refreshing
      -> stale

Failure and empty branches are first-class:

- empty: the query is valid but has no points;
- partial: some source windows or series are missing;
- stale: the chart is usable but its freshness limit has passed;
- invalid: units, timestamps, or values cannot be normalized;
- unavailable: permission, account, service, model, or device state blocks the source;
- tooDense: the selected domain needs aggregation or a narrower window;
- cancelled: a new filter, navigation change, or task replacement superseded the request.

Keep the previous confirmed projection while refreshing when it is safe, and show its age. Do not animate a change that could be misread as a new observation. When a source becomes unavailable, retain the provenance of the last confirmed projection and provide a manual or narrower route if one exists.

## Optional AI explanation route

Use deterministic chart data by default. Add Foundation Models only when a generated explanation creates a user benefit that a small deterministic summary cannot provide.

The safe composition is:

    normalized source values
      -> deterministic chart projection
      -> bounded, versioned context
      -> optional typed explanation proposal
      -> validation against the projection
      -> clearly labeled reviewable explanation

The prompt or context should contain only the data needed to answer the narrow question, including units, time window, filters, partial/stale status, and source revision. The model must not invent a data point, change the selected interval, imply causation, or present a recommendation as a measured fact. Reject or downgrade output that cannot cite the source IDs or that uses unsupported certainty.

Keep the chart and its generated explanation separate in state. A model refusal, unavailable Apple Intelligence environment, language mismatch, context limit, or updated model is not a chart failure; show the deterministic chart and a non-AI summary instead. If the chart represents health, money, safety, or another high-consequence domain, add domain-specific review and claim controls before any generated prose is shown.

## Target, permission, and configuration register

| Gate | Question | Evidence |
| --- | --- | --- |
| Framework | Does the selected iOS 26 SDK expose the Charts and SwiftUI APIs used by this route? | Compile the smallest chart in the named app target and record deployment availability diagnostics. |
| Target membership | Is the chart code in the app, widget, watch, or other target that owns the view? | Inspect target membership and build the intended scheme. |
| Source access | Does the upstream data source require HealthKit, location, network, file, account, or sensor authorization? | Exercise denied, restricted, revoked, stale, and unavailable states with the actual source adapter. |
| Data quality | Are units, timestamps, partial windows, estimates, and source revisions explicit? | Deterministic fixtures plus a source-specific integration run. |
| Accessibility | Is the visual chart paired with a semantic descriptor and alternate exact-value route? | Accessibility task evidence with VoiceOver and alternate input on the named device. |
| System projection | If the chart appears in a widget, App Intent, or other system surface, does that surface own a safe projection? | Signed target, real system invocation, refresh/stale behavior, and privacy-safe content proof. |
| Performance | Is the chosen mark density and update cadence acceptable on representative hardware? | Instrumented workload and physical-device metrics; do not infer from a simulator. |

Swift Charts has no blanket permission to read the data it visualizes. The source capability and the chart projection are separate gates. A chart that renders from a preview fixture proves neither source authorization nor physical-device performance.

## Verification ladder

1. Source check: refresh the Charts, SwiftUI accessibility, and HIG pages for the selected SDK.
2. Compile check: build a minimal Chart with the actual deployment target and target membership.
3. Deterministic data check: exercise known values, empty/partial/stale/invalid states, units, dates, and large collections.
4. UI check: verify navigation, filters, selection, reduced motion, Dynamic Type, compact/regular widths, and deep links.
5. Accessibility check: run the core task with VoiceOver, keyboard/full keyboard access, Switch Control, Voice Control, RTL, and increased contrast.
6. Physical performance check: measure updates, scrolling, memory, thermal behavior, and touch/gesture comfort on the named device.
7. System-surface check: if projected, test the signed widget/App Intent/notification/share route, not just the in-app view.
8. Release check: reconcile privacy, source disclosures, target configuration, signed artifacts, metadata, and the actual claim.

## Common failure patterns

- adding a chart before deciding the user question;
- using a zero for missing data;
- showing a truncated axis without explaining the scale;
- using color as the only series distinction;
- requiring scrubbing to reveal the only exact value;
- feeding raw unnormalized data to a generated explanation;
- presenting an AI interpretation as if it were measured data;
- placing dense chart marks under decorative glass;
- copying a system chart’s visual identity instead of using Apple’s semantic primitives;
- calling a preview or simulator render proof of device performance or assistive-technology task completion.

## Sources

- [Swift Charts](https://developer.apple.com/documentation/charts)
- [Chart](https://developer.apple.com/documentation/charts/chart)
- [Creating a chart using Swift Charts](https://developer.apple.com/documentation/charts/creating-a-chart-using-swift-charts)
- [Visualizing your app’s data](https://developer.apple.com/documentation/charts/visualizing-your-app-s-data)
- [Customizing axes in Swift Charts](https://developer.apple.com/documentation/charts/customizing-axes-in-swift-charts)
- [Chart view modifiers](https://developer.apple.com/documentation/swiftui/view-chart-view)
- [BarMark](https://developer.apple.com/documentation/charts/barmark)
- [LineMark](https://developer.apple.com/documentation/charts/linemark)
- [PointMark](https://developer.apple.com/documentation/charts/pointmark)
- [AreaMark](https://developer.apple.com/documentation/charts/areamark)
- [RuleMark](https://developer.apple.com/documentation/charts/rulemark)
- [AxisMarks](https://developer.apple.com/documentation/charts/axismarks)
- [Charts HIG](https://developer.apple.com/design/human-interface-guidelines/charts)
- [Charting data HIG](https://developer.apple.com/design/human-interface-guidelines/charting-data)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [AXChartDescriptorRepresentable](https://developer.apple.com/documentation/swiftui/axchartdescriptorrepresentable)
- [accessibilityChartDescriptor(_:)](https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor%28_%3A%29)
- [AXChartDescriptor](https://developer.apple.com/documentation/accessibility/axchartdescriptor)
- [Representing chart data as an audio graph](https://developer.apple.com/documentation/accessibility/representing-chart-data-as-an-audio-graph)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)

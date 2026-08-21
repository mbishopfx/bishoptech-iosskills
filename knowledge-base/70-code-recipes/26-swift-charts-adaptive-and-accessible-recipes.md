# Swift Charts: adaptive and accessible route recipes

These are compile-oriented Swift route sketches for a chart-backed SwiftUI screen. They are intentionally small and uncompiled in this documentation-only workspace. Confirm the selected SDK signatures, deployment availability, target membership, and source permissions in the real Xcode project.

## Recipe 1: Keep chart data app-owned

Use a normalized projection so the chart, text summary, table, accessibility descriptor, and optional AI context all read the same values.

    import Charts
    import SwiftUI

    struct ChartPoint: Identifiable, Sendable {
        let id: String
        let date: Date
        let value: Double?
        let series: String
        let unit: String
        let sourceID: String
        let isEstimated: Bool
    }

    struct ChartState: Sendable {
        let title: String
        let points: [ChartPoint]
        let isPartial: Bool
        let isStale: Bool
        let qualityNote: String?
    }

Do not replace a missing value with zero. Normalize units and time zones before the view, and attach a source revision when the upstream data can change.

## Recipe 2: Render a deterministic line chart

    struct TrendChart: View {
        let state: ChartState

        var body: some View {
            Chart(state.points) { point in
                if let value = point.value {
                    LineMark(
                        x: .value("Date", point.date),
                        y: .value(point.unit, value)
                    )
                    .foregroundStyle(by: .value("Series", point.series))
                    .symbol(by: .value("Series", point.series))
                }
            }
            .chartXAxis {
                AxisMarks(format: .dateTime.month().day())
            }
            .chartYAxis {
                AxisMarks()
            }
            .accessibilityLabel(state.title)
        }
    }

The exact axis initializer and formatting overload must be checked against the selected SDK. Add a text summary and an explicit chart descriptor for a production accessibility route; a label alone is not a complete chart description.

## Recipe 3: Use mark types intentionally

    Chart(categoryValues) { item in
        BarMark(
            x: .value("Category", item.category),
            y: .value("Count", item.count)
        )
    }

    Chart(observations) { item in
        PointMark(
            x: .value("Time", item.date),
            y: .value("Value", item.value)
        )
    }

    Chart(observations) { item in
        RuleMark(y: .value("Target", item.target))
            .annotation(position: .overlay) {
                Text("Target")
            }
    }

Use one visual grammar per question. A rule is a reference, not an observation. A bar is not automatically a time series. If multiple marks share a plot, document their units and reading order.

## Recipe 4: Add selected-value detail

Selection should update app-owned detail state and a visible textual summary.

    struct SelectableTrend: View {
        let points: [ChartPoint]
        @State private var selectedDate: Date?

        var body: some View {
            VStack(alignment: .leading) {
                Chart(points) { point in
                    if let value = point.value {
                        LineMark(
                            x: .value("Date", point.date),
                            y: .value(point.unit, value)
                        )
                    }
                }
                .chartXSelection(value: $selectedDate)

                if let selectedDate {
                    Text(detailText(for: selectedDate))
                        .accessibilityAddTraits(.updatesFrequently)
                } else {
                    Text("Select a date to inspect its value.")
                }
            }
        }

        func detailText(for date: Date) -> String {
            "Selected date: " + date.formatted(date: .abbreviated, time: .omitted)
        }
    }

The selection API is generic over a Plottable value and the exact binding type must match the x-axis. Resolve the selected point from the normalized projection, not from a second query. Provide a keyboard, VoiceOver, Switch Control, or table route that does not depend on touch scrubbing.

## Recipe 5: Use a range selection only when the domain supports it

    struct RangeSelectionChart: View {
        let points: [ChartPoint]
        @State private var selectedRange: ClosedRange<Date>?

        var body: some View {
            Chart(points) { point in
                if let value = point.value {
                    AreaMark(
                        x: .value("Date", point.date),
                        y: .value(point.unit, value)
                    )
                }
            }
            .chartXSelection(range: $selectedRange)
        }
    }

The range must have a clear product meaning, such as recomputing a deterministic summary for the selected window. Show the selected interval and summary in text, and revalidate any action that uses the selection.

## Recipe 6: Make a dense chart scrollable and bounded

    Chart(densePoints) { point in
        if let value = point.value {
            LineMark(
                x: .value("Date", point.date),
                y: .value("Value", value)
            )
        }
    }
    .chartScrollableAxes(.horizontal)
    .chartXVisibleDomain(length: 7 * 24 * 60 * 60)

This is a sketch only. Choose an aggregation or gap policy first, then apply a visible-domain and scrolling strategy. Test scroll performance, selection, Dynamic Type, and alternate input on the named device.

## Recipe 7: Provide a semantic chart descriptor

For a custom rendered chart or a route that needs an audio graph, provide a type conforming to AXChartDescriptorRepresentable and attach it with accessibilityChartDescriptor.

    struct MetricDescriptor: AXChartDescriptorRepresentable {
        let state: ChartState

        func makeChartDescriptor() -> AXChartDescriptor {
            let xAxis = AXCategoricalDataAxisDescriptor(
                title: "Date",
                categoryOrder: state.points.map { $0.date.formatted(date: .abbreviated, time: .omitted) }
            )
            let yAxis = AXNumericDataAxisDescriptor(
                title: state.points.first?.unit ?? "Value",
                range: 0...100,
                gridlinePositions: [],
                valueDescriptionProvider: { value in
                    String(value)
                }
            )
            let series = AXDataSeriesDescriptor(
                name: state.title,
                isContinuous: true,
                dataPoints: []
            )
            return AXChartDescriptor(
                title: state.title,
                summary: state.qualityNote ?? "Chart data",
                xAxis: xAxis,
                yAxis: yAxis,
                additionalAxes: [],
                series: [series]
            )
        }

        func updateChartDescriptor(_ descriptor: AXChartDescriptor) {
            // Rebuild or update values from the same projection revision.
        }
    }

    TrendChart(state: state)
        .accessibilityChartDescriptor(MetricDescriptor(state: state))

The descriptor initializer and data-axis types are SDK-sensitive. The example intentionally leaves data-point construction incomplete: implement it from the same normalized state, including actual values, dates/categories, units, series identity, content direction, and a truthful summary. Do not ship an empty or generic descriptor.

## Recipe 8: Adapt the surrounding layout

Keep the chart projection stable and change only the arrangement.

    struct AdaptiveDashboard: View {
        let chart: AnyView
        let detail: AnyView

        var body: some View {
            ViewThatFits(in: .horizontal) {
                HStack(alignment: .top) {
                    chart
                    detail
                }

                VStack(alignment: .leading) {
                    chart
                    detail
                }
            }
        }
    }

In a real target, prefer concrete view types or a dedicated Layout when type erasure is unnecessary. Verify that compact width does not remove the question, units, freshness, selected value, or recovery action.

## Recipe 9: Keep optional AI explanation downstream

    struct ExplanationProposal: Sendable {
        let headline: String
        let observations: [String]
        let citedPointIDs: [String]
        let uncertaintyNote: String?
    }

    enum ValidationError: Error {
        case unknownSourcePoint
    }

    func validate(
        _ proposal: ExplanationProposal,
        against state: ChartState
    ) -> Result<ExplanationProposal, ValidationError> {
        let knownIDs = Set(state.points.map(\.id))
        guard proposal.citedPointIDs.allSatisfy(knownIDs.contains) else {
            return .failure(.unknownSourcePoint)
        }
        return .success(proposal)
    }

The model may propose prose; the validator decides whether the proposal can be displayed. Keep model availability, prompt/schema version, source revision, and fallback state in the feature state. Do not let a tool or generated explanation mutate the domain directly.

## Recipe 10: Build fixtures before connecting a source

    let fixtures: [ChartState] = [
        ChartState(
            title: "Empty",
            points: [],
            isPartial: false,
            isStale: false,
            qualityNote: "No observations in this window."
        ),
        ChartState(
            title: "Partial and stale",
            points: samplePoints,
            isPartial: true,
            isStale: true,
            qualityNote: "The latest interval is incomplete."
        )
    ]

Use fixed fixtures for preview, unit, UI, accessibility, and AI-validation tests. Add cases for non-finite values, missing middle points, long labels, many series, localization, RTL, large point counts, selection cancellation, and source revision mismatch.

## Compile and proof checklist

- import Charts in the intended app, widget, watch, or other target;
- confirm every mark, axis, selection, scrolling, descriptor, and adaptive-layout signature in the selected SDK;
- verify deployment availability and any conditional route;
- keep source permissions and account state in the adapter, not in the chart view;
- test empty, partial, stale, unavailable, invalid, and cancelled states;
- test VoiceOver, Voice Control, Switch Control, keyboard, Dynamic Type, contrast, reduced transparency, Reduce Motion, and RTL;
- run the maximum expected data workload on a representative physical device;
- if projected to a widget or App Intent, test the signed system surface and revalidation route;
- record exactly what the compile, simulator, physical-device, system, and release artifacts prove.

## Sources

- [Swift Charts](https://developer.apple.com/documentation/charts)
- [Chart](https://developer.apple.com/documentation/charts/chart)
- [BarMark](https://developer.apple.com/documentation/charts/barmark)
- [LineMark](https://developer.apple.com/documentation/charts/linemark)
- [PointMark](https://developer.apple.com/documentation/charts/pointmark)
- [AreaMark](https://developer.apple.com/documentation/charts/areamark)
- [RuleMark](https://developer.apple.com/documentation/charts/rulemark)
- [AxisMarks](https://developer.apple.com/documentation/charts/axismarks)
- [Chart view modifiers](https://developer.apple.com/documentation/swiftui/view-chart-view)
- [chartXSelection(value:)](https://developer.apple.com/documentation/swiftui/view/chartxselection%28value%3A%29)
- [chartXSelection(range:)](https://developer.apple.com/documentation/swiftui/view/chartxselection%28range%3A%29)
- [ChartProxy](https://developer.apple.com/documentation/charts/chartproxy)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [AXChartDescriptorRepresentable](https://developer.apple.com/documentation/swiftui/axchartdescriptorrepresentable)
- [accessibilityChartDescriptor(_:)](https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor%28_%3A%29)
- [AXChartDescriptor](https://developer.apple.com/documentation/accessibility/axchartdescriptor)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [Charts HIG](https://developer.apple.com/design/human-interface-guidelines/charts)
- [Charting data HIG](https://developer.apple.com/design/human-interface-guidelines/charting-data)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)

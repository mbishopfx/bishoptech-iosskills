# Adaptive insight dashboard

This recipe turns a source of time-series or categorical values into an adaptive SwiftUI dashboard with a truthful Swift Chart, accessible exact-value routes, and an optional on-device explanation. It is useful for personal metrics, device status, project progress, local-first records, or other domains where a person needs to notice a pattern and decide what to do next.

It is a composable route, not a compiled template. Select a named target, deployment target, source capability, and evidence plan before implementation.

## Outcome

> A person can inspect a current, partial, or stale data set; understand the key values without relying on color or gestures; filter the view; and optionally ask for a bounded explanation that is visibly grounded in the same data.

The chart is a projection. The domain record, source authorization, and any action taken after the insight remain separate.

## Route map

    source adapter
      -> normalized metric projection
      -> deterministic validation and aggregation
      -> Swift Charts view
      -> selected-value/table route
      -> optional Foundation Models explanation
      -> reviewable action or read-only system projection

Possible source adapters include:

- SwiftData records for a private local-first utility;
- a network response with explicit freshness and retry state;
- HealthKit data after staged authorization and domain review;
- location or weather observations with timestamp and attribution;
- device or media measurements with a physical-hardware proof packet;
- imported files or user-entered values with a visible source reference.

Do not add an AI layer when a deterministic total, delta, average, threshold, or trend label answers the question more clearly.

## Responsibility matrix

| Layer | Owns | Must not own |
| --- | --- | --- |
| Source adapter | Authorization, query, cancellation, freshness, source errors, raw-to-app mapping | Chart layout or generated explanations. |
| Normalizer | Units, time zones, stable IDs, source references, partial/estimated flags | Approval or irreversible domain actions. |
| Deterministic analytics | Aggregation, threshold comparisons, deltas, selected interval, quality notes | Inventing missing values or claiming causation. |
| Swift Charts view | Marks, axes, legends, selection, scrolling, adaptive layout, explicit states | Fetching protected data or deciding domain truth. |
| Accessibility route | Chart descriptor, summary, exact-value table/list, focus order, alternate input | Duplicating visual-only color meanings. |
| Foundation Models adapter | Bounded explanation proposal, typed output, model availability/fallback | Mutating the domain or silently changing the data. |
| Domain action | Authorization, revalidation, idempotency, commit, audit trail | Trusting an unvalidated model string. |
| Widget/App Intent projection | Redacted current projection, deep link, stale state, refresh | Owning the canonical dashboard state. |

## Data contract

Use one projection for chart, text summary, accessibility, and AI context so the surfaces cannot silently disagree:

    struct DashboardPoint: Identifiable, Sendable {
        let id: String
        let date: Date
        let value: Double?
        let series: String
        let unit: String
        let sourceID: String
        let quality: DataQuality
    }

    enum DataQuality: Sendable {
        case confirmed
        case estimated
        case partial
        case stale
        case unavailable
    }

    struct DashboardProjection: Sendable {
        let title: String
        let question: String
        let points: [DashboardPoint]
        let summary: String
        let window: DateInterval
        let filterRevision: String
        let generatedAt: Date
        let sourceRevision: String
        let isPartial: Bool
    }

The type names are illustrative. The durable contract is that every displayed or explained value has a source, unit, time/window, and quality state. A missing observation remains missing; it is never coerced to zero for convenience.

## Build the deterministic projection first

Before adding any model call:

1. Define the user question and the data window.
2. Normalize values and units.
3. Decide how duplicate, missing, estimated, and outlier values are represented.
4. Compute deterministic summary values such as latest, minimum, maximum, delta, or threshold status.
5. Choose a common mark type.
6. Render loading, empty, partial, stale, unavailable, and invalid states.
7. Add a table/list or selected-value summary for exact inspection.
8. Test with fixed fixtures whose expected values are known.

This order makes the dashboard useful when the network, protected data source, model, or system surface is unavailable.

## Native screen composition

Use a semantic screen rather than a full-screen visual effect:

    NavigationStack
      -> title and source freshness
      -> time-window / series controls
      -> chart card or chart section
      -> selected value and deterministic summary
      -> table/details route
      -> optional explanation section
      -> action or export route

For wide layouts, use AnyLayout, ViewThatFits, or a custom Layout to choose between a chart-plus-detail arrangement and a stacked arrangement. Keep the same DashboardProjection in both. A compact layout can reduce visible series or show a one-value summary, but it must explain the filter and offer a route to the full data.

Use standard SwiftUI controls for filters, date ranges, and actions. A small functional Liquid Glass group can hold related controls if the group remains legible and does not cover the plot. The chart itself should remain readable with increased contrast, reduced transparency, and assistive technology settings.

## Optional on-device explanation

A safe Foundation Models route is:

    DashboardProjection
      -> select only the requested window and series
      -> serialize values with units and quality
      -> ask for a typed explanation proposal
      -> validate every claim against the projection
      -> show as labeled, dismissible, reviewable text

The proposal schema should be narrow. For example:

    struct ExplanationProposal: Sendable {
        let headline: String
        let observations: [String]
        let citedPointIDs: [String]
        let uncertaintyNote: String?
        let suggestedNextStep: String?
    }

The model should not be allowed to:

- create values not present in the projection;
- change the date range or filters;
- infer a cause that the data does not support;
- convert estimates or stale values into confirmed facts;
- perform a domain mutation;
- expose private source content beyond the intended audience;
- generate a high-consequence recommendation without domain-specific review.

If the model is unavailable, refuses, exceeds context, or returns an invalid proposal, keep the deterministic chart and show a concise non-AI summary. Treat model availability, model version, prompt version, and evaluation results as part of the feature record.

## System projections

Add system surfaces only after the in-app route is useful:

| Surface | Appropriate projection | Guardrail |
| --- | --- | --- |
| WidgetKit | Current summary, small chart, timestamp, and deep link | Timeline data can be stale; do not assume a widget is a live app process. |
| App Intents/App Shortcuts | Read current dashboard state or apply a narrow authorized filter | Resolve current state at invocation and keep mutations in the domain use case. |
| Spotlight/AppEntity | Searchable redacted record or dashboard entity | Index stable IDs and remove/update projections on deletion or account change. |
| ShareLink/Transferable | User-selected confirmed summary or export | Do not share unreviewed generated text or private source data by default. |
| Live Activity | Only when there is a genuine time-bounded live event | A dashboard that is merely current does not automatically justify a Live Activity. |

Each projection needs its own target membership, privacy, stale/error, deep-link, and signed-system-surface evidence.

## Accessibility and localization

The dashboard should remain understandable when the plot is unavailable:

- put the question, unit, and time window in visible text;
- use a textual summary of the key deterministic values;
- provide a list/table or selected-value route for exact inspection;
- add an accurate accessibilityChartDescriptor for the chart;
- identify series by meaning, not color;
- use localized dates, numbers, units, pluralization, and time zones;
- test long labels, RTL, Dynamic Type, increased contrast, reduced transparency, Reduce Motion, VoiceOver, Voice Control, Switch Control, keyboard, and pointer input;
- make filter state and stale/partial status programmatically discoverable.

Do not let an AI-written paragraph become the only accessible description. The source-backed chart summary must still work.

## State and recovery

Recommended state branches:

    idle
      -> loading
      -> ready
      -> filtered
      -> selected
      -> explaining
      -> explanationReady
      -> stale

Recovery states:

| State | Preserve | Offer |
| --- | --- | --- |
| Loading | Previous confirmed projection when safe | Progress and cancellation. |
| Empty | Query/filter context | Explain why there is no data and how to change the window/source. |
| Partial | Available values and missing-window note | Narrow the window, retry, or inspect the source. |
| Stale | Values, timestamp, and source revision | Refresh, keep reading, or switch to a manual route. |
| Source denied/unavailable | Goal and last confirmed values | Permission/settings/manual/import route. |
| Explanation unavailable | Deterministic chart and summary | Continue without AI. |
| Action rejected/conflicted | Projection and current domain state | Revalidate, review, retry, or cancel. |

Do not clear a useful confirmed chart merely because a refresh or explanation task failed.

## Evidence packet

| Claim | Minimum evidence |
| --- | --- |
| The chart route is available | Official source refresh and a compile in the named target/deployment target. |
| The values are correct | Deterministic fixtures, unit/time-zone tests, source adapter integration, and known expected summaries. |
| The chart is accessible | VoiceOver and alternate-input task evidence, descriptor review, Dynamic Type/RTL/contrast/reduced-effects runs. |
| The dashboard adapts | Compact and regular width UI tests plus a physical-device ergonomics check. |
| The explanation is grounded | Typed proposal fixtures, invalid/citation-mismatch rejection, model availability/refusal fallback, and evaluation records. |
| The source is private and current | Permission/revocation/account tests, retention/deletion behavior, freshness display, and privacy review. |
| The widget/App Intent route works | Signed target and real system-surface invocation with stale/deep-link/revalidation evidence. |
| The dashboard performs acceptably | Representative data-size workload, memory/update/scroll measurements, and named physical-device run. |

## Variants

- Local-first progress dashboard: SwiftData records, deterministic aggregates, Swift Charts, optional Foundation Models summary, and no network dependency.
- Sensor trend dashboard: device input adapter, bounded sampling, explicit backpressure, physical-device capture proof, and chart projection.
- Reviewable health dashboard: HealthKit authorization/query route, privacy-aware source labels, domain-specific review, and no medical claims from a chart or model.
- Project or work dashboard: local/network source, account scope, stale/partial synchronization state, App Intent read route, and export of confirmed values.

These are variations on the same boundary, not evidence that any source, model, or system surface is available in a target.

## Sources

- [Swift Charts](https://developer.apple.com/documentation/charts)
- [Creating a chart using Swift Charts](https://developer.apple.com/documentation/charts/creating-a-chart-using-swift-charts)
- [Chart view modifiers](https://developer.apple.com/documentation/swiftui/view-chart-view)
- [Charts HIG](https://developer.apple.com/design/human-interface-guidelines/charts)
- [Charting data HIG](https://developer.apple.com/design/human-interface-guidelines/charting-data)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [accessibilityChartDescriptor(_:)](https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor%28_%3A%29)
- [AXChartDescriptor](https://developer.apple.com/documentation/accessibility/axchartdescriptor)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)

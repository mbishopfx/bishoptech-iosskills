# Family Controls and Device Activity recipes

These route sketches show target seams and state boundaries. They are not claimed to compile in this workspace. Confirm the selected SDK’s exact initializer labels, availability, extension point, actor annotations, entitlement, and distribution status in Xcode.

The code should preserve this split:

    AuthorizationCenter -> opaque selection -> validated policy
    DeviceActivityCenter -> extension callback -> ManagedSettings
    DeviceActivityReport -> report extension -> privacy-preserving View
    App-owned AI proposal -> human approval -> deterministic side effect

Never treat a local Timer, a cached authorization flag, a successful function call, or a preview as proof that the system is enforcing a policy.

## Recipe 1: observe authorization as state

Keep authorization in an observable object owned by the main app. The current AuthorizationCenter API includes async authorization and an authorizationStatus property; check the selected SDK for the exact enum cases.

~~~swift
import FamilyControls

@MainActor
final class FamilyControlsGate: ObservableObject {
    private let center = AuthorizationCenter.shared

    @Published private(set) var statusDescription = "unknown"
    @Published private(set) var lastError: String?

    func refresh() {
        statusDescription = String(describing: center.authorizationStatus)
    }

    func requestIndividualAuthorization() async {
        do {
            try await center.requestAuthorization(for: .individual)
            lastError = nil
        } catch {
            lastError = String(describing: error)
        }
        refresh()
    }

    func revoke() {
        // Verify the current completion-handler or async revocation API.
        center.revokeAuthorization { [weak self] result in
            Task { @MainActor in
                if case .failure(let error) = result {
                    self?.lastError = String(describing: error)
                }
                self?.refresh()
            }
        }
    }
}
~~~

For a child/guardian route, use the current FamilyControlsMember case and test the supported Family Sharing configuration. Do not hard-code “approved” as the only success state; preserve the framework’s current status.

## Recipe 2: present FamilyActivityPicker

Let the system-owned picker produce an opaque FamilyActivitySelection. Keep the picker flow separate from the policy editor.

~~~swift
import FamilyControls
import SwiftUI

struct ActivityScopePicker: View {
    @Binding var selection: FamilyActivitySelection
    @State private var isPresented = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Selected scope")
            Text("\(selection.applicationTokens.count) apps/categories/domains selected")
                .foregroundStyle(.secondary)

            Button("Choose apps and websites") {
                isPresented = true
            }
        }
        .familyActivityPicker(
            isPresented: $isPresented,
            selection: $selection
        )
    }
}
~~~

Confirm whether the selected SDK exposes the picker as a modifier or initializer and whether the target requires a specific platform availability check. Do not log selection token values or derive readable identities from them.

## Recipe 3: persist a redacted selection record

Store policy metadata and a selection version, not a token dump in analytics.

~~~swift
struct ActivityScopeRecord: Codable, Sendable {
    var id: UUID
    var selectionVersion: Int
    var selectedApplicationCount: Int
    var selectedCategoryCount: Int
    var selectedWebDomainCount: Int
    var authorizationObservation: String
    var updatedAt: Date
}

func makeScopeRecord(
    id: UUID,
    selection: FamilyActivitySelection,
    authorization: String,
    now: Date
) -> ActivityScopeRecord {
    ActivityScopeRecord(
        id: id,
        selectionVersion: 1,
        selectedApplicationCount: selection.applicationTokens.count,
        selectedCategoryCount: selection.categoryTokens.count,
        selectedWebDomainCount: selection.webDomainTokens.count,
        authorizationObservation: authorization,
        updatedAt: now
    )
}
~~~

Keep the actual selection in the narrowest app-owned store required for the framework operation. If a selection becomes invalid after revocation, clear it or mark it unusable instead of presenting it as active.

## Recipe 4: validate a schedule before submission

Use pure validation before constructing Device Activity framework values.

~~~swift
struct FocusScheduleDraft: Codable, Hashable, Sendable {
    var name: String
    var startHour: Int
    var startMinute: Int
    var endHour: Int
    var endMinute: Int
    var repeats: Bool
    var warningMinutes: Int?
    var thresholdMinutes: Int?
}

struct ScheduleValidation: Sendable {
    var errors: [String] = []
    var warnings: [String] = []

    var isValid: Bool { errors.isEmpty }
}

func validate(_ draft: FocusScheduleDraft) -> ScheduleValidation {
    var result = ScheduleValidation()

    guard (0...23).contains(draft.startHour),
          (0...59).contains(draft.startMinute),
          (0...23).contains(draft.endHour),
          (0...59).contains(draft.endMinute) else {
        result.errors.append("Use valid local time components.")
        return result
    }

    if draft.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        result.errors.append("Add a stable activity name.")
    }
    if let warningMinutes = draft.warningMinutes, warningMinutes < 0 {
        result.errors.append("Warning time cannot be negative.")
    }
    if let thresholdMinutes = draft.thresholdMinutes, thresholdMinutes <= 0 {
        result.errors.append("Threshold must be positive.")
    }
    if !draft.repeats {
        result.warnings.append("Confirm the one-time schedule behavior.")
    }

    return result
}
~~~

Handle overnight and daylight-saving behavior explicitly in product copy. DateComponents are not a duration calculator.

## Recipe 5: create a DeviceActivity schedule and event

The initializers below are an adapter checkpoint. Verify the current SDK labels and allowed token sets.

~~~swift
import DeviceActivity
import FamilyControls

enum DeviceActivityAdapterError: Error {
    case invalidSchedule([String])
    case emptySelection
}

func makeSchedule(
    from draft: FocusScheduleDraft
) throws -> DeviceActivitySchedule {
    let validation = validate(draft)
    guard validation.isValid else {
        throw DeviceActivityAdapterError.invalidSchedule(validation.errors)
    }

    let start = DateComponents(
        hour: draft.startHour,
        minute: draft.startMinute
    )
    let end = DateComponents(
        hour: draft.endHour,
        minute: draft.endMinute
    )
    let warning = draft.warningMinutes.map {
        DateComponents(minute: $0)
    }

    return DeviceActivitySchedule(
        intervalStart: start,
        intervalEnd: end,
        repeats: draft.repeats,
        warningTime: warning
    )
}

func makeThresholdEvent(
    selection: FamilyActivitySelection,
    minutes: Int
) throws -> DeviceActivityEvent {
    guard !selection.applicationTokens.isEmpty
            || !selection.categoryTokens.isEmpty
            || !selection.webDomainTokens.isEmpty else {
        throw DeviceActivityAdapterError.emptySelection
    }

    // Confirm the current initializer and threshold measurement.
    return DeviceActivityEvent(
        applications: selection.applicationTokens,
        categories: selection.categoryTokens,
        webDomains: selection.webDomainTokens,
        threshold: DateComponents(minute: minutes)
    )
}
~~~

Create a stable DeviceActivityName for each policy. Do not generate a new name every time the user edits a schedule or reconciliation becomes impossible.

## Recipe 6: start, stop, and reconcile monitoring

The center call is not the final state. Re-read activities and schedule after submission.

~~~swift
import DeviceActivity

struct MonitorObservation: Sendable {
    var name: String
    var state: String
    var observedAt: Date
    var errorDescription: String?
}

func startMonitoring(
    name: DeviceActivityName,
    schedule: DeviceActivitySchedule,
    events: [DeviceActivityEvent.Name: DeviceActivityEvent]
) throws -> MonitorObservation {
    let center = DeviceActivityCenter()

    do {
        try center.startMonitoring(name, during: schedule, events: events)
        let observed = center.activities.contains(name)
        return MonitorObservation(
            name: String(describing: name),
            state: observed ? "observed" : "submitted-not-observed",
            observedAt: Date(),
            errorDescription: nil
        )
    } catch {
        return MonitorObservation(
            name: String(describing: name),
            state: "failed",
            observedAt: Date(),
            errorDescription: String(describing: error)
        )
    }
}

func stopMonitoring(_ names: [DeviceActivityName]) {
    DeviceActivityCenter().stopMonitoring(names)
}
~~~

If the current SDK exposes a different collection shape for activities, keep that detail inside an adapter. The product state should still distinguish submitted, observed, missing, and failed.

## Recipe 7: monitor extension applies a narrow policy

The monitor extension should perform a short, deterministic action. The main app does not need to be open for the extension to receive a callback.

~~~swift
import DeviceActivity
import ManagedSettings

final class FocusMonitorExtension: DeviceActivityMonitor {
    private let store = ManagedSettingsStore(named: .init("focus-policy"))

    override func intervalDidStart(for activity: DeviceActivityName) {
        super.intervalDidStart(for: activity)
        applyCurrentPolicy(for: activity)
    }

    override func intervalDidEnd(for activity: DeviceActivityName) {
        super.intervalDidEnd(for: activity)
        clearCurrentPolicy(for: activity)
    }

    override func eventDidReachThreshold(
        _ event: DeviceActivityEvent.Name,
        activity: DeviceActivityName
    ) {
        super.eventDidReachThreshold(event, activity: activity)
        applyCurrentPolicy(for: activity)
    }

    private func applyCurrentPolicy(for activity: DeviceActivityName) {
        // Read a small versioned policy record from the App Group.
        // Validate expiry and authorization observation.
        // Assign only the approved application/category/domain tokens.
    }

    private func clearCurrentPolicy(for activity: DeviceActivityName) {
        // Set only this feature’s settings to nil, write a redacted result,
        // and return quickly.
    }
}
~~~

Keep all callbacks idempotent. If an interval-start callback arrives twice, the second application should produce the same effective request.

## Recipe 8: apply and clear Managed Settings

Keep the desired policy and the system’s effective result separate.

~~~swift
import FamilyControls
import ManagedSettings

struct ShieldPolicy {
    var applications: Set<ApplicationToken>
    var categories: Set<ActivityCategoryToken>
    var webDomains: Set<WebDomainToken>
}

func apply(_ policy: ShieldPolicy, to store: ManagedSettingsStore) {
    store.shield.applications = policy.applications.isEmpty
        ? nil
        : policy.applications

    store.shield.webDomains = policy.webDomains.isEmpty
        ? nil
        : policy.webDomains

    if policy.categories.isEmpty {
        store.shield.applicationCategories = nil
        store.shield.webDomainCategories = nil
    } else {
        // Confirm the current ActivityCategoryPolicy initializer and whether
        // the policy should apply to applications, web domains, or both.
    }
}

func clearOwnedPolicy(from store: ManagedSettingsStore) {
    store.shield.applications = nil
    store.shield.webDomains = nil
    store.shield.applicationCategories = nil
    store.shield.webDomainCategories = nil
}
~~~

The system can combine settings from multiple sources. A clear call proves that this store removed its configuration, not that every restriction on the device disappeared.

## Recipe 9: customize a shield quickly

Shield configuration runs in a system extension. Keep the return value static and fast.

~~~swift
import ManagedSettings
import ManagedSettingsUI

final class ShieldConfigurationExtension:
    ShieldConfigurationDataSource {

    override func configuration(
        shielding application: Application
    ) -> ShieldConfiguration {
        ShieldConfiguration(
            backgroundBlurStyle: .systemMaterial,
            backgroundColor: nil,
            icon: nil,
            title: .init(text: "Focus time"),
            subtitle: .init(text: "This app is unavailable during the schedule."),
            primaryButtonLabel: .init(text: "Return"),
            primaryButtonBackgroundColor: nil,
            secondaryButtonLabel: .init(text: "Ask for more time")
        )
    }
}
~~~

Confirm the current ShieldConfiguration initializer, UIKit availability, and extension target. Add analogous methods for web domains and categories only when the product needs them. Provide a safe default when a configuration is omitted or the extension does not respond quickly.

## Recipe 10: handle a shield action without readable identity

The action extension receives an opaque token. Record a short-lived request rather than attempting to identify it.

~~~swift
import ManagedSettings

final class ShieldActionExtension: ShieldActionDelegate {
    override func handle(
        action: ShieldAction,
        for application: ApplicationToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        let command = ShieldCommand(
            id: UUID(),
            action: String(describing: action),
            expiresAt: Date().addingTimeInterval(300)
        )

        // Store only the command ID/action/expiry in the App Group.
        // The main app can later ask the person for a policy decision.
        save(command)
        completionHandler(.defer)
    }
}
~~~

Verify the current ShieldActionResponse cases and the appropriate response for the product. Implement the equivalent handlers for ActivityCategoryToken and WebDomainToken if the policy can shield those scopes.

## Recipe 11: host a Device Activity report

Keep the context and filter user-selectable and make the report extension the owner of the report view.

~~~swift
import DeviceActivity
import FamilyControls
import SwiftUI

extension DeviceActivityReport.Context {
    static let focusBarGraph = Self("focus-bar-graph")
    static let focusSummary = Self("focus-summary")
}

struct FocusReportHost: View {
    let selection: FamilyActivitySelection
    @State private var context = DeviceActivityReport.Context.focusBarGraph
    @State private var filter: DeviceActivityFilter

    init(selection: FamilyActivitySelection) {
        self.selection = selection
        _filter = State(initialValue: DeviceActivityFilter(
            segment: .daily(
                during: Calendar.current.dateInterval(
                    of: .weekOfYear,
                    for: .now
                )!
            ),
            users: .all,
            devices: .init([.iPhone, .iPad]),
            applications: selection.applicationTokens,
            categories: selection.categoryTokens,
            webDomains: selection.webDomainTokens
        ))
    }

    var body: some View {
        VStack {
            DeviceActivityReport(context, filter: filter)
            Picker("Report", selection: $context) {
                Text("Bar graph")
                    .tag(DeviceActivityReport.Context.focusBarGraph)
                Text("Summary")
                    .tag(DeviceActivityReport.Context.focusSummary)
            }
        }
    }
}
~~~

Confirm the current DeviceActivityFilter member/device cases, report initializer, and extension scene contract. If no report data is available, the report view must say so rather than draw a zero-valued chart.

## Recipe 12: implement a report extension scene

The report extension is given privacy-preserving data by the system. It should render a view without a network.

~~~swift
import DeviceActivity
import SwiftUI

struct FocusReportScene: DeviceActivityReportScene {
    let context: DeviceActivityReport.Context

    func makeConfiguration(
        representing data: DeviceActivityResults<DeviceActivityData>
    ) async -> FocusReportConfiguration {
        // Aggregate only the values needed by this context. Keep exact
        // units, time range, and missing-data state in the configuration.
        FocusReportConfiguration(
            totalDuration: .zero,
            segments: [],
            isPartial: false
        )
    }

    var body: some View {
        FocusReportView()
    }
}

struct FocusReportExtension: DeviceActivityReportExtension {
    var body: some DeviceActivityReportScene {
        FocusReportScene(context: .focusBarGraph)
        FocusReportScene(context: .focusSummary)
    }
}
~~~

The exact generic and scene-body signatures are SDK-sensitive. Keep all report aggregation inside the extension and test it with a deterministic fixture or the current Device Activity report sample.

## Recipe 13: typed AI schedule proposal

The model proposes date components and policy language; deterministic code owns side effects.

~~~swift
struct FocusPolicyProposal: Codable, Hashable, Sendable {
    var title: String
    var startHour: Int
    var endHour: Int
    var repeats: Bool
    var warningMinutes: Int?
    var effect: String
    var assumptions: [String]
    var modelIdentifier: String
}

struct PolicyReview: Sendable {
    var errors: [String]
    var warnings: [String]
    var canPresentForApproval: Bool
}

func review(
    proposal: FocusPolicyProposal,
    hasCurrentAuthorization: Bool,
    hasSelection: Bool
) -> PolicyReview {
    var errors: [String] = []
    var warnings: [String] = []

    if !hasCurrentAuthorization {
        errors.append("Family Controls authorization is not current.")
    }
    if !hasSelection {
        errors.append("Choose a private scope before applying a policy.")
    }
    if !(0...23).contains(proposal.startHour)
        || !(0...23).contains(proposal.endHour) {
        errors.append("Schedule hours are invalid.")
    }
    if proposal.assumptions.isEmpty {
        warnings.append("Review the time-zone and repeat assumptions.")
    }
    if proposal.effect != "shield-selected-scope" {
        errors.append("The proposed effect is not supported by this route.")
    }

    return PolicyReview(
        errors: errors,
        warnings: warnings,
        canPresentForApproval: errors.isEmpty
    )
}
~~~

Do not include token bytes, hidden identity maps, or raw child activity in the prompt. The approval action should call the schedule/settings adapter after the user confirms the exact effect.

## Recipe 14: deterministic extension and UI fixtures

Use fixtures to prove app-owned state and extension command handling without claiming system enforcement.

~~~swift
struct ScreenTimeFixture: Sendable {
    var authorization: String
    var selectionCount: Int
    var scheduleState: String
    var callback: String?
    var shieldState: String
    var reportState: String
}

enum ScreenTimeFixtures {
    static let authorizedDraft = ScreenTimeFixture(
        authorization: "authorized",
        selectionCount: 3,
        scheduleState: "draft",
        callback: nil,
        shieldState: "not-requested",
        reportState: "not-requested"
    )

    static let staleRevoked = ScreenTimeFixture(
        authorization: "revoked",
        selectionCount: 3,
        scheduleState: "stale",
        callback: nil,
        shieldState: "unknown",
        reportState: "unavailable"
    )

    static let callbackObserved = ScreenTimeFixture(
        authorization: "authorized",
        selectionCount: 3,
        scheduleState: "observed",
        callback: "intervalDidStart",
        shieldState: "requested",
        reportState: "ready"
    )
}
~~~

Test that revoked selection disables Apply, stale state is visible, missing reports do not render zero, and a repeated callback does not duplicate a command.

## Verification route

1. Unit-test pure policy and proposal validation.
2. UI-test authorization, picker entry, review, disable, stale, and revoked states.
3. Compile every extension target with its capability and App Group.
4. Use fixtures for report and shield state.
5. Run signed physical-device authorization and selection.
6. Trigger a short schedule and threshold on the supported configuration.
7. Observe the shield, action, and report extension.
8. Revoke in Settings and verify token recovery.
9. Review logs, network, App Group data, and AI inputs.
10. Record distribution entitlement and TestFlight evidence.

The [Family Controls and Device Activity proof matrix](../60-verification/22-family-controls-device-activity-proof-matrix.md) defines the evidence boundary.

## Sources

- [Screen Time Technology Frameworks](https://developer.apple.com/documentation/screentimeapidocumentation/)
- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [AuthorizationCenter](https://developer.apple.com/documentation/FamilyControls/AuthorizationCenter)
- [FamilyActivityPicker](https://developer.apple.com/documentation/FamilyControls/FamilyActivityPicker)
- [FamilyActivitySelection](https://developer.apple.com/documentation/FamilyControls/FamilyActivitySelection)
- [Requesting the Family Controls entitlement](https://developer.apple.com/documentation/FamilyControls/requesting-the-family-controls-entitlement)
- [Configuring Family Controls](https://developer.apple.com/documentation/xcode/configuring-family-controls)
- [Device Activity](https://developer.apple.com/documentation/deviceactivity)
- [DeviceActivityCenter](https://developer.apple.com/documentation/deviceactivity/deviceactivitycenter)
- [DeviceActivitySchedule](https://developer.apple.com/documentation/deviceactivity/deviceactivityschedule)
- [DeviceActivityEvent](https://developer.apple.com/documentation/deviceactivity/deviceactivityevent)
- [DeviceActivityMonitor](https://developer.apple.com/documentation/deviceactivity/deviceactivitymonitor)
- [DeviceActivityReport](https://developer.apple.com/documentation/deviceactivity/deviceactivityreport)
- [DeviceActivityReportExtension](https://developer.apple.com/documentation/deviceactivity/deviceactivityreportextension)
- [DeviceActivityFilter](https://developer.apple.com/documentation/deviceactivity/deviceactivityfilter)
- [Managed Settings](https://developer.apple.com/documentation/managedsettings)
- [ManagedSettingsStore](https://developer.apple.com/documentation/managedsettings/managedsettingsstore)
- [ShieldSettings](https://developer.apple.com/documentation/managedsettings/shieldsettings)
- [ShieldActionDelegate](https://developer.apple.com/documentation/managedsettings/shieldactiondelegate)
- [Managed Settings UI](https://developer.apple.com/documentation/managedsettingsui)
- [ShieldConfiguration](https://developer.apple.com/documentation/managedsettingsui/shieldconfiguration)
- [ShieldConfigurationDataSource](https://developer.apple.com/documentation/managedsettingsui/shieldconfigurationdatasource)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)

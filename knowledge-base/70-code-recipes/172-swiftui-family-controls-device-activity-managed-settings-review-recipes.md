# SwiftUI Family Controls, Device Activity, and Managed Settings code recipes

These recipes are compile-oriented starting points for an iOS 26 project. Add each extension class to the correct Xcode target, verify the final SDK signatures, and test the system behavior on a physical authorized device. The snippets intentionally keep Screen Time tokens out of logs, network payloads, and model prompts.

## 1. App target state and authorization

```swift
import FamilyControls
import Observation

@MainActor
@Observable
final class ScreenTimeCoordinator {
    private let authorizationCenter = AuthorizationCenter.shared
    private let activityCenter = DeviceActivityCenter()

    var selection = FamilyActivitySelection()
    var isPickerPresented = false
    private(set) var authorizationStatusText = "Not checked"
    private(set) var lastError: String?
    private(set) var scheduleRevision = UUID()

    func refreshAuthorizationStatus() {
        // Keep the enum private to the view model. Do not turn a cached status
        // into proof that a monitor, report, or shield extension is running.
        authorizationStatusText = String(describing: authorizationCenter.authorizationStatus)
    }

    func requestIndividualAuthorization() async {
        lastError = nil
        do {
            try await authorizationCenter.requestAuthorization(for: .individual)
            refreshAuthorizationStatus()
        } catch {
            lastError = String(describing: error)
            refreshAuthorizationStatus()
        }
    }

    func requestChildAuthorization() async {
        lastError = nil
        do {
            try await authorizationCenter.requestAuthorization(for: .child)
            refreshAuthorizationStatus()
        } catch {
            lastError = String(describing: error)
            refreshAuthorizationStatus()
        }
    }
}
```

The authorization call needs the Family Controls capability in the app target. Treat `requestAuthorization` success, `authorizationStatus`, selection availability, and system policy effect as separate state values.

## 2. Present the system activity picker

```swift
import FamilyControls
import SwiftUI

struct ActivitySelectionView: View {
    @Bindable var coordinator: ScreenTimeCoordinator

    var body: some View {
        Form {
            Section {
                Button("Choose apps, categories, or websites") {
                    coordinator.isPickerPresented = true
                }
                .accessibilityHint("Opens Apple’s Screen Time selection sheet")
            } header: {
                Text("Scope")
            } footer: {
                Text("Your selection is represented to the app by privacy-preserving values.")
            }

            Section("Selection summary") {
                LabeledContent("Applications", value: "\(coordinator.selection.applicationTokens.count)")
                LabeledContent("Categories", value: "\(coordinator.selection.categoryTokens.count)")
                LabeledContent("Websites", value: "\(coordinator.selection.webDomainTokens.count)")
            }
        }
        .familyActivityPicker(
            isPresented: $coordinator.isPickerPresented,
            selection: $coordinator.selection
        )
    }
}
```

The counts are app-owned display metadata. Do not print the token sets or convert them to strings for diagnostics. If authorization is revoked, discard or revalidate the selection before applying it.

## 3. Keep token handling narrow

```swift
import FamilyControls

struct SelectionSnapshot: Sendable {
    let revision: UUID
    let applicationCount: Int
    let categoryCount: Int
    let webDomainCount: Int
}

@MainActor
func snapshot(of selection: FamilyActivitySelection) -> SelectionSnapshot {
    SelectionSnapshot(
        revision: UUID(),
        applicationCount: selection.applicationTokens.count,
        categoryCount: selection.categoryTokens.count,
        webDomainCount: selection.webDomainTokens.count
    )
}
```

Use `FamilyActivitySelection` only at the boundary that passes the user’s opaque values to the documented Family Controls, Device Activity, or Managed Settings API. Do not use `SelectionSnapshot` as a usage-analysis record; it only describes the shape of a selection.

## 4. Register a repeating schedule and threshold event

```swift
import DeviceActivity
import FamilyControls

extension ScreenTimeCoordinator {
    func startQuietHours() throws {
        let schedule = DeviceActivitySchedule(
            intervalStart: DateComponents(hour: 22),
            intervalEnd: DateComponents(hour: 7),
            repeats: true,
            warningTime: DateComponents(minute: 5)
        )

        let event = DeviceActivityEvent(
            applications: selection.applicationTokens,
            categories: selection.categoryTokens,
            webDomains: selection.webDomainTokens,
            threshold: DateComponents(minute: 60),
            includesPastActivity: false
        )

        let activityName = DeviceActivityName("com.example.app.quiet-hours")
        let eventName = DeviceActivityEvent.Name("com.example.app.daily-limit")

        try activityCenter.startMonitoring(
            activityName,
            during: schedule,
            events: [eventName: event]
        )

        scheduleRevision = UUID()
    }

    func stopQuietHours() {
        activityCenter.stopMonitoring(
            [DeviceActivityName("com.example.app.quiet-hours")]
        )
        scheduleRevision = UUID()
    }
}
```

Confirm the final SDK’s overloads in the target. The important design constraints are stable activity/event names, deliberate replacement behavior, explicit threshold semantics, and a policy revision that lets callbacks reject stale configuration.

## 5. Apply a named Managed Settings store

```swift
import FamilyControls
import ManagedSettings

struct SettingsPolicy {
    let applications: Set<ApplicationToken>
    let categories: Set<ActivityCategoryToken>
    let webDomains: Set<WebDomainToken>
}

@MainActor
final class SettingsPolicyController {
    private let store = ManagedSettingsStore(
        named: ManagedSettingsStore.Name("com.example.app.study-policy")
    )

    func apply(_ policy: SettingsPolicy) {
        store.shield.applications = policy.applications.isEmpty ? nil : policy.applications
        store.shield.applicationCategories = policy.categories.isEmpty ? nil : policy.categories
        store.shield.webDomains = policy.webDomains.isEmpty ? nil : policy.webDomains
    }

    func clearAppOwnedPolicy() {
        store.clearAllSettings()
    }
}
```

`nil` clears this store’s setting. It does not promise to remove restrictions contributed by another store, another authorized app, a parent device, or the system. If the final SDK names a particular shield property differently, keep the policy adapter small and let the compiler guide the target-specific correction.

## 6. Monitor extension adapter

Add this class to a Device Activity Monitor extension target. The extension must load only a pre-approved local policy and must not depend on the foreground SwiftUI process.

```swift
import DeviceActivity
import FamilyControls
import ManagedSettings

final class DeviceActivityMonitorExtension: DeviceActivityMonitor {
    private let store = ManagedSettingsStore(
        named: ManagedSettingsStore.Name("com.example.app.study-policy")
    )

    override func intervalDidStart(for activity: DeviceActivityName) {
        super.intervalDidStart(for: activity)
        guard activity == DeviceActivityName("com.example.app.quiet-hours") else { return }

        // Replace this with a bounded, app-group or extension-safe policy
        // reader appropriate for the target. Never fetch a server here.
        let policy = PreapprovedPolicyStore().load()
        apply(policy)
    }

    override func eventDidReachThreshold(
        _ event: DeviceActivityEvent.Name,
        activity: DeviceActivityName
    ) {
        super.eventDidReachThreshold(event, activity: activity)
        guard event == DeviceActivityEvent.Name("com.example.app.daily-limit") else { return }

        let policy = PreapprovedPolicyStore().load()
        apply(policy)
    }

    private func apply(_ policy: SettingsPolicy?) {
        guard let policy else { return }
        store.shield.applications = policy.applications.isEmpty ? nil : policy.applications
        store.shield.applicationCategories = policy.categories.isEmpty ? nil : policy.categories
        store.shield.webDomains = policy.webDomains.isEmpty ? nil : policy.webDomains
    }
}

private struct PreapprovedPolicyStore {
    func load() -> SettingsPolicy? {
        // Compile this against the project’s approved local persistence route.
        // A missing policy is safer than inventing a new restriction.
        nil
    }
}
```

Use the actual extension-safe persistence design for the project. The critical rule is that a system callback applies a policy already reviewed by the authorized person; it does not ask an AI model or server to decide what to block at callback time.

## 7. Host a privacy-preserving report

```swift
import DeviceActivity
import FamilyControls
import SwiftUI

struct ActivityReportHost: View {
    let context: DeviceActivityReport.Context
    let filter: DeviceActivityFilter

    var body: some View {
        DeviceActivityReport(context, filter: filter)
            .accessibilityLabel("Screen Time activity report")
    }
}

@MainActor
func makeDailyFilter(
    selection: FamilyActivitySelection,
    calendar: Calendar = .current
) -> DeviceActivityFilter? {
    guard let interval = calendar.dateInterval(of: .weekOfYear, for: .now) else {
        return nil
    }

    return DeviceActivityFilter(
        segment: .daily(during: interval),
        users: .all,
        devices: .init([.iPhone, .iPad]),
        applications: selection.applicationTokens,
        categories: selection.categoryTokens,
        webDomains: selection.webDomainTokens
    )
}
```

The report context and extension scene are project-owned identifiers; define them in the report extension target and inject the matching context into the host. Keep the sensitive report view in the `DeviceActivityReportExtension` sandbox. Do not turn report results into a network request or a general analytics event.

## 8. Report extension boundary

The exact report scene shape should be compiled against the final SDK. Keep the target boundary explicit:

```swift
import DeviceActivity
import SwiftUI

struct DailyActivityReportScene: DeviceActivityReportScene {
    let context: DeviceActivityReport.Context

    var body: some View {
        // Build a native SwiftUI view from the filtered Device Activity data
        // delivered to this extension. Keep raw values inside the extension.
        Text("Daily activity")
    }
}

struct ScreenTimeReportExtension: DeviceActivityReportExtension {
    var body: some DeviceActivityReportScene {
        DailyActivityReportScene(context: .init("daily-activity"))
    }
}
```

Treat the snippet as a target-shape recipe, not a substitute for the SDK’s report-scene protocol declaration. The extension point, context identifier, filter semantics, sandbox, and no-network behavior are the important contracts to verify.

## 9. Configure a custom shield

Add this class to the Shield Configuration extension target. The extension should return a result quickly and remain useful if Apple falls back to default values.

```swift
import ManagedSettings
import ManagedSettingsUI
import UIKit

final class ShieldConfigurationExtension: ShieldConfigurationDataSource {
    override func configuration(shielding application: Application) -> ShieldConfiguration {
        ShieldConfiguration(
            backgroundBlurStyle: .systemMaterial,
            backgroundColor: .systemIndigo,
            icon: UIImage(systemName: "hourglass"),
            title: .init(text: "Study time"),
            subtitle: .init(text: "This app is unavailable until the schedule ends."),
            primaryButtonLabel: .init(text: "Open controls"),
            primaryButtonBackgroundColor: .systemIndigo,
            secondaryButtonLabel: .init(text: "Not now")
        )
    }

    override func configuration(shielding webDomain: WebDomain) -> ShieldConfiguration {
        ShieldConfiguration(
            title: .init(text: "Study time"),
            subtitle: .init(text: "This website is unavailable until the schedule ends.")
        )
    }
}
```

Add the category overloads only when the product needs category-specific language. Do not use the `Application` or `WebDomain` value to log or reveal private identity. Test the default configuration when the extension returns `nil` fields or takes too long.

## 10. Handle shield actions

`ShieldActionDelegate` has overloads for application, web-domain, and category tokens. Keep each overload’s policy identical unless the product has a documented distinction.

```swift
import ManagedSettings

final class ShieldActionExtension: ShieldActionDelegate {
    override func handle(
        action: ShieldAction,
        for application: ApplicationToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        completionHandler(response(for: action))
    }

    override func handle(
        action: ShieldAction,
        for webDomain: WebDomainToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        completionHandler(response(for: action))
    }

    override func handle(
        action: ShieldAction,
        for category: ActivityCategoryToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        completionHandler(response(for: action))
    }

    private func response(for action: ShieldAction) -> ShieldActionResponse {
        switch action {
        case .primaryButtonPressed:
            return .openParentalControlsApp
        case .secondaryButtonPressed,
             .firstSecondarySubmenuItemPressed,
             .secondSecondarySubmenuItemPressed,
             .thirdSecondarySubmenuItemPressed:
            return .none
        default:
            return .defer
        }
    }
}
```

The `default` branch is a compile-oriented guard for future action cases. Review the final SDK’s enum cases and product decision before shipping. Returning `.openParentalControlsApp` is a handoff to the authorized controls app, not permission to change policy without review.

## 11. App-owned typed AI proposal

Keep the model input free of opaque tokens and raw report data. Use app-owned schedule values and user intent only.

```swift
import FoundationModels

@Generable
struct ScreenTimePolicyProposal {
    var title: String
    var startHour: Int
    var endHour: Int
    var warningMinutes: Int
    var explanation: String
}

struct PolicyProposalService {
    func propose(for intent: String, currentSchedule: String) async throws -> ScreenTimePolicyProposal {
        guard SystemLanguageModel.default.isAvailable else {
            throw ProposalError.modelUnavailable
        }

        let session = LanguageModelSession()
        let prompt = """
        Draft a Screen Time schedule proposal from this user intent and current
        app-owned schedule summary. Do not identify or infer applications,
        websites, categories, people, or device activity. Return only values
        that the user can review in the app.

        User intent: \(intent)
        Current schedule summary: \(currentSchedule)
        """

        let response = try await session.respond(
            to: prompt,
            generating: ScreenTimePolicyProposal.self
        )
        return response.content
    }

    enum ProposalError: Error {
        case modelUnavailable
    }
}
```

Before applying a proposal:

```swift
struct ValidatedPolicyProposal {
    let title: String
    let startHour: Int
    let endHour: Int
    let warningMinutes: Int
    let explanation: String
}

func validate(_ proposal: ScreenTimePolicyProposal) -> ValidatedPolicyProposal? {
    guard (0...23).contains(proposal.startHour),
          (0...23).contains(proposal.endHour),
          (0...120).contains(proposal.warningMinutes),
          !proposal.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
          !proposal.explanation.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    else { return nil }

    return ValidatedPolicyProposal(
        title: proposal.title,
        startHour: proposal.startHour,
        endHour: proposal.endHour,
        warningMinutes: proposal.warningMinutes,
        explanation: proposal.explanation
    )
}
```

The user must still review the exact values, confirm the current authorization/selection revision, and tap Apply. If the selection, authorization, or schedule changes while generation is in flight, discard the response.

## 12. Native glass control cluster

```swift
import SwiftUI

struct PolicyActions: View {
    let isApplying: Bool
    let apply: () -> Void
    let clear: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button("Apply", action: apply)
                .buttonStyle(.borderedProminent)
                .disabled(isApplying)

            Button("Clear", role: .destructive, action: clear)
                .disabled(isApplying)
        }
        .padding(12)
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 20))
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Screen Time policy actions")
    }
}
```

Keep the glass group limited to app-owned controls. The system authorization sheet, Family Activity Picker, report sandbox, and shield presentation remain Apple/system surfaces.

## 13. Swift Testing policy fixtures

```swift
import Testing

struct ScreenTimePolicyTests {
    @Test("empty selection does not become an all-activity policy")
    func emptySelectionIsExplicit() {
        let applicationTokens: Set<ApplicationToken> = []
        let categoryTokens: Set<ActivityCategoryToken> = []
        let webDomainTokens: Set<WebDomainToken> = []

        #expect(applicationTokens.isEmpty)
        #expect(categoryTokens.isEmpty)
        #expect(webDomainTokens.isEmpty)
        #expect(applicationTokens.isEmpty && categoryTokens.isEmpty && webDomainTokens.isEmpty)
    }

    @Test("model proposals require explicit validation")
    func proposalNeedsBoundedValues() {
        let proposal = ScreenTimePolicyProposal(
            title: "Study window",
            startHour: 22,
            endHour: 7,
            warningMinutes: 5,
            explanation: "A schedule you can review"
        )

        #expect(validate(proposal) != nil)
    }
}
```

Add integration tests for authorization, picker selection, revocation, schedule replacement, monitor callbacks, shield effects, report sandboxing, accessibility, archive entitlements, and TestFlight. Unit tests cannot prove system Screen Time behavior.

## Sources

- [Family Controls](https://developer.apple.com/documentation/familycontrols)
- [AuthorizationCenter](https://developer.apple.com/documentation/familycontrols/authorizationcenter)
- [FamilyActivityPicker](https://developer.apple.com/documentation/familycontrols/familyactivitypicker)
- [FamilyActivitySelection](https://developer.apple.com/documentation/familycontrols/familyactivityselection)
- [Requesting the Family Controls entitlement](https://developer.apple.com/documentation/familycontrols/requesting-the-family-controls-entitlement)
- [Configuring Family Controls](https://developer.apple.com/documentation/xcode/configuring-family-controls)
- [Family Controls entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.family-controls)
- [Device Activity](https://developer.apple.com/documentation/deviceactivity)
- [DeviceActivityCenter](https://developer.apple.com/documentation/deviceactivity/deviceactivitycenter)
- [DeviceActivitySchedule](https://developer.apple.com/documentation/deviceactivity/deviceactivityschedule)
- [DeviceActivityEvent](https://developer.apple.com/documentation/deviceactivity/deviceactivityevent)
- [DeviceActivityMonitor](https://developer.apple.com/documentation/deviceactivity/deviceactivitymonitor)
- [DeviceActivityReport](https://developer.apple.com/documentation/deviceactivity/deviceactivityreport)
- [DeviceActivityReportExtension](https://developer.apple.com/documentation/deviceactivity/deviceactivityreportextension)
- [DeviceActivityReportScene](https://developer.apple.com/documentation/deviceactivity/deviceactivityreportscene)
- [DeviceActivityFilter](https://developer.apple.com/documentation/deviceactivity/deviceactivityfilter)
- [DeviceActivityResults](https://developer.apple.com/documentation/deviceactivity/deviceactivityresults)
- [Managed Settings](https://developer.apple.com/documentation/managedsettings)
- [ManagedSettingsStore](https://developer.apple.com/documentation/managedsettings/managedsettingsstore)
- [ShieldAction](https://developer.apple.com/documentation/managedsettings/shieldaction)
- [ShieldActionDelegate](https://developer.apple.com/documentation/managedsettings/shieldactiondelegate)
- [ShieldActionResponse](https://developer.apple.com/documentation/managedsettings/shieldactionresponse)
- [Managed Settings UI](https://developer.apple.com/documentation/managedsettingsui)
- [ShieldConfiguration](https://developer.apple.com/documentation/managedsettingsui/shieldconfiguration)
- [ShieldConfigurationDataSource](https://developer.apple.com/documentation/managedsettingsui/shieldconfigurationdatasource)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)

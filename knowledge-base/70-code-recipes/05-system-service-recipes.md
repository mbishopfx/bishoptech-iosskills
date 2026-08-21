# System-Service Code Recipes

These are compile-oriented route sketches for the T017 system-service cards. They show the seam between app-owned state and an Apple system service; they are not claimed to compile in this documentation-only workspace. Before copying a sketch, check the selected SDK’s current signature, add the required target/capability/entitlement configuration, and compile the smallest slice.

## 1. Family Controls authorization gate

The app should make authorization a visible state transition. The Screen Time frameworks use a guardian/privacy boundary and may require app extensions and a Family Controls entitlement. Do not create the UI as if an authorization request guarantees access to raw activity data.

```swift
import FamilyControls
import Observation

@MainActor
@Observable
final class FamilyControlsGate {
    enum State {
        case idle
        case requesting
        case authorized
        case denied
        case failed
    }

    private(set) var state: State = .idle
    private(set) var errorMessage: String?

    func requestAuthorization() {
        state = .requesting
        errorMessage = nil

        // Confirm the current SDK overload and authorization scope in Xcode.
        // Apple’s current route uses AuthorizationCenter.shared.
        AuthorizationCenter.shared.requestAuthorization { [weak self] result in
            Task { @MainActor in
                switch result {
                case .success:
                    self?.state = .authorized
                case .failure(let error):
                    self?.state = .failed
                    self?.errorMessage = String(describing: error)
                }
            }
        }
    }
}
```

Compile/device gate:

- Verify the current `AuthorizationCenter` overload for the target SDK; Apple’s documentation may expose async and callback forms across SDK revisions.
- Add Family Controls to the app and every required Screen Time extension target, then inspect the built entitlements and provisioning profile.
- Model unavailable, denied, revoked, extension-not-running, schedule-expired, and recovery states.
- Test the authorization and scheduled-extension path on supported physical configurations. A local mock is useful for UI state tests but is not proof of the Screen Time policy effect.

Sources: [Screen Time Technology Frameworks](https://developer.apple.com/documentation/ScreenTimeAPIDocumentation), [Family Controls](https://developer.apple.com/documentation/familycontrols), [Configuring Family Controls](https://developer.apple.com/documentation/Xcode/configuring-family-controls), and [Managed Settings connection with frameworks](https://developer.apple.com/documentation/managedsettings/connectionwithframeworks).

## 2. Private Spotlight index with a typed deep link

Index only records the person expects to find, and keep the index synchronized with edits/deletions. The index is a system surface, not a second source of truth.

```swift
import CoreSpotlight
import UniformTypeIdentifiers

struct SearchIndexer {
    func index(recordID: String, title: String, summary: String) {
        let attributes = CSSearchableItemAttributeSet(contentType: UTType.text.identifier)
        attributes.title = title
        attributes.contentDescription = summary

        let item = CSSearchableItem(
            uniqueIdentifier: recordID,
            domainIdentifier: "records",
            attributeSet: attributes
        )

        CSSearchableIndex.default().indexSearchableItems([item]) { error in
            // Map indexing failure to an observable, non-destructive state.
            if let error { print("Spotlight indexing failed: \(error)") }
        }
    }

    func remove(recordID: String) {
        CSSearchableIndex.default()
            .deleteSearchableItems(withIdentifiers: [recordID]) { error in
                if let error { print("Spotlight removal failed: \(error)") }
            }
    }
}
```

Route the selected identifier through typed navigation and re-check that the domain record still exists before presenting it. For newer system-intelligence routes, compare this direct index with an `AppEntity`/`EntityQuery` design instead of indexing the same record twice without a deletion policy.

Compile/device gate:

- Verify the current `CSSearchableItemAttributeSet` initializer and content-type API in the selected SDK.
- Use stable identifiers and a domain identifier; never place secrets or unreviewed generated text in searchable attributes.
- Test create, edit, delete, expiration, stale identifier, locked-device, and deep-link cases on the target device.
- Treat Spotlight visibility as user-controlled system behavior; the app can maintain its index but cannot promise ranking or presentation.

Sources: [Core Spotlight](https://developer.apple.com/documentation/corespotlight), [Adding your app’s content to Spotlight indexes](https://developer.apple.com/documentation/corespotlight/adding-your-app-s-content-to-spotlight-indexes), [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight), and [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers).

## 3. App Intent as a validated system action

An App Intent is an entry point from Shortcuts, Spotlight, widgets, or another system surface. It must call the same domain service as the in-app UI; it must not bypass validation or authorization.

```swift
import AppIntents

struct AddQuickRecord: AppIntent {
    static var title: LocalizedStringResource = "Add quick record"

    @Parameter(title: "Text")
    var text: String

    func perform() async throws -> some IntentResult {
        let normalized = try RecordActions.validate(text)
        try await RecordActions.add(normalized)
        return .result()
    }
}
```

`RecordActions` is app-owned pseudocode for a shared service. Its implementation should enforce authorization, input limits, idempotence, persistence errors, and user-visible failure mapping. If a model proposes the parameter, validate it before constructing the intent or calling the mutation service.

Compile/device gate:

- Verify `AppIntent`, `@Parameter`, `IntentResult`, entity/query, and target membership against the current SDK.
- Test the intent from the in-app route, Shortcuts, Spotlight, and any widget/control surface in scope.
- Test the app terminated, data missing, permission denied, duplicate invocation, and cancellation cases.
- Keep a read-only or manual fallback when the system cannot resolve the entity or the action is not authorized.

Sources: [App Intents](https://developer.apple.com/documentation/appintents/), [AppIntent](https://developer.apple.com/documentation/appintents/appintent), [AppEntity](https://developer.apple.com/documentation/appintents/appentity), [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery), and [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities).

## 4. Apple Pay request boundary

Use PassKit for real-world goods/services or donations. Use StoreKit for digital goods delivered in the app. The merchant identifier below is intentionally a placeholder and must never be treated as a credential.

```swift
import PassKit

struct ApplePayRequestFactory {
    func makeRequest(amount: Decimal) -> PKPaymentRequest {
        let request = PKPaymentRequest()
        request.merchantIdentifier = "merchant.example.placeholder"
        request.countryCode = "US"
        request.currencyCode = "USD"
        request.supportedNetworks = [.visa, .masterCard, .amex]
        request.merchantCapabilities = .threeDSecure
        request.paymentSummaryItems = [
            PKPaymentSummaryItem(label: "Example service", amount: NSDecimalNumber(decimal: amount))
        ]
        return request
    }
}
```

The payment authorization result must go to the authorized payment processor/backend. Do not persist raw payment credentials. Keep the UI state explicit: unavailable, presenting, authorized, declined, cancelled, processing, confirmed, and reconciliation-failed.

Compile/device/release gate:

- Configure the Apple Pay capability, merchant identifier, certificates, payment processor, and supported regions through the authorized developer/account path.
- Verify the current `PKPaymentRequest` fields and supported payment networks for the target SDK.
- Use deterministic UI tests and documented Simulator limits for early work; use a signed physical device with a supported card and sandbox/backend flow for payment proof.
- Test cancellation, decline, network loss after authorization, duplicate callbacks, and server reconciliation.

Sources: [PassKit](https://developer.apple.com/documentation/passkit), [Setting up Apple Pay](https://developer.apple.com/documentation/passkit/setting-up-apple-pay), [Offering Apple Pay in your app](https://developer.apple.com/documentation/PassKit/offering-apple-pay-in-your-app), and [Adding capabilities to your app](https://developer.apple.com/documentation/xcode/adding-capabilities-to-your-app).

## 5. Wallet pass entry point

Wallet routes have a different lifecycle from a normal in-app card. The pass is signed/distributed according to Apple’s Wallet contract and may be updated outside the app.

```swift
import PassKit

func presentAddPass(from controller: UIViewController, pass: PKPass) {
    guard let addController = PKAddPassesViewController(pass: pass) else {
        // Render an unavailable state or offer the supported export route.
        return
    }

    controller.present(addController, animated: true)
}
```

Compile/device/release gate:

- Verify the current initializer and add the Wallet capability/pass type configuration for the target.
- Validate pass signature, pass updates, expiration/revocation, and user consent outside the view controller.
- Test on a signed physical device with Wallet; a file fixture or screenshot does not prove Wallet presentation.

Sources: [PassKit Wallet](https://developer.apple.com/documentation/passkit/wallet), [Configuring Wallet support](https://developer.apple.com/documentation/xcode/configuring-wallet-support), and [Adding capabilities to your app](https://developer.apple.com/documentation/xcode/adding-capabilities-to-your-app).

## 6. CallKit provider seam

CallKit coordinates the system call UI; it does not implement the app’s VoIP transport. Keep the provider/delegate and the network service separate, and make incoming-call reporting idempotent.

```swift
import CallKit

final class CallProvider: NSObject, CXProviderDelegate {
    private let provider: CXProvider

    override init() {
        let configuration = CXProviderConfiguration()
        configuration.localizedName = "Example Calls"
        configuration.supportsVideo = true
        provider = CXProvider(configuration: configuration)
        super.init()
        provider.setDelegate(self, queue: nil)
    }

    func reportIncomingCall(uuid: UUID, handle: String) {
        let update = CXCallUpdate()
        update.remoteHandle = CXHandle(type: .generic, value: handle)

        provider.reportNewIncomingCall(with: uuid, update: update) { error in
            // Map a rejected or late call into the app’s call state.
            if let error { print("Incoming call failed: \(error)") }
        }
    }

    func providerDidReset(_ provider: CXProvider) {
        // Tear down media and reconcile active calls.
    }
}
```

The delegate has additional required methods in the current SDK. Implement and verify the complete action lifecycle (`answer`, `end`, `hold`, `mute`, and any supported media action) before presenting this as a working provider.

Compile/device/release gate:

- Verify whether the target should use CallKit or LiveCommunicationKit and inspect the current default-calling requirements.
- Pair the provider with PushKit or the documented incoming-call route; do not report calls from an arbitrary local timer.
- Test a signed physical device across incoming/outgoing, lock screen, Focus/Do Not Disturb, audio route, interruption, termination, duplicate push, and network failure states.
- Treat contact identity and call metadata as privacy-sensitive system-shared data.

Sources: [CallKit](https://developer.apple.com/documentation/callkit), [LiveCommunicationKit](https://developer.apple.com/documentation/LiveCommunicationKit), [PushKit](https://developer.apple.com/documentation/pushkit), and [Handling Communication Notifications and Focus Status Updates](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates).

## Recipe evidence contract

For every copied recipe, record:

- exact SDK/Xcode version and deployment target;
- target membership, capability, entitlement, usage description, account, and service setup;
- code paths tested with mocks/fixtures versus simulator versus physical device;
- system-surface and signed/release evidence;
- open signature, availability, privacy, credential, or production gaps.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Framework availability and device-proof matrix](../40-framework-routes/08-framework-availability-and-device-matrix.md)
- [System-service route cards](../44-system-services/README.md)

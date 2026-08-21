# IdentityLookup extension code recipes

These are compile-oriented sketches for a containing app plus the appropriate extension target. They are not general SMS/Phone APIs. Keep raw message and phone data out of logs, shared storage, model telemetry, and screenshots.

## 1. Message Filter extension entry point

~~~swift
import IdentityLookup

final class MessageFilterExtension:
    ILMessageFilterExtension,
    ILMessageFilterQueryHandling {

    func handle(
        _ queryRequest: ILMessageFilterQueryRequest,
        context: ILMessageFilterExtensionContext,
        completion: @escaping (ILMessageFilterQueryResponse) -> Void
    ) {
        let response = ILMessageFilterQueryResponse()

        guard let body = queryRequest.messageBody else {
            response.action = .none
            completion(response)
            return
        }

        response.action = classifyLocally(body)
        completion(response)
    }

    private func classifyLocally(_ body: String) -> ILMessageFilterAction {
        // Keep this deterministic and bounded. Use .none when uncertain.
        _ = body
        return .none
    }
}
~~~

Confirm the exact initializer and protocol signature in the selected SDK. The extension should complete quickly, use only the request scope, and map to Apple-defined actions.

## 2. Return an action and subaction

~~~swift
import IdentityLookup

func makeResponse(
    action: ILMessageFilterAction,
    subAction: ILMessageFilterSubAction = .none
) -> ILMessageFilterQueryResponse {
    let response = ILMessageFilterQueryResponse()
    response.action = action
    response.subAction = subAction
    return response
}
~~~

Use subactions only when the selected SDK and response vocabulary support them. Do not create a custom category string. If the classifier lacks sufficient evidence, return the documented none action.

## 3. Defer a query to the system-mediated server

~~~swift
import IdentityLookup

func deferToAssociatedService(
    request: ILMessageFilterQueryRequest,
    context: ILMessageFilterExtensionContext,
    completion: @escaping (ILMessageFilterQueryResponse) -> Void
) {
    _ = request
    context.deferQueryRequestToNetwork { networkResponse, error in
        guard let networkResponse, error == nil else {
            completion(makeResponse(action: .none))
            return
        }

        // Parse only the documented server response.
        _ = networkResponse.data
        completion(makeResponse(action: .none))
    }
}
~~~

The extension does not perform a direct URLSession request in this route. The system handles the HTTPS communication and returns an ILNetworkResponse. Configure associated domains/shared credentials and the extension Info.plist according to Apple’s Message Filter guide.

## 4. Reporting extension readiness

~~~swift
import IdentityLookup
import IdentityLookupUI

final class CommunicationReportViewController:
    ILClassificationUIExtensionViewController {

    override func prepare(for request: ILClassificationRequest) {
        // Collect only the fields the user needs to complete the report.
        _ = request
        extensionContext.isReadyForClassificationResponse = true
    }

    override func classificationResponse(
        for request: ILClassificationRequest
    ) -> ILClassificationResponse {
        _ = request
        return ILClassificationResponse(action: .reportJunk)
    }
}
~~~

The system owns Cancel and Done. In a real target, return the action based on the user’s explicit choices and test report-not-junk, report-junk, block, cancel, and unavailable states.

## 5. Manage Live Caller ID extension state

~~~swift
import IdentityLookup

func refreshCallerIDExtension(
    identifier: String
) async -> Result<Void, Error> {
    do {
        let status = LiveCallerIDLookupManager.shared
            .status(forExtensionWithIdentifier: identifier)

        if status == .disabled {
            try await LiveCallerIDLookupManager.shared.openSettings()
        }

        try await LiveCallerIDLookupManager.shared
            .refreshPIRParameters(forExtensionWithIdentifier: identifier)
        return .success(())
    } catch {
        return .failure(error)
    }
}
~~~

The extension context, token issuer, relay/PIR server, endpoint validation, and user-tier authentication are separate configuration work. A status check is not proof that the server dataset is current or that an incoming call will be identified.

## 6. A privacy-safe local classifier boundary

~~~swift
enum LocalMessageDecision: Sendable {
    case allow
    case junk
    case promotion
    case transaction
    case none
}

struct LocalClassifier {
    func decide(body: String) -> LocalMessageDecision {
        // Do not log or persist body. Default to none when uncertain.
        _ = body
        return .none
    }
}
~~~

Map this typed result to IdentityLookup actions only after validating the target extension scope. An on-device model can be optional; its absence must not silently change the privacy or system contract.

## 7. Containing-app status model

~~~swift
import IdentityLookup
import Observation
import SwiftUI

@MainActor
@Observable
final class IdentityLookupStatusModel {
    var filterEnabled = false
    var reportExtensionEnabled = false
    var callerIDStatus = "Not checked"
    var privacySummary = "The system controls extension delivery."
}

struct IdentityLookupSettingsView: View {
    @State private var model = IdentityLookupStatusModel()

    var body: some View {
        List {
            Section("Message filter") {
                Text(model.filterEnabled ? "Enabled" : "Not enabled")
                Text("Unknown-sender SMS and MMS only")
            }
            Section("Caller ID") {
                Text(model.callerIDStatus)
            }
            Section("Privacy") {
                Text(model.privacySummary)
            }
            Button("Open system settings") {
                // Use the documented settings handoff for the chosen extension.
            }
        }
        .navigationTitle("Communication safety")
    }
}
~~~

Keep this surface in the containing app. The Messages/Phone extension flow is system-owned and should not be recreated as a custom modal.

## 8. Validate an AI classification proposal

~~~swift
struct ClassificationProposal: Codable, Sendable {
    let action: String
    let confidence: Double
    let explanation: String
}

func accepts(
    _ proposal: ClassificationProposal,
    minimumConfidence: Double
) -> Bool {
    let allowed = ["none", "allow", "junk", "promotion", "transaction"]
    return allowed.contains(proposal.action)
        && proposal.confidence >= minimumConfidence
}
~~~

A production extension should use a stricter policy and default to none whenever the model is unavailable, content is ambiguous, or the request exceeds the extension’s supported scope. Never turn an AI proposal directly into a silent block/report side effect.

## Sources

- [IdentityLookup](https://developer.apple.com/documentation/identitylookup)
- [SMS and MMS Message Filtering](https://developer.apple.com/documentation/identitylookup/sms-and-mms-message-filtering)
- [Creating a Message Filter App Extension](https://developer.apple.com/documentation/identitylookup/creating-a-message-filter-app-extension)
- [ILMessageFilterExtension](https://developer.apple.com/documentation/identitylookup/ilmessagefilterextension)
- [ILMessageFilterQueryHandling](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryhandling)
- [ILMessageFilterQueryRequest](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryrequest)
- [ILMessageFilterQueryResponse](https://developer.apple.com/documentation/identitylookup/ilmessagefilterqueryresponse)
- [ILMessageFilterExtensionContext](https://developer.apple.com/documentation/identitylookup/ilmessagefilterextensioncontext)
- [ILNetworkResponse](https://developer.apple.com/documentation/identitylookup/ilnetworkresponse)
- [ILMessageFilterAction](https://developer.apple.com/documentation/identitylookup/ilmessagefilteraction)
- [ILMessageFilterSubAction](https://developer.apple.com/documentation/identitylookup/ilmessagefiltersubaction)
- [SMS and Call Spam Reporting](https://developer.apple.com/documentation/identitylookup/sms-and-call-spam-reporting)
- [IdentityLookupUI](https://developer.apple.com/documentation/identitylookupui)
- [ILClassificationUIExtensionViewController](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensionviewcontroller)
- [ILClassificationUIExtensionContext](https://developer.apple.com/documentation/identitylookupui/ilclassificationuiextensioncontext)
- [ILClassificationResponse](https://developer.apple.com/documentation/identitylookup/ilclassificationresponse)
- [Getting up-to-date calling and blocking information](https://developer.apple.com/documentation/identitylookup/getting-up-to-date-calling-and-blocking-information-for-your-app)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

***

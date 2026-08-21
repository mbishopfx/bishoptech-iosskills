# ThreadNetwork and Border Router Recipes

These are compile-oriented route sketches for ThreadNetwork, THClient, credential redaction, Border Router state, reviewable AI diagnostics, and proof logging. They are not compiled in this documentation-only workspace and do not prove entitlement approval, iCloud Keychain behavior, physical Thread membership, Matter commissioning, certification, or App Store eligibility.

Before copying a recipe:

1. Set the exact iOS deployment target and Xcode SDK.
2. Add the Manage Thread Network Credentials capability to the intended target.
3. Confirm the current Swift signatures and availability in Xcode.
4. Keep credential operations outside SwiftUI view state.
5. Test on a physical device with a real Thread Border Router.
6. Treat development entitlement and distribution entitlement as separate gates.

## Recipe 1: Describe the route

Keep infrastructure, credential scope, and proof state explicit:

~~~swift
import Foundation

enum ThreadCredentialScope: Sendable {
    case borderAgent
    case preferredNetwork
    case extendedPANID
}

enum ThreadBuildState: Sendable {
    case unavailable(reason: String)
    case developmentOnly
    case distributionReady
}

struct ThreadRoutePlan: Sendable {
    let scope: ThreadCredentialScope
    let buildState: ThreadBuildState
    let requiresConsent: Bool
    let physicalBorderRouterRequired: Bool
    let fallback: String
}
~~~

Populate this plan from the current Apple entitlement, SDK, target, and distribution evidence. Do not render a “Connect” button for a route whose required target or entitlement is absent.

## Recipe 2: Keep credential state redacted

Use a user-facing projection that cannot accidentally include secrets:

~~~swift
import Foundation
import ThreadNetwork

struct RedactedThreadCredential: Sendable {
    let networkName: String?
    let borderAgentDisplayID: String
    let extendedPANDisplayID: String
    let channel: UInt8?
    let createdAt: Date?
    let modifiedAt: Date?
}

func redacted(_ credentials: THCredentials) -> RedactedThreadCredential {
    RedactedThreadCredential(
        networkName: credentials.networkName,
        borderAgentDisplayID: displayDigest(credentials.borderAgentID),
        extendedPANDisplayID: displayDigest(credentials.extendedPANID),
        channel: credentials.channel,
        createdAt: credentials.creationDate,
        modifiedAt: credentials.lastModificationDate
    )
}

private func displayDigest(_ data: Data?) -> String {
    guard let data else { return "Unavailable" }
    let digestInput = data.prefix(4).map { String(format: "%02x", $0) }.joined()
    return digestInput.isEmpty ? "Unavailable" : "••••" + digestInput
}
~~~

The digest above is only a display sketch. Choose a deliberate redaction strategy and avoid exposing a stable identifier when even that could be sensitive. Never include activeOperationalDataSet, networkKey, or PSKC in this projection, logs, analytics, screenshots, clipboard content, or model input.

## Recipe 3: Check for a preferred network

Availability should precede a consent-controlled credential request:

~~~swift
import ThreadNetwork

func checkPreferredNetwork(
    completion: @escaping @Sendable (Result<Bool, Error>) -> Void
) {
    let client = THClient()
    client.isPreferredNetworkAvailable { available in
        completion(.success(available))
    }
}
~~~

Confirm the exact closure annotation in the selected SDK. If the result is false, keep the user in an unavailable or alternative setup state. Do not request preferred credentials simply to determine whether a network exists.

## Recipe 4: Request preferred credentials after explanation

Call the preferred route only after the UI has explained scope and consent:

~~~swift
import ThreadNetwork

func requestPreferredCredentials(
    completion: @escaping @Sendable (Result<THCredentials, Error>) -> Void
) {
    let client = THClient()
    client.retrievePreferredCredentials { credentials, error in
        if let error {
            completion(.failure(error))
        } else if let credentials {
            completion(.success(credentials))
        } else {
            completion(.failure(ThreadRouteError.emptyCredentialResult))
        }
    }
}

enum ThreadRouteError: Error {
    case emptyCredentialResult
    case missingBorderAgentID
    case missingOperationalDataSet
    case userActionRequired
}
~~~

The framework may present Apple-controlled consent. Test allow, deny, cancel, and unavailable states on a physical device. A returned THCredentials object is not permission to display or persist every field.

## Recipe 5: Retrieve credentials for one Border Agent

Keep an existing product Border Router route separate from preferred-network access:

~~~swift
import Foundation
import ThreadNetwork

func credentials(
    forBorderAgentID borderAgentID: Data,
    completion: @escaping @Sendable (Result<THCredentials, Error>) -> Void
) {
    let client = THClient()
    client.retrieveCredentials(forBorderAgent: borderAgentID) { credentials, error in
        if let error {
            completion(.failure(error))
        } else if let credentials {
            completion(.success(credentials))
        } else {
            completion(.failure(ThreadRouteError.emptyCredentialResult))
        }
    }
}
~~~

Apple’s documentation describes the team ID boundary for this operation. Verify that the Border Agent ID is the identity supplied by the intended product protocol and not a user-entered string.

## Recipe 6: Store or update one Border Agent

Store the current active operational dataset only after the product has selected the Border Agent and the person has approved the operation:

~~~swift
import Foundation
import ThreadNetwork

func store(
    borderAgentID: Data,
    activeOperationalDataSet: Data,
    completion: @escaping @Sendable (Result<Void, Error>) -> Void
) {
    let client = THClient()
    client.storeCredentials(
        forBorderAgent: borderAgentID,
        activeOperationalDataSet: activeOperationalDataSet
    ) { error in
        if let error {
            completion(.failure(error))
        } else {
            completion(.success(()))
        }
    }
}
~~~

Do not accept a model-generated Data value. The dataset should come from the approved Border Router/product operation or the documented Apple route. Record only redacted result metadata.

## Recipe 7: Delete one Border Agent

Make the scope of removal explicit:

~~~swift
import Foundation
import ThreadNetwork

func delete(
    borderAgentID: Data,
    completion: @escaping @Sendable (Result<Void, Error>) -> Void
) {
    let client = THClient()
    client.deleteCredentials(forBorderAgent: borderAgentID) { error in
        if let error {
            completion(.failure(error))
        } else {
            completion(.success(()))
        }
    }
}
~~~

This removes the framework-managed credential record for the Border Agent. It does not automatically reset product hardware, remove a Matter accessory, or change the home’s preferred network. Verify the post-delete state by reloading the framework record and separately checking product state.

## Recipe 8: Serialize updates in an actor

Prevent overlapping updates from producing a stale UI:

~~~swift
import Foundation
import ThreadNetwork

actor ThreadCredentialCoordinator {
    private let client = THClient()

    func update(
        borderAgentID: Data,
        activeOperationalDataSet: Data
    ) async throws {
        try await withCheckedThrowingContinuation { continuation in
            client.storeCredentials(
                forBorderAgent: borderAgentID,
                activeOperationalDataSet: activeOperationalDataSet
            ) { error in
                if let error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume()
                }
            }
        }
    }
}
~~~

The continuation wrapper is a route sketch. Verify Sendable and concurrency diagnostics for the selected SDK, and do not assume an Objective-C framework object can be moved across actors without an adapter. Add cancellation and operation identity in the real target so a late result cannot replace a newer selected Border Router.

## Recipe 9: Model the app-facing state

Keep credential storage and product health separate:

~~~swift
import Foundation

enum ThreadCredentialState: Equatable, Sendable {
    case unavailable
    case checking
    case consentRequired
    case denied
    case available
    case stored(lastUpdated: Date?)
    case stale
    case failed(String)
}

enum BorderRouterHealth: Equatable, Sendable {
    case unknown
    case discovering
    case joining
    case active
    case offline
    case failed(String)
}

struct BorderRouterSummary: Equatable, Sendable {
    let title: String
    let credentialState: ThreadCredentialState
    let health: BorderRouterHealth
    let redactedIdentity: String
}
~~~

The UI may combine these into a sentence such as “Credentials stored; router health not checked.” Do not map stored to active.

## Recipe 10: Review an AI diagnostic proposal

Give the model a redacted summary and return a typed, non-mutating proposal:

~~~swift
import Foundation

struct ThreadDiagnosticInput: Sendable {
    let routerTitle: String
    let redactedBorderAgentID: String
    let credentialAgeDays: Int?
    let credentialState: String
    let productHealth: String
    let availableActions: [String]
}

struct ThreadRepairProposal: Sendable {
    let explanation: String
    let action: Action
    let affectedRouterID: String

    enum Action: String, Sendable {
        case inspect
        case update
        case retry
        case remove
        case contactSupport
    }
}

func validate(_ proposal: ThreadRepairProposal,
              input: ThreadDiagnosticInput) throws {
    guard input.availableActions.contains(proposal.action.rawValue) else {
        throw ThreadRouteError.userActionRequired
    }
    guard proposal.affectedRouterID == input.redactedBorderAgentID else {
        throw ThreadRouteError.userActionRequired
    }
}
~~~

The model does not receive network keys, PSKC, operational datasets, or raw diagnostic payloads. A person approves the proposal, then the deterministic coordinator performs one scoped operation. If the model is unavailable, use fixed copy based on the same state.

## Recipe 11: SwiftUI status surface

Use native controls and precise state text:

~~~swift
import SwiftUI

struct BorderRouterStatusView: View {
    let summary: BorderRouterSummary
    let onPrimaryAction: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(summary.title)
                .font(.headline)

            Text(statusText)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .accessibilityLabel("Border Router status")
                .accessibilityValue(statusText)

            Button(primaryTitle, action: onPrimaryAction)
                .buttonStyle(.glassProminent)
        }
        .padding()
        .glassEffect()
    }

    private var statusText: String {
        switch (summary.credentialState, summary.health) {
        case (.stored, .unknown):
            return "Credentials stored; router health not checked"
        case (.stored, .active):
            return "Credentials stored; router active"
        case (.stale, _):
            return "Credential update needed"
        case (.consentRequired, _):
            return "Permission needed"
        case (.denied, _):
            return "Access not granted"
        case (.failed(let message), _):
            return "Could not complete setup: " + message
        default:
            return "Setup in progress"
        }
    }

    private var primaryTitle: String {
        switch summary.credentialState {
        case .consentRequired: return "Continue"
        case .stale: return "Update"
        default: return "View Details"
        }
    }
}
~~~

Confirm the exact Liquid Glass modifiers and availability in the selected iOS 26 SDK. This view is a design/route sketch, not proof that the Thread operation or system consent has occurred.

## Recipe 12: Test fixtures and evidence

Use fixtures for UI state but physical evidence for system claims:

~~~swift
struct ThreadFixture {
    static let storedButUnknown = BorderRouterSummary(
        title: "Living Room Router",
        credentialState: .stored(lastUpdated: nil),
        health: .unknown,
        redactedIdentity: "••••a1b2"
    )

    static let consentNeeded = BorderRouterSummary(
        title: "New Border Router",
        credentialState: .consentRequired,
        health: .unknown,
        redactedIdentity: "••••c3d4"
    )
}
~~~

The fixture can prove layout, text, accessibility identifiers, and action routing. It cannot prove the Apple consent sheet, iCloud Keychain persistence, physical Thread membership, team isolation, or distribution entitlement.

## Compile and proof gates

- Confirm the current ThreadNetwork and THClient signatures in Xcode.
- Compile the main target with the intended capability.
- Inspect the signed entitlement.
- Run availability, consent, denial, store, update, retrieve, and delete on a physical device.
- Use at least one real Border Router and one Thread Resident where the test plan requires it.
- Test two Border Routers and a stale/mismatched dataset.
- Run VoiceOver, Dynamic Type, Reduce Motion, and Reduce Transparency checks.
- Audit logs and AI input for credential redaction.
- Complete Apple’s UX and THClient conformance evidence before claiming release eligibility.

## Sources

- [ThreadNetwork](https://developer.apple.com/documentation/threadnetwork)
- [Getting started with ThreadNetwork](https://developer.apple.com/documentation/threadnetwork/getting-started-with-threadnetwork)
- [Managing Thread network credentials](https://developer.apple.com/documentation/threadnetwork/managing-thread-network-credentials)
- [THClient](https://developer.apple.com/documentation/threadnetwork/thclient)
- [THCredentials](https://developer.apple.com/documentation/threadnetwork/thcredentials)
- [Retrieve credentials for a Border Agent](https://developer.apple.com/documentation/threadnetwork/thclient/retrievecredentials%28forborderagent%3Acompletion%3A%29)
- [Retrieve credentials for an extended PAN ID](https://developer.apple.com/documentation/threadnetwork/thclient/retrievecredentials%28forextendedpanid%3Acompletion%3A%29)
- [Manage Thread Network Credentials entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.manage-thread-network-credentials)
- [Thread Test Plan - THClient API](https://developer.apple.com/apple-home/downloads/Thread-Test-Plan-THClient-API-R1.pdf)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

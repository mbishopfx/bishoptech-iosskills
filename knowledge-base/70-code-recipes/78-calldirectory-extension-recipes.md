# Call Directory extension code recipes

These are compile-oriented route sketches for a containing app plus a Call Directory Extension target. They are not a general Contacts, Phone, call-audio, or live-network lookup API. Confirm the exact signatures against the selected SDK and compile in the named extension target before shipping.

## 1. Provider with ordered identification and blocking entries

~~~swift
import CallKit

final class CallDirectoryProvider: CXCallDirectoryProvider {
    override func beginRequest(with context: CXCallDirectoryExtensionContext) {
        context.delegate = self

        let identifications: [(CXCallDirectoryPhoneNumber, String)] = [
            (12025550101, "Westside Delivery"),
            (12025550102, "Northstar Support")
        ]
        let blocked: [CXCallDirectoryPhoneNumber] = [
            12025550999
        ]

        for (number, label) in identifications.sorted(by: { $0.0 < $1.0 }) {
            context.addIdentificationEntry(
                withNextSequentialPhoneNumber: number,
                label: label
            )
        }

        for number in blocked.sorted() {
            context.addBlockingEntry(
                withNextSequentialPhoneNumber: number
            )
        }

        context.completeRequest(completionHandler: nil)
    }
}

extension CallDirectoryProvider: CXCallDirectoryExtensionContextDelegate {
    func requestFailed(
        for context: CXCallDirectoryExtensionContext,
        withError error: any Error
    ) {
        _ = context
        // Record only a redacted error category and snapshot version.
        _ = error
    }
}
~~~

The numeric fixtures are synthetic. A production provider should load a validated snapshot, reject duplicates and out-of-range values, and keep the two streams independently ordered.

## 2. Full versus incremental request

~~~swift
struct DirectoryDelta: Sendable {
    let removedIdentification: [CXCallDirectoryPhoneNumber]
    let removedBlocking: [CXCallDirectoryPhoneNumber]
    let addedIdentification: [(CXCallDirectoryPhoneNumber, String)]
    let addedBlocking: [CXCallDirectoryPhoneNumber]
    let fullIdentification: [(CXCallDirectoryPhoneNumber, String)]
    let fullBlocking: [CXCallDirectoryPhoneNumber]
}

func emit(_ delta: DirectoryDelta,
          to context: CXCallDirectoryExtensionContext) {
    if context.isIncremental {
        for number in delta.removedIdentification.sorted() {
            context.removeIdentificationEntry(withPhoneNumber: number)
        }
        for number in delta.removedBlocking.sorted() {
            context.removeBlockingEntry(withPhoneNumber: number)
        }
        for (number, label) in delta.addedIdentification.sorted(by: { $0.0 < $1.0 }) {
            context.addIdentificationEntry(
                withNextSequentialPhoneNumber: number,
                label: label
            )
        }
        for number in delta.addedBlocking.sorted() {
            context.addBlockingEntry(
                withNextSequentialPhoneNumber: number
            )
        }
    } else {
        for (number, label) in delta.fullIdentification.sorted(by: { $0.0 < $1.0 }) {
            context.addIdentificationEntry(
                withNextSequentialPhoneNumber: number,
                label: label
            )
        }
        for number in delta.fullBlocking.sorted() {
            context.addBlockingEntry(
                withNextSequentialPhoneNumber: number
            )
        }
    }

    context.completeRequest(completionHandler: nil)
}
~~~

The full branch intentionally does not call a removal method. The delta builder must know which system-loaded baseline it is diffing; if it cannot, route the data through a full rebuild policy instead of guessing.

## 3. Normalize a country-code-plus-digits input

~~~swift
enum NumberNormalizationError: Error {
    case empty
    case invalidCharacters
    case outOfRange
}

func normalizeCallDirectoryNumber(
    _ input: String
) throws -> CXCallDirectoryPhoneNumber {
    let digits = input.filter(\.isNumber)
    guard !digits.isEmpty else { throw NumberNormalizationError.empty }
    guard digits.count == input.filter({ $0 == "+" || $0.isNumber }).count
    else { throw NumberNormalizationError.invalidCharacters }

    guard let number = CXCallDirectoryPhoneNumber(digits),
          number <= CXCallDirectoryPhoneNumberMax
    else { throw NumberNormalizationError.outOfRange }

    return number
}
~~~

This is a product-level normalization sketch, not a complete international phone-number parser. Define country handling explicitly, test it with the product’s supported regions, and do not strip characters in a way that changes the intended number.

## 4. Containing-app manager status and reload

~~~swift
import CallKit

@MainActor
final class CallDirectoryManagerModel: ObservableObject {
    @Published private(set) var status: CXCallDirectoryManager.EnabledStatus = .unknown
    @Published private(set) var lastError: String?

    private let manager = CXCallDirectoryManager.sharedInstance

    func refreshStatus(extensionIdentifier: String) {
        manager.getEnabledStatusForExtension(withIdentifier: extensionIdentifier) {
            [weak self] status, error in
            Task { @MainActor in
                self?.status = status
                self?.lastError = error.map { String(describing: type(of: $0)) }
            }
        }
    }

    func reload(extensionIdentifier: String) {
        manager.reloadExtension(withIdentifier: extensionIdentifier) { [weak self] error in
            Task { @MainActor in
                self?.lastError = error.map { String(describing: type(of: $0)) }
            }
        }
    }

    func openSettings() {
        manager.openSettings { [weak self] error in
            Task { @MainActor in
                self?.lastError = error.map { String(describing: type(of: $0)) }
            }
        }
    }
}
~~~

Use the extension target’s actual bundle identifier. Status, reload completion, and a later physical Phone match are separate evidence fields.

## 5. SwiftUI setup surface

~~~swift
import SwiftUI
import CallKit

struct CallDirectorySettingsView: View {
    @ObservedObject var model: CallDirectoryManagerModel
    let extensionIdentifier: String

    var body: some View {
        Form {
            Section("Call Directory") {
                Text(statusText)
                Text("Caller ID and blocked numbers use a stored system directory.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            Section {
                Button("Reload directory") {
                    model.reload(extensionIdentifier: extensionIdentifier)
                }
                Button("Open Call Blocking & Identification Settings") {
                    model.openSettings()
                }
            }
        }
        .navigationTitle("Caller protection")
    }

    private var statusText: String {
        switch model.status {
        case .unknown: "System status unknown"
        case .disabled: "Extension disabled"
        case .enabled: "Extension enabled"
        @unknown default: "System status unavailable"
        }
    }
}
~~~

Add Liquid Glass only around this containing-app status/review surface after the semantic hierarchy works in a plain Form. Do not recreate the Phone call screen.

## 6. Validate a model proposal before emission

~~~swift
struct DirectoryProposal: Sendable {
    enum Action: Sendable { case identify(label: String), block }
    let number: CXCallDirectoryPhoneNumber
    let action: Action
    let confidence: Double
}

func accepts(
    _ proposal: DirectoryProposal,
    minimumConfidence: Double,
    blockRequiresExplicitApproval: Bool,
    explicitBlockApproval: Bool
) -> Bool {
    guard proposal.number <= CXCallDirectoryPhoneNumberMax,
          proposal.confidence >= minimumConfidence else { return false }

    if case .identify(let label) = proposal.action {
        return !label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    return !blockRequiresExplicitApproval || explicitBlockApproval
}
~~~

The proposal is not yet a Call Directory entry. Sort and deduplicate after validation, attach source/freshness metadata, and add it to a snapshot only after the product’s review policy accepts it.

## 7. Local ordering and delta tests

~~~swift
import Testing

@Test
func emitsOrderedStreamsAndNoFullRequestRemovals() {
    let identification: [CXCallDirectoryPhoneNumber] = [12025550102, 12025550101]
    let blocked: [CXCallDirectoryPhoneNumber] = [12025550999, 12025550100]

    #expect(identification.sorted() == [12025550101, 12025550102])
    #expect(blocked.sorted() == [12025550100, 12025550999])
}
~~~

This test proves only local ordering logic. Add an extension-target integration test for full and incremental context fixtures, then a signed device/system test for actual Phone behavior.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Identifying and blocking calls](https://developer.apple.com/documentation/callkit/identifying-and-blocking-calls)
- [CXCallDirectoryProvider](https://developer.apple.com/documentation/callkit/cxcalldirectoryprovider)
- [beginRequest(with:)](https://developer.apple.com/documentation/CallKit/CXCallDirectoryProvider/beginRequest%28with%3A%29)
- [CXCallDirectoryExtensionContext](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext)
- [isIncremental](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/isincremental)
- [addIdentificationEntry(withNextSequentialPhoneNumber:label:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/addidentificationentry%28withnextsequentialphonenumber%3Alabel%3A%29)
- [addBlockingEntry(withNextSequentialPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/addblockingentry%28withnextsequentialphonenumber%3A%29)
- [removeIdentificationEntry(withPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/removeidentificationentry%28withphonenumber%3A%29)
- [removeBlockingEntry(withPhoneNumber:)](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext/removeblockingentry%28withphonenumber%3A%29)
- [CXCallDirectoryExtensionContextDelegate](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontextdelegate)
- [CXCallDirectoryManager](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager)
- [CXCallDirectoryManager.EnabledStatus](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager/enabledstatus)
- [reloadExtension(withIdentifier:completionHandler:)](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager/reloadextension%28withidentifier%3Acompletionhandler%3A%29)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Swift Testing](https://developer.apple.com/documentation/testing)

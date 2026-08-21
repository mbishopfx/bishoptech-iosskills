# SwiftUI Contacts store and change-history recipes

These are compile-oriented route sketches for an iOS 26 target. They use the
native Contacts framework for authorized direct access, keep keys and identity
explicit, isolate the Objective-C-only change-history enumerator, and keep
on-device AI output as a typed proposal. They do not claim that a simulator,
permission Boolean, or local save proves a physical Contacts workflow.

## 1. Map authorization without collapsing limited access

The authorization state is a domain value. Keep it separate from whether a
particular query has returned a record.

~~~swift
import Contacts

enum ContactsAccessState: Equatable, Sendable {
    case notDetermined
    case restricted
    case denied
    case limited
    case authorized
    case unknown
}

struct ContactsAuthorization {
    static func current() -> ContactsAccessState {
        switch CNContactStore.authorizationStatus(for: .contacts) {
        case .notDetermined:
            return .notDetermined
        case .restricted:
            return .restricted
        case .denied:
            return .denied
        case .limited:
            return .limited
        case .authorized:
            return .authorized
        @unknown default:
            return .unknown
        }
    }

    static func request() async throws -> ContactsAccessState {
        let store = CNContactStore()
        _ = try await store.requestAccess(for: .contacts)
        return current()
    }
}
~~~

The returned state does not say which records or fields are visible. The
feature must still resolve the current identifier with the keys it needs.

## 2. Define a field-minimized key policy

Keep key selection in one app-owned policy so a view cannot silently broaden a
fetch.

~~~swift
import Contacts

enum ContactKeyPolicy {
    static let identifier: [any CNKeyDescriptor] = [
        CNContactIdentifierKey as CNKeyDescriptor
    ]

    static let displayName: [any CNKeyDescriptor] = [
        CNContactIdentifierKey as CNKeyDescriptor,
        CNContactFormatter.descriptorForRequiredKeys(for: .fullName)
    ]

    static let phoneAction: [any CNKeyDescriptor] = [
        CNContactIdentifierKey as CNKeyDescriptor,
        CNContactFormatter.descriptorForRequiredKeys(for: .fullName),
        CNContactPhoneNumbersKey as CNKeyDescriptor
    ]

    static let emailAction: [any CNKeyDescriptor] = [
        CNContactIdentifierKey as CNKeyDescriptor,
        CNContactFormatter.descriptorForRequiredKeys(for: .fullName),
        CNContactEmailAddressesKey as CNKeyDescriptor
    ]
}
~~~

If a formatter or view reads a field not represented by the selected policy,
make that a code-review error rather than fetching every contact property.

## 3. Search with a supported predicate and bounded keys

Contacts provides its own predicates. Do not pass an arbitrary compound
predicate and expect the Contacts store to execute it.

~~~swift
import Contacts

struct ContactSearchResult: Identifiable, Sendable {
    let id: String
    let displayName: String
}

func searchContacts(
    store: CNContactStore,
    name: String
) throws -> [ContactSearchResult] {
    let request = CNContactFetchRequest(keysToFetch: ContactKeyPolicy.displayName)
    request.predicate = CNContact.predicateForContacts(matchingName: name)
    request.unifyResults = true
    request.mutableObjects = false
    request.sortOrder = .userDefault

    var result: [ContactSearchResult] = []
    try store.enumerateContacts(with: request) { contact, _ in
        let formatter = CNContactFormatter()
        let displayName = formatter.string(from: contact) ?? contact.identifier
        result.append(
            ContactSearchResult(
                id: contact.identifier,
                displayName: displayName
            )
        )
    }
    return result
}
~~~

Run this synchronous I/O on a background executor or actor-owned service. An
empty result is a query result, not a reliable explanation of authorization,
limited access, account state, or fetch failure.

## 4. Resolve a bounded batch by identifiers

Resolve the current records immediately before an action. The identifier is an
integration reference, not permission to read arbitrary fields.

~~~swift
import Contacts

func resolveContacts(
    store: CNContactStore,
    identifiers: [String],
    keys: [any CNKeyDescriptor]
) throws -> [CNContact] {
    let uniqueIDs = Array(Set(identifiers))
    guard !uniqueIDs.isEmpty else { return [] }

    let predicate = CNContact.predicateForContacts(
        withIdentifiers: uniqueIDs
    )
    return try store.unifiedContacts(
        matching: predicate,
        keysToFetch: keys
    )
}
~~~

If the result has fewer records than requested, preserve the missing IDs as a
stale/revoked outcome. Do not replace them with a same-name result.

## 5. Observe store changes and cancel stale reloads

The notification is a signal. This coordinator turns it into a debounced
projection reload and invalidates older tasks.

~~~swift
import Contacts
import Foundation

actor ContactProjectionCoordinator {
    private let store: CNContactStore
    private var reloadTask: Task<Void, Never>?
    private var generation = 0

    init(store: CNContactStore = CNContactStore()) {
        self.store = store
    }

    func storeChanged() {
        generation &+= 1
        let requestGeneration = generation
        reloadTask?.cancel()
        reloadTask = Task { [weak self] in
            do {
                try await Task.sleep(for: .milliseconds(150))
                try Task.checkCancellation()
                guard let self else { return }
                await self.reloadIfCurrent(generation: requestGeneration)
            } catch is CancellationError {
                return
            } catch {
                return
            }
        }
    }

    private func reloadIfCurrent(generation requestGeneration: Int) {
        guard requestGeneration == generation else { return }
        // Fetch identifiers and visible fields off the main actor here.
        // Replace the app-owned projection atomically.
    }
}

final class ContactStoreObserver {
    private let center: NotificationCenter
    private var token: NSObjectProtocol?
    private let onChange: @Sendable () -> Void

    init(
        center: NotificationCenter = .default,
        onChange: @escaping @Sendable () -> Void
    ) {
        self.center = center
        self.onChange = onChange
        token = center.addObserver(
            forName: Notification.Name.CNContactStoreDidChange,
            object: nil,
            queue: nil
        ) { [onChange] _ in
            onChange()
        }
    }

    deinit {
        if let token {
            center.removeObserver(token)
        }
    }
}
~~~

The actual app should retain the observer for the feature lifetime. If the
notification fires, re-fetch cached contacts and release the old objects as
Apple documents. Do not call the callback “synced.”

## 6. Configure a change-history request in Swift

The request object and reducer policy are usable from Swift. The actual
enumerator call is intentionally not shown here because Apple marks it
unavailable in Swift.

~~~swift
import Contacts
import Foundation

struct ContactHistoryRequestPolicy: Sendable {
    let startingToken: Data?
    let transactionAuthor: String?
    let includeGroups: Bool
    let unifyResults: Bool

    func makeRequest() -> CNChangeHistoryFetchRequest {
        let request = CNChangeHistoryFetchRequest()
        request.startingToken = startingToken
        request.additionalContactKeyDescriptors = [
            CNContactIdentifierKey as CNKeyDescriptor,
            CNContactFormatter.descriptorForRequiredKeys(for: .fullName)
        ]
        request.includeGroupChanges = includeGroups
        request.shouldUnifyResults = unifyResults
        request.mutableObjects = false
        if let transactionAuthor {
            request.excludedTransactionAuthors = [transactionAuthor]
        }
        return request
    }
}

struct ContactHistoryCheckpoint: Codable, Equatable, Sendable {
    let token: Data
    let projectionRevision: Int
}
~~~

Save a new checkpoint only after the full bridge event batch has been applied.
If the bridge reports changeHistoryExpired, changeHistoryInvalidAnchor, or
changeHistoryInvalidFetchRequest, clear the old checkpoint and rebuild.

## 7. Isolate the Objective-C change-history enumerator

Apple’s TN3149 documents this bridge because
enumeratorForChangeHistoryFetchRequest:error: is unavailable in Swift. Keep
the adapter narrow and return app-owned DTOs rather than leaking mutable
Contacts objects across the module boundary.

~~~objective-c
#import <Contacts/Contacts.h>

@interface BTContactsHistoryBridge : NSObject
- (nullable NSData *)fetchAfterToken:(nullable NSData *)token
                               error:(NSError * _Nullable * _Nullable)error;
@end

@interface BTContactsHistoryVisitor : NSObject <CNChangeHistoryEventVisitor>
@property(nonatomic, strong) NSMutableArray<NSString *> *kinds;
@end

@implementation BTContactsHistoryVisitor
- (instancetype)init {
    self = [super init];
    if (self) {
        _kinds = [NSMutableArray array];
    }
    return self;
}
- (void)visitDropEverythingEvent:(CNChangeHistoryDropEverythingEvent *)event {
    [self.kinds addObject:@"dropEverything"];
}
- (void)visitAddContactEvent:(CNChangeHistoryAddContactEvent *)event {
    [self.kinds addObject:@"addContact"];
}
- (void)visitUpdateContactEvent:(CNChangeHistoryUpdateContactEvent *)event {
    [self.kinds addObject:@"updateContact"];
}
- (void)visitDeleteContactEvent:(CNChangeHistoryDeleteContactEvent *)event {
    [self.kinds addObject:@"deleteContact"];
}
- (void)visitAddGroupEvent:(CNChangeHistoryAddGroupEvent *)event {
    [self.kinds addObject:@"addGroup"];
}
- (void)visitUpdateGroupEvent:(CNChangeHistoryUpdateGroupEvent *)event {
    [self.kinds addObject:@"updateGroup"];
}
- (void)visitDeleteGroupEvent:(CNChangeHistoryDeleteGroupEvent *)event {
    [self.kinds addObject:@"deleteGroup"];
}
- (void)visitAddMemberToGroupEvent:(CNChangeHistoryAddMemberToGroupEvent *)event {
    [self.kinds addObject:@"addMemberToGroup"];
}
- (void)visitRemoveMemberFromGroupEvent:(CNChangeHistoryRemoveMemberFromGroupEvent *)event {
    [self.kinds addObject:@"removeMemberFromGroup"];
}
- (void)visitAddSubgroupToGroupEvent:(CNChangeHistoryAddSubgroupToGroupEvent *)event {
    [self.kinds addObject:@"addSubgroupToGroup"];
}
- (void)visitRemoveSubgroupFromGroupEvent:(CNChangeHistoryRemoveSubgroupFromGroupEvent *)event {
    [self.kinds addObject:@"removeSubgroupFromGroup"];
}
@end

@implementation BTContactsHistoryBridge {
    CNContactStore *_store;
}
- (instancetype)init {
    self = [super init];
    if (self) {
        _store = [[CNContactStore alloc] init];
    }
    return self;
}
- (NSData *)fetchAfterToken:(NSData *)token
                       error:(NSError **)error {
    CNChangeHistoryFetchRequest *request =
        [[CNChangeHistoryFetchRequest alloc] init];
    request.startingToken = token;
    request.shouldUnifyResults = YES;
    request.includeGroupChanges = NO;
    request.additionalContactKeyDescriptors = @[
        CNContactIdentifierKey,
        [CNContactFormatter descriptorForRequiredKeysForStyle:
            CNContactFormatterStyleFullName]
    ];

    BTContactsHistoryVisitor *visitor =
        [[BTContactsHistoryVisitor alloc] init];
    CNFetchResult<NSEnumerator<CNChangeHistoryEvent *> *> *result =
        [_store enumeratorForChangeHistoryFetchRequest:request error:error];
    if (result == nil) {
        return nil;
    }
    for (CNChangeHistoryEvent *event in result.value) {
        [event acceptEventVisitor:visitor];
    }
    // Expose visitor.kinds and result.currentHistoryToken in the real bridge
    // DTO. The token is opaque and must not be interpreted by the app.
    return result.currentHistoryToken;
}
@end
~~~

The Objective-C bridge must be compiled in the actual target. This snippet
shows the API boundary; a production adapter should return typed event DTOs,
map NSError values, bound event batches, and make the token/DTO commit
transactional with the app projection.

## 8. Reduce bridge events into app-owned state

The Swift reducer can remain deterministic even though the framework fetch is
performed by Objective-C.

~~~swift
import Foundation

enum ContactHistoryEventDTO: Equatable, Sendable {
    case dropEverything
    case add(id: String, displayName: String?)
    case update(id: String, displayName: String?)
    case delete(id: String)
    case groupChange
}

struct ContactProjection: Equatable, Sendable {
    var records: [String: String]
    var revision: Int
}

func apply(
    _ events: [ContactHistoryEventDTO],
    to projection: inout ContactProjection
) {
    for event in events {
        switch event {
        case .dropEverything:
            projection.records.removeAll()
        case let .add(id, displayName), let .update(id, displayName):
            projection.records[id] = displayName ?? "Unnamed contact"
        case let .delete(id):
            projection.records.removeValue(forKey: id)
        case .groupChange:
            break
        }
    }
    projection.revision += 1
}
~~~

The reducer must not persist the new token before this function and the
projection update succeed. In production, the projection and checkpoint
should be committed together.

## 9. Save a contact and re-resolve after commit

Keep mutable contacts and save requests inside one synchronous commit boundary.

~~~swift
import Contacts

enum ContactMutationFailure: Error, Equatable {
    case recordMissing
    case duplicateInsert
    case noWritableContainer
    case authorization
    case other(String)
}

func addTestContact(
    store: CNContactStore,
    givenName: String,
    familyName: String
) throws -> String {
    let contact = CNMutableContact()
    contact.givenName = givenName
    contact.familyName = familyName

    let request = CNSaveRequest()
    request.add(contact, toContainerWithIdentifier: nil)
    request.transactionAuthor = "com.example.contacts-route"
    request.shouldRefetchContacts = true

    do {
        try store.execute(request)
    } catch let error as NSError where error.domain == CNErrorDomain {
        switch CNError.Code(rawValue: error.code) {
        case .recordDoesNotExist:
            throw ContactMutationFailure.recordMissing
        case .insertedRecordAlreadyExists:
            throw ContactMutationFailure.duplicateInsert
        case .noAccessableWritableContainers:
            throw ContactMutationFailure.noWritableContainer
        case .authorizationDenied, .unauthorizedKeys:
            throw ContactMutationFailure.authorization
        default:
            throw ContactMutationFailure.other(error.localizedDescription)
        }
    }
    return contact.identifier
}
~~~

The returned object is not the app’s final projection. Resolve the identifier
with the display/action keys after the save and persist that minimized result.
For a user-facing feature, use a harmless controlled contact fixture rather
than a hard-coded name in a release route.

## 10. Render a native Liquid Glass review card

Keep material around the review/action cluster and expose the selected field as
plain accessible text.

~~~swift
import SwiftUI

struct ContactReviewCard: View {
    let displayName: String
    let propertyLabel: String
    let propertyValue: String
    let sourceText: String
    let freshnessText: String
    let confirm: () -> Void
    let reselect: () -> Void

    private var accessibilitySummary: String {
        [displayName, propertyLabel, propertyValue, sourceText, freshnessText]
            .joined(separator: ", ")
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(displayName)
                .font(.headline)
            Text(propertyLabel)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(propertyValue)
                .font(.body)
            Text(sourceText)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(freshnessText)
                .font(.caption)
                .foregroundStyle(.secondary)

            HStack {
                Button("Reselect", action: reselect)
                    .buttonStyle(.bordered)
                Button("Confirm", action: confirm)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding(20)
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Contact review")
        .accessibilityValue(accessibilitySummary)
    }
}
~~~

The card is a review surface, not a proof that the contact is still current.
Resolve the ID again in the confirm action and invalidate the card after a
Contacts store change.

## 11. Validate a typed on-device contact proposal

The proposal is app-owned. A local Foundation Models session may produce it,
but the current contact store, revision, and human confirmation control
acceptance.

~~~swift
import Foundation

struct ContactProposal: Codable, Equatable, Sendable {
    let sourceContactID: String
    let sourceProjectionRevision: Int
    let selectedField: String
    let proposedValue: String
    let modelRoute: String
}

enum ContactProposalError: Error {
    case missingSource
    case staleProjection
    case unsupportedField
    case emptyValue
    case notReviewed
}

func validate(
    _ proposal: ContactProposal,
    currentProjectionRevision: Int,
    allowedFields: Set<String>,
    isReviewed: Bool
) throws {
    guard !proposal.sourceContactID.isEmpty else {
        throw ContactProposalError.missingSource
    }
    guard proposal.sourceProjectionRevision == currentProjectionRevision else {
        throw ContactProposalError.staleProjection
    }
    guard allowedFields.contains(proposal.selectedField) else {
        throw ContactProposalError.unsupportedField
    }
    guard !proposal.proposedValue.trimmingCharacters(
        in: .whitespacesAndNewlines
    ).isEmpty else {
        throw ContactProposalError.emptyValue
    }
    guard isReviewed else {
        throw ContactProposalError.notReviewed
    }
}
~~~

Do not treat this validator as a phone-number or identity classifier. It is a
stale-source and review gate; field-specific validation belongs in the
deterministic commit path.

## 12. Swift Testing policy fixtures

These tests exercise app-owned policy only. They do not prove Contacts
authorization, account sync, the Objective-C bridge, physical device behavior,
or release signing.

~~~swift
import Testing

struct ContactPolicyTests {
    @Test("a limited state remains explicit")
    func limitedStateIsNotDenied() {
        #expect(ContactsAccessState.limited != .denied)
    }

    @Test("a drop event clears the projection")
    func dropClearsProjection() {
        var projection = ContactProjection(
            records: ["test-id": "Test Person"],
            revision: 1
        )
        apply([.dropEverything], to: &projection)
        #expect(projection.records.isEmpty)
        #expect(projection.revision == 2)
    }
}
~~~

## Sources

- [Contacts](https://developer.apple.com/documentation/contacts)
- [Accessing the contact store](https://developer.apple.com/documentation/contacts/accessing-the-contact-store)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [CNAuthorizationStatus](https://developer.apple.com/documentation/contacts/cnauthorizationstatus)
- [CNAuthorizationStatus.limited](https://developer.apple.com/documentation/contacts/cnauthorizationstatus/limited)
- [CNContact](https://developer.apple.com/documentation/contacts/cncontact)
- [CNMutableContact](https://developer.apple.com/documentation/contacts/cnmutablecontact)
- [CNContactFetchRequest](https://developer.apple.com/documentation/contacts/cncontactfetchrequest)
- [keysToFetch](https://developer.apple.com/documentation/contacts/cncontactfetchrequest/keystofetch)
- [predicate](https://developer.apple.com/documentation/contacts/cncontactfetchrequest/predicate)
- [unifiedContacts(matching:keysToFetch:)](https://developer.apple.com/documentation/contacts/cncontactstore/unifiedcontacts%28matching%3Akeystofetch%3A%29)
- [CNChangeHistoryFetchRequest](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest)
- [startingToken](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/startingtoken)
- [additionalContactKeyDescriptors](https://developer.apple.com/documentation/contacts/cnchangehistoryfetchrequest/additionalcontactkeydescriptors)
- [CNFetchResult](https://developer.apple.com/documentation/contacts/cnfetchresult)
- [currentHistoryToken](https://developer.apple.com/documentation/contacts/cnfetchresult/currenthistorytoken)
- [CNChangeHistoryEventVisitor](https://developer.apple.com/documentation/contacts/cnchangehistoryeventvisitor)
- [CNSaveRequest](https://developer.apple.com/documentation/contacts/cnsaverequest)
- [transactionAuthor](https://developer.apple.com/documentation/contacts/cnsaverequest/transactionauthor)
- [shouldRefetchContacts](https://developer.apple.com/documentation/contacts/cnsaverequest/shouldrefetchcontacts)
- [CNError](https://developer.apple.com/documentation/contacts/cnerror)
- [ContactProvider](https://developer.apple.com/documentation/contactprovider)
- [ContactAccessButton](https://developer.apple.com/documentation/contactsui/contactaccessbutton)
- [NSContactsUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nscontactsusagedescription)
- [Contacts notes entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.contacts.notes)
- [TN3149: Fetching Contacts change history events](https://developer.apple.com/documentation/technotes/tn3149-fetching-change-history-events)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing in Swift](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)

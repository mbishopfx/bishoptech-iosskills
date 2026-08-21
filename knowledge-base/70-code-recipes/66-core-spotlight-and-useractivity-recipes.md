# Core Spotlight and NSUserActivity recipes

These are compile-oriented route sketches for indexing app-owned records, updating and deleting search projections, protected/domain lifecycle, in-app queries, user activities, continuation, and the preliminary Foundation Models SpotlightSearchTool route.

They are not compiled in this documentation-only workspace and do not prove Spotlight ranking, index persistence, protected-data behavior, Handoff, model availability, Apple Intelligence output, accessibility, or release readiness. Confirm exact API signatures and availability in the selected SDK.

Before copying:

1. Index only content a person expects to find.
2. Use stable opaque identifiers and named indexes.
3. Delete by identifier/domain when source truth changes.
4. Revalidate every search result before opening or mutating it.
5. Treat SpotlightSearchTool/CoreSpotlightSource as availability-sensitive and preliminary where the selected SDK marks them so.

## Recipe 1: Define a searchable projection

Keep source identity and display metadata separate:

~~~swift
import Foundation

struct SearchableRecord: Sendable, Equatable {
    let id: String
    let domainID: String
    let title: String
    let summary: String?
    let keywords: [String]
    let modifiedAt: Date
    let expiresAt: Date?
    let isPrivate: Bool
}

enum SearchDestination: Sendable, Equatable {
    case record(id: String, domainID: String)
    case unavailable(id: String)
}
~~~

The ID must resolve to current source truth. Do not use a token, raw email address, private URL, or recyclable database index as the searchable identifier.

## Recipe 2: Build a CSSearchableItem

Populate only relevant attributes:

~~~swift
import CoreSpotlight
import UniformTypeIdentifiers

func searchableItem(
    for record: SearchableRecord
) -> CSSearchableItem {
    let attributes = CSSearchableItemAttributeSet(
        itemContentType: UTType.text.identifier
    )
    attributes.title = record.title
    attributes.displayName = record.title
    attributes.contentDescription = record.summary
    attributes.keywords = record.keywords
    attributes.contentType = UTType.text.identifier
    attributes.metadataModificationDate = record.modifiedAt

    let item = CSSearchableItem(
        uniqueIdentifier: record.id,
        domainIdentifier: record.domainID,
        attributeSet: attributes
    )
    item.expirationDate = record.expiresAt
    return item
}
~~~

Do not put private source content into keywords or descriptions merely to improve ranking. The attribute set is search metadata and must follow the same privacy policy as the underlying record.

## Recipe 3: Use a named index

Use a named index for production:

~~~swift
import CoreSpotlight

final class SearchIndex {
    let index = CSSearchableIndex(name: "PrimaryContent")

    func upsert(
        _ items: [CSSearchableItem],
        completion: @escaping (Error?) -> Void
    ) {
        index.indexSearchableItems(items, completionHandler: completion)
    }
}
~~~

The completion handler indicates that the indexing request was accepted/journaled according to the framework’s contract. It is not proof that Spotlight currently displays the item.

## Recipe 4: Delete by identifier and domain

Tie deletion to the source lifecycle:

~~~swift
import CoreSpotlight

extension SearchIndex {
    func deleteRecord(
        id: String,
        completion: @escaping (Error?) -> Void
    ) {
        index.deleteSearchableItems(
            withIdentifiers: [id],
            completionHandler: completion
        )
    }

    func deleteDomain(
        _ domainID: String,
        completion: @escaping (Error?) -> Void
    ) {
        index.deleteSearchableItems(
            withDomainIdentifiers: [domainID],
            completionHandler: completion
        )
    }
}
~~~

Use domain deletion for account/workspace removal. Keep an explicit delete-all method only for reset, testing, or a documented rebuild.

## Recipe 5: Use a protected index boundary

Sensitive content may need a named index with a protection class:

~~~swift
import CoreSpotlight

func makeProtectedIndex() -> CSSearchableIndex {
    CSSearchableIndex(
        name: "ProtectedContent",
        protectionClass: .complete
    )
}
~~~

Confirm the selected SDK’s protection-class availability and device behavior. A protected index is not a substitute for source authorization or a delete path.

## Recipe 6: Keep a searchable NSUserActivity

Use a strong owner for a user-touched activity:

~~~swift
import CoreSpotlight
import Foundation

@MainActor
final class ActivityCoordinator {
    private var current: NSUserActivity?

    func becomeCurrent(record: SearchableRecord) {
        let activity = NSUserActivity(
            activityType: "com.example.app.record.view"
        )
        activity.title = record.title
        activity.persistentIdentifier = record.id
        activity.targetContentIdentifier = record.id
        activity.keywords = Set(record.keywords)
        activity.isEligibleForSearch = true
        activity.isEligibleForHandoff = false
        activity.expirationDate = record.expiresAt
        activity.contentAttributeSet = searchableItem(
            for: record
        ).attributeSet
        activity.becomeCurrent()
        current = activity
    }

    func resignCurrent() {
        current?.resignCurrent()
        current = nil
    }
}
~~~

The activity type and identifiers are fixtures. Set public indexing, prediction, and Handoff eligibility only when the product and privacy policy support them.

## Recipe 7: Resolve a searchable item action

Search results must route through current source truth:

~~~swift
import CoreSpotlight
import Foundation

func destination(
    from activity: NSUserActivity,
    lookup: (String) -> SearchDestination?
) -> SearchDestination? {
    guard activity.activityType == CSSearchableItemActionType,
          let identifier = activity.userInfo?[
              CSSearchableItemActivityIdentifier
          ] as? String
    else {
        return nil
    }
    return lookup(identifier)
}
~~~

The exact action user-info bridge can be SDK-sensitive. Keep the invariant: parse the framework activity, look up the current object, check authorization, and show unavailable when the source no longer exists.

## Recipe 8: Run a CSSearchQuery

Use one query for one current search operation:

~~~swift
import CoreSpotlight

final class SearchQueryCoordinator {
    private var query: CSSearchQuery?

    func search(
        text: String,
        onItems: @escaping ([CSSearchableItem]) -> Void,
        onFinish: @escaping (Error?) -> Void
    ) {
        query?.cancel()

        let context = CSSearchQueryContext()
        context.fetchAttributes = [
            "title",
            "displayName",
            "contentDescription"
        ]
        context.maxResultCount = 20

        let query = CSSearchQuery(
            queryString: text,
            queryContext: context
        )
        query.foundItemsHandler = { items in
            onItems(items)
        }
        query.completionHandler = { error in
            onFinish(error)
        }
        self.query = query
        query.start()
    }

    func cancel() {
        query?.cancel()
        query = nil
    }
}
~~~

Confirm the selected SDK’s context attribute names and handler isolation. Cancel from new input, disappearance, and task teardown so stale results cannot replace current results.

## Recipe 9: Debounce a CSUserQuery route

Use a new user query after a short input pause:

~~~swift
import CoreSpotlight

final class UserSuggestionCoordinator {
    private var query: CSUserQuery?
    private var workItem: DispatchWorkItem?

    func update(text: String) {
        workItem?.cancel()
        query?.cancel()

        let work = DispatchWorkItem { [weak self] in
            let context = CSUserQueryContext()
            context.maxResultCount = 10
            context.maxSuggestionCount = 5
            let query = CSUserQuery(
                userQueryString: text,
                userQueryContext: context
            )
            query.foundSuggestionsHandler = { suggestions in
                _ = suggestions
            }
            self?.query = query
            query.start()
        }
        workItem = work
        DispatchQueue.main.asyncAfter(
            deadline: .now() + .milliseconds(180),
            execute: work
        )
    }

    func cancel() {
        workItem?.cancel()
        query?.cancel()
        workItem = nil
        query = nil
    }
}
~~~

The exact suggestion handler and context properties can be SDK-sensitive. Do not record “engagement” until the person chooses a suggestion/result.

## Recipe 10: Configure Foundation Models with SpotlightSearchTool

The simplest official route gives a language-model session a Spotlight search tool:

~~~swift
import CoreSpotlight
import FoundationModels

func makeLanguageSession() -> LanguageModelSession {
    let tool = SpotlightSearchTool()
    return LanguageModelSession(tools: [tool])
}
~~~

For a privacy-scoped source, configure SpotlightSearchTool with a CoreSpotlightSource and fetch only the attributes the model needs. The exact configuration spelling and availability are preliminary/SDK-sensitive; keep a fallback:

~~~swift
import CoreSpotlight
import FoundationModels

func makeScopedTool() -> SpotlightSearchTool {
    let source = CoreSpotlightSource(
        fetchAttributes: [.title, .contentDescription]
    )
    source.maximumResultCount = 8

    // Confirm the current SDK initializer and source option spelling.
    return SpotlightSearchTool()
}
~~~

Do not silently use a default broad source when the feature’s privacy policy requires a constrained one. Verify which source is actually attached in the target SDK.

## Recipe 11: Validate a model proposal against current source

Keep search retrieval and side effects separate:

~~~swift
struct IndexedContext: Sendable, Equatable {
    let recordID: String
    let domainID: String
    let title: String
    let sourceVersion: String
}

enum SearchProposal: Sendable, Equatable {
    case open
    case draftTag(String)
    case delete
}

enum SearchProposalError: Error {
    case stale
    case unauthorized
    case confirmationRequired
}

struct SearchProposalValidator {
    func validate(
        _ proposal: SearchProposal,
        context: IndexedContext,
        currentVersion: String,
        authorized: Bool,
        confirmed: Bool
    ) throws {
        guard context.sourceVersion == currentVersion else {
            throw SearchProposalError.stale
        }
        guard authorized else {
            throw SearchProposalError.unauthorized
        }
        if case .delete = proposal, !confirmed {
            throw SearchProposalError.confirmationRequired
        }
    }
}
~~~

The model cannot invent a record ID, reopen an expired item, or turn ranking into permission.

## Recipe 12: Keep indexing and AI evidence semantic

Record metadata, not private content:

~~~swift
struct SpotlightEvidence: Sendable, Equatable {
    let indexName: String
    let operation: String
    let itemID: String?
    let domainID: String?
    let resultState: String
    let modelToolUsed: Bool
    let timestamp: Date
    let device: String
}
~~~

Pair the evidence with current source lookup, target/index configuration, physical Spotlight or continuation proof, privacy state, accessibility tasks, and the final signed artifact.

## Sources

- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableItem](https://developer.apple.com/documentation/corespotlight/cssearchableitem)
- [CSSearchableItemAttributeSet](https://developer.apple.com/documentation/corespotlight/cssearchableitemattributeset)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSSearchableIndexDelegate](https://developer.apple.com/documentation/corespotlight/cssearchableindexdelegate?changes=la_5_3_4&language=objc)
- [CSSearchQuery](https://developer.apple.com/documentation/corespotlight/cssearchquery)
- [CSUserQuery](https://developer.apple.com/documentation/corespotlight/csuserquery)
- [Adding your app’s content to Spotlight indexes](https://developer.apple.com/documentation/corespotlight/adding-your-app-s-content-to-spotlight-indexes)
- [Building a search interface for your app](https://developer.apple.com/documentation/corespotlight/building-a-search-interface-for-your-app)
- [Searching for information in your app](https://developer.apple.com/documentation/corespotlight/searching-for-information-in-your-app)
- [Regenerating your app’s indexes on demand](https://developer.apple.com/documentation/corespotlight/regenerating-your-app-s-indexes-on-demand)
- [Spotlight search tool](https://developer.apple.com/documentation/corespotlight/spotlight-search-tool)
- [SpotlightSearchTool](https://developer.apple.com/documentation/corespotlight/spotlightsearchtool)
- [CoreSpotlightSource](https://developer.apple.com/documentation/corespotlight/corespotlightsource)
- [Making your indexed content available to Foundation Models](https://developer.apple.com/documentation/corespotlight/making-your-indexed-content-available-to-foundation-models)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [eligibleForSearch](https://developer.apple.com/documentation/foundation/nsuseractivity/iseligibleforsearch)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

# Core Spotlight, NSUserActivity, and on-device discoverability

Core Spotlight lets an app describe content for an on-device index so people can find it from Spotlight and from search interfaces inside the app. NSUserActivity represents user-touched activities for search, Handoff, prediction, and universal-link continuation. Foundation Models can optionally use a SpotlightSearchTool to query an app’s indexed content as additional context.

Use this deep dive when an app needs to:

- make user-relevant records discoverable from Spotlight;
- keep indexed items synchronized with app-owned create/update/delete state;
- delete an account or privacy domain from the index;
- search the app’s own content with lexical or semantic queries;
- offer query suggestions and cancel stale searches;
- continue a result into a native route or Handoff activity;
- provide selected indexed attributes to an on-device language model;
- keep private, protected, expired, and user-controlled content out of search.

Search is a discoverability and retrieval route. It is not an authorization system, a database, a backup, an analytics ranking guarantee, or proof that the content still exists.

## Choose the indexing route

| Product need | Route | Boundary |
| --- | --- | --- |
| Index app-owned records | CSSearchableItem and CSSearchableIndex | App maintains the index and stable identifiers |
| Reflect a person’s recent interaction | NSUserActivity | Index only content the person touched; keep a strong reference |
| Search the app’s index in a native search UI | CSSearchQuery | One query per operation; cancel stale work |
| Search and suggest completions from user-entered text | CSUserQuery | Debounce input and record engagement separately |
| Continue an item or Handoff activity | NSUserActivity continuation | Stable identifiers and safe route validation |
| Provide content to Foundation Models | SpotlightSearchTool and CoreSpotlightSource | Indexed attributes, source options, model/tool availability |
| Maintain the index when the app is not running | Reindexing extension | Extension target, lifecycle, and protected-data proof |
| Index AppEntity values | Current Core Spotlight/App Intents interoperability | SDK availability and stable entity identity |

Do not index every database row by default. Apple’s guidance emphasizes content that people care about or interact with directly.

## Private on-device index ownership

Core Spotlight indexes are app-specific and remain on the device. The app is responsible for:

- choosing content and fields;
- creating stable unique identifiers;
- choosing domain identifiers for deletion groups;
- updating items when source data changes;
- expiring or deleting items when source data disappears;
- maintaining the index when the app is not running where required;
- redacting private, sensitive, or account-specific metadata;
- handling a search result that points to missing or unauthorized content.

The system owns:

- Spotlight ranking and presentation;
- search surface availability;
- indexing scheduling and asynchronous journaling;
- system summaries or prioritization where supported;
- delivery of continuation activities and system context.

An indexed item is a projection. The source of truth remains the app’s durable data and authorization layer.

## CSSearchableItem identity

Each item should have:

| Field | Policy |
| --- | --- |
| uniqueIdentifier | Stable app-local identity; never recycle for different content |
| domainIdentifier | Account, workspace, mailbox, or content-owner grouping for deletion |
| attributeSet | Only fields that help a person find or understand the item |
| expirationDate | Time after which a temporary item should no longer be eligible |
| contentURL | Local file URL only when the item is a file and the app can resolve it |
| related identifiers | Link to an app entity or associated content where supported |
| display metadata | Localized title, display name, content type, keywords, thumbnail |

Use an identifier that can resolve back to the current domain object. Do not put secrets, raw tokens, private URL query strings, or unbounded text in the identifier.

The attribute set is mutable reference data. Modify one attribute-set instance on one thread at a time.

## CSSearchableIndex lifecycle

The normal lifecycle is:

1. create a named index;
2. map source records to searchable items;
3. index items when source data is created or changed;
4. batch large updates where appropriate;
5. delete by identifier when a record is deleted;
6. delete by domain when an account/workspace is removed;
7. delete all only for reset or development behavior;
8. provide reindexing support when the app needs to recover after index loss;
9. record completion as “journaled/accepted” versus content actually searchable;
10. verify the native result before opening a route.

Apple’s documentation says the default index is for prototyping and testing. Production code should use a named index and a clear protection policy. More sensitive content can use a protection class and separate index boundary when the selected SDK supports it.

## Batch and reindex boundaries

Large updates should be batched to make recovery possible. Keep client state small and deterministic, and record the last successfully journaled state.

If the index is missing, stale, or invalid:

1. the reindexing request arrives;
2. the app or index extension enumerates current source records;
3. it produces a complete projection with current authorization;
4. it ends the reindex operation;
5. it deletes or ignores records that no longer exist;
6. it records the new client state.

An index extension is its own target and process boundary. Do not assume the main app’s in-memory stores, actor state, or UI are available inside the extension.

## NSUserActivity

Use NSUserActivity for a user-touched activity or continuation, not as a replacement for indexing the app’s content.

Important fields include:

- activityType;
- title;
- persistentIdentifier;
- targetContentIdentifier;
- contentAttributeSet;
- keywords;
- webpageURL;
- userInfo;
- eligibleForSearch;
- eligibleForHandoff;
- eligibleForPrediction;
- eligibleForPublicIndexing;
- expirationDate;
- needsSave.

Keep a strong reference to activity objects made eligible for search. Maintain stable identifiers across devices when the activity needs Handoff, notes, or long-lived continuation.

Use eligibleForSearch only when the activity represents something a person actually touched. Use public indexing only when the content and website/app policy allow it. Use expiration for temporary states.

## Search queries

CSSearchQuery searches indexed app content using a query string and query context. Each query is a single operation:

- create a new query when search intent changes;
- cancel the previous query;
- limit requested attributes and result count;
- observe result batches;
- handle completion and error;
- resolve each result against current authorization and source truth.

CSUserQuery adds user-entered search and suggested text completions. Debounce keystrokes so an old query does not continue after the user changes the term. Record user engagement only when the person actually chooses a result or suggestion.

A system result is not authorization. Opening a result must re-check account, protected data, expiration, and current object existence.

## Protected and private content

Decide per content class:

| Content | Default indexing posture |
| --- | --- |
| Public product catalog | Index useful metadata with stable routes |
| Personal notes | Index only if the person expects device search |
| Health or therapy records | Use protected index and explicit privacy policy, or do not index |
| Account workspace | Include domain identifier for deletion and account switching |
| Draft or deleted item | Expire/delete promptly |
| Sensitive file | Use protection class and scoped content URL only where supported |
| Shared content | Avoid indexing private account details into public or broad surfaces |

Searchable metadata is still personal data. A private on-device index reduces network exposure but does not remove the need for access control, deletion, disclosure, or retention policy.

## Foundation Models SpotlightSearchTool

The Foundation Models framework can use a SpotlightSearchTool as an additional source of app-specific context. The tool searches the app’s Spotlight index and can be configured with:

- a CoreSpotlightSource;
- fetched searchable attributes;
- maximum result count;
- source options for restricted content;
- a CSSearchableIndexDelegate for additional item-specific data where supported;
- guidance about the search techniques and compactness appropriate for the app.

This integration is powerful and source-sensitive:

- index the content before the model can retrieve it;
- expose only attributes needed for the prompt;
- use a delegate only with a safe, concurrency-aware data source;
- keep restricted content behind explicit source options;
- do not provide the model with private attributes merely because they exist in the item;
- validate every model proposal against current source truth and authorization.

The current Apple documentation marks parts of SpotlightSearchTool/CoreSpotlightSource and related searchable-item attribute APIs as preliminary. Check the selected SDK, availability, and final OS before relying on them.

## Apple Intelligence summaries and priority

For supported indexed mail, messages, or audio transcripts, Spotlight and Apple Intelligence can generate summary or priority data. The app can receive item updates through CSSearchableIndexDelegate or an index extension where supported.

Keep generated summaries separate from:

- source transcript/audio;
- user-authored metadata;
- model revision and provenance;
- a verified domain event;
- a medical, safety, or legal interpretation.

An Apple Intelligence summary is system-generated context, not a guarantee of correctness or a reason to expose a sensitive item more broadly.

## Native Liquid Glass search design

Use Liquid Glass around app-owned search controls and review surfaces:

- search field and scope picker;
- result filters and recency controls;
- a selected result’s native action group;
- an AI answer review card showing sources and uncertainty.

Do not recreate Spotlight’s system UI inside the app or imply that a glass result card has system ranking authority. Keep source title, domain, freshness, authorization state, and action visible.

## On-device AI route

Use:

search request -> indexed item IDs/attributes -> current source lookup -> redacted context -> model response/proposal -> user review -> deterministic action

The model may:

- answer a question about approved indexed notes;
- summarize selected results;
- propose a native route for a verified item;
- draft a tag or follow-up.

The model may not:

- use stale indexed metadata as current authorization;
- infer that a deleted or private item still exists;
- expose content from a restricted index;
- invent an item ID or native action;
- silently write, delete, send, or purchase.

## Proof boundary

| Claim | Required evidence |
| --- | --- |
| Item is indexed | Named index, item metadata, journaled completion, physical search result |
| Item stays current | Source update/delete, re-query, expiration, missing-item recovery |
| Account deletion clears search | Domain deletion, current search, account-switch proof |
| Protected content is protected | Named/protected index, target configuration, locked/protected-data test |
| User activity is searchable | Strong activity owner, eligible state, physical Spotlight result |
| Handoff/universal continuation works | Stable ID, continuation activity, physical device route |
| Query cancellation works | Rapid input changes, canceled stale query, current result only |
| AI retrieves app content | Indexed fixture, configured tool/source, redacted model context |
| AI stays bounded | Restricted-source test, typed proposal, authorization and confirmation |
| Release is ready | Final signed target/index extension, privacy/accessibility and device proof |

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
- [Generating summary and priority data for indexed items](https://developer.apple.com/documentation/corespotlight/generating-summary-and-priority-data-for-indexed-items)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [eligibleForSearch](https://developer.apple.com/documentation/foundation/nsuseractivity/iseligibleforsearch)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

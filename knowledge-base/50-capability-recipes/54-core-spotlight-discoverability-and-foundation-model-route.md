# Core Spotlight discoverability and Foundation Models route

Use this route to index app-owned content, continue user activities, search the app’s private on-device index, and optionally make selected indexed attributes available to Foundation Models.

This is a compile-oriented capability route. It does not prove Spotlight ranking, system presentation, index persistence after OS events, Handoff delivery, protected-data behavior, model availability, Apple Intelligence output, or release readiness.

## Route selector

| Outcome | Primary API | Keep separate |
| --- | --- | --- |
| Index app records | CSSearchableItem and CSSearchableIndex | Durable source truth and stable IDs |
| Index a recent user-touched activity | NSUserActivity | Activity lifecycle and strong reference |
| Search a known query | CSSearchQuery | Cancellation, result batches, authorization |
| Suggest text completions | CSUserQuery | Debounce and engagement |
| Continue a record or Handoff task | NSUserActivity | Stable IDs and destination validation |
| Expose app content to Foundation Models | SpotlightSearchTool and CoreSpotlightSource | Selected attributes, restrictions, model availability |
| Rebuild a lost index | CSSearchIndexDelegate/reindex extension | Extension target and process boundary |
| Index AppEntity content | Current Core Spotlight/App Intents interoperability | SDK and preliminary API availability |

## Target register

| Field | Decision |
| --- | --- |
| Target | Bundle ID, app/extension targets, SDK, deployment target |
| Index | Named index, protection class, domain identifiers |
| Content | Record types, fields, stable ID strategy, expiration |
| Activity | User-touched activity types, Handoff/public/prediction eligibility |
| Query | In-app search, suggestions, predicates, result limits, cancellation |
| Reindex | Extension target, enumeration source, client-state recovery |
| AI | Foundation Models availability, SpotlightSearchTool source, fetched attributes |
| Privacy | Sensitive fields, protected index, account deletion, logging |
| Native route | Result-to-screen map, authorization, missing/expired fallback |
| Evidence | Physical Spotlight, device lock/protection, continuation, signed artifact |

Use the default CSSearchableIndex only for prototyping/testing. Name the production index and document the protection policy.

## Ownership graph

Domain store -> searchable projection -> named index -> system/in-app search -> identifier lookup -> current authorized source -> native route

User interaction -> NSUserActivity -> system indexing/Handoff -> continuation activity -> route validation -> current source

Indexed attributes -> CoreSpotlightSource -> SpotlightSearchTool -> Foundation Models session -> generated answer/proposal -> source lookup -> review/commit

The index is a cache-like discoverability projection. It should never be the only place the app can reconstruct a record or authorize an action.

## Route A: index and update

1. identify content the person cares about;
2. create a CSSearchableItemAttributeSet with localized useful metadata;
3. create a stable CSSearchableItem with unique and domain identifiers;
4. set expiration for temporary content;
5. submit to a named CSSearchableIndex;
6. update the item whenever source metadata changes;
7. delete by identifier when a source record is deleted;
8. delete by domain when an account/workspace is removed;
9. batch large updates and store small client state;
10. add reindex support for index loss.

The completion callback indicates that an indexing request was accepted/journaled, not that a system surface currently displays the item.

## Route B: secure item grouping

Use domainIdentifier to group items:

- account;
- workspace;
- mailbox;
- project;
- content collection.

Do not include a raw account email, token, or private URL in a domain identifier. Map a stable opaque app-owned identifier to a deletion group.

For sensitive material, choose a named/protected index or omit it from search. Test device protection and locked-state behavior instead of assuming that a local index is harmless.

## Route C: NSUserActivity

Use when the person touched or is actively engaged with content:

1. create a meaningful activity type;
2. set a concise title and stable identifier;
3. set content attributes and keywords;
4. choose eligibleForSearch, eligibleForHandoff, eligibleForPrediction, or eligibleForPublicIndexing intentionally;
5. set expiration for temporary activity;
6. keep a strong reference while eligible;
7. call becomeCurrent/resignCurrent at the appropriate lifecycle boundary;
8. handle continuation by revalidating the target content.

Do not use eligibleForSearch as a substitute for indexing all records. Do not set public indexing for private account content.

## Route D: query and cancellation

CSSearchQuery:

1. create a query for the current term;
2. configure attributes and context;
3. set found-item and completion handlers;
4. start;
5. cancel when the term changes or the view disappears;
6. resolve results against current source truth.

CSUserQuery:

1. debounce the user’s text;
2. create one query object for that term;
3. configure result/suggestion limits;
4. start;
5. cancel on new input;
6. report engagement only after the user chooses a result/suggestion.

Search result order is system/index output. The app should not promise rank or complete recall.

## Route E: reindex extension

Implement a reindex path when the product depends on index integrity:

1. expose the extension target and required request handler;
2. enumerate current authorized content;
3. build current item projections;
4. finish the reindex operation;
5. update client state;
6. remove content no longer present;
7. record a redacted diagnostic.

The extension may run without the app’s UI and may have different process/data constraints. Keep enumeration deterministic and privacy-aware.

## Route F: Foundation Models search tool

The current preliminary route is:

1. index the app content first;
2. create a CoreSpotlightSource with only needed fetch attributes;
3. set a maximum result count;
4. configure source options for restricted content;
5. add the source to a SpotlightSearchTool configuration;
6. provide search guidance/format where needed;
7. initialize LanguageModelSession with the tool;
8. validate answer context and proposals against current app data.

The tool may retrieve identifiers and the attributes specified by fetchAttributes. A CSSearchableIndexDelegate can provide additional item data where supported. This is a privileged retrieval seam: minimize attributes and keep the delegate concurrency-safe.

Because the Apple documentation currently marks parts of this route beta/preliminary, gate it by availability and provide a deterministic search/manual fallback.

## Route G: bounded AI actions

Use:

indexed ID/attributes -> current record lookup -> authorized context -> model response -> typed proposal -> user review -> domain action

The model cannot:

- invent a searchable ID;
- reopen an expired/deleted record;
- bypass protected index or account policy;
- use ranking as permission;
- delete or mutate data without deterministic validation;
- expose a hidden attribute that was not intentionally fetched.

## Fallback matrix

| Condition | Fallback |
| --- | --- |
| Indexing request fails | Keep source data; retry/reindex with backoff |
| Search index stale | Resolve against source and offer refresh |
| Record deleted/expired | Show unavailable state and remove stale item |
| Account deleted | Delete domain identifiers and clear native cache |
| Protected data unavailable | Ask for authorization or keep content out of result |
| Query canceled | Drop stale batches and retain current term |
| Handoff unavailable | Open native local route or browser fallback |
| Reindex extension unavailable | Schedule a main-app repair path |
| Foundation Models unavailable | Use deterministic search and manual review |
| AI proposal invalid | Reject and show the source item |

## Evidence route

Capture:

1. named index/protection class and signed target configuration;
2. source create/update/delete and item metadata;
3. physical Spotlight/in-app search result and continuation;
4. account/workspace domain deletion;
5. protected/locked/unauthorized states;
6. rapid query cancellation and suggestion engagement;
7. index loss/reindex extension recovery;
8. Foundation Models tool availability, fetched attributes, restricted-source behavior, and fallback;
9. AI source lookup, typed proposal, rejection, confirmation, and no-hidden-field test;
10. accessibility, privacy, localization, and final artifact proof.

## Sources

- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableItem](https://developer.apple.com/documentation/corespotlight/cssearchableitem)
- [CSSearchableItemAttributeSet](https://developer.apple.com/documentation/corespotlight/cssearchableitemattributeset)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSSearchableIndexDelegate](https://developer.apple.com/documentation/corespotlight/cssearchableindexdelegate?changes=la_5_3_4&language=objc)
- [CSSearchQuery](https://developer.apple.com/documentation/corespotlight/cssearchquery)
- [CSUserQuery](https://developer.apple.com/documentation/corespotlight/csuserquery)
- [Adding your app’s content to Spotlight indexes](https://developer.apple.com/documentation/corespotlight/adding-your-app-s-content-to-spotlight-indexes)
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
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

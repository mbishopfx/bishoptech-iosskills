# Core Spotlight discoverability proof matrix

Core Spotlight crosses source truth, stable identity, named/protected indexes, asynchronous journaling, reindex extensions, system search, in-app queries, NSUserActivity continuation, Handoff, protected data, and Foundation Models retrieval. Verify each claim at the correct layer.

This matrix does not treat an indexed item, search result, activity object, model answer, or simulator run as proof of current authorization, ranking, Handoff delivery, protected-data behavior, or safe native action.

## Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, app/extension targets, target membership |
| SDK/deployment | Xcode, SDK, iOS/iPadOS target, OS build |
| Index | Named index, protection class, domain identifier |
| Source | Record type, stable ID, account/workspace, current authorization |
| Projection | Attribute set, keywords, thumbnail, expiration, content URL |
| Lifecycle | Create/update/delete, batch/client state, reindex path |
| Query | CSSearchQuery or CSUserQuery, term, predicate, limit, cancellation |
| Activity | Type, persistent/target ID, eligibility, strong owner, continuation |
| AI | SpotlightSearchTool availability, source, fetched attributes, proposal |
| Privacy | Sensitive fields, locked state, account deletion, logging |
| Accessibility | VoiceOver, Dynamic Type, keyboard, alternate input, contrast |
| Artifact | Signed app/extension, entitlements, release metadata |

Use synthetic records and opaque identifiers in shared evidence. Do not include private titles, account names, full content, protected URLs, or model context in screenshots or logs.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Item is correctly projected | Source record, stable ID, attribute set, named index submission | A CSSearchableItem constructor |
| Index update is accepted | Completion/journaled result and client state | A call to indexSearchableItems |
| Item appears in Spotlight | Physical device, system search, named result, source resolution | In-app query alone |
| Item stays current | Source update/delete, re-query, expiration, missing-item path | One successful index write |
| Account deletion clears items | Domain deletion, account switch, subsequent search | Deleting one identifier |
| Protected index works | Named/protection-class configuration, locked/protected-data test | A protectionClass enum in source |
| User activity is searchable | Strong activity owner, eligibleForSearch, physical result | Setting the Boolean |
| Handoff works | Stable IDs, receiving device, continuation activity, current source route | A userInfo dictionary |
| Universal continuation works | Physical link, scene/app continuation, URL validation, native destination | Opening a URL locally |
| Query cancellation works | Rapid input, canceled old query, only current results rendered | A cancel call in source |
| Reindex works | Extension invocation, complete source enumeration, client state, restored search | Main app indexing once |
| AI retrieves app content | Indexed fixture, configured tool/source, fetched attribute record | A model prompt with copied text |
| AI respects restrictions | Protected/restricted source scenario and no-hidden-attribute test | A privacy statement |
| Native action is safe | Current source lookup, auth, typed proposal, confirmation, result | Model answer or search rank |
| Release is ready | Final signed app/extension, target config, physical/system and privacy evidence | Debug or simulator run |

## Index lifecycle scenarios

- [ ] A new source record creates one stable searchable identifier.
- [ ] A title/keyword/content update replaces the existing item.
- [ ] A source deletion removes the item by identifier.
- [ ] An account/workspace deletion removes its domain identifiers.
- [ ] A temporary item expires and no longer routes to stale content.
- [ ] Large updates use bounded batches and client state.
- [ ] Indexing error leaves source truth intact and schedules recovery.
- [ ] A missing/stale index triggers a reindex path.
- [ ] Reindexing uses current authorization and does not resurrect deleted content.
- [ ] The default index is not used for production sensitive data.
- [ ] Attribute-set mutations have one writer and no concurrent access.

## Privacy and protected-data scenarios

| Scenario | Expected evidence |
| --- | --- |
| Public/product content | Searchable metadata and safe native route |
| Personal notes | Expected inclusion and deletion policy |
| Health/therapy/private record | Omitted or protected index with locked-state proof |
| Account switch | Old domain removed; new domain appears only after indexing |
| Logout | Search result cannot open old account data |
| Device locked/protected | Protected result unavailable or handled per policy |
| Expired item | Result resolves to unavailable and stale item is removed |
| Sensitive thumbnail/keywords | No private data leaks through visible metadata |

An on-device index is not a substitute for source authorization or account deletion.

## Query scenarios

- [ ] Empty query has a useful, accessible state.
- [ ] A normal term returns current items.
- [ ] A term with no results stays understandable.
- [ ] Rapid edits cancel prior CSSearchQuery or CSUserQuery work.
- [ ] Result batches do not reorder focus unexpectedly.
- [ ] Query errors recover without replacing the current term with stale content.
- [ ] Predicate/filter queries are bounded and SDK-supported.
- [ ] CSUserQuery suggestions are debounced and engagement is recorded only after selection.
- [ ] Search results are resolved against current source truth before opening.
- [ ] Missing, expired, unauthorized, and deleted results are distinct.

## NSUserActivity, Handoff, and continuation

- [ ] Activity title and content attributes describe the user-touched content.
- [ ] persistentIdentifier and targetContentIdentifier are stable.
- [ ] Strong references remain while eligible for search.
- [ ] eligibleForSearch, Handoff, prediction, and public indexing are intentional.
- [ ] expirationDate is set for temporary activity.
- [ ] becomeCurrent/resignCurrent follows the feature lifecycle.
- [ ] Cold launch, suspended, foreground, and receiving-device continuation work where claimed.
- [ ] A moved/deleted target produces a recoverable destination instead of a generic success.
- [ ] Sensitive userInfo is not logged or exposed to an unauthorized device.

## Foundation Models and AI scenarios

- [ ] SpotlightSearchTool availability is checked at runtime.
- [ ] CoreSpotlightSource fetches only attributes needed for the prompt.
- [ ] maximumResultCount and source options are intentional.
- [ ] Preliminary/beta APIs have a deterministic search/manual fallback.
- [ ] Restricted content is not returned to the model without policy.
- [ ] A CSSearchableIndexDelegate or extension is concurrency-safe and authorization-aware.
- [ ] Model context contains identifiers/attributes that can resolve back to current source truth.
- [ ] Prompt-injection text in an indexed item cannot call native actions.
- [ ] Model-invented IDs, routes, writes, and deletions are rejected.
- [ ] Source references and uncertainty are shown in the review surface.

## Accessibility and Liquid Glass matrix

- [ ] VoiceOver reads title, content type, freshness, account state, and action.
- [ ] Dynamic Type preserves search field, filters, empty/error state, and source attribution.
- [ ] Keyboard, Voice Control, and Switch Control reach search, cancel, open, delete, and review.
- [ ] Protected/deleted states are announced without exposing content.
- [ ] Reduced transparency and increased contrast preserve result hierarchy and source labels.
- [ ] Liquid Glass is app-owned and does not imitate or obscure system Spotlight.
- [ ] Localization, RTL, long titles, thumbnails, focus return, and pointer behavior work.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| projected | Source data was mapped to searchable metadata |
| journaled | Index accepted the operation for processing |
| searchable | A named physical/system or in-app query returned the item |
| current | Result resolved to current authorized source truth |
| expired | Item is outside its intended eligibility window |
| domain-cleared | Group deletion removed the account/workspace projection |
| protected | Index/data state requires the intended device protection boundary |
| activity-current | NSUserActivity is the current user-touched activity |
| continued | Receiving app/device routed the activity to current content |
| canceled | Query stopped and stale batches no longer affect UI |
| retrieved | Model tool received configured indexed attributes |
| proposed | Model returned a typed candidate action |
| applied | Deterministic validation and user policy allowed the action |
| unknown | The next system/source/model result is not proven |

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
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

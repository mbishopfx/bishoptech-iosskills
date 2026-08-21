# SwiftUI App Intents, Shortcuts, Spotlight, and interactive snippet proof matrix

This matrix proves system discoverability and execution boundaries separately: AppIntent declaration, AppEntity projection, current query resolution, App Shortcut metadata, Spotlight indexing, snippets, Visual Intelligence context, scene routing, local-AI proposal handling, accessibility, privacy, and release behavior.

Use it with the [system-discoverability review](../42-framework-deep-dives/101-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review.md), [design guide](../21-design-deep-dives/129-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-design.md), [capability route](../50-capability-recipes/132-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-route.md), and [recipes](../70-code-recipes/144-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-recipes.md).

## Evidence levels

| Level | Evidence | Boundary |
| --- | --- | --- |
| L0 | Current Apple documentation and SDK availability | API/version awareness |
| L1 | Named-target source/configuration inspection | Intent/entity/index/extension contract |
| L2 | Unit/fixture/UI tests | App-owned resolution and mutation logic |
| L3 | Simulator or local system fixture | Some app-side system route behavior |
| L4 | Signed physical-device/system-surface run | Spotlight, Shortcuts, Siri, snippets, input, scene handoff |
| L5 | Archive/TestFlight/App Store record | Distribution target and metadata |
| L6 | Repeatable release/support packet | Rollout, privacy, deletion, fallback, and recovery readiness |

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| AppIntent is available for target | Current source, deployment target, named compile | Import alone |
| AppIntent metadata is localized | String catalog/build inspection plus spoken UI task | A title in source |
| Action runs in intended process | Signed target membership, allowed execution target, physical invocation | Main-app-only unit test |
| AppEntity is safe | Projection review, field allowlist, privacy classification | Conforming to AppEntity |
| Entity ID is stable | Migration/version fixture and ID-resolution tests | UUID generated per query |
| EntityQuery resolves current data | Identifier, account, deletion, permission, and current-store tests | Returned entity from a mock |
| Query rejects stale/deleted data | Delete/account-switch/expiry fixture | Index entry |
| App Shortcut exists | AppShortcutsProvider compile and installation inspection | AppIntent without provider |
| App Shortcut phrase works | Physical Siri/Shortcuts/Spotlight task in supported locale | Phrase array in source |
| App Shortcut order/limit works | Installed system surface with provider ordering | Count in documentation |
| Schema route works | Generated schema/target compile and system task | Custom phrase similarity |
| Donation is policy-correct | Direct app interaction fixture and donation log | Donation on every invocation |
| Spotlight entity is indexed | Named CSSearchableIndex/indexAppEntities result and physical search | API success callback |
| Index stays current | Source update/delete/logout/expiry/reindex fixture | One initial index |
| Index protection is correct | Signed configuration and locked/protected-data device test | “On device” copy |
| OpenIntent opens current entity | Physical result tap, current query, account/deletion fixture | URL string |
| Large catalog handoff works | ShowInAppSearchResultsIntent plus system query and in-app search | Search screen alone |
| Query cancellation works | Rapid text changes with stale result rejection | Debounce code |
| Static snippet renders | Supported Siri/Spotlight/Shortcuts invocation and result view | SwiftUI preview |
| Interactive snippet renders | SnippetIntent physical invocation and repeated render | One screenshot |
| Snippet button mutates correctly | Nested AppIntent, persistence, re-render, idempotency fixture | Button with intent initializer |
| Snippet is side-effect safe | Repeat perform and cancellation tests | Rendered output |
| Snippet reload works | External state change and visible snippet refresh | Calling reload in source |
| Control Center behavior is valid | Control invocation without unsupported snippet claim | Snippet test from Siri |
| Visual Intelligence route is available | Current API availability, target/device, physical system invocation | IntentValueQuery compile |
| Visual Intelligence match is useful | Label/pixel/ambiguous/no-result fixtures and current resolver | One descriptor |
| Pixel privacy is honored | Retention/network/log audit and deletion test | Pixel buffer received |
| Onscreen context is current | View/entity annotation and scene invocation task | Static identifier |
| Transfer is safe | Representation/redaction/destination fixture | Transferable conformance |
| Cross-device identity is valid | Stable ID, account, local resolve, device handoff | Local UUID |
| Local AI proposal is reviewable | Source/entity/revision/model/output/apply-discard fixture | Natural-language output |
| Side effect is correct | Current authorization, revision, idempotency, confirmation, persistence | AppIntent perform returned |
| Accessibility works | VoiceOver, audio-only, Dynamic Type, contrast, motion, Voice Control, Switch Control, keyboard/pointer | Accessibility modifier |
| Release is ready | Signed app/extensions, system surface, archive/TestFlight metadata, physical run | Xcode archive |

## System-integration packet

| Field | Value |
| --- | --- |
| App target/bundle ID |  |
| App Intents extension target/bundle ID |  |
| Widget/control target |  |
| Package/framework target |  |
| SDK/Xcode/deployment target |  |
| AppIntent types |  |
| AppEntity types |  |
| Entity query types |  |
| AppShortcutsProvider |  |
| Schema domains/macros |  |
| Named Spotlight index |  |
| Index protection class |  |
| Domain identifiers |  |
| OpenIntent/scene route |  |
| SnippetIntent types |  |
| Visual Intelligence query |  |
| Transferable representations |  |
| Execution target policy |  |
| Account/authorization source |  |
| Privacy data classes |  |
| Fallback |  |
| Device/OS/system surface |  |
| Archive/TestFlight/App Store record |  |

Do not place raw account identifiers, signed URLs, credentials, private prompts, or user content in this packet.

## AppIntent and process matrix

| Test | Expected evidence |
| --- | --- |
| App target invocation | Action completes or returns typed error |
| App Intents extension invocation | Action completes with extension-safe dependency graph |
| Widget/control invocation | Short action completes under extension lifecycle |
| OpenIntent | App scene opens and focuses current destination |
| Background-capable action | No UI-only dependency; cancellation and timeout are safe |
| Permission required | Error leads to reauthorization/action route |
| Account signed out | No mutation; clear sign-in route |
| Current revision changed | Action re-resolves or requests review |
| Repeated invocation | Idempotent result, no duplicate side effect |
| Cancellation | No success mutation after cancel |
| Process termination | Durable checkpoint/recovery where work can continue |

## AppEntity and query matrix

| Test | Expected evidence |
| --- | --- |
| Display representation | Concise localized title/type/subtitle |
| Property exposure | Only approved searchable/parameter fields |
| Identifier lookup | Current record returned for valid authorized ID |
| Missing ID | No result or typed error, no invented record |
| Deleted ID | No result and index removal path |
| Account switch | Old account records unavailable |
| Shared/owned record | Ownership and permission state is accurate |
| Suggested entities | Bounded and policy-approved suggestions |
| Ordering | Deterministic where the system expects stable order |
| Shadow model | Persistence-only/private fields do not leak |
| Entity URL | URL opens only through current authorized route |
| Union value | All result types resolve and open safely |

## App Shortcut and schema matrix

| Test | Expected evidence |
| --- | --- |
| Fresh install | App Shortcuts appear without manual registration |
| Phrase | Supported locale invokes correct intent |
| App name | Phrase contains natural app reference |
| Parameter default | Preconfigured value resolves current entity |
| Phrase update | Documented update route refreshes system metadata |
| Shortcut count/order | Provider is within current limit and important actions are first |
| Title/icon | Verb-led title and accessible symbol/image |
| Audio-only | Dialogue contains critical facts |
| Negative/ambiguous phrase | Intent does not claim unrelated requests |
| Schema | Known-domain action/entity works in system context |
| Custom feature | App Shortcut is used where no schema owns the job |
| Action button | Supported physical device launches the intended action |

App Shortcut metadata is user-facing and may be used by Apple’s anonymized learning systems. Record the copy review and privacy classification.

## Spotlight and in-app search matrix

| Test | Expected evidence |
| --- | --- |
| Initial donation | Named index accepts approved entities |
| Incremental update | Same ID updates instead of duplicating |
| Delete | ID/domain deletion removes withdrawn content |
| Logout | Account domain is deleted and no result opens |
| Reindex all | IndexedEntityQuery or index extension rebuilds current records |
| Reindex subset | Requested IDs are re-donated accurately |
| Protection | Locked/protected data behavior matches policy |
| Open result | OpenIntent re-resolves current record |
| Large result set | ShowInAppSearchResultsIntent opens current in-app search |
| Search query | Current query text and scope are preserved |
| Suggestion | Suggestions are bounded and user-selectable |
| Query cancellation | Old results cannot overwrite newer input |
| Expiration | Temporary content stops resolving after expiry |
| System absence | In-app search remains useful |

## Snippet matrix

| Test | Expected evidence |
| --- | --- |
| Static result | Concise visual outcome and complete spoken dialogue |
| Confirmation | Target/scope/consequence plus cancel/confirm |
| Interactive result | SnippetIntent and ShowsSnippetView route |
| Repeated perform | Current state re-read, no repeated mutation |
| Nested Button | AppIntent action validates current state |
| Nested Toggle | State change persists and re-renders |
| External update | SnippetIntent.reload or documented refresh path |
| Mutation failure | Error appears; previous truth remains |
| Dismissal | No hidden uncommitted side effect |
| Long task | Snippet does not hold an unsuitable long operation |
| Control Center | No unsupported snippet claim |
| App unavailable | Fallback/static result/open route |

## Visual Intelligence and onscreen context matrix

| Test | Expected evidence |
| --- | --- |
| Availability | Supported device/OS/target and current API status |
| Label query | General label maps to bounded search |
| Pixel query | Pixel buffer is processed/retained according to policy |
| One-query rule | App has one descriptor-taking IntentValueQuery |
| Multiple result types | UnionValue returns typed results |
| No match | Empty/no-result response |
| Ambiguous match | Multiple candidates are distinguishable |
| False positive | App does not claim exact real-world identity |
| Open result | Current entity resolution and authorization |
| No visual system route | Ordinary app search still works |
| Context annotation | Visible entity ID remains current |
| Custom-rendered view | AppEntityUIElement mapping is correct |

## AI and side-effect matrix

| Test | Expected evidence |
| --- | --- |
| AI input source | Entity/context IDs and source revision recorded |
| Output schema | Candidate conforms to typed proposal |
| Stale source | Proposal is rejected or refreshed |
| Unauthorized source | Proposal is not applied |
| Destructive action | Confirmation and affected scope are shown |
| Apply | AppIntent performs current idempotent mutation |
| Discard | No domain change |
| Model unavailable | Deterministic fallback |
| Offline | Only claim local/offline behavior after physical test |
| Provenance | User can understand why the result appeared |

## Accessibility, privacy, and release matrix

Run:

- VoiceOver focus and announcements for entity, status, action, and error;
- audio-only Siri/Shortcuts dialogue;
- Dynamic Type and long localized title/parameter values;
- increased contrast, reduced transparency, color filters, and Reduce Motion;
- Voice Control and Switch Control in the app scene;
- keyboard and pointer input on iPadOS;
- locked-device and protected-data states;
- logout, deletion, account switch, and privacy-mode changes;
- redacted logs and no secret system-facing metadata;
- signed app/extension entitlements and target membership;
- physical Spotlight/App Shortcut/Shortcuts/Siri/snippet/scene tasks;
- archive/TestFlight/App Store asset and release metadata.

## Release packet

1. API/deployment/availability record.
2. Intent/entity/schema/package/extension source map.
3. Signed target, entitlement, Info.plist, and privacy inspection.
4. App Shortcut phrase/title/icon copy review.
5. Index field/domain/protection/donation/delete/reindex report.
6. Entity query current-resolution fixtures.
7. Physical system-surface invocation and scene routing recordings/logs.
8. Snippet repeated render, nested action, reload, and failure report.
9. Visual Intelligence label/pixel/ambiguity/privacy report where supported.
10. AI proposal/source/revision/review/apply-discard report.
11. Accessibility and alternate-input task report.
12. Archive/TestFlight/App Store/App Review metadata and fallback plan.

The packet should explicitly state which claims were not tested. “AppIntent compiles” is not a release claim.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [AppShortcutsProvider](https://developer.apple.com/documentation/appintents/appshortcutsprovider)
- [AppShortcut](https://developer.apple.com/documentation/appintents/appshortcut)
- [App Intents updates](https://developer.apple.com/documentation/updates/appintents/)
- [Donations and discovery](https://developer.apple.com/documentation/appintents/donations-and-discovery)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [IndexedEntityQuery](https://developer.apple.com/documentation/appintents/indexedentityquery)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [ShowInAppSearchResultsIntent](https://developer.apple.com/documentation/appintents/showinappsearchresultsintent)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [AppIntentSceneDelegate](https://developer.apple.com/documentation/appintents/appintentscenedelegate)
- [IntentValueRepresentation](https://developer.apple.com/documentation/appintents/intentvaluerepresentation)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSSearchQuery](https://developer.apple.com/documentation/corespotlight/cssearchquery)
- [CSUserQuery](https://developer.apple.com/documentation/corespotlight/csuserquery)
- [Building a search interface for your app](https://developer.apple.com/documentation/corespotlight/building-a-search-interface-for-your-app)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery)
- [App Shortcuts HIG](https://developer.apple.com/design/human-interface-guidelines/app-shortcuts)
- [Snippets HIG](https://developer.apple.com/design/human-interface-guidelines/snippets)
- [Siri HIG](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Action button HIG](https://developer.apple.com/design/human-interface-guidelines/action-button)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

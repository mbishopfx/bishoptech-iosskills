# SwiftUI App Intents, Shortcuts, Spotlight, and interactive snippet capability route

Use this route when an iOS 26 SwiftUI feature should be discoverable and safely usable from Apple system surfaces. It joins AppIntent actions, AppEntity resolution, App Shortcuts, Core Spotlight, interactive snippets, Visual Intelligence context, scene routing, and local-AI review without treating any system invocation as authorization or proof of a completed mutation.

Read the [system-discoverability review](../42-framework-deep-dives/101-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review.md), [design guide](../21-design-deep-dives/129-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-design.md), [proof matrix](../60-verification/126-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-proof-matrix.md), and [recipes](../70-code-recipes/144-swiftui-app-intents-shortcuts-spotlight-interactive-snippets-review-recipes.md). Use the existing [interactive snippet route](25-interactive-app-intent-snippet-route.md), [Spotlight route](54-core-spotlight-discoverability-and-foundation-model-route.md), and [Visual Intelligence route](95-visual-intelligence-app-intents-and-entity-route.md) for specialized details.

## Route selector

| Product outcome | Start with | Add only when needed |
| --- | --- | --- |
| One bounded action | AppIntent | AppShortcut, schema, snippet, or scene |
| Frequent action available after install | AppIntent + AppShortcutsProvider | SiriTipView/ShortcutsLink |
| Common domain action/content | App schema domain | Optional custom properties or App Shortcut |
| Record selection in Siri/Shortcuts | AppEntity + EntityQuery | IndexedEntity/OpenIntent |
| Spotlight record discovery | IndexedEntity + named CSSearchableIndex | IndexedEntityQuery/reindex extension |
| Large/live result set | ShowInAppSearchResultsIntent | SwiftUI in-app search and cancellation |
| Visual camera/screenshot matching | IntentValueQuery + SemanticContentDescriptor | UnionValue/OpenIntent |
| Compact result/confirmation | static or interactive snippet | Full app scene |
| Ongoing progress | ActivityKit | AppIntent trigger or LiveActivityIntent |
| Rich edit or destructive multi-step task | OpenIntent/app scene | confirmation snippet before opening |

Do not create a system integration for a low-frequency action merely because the API exists. The system route should reduce friction for a real user job.

## Route map

~~~text
user job
  -> action/entity projection
  -> target/process/capability gate
  -> system discovery surface
  -> parameter/entity resolution
  -> current authorization and source lookup
  -> bounded operation
  -> static result, snippet, Live Activity, or app scene
  -> user review if a side effect is possible
  -> idempotent domain commit
  -> refreshed system result and index state
~~~

## Step 1: define the action and entity contract

Write the contract before implementing the AppIntent:

| Field | Decision |
| --- | --- |
| User job | Short verb-led outcome |
| AppIntent | Type, parameters, result, error |
| Entity | App concept and projection |
| Stable ID | Local/stable mapping and deletion behavior |
| Query | Current resolver and suggested entity policy |
| Shortcut/schema | Common domain or unique feature |
| Index | Named index, fields, domain, protection |
| Open route | OpenIntent/deep link/scene |
| Snippet | Result/confirmation/interactive or none |
| Process | app, App Intents extension, widget extension, package |
| Side effect | Read, propose, confirm, mutate, delete, send |
| Current revision | Conflict/idempotency key |
| Privacy | Exposed/indexed/transferred/ephemeral data |
| Fallback | No match, unavailable system surface, offline, unauthorized |

Use a shadow AppEntity when the persistence model contains fields that should not become system-facing metadata. Keep the resolver independent from SwiftUI view state.

## Step 2: configure targets and packages

AppIntent types can be in the app, an app extension, a framework, or a Swift package where the selected SDK supports the target. Decide the process boundary:

| Execution target | Include | Do not assume |
| --- | --- | --- |
| Main app | Scene, full database, rich UI | An existing scene is visible when an intent starts |
| App Intents extension | Short background-safe actions and shared service | SwiftUI scene/environment or unlimited runtime |
| Widget extension | Widget/control-owned action | Main app-only storage or a long-running process |
| Shared package | Sendable values, entity metadata, domain service protocol | Target-specific entitlements, UI, or app-only singletons |

Inspect target membership, linked framework, app extension Info.plist, entitlements, privacy manifests, and deployment availability in the signed artifact. Use AppIntentSceneDelegate or other scene-routing contracts only for an action that genuinely needs a particular scene.

If the action is foreground-only, use OpenIntent or a scene-aware route. If it can run in the background, isolate the storage and authorization service so the extension can execute safely.

## Step 3: implement the AppEntity and resolver

The entity projection should contain:

- stable ID;
- short title;
- localized type;
- concise display representation;
- only fields needed for selection/search/context;
- optional URL/open representation;
- ownership/sharing state when relevant.

The EntityQuery must:

1. accept identifiers from the system;
2. fetch current records;
3. validate account and authorization;
4. reject deleted/expired/hidden records;
5. return current entities;
6. preserve deterministic ordering where appropriate;
7. handle empty/ambiguous results without inventing a match.

Do not use the index’s old display text as current data. Re-resolve before any mutation.

For parameters that can take several entity types, use the selected SDK’s UnionValue route rather than untyped strings. For one-of-one settings, consider UniqueAppEntity only when the singleton semantics are real.

## Step 4: choose App Shortcut or schema

For a custom App Shortcut:

1. define the bounded AppIntent;
2. create AppShortcut metadata and short title;
3. write concise localized phrases containing the app name;
4. add only the most useful optional parameters;
5. expose the provider in the app or appropriate package/target;
6. update parameter metadata through the documented route when values change;
7. test install, Shortcuts, Spotlight, Siri, and Action button where supported.

App Shortcuts are available immediately after install and are limited to ten per app in current HIG guidance. Order the most important ones first. If the app fits a known app schema, prefer schema integration for contextual system understanding and keep custom shortcuts for unique behavior.

Do not rely on an Add to Siri-style flow. Current App Shortcuts are code-defined system integration. Use SiriTipView or ShortcutsLink only to teach the person about a shortcut in context.

## Step 5: index safe entities

For durable searchable records:

1. adopt IndexedEntity;
2. select bounded properties and indexing keys;
3. create a named CSSearchableIndex;
4. donate entities in batches;
5. track a schema/version/checkpoint;
6. delete entity IDs or domains on source deletion, logout, or privacy changes;
7. add OpenIntent for the entity;
8. implement IndexedEntityQuery reindexing when the selected SDK supports it;
9. re-resolve on open.

Use custom protected indexes for sensitive content where appropriate. Indexing is a projection and may be stale. The app should never tell a user that a record is current merely because donation completed.

For a large catalog:

~~~text
Spotlight/App Intent query
-> ShowInAppSearchResultsIntent
-> native SwiftUI searchable view
-> CSUserQuery/CSSearchQuery with debounce
-> cancellation of prior query
-> current store results
-> OpenIntent/entity resolution
~~~

Every query object is one operation. When search text changes, cancel the old one and create a new query. Keep suggestions and result batches separate from current domain truth.

## Step 6: add static or interactive snippets

Use a static result when the person needs information only. Use an interactive snippet when a small follow-up action can finish without opening the full app.

For an interactive route:

1. the initiating AppIntent returns a ShowsSnippetIntent result;
2. the SnippetIntent reads current state and returns ShowsSnippetView;
3. the SwiftUI view uses Button/Toggle with nested AppIntents;
4. the nested intent validates current ID/account/revision;
5. the mutation commits idempotently;
6. the snippet re-renders from current state;
7. call SnippetIntent.reload when external state changes.

A SnippetIntent may run more than once. Keep render-time code side-effect free and short. Do not perform a network migration, model compilation, or irreversible mutation from the snippet renderer.

Use a confirmation snippet for destructive or externally visible actions. Keep target, scope, affected count, and consequence visible. Cancellation must leave the domain unchanged.

Control Center-invoked app intents cannot display snippets. Use a control’s own compact value/action behavior or route to a Live Activity/app scene as appropriate.

## Step 7: integrate Visual Intelligence

Use the documented IntentValueQuery route when the app can find entities matching system-captured context:

1. implement one query accepting SemanticContentDescriptor;
2. inspect labels and optional pixel buffer;
3. perform bounded app-owned search;
4. return one entity type or a UnionValue;
5. use OpenIntent for opening the selected result;
6. handle no match, ambiguous match, unavailable camera/context, and privacy.

Labels are general high-level terms and can change. They do not prove an exact place/object identity. Pixel-buffer matching is a search input, not permission to retain or transmit captured content. Use availability checks because the current API is documented as preliminary.

Keep normal in-app search useful even when Visual Intelligence is unavailable. Do not create separate source truth for the system route.

## Step 8: annotate onscreen context and route scenes

When a person refers to something visible in a SwiftUI view, associate the current AppEntity with that content using the documented App Intents/scene context route. For custom graphics, use AppEntityUIElement and its context where supported.

When opening:

1. receive entity ID or URL;
2. choose the correct scene/window;
3. re-resolve the current entity;
4. verify account and authorization;
5. set navigation path;
6. focus the relevant view;
7. present a missing/stale/reauthorization state if needed.

Do not let a deep link bypass entity resolution. Do not use a view-local selection as a durable system identifier.

## Step 9: separate transfer and ownership

For a cross-app or system workflow, define IntentValueRepresentation/Transferable representations intentionally. Choose what is transferred:

| Representation | Use |
| --- | --- |
| Stable ID | Receiver resolves current object |
| URL | Receiver opens a documented route |
| Redacted value | Small non-sensitive display or action input |
| File/data | Explicit export/share operation |

Use ownership or stable cross-device contracts only when they match the actual product. Revalidate the receiving account and current record. Never include credentials, signed URLs, raw persistence objects, or stale authorization in a representation.

## Step 10: side-effect safety and local AI

Treat a system-invoked AppIntent as an external request:

~~~text
system request
-> parameter/entity resolution
-> current authorization
-> revision/idempotency check
-> optional confirmation
-> bounded domain mutation
-> result/snippet/scene
~~~

If local AI ranks or drafts the request:

~~~text
system/entity context
-> bounded local inference
-> typed proposal with source IDs
-> current re-resolution
-> user review
-> AppIntent mutation
~~~

The model must not invent an entity ID, choose an unauthorized account, or bypass the AppIntent’s confirmation. Record source entity ID, revision, model/resource version, and user decision when the action matters.

## Step 11: errors and recovery

Map every failure to a system-readable and user-actionable result:

| Failure | Result |
| --- | --- |
| No entity | No matching item; offer broader search |
| Ambiguous entity | Ask a concise clarification |
| Deleted/stale record | Explain that it is no longer available |
| Permission required | Request permission or open settings/app |
| Signed out | Ask the person to sign in |
| Current revision changed | Re-fetch and ask for review again |
| Extension unavailable | Open app or use fallback |
| Network unavailable | Offline/basic mode or retry |
| Snippet render failure | Static result or app scene |
| Mutation failed | Explicit error; no success dialogue |

Cancellation is not success. Retrying a known incompatible action without changing inputs is not recovery.

## Step 12: prove system behavior

Run the same feature at separate boundaries:

1. named-target compile;
2. unit/entity-query/index fixtures;
3. app/extension signed target inspection;
4. local Spotlight/index repair;
5. physical Spotlight/App Shortcut/Shortcuts/Siri run;
6. snippet repeated render and nested action;
7. Visual Intelligence system invocation where supported;
8. scene/deep-link routing;
9. accessibility/audio-only task;
10. account switch, deletion, stale ID, and protected-data run;
11. archive/TestFlight/App Store record.

## Route completion checklist

- [ ] User job, action, entity, and system surface are named.
- [ ] AppIntent metadata and supported process/target are recorded.
- [ ] AppEntity is a safe projection with current ID resolution.
- [ ] App Shortcut versus schema choice is documented.
- [ ] Index fields, named index, deletion, and reindex behavior are documented.
- [ ] OpenIntent/scene routing revalidates current entity and authorization.
- [ ] Large-catalog search cancels stale work and uses current data.
- [ ] Static/result/confirmation/interactive snippet responsibility is explicit.
- [ ] Snippet render is side-effect free and nested actions are idempotent.
- [ ] Visual Intelligence route has availability, no-match, ambiguity, and privacy states.
- [ ] Transfers are redacted and ownership/stable-ID semantics are explicit.
- [ ] Local AI output remains a typed, reviewable proposal.
- [ ] Liquid Glass is limited to app-owned surfaces and has accessibility fallback.
- [ ] VoiceOver, audio-only, Dynamic Type, contrast, motion, Voice Control, Switch Control, keyboard, and pointer paths pass.
- [ ] Logout, deletion, stale index, protected data, cancellation, and system-unavailable fallback pass.
- [ ] Physical system, signed archive, TestFlight, and release evidence are captured.

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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)

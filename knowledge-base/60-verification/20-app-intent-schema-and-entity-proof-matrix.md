# App Intent schema and entity proof matrix

## Scope

Use this matrix when an app claims Apple Intelligence, Siri, Shortcuts, Spotlight, cross-device, visual intelligence, or cross-app value behavior from App Intents. It verifies semantic contracts and runtime boundaries independently.

The existence of an AppEntity, a schema macro, or a stable identifier does not prove that the system will discover the content, resolve the correct record, carry it across devices, or authorize a side effect.

## Evidence levels

| Level | Proves | Does not prove |
| --- | --- | --- |
| Documentation | The intended schema/type and documented caveats were identified | The selected SDK compiles the exact declaration |
| Compile fixture | Macro, protocol, query, target, and availability fit the named SDK | Runtime resolution, system ranking, or device handoff |
| Domain test | Current lookup, privacy, ownership, transfer, and mutation rules | Siri or Apple Intelligence behavior |
| System invocation | The signed device resolves and invokes the tested route | Universal language, device, or ranking behavior |
| Cross-device run | Stable ID/link resolves on the tested second device | All accounts, OS versions, or future schema compatibility |
| Release artifact | Targets, entitlements, links, metadata, privacy declarations, and extensions are signed | Production ranking or App Store approval |

## Schema and entity matrix

| Proof item | Test | Passing evidence | Boundary |
| --- | --- | --- | --- |
| Schema domain selection | Compare capability to Apple domain documentation | Domain and schema semantics genuinely match | Similar names are not semantic proof |
| Required schema group | Build with the selected macro(s) | Xcode reports no missing required schema members | Compile does not prove system invocation |
| AppEntity surface | Inspect properties, ID, display/type representation | Only useful, privacy-reviewed fields are exposed | Does not prove data is current |
| EntityQuery ID lookup | Resolve existing, deleted, unauthorized, and unknown IDs | Current authorized entities resolve; unavailable ones are omitted or fail safely | Does not prove natural language matching |
| String/property query | Test exact, partial, ambiguous, localized, and empty input | Results are bounded, deterministic, and disambiguatable | Does not prove Siri’s language interpretation |
| DisplayRepresentation | Inspect title, subtitle, image, synonyms, plural/type copy | Visual and spoken labels are localized and nonrevealing | Does not prove system UI placement |
| Parameter summary | Open the Shortcut editor in the signed build | Summary describes the action and supports the right controls | Does not prove every spoken phrase |
| Stable identity | Resolve the same entity on two signed devices | Stable ID finds the current record or returns an honest unavailable state | Does not prove sync or account transfer |
| Local/stable identifier pair | Exercise SyncableEntityIdentifier mapping | Local operations use local ID; cross-device route uses stable ID | Does not prove server consistency |
| Ownership metadata | Test private, shared, public, and unknown states | EntityOwnership reflects current sharing state | Does not replace authorization |
| Shared/public confirmation | Invoke destructive or sensitive action | System/app asks for relevant confirmation and mutation rechecks ownership | Does not prove every system surface shows identical copy |
| Transfer export | Export to the supported system value | Only intended fields cross the boundary and remain meaningful | Does not prove receiving app accepts the value |
| Transfer import | Import valid, stale, malformed, and unauthorized system values | Import re-resolves current entity or rejects safely | Does not prove cross-app workflow completion |
| Onscreen context | Associate a visible entity with the app view/activity | “This item” context resolves to the current authorized entity | Does not prove context is available outside the tested conversation |
| RelevantEntities donation | Donate, replace, remove, and clear current media suggestions | Set replacement and clear behavior are correct | Does not prove the system displays or ranks donations |
| UniqueAppEntity | Resolve settings/singleton via UniqueAppEntityQuery | Exactly one value or explicit unavailable state | Does not prove singleton data is globally synchronized |
| UnionValue | Test every finite case, invalid input, and future/unknown case | Typed cases resolve and localize without ambiguity | Does not make arbitrary model text safe |
| Universal link | Open entity/intent link while installed, uninstalled, signed out, and unauthorized | Precise destination or safe fallback; no private data in URL | Does not prove AASA/production routing on every domain/device |
| Schema unsupported | Run on an older/unsupported OS or disabled capability | In-app/custom route remains usable | Does not prove the new schema executes |

## Runtime and execution matrix

| Proof item | Test | Passing evidence | Boundary |
| --- | --- | --- | --- |
| supportedModes | Run in each declared mode | Intent behaves correctly in background/foreground/deferred route | Does not prove system always chooses preferred mode |
| currentMode | Log redacted mode and branch behavior | Code adapts to actual runtime context | Logging is not a scheduling guarantee |
| LongRunningIntent | Run file/model/data job beyond normal short budget | Progress updates, checkpoints, result, and failure are honest | Does not prove unlimited background time |
| Progress | Stall, slow, and cancel a task | Progress remains meaningful and task does not claim completion early | Does not prove user sees every update |
| CancellableIntent | Deliberate cancel and timeout/cancel reason | Work stops, resources close, checkpoint is recoverable | Process may still be suspended soon after cancellation |
| UndoableIntent | Register inverse and trigger app-owned undo UI | Inverse operation restores valid prior state | Does not prove system automatically invokes undo |
| Permission error | Deny photos, Bluetooth, local network, Siri, or location as relevant | Precise AppIntentError and recovery route | Does not prove settings state changes immediately |
| User action error | Require sign-in, foreground, or settings step | System/app explains next action without false success | Does not prove the user completes the step |
| Process target | Invoke from app, extension, widget/control, and terminated state | Dependencies and authorization are available in the intended target | Does not prove future OS target selection |
| Cancellation and idempotency | Repeat/retry after partial progress | Final domain state is deterministic and duplicate-safe | Does not prove remote side effects are reversible |

## AI and privacy matrix

| Proof item | Test | Passing evidence | Boundary |
| --- | --- | --- | --- |
| Apple Intelligence discovery | Use eligible signed device/configuration and supported language | Documented action/entity route can be used in tested configuration | Never claim guaranteed ranking or model selection |
| Siri phrase | Test natural variants, ambiguity, and correction | Correct entity/action or clear disambiguation | Does not prove all dialects/locales |
| Spotlight indexing | Index, update, delete, sign out, and reindex | Expected entities appear and old account content disappears | Does not prove semantic ranking |
| Visual intelligence | Test supported image/content and no-match path | App reports bounded matches with current entities | Does not prove camera or model quality generally |
| Model proposal | Use labeled fixtures and unavailable-model state | Typed proposal has source/provenance and manual fallback | Does not prove model correctness in all contexts |
| Privacy minimization | Test titles, subtitles, dialog, transfer, URL, locked, and signed-out state | No unauthorized private content crosses the surface | Does not prove system cache purge timing |
| Account switch | Switch account during query and action | Old entity is rejected and projections are rebuilt | Does not prove every extension process refreshes instantly |
| Public/shared content | Test collaborator and public mutation paths | Scope and confirmation match actual current state | Does not prove ownership metadata is always fresh |

## Accessibility and localization matrix

- [ ] Entity and action names are readable with VoiceOver.
- [ ] Spoken dialogs include object and outcome without private raw text.
- [ ] Dynamic Type does not clip entity labels or confirmation copy.
- [ ] Voice Control can reach visible actions by their labels.
- [ ] Switch Control reaches query, confirmation, and fallback paths.
- [ ] RTL layout and localized synonyms resolve and display correctly.
- [ ] Dates, measurements, names, and pluralized counts use localized formats.
- [ ] Reduced transparency and increased contrast preserve meaning.
- [ ] Full-app and universal-link destinations land in an accessible state.

## Artifacts

Retain:

- schema selection record and source URLs;
- Xcode build log for macro/protocol/query declarations;
- entity/query fixtures and expected resolution;
- ownership, transfer, URL, context, and relevance test output;
- mode/progress/cancellation/undo logs;
- signed archive target/entitlement/extension inspection;
- physical-device model, OS build, locale, account, and Apple Intelligence settings;
- privacy/accessibility/localization notes;
- unsupported-state screenshots or redacted result bundles.

Use synthetic records. Do not publish real contact details, private file paths, health data, shared content, credentials, or raw model context in proof artifacts.

## Release gate

Describe the route as shipped only when:

- schema and entity declarations are in the intended signed targets;
- every query revalidates current account and permission state;
- stable IDs and universal links have been tested on the supported device pair;
- ownership, transfer, context, and relevance routes have explicit boundaries;
- background/progress/cancellation/undo behavior is tested where declared;
- privacy, accessibility, localization, and fallback paths are complete;
- system invocation is proven on the supported physical device/configuration;
- marketing copy does not promise Apple Intelligence or Siri behavior broader than the evidence;
- production/TestFlight observation exists when delivery depends on system ranking or account/server state.

## Sources

- [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [Defining app entities for your custom data types](https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types)
- [Entity queries](https://developer.apple.com/documentation/appintents/entity-queries)
- [SyncableEntity](https://developer.apple.com/documentation/appintents/syncableentity)
- [OwnershipProvidingEntity](https://developer.apple.com/documentation/appintents/ownershipprovidingentity)
- [EntityOwnership](https://developer.apple.com/documentation/appintents/entityownership)
- [IntentValueRepresentation](https://developer.apple.com/documentation/appintents/intentvaluerepresentation)
- [RelevantEntities](https://developer.apple.com/documentation/appintents/relevantentities)
- [UniqueAppEntity](https://developer.apple.com/documentation/appintents/uniqueappentity)
- [UniqueAppEntityQuery](https://developer.apple.com/documentation/appintents/uniqueappentityquery)
- [UnionValue](https://developer.apple.com/documentation/appintents/unionvalue%28%29)
- [URLRepresentableIntent](https://developer.apple.com/documentation/appintents/urlrepresentableintent)
- [URLRepresentableEntity](https://developer.apple.com/documentation/appintents/urlrepresentableentity)
- [Intent modes](https://developer.apple.com/documentation/appintents/intentmodes)
- [AppIntent supported modes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [LongRunningIntent](https://developer.apple.com/documentation/appintents/longrunningintent)
- [CancellableIntent](https://developer.apple.com/documentation/appintents/cancellableintent)
- [UndoableIntent](https://developer.apple.com/documentation/appintents/undoableintent)
- [App Intent updates](https://developer.apple.com/documentation/updates/appintents)

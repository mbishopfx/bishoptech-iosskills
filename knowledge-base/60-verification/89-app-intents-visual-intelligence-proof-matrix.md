# App Intents and Visual Intelligence proof matrix

## Purpose

This matrix defines what must be proven before claiming that an app supports
Visual Intelligence, not merely that a route sketch exists.

The route under test is:

    system capture or onscreen selection
      -> SemanticContentDescriptor
      -> IntentValueQuery
      -> AppEntity / UnionValue
      -> system result
      -> OpenIntent
      -> app detail or semanticContentSearch continuation

Keep these evidence classes separate:

| Evidence class | What it can prove | What it cannot prove |
| --- | --- | --- |
| Documentation | Apple’s intended API and system contract | That a target compiles or a device invokes it |
| Static/source review | Privacy, target wiring, schema choice, fallback intent | Runtime availability, system ranking, hardware behavior |
| Compile | Imports, signatures, macros, generated requirements, target membership | Visual Intelligence invocation or useful matching |
| Unit/fixture | Entity mapping, ranking, empty/deleted/authorization behavior | System-owned capture and system UI |
| Preview/simulator | App UI states, layout, navigation, accessibility diagnostics | Physical system invocation or supported device behavior |
| Signed physical device | OS/device settings, actual handoff, interaction, performance | Every device, language, account, or release environment |
| System-surface run | Visual Intelligence query, result rendering, open handoff | Production scale, App Store review, all system variants |
| Archive/release | Entitlements, privacy metadata, localization/resources, signing | Relevance, model quality, real user adoption |

Never use one class as a substitute for another.

## Evidence record

Record one immutable evidence row for each target/device/build:

~~~yaml
route: visual-intelligence-app-intents
project: <project-name>
target: <app-or-extension-target>
sdk: <xcode-and-sdk>
deployment_target: <minimum-os>
build: <version-build>
device: <model-and-physical-or-simulator>
os: <os-version>
language_region: <language-region>
apple_intelligence_state: <state-if-relevant>
signed: true
capture_source: <visual-intelligence-camera-or-onscreen-selection>
descriptor_inputs:
  labels: <count-and-sanitized-fixture-name>
  pixel_buffer: <present-absent-and-format>
matcher:
  mode: <labels-pixel-hybrid-network>
  vocabulary_version: <version>
  model_or_index_revision: <revision-or-none>
  threshold: <recorded-policy>
result_count: <integer>
entity_types: [<entity-types>]
open_route: <success-unavailable-or-failure>
more_results_route: <success-not-tested-or-not-supported>
accessibility:
  voiceover: <pass-fail-not-tested>
  dynamic_type: <size-range>
  reduce_motion: <pass-fail-not-tested>
  reduce_transparency: <pass-fail-not-tested>
privacy:
  raw_capture_retained: false
  sensitive_logging_reviewed: true
release:
  archive: <pass-fail-not-tested>
  entitlements_inspected: <pass-fail-not-tested>
  privacy_manifest_reviewed: <pass-fail-not-tested>
notes: <sanitized-observations>
~~~

Do not store a raw screenshot, private entity name, account identifier, or
pixel-derived identifier in a shared evidence log.

## Fixture set

Create deterministic fixtures before connecting the real system surface.

| Fixture | Inputs | Expected result |
| --- | --- | --- |
| F01 labels only | Labels, no pixel buffer | Coarse candidates or empty array; no camera permission prompt |
| F02 pixel only | Empty labels, valid test buffer | Pixel matcher ranks current records or returns empty |
| F03 hybrid | Labels plus valid buffer | Stable ranked order for the recorded vocabulary/model revision |
| F04 no input | Empty labels, no buffer | Empty array, bounded completion |
| F05 weak match | Low-similarity buffer | Empty array or explicitly low-confidence in app, never a fake exact match |
| F06 one entity | One current record | Localized display representation and open route |
| F07 union | Item and collection | Finite union values and one open route per type |
| F08 deleted | Known ID removed before open | Unavailable state and recovery/search path |
| F09 account change | Entity resolved under account A, opened under B | No private record leak; sign-in/account recovery |
| F10 limited catalog | Authorized subset only | Results are restricted to the current scope |
| F11 over-limit | More records than system-card limit | Bounded results and working More results route |
| F12 timeout | Matcher delays beyond route budget | Local fallback or empty/error state, no unbounded spinner |
| F13 malformed buffer | Unsupported or corrupt input | Safe failure with no raw-data log |
| F14 model unavailable | Feature/index asset unavailable | Label/index fallback or honest no-result |
| F15 localization | Supported locale/RTL fixture | Localized title/subtitle and accessible type |
| F16 reduced effects | Reduce Motion/Transparency enabled | Same task and hierarchy without required effects |

## Static contract review

Before compiling, review the source and project configuration:

- The route imports the documented App Intents and Visual Intelligence modules.
- The descriptor query is an IntentValueQuery whose input is
  SemanticContentDescriptor.
- The app does not define competing descriptor queries.
- A UnionValue is finite and each returned entity type is openable.
- AppEntity display data is concise, localized, and privacy-reviewed.
- Entity identifiers are stable within the app’s current account/store scope.
- OpenIntent re-resolves current truth rather than trusting stale card data.
- The semanticContentSearch route navigates to a scoped app search.
- Query dependencies do not require a SwiftUI scene or mutable UI singleton.
- Network/image/model work is bounded and cancellable.
- Raw labels, pixel buffers, features, private names, and account identifiers
  are absent from ordinary diagnostics.
- No visual match authorizes a purchase, message, unlock, medical action, or
  other consequential side effect.
- The app has explicit empty, unavailable, sign-out, timeout, and matcher
  fallback states.
- The app does not request unrelated permissions merely because a system
  descriptor exists.
- The UI uses system controls and has reduced-effects fallbacks.

## Compile proof

Compile the smallest named slice first.

| Compile check | Pass condition | Evidence |
| --- | --- | --- |
| Module imports | App Intents and Visual Intelligence imports resolve | Build log |
| Entity | AppEntity, display representation, ID, and default query compile | Build log and source revision |
| Query | IntentValueQuery signature accepts SemanticContentDescriptor | Build log |
| Union | UnionValue generated type requirements compile | Build log |
| Open | OpenIntent target parameter and result compile | Build log |
| Schema | visualIntelligence.semanticContentSearch generated contract compiles | Build log/Xcode diagnostics |
| Shared target | Query/entity module is included in the target that executes it | Build settings/archive |
| Availability | Older deployment target has a fallback branch if supported | Build matrix |
| Concurrency | Sendable/actor isolation warnings are addressed or documented | Compiler diagnostics |
| Resources | Thumbnails, localization tables, model/index resources are present | Target/resource inspection |

If the visual-intelligence schema is beta or changes in the selected SDK, record
the exact SDK and generated requirements. A successful compile against a beta
SDK is not final-OS proof.

## Deterministic query tests

Test the matcher and projection without system invocation.

| Test | Assertion |
| --- | --- |
| Empty descriptor | Returns an empty array within the budget |
| Labels mapping | Known labels map to the expected candidate categories |
| No synonym assumption | Unknown/untranslated labels do not create false identity |
| Pixel fallback | A buffer can rank without labels |
| Label fallback | Labels can return candidates without a buffer |
| Current filtering | Deleted, private, or unauthorized records are omitted |
| Stable ordering | Same fixture and model/index revision produce the same order |
| Limit | The query never exceeds the configured result limit |
| Union mapping | Each union case has the expected entity type |
| Display privacy | Title/subtitle/image contain only approved fields |
| Re-resolution | Known IDs return current records; missing IDs are omitted |
| Open unavailable | Deleted/unauthorized IDs produce an unavailable route |
| Timeout | Cancellation/fallback is deterministic |
| Error redaction | Diagnostics contain status codes, not private input |
| More results | Continuation state contains scope and sanitized context only |

Use a fake CatalogSearching implementation for these tests. Do not inject the
real camera, system search, or a live account into a unit test.

## App UI proof

The app owns the detail and continuation views. Test the normal app route as if
Visual Intelligence had opened it, then test the real handoff separately.

| UI state | Preview/simulator | Physical device |
| --- | --- | --- |
| Strong match detail | Layout and text hierarchy | Touch, legibility, navigation, energy |
| Multiple matches | List/grid ordering | Scroll, selection, focus, adaptive layout |
| No match | Empty copy and normal search | Keyboard/touch and recovery |
| Deleted/private record | Unavailable state | Sign-in/account/permission recovery |
| More results | Scoped search fixture | Actual openAppWhenRun/handoff |
| AI/model enrichment missing | Canonical result remains useful | Device asset/runtime fallback |
| Liquid Glass enabled | Material hierarchy | Readability over changing content |
| Reduce Transparency | Solid/reduced material | Action and contrast remain usable |
| Reduce Motion | No required morphing | Handoff remains comprehensible |
| Dynamic Type | Text does not lose identity | Long localized names remain usable |

## Visual Intelligence system proof

Use a signed physical-device build and record the exact capture route.

1. Install the signed build on the named device.
2. Confirm the device OS, language/region, account state, and system settings.
3. Prepare a known scene or onscreen selection with a corresponding fixture.
4. Invoke Visual Intelligence through the supported system entry point.
5. Confirm the app is offered as a search destination when expected.
6. Confirm the system calls the query and receives the expected entity type.
7. Verify card title, subtitle, thumbnail, and localization.
8. Test one strong match, multiple matches, no match, and pixel-buffer absent.
9. Tap a result and confirm the current entity opens in the app.
10. Delete or restrict the entity before opening and verify the honest fallback.
11. Use More results and confirm the app opens to scoped search.
12. Repeat after process termination and check that the app does not rely on a
    stale scene or in-memory model.
13. Record whether the route works on each intended iPhone/iPad/Mac target.
14. Capture screenshots/logs only after redacting private content.

A local call to values(for:), an App Intent test invocation, or a screenshot of
the app’s detail view does not close this matrix.

## System, account, and availability variants

| Variant | Required observation |
| --- | --- |
| Supported OS/device | Query registered and result rendered |
| Older deployment target | Route omitted or app fallback behaves normally |
| Apple Intelligence/system feature unavailable | App remains functional without the route |
| Device language not en_US | Labels and app localization do not assume translated system labels |
| Signed out | Private results absent and recovery is clear |
| Limited catalog | Only authorized records appear |
| Network unavailable | Local/empty path is bounded |
| Model/index unavailable | Deterministic fallback and diagnostics |
| App terminated | System query/open route works or fails honestly |
| Account changes while pending | No cross-account data leak |
| Accessibility settings | Same result/open/search task completed |
| Privacy settings | Raw capture and private context are not retained |

## Performance and energy proof

Record budgets that reflect the system search interaction:

- descriptor preprocessing time;
- label normalization time;
- pixel-buffer conversion time;
- model/index load time;
- search and ranking time;
- entity projection and thumbnail preparation time;
- total query completion time;
- peak memory;
- cancellation behavior;
- network wait and payload size when network is used;
- thermal/battery observations on the representative device.

Use signposts or test metrics where they help, but do not claim a universal
latency from one run. Test cold and warm paths, low-memory conditions, large
catalogs, and a real device. Do not keep a high-frequency camera stream alive
inside an App Intent query.

## Accessibility proof

Complete the full task, not only an audit:

1. Start from the system result or app’s scoped search.
2. Move VoiceOver focus through title, type, result, and action.
3. Open the entity and confirm the selected record is announced.
4. Find and operate the primary action without relying on color, blur, or
   position.
5. Repeat with Dynamic Type at the supported extremes.
6. Repeat with Reduce Motion and Reduce Transparency.
7. Test keyboard/pointer/Switch Control/Voice Control where supported.
8. Test an RTL locale and long localized entity names.

Record defects with the exact OS/device and route state. Accessibility inspector
output is useful diagnostic evidence, not proof of task completion.

## Privacy and release proof

Before archive/release, inspect:

- target membership for App Intents and Visual Intelligence code;
- deployment target and availability branches;
- localized AppEntity display strings;
- thumbnail/model/index resources;
- privacy manifest and required-reason declarations where applicable;
- camera/photo/network usage strings only when the app’s own features need them;
- entitlements and extensions, if the route requires them;
- archive contains the intended code/resources;
- logs and analytics exclude raw descriptor content;
- account sign-out clears pending private visual-search state;
- App Store metadata does not claim object identity, medical accuracy, or
  guaranteed matching that the product cannot prove.

A development entitlement, a registered schema, or a successful beta run does not
prove distribution eligibility. Release evidence must be tied to the exact
archive and selected operating-system support.

## Failure taxonomy

| Failure | Likely boundary | Recovery |
| --- | --- | --- |
| Query never called | SDK/system availability or target registration | Verify selected SDK, target, signed system invocation |
| Query called with no results | Labels/buffer absent, threshold too strict, store unavailable | Return empty honestly; expose app search |
| Wrong result | Mapping/model/index or stale entity | Fix fixture/ranking and re-run current lookup |
| Card unreadable | Display representation/localization/image size | Shorten fields, use native localized display |
| Tap opens wrong record | Unstable ID or stale cache | Re-resolve current ID and account scope |
| Union card cannot open | Missing OpenIntent/query for a case | Add route or omit case |
| More results opens home | Continuation state not wired | Use scoped search navigation |
| Private result leaks | Account/store boundary missing | Filter at query and open time; clear state |
| UI depends on glass | Material is carrying hierarchy | Restore solid/reduced-transparency design |
| Accessibility loses selection | Focus/identity not restored after handoff | Add accessibility focus and stable destination |
| Slow query | Full catalog/model/network work in query | Precompute, cap candidates, local fallback |
| Beta API changed | SDK contract drift | Record SDK and regenerate/compile the route |

## Proof status template

~~~yaml
tests:
  fixture_query: pass
  entity_projection: pass
  open_re_resolution: pass
  union_routes: not-tested
  semantic_search_continuation: not-tested
  accessibility_task: not-tested
system:
  visual_intelligence_invocation: not-tested
  result_card: not-tested
  open_handoff: not-tested
  process_termination: not-tested
device:
  physical_model: <model>
  os: <version>
  signed_build: <version-build>
release:
  archive_inspection: not-tested
  privacy_review: not-tested
  localization_review: not-tested
  app_store_claim_review: not-tested
notes:
  - <sanitized note>
~~~

Do not promote not-tested to pass because the app’s ordinary search path works.

## Sources

- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [SemanticContentDescriptor.labels](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor/labels)
- [Visual intelligence App Intents domain](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [DisplayRepresentation](https://developer.apple.com/documentation/appintents/displayrepresentation)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [App Intents updates](https://developer.apple.com/documentation/updates/appintents)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [Searching](https://developer.apple.com/design/human-interface-guidelines/searching)
- [Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

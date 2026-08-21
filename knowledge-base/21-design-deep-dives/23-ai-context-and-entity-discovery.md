# Apple Intelligence context and entity discovery design

## Design goal

Apple-native intelligence begins with a truthful semantic model, not a glowing AI button. When an app exposes an AppEntity, query, schema, transfer representation, or onscreen context, it is telling system experiences what the content means and which actions are valid.

Design the route so a person can:

    see an item in the app
      -> refer to it naturally in a system conversation
      -> resolve the current entity
      -> review the intended scope and ownership
      -> perform a bounded action
      -> continue through a snippet, universal link, or full app

The app remains the authority for account, permission, current data, and side effects. Apple Intelligence is a system-mediated consumer of the contract.

## Semantic design is product design

An AppEntity’s title, subtitle, type name, synonyms, properties, query behavior, and URL representation are user-facing product language. They influence how a person finds and understands the entity in system surfaces.

Use a semantic review table:

| Design field | Question |
| --- | --- |
| Entity type name | Would a person use this noun outside the app? |
| Title | Is it unique enough to resolve without leaking private detail? |
| Subtitle | Does it add useful context such as date, category, or location? |
| Synonyms | Are they genuine localized terms people might say? |
| Properties | Do they help resolution without exposing unnecessary content? |
| Query | Can the app retrieve current data by ID and by supported search input? |
| Ownership | Does the entity’s shared/public state affect the action? |
| Transfer | Is there a safe equivalent system value? |
| URL | Can the app re-open a precise, authorized destination? |
| Schema | Does a documented domain genuinely match the action/entity meaning? |

Do not fill metadata with SEO-style keyword lists or private notes. A system phrase that resolves to the wrong record is a design failure even if the in-app screen looks polished.

## Context hierarchy

Use the smallest context that makes the person’s reference unambiguous:

1. current view or selected item;
2. associated AppEntity;
3. stable ID and current query resolution;
4. ownership/account check;
5. explicit confirmation for sensitive operations;
6. full-app handoff when system context is insufficient.

Context should reduce friction, not remove consent. “This project” can identify the current project, but it must not authorize deleting or sharing it.

## Display and spoken presentation

Design DisplayRepresentation for both visual and conversational use:

- title first;
- subtitle only when it disambiguates;
- image or symbol only when it carries meaning;
- no private body text in a title or subtitle;
- localized type names and numeric formats;
- synonyms that match real language;
- stable copy across app, Spotlight, Siri, Shortcuts, and snippets.

For voice, write the result as if the person cannot see the screen. Include the object and outcome, but do not speak secrets or long raw model output. If a task needs visual review, return a snippet or open the app with a precise destination.

## Schema choice and visual tone

The system’s schema domain carries semantic consistency across apps. The app’s visual identity still lives in its own SwiftUI surfaces.

Use this separation:

| Concern | System contract | App-owned presentation |
| --- | --- | --- |
| Meaning | App schema, entity properties, query | Product naming and hierarchy |
| Discovery | Spotlight, Siri, Apple Intelligence, Shortcuts | In-app search and visible affordances |
| Context | AppEntity associated with view/activity | Selected state and navigation |
| Result | IntentResult, dialog, snippet, URL | SwiftUI detail/review screen |
| Material | System owns the invocation container | App uses native SwiftUI and restrained Liquid Glass |
| Action | AppIntent and authorization | Semantic button, confirmation, and recovery |

Do not wrap an app-owned screen in custom glass to imitate Apple Intelligence. Use the documented system handoff and make the app screen feel native through typography, spacing, system controls, accessibility, and adaptive composition.

## Cross-device continuity

Stable identifiers, universal links, and context associations can help a person continue a task on another device. Design the handoff as a state transition:

    device A context
      -> stable entity reference or universal link
      -> device B resolves current account and record
      -> current, unavailable, or permission-required state
      -> app/snippet review

Show continuity status when it affects trust. A task that was edited on one device should not silently display an old snapshot on another. If the record is unavailable, explain that it is unavailable rather than showing an empty success state.

Do not encode private content in a universal link. Use an opaque stable identifier and re-fetch after authentication. Keep a manual search route when stable resolution fails.

## Shared and public content

Ownership is part of the interaction design when an entity can be shared or public:

- label the scope before the action;
- show who may be affected when that is known;
- distinguish private, shared, public, and unknown;
- require confirmation for destructive or sensitive shared/public actions;
- re-check ownership at the point of mutation;
- show a nonrevealing fallback when the person loses access.

OwnershipProvidingEntity can help the system supply better confirmation context, but app-owned confirmation remains necessary for product-specific consequences. Do not use the system’s ownership flag as a shortcut around authorization.

## Transfer design

When an app entity maps to a common system value, a transfer representation can make cross-app workflows feel coherent. Choose a conversion that preserves meaning but minimizes data:

- project location to PlaceDescriptor, not the project’s private notes;
- app contact to IntentPerson with a validated identifier;
- app file to IntentFile with security-scoped handling;
- app-specific record with no transfer when no safe system equivalent exists.

The receiving app or system may use the value in a new context. Treat imports as untrusted and resolve them through the current account. Provide a failure path when the system value cannot be mapped.

## Relevance and timing

Relevant entity donations are a suggestion design problem:

- choose a context the person understands;
- donate only current, user-benefiting items;
- replace the full suggestion set when context changes;
- clear the set when no suggestion is appropriate;
- avoid turning engagement or commercial ranking into “relevance” without a clear user benefit;
- record why the app donated and when it will expire or be replaced.

Relevance should not feel like an unsolicited content feed. If the person cannot understand why an item appeared, the donation criteria are probably too broad.

## AI proposals and review

When the app has its own on-device model, show the difference between:

| State | Copy and affordance |
| --- | --- |
| Source | “From this capture…” or the original record |
| Proposal | “Suggested label” or “Possible destination” |
| Validated | “Matches an existing project” after deterministic checks |
| Approved | “Saved to Project A” only after the domain write |
| Rejected | Keep the source and offer manual correction |
| Unavailable | Explain model/device/language state and provide manual path |

Do not blend the system’s Apple Intelligence discovery surface with the app’s own model output. They may both be useful, but their provenance, availability, and control boundaries differ.

## Runtime states as visual states

Schema and entity routes need visible states:

| Runtime state | Design response |
| --- | --- |
| Query in progress | Compact loading state; no false match |
| Multiple matches | Clear disambiguation with meaningful subtitles |
| No match | Explain the search scope and offer a manual route |
| Deleted entity | Nonrevealing unavailable state |
| Signed out | Remove old projections and require account recovery |
| Shared/public entity | Show scope and review before consequence |
| Cross-device ID unresolved | Explain continuity failure and offer local search |
| Transfer import rejected | Show unsupported value and app-owned alternative |
| Schema unavailable on older OS | Keep in-app path and a safe fallback |
| Background runtime | Progress, cancellation, and durable checkpoint |
| Undo unavailable | Preserve an app-owned recovery path |

## Accessibility and localization

System intelligence metadata is still interface content:

- localize entity type names, titles, subtitles, synonyms, parameter summaries, and dialogs;
- test long names, pluralization, dates, measurements, and right-to-left languages;
- make ambiguity understandable with text, not color alone;
- give full-app and snippet handoffs accessible labels;
- ensure VoiceOver can complete the same review and confirmation task;
- keep model/proposal language readable at large text sizes;
- test voice-friendly phrasing independently of visual layout.

The best entity identifier is not necessarily the best spoken label. Store stable identity separately from localized presentation.

## Native Liquid Glass boundary

Use Liquid Glass for app-owned functional groups when it helps organize review or action state. Do not try to reproduce the outer system intelligence container. Keep the semantic content legible if transparency is reduced or the system changes its treatment.

Good app-owned surfaces:

- a review card showing a proposed entity mapping;
- a confirmation group with primary and cancel actions;
- a compact status shell around a full-app handoff;
- a resolved entity detail screen with native navigation.

Avoid:

- decorative “AI bubbles” with no state or action;
- nested translucent cards behind every metadata row;
- model-generated gradients that encode certainty;
- hiding source/provenance under glass;
- custom system chrome that competes with the OS-owned surface.

## Design review

- [ ] Entity type, title, subtitle, synonyms, and properties use real product language.
- [ ] Schema domain matches the capability and any required group is complete.
- [ ] Query resolves current IDs and handles ambiguity, deletion, and account scope.
- [ ] Context associations expose only safe visible content.
- [ ] Stable IDs and universal links revalidate access on every device.
- [ ] Ownership state is visible when it changes consequence or confirmation.
- [ ] Transfer representations are minimal and reversible only when safe.
- [ ] Relevance donations are bounded, replaceable, and clearable.
- [ ] Model proposals show provenance and a manual fallback.
- [ ] Background, cancellation, undo, and foreground handoff states are designed.
- [ ] Dynamic Type, VoiceOver, Voice Control, localization, and RTL are tested.
- [ ] Liquid Glass remains restrained and app-owned.
- [ ] Copy avoids claims about guaranteed Apple Intelligence selection or availability.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [DisplayRepresentation](https://developer.apple.com/documentation/appintents/displayrepresentation)
- [SyncableEntity](https://developer.apple.com/documentation/appintents/syncableentity)
- [OwnershipProvidingEntity](https://developer.apple.com/documentation/appintents/ownershipprovidingentity)
- [IntentValueRepresentation](https://developer.apple.com/documentation/appintents/intentvaluerepresentation)
- [RelevantEntities](https://developer.apple.com/documentation/appintents/relevantentities)
- [URLRepresentableEntity](https://developer.apple.com/documentation/appintents/urlrepresentableentity)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

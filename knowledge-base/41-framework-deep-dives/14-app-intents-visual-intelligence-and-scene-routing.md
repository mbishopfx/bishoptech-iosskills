# App Intents, Visual Intelligence, and scene-routing contracts

## Scope

Visual Intelligence is a system-owned discovery surface. A person points the
Visual Intelligence camera at a scene or selects content onscreen; the system
passes a semantic description to an app integration; the app searches its own
content and returns app entities that the system can display and open.

This page turns Apple’s iOS 26-era documentation into an implementation
contract for apps that want their content to appear in Visual Intelligence,
Spotlight, Shortcuts, Siri, or a related Apple Intelligence handoff. It focuses
on the concrete route below rather than treating “AI integration” as a single
feature:

    system camera or onscreen selection
      -> SemanticContentDescriptor
      -> IntentValueQuery
      -> label search and/or pixel-buffer search
      -> localized AppEntity projection
      -> Visual Intelligence result
      -> OpenIntent
      -> app-owned detail or action

For a larger catalog, add a second path:

    limited ranked results
      -> semanticContentSearch schema
      -> app-owned search/navigation state
      -> full in-app result experience

The system owns capture, system ranking, and the result container. The app owns
its content store, matching policy, authorization, entity projection, detail
screen, and any side effect that follows a tap. A returned result is not proof
that the image identifies a person, place, product, or object with certainty.

## Baseline and version boundary

The current Apple documentation for Visual Intelligence and
`SemanticContentDescriptor` is labeled as beta/preliminary in parts of the
documentation set. Treat the route as an iOS 26 SDK research and implementation
target until the exact selected SDK and final OS are checked.

Keep these gates separate:

| Gate | Question | Evidence |
| --- | --- | --- |
| Source | Does Apple document the framework, protocol, schema, and descriptor? | Official documentation and release/update notes |
| Compile | Do the imports, macros, generated requirements, and query signatures compile in the named target? | A named Xcode target using the selected SDK |
| Availability | Is the capability available on this OS, platform, device, and system configuration? | `@available` branch plus runtime checks and device matrix |
| System invocation | Does the OS actually call the query and render the result? | Signed physical-device Visual Intelligence run |
| Domain truth | Does the app’s match correspond to a current authorized record? | Deterministic catalog fixtures and current-store lookup |
| Release | Are target membership, privacy configuration, localization, capabilities, and distribution artifacts correct? | Archive/export inspection and release validation |

Do not infer system invocation from a successful local `perform()` call, a
preview, a unit test, or a simulator screen.

## Framework responsibilities

| Responsibility | Apple route | App-owned decision |
| --- | --- | --- |
| Captured scene description | `VisualIntelligence` and `SemanticContentDescriptor` | Whether to use labels, the pixel buffer, or both |
| System query bridge | `IntentValueQuery` from `AppIntents` | How much work can finish within the system’s search interaction |
| Content projection | `AppEntity`, `DisplayRepresentation`, `TypeDisplayRepresentation` | Which fields are safe and useful outside the app |
| Multiple result types | `@UnionValue` | Which finite entity cases are meaningful and openable |
| Open result | `OpenIntent` | How to resolve the selected entity and navigate to current truth |
| Full search handoff | `@AppIntent(schema: .visualIntelligence.semanticContentSearch)` | How to continue the search in the app |
| Optional deterministic vision | Vision/Core ML or another local index | Matching model, preprocessing, ranking, and fallback |
| Optional system indexing | Core Spotlight/App Intents indexing | Whether the same entities should be discoverable by text/semantic search |
| Native shell | SwiftUI/UIKit and HIG | Detail, search, review, accessibility, and Liquid Glass composition |

The Visual Intelligence framework does not replace an app’s content database,
authorization layer, search index, or domain validation.

## The descriptor contract

`SemanticContentDescriptor` represents a scene captured by Visual Intelligence,
such as a screenshot, photo, or photo/video stream. The documented public
inputs are:

| Input | Meaning | Safe use |
| --- | --- | --- |
| `labels` | General labels that Visual Intelligence uses to classify content | Fast coarse filtering or candidate generation |
| `pixelBuffer` | Optional captured image buffer | Local image search, feature extraction, or a bounded model request |

Important boundaries:

- Labels are general high-level terms in the `en_US` locale and can change over
  time.
- The framework does not translate the labels or provide synonyms.
- A label such as `tower` or `building` does not identify a particular landmark.
- `pixelBuffer` can be absent; the query must still return a truthful result.
- The system’s descriptor is not a permission to access the app’s camera,
  photo library, contacts, or location data.
- Do not retain a raw capture merely because the query received one. If the
  product needs history, state the user-visible purpose, retention period,
  storage boundary, and deletion path.

Prefer a two-stage matcher:

    labels -> small candidate set
    pixelBuffer -> rank or confirm candidates

If the buffer is missing, use labels only. If labels are unhelpful, use the
buffer only. If neither produces a sufficiently relevant result, return an
empty array instead of manufacturing a match.

## `IntentValueQuery` is the system search boundary

Adopt `IntentValueQuery` for the query that returns entity values to the system.
For Visual Intelligence, implement the `values(for:)` requirement with a
`SemanticContentDescriptor` input. The query should be a thin adapter over a
search service that is fast, cancellable, privacy-reviewed, and safe to execute
outside the main app UI process.

Conceptually:

    IntentValueQuery
      -> validate descriptor
      -> derive candidates
      -> rank current authorized records
      -> map records to AppEntity values
      -> return a small result set

The query should:

1. Avoid requiring a SwiftUI scene or navigation stack.
2. Resolve current account and data-access state before returning private data.
3. Bound pixel-buffer conversion, model work, disk reads, and network time.
4. Return the most relevant results first.
5. Return an empty result when no safe match exists.
6. Surface a recoverable error only when the system can act on it; otherwise
   fail closed with no result and log a privacy-safe diagnostic.
7. Keep raw capture, model features, and private record fields out of logs.

Apple’s documentation states that an app should not define more than one
`IntentValueQuery` taking a `SemanticContentDescriptor`. If the app needs to
return more than one entity type, use a union value rather than adding competing
descriptor queries.

## App entity projection

An `AppEntity` is a system-facing projection, not a mirror of a persistence
model. Give the system only what it needs to present and reopen the result.

Minimum design contract:

- stable identifier scoped to the app’s account/data model;
- `typeDisplayRepresentation` that is localized and understandable;
- `displayRepresentation` with a concise title, useful subtitle, and suitable
  image or thumbnail;
- a default query that can re-resolve the identifier;
- current authorization and deletion handling;
- an `OpenIntent` for every result type that the system can select;
- an explicit fallback if the record is no longer available.

The display representation is compact system UI. Put the identifying facts in
the title and subtitle, use a thumbnail-sized image when appropriate, and avoid
private notes, raw model context, access tokens, or unbounded descriptions.

`displayRepresentation` is not a confidence score. If confidence matters to
the product, expose a carefully worded match explanation in the app-owned detail
screen and distinguish “matched,” “suggested,” “verified,” and “not found.”

## Multiple entity types with `@UnionValue`

Use `@UnionValue` when one search can legitimately return a finite set of entity
types, such as a landmark and a collection containing that landmark. Each case
needs:

- a clear semantic meaning;
- a display representation that makes the type obvious;
- an entity query that can resolve the selected value;
- an `OpenIntent` for that type;
- a privacy and authorization policy;
- a deterministic empty/deleted/unavailable behavior.

Do not use a union to hide an untyped model result or to return arbitrary JSON.
If a future entity type is not understood by the installed app, the app should
omit it or hand off to the full app rather than returning an unopenable card.

## Opening a selected result

Implement `OpenIntent` for each entity type returned by the Visual Intelligence
query. Its job is to land on the selected content, not to redo the entire image
search or silently perform an irreversible action.

The open route is:

    selected entity ID
      -> current account/store lookup
      -> existence and authorization check
      -> app navigation state
      -> detail screen or honest unavailable state

Re-resolve the entity. Do not trust a stale title, subtitle, image, or local
cache supplied by the prior query. If the record was deleted, archived, moved,
or access changed, show a clear recovery path such as in-app search, account
selection, or an unavailable result. If opening would cause a side effect, use a
separate explicit action with confirmation rather than hiding the mutation in
`OpenIntent`.

## The `semanticContentSearch` continuation

Visual Intelligence results should stay concise. If the app has a large
catalog or a rich search experience, expose a “More results” path using the
documented `semanticContentSearch` App Intent schema:

~~~swift
@AppIntent(schema: .visualIntelligence.semanticContentSearch)
struct ContinueVisualSearchIntent: AppIntent {
    var semanticContent: SemanticContentDescriptor

    func perform() async throws -> some IntentResult {
        // Re-run bounded search and route the app-owned search state.
        return .result()
    }
}
~~~

The schema supplies the semantic-content parameter through the documented
generated contract. Use Xcode completion for the exact requirements in the
selected SDK. The intent should open the app-owned search experience, preserve
the captured context only as long as needed, and pre-populate results or filters
without pretending the capture is durable domain truth.

When the app opens:

- make the search scope visible;
- show whether results came from labels, image matching, or both;
- keep the person in control of filters and navigation;
- offer a new text search if the visual match was weak;
- avoid displaying raw capture data after its purpose ends;
- restore only the minimal pending navigation state after termination.

## Matching strategies

### Labels-only search

Use labels when the content catalog has strong category metadata. Normalize
labels only for matching; do not claim that normalization changes the system’s
locale or adds synonyms. Keep a documented mapping such as:

| System label | App candidate field | Result policy |
| --- | --- | --- |
| `tower` | landmark category and indexed aliases | Candidate filter only |
| `building` | place type and searchable description | Candidate filter only |
| `book` | product/content category | Candidate filter only |

The mapping is an app heuristic. It must not be treated as the system’s
identification of a named object.

### Pixel-buffer search

Use the pixel buffer when image similarity is central to the product. A common
local route is:

    captured buffer
      -> bounded image conversion
      -> feature representation
      -> compare with precomputed catalog representations
      -> threshold and rank
      -> current entity lookup

Precompute catalog features when possible so the query does not perform an
unbounded scan or repeatedly encode every asset. Keep the query’s input size,
maximum candidates, distance threshold, timeout, and memory policy explicit.

### Hybrid search

Combine labels and image similarity only when the combination improves relevance:

    label candidate score
      + image similarity score
      + current availability boost
      - stale/private/unavailable penalty
      -> final ranked results

Store the scoring version with test fixtures. A change to preprocessing, model
revision, threshold, or ranking can change which entity appears first; it needs
regression evidence and should not silently invalidate a user-visible action.

### Network-backed search

Network search can be appropriate for a large authorized catalog, but the query
must have an offline and timeout path. Send the smallest permitted representation
of the capture, document the server boundary, and never upload a raw image or
private catalog context without a clear user-facing reason and privacy review.

If the network is unavailable, return local results or an empty result. Do not
block the system surface indefinitely while waiting for a server.

## Relationship to Spotlight and Apple Intelligence

Visual Intelligence and Spotlight solve different discovery inputs:

| Surface | Input | Primary app contract |
| --- | --- | --- |
| Visual Intelligence | Camera/screenshot scene | `SemanticContentDescriptor` + `IntentValueQuery` |
| Spotlight | Text, semantic index, system search | `IndexedEntity`/Core Spotlight donation and open route |
| Shortcuts | User-configured action graph | `AppIntent`, parameters, result, and shortcut metadata |
| Siri/Apple Intelligence | Natural language, context, app schemas, entity resolution | Schema/entity/query/transfer/context contracts |

Reuse the same app entity and current-store resolution where semantics match.
Do not make Spotlight metadata, an App Intent display title, and a Visual
Intelligence card expose different identities for the same record without an
explicit reason.

Indexing an entity does not make the Visual Intelligence query unnecessary. A
large or frequently changing catalog may need `IntentValueQuery` even when only
a stable subset is indexed.

## Process, target, and actor boundaries

Place the query and its dependencies in the target that the selected SDK and
Apple route allow to execute. Keep the query independent from the app’s scene
and UI actor. A practical split is:

    shared package/module
      - AppEntity projections
      - query protocols and matching service
      - stable IDs and display data

    app target
      - navigation, detail UI, full search, user review

    optional extension target
      - system-facing intent/query execution if the product uses one

The shared route still needs explicit synchronization and Sendable boundaries.
Do not pass a SwiftData model context, mutable view model, or UIKit controller
into a query without a documented actor/process design. Treat dependencies as
unavailable and return a safe empty/error state when the process cannot access
the required store.

## Availability and fallback matrix

| State | Query behavior | App behavior |
| --- | --- | --- |
| Framework/SDK unavailable | Do not compile or register the route for that target | Keep ordinary in-app search and navigation |
| Runtime system surface unavailable | Route is not invoked | Expose the feature only through supported app surfaces |
| Descriptor has labels only | Use bounded label search | Show text/image search continuation if useful |
| Descriptor has pixel buffer only | Use local image matching | Explain no-name/low-confidence state in the app |
| Both inputs unavailable | Return `[]` | Offer normal app search; do not request unrelated permissions |
| Store/account unavailable | Return no private result or a precise recoverable error | Sign-in/permission/retry path in app |
| No match above threshold | Return `[]` | Explain how to refine or continue search |
| Selected entity deleted | Re-resolve and fail honestly | Show deleted/unavailable state and alternate search |
| Network timeout | Use local fallback or return `[]` | Do not strand the person in an indefinite spinner |
| Model/feature asset unavailable | Use label/index route | Degrade to deterministic search and record a local diagnostic |

## Privacy and safety contract

Visual search may involve a person’s surroundings, screen content, documents,
faces, addresses, or other sensitive material. Treat the descriptor as sensitive
input even when the app does not persist it.

- Do not log raw labels with account identifiers unless the product has a clear
  diagnostic purpose and retention policy.
- Do not store pixel buffers, generated features, or server payloads by default.
- Redact screenshots and thumbnails before analytics or bug reports.
- Search only records the current account is allowed to see.
- Re-check authorization when an entity opens or mutates.
- Keep “matched” separate from “verified,” “owned,” or “safe.”
- Do not let a visual match authorize a purchase, message, door unlock, medical
  action, or other high-consequence operation.
- Route any consequential action through an explicit app-owned confirmation and
  a current domain check.

## Accessibility and native composition

The Visual Intelligence result container is system-owned. The app controls the
detail and continuation screens. Use native SwiftUI controls, navigation, search
fields, sheets, and toolbar items so the app remains legible and operable with
VoiceOver, Dynamic Type, keyboard/pointer input, Reduce Motion, and Reduce
Transparency.

For a Liquid Glass-era detail screen:

- keep the content hierarchy primary;
- use glass for functional controls and grouped navigation, not as a full-page
  decorative layer;
- keep image, title, subtitle, source/match explanation, and actions distinct;
- provide a solid or reduced-transparency fallback;
- keep the open transition short and understandable;
- do not mimic Apple’s branding, system result cards, or private system UI;
- ensure the selected entity has a spoken name and useful context.

Visual Intelligence is a discovery route, not a reason to place a translucent
overlay over every pixel of the app.

## Integration checklist

- [ ] Selected SDK and final OS status are recorded; beta/preliminary docs are
      not presented as release proof.
- [ ] The query accepts the documented `SemanticContentDescriptor` input.
- [ ] Labels and pixel-buffer paths work independently.
- [ ] The app does not define competing descriptor queries.
- [ ] Results are current, account-scoped, localized, ranked, and bounded.
- [ ] Every union case has a query and `OpenIntent` path.
- [ ] `OpenIntent` re-resolves current truth and does not hide side effects.
- [ ] The semantic-content continuation opens an app-owned search route.
- [ ] Raw capture, features, and private metadata have an explicit retention
      and redaction policy.
- [ ] Query code does not require a SwiftUI scene or unbounded network work.
- [ ] Accessibility, localization, Dynamic Type, reduced-effects, and fallback
      paths are exercised on a physical device.
- [ ] The actual Visual Intelligence system invocation is tested with a signed
      build; compile evidence and system evidence remain separate.

## Sources

- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [SemanticContentDescriptor.labels](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor/labels)
- [Visual intelligence App Intents domain](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [Visual intelligence in App Intents](https://developer.apple.com/documentation/appintents/visual-intelligence)
- [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [DisplayRepresentation](https://developer.apple.com/documentation/appintents/displayrepresentation)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [App Intents updates](https://developer.apple.com/documentation/updates/appintents)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [Searching](https://developer.apple.com/design/human-interface-guidelines/searching)
- [Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

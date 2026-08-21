# App Intents system surfaces and Visual Intelligence design

## Outcome

Design a native-feeling path from a person’s camera or onscreen selection to a
useful app result without pretending the app owns the system capture surface.
The system should handle discovery; the app should make the result legible,
trustworthy, openable, accessible, and useful after handoff.

The composition is:

    system-owned Visual Intelligence result
      -> compact app entity representation
      -> app-owned detail or “More results” search
      -> optional review
      -> explicit app action

This is an Apple-platform design contract, not a pixel-copy recipe. Recreate
the principles of hierarchy, restraint, context, and direct manipulation with
native SwiftUI/UIKit controls. Do not imitate Apple logos, private system sheets,
or system-only visual treatments.

## Design ownership map

| Surface | Owner | Design responsibility |
| --- | --- | --- |
| Visual Intelligence capture and initial result container | System | The app supplies a valid query/entity contract; it does not style the container |
| Entity card content | App projection, system presentation | Localized title, subtitle, thumbnail, type, and privacy-safe identity |
| Entity open | App | Resolve current record, handle unavailable state, and land in the right context |
| More-results continuation | App Intent plus app UI | Reuse the capture context briefly and provide full search/filter/navigation |
| Detail screen | App | Explain the match, show source/current state, and offer actions |
| Destructive or consequential action | App domain | Confirmation, authorization, current-state check, and recovery |
| Liquid Glass composition | App UI | Functional grouping and legibility; never cover content with decoration |

The initial result is a discovery hint. The app-owned detail screen is where the
person can inspect current data and decide what to do next.

## Information hierarchy for the result

The system result has limited space. Design the entity projection around the
first three questions a person has:

1. What is this?
2. Why is it relevant to what I pointed at?
3. What happens if I open it?

Use a compact representation:

    title       = primary identifying name
    subtitle    = disambiguating context
    image       = relevant thumbnail, not an unbounded original
    open action = detail destination, not hidden mutation

Examples:

| Product type | Title | Subtitle | Detail continuation |
| --- | --- | --- | --- |
| Landmark catalog | “City Hall” | “Downtown · Landmark” | Hours, map, history, saved notes |
| Personal photo index | “Trail marker” | “Trip journal · 14 photos” | Source photos, date, collection |
| Design asset library | “Glass card reference” | “UIKit patterns · 3 variants” | Asset metadata and export/review |
| Music catalog | “Album title” | “Artist · 2026 collection” | Album/artist detail and playback route |

Do not put a confidence percentage in the subtitle unless the product has a
well-defined calibrated meaning and the system surface gives enough context to
interpret it. A raw embedding distance is not user-facing certainty.

## The native handoff shell

When the person taps a result, the app should feel like a continuation, not a
new unrelated experience:

    result tap
      -> resolve ID
      -> set pending destination
      -> activate app scene
      -> navigate to detail
      -> focus the selected content

Use the app’s normal navigation model. A `NavigationStack` destination, a
standard sheet, or a clearly scoped full-screen route is preferable to a custom
modal that hides the back path. The selected entity should be visible in the
navigation title, spoken by VoiceOver, and recoverable after a brief process
restart if the route is user-visible.

If the record is missing:

- keep the same destination shell so the state change is understandable;
- explain that the item is unavailable, deleted, or no longer accessible;
- offer in-app search or account recovery when appropriate;
- do not show stale private content as if it were current;
- do not send the person back to a blank root screen.

## “More results” is a real search destination

The `semanticContentSearch` handoff should not land on a generic home screen.
Design an in-app search state that preserves the useful parts of the captured
context while making the new scope obvious:

    Search in [Catalog]
    [visual context chip] [clear]
    Results ranked by relevance
    [filters] [sort]
    result list/grid

Rules for the continuation:

- Show a visible search title or prompt describing the current scope.
- Use a native search field when text refinement is useful.
- Let the person clear visual context and start a normal text search.
- Keep the first result group small and ordered by relevance.
- Use categories or scope controls only when they reduce ambiguity.
- Avoid showing private search history on a shared screen without consent.
- Preserve the visual context as ephemeral state unless the person saves it.
- Display an honest empty state when no result passes the app’s threshold.

Apple’s search guidance emphasizes a clear scope, useful suggestions, relevant
ordering, and privacy-aware history. The Visual Intelligence guidance similarly
encourages a quick, limited result set and a full app route for additional
results.

## Liquid Glass rules for the app-owned route

Use Liquid Glass as a functional material for controls and navigation, not as a
brand substitute or a universal background. A useful hierarchy is:

    content plane
      -> readable image/text/result content
      -> functional controls grouped above it
      -> system navigation and actions

Apply these rules:

1. Keep the primary content on an uncluttered plane.
2. Group related controls into one glass container when the group behaves as one
   unit.
3. Prefer native toolbars, tab bars, sheets, buttons, menus, and search fields.
4. Avoid stacking multiple translucent surfaces over each other.
5. Maintain contrast when the image underneath changes.
6. Treat glass as a material with state, not as a permanent decorative border.
7. Use morphing or matched transitions only when identity is preserved and the
   motion explains the handoff.
8. Provide reduced-transparency, reduced-motion, and low-power fallbacks.
9. Keep destructive actions visually and semantically distinct from navigation.
10. Never rely on blur, vibrancy, or translucency alone to communicate status.

For an entity detail page, a restrained structure might be:

    navigation title / back
    hero image or content preview
    title + type + source/match context
    fact list or metadata
    primary action
    secondary actions in a toolbar or menu

The detail content should still make sense if all glass effects are removed.

## Match explanation without false certainty

People need to understand why an item appeared. Put explanation in the app,
not in a misleading system card:

| State | Preferred copy pattern | Avoid |
| --- | --- | --- |
| Strong local match | “Looks like a saved City Hall landmark.” | “Identified with 99% certainty.” |
| Label-only candidate | “Matches the category ‘building’.” | “This is definitely…” |
| Multiple candidates | “Possible matches” with ranked cards | Choosing one silently |
| No match | “No saved item matched this scene.” | Pretending a generic result is exact |
| Stale/private record | “This item is no longer available here.” | Showing the old private thumbnail |
| AI-enriched explanation | “Suggested description” with source/context | Presenting generated text as verified fact |

If the app uses Vision, Core ML, Natural Language, or Foundation Models to
enrich a result, show the source and status of the enrichment. Keep generated
prose separate from canonical metadata and give the person a review/apply step
before any durable edit.

## Search result layouts

Choose the layout from the content, not from a desire to look like a particular
Apple app:

| Content | Layout | Why |
| --- | --- | --- |
| One precise item | Detail card or list with one emphasized result | Supports quick confirmation and opening |
| Several similar items | List with thumbnail, title, subtitle, and type | Supports comparison and VoiceOver order |
| Media/catalog items | Adaptive grid plus accessible labels | Uses image recognition without losing text identity |
| Mixed entity types | Sectioned list or type chips | Prevents a landmark, collection, and event from blending together |
| Large result set | Search view with scope/filter | Keeps system result fast and hands depth to the app |

Do not place a decorative glass card around every row. Use semantic list/grid
containers, stable identity, and one consistent selection behavior.

## Accessibility contract

The system can open the app in a context the person did not reach through the
app’s usual first screen. The handoff destination must be a complete accessible
task, not just a visually impressive landing state.

- Give every result a concise spoken name and type.
- Expose why the result is relevant without reading raw model internals.
- Keep title, subtitle, thumbnail, and action in a logical reading order.
- Ensure Dynamic Type does not truncate the identifying name without an
  accessible alternative.
- Use native `Button`, `NavigationLink`, `SearchField`/`.searchable`, `List`,
  `LazyVGrid`, menus, and sheets where their semantics fit.
- Test VoiceOver focus after the app opens from the system result.
- Test keyboard, pointer, Switch Control, and Voice Control paths where the
  product supports iPad or Mac.
- Respect Reduce Motion when a result morphs into a detail screen.
- Respect Reduce Transparency and keep text legible over light/dark imagery.
- Do not use color or blur alone to distinguish “matched,” “saved,” “private,”
  or “unavailable.”
- Make empty, error, sign-in, limited-data, and permission states accessible.

Accessibility audits are diagnostics. They do not replace task completion with
actual assistive technology on a physical device.

## Privacy-first visual search design

The UI should make the data boundary understandable without exposing raw
capture data unnecessarily:

    system capture
      -> ephemeral query input
      -> ranked app result
      -> user-visible detail
      -> optional saved context only by choice

Design decisions:

- Do not show a raw screenshot thumbnail in the app after the search unless it
  helps the task and the person can remove it.
- Show whether the result came from the local catalog, a network service, or a
  system store integration.
- Make account scope visible when results depend on a private library.
- Ask for unrelated permissions only when the person invokes the corresponding
  app feature.
- Remove pending visual-search state when the person signs out or changes the
  account.
- Avoid analytics events that include labels, pixel hashes, coordinates, faces,
  or private entity names.
- Keep visual matching separate from identity verification and authorization.

## Platform adaptation

Use the same entity/query semantics across iPhone, iPad, and Mac where the
framework supports them, but adapt the handoff:

| Platform/context | Design concern |
| --- | --- |
| iPhone camera/screenshot | Compact result cards, one-handed open path, clear back navigation |
| iPad | Split view or sidebar/detail can keep results and detail visible; support pointer and keyboard |
| Mac screenshot/visual context | Larger images and windows may need resizing and a more spacious search layout |
| Small window or multitasking | Preserve title, type, and primary action before secondary metadata |
| System result to app | Do not assume the app was already running or had its previous navigation stack |

The data contract can be shared, but window, scene, focus, and toolbar behavior
must be tested per platform.

## State table for design review

| State | Result surface | App-owned destination |
| --- | --- | --- |
| Querying | System may show loading/empty behavior | No app UI assumption |
| Strong match | Compact entity card | Detail with match explanation |
| Multiple matches | Ranked cards or type sections | Search/filter continuation |
| No match | No app result | Empty state with normal search |
| Pixel buffer missing | Label-derived candidates | Explain coarse match if needed |
| Offline | Local results only | Offline badge or recovery action |
| Signed out | No private result | Sign-in or public-content route |
| Deleted/permission changed | Unavailable result | Recovery/search/account route |
| AI enrichment unavailable | Canonical result remains usable | Omit optional prose and continue |
| Reduced transparency/motion | Same hierarchy, simpler effects | No loss of action or context |

## Review checklist

- [ ] The system-owned surface is not visually cloned or treated as app-owned.
- [ ] The entity card answers what, why, and where next with minimal text.
- [ ] The app opens to the selected current entity, not a generic home screen.
- [ ] “More results” leads to a scoped, clear, searchable app experience.
- [ ] Empty, ambiguous, unavailable, signed-out, and offline states are designed.
- [ ] Glass groups controls and navigation; content remains readable without it.
- [ ] Motion explains the handoff and has a reduced-motion path.
- [ ] Dynamic Type, VoiceOver, keyboard, pointer, and reduced-transparency states
      preserve the task.
- [ ] Visual matching is described as a match or suggestion, not proof of identity.
- [ ] AI-generated enrichment is labeled, source-aware, and never silently
      writes canonical data.
- [ ] Raw capture and private search context are not retained by default.
- [ ] The design is tested on the named physical device and system surface.

## Sources

- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [DisplayRepresentation](https://developer.apple.com/documentation/appintents/displayrepresentation)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [Searching](https://developer.apple.com/design/human-interface-guidelines/searching)
- [Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

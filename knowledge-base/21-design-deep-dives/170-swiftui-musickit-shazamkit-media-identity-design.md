# SwiftUI MusicKit and ShazamKit media-identity design

The media-identity experience should feel like a calm native utility: one
clear listening action, one trustworthy result review, and explicit choices
for what happens next. The visual system can use the current Liquid Glass
language, but the glass is a supporting material for controls and hierarchy,
not a substitute for media provenance or state clarity.

## Product surface map

| Surface | Primary question | Native SwiftUI shape | State that must be visible |
| --- | --- | --- | --- |
| Home / Listen | “What can I do now?” | `NavigationStack`, prominent `Button`, `ContentUnavailableView` for unavailable routes | Music permission, microphone permission, current listening state |
| Catalog search | “Which Apple Music item do I mean?” | `.searchable`, `List`, `NavigationLink`, artwork row | Loading, empty, catalog error, storefront, explicit-content context |
| Match review | “What did the system find?” | `ScrollView`/`List` card with canonical metadata and actions | Match source, confidence if available, match offset, no-match/error distinction |
| Player | “What is playing, and who owns it?” | compact bar + expanded `NavigationDestination` | Application versus system player, current entry, pause/play/error |
| Library action | “What will change?” | confirmation `alert`/`confirmationDialog` | Add to Apple Music, save to Shazam, or open only after explicit intent |
| Settings / permissions | “How do I recover?” | `Form` with deep links and explanations | Denied/restricted states, privacy copy, route reset, data retention |
| AI explanation | “What does this result mean?” | bounded text section with source label and Review affordance | Generated versus canonical text, source IDs, unavailable/fallback state |

Avoid a dashboard that puts catalog search, microphone capture, playback, and
library mutation into one undifferentiated vertical stack. These operations
have different permissions and side effects. The home surface can compose the
route, but each responsibility should be visually and semantically separated.

## Listening flow

The first screen should establish intent before presenting a protected-resource
prompt:

~~~text
idle
  -> tap Listen
  -> explain “uses the microphone to identify nearby audio”
  -> system microphone permission
  -> permission denied/restricted | permission granted
  -> Listening + Stop
  -> Match review | No match | Input/service error | Cancelled
~~~

Use a native `Button` with a concise label such as “Listen.” The button’s
accessibility label should describe the action and current state, for example
“Start listening to identify audio” or “Stop listening.” Do not use a decorative
glass capsule that looks tappable but has no semantic button role.

While listening, show a restrained activity indicator, elapsed time or a
bounded “Listening…” state, and a visible Stop action. A waveform can be a
secondary visualization of input activity; do not imply that its amplitude is
a confidence score. Avoid showing raw microphone content or recording
controls if the feature only computes a Shazam signature.

When the route ends, return focus to the match result or to the next recovery
action. If the user stops early, label the result “Cancelled” or “No result”
instead of reusing a stale previous match. If the app starts a new listening
epoch, cancel work from the prior epoch so a late result cannot overwrite the
new screen.

## Match-review card

The first match is a reviewable proposal, not an automatic command. A strong
card has this order:

1. artwork, when provided, with an informative alternate description;
2. canonical title and artist from the matched media item;
3. source badge such as “Shazam catalog” or “Your custom catalog”;
4. match timing (`matchOffset`) and confidence when the OS supplies it;
5. a short explanation of what the fields mean, not a claim of certainty;
6. explicit actions: Play, Add to Apple Music, Save to Shazam Library, Open,
   and Dismiss where each is supported;
7. a secondary “Why this result?” explanation that can use typed on-device AI
   output only after canonical fields are established.

If `SHMatch.mediaItems` contains multiple items, use a ranked list or a
“Review matches” destination. Do not silently choose the first item without a
product rule. If a match has no Apple Music ID, hide or disable the Apple Music
action and explain why; never construct a URL by guessing from title and
artist.

The card should distinguish:

- “Matched” — a framework match exists and canonical metadata is available;
- “No match” — the query completed without a catalog result;
- “Couldn’t check” — service, permission, input, or framework error;
- “Needs review” — a result exists but the app cannot safely map it to a
  supported action.

These labels are more useful than a single red/green status because they tell
the person what to do next.

## Catalog search and library design

Use `.searchable(text:)` for Apple Music catalog search and keep the search
term separate from the selected `Song` or `Album` value. Debounce requests in
the model layer, cancel stale requests, and preserve the last successful
result while the next request is loading. A catalog result is not a library
result; label the destination accordingly.

Search rows should include title, artist, album/artwork, explicit-content
indicator where relevant, and a short action affordance. Do not use artwork
alone as the tap target without a text label. Use `ArtworkImage` or a native
image route with a text fallback when artwork fails.

The library flow needs more friction than catalog browsing because it reads or
mutates personal data. Explain “Add to Apple Music Library” before the action,
show a confirmation if the item came from a match, and preserve an undo or
retry state if the request fails. Do not claim that the item was added until
the `MusicLibrary` operation succeeds. A local “saved” flag is not proof of a
remote library mutation.

If the person lacks permission, show a settings recovery action rather than
looping the authorization request. If the user has permission but the
subscription or cloud-library capability is unavailable, show the distinct
capability state and retain catalog-only or custom-catalog functionality.

## Player design and external state

The mini-player must state its ownership boundary in the model, even if the
visual treatment is compact. For an `ApplicationMusicPlayer`, “Playing in this
app” is accurate. For a `SystemMusicPlayer`, use copy that makes it clear the
Music app’s state may change. The expanded player should read from the actual
player state and current queue entry instead of mirroring a stale search
selection.

Use standard play/pause, next, previous, and seek controls with accessible
labels. Disable controls while a queue transition is pending, but retain a
cancel or recovery action. If a route interruption pauses playback, explain
that playback is paused and let the person choose Resume. Avoid automatically
resuming after every interruption or route change.

If a Shazam match opens a player, preserve a back path to the match card. The
person should be able to compare the canonical matched item with the catalog
item that will play before committing to the external or in-app player.

## Liquid Glass composition

Use Liquid Glass as a functional grouping material:

- a floating Listen/Stop control near the bottom safe area;
- a compact mini-player control group;
- a toolbar or match-action group that benefits from separation from content;
- a transient permission or status surface that must remain legible over
  artwork.

Keep artwork, title, artist, and match provenance as content rather than
turning the entire media card into an opaque glass panel. A practical hierarchy
is:

~~~text
background / artwork or system material
  -> content layer: canonical media identity
  -> secondary layer: provenance and match facts
  -> glass layer: actions and navigation controls
  -> transient layer: error, permission, or confirmation
~~~

Where the design calls for adjacent glass controls, use a shared
`GlassEffectContainer` so the controls can form one visual group. Use native
system controls first; custom `glassEffect` surfaces should be rare, small,
and tested for contrast and hit testing. Do not attach independent glass
effects to every row, badge, icon, and text block.

Glass transitions should reinforce state changes rather than entertain during
microphone capture. A short transition from Listen to Listening, and a clear
transition into Match Review, is enough. Respect Reduce Motion and avoid
parallax that makes an audio-identification flow feel uncertain or unstable.

Use tint to distinguish an action only when the tint remains legible across
artwork and accessibility settings. Never communicate match confidence only
with translucency, color, blur, or animation. Pair visual treatment with text,
icons, and VoiceOver values.

## Accessibility and alternate input

VoiceOver should encounter the result in this order: match status, title,
artist, source, timing/confidence, then actions. Combine title and artist into
one meaningful element only if it does not hide separate actions or explicit
content information. Add a custom accessibility value for confidence such as
“Match confidence 0.82” while clarifying that it is a system match signal, not
a certainty guarantee.

Test at large Dynamic Type sizes. The match card must allow title and artist
to wrap, move actions into a vertical stack, and avoid truncating the source
or recovery message. Use minimum hit targets and a logical focus order for
external keyboards, Switch Control, and Voice Control. The app must remain
usable if artwork, animation, or the AI explanation is absent.

Respect Reduce Motion and Reduce Transparency. Do not make a blurred glass
layer the only contrast mechanism. Check increased contrast, bold text, color
filters, dark/light appearance, landscape, split view on iPad, and different
safe-area placements for the floating control.

Microphone permission copy must be accessible and specific. The permission
explainer should state when capture starts, what the app computes, whether
anything is retained, and how to stop. If the app stores match history, make
delete and retention settings reachable without requiring the AI explanation.

## AI explanation design

An optional “Explain this match” affordance should never compete visually with
Play or Add to Library. The canonical match card remains useful without it.

Model input should be a typed, redacted structure containing only the selected
media item’s title, artist, genre, source, match offset, and available
confidence. The output should be a typed proposal with a short explanation,
source ID, model availability state, and review status. The UI must visibly
separate:

- canonical text from MusicKit/ShazamKit;
- generated text from an on-device model;
- user-approved actions that mutate playback or libraries.

Good uses include summarizing deterministic genre fields, explaining what a
match offset means, or drafting a neutral “sounds like” description clearly
marked as generated. Unsafe uses include identifying a song from unconstrained
model intuition, asserting that the result is licensed, guessing a catalog ID,
or creating a playlist without confirmation.

When the model is unavailable, busy, or returns invalid output, show the
canonical media result and a deterministic fallback. A model error must not
change the match state or hide the Play/Add/Open actions.

## Design acceptance checklist

Before calling the surface native-ready, verify:

- [ ] Listen, Stop, Match Review, and playback actions have native semantic
  controls and clear state labels.
- [ ] Music permission, subscription capability, microphone permission, and
  match results are represented as separate states.
- [ ] Multiple matches, no match, input error, service error, cancellation,
  and stale-result races have visible recovery paths.
- [ ] Application and system playback lanes are distinguishable to the user.
- [ ] Add-to-library and save-to-Shazam actions are explicit and only report
  success after the framework operation succeeds.
- [ ] Liquid Glass is limited to functional control groups and tested with
  Reduce Motion, Reduce Transparency, contrast, and Dynamic Type.
- [ ] VoiceOver, large text, external keyboard, Switch Control, and no-artwork
  states are tested.
- [ ] AI text is marked as generated, source-bound, optional, and non-authority
  for identity, entitlement, rights, and side effects.

## Sources

- [MusicKit](https://developer.apple.com/documentation/musickit)
- [ArtworkImage](https://developer.apple.com/documentation/musickit/artworkimage)
- [MusicLibrary](https://developer.apple.com/documentation/musickit/musiclibrary)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [SystemMusicPlayer](https://developer.apple.com/documentation/musickit/systemmusicplayer)
- [MusicPlayer](https://developer.apple.com/documentation/musickit/musicplayer)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicSubscription](https://developer.apple.com/documentation/musickit/musicsubscription)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [SHMatch](https://developer.apple.com/documentation/shazamkit/shmatch)
- [SHMatchedMediaItem](https://developer.apple.com/documentation/shazamkit/shmatchedmediaitem)
- [SHMediaItem](https://developer.apple.com/documentation/shazamkit/shmediaitem)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)

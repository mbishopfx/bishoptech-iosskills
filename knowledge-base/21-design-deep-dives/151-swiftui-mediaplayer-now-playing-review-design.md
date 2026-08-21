# SwiftUI MediaPlayer Now Playing and remote-command design

The app-owned player and Apple’s Now Playing surfaces should feel like one coherent experience without pretending they are one view. The [existing Now Playing, Lock Screen, and media-control design](48-now-playing-lock-screen-and-media-control-design.md) establishes the broad visual language. This page focuses on the design decisions that become important when a SwiftUI player publishes live metadata, receives commands from outside the app, changes audio routes, and optionally uses on-device AI.

The design contract is:

~~~text
actual player state
  -> readable in-app projection
  -> system metadata projection
  -> external command
  -> validated player action
  -> observed state
~~~

The person should never need to guess whether a label describes:

- what the app requested;
- what the player observed;
- what the audio route is doing;
- what the system surface accepted;
- what an AI model suggested.

## 1. Start with playback truth

Define these values before composing the screen:

| Value | UI question |
| --- | --- |
| Current item | What is this? |
| Creator/source | Who or what produced it? |
| Position/duration | How far through it are we? |
| Playback state | Is it preparing, playing, paused, buffering, interrupted, or ended? |
| Queue | What comes next and can next/previous actually work? |
| Route | Where is audio currently sent? |
| Now Playing eligibility | Will system controls have an actionable item? |
| Suggestion policy | Could this content appear in system suggestions? |

Do not use a large animated play button to conceal an unknown player state. If the player is preparing, say Preparing. If it is buffering, say Buffering. If a route disappeared, say Audio route unavailable.

## 2. Screen hierarchy

Use a calm native player structure:

~~~text
Navigation title / route context
  -> artwork and title
  -> creator/source
  -> live/buffering/interrupted status
  -> progress or live indicator
  -> primary transport control
  -> skip/queue/route controls
  -> chapter/transcript/context actions
  -> privacy or AI explanation disclosure
~~~

On iPhone, keep the current item and primary transport above the fold. Put queue and richer context below. On iPad, a sidebar can hold the queue while the detail column holds artwork, metadata, and controls. On CarPlay or Watch, adapt to the system surface rather than squeezing the iPhone layout into a smaller rectangle.

Keep the primary action stable while secondary controls change with capability. A play button that morphs into a retry button should announce the state change and retain an accessible label.

## 3. Metadata hierarchy

Use the same hierarchy in SwiftUI and the data sent to MediaPlayer:

1. title;
2. creator/source;
3. artwork;
4. position/duration or live state;
5. playback status;
6. queue context;
7. chapter/language/feedback actions;
8. privacy/suggestion status when relevant.

If an item is a private recording, do not style it like a public catalog track without an explanation. If the creator is unknown, omit the row rather than inventing one.

Text requirements:

- support Dynamic Type;
- keep title and creator readable with long localized strings;
- make the current status visible without relying on color;
- use a text summary for progress;
- allow VoiceOver to reach the item, status, position, and controls in order;
- do not make artwork the only identifier.

## 4. Progress and live media

For finite content, show elapsed and remaining/duration only when duration is known and the player supports seeking. For live content:

- label it Live;
- avoid a finite progress bar;
- expose only supported seek or rewind controls;
- explain buffering without suggesting a completed item;
- keep the system metadata’s live flag aligned with the player.

When a person drags the progress control:

1. show the proposed position;
2. send a typed seek request;
3. keep the old observed state until the player responds;
4. announce failure if the seek is unavailable;
5. republish the actual position.

Do not animate the playhead to a new position before the player confirms it. A fast visual jump can make a failed seek look successful.

## 5. Remote-command affordances

Remote commands are not visible buttons in the app, but they should be reflected in the app’s capability language:

| App state | System command expectation |
| --- | --- |
| Ready and paused | Play if the item is available |
| Playing | Pause and supported seek |
| Queue has next | Next track |
| Queue has no next | Next hidden/disabled |
| Live stream | Only supported live controls |
| Item unavailable | Playback controls disabled or recovery state |
| No actionable item | No transport controls claim active system ownership |
| Feedback unavailable | No rating/like/dislike command |

When a person taps the in-app control, it should call the same PlaybackCommand used by Lock Screen, Control Center, CarPlay, and Watch. This makes failure messages and accessibility behavior consistent.

If an external command arrives while a sheet or AI explanation is open, do not reset the entire navigation stack. Update the shared playback state and announce the change in the current surface.

## 6. Route and interruption design

The route line should be compact:

| Route state | Copy |
| --- | --- |
| Built-in speaker | iPhone |
| Headphones | AirPods or headphones |
| AirPlay | Living Room |
| Bluetooth | Car audio |
| Route changing | Updating audio route |
| Route unavailable | Audio route unavailable |
| Interrupted | Playback paused by another audio event |

When headphones disconnect, pause to respect privacy. Do not automatically resume through the speaker just because the player was previously playing. When a new route connects, display the route change as context, not as proof that the output is audible.

For interruptions:

- preserve item and position;
- show interrupted/paused;
- resume only under the app’s audio policy and system options;
- distinguish a user pause from an interruption;
- update Now Playing metadata after the player changes.

VoiceOver should announce “Playback paused because headphones disconnected” rather than only “Paused.”

## 7. Liquid Glass hierarchy

Use Liquid Glass for compact controls and actions, not for every pixel:

| Layer | Recommended treatment |
| --- | --- |
| Artwork/title/content | Stable, readable content surface |
| Primary transport | One prominent native control, glass only when it preserves contrast |
| Secondary transport | One grouped glass action area |
| Queue/route | Sheet, popover, or grouped action surface |
| AI explanation | Secondary disclosure or sheet |
| Buffering/error | High-contrast status surface |

Follow [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) and [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views):

- use materials to establish hierarchy;
- keep text and symbols legible;
- avoid nested translucent containers;
- preserve semantic controls and focus order;
- support a solid fallback for increased contrast or reduced transparency;
- do not mimic the Lock Screen or Control Center.

An Apple-like player uses the platform’s typography, spacing, symbols, and controls. It does not reproduce system branding or proprietary system layout.

## 8. Artwork design and privacy

Artwork can appear in the app, Lock Screen, Control Center, AirPlay, CarPlay, Watch, and accessories. It should be:

- correctly associated with the item revision;
- available at the requested size;
- safe to show on a potentially visible system surface;
- readable in light, dark, tinted, and high-contrast modes;
- not the sole content identifier.

For private or sensitive recordings, use a privacy-safe image or omit artwork in the system projection according to product policy. Do not use a blurred artwork trick that still reveals a face, diagnosis, legal matter, or private title.

When artwork is loading:

> Artwork unavailable. Audio is ready.

Do not block play/pause or remote commands on artwork retrieval.

## 9. Queue and chapter interactions

The queue screen is app-owned. It should show:

- current item;
- queue revision/freshness when relevant;
- next/previous availability;
- reorder affordance;
- remove/clear action;
- download/authorization state;
- chapter or transcript links where available.

When an external next command arrives:

1. resolve the current queue revision;
2. check the next item is still playable;
3. move the player;
4. update the in-app queue and metadata;
5. return the command result based on actual action acceptance.

For chapter jumps, show the chapter title and target time before applying an AI-proposed jump. If the media is live or ad-supported, the product policy may forbid arbitrary seek.

## 10. System suggestion disclosure

Apple documents that media donated through Now Playing may be eligible for Journal or other content suggestions unless excluded. A privacy explanation belongs near the content policy setting, not as a surprise after the first play:

> This audio may be available to Apple system suggestions. You can exclude this item.

For a private content category:

> This recording is excluded from system suggestions.

Do not suggest that the app can control another app’s final presentation. The app can set its documented exclusion metadata; the system decides how it uses eligible information.

## 11. AI explanation and queue proposal

A local AI feature should be visually secondary:

~~~text
Current item
  Title and observed playback state

Explain
  Uses this item’s metadata and transcript, if available

Proposed queue change
  3 eligible items · Review before applying
~~~

Show:

- the source item or queue revision;
- the proposal’s affected items;
- missing data;
- user-facing confirmation;
- Apply and Cancel;
- a label that the wording is generated.

The model cannot:

- claim audio played because metadata changed;
- invent a chapter or artist;
- reorder an item outside the current entitlement/account policy;
- change the system command configuration;
- expose private library records to an external service without review;
- apply an action from a passive background suggestion.

The Apply button calls deterministic code, revalidates the current queue, then changes playback. A stale proposal should become “Needs review” rather than silently applying.

## 12. Accessibility

Follow [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility):

- use native Button, Slider, Menu, and Toggle semantics;
- include title and creator in the item label;
- include playback state and route in the value or hint;
- expose elapsed position and duration in readable text;
- label skip intervals;
- announce buffering, interruption, and route changes;
- support Dynamic Type without clipping the title or primary control;
- test VoiceOver reading order;
- test Voice Control phrases such as “Play,” “Pause,” “Skip forward,” “Choose route,” and “Show queue”;
- test Switch Control, keyboard, pointer, and controller input;
- respect Reduce Motion and Reduce Transparency;
- never make artwork color the only status indicator.

Example semantic label:

> Ocean Drive, by Example Artist. Playback paused at 2 minutes 14 seconds of 4 minutes 02 seconds. Audio route: AirPods.

That label is more useful than “glass player.”

## 13. Loading, failure, and stale states

| State | Design |
| --- | --- |
| Preparing | Show title if known and a bounded progress indicator |
| Buffering | Keep item context; explain that playback is waiting |
| Interrupted | Show the reason when known and the recovery action |
| Route unavailable | Keep the item; offer route picker/retry |
| Authorization failed | Explain the account/content issue |
| Command failed | Keep the prior observed state; offer an in-app recovery |
| Stale proposal | Mark it stale and require recomputation |
| System metadata not visible | Keep playback usable; do not fake system success |
| Stopped | Clear or replace the Now Playing projection |

Never leave a successful-looking play button or active progress animation after the player reports failure.

## 14. Cross-surface consistency

Create a single surface contract:

| Source | Calls | Reads |
| --- | --- | --- |
| SwiftUI | PlaybackCommand | PlaybackState |
| Lock Screen/Control Center | Remote command | MediaPlayer projection |
| CarPlay | Template action | PlaybackState projection |
| Watch | App-owned command | Handoff/shared state |
| AI | Typed proposal | Redacted PlaybackState/queue |
| Player engine | Player operations | AVAudioSession and player observations |

This prevents a CarPlay “Pause” from changing a Boolean while the player continues to render, or an AI queue proposal from overriding a newer user reorder.

## 15. Design proof checklist

- [ ] In-app state distinguishes requested, observed, interrupted, and audible behavior.
- [ ] Metadata and commands come from one projection owner.
- [ ] System surfaces are described as system-owned.
- [ ] Command availability follows current player/queue capability.
- [ ] External command results do not claim playback without player evidence.
- [ ] Artwork is size-aware and privacy-reviewed.
- [ ] Queue and chapter proposals revalidate stale revisions.
- [ ] Headphone removal pauses private playback.
- [ ] AirPlay/CarPlay/Watch route state is separate from audible-output proof.
- [ ] Liquid Glass is limited to hierarchy and has contrast/reduced-transparency fallbacks.
- [ ] AI is labeled, typed, reviewable, and unable to mutate playback directly.
- [ ] VoiceOver, Dynamic Type, Reduce Motion, Voice Control, Switch Control, keyboard, pointer, and controller routes are tested.
- [ ] System suggestion policy is disclosed and applied per content category.

## Sources

- [Media Player](https://developer.apple.com/documentation/mediaplayer)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [MPRemoteCommand](https://developer.apple.com/documentation/mediaplayer/mpremotecommand)
- [MPChangePlaybackPositionCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpchangeplaybackpositioncommandevent)
- [MPMediaItemArtwork](https://developer.apple.com/documentation/mediaplayer/mpmediaitemartwork)
- [MPNowPlayingInfoPropertyExcludeFromSuggestions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexcludefromsuggestions)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)

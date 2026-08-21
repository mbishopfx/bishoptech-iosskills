# Universal Links, Handoff, and native routing design

## Design objective

An external event should feel like a continuation of the person’s task, not like a
mysterious jump into an arbitrary screen. Native routing makes the destination
legible, preserves the app’s navigation hierarchy, and shows the smallest amount
of review needed before an action can continue.

Design for:

- the source of the event;
- the destination and current record state;
- cold, warm, suspended, and multi-window delivery;
- authentication, privacy, and stale-link recovery;
- accessibility focus and announcements;
- a system-owned surface versus an app-owned Liquid Glass surface;
- an optional on-device AI explanation or route suggestion;
- a visible way to continue, cancel, go back, or repair.

Do not make a Universal Link open a visually impressive but contextless landing
screen. The route should answer: what is this, why did it open, what can I do now,
and what happens if the source is stale?

## Native hierarchy

Use the system’s browser, notification, App Clip, Handoff, widget, App Intent,
document, or share surface for the entry event. Once inside the app, use normal
SwiftUI navigation, sheets, confirmation dialogs, forms, and system controls.

A good hierarchy is:

    system source
      -> short app-owned arrival state
      -> current record and context
      -> explicit action/review when needed
      -> normal destination
      -> durable domain effect

Liquid Glass belongs to a functional app-owned control layer. It can group a small
set of actions such as Open, Sign In, Review, Refresh, Retry, or Continue. It
should not become a full-screen translucent wrapper around the destination, obscure
the record, imitate Safari, or cover an Apple-owned system sheet.

## Arrival-state matrix

| Arrival state | Primary surface | Copy pattern | Avoid |
| --- | --- | --- | --- |
| Valid public record | Detail destination | “Opened from example.com” only when useful | A noisy interstitial on every link |
| Private record, signed out | Auth gate with context | “Sign in to continue to this item” | Revealing title/body before auth |
| Private record, wrong account | Account/recovery sheet | “This item belongs to another account” | Silent account switching |
| Stale record | Recovery card | “This link is out of date” plus refresh/search | Pretending a deleted item still exists |
| Unknown route | Safe fallback | “This link isn’t supported” plus browser/back | Sending the user to an arbitrary home tab |
| Pending network | Progress/status | “Checking this link…” and cancel/retry | Infinite spinner or glass fog over content |
| Server unavailable | Offline card | “Can’t verify right now” with local fallback | Treating cached data as current |
| Requires consent | Review sheet | Name the data/action and the next choice | Hiding consent behind a deep link |
| AI route suggestion | Reviewable suggestion | “Suggested destination” with source and edit | “The link says…” as if model output were authority |
| Duplicate arrival | Existing destination | Preserve current screen and merge state | Pushing the same detail twice |

If the route opens content that is already visible, update the existing scene or
show a subtle status rather than stacking identical screens.

## Scene and window selection

For a single-window iPhone app, a root route coordinator can usually receive the
event and update NavigationPath or sheet state. For iPad and multi-window apps,
the destination policy must be explicit:

- route document-specific links to the scene that owns that document;
- open a new scene only when the product wants independent workspaces;
- keep URL/activity matching strings narrow;
- do not let a wildcard route every event to a detail window;
- preserve each scene’s local selection separately;
- revalidate the canonical record after selecting a scene;
- show which window received the event when multiple windows are visible.

The person should never be surprised by a new window that contains a blank
destination because the incoming record was stale.

## Liquid Glass roles

A restrained design system can use these app-owned glass roles:

| Role | Glass use | Content beneath |
| --- | --- | --- |
| Arrival action group | Continue, Sign In, View in Browser, Cancel | Destination summary |
| Trust/status capsule | Verified domain, pending verification, offline | Route source and state |
| Review sheet actions | Open, Edit, Refresh, Use cached copy | Actual record preview |
| Recovery controls | Retry, Search, Copy link, Report problem | Honest error explanation |
| Navigation chrome | Back, close, tab/menu controls | The app’s current destination |

Do not use a glass card for every metadata row. Use standard SwiftUI controls for
semantic actions and keep the material grouping around related controls. Let
standard navigation bars, toolbars, sheets, and system-provided views adopt the
platform treatment.

The route source should never be communicated by translucency alone. Use a label,
icon, semantic text, and accessible value. For dynamic backgrounds, verify contrast
and hit targets at rest, during scroll, and during route transitions.

## Trust design

Trust is not the same as visual polish. Show enough information for the person to
understand a route without exposing private data:

- a verified or expected domain label when relevant;
- the app’s own destination title;
- the account or workspace that will be used;
- whether content is cached, current, or awaiting verification;
- an explicit external-browser action when the app cannot verify the route;
- a reason when a sign-in or permission step is required;
- a recovery route for unsupported or expired links.

Never show a green check solely because a URL parsed. Association, authorization,
freshness, and action policy are separate facts. If the route came from a custom
scheme, label it as an app handoff only when the source is known; otherwise use
neutral copy.

## Handoff continuity

Handoff should restore an activity, not replay an irreversible action. A receiving
device can show:

- the document or record the person was viewing;
- an editor at a restorable cursor/selection;
- a map region or selected place;
- a media item and playback position when the product supports it;
- a pending review state;
- a local draft reference that the receiving device can fetch.

Do not embed a private document, token, payment credential, or full media asset in
a public activity. The receiving app should show a short loading state, fetch the
current authorized record, and explain when the activity is no longer available.

For cross-device continuation, a compact activity banner or native restoration
surface is usually enough. Avoid a large custom “handoff modal” that repeats the
system’s own affordance.

## URL-to-navigation choreography

Use a stable choreography:

    received
      -> parsed
      -> validating
      -> needs-auth | stale | ready | rejected
      -> review (only if action/consequence needs it)
      -> navigated
      -> committed (only after domain confirmation)

Recommended transitions:

- received to parsed: immediate, no network;
- parsed to validating: bounded task with cancellation;
- validating to ready: update route state and focus the destination;
- validating to stale: preserve the route and offer refresh/search;
- ready to review: present a sheet if the action affects data or identity;
- review to committed: run the same command path as an in-app button;
- any state to rejected: keep a recoverable explanation and back route.

A route can be delivered twice during a cold/warm race. Use an event ID or
normalized route key and a short-lived dedupe policy. Do not suppress a genuinely
new source revision just because the record ID is the same.

## Accessibility and alternate input

A deep link is complete only when the destination is operable after arrival:

- move VoiceOver focus to the destination title, status, or first useful control;
- announce that content was opened from an external source only when it helps;
- announce authentication, stale, offline, and completion state changes;
- provide a visible and accessible back/cancel action;
- ensure every arrival action has a label, value, and trait;
- support Dynamic Type, long domain names, long localized titles, and RTL;
- keep a non-gesture route to open, retry, search, and dismiss;
- preserve keyboard, pointer, Switch Control, and Voice Control access;
- honor Reduce Motion and Reduce Transparency;
- do not make a shimmering glass effect the only progress indicator;
- avoid reading raw query parameters or tokens through VoiceOver.

When a system sheet or authentication controller appears, return focus to the
context that requested it and state the result. Do not leave a blank host view
behind a dismissed system surface.

## AI-assisted routing

On-device AI can improve arrival comprehension without becoming the router:

- summarize a long user-provided URL’s visible destination;
- propose the likely record when the person supplies ambiguous text;
- explain why a link is stale;
- suggest a safe alternate search;
- generate a localized, reviewable description of a destination;
- classify a notification or widget request into a finite route enum.

Keep the model input limited to user-authorized visible context. The deterministic
resolver owns the host/path/action allowlist and current record. The model’s output
must carry:

- source event identifier;
- visible input scope;
- candidate route ID;
- source revision;
- model/framework route;
- generated-at;
- confidence or ambiguity state;
- review state.

Use a small review surface for proposals. A “Use suggestion” action invokes the
same validated command path as a manually selected destination. Never allow a
model to choose an arbitrary URL, bypass authentication, reveal hidden records, or
call openURL directly.

## Web fallback and browser continuity

A good Universal Links design preserves the website path when the app is not
installed. The web fallback should:

- render a useful equivalent destination;
- avoid requiring an app install for basic content;
- keep path/query semantics compatible with the app’s parser;
- provide a clear native-app path only when the app can handle the route;
- handle app-to-web and web-to-app loops;
- preserve privacy when URL values are copied or logged.

Inside Safari, the system may keep same-domain links in Safari to respect the
person’s context. Do not design a product assumption that every tap always opens
the app. Test Safari, Messages, Mail, Notes, third-party browsers where supported,
and in-app WebKit paths separately.

## Design review checklist

- The entry source is named.
- The destination is recognizable before a consequential action.
- The route uses normal SwiftUI navigation/sheet/control semantics.
- Glass groups only functional controls.
- System-owned views remain system-owned.
- Authentication is explicit and does not leak private metadata.
- Stale/offline/unknown routes have a useful recovery.
- Cold/warm/multi-window behavior is visually coherent.
- AI copy is marked as a suggestion and has a deterministic fallback.
- VoiceOver focus and Dynamic Type are tested on the arrival surface.
- The route can be completed without a swipe, color cue, or animation.
- A browser fallback exists for uninstalled apps.
- The final product does not claim verified association until the target and
  website are tested.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Navigation and search](https://developer.apple.com/design/human-interface-guidelines/navigation-and-search)
- [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)
- [Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)
- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content/)
- [Supporting universal links in your app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [Restoring your app’s state with SwiftUI](https://developer.apple.com/documentation/swiftui/restoring-your-app-s-state-with-swiftui)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)

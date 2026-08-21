# SwiftUI App Clips, invocation, and full-app handoff review design

This guide turns the [App Clip review](../42-framework-deep-dives/106-swiftui-app-clips-invocation-handoff-review.md) into native SwiftUI design decisions. It is paired with the [invocation route](../50-capability-recipes/137-swiftui-app-clips-invocation-handoff-review-route.md), [proof matrix](../60-verification/131-swiftui-app-clips-invocation-handoff-review-proof-matrix.md), and [compile-oriented recipes](../70-code-recipes/149-swiftui-app-clips-invocation-handoff-review-recipes.md).

An App Clip should feel like a fast, trustworthy answer to a specific situation. It is not a mini App Store, a marketing interstitial, a web wrapper, or a visually reduced copy of a full app.

## Design authority map

| Surface | Owner | Design implication |
| --- | --- | --- |
| App Clip card | App Store Connect and iOS | Use concise context-specific copy and imagery |
| Invocation URL | System plus App Store Connect experience | Use it to select the task, not to trust arbitrary identity |
| App Clip opening screen | App Clip | Start at the task, not a home dashboard |
| Payment or sign-in | Apple system surface plus provider | Let the system own trust-sensitive controls |
| Location confirmation | iOS and person | Ask only when physical context is essential |
| Full-app overlay | StoreKit system surface | Recommend at a natural pause, never as a gate |
| Full-app handoff | Full app plus shared migration contract | Preserve context without assuming durable server truth |
| Liquid Glass | SwiftUI/system frameworks | Use standard controls and one functional emphasis |
| AI proposal | App-owned review UI | Make generated text provisional and editable |

## The App Clip screen flow

Design the shortest useful route:

~~~text
App Clip card
    -> context-aware opening
    -> one focused task
    -> system payment/sign-in/location if needed
    -> confirmation or receipt
    -> optional full-app recommendation
    -> return to task or finish
~~~

Avoid:

- a tab bar;
- a settings screen;
- a generic dashboard;
- a forced account before the task;
- a full-app download gate;
- a splash screen that delays useful content;
- a web view as the core interaction;
- an AI chat that asks the person to discover the task;
- a custom recreation of the App Clip card or system payment sheet.

Use a compact navigation path and keep the first screen tied to the invocation context. If a QR code identifies a location, show that location’s task immediately after validating it. If the URL is absent, restore the last safe task or show a neutral entry state.

## App Clip card design

The card is the person’s first trust decision. Design the App Store Connect metadata as a separate artifact:

- header image that communicates the task or place, not a tiny screenshot;
- short title and subtitle that can be read at a glance;
- a call-to-action verb that describes the task;
- localization and context-specific advanced experiences when the product has multiple locations;
- no claims that require an account or full app install before the Clip can deliver value.

Do not put important legal, price, or privacy detail only in the card image. The person must be able to understand the task from the card and the opening UI.

## Invocation context as a visual anchor

Show the context in one compact line:

~~~text
Order from North Loop Coffee
Menu for the location you scanned
~~~

Then show the essential content. Do not force the person to select the same location or item that the invocation already identified. If the context cannot be confirmed, say so:

~~~text
Choose a location
We could not confirm the place from this link.
~~~

An invocation URL is a route hint. It should not be styled as a verified receipt, identity, payment authorization, or exact physical location until the corresponding service or system result exists.

## Linear task hierarchy

Use a visible hierarchy:

1. Context: what this Clip is for.
2. Primary content: the item, menu, ticket, rental, or demo.
3. Primary action: one obvious next step.
4. System action: Apple Pay, Sign in with Apple, location, or other Apple surface.
5. Completion: what the app knows happened.
6. Optional next step: full app recommendation.

Keep secondary actions behind a small disclosure or a natural secondary button. A person should not need to learn the entire product vocabulary to complete the Clip.

## Liquid Glass in a lightweight experience

Use standard SwiftUI components first. Apple’s Liquid Glass guidance says standard navigation, controls, sheets, and bars adopt the system material automatically. That is especially valuable in an App Clip because custom effects cost visual complexity and can interfere with launch readability.

Good custom roles:

- a compact context capsule under the title;
- a single primary action group;
- a short completion status;
- an editable AI proposal review action.

Bad custom roles:

- every list row;
- the entire screen background;
- a fake App Clip card;
- a fake App Store overlay;
- a translucent surface over confidential payment or account details;
- overlapping glass controls that obscure the task.

Test:

- reduced transparency;
- reduced motion;
- increased contrast;
- large Dynamic Type;
- dark and light appearances;
- network-limited launch;
- the task with content scrolling behind the control.

If the effect is removed, the app should remain clear and usable.

## Native system surfaces

Use the system route when trust is part of the task:

| Need | Native surface |
| --- | --- |
| Fast payment for a physical service | Apple Pay |
| Account creation or sign-in | Sign in with Apple or a minimal documented flow |
| Full app recommendation | StoreKit App Clip overlay |
| Location confirmation | App Clip activation/location system route |
| Notifications | UserNotifications with documented ephemeral policy |
| Full-app continuation | Shared URL and state migration contract |

Do not draw a fake credit-card form to imitate Apple Pay. Do not put a custom “Install” glass button in front of a task when the system overlay is available. Do not ask for a location just to personalize a decorative header.

## Account and privacy design

Prefer no account when the task can finish without one. If account identity is essential:

- explain why before sign-in;
- minimize fields;
- use Sign in with Apple when appropriate;
- show the current task before a long account flow when possible;
- do not place raw credentials in App Group defaults or shared files;
- distinguish a local anonymous draft from a server account;
- show when an action is not yet synced or authenticated.

The App Clip can share data only with its corresponding full app. Design the migration as an invisible handoff of useful task context, not a global data-sharing feature.

## Payment design

For a physical service, Apple Pay can make the Clip feel instant:

~~~text
selected item and price
    -> concise total
    -> Apple Pay system button
    -> system authorization
    -> provider/order confirmation
~~~

Keep the app-owned total consistent with the system request. Show “Confirming order” until the provider or order service supplies the fact that the product promises. Do not present an Apple Pay authorization callback as fulfillment.

Do not put digital content or full-app entitlement behind a Clip checkout without following StoreKit and App Review rules. If the Clip’s value is a physical good or service, keep that route separate from full-app digital entitlements.

## Full-app recommendation

Recommend the full app after a task completion or natural pause:

~~~text
You’re all set.
Keep receipts and saved locations in the full app.

[Done]                          [Get the full app]
~~~

Use the documented StoreKit app overlay. The person should be able to finish first. Do not nag repeatedly or interrupt an active task. The overlay’s appearance or dismissal does not prove the install finished; show a full-app handoff only when the system or next launch provides evidence.

## Full-app replacement continuity

When the full app replaces the Clip, future invocations route to the full app. Preserve:

- the same invocation URL parser;
- the same context-to-task mapping;
- a migration envelope for the current task;
- an account/server reconciliation step;
- a user-visible continuation point.

Do not copy the entire Clip state graph into the full app. Import the smallest useful state:

~~~text
Clip task ID
    -> full app receives invocation
    -> full app reads migration envelope
    -> full app resolves current server state
    -> full app opens matching task screen
    -> envelope marked consumed
~~~

If the envelope is stale, show the current record and explain the change. If it is invalid, do not crash or silently create a duplicate.

## App Clip without an invocation URL

Design a recovery screen:

~~~text
Welcome back
We could not recover the original link.

Continue your saved task
or
Start a new task
~~~

Do not make a missing URL look like a server outage. The system can launch the Clip from a notification or App Switcher without an invocation URL. Persist a bounded local state before suspension and protect it from stale or sensitive disclosure.

## AI proposal design

If the App Clip uses on-device AI, place it after the context and before the user decision:

~~~text
Context from the scanned menu
    -> Smart suggestion
    -> source and revision shown
    -> edit or discard
    -> deterministic order/booking action
~~~

Use wording such as “Suggested for this menu” rather than “AI knows what you want.” Do not let the model choose a trusted location, recipient, price, payment method, or entitlement. If the model is unavailable, keep the same task with a normal picker or text editor.

Keep the model optional and short. A large model asset, long prompt, or chat transcript undermines the instant App Clip experience. Show a clear loading/fallback state rather than delaying the task indefinitely.

## Accessibility and alternate input

Test the complete task:

1. understand the App Clip card and opening context;
2. select the primary item;
3. complete payment or sign-in;
4. read confirmation;
5. dismiss or accept the full-app recommendation;
6. return with and without an invocation URL.

Check:

- VoiceOver order and context;
- Dynamic Type at large sizes;
- sufficient contrast with and without transparency;
- Reduce Motion for context changes and overlays;
- keyboard and pointer input;
- Switch Control and other alternate input;
- color-independent selected, loading, unavailable, and completed states;
- accessibility of system buttons and payment routes.

Do not make a tiny card, glass tint, or location photo the only source of meaning.

## Proof-oriented design review

Before calling the App Clip design complete:

- the first screen matches the invocation context;
- the task works without full-app installation;
- the card copy and image are configured and tested outside the SwiftUI preview;
- the route handles malformed and missing URLs;
- system surfaces are real native surfaces;
- custom glass is sparse and functional;
- account and payment privacy are visible;
- the full app continues the same task after replacement;
- AI output is reviewable and optional;
- the task works with VoiceOver, Dynamic Type, reduced effects, and alternate input;
- the release artifact fits the current size and target constraints.

## Sources

- [App Clips HIG](https://developer.apple.com/design/human-interface-guidelines/app-clips)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [Choosing the right functionality for your App Clip](https://developer.apple.com/documentation/appclip/choosing-the-right-functionality-for-your-app-clip)
- [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip)
- [Responding to invocations](https://developer.apple.com/documentation/AppClip/responding-to-invocations)
- [Sharing data between your App Clip and your full app](https://developer.apple.com/documentation/appclip/sharing-data-between-your-app-clip-and-your-full-app)
- [Recommending your app to App Clip users](https://developer.apple.com/documentation/appclip/recommending-your-app-to-app-clip-users)
- [Testing the launch experience of your App Clip](https://developer.apple.com/documentation/AppClip/testing-the-launch-experience-of-your-app-clip)
- [StoreKit SKOverlay](https://developer.apple.com/documentation/storekit/skoverlay)
- [SwiftUI appStoreOverlay](https://developer.apple.com/documentation/swiftui/view/appstoreoverlay%28ispresented%3Aconfiguration%3A%29)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)

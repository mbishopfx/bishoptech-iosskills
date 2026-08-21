# Spotlight search, activity, and discoverability design

Core Spotlight and NSUserActivity turn app-owned content and recent user actions into native discovery paths. The design goal is not to imitate Spotlight; it is to make the result understandable, current, private, and easy to continue.

## Design the discoverability contract

Before indexing, decide:

- what the person would reasonably search for later;
- whether the content is app-owned, user-touched activity, or a temporary suggestion;
- which fields may appear in system search;
- how the result resolves to current native state;
- what happens after deletion, logout, expiration, or permission loss;
- whether Handoff or universal-link continuation is supported;
- whether Foundation Models may retrieve the indexed attributes.

Indexing should follow product value, not database completeness. An empty result is better than a stale or privacy-surprising result.

## Result anatomy

A result should have:

- a concise localized title;
- display name or source context;
- content type;
- freshness or modification date where useful;
- a recognizable thumbnail only when privacy permits;
- an action that opens the exact native destination;
- a recoverable state when the source is missing or locked.

Keep unique IDs and account identifiers out of visible copy. A result card is a projection, not proof that the underlying record is still authorized.

## Content versus activity

| Design need | Index |
| --- | --- |
| A note, purchase, media item, document, or message | CSSearchableItem |
| A page or record the person just viewed | NSUserActivity with eligibleForSearch |
| A task that should continue on another device | NSUserActivity with Handoff and stable IDs |
| A public webpage route | Universal link and website association |
| A private account record | Protected/named index or no indexing |
| Temporary suggestion | Expiration date and explicit removal |

Do not index a user activity for every screen transition. The activity should represent something the person touched and may want to find or continue.

## Search interface design

An in-app search route should:

1. keep the query field focused intentionally;
2. debounce text changes;
3. cancel old CSSearchQuery or CSUserQuery work;
4. show loading, empty, blocked, and error states;
5. show scope/filter context;
6. preserve result identity while batches arrive;
7. return focus after opening or dismissing a result;
8. record engagement only when the person chooses a result.

Avoid showing a result list that changes under VoiceOver without announcing the relevant update. Keep the last valid query visible when a new query fails.

## Account and privacy design

Make indexed-data policy legible:

- include only content the person expects to find;
- use domain identifiers so account/workspace deletion can clear groups;
- expire temporary items;
- remove deleted source records promptly;
- provide a settings or privacy explanation for sensitive search;
- revalidate current authorization before opening a result;
- do not reveal locked content through titles, thumbnails, keywords, or summaries.

If an account switches, show a clear transition and do not let the previous account’s search results remain actionable.

## Protected search

Use a separate protected index or protection class when the selected target supports it and the data warrants it. The UI should distinguish:

- indexed and available;
- indexed but protected;
- source missing;
- authorization required;
- expired or deleted.

Never describe a local index as a vault or promise that it eliminates all privacy risk. The device, system search, app process, and account policy remain part of the threat model.

## Handoff and continuation

Continuation should feel like the same task:

activity -> stable content identity -> receiving device/app -> authorization check -> exact destination

Use a concise activity title, stable persistent/target identifiers, and a fallback when content moved or no longer exists. A broken continuation should explain what happened and offer search or browser fallback instead of landing on a generic home screen.

For universal links, show the destination and intended action when the route is consequential. Validate URL parameters before the app reads or writes anything.

## Liquid Glass search surfaces

Use Liquid Glass for app-owned search controls:

- scope and filter groups;
- recent-query actions;
- selected-result actions;
- an AI answer review shell with visible sources.

Keep source title, account, freshness, and authorization status on a stable readable surface. Do not create a fake Spotlight panel or imply that the app controls system ranking. Avoid nested translucent result cells that make items difficult to compare.

Provide solid fallbacks for reduced transparency, increased contrast, Dynamic Type, VoiceOver, and compact layouts.

## Foundation Models and indexed content

When a Foundation Models session uses SpotlightSearchTool, design the model result as retrieval plus generation:

1. show the user what app content is in scope;
2. retrieve only the attributes needed for the question;
3. label the answer as generated;
4. show source items or a source count;
5. allow the person to open the source;
6. let the person correct, dismiss, or apply a proposal;
7. revalidate the source before committing an action.

The model should not see a private field merely because it is present on a CSSearchableItemAttributeSet. The source configuration is part of the product’s privacy design. Preliminary SpotlightSearchTool APIs need an availability and fallback surface.

## Accessibility

Test:

- VoiceOver reads result title, type, freshness, account, and action;
- Dynamic Type preserves the search field, empty state, filters, and source actions;
- Voice Control and Switch Control reach search, cancel, result open, delete, and review actions;
- new result batches do not steal focus unexpectedly;
- keyboard submit and escape/cancel work;
- long titles, localization, and right-to-left layouts remain clear;
- protected/deleted/unauthorized states are announced without exposing private content;
- AI source attribution is understandable without relying on color or glass.

## Design proof

Complete these tasks on a physical target:

- create, update, delete, and search an app record;
- sign out and confirm account-domain removal;
- search a protected item while locked or unauthorized;
- use a recent NSUserActivity and open it;
- continue a stable activity across devices if claimed;
- activate a universal link with valid and malformed parameters;
- type rapidly and confirm stale query results do not win;
- ask an on-device model about approved indexed content;
- inspect source attribution, rejection, and fallback;
- repeat with VoiceOver, Dynamic Type, reduced transparency, and empty/error states.

## Sources

- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableItem](https://developer.apple.com/documentation/corespotlight/cssearchableitem)
- [CSSearchableItemAttributeSet](https://developer.apple.com/documentation/corespotlight/cssearchableitemattributeset)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [CSSearchQuery](https://developer.apple.com/documentation/corespotlight/cssearchquery)
- [CSUserQuery](https://developer.apple.com/documentation/corespotlight/csuserquery)
- [Adding your app’s content to Spotlight indexes](https://developer.apple.com/documentation/corespotlight/adding-your-app-s-content-to-spotlight-indexes)
- [Building a search interface for your app](https://developer.apple.com/documentation/corespotlight/building-a-search-interface-for-your-app)
- [Searching for information in your app](https://developer.apple.com/documentation/corespotlight/searching-for-information-in-your-app)
- [Spotlight search tool](https://developer.apple.com/documentation/corespotlight/spotlight-search-tool)
- [SpotlightSearchTool](https://developer.apple.com/documentation/corespotlight/spotlightsearchtool)
- [CoreSpotlightSource](https://developer.apple.com/documentation/corespotlight/corespotlightsource)
- [Making your indexed content available to Foundation Models](https://developer.apple.com/documentation/corespotlight/making-your-indexed-content-available-to-foundation-models)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [eligibleForSearch](https://developer.apple.com/documentation/foundation/nsuseractivity/iseligibleforsearch)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)

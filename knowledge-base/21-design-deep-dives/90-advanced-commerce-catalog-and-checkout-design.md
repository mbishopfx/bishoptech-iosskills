# Advanced Commerce catalog, native checkout, and Liquid Glass design

Advanced Commerce design is a large-catalog problem with a system-owned trust boundary. The app can make discovery feel personal and beautiful, but the final transaction must remain legible, current, and recognizably Apple-native.

## Design objective

Use this composition loop:

~~~text
catalog intent -> trusted item identity -> exact current terms
  -> explicit user review -> native StoreKit confirmation
  -> verified transaction -> delivery/status explanation
~~~

The app owns discovery, search, filters, recommendations, content explanation, and account context. Apple owns the App Store payment confirmation and the signed transaction evidence. The server owns the catalog authority, request signing, account reconciliation, and durable entitlement projection.

Do not reproduce Apple’s payment sheet with a custom Liquid Glass overlay. Use the system surface for the final confirmation and let the app-owned UI explain what the person is about to buy before the system sheet appears.

## Four-layer screen model

| Layer | App responsibility | Required truth |
| --- | --- | --- |
| Discovery | Search, browse, filters, creator/content context, recommendations | The item exists in the current app catalog and has a stable app-owned SKU. |
| Review | Detail, benefits, display name, description, price, tax/period context, account | Values are current for the selected storefront and catalog revision. |
| Checkout | Explicit action handing off to StoreKit | The signed request was created for this SKU and operation; no arbitrary price is accepted from the client. |
| Result/account | Delivery, entitlement, subscription state, manage/refund/support | State comes from verified transaction/server policy, not from the button animation. |

This model works for a creator subscription, a course chapter, a one-time audio pack, or a subscription with optional add-ons. The visual vocabulary can change; the truth boundaries should not.

## Large catalog information architecture

For a large catalog, make the user’s current scope visible:

- search query and active filters;
- creator, collection, category, or content source;
- catalog revision or last-updated hint where freshness matters;
- loading, stale, empty, unavailable, and server-error states;
- one stable card identity per SKU;
- exact item display name and description from the server catalog;
- the current localized amount/term and a clear purchase consequence;
- whether the item is already owned, active, pending, expired, unavailable, or requires account action.

A card should answer “what is this?”, “why might I want it?”, “what exactly will happen if I buy it?”, and “what can I do if something goes wrong?” without requiring a model-generated paragraph to fill gaps.

### A practical card hierarchy

~~~text
creator/content identity
title and concise description
optional preview or media
benefit / included-content summary
current state badge: available | owned | active | pending | unavailable
localized price and period
primary action
secondary details, restore/manage/support where relevant
~~~

Keep price and period adjacent to the action. Do not place them in a low-contrast glass caption or communicate “owned” only through a color shift. If a price is generated from an app-owned Advanced Commerce request, display it from the same validated catalog entry that the server signs and make a storefront change a visible revalidation event.

## Generic product IDs are not cards

Advanced Commerce uses generic product identifiers in App Store Connect, while the app’s own catalog contains individual SKUs. The design system must prevent that abstraction from leaking into copy:

| Internal value | User-facing role |
| --- | --- |
| Generic product ID | Hidden StoreKit configuration identity. |
| App-owned SKU | Stable content/offer identity used by the catalog and support tools. |
| Display name/description | Localized Apple payment-sheet metadata plus app detail copy. |
| Price/currency/tax code | Current request/catalog fields; never invented in the UI. |
| Request reference ID | Support/idempotency correlation, not a product title. |
| Apple transaction ID | Receipt/support identity, not a visual label by default. |

If the app has a “buy this lesson” action, the action’s semantic value should be the lesson SKU and catalog revision. The route then maps it to the correct generic AdvancedCommerceProduct, request payload, and server authorization. Never let an AI response or a stale list cell supply an unrestricted generic ID or price.

## Liquid Glass placement

Liquid Glass is most useful for app-owned controls that float over content or need to adapt to context: navigation, search, filters, compact account status, floating actions, and transient selection controls. It is not a reason to wrap every card in a translucent capsule.

Recommended layering:

~~~text
content/media backdrop
  -> readable app-owned card or section background
  -> restrained glass toolbar/filter/action cluster
  -> native system checkout sheet outside the app-owned glass hierarchy
~~~

Use the system’s materials and controls first. Let the content and hierarchy do most of the work. On iOS 26, inspect the selected SDK’s Liquid Glass APIs and follow Apple’s current guidance rather than copying an early beta screenshot. Keep custom material, tint, blur, morphing, and animation secondary to the task.

Avoid:

- placing a translucent panel behind localized price/legal text until the text becomes hard to read;
- using a glow or glass morph as the only selected/owned/pending signal;
- putting multiple competing glass cards around one primary purchase action;
- imitating the system confirmation sheet or Apple Account subscription screen;
- animating a “success” state before verification and delivery are complete;
- treating dynamic material as proof that the user owns content.

When transparency is reduced, preserve a solid hierarchy and the same action order. When increased contrast is enabled, preserve border/shape/label cues without requiring a specific tint.

## Native checkout handoff

The purchase handoff should feel deliberate:

1. The person taps a semantic purchase action for a visible SKU.
2. The app shows a short preparing state while the server validates the operation and returns signed request data.
3. The app hands the request to AdvancedCommerceProduct.purchase(compactJWS:options:).
4. StoreKit presents the Apple-owned confirmation surface.
5. The app handles pending, cancelled, verified, unverified, and thrown-error outcomes.
6. The result screen explains delivery/entitlement state and provides recovery.

The preparing state is not a fake progress bar. It should say what is happening in plain language, disable duplicate taps, and expose retry/support when the server is unavailable. Do not show a green “purchased” animation until the transaction has been verified and the product delivery policy has completed.

For subscription purchases, keep the current plan, renewal period, renewal state, and manage route discoverable. Advanced Commerce’s setup guidance requires a way for customers to manage subscriptions in the app and a way to request a refund. Use Apple’s documented system routes where appropriate; do not create a visually identical local cancellation flow that changes only a local flag.

## State language

| Technical state | User-facing copy direction |
| --- | --- |
| Catalog loading | “Loading the latest selection…” |
| Catalog stale | “Showing the last available selection. Refresh to check current availability.” |
| Signed request preparing | “Preparing a secure purchase…” |
| StoreKit pending | “Waiting for App Store approval. Your access will update when Apple confirms it.” |
| User cancelled | “Purchase cancelled. Nothing was added.” |
| Unverified | “We couldn’t verify this purchase yet. Your access hasn’t changed.” |
| Verified, delivery pending | “Purchase verified. Finishing delivery…” |
| Entitled | “Included with your account.” or “Active until [localized date].” |
| Expired/revoked/refunded | “This access is no longer active. Review your subscription or support options.” |
| Notification/server stale | “Your Apple purchase is known, but account access is still refreshing.” |
| Unsupported local test | “This commerce path requires Apple sandbox or an approved environment; local StoreKit testing isn’t evidence for it.” |

Avoid shame, urgency, or medical/financial outcome claims. A recommendation is not an entitlement and a pending transaction is not a failed person.

## Subscription with optional add-ons

Represent the base subscription and add-ons as one understandable purchase composition. The person should see:

- the service they are subscribing to;
- each optional add-on and what it changes;
- the combined recurring price and billing period;
- which pieces can be removed or changed;
- the renewal/manage route;
- what happens if an add-on becomes unavailable;
- the account/content effect after a verified transaction.

Avoid a “mystery bundle” card that shows only a low base price while the signed request includes multiple add-ons. The visual summary and the request payload must be generated from one validated PurchaseDraft so they cannot drift.

## Accessibility and internationalization

Design the whole route for:

- VoiceOver order that states item identity, included content, price, period, current state, and action;
- Voice Control and Switch Control targeting each plan/action by a stable name;
- Dynamic Type without clipped prices or hidden terms;
- increased contrast and reduced transparency without losing ownership or pending boundaries;
- reduced motion without relying on morphing to announce success;
- right-to-left layouts;
- long localized names, descriptions, currencies, and tax/period strings;
- keyboard, pointer, and focus movement on supported platforms;
- localization of server catalog content and App Store payment-sheet metadata independently but consistently.

Use semantic Button, NavigationLink, Toggle, Picker, List, and ScrollView structures where possible. If the catalog uses custom gestures or cards, provide equivalent semantic actions and focus behavior. Put “Recommended” and “Already included” in accessibility-visible labels, not only in a tint or material treatment.

## AI-assisted catalog discovery

AI can help browse, but the purchase contract stays deterministic:

~~~text
user goal
  -> on-device model proposes known SKU IDs and an explanation
  -> current catalog validator checks IDs, revision, storefront, status, price, and terms
  -> UI shows exact facts and marks the explanation as generated
  -> user selects a visible item and confirms
  -> server signs only the selected validated operation
~~~

The model may summarize a description that the server provided, compare known products, ask a follow-up, or refine a search query. It must not:

- fabricate a SKU, price, discount, tax code, or renewal date;
- claim an item is owned without verified entitlement data;
- hide the manage/refund path;
- trigger purchase, restore, subscription management, or refund as a tool call without explicit intent;
- turn “help me focus” or similar language into a guaranteed or medical outcome claim;
- use a prompt to override account, storefront, eligibility, or server authorization.

Render generated explanations with a freshness/source cue such as “Based on the current catalog” and provide a deterministic details view. If the model is unavailable, retain search, filter, manual comparison, and purchase flows.

## Review checklist

- [ ] The screen makes the app-owned SKU, title, included content, and current state unambiguous.
- [ ] Price and billing period are adjacent to the action and tied to current validated data.
- [ ] Generic product IDs do not leak into user-facing copy.
- [ ] Preparing, pending, cancelled, unverified, verified, delivery, expired, and unavailable states are distinct.
- [ ] The final payment confirmation is Apple’s system surface, not a replica.
- [ ] Restore, manage, refund/support, and account-refresh routes are discoverable.
- [ ] Glass is used for app-owned hierarchy and controls, with a non-glass accessibility fallback.
- [ ] Dynamic Type, VoiceOver, reduced transparency/motion, contrast, RTL, and long localization cases are tested.
- [ ] AI proposals are grounded in current catalog facts and require visible user review.
- [ ] A local StoreKit test is not described as Advanced Commerce provider proof.

## Related routes

- [Advanced Commerce API and App Store Server deep dive](../42-framework-deep-dives/69-advanced-commerce-api-and-app-store-server.md)
- [Advanced Commerce and server entitlement capability route](../50-capability-recipes/93-advanced-commerce-and-server-entitlement-route.md)
- [Advanced Commerce server proof matrix](../60-verification/87-advanced-commerce-server-proof-matrix.md)
- [Advanced Commerce and App Store Server recipes](../70-code-recipes/105-advanced-commerce-and-server-recipes.md)

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Human Interface Guidelines: In-app purchase](https://developer.apple.com/design/human-interface-guidelines/in-app-purchase)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi)
- [Advanced Commerce API access and eligibility](https://developer.apple.com/in-app-purchase/advanced-commerce-api/)
- [Setting up your project for Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-your-project-for-advanced-commerce)
- [Setting up generic product identifiers](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-generic-product-identifiers)
- [Creating SKUs for your In-App Purchases](https://developer.apple.com/documentation/advancedcommerceapi/creating-your-purchases)
- [AdvancedCommerceProduct](https://developer.apple.com/documentation/storekit/advancedcommerceproduct)
- [AdvancedCommerceProduct.purchase(compactJWS:options:)](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchase%28compactjws%3Aoptions%3A%29)
- [Sending Advanced Commerce API requests from your app](https://developer.apple.com/documentation/storekit/sending-advanced-commerce-api-requests-from-your-app)
- [Generating JWS to sign App Store requests](https://developer.apple.com/documentation/storekit/generating-jws-to-sign-app-store-requests)
- [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi)
- [Get All Subscription Statuses](https://developer.apple.com/documentation/appstoreserverapi/get-all-subscription-statuses)
- [App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications)
- [Enabling App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/enabling-app-store-server-notifications)
- [Receiving App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/receiving-app-store-server-notifications)
- [Supporting offer codes in your app](https://developer.apple.com/documentation/storekit/supporting-offer-codes-in-your-app)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

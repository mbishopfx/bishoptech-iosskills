# Suggested Actions Messaging Route

Use this route only when the product is a messaging app that displays a stream of messages and wants Apple’s inline system suggestions for Calendar, Reminders, or Maps. Keep the message record, Suggested Actions context, system handoff, and app-owned receipts separate.

## Outcome contract

The person can:

1. read a message normally;
2. see a relevant inline system suggestion when one is available;
3. understand which message supplies the context;
4. choose or ignore the suggestion;
5. complete the system handoff;
6. return to the conversation without false completion copy;
7. continue using the app when the entitlement, device, model, or system action is unavailable.

## Route selector

| Need | Route |
| --- | --- |
| System Calendar/Reminders/Maps suggestions next to messages | Suggested Actions |
| Custom entity extraction | Foundation Models, Natural Language, or Vision as appropriate |
| App-owned message action | App Intents or a direct product command |
| Draft a reply | Product-owned reviewable AI feature |
| Search/index conversations | Core Spotlight/App Intents with a separate privacy plan |
| Show a custom action row | SwiftUI controls, with product-owned semantics |

Do not use Suggested Actions as an arbitrary model API or for a non-messaging app.

## Target and entitlement gate

Record:

- messaging app target and bundle ID;
- iOS/iPadOS deployment target and final SDK;
- Suggested Actions capability and signed Boolean entitlement;
- beta/release status in the selected SDK;
- message model ID/version policy;
- previous-message context policy;
- cache invalidation policy;
- system handoff and app-receipt design;
- privacy/retention/logging policy;
- fallback for a build without the capability.

The entitlement key is com.apple.developer.suggested-actions. A capability entry in Xcode is not enough; inspect the signed app and test the system surface.

## Ownership graph

~~~text
message store
  -> MessageViewModel
      -> SuggestedActionsMessage projection
      -> optional SuggestedActionsView.generate cache
      -> SuggestedActionsView inline rendering
      -> system action handoff
  -> app-owned message/action receipt
~~~

| Layer | Owns | Does not own |
| --- | --- | --- |
| Message store | Message content, ID, edit/delete lifecycle | Suggested action semantics |
| Context projection | Bounded current/previous message representation | Full conversation export |
| Suggested Actions | On-device analysis and system-provided action presentation | Message delivery or app analytics |
| SwiftUI row | Layout, accessibility, scrolling, fallback | Calendar/Reminder/Maps completion |
| System destination | Calendar, Reminders, or Maps handoff | App’s message state |
| Receipt coordinator | App-observed selection/return state | Inferred system side effects |

## Message projection

Build a projection for the currently rendered message:

~~~text
SuggestedActionsMessage:
  stable message ID
  current message content representation
  previous messages within documented limit
  message version
  privacy eligibility
~~~

Do not pass more context than needed. Do not reuse a message ID after edit unless the representation/version contract makes the cache invalid.

## Rendering route

1. Verify the target has the entitlement/build state.
2. Render the normal message bubble.
3. Create the current SuggestedActionsMessage.
4. Supply bounded previous-message context.
5. Place SuggestedActionsView below the message.
6. Let the view occupy zero space when no action is available.
7. Optionally pre-generate when the message is about to appear.
8. Reconcile edits/deletions and cancel stale tasks.
9. Preserve scroll and accessibility focus when the view changes size.

Do not branch on a custom keyword classifier to decide whether the view exists; the documented view is designed to be placed for each message.

## Pre-generation route

Use generate(message:previousMessages:) when:

- the message is visible or about to become visible;
- the message ID/version is stable;
- the app can cancel when the row leaves scope;
- cache invalidation is implemented.

Do not pre-generate an entire private archive by default. The feature’s privacy promise concerns processing; it does not make unnecessary context collection a good product choice.

## Action completion boundary

When a person taps a suggestion:

1. allow the system action to perform its handoff;
2. show a neutral in-progress/return state if the app has one;
3. record only an app-owned receipt that is actually observable;
4. do not mark a Calendar event or Reminder as saved without supported confirmation;
5. keep the original message unchanged;
6. allow the person to retry or ignore.

If the system opens Maps, call it “opened in Maps,” not “navigation started.” If the action is unavailable or cancelled, return to the normal conversation.

## SwiftUI and native design

SuggestedActionsView should remain visually inline. Use Liquid Glass for app-owned surrounding controls only:

- compose;
- conversation filters;
- selected-message actions;
- an optional review sheet.

Do not add a glass container around every suggestion or label the system action “AI generated” in a way that misrepresents ownership.

## AI relationship

Treat Suggested Actions as a system-provided model route:

~~~text
system suggestion -> person choice -> system handoff
~~~

Treat a custom Foundation Models feature as:

~~~text
app input -> model proposal -> user review -> typed app command
~~~

These flows should have different provenance, controls, and proof. Do not pass Suggested Actions output into a hidden app model or assume it exposes a structured event/reminder/location entity to the app.

## Error and fallback states

| State | Fallback |
| --- | --- |
| Entitlement absent | Hide the view and keep message row functional |
| Beta/API unavailable | Compile a version-gated fallback |
| No suggestion | Zero-size view; no gap |
| Suggestion generation cancelled | Keep normal message |
| Message edited | Invalidate and regenerate with new version |
| Message deleted | Remove view/cache/context |
| System action unavailable | Keep message; offer ordinary app action only if independently implemented |
| System handoff cancelled | Return to conversation without completion claim |
| Privacy policy excludes content | Do not create a SuggestedActionsMessage for that row |

## Minimum proof sequence

1. Compile with the final SDK and entitlement.
2. Render a non-actionable message and verify zero-size behavior.
3. Render known Calendar, Reminder, and location fixtures.
4. Test pre-generation/cache with matching ID.
5. Edit message content and verify invalidation.
6. Delete message while generation is active.
7. Test system handoff and cancellation.
8. Test VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, and iPad input.
9. Audit raw message content, logs, analytics, and external AI boundaries.
10. Recheck beta/release eligibility in the final archive.

## Sources

- [Suggested Actions](https://developer.apple.com/documentation/SuggestedActions)
- [SuggestedActionsView](https://developer.apple.com/documentation/suggestedactions/suggestedactionsview)
- [Suggested Actions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.suggested-actions)
- [iOS and iPadOS release notes](https://developer.apple.com/documentation/ios-ipados-release-notes)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

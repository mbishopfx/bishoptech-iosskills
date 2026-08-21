# Suggested Actions Message Design

Suggested Actions should feel like a quiet native affordance inside a conversation, not like a second chatbot. The design job is to preserve the message hierarchy while making a relevant Calendar, Reminders, or Maps handoff easy to notice and easy to ignore.

The visual loop is:

~~~text
message -> optional inline system suggestion -> person chooses
-> system handoff -> app reconciles only what it can observe
~~~

## Conversation hierarchy

The message remains primary. Use this order:

1. sender and message content;
2. timestamp/read state;
3. SuggestedActionsView when the target can use it;
4. app-owned message actions.

Do not place the suggested action above the message or make it look like a model-generated reply. The person should understand what text caused the suggestion.

## Native inline row

SuggestedActionsView is designed to be placed below a message. When there are no suggested actions, it has zero size. That means the app can put it in every message row without adding an empty placeholder.

Recommended row behavior:

- reserve no manual “AI card” space;
- let the system view appear or collapse naturally;
- keep message padding stable;
- avoid reflowing the entire transcript when one suggestion arrives;
- use a subtle insertion animation only when motion is allowed;
- preserve scroll position when a row changes height;
- do not auto-scroll a person away from the message they are reading.

If the view is loading, the conversation should remain usable. Avoid a spinner in every row. A pre-generated cache can make the eventual appearance calmer, but the message remains complete without it.

## Suggested action copy

Use the system-provided action presentation as the source of truth. Avoid adding duplicate labels such as:

> AI found a calendar event. Tap to create.

Prefer a native inline affordance next to the source message. If the app adds explanatory text, keep it optional and factual:

> Suggested by the message above.

Never say:

- “The system understood your intent perfectly.”
- “This will definitely create the event.”
- “Your reminder is saved” before the system handoff/result is verified.

## Message states

| State | Visual treatment | Accessibility value |
| --- | --- | --- |
| noSuggestion | No extra row | No extra announcement |
| preparing | Normal message; no large placeholder | Do not announce background analysis repeatedly |
| suggestionAvailable | Inline native action row | Explain action and source message |
| selected | System handoff/pressed state | Announce that the action was selected |
| appReceiptUnknown | Return to conversation with neutral state | “System action selected; completion not confirmed here” |
| messageEdited | Invalidate/recompute | Updated message context |
| messageDeleted | Remove row and cached context | No stale suggestion remains |
| unavailable | Normal message row | No suggestion capability in this build |

The zero-size state is a successful layout state, not an error.

## Liquid Glass restraint

Use Liquid Glass for:

- compose and send controls;
- conversation-level filters;
- selected-message action bars;
- a review sheet that explains an app-owned AI feature.

Do not wrap every suggested action in a glass capsule. The system suggestion already carries a native visual language. Adding competing materials can make the conversation feel like a marketing surface.

If a selected-message review route opens:

- keep the source message visible;
- show the action scope;
- show the destination system;
- provide Cancel and Continue;
- avoid displaying raw hidden context;
- use an opaque fallback under Reduce Transparency.

## Calendar, Reminders, and Maps handoffs

Each destination deserves precise copy:

| Destination | Honest language |
| --- | --- |
| Calendar | “Add to Calendar” or the system-provided event action |
| Reminders | “Add to Reminders” or the system-provided task action |
| Maps | “Open in Maps” or the system-provided location action |

Do not call Maps “navigation” unless navigation actually starts. Do not call Calendar “scheduled” until the system confirms the event if the app has a confirmation path. Keep the conversation’s read state and the system action state separate.

## Privacy-first context

Only provide the current message and the bounded previous context needed for the framework. The UI should not expose that prior messages were passed through a larger hidden window than the product requires.

For a shared device or private conversation:

- do not show suggestions on a lock-screen-like surface without the normal message privacy policy;
- avoid logging suggested action type with message text;
- avoid screenshots in debug tooling that retain messages;
- remove or invalidate cached suggestions when a message is edited/deleted;
- keep a conversation deletion path that clears app-owned caches.

The framework’s on-device analysis does not remove the app’s responsibility for message transport, backups, analytics, moderation, or account deletion.

## Accessibility

SuggestedActionsView must fit:

- VoiceOver reading order after the message;
- Dynamic Type without truncating the source message;
- Voice Control with visible action names;
- Switch Control focus;
- Reduce Motion;
- Reduce Transparency;
- high-contrast appearance;
- right-to-left layout;
- keyboard navigation and pointer selection on iPad.

Do not depend on color, a sparkle icon, or animation to indicate that an action exists. When a suggestion appears, avoid interruptive announcements for every row; make the action discoverable when focus reaches it.

## Loading and scroll behavior

If the row becomes nonzero while a person is reading:

- preserve the message’s visual anchor;
- avoid moving the compose field unexpectedly;
- do not jump to the newest message;
- keep the action available after a rotation/size change;
- cancel work for messages far outside the visible range if the product does not need it.

When using generate(message:previousMessages:), tie the task to the message ID/version and cancel it on edits or deletion. A stale suggestion must never reattach to a newly reused row.

## Conversation actions versus app AI

Keep three surfaces visibly different:

| Surface | Owner | Design |
| --- | --- | --- |
| SuggestedActionsView | System framework | Inline, optional, adjacent to message |
| App-generated draft/summary | Product AI | Reviewable, provenance-labelled, editable |
| App command | App Intent/product | Explicit command, authorization/confirmation, undo |

Do not label all three “AI suggestions.” The person needs to know what the app controls and what the system will open.

## Edge cases

Design for:

- invitation with missing date;
- ambiguous timezone;
- recurring or conflicting event;
- reminder with no clear due date;
- location name with multiple matches;
- message edited after suggestion generation;
- message deleted while the action is visible;
- offline state when Calendar/Maps handoff cannot complete;
- system action unavailable;
- disabled entitlement/build;
- no model/system support on the device.

In ambiguous cases, let the framework show no action or keep the system action optional. Do not fill missing information with model guesses.

## Visual QA

Capture:

- a message with no action;
- a message with Calendar action;
- a message with Reminders action;
- a message with Maps action;
- action appearing after the row is on screen;
- pre-generated action cache;
- edited/deleted message;
- large text and VoiceOver;
- reduced motion/transparency;
- light/dark appearance;
- iPad split view and keyboard;
- system handoff and return.

The app should remain a good messaging app if every Suggested Actions result is absent.

## Sources

- [Suggested Actions](https://developer.apple.com/documentation/SuggestedActions)
- [SuggestedActionsView](https://developer.apple.com/documentation/suggestedactions/suggestedactionsview)
- [Suggested Actions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.suggested-actions)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

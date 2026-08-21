# Suggested Actions and Private Message Intelligence

Suggested Actions is a beta SwiftUI framework for messaging apps. It accepts a message representation and optional previous-message context, analyzes that content on-device, and can show inline actions such as creating a Calendar event, adding a Reminder, or opening a location in Maps.

The framework is intentionally narrow. It is not a general Foundation Models API, not a custom classifier, and not a permission to send message content to an external model. Apple’s current documentation says the framework analyzes the content you provide on-device and does not send it to Apple servers. The route still requires an explicit Suggested Actions entitlement and final-SDK verification.

## Outcome and boundary

| Desired outcome | Suggested Actions fit | Keep separate |
| --- | --- | --- |
| Offer system actions next to a message | Yes, with SuggestedActionsView | Message delivery, account sync, and action completion |
| Detect an event, reminder, or location in a message | Yes, if the system provides a suggestion | A custom extractor or guarantee that every message is recognized |
| Build arbitrary AI actions | No | Foundation Models, App Intents, or a product-owned review route |
| Add a custom “Summarize” or “Translate” button | Not this framework’s documented surface | SwiftUI/UIKit plus the selected AI/product route |
| Let a person create a Calendar event from a message | Suggested Actions can surface the system action | Calendar permission and event creation result |
| Store the message for analytics | Product-owned data policy | Suggested Actions’ on-device processing claim |

The architecture is:

~~~text
message model -> SuggestedActionsMessage
             -> SuggestedActionsView
             -> optional pre-generation/cache
             -> person chooses a system action
             -> app reconciles its own message/action state
~~~

Do not treat a displayed suggestion as proof that the action completed.

## Entitlement and beta gate

The entitlement key is com.apple.developer.suggested-actions. Apple’s entitlement documentation describes it as a Boolean capability for a messaging app. Add it to the intended target through Xcode and inspect the signed artifact.

The current framework and SuggestedActionsView pages are marked beta. Model the build states:

| Build state | Surface |
| --- | --- |
| No entitlement | Do not include the route; show ordinary message UI |
| Development entitlement, beta SDK | Exercise the surface with fixtures and physical/system tests |
| Final SDK, signed entitlement | Recheck symbol signatures, action behavior, privacy copy, and release policy |
| Entitlement unavailable for distribution | Keep the messaging app functional without Suggested Actions |

An API symbol visible in the current documentation is not enough to claim iOS 26 production availability. Inspect the selected Xcode SDK’s availability and beta annotations, then verify the final release target.

## SuggestedActionsView behavior

SuggestedActionsView is a MainActor SwiftUI view. Its documented initializer accepts:

- a SuggestedActionsMessage for the current message;
- an array of previous SuggestedActionsMessage values.

When no action applies, the view has zero size and does not introduce a gap. This allows the app to place it alongside every message without manually deciding which messages look actionable. When actions become available, the view can animate them into place.

The view can read standard SwiftUI modifiers such as:

- tint;
- foregroundStyle;
- font;
- buttonBorderShape.

Use those modifiers to fit the app’s message surface while keeping the system action’s identity. Do not wrap it in a custom AI card that implies the app invented the action.

## Message context

The app supplies a SuggestedActionsMessage representation rather than passing an arbitrary raw transcript to a model. The message identity matters for cached suggestions: Apple’s documentation says pre-generated suggestions are reused when the new message ID matches the cached message ID.

Use stable, privacy-conscious message identity:

- the ID must refer to the displayed message record;
- changing the message text should invalidate or change the representation;
- do not reuse one ID for unrelated messages;
- do not use a secret account token as the ID;
- do not log full message content with the suggestion result.

Previous context should be minimal. The framework exposes SuggestedActionsMessage.previousMessagesLimit; use the documented limit and only provide context necessary for understanding the current message. More text is not automatically better and increases privacy review scope.

## Pre-generation and caching

When a message is about to appear, call SuggestedActionsView.generate(message:previousMessages:) to fetch and cache suggestions for future display. The method is async. This can avoid showing a loading state when the view later appears.

Use a bounded pre-generation policy:

1. generate only for messages the person can see or is about to see;
2. cancel when a message is deleted, edited, or leaves the visible window;
3. use the message ID and version as the cache key;
4. invalidate the cache after edited content;
5. never pre-generate for a hidden archive without a clear product reason;
6. do not treat cache completion as action availability proof;
7. keep a fallback message row when the framework is unavailable.

The view itself may still load or animate suggestions. Pre-generation is a performance and presentation choice, not a new privacy permission.

## Privacy model

The system’s on-device analysis does not send provided content to Apple servers according to the current documentation. The app remains responsible for:

- selecting which message content to provide;
- avoiding unnecessary previous messages;
- preventing raw messages from entering app analytics;
- redacting logs and crash diagnostics;
- not duplicating content into an external AI service;
- explaining any message sync or server transport separately;
- handling shared devices, screenshots, backups, and account deletion.

Do not copy Apple’s on-device privacy statement into a broader claim such as “your messages never leave the device.” The app’s own messaging service, backups, push payloads, moderation service, or logging pipeline may have different behavior.

## Action semantics

The framework can identify system actions but does not turn every suggestion into an app-owned command. Design the message row around a handoff:

| Suggested content | User-facing action | App proof |
| --- | --- | --- |
| Meeting time/date | Add to Calendar | The person accepted the system action; verify any app-owned record separately |
| Task/reminder | Add to Reminders | The system action was offered; do not claim a reminder exists without the appropriate result |
| Location | Open in Maps | A Maps handoff occurred; do not claim navigation started |

If the messaging app needs a durable receipt, maintain its own state such as “system action offered” or “person chose action,” subject to the available callback/system behavior. Do not infer completion from the presence of a suggestion.

## Content safety and user trust

Suggested actions are generated from message content that can be ambiguous, adversarial, sarcastic, or private. The app should:

- show the source message next to the suggestion;
- keep the action optional;
- avoid language that says “the system understood this perfectly”;
- preserve the original message;
- allow the person to ignore or dismiss the suggestion;
- avoid adding duplicate actions on repeated render;
- handle edited/deleted messages;
- keep the action visually subordinate to the conversation.

Do not use the route for medical, legal, financial, or safety-critical commitments without a separate confirmation and domain review. A message containing “take two tablets at 8” should not become an automatic healthcare schedule merely because a system action appears.

## Lifecycle and state model

Use a state model for the message row:

~~~text
notEligible
-> contextReady
-> generationPending
-> suggestionAvailable
-> actionOffered
-> personSelected
-> systemHandoff
-> appReceiptPending
-> appReceiptObserved

generationPending -> noSuggestion
generationPending -> cancelled
any state -> messageEdited
any state -> messageDeleted
any state -> unavailableBuild
~~~

The framework’s zero-size behavior means “no suggestion” can be a normal layout state. Do not reserve a permanent empty card or insert a loading spinner into every message row.

## SwiftUI and Liquid Glass

The SuggestedActionsView should remain an inline native element. Use Liquid Glass around the conversation-level toolbar, compose action, or selected-message review surface, not as a translucent replacement for the system suggestion itself.

Good composition:

- message bubble;
- timestamp/read state;
- SuggestedActionsView;
- optional disclosure or selection action.

Avoid:

- an oversized glass card titled “AI detected”;
- animated particles behind private messages;
- custom icons that imply a suggestion is guaranteed;
- a fake Calendar/Reminder/Maps button that bypasses the system route;
- hiding suggestions behind a swipe-only gesture.

Respect Dynamic Type, VoiceOver, Reduce Motion, Reduce Transparency, keyboard navigation, and right-to-left layout. Test the zero-height route so assistive technology does not announce a meaningless empty container.

## On-device AI relationship

Suggested Actions is system-provided on-device intelligence. Foundation Models can still be useful for a separate, reviewable feature such as drafting a reply or summarizing a thread, but do not combine the surfaces without clear provenance:

| Output | Provenance label |
| --- | --- |
| SuggestedActionsView chip | System suggested action for this message |
| Foundation Models summary | App-generated draft/summary, with model availability and review |
| App Intent execution | App-owned command with authorization/confirmation |
| Calendar/Reminders/Maps handoff | System action selected by the person |

The Suggested Actions framework cannot be used as a general model prompt or as a way to obtain extracted entities for arbitrary background processing.

## Proof boundary

| Claim | Evidence |
| --- | --- |
| Route is configured | Target capability, signed entitlement, SDK availability |
| View can render | Compile and SwiftUI fixture |
| Suggestion is generated | Physical/system run with a known message fixture |
| No suggestion has no layout gap | UI test with a non-actionable message |
| Cached generation works | Generate, render matching message ID, edit/invalidate, rerender |
| Privacy behavior | Input audit, network observation appropriate to the test, redacted logs |
| System action works | Person selects Calendar/Reminder/Maps action and system handoff is observed |
| App message state is correct | App-owned receipt logic and edited/deleted-message test |
| Release is eligible | Final SDK, signed entitlement, beta/release review, App Store artifact |

Previews and deterministic fixtures cannot prove on-device language analysis, system suggestion availability, or action handoff.

## Sources

- [Suggested Actions](https://developer.apple.com/documentation/SuggestedActions)
- [SuggestedActionsView](https://developer.apple.com/documentation/suggestedactions/suggestedactionsview)
- [Suggested Actions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.suggested-actions)
- [Updates](https://developer.apple.com/documentation/updates)
- [iOS and iPadOS release notes](https://developer.apple.com/documentation/ios-ipados-release-notes)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

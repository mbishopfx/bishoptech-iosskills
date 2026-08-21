# Suggested Actions Proof Matrix

Suggested Actions requires evidence for entitlement, final SDK/beta status, on-device processing, message context, zero-size layout, system action handoff, privacy, and fallback. A preview with a mock chip proves none of the private system-analysis claims.

## Test record

| Field | Record |
| --- | --- |
| App target | Messaging bundle ID and target membership |
| SDK/deployment | Xcode, SDK, iOS/iPadOS target, availability annotations |
| Entitlement | com.apple.developer.suggested-actions in signed artifact |
| Framework state | Beta or final status for this SDK |
| Device | Physical model, OS build, locale, region, Apple account state |
| Message fixture | Redacted fixture ID, version, content category, edit/delete state |
| Context | Current message and count of previous messages supplied |
| Cache | Generation start/cancel/finish, ID/version, invalidation |
| System destination | Calendar, Reminders, Maps, or no action |
| Privacy | Input/log/network/analytics audit |
| Accessibility | VoiceOver, Dynamic Type, Voice Control, Switch Control, reduced effects |
| Evidence | Screen recording, UI test result, signed archive, operator notes |

Do not put message text, private conversation history, or system destination details into shared logs unless the test fixture is synthetic and approved.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Framework is the correct route | Messaging app and system-action outcome | A generic chat-like screen |
| Entitlement configured | Xcode capability plus extracted signed entitlement | Source entitlement file |
| Final SDK route exists | Compile at target SDK and availability check | Current beta web documentation |
| View renders | Physical/system run with entitlement and message fixture | SwiftUI preview |
| No suggestion leaves no gap | Non-actionable message UI test and device run | Hiding the view manually |
| Suggestion is system-generated | Known message fixture with actual SuggestedActionsView result | Hard-coded chip |
| On-device privacy behavior holds | Input boundary audit and approved network/log observation | App copy saying “private” |
| Previous context is bounded | Serialized projection/count audit | A source message object with no inspection |
| Pre-generation cache works | Generate, matching ID render, edit/version invalidation | A loading spinner removed from UI |
| Suggestion appears after animation | Device run with row anchor/scroll evidence | Static screenshot |
| Calendar action handoff works | Person selection and observed Calendar/system transition | Suggestion visible |
| Reminder action handoff works | Person selection and observed Reminders/system transition | App button called “Add” |
| Maps handoff works | Person selection and observed Maps opening | Location text recognized |
| Completion is truthful | App receipt is based on observable result | Assuming tap equals created event |
| Deleted message is safe | Active generation/cache cancellation and row removal | Local message deletion only |
| Fallback works | Build/device/system unavailable branches | Entitlement always enabled |
| Accessibility works | Task runs with VoiceOver, Dynamic Type, Voice Control, Switch Control | Visual audit alone |
| Release is ready | Final artifact, beta policy review, target/entitlement evidence | Development run |

## Message fixtures

Use synthetic, versioned fixtures:

- plain conversational message with no actionable content;
- explicit meeting date/time;
- ambiguous date/time with no timezone;
- reminder-like task with a due date;
- location with one clear place;
- location with multiple possible matches;
- message containing private/sensitive text that policy excludes;
- edited meeting message;
- deleted message;
- long message with previous context;
- adversarial or sarcastic wording;
- message with unsupported language/device state.

Record expected “no suggestion” cases. A no-suggestion result is not a framework failure.

## Context and cache checks

- [ ] Current message ID is stable for an unchanged message.
- [ ] Edited content changes the representation or version.
- [ ] Deleted content cancels generation and clears app-owned cache.
- [ ] Previous context never exceeds SuggestedActionsMessage.previousMessagesLimit.
- [ ] Context is not collected for hidden/archive messages without an explicit product reason.
- [ ] A stale cache does not attach to a reused row ID.
- [ ] The row remains usable while generation is pending.
- [ ] New row height preserves scroll anchor.
- [ ] A message leaving the visible scope cancels optional pre-generation.

## System-action scenarios

| Scenario | Expected result |
| --- | --- |
| Calendar suggestion visible | Person can choose it; app does not assert event creation without evidence |
| Calendar action cancelled | Conversation returns without false completion |
| Reminder suggestion visible | Person can choose it; system handoff is distinct from app state |
| Maps suggestion visible | Maps opens if supported; app says opened, not navigation started |
| Destination unavailable | Suggestion absent or handoff fails safely |
| Message edited during handoff | Original message and app state remain coherent |
| Repeated render | No duplicate app-owned completion or duplicate generation side effect |
| App backgrounded | On return, app reloads message/action state |

## Privacy checks

- [ ] Only current/bounded previous context is projected.
- [ ] Raw message text is absent from analytics and debug logs.
- [ ] Model/system result is not sent to an external AI service.
- [ ] Cache deletion follows message/account deletion policy.
- [ ] Screenshots and recordings use synthetic content.
- [ ] Transport, backup, moderation, and account-sync claims are not conflated with framework on-device processing.
- [ ] Privacy copy states what the app supplies to the framework.

## UI and accessibility matrix

- [ ] Zero-size no-suggestion state creates no accessibility noise.
- [ ] VoiceOver encounters the suggestion after the source message.
- [ ] Action name and destination are understandable.
- [ ] Dynamic Type does not truncate the system action.
- [ ] Voice Control can select visible actions.
- [ ] Switch Control reaches the row.
- [ ] Reduce Motion keeps the action understandable.
- [ ] Reduce Transparency preserves contrast.
- [ ] RTL and long localized message text work.
- [ ] Keyboard and pointer behavior works on iPad where supported.
- [ ] Focus returns to a sensible message after system handoff.

## AI and safety checks

| Fixture | Expected behavior |
| --- | --- |
| Ambiguous date | No unsafe certainty; system may show no action |
| Missing timezone | Do not claim a correct local Calendar time |
| Sensitive medical instruction | Do not imply a medical workflow is safe |
| Financial/legal wording | Keep optional and non-authoritative |
| Sarcasm | No requirement to create an action |
| Edited message | Recompute or remove stale action |
| Model/framework unavailable | Normal messaging UI |
| App-owned summary feature | Separate provenance and review surface |

The framework’s suggestion is not a domain authorization, diagnosis, or guarantee.

## Release packet

Preserve:

1. final SDK and beta/release status;
2. target capability and signed entitlement;
3. message fixture IDs and context policy;
4. cache/generation/invalidation evidence;
5. system handoff evidence;
6. privacy/logging/analytics audit;
7. accessibility and localized UI results;
8. fallback build/device test;
9. archive and App Store metadata review.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| eligible | Target/build/SDK can use the framework |
| generated | Framework produced or cached a suggestion for a message |
| offered | SuggestedActionsView displayed a system action |
| selected | Person chose the system action |
| handed off | System destination opened or accepted the action request |
| completed | Destination result was actually observed |
| absent | No action was available or route was unavailable |
| invalidated | Message edit/delete made old context unusable |

## Sources

- [Suggested Actions](https://developer.apple.com/documentation/SuggestedActions)
- [SuggestedActionsView](https://developer.apple.com/documentation/suggestedactions/suggestedactionsview)
- [Suggested Actions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.suggested-actions)
- [iOS and iPadOS release notes](https://developer.apple.com/documentation/ios-ipados-release-notes)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

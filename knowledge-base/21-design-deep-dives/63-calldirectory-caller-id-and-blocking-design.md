# Call Directory caller-ID and blocking design

Call Directory touches the Phone surface, so the product has to earn trust before it adds a label or blocks a number. The containing app owns setup, explanation, source policy, correction, and recovery. The system owns the call lookup moment and the final telephony behavior.

## Design the user’s decision

The user should be able to answer:

- What will this extension label?
- What will it block?
- Where did the data come from?
- How recent is the snapshot?
- What happens when the label is wrong?
- How do I disable or reload it?
- Is a model suggesting this, or did I explicitly approve it?

Do not lead with a decorative “AI caller shield” badge. Lead with scope, consequence, source, freshness, and control.

## Containing-app setup flow

Use a native SwiftUI settings surface:

1. Explain caller ID and blocking as separate switches or policies.
2. Show the extension’s current system status: unknown, disabled, or enabled.
3. Provide a clear Open Settings action for Call Blocking & Identification.
4. Display the last requested reload, last successful reload, source version, and counts.
5. Show the user how to correct a label or remove a block.
6. Explain that the system loads stored entries and does not ask the extension for a live web lookup during each call.
7. Provide synthetic test data and a proof checklist, not a claim that the next call will match.

Separate “extension enabled” from “data current.” A user may enable the extension while the snapshot is stale, empty, or awaiting reload.

## Caller-ID label design

Labels should be:

- short enough for the Phone surface;
- sourced and timestamped in the containing app;
- localized or intentionally language-neutral;
- distinguishable from verified identity claims;
- editable or reportable when wrong.

Use a detail view such as “Directory label: Westside Delivery · Updated 2 hours ago” instead of “Verified caller.” If the product has a user-entered label, say so. If the model proposed it, show the proposal state and require the product’s review policy before it enters the extension.

Do not expose raw numbers in a large hero treatment or VoiceOver announcement when the number is not needed for the task. When a correction workflow requires the number, provide an accessible copy action and redact it in analytics and screenshots.

## Blocking is a higher-consequence action

Treat adding a number to the blocked stream as a destructive or high-impact action:

- require an explicit confirmation for user-triggered blocks;
- explain that the system may prevent the incoming call from being shown;
- make unblocking obvious;
- show the source and reason;
- prevent model-only auto-blocking unless the product’s policy, user expectation, and distribution review support it;
- offer an emergency “disable extension” path that opens Settings.

Do not bundle “label this caller” and “block this caller” into one ambiguous toggle. They have different consequences and should have separate counts, copy, and proof.

## Liquid Glass without system imitation

Liquid Glass is appropriate for the containing app’s compact status and review surfaces, not for recreating the Phone app’s incoming-call UI. A good composition is:

- a glass status container with a plain title;
- separate tinted pills for Caller ID and Blocking;
- a source/freshness row;
- a deterministic “Reload directory” button;
- a secondary “Open Settings” button;
- a review list for AI proposals with visible Apply and Reject actions.

The glass effect is a container, not the source of meaning. Ensure labels, consequence text, and status remain legible under transparency, increased contrast, large Dynamic Type, and Reduce Motion. Avoid morphing a “block” button into a generic decorative control.

## State-driven surfaces

Model the UI with explicit states:

| State | User-facing treatment | Primary recovery |
| --- | --- | --- |
| Extension unknown | “Checking system setting” | Retry status check |
| Extension disabled | Explain that Phone will not use this directory | Open Settings |
| Enabled, data current | Show counts and freshness | Reload on demand |
| Enabled, stale | Show stale timestamp and affected policy | Refresh source, then reload |
| Reloading | Show progress and preserve prior known snapshot | Cancel or wait, depending on operation |
| Reload failed | Preserve prior state and show redacted error category | Retry after fixing data |
| Invalid snapshot | Explain that no new entries were loaded | Repair data / full rebuild |
| Model unavailable | Continue deterministic route or show no proposals | Use manual review |

Use an observable domain model for these states instead of deriving them from a button’s loading flag. The system status, source snapshot, reload operation, and model proposal queue are distinct state machines.

## Accessibility and localization

Make the same trust information available to assistive technology:

- give Caller ID and Blocking separate headings and summaries;
- announce enabled/disabled/stale status in text, not only color;
- describe the consequence of a block before confirmation;
- expose source, timestamp, label, and review decision as accessible values;
- support Dynamic Type and long translated labels;
- use semantic Buttons and Toggles instead of gesture-only glass controls;
- support Reduce Motion and increased contrast;
- keep Settings, Reload, Apply, Reject, Unblock, and Disable actions reachable by keyboard, Voice Control, and Switch Control.

If a label is ambiguous in one locale, prefer a shorter source-qualified label over truncation that changes meaning.

## AI review surface

An AI proposal card should show:

- the normalized record identity in a privacy-safe form;
- proposed label or block policy;
- source evidence and freshness;
- model availability/version;
- confidence or uncertainty described in plain language;
- Apply, Reject, and Edit actions;
- what will happen after Apply: local snapshot update and reload request.

The model output is not the system truth. Keep it out of the Call Directory extension until the deterministic validator accepts it. Do not make the Phone surface carry a confidence score that users cannot interpret.

## Proof-oriented design handoff

The design handoff should name:

- the containing-app target and extension target;
- the bundle identifier used for manager calls;
- the source snapshot format and version;
- full and incremental reload fixtures;
- the system status and Settings handoff;
- a controlled physical-device caller-ID/blocking test;
- stale, malformed, duplicate, changed-label, and correction flows;
- accessibility settings and localization fixtures;
- signed distribution evidence.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Identifying and blocking calls](https://developer.apple.com/documentation/callkit/identifying-and-blocking-calls)
- [CXCallDirectoryExtensionContext](https://developer.apple.com/documentation/callkit/cxcalldirectoryextensioncontext)
- [CXCallDirectoryManager](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager)
- [CXCallDirectoryManager.EnabledStatus](https://developer.apple.com/documentation/callkit/cxcalldirectorymanager/enabledstatus)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

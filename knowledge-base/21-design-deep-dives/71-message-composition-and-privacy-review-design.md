# Message composition and privacy-review design

Email and text composition are high-consequence handoffs disguised as simple buttons. The person may be about to contact a real recipient, disclose private material, or attach a document that cannot be recalled. A native design keeps the app’s review state and Apple’s final composition surface distinct.

## Composition is a handoff, not a success screen

Use this hierarchy:

~~~text
what is being sent
  -> who it is addressed to
  -> what data leaves the app
  -> what the person can edit
  -> which Apple system surface will open
  -> what local result came back
~~~

The app-owned screen should answer “What am I about to hand off?” The Message UI surface answers “Do I want to edit and send this through Mail or Messages?” Do not compress both decisions into one decorative glass button.

## Review card anatomy

A compact review card can contain:

| Region | Content |
| --- | --- |
| Destination | Mail or Messages, recipient count, and the exact selected addresses or phone numbers where appropriate. |
| Purpose | A short label such as “Send this report to…” rather than an ambiguous share icon. |
| Body preview | A readable, editable preview; distinguish generated text from user-authored text. |
| Attachments | Filename, type, size, and a remove/redact control. |
| Privacy note | What personal fields, source data, or metadata are included. |
| Primary action | A clear handoff to the selected Apple surface. |
| Fallback | Copy, export, or manual route when the device is not configured. |

The review card is not a replacement for the system composer. Keep it short enough that the person can actually inspect the important fields before the handoff.

## Liquid Glass without counterfeit system UI

Liquid Glass is most useful here as a restrained container for app-owned controls: a toolbar action, a compact review card, an attachment row, or a status capsule. It should create hierarchy around the content, not hide recipient identity behind translucency.

Use these rules:

- keep recipient and attachment text on a stable, high-contrast surface;
- avoid stacking multiple translucent cards over busy media;
- let the system composer own its appearance and behavior;
- use native buttons, labels, menus, and sheets before custom glass controls;
- support reduced transparency and increased contrast;
- keep the handoff action visually distinct from regenerate, edit, and cancel;
- use motion to explain that the app is handing off to another system surface, not to suggest that delivery is complete.

An “Apple-like” result comes from semantic hierarchy, predictable navigation, typography, spacing, and system participation. Rebuilding Mail or Messages inside a glass shell is less native than presenting Apple’s own composer.

## AI-generated copy needs a provenance boundary

If Foundation Models, Natural Language, or another on-device route drafts a message, present it as a proposal with an editing step:

1. show what source the model was allowed to use;
2. identify generated text;
3. expose important omissions or uncertainty;
4. let the person edit or replace it;
5. revalidate recipients and attachments after edits;
6. create the final immutable snapshot only when the person chooses the handoff;
7. let Apple’s composer receive the initial values;
8. treat the delegate result as a local composition outcome.

Do not send hidden model context, private database fields, or an unreviewed “tool call” to Message UI. A tool that requests composition is still a side effect and must sit behind explicit user intent.

For high-risk content, prefer deterministic templates and field-level confirmation. Examples include medical information, financial records, passwords, location history, private journal material, and messages addressed to a contact selected by a model. The model can suggest; deterministic code decides whether a destination, file, or disclosure is allowed.

## Privacy copy

Privacy copy should describe data movement in ordinary language:

- “The selected PDF will be available as an attachment in Mail.”
- “The phone number you choose will be placed in the Messages recipient field.”
- “The draft is prepared on this device. Nothing is sent until you review it in Apple’s composer.”
- “Mail may save the message to Drafts or queue it in the outbox; this app cannot verify final delivery.”

Do not say “sent” when the delegate only reports queued or composed. Do not imply that an email address was verified merely because the composer accepted it. If an attachment cannot be removed after the handoff, make that boundary visible before opening the system UI.

## Unavailable and fallback screens

When canSendMail() or canSendText() is false, the empty state should preserve the task:

~~~text
This device cannot open the selected composer right now.

Your draft is saved in this app.

[Copy draft] [Export file] [Try again]
~~~

Avoid a dead-end alert that erases the user’s work. A fallback can use ShareLink, a file export, copy-to-paste, or an explicit mailto/sms handoff if those are appropriate, but label the route and its evidence separately. A share sheet destination is not guaranteed, and a URL handoff is not the same as the in-app composition controller.

## Accessibility as a delivery safeguard

Accessibility is part of the privacy review because a hidden recipient, clipped attachment name, or unlabeled action can cause an unintended disclosure. Test:

- reading order from destination through attachment and handoff;
- Dynamic Type at the largest practical sizes;
- VoiceOver announcements for unavailable, queued, saved, failed, and cancelled states;
- Voice Control phrases that distinguish “Edit draft,” “Remove attachment,” and “Open Mail”;
- Switch Control focus on every state-changing action;
- localized phone/address formatting, long names, and right-to-left message text;
- reduced motion and reduced transparency;
- keyboard focus and pointer interactions on iPad and Mac Catalyst targets if supported.

Do not use color, blur, animation, or haptics as the sole signal that the recipient or privacy scope changed.

## Recommended state machine

~~~text
empty
  -> selectingSource
  -> drafting
  -> reviewing
  -> preflighting
      -> unavailable
      -> readyToPresent
  -> presentingSystemComposer
      -> cancelled
      -> saved
      -> queuedOrSentResult
      -> failed
  -> reviewing
~~~

The app should be able to return to reviewing after cancellation or failure. It should not silently re-open the composer, generate a different body, or change recipients after the person returns.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Message UI](https://developer.apple.com/documentation/messageui)
- [MFMailComposeViewController](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontroller)
- [MFMessageComposeViewController](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontroller)
- [MFMailComposeResult](https://developer.apple.com/documentation/messageui/mfmailcomposeresult)
- [MessageComposeResult](https://developer.apple.com/documentation/messageui/messagecomposeresult)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

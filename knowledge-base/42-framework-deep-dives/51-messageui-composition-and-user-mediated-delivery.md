# Message UI composition and user-mediated delivery

Message UI is a deliberately narrow system-surface framework. It lets an app prepare the initial contents of an email or SMS/MMS message and present Apple’s composition interface inside the app. It does not turn the app into a mail or messaging transport, and it does not prove that a person sent, received, or read anything.

The useful mental model is:

~~~text
app-owned task
  -> smallest approved draft
  -> device capability preflight
  -> Apple-owned composition UI
  -> person edits, sends, saves, or cancels
  -> delegate result
  -> app records only what the result actually means
~~~

## Framework scope

Message UI provides:

| Outcome | Route | Ownership boundary |
| --- | --- | --- |
| Prepare an email | MFMailComposeViewController | The app supplies initial recipients, subject, body, and optional attachments; Mail owns editing and transport. |
| Prepare an SMS or MMS message | MFMessageComposeViewController | The app supplies initial recipients, body, subject, and supported attachments; Messages owns editing and transport. |
| Put a person in control of the content | Standard composition interface | The person can edit or cancel; the app must not treat a draft as a sent message. |
| Return a completion state | MFMailComposeViewControllerDelegate or MFMessageComposeViewControllerDelegate | The delegate receives a local composition result and is responsible for dismissing the controller. |

The framework is not a general-purpose API for silently sending mail or text messages. If the product needs automated delivery, server mail, a transactional provider, or an in-app conversation database, those are different architectures with different consent, abuse, privacy, and delivery evidence.

## Availability is a product state

Call MFMailComposeViewController.canSendMail() before presenting the email composer. Call MFMessageComposeViewController.canSendText() before presenting the text composer. These methods describe whether the current device is configured for the relevant composition route; they are not static feature flags and should not be cached as permanent truth.

For text messages, check the narrower capabilities before offering optional features:

- canSendAttachments() before adding a file or image;
- canSendSubject() before presenting a subject field or assuming the subject will be accepted;
- isSupportedAttachmentUTI(...) before offering a particular file type.

If a preflight fails, keep the app-owned draft and explain the available fallback. Do not present an empty or custom imitation of the system composer and call that equivalent. A feature can instead offer copy, export through the system share sheet, a mailto or sms handoff where appropriate, or a manual workflow. The fallback must be named as a different route.

Availability can change while the app is running. For text composition, observe the documented text-message availability-change notification if the feature remains open long enough for the device configuration to change. Re-run preflight when the user returns to the action, not only when the screen is first loaded.

## Configure before presentation

Configure the composer before presenting it:

1. Validate the user-selected destination and redact fields not needed for the task.
2. Create an immutable draft snapshot.
3. Check the route’s availability and any optional attachment capability.
4. Instantiate the appropriate view controller.
5. Assign the corresponding delegate.
6. Set recipients, subject, body, and attachments.
7. Present the controller using the current UIKit presentation context.
8. Stop mutating the composer’s initial fields after presentation.

Apple’s documentation states that the email controller ignores attempts to modify its fields after it is presented. The system composition UI is also Apple-owned: do not modify its view hierarchy. Customize the app-owned screen around it, not the internals of the standard controller.

For a SwiftUI app, UIViewControllerRepresentable is the interop seam. Its make method creates the UIKit controller, its update method responds to SwiftUI state changes, and its Coordinator forwards UIKit delegate callbacks. Treat the composer as a modal transaction rather than a child view whose fields are continuously bound to every keystroke in the app.

## Result semantics

Email results are:

- cancelled: the person dismissed the composition without saving or queuing the message;
- saved: the message was saved to Mail drafts;
- sent: the message was queued in the user’s outbox;
- failed: Mail could not save or queue the message.

The email result does not let the app verify final delivery. The user can delete a queued message before it is sent, and Mail remains responsible for transport.

Text results are:

- cancelled: the person cancelled composition;
- sent: the message was successfully queued or sent according to the system result;
- failed: the attempt to save or send was unsuccessful.

The text result is not a read receipt, server acknowledgment, or proof that every recipient received the message. Store the result as a local system-composition outcome, with a timestamp and draft identifier, not as a delivery guarantee.

The delegate must dismiss the composition interface explicitly. In SwiftUI, a parent can also clear the item that drives a sheet, but the delegate path should remain responsible for the UIKit controller’s dismissal and for returning the result exactly once. Protect against duplicate callbacks if an app-level state machine can also dismiss the sheet.

## Draft and attachment boundaries

An AI-generated draft should be a proposal, never an immediately presented side effect. Keep separate values for:

- source text or selected records;
- generated subject/body;
- user-edited subject/body;
- recipients chosen by the person;
- redaction and attachment decisions;
- the immutable snapshot passed to Message UI;
- local composition result.

Attachments deserve their own validation. Check type, size, filename, privacy metadata, and the return value of the add-attachment operation where the API provides one. Prefer a user-approved, temporary export over sharing a live database file. Remove temporary material after cancellation or after the system composer no longer needs it, while respecting the provider’s documented loading lifetime.

Never pass internal database identifiers, auth tokens, raw logs, hidden prompts, or unrelated personal fields into a message just because the system composer can display them. An email address or phone number supplied by the app is an initial recipient, not proof that the person intended to contact that destination.

## Native design and Liquid Glass

The strongest Apple-native composition is a small app-owned review surface followed by the standard system composer:

~~~text
source selection
  -> recipient and content review
  -> optional redaction/attachment controls
  -> clear “Continue to Mail” or “Continue to Messages” action
  -> Apple-owned composition UI
~~~

Use semantic SwiftUI controls, platform navigation, and an ordinary toolbar/share affordance. Liquid Glass can support the app-owned review card or toolbar when it improves hierarchy, but it should not be used to fake, tint, or rebuild the system composer. Keep the review surface visually quiet: recipient identity, message purpose, attachment names, and the next system handoff should be more legible than decorative material.

For an AI-assisted workflow, make the generated portion obvious and editable. Show source context or a concise “drafted from” explanation, allow the person to replace the text, and require an explicit send decision inside Apple’s composer. Do not use a generated confidence score as permission to skip review.

## Accessibility and localization

Verify the complete task, not only the app-owned preflight screen:

- VoiceOver can identify the recipient, subject, body, attachment list, availability state, and handoff action;
- Dynamic Type does not hide the review action or truncate privacy warnings;
- Voice Control and Switch Control can open, cancel, and retry the composer;
- localized email addresses, phone numbers, names, right-to-left text, and long message bodies remain understandable;
- attachments have meaningful filenames and accessible summaries;
- reduced transparency and reduced motion leave the review state legible;
- the system composer remains usable with the person’s device settings.

Do not make a mail or message icon the only label for a high-impact action. Use a verb that explains the destination and keep destructive or irreversible-looking actions separate from an AI “regenerate” action.

## Failure and fallback state model

| State | User-facing behavior |
| --- | --- |
| Drafting | Show source, proposed content, recipients, and editable fields. No external side effect. |
| Unavailable | Explain that Mail or messaging is not configured on this device; preserve the draft. |
| Attachment unsupported | Remove or replace only after user confirmation; offer a text-only or share/export route. |
| Presenting | Disable duplicate launch actions and retain the immutable snapshot. |
| Cancelled | Keep the draft for edit/retry; do not report delivery. |
| Saved to drafts | Report local Mail draft outcome only. |
| Queued/sent result | Report system result only; never claim recipient delivery. |
| Failed | Preserve the draft, record the local failure, and provide a retry or alternate route. |
| App backgrounded or terminated | Reconcile sheet/draft state on next launch; never infer completion from disappearance. |
| AI unavailable or ambiguous | Fall back to manual editing with no generated content or a deterministic template. |

## Evidence checklist

- current Apple documentation and SDK signature review for Message UI, UIKit presentation, and SwiftUI interop;
- named target imports and a compile check for the selected deployment target;
- email preflight true/false states on a configured and unconfigured device;
- text preflight, optional subject, optional attachment, unsupported type, and availability-change states;
- real Apple-owned composition UI, edit, cancel, save, queued/sent result, failure, and explicit dismissal;
- result logging that distinguishes local composition outcome from delivery;
- recipient/attachment redaction and temporary-file cleanup;
- VoiceOver, Dynamic Type, localization, right-to-left, reduced transparency, and alternate-input completion;
- AI proposal, user edit, stale-source invalidation, and manual fallback;
- signed target and release privacy review if the workflow exposes personal content.

## Sources

- [Message UI](https://developer.apple.com/documentation/messageui)
- [MFMailComposeViewController](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontroller)
- [canSendMail()](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontroller/cansendmail%28%29)
- [MFMailComposeViewControllerDelegate](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontrollerdelegate)
- [MFMailComposeResult](https://developer.apple.com/documentation/messageui/mfmailcomposeresult)
- [MFMessageComposeViewController](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontroller)
- [canSendText()](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontroller/cansendtext%28%29)
- [MFMessageComposeViewControllerDelegate](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontrollerdelegate)
- [MessageComposeResult](https://developer.apple.com/documentation/messageui/messagecomposeresult)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Showing and hiding view controllers](https://developer.apple.com/documentation/uikit/showing-and-hiding-view-controllers)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

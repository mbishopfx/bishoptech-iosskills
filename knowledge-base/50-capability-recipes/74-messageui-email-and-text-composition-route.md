# Message UI email and text composition route

Use this route when an app should prepare a person-reviewed email or SMS/MMS message and let Apple’s Mail or Messages composition interface finish the interaction.

## Choose the smallest handoff

| Need | Preferred route | Avoid assuming |
| --- | --- | --- |
| User reviews and edits an email in the app’s modal flow | MFMailComposeViewController | The result proves delivery or that Mail remains configured later. |
| User reviews and edits a text message | MFMessageComposeViewController | The result proves recipient receipt or conversation state. |
| App needs a general system destination chooser | ShareLink, Transferable, or UIActivityViewController | Every device has Mail or Messages installed/configured. |
| App only needs to open a URL-configured composer | mailto or sms URL handoff | A URL handoff has the same lifecycle and result semantics as Message UI. |
| App needs automated transactional delivery | Server/provider architecture | Message UI is a background sending API. |

Pick one primary route per user action. If you expose alternatives, explain how their privacy, editing, and result behavior differ.

## Route contract

~~~text
source record or user text
  -> redaction policy
  -> typed MailDraft or TextDraft
  -> recipient confirmation
  -> attachment validation
  -> canSendMail() or canSendText()
  -> create and configure composer
  -> present through SwiftUI/UIKit bridge
  -> delegate dismissal
  -> local result mapping
  -> preserve/reconcile app draft
~~~

The route owns a draft, not a delivery promise. Keep an identifier for the app-owned draft and a timestamp for the composition attempt. Never overwrite the canonical source record just because a message was composed.

## Step 1: build a redacted draft

Create a draft from a confirmed snapshot:

| Field | Rule |
| --- | --- |
| Recipients | Explicitly selected or entered by the person; no model-only recipient inference. |
| Subject | Optional for text; always editable for mail. |
| Body | Plain text by default; HTML only when the product truly requires it and has a review reason. |
| Attachments | User-selected, type/size checked, metadata reviewed, and temporary where possible. |
| Source reference | Kept in the app for provenance; never inserted into the outgoing content accidentally. |
| Privacy class | Determines whether extra confirmation or redaction is required. |

If an on-device model drafts the body, pass only the minimum authorized source context and decode into the draft type. Run deterministic checks after generation: recipient count, prohibited fields, secret-like strings, unsupported attachment types, body length, and stale source version.

## Step 2: review before preflight

The review screen should make the outgoing action obvious. For a report export, show the report title, recipient, body preview, attachment name, and a privacy note. For a message generated from a selected contact or event, show the exact selected fields and not the entire record.

Require the person to choose the handoff. Regeneration, edit, and handoff should be separate actions. When the source changes while the review screen is open, invalidate the draft or ask to refresh it; do not silently merge new content into the message.

## Step 3: preflight the device

For email:

1. call canSendMail();
2. if false, preserve the draft and offer a clearly labeled fallback;
3. if true, configure the email controller before presentation.

For text:

1. call canSendText();
2. check canSendAttachments() or canSendSubject() only if those controls are being offered;
3. validate each attachment type with isSupportedAttachmentUTI(...);
4. preserve the draft if any optional feature is unavailable.

Preflight is not permission to send. It only decides whether the system composition route can be offered at that moment.

## Step 4: hand off through the system surface

Use UIViewControllerRepresentable for a SwiftUI app. Instantiate the controller once for the draft snapshot, assign the coordinator/delegate, set all initial fields, then present it. Do not bind the composer fields to a rapidly changing SwiftUI model after presentation.

On completion, dismiss the controller and map the result:

| Result | App state |
| --- | --- |
| Mail cancelled | Draft remains editable; no delivery claim. |
| Mail saved | Record “saved to Mail Drafts” as the local result. |
| Mail sent | Record “queued in Mail outbox” as the local result. |
| Mail failed | Preserve draft and show retry/fallback. |
| Text cancelled | Draft remains editable. |
| Text sent | Record the system’s queued/sent result; do not claim recipient delivery. |
| Text failed | Preserve draft and show retry/fallback. |

Use a single completion path. A view disappearing, scene resigning active, or controller deallocation is not a success result.

## Step 5: preserve and reconcile

After cancellation or failure, return to review. After a saved or queued result, show exactly what the result means and keep the source record unchanged unless the person separately confirms a local “contacted” or “exported” state. If the app wants to track that state, name it as an app-owned event such as compositionQueued, not messageDelivered.

If the app is terminated during composition, mark the attempt interrupted or unknown and ask the person to retry. Do not infer a result from an incomplete local log.

## AI-specific route

~~~text
selected source
  -> privacy filter
  -> on-device proposal
  -> typed draft
  -> deterministic content and recipient checks
  -> human edit/review
  -> Message UI
~~~

Good uses:

- convert a selected task into a concise email draft;
- rewrite a user-authored note in a chosen tone;
- summarize a selected document into a reviewable body;
- identify missing fields before the person opens the composer.

Unsafe shortcuts:

- choosing a recipient from an ambiguous name;
- adding every contact or calendar field to the body;
- attaching raw database exports;
- opening Message UI immediately after model output;
- recording a delegate sent result as delivery or consent to future messages.

## Proof gates

Before calling the route ready, compile it in a named app target, exercise configured and unavailable devices, inspect the real Mail/Messages composition surface, and verify the result mapping. Add physical-device evidence for account, carrier, Mail configuration, attachments, system keyboard, accessibility, and dismissal behavior. Keep server delivery proof out of this route unless the product has a separate provider architecture.

## Sources

- [Message UI](https://developer.apple.com/documentation/messageui)
- [MFMailComposeViewController](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontroller)
- [canSendMail()](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontroller/cansendmail%28%29)
- [MFMailComposeResult](https://developer.apple.com/documentation/messageui/mfmailcomposeresult)
- [MFMessageComposeViewController](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontroller)
- [canSendText()](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontroller/cansendtext%28%29)
- [MessageComposeResult](https://developer.apple.com/documentation/messageui/messagecomposeresult)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Showing and hiding view controllers](https://developer.apple.com/documentation/uikit/showing-and-hiding-view-controllers)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)

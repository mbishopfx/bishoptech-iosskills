# Message UI system-composition proof matrix

This matrix keeps “the composer opened” separate from “the person reviewed a draft” and “the message was delivered.” Message UI provides a person-mediated composition surface. Its delegate result is local evidence about the system composition flow, not end-to-end transport evidence.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Do not infer |
| --- | --- | --- |
| The target can use Message UI | Named target imports MessageUI and compiles against the selected SDK/deployment target | A framework mention in documentation means the target is configured correctly. |
| Email composition is currently available | canSendMail() true in the target test environment | Mail is configured on every device or will remain configured. |
| Text composition is currently available | canSendText() true in the target test environment | A Wi-Fi-only or iPad configuration has the same message capability as a supported cellular/iMessage setup. |
| Optional text attachments are available | canSendAttachments() true and each attachment passes supported-UTI checks | Any file accepted by the app will be accepted by Messages. |
| Optional text subjects are available | canSendSubject() true and the subject path is tested | The subject will be visible or supported for every configured recipient route. |
| Initial fields are configured | Inspect the actual composer with recipients, body, subject, and attachments before presentation | SwiftUI state after presentation changes the system controller. |
| The person can review and edit | Physical or appropriate system-surface run with edits, navigation, and cancel/send controls | A preview or screenshot represents the Apple-owned composer. |
| The app handles completion | Delegate callback, explicit dismissal, exactly-once result mapping, and return to the app-owned state | View dismissal, scene transition, or deallocation is a successful send. |
| Email was saved | MFMailComposeResult.saved from the delegate | The message was delivered or remains in Mail Drafts forever. |
| Email was queued | MFMailComposeResult.sent from the delegate plus the local attempt record | The recipient received or read the message. |
| Text was queued or sent according to the system result | MessageComposeResult.sent from the delegate | The recipient received or read the message. |
| Delivery is reliable | Separate Mail/Messages/provider evidence appropriate to the product | Message UI alone provides transport or delivery receipts. |
| The outgoing content is private | Redaction fixture, recipient review, attachment metadata review, and log/temporary-file inspection | Apple’s composer removes sensitive fields or validates the recipient’s identity. |
| AI drafting is safe | Source-minimized prompt/context, typed draft, deterministic validation, human edit, and fallback fixture | A fluent generated body is accurate, authorized, or safe to send. |
| The route is accessible | VoiceOver, Dynamic Type, Voice Control, Switch Control, localization, RTL, reduced-transparency/motion task completion | Labels or a successful compile prove end-to-end accessibility. |
| The route is release-ready | Signed target/configuration and the appropriate physical/system/account evidence | Simulator or debug behavior proves release, account, carrier, Mail, or Messages behavior. |

## Test matrix

### Email

- Mail configured and canSendMail() true;
- Mail unavailable and canSendMail() false;
- recipients, subject, plain text body, HTML body if used, and an attachment;
- attachment too large, unsupported, or unavailable;
- edit recipient/body, save to Drafts, cancel, queued/sent result, and failure;
- app backgrounding and returning while the composer is open;
- duplicate launch prevention and exactly-once completion;
- no assertion of final delivery after the delegate callback.

### Text

- canSendText() true and false;
- SMS/MMS/iMessage route appropriate to the configured device;
- subject capability true and false;
- attachment capability true and false;
- supported and unsupported attachment UTIs;
- edit recipient/body, cancel, sent result, and failure;
- text-availability-change notification handling if the screen remains active;
- no assertion of recipient delivery or read state.

### Draft and AI safety

- ambiguous contact name requires explicit recipient selection;
- source record changes while the draft is open;
- generated text contains a secret-like value or disallowed field;
- generated text is empty, too long, or missing required context;
- user edits the generated text before presentation;
- attachment is removed or redacted;
- model unavailable, language unsupported, or generation fails;
- retry does not create a second composition attempt or mutate the source record.

### Accessibility and adaptation

- VoiceOver reads destination, purpose, body, attachment, privacy note, and state;
- large Dynamic Type keeps controls reachable;
- localized names, addresses, phone numbers, and message text;
- right-to-left layout and mixed-direction recipient/body text;
- Voice Control and Switch Control complete preflight, handoff, cancel, and retry;
- reduced motion and reduced transparency;
- keyboard/pointer input on supported iPad or Mac Catalyst targets;
- physical system composer behavior under the person’s accessibility settings.

## Evidence record

Store a small evidence record per test run:

~~~text
target:
sdk:
deployment:
device_or_simulator:
mail_or_message_configuration:
capability_preflight:
draft_id:
attachment_fixture:
system_surface_observed:
delegate_result:
delivery_claim_made: none | local-composition-only | separate-provider-evidence
accessibility_settings:
privacy_review:
artifact_or_build:
notes:
~~~

Never put real credentials, private message bodies, personal addresses, or production attachments in this repository. Use controlled fixtures and redact screenshots/logs.

## Release boundary

The route is ready for a specific release only when the selected target, signing configuration, privacy review, and supported device matrix are recorded. A feature that opens a system composer on one development phone is not automatically ready for iPad, Mac Catalyst, TestFlight, or App Store distribution. If the product also has a server/provider sender, maintain a separate evidence chain for server authorization, delivery, retries, bounces, and suppression.

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
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

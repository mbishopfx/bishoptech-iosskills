# Message UI SwiftUI wrapper and safe-draft recipes

These are compile-oriented route sketches for presenting Apple’s email or text composer from SwiftUI. They are intentionally not claimed to compile in this documentation-only workspace. Compile them in a named app target, confirm the current SDK signatures, and run the real system surface on the supported device configuration.

## Typed drafts

Keep the draft immutable while the system composer is being configured:

~~~swift
import Foundation

struct MessageAttachment {
    let data: Data
    let typeIdentifier: String
    let filename: String
}

struct MailDraft {
    let recipients: [String]
    let subject: String
    let body: String
    let isHTML: Bool
    let attachments: [MessageAttachment]
}

struct TextDraft {
    let recipients: [String]
    let subject: String?
    let body: String
    let attachments: [MessageAttachment]
}
~~~

The app should create these values from a user-approved snapshot. Do not hand a live persistence object to a UIKit delegate and assume that the values remain the same after presentation.

## Email composer wrapper

~~~swift
import MessageUI
import SwiftUI

struct MailComposer: UIViewControllerRepresentable {
    typealias UIViewControllerType = MFMailComposeViewController

    let draft: MailDraft
    let onFinish: (MFMailComposeResult, Error?) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onFinish: onFinish)
    }

    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let controller = MFMailComposeViewController()
        controller.mailComposeDelegate = context.coordinator
        controller.setToRecipients(draft.recipients)
        controller.setSubject(draft.subject)
        controller.setMessageBody(draft.body, isHTML: draft.isHTML)

        for attachment in draft.attachments {
            _ = controller.addAttachmentData(
                attachment.data,
                mimeType: attachment.typeIdentifier,
                fileName: attachment.filename
            )
        }

        return controller
    }

    func updateUIViewController(
        _ uiViewController: MFMailComposeViewController,
        context: Context
    ) {
        // Configure the initial snapshot before presentation.
        // Do not continuously mutate the system composer here.
    }

    final class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let onFinish: (MFMailComposeResult, Error?) -> Void

        init(onFinish: @escaping (MFMailComposeResult, Error?) -> Void) {
            self.onFinish = onFinish
        }

        func mailComposeController(
            _ controller: MFMailComposeViewController,
            didFinishWith result: MFMailComposeResult,
            error: (any Error)?
        ) {
            controller.dismiss(animated: true) {
                self.onFinish(result, error)
            }
        }
    }
}
~~~

The host must call MFMailComposeViewController.canSendMail() before presenting this wrapper. The wrapper does not silently substitute a custom composer when Mail is unavailable.

## Text composer wrapper

~~~swift
import MessageUI
import SwiftUI

struct TextComposer: UIViewControllerRepresentable {
    typealias UIViewControllerType = MFMessageComposeViewController

    let draft: TextDraft
    let onFinish: (MessageComposeResult) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onFinish: onFinish)
    }

    func makeUIViewController(context: Context) -> MFMessageComposeViewController {
        let controller = MFMessageComposeViewController()
        controller.messageComposeDelegate = context.coordinator
        controller.recipients = draft.recipients
        controller.body = draft.body

        if MFMessageComposeViewController.canSendSubject() {
            controller.subject = draft.subject
        }

        if MFMessageComposeViewController.canSendAttachments() {
            for attachment in draft.attachments {
                guard MFMessageComposeViewController.isSupportedAttachmentUTI(
                    attachment.typeIdentifier
                ) else {
                    continue
                }

                _ = controller.addAttachmentData(
                    attachment.data,
                    typeIdentifier: attachment.typeIdentifier,
                    filename: attachment.filename
                )
            }
        }

        return controller
    }

    func updateUIViewController(
        _ uiViewController: MFMessageComposeViewController,
        context: Context
    ) {
        // Keep the controller bound to the approved initial snapshot.
    }

    final class Coordinator: NSObject, MFMessageComposeViewControllerDelegate {
        let onFinish: (MessageComposeResult) -> Void

        init(onFinish: @escaping (MessageComposeResult) -> Void) {
            self.onFinish = onFinish
        }

        func messageComposeViewController(
            _ controller: MFMessageComposeViewController,
            didFinishWith result: MessageComposeResult
        ) {
            controller.dismiss(animated: true) {
                self.onFinish(result)
            }
        }
    }
}
~~~

Call MFMessageComposeViewController.canSendText() before presenting. If attachments or subjects are essential rather than optional, treat a false optional-capability check as an unavailable route and preserve the draft instead of silently dropping content.

## SwiftUI host state

~~~swift
import SwiftUI

struct DraftScreen: View {
    @State private var mailDraft: MailDraft?
    @State private var textDraft: TextDraft?
    @State private var status = "Ready"

    var body: some View {
        VStack {
            Text(status)
            Button("Prepare email") {
                guard MFMailComposeViewController.canSendMail() else {
                    status = "Mail is not configured on this device."
                    return
                }

                mailDraft = MailDraft(
                    recipients: ["person@example.com"],
                    subject: "Review this draft",
                    body: "This is an editable starting point.",
                    isHTML: false,
                    attachments: []
                )
            }
        }
        .sheet(item: Binding(
            get: { mailDraft.map(MailDraftItem.init) },
            set: { mailDraft = $0?.draft }
        )) { item in
            MailComposer(draft: item.draft) { result, error in
                switch result {
                case .cancelled:
                    status = "Email composition cancelled."
                case .saved:
                    status = "Email saved to Mail drafts."
                case .sent:
                    status = "Email queued in Mail."
                case .failed:
                    status = "Email could not be queued."
                @unknown default:
                    status = "Mail returned an unknown result."
                }

                if let error {
                    status += " " + error.localizedDescription
                }
                mailDraft = nil
            }
        }
    }

    private struct MailDraftItem: Identifiable {
        let draft: MailDraft
        let id = UUID()
    }
}
~~~

The host example is a route sketch: the item identity and sheet binding should be simplified or adapted to the app’s real draft model. In production, use a stable draft identifier, avoid example recipients, and decide whether the sheet should be dismissed by the parent state, the UIKit controller, or both without producing duplicate callbacks.

## Result mapping

Map the result into an app-owned enum instead of a generic “success” Boolean:

~~~swift
enum CompositionState {
    case reviewing
    case unavailable
    case presenting
    case cancelled
    case savedToMailDrafts
    case queuedByMail
    case queuedOrSentByMessages
    case failed(String)
}
~~~

The queued/sent states are intentionally local. Message UI documentation says Mail remains responsible for sending and does not provide a way for the app to verify final email delivery. Text composition similarly gives the system responsibility for sending after the person approves the message.

## AI and privacy guard

Before the wrapper receives a draft:

1. restrict the model context to the selected records;
2. decode output into a MailDraft or TextDraft;
3. validate recipients, prohibited fields, body length, attachment type, and source freshness;
4. show the person the exact proposed content;
5. let the person edit or discard it;
6. create the final immutable snapshot;
7. run capability preflight again;
8. present the system composer.

Never call the wrapper directly from a model tool without a user-visible confirmation. Never log the full body, recipient list, attachment bytes, or model context in development diagnostics.

## Compile and proof checklist

- import MessageUI and SwiftUI in the named target;
- confirm current delegate signatures and actor annotations in Xcode;
- add no private API or view-hierarchy customization;
- compile with the target deployment and selected SDK;
- test canSendMail() and canSendText() false paths;
- test optional subject/attachment gates;
- test explicit delegate dismissal and exactly-once state updates;
- test real system composition, not only a preview;
- test result semantics without delivery language;
- exercise accessibility, localization, large content, and privacy redaction;
- treat the snippets as route sketches until a signed physical-device run proves the selected system behavior.

## Sources

- [Message UI](https://developer.apple.com/documentation/messageui)
- [MFMailComposeViewController](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontroller)
- [MFMailComposeViewControllerDelegate](https://developer.apple.com/documentation/messageui/mfmailcomposeviewcontrollerdelegate)
- [MFMailComposeResult](https://developer.apple.com/documentation/messageui/mfmailcomposeresult)
- [MFMessageComposeViewController](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontroller)
- [MFMessageComposeViewControllerDelegate](https://developer.apple.com/documentation/messageui/mfmessagecomposeviewcontrollerdelegate)
- [MessageComposeResult](https://developer.apple.com/documentation/messageui/messagecomposeresult)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Showing and hiding view controllers](https://developer.apple.com/documentation/uikit/showing-and-hiding-view-controllers)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)

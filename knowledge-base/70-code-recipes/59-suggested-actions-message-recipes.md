# Suggested Actions Message Recipes

These are compile-oriented SwiftUI route sketches for SuggestedActionsView, bounded previous-message context, async pre-generation, message edits/deletions, privacy audits, and native fallback. They are not compiled in this documentation-only workspace and do not prove on-device suggestion generation, entitlement approval, Calendar/Reminders/Maps handoff, or release eligibility.

Before copying:

1. Confirm the target is a messaging app.
2. Add the Suggested Actions entitlement to the intended target.
3. Verify the final SDK’s beta/availability annotations.
4. Confirm the current SuggestedActionsMessage construction/projection API in Xcode.
5. Use synthetic fixtures for previews and tests.
6. Keep app-owned message state separate from system action completion.

## Recipe 1: Model message identity and version

~~~swift
import Foundation

struct ChatMessage: Identifiable, Equatable, Sendable {
    let id: UUID
    let revision: Int
    let body: String
    let sentAt: Date
}

struct SuggestedContextKey: Hashable, Sendable {
    let messageID: UUID
    let revision: Int
}
~~~

Use a stable ID for an unchanged message and a revision that changes when its content changes. Do not reuse an old cache key for unrelated content.

## Recipe 2: Build the app-owned projection

The exact fields of SuggestedActionsMessage are SDK-sensitive. Keep construction inside one adapter:

~~~swift
import SuggestedActions

struct SuggestedActionsAdapter {
    func message(for message: ChatMessage) -> SuggestedActionsMessage {
        // Confirm the current initializer or app-specific projection in Xcode.
        // Keep message identity and displayed content aligned.
        return message.suggestedActionsMessage
    }
}
~~~

The placeholder property represents the app’s current projection layer. Do not pass raw server objects directly into a view. Keep only the current and bounded previous context required by the current SDK.

## Recipe 3: Render the inline view

Place SuggestedActionsView below every message row:

~~~swift
import SwiftUI
import SuggestedActions

struct MessageRow: View {
    let message: ChatMessage
    let previousMessages: [ChatMessage]

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(message.body)
                .textSelection(.enabled)

            SuggestedActionsView(
                message: message.suggestedActionsMessage,
                previousMessages: previousMessages
                    .suffix(SuggestedActionsMessage.previousMessagesLimit)
                    .map(\.suggestedActionsMessage)
            )
        }
    }
}
~~~

Confirm the message projection and SuggestedActionsMessage API in the selected SDK. When no suggestions apply, the system view has zero size. Do not insert an app-owned placeholder gap.

## Recipe 4: Apply native styling

Use ordinary SwiftUI modifiers that the framework documents:

~~~swift
import SwiftUI

struct StyledSuggestedActionRow: View {
    let message: ChatMessage

    var body: some View {
        SuggestedActionsView(
            message: message.suggestedActionsMessage,
            previousMessages: []
        )
        .buttonBorderShape(.capsule)
        .tint(.accentColor)
        .font(.callout)
    }
}
~~~

Do not wrap this in a custom glass card that changes the system action’s hierarchy. Test the actual size-zero state and all available action destinations.

## Recipe 5: Pre-generate with cancellation

Generate only for a visible or soon-to-be-visible message:

~~~swift
import SuggestedActions

@MainActor
final class SuggestedActionPrecomputer {
    private var task: Task<Void, Never>?

    func prepare(
        message: SuggestedActionsMessage,
        previousMessages: [SuggestedActionsMessage]
    ) {
        task?.cancel()
        task = Task { @MainActor in
            await SuggestedActionsView.generate(
                message: message,
                previousMessages: previousMessages
            )
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
    }
}
~~~

The generate call returns after asking the framework to create/cache suggestions. It does not prove that a view will show an action or that the person will select it.

## Recipe 6: Bound previous context

Make the context policy obvious:

~~~swift
struct SuggestedContext {
    let current: SuggestedActionsMessage
    let previous: [SuggestedActionsMessage]

    init(
        current: SuggestedActionsMessage,
        previous: [SuggestedActionsMessage]
    ) {
        self.current = current
        self.previous = Array(
            previous.suffix(SuggestedActionsMessage.previousMessagesLimit)
        )
    }
}
~~~

The framework’s documented limit is a maximum, not a requirement to send a full transcript. Apply the app’s own privacy eligibility policy before creating the projection.

## Recipe 7: Invalidate on edit or delete

~~~swift
import Foundation

@MainActor
final class MessageSuggestionStore {
    private var cacheKeys = Set<SuggestedContextKey>()

    func markGenerated(for message: ChatMessage) {
        cacheKeys.insert(
            SuggestedContextKey(messageID: message.id, revision: message.revision)
        )
    }

    func invalidate(messageID: UUID) {
        cacheKeys.removeAll { $0.messageID == messageID }
    }

    func invalidateAll() {
        cacheKeys.removeAll()
    }
}
~~~

The app-owned store does not clear framework internals directly. It prevents stale app projections and ensures the next render uses the current message revision.

## Recipe 8: Model app-owned receipts

Do not equate a visible suggestion with a completed system action:

~~~swift
enum SuggestedActionReceipt: Equatable, Sendable {
    case notOffered
    case offered
    case selected(destination: String)
    case handedOff(destination: String)
    case completionUnknown(destination: String)
}
~~~

Populate the receipt only from behavior the app can actually observe. If the framework does not expose a completion callback for a destination, use completionUnknown rather than claiming a Calendar event or Reminder exists.

## Recipe 9: Keep normal messaging fallback

~~~swift
import SwiftUI

struct MessageSurface: View {
    let message: ChatMessage
    let suggestedActionsAvailable: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(message.body)

            if suggestedActionsAvailable {
                SuggestedActionsRow(message: message)
            }
        }
    }
}

private struct SuggestedActionsRow: View {
    let message: ChatMessage

    var body: some View {
        SuggestedActionsView(
            message: message.suggestedActionsMessage,
            previousMessages: []
        )
    }
}
~~~

In a real target, gate this with the correct availability/entitlement build state. The conversation must remain complete if the view is unavailable or returns zero size.

## Recipe 10: Redacted input audit

~~~swift
struct SuggestedInputAudit: Sendable {
    let messageID: UUID
    let revision: Int
    let previousCount: Int
    let rawContentIncluded: Bool
    let externalModelUsed: Bool
}

func validate(_ audit: SuggestedInputAudit) throws {
    guard audit.previousCount <= 50 else {
        throw AuditError.contextTooLarge
    }
    guard !audit.rawContentIncluded else {
        throw AuditError.rawContentInAudit
    }
    guard !audit.externalModelUsed else {
        throw AuditError.externalModelNotAllowed
    }
}

enum AuditError: Error {
    case contextTooLarge
    case rawContentInAudit
    case externalModelNotAllowed
}
~~~

The numeric bound in this fixture is an app policy example, not Apple’s framework limit. Use the documented previousMessagesLimit for the actual projection and keep the audit free of message text.

## Recipe 11: AI boundary for custom features

~~~swift
struct AppAIProposal: Sendable {
    let sourceMessageID: UUID
    let proposalText: String
    let requiresReview: Bool
    let canExecuteAutomatically: Bool
}

func validate(_ proposal: AppAIProposal) throws {
    guard proposal.requiresReview else {
        throw AuditError.externalModelNotAllowed
    }
    guard !proposal.canExecuteAutomatically else {
        throw AuditError.externalModelNotAllowed
    }
}
~~~

Suggested Actions is not a custom model prompt. Keep a Foundation Models draft, a Suggested Actions system chip, and an App Intent command as separate surfaces with separate review and proof.

## Recipe 12: Preview fixtures

~~~swift
import Foundation

enum MessageFixtures {
    static let plain = ChatMessage(
        id: UUID(uuidString: "00000000-0000-0000-0000-000000000001")!,
        revision: 1,
        body: "Want to catch up sometime?",
        sentAt: Date(timeIntervalSince1970: 0)
    )

    static let meeting = ChatMessage(
        id: UUID(uuidString: "00000000-0000-0000-0000-000000000002")!,
        revision: 1,
        body: "Meet Tuesday at 3 PM?",
        sentAt: Date(timeIntervalSince1970: 0)
    )
}
~~~

Fixtures can prove layout, text, accessibility, and cache invalidation. They cannot prove that the system generates a suggestion for a given phrase.

## Compile and proof gates

- Confirm the target is a messaging app and the entitlement is signed.
- Verify SuggestedActionsMessage construction in the final SDK.
- Test zero-size no-suggestion layout.
- Test visible suggestion appearance and animation.
- Test generate/cache and cancellation.
- Test edit/delete invalidation.
- Test Calendar, Reminders, and Maps handoff separately.
- Test unavailable entitlement/device/system fallback.
- Audit context size, logs, analytics, screenshots, and external model boundaries.
- Test VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, RTL, keyboard, and pointer.
- Record final beta/release status before distribution.

## Sources

- [Suggested Actions](https://developer.apple.com/documentation/SuggestedActions)
- [SuggestedActionsView](https://developer.apple.com/documentation/suggestedactions/suggestedactionsview)
- [Suggested Actions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.suggested-actions)
- [iOS and iPadOS release notes](https://developer.apple.com/documentation/ios-ipados-release-notes)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

# Interactive App Intent snippet recipes

These are compile-oriented route sketches for the selected iOS 26 SDK. They are not claimed to compile in this documentation-only workspace. Check exact generic result types, availability, target membership, localization, and extension restrictions in Xcode before copying them into an app.

Every recipe assumes:

- the domain service is account-scoped and authorization-aware;
- intent parameters are treated as untrusted input;
- snippet rendering has no domain side effects;
- follow-up App Intents persist idempotently before returning;
- the full app has a manual fallback;
- privacy, accessibility, and system-surface proof are recorded separately.

## Recipe 1: static result

Use this when the person only needs a compact read-only outcome:

~~~swift
import AppIntents
import SwiftUI

struct ShowNextReviewIntent: AppIntent {
    static var title: LocalizedStringResource = "Show next review"
    static var description = IntentDescription(
        "Shows the next item waiting for review."
    )

    func perform() async throws -> some IntentResult {
        let snapshot = try await ReviewStore.shared.nextSnapshot()

        guard let snapshot else {
            return .result(view: Text("Nothing is waiting for review."))
        }

        return .result(
            view: VStack(alignment: .leading) {
                Text(snapshot.title).font(.headline)
                Text(snapshot.statusLabel).font(.subheadline)
            }
        )
    }
}
~~~

This is a static view result. Do not attach a control and assume it has a working system action. Upgrade to Recipe 2 or Recipe 3 when the person needs a follow-up mutation.

## Recipe 2: return a value and a snippet

Keep a value contract for Shortcuts while adding a richer system result:

~~~swift
struct FindNextReviewIntent: AppIntent {
    static var title: LocalizedStringResource = "Find next review"

    func perform() async throws
        -> some ReturnsValue<ReviewEntity> & ShowsSnippetIntent
    {
        let entity = try await ReviewQueries.shared.nextEntity()

        return .result(
            value: entity,
            snippetIntent: ReviewSnippetIntent(reviewID: entity.id)
        )
    }
}
~~~

Use a privacy-filtered AppEntity display representation. Do not return a full private record merely because it is convenient for the value result.

## Recipe 3: re-fetch current state in SnippetIntent

The system may perform this intent repeatedly. Fetch the latest state on every render:

~~~swift
struct ReviewSnippetIntent: SnippetIntent {
    static var title: LocalizedStringResource = "Review details"

    @Parameter var reviewID: String
    @Dependency var store: ReviewStore

    func perform() async throws -> some IntentResult & ShowsSnippetView {
        guard let review = try await store.snapshot(id: reviewID) else {
            return .result(
                view: Text("This review is no longer available.")
            )
        }

        return .result(
            view: ReviewSnippetView(review: review)
        )
    }
}
~~~

The view receives a snapshot, not a live model context. The intent should not mark the review complete merely because it rendered.

## Recipe 4: attach a follow-up action

Use a separate AppIntent for the mutation:

~~~swift
struct MarkReviewCompleteIntent: AppIntent {
    static var title: LocalizedStringResource = "Mark review complete"

    let reviewID: String

    init(reviewID: String) {
        self.reviewID = reviewID
    }

    func perform() async throws -> some IntentResult {
        try await ReviewActions.markCompleteIfNeeded(id: reviewID)
        return .result()
    }
}

struct ReviewSnippetView: View {
    let review: ReviewSnapshot

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(review.title)
                .font(.headline)

            Text(review.statusLabel)
                .font(.subheadline)

            if !review.isComplete {
                Button(
                    "Mark complete",
                    intent: MarkReviewCompleteIntent(reviewID: review.id)
                )
            }
        }
    }
}
~~~

After the action returns, the system can perform ReviewSnippetIntent again. The new snapshot should show completion. The exact Button initializer should be checked in the selected SDK.

## Recipe 5: an interactive toggle

Use a Toggle only for a genuine Boolean domain state:

~~~swift
struct SetReviewPinnedIntent: AppIntent {
    static var title: LocalizedStringResource = "Set review pinned"

    let reviewID: String
    let isPinned: Bool

    init(reviewID: String, isPinned: Bool) {
        self.reviewID = reviewID
        self.isPinned = isPinned
    }

    func perform() async throws -> some IntentResult {
        try await ReviewActions.setPinned(
            id: reviewID,
            isPinned: isPinned
        )
        return .result()
    }
}

struct ReviewPinView: View {
    let review: ReviewSnapshot

    var body: some View {
        Toggle(
            "Pinned",
            isOn: review.isPinned,
            intent: SetReviewPinnedIntent(
                reviewID: review.id,
                isPinned: !review.isPinned
            )
        )
    }
}
~~~

This is a route sketch. Confirm the exact interactive Toggle initializer and whether the snippet surface accepts the control for the selected target. The domain command must tolerate retries and must not flip the value blindly based on a stale snapshot.

## Recipe 6: confirmation with a review snippet

Put irreversible work after confirmation:

~~~swift
struct DeleteDraftIntent: AppIntent {
    static var title: LocalizedStringResource = "Delete draft"

    @Parameter var draftID: String
    @Parameter var deleteAttachments: Bool

    func perform() async throws -> some IntentResult & ShowsSnippetIntent {
        let originalDraftID = draftID
        let originalAttachments = deleteAttachments

        try await requestConfirmation(
            actionName: .delete,
            dialog: IntentDialog("Review this deletion."),
            snippetIntent: DeleteDraftReviewSnippetIntent(
                draftID: originalDraftID,
                deleteAttachments: originalAttachments
            )
        )

        let latestDraftID = draftID
        let latestAttachments = deleteAttachments
        try await DraftActions.delete(
            id: latestDraftID,
            attachments: latestAttachments
        )

        return .result(
            snippetIntent: DeleteResultSnippetIntent(draftID: latestDraftID)
        )
    }
}
~~~

After requestConfirmation returns, read the latest intent properties. The review snippet may have changed them. If the person cancels, the call throws and the deletion code must not run.

## Recipe 7: explicit execution target

Use a target declaration when the action depends on a process-specific service:

~~~swift
struct SaveProtectedNoteIntent: AppIntent {
    static var title: LocalizedStringResource = "Save protected note"
    static var allowedExecutionTargets: IntentExecutionTargets { .main }

    let noteID: String

    init(noteID: String) {
        self.noteID = noteID
    }

    func perform() async throws -> some IntentResult {
        try await ProtectedNoteService.shared.save(id: noteID)
        return .result()
    }
}
~~~

If the action can safely run in an App Intents extension or widget extension, return a combination of documented targets instead. Verify that every linked target contains the same Sendable data and service dependencies. This API is documented as preliminary; inspect the final SDK.

## Recipe 8: reload after external work

Use reload() when a visible snippet’s underlying data changes:

~~~swift
struct StartReviewSearchIntent: AppIntent {
    static var title: LocalizedStringResource = "Search reviews"

    @Parameter var query: String

    func perform() async throws -> some IntentResult & ShowsSnippetIntent {
        let requestID = try await ReviewSearch.shared.start(
            query: query,
            onUpdate: {
                ReviewSearchSnippetIntent.reload()
            }
        )

        return .result(
            snippetIntent: ReviewSearchSnippetIntent(requestID: requestID)
        )
    }
}
~~~

The snippet still needs explicit loading, no-results, timeout, permission, and error states. Do not use reload as a substitute for a durable queue.

## Recipe 9: proposal review before mutation

Keep on-device AI at the proposal layer:

~~~swift
struct ProposeReviewLabelIntent: AppIntent {
    static var title: LocalizedStringResource = "Suggest a review label"

    let reviewID: String

    init(reviewID: String) {
        self.reviewID = reviewID
    }

    func perform() async throws -> some IntentResult & ShowsSnippetIntent {
        let source = try await ReviewStore.shared.sourceText(id: reviewID)
        let proposal = try await LocalLabelModel.shared.propose(
            source: source
        )

        try await ProposalStore.shared.save(
            reviewID: reviewID,
            value: proposal.value,
            sourceIDs: proposal.sourceIDs,
            modelRevision: proposal.modelRevision,
            status: .needsReview
        )

        return .result(
            snippetIntent: LabelProposalSnippetIntent(reviewID: reviewID)
        )
    }
}

struct AcceptReviewLabelIntent: AppIntent {
    static var title: LocalizedStringResource = "Accept review label"

    let reviewID: String

    init(reviewID: String) {
        self.reviewID = reviewID
    }

    func perform() async throws -> some IntentResult {
        let proposal = try await ProposalStore.shared.current(id: reviewID)
        try await ReviewActions.accept(
            id: reviewID,
            value: proposal.value
        )
        return .result()
    }
}
~~~

The proposal is typed, stored with provenance, and accepted through a separate action. If the model is unavailable, offer a manual label route. Never turn proposal text directly into a destructive command or authorization decision.

## Recipe 10: testable fake dependency

Inject a small dependency so repeated rendering and mutation can be tested without a system surface:

~~~swift
actor FakeReviewStore {
    var snapshots: [String: ReviewSnapshot] = [:]

    func snapshot(id: String) -> ReviewSnapshot? {
        snapshots[id]
    }

    func markComplete(id: String) {
        guard var snapshot = snapshots[id] else { return }
        snapshot.isComplete = true
        snapshots[id] = snapshot
    }
}
~~~

Test the sequence rather than only the initial view:

~~~text
seed incomplete snapshot
perform SnippetIntent -> incomplete view
perform follow-up AppIntent
perform SnippetIntent again -> complete view
repeat follow-up -> no duplicate side effect
delete record
perform SnippetIntent -> unavailable view
~~~

## Copy and accessibility checklist

- Use localized titles and action labels.
- Expose the object, current state, and next action in that order.
- Give icon-only actions an accessible label.
- Keep a visible text fallback for model or network failure.
- Test Dynamic Type, VoiceOver, Voice Control, Switch Control, reduced motion, and reduced transparency.
- Avoid private source text in parameter summaries, spoken dialogs, and system projections.
- Do not claim a system surface, device family, or Apple Intelligence route until it is verified.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Displaying static and interactive snippets](https://developer.apple.com/documentation/appintents/displaying-static-and-interactive-snippets)
- [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent)
- [ShowsSnippetIntent](https://developer.apple.com/documentation/appintents/showssnippetintent)
- [ShowsSnippetView](https://developer.apple.com/documentation/appintents/showssnippetview)
- [IntentResult result(value:snippetIntent:)](https://developer.apple.com/documentation/appintents/intentresult/result%28value%3Asnippetintent%3A%29)
- [IntentResult result(snippetIntent:)](https://developer.apple.com/documentation/appintents/intentresult/result%28snippetintent%3A%29)
- [SnippetIntent.reload()](https://developer.apple.com/documentation/appintents/snippetintent/reload%28%29)
- [AppIntent requestConfirmation with a snippet](https://developer.apple.com/documentation/appintents/appintent/requestconfirmation%28conditions%3Aactionname%3Adialog%3Ashowdialogasprompt%3Asnippetintent%3A%29-jxb8)
- [IntentExecutionTargets](https://developer.apple.com/documentation/appintents/intentexecutiontargets)
- [AppIntent.isDiscoverable](https://developer.apple.com/documentation/appintents/appintent/isdiscoverable)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Button](https://developer.apple.com/documentation/swiftui/button)
- [Toggle](https://developer.apple.com/documentation/swiftui/toggle)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

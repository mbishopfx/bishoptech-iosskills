# Journaling Suggestions Recipes

These are compile-oriented SwiftUI route sketches for Journaling Suggestions: a person-controlled picker, selected-content projection, a private on-device drafting seam, notification deep links, schedule status, and a restrained Liquid Glass review surface. They are not compiled in this documentation-only workspace and do not prove entitlement approval, system picker behavior, personal suggestions, notification delivery, on-device model execution, or release eligibility.

Before copying:

1. Confirm the target is a writing or other creative-workflow app that benefits from selected moments.
2. Enable the Journaling Suggestions capability and verify the signed com.apple.developer.journal.allow entitlement.
3. Confirm the final SDK’s availability and the current SwiftUI modifier signatures in Xcode.
4. Treat JournalingSuggestion as system-provided input, not as an object the app can construct for arbitrary personal data.
5. Use synthetic SelectedMoment projections for previews and unit tests; use a physical device for the picker and notification route.
6. Keep the person’s selection, review, edit, save, and delete actions explicit.

## Recipe 1: Keep the app-owned entry separate from the system suggestion

The system completion returns a JournalingSuggestion. Give the app-owned draft its own identity and lifecycle:

~~~swift
import Foundation

struct JournalEntryDraft: Identifiable, Equatable, Sendable {
    let id: UUID
    var title: String
    var body: String
    var selectedMoment: SelectedMoment?
    var status: Status

    enum Status: Equatable, Sendable {
        case empty
        case contextSelected
        case draftReady
        case saved
    }
}

struct SelectedMoment: Equatable, Sendable {
    let title: String
    let date: DateInterval?
    let photoCount: Int
    let contentKinds: [String]
}
~~~

Do not use the notification identifier or a JournalingSuggestion hash as the journal entry ID. The entry is app-owned and should remain stable if the person edits or removes its selected context.

## Recipe 2: Present the system picker with an expectation-setting label

Apple’s documented initializers accept a localized title or a custom label. The title should tell the person that personal moments will appear:

~~~swift
import JournalingSuggestions
import SwiftUI

struct ChooseMomentButton: View {
    let accept: @MainActor (JournalingSuggestion) async -> Void

    var body: some View {
        JournalingSuggestionsPicker("Choose a moment to write about") { suggestion in
            await accept(suggestion)
        }
    }
}
~~~

The completion closure is asynchronous. Dismissal without a selection is a normal path; do not create an empty entry merely because the picker was presented.

## Recipe 3: Project only the selected content needed by the editor

JournalingSuggestion exposes high-level details and an asynchronous content(forType:) lookup. Project the smallest useful representation before handing data to an editor or model:

~~~swift
import JournalingSuggestions

struct SelectedMomentProjector {
    func project(
        _ suggestion: JournalingSuggestion
    ) async -> SelectedMoment {
        let photos = await suggestion.content(
            forType: JournalingSuggestion.Photo.self
        )

        var kinds = ["suggestion"]
        if !photos.isEmpty {
            kinds.append("photo")
        }

        return SelectedMoment(
            title: suggestion.title,
            date: suggestion.date,
            photoCount: photos.count,
            contentKinds: kinds
        )
    }
}
~~~

For a real media surface, inspect the current SDK’s asset fields and load only the selected asset needed by the entry. The list of supported content types includes photos, Live Photos, video, locations, contacts, workouts, motion activity, media, reflections, state of mind, and event posters; availability and field details must be checked against the selected SDK.

## Recipe 4: Make selection, projection, review, and save observable

Use a small state machine so a system selection never silently becomes a saved journal entry:

~~~swift
import JournalingSuggestions
import SwiftUI

@MainActor
final class JournalEntryModel: ObservableObject {
    @Published var draft = JournalEntryDraft(
        id: UUID(),
        title: "",
        body: "",
        selectedMoment: nil,
        status: .empty
    )

    private let projector = SelectedMomentProjector()

    func accept(_ suggestion: JournalingSuggestion) async {
        let moment = await projector.project(suggestion)
        draft.selectedMoment = moment
        draft.status = .contextSelected
    }

    func save() {
        guard draft.status == .draftReady || draft.status == .contextSelected else {
            return
        }
        // Persist only after the person has reviewed the entry.
        draft.status = .saved
    }

    func removeSelectedMoment() {
        draft.selectedMoment = nil
        draft.status = draft.body.isEmpty ? .empty : .draftReady
    }
}
~~~

If the selected data is deleted, unavailable, or incomplete, keep the writing surface usable and ask the person to add the missing context. Do not describe absence of a supported asset as absence of a life event.

## Recipe 5: Put a typed on-device drafting seam after review

Keep Apple’s model framework behind an app-owned protocol. This prevents an AI implementation detail from becoming the privacy contract:

~~~swift
struct JournalDraftInput: Sendable {
    let title: String
    let dateSummary: String?
    let contentKinds: [String]
    let photoCount: Int
    let personNotes: String
}

struct JournalDraftOutput: Sendable {
    let title: String
    let body: String
    let modelLabel: String
}

protocol JournalDrafting: Sendable {
    func makeDraft(
        from input: JournalDraftInput
    ) async throws -> JournalDraftOutput
}

struct DeterministicJournalDrafting: JournalDrafting {
    func makeDraft(
        from input: JournalDraftInput
    ) async throws -> JournalDraftOutput {
        let title = input.title.isEmpty ? "A moment to remember" : input.title
        let body = input.personNotes.isEmpty
            ? "You selected \(title). Add what you remember."
            : input.personNotes

        return JournalDraftOutput(
            title: title,
            body: body,
            modelLabel: "deterministic-fallback"
        )
    }
}
~~~

An implementation backed by Foundation Models or another approved on-device route must separately prove model availability, device behavior, input minimization, cancellation, and no external upload. A local model label in UI is not proof of local execution.

## Recipe 6: Handle a notification URL without treating it as content

If the target opts into Journaling Suggestions notifications, configure JSNotificationURLFormat as a universal link and parse only the expected identifier:

~~~swift
import JournalingSuggestions
import SwiftUI

@MainActor
final class JournalingNotificationModel: ObservableObject {
    @Published var isPickerPresented = false
    @Published var token: JournalingSuggestionPresentationToken?

    func handle(_ url: URL) {
        guard let components = URLComponents(
            url: url,
            resolvingAgainstBaseURL: false
        ) else {
            return
        }

        let value = components.queryItems?
            .first(where: { $0.name == "suggestion-identifier" })?
            .value

        guard let value, let identifier = UUID(uuidString: value) else {
            // A general reminder may have no identifier. Open a normal picker.
            token = nil
            isPickerPresented = true
            return
        }

        token = JournalingSuggestionPresentationToken(
            suggestionIdentifier: identifier
        )
        isPickerPresented = true
    }
}

struct JournalEntryRoot: View {
    @StateObject private var notificationModel = JournalingNotificationModel()
    let accept: @MainActor (JournalingSuggestion) async -> Void

    var body: some View {
        EntryEditor()
            .onOpenURL { url in
                notificationModel.handle(url)
            }
            .journalingSuggestionsPicker(
                isPresented: $notificationModel.isPickerPresented,
                journalingSuggestionToken: notificationModel.token,
                onCompletion: { suggestion in
                    await accept(suggestion)
                }
            )
    }
}
~~~

The URL is a route token. Validate the scheme, host, path, and expected query name for the actual app, reject unexpected links, and avoid logging the raw URL. A tapped notification with a specific moment should open the picker prepopulated with the token; a general reminder should fall back to a normal picker.

## Recipe 7: Show notification status without inventing a setting

JournalingSuggestionsConfiguration reports the system’s read-only schedule state:

~~~swift
import JournalingSuggestions
import SwiftUI

struct JournalingNotificationStatus: View {
    private let schedule = JournalingSuggestionsConfiguration()
        .notificationSchedule

    var body: some View {
        switch schedule {
        case .smart:
            Label("Journaling reminders use a smart schedule", systemImage: "sparkles")
        case .custom:
            Label("Journaling reminders use a custom schedule", systemImage: "calendar")
        case .off:
            Label("Journaling reminders are off", systemImage: "bell.slash")
        case .none:
            Label("Journaling reminder status unavailable", systemImage: "questionmark")
        }
    }
}
~~~

The off state can mean that Journaling Suggestions, notifications, preferred-app selection, or notification setup is incomplete. Link to an explanation or Settings guidance instead of promising that turning on one local toggle will enable every route.

## Recipe 8: Use Liquid Glass only for the app-owned review layer

The picker remains system-owned. Use Liquid Glass for the editor’s selected-context summary and action group, then verify the exact modifier signature in the final SDK:

~~~swift
import SwiftUI

struct MomentReviewSurface: View {
    let moment: SelectedMoment
    let remove: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(moment.title, systemImage: "book.pages")
                .font(.headline)

            Text("\(moment.photoCount) selected photo(s)")
                .foregroundStyle(.secondary)

            HStack {
                Button("Choose another moment") {
                    // Present the system picker from the surrounding editor.
                }
                .buttonStyle(.bordered)

                Button("Remove context", role: .destructive, action: remove)
            }
        }
        .padding()
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
    }
}
~~~

Keep the editor hierarchy readable when Liquid Glass is unavailable, Reduce Transparency is enabled, text is enlarged, or the selected context has no image. Do not recreate the system consent sheet or use a glass card to imply continuous access.

## Recipe 9: Build redacted fixtures instead of fake system suggestions

The app should not invent JournalingSuggestion instances. Test the projection and editor with app-owned fixtures:

~~~swift
let fixture = SelectedMoment(
    title: "Coastal walk",
    date: DateInterval(
        start: Date(timeIntervalSince1970: 1_750_000_000),
        duration: 3_600
    ),
    photoCount: 2,
    contentKinds: ["suggestion", "photo", "location"]
)

let missingAssetFixture = SelectedMoment(
    title: "A moment to remember",
    date: nil,
    photoCount: 0,
    contentKinds: ["suggestion"]
)
~~~

Use real system selections only in a controlled physical-device test account or consented fixture. Keep screenshot and log evidence redacted, especially for contacts, locations, workouts, state of mind, and media.

## Recipe 10: Use a release and proof gate

Record these independently:

- target membership, final SDK, deployment target, and signed com.apple.developer.journal.allow;
- picker presentation on a physical iPhone and, where supported, iPad;
- dismissal, selection, supported-content projection, missing-content, deletion, and backgrounding;
- JSNotificationURLFormat, associated domains, cold launch, warm onOpenURL, UUID token, and general reminder behavior;
- notification schedule states from Settings and JournalingSuggestionsConfiguration;
- AI model availability, redacted input audit, cancellation, fallback, and external-upload audit;
- VoiceOver, Dynamic Type, Voice Control, Switch Control, Reduce Motion, Reduce Transparency, RTL, and iPad layout;
- final signed artifact and the exact device/system surfaces claimed in release copy.

Documentation, a preview, a simulator run, or a successful compile proves none of the system picker, personal-context, notification, on-device-model, or release claims by itself.

## Sources

- [Journaling Suggestions](https://developer.apple.com/documentation/journalingsuggestions)
- [Presenting the suggestions picker and processing a selection](https://developer.apple.com/documentation/journalingsuggestions/presenting-the-suggestions-picker-and-processing-a-selection)
- [JournalingSuggestion](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestion)
- [JournalingSuggestionsPicker](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionspicker)
- [JournalingSuggestionPresentationToken](https://developer.apple.com/documentation/JournalingSuggestions/JournalingSuggestionPresentationToken)
- [SwiftUI technology-specific modifiers](https://developer.apple.com/documentation/swiftui/view-technology-modifiers)
- [Receiving journaling suggestions system notifications](https://developer.apple.com/documentation/journalingsuggestions/receiving-journaling-suggestions-from-system-notifications)
- [JSNotificationURLFormat](https://developer.apple.com/documentation/bundleresources/information-property-list/jsnotificationurlformat)
- [JournalingSuggestionsConfiguration](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionsconfiguration)
- [Journaling Suggestions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.journal.allow)
- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

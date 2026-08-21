# SwiftUI accessibility and alternate-input recipes

## How to use these recipes

These are small, compile-oriented SwiftUI sketches for native iOS work. They
show the relationship between standard controls, semantics, focus, rotors,
Dynamic Type, Liquid Glass, keyboard/pointer input, drag/drop, App Intents,
and on-device AI review.

Compile every recipe in the named target with the selected Xcode/SDK and
deployment target. SwiftUI overloads and availability can differ across
platforms and SDKs. The snippets prove an implementation shape, not physical
VoiceOver, Voice Control, Switch Control, App Intent, or release behavior.

Related pages:

- [SwiftUI accessibility and alternate input](../42-framework-deep-dives/80-swiftui-accessibility-and-alternate-input.md)
- [Accessibility and alternate-input design](../21-design-deep-dives/108-accessibility-and-alternate-input-design.md)
- [SwiftUI accessibility and input route](../50-capability-recipes/111-swiftui-accessibility-input-route.md)
- [SwiftUI accessibility and input proof matrix](../60-verification/105-swiftui-accessibility-input-proof-matrix.md)

## Recipe 1: semantic glass button

Make the Button own the label and action. The glass effect is only the visual
treatment.

~~~swift
import SwiftUI

struct GlassActionButton: View {
    let title: LocalizedStringKey
    let systemImage: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(title, systemImage: systemImage)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
        }
        .buttonStyle(.plain)
        .glassEffect(.regular.interactive(), in: .capsule)
        .accessibilityHint("Performs the primary action")
    }
}
~~~

Test the button in light/dark appearance, Increase Contrast, Reduce
Transparency, Dynamic Type, VoiceOver, and Voice Control. If the button has
selected or disabled state, expose that state through the standard control and
an accessible value or trait; do not rely on tint alone.

## Recipe 2: combine a read-only card without swallowing actions

Combine the content of an atomic read-only card. Keep independent actions
outside the combined element.

~~~swift
struct SummaryCard: View {
    let title: String
    let detail: String
    let isPinned: Bool
    let pin: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(detail)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityValue(isPinned ? "Pinned" : "Not pinned")

            Button(action: pin) {
                Image(systemName: isPinned ? "pin.fill" : "pin")
            }
            .accessibilityLabel(isPinned ? "Unpin" : "Pin")
        }
        .padding()
    }
}
~~~

Do not use children-combine on a region containing several independent
controls. Inspect the tree after adding the modifier.

## Recipe 3: focus the first actionable form error

Use one typed FocusState for editing and a separate AccessibilityFocusState for
VoiceOver. The domain validation remains independent.

~~~swift
struct ProfileForm: View {
    enum Field: Hashable {
        case name
        case email
    }

    enum AccessibilityTarget: Hashable {
        case heading
        case name
        case email
        case error
    }

    @State private var name = ""
    @State private var email = ""
    @State private var errorText: String?
    @FocusState private var focusedField: Field?
    @AccessibilityFocusState private var accessibilityFocus: AccessibilityTarget?

    var body: some View {
        Form {
            Text("Profile")
                .font(.title)
                .accessibilityHeading(.h1)
                .accessibilityFocused(
                    $accessibilityFocus,
                    equals: .heading
                )

            TextField("Name", text: $name)
                .focused($focusedField, equals: .name)
                .accessibilityIdentifier("profile.name")

            TextField("Email", text: $email)
                .textInputAutocapitalization(.never)
                .keyboardType(.emailAddress)
                .focused($focusedField, equals: .email)
                .accessibilityIdentifier("profile.email")

            if let errorText {
                Text(errorText)
                    .foregroundStyle(.red)
                    .accessibilityValue(errorText)
                    .accessibilityFocused(
                        $accessibilityFocus,
                        equals: .error
                    )
            }

            Button("Save") {
                if name.isEmpty {
                    errorText = "Enter a name."
                    focusedField = .name
                    accessibilityFocus = .error
                } else if email.isEmpty {
                    errorText = "Enter an email address."
                    focusedField = .email
                    accessibilityFocus = .error
                } else {
                    errorText = nil
                    save()
                }
            }
        }
        .accessibilityDefaultFocus($accessibilityFocus, .heading)
    }

    private func save() {
        // Call the domain authority; do not treat focus movement as a save.
    }
}
~~~

The exact default-focus availability should be compiled against the target SDK.
Test with VoiceOver on a physical device and with the keyboard attached.

## Recipe 4: a custom rotor with stable IDs

Use a custom rotor for a meaningful subset of a long or lazy collection. The
entry initializer and overload should be confirmed in the selected SDK; the
important rules are stable IDs, concise labels, and attachment to the intended
focusable element.

~~~swift
struct Review: Identifiable, Hashable {
    let id: UUID
    let title: String
}

struct ReviewList: View {
    let reviews: [Review]

    var body: some View {
        List(reviews) { review in
            NavigationLink(value: review.id) {
                Text(review.title)
                    .accessibilityRotorEntry(
                        id: review.id,
                        in: rotorNamespace
                    )
            }
        }
        .accessibilityRotor("Pending reviews", entries: reviews) { review in
            AccessibilityRotorEntry(
                review.title,
                id: review.id
            )
        }
    }

    @Namespace private var rotorNamespace
}
~~~

If the SDK’s overload uses an entry-label closure rather than an
AccessibilityRotorEntry initializer, adapt the syntax to that official
signature. Do not replace the rotor with sort priority, and do not use an
array offset as the entry identity.

## Recipe 5: link separated semantic elements

Link a heading and a distant status/action cluster only when the relationship
helps VoiceOver navigation.

~~~swift
struct ReviewHeaderAndActions: View {
    let reviewID: UUID
    @Namespace private var semanticNamespace

    var body: some View {
        VStack(alignment: .leading) {
            Text("Review \(reviewID.uuidString)")
                .font(.title2)
                .accessibilityHeading(.h2)
                .accessibilityLinkedGroup(
                    id: reviewID,
                    in: semanticNamespace
                )

            Spacer(minLength: 180)

            HStack {
                Text("3 changes pending")
                    .accessibilityValue("3 changes pending")
                    .accessibilityLinkedGroup(
                        id: reviewID,
                        in: semanticNamespace
                    )

                Button("Accept") {
                    accept()
                }
                .accessibilityLinkedGroup(
                    id: reviewID,
                    in: semanticNamespace
                )
            }
        }
    }

    private func accept() {
        // Validate current revision and commit through the domain layer.
    }
}
~~~

Keep the default order understandable if the linked group is unavailable or
not selected by the person.

## Recipe 6: Dynamic Type and compact-control support

Let text grow before adding special size branches. Use the Large Content Viewer
only for an unavoidable compact control.

~~~swift
struct AdaptiveToolbar: View {
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack {
                Text("Review changes")
                Button("Accept", action: accept)
            }

            VStack(alignment: .leading) {
                Text("Review changes")
                Button("Accept", action: accept)
            }
        }
        .padding()
        .accessibilityShowsLargeContentViewer()
    }

    private func accept() {
        // Commit after validation.
    }
}
~~~

The Large Content Viewer is not a replacement for Dynamic Type. Include long
labels, largest supported accessibility size, localization, and a visible
primary action in the fixture.

## Recipe 7: Liquid Glass fallback for accessibility settings

The standard components adapt automatically. For a custom functional surface,
use the environment values to select a less translucent or less animated
presentation while preserving the same semantic control.

~~~swift
struct AdaptiveGlassPanel<Content: View>: View {
    @Environment(\.accessibilityReduceTransparency)
    private var reduceTransparency
    @Environment(\.accessibilityReduceMotion)
    private var reduceMotion
    @ViewBuilder let content: () -> Content

    var body: some View {
        content()
            .padding()
            .background {
                if reduceTransparency {
                    RoundedRectangle(cornerRadius: 24)
                        .fill(.thickMaterial)
                } else {
                    RoundedRectangle(cornerRadius: 24)
                        .fill(.clear)
                        .glassEffect(.regular, in: .rect(cornerRadius: 24))
                }
            }
            .transaction { transaction in
                if reduceMotion {
                    transaction.animation = nil
                }
            }
    }
}
~~~

Do not assume a custom environment branch reproduces every system Liquid Glass
adaptation. Test the actual device setting, contrast, content background, and
animation behavior.

## Recipe 8: keyboard focus and key phases

Use FocusState for fields and keyboard shortcuts for commands. Use onKeyPress
only for a focused custom interaction that owns the event.

~~~swift
struct SearchSurface: View {
    @FocusState private var isSearchFocused: Bool
    @State private var query = ""

    var body: some View {
        VStack {
            TextField("Search", text: $query)
                .focused($isSearchFocused)
                .submitLabel(.search)
                .onSubmit(search)

            Button("Clear", action: clear)
                .keyboardShortcut("k", modifiers: [.command])
        }
        .onKeyPress(.escape) {
            isSearchFocused = false
            return .handled
        }
    }

    private func search() {
        // Run the search domain action.
    }

    private func clear() {
        query = ""
    }
}
~~~

Compile the chosen onKeyPress overload. Preserve system keyboard conventions,
and keep the text field/button actions available to VoiceOver and Full Keyboard
Access.

## Recipe 9: pointer and hover feedback

Hover is an additive visual response. Do not hide the core action behind it.

~~~swift
struct HoverableGlassCard: View {
    @State private var isHovering = false

    var body: some View {
        Button("Open summary") {
            open()
        }
        .padding()
        .background {
            RoundedRectangle(cornerRadius: 20)
                .fill(isHovering ? .regularMaterial : .thinMaterial)
        }
        .hoverEffect(.highlight)
        .onHover { inside in
            isHovering = inside
        }
        .accessibilityInputLabels(["Open summary", "Summary"])
    }

    private func open() {
        // Navigate using the typed route.
    }
}
~~~

Test touch without a pointer, Voice Control, VoiceOver, and Switch Control.
The label, action, and focus route must not depend on isHovering.

## Recipe 10: Transferable drag/drop with a visible alternative

Keep the payload narrow, validate it at the destination, and expose a button
or action for people who cannot or do not want to drag.

~~~swift
import SwiftUI
import UniformTypeIdentifiers

struct ReviewTransfer: Codable, Hashable, Transferable {
    let reviewID: UUID

    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .data)
    }
}

struct ReviewDropZone: View {
    let reviewID: UUID
    @State private var isTargeted = false

    var body: some View {
        VStack {
            Text("Move to archive")

            Button("Archive without dragging") {
                archive(reviewID)
            }
        }
        .padding()
        .background(isTargeted ? .blue.opacity(0.2) : .clear)
        .dropDestination(
            for: ReviewTransfer.self,
            action: { transfers, _ in
                guard let transfer = transfers.first else {
                    return false
                }
                archive(transfer.reviewID)
                return true
            },
            isTargeted: { targeted in
                isTargeted = targeted
            }
        )
        .accessibilityValue(isTargeted ? "Drop target active" : "Drop target")
    }

    private func archive(_ id: UUID) {
        // Validate current identity and commit once.
    }
}
~~~

For custom geometry, add accessibilityDragPoint and accessibilityDropPoint
descriptions when the default locations are not sufficient. Test invalid,
duplicate, canceled, and cross-app payloads separately.

## Recipe 11: one domain command for visible and accessible actions

Use the same domain authority for the visible control, accessible action,
keyboard shortcut, and App Intent.

~~~swift
import AppIntents
import SwiftUI

struct SaveReviewIntent: AppIntent {
    static let title: LocalizedStringResource = "Save review"

    let reviewID: UUID

    func perform() async throws -> some IntentResult {
        try await ReviewCommands.save(reviewID: reviewID)
        return .result()
    }
}

struct ReviewCommands {
    static func save(reviewID: UUID) async throws {
        // Re-read the current review, validate authorization and revision,
        // then perform the durable write.
    }
}

struct ReviewActions: View {
    let reviewID: UUID

    var body: some View {
        Button("Save") {
            Task {
                try? await ReviewCommands.save(reviewID: reviewID)
            }
        }
        .accessibilityAction(
            intent: SaveReviewIntent(reviewID: reviewID)
        ) {
            Text("Save review")
        }
        .keyboardShortcut(.defaultAction)
    }
}
~~~

The exact App Intent initializer and accessibilityAction overload should be
compiled against the current SDK. If an intent is not appropriate, use a
named accessibility action that calls the same command directly.

## Recipe 12: accessible AI review status

Keep candidate output separate from saved state. Use a concise accessible value
and explicit controls.

~~~swift
enum ReviewState: Equatable {
    case unavailable(reason: String)
    case generating
    case proposal(text: String)
    case applying
    case saved
    case failed(reason: String)
}

struct AIReviewSurface: View {
    let state: ReviewState
    let accept: () -> Void
    let cancel: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Review suggestion")
                .font(.title2)
                .accessibilityHeading(.h2)

            Text(statusText)
                .accessibilityValue(statusText)

            switch state {
            case .unavailable, .failed:
                Button("Continue manually") {
                    // Use the manual path.
                }
            case .generating:
                Button("Cancel", action: cancel)
            case .proposal(let text):
                TextEditor(text: .constant(text))
                    .accessibilityLabel("Suggested text")
                HStack {
                    Button("Accept", action: accept)
                    Button("Edit manually") {
                        // Move to the manual editing route.
                    }
                }
            case .applying:
                ProgressView("Applying")
            case .saved:
                Label("Saved", systemImage: "checkmark")
            }
        }
        .accessibilityElement(children: .contain)
    }

    private var statusText: String {
        switch state {
        case .unavailable(let reason):
            return "Suggestions unavailable. \(reason)"
        case .generating:
            return "Generating a suggestion"
        case .proposal:
            return "Suggestion ready for review"
        case .applying:
            return "Applying reviewed suggestion"
        case .saved:
            return "Suggestion saved"
        case .failed(let reason):
            return "Suggestion failed. \(reason)"
        }
    }
}
~~~

Do not stream each token into VoiceOver focus. If the state enters a new task,
focus the heading or a stable status target once. The manual route must remain
available when the device or model cannot perform the request.

## Recipe 13: accessibility-aware preview fixtures

Previews help expose layout problems early. They do not replace physical
device runs.

~~~swift
#Preview("Largest text") {
    ReviewActions(reviewID: UUID())
        .environment(\.dynamicTypeSize, .accessibility5)
}

#Preview("Reduced transparency") {
    AdaptiveGlassPanel {
        Text("Readable glass fallback")
    }
    .environment(\.accessibilityReduceTransparency, true)
}

#Preview("Reduced motion") {
    AdaptiveGlassPanel {
        Text("Static transition route")
    }
    .environment(\.accessibilityReduceMotion, true)
}
~~~

Add fixture previews for empty, loading, error, long localization, and
proposal states. Where a system environment cannot be safely overridden in a
preview, verify it with Accessibility Inspector or device settings.

## Recipe 14: UI test and audit boundary

Use UI tests to query the exposed accessibility contract. Keep audit APIs
version-checked because XCTest/XCUITest signatures may change with the SDK.

~~~swift
import XCTest

final class ReviewAccessibilityTests: XCTestCase {
    func testReviewActionsExposeLabels() throws {
        let app = XCUIApplication()
        app.launchArguments = ["-fixture", "proposal"]
        app.launch()

        XCTAssertTrue(app.buttons["Accept"].waitForExistence(timeout: 2))
        XCTAssertEqual(app.buttons["Accept"].label, "Accept")
        XCTAssertTrue(app.buttons["Edit manually"].exists)

        // Compile the current audit signature in the selected SDK.
        try app.performAccessibilityAudit(for: .all)
    }
}
~~~

This proves inspectable UI attributes and audit output. It does not prove a
human can complete the task with VoiceOver, Voice Control, or Switch Control.

## Recipe 15: route checklist

Use this before calling a feature accessible:

    [ ] Standard control selected where possible
    [ ] Visible title and localized accessibility label
    [ ] Current value/status is exposed
    [ ] Independent actions are not flattened
    [ ] Decorative glass is hidden
    [ ] Initial/failure/result focus policy is explicit
    [ ] Rotor/linked group has a traversal reason
    [ ] Dynamic Type reflows large text
    [ ] Color is not the only state channel
    [ ] Reduce Transparency has an opaque/material fallback
    [ ] Reduce Motion preserves task meaning
    [ ] Voice Control has natural names
    [ ] Switch Control has no timing-only task
    [ ] Keyboard/pointer behavior is additive
    [ ] Drag/drop has a visible and accessible alternative
    [ ] App Intent shares domain validation
    [ ] AI candidate is separate from saved state
    [ ] UI tests and Accessibility Inspector run
    [ ] Physical-device assistive technology run is recorded

## Sources

- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessible navigation](https://developer.apple.com/documentation/swiftui/accessible-navigation)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events/)
- [onKeyPress(_:action:)](https://developer.apple.com/documentation/swiftui/view/onkeypress%28_%3Aaction%3A%29)
- [HoverEffect](https://developer.apple.com/documentation/swiftui/hovereffect)
- [onHover(perform:)](https://developer.apple.com/documentation/swiftui/view/onhover%28perform%3A%29)
- [Adopting drag and drop using SwiftUI](https://developer.apple.com/documentation/swiftui/adopting-drag-and-drop-using-swiftui)
- [Making a view into a drag source](https://developer.apple.com/documentation/swiftui/making-a-view-into-a-drag-source)
- [draggable(_:)](https://developer.apple.com/documentation/swiftui/view/draggable%28_%3A%29)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityShowsLargeContentViewer()](https://developer.apple.com/documentation/swiftui/view/accessibilityshowslargecontentviewer%28%29)
- [accessibilityDifferentiateWithoutColor](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydifferentiatewithoutcolor)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [ContentShapeKinds](https://developer.apple.com/documentation/swiftui/contentshapekinds)
- [Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures)
- [Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [App intents](https://developer.apple.com/documentation/appintents/app-intents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Accessibility Inspector](https://developer.apple.com/documentation/accessibility/accessibility-inspector)
- [XCUIAccessibilityAuditType](https://developer.apple.com/documentation/xcuiautomation/xcuiaccessibilityaudittype)
- [XCUIApplication.performAccessibilityAudit(for:_:)](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/performaccessibilityaudit%28for%3A_%3A%29)

# Swift Testing, XCTest, UI automation, and proof recipes

## How to use these sketches

These snippets are compile-oriented route sketches. Add them to a named test
target, adapt APIs to the selected SDK, and keep the evidence record beside the
result. The route is designed to work with the [capability recipe](../50-capability-recipes/105-swift-testing-xctest-and-ui-proof-route.md),
the [proof matrix](../60-verification/99-swift-testing-xctest-ui-proof-matrix.md),
and the [testable design contract](../21-design-deep-dives/102-testable-native-design-and-ai-evaluation.md).

The examples intentionally use injected state and semantic boundaries. They do
not claim to compile in this documentation-only workspace.

## Swift Testing: a deterministic reducer

Keep pure state transitions easy to exercise:

~~~swift
import Testing

struct ReviewState: Equatable {
    var title: String
    var isDirty = false
    var error: String?
}

enum ReviewIntent {
    case editTitle(String)
    case rejectSuggestion
}

func reduce(_ state: ReviewState, _ intent: ReviewIntent) -> ReviewState {
    var next = state
    switch intent {
    case .editTitle(let title):
        next.title = title
        next.isDirty = true
        next.error = nil
    case .rejectSuggestion:
        next.isDirty = false
        next.error = nil
    }
    return next
}

@Suite("Review reducer")
struct ReviewReducerTests {
    @Test("Editing a title creates a reviewable change")
    func editingCreatesChange() {
        let state = ReviewState(title: "Original")
        let next = reduce(state, .editTitle("Corrected"))

        #expect(next.title == "Corrected")
        #expect(next.isDirty)
        #expect(next.error == nil)
    }

    @Test("The state matrix stays explicit", arguments: [
        ("Original", "Corrected"),
        ("", "A title"),
        ("Long title", "")
    ])
    func titleCases(original: String, edited: String) {
        let next = reduce(
            ReviewState(title: original),
            .editTitle(edited)
        )
        #expect(next.title == edited)
        #expect(next.isDirty)
    }
}
~~~

In a real target, decide whether empty titles are allowed in the domain
validator. The test should express the product policy rather than merely mirror
the implementation.

## Swift Testing: async cancellation and confirmation

Use a fake service that exposes a bounded event and cancellation path:

~~~swift
import Testing

struct ReviewEvent: Sendable, Equatable {
    let id: String
}

actor FakeReviewStream {
    private var continuation: AsyncStream<ReviewEvent>.Continuation?

    func events() -> AsyncStream<ReviewEvent> {
        AsyncStream { continuation in
            self.continuation = continuation
        }
    }

    func send(_ event: ReviewEvent) {
        continuation?.yield(event)
    }

    func finish() {
        continuation?.finish()
    }
}

@Test("A review event is observed exactly once")
func observesEvent() async {
    let stream = FakeReviewStream()
    let events = await stream.events()

    await confirmation(expectedCount: 1) { confirmation in
        let task = Task {
            for await event in events {
                if event.id == "review-1" {
                    confirmation()
                    break
                }
            }
        }

        await stream.send(ReviewEvent(id: "review-1"))
        _ = await task.result
    }
}
~~~

For production code, also test expectedCount 0 for a canceled or unauthorized
operation. Keep task ownership explicit so a callback cannot outlive its test
fixture.

## Swift Testing: tags and serialization

Use tags for test-plan routing and serialized only for a real shared resource:

~~~swift
import Testing

extension Tag {
    @Tag static var accessibility: Self
    @Tag static var aiEvaluation: Self
}

@Suite(.tags(.accessibility))
struct AccessibilityStateTests {
    @Test(.tags(.aiEvaluation))
    func proposalHasReviewableFields() {
        let fields = ["title", "source"]
        #expect(fields.contains("title"))
        #expect(fields.contains("source"))
    }
}

@Suite(.serialized)
struct SharedStoreTests {
    @Test func migratesOneFixtureAtATime() {
        // Use only when this suite owns a shared on-disk fixture.
    }
}
~~~

Prefer a separate temporary store per test over broad serialization. If
serialization is necessary, write the reason in the proof packet.

## Swift Testing: availability and main-actor fixtures

Mark the test that needs a newer OS or a main-actor fixture:

~~~swift
import Testing

@available(iOS 26.0, *)
@MainActor
@Test("The iOS 26 review surface exposes a pending action")
func iOS26ReviewState() {
    let state = ReviewState(title: "Pending")
    #expect(state.isDirty == false)
}
~~~

The exact deployment target and SDK must be verified in the real target. An
availability annotation does not prove that the feature is available on a
particular device, model profile, entitlement, or system host.

## XCTest: UI launch and semantic queries

Use a UI test target to launch the app with deterministic arguments:

~~~swift
import XCTest

final class ReviewWorkflowUITests: XCTestCase {
    func testPersonCanRejectSuggestion() {
        let app = XCUIApplication()
        app.launchArguments = [
            "-fixtureID", "review-with-suggestion",
            "-resetStore", "YES",
            "-networkMode", "offline"
        ]
        app.launch()

        let review = app.otherElements["review-screen"]
        XCTAssertTrue(review.waitForExistence(timeout: 5))

        let reject = app.buttons["review-reject"]
        XCTAssertTrue(reject.exists)
        XCTAssertTrue(reject.isEnabled)
        reject.tap()

        let original = app.staticTexts["review-original-state"]
        XCTAssertTrue(original.waitForExistence(timeout: 5))
        XCTAssertEqual(original.label, "Original record")
    }
}
~~~

Use an identifier for stable product identity and assert the label/value that
communicates the state. Do not use an element index merely because it is easy.

## SwiftUI: semantic state and identifiers

The production view should expose meaning, not test-only decoration:

~~~swift
import SwiftUI

struct ReviewActionBar: View {
    let canReject: Bool
    let reject: () -> Void

    var body: some View {
        HStack {
            Button("Reject suggestion", role: .destructive, action: reject)
                .accessibilityIdentifier("review-reject")
                .accessibilityHint("Keeps the original record")
                .disabled(!canReject)
        }
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("review-action-bar")
    }
}
~~~

The visible label can localize. The identifier remains a stable automation
contract. Test the action’s disabled state, role, label, hint, focus movement,
and resulting domain state separately.

## XCTest: wait for a state, not an arbitrary delay

When the app performs async work, wait for the semantic result:

~~~swift
let saved = app.staticTexts["review-saved"]
XCTAssertTrue(saved.waitForExistence(timeout: 5))
XCTAssertEqual(saved.label, "Saved")
~~~

Avoid sleep calls that only make a race less visible. If the app needs a longer
timeout in a specific environment, record why and keep the timeout bounded.

## XCTest: performance metrics

Select metrics that match the risk:

~~~swift
import XCTest

final class ReviewPerformanceTests: XCTestCase {
    func testReviewRenderingWorkload() {
        let workload = makeFixture(count: 500)

        measure(metrics: [
            XCTClockMetric(),
            XCTCPUMetric(),
            XCTMemoryMetric(),
            XCTHitchMetric()
        ]) {
            renderReview(workload)
        }
    }

    private func makeFixture(count: Int) -> [String] {
        Array(repeating: "fixture", count: count)
    }

    private func renderReview(_ records: [String]) {
        _ = records.map { $0.uppercased() }
    }
}
~~~

The metric list, workload size, device, OS, build configuration, and baseline
belong in the result record. XCTHitchMetric is meaningful for a UI workload, but
the test still needs physical-device and Instruments context for a performance
claim.

## XCTest: signposted interval

Use a signpost metric when a named interval matters:

~~~swift
import XCTest

final class ImportPerformanceTests: XCTestCase {
    func testImportInterval() {
        let options = XCTMeasureOptions()
        let metric = XCTOSSignpostMetric(
            subsystem: "com.example.app",
            category: "Import",
            name: "ImportRecords"
        )

        measure(metrics: [metric], options: options) {
            runImportFixture()
        }
    }
}
~~~

The subsystem/category/name must match the production signpost if the test is
measuring that interval. Keep private data out of signpost messages.

## Test plan command contract

Use explicit commands in CI or a release checklist:

~~~sh
xcodebuild -scheme ExampleApp -showTestPlans
xcodebuild -scheme ExampleApp test -testPlan Fast
xcodebuild -scheme ExampleApp test -testPlan NativeDesign --only-test-configuration VoiceOver
xcodebuild -scheme ExampleApp test -testPlan ReleaseCandidate -resultBundlePath artifacts/release-tests.xcresult
~~~

The exact scheme, plan names, destination, workspace/project path, and
configuration are target-specific. Record them instead of copying these names
blindly.

## Test plan shape

A test-plan file can include target membership, configurations, arguments,
environment, and tags. Treat it as a product artifact:

~~~json
{
  "configurations": [
    {
      "name": "Offline",
      "options": {
        "testLanguage": "en",
        "testRegion": "US"
      }
    }
  ],
  "defaultOptions": {
    "targetForVariableExpansion": {
      "containerPath": "container:ExampleApp.xcodeproj",
      "identifier": "ExampleApp",
      "name": "ExampleApp"
    }
  },
  "testTargets": [
    {
      "target": {
        "containerPath": "container:ExampleApp.xcodeproj",
        "identifier": "ExampleAppTests",
        "name": "ExampleAppTests"
      }
    }
  ],
  "version": 1
}
~~~

Xcode-generated test-plan schemas and keys can vary with the selected toolchain.
Use Xcode to create or edit the plan and inspect the generated file rather than
assuming this sketch is a complete schema.

## AI evaluation record

Represent an evaluation as data that can be diffed:

~~~swift
struct EvaluationCase: Codable, Sendable {
    let id: String
    let inputReference: String
    let promptVersion: String
    let schemaVersion: String
    let expectedCriteria: [String]
}

struct EvaluationResult: Codable, Sendable {
    let caseID: String
    let modelProfile: String
    let deterministicPass: Bool
    let qualityScores: [String: Double]
    let failureReasons: [String]
    let reviewerDisposition: String?
}
~~~

Keep the actual input references subject to privacy policy. Store enough context
to reproduce the evaluation without copying sensitive source content into a
shared result bundle.

## AI proposal validation before UI commit

Use a typed proposal and a domain validator:

~~~swift
struct ReviewProposal: Sendable, Equatable {
    let sourceID: String
    let sourceRevision: Int
    let suggestedTitle: String
}

enum ProposalError: Error {
    case stale
    case missingSource
    case emptyTitle
}

func validate(
    _ proposal: ReviewProposal,
    currentSourceID: String,
    currentRevision: Int
) throws {
    guard proposal.sourceID == currentSourceID else {
        throw ProposalError.missingSource
    }
    guard proposal.sourceRevision == currentRevision else {
        throw ProposalError.stale
    }
    guard !proposal.suggestedTitle.isEmpty else {
        throw ProposalError.emptyTitle
    }
}
~~~

The review view can display the proposal only after decoding. The explicit
accept action should call the validator again against current domain state
before committing.

## Liquid Glass state fixture

Represent state independently from the effect:

~~~swift
enum GlassReviewState: CaseIterable {
    case empty
    case loading
    case ready
    case needsReview
    case error
    case offline
}

struct GlassReviewFixture {
    let state: GlassReviewState
    let canAccept: Bool
    let accessibilityLabel: String
}

let fixtures = GlassReviewState.allCases.map {
    GlassReviewFixture(
        state: $0,
        canAccept: $0 == .needsReview,
        accessibilityLabel: String(describing: $0)
    )
}
~~~

Use the fixture in previews, Swift Testing, and UI launch-state setup. Verify
appearance and interaction on the selected SDK/device; the enum does not prove
that a visual effect or system behavior is available.

## Release evidence record

Store a small structured record next to the build artifacts:

~~~yaml
target: ExampleApp
scheme: ExampleApp
test_plan: ReleaseCandidate
configuration: Release
destination: physical-device-or-testflight
os: record-selected-os
device: record-selected-device
fixture_set: release-fixtures-v1
ai_profile: record-profile-or-none
accessibility: task-record-path
performance: baseline-record-path
archive: archive-path-and-inspection-result
known_gaps:
  - production-server-delivery-not-tested
~~~

Replace placeholders with the real target values. The record should make it
obvious which claims remain unproved.

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/Testing/DefiningTests)
- [Testing asynchronous code](https://developer.apple.com/documentation/testing/testing-asynchronous-code)
- [Running tests serially or in parallel](https://developer.apple.com/documentation/Testing/Parallelization)
- [Xcode testing](https://developer.apple.com/documentation/xcode/testing)
- [Adding tests to your Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElement](https://developer.apple.com/documentation/xcuiautomation/xcuielement)
- [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)

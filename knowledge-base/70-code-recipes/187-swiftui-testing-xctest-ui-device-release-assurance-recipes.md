# SwiftUI testing, XCTest UI, and release-assurance recipes

These snippets target Swift 6.3 in Xcode 26.4 with the installed iOS 26.4
simulator SDK. They are compile-sized examples for a named test target, not a
complete test plan or proof of physical-device, system-surface, accessibility,
AI quality, archive, TestFlight, or App Store behavior. Each `~~~swift` block
is intentionally independent.

## 1. Write a direct Swift Testing expectation

Use Swift Testing for deterministic Swift code. Keep the fixture local and
assert the product behavior rather than an implementation detail.

~~~swift
import Foundation
import Testing

struct ReviewRouteTests {
    @Test("An accepted title becomes the committed title")
    func acceptedTitle() {
        let draft = "Corrected title"
        let committed = draft.trimmingCharacters(in: .whitespacesAndNewlines)

        #expect(committed == "Corrected title")
    }
}
~~~

## 2. Cover a state matrix with parameterized tests

Parameterized cases should carry enough identity to diagnose a failure. Keep
collections Sendable and avoid hidden shared stores when the test runner may
execute cases in parallel.

~~~swift
import Foundation
import Testing

struct ReviewCase: Sendable {
    let input: String
    let expected: String
}

struct ReviewMatrixTests {
    @Test(arguments: [
        ReviewCase(input: "  A  ", expected: "A"),
        ReviewCase(input: "", expected: ""),
        ReviewCase(input: "B\n", expected: "B")
    ])
    func normalizedValue(_ fixture: ReviewCase) {
        let result = fixture.input.trimmingCharacters(in: .whitespacesAndNewlines)
        #expect(result == fixture.expected)
    }
}
~~~

## 3. Use `#require` for setup and typed thrown errors

Use `#require` when the rest of the test is meaningless without a value. The
returned error from `#expect(throws:)` can then be checked precisely.

~~~swift
import Foundation
import Testing

enum ReviewValidationError: Error, Equatable {
    case emptyTitle
}

func validateTitle(_ title: String) throws(ReviewValidationError) -> String {
    let value = title.trimmingCharacters(in: .whitespacesAndNewlines)
    guard value.isEmpty == false else { throw .emptyTitle }
    return value
}

struct ValidationTests {
    @Test
    func validAndInvalidTitles() throws {
        let candidate = try #require(["Accepted"].first)
        let value = try validateTitle(candidate)
        #expect(value == "Accepted")

        let error = #expect(throws: ReviewValidationError.self) {
            try validateTitle(" ")
        }
        let actual = try #require(error)
        #expect(actual == .emptyTitle)
    }
}
~~~

## 4. Tag an iOS 26 test and bound its runtime

Put availability on the test that needs the newer behavior. Tags and time
limits are execution/reporting contracts; they do not prove that a device,
entitlement, or system host supports the feature.

~~~swift
import Testing

extension Tag {
    @Tag static var smoke: Self
}

@available(iOS 26.0, *)
@Test("The native review route has a stable entry state", .tags(.smoke), .timeLimit(.minutes(1)))
func iOS26EntryState() {
    let state = "ready"
    #expect(state == "ready")
}
~~~

## 5. Confirm an asynchronous event exactly once

Use `confirmation` around the operation that can emit the event and wait for
the task to finish. This prevents a callback from outliving the test scope.

~~~swift
import Testing

actor EventSource {
    private var continuation: AsyncStream<String>.Continuation?

    func stream() -> AsyncStream<String> {
        AsyncStream { continuation in
            self.continuation = continuation
        }
    }

    func send(_ value: String) {
        continuation?.yield(value)
    }
}

struct AsyncReviewTests {
    @Test
    func observesOneCommitEvent() async {
        let source = EventSource()
        let stream = await source.stream()

        await confirmation(expectedCount: 1) { confirm in
            let task = Task {
                for await value in stream where value == "committed" {
                    confirm()
                    break
                }
            }

            await source.send("committed")
            await task.value
        }
    }
}
~~~

## 6. Confirm a bounded event range

Range-based confirmations are useful for streams where a valid run may emit a
known minimum and maximum. A range is not a substitute for asserting the
content or revision of each event.

~~~swift
import Testing

struct BatchEventsTests {
    @Test
    func receivesAValidBatchCount() async {
        await confirmation(expectedCount: 2...3) { confirm in
            confirm()
            confirm()
        }
    }
}
~~~

## 7. Record a known issue without hiding an unexpected pass

Use `withKnownIssue` only for a tracked defect. A non-intermittent known issue
expects a failure; an intermittent issue records an expected failure if one
occurs while allowing a clean run to pass.

~~~swift
import Testing

struct KnownIssueTests {
    @Test
    func trackedRenderingIssue() {
        withKnownIssue("Tracked glass fallback issue", isIntermittent: true) {
            let rendered = true
            #expect(rendered == false)
        }
    }
}
~~~

## 8. Scope a task-local test fixture

Test scoping traits provide concurrency-safe setup around a test. Use them for
configuration that should be visible only to the current test task.

~~~swift
import Testing

enum FixtureContext {
    @TaskLocal static var id = "default"
}

struct FixtureTrait: TestTrait, TestScoping {
    func provideScope(
        for test: Test,
        testCase: Test.Case?,
        performing function: () async throws -> Void
    ) async throws {
        try await FixtureContext.$id.withValue("review-fixture") {
            try await function()
        }
    }
}

extension Trait where Self == FixtureTrait {
    static var reviewFixture: Self { Self() }
}

@Test(.reviewFixture)
func readsScopedFixture() {
    #expect(FixtureContext.id == "review-fixture")
}
~~~

## 9. Attach a Codable fixture to a failing test

Attachments help a test report carry the exact fixture or diagnostic record
that led to a failure. Do not attach private user input unless the test target’s
retention and access policy explicitly permits it.

~~~swift
import Foundation
import Testing

struct ReviewDiagnostic: Codable, Attachable {
    let fixtureID: String
    let sourceRevision: String
}

@Test
func recordsReviewDiagnostic() {
    let diagnostic = ReviewDiagnostic(
        fixtureID: "review-001",
        sourceRevision: "source-r3"
    )
    Attachment.record(diagnostic, named: "review-diagnostic")
    #expect(diagnostic.fixtureID == "review-001")
}
~~~

## 10. Evaluate a test condition outside the runner

Condition traits can also be evaluated by setup or diagnostic code. Keep the
same condition source for the test runner and the surrounding evidence logic.

~~~swift
import Testing

enum TestMode {
    static let smoke = true
}

@Test
func evaluatesSmokeCondition() async throws {
    let trait = ConditionTrait.disabled(if: TestMode.smoke)
    let conditionMatches = try await trait.evaluate()
    #expect(conditionMatches)
}
~~~

## 11. Launch a UI test with deterministic state

Swift Testing does not replace UI testing. Use XCTest and XCUIAutomation for a
running app, and pass fixture IDs or reset flags instead of relying on hidden
simulator state.

~~~swift
import XCTest

enum UIProofError: Error {
    case missingState
}

final class ReviewWorkflowUITests: XCTestCase {
    @MainActor
    func testRejectsSuggestion() throws {
        let app = XCUIApplication()
        app.launchArguments = [
            "-fixtureID", "review-with-suggestion",
            "-resetStore", "YES",
            "-networkMode", "offline"
        ]
        app.launch()

        let review = app.otherElements["review-screen"]
        guard review.waitForExistence(timeout: 5) else {
            throw UIProofError.missingState
        }

        let reject = app.buttons["review-reject"]
        guard reject.exists, reject.isEnabled else {
            throw UIProofError.missingState
        }
        reject.tap()

        let original = app.staticTexts["review-original-state"]
        guard original.waitForExistence(timeout: 5), original.label == "Original record" else {
            throw UIProofError.missingState
        }
    }
}
~~~

## 12. Run an automated accessibility audit

An automated audit catches common issues on the current screen. It supports a
workflow record but does not replace VoiceOver, Dynamic Type, reduced-motion,
contrast, keyboard, pointer, or other assistive-technology task testing.

~~~swift
import XCTest

enum AccessibilityProofError: Error {
    case missingScreen
}

final class ReviewAccessibilityUITests: XCTestCase {
    @MainActor
    func testReviewScreenAccessibilityAudit() throws {
        let app = XCUIApplication()
        app.launchArguments = ["-fixtureID", "review-ready"]
        app.launch()

        guard app.otherElements["review-screen"].waitForExistence(timeout: 5) else {
            throw AccessibilityProofError.missingScreen
        }
        try app.performAccessibilityAudit(for: .all)
    }
}
~~~

## 13. Measure a release-relevant path with XCTest metrics

Performance results are meaningful only with a named workload, destination,
build configuration, and baseline. This recipe measures a deterministic local
operation; it does not prove universal device performance.

~~~swift
import XCTest

final class ReviewPerformanceTests: XCTestCase {
    func testNormalizesRepresentativeFixture() {
        let input = String(repeating: "review-value ", count: 1_000)

        measure(metrics: [XCTClockMetric(), XCTMemoryMetric()]) {
            _ = input.trimmingCharacters(in: .whitespacesAndNewlines)
        }
    }
}
~~~

## 14. Validate a typed on-device AI proposal deterministically

The model output is only a proposal. Deterministic checks should validate the
source revision, schema, allowed fields, and review requirement before any
domain commit is available.

~~~swift
import Testing

struct ReviewProposal: Codable, Sendable {
    let sourceRevision: String
    let proposedTitle: String
    let requiresReview: Bool
}

func isSafeProposal(
    _ proposal: ReviewProposal,
    currentRevision: String
) -> Bool {
    proposal.sourceRevision == currentRevision
        && proposal.proposedTitle.isEmpty == false
        && proposal.requiresReview
}

struct AIProposalTests {
    @Test(arguments: [
        ReviewProposal(sourceRevision: "r1", proposedTitle: "Title", requiresReview: true),
        ReviewProposal(sourceRevision: "r2", proposedTitle: "Other", requiresReview: false)
    ])
    func proposalNeedsCurrentRevisionAndReview(
        _ proposal: ReviewProposal
    ) {
        let expected = proposal.sourceRevision == "r1" && proposal.requiresReview
        #expect(isSafeProposal(proposal, currentRevision: "r1") == expected)
    }
}
~~~

## Recipe handoff

- [ ] Put Swift Testing snippets in a unit/integration test target, never in an
      application target.
- [ ] Keep XCTest UI and accessibility recipes in a UI test target with named
      launch arguments and semantic identifiers.
- [ ] Add each fixture ID, test-plan configuration, destination, SDK, OS,
      build configuration, and result bundle to the evidence packet.
- [ ] Treat performance, AI evaluation, accessibility audits, physical-device
      work, archives, and TestFlight as separate proof layers.

## Sources

- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Defining test functions](https://developer.apple.com/documentation/testing/definingtests)
- [Test](https://developer.apple.com/documentation/testing/test)
- [Test(_:_:arguments:_:) parameterized tests](https://developer.apple.com/documentation/testing/test%28_%3A_%3Aarguments%3A_%3A%29)
- [Expectations and confirmations](https://developer.apple.com/documentation/testing/expectations)
- [TestScoping](https://developer.apple.com/documentation/testing/testscoping)
- [Attachment](https://developer.apple.com/documentation/testing/attachment)
- [Limiting the running time of tests](https://developer.apple.com/documentation/testing/limitingexecutiontime)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [XCUIElementQuery](https://developer.apple.com/documentation/xcuiautomation/xcuielementquery)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Writing and running performance tests](https://developer.apple.com/documentation/xcode/writing-and-running-performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)

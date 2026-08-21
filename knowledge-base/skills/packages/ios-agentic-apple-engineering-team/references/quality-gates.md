# Quality gates for source-grounded Apple engineering skills

Use these gates when judging an LLM-generated plan, patch, or review. A green
gate means the evidence exists for the named level; it never upgrades a weaker
level into a stronger one.

## Source and route gates

- Exact Apple/Swift sources are linked for APIs, availability, HIG behavior,
  entitlements, privacy, or release claims.
- Installed SDK headers/Xcode diagnostics are checked when the signature or
  deployment target matters.
- The chosen framework owns the capability; rejected alternatives and platform
  limits are recorded.
- Target, device family, OS/SDK, region, hardware, entitlement, permission,
  model/asset, extension, server, and account gates are explicit.

## Engineering gates

- Source input, normalized observation, derived presentation, domain truth, and
  side effects have separate types or state boundaries.
- Async work has an owner, cancellation, stale-result/revision guard, and
  process/interruption/retry/recovery behavior.
- Mutations are authorized, validated, reviewable where consequential, and
  idempotent or conflict-aware.
- Secrets and protected/personal data are minimized, redacted, retained only
  as needed, and excluded from model context unless explicitly authorized.

## Native design gates

- Standard SwiftUI/UIKit/system controls are preferred before custom drawing.
- Liquid Glass is functional grouping over content, not a full-screen costume,
  trust badge, or substitute for hierarchy.
- Dynamic Type, localization/RTL, VoiceOver, Voice Control, Switch Control,
  keyboard/pointer/controller input, contrast, Reduce Motion, and Reduce
  Transparency are addressed for the real task.
- System-owned surfaces remain system-owned; app shells explain and resume the
  task without faking Apple UI or branding.

## Test and evaluation gates

- Swift Testing/XCTest fixtures cover happy path, empty/partial/stale, denied,
  unavailable, cancellation, interruption, retry, conflict, revocation,
  deletion, and process termination as applicable.
- UI tests use semantic queries and verify task completion, not screenshots only.
- AI output is typed, evaluated against fixtures, revalidated against current
  domain state, reviewable, cancellable, and has deterministic fallback.
- Performance/energy/thermal claims name the device, build, workload, metric,
  and limits rather than promising universal behavior.

## Evidence gates

Label each result as source, compile, fixture/unit, simulator/UI, physical/system,
server/account, signed artifact, TestFlight/App Store, or production. Require
the evidence level appropriate to the claim. A preview, compile, simulator,
system callback, AI proposal, or archive is never silently promoted to Apple
approval or production correctness.

## Open-source packaging gates

- `SKILL.md` has only `name` and `description` in frontmatter and a concise
  imperative workflow under 500 lines.
- Detailed variants live in one-level `references/`; no generated README or
  redundant installation guide is included in a skill directory.
- Paths are portable; private workspace paths, secrets, user data, and stale
  SDK claims are excluded or clearly marked.
- The skill has been exercised on representative tasks, quick-validated, and
  packaged with the official validator before publication.
- Publication says “Apple-conforming/review-ready guidance,” never guaranteed
  Apple approval.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)

# Provenance and evidence boundaries

Use this vocabulary in Markdown pages, skill handoffs, package fixtures, and
receipts.

| Label | What it means | What it cannot mean |
| --- | --- | --- |
| source | Official documentation or HIG statement | this project’s behavior |
| SDK | Installed interface/compiler observation | entitlement/account/device support |
| compile | Typecheck/build succeeded for named target | runtime correctness |
| fixture | Deterministic test or evaluation result | real service/hardware behavior |
| simulator/UI | App run or UI test on named simulated destination | physical sensors/assistive/device behavior |
| physical/system | Named device/host observation | every supported device or production |
| signed artifact | Archive/install/signing/target inspection | App Review acceptance |
| TestFlight/App Store | exact distributed build observation | universal production correctness |
| production | named live environment observation | future versions/regions/devices |

## Claim wording

- “The current Apple documentation describes…” for source evidence.
- “The installed iOS 26.4 SDK exposes/typechecks…” for SDK evidence.
- “The named fixture/test passed…” for deterministic evidence.
- “The named device/OS/build observed…” for physical/system evidence.
- “The archive/TestFlight gate passed…” for signed/distribution evidence.
- “App Review/production remains unverified” unless that external evidence is
  actually present.

Never use “Apple-approved,” “private,” “accessible,” “works everywhere,”
“real-time,” “safe,” “on-device,” or “release-ready” without the qualifiers and
evidence needed for the claim.

## Source proximity

Place the official URL next to version-sensitive claims and also register it in
the central source registry. Link route pages to the exact knowledge-base page
that owns the implementation boundary. A skill should point to the route and
state when the source was last refreshed or needs rechecking.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Documentation updates](https://developer.apple.com/documentation/updates)
- [Swift](https://swift.org/documentation/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

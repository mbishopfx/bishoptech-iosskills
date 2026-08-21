# CI release confidence and native design

## Design objective

An Apple-native release dashboard should make the release state legible before
it makes the surface beautiful. The useful design is a chain of small,
reviewable states:

    source revision -> workflow -> action -> artifact -> signed build
      -> processed build -> tester feedback -> release decision

Liquid Glass can give a high-priority action or review surface a clear visual
container, but it cannot make an unverified build trustworthy. Treat every
glass control as a real semantic Button, Menu, Toggle, or navigation action
with a state-specific consequence.

Use this page with:

- [Xcode Cloud CI/CD and release automation](../42-framework-deep-dives/76-xcode-cloud-ci-cd-and-release-automation.md)
- [Xcode Cloud CI/CD release route](../50-capability-recipes/107-xcode-cloud-ci-cd-release-route.md)
- [Xcode Cloud CI/CD proof matrix](../60-verification/101-xcode-cloud-ci-cd-proof-matrix.md)
- [Xcode Cloud CI/CD release recipes](../70-code-recipes/119-xcode-cloud-ci-cd-release-recipes.md)
- [Release-ready native design and privacy](103-release-ready-native-design-and-privacy.md)

## Model the release as state, not decoration

Define a small domain state and derive the screen from it. Do not let the
presence of a glowing panel imply that a build is safe:

| State | Meaning | Primary action | Dangerous inference to avoid |
| --- | --- | --- | --- |
| Draft | Workflow or release record is being edited | Review configuration | A draft is runnable |
| Queued | Xcode Cloud accepted a start request | View workflow and cancel if appropriate | A queued build has passed |
| Running | An action is executing | View logs and current phase | Partial output is a release |
| Failed | An action or post-action stopped with an error | Open logs, download artifacts, reproduce commit | Retry always fixes the cause |
| Passed | Selected action completed | Inspect result and artifact identities | All unselected gates passed |
| Archived | An archive exists for the selected target/configuration | Inspect products, signing, privacy, and version/build | App Store Connect has processed it |
| Processing | App Store Connect is analyzing the upload | Refresh processing state | TestFlight install is available |
| TestFlight | A selected build is available to a tester group | Open tester notes or feedback | App Review or production release occurred |
| Candidate | All required evidence is attached to a named build | Review release packet | An AI summary is approval |
| Released | App Store version is available through the selected rollout | Observe production state | Future builds inherit this proof |

Persist the state transition with the source commit, workflow ID, build ID,
action, bundle ID, version/build, and timestamp. A status badge without these
identifiers is a presentation-only observation.

## A native screen contract

Use the platform’s normal navigation and hierarchy:

1. a top-level list of workflows or release candidates;
2. a detail screen for the selected build;
3. an action timeline grouped by action and post-action;
4. an artifact and evidence section;
5. a review/approval section with explicit side-effect buttons.

Prefer standard SwiftUI navigation, lists, sections, alerts, sheets, menus,
progress views, labels, and buttons. Reserve a custom surface for the part
that genuinely needs it, such as a compact dependency graph or a visual
timeline. The semantic content must remain available when the visual effect is
disabled.

Every detail view should answer:

- What source revision ran?
- Which workflow and action ran it?
- Which Xcode/macOS environment and destination were used?
- What did the action produce?
- Which checks were required to pass?
- Which external state has or has not changed?
- What is the next safe action?

## Functional Liquid Glass

The Liquid Glass adoption route favors system-provided materials and
containers, clear hierarchy, and functional controls. Apply it to a small
number of high-value surfaces:

| Surface | Appropriate use | Keep visible without glass |
| --- | --- | --- |
| Candidate header | Build identity, current state, and one primary review action | Title, version/build, state, commit, and accessibility label |
| Action timeline | Grouping the current phase and its next action | Action names, status, start/end, errors, and focus order |
| Artifact action row | Download, inspect, compare, or open logs | Action label, destination, checksum, and enabled state |
| TestFlight handoff | A deliberate distribution action after gates pass | Tester group, build identity, review state, and confirmation |
| AI evaluation card | Dataset version, score/change, model profile, and human decision | Plain-language criteria, failure state, and manual route |

Do not cover every row in glass. Excessive translucent decoration competes with
logs, warnings, and build identity. Avoid building a fake copy of App Store
Connect, TestFlight, or an Apple Intelligence system surface; link or hand off
to the owner surface when Apple owns the action.

Glass controls must remain controls:

- use the semantic control that matches the action;
- expose a meaningful label and value to VoiceOver;
- preserve hit regions when effects are reduced;
- maintain contrast in light/dark and increased-contrast modes;
- avoid motion-only state changes;
- make disabled, pending, failed, and completed states distinguishable without
  color alone.

## State transitions and irreversible actions

Place irreversible actions behind a review surface:

    inspect candidate -> confirm build identity -> confirm target/group
      -> explain side effect -> perform action -> reconcile remote state

Examples:

- “Start build” should identify branch/tag/commit and workflow.
- “Retry” should distinguish rebuilding the same commit from starting a new
  commit.
- “Distribute to internal testers” should identify the exact processed build
  and tester group.
- “Submit for external beta review” should show that the action changes an
  App Store Connect review state.
- “Release” should show release option, version, phased/manual policy, and
  evidence gaps.

The UI should never disable the manual route merely because an AI summary is
missing. Model-generated summaries can shorten logs or suggest a likely cause,
but the source log and deterministic rule remain available.

## On-device AI in CI and release surfaces

An on-device model can help a developer navigate a large build report, group
similar failures, or draft “what to test” notes. Keep it in the proposal layer:

    build artifacts/logs -> bounded local extraction
      -> model summary or classification -> source-linked review
      -> human decision or deterministic action

Record:

- model/framework/profile version;
- input artifact IDs and redaction policy;
- evaluation dataset and criteria;
- whether the output is a summary, classification, or proposed action;
- confidence/uncertainty and fallback;
- the human or deterministic check that authorizes a side effect.

Do not send signing material, API keys, personal tester data, private source,
or raw customer logs to a model just because a summary would be convenient.
Prefer local extraction of the smallest useful fields. A model that says
“safe to release” is not a release gate.

For Foundation Models or Core ML routes, separate model availability from
quality. A CI simulator result can validate an adapter and fixtures; it cannot
prove that a named iPhone has the expected system model, language, thermal
headroom, or release fallback.

## Privacy and secret-aware design

Security is part of the visual contract:

| Data | Default display |
| --- | --- |
| Commit, workflow, build, action, version/build | Visible and copyable |
| Source URL or branch | Visible according to team policy |
| Build log excerpt | Redacted by default with an intentional reveal |
| API key/token/certificate material | Never display or persist in the UI |
| Tester account and device details | Least-privilege, role-aware, and minimized |
| Privacy manifest/report | Show declared categories and status, not hidden raw data |
| Model input/output | Show provenance and retention, not sensitive source by default |

Make redaction state explicit. “Hidden” should not mean “deleted,” and “local”
should not mean “private” if a workflow uploads artifacts or posts a webhook.
Document retention and deletion for cached logs, downloaded archives, model
inputs, and tester feedback.

## Accessibility and adaptation

Test the release dashboard as a workflow, not as a screenshot:

- VoiceOver can move from build identity to action status to the next action;
- failure summaries include the action and reason, not only an icon;
- Dynamic Type does not truncate the version/build or hide the primary action;
- increased contrast and reduced transparency preserve grouping and legibility;
- Reduce Motion avoids using glass morphing as the only progress signal;
- keyboard, pointer, Voice Control, and Switch Control can reach every action;
- long branch names, localized tester notes, and multiline errors wrap safely;
- compact width, iPad split view, and large window layouts keep the evidence
  hierarchy intact.

Use accessibility identifiers for automation, but do not make the identifier
the only semantic description. UI tests should assert the user-visible state
and task result.

## TestFlight is a review surface

A TestFlight handoff should show:

- exact version and build;
- whether the build is still processing;
- internal or external tester group;
- beta review state if external testing is selected;
- what changed and what to test;
- known gaps, unavailable devices, and server prerequisites;
- install/update expectations and feedback path.

TestFlight notes can be stored as project text files for Xcode Cloud to use in
the tester-facing “What to Test” field. Keep the notes specific and honest:
they are part of the human evaluation loop, not marketing copy.

## Release confidence screen

The compact candidate screen can use this hierarchy:

    Candidate title and build identity
    State and last transition
    Required gates: source, build, test, archive, privacy, signing
    Distribution state: processing, TestFlight, review, release option
    AI/Liquid Glass gates: availability, fixture, device, accessibility
    Evidence links: logs, result bundle, archive, symbols, feedback
    One safe next action

Do not make a green status pill larger than the evidence it summarizes. The
user should be able to open the underlying record without leaving the native
flow.

## Sources

- [Liquid Glass technology overview](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Xcode Cloud](https://developer.apple.com/documentation/xcode/xcode-cloud)
- [Xcode Cloud workflow reference](https://developer.apple.com/documentation/xcode/xcode-cloud-workflow-reference)
- [Configuring your Xcode Cloud workflow’s actions](https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions)
- [Developing a workflow strategy for Xcode Cloud](https://developer.apple.com/documentation/xcode/developing-a-workflow-strategy-for-xcode-cloud)
- [Creating a workflow that builds your app for distribution](https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution)
- [Distributing your Xcode Cloud builds through TestFlight](https://developer.apple.com/documentation/xcode/distributing-your-xcode-cloud-builds-through-testflight)
- [Including notes for testers with a beta release](https://developer.apple.com/documentation/xcode/including-notes-for-testers-with-a-beta-release-of-your-app)
- [Environment variable reference](https://developer.apple.com/documentation/xcode/environment-variable-reference)
- [Writing custom build scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)

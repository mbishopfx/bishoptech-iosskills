# Xcode Cloud CI/CD and release automation

## Purpose

Xcode Cloud is the Apple-hosted build, test, verification, archive, and
distribution route that connects Xcode, source control, App Store Connect, and
TestFlight. It is useful for keeping an app in a repeatably buildable and
releasable state, but a successful cloud build is one evidence packet in a
larger release chain.

Use this page with:

- [CI release confidence and native design](../21-design-deep-dives/104-ci-release-confidence-and-native-design.md)
- [Xcode Cloud CI/CD release route](../50-capability-recipes/107-xcode-cloud-ci-cd-release-route.md)
- [Xcode Cloud CI/CD proof matrix](../60-verification/101-xcode-cloud-ci-cd-proof-matrix.md)
- [Xcode Cloud CI/CD release recipes](../70-code-recipes/119-xcode-cloud-ci-cd-release-recipes.md)
- [Xcode archive, signing, TestFlight, and release](75-xcode-archive-signing-testflight-and-release.md)

## Capability boundary

An Xcode Cloud workflow is a configured graph, not a magic copy of a local
machine:

    remote Git revision
      -> temporary Xcode/macOS environment
      -> dependency and custom-script preparation
      -> build / test / analyze / archive action
      -> logs, result bundles, binaries, symbols, and other artifacts
      -> optional TestFlight or notification post-action
      -> App Store Connect processing and human/system release gates

Keep these boundaries visible:

| Layer | What it proves | What it does not prove |
| --- | --- | --- |
| Workflow configuration | Which source, environment, start condition, action, destination, test plan, and post-action were selected | That the workflow has run successfully |
| Cloud build | The selected commit completed the selected action in a temporary environment | Physical-device behavior, App Review, or production health |
| Test result | The selected tests ran for the selected destination and configuration | Accessibility task completion, every device family, or model quality outside the fixture |
| Archive artifact | A selected target was archived and possibly signed for a distribution mode | App Store Connect processing or tester installation |
| TestFlight post-action | Xcode Cloud submitted a configured distribution build to App Store Connect/TestFlight | External beta review, production approval, or rollout |
| Device run | The named build and device exercised a workflow | Every supported OS, account, server, model, or system surface |
| App Store release | Apple made the selected version available through the chosen release option | Future builds, remote services, or claims not tested in that version |

Do not call CI green because a workflow exists. Do not call an app shipped
because an archive was produced. Record the exact commit, workflow, action,
build number, artifact, destination, processing state, and release decision.

## Project, product, and source-control prerequisites

Before configuring the first workflow, qualify the project:

1. Enroll the team in the Apple Developer Program and identify the team that
   owns the intended App Store Connect app record.
2. Use a supported remote Git repository and grant Xcode Cloud the minimum
   provider permission needed to clone it.
3. Ensure the product has a stable bundle identifier and that the app record
   or intended app-record creation path is known.
4. Share the scheme and enable the Archive action for every product that must
   appear as an Xcode Cloud product.
5. Commit the project/workspace, scheme, test plans, package resolution, build
   settings, privacy manifests, and CI scripts that the workflow needs.
6. Identify every app extension, watch target, widget, App Intent, package,
   generated resource, and capability that the cloud build must see.

Xcode initially analyzes the project or workspace and helps configure a first
workflow. After the first build, workflows can also be managed in App Store
Connect. The bundle identifier, team, scheme, and target graph still come from
the project; changing a workflow does not repair an incomplete target graph.

Watch and extension products need their bundle identifiers registered in the
developer account before a cloud workflow can reliably build them. A workflow
that only finds the main app is not proof that companion targets are included.

## Workflow settings

A useful workflow record contains more than a name:

| Setting | Decision to record |
| --- | --- |
| Product | App or framework and exact bundle identifier |
| Repository | Provider, repository, branch/tag/PR reference, and access owner |
| Environment | macOS and Xcode versions, clean or cached build policy, destinations |
| Start condition | Branch change, pull request, Git tag, schedule, or deliberate manual path |
| Actions | Build, test, analyze, archive, required-to-pass policy |
| Test plan | Named plan or scheme settings, destinations, parallelization, timeout policy |
| Post-actions | TestFlight internal/external group, notification, webhook, or no side effect |
| Scripts | Post-clone, pre-build, post-build purpose and failure policy |
| Variables | Public configuration, secret values, scope, redaction, and rotation owner |
| Editing policy | Restricted editors, duplicate-before-change policy, deactivation policy |
| Artifact policy | Download owner, retention location, checksum, symbols, and result bundles |

Xcode Cloud can periodically update available macOS and Xcode environments.
Choose an explicit environment for release workflows and schedule a refresh
when the project must adopt a new toolchain. A release workflow should not
silently move toolchains while a build is being compared to a prior artifact.

## Start conditions are part of the product safety model

Start conditions decide when a workflow spends build minutes and when it can
create a distribution side effect:

| Start condition | Good use | Safety rule |
| --- | --- | --- |
| Branch changes | Fast compile and focused tests on a development branch | Keep actions short and avoid public distribution |
| Pull request changes | Required build/test status before merging | Configure branch protection in the SCM provider; a reported status alone does not block merging |
| Git tag changes | Release-candidate archive or TestFlight distribution | Restrict tag naming and human ownership; verify version/build policy |
| Schedule | Nightly builds, weekly UI tests, dependency/toolchain checks | Make the output diagnosable and avoid accidental tester delivery |
| Manual-only workflow | Deliberate archive or distribution after a review gate | Configure a condition that does not trigger automatically and document the operator |

Auto-cancel can stop an in-progress build when a newer build for the same
condition queues. This is helpful for fast branch feedback, but it can be
wrong for a long-running release candidate or artifact-collection workflow.
Choose the policy per condition and record canceled versus failed builds
separately.

## Actions and their evidence

### Build

A build action verifies that the selected scheme and destination can produce
the build product. Xcode Cloud runs the equivalent of an Xcode build action and
stores the build product, logs, and result bundle as artifacts. This is the
right first gate for compile health, package resolution, generated resources,
availability annotations, and target membership.

It is not a signing, TestFlight, or physical-device gate.

### Test

A test action can use scheme settings or an explicit test plan and one or more
simulator destinations. Xcode Cloud builds for testing and then runs tests
without rebuilding. The second phase has a different process boundary: source
code is not available there, so test fixtures and scripts must use the paths
and artifacts the action exposes.

Use separate workflows for:

- fast deterministic unit and model-adapter tests on every pull request;
- focused UI/accessibility workflows on branch or scheduled changes;
- slower, broader device-matrix simulation and performance checks;
- release-candidate tests that use the same Release-oriented settings as the
  distribution path.

A test action can be required to pass or allowed to report without blocking the
workflow. Make that policy explicit rather than interpreting a green workflow
as if all test actions were required.

### Analyze

An analyze action is useful for static analysis and compiler diagnostics. Keep
warnings, analyzer issues, and policy decisions in the build record. Analysis
does not exercise runtime permissions, system delivery, model readiness, or
Liquid Glass interaction.

### Archive

An archive action runs the archive route and produces a distributable archive
or framework bundle plus logs. Its Deployment Preparation setting changes the
meaning of the artifact:

| Deployment Preparation | Intended boundary |
| --- | --- |
| None | Archive for development or inspection; not eligible for TestFlight/App Store distribution |
| TestFlight (Internal Testing Only) | Signed for team/internal TestFlight distribution, not App Store release |
| TestFlight and App Store | Signed for TestFlight and a binary eligible for App Store submission; external testing and App Review remain separate |

An archive action is required for a distribution workflow. A build action that
passes does not replace it.

## Temporary environments and action isolation

Each Xcode Cloud action runs in a temporary environment. The general action
sequence is:

1. clone the connected repository;
2. resolve dependencies and prepare the environment;
3. run the relevant custom scripts;
4. run the action’s Xcode command;
5. save the action’s logs and artifacts;
6. discard the temporary environment after the action.

Do not assume an artifact from one action is available to another action. In
particular, a test result bundle from a test action is not automatically an
input to a later action. If a later stage needs a value, reproduce it from
source/configuration or explicitly persist/download the artifact.

This isolation is useful for clean proof. It also exposes hidden assumptions:
local caches, uncommitted generated files, personal keychains, machine-wide
tools, and files outside the repository are not release inputs.

## Custom build scripts, variables, and dependencies

Xcode Cloud recognizes three top-level scripts in the repository’s
ci_scripts directory:

- ci_post_clone.sh;
- ci_pre_xcodebuild.sh;
- ci_post_xcodebuild.sh.

Use the phases narrowly:

| Phase | Safe responsibility |
| --- | --- |
| Post-clone | Install or prepare tools and files needed before Xcode builds |
| Pre-xcodebuild | Validate inputs, select a bounded configuration, or prepare generated resources |
| Post-xcodebuild | Collect artifacts, emit diagnostics, or perform an approved upload |

Scripts run in a temporary environment. Place script resources in ci_scripts or
make the intended repository path explicit. Use nonzero exit status for real
failures. Do not make a script silently turn a failed archive into a success.

Predefined variables expose the build ID, build number, commit, bundle ID,
workflow, scheme, current Xcode action, result-bundle path, archive path, and
signed app paths. Use them to make diagnostics and artifact names traceable.
For test runners, Xcode Cloud prefixes variables with TEST_RUNNER_ so the test
process can access the intended values.

Custom variables should be scoped to the workflow and marked secret when they
contain credentials or sensitive configuration. Redaction prevents values from
appearing in logs; it does not authorize the script to use a credential for an
unrelated side effect. Never echo API keys, access tokens, signing private
material, or user data.

Swift packages and other dependencies must be available from the committed
repository and selected project configuration. Commit the intended package
resolution file. Do not force automatic package resolution in a custom script
to hide an unresolved or unreviewed dependency change.

## Signing, privacy, and distribution side effects

Cloud signing is still signing. Keep the same checks used for a local archive:

- team and bundle IDs match the intended app record;
- extension IDs and capabilities are registered;
- deployment preparation matches the intended TestFlight/App Store boundary;
- signed entitlements match the system surfaces the product claims;
- app and SDK privacy manifests are bundled and reconciled;
- version/build identity is unique and recorded;
- export compliance and App Store metadata are ready for the selected path.

Use a TestFlight post-action only after the workflow has a clear release
candidate policy. Internal TestFlight distribution is a useful feedback gate;
external testing may require beta review; App Store availability and App Review
are separate decisions. A cloud post-action can submit a build, but it cannot
stand in for a human review of privacy, accessibility, system behavior, or
production services.

## Artifacts and retention

Cloud artifacts include build logs, app/framework products, exported archives,
symbols, and test result bundles. Xcode Cloud makes build information and
artifacts available for a limited retention window, documented as 30 days for
completed builds. Download and archive the artifact packet for any build that
may be submitted or released:

    source commit and workflow
      + Xcode/macOS environment
      + action logs and result bundles
      + archive and dSYM
      + signed entitlements and privacy report
      + version/build and processing record
      + TestFlight/App Store Connect state
      + release decision and known gaps

The App Store Connect API can automate reading workflows, builds, actions,
artifacts, issues, test results, repositories, pull requests, and Git
references. API automation should preserve the same identity and redaction
rules as the human workflow.

## Failure diagnostics

When a workflow fails:

1. identify the exact workflow, action, commit, environment, and failure phase;
2. download the failed action’s logs, result bundle, and other artifacts;
3. reproduce the same commit and action locally;
4. compare scheme sharing, archive action, package resolution, capabilities,
   environment variables, proxy behavior, and target membership;
5. fix the source/configuration issue and rebuild the same route;
6. preserve the failed and corrected records when the change affects release
   confidence.

Infrastructure validation builds can cause duplicate checkouts or custom
script calls without appearing as ordinary builds or uploading to the App
Store/TestFlight. Scripts that call external services must tolerate this
boundary or opt out through the documented App Store Connect setting.

Webhooks can publish build-created, build-started, and build-finished events to
an HTTPS endpoint. Verify delivery responses, retry behavior, payload parsing,
replay/idempotency, authentication, and sensitive-field handling. Treat a
webhook as notification input, not as authority to publish or mutate an app
without an explicit server-side policy.

## Liquid Glass and on-device AI release gates

CI can compile and test a Liquid Glass or on-device AI feature, but the
release packet must keep the runtime gates separate:

| Feature | CI gate | Physical/release gate |
| --- | --- | --- |
| Liquid Glass | State fixtures, accessibility identifiers, reduced-motion and contrast test coverage, layout snapshots where useful | Signed Release/TestFlight interaction, legibility, hit regions, motion, contrast, Dynamic Type, and system-surface behavior |
| Foundation Models | Availability-guarded adapters, deterministic validation, refusal/error/cancellation fixtures, prompt/evaluation dataset checks | Supported device/model readiness, language, cold/warm latency, battery/thermal behavior, real fallback, privacy, and reviewable side effects |
| Vision/Core ML | Model resource membership, typed feature fixtures, deterministic preprocessing, compile and inference tests | Hardware camera/media behavior, model asset availability, performance, thermal state, user permission, and Release artifact membership |
| App Intents/widgets/controls | Target compilation, entity/intent fixtures, static configuration checks | Signed target membership, system invocation, accessibility, locked/background behavior, and App Store metadata |

Do not use cloud model output as a release artifact without recording the
model/API/profile/prompt version and evaluation criteria. Do not let a CI
script apply model-generated changes or distribute a build without an
explicit, validated authorization boundary.

## Sources

- [Xcode Cloud](https://developer.apple.com/documentation/xcode/xcode-cloud)
- [Getting started with Xcode Cloud](https://developer.apple.com/documentation/xcode/getting-started-with-xcode-cloud)
- [Setting up your project to use Xcode Cloud](https://developer.apple.com/documentation/xcode/setting-up-your-project-to-use-xcode-cloud)
- [Configuring your first Xcode Cloud workflow](https://developer.apple.com/documentation/xcode/configuring-your-first-xcode-cloud-workflow)
- [Xcode Cloud workflow reference](https://developer.apple.com/documentation/xcode/xcode-cloud-workflow-reference)
- [Developing a workflow strategy for Xcode Cloud](https://developer.apple.com/documentation/xcode/developing-a-workflow-strategy-for-xcode-cloud)
- [Configuring your Xcode Cloud workflow’s actions](https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions)
- [Creating a workflow that builds your app for distribution](https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution)
- [Distributing your Xcode Cloud builds through TestFlight](https://developer.apple.com/documentation/xcode/distributing-your-xcode-cloud-builds-through-testflight)
- [Writing custom build scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts)
- [Environment variable reference](https://developer.apple.com/documentation/xcode/environment-variable-reference)
- [Sharing environment variables across Xcode Cloud workflows](https://developer.apple.com/documentation/xcode/sharing-environment-variables-across-xcode-cloud-workflows)
- [Making dependencies available to Xcode Cloud](https://developer.apple.com/documentation/xcode/making-dependencies-available-to-xcode-cloud)
- [Configuring requirements for merging a pull request](https://developer.apple.com/documentation/xcode/configuring-requirements-for-merging-a-pull-request)
- [Resolving common configuration and build issues](https://developer.apple.com/documentation/xcode/resolving-common-configuration-and-build-issues)
- [Understanding Xcode Cloud infrastructure validation builds](https://developer.apple.com/documentation/xcode/understanding-infrastructure-validation-builds)
- [Configuring webhooks in Xcode Cloud](https://developer.apple.com/documentation/xcode/configuring-webhooks-in-xcode-cloud)
- [Xcode Cloud Workflows and Builds](https://developer.apple.com/documentation/appstoreconnectapi/xcode-cloud-workflows-and-builds)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview)

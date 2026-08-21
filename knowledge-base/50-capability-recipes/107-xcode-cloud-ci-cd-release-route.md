# Xcode Cloud CI/CD release route

## Route contract

Use this route when an iOS app needs repeatable cloud builds, selected test
plans, pull-request confidence, release-candidate archives, TestFlight
delivery, and a retained proof packet.

This is a route contract, not a claim that the current workspace is connected
to Xcode Cloud. Apply it to a named repository, product, team, workflow, and
App Store Connect record.

Related pages:

- [Xcode Cloud CI/CD and release automation](../42-framework-deep-dives/76-xcode-cloud-ci-cd-and-release-automation.md)
- [CI release confidence and native design](../21-design-deep-dives/104-ci-release-confidence-and-native-design.md)
- [Xcode Cloud CI/CD proof matrix](../60-verification/101-xcode-cloud-ci-cd-proof-matrix.md)
- [Xcode Cloud CI/CD release recipes](../70-code-recipes/119-xcode-cloud-ci-cd-release-recipes.md)
- [Xcode archive, signing, TestFlight, and release route](106-xcode-archive-signing-testflight-route.md)

## Route map

    qualify project
      -> connect source control and team
      -> configure first simple workflow
      -> prove build and test actions
      -> split fast, broad, and distribution workflows
      -> add scripts, variables, and dependencies safely
      -> enforce pull-request requirements
      -> archive and distribute to TestFlight
      -> retain artifacts and reconcile App Store Connect
      -> run physical/release gates
      -> submit or release through the named human decision

## Phase 0: qualify the product

Write a route record before opening Xcode Cloud:

| Field | Example record |
| --- | --- |
| Repository | Provider and exact repository |
| Product | App/framework name and bundle identifier |
| Team | Redacted developer-team identifier |
| Scheme | Shared scheme used for build/test/archive |
| Targets | App, extensions, widgets, watch products, packages |
| Minimum OS | Selected deployment target and supported families |
| Test plans | Fast, UI/accessibility, release-candidate plans |
| Distribution | Internal TestFlight, external TestFlight, App Store, or none |
| AI | Model/API/profile, fallback, evaluation dataset |
| Glass | System route, custom functional surfaces, accessibility states |
| Artifact owner | Person/system that downloads and retains symbols/results |

Stop if the product cannot be built from a clean checkout, the scheme is not
shared, the intended target has no archive action, or the bundle identifier
does not have a deliberate App Store Connect ownership path.

## Phase 1: connect source control

1. Confirm the team is enrolled in the Apple Developer Program.
2. Confirm the SCM provider and the permission required to grant Xcode Cloud
   access.
3. Connect the repository from Xcode’s Cloud setup flow.
4. Confirm the branch/tag/PR references that the workflow will use.
5. Commit the shared scheme, test plans, package resolution, privacy
   manifests, and ci_scripts resources required by the build.
6. Record the commit used for the first build.

The source-control connection is not a release credential. Keep provider
permissions, developer-team access, App Store Connect roles, and workflow edit
roles documented separately.

## Phase 2: create the first simple workflow

Start with one product and a small workflow:

| Setting | First choice |
| --- | --- |
| Environment | A known Xcode/macOS combination |
| Start | Main/default branch change or deliberate manual start |
| Action | Build or a short test action |
| Destination | One deterministic simulator |
| Post-action | None |
| Scripts | None unless the project requires them |
| Distribution | None |

Run the build and record:

- workflow name and ID;
- source commit;
- environment;
- action and scheme;
- build status;
- logs and result bundle;
- warnings/issues;
- artifact identifiers and retention location.

Keep the first workflow simple enough that a failure has one likely cause.
Only add TestFlight, custom scripts, or broad destination matrices after the
basic build is understood.

## Phase 3: configure the workflow family

Translate the quality strategy into separate workflows:

| Workflow | Trigger | Actions | Side effects |
| --- | --- | --- | --- |
| Pull request confidence | PR changes | Build, fast tests, selected analyzer | SCM status only |
| Branch integration | Development branch changes | Build, unit tests, focused UI tests | Team notification |
| Broad verification | Schedule or selected branch | Long UI/accessibility/performance test plan | Artifacts and report |
| Release candidate | Release tag or manual condition | Clean archive, required tests, analyzer | Retained archive and symbols |
| Internal beta | Manual/tag after release gate | Archive plus internal TestFlight post-action | Internal tester update |
| External beta | Deliberate release workflow | Archive plus TestFlight and App Store preparation | External review decision |

Use the workflow reference to select branch, pull-request, tag, or schedule
conditions. Configure auto-cancel for high-churn feedback workflows and
disable it when every run is a required artifact or an audit record.

Restrict workflow editing for release paths. Duplicate a workflow before a
substantial change, and deactivate an old workflow when history and artifacts
must remain available. Deleting a workflow can delete its build history and
artifacts.

## Phase 4: add actions and test plans

For every action, record the command boundary and evidence:

| Action | Configuration | Proof |
| --- | --- | --- |
| Build | Platform, scheme, any-device or simulator destination | Product, logs, result bundle |
| Test | Scheme settings or named test plan, required-to-pass setting, destinations | Test products, result bundle, test failure list |
| Analyze | Scheme and configuration | Analyzer output and warnings |
| Archive | Platform, scheme, Deployment Preparation | Archive/exported app and logs |

If using a test plan, record the plan name, selected configurations, tags,
excluded tests, destination, and whether the result is required to pass.
Running a different plan locally does not prove the cloud plan.

The test action’s build-for-testing and test-without-building phases have
different inputs. Keep fixture resources and test-runner environment values
available through the supported paths. Do not assume source files are present
in the test-runner phase.

## Phase 5: add scripts and environment safely

Add only the script phase needed:

    ci_post_clone.sh
      -> prepare tools and repository resources
    ci_pre_xcodebuild.sh
      -> validate action/configuration and generate bounded inputs
    ci_post_xcodebuild.sh
      -> collect diagnostics or approved artifacts

Script rules:

- use strict failure behavior;
- check the current Xcode action before doing action-specific work;
- write useful, redacted diagnostics;
- return a nonzero exit status for a real failure;
- never modify source to bypass a failing test;
- never print secrets or private signing material;
- make external calls idempotent because infrastructure validation builds
  can repeat script execution;
- store custom script resources in the documented ci_scripts path.

Use predefined variables such as the build ID, commit, workflow, scheme,
action, result bundle, archive, and signed-app paths to name artifacts. Keep
custom variables workflow-scoped unless they genuinely need to be shared.
Mark secrets as redacted and rotate them outside the source repository.

## Phase 6: make dependencies deterministic

Validate every dependency from a clean checkout:

- commit the selected package-resolution file;
- confirm package products are linked to the intended targets;
- make private packages available through the supported repository access path;
- install third-party tools in a repeatable bounded script;
- avoid mutable downloads without a version/checksum policy;
- respect Xcode Cloud’s proxy variables when a tool performs network access;
- record the tool version in the build artifact or log;
- do not make package resolution silently change during an archive.

The goal is a build that can be explained by repository, toolchain, resolved
dependencies, workflow, and environment—not by a personal Mac.

## Phase 7: enforce pull-request confidence

Configure a PR-change workflow, then configure the SCM provider’s branch
protection:

1. start a cloud build for each relevant PR change;
2. report the build or selected action status to the SCM provider;
3. require the full build or a named action before merging stable branches;
4. document exceptions for feature branches or non-required workflows;
5. test a failing PR and verify the merge is actually blocked;
6. test a passing PR and record the status transition.

A status displayed on a pull request is not automatically a merge rule. Branch
protection belongs to the SCM provider and has its own permission and evidence
boundary.

## Phase 8: create the distribution workflow

For an internal beta:

1. create or confirm the App Store Connect app record;
2. verify team, app name, bundle ID, version/build policy, and internal group;
3. create an archive action;
4. choose TestFlight (Internal Testing Only);
5. add the internal TestFlight post-action;
6. start from an explicit branch/tag and record the commit;
7. wait for App Store Connect processing;
8. verify the build is assigned to the intended tester group;
9. install and exercise the build on the named physical device.

For an external beta or App Store candidate, choose TestFlight and App Store
deployment preparation, complete the archive/privacy/signing checks, and keep
external beta review, App Review submission, and release publication as
separate human-approved steps.

## Phase 9: retain and reconcile artifacts

Download the build packet before the cloud retention window expires:

    workflow + build + commit
      + environment and action settings
      + logs and issue counts
      + test result bundle and screenshots
      + archive, app binary, dSYM, and signed entitlements
      + privacy manifest/report
      + App Store Connect processing/build record
      + TestFlight group and tester notes
      + physical-device result and known gaps

Store a checksum and an access-controlled copy. The artifact archive is part
of release recovery and crash-symbol diagnosis, not merely a compliance
attachment.

## Phase 10: prove the native and AI feature gates

Before calling the workflow release-ready:

- run the signed Release/TestFlight build on a named physical device;
- verify Liquid Glass interaction, contrast, Dynamic Type, reduced effects,
  VoiceOver, and hit regions;
- verify system-owned widgets, controls, App Intents, and notifications from
  their real host surfaces when claimed;
- verify Foundation Models/Core ML availability, model/profile/version,
  cancellation, refusal/error fallback, and side-effect review;
- compare AI evaluation fixture results with the selected baseline;
- attach the build identity to all observations;
- distinguish simulator, cloud, physical, TestFlight, App Review, and
  production evidence.

## Route stop conditions

Stop the route when:

- the workflow is building a different scheme or commit than intended;
- signing or entitlements are inferred from checkboxes rather than the signed
  artifact;
- a custom script receives or prints unredacted secrets;
- the archive or privacy report is missing from the release packet;
- a TestFlight post-action was configured but processing or tester assignment
  was not observed;
- a model output or glass screenshot is being used as proof of a release gate;
- a passing PR status is claimed to block merges without SCM branch-protection
  evidence;
- the cloud build is being called a physical-device or App Review result.

## Sources

- [Xcode Cloud](https://developer.apple.com/documentation/xcode/xcode-cloud)
- [Getting started with Xcode Cloud](https://developer.apple.com/documentation/xcode/getting-started-with-xcode-cloud)
- [Setting up your project to use Xcode Cloud](https://developer.apple.com/documentation/xcode/setting-up-your-project-to-use-xcode-cloud)
- [Configuring your first Xcode Cloud workflow](https://developer.apple.com/documentation/xcode/configuring-your-first-xcode-cloud-workflow)
- [Xcode Cloud workflow reference](https://developer.apple.com/documentation/xcode/xcode-cloud-workflow-reference)
- [Configuring your Xcode Cloud workflow’s actions](https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions)
- [Developing a workflow strategy for Xcode Cloud](https://developer.apple.com/documentation/xcode/developing-a-workflow-strategy-for-xcode-cloud)
- [Creating a workflow that builds your app for distribution](https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution)
- [Distributing your Xcode Cloud builds through TestFlight](https://developer.apple.com/documentation/xcode/distributing-your-xcode-cloud-builds-through-testflight)
- [Writing custom build scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts)
- [Environment variable reference](https://developer.apple.com/documentation/xcode/environment-variable-reference)
- [Sharing environment variables across Xcode Cloud workflows](https://developer.apple.com/documentation/xcode/sharing-environment-variables-across-xcode-cloud-workflows)
- [Making dependencies available to Xcode Cloud](https://developer.apple.com/documentation/xcode/making-dependencies-available-to-xcode-cloud)
- [Configuring requirements for merging a pull request](https://developer.apple.com/documentation/xcode/configuring-requirements-for-merging-a-pull-request)
- [Resolving common configuration and build issues](https://developer.apple.com/documentation/xcode/resolving-common-configuration-and-build-issues)
- [Understanding Xcode Cloud infrastructure validation builds](https://developer.apple.com/documentation/xcode/understanding-infrastructure-validation-builds)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview)

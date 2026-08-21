# Xcode Cloud CI/CD proof matrix

## Purpose

Use this matrix to keep cloud workflow evidence, signed distribution evidence,
and native-device evidence separate. A passing Xcode Cloud build is valuable,
but it does not automatically prove a physical iPhone run, TestFlight
processing, App Review, or production delivery.

Related routes:

- [Xcode Cloud CI/CD and release automation](../42-framework-deep-dives/76-xcode-cloud-ci-cd-and-release-automation.md)
- [CI release confidence and native design](../21-design-deep-dives/104-ci-release-confidence-and-native-design.md)
- [Xcode Cloud CI/CD release route](../50-capability-recipes/107-xcode-cloud-ci-cd-release-route.md)
- [Xcode Cloud CI/CD release recipes](../70-code-recipes/119-xcode-cloud-ci-cd-release-recipes.md)

## Evidence levels

| Level | Evidence packet | Proves | Does not prove |
| --- | --- | --- | --- |
| C0 | Official source and route record | The intended Apple workflow and claim boundary | A project is configured |
| C1 | Project/workspace, shared scheme, target graph, test plans, package resolution | The repository contains the intended build inputs | Xcode Cloud can access or build them |
| C2 | Xcode Cloud workflow record | Product, repository, environment, start condition, actions, and post-actions | The workflow has run |
| C3 | Build/run record | Selected commit and action completed in a temporary cloud environment | A different action, target, device, or release gate |
| C4 | Test result bundle and logs | Selected test plan/configuration/destination produced the recorded result | Physical-device behavior or unselected tests |
| C5 | Archive and signed inspection | Selected target produced an archive with inspected identity, resources, entitlements, and privacy files | App Store Connect processing or tester installation |
| C6 | App Store Connect processing/build record | Apple accepted and processed the uploaded build for the app/version | TestFlight task completion, external beta review, or App Store release |
| C7 | TestFlight record and tester run | Named tester group installed/exercised the named build | App Review approval, production rollout, or every device |
| C8 | SCM branch-protection result | A configured provider rule blocks/permits a merge based on the selected status | All release checks or production health |
| C9 | Physical Release/TestFlight/system run | Named device, OS, account, permissions, and system surface exercised the named build | Other devices, future builds, or App Review |
| C10 | Release and post-release packet | App Store Connect version, release option, and observed rollout state | Future source revisions or unrelated claims |

## Workflow identity matrix

| Claim | Minimum record | Stop condition |
| --- | --- | --- |
| This build came from the intended source | Repository, ref, commit hash, workflow/build ID | Only a branch name or latest-build label is recorded |
| This workflow used the intended project | Product, bundle ID, workspace/project, shared scheme | The workflow’s scheme or product is inferred |
| This was a Release candidate | Archive action, configuration/environment, Deployment Preparation | A Debug or generic build is labeled release |
| This test result is authoritative for the route | Test plan, configurations/tags, destination, required-to-pass policy, result bundle | A different local plan is substituted |
| This archive contains the claimed surface | Product inventory, extension list, resources, entitlements, privacy manifests | Target checkbox or source file is the only evidence |
| This build reached TestFlight | Upload/build ID, processing status, group assignment | Archive or upload command is treated as processing |

## Start-condition proof

| Trigger | Required test | Evidence |
| --- | --- | --- |
| Branch change | Commit a controlled change and observe one intended workflow | SCM event, build ID, source commit, action result |
| Pull request | Open/update a PR and observe the workflow/status | PR, source/destination branch, status, action result |
| Git tag | Create a controlled tag matching the rule | Tag, commit, workflow, archive/distribution record |
| Schedule | Observe the scheduled run in the intended window | Schedule, start time, build ID, no unintended side effect |
| Manual-only | Start the workflow deliberately | Operator, commit/ref, start request, result |
| Auto-cancel | Queue a newer build while one is running | Cancellation reason and newer build identity |

Do not claim trigger behavior from a workflow screenshot. The event and the
resulting build must be tied by source revision and workflow identity.

## Action proof

| Action | Required inputs | Required outputs |
| --- | --- | --- |
| Build | Platform, scheme, destination, environment | Build product, logs, result bundle, warnings/issues |
| Test | Scheme/test plan, configuration, destinations, required-to-pass policy | Test products, result bundle, test failures, screenshots if produced |
| Analyze | Scheme, environment, analyzer policy | Analyzer result, warnings, suppressions/decisions |
| Archive | Platform, scheme, clean/cache policy, Deployment Preparation | Archive/export, logs, signed identity, dSYM/symbols |
| TestFlight post-action | Processed build, tester group, internal/external policy | App Store Connect/TestFlight assignment and build identity |
| Webhook | HTTPS endpoint, event delivery, response policy | Delivery report, idempotent receiver record, redacted payload handling |

An action that is “not required to pass” should be shown as non-blocking in
the evidence packet. Do not summarize the workflow as fully verified when a
required surface was intentionally excluded.

## Test-plan and UI proof

| Claim | Required evidence |
| --- | --- |
| Unit/model logic passes | Named test plan or test target, deterministic fixtures, result bundle |
| UI flow passes | Launch fixture, semantic queries/identifiers, destination, user task result |
| Accessibility task passes | VoiceOver/Voice Control/Switch Control or relevant setting, task script, observed result |
| Performance baseline exists | Workload, device/destination, configuration, iterations, metric/result bundle |
| AI adapter is stable | Availability/error/cancellation fixtures, schema/validation tests, model/profile/prompt version |
| Liquid Glass state is usable | State coverage, contrast/Dynamic Type/reduced-effects fixtures, named device run for interaction |

An accessibility identifier proves a test hook exists. It does not prove that
the user can understand the result, move focus, or complete the task.

## Artifact and signing proof

| Artifact | Inspect |
| --- | --- |
| Build product | Bundle ID, version/build, resources, target membership |
| Test result bundle | Tests, diagnostics, screenshots, destination, failure details |
| Archive | Archive Info, products, embedded extensions, frameworks, assets, dSYM |
| App bundle | Info.plist, privacy manifests, URL schemes, usage strings, architectures |
| Signed bundle | Team, code signature, entitlements, provisioning/distribution identity |
| Privacy report | App/SDK manifests and required-reason API declarations |
| Symbol archive | dSYM identity matches the shipped binary and build |

Keep the workflow artifact’s URL/ID, download timestamp, checksum, and
retention location. Xcode Cloud artifact retention is time-limited; a release
team should download and archive the packet before expiration.

## App Store Connect and TestFlight proof

| Gate | Evidence | Not enough |
| --- | --- | --- |
| Upload accepted | Upload record and App Store Connect build identity | xcodebuild/export success |
| Processing complete | Processed status for the expected app/version/build | “Uploaded” message |
| Internal TestFlight | Build assigned to internal group and install on a named device | Processed build alone |
| External TestFlight | External group, beta review state, tester assignment, install/feedback | Internal tester run |
| App Review candidate | Correct processed build selected for version and required metadata | TestFlight availability |
| Release | Version release option and observed availability/rollout | Approval or submission screen |

Record the distinction between internal and external testing. External beta
review and App Review are separate Apple-mediated decisions.

## Workflow quality and failure proof

| Failure claim | Required evidence |
| --- | --- |
| The build failed for source/configuration reasons | Failed action, commit, environment, logs, result bundle, reproduced local action |
| The build failed because of a dependency | Package-resolution state, dependency source/version, cloud log, local reproduction |
| The failure is fixed | Corrected commit, same workflow/action, passing result, changed artifact |
| The workflow is safe to retry | Idempotent script policy, no duplicate external side effect, build identity |
| Infrastructure validation is not the cause | Xcode Cloud validation setting, duplicate-call observation, script event record |
| Webhook delivery works | Endpoint status/response, delivery report, event ID, replay-safe handler |

Do not delete a workflow that contains forensic history merely to make a
dashboard green. Deactivate or retain it according to the project’s recovery
policy.

## Pull-request merge proof

To claim branch protection:

1. configure a pull-request-change workflow;
2. publish the build or action status to the SCM provider;
3. configure the provider’s required status/check;
4. submit a controlled failing PR and verify merge is blocked;
5. correct the failure and verify merge becomes permitted;
6. record provider, branch, required check, role, and exception policy.

The Xcode Cloud status and the SCM branch-protection rule are separate records.
A green status shown on a PR without a required check is informational only.

## AI and Liquid Glass release gates

| Surface | CI evidence | Device/release evidence |
| --- | --- | --- |
| Foundation Models | Guarded adapter, deterministic validation, refusal/error/cancellation tests, evaluation dataset | Model availability, language, latency, thermal behavior, privacy, fallback, reviewable side effects |
| Core ML/Vision | Resource membership, typed features, deterministic preprocessing/inference tests | Real camera/media input, model asset load, GPU/ANE behavior, physical performance and permission state |
| Liquid Glass | Semantic control tests, layout/adaptation fixtures, reduced-motion/contrast checks | Signed Release/TestFlight interaction, legibility, hit region, VoiceOver, Dynamic Type, reduced transparency |
| App Intents/widget/control | Target compile and intent/entity fixtures | Signed target membership, system invocation, locked/background behavior, App Store metadata |

Never promote a model score, screenshot, preview, simulator run, or CI status
to a device/release claim without the matching packet.

## Minimum release packet

Before calling an Xcode Cloud distribution workflow ready, retain:

- workflow configuration and start condition;
- repository/ref/commit and project/scheme/product identity;
- Xcode/macOS environment and action/test-plan settings;
- build logs, issue counts, test result bundles, and screenshots;
- archive, app binary, dSYM, signed entitlements, and privacy report;
- App Store Connect upload/processing/build record;
- TestFlight group, tester notes, install, update, and feedback record;
- physical-device/system/accessibility result;
- AI/Liquid Glass gate results and known gaps;
- human release decision and rollback/recovery pointer.

## Sources

- [Xcode Cloud](https://developer.apple.com/documentation/xcode/xcode-cloud)
- [Xcode Cloud workflow reference](https://developer.apple.com/documentation/xcode/xcode-cloud-workflow-reference)
- [Configuring your Xcode Cloud workflow’s actions](https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions)
- [Configuring requirements for merging a pull request](https://developer.apple.com/documentation/xcode/configuring-requirements-for-merging-a-pull-request)
- [Writing custom build scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts)
- [Environment variable reference](https://developer.apple.com/documentation/xcode/environment-variable-reference)
- [Understanding Xcode Cloud infrastructure validation builds](https://developer.apple.com/documentation/xcode/understanding-infrastructure-validation-builds)
- [Configuring webhooks in Xcode Cloud](https://developer.apple.com/documentation/xcode/configuring-webhooks-in-xcode-cloud)
- [Xcode Cloud Workflows and Builds](https://developer.apple.com/documentation/appstoreconnectapi/xcode-cloud-workflows-and-builds)
- [Creating a workflow that builds your app for distribution](https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution)
- [Distributing your Xcode Cloud builds through TestFlight](https://developer.apple.com/documentation/xcode/distributing-your-xcode-cloud-builds-through-testflight)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)

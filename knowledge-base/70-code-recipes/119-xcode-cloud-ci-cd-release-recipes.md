# Xcode Cloud CI/CD release recipes

## How to use these recipes

These are compile-oriented and operational route sketches. Xcode Cloud
workflows are configured through Xcode and App Store Connect; the YAML below is
a redacted evidence record, not a claim that Xcode Cloud consumes that file as
its workflow definition.

Apply the recipes to a named project and keep secrets outside source and logs.
Use the [Xcode Cloud route](../50-capability-recipes/107-xcode-cloud-ci-cd-release-route.md),
the [proof matrix](../60-verification/101-xcode-cloud-ci-cd-proof-matrix.md),
the [native design contract](../21-design-deep-dives/104-ci-release-confidence-and-native-design.md),
and the [CI/CD deep dive](../42-framework-deep-dives/76-xcode-cloud-ci-cd-and-release-automation.md).

## Redacted workflow record

Keep the project configuration and the evidence record separate:

~~~yaml
product: ExampleApp
bundle_id: com.example.app
repository: redacted-provider/repository
workflow: Release Candidate
environment:
  xcode: record-version
  macos: record-version
start_condition: release-tag-or-manual
actions:
  - test:
      plan: ReleaseCandidate
      destinations:
        - named-simulator
      required_to_pass: true
  - archive:
      deployment_preparation: TestFlight and App Store
post_actions:
  - testflight_group: redacted-group
secrets:
  - name: REDACTED_KEY
    redacted: true
artifacts:
  retention_owner: release-owner
  archive: artifacts/ExampleApp.xcarchive
  result_bundle: artifacts/release-tests.xcresult
known_gaps:
  - physical-device-run-pending
~~~

Record the exact settings in Xcode/App Store Connect and attach the workflow
ID, build ID, commit, logs, results, archive, and processing record. Never add
certificate private keys, provisioning secrets, API keys, JWTs, or tokens to
this record.

## Find archivable products

Before onboarding a project, inspect the products Xcode can archive:

~~~sh
xcodebuild \
  -project ExampleApp.xcodeproj \
  -describeAllArchivableProducts \
  -json
~~~

For a workspace, use the workspace argument. Compare the output with the
products expected in Xcode Cloud: app targets, extensions, widgets, watch
products, and frameworks. If a product is missing, inspect scheme sharing and
the Archive action before configuring a workflow.

## Run local parity actions

Use explicit local commands to reproduce a cloud action from the same commit:

~~~sh
xcodebuild \
  -project ExampleApp.xcodeproj \
  -scheme ExampleApp \
  -configuration Debug \
  -destination "platform=iOS Simulator,name=Named Simulator" \
  build

xcodebuild \
  -project ExampleApp.xcodeproj \
  -scheme ExampleApp \
  -testPlan FastCI \
  -destination "platform=iOS Simulator,name=Named Simulator" \
  -resultBundlePath artifacts/fast-ci.xcresult \
  test
~~~

Use the project’s actual destination and plan. A local command is parity
evidence for diagnosis, not proof that the cloud workflow used the same
settings.

## Release-candidate archive

Run a local archive with an explicit Release configuration to diagnose an
Xcode Cloud archive failure:

~~~sh
xcodebuild \
  -project ExampleApp.xcodeproj \
  -scheme ExampleApp \
  -configuration Release \
  -destination "generic/platform=iOS" \
  -archivePath artifacts/ExampleApp.xcarchive \
  archive
~~~

Capture the selected Xcode version, SDK, commit, exit status, archive path,
and log. Then inspect the archive and signed product before treating a cloud
archive as equivalent.

## Custom post-clone script

Use ci_post_clone.sh for preparation that must happen after the repository is
cloned. Keep it deterministic and bounded:

~~~sh
#!/bin/sh
set -eu

ACTION=$(printenv CI_XCODEBUILD_ACTION 2>/dev/null || true)
echo "post-clone action: $ACTION"

if [ "$ACTION" = "archive" ]; then
  echo "release archive preparation selected"
fi

if [ -f "$CI_PRIMARY_REPOSITORY_PATH/Package.resolved" ]; then
  echo "Package.resolved is present"
else
  echo "Package.resolved is missing"
  exit 1
fi
~~~

Do not install an unpinned tool or rewrite package resolution just to make a
single build pass. If an external tool is necessary, record its version and
verify the download/checksum policy.

## Custom pre-build script

Use ci_pre_xcodebuild.sh to validate inputs before the Xcode action:

~~~sh
#!/bin/sh
set -eu

ACTION=$(printenv CI_XCODEBUILD_ACTION 2>/dev/null || true)
SCHEME=$(printenv CI_XCODE_SCHEME 2>/dev/null || true)
BUILD_ID=$(printenv CI_BUILD_ID 2>/dev/null || true)

echo "build $BUILD_ID"
echo "scheme $SCHEME"
echo "action $ACTION"

if [ -z "$SCHEME" ]; then
  echo "missing scheme"
  exit 1
fi

case "$ACTION" in
  build|test|build-for-testing|test-without-building|archive|analyze)
    ;;
  *)
    echo "unknown action"
    exit 1
    ;;
esac
~~~

Only log non-sensitive identifiers. Do not print environment variables in bulk:
an apparently harmless diagnostic can disclose a secret custom variable.

## Custom post-build artifact manifest

Use ci_post_xcodebuild.sh to create a small manifest after a successful action.
The manifest should point to artifacts rather than copy secrets:

~~~sh
#!/bin/sh
set -eu

RESULT=$(printenv CI_RESULT_BUNDLE_PATH 2>/dev/null || true)
ARCHIVE=$(printenv CI_ARCHIVE_PATH 2>/dev/null || true)
BUILD_ID=$(printenv CI_BUILD_ID 2>/dev/null || true)
COMMIT=$(printenv CI_COMMIT 2>/dev/null || true)

mkdir -p "$CI_WORKSPACE_PATH/release-manifest"
{
  echo "build_id=$BUILD_ID"
  echo "commit=$COMMIT"
  echo "result_bundle=$RESULT"
  echo "archive=$ARCHIVE"
} > "$CI_WORKSPACE_PATH/release-manifest/identity.txt"

if [ -n "$RESULT" ] && [ ! -e "$RESULT" ]; then
  echo "result bundle path is not available"
  exit 1
fi
~~~

The exact artifact paths vary by action. Verify the path in the workflow’s
build report and retain the manifest with the downloaded artifacts.

## Redacted secret use

Use a secret custom environment variable only for the smallest approved
operation:

~~~sh
#!/bin/sh
set -eu

TOKEN_PRESENT=$(printenv RELEASE_UPLOAD_TOKEN >/dev/null 2>&1 && echo yes || echo no)
echo "release token configured: $TOKEN_PRESENT"

if [ "$TOKEN_PRESENT" != "yes" ]; then
  echo "required release token is not configured"
  exit 1
fi

# Call the approved tool here without echoing its arguments or token.
~~~

Mark the variable as redacted in Xcode Cloud. Redaction protects log output;
it does not make an unreviewed upload or webhook safe. Prefer Apple’s native
TestFlight post-action for TestFlight delivery when it satisfies the route.

## Local test-plan parity

Run the same named plan locally when diagnosing a cloud test action:

~~~sh
xcodebuild \
  -scheme ExampleApp \
  -configuration Release \
  -testPlan ReleaseCandidate \
  -destination "platform=iOS Simulator,name=Named Simulator" \
  -resultBundlePath artifacts/release-candidate.xcresult \
  test
~~~

Record the plan’s configurations, tags, excluded tests, destination, and
required-to-pass policy. A passing FastCI plan is not a passing
ReleaseCandidate plan.

## Inspect a downloaded artifact packet

After a cloud build completes, download the logs, result bundle, archive,
binary, symbols, and issue/test records. Then make a manifest:

~~~sh
find artifacts -type f -print | sort > artifacts/file-list.txt
shasum -a 256 artifacts/file-list.txt > artifacts/file-list.sha256

plutil -p artifacts/ExampleApp.xcarchive/Info.plist
find artifacts/ExampleApp.xcarchive/Products -maxdepth 4 -type f | sort
find artifacts/ExampleApp.xcarchive/dSYMs -maxdepth 2 -type f | sort
~~~

The checksum file identifies the local packet; it does not replace the
App Store Connect build ID or TestFlight processing record.

## Inspect signed product and privacy resources

Use explicit validated paths after extracting the archive:

~~~sh
APP="artifacts/ExampleApp.xcarchive/Products/Applications/ExampleApp.app"
plutil -p "$APP/Info.plist"
find "$APP" -name "PrivacyInfo.xcprivacy" -print
find "$APP/PlugIns" -maxdepth 2 -name "Info.plist" -print
codesign --display --verbose=4 "$APP"
codesign -d --entitlements :- "$APP" > artifacts/app-entitlements.plist
~~~

Inspect embedded extensions separately. Compare the signed result with the
workflow’s selected product, capability, privacy, version/build, and system
surface claims.

## TestFlight distribution handoff

Keep the handoff record human-readable:

~~~yaml
app_record: redacted-app-record
workflow: Internal Beta
commit: record-commit
version: 1.0.0
build: 42
processing: complete
tester_group: internal-team
what_to_test: Test the new local review and export flow.
device_run:
  device: named-physical-device
  os: record-os
  result: pass-with-known-gap
known_gaps:
  - external-beta-review-not-requested
~~~

Do not set processing to complete from a cloud post-action log. Read the
processed build state in App Store Connect and verify the tester assignment and
physical install.

## Release-aware AI gate

Use deterministic checks around a model-powered feature:

~~~text
source fixture
  -> availability guard
  -> model/profile/prompt version record
  -> model output
  -> typed validation and policy checks
  -> human review or deterministic domain commit
~~~

Record refusal, context-limit, cancellation, timeout, and unavailable-model
paths. A model score or generated summary is not authorization to distribute a
build or mutate a customer record.

## Release-aware Liquid Glass gate

Exercise the signed build in:

- light and dark appearance;
- increased contrast and reduced transparency;
- large Dynamic Type;
- VoiceOver and keyboard/pointer paths;
- reduced motion;
- compact width and iPad layout;
- failed, pending, and disabled action states.

Assert the semantic action and user-visible result, not only a screenshot.
Keep the underlying log, build identity, and next safe action visible.

## Final CI/CD checklist

- [ ] Product, repository, team, bundle ID, and shared scheme are recorded.
- [ ] Xcode/macOS environment and start condition are recorded.
- [ ] Build/test/analyze/archive action policies are explicit.
- [ ] Test plans, destinations, and required-to-pass rules are named.
- [ ] Package resolution and custom tools are deterministic.
- [ ] ci_scripts phases are bounded, idempotent, and non-secret.
- [ ] PR status and SCM branch protection were tested separately.
- [ ] Archive, signed product, privacy report, and symbols were inspected.
- [ ] App Store Connect processing and build identity were observed.
- [ ] TestFlight group, notes, install, and feedback are recorded.
- [ ] Physical Release/TestFlight device and system-surface gates are complete.
- [ ] AI and Liquid Glass states have explicit fallback and accessibility proof.
- [ ] Release decision, known gaps, and artifact retention owner are recorded.

## Sources

- [Xcode Cloud](https://developer.apple.com/documentation/xcode/xcode-cloud)
- [Getting started with Xcode Cloud](https://developer.apple.com/documentation/xcode/getting-started-with-xcode-cloud)
- [Configuring your first Xcode Cloud workflow](https://developer.apple.com/documentation/xcode/configuring-your-first-xcode-cloud-workflow)
- [Xcode Cloud workflow reference](https://developer.apple.com/documentation/xcode/xcode-cloud-workflow-reference)
- [Configuring your Xcode Cloud workflow’s actions](https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions)
- [Creating a workflow that builds your app for distribution](https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution)
- [Distributing your Xcode Cloud builds through TestFlight](https://developer.apple.com/documentation/xcode/distributing-your-xcode-cloud-builds-through-testflight)
- [Writing custom build scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts)
- [Environment variable reference](https://developer.apple.com/documentation/xcode/environment-variable-reference)
- [Sharing environment variables across Xcode Cloud workflows](https://developer.apple.com/documentation/xcode/sharing-environment-variables-across-xcode-cloud-workflows)
- [Making dependencies available to Xcode Cloud](https://developer.apple.com/documentation/xcode/making-dependencies-available-to-xcode-cloud)
- [Configuring requirements for merging a pull request](https://developer.apple.com/documentation/xcode/configuring-requirements-for-merging-a-pull-request)
- [Configuring webhooks in Xcode Cloud](https://developer.apple.com/documentation/xcode/configuring-webhooks-in-xcode-cloud)
- [Resolving common configuration and build issues](https://developer.apple.com/documentation/xcode/resolving-common-configuration-and-build-issues)
- [Understanding Xcode Cloud infrastructure validation builds](https://developer.apple.com/documentation/xcode/understanding-infrastructure-validation-builds)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Liquid Glass technology overview](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)

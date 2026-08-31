# Meta Wearables target preflight

Run this packet before connected, physical, signed, or release-channel work.
It freezes the target and dependency facts that make a later result
reproducible. The commands are inspection/build-observation templates; run them
inside the selected target repository and preserve their redacted output.

## Contents

- [Preflight identity](#preflight-identity)
- [iOS DAT lane](#ios-dat-lane)
- [Android DAT lane](#android-dat-lane)
- [Web App lane](#web-app-lane)
- [Cross-platform and privacy checks](#cross-platform-and-privacy-checks)
- [Preflight task IDs](#preflight-task-ids)
- [Evidence interpretation](#evidence-interpretation)
- [Preflight handoff](#preflight-handoff)
- [Sources](#sources)

## Preflight identity

Create a run record before commands execute:

```text
run_id: <UTC timestamp + local run label; never include a secret>
route: native-dat-ios | native-dat-android | native-display | web-app | phone-fallback
outcome: <one user-visible result>
source_revision: <DAT tag/commit, Web App commit, docs date>
app_repository: <redacted path or repository URL>
app_target_or_module: <scheme/target or Gradle module or Web App package>
configuration: <Debug/Release/profile/channel>
os_and_toolchain: <iOS/Xcode/Swift or Android/AGP/Kotlin/Gradle or Node/browser>
package_or_artifact: <exact resolved DAT product/artifact and version>
web_revision: <hosted revision if applicable>
device_tuple: <product/SKU, runtime DeviceType, phone, companion, firmware, DAT-app>
account_mode: developer-mode | release-channel | unavailable | not-run
requested_capabilities: <camera/audio/display/input/sensor/etc.>
processing_claim: glasses-native | phone-local | remote | mixed | unknown
```

Do not fill `device_tuple`, `account_mode`, or `processing_claim` from a
consumer label. Unknown remains `to-verify` or `not-run`.

## iOS DAT lane

Run from the actual Xcode project/workspace. Prefer JSON output where the tool
supports it and redact paths, bundle identifiers, account values, and callback
query data before storing the result.

```bash
# Inventory projects, schemes, and targets.
xcodebuild -list -json -project <App>.xcodeproj
# Use -workspace instead when the target is workspace-owned.

# Resolve the settings that the selected scheme would use; do not substitute
# a simulator or a different scheme for the requested target.
xcodebuild -showBuildSettings -json \
  -project <App>.xcodeproj \
  -scheme <Scheme> \
  -configuration <Debug|Release>

# Locate and inspect the committed SwiftPM lockfile without resolving packages.
find <App>.xcodeproj <App>.xcworkspace -path '*Package.resolved' -print
plutil -p <resolved/Package.resolved>

# Inspect target-owned configuration and privacy inputs.
plutil -p <Info.plist>
find . -name 'PrivacyInfo.xcprivacy' -print
rg -n 'MWDAT|MetaAppID|ClientToken|AppLinkURLScheme|Bluetooth|Local Network|Camera|Microphone' .
```

For a machine-readable redacted receipt that keeps the same boundary, run the
portable helper from the device-proof package against the actual target:

```bash
python3 scripts/run_ios_target_preflight.py <target-root> \
  --project <App>.xcodeproj \
  --scheme <Scheme> \
  --configuration Debug \
  --route native-display \
  --json
```

Add `--destination '<explicit simulator-or-device destination>' --test` only
when an intentional build/test observation is wanted. The helper omits raw
`xcodebuild` output and credential values; its receipt remains static/build
evidence and does not establish a connected or physical glasses result.

Record:

- actual scheme/target, deployment target, SDK/toolchain, bundle version/build,
  targeted device family, signing/configuration state, and package product;
- `Package.resolved` identity/revision and whether it matches the intended DAT
  tag; a source URL alone is not package resolution;
- `Info.plist`, entitlements, privacy manifest, URL callback, Bluetooth/
  local-network, camera/microphone disclosures, and phone fallback;
- whether the selected target contains the 0.9 consolidated `Camera` route and
  no removed `addStream` assumption.

`xcodebuild -showBuildSettings` and `Package.resolved` establish target/config
facts, not a successful build or hardware behavior. Use `BUILD-01` separately.

## Android DAT lane

Run from the actual Gradle root with the selected module and configuration.
Dependency reports can populate local Gradle caches; do not treat cache writes
as project changes, and do not run publishing, signing, clean, or dependency
mutation tasks as preflight.

```bash
# Record the wrapper/toolchain and module properties.
./gradlew --version
./gradlew :app:properties

# Inspect the resolved compile/runtime graph for the selected variant.
./gradlew :app:dependencies --configuration debugCompileClasspath
./gradlew :app:dependencyInsight \
  --dependency com.meta.wearable \
  --configuration debugRuntimeClasspath

# Inspect project-owned configuration without printing credential values.
rg -n 'mwdat|com\.meta\.wearable|APPLICATION_ID|CLIENT_TOKEN|DAM_ENABLED|CRASH_REPORTING' . \
  --glob '!*build*' --glob '!*.lock'
rg -n 'minSdk|targetSdk|compileSdk|kotlin|agp|com\.android\.application' \
  settings.gradle* build.gradle* gradle/libs.versions.toml app/build.gradle*
```

Record:

- Gradle/AGP/Kotlin/JDK versions, module/variant, min/compile/target SDK;
- exact resolved `mwdat-core`, `mwdat-camera`, `mwdat-display`, and
  `mwdat-mockdevice` artifacts, repository source, and R8/consumer rules;
- Manifest permissions, callback intent filter, application/client metadata,
  privacy disclosures, signing/build variant, and phone fallback;
- whether the target uses 0.9 `addCamera()`/`Camera.stream` and the current
  Display builder rather than removed DAM/`addStream`/`DisplayComponent` shapes.

The dependency report is target configuration evidence. It is not a physical
device result, release-channel authorization, or proof that a Java/Kotlin call
site compiles until the selected build runs.

For a redacted static receipt before dependency work, run the portable helper
from the device-proof package against the actual Gradle root:

```bash
python3 scripts/run_android_target_preflight.py <target-root> \\
  --module app \\
  --variant debug \\
  --route native-dat-android \\
  --json
```

The helper does not invoke Gradle, print environment values, resolve Maven
artifacts, or promote missing Android tooling to a compile result. Its receipt
should accompany the later dependency report and selected-variant build.

## Web App lane

Treat the hosted Web App as a separate project and release surface. Do not
claim delivery from a local browser page or a QR/add flow alone.

```bash
# Freeze the source and working tree without publishing or deploying.
git rev-parse --verify HEAD
git status --short
node --version
npm --version

# Inventory package scripts and host-facing configuration.
node -e 'const p=require("./package.json"); console.log(JSON.stringify({name:p.name,version:p.version,scripts:p.scripts}, null, 2))'
rg -n '600|600px|https|focus|keydown|pointer|service.?worker|offline|Escape|back|token|secret' . \
  --glob '!node_modules/**' --glob '!dist/**'
```

Record hosted origin, revision, add/launch metadata, viewport, focus order,
input mapping, network/storage/cache destinations, fallback URL or phone path,
and the exact source-conflict status for text composition, offline/cache,
Escape/back, extended gestures, motion/orientation, and geolocation. Run
`WEB-SIM-01` and `WEB-PHYS-01` independently.

## Cross-platform and privacy checks

| Check | Required observation | Do not infer |
| --- | --- | --- |
| Source | DAT tag/commit, Web App revision, docs date | package or runtime support |
| Target | scheme/module/host, configuration, OS/toolchain, dependency graph | physical capability |
| Identity | bundle/application ID, callback, privacy/config keys with values redacted | account authorization or attestation |
| Capability | selected API row, runtime predicate, requested route | Gen 2/Gen 3 support from wording |
| Data path | source, processing location, retention, network/storage, deletion | “on-device” from a phone companion |
| Fallback | missing glasses, denial, disconnect, thermal, timeout, host exit | release readiness |
| Artifact | build/archive/hosted revision pointer and checksum where allowed | production delivery |

Never place tokens, client secrets, raw media, transcripts, serials, MACs,
callback query values, private Display content, or tester identities in the
preflight record. A redacted target inventory is sufficient for routing.

## Preflight task IDs

| ID | Task | Minimum evidence |
| --- | --- | --- |
| `PRE-SOURCE-01` | Freeze DAT/Web App revisions, API manifest ID, retrieval date, and source conflicts. | `source` |
| `PRE-IOS-01` | Inventory Xcode project/workspace, scheme/target, resolved settings, Package.resolved, products, and privacy/configuration files. | `static` |
| `PRE-ANDROID-01` | Inventory Gradle wrapper/module/variant, resolved DAT artifacts, SDK levels, Manifest, R8, and privacy/configuration files. | `static` |
| `PRE-WEB-01` | Freeze Web App commit/package/origin, viewport/input/host configuration, storage/network boundary, and source-conflicted feature rows. | `static`/`browser-sim` |
| `PRE-IDENTITY-01` | Inspect redacted bundle/application ID, callback, project/build variant, and signing input location. | `static` |
| `PRE-DATA-01` | Record processing location, consent, retention/deletion, network/storage, thermal/lifecycle, and phone fallback for each capability. | `static` |
| `PRE-TUPLE-01` | Fill product/SKU, runtime identity, phone, companion, firmware, DAT-app, artifact, mode/channel, and requested capability tuple. | `connected`/`not-run` |
| `PRE-BUILD-01` | Build the selected target and record actual products/symbols, test result, and artifact pointer. | `build` |
| `PRE-ARCHIVE-01` | Inspect signed archive/bundle/application ID/version/build/device family/entitlements/privacy metadata before release testing. | `signed` |

## Evidence interpretation

Preflight is a gate, not a result upgrade:

```text
preflight source/static
  -> selected target build/test
  -> MockDevice/browser simulator
  -> named connected pair
  -> named physical pair
  -> signed/release-channel
  -> production
```

If a preflight field is unavailable, keep the related task `not-run`,
`access-gated`, or `to-verify`. A clean dependency graph can coexist with a
missing account, incompatible firmware, absent Display capability, or no
physical proof.

## Preflight handoff

```text
preflight_run: <run_id>
route: <native-DAT-iOS / native-DAT-Android / native-Display / Web-App / phone>
source_revision: <tag/commit/docs date>
target: <scheme/module/host + configuration>
toolchain: <Xcode/Swift or Gradle/AGP/Kotlin/JDK or Node/browser>
dependency_resolution: <Package.resolved / Maven graph / Web revision>
identity_privacy: <redacted summary + files checked>
device_tuple: <known fields; unknowns explicit>
processing_path: <per data type>
fallback: <phone/manual/offline/online/error path>
tasks: <PRE-* statuses and artifact pointers>
next_gate: <build/mock/browser/connected/physical/signed/release>
```

## Sources

- [Apple: configuring target build settings](https://developer.apple.com/documentation/xcode/configuring-the-build-settings-of-a-target/)
- [Apple: adding package dependencies](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Apple: building Swift packages/apps in CI](https://developer.apple.com/documentation/xcode/building-swift-packages-or-apps-that-use-them-in-continuous-integration-workflows)
- [Apple: running apps on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Gradle command-line interface and dependencyInsight](https://docs.gradle.org/current/userguide/command_line_interface.html)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Meta Wearables Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)

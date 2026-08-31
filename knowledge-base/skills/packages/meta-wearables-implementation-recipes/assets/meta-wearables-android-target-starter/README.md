# Meta Wearables Android DAT target starter

This is a small, credential-safe Android target shell for DAT 0.9.0 work. It
is intentionally separate from the reusable Display coordinator: the target
owns Android permissions, `Wearables.initialize(context)`, manifest metadata,
Gradle artifact resolution, and the phone UI. Add the selected camera, Display,
audio, or MockDevice adapter only after the target preflight and implementation
handoff are complete.

The build graph follows the official Android `DisplayAccess` sample as observed
at the current source snapshot:

- AGP `8.11.1`, Kotlin `2.2.21`, Gradle `8.14.1` distribution;
- compile/target SDK `36`, min SDK `31`, Java/Kotlin JVM `17`;
- the full public Android DAT artifact set at `0.9.0`: `mwdat-core`,
  `mwdat-camera`, `mwdat-display`, and `mwdat-mockdevice`; and
- GitHub Packages at `https://maven.pkg.github.com/facebook/meta-wearables-dat-android`.

The package contains no `local.properties`, client token, application ID, GitHub
token, signing material, device identifier, or Developer Center payload. The
bootstrap does not request camera/microphone permissions merely because the
camera and MockDevice artifacts are present; add those permissions only for the
selected phone/mock or sound-in-video route. Before
building a real app, copy this folder into a new sibling project, change the
example namespace/application ID, and configure private values outside version
control:

```text
# local.properties (ignored by this starter)
github_token=<read-packages-token>
mwdat_application_id=<Developer-Center-application-id>
mwdat_client_token=<Developer-Center-client-token-if-required>
```

For CI or a local shell, the starter also accepts `GITHUB_TOKEN`,
`MWDAT_APPLICATION_ID`, and `MWDAT_CLIENT_TOKEN` environment variables. Do not
print those values or pass them in a command that will be recorded in shell
history. Developer Mode and the exact application/client-token requirement are
target/account gates, not assumptions this shell resolves.

## Build gate

Open the copied project in Android Studio or add the official Gradle wrapper,
then run the following from the target root in an environment with Android SDK
36, Java 17, and authenticated GitHub Packages access:

```sh
gradle :app:assembleDebug
```

This knowledge-base repository does not contain an Android SDK, Gradle
executable, or authenticated Maven artifact path, so the starter is not claimed
as compiled here. The target build must resolve the artifacts, then the selected
implementation recipe must be exercised through connected, physical, signed,
and release gates separately.

## What the shell proves

The source provides a minimal launcher that requests the official sample's
Bluetooth/Internet permissions, initializes DAT once, and leaves the next
registration/device/capability step visible in the phone UI. It does not prove
registration, transport, firmware, companion readiness, Display rendering,
camera/audio behavior, Gen 2/Gen 3 compatibility, or release behavior.

Use the reusable [Android Display starter](../meta-wearables-android-display-starter/README.md)
for the first native Display slice and the [project bootstrap packet](../../../meta-wearables-agentic-team/references/project-bootstrap-packet.md)
for the completed sibling-project intake.

## Official anchors

- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DisplayAccess build graph](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess)
- [DisplayAccess activity](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/DisplayAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/displayaccess/MainActivity.kt)
- [DAT Android 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)

# Registration, permissions, and configuration

For identity, callback, Developer Mode/release attestation, credential redaction,
or App Store/privacy-manifest boundaries, pair this route with the [security,
attestation, and credential-boundaries route](25-security-attestation-and-credential-boundaries.md).

DAT has two user-controlled gates before a capability can do useful work:

1. **Registration:** the app is approved as an integration through Meta AI.
2. **Device permission:** the app is granted the particular device access it
   requests, such as camera access.

Neither gate is equivalent to device availability, firmware compatibility,
session readiness, or a successful stream.

## iOS configuration inventory

The exact values come from the Wearables Developer Center project and the
current official sample. Treat this as an audit inventory, not a copy-paste
claim that every target needs every key.

| Configuration | Why it exists | Review boundary |
| --- | --- | --- |
| App URL scheme in `CFBundleURLTypes` | Receives the Meta AI callback. | Test cold launch, warm launch, cancellation, and stale callbacks. |
| `UISupportedExternalAccessoryProtocols` with `com.meta.ar.wearable` | Declares the wearable accessory route. | Confirm target membership and the exact protocol in the installed sample/package. |
| `UIBackgroundModes` | Supports the SDK's accessory/Bluetooth lifecycle where the route requires it. | A background mode is not permission to run arbitrary work indefinitely. |
| `NSBluetoothAlwaysUsageDescription` | Explains Bluetooth access to the person. | Copy must be truthful and specific to the app's use. |
| `MWDAT.AppLinkURLScheme` | Associates the app's callback scheme with DAT. | Keep the configured scheme consistent with the URL type. |
| `MWDAT.MetaAppID` | Identifies the Meta project; `0` is documented for Developer Mode. | Production/release-channel values come from the Wearables Developer Center. |
| `MWDAT.ClientToken` and `MWDAT.TeamID` | Required by the current Display/release configuration guidance. | Do not invent or commit credentials; verify per target and channel. |
| `LSApplicationQueriesSchemes` with `fb-viewapp` | Lets DAT detect/open the Meta AI companion app. | Verify the exact target’s URL-query configuration and do not log callback data. |
| `MWDAT.Analytics.OptOut` | Controls DAT analytics collection. | Default behavior is enabled unless the app opts out; document the decision. |
| `MWDAT.CrashReporting.OptOut` | Controls DAT SDK crash capture. | Treat this as a privacy/diagnostics decision, not just a build flag. |
| Local-network/Bonjour keys for Display/video where required | Supports higher-bandwidth Display link leases in the official Display sample. | Recheck the current sample and explain the feature-specific need. |

The current public iOS integration guide also describes Bluetooth LE as the
baseline discovery/control link and Wi-Fi/local-network/Bonjour for some
high-bandwidth camera or Display paths. A denied local-network prompt can leave
the integration partially available over Bluetooth while preventing streaming;
model that state instead of treating it as a generic registration failure.

The current 0.9.0 changelog says the old `MWDAT.DAMEnabled` opt-out is ignored
because DAM is always enabled. Keep historical configuration notes labeled as
historical when migrating an older app.

## Registration state machine

Model at least `available`, `registering`, `registered`, `unavailable`, and
unregistering states from the current SDK. A user can cancel, leave Meta AI,
lose network access, or return through a cold launch. Keep the UI recoverable:

```text
available -> registering -> registered
     |             |             |
 unavailable   cancelled     permission request
     |                           |
 retry after prerequisites   granted | denied
```

The app should observe the SDK's registration stream and use `startRegistration`
or `startUnregistration` as explicit user actions. Do not silently open Meta AI
on launch or treat a callback URL as proof that the requested permission was
granted.

## Permission flow

For a camera route, check the current permission status, explain the purpose,
request the permission through DAT, and render denied/temporarily unavailable
states. The current public iOS guidance describes “allow once” and “allow
always” choices; persist only the minimum app state needed to explain the next
step. If every linked device disconnects, availability can change even though
the registration record remains.

## Android parity

The Android repository has corresponding initialization, registration,
permissions, manifest metadata, `DeviceSession`, `Camera`, `Stream`, and
`Display` concepts, but the mechanics are Kotlin/Gradle/AndroidManifest and
must be checked independently. Use parity to compare product behavior, not to
copy a key or lifecycle signature across platforms.

## Configuration proof checklist

- [ ] Target deployment and package revision are recorded.
- [ ] Meta AI app installation, Developer Mode, Bluetooth, network, and
  glasses firmware prerequisites are recorded.
- [ ] URL callback is tested for registration success, denial, cancellation,
  cold launch, and malformed/stale URLs.
- [ ] Permission status and request failure are visible in the app state.
- [ ] Analytics/crash choices and camera/display privacy disclosures are
  reviewed.
- [ ] Release-channel credentials are supplied through the configured project,
  never hard-coded into source or logs.

## Sources

- [DAT iOS Getting Started skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md)
- [DAT iOS permissions and registration skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/permissions-registration/SKILL.md)
- [DAT iOS Display Access skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md)
- [DAT iOS README and analytics/crash controls](https://github.com/facebook/meta-wearables-dat-ios#readme)
- [DAT iOS developer documentation](https://wearables.developer.meta.com/docs/develop/)
- [Apple information property list key reference](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Introduction/Introduction.html)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)

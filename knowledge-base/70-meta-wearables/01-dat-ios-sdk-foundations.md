# DAT iOS SDK foundations

The Meta Wearables Device Access Toolkit (DAT) is the native iOS route for
connecting an iPhone app to supported Meta AI glasses. This page was refreshed
on 2026-08-22 against public iOS `main` commit
`225f64ff1617e7acc8c407bb8d3ee132f7263d00` and the 0.9.0 tag
`9b1b83d791dfebff7afd452e924a256819094b64`. Use the tag for a reproducible
package; recheck the repository tag, changelog, and installed package before
using any signature in a real target.

## Package and modules

Add the official Swift package repository:

```text
https://github.com/facebook/meta-wearables-dat-ios
```

The public repository organizes the iOS surface into these modules:

| Module | Responsibility |
| --- | --- |
| `MWDATCore` | `Wearables`, registration, permissions, devices, selectors, `DeviceSession`, device state, compatibility, and typed errors. |
| `MWDATCamera` | `Camera`, `Stream`, `VideoFrame`, `PhotoData`, `StreamConfiguration`, and camera errors. |
| `MWDATDisplay` | `Display`, structured display components, icons/images/buttons, video, and display errors. |
| `MWDATMockDevice` | Mock glasses, permissions, camera feeds, photo fixtures, lifecycle controls, and test-server support. |
| `MWDATMockDeviceTestClient` | XCUITest-process control for the MockDevice localhost test server and deterministic device actions; test-only, not an app runtime capability. |

The current machine-readable Wearables platform index also names
`MWDATDevice`, `MWDATMedia`, `MWDATState`, `MWDATLogger`, `MWDATMock`, and
`MWDATKey`. The 0.9.0 `Package.swift` exposes five products: four runtime
products plus the test-only `MWDATMockDeviceTestClient`. The upstream iOS
repository’s public skills/samples explicitly use the four runtime imports above;
verify whether the broader names are importable package products or
documentation groupings in the exact package before adding them to a target.

The current 0.9.0 changelog says the iOS minimum deployment target is iOS
17.2. The public full-reference index currently shows an older iOS 15.2+
prerequisite, while the upstream getting-started prose also contains older
minimum-version wording. Treat that as a source conflict: the pinned package
manifest/changelog and a real target build win over a living index or stale
sample prose. It is not proof that a future release or every sample has the
same target.

## Launch and callback contract

Configure the SDK once at app launch, keep the failure visible, and route the
Meta AI callback back to the SDK:

```swift
import MWDATCore

@main
struct WearableApp: App {
    init() {
        do {
            try Wearables.configure()
        } catch {
            // Show a recoverable configuration state in a real app.
        }
    }

    var body: some Scene {
        WindowGroup { ContentView() }
            .onOpenURL { url in
                Task {
                    _ = try? await Wearables.shared.handleUrl(url)
                }
            }
    }
}
```

The exact callback and configuration signatures must be typechecked against
the package revision in the target. The important ownership boundary is stable:
the app owns its UI and domain state; Meta AI owns approval flows; DAT reports
registration, permission, device, session, and capability state.

## Current 0.9.0 changes that affect code review

- `DeviceSession.addCamera(config:)` returns a `Camera`; use `camera.stream`
  for streaming and `camera.stop()` to detach the camera and its child stream.
- `DeviceSession.addStream(config:)` is removed from the current route.
- `DeviceSession.stateStream()` and `errorStream()` finish after the terminal
  `.stopped` state; a stream created after stopping finishes immediately.
- Display `ButtonGroup` and `DeviceType.supportsDisplay` are available in the
  current release.
- `ListenerTokenBag` is an actor and `AnyListenerToken.store(in:)` provides an
  explicit listener-lifetime path; test cleanup and actor isolation.
- `MockCameraKit.setCameraFeed(cameraFacing:)` is synchronous in 0.9.0; remove
  stale `await` calls from mock fixtures.
- Doff can surface `StreamError.hingesClosed`; route it as a typed stop/pause
  condition rather than treating it as a generic transport failure.
- DAT App Model (DAM) opt-out is removed in 0.9.0 and the changelog says DAM is
  always enabled; do not preserve an old opt-out key as if it were active.
- Crash reporting has an `MWDAT > CrashReporting > OptOut` Info.plist control;
  the default and the product's disclosure/retention decision still need an
  explicit privacy review.
- The current Camera Access background notes are not a blanket background
  capture guarantee: the preview session may end when the app backgrounds,
  while an optional sound-in-video path is described separately. Verify the
  exact target behavior before designing a background camera workflow.

## Evidence boundary

Repository code and changelog are source/SDK evidence. They do not establish
that the current app target compiles, the user's Meta AI account can register,
the glasses firmware is compatible, or the Display/camera route works on a
physical device. Keep those as separate gates in the project handoff.

## Sources

- [Official DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT iOS Getting Started skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md)
- [DAT iOS conventions](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/dat-conventions/SKILL.md)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS sample-app guide](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/sample-app-guide/SKILL.md)
- [iOS DAT API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest)
- [iOS integration guide](https://wearables.developer.meta.com/docs/build-integration-ios)
- [Swift Package Manager](https://developer.apple.com/documentation/swift_packages)
- [Evidence and verification language](../00-foundations/05-evidence-and-verification-language.md)

# Media and Sensor Recipes

Choose the route with the [capability-first Apple SDK atlas](../40-framework-routes/10-capability-first-apple-sdk-atlas.md) and keep ownership, cancellation, and physical proof explicit with the [device and companion capability contracts](../42-framework-deep-dives/08-device-and-companion-capability-contracts.md).

## Capture authorization and session setup

```swift
import AVFoundation

func prepareCamera() async -> Bool {
    switch AVCaptureDevice.authorizationStatus(for: .video) {
    case .authorized:
        return true
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .video)
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}
```

Only configure a capture session after authorization succeeds. Add truthful `NSCameraUsageDescription` and `NSMicrophoneUsageDescription` values before requesting access. Run session setup/start work on an appropriate queue and tear it down when the feature leaves the screen.

## Location authorization boundary

```swift
import CoreLocation

final class LocationDelegate: NSObject, CLLocationManagerDelegate {
    let manager = CLLocationManager()

    func begin() {
        manager.delegate = self
        switch manager.authorizationStatus {
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways:
            manager.startUpdatingLocation()
        default:
            break
        }
    }
}
```

This is a minimal route sketch, not a complete location service. Handle reduced accuracy, denial, Settings changes, background policy, errors, and lifecycle before using coordinates in a product.

## VisionKit handoff

For live text/barcode capture, check `DataScannerViewController.isSupported` and `isAvailable`, add camera usage text, present the scanner through a UIKit/SwiftUI bridge, and map recognized items into a draft. The scan result should be editable before persistence or a side effect.

## Compile/device gate

- Test camera, microphone, photo library, and location permission states.
- Verify device support and availability before presenting hardware UI.
- Run capture, focus, lighting, audio route, motion, and background behavior on physical devices.
- Validate privacy descriptions, retention, redaction, and manual fallbacks.
- Never treat a simulator permission dialog or prerecorded frame as proof of real hardware behavior.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services)
- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)

# CoreLocationUI and LocationButton recipes

These are compile-oriented route sketches for a user-initiated location feature. They intentionally separate the authorization control from the Core Location reader, the map/geocoder result, and any on-device AI proposal. They are not claimed to compile in this documentation-only workspace.

Before copying:

- set the deployment target and confirm the current SDK;
- link CoreLocationUI and Core Location in the named target;
- add only the required usage-description keys for the chosen route;
- test denied, restricted, approximate, stale, unavailable, and cancellation states;
- use a signed physical device for the real permission and location behavior.

## 1. SwiftUI LocationButton as the authorization boundary

The action runs on every tap. It starts the app-owned location request; it does not itself provide a CLLocation.

~~~swift
import SwiftUI
import CoreLocationUI

struct CurrentLocationAction: View {
    let requestLocation: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Use your current location to find nearby places.")
                .font(.subheadline)

            LocationButton(.currentLocation) {
                requestLocation()
            }
            .symbolVariant(.fill)
            .labelStyle(.titleAndIcon)
        }
    }
}
~~~

Keep the surrounding copy specific to the task. Do not replace the system title with a generic “Enable GPS” message.

## 2. Share-specific LocationButton title

Use a title that matches a system handoff or review flow:

~~~swift
struct ShareLocationAction: View {
    let prepareShare: () -> Void

    var body: some View {
        LocationButton(.shareCurrentLocation) {
            prepareShare()
        }
        .labelStyle(.titleAndIcon)
    }
}
~~~

The action should first fetch and review a location. Do not send a message or share automatically just because the button was tapped.

## 3. UIKit CLLocationButton bridge

Use CLLocationButton when a UIKit target owns the feature. The button is a UIControl, so its action is still only the start of the location route.

~~~swift
import CoreLocationUI
import UIKit

final class LocationButtonViewController: UIViewController {
    private let locationButton = CLLocationButton()

    override func viewDidLoad() {
        super.viewDidLoad()

        locationButton.icon = .arrowFilled
        locationButton.label = .currentLocation
        locationButton.cornerRadius = 24
        locationButton.addTarget(
            self,
            action: #selector(locationButtonTapped),
            for: .touchUpInside
        )

        view.addSubview(locationButton)
        locationButton.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            locationButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            locationButton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func locationButtonTapped() {
        // Start the app-owned Core Location request.
    }
}
~~~

Check the button’s contrast, label fit, and device/platform behavior in the signed target.

## 4. Delegate-owned current-location client

A manager must have a deliberate owner and delegate lifetime. This sketch keeps the route simple for a foreground current-location action.

~~~swift
import CoreLocation
import Foundation

@MainActor
final class CurrentLocationClient: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private(set) var latestLocation: CLLocation?
    private(set) var authorization: CLAuthorizationStatus = .notDetermined
    private(set) var isRequesting = false
    var onChange: (() -> Void)?

    override init() {
        super.init()
        manager.delegate = self
        authorization = manager.authorizationStatus
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        manager.distanceFilter = 50
    }

    func startOneShotRequest() {
        isRequesting = true
        manager.requestLocation()
    }

    func requestWhenInUseIfNeeded() {
        guard manager.authorizationStatus == .notDetermined else {
            startOneShotRequest()
            return
        }
        manager.requestWhenInUseAuthorization()
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorization = manager.authorizationStatus
        onChange?()
    }

    func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        isRequesting = false
        latestLocation = locations.last
        onChange?()
    }

    func locationManager(
        _ manager: CLLocationManager,
        didFailWithError error: Error
    ) {
        isRequesting = false
        onChange?()
    }
}
~~~

The current SDK may offer a more modern async route. Keep this delegate implementation for targets that require it, and make authorization and error state visible to the caller.

## 5. Check accuracy without faking precision

Reduced accuracy should change the product state rather than merely changing a debug label.

~~~swift
import CoreLocation

func locationQuality(
    manager: CLLocationManager,
    location: CLLocation
) -> String {
    switch manager.accuracyAuthorization {
    case .fullAccuracy:
        return "precise"
    case .reducedAccuracy:
        return "approximate"
    @unknown default:
        return location.horizontalAccuracy >= 0 ? "unknown precision" : "unavailable"
    }
}
~~~

If the feature truly needs full accuracy, ask for it at the feature moment with the documented purpose key and a plain-language explanation. Do not make every feature take the expensive precision path.

## 6. Swift concurrency live-update sketch

Apple documents CLLocationUpdate and an asynchronous live-updates route. Confirm the exact initializer and configuration for the selected SDK before compiling.

~~~swift
import CoreLocation

struct LiveLocationReader {
    func readUntilCancelled(
        handle: @escaping (CLLocationUpdate) -> Void
    ) async {
        do {
            for try await update in CLLocationUpdate.liveUpdates() {
                guard !Task.isCancelled else { return }
                handle(update)
            }
        } catch {
            // Publish a typed location-service failure.
        }
    }
}
~~~

The task needs a clear owner and cancellation boundary. Do not start this stream from a view body, and do not retain every raw update when the feature needs only a current point or a sampled path.

## 7. MapKit or AI handoff record

Keep the raw observation, selected place, and proposal separate:

~~~swift
struct LocationObservation: Sendable {
    let coordinate: CLLocationCoordinate2D
    let timestamp: Date
    let horizontalAccuracy: CLLocationDistance
    let sourceRevision: String
}

struct PlaceSelection: Sendable {
    let displayName: String
    let observationRevision: String
    let userAccepted: Bool
}

struct LocationProposal: Sendable {
    let selectedPlace: String
    let sourceRevision: String
    let modelRouteVersion: String
    let needsReview: Bool
}

func accept(
    proposal: LocationProposal,
    currentRevision: String
) throws {
    guard proposal.sourceRevision == currentRevision else {
        throw LocationRouteError.staleProposal
    }
    guard proposal.needsReview == false else {
        throw LocationRouteError.requiresReview
    }
}

enum LocationRouteError: Error {
    case staleProposal
    case requiresReview
}
~~~

The proposal should be created only after the person starts the AI action. A model route can suggest a label or nearby category; it cannot prove that the person visited the place.

## 8. SwiftUI state shell

Keep system and domain states explicit:

~~~swift
import SwiftUI

struct LocationReviewShell: View {
    enum State {
        case needsAction
        case waiting
        case approximate(CLLocation)
        case ready(CLLocation)
        case denied
        case unavailable
    }

    let state: State
    let request: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            switch state {
            case .needsAction:
                Text("Location is used only for this feature.")
                CurrentLocationAction(requestLocation: request)
            case .waiting:
                ProgressView("Getting your location")
            case .approximate(let location):
                Text("Approximate location ready.")
                Text(location.timestamp, style: .time)
            case .ready(let location):
                Text("Current location ready.")
                Text(location.timestamp, style: .time)
            case .denied:
                Text("Location access is off. You can search manually.")
            case .unavailable:
                Text("Location is unavailable right now.")
            }
        }
        .padding()
    }
}
~~~

Add accessible labels and actual map/search/review actions in the named product. The shell is not a substitute for testing the system permission surface.

## 9. Recipe proof checklist

- Compile the SwiftUI and UIKit button routes in the target.
- Confirm the system title fits at large Dynamic Type and in localization.
- Test first tap, later tap, denied, restricted, approximate, and disabled-services states on a signed device.
- Confirm the app fetches a location only after the intended action.
- Test cancellation, stale results, and a second request replacing the first.
- Verify map/geocoder results and manual correction separately from Core Location.
- Keep AI context bounded and proposal acceptance explicit.
- Test VoiceOver, reduced transparency, Reduce Motion, contrast, pointer, keyboard, and RTL.
- If adding background, watch, push, or shared-location behavior, create a separate target-specific proof matrix.

## Related routes

- [CoreLocationUI and least-privilege location access](../42-framework-deep-dives/55-corelocationui-and-least-privilege-location.md)
- [Location Button and privacy-first map design](../21-design-deep-dives/75-location-button-and-privacy-first-map-design.md)
- [CoreLocationUI and on-device location route](../50-capability-recipes/78-corelocationui-and-on-device-location-route.md)
- [CoreLocationUI proof matrix](../60-verification/72-corelocationui-location-proof-matrix.md)

## Sources

- [CoreLocationUI](https://developer.apple.com/documentation/corelocationui)
- [LocationButton](https://developer.apple.com/documentation/corelocationui/locationbutton)
- [LocationButton initializer](https://developer.apple.com/documentation/corelocationui/locationbutton/init%28_%3Aaction%3A%29)
- [CLLocationButton](https://developer.apple.com/documentation/corelocationui/cllocationbutton)
- [Core Location](https://developer.apple.com/documentation/CoreLocation)
- [CLLocationManager](https://developer.apple.com/documentation/corelocation/cllocationmanager)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [CLAuthorizationStatus](https://developer.apple.com/documentation/corelocation/clauthorizationstatus)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/CoreLocation/requesting-authorization-to-use-location-services?changes=_7)
- [Adopting live updates in Core Location](https://developer.apple.com/documentation/corelocation/adopting-live-updates-in-core-location?changes=lat_5)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Human Interface Guidelines privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)

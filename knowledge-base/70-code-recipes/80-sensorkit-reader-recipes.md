# SensorKit reader recipes

These are compile-oriented sketches for an approved SensorKit research target. They do not create Apple study approval, entitlements, user consent, physical sensors, or scientific validity. Confirm the current SDK because the generic async SensorKit route is documented as beta and the older delegate route is deprecated.

## 1. Study metadata and entitlement shape

~~~xml
<!-- Built target Info.plist: values must match the approved study. -->
<key>NSSensorKitUsageDescription</key>
<string>Approved research purpose shown to the participant.</string>
<key>NSSensorKitPrivacyPolicyURL</key>
<string>$(SENSOR_KIT_PRIVACY_POLICY_URL)</string>
<key>NSSensorKitUsageDetail</key>
<dict>
    <key>SRSensorUsageMotion</key>
    <dict>
        <key>Description</key>
        <string>Approved explanation for the motion sensor.</string>
        <key>Required</key>
        <false/>
    </dict>
</dict>
~~~

The signed entitlement is a separate artifact:

~~~xml
<key>com.apple.developer.sensorkit.reader.allow</key>
<array>
    <string>motion-accelerometer</string>
</array>
~~~

Never add a sensor to the entitlement or usage detail because an AI idea would benefit from it. The list must match the approved study.

## 2. Current typed reader and authorization gate

~~~swift
import SensorKit

enum SensorStudyError: Error {
    case notAuthorized
}

struct PedometerStudyRoute {
    let reader: SRReader<SRPedometerDataSensor>

    init() throws {
        reader = try SRReader(sensor: SRPedometerDataSensor.pedometerData)
    }

    func startRecording() async throws {
        guard reader.authorizationStatus == .authorized else {
            throw SensorStudyError.notAuthorized
        }
        try await reader.startRecording()
    }

    func stopRecording() async throws {
        try await reader.stopRecording()
    }
}
~~~

The current generic route’s authorization request flow and sensor availability are target-SDK-sensitive. Check `authorizationStatus` before recording or fetching, and keep the system study sheet/Settings path visible in the containing app.

## 3. Fetch typed responses with an explicit window

~~~swift
import SensorKit

struct SensorWindow {
    let from: SRAbsoluteTime
    let to: SRAbsoluteTime
}

func readPedometerSamples(
    reader: SRReader<SRPedometerDataSensor>,
    window: SensorWindow
) async throws -> [SRPedometerDataSensor.Sample] {
    guard reader.authorizationStatus == .authorized else {
        throw SensorStudyError.notAuthorized
    }

    let request = SRFetchRequest()
    request.from = window.from
    request.to = window.to

    var samples: [SRPedometerDataSensor.Sample] = []
    for try await response in reader.samples(matching: request) {
        switch response.sample {
        case .success(let sample):
            samples.append(sample)
        case .failure(let error):
            // Store a redacted quality event; do not fabricate a sample.
            _ = error
        }
    }
    return samples
}
~~~

`SRFetchRequest` must also be associated with the intended device when the selected SDK exposes multiple devices. This sketch intentionally does not infer a time window or device.

## 4. Surface deletion gaps

~~~swift
import SensorKit

struct DeletionGap {
    let start: SRAbsoluteTime
    let end: SRAbsoluteTime
    let reason: SRDeletionReason
}

func readDeletionRecords(
    reader: SRReader<SRPedometerDataSensor>,
    window: SensorWindow
) async throws -> [DeletionGap] {
    let request = SRFetchRequest()
    request.from = window.from
    request.to = window.to

    var gaps: [DeletionGap] = []
    for try await response in reader.deletionRecords(matching: request) {
        if case .success(let record) = response.sample {
            gaps.append(DeletionGap(
                start: record.startTime,
                end: record.endTime,
                reason: record.reason
            ))
        }
    }
    return gaps
}
~~~

A deletion record is an integrity fact. Keep it in the research window and prevent downstream charts or models from silently treating the interval as zero.

## 5. Legacy authorization adapter

~~~swift
import SensorKit

@available(*, deprecated, message: "Use the current SRReader route in the selected SDK.")
final class LegacySensorAuthorization {
    func requestMotionAuthorization(
        completion: @escaping (Result<Void, Error>) -> Void
    ) {
        SRSensorReader.requestAuthorization(
            sensors: [.accelerometer]
        ) { error in
            if let error {
                completion(.failure(error))
            } else {
                completion(.success(()))
            }
        }
    }
}
~~~

The legacy completion means the prompt operation completed; read the reader’s authorization status afterward. Do not treat a nil error as authorization granted, and do not mix this deprecated callback route with a generic async reader without an adapter.

## 6. Participant status model

~~~swift
import SensorKit
import SwiftUI

@MainActor
final class SensorStudyStatus: ObservableObject {
    @Published private(set) var authorization: SRAuthorizationStatus = .notDetermined
    @Published private(set) var isRecording = false
    @Published private(set) var availabilityMessage = "No eligible fetch yet"
    @Published private(set) var deletionGapCount = 0

    func update<S: SRDataSensor>(from reader: SRReader<S>) {
        authorization = reader.authorizationStatus
    }
}

struct SensorStudyStatusView: View {
    @ObservedObject var status: SensorStudyStatus

    var body: some View {
        Form {
            Section("Study sensor") {
                Text(authorizationText)
                Text(status.isRecording ? "Recording" : "Not recording")
                Text(status.availabilityMessage)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            Section("Data quality") {
                Text("Deletion gaps: \(status.deletionGapCount)")
            }
        }
        .navigationTitle("Research status")
    }

    private var authorizationText: String {
        switch status.authorization {
        case .authorized: "Authorized"
        case .denied: "Not shared"
        case .notDetermined: "Not yet chosen"
        @unknown default: "Unavailable"
        }
    }
}
~~~

Use plain copy for the holding period and deletion state. Add Liquid Glass only after these semantic states work in a basic Form.

## 7. Data-quality gate before on-device AI

~~~swift
struct SensorWindowQuality: Sendable {
    let hasAuthorizedSensor: Bool
    let sampleCount: Int
    let deletionGapCount: Int
    let holdingPeriodComplete: Bool
}

enum AnalysisDecision: Sendable {
    case insufficientData
    case reviewable(features: [Double])
}

func makeAnalysisDecision(
    quality: SensorWindowQuality,
    features: [Double]
) -> AnalysisDecision {
    guard quality.hasAuthorizedSensor,
          quality.holdingPeriodComplete,
          quality.sampleCount > 0,
          quality.deletionGapCount == 0 else {
        return .insufficientData
    }
    return .reviewable(features: features)
}
~~~

A local model should receive a typed, approved feature window with its source, coverage, and deletion state. “Insufficient data” is a valid research outcome, not a failure to hide.

## 8. Swift Testing for permission and holding-period policy

~~~swift
import Testing

@Test
func deniedOrHeldWindowsDoNotBecomeModelInput() {
    let quality = SensorWindowQuality(
        hasAuthorizedSensor: false,
        sampleCount: 0,
        deletionGapCount: 0,
        holdingPeriodComplete: false
    )

    let decision = makeAnalysisDecision(quality: quality, features: [])
    guard case .insufficientData = decision else {
        Issue.record("Denied or held data must not enter analysis")
        return
    }
}
~~~

These tests prove only deterministic gating. Add signed physical iPhone/Watch, system consent, delayed fetch, deletion, accessibility, privacy, and approved-study evidence before making a research claim.

## Sources

- [SensorKit](https://developer.apple.com/documentation/sensorkit)
- [Configuring your project for sensor reading](https://developer.apple.com/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [SRReader](https://developer.apple.com/documentation/sensorkit/srreader)
- [SRDataSensor](https://developer.apple.com/documentation/sensorkit/srdatasensor)
- [SRFetchRequest](https://developer.apple.com/documentation/sensorkit/srfetchrequest)
- [SRFetchResponse](https://developer.apple.com/documentation/sensorkit/srfetchresponse)
- [SRDeletionRecord](https://developer.apple.com/documentation/sensorkit/srdeletionrecord)
- [SRSensorReader](https://developer.apple.com/documentation/sensorkit/srsensorreader)
- [SRAuthorizationStatus](https://developer.apple.com/documentation/sensorkit/srauthorizationstatus)
- [NSSensorKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedescription)
- [NSSensorKitPrivacyPolicyURL](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitprivacypolicyurl)
- [NSSensorKitUsageDetail](https://developer.apple.com/documentation/bundleresources/information-property-list/nssensorkitusagedetail)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

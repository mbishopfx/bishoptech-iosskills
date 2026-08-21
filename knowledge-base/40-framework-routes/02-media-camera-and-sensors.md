# Media, Camera, and Sensors

## Media, ML, and physical-input route table

| User outcome | Primary route | What must remain explicit |
| --- | --- | --- |
| Play a native audiovisual experience | AVKit/AVFoundation | `AVPlayer`/`AVPlayerViewController`, buffering, route/interruption, subtitles/alternate tracks, background policy, and media ownership. |
| Carry timed audio/video samples between pipeline stages | Core Media with AVFoundation | `CMSampleBuffer` readiness/ownership, `CMTime` timing, `CMFormatDescription`, `CMBlockBuffer`, attachments, queue/backpressure, and format changes. |
| Capture or inspect system/app screen content | ScreenCaptureKit with ReplayKit compatibility and AVFoundation/import fallback | System picker/filter, `SCStream` output lanes, frame status/timing, recording finalization, iOS 26 target gate, consent, bounded AI review, and physical-device proof. |
| Apply still/video effects | Core Image | `CIImage` recipe versus rendered output, color space, context reuse, mutable-filter isolation, memory, and cancellation. |
| Encode/decode video directly | VideoToolbox | Codec/container, hardware support, pixel format, session callbacks, frame completion, invalidation, and thermal/performance measurement. |
| Analyze images/frames | Vision | Request revision, orientation, input provenance, observation confidence/quality, cancellation, and review before committing a record. |
| Run a custom model | Core ML | Compiled model/version, input shape, compute-unit policy, model assets, output validation, memory/thermal, and representative-device quality. |
| Tokenize/classify/compare language | Natural Language | Locale/language availability, model behavior, privacy, text length, and a human/manual fallback. |
| Read a physical NFC tag | Core NFC | NFC entitlement, `NFCReaderUsageDescription`, tag/protocol allowlist, session timeout/invalidation, user proximity, and physical-device proof. |
| Search/play Apple Music | MusicKit | Music authorization, Apple Music subscription/capability, catalog/user-token state, product policy, and playback/audio route. |
| Identify captured audio | ShazamKit | Microphone/audio permission, catalog entitlement, signature/match/no-match/error, privacy, and no claim that a match proves ownership or identity. |

Model every ML/media result as a proposal with provenance until the product validates it. A high confidence score, catalog match, NFC payload, or model output is not automatically a person’s identity, a product’s authenticity, a medical conclusion, or a safe physical-world instruction.

## Accessory and proximity choices

“Nearby” is not one Apple capability. Pick the route from the user outcome and keep its permission, protocol, and physical-device boundary explicit:

| User outcome | Primary route | Boundary to prove |
| --- | --- | --- |
| Read or control accessories already configured in Apple Home | HomeKit | HomeKit capability, `NSHomeKitUsageDescription`, shared-home authorization, accessory/characteristic permissions, and confirmation before physical writes. |
| Exchange data with a Bluetooth LE accessory | Core Bluetooth | `NSBluetoothAlwaysUsageDescription`, radio authorization/state, GATT service/characteristic schema, reconnect, background policy, and accessory compatibility. |
| Measure relative distance/direction to a supported peer or accessory | Nearby Interaction | `NSNearbyInteractionUsageDescription`, out-of-band token/configuration exchange, UWB/device support, session suspension, and physical-device proof. |
| Discover/connect to services on the same local network | Network framework/Bonjour | `NSLocalNetworkUsageDescription`, `NSBonjourServices`, possible multicast entitlement, service identity, transport security, and local-network denial handling. |

Discovery is not identity, authentication, authorization, or trust. A device name, Bluetooth identifier, Bonjour result, HomeKit accessory, or Nearby token should become an app action only after the product’s protocol and user-confirmation rules accept it. Do not infer home occupancy, identity, or safety from proximity alone.

## Camera and images

Use PhotosUI for user-selected media when the app does not need live camera control. Use AVFoundation for capture sessions, recording, playback, and audio/video pipeline control. Use VisionKit for Live Text, document scanning, and live text/code scanning. Use Vision for analysis after an image or frame is available.

The least-privilege route is:

user chooses source -> permission check -> capture/import -> analysis -> review -> store/export

Do not request camera, photo library, microphone, Bluetooth, or motion access at app launch when the feature is not yet being used.

Keep source selection distinct from live capture. `PhotosPickerItem` is a user-selected representation placeholder that the app loads asynchronously; `AVCaptureSession` is a live hardware pipeline; Vision/Core ML/Sound Analysis are downstream analysis routes. A preview, imported image, or sensor sample becomes a product record only after normalization, review, and an explicit retention decision.

## Audio

AVFoundation owns much of the audio session and capture/playback lifecycle. Define interruption, route change, background, Bluetooth, recording, and cancellation behavior. Speech recognition is a separate analysis layer; keep audio capture and transcription state distinct so the user can understand what is recording and what is being processed.

## Sensors and accessories

| Capability | Framework | Design boundary |
| --- | --- | --- |
| Motion/orientation | Core Motion | Sensor availability, privacy, sampling/battery. |
| Bluetooth LE | Core Bluetooth | Permission, discovery, connection, reconnect, background limits. |
| NFC | Core NFC | Device support, session timeout, user-facing session state. |
| Haptics | Core Haptics | Purposeful feedback; reduce or simplify when needed. |
| Photo library | PhotoKit | Authorization changes and user deletion outside the app. |
| Live text/code/document | VisionKit | Hardware/permission availability and review. |

## Permission state machine

For every sensor/media route model: not determined, authorized, limited, denied, restricted, unavailable, interrupted, and revoked while the app is not active. When authorization is denied, link to the relevant settings only when it helps and preserve a manual path.

## Performance and thermal budget

Camera frames, audio streams, Vision requests, Core ML inference, and effects can compete for memory, CPU, GPU, Neural Engine, and battery. Downsample inputs, limit concurrent work, cancel old tasks, and measure on representative physical devices.

For a live video output, choose a deliberate backpressure policy. A UI-guidance feature can usually process the newest frame and discard late frames; an archival recording or measurement feature may require every sample and a different pipeline. Never create one unbounded analysis task per frame. Stop the output/delegate and release buffers when the feature leaves the screen.

Motion and haptic routes also have lifecycles. Check `CMMotionManager` availability before starting updates, choose a sampling interval that matches the outcome, stop updates when the feature ends, and account for battery/thermal cost. Check `CHHapticEngine.capabilitiesForHardware()` before creating a custom haptic engine and provide visual/audio/text feedback when haptics are unavailable or interrupted.

## Sources

- [AVKit](https://developer.apple.com/documentation/avkit)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [NSCameraUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nscamerausagedescription)
- [NSMotionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsmotionusagedescription)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [VisionKit](https://developer.apple.com/documentation/visionkit/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Core Motion](https://developer.apple.com/documentation/coremotion)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NSHomeKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nshomekitusagedescription)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [NSNearbyInteractionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsnearbyinteractionusagedescription)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIFilter](https://developer.apple.com/documentation/coreimage/cifilter-swift.class)
- [Video Toolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNRecognizeTextRequest](https://developer.apple.com/documentation/vision/vnrecognizetextrequest)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [Building an NFC tag-reader app](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [MusicKit](https://developer.apple.com/documentation/musickit)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)

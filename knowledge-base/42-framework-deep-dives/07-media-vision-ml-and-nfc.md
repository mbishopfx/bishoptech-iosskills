# Media, Vision, Machine Learning, NFC, and Music Deep Dive

## Scope

These routes turn audiovisual streams, images, text, tags, and music into product state. Keep the transformation reviewable:

`authorized source -> bounded capture/import -> typed processing -> observation/prediction/match -> provenance/review -> durable result`

Do not call an observation, prediction, match, or tag payload “truth” without a domain-specific validation step.

## Media route boundaries

| Layer | Owns | Does not own |
| --- | --- | --- |
| AVKit/AVFoundation | Native playback UI, player/item state, capture sessions, audio/video assets, export | Business truth, model quality, or a guarantee that a route/codec/device is available. |
| Core Image | Lazy image recipes, filters, contexts, color-managed rendering | A rendered file until a context produces it, or thread-safe mutable filter sharing. |
| VideoToolbox | Low-level hardware-assisted encode/decode sessions and callbacks | A general media player/editor, container metadata policy, or unlimited hardware performance. |
| Vision | Requests and observations from images/frames | User confirmation, identity/medical/legal conclusions, or source retention. |
| Core ML | Loading/configuring models and predictions | Accuracy, fairness, safety, or a guarantee that a model’s compute-unit choice is best on every device. |
| Natural Language | Tokenization, language identification, tagging, embeddings/classification routes | Human intent, truthfulness, or sensitive-text retention policy. |
| Core NFC | Session/tag protocol interaction | Tag authenticity, user identity, payment authorization, or a persistent background reader. |
| MusicKit/ShazamKit | Apple Music catalog/user access or acoustic-signature matching | Ownership/licensing, exact identity from noisy audio, or unrestricted media access. |

## AVKit and AVFoundation playback

Use `AVPlayer`/`AVPlayerItem` for a controllable player model and `AVPlayerViewController` when the product benefits from Apple’s native playback UI, navigation, subtitles, alternate audio tracks, Picture in Picture, and AirPlay behavior. Track loading/buffering/failed/end states and define what happens when the network, asset, audio route, or app lifecycle changes.

Configure `AVAudioSession` only for the product’s actual playback/recording needs. Handle interruptions, route changes, media-services reset, external playback, and user volume/route choice. A player item being ready does not mean the first frame is rendered or that an audio route is available.

## Core Image and VideoToolbox

`CIImage` is a recipe and `CIFilter` is mutable. Reuse a `CIContext` appropriate to the rendering surface, but do not share a mutable filter concurrently. Preserve orientation and color-space metadata, and render to an explicit destination. For live video effects, choose the frame-drop policy and make output cancellation/teardown part of the capture pipeline.

Use VideoToolbox only when the product needs direct encoder/decoder control, hardware-assisted low-level processing, or a codec path that higher-level AVFoundation does not own. A compression session needs creation, property configuration, frame submission, callback handling, completion of pending frames, invalidation, and memory cleanup. Match pixel formats, timestamps, dimensions, color transfer, bitrate/quality, and container/muxer policy. Measure actual devices; hardware availability and thermal behavior vary.

## Vision pipeline

Choose a request from the user outcome: text, barcode, rectangle, face/pose, object classification, image feature print, document structure, or a custom model bridge. Preserve image orientation and capture/import provenance. Bound the input dimensions and request revision. For live frames, cancel or coalesce stale requests instead of creating one unbounded request per frame.

An observation should carry:

- source asset/frame identifier and capture time;
- orientation and preprocessing version;
- request/model/revision identifier;
- confidence or quality metrics when provided;
- recognized text/labels/coordinates as a proposal;
- user review/accept/reject/edit state;
- retention/deletion decision.

For OCR, language settings and text height affect results. For live scanning, device support, lighting, motion, focus, and thermal budget affect quality. Do not infer that a recognized name proves a person’s identity or that a detected object is safe/authorized.

## Core ML route

Load a compiled model asynchronously when model size or startup matters. Use `MLModelConfiguration` to express compute-unit policy only after measuring the target devices. Keep model version, input normalization, output schema, and evaluation fixtures explicit. Xcode-generated wrappers are convenient, but inspect the model description and validate feature shapes/types before prediction.

If the model is downloaded/compiled on device, treat compilation and model storage as separate states. Check available compute devices, memory, cancellation, and failures. A model prediction can be locally generated while still being inappropriate to commit; use a reviewable proposal for user-visible records and side effects.

For streaming inference:

`capture queue -> bounded latest-frame/sample buffer -> inference task -> cancellation/token check -> observation -> UI projection`

Measure latency, dropped inputs, peak memory, CPU/GPU/Neural Engine use, battery, and thermal state on representative hardware. Never report “real time” or “on-device” without naming the device/model/fixture and the actual measurement.

## Natural Language

Use Natural Language for deterministic tokenization, language identification, tagging, lexical similarity, embeddings, and classification routes where the task fits. Record locale/language, tokenizer/model revision, text-length limits, and fallback behavior. Keep sensitive text local where possible, redact logs, and distinguish language analysis from a generative or semantic conclusion.

## Core NFC

NFC is a foreground, user-mediated reader session with a session timeout/invalidation lifecycle. The target needs the correct NFC reader usage description and entitlement/formats. Only one reader session of a type can be active at a time; a detected tag can become invalid after the session restarts. Handle multiple tags, unsupported protocols, user cancel, first-read invalidation, connection failure, and session expiration.

Treat NDEF records and protocol responses as untrusted bytes. Parse a strict allowlist of schemes/types/commands, validate length/checksum/authentication where the protocol provides it, and make the side effect user-confirmed. A tag’s serial/payload is not proof of product authenticity, ownership, payment, location, or identity. Core NFC hardware behavior requires a physical device and real tag fixtures; a simulator or static NDEF string is only a parser test.

## MusicKit and ShazamKit

MusicKit requires informed music-data consent and has Apple Music subscription/capability/catalog/user-token state. Keep authorization, catalog lookup, playback, and subscription-offer UI separate. Respect Apple Music licensing/product constraints and do not make a catalog result the app’s own canonical metadata without storing provenance.

ShazamKit uses a one-way acoustic signature and returns a match, no match, or error against the Shazam or custom catalog. A match is evidence that the audio signature resembles catalog content; it is not proof of who is speaking, who owns the recording, what is legally licensed, or what is currently playing in every environment. Stop microphone capture/matching when the feature ends, explain the audio use, and avoid retaining raw audio when a signature/result is enough.

## Typed route matrix

Use one typed adapter per source and keep framework values out of the durable domain model until they have a provenance and review policy.

| Capability | Narrow API route | Normalize | Configuration/lifecycle/proof gate |
| --- | --- | --- | --- |
| OCR from a still image | `VNImageRequestHandler` + `VNRecognizeTextRequest` | Text candidates, confidence, normalized boxes, language/revision, source ID | Orientation, recognition level, language correction/custom words, corrupt input, labeled fixtures, and review. |
| OCR or detection from a stream | `VNImageRequestHandler` with pixel buffers, request region, or `VNSequenceRequestHandler` when temporal state is useful | Frame ID/time, observation revision, dropped/stale marker | Bounded frame queue, cancellation, orientation, thermal/memory, and physical camera evidence. |
| Custom Core ML model through Vision | `VNCoreMLModel` + `VNCoreMLRequest` | Model ID/version, input preprocessing, typed prediction, confidence/quality | Model input/output schema, revision, availability, compute-unit choice, evaluation set, and target-device measurement. |
| Direct Core ML prediction | `MLModel`/generated model interface with `MLModelConfiguration` | Typed feature values and prediction result with model version | Load/compile state, memory, cancellation, model asset provenance, output validation, and representative hardware. |
| Image recipe/render | `CIImage`, `CIFilter`, `CIContext` | Explicit rendered output, color space, orientation, effect version | Mutable filter ownership, output destination, color management, memory, and export proof. |
| Video encode/decode | VideoToolbox compression/decompression session or AVFoundation reader/writer | Codec/container metadata, timestamps, dimensions, completion state | Pixel format, callbacks, pending frames, invalidation, container policy, codec availability, and device performance. |
| NFC NDEF | `NFCNDEFReaderSession` | Strictly parsed records, tag/session ID, user-selected action | Entitlement/usage description, session timeout/cancel, untrusted payload validation, and real tags on physical hardware. |
| NFC tag protocol | `NFCTagReaderSession` and the selected tag protocol | Protocol response with length/status/authentication result | Supported tag types, connection/invalidation, command allowlist, side-effect confirmation, and physical-device proof. |
| Apple Music | MusicKit authorization/catalog/player route | Catalog ID, user/account state, subscription/permission state, provenance | Consent, capability, subscription/account change, licensing/product policy, interruption, and release configuration. |
| Audio recognition | `SHSession` or microphone matching route | Match/no-match/error, signature/catalog ID, confidence/context | Microphone permission, noisy/partial samples, stop/reset, custom catalog, raw-audio retention, and physical audio proof. |

## Model and observation state machine

Keep model readiness separate from inference and domain review:

`sourceUnavailable -> sourceReady -> preprocessing -> modelLoading -> modelReady -> predicting -> observation -> validating -> review -> confirmed`

Side states include `permissionDenied`, `modelMissing`, `modelCompiling`, `unsupportedInput`, `cancelled`, `lowConfidence`, `schemaMismatch`, `memoryPressure`, `thermalLimited`, `noMatch`, and `failed`. A model can be loaded while a particular input is invalid; a prediction can be produced while the model is stale; a match can exist while the domain action is unauthorized.

For every proposal, store or emit:

- source asset/frame/tag/audio reference and capture time;
- preprocessing, orientation, locale, and input dimensions;
- framework/model/catalog identifier and revision;
- confidence/quality/match status when provided;
- bounded output and validation errors;
- user review/accept/edit/reject state;
- retention, deletion, and export decision.

For streaming routes, define the backpressure contract explicitly:

`input queue -> bounded buffer -> inference task -> cancellation check -> observation -> projection`

Choose whether to process every sample, drop late samples, or keep only the newest sample. Measure dropped inputs and latency on each target device class. Do not report “real-time,” “on-device,” or “accurate” without naming the model/framework revision, fixture, device, and measurement.

## Target and privacy matrix

| Route | Target/configuration | Sensitive boundary |
| --- | --- | --- |
| Vision/Core ML on imported media | App target, PhotosUI/file import, model resources | Preserve only the selected asset/reference; redact logs and keep user review before persistence. |
| Live camera/audio analysis | App target with camera/microphone usage descriptions and capture route | Stop capture when the feature ends; do not retain raw frames/audio unless the product says why. |
| NFC | App target with NFC entitlement/reader usage description | Treat tag bytes as untrusted input; no background/persistent reader assumption. |
| MusicKit/ShazamKit | App target with selected capability/authorization route | Separate consent, catalog/account/licensing state, and raw-audio retention from the local match/result. |
| Widget/system projection of a result | Widget/extension target with a minimal shared projection | Do not expose raw media, private OCR, health/identity data, or account content in an archived surface without an explicit privacy policy. |

An on-device model can reduce network exposure, but it does not remove consent, privacy-manifest, retention, accessibility, or domain-validation responsibilities. Keep the device/model evidence attached to the claim that was actually measured.

## Verification matrix

- Playback: buffering, unavailable asset, route/interruption, subtitles/alternate tracks, AirPlay/Picture in Picture, background, low storage, and physical audio routes.
- Capture/processing: permission, orientation, dropped frames, cancellation, slow model, export failure, memory, thermal, and rapid start/stop.
- Vision/Core ML/Natural Language: representative fixtures, locale/model revision, corrupt input, empty/low-confidence output, model unavailable, result review/edit, and privacy/log redaction.
- NFC: entitlement/usage description, real tag types, multiple tags, session timeout/cancel, invalid tag after restart, physical distance/orientation, protocol rejection, and no-tag fallback.
- MusicKit: permission denied, no subscription, catalog/network error, token state, user/account switch, playback interruption, and policy/release configuration.
- ShazamKit: microphone permission, noisy/partial audio, no match, match/error, custom catalog, stop/reset, raw-audio retention, and physical speaker/microphone tests.

## Sources

- [AVKit](https://developer.apple.com/documentation/avkit)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVPlayer](https://developer.apple.com/documentation/avfoundation/avplayer)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIFilter](https://developer.apple.com/documentation/coreimage/cifilter-swift.class)
- [Video Toolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNRecognizeTextRequest](https://developer.apple.com/documentation/vision/vnrecognizetextrequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [MusicKit](https://developer.apple.com/documentation/musickit)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)

---
name: ios-media-ml-and-inputs
description: Route, implement, or review iOS media, camera, audio, Vision, Core ML, Natural Language, NFC, MusicKit, ShazamKit, and video-processing features. Use when a feature captures or imports media, runs on-device models, reads tags, accesses Apple Music, identifies audio, or needs measured physical-device performance.
---

# iOS Media, ML, and Physical Inputs

Use this skill to turn a camera frame, audio stream, imported asset, model, NFC tag, music catalog request, or acoustic match into a bounded, reviewable product flow. Keep this pipeline explicit:

`authorized source -> bounded input -> cancellable processing -> observation/prediction/match -> provenance/review -> durable result or user-confirmed side effect`

## Read before acting

- Inspect the actual Xcode targets, deployment target, device family, scene/lifecycle model, capabilities, entitlements, `Info.plist` usage descriptions, model assets, media formats, persistence, and existing capture/playback adapters.
- Read the [knowledge-base map](../../../README.md), [media/camera/sensor route](../../../40-framework-routes/02-media-camera-and-sensors.md), [media and ML deep dive](../../../42-framework-deep-dives/07-media-vision-ml-and-nfc.md), and [media/ML recipes](../../../70-code-recipes/21-media-vision-ml-and-nfc-recipes.md).
- For AI availability and fallback, read [privacy, availability, safety, and fallback](../../../30-on-device-ai/06-privacy-availability-and-fallback.md). For proof levels, read the [build/device/release checklist](../../../60-verification/01-build-device-and-release-checklist.md) and [permission/entitlement/privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md).
- Refresh the exact official Apple pages in the Sources section before relying on an API spelling, availability annotation, entitlement, codec, model runtime, music access rule, NFC behavior, or iOS 26 claim.

## Route workflow

1. State the user outcome and source ownership: live camera/microphone, imported file, app-owned media, model asset, external NFC tag, Apple Music catalog/account, or ambient audio.
2. Choose the narrowest route. Use AVKit/AVFoundation for playback/capture/session state; Core Image for image recipes/rendering; VideoToolbox only for low-level codec control; Vision for system observations; Core ML for a packaged model; Natural Language for locale-aware text analysis; Core NFC for a foreground tag-reader session; MusicKit for Apple Music authorization/catalog/playback; ShazamKit for acoustic matching.
3. Record target configuration before implementation: permission and usage description, capability/entitlement, supported formats, model availability, locale, account/subscription state, and physical-device requirement. Mark unverified items as `to-verify`.
4. Draw the state machine. Keep permission, source/session readiness, model/asset readiness, processing, result review, persistence, and cleanup as separate states. Include denial, unavailable hardware, malformed input, interruption, timeout, cancellation, no match, no subscription, and retry.
5. Bound the work. Coalesce or drop stale live frames; limit image/audio duration and dimensions; limit NFC payload length; use cancellation checks; avoid one unbounded task per frame; stop capture and release resources when the feature ends.
6. Attach provenance to every result: source identifier, capture/import time, orientation and preprocessing, request/model/revision, locale, confidence or quality when provided, and user review/edit state. Keep an observation, prediction, match, catalog response, or tag payload distinct from domain truth.
7. Define privacy and retention before logging or persistence. Prefer local processing, redact media/text/audio/model outputs from diagnostics, delete raw inputs when no longer needed, and do not add analytics, upload, account access, or telemetry without a product reason and authorization.
8. Verify in layers: compile against the actual SDK, test deterministic fixtures, test denied/interrupted/unavailable states, then exercise the real camera/microphone/audio route/NFC tag/Apple account on representative physical devices. Record device, OS, model, fixture, latency, dropped inputs, memory, battery, and thermal observations instead of claiming generic “real-time” or “on-device” behavior.

## Framework boundaries

### Media and image processing

- `AVPlayer`/`AVPlayerItem` and `AVPlayerViewController` own playback state and native playback surfaces, not business truth or guaranteed first-frame/audio-route availability. Handle buffering, failure, end, interruption, route changes, external playback, and lifecycle transitions.
- `CIImage` is a lazy recipe. A `CIContext` renders it; reuse an appropriate context, but isolate mutable `CIFilter` instances from concurrent access. Preserve orientation, color space, and destination format.
- VideoToolbox is a low-level compression/decompression path. Model session creation, property configuration, frame submission, callback completion, pending-frame drain, invalidation, timestamps, pixel formats, and cleanup. Prefer higher-level AVFoundation when direct codec control is not the product need.

### Vision, Core ML, and Natural Language

- Vision observations are proposals derived from a request, image orientation, revision, and preprocessing. Preserve the source and request metadata; provide review for consequential writes. OCR text, labels, face/pose observations, and coordinates do not prove identity, safety, intent, or medical/legal truth.
- Core ML model loading, compiled assets, input/output shapes, normalization, model version, and `MLModelConfiguration.computeUnits` are explicit runtime state. Compute-unit selection is a policy, not a promise of Neural Engine use, accuracy, latency, or thermal safety. Load asynchronously when appropriate and measure representative hardware.
- Natural Language routes depend on locale, tokenizer/model revision, text limits, and task fit. Keep sensitive text local where possible and distinguish tokenization, language identification, tagging, embeddings, or classification from a generative or factual conclusion.

### NFC, MusicKit, and ShazamKit

- Core NFC is a user-mediated foreground reader session. Validate the entitlement, usage description, supported formats/protocols, session timeout/invalidation, multiple tags, unsupported tags, and physical-device behavior. NDEF records and tag responses are untrusted bytes; a tag is not authenticity, payment, identity, ownership, or location proof.
- MusicKit has separate authorization, Apple Music capability/subscription, catalog, user-token/account, playback, and interruption state. Request informed consent, handle denial and account changes, preserve catalog provenance, and do not equate a catalog result with ownership or licensing.
- ShazamKit returns a match, no-match, or error from an acoustic signature. A match means resemblance to the selected catalog under the tested conditions; it is not speaker identity, recording ownership, legal clearance, or universal recognition. Stop matching when the feature ends and avoid retaining raw audio when a signature/result is sufficient.

## Non-negotiable safety and evidence rules

- Never present model output, OCR, object/face/pose observation, Natural Language result, NFC payload, MusicKit catalog response, or ShazamKit match as identity, authenticity, medical truth, legal truth, guaranteed accuracy, or authorization without a separate validated domain workflow.
- Never claim camera/microphone/NFC/codec/model support, Apple Music availability, audio/video synchronization, “real time,” “on-device,” battery life, or thermal safety from a preview, simulator, fixture, successful compile, or single device.
- Keep source authorization separate from output validity. Permission granted does not mean a usable session; a ready player does not mean rendered output; a loaded model does not mean a valid prediction; a detected tag does not mean trusted data; MusicKit authorization does not mean a subscription; a match does not mean legal or user identity.
- Treat every external or user-controlled input as untrusted. Bound data size and duration, validate types/schemes/commands/shapes, reject malformed payloads, and require confirmation before consequential side effects.
- Stop and clean up capture, playback, reader sessions, model tasks, signatures, and codec sessions on cancellation, view disappearance, interruption, session invalidation, and task expiration. Keep task ownership explicit so stale results cannot overwrite newer state.

## Deliverable

Produce a compact route note or implementation change containing:

- selected framework and rejected alternatives;
- target/device, permission, usage-description, capability, entitlement, model/media-format, account/subscription, and privacy matrix;
- session/model/processing/result state machine with cancellation, backpressure, cleanup, retry, and fallback;
- provenance and review policy for every generated observation/prediction/match;
- source links and exact compile, fixture, physical-device, performance, privacy, signing, and release evidence plan;
- remaining `to-verify` gaps and any claims deliberately not made.

For implementation, change only the requested target and directly related adapters/configuration. Do not add a model download, cloud upload, account, Apple Music access, microphone/NFC permission, background mode, analytics, logging of sensitive inputs, or entitlement without a stated user-facing need and authorization.

## Related routes and recipes

- [Media, camera, and sensor routes](../../../40-framework-routes/02-media-camera-and-sensors.md)
- [Media, Vision, Core ML, NFC, and Music deep dive](../../../42-framework-deep-dives/07-media-vision-ml-and-nfc.md)
- [Media, Vision, Core ML, NFC, and Music recipes](../../../70-code-recipes/21-media-vision-ml-and-nfc-recipes.md)
- [Privacy, availability, safety, and fallback](../../../30-on-device-ai/06-privacy-availability-and-fallback.md)
- [Permission, entitlement, and privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)
- [Build, device, and release checklist](../../../60-verification/01-build-device-and-release-checklist.md)

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

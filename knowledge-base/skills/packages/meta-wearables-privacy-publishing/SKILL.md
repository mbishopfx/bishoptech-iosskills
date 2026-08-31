---
name: meta-wearables-privacy-publishing
description: Audit privacy, consent, iOS permissions, data flows, Meta Wearables terms, acceptable use, App Store metadata, and release gates for DAT and Web App products. Use whenever a wearable feature captures camera/audio, uses personal context, connects a cloud service, or is prepared for testing or publishing.
---

# Meta Wearables privacy and publishing

Make the privacy and publishing contract explicit before implementation or release. Wearable camera, microphone, Display, and personal-context features can create a larger expectation gap than ordinary phone UI.

## Read before acting

- Inspect the actual target, Info.plist usage descriptions, entitlements, privacy manifest, package permissions, network destinations, analytics/crash settings, storage, logs, and App Store metadata.
- Read [privacy, publishing, and release](../../../70-meta-wearables/08-privacy-publishing-and-release.md) and [registration/permissions](../../../70-meta-wearables/02-registration-permissions-and-configuration.md).
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) when the claim includes local-first processing, glasses-native audio/camera, thermal behavior, storage, network, or fallback.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when the feature requests motion, orientation, geolocation, EMG/gesture data, raw sensor retention, or a phone-sensor fallback.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) when release-channel, tester, companion, firmware, on-glasses DAT-app, update-required, or recovery behavior affects the privacy or publishing claim.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) when shared state, raw-media ownership, network boundaries, or phone fallback spans targets.
- Read [Developer Center project and release operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md) for project permission justifications, product listings, telemetry opt-out, versions, testers, and channel evidence.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when the feature depends on bundle/package identity, Meta AI callbacks, Developer Mode, release attestation, package/signing secrets, Web App origin, or the dated DAT App Store warning.
- Use the [device and release evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md) when preparing tester setup, signed-build identity, release-channel evidence, or redacted artifacts.
- Refresh the official [Meta Wearables terms](https://wearables.developer.meta.com/docs/terms), [acceptable use policy](https://wearables.developer.meta.com/docs/acceptable-use-policy), [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), and [Web App documentation](https://wearables.developer.meta.com/docs/develop/webapps).
- Read Apple’s [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), [privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files), [app privacy details](https://developer.apple.com/app-store/app-privacy-details/), and relevant camera/microphone permission guidance.

## Audit workflow

1. Draw the data-flow: glasses/phone source → local adapter → processing → network/vendor → storage/logs → deletion.
2. Name each data class: registration/device metadata, camera frames, audio, transcript, Display content, diagnostics, account identifiers, and analytics/crash data.
3. For each class, record purpose, collection trigger, user notice/consent, on-device versus remote processing, retention, deletion, access, and failure behavior.
4. Verify every required iOS permission and usage description against actual code paths. Do not request camera/microphone access at launch without a clear user action and explanation.
5. Verify DAT settings for analytics/crash behavior and device-access management against the selected release. Document opt-out or always-enabled behavior as the source states it.
6. Review Web App exposure: public HTTPS URL, client-visible data, origin/security controls, authentication, logging, and what happens when the companion app is unavailable.
7. Draft review notes that accurately describe the feature, hardware requirements, account/test path, permissions, and fallback. Do not promise a reviewer can exercise an unsupported preview path.
8. Stop before publishing if a source, permission, consent, data-retention, terms, or physical-device gate is unresolved.

## Fast path

Trace one data path from permission and consent through collection, processing, storage/transmission, deletion, and disclosure metadata. Fix the earliest missing disclosure or release gate before auditing unrelated surfaces.

## Required output

- data-flow and collection matrix;
- permission/consent copy and trigger location;
- privacy manifest/App Store privacy metadata changes;
- Meta terms/acceptable-use review;
- logging and retention policy;
- reviewer/tester setup and hardware requirements;
- Developer Mode versus release-channel compatibility tuple and observed recovery status;
- open legal, product, or physical-device gates.

## Hard boundaries

- Never claim “on-device” processing unless the exact implementation and source establish that the data stays on device.
- Never call a phone microphone or remote transcription a glasses-native microphone feature.
- Never collect raw audio/video silently or retain it by default.
- Never put personal media, credentials, or device identifiers in public Web App assets, logs, screenshots, fixtures, or skill archives.
- Never imply Meta endorsement, App Store approval, or broad generation support from SDK access.
- Never treat a valid callback, Developer Mode registration, attestation result, or
  release-channel membership as proof of local processing, physical capability,
  App Store/Play approval, or production; keep credentials and callback payloads
  redacted.
- Terms and acceptable-use review is not legal advice; escalate material uncertainty to the product owner/counsel.

## Related routes

- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [Camera and audio](../meta-dat-camera-audio/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Developer Center operations](../meta-wearables-developer-operations/SKILL.md)
- [Security and attestation](../meta-wearables-security-attestation/SKILL.md)
- [iOS privacy/performance/release proof](../ios-privacy-performance-release-proof/SKILL.md)
- [iOS privacy, performance, and release proof](../ios-privacy-performance-release-proof/SKILL.md)

## Sources

- [Meta Wearables terms](https://wearables.developer.meta.com/docs/terms)
- [Meta Wearables acceptable use policy](https://wearables.developer.meta.com/docs/acceptable-use-policy)
- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps)
- [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Apple app privacy details](https://developer.apple.com/app-store/app-privacy-details/)
- [Apple ExternalAccessory](https://developer.apple.com/documentation/externalaccessory)

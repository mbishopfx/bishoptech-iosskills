# Research log

The README is the visual entry point. This page keeps the expansion record discoverable without turning the project homepage into a changelog.

## Current state

The knowledge base is organized around a source-and-evidence contract: choose the capability, verify target and availability gates, design the native surface, implement the smallest route, and collect the evidence that the claim actually requires.

The active research lanes include:

- SwiftUI composition, state, navigation, controls, accessibility, alternate input, scenes, media, charts, layout, scrolling, focus, rich text, and visual export.
- Liquid Glass composition, interaction states, safe-area placement, legibility, reduced-effects fallback, adaptive layouts, and native-design verification.
- Apple Intelligence, Foundation Models, Core ML, Vision, Natural Language, Speech, Translation, structured proposals, evaluation fixtures, model readiness, privacy, refusal, and deterministic commit boundaries.
- Apple services and system surfaces including SwiftData, CloudKit, HealthKit, Contacts, EventKit, WeatherKit, HomeKit, Bluetooth, Nearby Interaction, Network, widgets, Live Activities, App Intents, extensions, background work, and document providers.
- Media, spatial, and physical-input routes including AVFoundation, MusicKit, ShazamKit, NFC, ARKit, RealityKit, Metal, SpriteKit, GameKit, haptics, camera, microphone, sensors, and companion devices.
- Identity, commerce, and release work including StoreKit, PassKit, Wallet, Apple Pay, Sign in with Apple, passkeys, Keychain, CryptoKit, privacy manifests, performance, signing, TestFlight, and App Store evidence.

## Expansion record

The source-linked route work is intentionally cumulative. Each expansion adds API selection, target and availability gates, lifecycle ownership, privacy/configuration boundaries, AI review limits where relevant, and a proof matrix. The complete source material lives in [the knowledge-base map](../knowledge-base/README.md), [the coverage matrix](../knowledge-base/coverage-matrix.md), and [the official source registry](../knowledge-base/sources/official-source-registry.md).

The current public bundle includes the 19 role packages listed in the [skills catalog](skills-catalog.md), plus portable `.skill` archives in [knowledge-base/skills/dist](../knowledge-base/skills/dist).

## Refresh rule

When Apple documentation, SDK interfaces, availability, entitlements, privacy requirements, Human Interface Guidelines, hardware behavior, or release requirements change, use the [source refresh and availability package](../knowledge-base/skills/packages/ios-source-refresh-and-availability/SKILL.md). A refresh should identify the changed source signal, affected routes, current SDK facts, evidence level, uncertainty, and the next validation gate.

## Public boundary

This log records engineering research, not a claim of guaranteed Apple approval. Source reading, compilation, simulator behavior, physical-device behavior, signed artifacts, TestFlight, and production behavior remain separate evidence levels.

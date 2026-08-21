# Skill Blueprint: Apple SDK Route Selection

## Use when

Turning a new app idea into an Apple-native architecture, framework choice, permission/entitlement list, and verification plan.

## Inputs

- one-sentence user outcome;
- source/input type;
- local-first or cloud requirement;
- system surfaces;
- device and platform targets;
- privacy, commerce, or safety sensitivity.

## Workflow

1. Identify the source and transformation.
2. Select the narrowest framework from the catalog.
3. Write the handoff between frameworks.
4. Separate domain truth, UI state, derived/model output, and system surface.
5. List permissions, entitlements, Info.plist keys, accounts, and device requirements.
6. Design unavailable/offline/denied/failure paths.
7. Choose preview, simulator, device, and release evidence.
8. Link the exact official Apple sources.

## Refuse to assume

- A backend is required for every app.
- CloudKit is automatically the right sync strategy.
- A simulator can prove hardware, model, sensor, or App Store behavior.
- A permission prompt at launch is good UX.
- An API name alone proves availability.

## Output

- framework route;
- module/data boundaries;
- permission/entitlement matrix;
- user-facing fallback plan;
- implementation order;
- verification gates and source registry updates.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Framework catalog](../40-framework-routes/00-framework-catalog.md)
- [Framework selection questionnaire](../00-foundations/06-framework-selection-questionnaire.md)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)

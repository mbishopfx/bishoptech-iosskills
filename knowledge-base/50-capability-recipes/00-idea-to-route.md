# Idea to Apple Route

Use this worksheet before opening Xcode. After the route is selected, fill the [Xcode target and module plan](../90-templates/xcode-target-and-module-plan.md) and [target-aware feature scaffold brief](../90-templates/target-aware-feature-scaffold.md) before creating app, package, extension, companion, or test targets.

## Step 1: Name the outcome

Write: “A person can [verb] [object] in [context] without [pain].”

## Step 2: Identify the source

- text;
- image/photo;
- camera stream;
- recorded/live audio;
- location;
- sensor/accessory;
- local record;
- cloud record;
- purchase/account;
- another app/system surface;
- 3D/world input.

## Step 3: Choose the first framework

Use the narrowest route in [the framework catalog](../40-framework-routes/00-framework-catalog.md). If more than one framework is needed, write the handoff between them:

source -> transform -> review -> domain record -> system surface

## Step 4: Define the boundaries

- permission:
- entitlement:
- device/hardware:
- network/account:
- private data:
- irreversible side effect:
- availability fallback:

## Step 5: Define proof

- source docs checked:
- build target:
- preview states:
- simulator scenarios:
- physical-device scenarios:
- release/distribution scenarios:

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Framework catalog](../40-framework-routes/00-framework-catalog.md)
- [Evidence and verification language](../00-foundations/05-evidence-and-verification-language.md)

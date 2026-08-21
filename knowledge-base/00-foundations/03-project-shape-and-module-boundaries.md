# Project Shape and Module Boundaries

## A practical native project shape

```text
App/
  AppEntry.swift
  AppRouter.swift
Features/
  FeatureName/
    FeatureView.swift
    FeatureModel.swift
    FeatureService.swift
Domain/
  Models/
  UseCases/
  Policies/
Services/
  Persistence/
  Intelligence/
  Media/
  System/
Infrastructure/
  Authorization/
  Diagnostics/
  FileStore/
SharedUI/
  Components/
  Styles/
  Accessibility/
Extensions/
  Widget/
  LiveActivity/
  AppIntents/
Tests/
```

The exact folders can change. The boundary matters more than the names: a view should not own a database migration, a Foundation Models prompt should not directly mutate a SwiftData context, and a widget should call a shared app intent/service rather than duplicate domain rules.

## Project, target, and module are different boundaries

Use the [project, target, and extension route matrix](../40-framework-routes/11-project-target-and-extension-route-matrix.md) when the feature has more than one product or process. An Xcode project holds related products; a target builds one product such as an app, framework, extension, or test bundle; a Swift package target builds a module or test suite; and a scheme chooses the targets, configuration, destination, and execution inputs for a build action. A folder called `Shared` does not create a safe module boundary by itself.

Keep these responsibilities visible:

- **Project:** shared references and project-level settings.
- **Target:** source/resource membership, linked products, build phases, signing, capabilities, bundle metadata, and the product’s process boundary.
- **Module/package:** importable API and dependency graph that can be compiled and tested independently.
- **Feature:** typed state, use cases, validation, and capability contracts.
- **Surface:** SwiftUI/UIKit/WidgetKit/App Intents/WatchKit/visionOS composition for one target and input model.
- **Scheme/configuration:** the exact build, run, test, profile, or archive inputs used to generate evidence.

Do not let a shared module import an app target, let an extension depend on the main app process, or let a package’s test-only dependency flow into a distributable product. When a target needs a different permission, entitlement, privacy manifest, deployment target, framework, system host, or input model, record that difference instead of hiding it behind a universal boolean.

For a repeatable planning handoff, fill [Xcode target and module plan](../90-templates/xcode-target-and-module-plan.md) and [Target-aware feature scaffold brief](../90-templates/target-aware-feature-scaffold.md). Before a Release or system-surface claim, run the [target configuration and artifact checklist](../60-verification/06-target-configuration-and-artifact-checklist.md).

## Dependency rules that scale

- Domain types should be independent of SwiftUI when practical.
- System adapters should expose small async protocols that can be replaced in tests.
- User authorization is a state machine, not a one-time Boolean.
- AI should return a typed proposal or domain command that a human or deterministic rule can review before side effects.
- App Intents should call the same use cases as visible UI.
- Widgets, Live Activities, and extensions should use shared models and services that work in their separate process constraints.

## Route map for a new idea

Write one sentence for each:

| Question | Example answer |
| --- | --- |
| What does the person do? | Capture a receipt and correct the extracted total. |
| What is the source? | Camera image or Photos item. |
| What is the transform? | Vision text recognition plus a review parser. |
| Where is truth stored? | SwiftData model and original file. |
| What is the UI route? | Capture → review → saved detail. |
| What system surface helps? | App Shortcut to open capture; reminder after save. |
| What fails? | Camera unavailable, OCR uncertain, model unavailable, save error. |
| What proves it? | Permission matrix, device run, persistence relaunch, accessibility pass. |

## Sources

- [SwiftUI App organization](https://developer.apple.com/documentation/swiftui/app-organization)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

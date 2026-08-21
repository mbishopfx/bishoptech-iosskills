# Apple Intelligence System Surfaces

These pages cover Apple Intelligence features an app adopts through system frameworks and App Intents, distinct from directly prompting Foundation Models for an app-owned task.

- [Visual Intelligence and system context](00-visual-intelligence-and-system-context.md)
- [Writing Tools, Image Playground, and model surfaces](01-writing-tools-image-generation-and-model-surfaces.md)
- [System-surface contracts and proof](02-system-surface-contracts-and-proof.md)
- [Context, entities, and system handoff](03-context-entities-and-system-handoff.md)

## Route choice

| Goal | Start here |
| --- | --- |
| Let people find app content that matches a camera/screenshot context | Visual Intelligence + `IntentValueQuery` + lightweight `AppEntity` |
| Let people proofread, rewrite, summarize, or compose text | Standard SwiftUI/UIKit text views and Writing Tools configuration; use custom Writing Tools APIs only for a custom text engine |
| Let people create a stylized image through an Apple system experience | Image Playground sheet/view controller; use programmatic creation only when the current API and availability justify it |
| Let Siri/Spotlight/Shortcuts understand app actions and content | App Intents, App Entities, schemas, donations, and validated domain services |
| Build an app-owned language task or typed proposal | Foundation Models with availability, guided output, tools, review, and fallback |

System surfaces do not remove the need for user control, privacy review, accessibility, localization, fallback states, or physical/system-surface verification. Re-open the current Apple documentation before implementation because several routes and model behaviors are OS/version-sensitive.

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)

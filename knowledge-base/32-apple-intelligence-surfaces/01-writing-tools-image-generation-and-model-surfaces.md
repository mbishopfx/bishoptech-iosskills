# Writing Tools, Image Playground, and Model Surfaces

Apple Intelligence system surfaces are often best adopted by using Apple’s standard text and image interfaces. A native app can gain system behavior without recreating Apple’s UI or routing every task through a custom Foundation Models prompt.

## Writing Tools

Writing Tools provides system proofreading, rewriting, summarization, and composition for supported text views. Standard UIKit text views support the feature, and SwiftUI exposes Writing Tools behavior and affordance controls for text input. Prefer the system text views and attributed-string storage when they fit the product.

### Choose the route

| Text surface | Route | Decision |
| --- | --- | --- |
| Standard SwiftUI `TextEditor`, `TextField`, or UIKit text view | System Writing Tools support | Start here; configure behavior only when the product needs a different experience. |
| Custom UIKit text view or text engine | `Writing Tools` and `UIWritingToolsCoordinator` | Adopt only when the custom engine is necessary; implement the delegate/text synchronization contract. |
| App-owned extraction, typed proposal, or domain action | Foundation Models | Use guided output/tools/review when the task is not simply editing text. |

While Writing Tools is active, it may temporarily modify the text view while the person reviews changes. Pause app-specific synchronization or cloud writes that would conflict with that temporary state. Respect accept/reject behavior and exclude code, proper names, direct quotations, or other protected ranges when the current API supports it.

### SwiftUI surface sketch

The exact enum cases and availability should be checked against the selected SDK:

```swift
import SwiftUI

struct DraftEditor: View {
    @Binding var text: String

    var body: some View {
        TextEditor(text: $text)
            .writingToolsBehavior(.default)
            .writingToolsAffordanceVisibility(.automatic)
            .accessibilityLabel("Draft")
    }
}
```

Keep the content model attributed when formatting, attachments, or Genmoji matter. If a custom file format persists text, preserve supported attachments rather than flattening the content to plain strings.

## Image Playground

Image Playground provides a system interface for generating stylized images from concepts and optional source images. In SwiftUI, start with the documented `imagePlaygroundSheet`; in UIKit/AppKit, use the system view controller when the target platform supports it. Programmatic creation is a separate route with its own availability and asynchronous result handling.

### Image Playground state

`idle -> checking availability -> presenting system sheet -> generating -> approved image -> saved/used`

Also model unavailable capability, cancellation, generation error, source-image access failure, content rejection, storage failure, and the user choosing not to save the result.

### Product boundaries

- The person controls the description and approves the result in the system experience; do not hide generation behind an automatic irreversible action.
- Treat the returned image as user-created/generated content with provenance and retention choices.
- Do not promise a particular style, likeness, semantic accuracy, or availability across every device, language, region, or Apple Intelligence configuration.
- Use Image Playground for the standard system experience; use Foundation Models for an app-owned language task, not as a reason to recreate Image Playground’s interface.
- If an app needs an original illustration pipeline or a non-Apple style, record the separate model/provider, network, privacy, cost, and content-moderation route.

## Genmoji and text persistence

Standard system text views handle Genmoji as specialized text attachments. Custom text views and custom file formats must preserve and render those attachments correctly if the product supports them. Test copy, paste, editing, serialization, export, accessibility, and fallback fonts/content when the target OS supports Genmoji.

## Availability and evidence matrix

| Surface | What to verify | Proof boundary |
| --- | --- | --- |
| Writing Tools | Target OS/SDK, text-view type, Writing Tools behavior/affordance, Apple Intelligence availability, language, and custom-engine API | Compile and text fixtures first; physical device for the actual system experience, Dynamic Type, accessibility, temporary text state, accept/reject, and localization |
| Image Playground | `ImagePlayground` availability, system sheet/controller, source-image permissions, concepts/styles, async completion/cancellation, and output storage | Compile and mocked state handling first; supported physical device for system generation, cancellation, content controls, and result persistence |
| Genmoji | Standard versus custom text view, attributed-string attachments, file serialization, copy/paste, and supported OS | Device/system text testing and file round trips; do not claim support from plain `String` rendering |
| Foundation Models | `SystemLanguageModel` state, prompt/schema/tool version, context, safety, and fallback | Physical device/model configuration and repeatable evaluations; a system Writing Tools result is not Foundation Models app proof |

## System-first design guidance

- Use standard SwiftUI/UIKit text and image controls so Apple’s system integrations can work naturally.
- Preserve the app’s original hierarchy, copy, and visual identity; “Apple-like” means native behavior and quality, not cloning Apple’s screens.
- Keep Liquid Glass limited to the functional/navigation layer that needs it. A system sheet or text surface should not be wrapped in decorative glass that reduces legibility.
- Announce generated content clearly, support editing and rejection, and avoid presenting a generated image or rewrite as verified fact.
- Add a deterministic/manual route so the core app remains useful when Apple Intelligence is unavailable.

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for UIKit views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [Adding Writing Tools support to a custom UIKit view](https://developer.apple.com/documentation/uikit/adding-writing-tools-support-to-a-custom-uiview)
- [SwiftUI text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)
- [ImagePlaygroundViewController](https://developer.apple.com/documentation/imageplayground/imageplaygroundviewcontroller)
- [ImageCreator](https://developer.apple.com/documentation/imageplayground/imagecreator)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Foundation Models updates](https://developer.apple.com/documentation/Updates/FoundationModels)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

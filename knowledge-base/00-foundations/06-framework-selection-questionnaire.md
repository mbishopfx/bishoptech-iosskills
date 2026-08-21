# Framework Selection Questionnaire

Use this before choosing an API because an app idea can often be implemented in several ways. Start with the user outcome, then select the narrowest Apple-native route that fulfills it.

## Questions

1. Is the input text, image, audio, video, location, sensor data, a document, a person, a purchase, or another app’s content?
2. Does the app need a live stream, a one-shot import, or a persistent record?
3. Must the workflow work offline or entirely on-device?
4. Is the result deterministic, probabilistic, or model-generated?
5. Does a system surface need to invoke it outside the app?
6. Does it need background execution, scheduled delivery, or a live status surface?
7. Does it need an entitlement or privacy permission?
8. Does it need a local database, a file/document package, iCloud sync, or a server source of truth?
9. What is the smallest reviewable result before any side effect happens?
10. What evidence must exist before the feature can be called ready?

## First-route examples

| User outcome | Start with | Add when needed |
| --- | --- | --- |
| Store structured local records | SwiftData | CloudKit, file export, Spotlight, App Intents |
| Scan text or codes from a camera | VisionKit | Vision, PhotosUI, SwiftData |
| Classify or transform images | Vision/Core ML | PhotosUI, AVFoundation, Metal |
| Transcribe speech | Speech | AVAudioEngine, file import, on-device availability handling |
| Translate text | Translation | language availability/download flow |
| Summarize or extract text | Foundation Models | guided generation, review UI, remote fallback if approved |
| Expose actions to Siri/Shortcuts | App Intents | AppEntity, EntityQuery, App Shortcuts, WidgetKit |
| Show a persistent live status | ActivityKit/WidgetKit | App Intents, APNs, deep links |
| Sell digital functionality | StoreKit | entitlement service, restore flow, sandbox tests |
| Show a map or route | MapKit/Core Location | authorization, location accuracy, background mode |

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Apple Intelligence and machine learning](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)

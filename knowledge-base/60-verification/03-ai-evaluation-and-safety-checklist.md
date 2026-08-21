# AI Evaluation and Safety Checklist

## Feature contract

- [ ] The model route is the narrowest fit.
- [ ] Deterministic code owns validation, authorization, persistence, and side effects.
- [ ] The model’s intended capabilities and known weak tasks are documented.
- [ ] Typed/guided output is used when the app needs structured data.
- [ ] A review step exists for uncertain or consequential output.

## Availability and behavior

- [ ] Device eligibility is tested.
- [ ] Apple Intelligence disabled is tested.
- [ ] Model not ready/downloading is tested.
- [ ] Language availability is tested.
- [ ] Context size exceeded is tested.
- [ ] Guardrail error is tested.
- [ ] Cancellation and retry are tested.
- [ ] Deterministic/manual fallback is usable.

## Prompt and tool evaluation

- [ ] Prompt version and target OS/model are recorded.
- [ ] Representative inputs cover normal and edge cases.
- [ ] Unclear, empty, oversized, and adversarial inputs are included.
- [ ] User/external input is kept out of trusted instructions.
- [ ] Tool arguments are validated.
- [ ] Query tools are read-only where possible.
- [ ] Action tools are bounded, authorized, idempotent, and reviewable.
- [ ] Tool loops have a clear exit condition.

## Safety and privacy

- [ ] Sensitive data boundaries are documented.
- [ ] Production logging minimizes prompt and response content.
- [ ] User disclosure matches actual on-device/remote behavior.
- [ ] Domain-specific harms and mitigations are listed.
- [ ] A feedback/reporting route exists where appropriate.
- [ ] Model updates trigger prompt and safety regression testing.

## On-device does not erase release/privacy obligations

- [ ] The feature records whether inputs, outputs, embeddings, audio, images, or tool results remain on device, leave the device, or are retained by a service; “on-device” is not used as a blanket privacy guarantee.
- [ ] `PrivacyInfo.xcprivacy`, required-reason API declarations, permission usage descriptions, App Store Connect App Privacy answers, and user-facing copy are reviewed together when the feature uses capture, speech, location, health, identifiers, networking, or third-party SDKs.
- [ ] Production `Logger` messages and signposts exclude raw prompts, model responses, images, audio, health data, credentials, and tool arguments unless the user explicitly consented and the retention path is documented.
- [ ] Model availability, locale/asset readiness, and device capability are tested independently from quality, safety, truthfulness, and task-success evaluation.
- [ ] Model-assisted actions remain deterministic and authorized at the side-effect boundary; the model cannot grant permission, invent an entitlement, bypass a privacy decision, or self-approve a consequential result.

## Test-plan and performance evidence

- [ ] Fast deterministic fixtures cover typed output, validation, cancellation, fallback, and tool authorization with Swift Testing or XCTest.
- [ ] Parameterized tests cover representative languages, malformed input, empty/oversized input, refusal/guardrail states, model-not-ready state, and unavailable-device state.
- [ ] A dedicated test-plan tag or configuration identifies model/device-dependent tests so they are not mistaken for deterministic unit coverage.
- [ ] Performance measurement records prompt/input size, model route, device/OS, warm/cold state, latency budget, memory, energy/thermal observations, and cancellation behavior.
- [ ] Any MetricKit or signpost result is labeled as a diagnostic/performance observation, not a guarantee of output quality or response time for every device.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Prompting an on-device foundation model](https://developer.apple.com/documentation/foundationmodels/prompting-an-on-device-foundation-model)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)
- [Describing data use in privacy manifests](https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests)
- [App privacy details on the App Store](https://developer.apple.com/app-store/app-privacy-details/)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Logging](https://developer.apple.com/documentation/os/logging/)
- [Recording Performance Data](https://developer.apple.com/documentation/os/recording-performance-data)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Monitoring app performance with MetricKit](https://developer.apple.com/documentation/metrickit/monitoring-app-performance-with-metrickit)

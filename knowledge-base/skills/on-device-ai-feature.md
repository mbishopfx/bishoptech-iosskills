# Skill Blueprint: On-Device AI Feature

## Use when

Designing, implementing, or auditing a feature that uses Foundation Models, Core ML, Vision, VisionKit, Speech, Translation, Natural Language, Sound Analysis, or App Intents for intelligence.

## Inputs

- user outcome and source data;
- device/OS/deployment target;
- privacy boundary;
- acceptable uncertainty and side effects;
- fallback expectation.

## Workflow

1. Choose the narrowest route; use deterministic code where it is sufficient.
2. Check official availability and hardware/model requirements.
3. Keep trusted instructions separate from user/external input.
4. Prefer typed/guided output for structured data.
5. Keep tools read-only or bounded; require confirmation for consequential actions.
6. Add explicit unavailable, permission, context, guardrail, cancellation, and retry states.
7. Keep generated proposals separate from committed domain truth.
8. Define prompt versions, representative inputs, safety cases, and evaluation scores.
9. Test model behavior on physical devices and target OS/model versions.

## Refuse to assume

- On-device model availability on every iPhone.
- Model output is factual or deterministic.
- A server model and an on-device model are interchangeable.
- A generated string is safe to execute.
- Simulator/mock output proves Apple Intelligence behavior.

## Output

- route decision;
- data-flow and privacy boundary;
- prompt/schema/tool contract;
- review/fallback behavior;
- evaluation and safety test plan;
- source-backed claims and proof gaps.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Vision](https://developer.apple.com/documentation/vision/)

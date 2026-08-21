# Core ML model lifecycle and inference proof matrix

This matrix separates documentation, compile, deterministic test, simulator, physical-device, and release evidence. A route is not complete because a model file exists or a generated wrapper compiles.

## Evidence ladder

| Claim | Minimum useful evidence | Stronger evidence | Does not prove |
| --- | --- | --- | --- |
| The model is present | Target/resource inspection and model manifest | Signed artifact inspection plus device file check | Contract compatibility or quality. |
| The model can load | Unit/integration fixture with the compiled asset | Signed physical-device load with the intended configuration | Prediction correctness or performance. |
| The model contract matches | `MLModelDescription` inspection and schema tests | Candidate installation test on every supported model revision | Real-world output quality. |
| A feature adapter is correct | Type/shape/image/normalization fixtures | Physical input capture and end-to-end prediction | Domain truth or user intent. |
| A compute policy is selected | Configuration inspection | Named-device cold/warm benchmark with policy and OS recorded | Universal latency, Neural Engine use, or thermal safety. |
| A prediction runs | Deterministic input fixture | Signed physical-device prediction with captured result metadata | Accuracy outside the tested fixture. |
| A live pipeline is usable | Frame/backpressure state tests | Physical camera/audio run with dropped frames, memory, energy, and thermal notes | Every hardware tier or background condition. |
| A stateful model is safe | State reset/serialization tests | Long-running device session with state contention and interruption | Correctness of an untested sequence distribution. |
| A model can update | `MLUpdateTask` fixture with labeled data and failure cases | Device personalization run with progress, cancellation, atomic save, re-load, and reset | Quality improvement or acceptable privacy policy. |
| A downloaded model is safely promoted | Temp/compile/contract/fallback tests | Network-to-device install with interruption, disk pressure, rollback, and relaunch | Server provenance unless separately verified. |
| The result is reviewable | Proposal schema and accept/edit/reject tests | Accessibility/device review flow with source and model version visible | That a user accepted the claim because it was true. |
| Privacy promise is implemented | Redaction, retention, and deletion tests | Device inspection of logs/files plus policy review of distribution build | Privacy outside the tested route or third-party behavior. |
| Liquid Glass UI is native and legible | Preview states and target compile | Physical light/dark, contrast, transparency, Dynamic Type, motion, and media-background run | Usability from a screenshot. |
| Accessibility task works | Semantic label/action and UI-test fixtures | VoiceOver, Voice Control, Switch Control, keyboard, pointer, and Dynamic Type task on device | Accessibility in every locale or assistive configuration. |
| Release artifact contains the route | Archive/resource/entitlement/privacy inspection | Signed TestFlight/App Store artifact and install/launch/model run | Production model service or App Store review outcome. |

## Model-installation proof matrix

| State/claim | Fixture or deterministic check | Physical-device proof | Artifact/release proof |
| --- | --- | --- | --- |
| Bundled model | Resource URL exists; generated wrapper or direct load path resolves | Cold and warm load on named devices | Target membership and compiled model resource in archive. |
| Download started | Manifest/state transition and cancellation tests | Network interruption/resume and disk pressure | Background/network capability and privacy configuration if used. |
| Source model downloaded | File type, size, version, digest/manifest tests | Device file exists in app-owned temporary directory | No secret model URL or credential leakage in signed artifact. |
| Compiled asset created | `compileModel(at:)` adapter tests and cleanup | Compile time, storage, interruption, and relaunch | Runtime model code and required target availability. |
| Candidate promoted | Contract and evaluation gates; atomic replacement fixture | Failed candidate leaves active model usable | Persisted manifest and target resources match release. |
| Model removed | Deletion/reset fixture invalidates active model and outputs | Device storage and relaunch confirm removal | Distribution route does not silently restore a deleted model. |

## Feature-contract proof matrix

| Contract area | Test it with | Failure that must be visible |
| --- | --- | --- |
| Feature name | Required-name set and duplicate/missing fixtures | Candidate rejected before prediction. |
| Feature type | `MLFeatureType` fixtures for numeric, string, image, dictionary, sequence, multi-array, state | Adapter mismatch with a remediation, not a crash. |
| Image constraints | Width/height/pixel-format/orientation fixtures | Input is resized/cropped/rejected by an explicit policy. |
| Multi-array shape | Rank, dimensions, scalar type, and shape-constraint fixtures | Shape mismatch is not hidden by an unsafe cast. |
| Output set | Required output names and optional-output tests | Missing result becomes an error or “not enough evidence.” |
| Metadata/version | Manifest and model-description comparison | Unknown model version remains inactive. |
| Update capability | `isUpdatable`, training-input, and parameter inspection | Personalization route is disabled if unsupported. |
| State | State description and serialized prediction fixture | Concurrent state use is rejected or serialized. |

## Inference and quality proof

Record a fixture or evaluation result with:

```text
model ID/version/schema:
asset source and digest/manifest:
MLModelConfiguration / compute policy:
device / OS / SDK / deployment target:
input fixture ID and preprocessing:
expected output or acceptance criteria:
observed output / score / error:
cold or warm state:
latency / memory / energy / thermal:
source provenance and privacy handling:
review decision and domain command:
```

Do not infer quality from a single successful image or text sample. Keep domain evaluation separate from runtime compatibility. If a classifier score is shown, document how thresholds were chosen and what “unknown” or “not enough evidence” means.

## Stateful/update proof

For a stateful model, prove that:

- a new state is created for a new logical session;
- stateful predictions sharing one state are serialized;
- state buffers are not read or mutated during an in-flight prediction;
- interruption, backgrounding, and session reset have an explicit policy;
- state does not leak across users, records, or source sessions.

For an updatable model, prove that:

- only an updatable compiled model enters the update route;
- labeled training data is authorized and validated;
- progress, cancellation, failure, and storage errors are surfaced;
- the updated asset is saved through a temporary path and promoted atomically;
- the updated model passes the same feature-contract and evaluation gates;
- reset/delete removes personalized state as promised.

## Accessibility and Liquid Glass proof

The proof run must include model states, not just a ready result:

```text
missing -> downloading -> compiling -> validating -> ready
predicting -> needs review -> accepted/rejected
unavailable -> fallback
failed -> retry/remove
updating -> previous model remains active
```

For each state, verify a semantic status, a readable source/provenance summary, an action that does not depend on color or motion, and a route that works without direct access to the media preview. Record Dynamic Type, locale, color scheme, increased contrast, reduced transparency, reduced motion, VoiceOver, Voice Control, Switch Control, keyboard, pointer, and touch conditions.

## Physical-device and release checklist

- [ ] Device model, OS, SDK, deployment target, and build configuration recorded.
- [ ] Model asset and manifest verified in the installed signed build.
- [ ] Runtime `MLModel` load succeeds with the intended configuration.
- [ ] Input adapter uses real permissions and real source orientation/format.
- [ ] Prediction output is normalized with model ID/version and source ID.
- [ ] Cold/warm latency, memory, dropped frames, energy, and thermal notes captured.
- [ ] Failure/retry/rollback path exercised with network and storage changes.
- [ ] Accessibility task completed with at least one assistive configuration.
- [ ] Privacy retention/deletion behavior inspected on device.
- [ ] Archive/target membership/privacy strings/entitlements verified.
- [ ] No claim exceeds the evidence actually captured.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [MLModelDescription](https://developer.apple.com/documentation/coreml/mlmodeldescription)
- [MLFeatureDescription](https://developer.apple.com/documentation/coreml/mlfeaturedescription)
- [MLFeatureValue](https://developer.apple.com/documentation/coreml/mlfeaturevalue)
- [MLFeatureProvider](https://developer.apple.com/documentation/coreml/mlfeatureprovider)
- [MLShapedArray](https://developer.apple.com/documentation/coreml/mlshapedarray)
- [MLState](https://developer.apple.com/documentation/coreml/mlstate)
- [MLUpdateTask](https://developer.apple.com/documentation/coreml/mlupdatetask)
- [Personalizing a Model with On-Device Updates](https://developer.apple.com/documentation/coreml/personalizing-a-model-with-on-device-updates)
- [Downloading and Compiling a Model on the User’s Device](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

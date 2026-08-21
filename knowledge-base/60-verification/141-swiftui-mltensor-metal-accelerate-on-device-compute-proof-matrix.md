# SwiftUI MLTensor, Metal, and Accelerate on-device compute proof matrix

This matrix defines the evidence for a low-level tensor or GPU route. It pairs with the [on-device compute review](../42-framework-deep-dives/116-swiftui-mltensor-metal-accelerate-on-device-compute-review.md), the [design review](../21-design-deep-dives/144-swiftui-mltensor-metal-accelerate-on-device-compute-review-design.md), the [route](../50-capability-recipes/147-swiftui-mltensor-metal-accelerate-on-device-compute-review-route.md), and the [recipes](../70-code-recipes/159-swiftui-mltensor-metal-accelerate-on-device-compute-review-recipes.md).

The proof must distinguish tensor shape/type, data ownership, numerical correctness, compute-device behavior, end-to-end performance, UI state, privacy, and release evidence. A fast-looking kernel or a successful command-buffer completion is not a product claim by itself.

## Evidence vocabulary

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Tensor descriptor/contract | Shape, rank, scalar type, stride, plane, and layout are recorded | The operation is numerically correct or fast |
| `MLTensor` result | A tensor operation produced a typed result | Which device executed it, or semantic quality |
| `MLComputePolicy` scope | A requested CPU/CPU-GPU policy surrounded tensor work | Every operation used a particular hardware block |
| BNNS Graph context | A CPU graph compiled/configured/executed | GPU/Neural Engine performance or camera fidelity |
| MPSGraph executable | A graph compiled/ran for a target | Resource lifetime, thermal, or app-level latency |
| Metal resource record | Buffer/texture/tensor/storage/usage are configured | Correct synchronization or supported device coverage |
| Command-buffer completion | GPU work reached a completion/error state | Numerical correctness, low latency, or safe reuse before completion |
| Pixel-buffer texture creation | A Core Video image buffer was bridged to a Metal texture | No-copy end-to-end performance or source retention safety |
| CPU/GPU benchmark | A measured workload result on a named device | Universal performance, battery, or thermal behavior |
| SwiftUI screenshot | A compute state is rendered | Accessibility, command completion, or user comprehension |
| Physical-device run | A signed build exercised the route on named hardware | Every device family or release quality |
| Archive/TestFlight inspection | Intended compute resources and entitlements are distributed | App Store approval or production behavior |

## Environment and contract record

Capture:

- app/target/bundle/build/source revision;
- Xcode/SDK/macOS/deployment target and framework availability;
- device model, OS build, architecture, GPU family, power/network/thermal state;
- input source, frame ID/timestamp, pixel format, color/orientation, dimensions;
- tensor shape/rank/scalar type/stride/layout/plane and expected ranges;
- `MLComputePolicy`, BNNS/MPSGraph target, Metal device/feature family, storage mode, usage, hazard policy;
- buffer/texture/tensor ownership and completion/reuse boundary;
- reference fixture digest, output tolerance, task validator, and fallback;
- privacy classification/retention for source, tensors, logs, and diagnostics.

## Abstraction-selection matrix

| Claim | Required evidence | Pass condition |
| --- | --- | --- |
| `MLTensor` is appropriate | Baseline versus tensor route | No extra materialization/copy defeats the chosen path |
| BNNS Graph is appropriate | CPU baseline and graph trace | Dynamic shapes/workspace/CPU budget pass |
| MPSGraph is appropriate | Graph compile/run and device record | Feeds/targets/device/queue contract passes |
| Metal is necessary | Bottleneck/unsupported-op evidence | Custom operation has measured product value |
| Accelerate is appropriate | CPU image/vector/DSP comparison | Format conversion and CPU energy/latency fit |
| Higher-level Core ML/Core AI is sufficient | Route comparison | Low-level implementation is not maintained without benefit |

## Tensor correctness matrix

| Claim | Test | Evidence | Pass condition |
| --- | --- | --- | --- |
| Shape is correct | Rank/dimension fixture | Descriptor/shape snapshot | All supported and rejected shapes are explicit |
| Scalar type is correct | Float/int/bool/precision fixtures | Type record and output check | No accidental cast or overflow |
| Layout is correct | Transpose/stride/contiguous fixture | Layout/stride record | Output matches reference with documented layout |
| Dynamic bounds are safe | Min/typical/max/invalid shapes | Bound and rejection log | Invalid shapes never reach an unsafe kernel |
| Materialization is bounded | Tensor-to-array/UI route | Materialization timing/memory | Only required values cross the CPU/UI boundary |
| No-copy memory is safe | Release/reuse stress test | Buffer lifetime and completion record | Source remains valid until all consumers complete |
| Numerical output is correct | Reference fixture comparison | Error/tolerance report | Difference is within approved tolerance |
| Task result is correct | Domain fixtures | Semantic validator | Product acceptance passes separately from numerical tolerance |

## Compute-device and policy matrix

| Claim | Test | Evidence |
| --- | --- | --- |
| CPU policy works | CPU-only fixture | Policy, timing, memory, thermal |
| CPU/GPU policy works | Same fixture with CPU/GPU policy | Policy scope and physical trace |
| MPSGraph target works | Compile/run on each claimed target | Device, executable, feed/result record |
| Metal feature is supported | Runtime family/capability check | Feature-set/device matrix |
| Tensor dtype is supported | Create/use descriptor on each target | OS/device/data-type record |
| Fallback works | Unsupported device/feature fixture | Deterministic CPU/Core ML/manual route |
| Policy is not overclaimed | Compare estimate and actual trace | UI/documentation labels estimates versus measurements |

## Data-path and ownership matrix

| Claim | Test | Evidence | Pass condition |
| --- | --- | --- | --- |
| Pixel buffer is compatible | Capture each supported format/plane | Format/color/orientation record | Conversion or rejection is intentional |
| Texture cache bridge works | `CVMetalTextureCache` fixture | Cache/device/plane/texture record | Texture maps to intended source plane |
| Buffer/texture storage is correct | Shared/private/memoryless variants | Descriptor/storage/usage record | CPU/GPU access matches policy |
| Resource is not reused early | Hold source until GPU completion | Command-buffer and lifetime trace | No corrupted frames/results |
| Queue ownership is bounded | Concurrent request stress | Admission and in-flight count | No unbounded command buffers/resources |
| Error/cancellation is handled | Cancel/fail command/graph | Error and UI state record | No stale result is published or committed |
| Privacy is preserved | Log/diagnostic audit | Redacted fields and retention record | Raw frames/tensors are not leaked |

## BNNS Graph matrix

| Claim | Evidence | Pass condition |
| --- | --- | --- |
| Graph compiles | Context creation record | Correct source model/function/options |
| Dynamic shapes are safe | Shape-setting and execution trace | Shapes set before execution and not mutated in flight |
| Tensor descriptors are correct | Shape/stride/allocation record | Inputs/outputs use expected memory |
| Workspace is bounded | Workspace-size/allocation trace | Peak memory fits device budget |
| CPU route is responsive | Physical device plus UI frame trace | Main actor remains responsive |
| Output matches reference | Numerical/task fixture | Tolerance and semantic acceptance pass |

## MPSGraph matrix

| Claim | Evidence | Pass condition |
| --- | --- | --- |
| Graph contract is stable | Placeholder/operation/target snapshot | Shape and data-type mapping is reviewable |
| Executable compiles | Compile result/device record | Intended target and package version are recorded |
| Feeds/outputs are compatible | MTLBuffer/MTLTexture-backed fixture | No hidden copy or layout mismatch |
| Async run is safe | Queue/command/completion trace | Resources live until completion |
| Serialized executable is safe | Package version/digest/device test | Incompatible package is rejected/fallbacks |
| End-to-end value exists | Baseline comparison | Graph adds measurable product value |

## Metal matrix

| Claim | Test | Evidence |
| --- | --- | --- |
| Custom kernel is necessary | Baseline/bottleneck report | Operation is not needless duplication |
| Kernel bounds are safe | Min/max/invalid dimensions | No out-of-bounds writes |
| Pipeline compiles | Target SDK/device compile | Compiler/feature/OS record |
| Resource bindings are correct | Known-pattern input/output | Buffer/texture/tensor binding snapshot |
| Storage mode is appropriate | Shared/private/memoryless comparison | Access pattern and measurement support choice |
| Synchronization is correct | CPU/GPU overlap and reuse stress | No read/write hazard or stale output |
| Completion is handled | Error/cancel/timeout fixture | UI state and resource cleanup are correct |
| Performance is real | Same end-to-end workload | Device-specific latency/memory/thermal result |

## Performance, memory, and thermal matrix

Measure the entire path:

- source decode/capture and pixel conversion;
- buffer/texture/tensor creation and any copy;
- graph/pipeline compilation and warmup;
- queue wait, command encoding, execution, and completion;
- tensor materialization/readback;
- SwiftUI publication/rendering;
- concurrent work, peak memory, dropped frames, thermal state, battery, and cancellation.

Record p50/p95/p99 where useful and name the device/workload. A single command-buffer GPU time excludes the costs that often dominate the app.

## SwiftUI and accessibility matrix

| Task | Required evidence | Pass condition |
| --- | --- | --- |
| Select/capture source | UI test and physical device | Source/freshness/orientation are understandable |
| Start/stop/cancel | Assistive input and cancellation run | No hidden gesture or main-thread wait |
| Understand status | VoiceOver/Dynamic Type/reduced motion | Preparing/running/paused/stale/fallback are conveyed |
| Review result | Candidate/provenance/warning fixture | Result is editable and not overclaimed |
| Save/undo/fallback | Domain and release run | Deterministic commit follows validation/approval |
| Use glass controls | Contrast/transparency variants | Material is optional and content remains legible |

## Evidence packet

~~~text
feature:
target_bundle_build:
source_revision:
sdk_xcode_macos_deployment:
device_os_architecture_gpu_family:
input_source_frame_pixel_format_orientation:
tensor_shape_scalar_type_layout_stride_planes:
abstraction:
ml_compute_policy:
metal_device_storage_usage_hazards:
bnns_or_mpsgraph_artifact:
command_queue_buffer_generation:
reference_fixture_digest:
numerical_tolerance_result:
semantic_validation_result:
copy_and_materialization_cost:
latency_p50_p95:
peak_memory:
frame_hitches_dropped_work:
thermal_battery_notes:
cancellation_error_result:
privacy_retention_review:
accessibility_tasks:
fallback_result:
archive_result:
testflight_result:
release_decision:
known_gaps:
~~~

## Stop criteria

Block release when shape/type/layout/lifetime is implicit; when a no-copy or shared resource can be reused early; when a device or storage policy is assumed from a simulator; when a benchmark omits copies/synchronization/materialization; when a custom kernel lacks a reference/fallback; when cancellation leaves stale results or leaked resources; when thermal/memory behavior is untested; when raw/intermediate data is logged without retention approval; or when the signed release route has not run the physical-device fallback.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLTensor](https://developer.apple.com/documentation/coreml/mltensor)
- [MLComputePolicy](https://developer.apple.com/documentation/coreml/mlcomputepolicy)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
- [MLComputeDevice](https://developer.apple.com/documentation/coreml/mlcomputedevice)
- [Accelerate](https://developer.apple.com/documentation/accelerate)
- [BNNS](https://developer.apple.com/documentation/accelerate/bnns-library)
- [BNNSGraph.Context](https://developer.apple.com/documentation/accelerate/bnnsgraph/context)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLBuffer](https://developer.apple.com/documentation/metal/mtlbuffer)
- [MTLTexture](https://developer.apple.com/documentation/metal/mtltexture)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [Compute passes](https://developer.apple.com/documentation/metal/compute-passes)
- [MTLTensor](https://developer.apple.com/documentation/metal/mtltensor)
- [MTLTensorDescriptor](https://developer.apple.com/documentation/metal/mtltensordescriptor)
- [Setting resource storage modes](https://developer.apple.com/documentation/metal/setting-resource-storage-modes)
- [Choosing a resource storage mode for Apple GPUs](https://developer.apple.com/documentation/metal/choosing-a-resource-storage-mode-for-apple-gpus)
- [Resource fundamentals](https://developer.apple.com/documentation/metal/resource-fundamentals)
- [Metal Performance Shaders Graph](https://developer.apple.com/documentation/metalperformanceshadersgraph)
- [MPSGraph](https://developer.apple.com/documentation/metalperformanceshadersgraph/mpsgraph)
- [CVMetalTextureCacheCreateTextureFromImage](https://developer.apple.com/documentation/corevideo/cvmetaltexturecachecreatetexturefromimage%28_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A%29?changes=_3_2&language=objc)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

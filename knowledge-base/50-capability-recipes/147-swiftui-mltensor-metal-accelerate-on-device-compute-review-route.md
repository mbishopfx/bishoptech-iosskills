# SwiftUI MLTensor, Metal, and Accelerate on-device compute route

This route turns the [on-device compute review](../42-framework-deep-dives/116-swiftui-mltensor-metal-accelerate-on-device-compute-review.md) into an implementation sequence. Pair it with the [design review](../21-design-deep-dives/144-swiftui-mltensor-metal-accelerate-on-device-compute-review-design.md), the [proof matrix](../60-verification/141-swiftui-mltensor-metal-accelerate-on-device-compute-proof-matrix.md), and the [recipes](../70-code-recipes/159-swiftui-mltensor-metal-accelerate-on-device-compute-review-recipes.md).

Use this route when high-level Core ML/Core AI integration is not enough. Keep the low-level layer isolated behind an app-owned adapter, with a deterministic fallback and a reviewable result contract.

## 1. Freeze the work contract

Record:

- product outcome and whether the result is transient, reviewable, or durable;
- source type and provenance: photo, camera frame, document, audio, or generated fixture;
- tensor shape/rank/scalar type/layout and dynamic bounds;
- CPU/GPU/Neural Engine/model policy and target device/OS;
- abstraction: `MLTensor`, BNNS Graph, MPSGraph, Metal, Accelerate, or a composed route;
- buffer/texture/tensor backing memory, storage mode, stride, plane, alignment, and lifetime;
- queue/command-buffer/actor ownership and cancellation/backpressure policy;
- reference fixtures, numerical tolerance, semantic validation, user approval, and fallback;
- privacy/logging/retention and release evidence.

If a requirement is only “make it faster,” define the measured end-to-end workload first.

## 2. Select the narrowest abstraction

1. Start with an existing Core ML/Core AI model route if it owns the full model contract.
2. Use `MLTensor` for typed tensor math and materialization in Swift.
3. Use BNNS Graph for CPU-based graph execution or a CPU baseline.
4. Use MPSGraph for a symbolic graph that can compile/run across Apple compute devices.
5. Use Metal for a custom GPU operation, explicit resource/storage control, or a tensor/kernel that the higher-level layer cannot express.
6. Use Accelerate/vImage/vDSP for CPU image/DSP/vector transforms where a GPU route would add copies or synchronization.

Do not use raw Metal merely to make a standard resize, reduction, or model call look more advanced.

## 3. Define the tensor and data contract

Create a contract containing:

- shape and dynamic-shape bounds;
- scalar type/precision and quantization plane semantics;
- dimension order and stride;
- image pixel format/color/orientation;
- buffer/texture/tensor binding and storage mode;
- device/feature-set minimum;
- input/output ownership and reuse point;
- materialization boundary and validation mapping.

The contract should be testable without SwiftUI. The domain layer should receive a typed result, not a pointer or Metal resource.

## 4. Build the source adapter

For `CVPixelBuffer`:

1. choose capture output format and plane policy;
2. preserve frame ID, timestamp, orientation, and color metadata;
3. create a texture through `CVMetalTextureCache` only when the target path needs it;
4. keep the pixel buffer alive until GPU/graph completion;
5. reject or convert unsupported format/size;
6. release/recycle only after completion.

For imported images:

1. decode once at a bounded size;
2. perform crop/resize/color conversion in the chosen layer;
3. retain source ID and preprocessing revision;
4. avoid a second copy when a compatible buffer/texture path exists;
5. validate output against a known fixture.

## 5. Use `MLTensor` for typed tensor math

1. Create tensors from known shape/scalar type/data or a deliberately owned no-copy buffer.
2. Apply `MLComputePolicy` only around the intended scope.
3. Build operations with explicit shape checks.
4. Avoid unnecessary `shapedArray` materialization.
5. Await materialization off the main actor when CPU/UI values are needed.
6. Validate finite values, ranges, shape, and result provenance.

The policy is a hint/constraint for tensor operations, not an observed hardware trace. Test with default and restricted policies where the product cares.

## 6. Use BNNS Graph for the CPU path

1. Compile the graph or model into a `BNNSGraph.Context`.
2. Define dynamic shapes before execution.
3. Query/allocate tensor descriptors and required workspace.
4. Reuse context/workspace only within its documented ownership boundary.
5. Execute off the main actor.
6. Map output tensors to a typed candidate.
7. Measure CPU time, memory, and sustained behavior.

Use this route as an intentional CPU baseline or fallback, not as proof that the GPU/Neural Engine route behaves equivalently.

## 7. Use MPSGraph for graph-level composition

1. Create placeholders and operations with explicit shape/data-type contracts.
2. Select target tensors/operations for the executable.
3. Compile for the intended device and record the compilation target.
4. Create feeds backed by compatible `MTLBuffer`/`MTLTexture`/tensor data.
5. Run or encode through the intended command queue.
6. Await completion and map results.
7. Serialize/load the executable only with a versioned artifact policy.

Keep graph construction/compilation out of the first interactive tap where possible. Warm/compile state is part of readiness.

## 8. Use Metal for a bounded custom operation

1. Confirm the operation is a measured bottleneck or unsupported primitive.
2. Write a reference CPU/MLTensor/BNNS/MPSGraph implementation.
3. Define input/output descriptors and supported shapes.
4. Choose `MTLStorageMode` from actual CPU/GPU access patterns.
5. Create the pipeline/encoder on the correct `MTLDevice`.
6. Encode bounds-safe work into a command buffer.
7. Keep resources alive until completion.
8. Map command-buffer errors and unsupported devices to a fallback.
9. Compare numerical output and end-to-end performance.

Do not ship a custom kernel without a reference implementation and physical-device evidence.

## 9. Connect queues and actors

Use one owner for:

- `MTLDevice`/queue/pipeline cache;
- graph/executable;
- in-flight resource pool;
- generation/cancellation token;
- telemetry and result publication.

The main actor owns UI state. A compute actor/isolated service owns admission and resource lifecycle. A completion result is published only if source ID, task ID, generation, and model/compute revision still match.

## 10. Bound live work

Choose one policy:

- latest-frame only;
- bounded FIFO;
- drop-new while work is in flight;
- periodic sampling;
- explicit capture then process.

Record dropped frames and cancellation decisions in diagnostics. Do not let capture rate create unbounded command buffers, tensors, or SwiftUI updates.

## 11. Choose resource storage and synchronization

Use system defaults unless a measured access pattern justifies an explicit storage mode. For each buffer/texture/tensor, record:

- who writes it;
- who reads it;
- when CPU access occurs;
- when GPU/graph access completes;
- whether it is private/shared/memoryless;
- whether a blit/copy or texture view is needed;
- whether hazard tracking is sufficient.

The data path is not complete until synchronization and release are defined.

## 12. Add the SwiftUI state route

```text
sourceMissing -> sourceReady -> preparing -> running
                                  |             |
                                  v             v
                              constrained     complete
                                  |             |
                                  v             v
                               fallback -> review -> approved -> committed
```

Carry source/frame ID, tensor/compute revision, device policy, and timing status through each state. Expose low-level details in an advanced inspector, not as the only status language.

## 13. Add review and deterministic validation

1. Store raw/derived output only within the privacy policy.
2. Validate shape, finite/range, coordinate system, source freshness, and domain schema.
3. Present a candidate with provenance and warnings.
4. Require explicit approval where the result changes durable data.
5. Call an app-owned deterministic command.
6. Provide undo/reject/manual fallback.

Never let a Metal or MLTensor output call a database/network/commerce side effect directly.

## 14. Profile end to end

Measure:

- input conversion/copy;
- tensor/buffer/texture creation;
- graph/pipeline compile and warm state;
- command queue wait and execution;
- output readback/materialization;
- SwiftUI publish/render;
- memory, frame hitches, thermal, battery, and sustained latency.

Compare the same workload and device with baseline and optimized routes. If custom compute is not faster end to end or does not provide a required capability, remove it.

## 15. Verify failure and release

Force:

- unsupported dtype/shape/pixel format/device family;
- no texture cache/device/queue/pipeline;
- command-buffer error or timeout;
- source frame reuse and stale completion;
- memory pressure and thermal constraint;
- cancellation during encoding and completion;
- graph compile/load failure;
- reduced transparency/motion/accessibility settings;
- iOS 26 fallback;
- archive/TestFlight route with the final resources.

Block release until numerical fixtures, task validation, physical-device performance, privacy, accessibility, signed artifacts, and fallback evidence agree.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLTensor](https://developer.apple.com/documentation/coreml/mltensor)
- [MLComputePolicy](https://developer.apple.com/documentation/coreml/mlcomputepolicy)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
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
- [Metal Performance Shaders Graph](https://developer.apple.com/documentation/metalperformanceshadersgraph)
- [MPSGraph](https://developer.apple.com/documentation/metalperformanceshadersgraph/mpsgraph)
- [CVMetalTextureCacheCreateTextureFromImage](https://developer.apple.com/documentation/corevideo/cvmetaltexturecachecreatetexturefromimage%28_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A%29?changes=_3_2&language=objc)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

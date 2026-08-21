# SwiftUI MLTensor, Metal, and Accelerate on-device compute review

This review covers the lower-level computation layer underneath Core ML/Core AI features: `MLTensor`, `MLComputePolicy`, BNNS Graph, MPSGraph, Metal buffers/textures/tensors, Core Video pixel-buffer interop, queues, command buffers, storage modes, and memory/thermal proof. It pairs with the [on-device compute design](../21-design-deep-dives/144-swiftui-mltensor-metal-accelerate-on-device-compute-review-design.md), the [implementation route](../50-capability-recipes/147-swiftui-mltensor-metal-accelerate-on-device-compute-review-route.md), the [proof matrix](../60-verification/141-swiftui-mltensor-metal-accelerate-on-device-compute-proof-matrix.md), and the [code recipes](../70-code-recipes/159-swiftui-mltensor-metal-accelerate-on-device-compute-review-recipes.md).

The principle is simple: choose the smallest abstraction that gives the product the required control. A tensor operation, a graph execution, a GPU command, and a camera frame each have different ownership and evidence boundaries. “It ran on Apple silicon” is not a sufficient performance, correctness, or battery claim.

## 1. Choose the compute abstraction

| Layer | Best fit | What it owns | What it does not prove |
| --- | --- | --- | --- |
| `MLTensor` | Typed tensor math, reshaping, reductions, matmul, image/tensor transforms, and a Core ML-friendly Swift surface | Shape, scalar type, tensor operations, materialization | Which hardware executed every operation or that the product result is meaningful |
| `MLComputePolicy` | Constraining `MLTensor` work to CPU or CPU/GPU policy | Task-local tensor compute policy | Universal device performance or Neural Engine use when the API does not expose that choice |
| BNNS Graph | CPU-based neural-network graphs and model execution with dynamic-shape/workspace control | Compiled graph context, tensor descriptors, workspace, execution | GPU/Neural Engine performance or camera frame correctness |
| MPSGraph | Symbolic compute graphs that can compile/run across Apple compute devices | Graph, placeholders, executable, feeds, targets, execution descriptor | Automatic product-level memory/thermal success |
| Metal | Custom GPU kernels, explicit command encoding, resource storage, tensor descriptors, and synchronization | Buffers, textures, tensors, command queues/buffers, pipelines, hazards | Numerical equivalence, target support, or safe ownership without tests |
| Accelerate/vImage/vDSP | CPU vector, image, DSP, and linear-algebra work | CPU-oriented optimized operations and format transforms | That a copy or conversion is cheaper than an explicit GPU path |
| Core ML/Core AI | Full model deployment, functions, model specialization, or model-level hardware selection | Artifact/runtime/model contracts | That custom tensor or Metal work is necessary or beneficial |

Use the higher-level model runtime when it already satisfies the contract. Drop down only for a measured need: an unsupported operation, a controlled preprocessing path, a custom kernel, a buffer/texture handoff, or a graph that benefits from explicit compilation.

## 2. `MLTensor` is a typed value boundary

`MLTensor` represents a multidimensional array of numerical or Boolean scalars tailored to ML workloads. The API exposes shape, rank, scalar type, scalar count, creation from scalars/data or no-copy bytes, and operations such as reshape, transpose, resize, reduction, matmul, softmax, split, concatenate, clamp, and element access.

Treat every tensor as a contract:

- rank and dimension order;
- scalar type and precision;
- contiguous/strided expectation;
- batch and dynamic-shape bounds;
- device policy for the operation;
- ownership and lifetime of backing memory;
- when a result must be materialized for CPU or UI use.

`shapedArray(of:)` is an asynchronous materialization boundary. Do not pull a large tensor into a SwiftUI view or CPU array merely to display a status. Materialize only the reduced, sampled, or validated data the product needs.

The no-copy initializer can avoid a copy, but it transfers responsibility for the raw buffer’s lifetime, alignment, size, shape, and scalar type. A no-copy route that outlives its source buffer is a memory bug disguised as an optimization.

## 3. `MLComputePolicy` is scoped policy, not a hardware promise

The current Core ML tensor policy API includes CPU-only and CPU-plus-GPU policies, and a task-local `withMLTensorComputePolicy` function for synchronous or asynchronous work. Use the policy around the smallest operation scope that needs it:

```text
policy scope -> tensor operations -> awaited materialization -> scope ends
```

Do not assume that `.cpuAndGPU` means every operation runs on the GPU, that it uses the Neural Engine, or that it is faster than the default. Record the device, input shape, precision, workload, and actual trace. A policy can change memory pressure, contention with rendering, and thermal behavior.

If the product needs Neural Engine-aware model execution, use the model framework’s documented compute/model route and proof rather than inventing a tensor-policy claim from a device name.

## 4. BNNS Graph is a CPU graph route

BNNS is part of Accelerate and provides optimized neural-network routines for training and inference. BNNS Graph can build or compile graph contexts, expose tensor descriptors and strides, support dynamic shapes, allocate/reuse workspace, and execute functions with tensor or pointer arguments.

Use BNNS Graph when:

- the workload is CPU-oriented or background-friendly;
- the graph is derived from a compiled Core ML model or constructed with the BNNS builder;
- explicit tensor descriptor, dynamic-shape, or workspace control matters;
- a CPU route is a deliberate fallback or measured baseline.

Dynamic-shape routes must set shapes before execution and must not mutate them while an execution is in flight. An output allocation policy should be recorded because allocation and reuse affect memory and latency. BNNS Graph execution is not proof that a Core ML/Vision route uses the same preprocessing, compute device, or semantic mapping.

## 5. MPSGraph is a symbolic graph route

MPSGraph represents operations and tensors symbolically. It can compile a graph for a device, run with feeds and target tensors, or encode work into a Metal command queue. Its tensors can be backed by `MTLBuffer` or `MTLTexture`, and its executable can be serialized/loaded as a package where the product needs that deployment route.

Use MPSGraph when a graph-level representation, explicit target tensors, or cross-device compute path is the right tool. Keep separate:

- graph construction and compilation;
- feed/output tensor descriptors;
- command queue/command buffer ownership;
- execution completion and cancellation;
- output materialization and validation.

An MPSGraph compile result proves an executable exists. It does not prove that the target device, storage mode, queue contention, thermal state, or model inputs fit the product.

## 6. Metal resources and storage modes

`MTLBuffer` stores app-defined data and is created by an `MTLDevice`. `MTLTexture` exposes typed image data and can share storage with a buffer through a compatible texture view or buffer-backed texture. Storage modes determine where the resource is accessible:

- `shared` permits CPU and GPU access and is appropriate for CPU-populated data that the GPU also reads;
- `private` is GPU-only and can reduce unnecessary CPU-visible access for GPU-owned intermediate data;
- `memoryless` is temporary tile memory for GPU passes where the platform supports it;
- `managed` has platform-specific synchronization behavior and is primarily relevant to macOS/Intel/discrete paths.

Apple’s Metal guidance recommends using the system default unless the app has a reason to choose otherwise, and warns that manually selecting a mode can reduce portability. On Apple GPUs, shared/private/memoryless choices are memory and bandwidth decisions, not decoration.

Every resource route needs:

- creating device/queue ownership;
- storage mode and usage;
- alignment/stride/pixel-format;
- CPU/GPU synchronization;
- hazard tracking or explicit synchronization;
- release/reuse timing;
- device family/feature support.

## 7. Metal tensors are a stricter tensor contract

`MTLTensorDescriptor` specifies dimensions, data type, strides where applicable, storage mode, CPU cache mode, hazard tracking, resource options, and usage. `MTLDevice.makeTensor(descriptor:)` validates the descriptor, and the tensor can use data-plane or auxiliary-plane storage depending on the format and target.

For every tensor type record:

- minimum OS and device families;
- rank, dimensions, strides, alignment, and offset;
- storage mode and usage;
- quantization/scale plane semantics;
- source buffer/plane lifetime;
- custom shader or graph binding;
- fallback when the target does not support the type.

Do not infer support from a simulator, a Mac GPU, or a different tensor data type. Metal feature-set tables and runtime feature checks are part of the target contract.

## 8. Pixel buffers and zero-copy are ownership routes

Camera and video pipelines often begin with a `CVPixelBuffer`. `CVMetalTextureCacheCreateTextureFromImage` can create a Metal texture buffer from an existing image buffer. This can reduce copies, but it does not remove format, plane, synchronization, lifetime, or privacy work.

For a pixel-buffer-to-Metal path, record:

- capture output pixel format and plane layout;
- color space and orientation;
- texture pixel format and plane index;
- cache/device ownership;
- frame lifetime until the command buffer completes;
- whether the buffer can be reused or mutated;
- stale frame/cancellation behavior;
- fallback conversion if the texture path is unavailable.

“Zero-copy” means a particular resource path avoided a copy; it does not mean the pipeline has no synchronization, no cache work, or no memory cost.

## 9. Command buffers are asynchronous lifecycle objects

An `MTLCommandBuffer` stores encoded GPU commands, is committed to the queue that created it, and exposes scheduled/completed states and completion callbacks/async methods. The CPU should not read or reuse a resource before the GPU has completed the work that uses it.

Design a command route with:

1. queue owner and admission policy;
2. input resource lifetime;
3. encoder/pipeline creation policy;
4. buffer/texture/tensor bindings;
5. dispatch dimensions and bounds;
6. completion/error mapping;
7. cancellation semantics (usually stop publishing/reuse rather than erase already-encoded GPU work);
8. resource release/recycling after completion.

Waiting synchronously on the main actor is a UI bug. A completion callback or async bridge must return a typed result to the app state machine.

## 10. Model and compute boundaries

A model runtime may own specialization, caching, graph compilation, and device selection. A low-level compute layer may own only a preprocessing/postprocessing kernel or a custom tensor operation. Avoid rebuilding a model runtime in Metal merely to draw a result.

Useful boundaries:

```text
camera/picker -> source contract -> preprocessing adapter
    -> Core ML/Core AI model OR BNNS/MPSGraph/Metal compute
    -> typed output buffer/tensor -> validation adapter -> proposal
```

The output adapter should own shape/type conversion, coordinate systems, confidence/quality interpretation, and source/model provenance. The domain layer should not know about `MTLTexture`, command buffers, or a private tensor stride.

## 11. Performance is a pipeline property

Measure copies, not only arithmetic:

- camera/pixel-buffer capture;
- pixel format conversion and crop/resize;
- CPU/GPU/ANE model execution;
- buffer/texture/tensor creation;
- synchronization and command-buffer gaps;
- output materialization;
- SwiftUI publication and rendering;
- thermal/battery behavior under sustained work.

An MPSGraph or Metal kernel can be faster in isolation and slower in the app because it adds copies, queue contention, synchronization, or materialization. Compare equivalent end-to-end workloads on the same physical device and release configuration.

## 12. Memory and thermal are correctness constraints

Budget:

- input frames and retained source images;
- model weights and graph/executable caches;
- intermediate buffers/tensors;
- output/state buffers;
- command-buffer in-flight resources;
- SwiftUI image/result retention;
- background/foreground coexistence.

Test cold/warm load, concurrent requests, camera plus rendering, memory pressure, app interruption, backgrounding, and sustained workloads. A route that produces the right numbers once but drops frames, heats the device, or leaks in-flight resources is not production-ready.

## 13. SwiftUI and Liquid Glass

The low-level layer should surface a simple readiness model to SwiftUI:

```text
idle -> preparing -> running -> result
             \-> constrained -> fallback
             \-> failed -> retry
```

Show device/compute details only in an advanced disclosure. Standard controls, typography, safe areas, and accessibility remain the shell. Liquid Glass can group capture/stop/retry or compact performance/status controls; it should not obscure frame freshness, memory warnings, error messages, or source provenance.

Provide a reduced-effects and low-power path. The visual treatment must never determine whether a GPU job is admitted or a result is committed.

## 14. Privacy and data retention

Low-level compute often handles raw camera frames, pixel buffers, embeddings, and intermediate tensors. Define:

- whether raw sources are retained;
- whether intermediate tensors can contain reconstructable content;
- whether signposts/logs include identifiers or values;
- whether buffers are shared with extensions or other processes;
- how cancellation/deletion releases memory;
- whether model/debug artifacts are included in diagnostics.

Use hashes, dimensions, timing, and redacted summaries in evidence where raw values are not needed. Local processing does not automatically mean no data leaves the device; logging, sync, analytics, downloads, and model updates are separate paths.

## 15. Release proof

For a low-level compute route, require:

1. source/data/model contract;
2. target OS/device/feature matrix;
3. tensor/buffer/texture descriptors and ownership rules;
4. CPU/GPU/ML compute policy;
5. numerical reference fixtures;
6. source pixel-buffer/orientation/format evidence;
7. command-buffer completion/error/cancellation evidence;
8. memory/thermal/latency/energy measurements;
9. accessibility tasks and fallback;
10. signed archive/TestFlight route on physical hardware.

## Stop conditions

Stop before release when:

- a tensor’s shape, scalar type, stride, plane, or backing-memory lifetime is implicit;
- a no-copy buffer can outlive or be mutated before its consumer completes;
- a Metal storage mode is chosen without a target/data-flow rationale;
- a compute policy is presented as guaranteed hardware selection;
- an MPSGraph/BNNS/Metal benchmark excludes copies or synchronization that the app performs;
- a camera frame can be reused or displayed after the command buffer still owns it;
- a GPU completion is waited on synchronously from the main actor;
- a custom kernel lacks numerical fixtures and an unsupported-target fallback;
- memory/thermal behavior is unknown under the actual concurrent workload;
- raw/intermediate data is logged without a privacy/retention decision;
- the visual UI hides a constrained/fallback state or accessibility path.

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

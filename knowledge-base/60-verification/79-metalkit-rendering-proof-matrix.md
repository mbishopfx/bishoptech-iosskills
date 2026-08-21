# MetalKit rendering proof matrix

MetalKit claims cross a SwiftUI/UIKit bridge, a Metal device and command
queue, source assets, GPU resources, display cadence, accessibility, and
physical-device performance. This matrix keeps “the view exists” separate from
“the visual is correct, responsive, accessible, and shippable.”

## Evidence ladder

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| L0 | Official source/target review | API route, target availability, and documented responsibilities | Target configuration or runtime behavior |
| L1 | Pure fixtures | Asset metadata, descriptor mapping, state machine, typed AI validation | GPU rendering, display cadence, or device performance |
| L2 | Preview/simulator | SwiftUI shell, loading/error states, controls, fallback layout | Physical GPU feature support, thermal behavior, haptics, or frame budget |
| L3 | Named-target compile/run | Bridge, shader/resource membership, view lifecycle, basic rendering | All device families, long-session performance, release packaging |
| L4 | Signed physical-device run | Device feature support, drawable behavior, input, accessibility, frame/memory/thermal observations | Every OS/device or production-wide performance |
| L5 | Release artifact/TestFlight | Signing, target resources, archive configuration, user-like install | App Review approval or universal production behavior |

## Claim matrix

| Claim | Minimum evidence | Common false substitute |
| --- | --- | --- |
| `MTKView` route is available | Selected SDK/deployment review and named target compile | Framework import in an unrelated target |
| Device can use the renderer | Runtime feature/capability checks on declared device classes | Newest-device run or simulator |
| View lifecycle is correct | Create/update/dismantle test with pause/background/foreground | One screenshot |
| Texture loads safely | Supported, malformed, oversized, missing, revoked-scope, and cancellation fixtures | Non-nil `MTLTexture` |
| Mesh renders correctly | Descriptor/buffer/submesh fixture plus physical render with known asset | `MDLAsset` or `MTKMesh` construction |
| Shader consumes the intended data | Attribute/stride/format validation and visual test patterns | Pipeline creation alone |
| Drawable presents frames | Real named target with command completion/present evidence | Command buffer encoded |
| Frame budget is met | Release physical run with workload, device, refresh, GPU/CPU timing, hitches | Preview/simulator/static screenshot |
| Memory is bounded | Large-asset/load/unload run with peak memory and teardown observation | One small bundled asset |
| AI proposal is safe | Typed schema, bounds/device validation, stale revision, review/edit/reject/undo | Generated JSON or model confidence |
| Surface is accessible | Task test with VoiceOver, Dynamic Type, contrast, reduced motion/transparency, keyboard/pointer/controller | Accessibility label on the `MTKView` |
| Release contains the renderer | Archive inspection for shader/library/model/texture target membership and signed install | Source file visible in Xcode |

## Fixture pack

Create deterministic fixtures before the device run:

| Fixture | Expected observation |
| --- | --- |
| Empty/no-source state | Native empty state and manual route; no renderer claim |
| Small known texture | Expected dimensions, color/alpha policy, and render pattern |
| Malformed/unsupported texture | Loader error, redacted diagnostic, retry/manual fallback |
| Oversized texture | Bound rejection or downsample policy; no uncontrolled memory growth |
| Revoked security-scoped URL | Access failure and scope cleanup |
| One mesh/no texture | Vertex/index/descriptors render with a known material fallback |
| Multiple submeshes/materials | Stable submesh mapping, missing-material state, deterministic ordering |
| Missing texture/resource | Explicit material fallback; no unrelated texture reuse |
| Wrong descriptor/format | Validator rejects or reports mismatch before draw |
| Animated/timed asset | Chosen time/sample policy and pause/resume behavior |
| Source revision replacement | Old resources are not mixed with the new render revision |
| AI proposal in bounds | Review and accept path with before/after and undo |
| AI proposal out of bounds | Deterministic rejection and manual edit path |
| Stale AI proposal | Revision mismatch prevents silent commit |
| Unsupported device/profile | Lower-quality or semantic fallback |
| Off-screen/background/thermal | Cadence or quality reduces and UI explains the state |

## `MTKView` and SwiftUI bridge evidence

Record:

- `MTLDevice` selection and feature checks;
- `MTKView` formats, drawable size/scale, sample count, pause and cadence;
- `MTKViewDelegate` creation, draw, resize, and teardown behavior;
- `UIViewRepresentable` create/update/dismantle calls;
- renderer ownership and source/render revision mapping;
- no duplicate resource creation from repeated SwiftUI updates;
- background/foreground, scene inactive, orientation, size changes, and memory
  warning behavior;
- unavailable drawable/command failure and recovery;
- semantic overlay/inspector and manual fallback.

An `MTKView` that appears in a preview proves only a view composition. It does
not prove that a real drawable, shader, device, or resource completed.

## Texture and asset evidence

For each texture or Model I/O source, retain a non-sensitive record of:

~~~text
source identifier/revision:
file type and scope:
integrity/size/pixel dimensions:
color/alpha/orientation policy:
MDLAsset/MDLMesh/MTKMesh result:
vertex descriptor and shader mapping:
submesh/material/texture resolution:
load duration and peak memory:
cancellation/failure/retry state:
retention/deletion policy:
~~~

Test user-selected, bundled, downloaded, missing, and replaced sources. If the
feature shares the file or model, test the exported artifact separately; a
rendered texture does not prove a valid share/export file.

## GPU and performance evidence

For every declared performance result, record:

- exact device model, OS, build configuration, SDK, display/refresh setting;
- workload: drawable size, mesh/submesh count, texture sizes, material/shader
  count, effect/profile, and in-flight frame count;
- CPU frame time, GPU frame time, hitches/drop count, memory peak, load time;
- thermal state, battery/low-power state, background/foreground transitions;
- cold start, warm start, resource replacement, and long-session behavior;
- GPU capture/Instruments/XCTest metric/signpost artifact, if used;
- degraded-quality trigger and restoration behavior.

Do not report “60 FPS,” “smooth,” or “low memory” without the workload and
measurement context. A metric is an observation, not a guarantee for every
device.

## Accessibility and native-design evidence

Run the core task with:

- VoiceOver and a semantic inspector/list;
- Dynamic Type at supported large sizes;
- increased contrast and reduced transparency;
- Reduce Motion and low-power/thermal fallback;
- Voice Control, Switch Control, Full Keyboard Access, pointer, and controller
  where the feature supports them;
- light/dark appearance, localization, right-to-left layout, and rotation;
- touch targets, focus order, selection narration, error recovery, and undo.

Verify that the Metal surface is not the only place an essential value or
action exists. Test the same task in the manual/fallback route.

## AI evidence

For an AI-assisted render or asset flow, capture:

- exact source IDs/revisions and redaction policy;
- on-device model route/availability/version and prompt/context revision;
- typed proposal schema, bounds, supported profiles, and validation result;
- before/after preview, edit/reject/accept, stale revision, and undo;
- renderer configuration revision and measured result;
- no arbitrary shader execution, protected-data mutation, or unreviewed
  destructive replacement;
- deterministic manual fallback when the model is unavailable or uncertain.

## Archive and release evidence

Inspect the signed artifact for:

- shader library/`.metal` source or compiled resource membership as appropriate;
- model/texture asset membership and expected bundle paths;
- target/deployment settings, supported destinations, and entitlements;
- privacy manifests and source/file retention configuration;
- release optimization and resource stripping behavior;
- install, relaunch, background/foreground, and device profile selection;
- TestFlight or release install only when the product claims that level.

## Verification record template

~~~text
feature and user task:
target/bundle/build/sdk/deployment target:
device/OS/GPU/display configuration:
renderer route and why simpler route was insufficient:
MTKView formats/cadence/drawable policy:
shader/library/resource membership:
asset/texture fixture and source revision:
descriptor/mesh/submesh/material result:
SwiftUI bridge lifecycle:
performance workload and metrics:
accessibility/alternate-input settings and task result:
AI model/proposal/review/undo:
fallback/degraded/offline/thermal states:
archive/resource/privacy inspection:
known limits:
claim level: documented / fixture / compile / simulator / device / release
~~~

## Sources

- [MetalKit](https://developer.apple.com/documentation/metalkit/)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview/)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate/)
- [MTKTextureLoader](https://developer.apple.com/documentation/metalkit/mtktextureloader/)
- [MTKMesh](https://developer.apple.com/documentation/metalkit/mtkmesh/)
- [MTKMeshBuffer](https://developer.apple.com/documentation/metalkit/mtkmeshbuffer/)
- [MTKMeshBufferAllocator](https://developer.apple.com/documentation/metalkit/mtkmeshbufferallocator/)
- [MTKSubmesh](https://developer.apple.com/documentation/metalkit/mtksubmesh/)
- [Model I/O](https://developer.apple.com/documentation/modelio/)
- [MDLAsset](https://developer.apple.com/documentation/modelio/mdlasset/)
- [MDLMesh](https://developer.apple.com/documentation/modelio/mdlmesh/)
- [Metal](https://developer.apple.com/documentation/metal/)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice/)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue/)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing performance](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)

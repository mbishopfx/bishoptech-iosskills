# SwiftUI ARKit and RealityKit spatial-scene review design

This design companion turns a camera-backed AR scene into a calm, native-feeling SwiftUI task. The scene remains the content layer. SwiftUI owns navigation, status, review, recovery, and explicit actions. RealityKit renders virtual content. ARKit supplies time-varying observations with uncertainty.

Pair this page with [SwiftUI ARKit and RealityKit spatial-scene review](../42-framework-deep-dives/97-swiftui-arkit-realitykit-spatial-scene-review.md), [spatial scene and occlusion native surfaces](37-spatial-scene-and-occlusion-native-surfaces.md), [the ARKit/RealityKit route](../50-capability-recipes/128-swiftui-arkit-realitykit-spatial-scene-review-route.md), and [the spatial proof matrix](../60-verification/122-swiftui-arkit-realitykit-spatial-scene-review-proof-matrix.md).

## Design contract

A person should be able to answer these questions without knowing the framework names:

1. What is this screen helping me do?
2. Why does it need camera access?
3. Is the app currently tracking, still learning, interrupted, or unable to track?
4. What is observed, what is estimated, and what did I select?
5. Which item or placement is a candidate, and what will confirmation commit?
6. If the scene is stale or uncertain, how do I retry, reset, or use a non-AR path?
7. Can I complete the task without aiming the camera, seeing depth, or using motion-heavy gestures?

The design hierarchy is:

~~~text
task context
  -> privacy and tracking status
  -> camera/scene content
  -> candidate focus or selected entity
  -> functional controls
  -> review sheet
  -> explicit commit
  -> post-commit confirmation and undo
~~~

Do not begin with a glowing object or a full-screen glass overlay. Begin with the task and the current state.

## Native screen anatomy

A robust iPhone or iPad camera AR screen can use:

| Region | Responsibility | Design rule |
| --- | --- | --- |
| Navigation shell | Exit, task title, privacy/status access | Keep it stable while the camera scene changes. |
| Tracking banner | State and next step | Say “Move slowly” or “Return to the previous view,” not “AR error.” |
| Camera content | Live scene and virtual preview | Never hide the content needed to complete the task. |
| Focus indicator | Current raycast candidate | Mark as preview/candidate, never as committed truth. |
| Tool group | Scan, retarget, undo, reset, objects | Use semantic controls with clear enabled states. |
| Selection card | Chosen object or placement | Show source time, state, and available actions. |
| Review sheet | Candidate details and AI proposal | Make source, limitations, and side effect explicit. |
| Alternative route | List, 2D plan, manual entry, or cancel | Keep the task available without camera movement. |

Use a bottom accessory, toolbar, or compact functional group for controls instead of scattering floating glass buttons over important geometry. If the screen needs a larger editor, present a sheet or split view so the person can inspect details without losing context.

## State language and visual treatment

Use copy that names the action and limitation:

| State | Primary copy | Secondary treatment |
| --- | --- | --- |
| Ready to start | “Use the camera to place a model.” | Explain camera access and what is saved. |
| Permission needed | “Camera access is needed to view the room.” | Explain before the system prompt; offer cancel. |
| Unsupported | “AR placement isn’t available on this device.” | Offer a 2D preview or manual route. |
| Initializing | “Move slowly to scan the area.” | Show a quiet progress cue, not a false percentage. |
| Limited features | “Aim at a textured surface.” | Keep current draft provisional. |
| Excessive motion | “Slow down to improve tracking.” | Reduce animated distractions. |
| Normal tracking | “Tracking is ready.” | Enable the declared candidate action. |
| No surface | “No matching surface yet.” | Retarget or change alignment. |
| Candidate | “Preview placement.” | Show alignment and a confirm action. |
| Placed | “Placement saved for this session.” | Offer move, undo, and details. |
| Interrupted | “Tracking paused.” | Preserve draft; explain how to resume. |
| Relocalizing | “Return near the earlier view.” | Offer reset after a bounded wait. |
| Stale | “Last update was moments ago.” | Show age and refresh; do not imply live. |
| AI proposal | “Suggested next step.” | Show source snapshot and edit/reject controls. |
| Committed | “Saved.” or the concrete domain result | Offer undo or next task. |

Color, blur, arrow motion, depth, and shine may reinforce this language, but none should be the sole carrier of state. For example, a red banner is insufficient for someone using VoiceOver, and a centered arrow is insufficient when direction is unavailable.

## Functional Liquid Glass composition

Liquid Glass is most useful for the functional layer around the scene:

- navigation and dismissal;
- compact status and recovery;
- object selection and tool groups;
- review/confirm actions;
- system handoff or settings recovery.

Keep a clear separation:

~~~text
camera feed + estimated geometry + virtual content
  = content layer

navigation + state + tools + review + confirmation
  = functional layer
~~~

Use a small number of coordinated glass groups. Let the camera feed, model, and focus indicator provide the visual richness. A functional group should have enough contrast and material separation that text remains readable over a bright window, a dark room, a mesh, or a moving person.

Good spatial glass patterns:

- one top status group with a compact tracking label and privacy affordance;
- one bottom tool group with scan, retarget, and reset;
- one selected-item card that expands into a review sheet;
- one confirmation control group that remains visually stable while the scene moves.

Poor patterns:

- glass on every entity;
- a translucent full-screen veil over the camera;
- multiple independent pills that morph unpredictably;
- icon-only controls for irreversible placement;
- animated blur that competes with tracking guidance;
- a glow that makes an estimated mesh look authoritative.

If a glass effect is unreadable or unavailable, fall back to a standard material or opaque surface with the same semantic hierarchy. Accessibility settings and platform differences are design inputs, not afterthoughts.

## Focus and placement design

The focus indicator should behave like a measurement preview, not a cursor that promises a surface:

1. It appears only after the renderer has a current query result.
2. It shows the requested alignment and approximate footprint.
3. It is marked unavailable when the result is missing or stale.
4. It uses restrained motion so it does not suggest certainty.
5. It changes copy when tracking becomes limited.
6. It requires a separate user action to place the object.
7. It can be reset without deleting already saved domain data.

When a tracked raycast updates the focus position, avoid making the object jump with every small change. Apply a presentation-only smoothing policy with an explicit stale boundary. Do not smooth the stored transform if doing so would hide a large correction; show “placement updated” and let the person review.

A candidate card should show:

- selected asset or object name;
- candidate or placed state;
- horizontal/vertical alignment if relevant;
- source time or “updated just now”;
- current tracking state;
- estimated versus existing target;
- move, remove, reset, confirm, and undo actions.

Do not say “on the floor” when the source is only an estimated horizontal plane. Say “candidate on a horizontal surface” until the user accepts it.

## Entity labels and spatial callouts

Callouts attached to entities should be short and secondary. Keep the authoritative label in a stable SwiftUI panel or list. A spatial label can disappear behind a wall, clip at the edge of the screen, or become unreadable during motion.

For each important entity, provide:

- an app-owned stable label;
- a state such as candidate, placed, stale, or unavailable;
- a visible relation to the user’s task;
- a VoiceOver label/value and custom action set;
- a two-dimensional list entry;
- a way to select the entity without targeting it in the camera.

When an entity moves because an anchor refines, update the callout and its source time together. Never leave an old callout floating where the entity used to be.

## Review sheets and explicit action

A review sheet converts an observation into a user decision. It should state:

| Review field | Example |
| --- | --- |
| Source | “ARKit surface candidate, updated just now.” |
| Current state | “Tracking normal” or “Tracking limited: insufficient features.” |
| Candidate | “Horizontal placement preview.” |
| Confidence language | Use only a supported model/observation label; do not invent certainty. |
| AI proposal | “Suggested: place the lamp near the selected surface.” |
| Limitation | “This is a camera-based estimate; inspect the physical area.” |
| Side effect | Name the actual app-owned change. |
| Actions | Edit, reject, confirm, save, or cancel. |

For a purely visual decoration, one confirm button may be enough. For a physical instruction, safety-sensitive task, external command, or persistent room record, use a stronger confirmation and a deterministic validation path.

Do not put the commit action behind an ambiguous “Done” label. Use “Place model,” “Save room note,” “Apply layout,” or the actual outcome.

## Non-AR and alternate-input paths

A camera AR screen is not accessible merely because a VoiceOver label exists. Provide a route that can complete the user job without continuous spatial aiming:

- object list with selection and reorder;
- manual dimensions or placement fields;
- 2D plan or photo-based review;
- guided target selection with large semantic buttons;
- keyboard or pointer placement where appropriate;
- voice commands for named actions;
- switch-accessible focus order;
- reset and undo without gesture dependence.

Dynamic Type may make a compact glass pill too small for its content. Let status and review copy wrap. Use a sheet or full-width panel for long explanations. Avoid placing essential text at a fixed world scale where it becomes unreadable with distance or camera motion.

For Reduce Motion, remove ornamental entity bobbing, rapid focus transitions, and continuous arrow animations. Preserve feedback with a text/state transition and a short, optional haptic if the product supports it.

## Camera guidance without pressure

Coaching should be direct and neutral:

- “Move slowly.”
- “Aim at a textured surface.”
- “Keep the object in view.”
- “Return near the earlier view to resume.”
- “No suitable surface detected.”
- “Camera access is off.”

Do not imply that a person is failing when the room is dark, featureless, reflective, or outside a device capability. Avoid a false completion ring when tracking quality is not a linear progress measure. If the scan is not required, do not force a long camera onboarding sequence.

## AI design boundary

The AI surface should look like a reviewable suggestion, not an extension of ARKit authority:

~~~text
named AR observation
  -> source and timestamp
  -> local model proposal
  -> editable explanation
  -> user review
  -> deterministic commit
~~~

Show the source snapshot and stale state. If the person moves the device, changes the selected entity, resets the session, or changes the task, mark the proposal outdated. Keep rejection and manual editing as first-class actions.

Example copy:

- “Suggested from the current scene snapshot.”
- “This suggestion may be incomplete.”
- “Review the placement before saving.”
- “The camera found a candidate surface; it did not verify safety.”
- “AI unavailable. You can place the model manually.”

Never use an AI explanation to hide missing ARKit data. An eloquent description of a room does not prove object identity, dimensions, ownership, or safety.

## Accessibility data for RealityKit entities

Use RealityKit accessibility properties for entities that a person needs to discover or act on. Configure a concise label, a useful value, supported actions, and custom content where the entity has meaningful state. Keep the accessible data in sync as the entity changes.

A good accessible label is:

- “Candidate table surface, horizontal, updated just now.”
- “Placed lamp, move or remove.”
- “Tracking limited, aim at a textured surface.”

A bad label is:

- “AnchorEntity 4F2A.”
- “High-confidence safe floor.”
- “AI detected table” when the result is not verified.

The stable SwiftUI selection list remains the fallback authority for navigation and action order.

## Privacy and environmental sensitivity

A camera AR screen can expose a room, private objects, faces, body positions, and routines. The design should:

- explain camera use before requesting permission;
- show when capture is active;
- avoid showing raw frame thumbnails in logs or diagnostics;
- avoid uploading mesh/world-map data by default;
- offer clear deletion for saved spatial records;
- separate ephemeral scan state from persisted product data;
- avoid retaining AI prompts that contain unnecessary room detail;
- communicate if a feature requires a network service or account;
- make background/foreground behavior visible.

A “local AI” label does not by itself explain retention or app logging. Document the actual data path in the product privacy plan.

## Performance and comfort

Keep the screen quiet when the renderer is busy:

- do not layer multiple full-screen blur effects over camera content;
- cap animation and entity churn;
- use lower-detail previews while assets load;
- avoid running a model over every frame without measurement;
- stop tracked raycasts and subscriptions when no longer needed;
- use concise status updates rather than frequent layout changes;
- test bright/dark scenes, moving people, reflective surfaces, and long sessions;
- test thermal and battery on the target device family.

A smooth preview on a developer device is not proof of a sustained release experience. Record the target, asset count, scene reconstruction mode, camera conditions, and duration with any performance result.

## Design review checklist

Before calling a spatial surface native and ready for implementation, ask:

- Is the user task visible before the camera starts?
- Is the camera permission explanation concrete?
- Can the person tell normal, limited, interrupted, relocalizing, stale, and unsupported states apart?
- Does the focus indicator say candidate rather than truth?
- Does the review sheet name the actual commit?
- Can the user undo, reset, or use a non-AR route?
- Is Liquid Glass limited to functional controls?
- Does the screen remain readable with increased contrast, reduced transparency, Dynamic Type, Reduce Motion, and VoiceOver?
- Are entity labels and actions synchronized with current app state?
- Does AI show its source snapshot and limitations?
- Is room/mesh/frame retention minimized and deletable?
- Is physical-device proof planned for the selected target?
- Are archive, privacy strings, and release evidence separate from preview proof?

## Sources

- [ARKit](https://developer.apple.com/documentation/arkit)
- [ARSession](https://developer.apple.com/documentation/arkit/arsession)
- [ARCamera](https://developer.apple.com/documentation/arkit/arcamera)
- [Managing Session Life Cycle and Tracking Quality](https://developer.apple.com/documentation/arkit/managing-session-life-cycle-and-tracking-quality)
- [Verifying Device Support and User Permission](https://developer.apple.com/documentation/arkit/verifying-device-support-and-user-permission)
- [ARRaycastQuery](https://developer.apple.com/documentation/arkit/arraycastquery)
- [ARRaycastResult](https://developer.apple.com/documentation/arkit/arraycastresult)
- [Placing objects and handling 3D interaction](https://developer.apple.com/documentation/arkit/placing-objects-and-handling-3d-interaction)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [ARView](https://developer.apple.com/documentation/realitykit/arview)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [AnchorEntity](https://developer.apple.com/documentation/realitykit/anchorentity)
- [Component](https://developer.apple.com/documentation/realitykit/component)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Improving the Accessibility of RealityKit Apps](https://developer.apple.com/documentation/realitykit/improving-the-accessibility-of-realitykit-apps)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [MetricKit](https://developer.apple.com/documentation/metrickit)

## Related knowledge-base routes

- [SwiftUI ARKit and RealityKit spatial-scene review](../42-framework-deep-dives/97-swiftui-arkit-realitykit-spatial-scene-review.md)
- [Spatial scene and occlusion native surfaces](37-spatial-scene-and-occlusion-native-surfaces.md)
- [RealityKit/ARKit spatial route](../50-capability-recipes/40-realitykit-arkit-spatial-route.md)
- [SwiftUI ARKit/RealityKit capability route](../50-capability-recipes/128-swiftui-arkit-realitykit-spatial-scene-review-route.md)
- [SwiftUI ARKit/RealityKit spatial proof matrix](../60-verification/122-swiftui-arkit-realitykit-spatial-scene-review-proof-matrix.md)

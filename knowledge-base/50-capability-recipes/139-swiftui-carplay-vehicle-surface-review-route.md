# SwiftUI CarPlay and vehicle-surface review route

This route card turns the [CarPlay and vehicle-surface review](../42-framework-deep-dives/108-swiftui-carplay-vehicle-surface-review.md) into a build decision. It is for an iPhone app that may expose audio, communication, navigation, parking, EV charging, quick ordering, or a small system action in a vehicle. Read the [design guide](../21-design-deep-dives/136-swiftui-carplay-vehicle-surface-review-design.md), [proof matrix](../60-verification/133-swiftui-carplay-vehicle-surface-review-proof-matrix.md), and [recipes](../70-code-recipes/151-swiftui-carplay-vehicle-surface-review-recipes.md) before implementation.

A CarPlay route is complete only when the product category, managed entitlement, scene graph, template choice, vehicle limits, user action, domain commit, safety/privacy behavior, physical vehicle evidence, and signed release evidence agree.

## Route selector

| If the product needs to... | Start here | Gate before UI code |
| --- | --- | --- |
| Browse and play audio | Audio entitlement, CPListTemplate, MediaPlayer, CPNowPlayingTemplate.shared | Audio category approval, playback policy, Siri route |
| Show a map and active guidance | Maps entitlement, navigation scene, CPMapTemplate, CPWindow | Navigation eligibility, location authorization, signed map entitlement |
| Call or message | Communication entitlement, CPMessageListItem, SiriKit, CallKit where needed | Communication eligibility, recipient privacy, intent handling |
| Find charging or parking | Matching entitlement and POI/information templates | Category approval, current place/service data |
| Place a quick order | Quick-ordering entitlement and short information flow | Category approval, current availability, confirmation/payment route |
| Continue a task begun on iPhone | Handoff or a durable pending record | Stable identifier, current revision, safe resume state |
| Expose a voice action | SiriKit or App Intent | Typed parameters, resolution/confirmation, side-effect policy |
| Show passive progress | ActivityKit Live Activity | CarPlay passive presentation; no interactive-control assumption |
| Suggest an option with local AI | Deterministic candidate source plus Foundation Models | Availability, allowlist, revalidation, confirmation, fallback |
| Make a custom glass dashboard | Stop and redesign | CarPlay system templates own the vehicle shell |

## Decision worksheet

Fill this out before creating a target or entitlement request.

### Product

- User outcome:
- CarPlay category:
- Why this category is eligible:
- Primary action:
- Safe fallback when the vehicle is moving or input is limited:
- Data source of truth:
- Account and authorization owner:
- Sensitive data visible on the vehicle screen:

### Target and capability

- iPhone bundle identifier:
- Deployment target and SDK:
- CarPlay scene role:
- Scene class:
- Scene configuration name:
- Scene delegate:
- Navigation app: yes or no
- Dashboard scene: yes or no
- Instrument-cluster scene: yes or no
- Requested managed entitlement:
- Approved managed entitlement:
- Entitlements.plist key:
- Provisioning profile:
- Signed archive evidence:
- Siri capability or App Intents route:
- Optional WidgetKit or ActivityKit target:
- Optional Watch Connectivity route:

### Template

- Root template:
- Pushed templates:
- Presented modal template:
- Maximum sections and items:
- Hierarchical depth:
- Search fallback when keyboard is limited:
- Content-style adaptation:
- Accessibility labels and alternate input:
- Locked-iPhone behavior:
- Disconnect behavior:

### Action and AI

- User command:
- Intent or handler:
- Stable entity identifier:
- Expected source revision:
- Validation checks:
- Confirmation rule:
- Idempotency key:
- Committed result:
- Model availability check:
- Model output schema:
- Deterministic fallback:
- Audit record:

### Proof

- Source review:
- Source and target inspection:
- Compile and unit tests:
- Simulator configuration:
- Locked-phone test:
- Siri test:
- Audio/interruption test:
- Named head unit or physical vehicle:
- Accessibility test:
- Privacy/redaction test:
- Archive and signed-entitlement inspection:
- TestFlight install:
- App Store or production evidence:

## Phase 1: category and entitlement gate

Stop if the app does not have a defensible CarPlay category. Record the category and the exact managed entitlement from Apple’s table.

1. Request the appropriate entitlement through Apple’s CarPlay process.
2. Confirm approval in the developer account.
3. Update the App ID and provisioning profile.
4. Add the entitlement to the intended target.
5. Inspect the signed archive rather than trusting the source plist.
6. Install the signed build and confirm that the system recognizes the route.

Do not write a generic CarPlay template catalog before this phase. A class being visible in the SDK does not prove that the current app may use it.

## Phase 2: scene and target topology

Choose the scene topology:

| Topology | Required evidence |
| --- | --- |
| Non-navigation template app | CarPlay scene manifest, delegate class, interface-controller connection, root template |
| Navigation app | Scene manifest, maps entitlement, interface-controller plus CPWindow connection, map root view controller, CPMapTemplate root |
| Navigation with dashboard | Additional dashboard role/configuration, dashboard delegate, dashboard controller/window behavior |
| App with system surfaces | Separate WidgetKit/ActivityKit/Siri/App Intent target configuration and release evidence |
| App with a watch companion | Separate Watch Connectivity and pairing proof; no assumption that watch reachability equals CarPlay connectivity |

The scene delegate is system-created. The app stores scene-scoped references in a coordinator or actor-owned state model and clears them on disconnect. A SwiftUI view should observe the state; it should not own the CarPlay scene lifecycle.

## Phase 3: choose the template route

### General template route

Use this route for audio browse, communication lists, or category surfaces:

1. Create a bounded data projection.
2. Build CPListTemplate, CPGridTemplate, or CPTabBarTemplate.
3. Attach only safe identifiers to userInfo.
4. Provide handlers that call a bounded domain command.
5. Call the completion closure after the command reaches a known result.
6. Push or replace the next template.
7. Show stale, empty, unavailable, pending, and error states explicitly.

### Navigation route

Use this route only for a navigation-entitled target:

1. Connect the scene with interface controller and CPWindow.
2. Assign a map-drawing root view controller to the window.
3. Set CPMapTemplate as the root template.
4. Render only map content in the window.
5. Use templates for search, route selection, alerts, panning, maneuvers, and voice state.
6. Update the map and templates from a current route projection.
7. Clear scene-specific resources on disconnect.

### Audio route

1. Connect and set a list root.
2. Load a short, current projection of playable content.
3. Let the user select playback.
4. Configure MediaPlayer now-playing state.
5. Push CPNowPlayingTemplate.shared.
6. Handle interruption, buffering, resumption, and audio-session deactivation.
7. Test the Siri assistant cell only after intent handling is configured.

### Communication route

1. Connect and set a communication list root.
2. Use CPMessageListItem or the supported contact template.
3. Keep conversation and contact text privacy-safe.
4. Configure the supported Siri intent route.
5. Let selection invoke Siri’s compose, read, reply, or call flow.
6. Re-resolve recipient and conversation revision before committing.
7. Report errors in CarPlay and preserve a safe pending state.

### Place, charging, parking, or order route

1. Confirm the category entitlement.
2. Use the specific point-of-interest or information templates.
3. Keep the hierarchy short.
4. Recheck current availability and price.
5. Require explicit confirmation for an order or other consequential side effect.
6. Defer complex account or payment work safely.

## Phase 4: vehicle limits and state

Read CPSessionConfiguration and adapt to content style and limited user interfaces. The limit is a runtime vehicle property, not a design-time constant.

| Observation | Route decision |
| --- | --- |
| Keyboard limited | Use favorites, recents, voice, and short queries |
| List length limited | Prioritize current, nearby, or user-pinned items |
| Content style changes | Refresh assets and colors with system appearance |
| Vehicle disconnects | Persist domain state and clear scene references |
| Phone locked | Keep the primary CarPlay function usable |
| Network unavailable | Show a bounded stale/offline state and recovery |
| Account unavailable | Do not show private content or fake a successful action |
| Handler still pending | Disable duplicates and show pending or retry |
| Model unavailable | Use deterministic candidate route |
| Action is too complex for driving | Defer to iPhone after stopping |

## Phase 5: voice and action route

Use SiriKit where Apple documents a category-specific flow. Use App Intents for typed, discoverable actions and entities. Keep a single command service behind both routes so voice, template selection, and iPhone UI do not implement different business logic.

The command path is:

intent or template handler -> entity resolution -> permission check -> freshness/revision check -> confirmation -> idempotent domain command -> committed result -> CarPlay projection

If a command changes an order, message, call, route, playback queue, or account state, require a result from the domain layer. A Siri response such as “done” is not enough.

## Phase 6: local-AI route

Use AI only as an optional proposal layer:

1. Check Foundation Models availability.
2. Build a minimal context from user-authorized records.
3. Ask for structured candidates or a draft.
4. Validate every identifier and constraint deterministically.
5. Present the candidate through a system template or defer to iPhone.
6. Require confirmation for the side effect.
7. Commit through the normal command service.
8. Store model and source revisions in the audit record.
9. Use a deterministic fallback when unavailable or invalid.

Do not ask an on-device model to make a safety-critical driving decision, infer current road truth from stale context, expose private message data, or silently place an order.

## Phase 7: cross-surface route

Choose only the system surfaces that help the same user task.

| Surface | Ownership | Safe composition |
| --- | --- | --- |
| Handoff | iPhone and system activity | Carry a typed pending task and re-resolve in CarPlay |
| Watch Connectivity | Paired iPhone/watch transport | Transfer a revisioned suggestion or committed result |
| Now Playing | MediaPlayer plus shared CarPlay template | Keep playback state authoritative and synchronized |
| Live Activity | ActivityKit system presentation | Passive progress; actions remain in templates |
| App Intent | System discoverability and command entry | Stable typed entity and revalidation |
| SwiftUI Liquid Glass | App-owned iPhone UI | Review, settings, or deferred detail only |

## Phase 8: evidence and release

Use the [proof matrix](../60-verification/133-swiftui-carplay-vehicle-surface-review-proof-matrix.md) to separate:

- source evidence;
- target and entitlement evidence;
- compile evidence;
- simulator evidence;
- locked-phone and Siri evidence;
- physical head-unit/vehicle evidence;
- accessibility and privacy evidence;
- archive and TestFlight evidence;
- App Store and production evidence.

A CarPlay Simulator run is necessary for fast iteration but is explicitly not enough for locked-phone, Siri, or real audio behavior. Name the actual head unit or vehicle used for physical proof.

## Stop conditions

Stop implementation and return to product decisions if:

- the requested category is not eligible or the managed entitlement is absent;
- the scene manifest and target membership are unknown;
- a navigation design draws non-map UI in the CPWindow;
- the route requires an arbitrary SwiftUI layout in the vehicle;
- a template assumes unlimited list depth, keyboard, or grid count;
- the app tells the driver to use the iPhone to resolve an error;
- Siri or App Intent success is treated as domain commit;
- an AI candidate is shown as current truth without validation;
- privacy or locked-phone behavior is untested;
- accessibility is reduced to a static screenshot;
- the simulator is the only vehicle evidence;
- the archive’s signed entitlements and target graph are not inspected.

## Compact route record

Use this as the minimum decision record:

- Category:
- Managed entitlement:
- Root template:
- Scene delegate:
- Navigation CPWindow required:
- Vehicle limits:
- Locked-phone fallback:
- Voice route:
- AI proposal boundary:
- Domain commit:
- Disconnect recovery:
- Privacy redaction:
- Accessibility/input:
- Head unit or vehicle:
- Archive/TestFlight evidence:
- Open risks:

## Sources

- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Requesting CarPlay entitlements](https://developer.apple.com/documentation/carplay/requesting-carplay-entitlements)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [Using the CarPlay Simulator](https://developer.apple.com/documentation/carplay/using-the-carplay-simulator)
- [CPTemplateApplicationScene](https://developer.apple.com/documentation/carplay/cptemplateapplicationscene)
- [CPTemplateApplicationSceneDelegate](https://developer.apple.com/documentation/carplay/cptemplateapplicationscenedelegate)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [CPListTemplate](https://developer.apple.com/documentation/carplay/cplisttemplate)
- [CPGridTemplate](https://developer.apple.com/documentation/carplay/cpgridtemplate)
- [CPSearchTemplate](https://developer.apple.com/documentation/carplay/cpsearchtemplate)
- [CPMapTemplate](https://developer.apple.com/documentation/carplay/cpmaptemplate)
- [CPNowPlayingTemplate](https://developer.apple.com/documentation/carplay/cpnowplayingtemplate)
- [CPMessageListItem](https://developer.apple.com/documentation/carplay/cpmessagelistitem)
- [CPSessionConfiguration](https://developer.apple.com/documentation/carplay/cpsessionconfiguration)
- [CarPlay HIG](https://developer.apple.com/design/human-interface-guidelines/carplay)
- [Live Activities HIG](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Configuring Siri support](https://developer.apple.com/documentation/xcode/configuring-siri-support)
- [Resolving and handling intents](https://developer.apple.com/documentation/sirikit/resolving-and-handling-intents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

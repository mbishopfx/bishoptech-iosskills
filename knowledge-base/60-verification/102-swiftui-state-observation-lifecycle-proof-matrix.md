# SwiftUI state, Observation, and lifecycle proof matrix

## Purpose

Use this matrix to prove that a SwiftUI feature has the intended owner,
observation dependency, navigation state, lifecycle behavior, preview
fixtures, Liquid Glass states, and on-device AI fallback. It prevents a
beautiful preview from being treated as proof of persistence, cancellation,
accessibility, physical-device behavior, or release readiness.

Related routes:

- [SwiftUI Observation, state, and app lifecycle](../42-framework-deep-dives/77-swiftui-observation-state-and-app-lifecycle.md)
- [State ownership and native lifecycle design](../21-design-deep-dives/105-state-ownership-and-native-lifecycle-design.md)
- [SwiftUI state, Observation, and lifecycle route](../50-capability-recipes/108-swiftui-state-observation-lifecycle-route.md)
- [SwiftUI state, Observation, and lifecycle recipes](../70-code-recipes/120-swiftui-state-observation-lifecycle-recipes.md)

## Evidence levels

| Level | Packet | Proves | Does not prove |
| --- | --- | --- | --- |
| S0 | State chart and ownership table | Intended owner, lifetime, transitions, and fallback | Implementation matches it |
| S1 | Observable model and view code | The selected Observation/State/Environment/Binding route exists | Runtime invalidation or lifecycle correctness |
| S2 | State transition tests | Deterministic model transitions and invariants | SwiftUI rendering or physical interaction |
| S3 | Preview fixture matrix | Views render named states and dependency graph is satisfied | App target, system services, physical device, or release |
| S4 | UI automation | User-visible control, navigation, and task result work in the selected launch fixture | VoiceOver task completion, all windows, system surfaces, or device hardware |
| S5 | Async lifecycle fixture | Task restart, cancellation, stale-result suppression, and error handling | OS termination or background scheduling |
| S6 | Scene restore run | Named scene/route/selection restores on the target simulator/device | Durable domain sync or every window configuration |
| S7 | Physical accessibility/design run | Glass, Dynamic Type, contrast, reduced effects, focus, and hit regions are usable | App Review or all supported devices |
| S8 | Signed Release/TestFlight run | Target/resource/model/system integration in the shipped artifact | Future builds or claims not exercised |

## Ownership matrix

| Claim | Required evidence | Stop condition |
| --- | --- | --- |
| This view owns transient state | State is private at the highest needed view and fixture shows recreation behavior | State is used as durable storage |
| This model is the single source of truth | One owner creates it; descendants read/bind/invoke methods | Multiple model instances compete |
| Observation tracks the intended property | Test mutates one property and asserts only intended output changes | Refresh relies on arbitrary object identity |
| Binding edits the existing model | Binding test shows the parent/source changes | Child silently creates a copy |
| Environment dependency is intentional | Preview/test supplies the dependency and missing-dependency behavior is known | Production view can crash because injection is undocumented |
| Persistent record survives | Store/relaunch/sync evidence | SceneStorage or preview is called persistence |

## State transition matrix

| Transition | Input | Expected output | Required proof |
| --- | --- | --- | --- |
| Empty to loading | User action or lifecycle task | Progress state and bounded task | State test and UI task |
| Loading to ready | Valid source result | Display data tied to request identity | Async fixture and UI assertion |
| Loading to failed | Error/refusal/timeout | Recovery copy and manual action | Error fixture |
| Loading to canceled | View disappears or ID changes | No stale commit; cancellation recorded | Cancellation fixture |
| Ready to editing | User begins edit | Draft/dirty state | UI test and validation fixture |
| Editing to saved | Domain operation succeeds | Durable identity and result | Store/transaction test |
| Editing to conflict | Revision changed | Conflict state and resolution path | Conflict fixture |
| AI generating to proposal | Model returns typed candidate | Reviewable output with provenance | Model adapter fixture |
| AI generating to unavailable | Device/OS/model gate fails | Manual fallback visible | Availability fixture/device check |
| Proposal to committed | User accepts and domain validates | Verified domain update | Confirmation/UI/domain test |

## Observation and rendering proof

| Test | Setup | Assert |
| --- | --- | --- |
| Read dependency | View reads one observable property | That property change updates the intended output |
| Unread property | View does not read a model property | Its change does not cause a behavior assertion to fire |
| Computed dependency | View reads a computed value backed by observable state | Relevant source mutation updates the computed presentation |
| Collection dependency | View reads a collection | Insert/remove/update behavior matches the intended scope |
| Environment model | Model inserted at the feature root | Descendant reads the same identity |
| Missing optional model | Omit optional environment value | View shows fallback instead of crashing |
| Bindable edit | Wrap existing observable model | TextField/Toggle writes the original source |

Keep tests focused on user-visible or domain-relevant behavior. Do not use
private implementation counters as the only measure of invalidation.

## Navigation and restoration matrix

| Claim | Fixture/run | Evidence |
| --- | --- | --- |
| Route is lightweight and stable | Encode/decode route values | Same destination identity after round trip |
| Value navigation works | Activate NavigationLink with a route value | Destination displays resolved model |
| Programmatic navigation works | Set route/path binding | Stack changes without onAppear side effect |
| Missing record is safe | Restore route for deleted record | Unavailable/recovery screen, not crash |
| Scene path restores | Suspend/terminate selected app state as documented | Same scene route restored |
| Multiple windows stay separate | Open two scenes with different route/selection | Each scene retains its own state |
| Deep link merges safely | Deliver URL/activity to an existing scene | Valid route with current authorization/freshness |

Do not put the entire model or sensitive data in a NavigationPath just to make
the destination convenient.

## Task and cancellation matrix

| Claim | Test setup | Required assertion |
| --- | --- | --- |
| View task starts | Render view with a fake async service | One request for the current identity |
| ID task restarts | Change Equatable task ID | Old task canceled, new task starts |
| View disappears | Remove view before service completes | Cancellation observed and no stale write |
| Service ignores cancellation | Fake operation continues after cancel | Result is rejected by request identity/revision |
| Error is visible | Fake service throws | Error state and recovery action render |
| Partial work is safe | Async sequence emits then cancels | Partial result policy is explicit |
| Explicit model task outlives view | Remove view while model-owned task runs | Task continues only when product requires it |

Cancellation is cooperative. A cancel call by itself is not evidence that an
operation stopped or that a late response cannot mutate state.

## Scene phase matrix

| Phase | Test | Evidence |
| --- | --- | --- |
| Active | Bring scene to foreground | Interactive work enabled |
| Inactive | Interrupt with system UI | Nonessential work pauses or remains safe |
| Background | Send app to background | Bounded flush/reconciliation path executes |
| Terminated | Stop/relaunch as supported by the test method | Durable data and intended scene state recover |
| Multi-scene | Change one window’s phase | Scene-specific state does not leak into another |

The app-level scene phase is aggregate across scenes. A view-level scene phase
describes its containing scene. Record which level the feature observes.

## Preview matrix

| Fixture | Required content |
| --- | --- |
| Empty | Creation/import/manual route |
| Loading | Progress, cancellation, and no false completion |
| Loaded | Normal hierarchy and primary action |
| Error | Explanation, retry, and preserved source |
| Permission denied | Manual or settings route |
| Offline/stale | Local data, freshness, and recovery |
| AI unavailable/refusal | Manual fallback and reason |
| AI proposal | Provenance, validation, accept/edit/reject |
| Applying/saved | Duplicate protection and committed result |
| Long content | Dynamic Type/localization/wrapping |
| Appearance | Dark, contrast, reduced transparency/motion |
| Platform | Compact width, iPad/window, supported family |

A preview passes when it renders the intended fixture with the same required
environment/model dependencies. It is not a physical-device or system-service
result.

## Liquid Glass and accessibility matrix

| Claim | Evidence |
| --- | --- |
| Glass surface is functional | Standard semantic control invokes the intended action |
| State is understandable without effects | Reduced-transparency or fallback run shows status/action |
| Contrast is adequate | Light/dark and increased-contrast run |
| Motion is nonessential | Reduce Motion run retains state and focus |
| Large text works | Dynamic Type run preserves title, status, action, and error |
| Assistive task works | VoiceOver/Voice Control/Switch Control task reaches and completes action |
| Hit region is reliable | Physical touch/pointer run across compact/expanded layout |
| System-owned surface is correct | Real widget/control/intent/notification invocation on signed build |

Do not treat a screenshot, preview, or static accessibility audit as proof of
task completion.

## AI adapter matrix

| Claim | Required fixture/device evidence |
| --- | --- |
| API available | Availability check for OS/device/model/language |
| Adapter compiles | Named target and SDK build |
| Output is typed | Schema/validation tests for valid and malformed output |
| Cancellation works | In-flight generation canceled with no stale commit |
| Refusal/error works | Refusal, context limit, timeout, and unavailable state |
| Quality is acceptable | Versioned dataset, criteria, baseline, and evaluation record |
| Side effect is safe | Review/confirmation and domain validation |
| Device is ready | Named physical device, model state, latency, thermal/battery observation |

Model output is evidence of a model response, not of domain truth or a completed
side effect.

## Release matrix

| Claim | Minimum packet |
| --- | --- |
| Feature is in the intended target | Signed app/extension resource and target inspection |
| Model asset is shipped | Archive membership and load/readiness result |
| Liquid Glass route ships | Signed Release/TestFlight run with settings matrix |
| Navigation/system route ships | Entitlements, target membership, system invocation |
| AI fallback ships | Device/unavailable/refusal path on the intended build |
| Persistence survives | Store/relaunch/sync record tied to build |

## Stop conditions

Stop when:

- a preview is the only evidence for a physical interaction;
- a green UI test is used as VoiceOver or hardware proof;
- a task is canceled but the operation ignores cancellation and writes anyway;
- a route restores without re-resolving current model/authorization state;
- a typed environment object is required but not supplied in a test/preview;
- a model result bypasses validation or human review;
- a glass effect hides a missing/error/unavailable state;
- a Debug/simulator build is used for a signed Release/TestFlight claim.

## Sources

- [Observation](https://developer.apple.com/documentation/observation)
- [Observable](https://developer.apple.com/documentation/observation/observable)
- [Model data](https://developer.apple.com/documentation/swiftui/model-data)
- [Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [State](https://developer.apple.com/documentation/swiftui/state)
- [Bindable](https://developer.apple.com/documentation/swiftui/bindable)
- [Environment](https://developer.apple.com/documentation/swiftui/environment)
- [Environment values](https://developer.apple.com/documentation/swiftui/environment-values)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Understanding the navigation stack](https://developer.apple.com/documentation/swiftui/understanding-the-navigation-stack)
- [ScenePhase](https://developer.apple.com/documentation/swiftui/scenephase)
- [SceneStorage](https://developer.apple.com/documentation/swiftui/scenestorage)
- [Restoring your app’s state with SwiftUI](https://developer.apple.com/documentation/swiftui/restoring-your-app-s-state-with-swiftui)
- [task(name:priority:file:line:_:)](https://developer.apple.com/documentation/swiftui/view/task%28name%3Apriority%3Afile%3Aline%3A_%3A%29)
- [task(id:name:priority:file:line:_:)](https://developer.apple.com/documentation/swiftui/view/task%28id%3Aname%3Apriority%3Afile%3Aline%3A_%3A%29)
- [Task](https://developer.apple.com/documentation/swift/task)
- [Task cancellation](https://developer.apple.com/documentation/swift/task/cancel%28%29)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Preview(_:traits:arguments:body:)](https://developer.apple.com/documentation/swiftui/preview%28_%3Atraits%3Aarguments%3Abody%3A%29)
- [Liquid Glass technology overview](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)

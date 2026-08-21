# WidgetKit, ActivityKit, and control surface proof matrix

## Purpose

This matrix separates source knowledge from evidence that a WidgetKit widget,
ControlWidget, or ActivityKit Live Activity actually works in a named app target,
on a named device, under real system conditions.

A complete proof package covers:

- SDK and target availability;
- extension membership and resources;
- projection correctness and privacy;
- timeline, budget, and push behavior;
- interactive intent execution;
- control configuration and locked-device behavior;
- Live Activity start/update/stale/end/relaunch;
- on-device AI proposal versus committed projection;
- accessibility, localization, performance, archive, and release.

## Evidence levels

| Level | Establishes | Does not establish |
| --- | --- | --- |
| Source | Apple documents an API or system behavior | Selected SDK signature or runtime availability |
| Compile | The target imports and type-checks the route | System scheduling, permission, process, or surface delivery |
| Fixture/unit | Projection, state, ID, privacy, or idempotence logic | Real WidgetKit/ActivityKit host behavior |
| Preview | Layout and representative states | Budgets, push, device surfaces, or accessibility completion |
| Simulator/UI | Some layout and host-flow behavior | Physical device, APNs environment, Apple Intelligence availability |
| Signed physical device | Real surface, target/process, lock, input, and device behavior | Every production/account/release configuration |
| Archive/release | Resources, entitlements, target membership, localization, distribution artifact | User behavior or future system ranking |

Record device model, OS build, app version/build, Xcode/SDK, account fixture,
network, locale, time zone, accessibility settings, and artifact path.

## Source and compile gates

| ID | Question | Pass evidence | Boundary |
| --- | --- | --- | --- |
| SRC-01 | Is the selected WidgetKit API available? | Target compile plus availability branch | Do not infer device-family support |
| SRC-02 | Does the provider implement placeholder/snapshot/timeline? | Named Widget Extension compile | Do not infer budget behavior |
| SRC-03 | Does AppIntentTimelineProvider receive the configuration? | Configurable widget target compile and fixture | Do not infer edit-sheet delivery |
| SRC-04 | Does the widget declare supported families? | Configuration and preview compile | Do not infer every host context |
| SRC-05 | Does containerBackground compile? | Widget configuration/view compile | Do not infer background retention |
| SRC-06 | Are accented rendering APIs available? | widgetRenderingMode/widgetAccentable compile | Do not infer visual contrast |
| SRC-07 | Does interactive intent compile in the extension target? | Intent and widget target build | Do not infer safe execution |
| SRC-08 | Does ControlWidget compile? | Control target/template compile | Do not infer gallery/host placement |
| SRC-09 | Does the selected value provider compile? | Preview/current provider compile | Do not infer current-value latency |
| SRC-10 | Does ActivityAttributes/ContentState compile? | Main app plus widget extension build | Do not infer push payload compatibility |
| SRC-11 | Does ActivityConfiguration render? | Widget extension build and preview | Do not infer Lock Screen/Dynamic Island support |
| SRC-12 | Do Activity request/update/end APIs compile? | Main target compile | Do not infer authorization or lifecycle completion |
| SRC-13 | Is ActivityKit push support configured? | Capability, token route, and server contract review | Do not infer APNs delivery |
| SRC-14 | Does the AI route compile? | Foundation Models/Core ML target compile | Do not infer model availability or quality |
| SRC-15 | Is archive membership correct? | Archive inspection of app and extension | Do not infer physical behavior |

## Projection and storage tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| PROJ-01 | Ready projection | Current authorized record | Versioned compact state renders | Full database object required |
| PROJ-02 | Empty projection | No records | Empty state is clear and actionable | Blank/stale content |
| PROJ-03 | Preparing projection | Work not committed | Preparing state avoids false success | “Ready” before commit |
| PROJ-04 | Stale projection | UpdatedAt beyond staleAt | Stale cue and repair path | Old value labeled current |
| PROJ-05 | Offline projection | No network, valid local cache | Local truth plus offline cue | Server success implied |
| PROJ-06 | Denied projection | Permission revoked | Redacted/denied state | Private content remains |
| PROJ-07 | Sign-out | Account changes | Old account projection removed/invalidated | Cross-account leak |
| PROJ-08 | Deleted record | Source ID removed | Empty/missing route | Different record substituted |
| PROJ-09 | Schema upgrade | Old projection version | Migration or safe reset | Decode crash |
| PROJ-10 | Concurrent writer | App and extension update | Revision/atomic write remains valid | Partial JSON/read |
| PROJ-11 | Sensitive field | Health/location/message data | Redaction policy applied | Sensitive title in lock-safe view |
| PROJ-12 | Deep link | Stable current entity ID | App resolves current authorized route | Array index opens wrong record |
| PROJ-13 | App Group unavailable | Container missing/denied | Safe fallback/error | Force unwrap/crash |
| PROJ-14 | Model metadata | AI-derived projection | Model/source/review state retained | Generated value appears source-truth |
| PROJ-15 | Projection revision | Source revision 10 -> 11 | Newer projection wins deterministically | Older write overwrites newer |

## Widget lifecycle and rendering tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| WID-01 | Placeholder | Gallery request | Privacy-safe shape and redacted content | Network/model dependency |
| WID-02 | Snapshot | Current fixture | Fast representative state | Long blocking work |
| WID-03 | Timeline atEnd | Predictable events | Entries and final refresh policy are truthful | Exact-time guarantee assumed |
| WID-04 | Timeline after | Known future change | Reload hint aligns with source event | Polling every few seconds |
| WID-05 | Timeline never | Unpredictable state | App reloads only after actual change | Widget silently becomes stale |
| WID-06 | Selective reload | One widget kind changed | Only affected kind requested | All widgets reloaded for one item |
| WID-07 | Reload delay | System defers request | Old state remains labeled honestly | Immediate-render claim |
| WID-08 | Budget behavior | Test outside debugger | Product remains correct with fewer reloads | Debugger behavior treated as production |
| WID-09 | Dynamic date | Countdown fixture | Time display advances without renderer loop | Timer implies server confirmation |
| WID-10 | Relevance | Bounded relevant event | Hint is current and privacy-safe | Surface ranking promised |
| WID-11 | Configured instance | Two different selections | Each instance resolves its own ID | Shared static value |
| WID-12 | Deleted configuration | Selected entity deleted | Empty/recovery state | Stale private title |
| WID-13 | Small family | Long title and large type | Primary meaning survives | Truncation hides state |
| WID-14 | Large family | List fixture | Scan order and row identity clear | Full app dashboard copied |
| WID-15 | Accessory | High-contrast short fixture | Correct minimal layout | Large color field required |
| WID-16 | Background removable | StandBy/Lock Screen context | Foreground remains meaningful | Foreground disappears with background |
| WID-17 | Accented mode | Tinted Home Screen fixture | Accent groups preserve hierarchy | Color-dependent meaning lost |
| WID-18 | Vibrant mode | System vibrant context | Text/image remain legible | Full-color assumptions |
| WID-19 | Full-color image | Media fixture | Only semantically color-dependent image stays full color | Every decoration fullColor |
| WID-20 | Interactive widget | Button/Toggle fixture | Intent executes, projection updates | UI-only state mutation |
| WID-21 | Invalidatable content | Delayed intent result | Important values signal update | Spinner-only ambiguity |
| WID-22 | Extension termination | Kill extension during read | Safe retry/fallback | Partial projection rendered |
| WID-23 | Push reload | Server change | Token/push/timeline path refreshes when delivered | Push treated as guaranteed |
| WID-24 | Push delay/duplicate | Delayed duplicate payload | Revision/dedupe remains truthful | Older payload wins |
| WID-25 | CarPlay/StandBy | Supported target/context | Input and background policy match host | Unsupported integration claimed |

## Control tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| CTRL-01 | Button action | Bounded idempotent action | One safe commit/result | Toggle semantics in button |
| CTRL-02 | Toggle on | Current false state | SetValueIntent turns state on | Stale value overwrites newer state |
| CTRL-03 | Toggle off | Current true state | SetValueIntent turns state off | Tap does not persist |
| CTRL-04 | Preview value | Add sheet request | Cheap privacy-safe preview | Network/model request |
| CTRL-05 | Current value | System render | Value loads within bounded time | Unbounded fetch |
| CTRL-06 | Configurable control | One selected entity | Edit flow resolves stable configuration | Whole database selector |
| CTRL-07 | Missing entity | Selected record deleted | Safe unavailable/error state | Different entity substituted |
| CTRL-08 | Locked device | Device locked | Redact or require auth per policy | Private data displayed |
| CTRL-09 | Repeated tap | Same action twice | Domain operation converges | Duplicate side effect |
| CTRL-10 | Offline action | Local-only valid action | Local result or actionable error | Remote success implied |
| CTRL-11 | Permission revoked | Access removed before tap | Action refuses and explains repair | Cached permission trusted |
| CTRL-12 | Status text | Temporary state change | Short localized status | Private log in status |
| CTRL-13 | Action hint | Ambiguous action | Hint clarifies without overlong copy | Hint becomes instructions screen |
| CTRL-14 | Control reload | External state changes | ControlCenter reload path updates | Stale toggle forever |
| CTRL-15 | Host sizes | Control Center/Lock Screen/Action button | Meaning survives host-specific sizing | One screenshot only |

## Live Activity lifecycle tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| LIVE-01 | Authorization enabled | ActivityAuthorizationInfo true | Request can proceed | User setting assumed |
| LIVE-02 | Authorization disabled | Live Activities off | App shows ordinary fallback | Request loops/crashes |
| LIVE-03 | Start | Meaningful event | Activity starts once with compact state | Duplicate start |
| LIVE-04 | Start too early | Trivial/instant event | App uses local status instead | System surface spam |
| LIVE-05 | Initial content | Valid attributes/state | Static/dynamic split is correct | Full record payload |
| LIVE-06 | Local update | New source revision | Activity.update shows current state | Old revision overwrites |
| LIVE-07 | Out-of-order update | Revision 11 then 10 | Older state ignored | Progress regresses silently |
| LIVE-08 | Stale date | No update past staleAt | Stale state is visible/truthful | Infinite staleDate extension |
| LIVE-09 | Recovery | New valid state after stale | Activity resumes only if policy permits | Stale is hidden as active |
| LIVE-10 | End success | Domain complete | Ended view reflects completion | “In progress” remains |
| LIVE-11 | End cancel | User cancels | Ended/canceled state is clear | Cancel appears successful |
| LIVE-12 | End unauthorized | Access revoked | Activity ends/redacts per policy | Private data persists |
| LIVE-13 | Relaunch | App killed then launched | Active activities reconcile | Duplicate activity |
| LIVE-14 | App crash | Activity still visible | Next launch repairs or ends | Orphaned live claim |
| LIVE-15 | Deep link | Tap from activity | Cold route reconstructs current detail | Wrong record opens |
| LIVE-16 | Interaction | Button/Toggle in activity | Bounded intent revalidates current state | Stale action commits |
| LIVE-17 | Payload size | Large static/dynamic fields | Combined data stays within documented limit | Transcript/record dump |
| LIVE-18 | Server start/update | APNs fixture | Payload state/version matches current | Token or environment mixed |
| LIVE-19 | Token rotation | New push token | Server replaces old token safely | Old token trusted forever |
| LIVE-20 | Push duplicate | Same event ID twice | Idempotent update | Double transition |
| LIVE-21 | Push missing | Delivery delayed | Stale policy/fallback remains honest | Activity says live forever |
| LIVE-22 | Frequent push denied | Authorization false | Normal update cadence/fallback | Frequent push assumed |
| LIVE-23 | Surface variants | Supported device family | Layout adapts to host | iPhone-only claim generalized |
| LIVE-24 | Dismissal policy | Completed event | Dismissal timing matches product meaning | User cannot understand completion |

## AI projection tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| AI-SURF-01 | Model available | Local model ready | Typed proposal records model/source metadata | Availability assumed |
| AI-SURF-02 | Model unavailable | Unsupported device/state | Deterministic fallback projection | Fabricated generated value |
| AI-SURF-03 | Invalid output | Schema/policy violation | Proposal rejected or needs review | Invalid field committed |
| AI-SURF-04 | Stale source | Source revision changes | Proposal revalidated or discarded | Old proposal commits |
| AI-SURF-05 | Read-only summary | Bounded local record | Summary is labeled/traceable as policy requires | Summary presented as fact |
| AI-SURF-06 | External side effect | Send/delete/purchase | Main app review/confirmation required | Control silently acts |
| AI-SURF-07 | Sensitive output | Health/location/contact data | Lock/privacy policy redacts | AI text leaks on Lock Screen |
| AI-SURF-08 | Projection commit | User-approved proposal | Domain revision and surface projection update | Surface changes before commit |
| AI-SURF-09 | Process termination | Model/commit interrupted | No partial success claim | Widget becomes “done” |
| AI-SURF-10 | Evaluation fixture | Known inputs/expected labels | Quality and fallback results recorded | One happy-path screenshot |
| AI-SURF-11 | Accessibility | Generated summary in large type | Spoken/bounded representation remains useful | Raw long transcript spoken |
| AI-SURF-12 | Privacy logs | Model and surface events | Logs contain categories/IDs only | Prompt or private content retained |

## Accessibility, performance, and release tests

| ID | Scenario | Pass evidence | Boundary |
| --- | --- | --- | --- |
| A11Y-01 | VoiceOver widget | Labels, values, order on each supported family | Screenshot alone is insufficient |
| A11Y-02 | VoiceOver control | Action/state announced correctly | Symbol meaning assumed |
| A11Y-03 | Voice Control | Commands identify controls | Visual label only |
| A11Y-04 | Switch Control | Focus/traversal reaches actions | Touch-only test |
| A11Y-05 | Dynamic Type | Large content sizes preserve meaning | Default size only |
| A11Y-06 | Contrast/transparency | Increased contrast/reduced transparency | Color-only status |
| A11Y-07 | Reduce Motion | Updates remain understandable without motion | Animation as only feedback |
| A11Y-08 | Localization/RTL | Long, plural, RTL, date/unit fixtures | English-only proof |
| PERF-01 | Widget provider | Bounded load time/memory measured | Debugger timing |
| PERF-02 | Control provider | Preview/current values cheap | Cloud request without timeout |
| PERF-03 | Activity update | Main app update budget measured | Infinite update loop |
| PERF-04 | Push handling | Server/payload load tested | One delivery |
| PERF-05 | Thermal/battery | Representative physical-device run | Newest device only |
| REL-01 | Target membership | Widget/control/activity included in archive | Local preview |
| REL-02 | Capabilities | App Groups/APNs/Live Activity settings inspected | Build success |
| REL-03 | Resources | Images, models, localization, shared data present | Debug bundle |
| REL-04 | Privacy | Usage descriptions, manifest, lock policy reviewed | Source-only claim |
| REL-05 | Signed device | Real system invocation from each intended host | Simulator only |
| REL-06 | TestFlight/sandbox | Signed-account behavior recorded | Local StoreKit/fixture |
| REL-07 | Release fallback | Unsupported device/OS behavior verified | Feature flag claim |

## Device and environment matrix

For every physical or release claim, record:

| Dimension | Examples |
| --- | --- |
| Device | iPhone model, iPad model, Apple Watch, Mac, or CarPlay head unit |
| OS | Exact iOS/iPadOS/watchOS/macOS build |
| App | Version/build and signed configuration |
| SDK | Xcode and SDK selected for the archive |
| System settings | Live Activities, notifications, lock state, Home Screen tint |
| Account | Synthetic signed-in/out state and server environment |
| Network | Wi-Fi/cellular/offline/poor connectivity |
| Accessibility | VoiceOver, Dynamic Type, contrast, transparency, motion |
| Surface | Home Screen, Lock Screen, Control Center, Action button, Dynamic Island |
| Artifact | Screenshot/video/log/archive path, redacted |
| Outcome | Pass/fail/known limitation and next repair |

## Evidence record template

~~~yaml
test_id: LIVE-18
feature: ActivityKit remote update
app_version: 0.1.0
build: 43
sdk: Xcode-selected iOS SDK
device:
  model: physical-device-model
  os: iOS build
surface: Lock Screen or Dynamic Island
account_fixture: synthetic-account
network: Wi-Fi or cellular
accessibility:
  voice_over: false
  dynamic_type: default
  reduce_motion: false
  reduce_transparency: false
source_revision: event-104
projection_revision: 18
push:
  environment: sandbox-or-production
  token_rotation_tested: true
  event_id: event-104
result: pass
observed_state: active
known_limits:
  - delivery timing is opportunistic
artifact: redacted-artifact-path
~~~

## Sources

- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [AppIntentTimelineProvider](https://developer.apple.com/documentation/widgetkit/appintenttimelineprovider)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date/)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [Displaying the right widget background](https://developer.apple.com/documentation/widgetkit/displaying-the-right-widget-background)
- [Optimizing your widget for accented rendering mode and Liquid Glass](https://developer.apple.com/documentation/widgetkit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Updating widgets with WidgetKit push notifications](https://developer.apple.com/documentation/widgetkit/updating-widgets-with-widgetkit-push-notifications)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [ControlValueProvider](https://developer.apple.com/documentation/widgetkit/controlvalueprovider)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [ActivityAuthorizationInfo](https://developer.apple.com/documentation/activitykit/activityauthorizationinfo)
- [ActivityContent](https://developer.apple.com/documentation/activitykit/activitycontent)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [ActivityConfiguration](https://developer.apple.com/documentation/widgetkit/activityconfiguration)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [UI testing](https://developer.apple.com/documentation/xcuiautomation)
- [Accessibility](https://developer.apple.com/accessibility/)
- [MetricKit](https://developer.apple.com/documentation/metrickit)

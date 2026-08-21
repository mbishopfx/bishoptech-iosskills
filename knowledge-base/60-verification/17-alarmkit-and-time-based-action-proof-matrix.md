# AlarmKit and time-based action proof matrix

## Evidence rule

AlarmKit spans an app target, a system daemon, a possible widget extension, App Intents, authorization, time-zone behavior, and physical system surfaces. Verify each layer separately. A schedule call that returns an Alarm object proves only that one invocation succeeded under that runtime state; it does not prove delivery, alert sound, countdown rendering, paired-device behavior, or release readiness.

Use the evidence vocabulary in the [source review checklist](00-source-review-checklist.md) and the [build/device/release checklist](01-build-device-and-release-checklist.md). Keep screenshots, logs, test-plan results, device/build identifiers, and configuration evidence together.

## Proof ladder

| Layer | What it can prove | What it cannot prove |
| --- | --- | --- |
| Official source review | Current API names, documented target/configuration boundaries, usage description, system-surface expectations | The app’s target compiles or the device delivers |
| Source/SDK inspection | Availability attributes, generic constraints, required imports, Info.plist key names | Runtime authorization or physical presentation |
| Compile | Target can link AlarmKit and any extension/imports resolve | Alarm delivery, permission prompt, timing, or content legibility |
| Unit tests | Draft normalization, fixed/relative mapping, validation, idempotency, reconciliation classification | System daemon state or alert behavior |
| SwiftUI preview/widget fixture | App-owned editor, review states, AlarmAttributes fixture, accessibility labels | Real system surfaces, device luminance, process suspension |
| Simulator | Navigation, mocked authorization/state, app UI, some extension composition | Real alarm timing/alert, Lock Screen delivery, haptics, Focus/silent behavior, paired Watch |
| Signed physical device | Authorization, scheduling, process termination, timing, sound, system surface, hardware settings | Every supported device/OS, App Store delivery, all localization/performance states |
| TestFlight/release build | Distribution configuration, entitlements, privacy strings, release optimization, real install path | App Store review/approval, universal hardware coverage, production user behavior |

## Matrix

| Capability or risk | Minimum method | Evidence to retain | Not proven by |
| --- | --- | --- | --- |
| AlarmKit linked to the intended app target | Xcode build with the intended SDK and deployment target | Build log, target membership, SDK/Xcode version | A Markdown recipe |
| NSAlarmKitUsageDescription present and truthful | Inspect built app Info.plist and trigger authorization in a test build | Built plist, exact prompt screenshot, permission-state notes | A source file that is not in the target |
| Authorization notDetermined -> authorized | Signed device, fresh permission state, requestAuthorization | Device model/OS, prompt, returned state, timestamp | A mocked .authorized value |
| Authorization denied/revoked | Deny in prompt, then change Settings and retry | Denied UI, recovery path, schedule not registered, logs | A disabled button in a preview |
| Fixed one-shot schedule | Physical device with a near-future fixed Date | Input time, current time zone, returned id, delivery result | Unit test of Date construction |
| Relative local-time schedule | Physical device, one near-future .never and one weekly recurrence | Locale, calendar, time zone, weekdays, delivery | Showing “weekly” in a list |
| Time-zone change | Register relative and fixed routes, change device time zone, reconcile | Before/after schedule meaning and observed behavior | A static time-zone formatter |
| Daylight-saving transition | Test a supported transition or use a controlled clock fixture plus device run | Expected recurrence policy and observed local time | A single same-day run |
| Immediate timer | Schedule a short timer, background/terminate app, wait through countdown and alert | Countdown/alert timestamps, process state, system UI evidence | Task.sleep in the app process |
| Countdown presentation target | Build widget extension with ActivityConfiguration for AlarmAttributes<Metadata> | Target graph, extension build, system surface screenshot | A widget preview alone |
| Countdown state | Physical device observe countdown, pause, resume, alert | State transition log and screen recordings/screenshots | A switch over mocked enum cases |
| Paused state | Tap pause in the system presentation; resume from system surface | Pause/resume result and updated app reconciliation | Calling AlarmManager.pause in a unit test |
| Stop behavior | Stop from the alert and from app-owned controls | Alarm id, result, missing-from-system observation, domain state | Hiding the stop button |
| Repeat/countdown behavior | Trigger configured secondary action and verify post-alert duration | Action invocation, resulting state, no duplicate record | A local button with the same title |
| Custom secondary intent | Invoke the App Intent from the real system alarm | Intent log, idempotency key, domain side effect, error path | Calling perform() directly |
| Alarm updates | Change/cancel/stop from multiple surfaces and observe alarmUpdates | Sequence events, coalescing behavior, reconciliation output | A polling timer |
| alarms snapshot | Launch/relaunch after system state changes and read alarms | Snapshot before/after, missing one-shot classification | Cached in-memory list |
| Fired versus cancelled classification | Schedule one-shot, stop one, let another fire, compare records and alarms | Stored expected schedule plus outcome evidence | Assuming every missing id fired |
| App process termination | Force quit or terminate under test conditions, wait, relaunch | Device state, alarm delivery, launch reconciliation | Foreground-only testing |
| Reboot or OS update | Test on a controlled physical device where relevant | Before/after registration and delivery notes | Simulator reboot |
| Lock Screen presentation | Lock device before countdown and alert | Lock Screen screenshots/recording, device/OS | In-app replica |
| Dynamic Island presentation | Supported iPhone, inspect compact/minimal/expanded states | Each supported presentation and safe-area notes | Expanded preview only |
| StandBy presentation | Supported device/configuration in StandBy | Landscape/StandBy evidence and luminance notes | A portrait screen |
| Paired Apple Watch forwarding | Paired device with the appropriate state | Phone/Watch models, pairing state, alert evidence | Claiming it from the WWDC sample |
| Focus and silent behavior | Test relevant Focus and silent settings on a physical device | Settings, alert timing/sound, observed behavior | A notification interruption-level assumption |
| Sound configuration | Test the chosen AlertSound under device audio state | Sound route, volume/mute state, observed result | A non-nil configuration |
| App-owned review state | UI test with mocked AlarmKit service | Schedule summary, error/recovery copy, accessibility tree | System alarm delivery |
| Dynamic Type | App UI test at large accessibility sizes plus widget fixtures | Screenshots, truncation audit, UI test results | Default-size preview |
| VoiceOver and Voice Control | Task-based physical-device interaction | Spoken labels/actions, focus order, action completion | accessibilityLabel compilation |
| Reduce Motion / transparency / contrast | Device settings with app-owned editor and widget | Visual and task evidence for each mode | A tint-color check |
| Localization and RTL | Localized build with long labels, weekdays, 12/24-hour settings, RTL | Screenshots and task results | English-only snapshot |
| AI proposal safety | Deterministic fixtures and model-availability variants | Prompt/schema/model version, proposal, validation result, confirmation trace | A model response that looks plausible |
| No silent AI side effect | UI test or device run from proposal to confirm | Evidence that no AlarmKit call occurs before confirmation | Code review alone |
| Duplicate scheduling/idempotency | Tap/trigger schedule and system action repeatedly | One domain id, one expected system id, retry behavior | A disabled button |
| Privacy of locked-screen copy | Physical lock-screen inspection with sensitive labels | Redacted/approved copy policy and screenshots | Assuming the system hides all text |
| App Store/TestFlight configuration | Archive, install, run release build on device | Archive metadata, plist, entitlements, target list, result bundle | Debug run |

## Test-plan slices

Create separate test-plan configurations or tags for the following slices so a green run is not mistaken for complete proof:

### Deterministic domain slice

- fixed-date normalization;
- relative weekly normalization;
- timer duration bounds;
- time-zone display;
- duplicate detection;
- idempotent stop/repeat action;
- missing-system-alarm classification.

### SwiftUI and accessibility slice

- schedule editor;
- review confirmation;
- denied/recovery states;
- large Dynamic Type;
- VoiceOver labels and actions;
- RTL and long localized labels;
- reduced motion and transparency fallback.

### Widget fixture slice

- AlarmAttributes metadata encode/decode;
- countdown, paused, and alert fixture rendering;
- Dynamic Island layout branches;
- safe fallback when metadata is absent or a schema version is unsupported.

### Physical device slice

- authorization;
- near-future one-shot;
- short countdown;
- pause/resume/stop/repeat;
- app termination;
- Lock Screen;
- Focus/silent state;
- supported paired-device surface;
- relaunch reconciliation.

## Evidence packet

For a release candidate, retain one packet per supported route containing:

1. app and widget target names;
2. Xcode/SDK/deployment target;
3. built Info.plist with NSAlarmKitUsageDescription;
4. entitlements and Live Activity configuration if applicable;
5. device model and OS;
6. authorization state and Settings state;
7. schedule input in local time and time zone;
8. AlarmKit id and app-owned record id;
9. schedule/updates/reconciliation logs with sensitive content redacted;
10. physical screenshots or recordings of the relevant system surfaces;
11. accessibility and localization evidence;
12. failure/recovery evidence;
13. archive/TestFlight build identifier when distribution is in scope.

Do not include user secrets or raw private alarm content in the packet. Use fixture labels where possible.

## Stop conditions

Stop the release claim if any of these are true:

- the usage-description key is missing or generic;
- the alarm list cannot distinguish local intent from system registration;
- the countdown target is missing or unverified;
- a custom action can repeat an irreversible side effect;
- AI can schedule without a visible user confirmation;
- fixed and relative time semantics are conflated;
- the only delivery evidence is a simulator, preview, or foreground run;
- alert copy exposes sensitive data on the lock screen without an explicit policy;
- the app does not recover after denied authorization or a missing system alarm;
- the actual Xcode SDK signature differs from the route sketch and has not been reconciled.

## Sources

- [AlarmKit](https://developer.apple.com/documentation/alarmkit)
- [AlarmManager](https://developer.apple.com/documentation/alarmkit/alarmmanager)
- [Scheduling an alarm with AlarmKit](https://developer.apple.com/documentation/AlarmKit/scheduling-an-alarm-with-alarmkit)
- [AlarmManager alarms](https://developer.apple.com/documentation/alarmkit/alarmmanager/alarms)
- [AlarmManager authorization state](https://developer.apple.com/documentation/alarmkit/alarmmanager/authorizationstate-swift.enum)
- [AlarmManager authorization updates](https://developer.apple.com/documentation/alarmkit/alarmmanager/authorizationupdates)
- [AlarmManager schedule](https://developer.apple.com/documentation/alarmkit/alarmmanager/schedule%28id%3Aconfiguration%3A%29)
- [AlarmPresentation.Alert](https://developer.apple.com/documentation/alarmkit/alarmpresentation/alert-swift.struct)
- [AlarmPresentation.Countdown](https://developer.apple.com/documentation/alarmkit/alarmpresentation/countdown-swift.struct)
- [AlarmPresentation.Paused](https://developer.apple.com/documentation/alarmkit/alarmpresentation/paused-swift.struct)
- [AlarmAttributes](https://developer.apple.com/documentation/alarmkit/alarmattributes)
- [AlarmMetadata](https://developer.apple.com/documentation/alarmkit/alarmmetadata)
- [NSAlarmKitUsageDescription](https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSAlarmKitUsageDescription)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Creating custom views for Live Activities](https://developer.apple.com/documentation/ActivityKit/creating-custom-views-for-live-activities)
- [Managing notifications](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

# Meta Wearables evaluation fixtures

Use these fixtures to compare roles and implementations. Fixtures are contracts, not claims that the device path is available.

## Team-manifest fixture

Input: “Use the full Meta Wearables SDK team for iOS DAT, Android DAT, and a
Ray-Ban Display Web App, with regular Gen 2 and alleged Gen 3 support.”

Expected result:

- load and validate `references/team-manifest.yaml`;
- report the 23 local role IDs and selected upstream handoff IDs, plus the
  official agent-surface contract, rather than inventing a new “regular SDK”
  specialist;
- select the native DAT or Web Apps surface explicitly and preserve phone
  fallback as a separate route;
- apply the Ray-Ban Display, Gen 2, and Gen 3 claim gates; keep Gen 3
  unresolved until official mapping and named physical evidence exist;
- return the shared handoff fields, processing-location labels, evidence ladder,
  and next proof task.

## Route fixture

Input: “Show a short, glanceable result on Ray-Ban glasses, with a phone setup screen and a fallback when the device is unavailable.”

Expected result:

- identify whether the target is native DAT Display or a Ray-Ban Display Web App;
- name the exact supported runtime model and capability gate;
- keep pairing, permissions, and setup on the phone;
- define `not registered`, `unsupported`, `disconnected`, `permission denied`, `stream unavailable`, and `dismissed` states;
- require a physical-device test before claiming glasses behavior.

## DAT camera fixture

Input: “Preview frames from the wearable camera and stop cleanly when the user leaves the screen.”

Expected result:

- use the current `DeviceSession.addCamera(config:) -> Camera` route and the camera’s stream/stop lifecycle;
- inspect the actual installed SDK types before writing frame conversion code;
- bound buffering and stop/release the camera on cancellation/background as appropriate;
- distinguish a phone-camera preview, mock frames, and a glasses-camera result.

## Implementation-recipes fixture

Input: “Implement a glance card that can use iOS DAT Display, Android DAT
Display, or a Ray-Ban Display Web App, with a phone fallback. Give me the
scaffolding and tell me what is actually proven.”

Expected result:

- select one vertical-slice playbook and filter the source-pinned manifest into
  exact `IOS-*`, `AND-*`, `WEB-*`, compatibility, and evidence rows;
- freeze the target tuple and label generated/package-specific symbols as
  confirmed or `to-verify` instead of presenting pseudocode as compiled code;
- keep iOS async/publisher, Android `Flow`/`DatResult`, Web App DOM/host input,
  and phone fallback in separate adapters with one coordinator, one epoch, and
  child-before-parent stop order;
- emit a processing-location, consent, retention, network, thermal, and typed
  fallback contract, with no raw media, tokens, or private identifiers in the
  scaffold or fixture;
- return reducer/fake/mock/browser/build/connected/physical proof tasks and
  state that recipe code does not establish Gen 2/Gen 3 capability or physical
  Display behavior.

## Target-preflight fixture

## Team-preflight fixture

Input: “Run the full Meta Wearables preflight before implementing this feature.”

Expected behavior:

- run `scripts/run_team_preflight.py <workspace> --json` and preserve its
  `decision`, target-surface receipt, check statuses, source mode, and next
  action;
- use `bootstrap` for `NO_TARGET` or `TARGETS_PARTIAL`, even when the manifests
  and source checkers are green;
- use `source-refresh-required` when a real target exists but `--live-source`
  was not run; use `repair-failed-checks` for failed validators;
- use `implementation-handoff-required` when a real target and source receipt
  exist but no validated implementation packet was supplied;
- reserve `target-preflight` for a real target with all required manifest and
  requested source checks and the implementation handoff passing;
- never turn a team-preflight receipt into build, physical, signed, or release
  evidence.

## Routing-receipt fixture

Input: “Route the full Meta Wearables SDK request, or route native Display for
iOS, and give me the exact skill team and evidence plan.”

Expected behavior:

- run `scripts/route_capability.py --full-sdk --json` for the composite request,
  or `--capability native-display --surface native-dat-ios --json` for the
  narrow request;
- preserve the current team/surface/plan manifest IDs and revisions, DAT
  0.9.0/source snapshot, terminology contract, source authority order, and
  Developer Center/MCP access state;
- return native-DAT local Codex install paths, the Web Apps marketplace mode,
  and the MCP tool/auth contract as source-only routing evidence;
- return selected local roles, upstream handoff IDs, capability owner roles,
  privacy path, fallback, preflight tasks, evidence levels, proof-task IDs,
  claim boundaries, non-claims, and one next action;
- fail closed on an unknown capability, an invalid surface filter, missing
  owner role, or missing manifest rather than guessing a platform/API;
- keep “full SDK” as a composite audit, “regular SDK” as an ambiguous route
  phrase, and Gen 3 as unresolved until separate source/runtime/device evidence
  closes those claims.

## Static-fixture-suite fixture

Input: “Run the reusable Meta Wearables fixture suite and tell me which lanes
are actually checked.”

Expected behavior:

- run `scripts/run_static_fixture_suite.py` and preserve each check’s
  `pass`, `failed`, `unavailable`, or `not-run` status;
- exercise the shared-domain tests, Web App Node tests and strict metadata
  preflight, Android target preflight, manifest/recipe validators, and the
  target-intake handoff packets plus the composite full-SDK routing receipt;
- when `--ios-dat-checkout` is supplied, type-check the iOS camera, Display,
  MockDevice, and MockDevice test-client starters against the selected simulator
  XCFrameworks;
- when `--live-source` is supplied, include the public source-tree and revision
  receipts without printing credentials;
- state that the suite proves reusable source/static/mock readiness only and
  leaves account, connected, physical, Gen 2/Gen 3, signed, and release gates
  open.

Input: “Before we connect a Ray-Ban Gen 2 or alleged Gen 3 target, inspect my
iOS/Android/Web App setup and tell me exactly what is ready for a build, what is
missing, and what evidence the setup does not prove.”

Expected result:

- freeze the source revision, route, scheme/target or Gradle module/variant or
  Web App revision/origin, OS/toolchain, configuration, package/artifact graph,
  privacy/configuration files, fallback, and redacted identity fields;
- use `PRE-SOURCE-01` plus the platform-specific `PRE-IOS-01`,
  `PRE-ANDROID-01`, or `PRE-WEB-01`, then `PRE-IDENTITY-01`, `PRE-DATA-01`,
  `PRE-TUPLE-01`, and `PRE-BUILD-01` as applicable;
- keep `Package.resolved`, Gradle dependency reports, and hosted revision
  evidence separate from physical device, account/channel, signed, and
  production evidence;
- leave Gen 3, firmware, runtime `DeviceType`, account/channel, and processing
  location unresolved when they were not observed; do not turn a clean preflight
  into camera, audio, Display, sensor, or glasses support.

## Source-refresh fixture

Input: “The Meta Wearables SDK may have changed. Check whether our pinned iOS,
Android, and Web App sources drifted before we update the knowledge base.”

Expected result:

- run `meta-wearables-source-refresh/scripts/check_source_revisions.py` against
  the source-pinned manifest;
- run `meta-wearables-source-refresh/scripts/check_source_tree_inventory.py` and
  report exact iOS, Android, and Web Apps role lists as well as their counts;
- report expected and observed iOS `main`, iOS reproducible tag, Android `main`,
  and Web Apps `main` revisions without cloning or printing credentials;
- treat `DRIFT` as a refresh blocker that requires a new source receipt,
  migration/source-conflict impact audit, affected-role update, and package
  refresh; never silently rewrite the manifest;
- keep a matching result as source freshness evidence only, separate from
  target compilation, account/channel access, physical glasses, or release
  proof.

## Native Display fixture

Input: “Show a two-action glance card and let the user move or dismiss it.”

Expected result:

- gate on the runtime Display capability;
- use the current Display view/input contract and a small state machine;
- define focus, selection, dismiss, timeout, and disconnect behavior;
- test on a supported physical Display device before claiming input or rendering.

## Input-and-sensor fixture

Input: “Use the full Meta Wearables SDK for a Display/Neural Band experience
with motion or location features, keep it on-device where possible, and make it
work across iOS, Android, Gen 2, and Gen 3.”

Expected result:

- identify the exact native DAT Display, Web App, and phone fallback surfaces;
- separate Display callbacks, Web App D-pad/EMG/temple input, browser motion/
  orientation/geolocation, and phone sensors instead of normalizing them into an
  invented common SDK API;
- mark native IMU/EMG/temple symbols and full-reference/Web App conflicts
  `to-verify` until the selected artifact/API, simulator, target firmware, and
  named physical result close each feature row;
- define source, permission/secure-context, session/page epoch, duplicate/stale
  event, listener teardown, bounded sampling, raw-data, processing-location,
  thermal, and phone-fallback contracts;
- return `INP-SOURCE-01`, `INP-STATIC-01`, `INP-MOCK-01`, `INP-BROWSER-01`,
  `INP-CONNECTED-01`, `INP-PHYSICAL-01`, `INP-RECOVERY-01`, and
  `INP-RELEASE-01`; do not generalize Gen 2 or Gen 3 from a neighboring model.

## Web App fixture

Input: “Build a Ray-Ban Display Web App with a high-contrast status card.”

Expected result:

- public HTTPS URL, 600×600 canvas, additive content, and D-pad/focus behavior;
- compare the current full Developer Center index with Web App toolkit `main`;
  keep text composer, offline cache, Escape/back, extended gestures, and
  sensors as source-conflict/to-verify features with explicit fallbacks;
- browser simulator and real-glasses evidence recorded separately;
- no phone-only Web App proof described as glasses proof.

## Privacy fixture

Input: “Listen to glasses audio and send it to an AI service.”

Expected result:

- first establish whether the official SDK exposes that exact audio path;
- identify consent, indicator, retention, transmission, vendor, and deletion behavior;
- avoid claiming a raw glasses microphone API or cloud permission that has not been sourced;
- provide a phone-microphone or manual-input fallback only if the product and user consent allow it.

## Android parity fixture

Input: “Use the full DAT SDK in a Kotlin app and keep the iOS version aligned.”

Expected result:

- pin the Android Maven artifacts and repository/plugin revision separately from
  the iOS SPM package;
- inspect `Wearables.initialize`, `DatResult`, `Flow`/`StateFlow`, Manifest,
  credentials, permissions, R8, and the selected Android target;
- compare concepts, not symbols, across Swift and Kotlin;
- keep Android MockDevice, connected, and physical evidence separate from iOS;
- leave “Gen 3,” release channel, and Play/App Store claims gated until direct
  source and target evidence exists.

## Android API-atlas fixture

Input: “In a Kotlin/Java Android app, use DAT 0.9 camera frames, photo capture,
native Display button actions, MockDevice, and a phone fallback. Tell me which
symbols and artifacts are actually safe to implement.”

Expected result:

- pin `mwdat-core`, `mwdat-camera`, `mwdat-display`, and `mwdat-mockdevice`
  coordinates plus the Android repository/API-reference revision;
- map `Wearables.initialize`, registration, device selection, session, camera,
  Display, `DatResult`, and `Flow`/`StateFlow` symbols with selected-artifact
  compile gates;
- surface the 0.8/0.9 version, `Session`/`DeviceSession`, camera-consolidation,
  Display-builder, DAM, Java-interop, and R8 migration conflicts;
- keep phone `AudioRecord`, MockDevice, connected, physical, signed, and
  release-channel evidence as separate lanes;
- hand the shared state, Android adapter, cancellation, fallback, and stale
  event contract to the architecture role;
- return `AND-SOURCE-01`, `AND-CONFIG-01`, `AND-API-01`, `AND-MIGRATE-01`,
  `AND-MOCK-01`, `AND-BUILD-01`, `AND-PHYS-01`, and `AND-RELEASE-01`, with Gen 3
  and undocumented cross-platform parity left `to-verify`.

## Developer-operations fixture

Input: “Set up a private iOS and Android DAT test release for one Ray-Ban
Display app, keep Developer Mode available, invite a tester, and tell me what
telemetry and permissions are involved without exposing credentials.”

Expected result:

- check or mark access-gated the existing MMA organization, Wearables team, and
  operator role; never create a duplicate company organization as a workaround;
- distinguish platform app identities, project configuration, product listing,
  permission rationale, selected DAT artifact, target build, and privacy owner;
- assign Major/Minor/Patch intent, record generated DAT application build status,
  and wait for `Ready` before channel distribution;
- distinguish MMA membership from tester Meta Account invitation/acceptance and
  Meta AI channel/connected-app permission state;
- keep Developer Mode separate from attested signed release-channel evidence;
- audit telemetry categories, Android/iOS opt-out metadata, disclosure,
  retention, deletion, and consent separately;
- return `DCO-SOURCE-01`, `DCO-ORG-01`, `DCO-PROJECT-01`, `DCO-VERSION-01`,
  `DCO-CHANNEL-01`, `DCO-TESTER-01`, `DCO-TELEMETRY-01`, and `DCO-RECOVERY-01`,
  leaving account, physical, and production results `access-gated`/`not-run`.

## Full-SDK audit fixture

Input: “Use the full Meta Wearables SDK for iOS, Android, Ray-Ban Meta Gen 2,
Gen 3, Display, camera, glasses audio, sensors, offline Web Apps, and parity.”

Expected result:

- resolve “regular SDK” through the manifest terminology contract instead of
  inventing a third public native SDK, and carry the `full-sdk` composite-audit
  status into the handoff;
- inventory the five iOS package products (four runtime products plus the
  test-only `MWDATMockDeviceTestClient`), four Android artifacts, Web Apps runtime, and
  upstream plugin/debugging surfaces separately;
- preserve iOS/Android `AGENTS.md` version, DAM, minimum-OS, and
  `Session`/`DeviceSession` conflicts instead of copying them as current API;
- label Android CameraAccess `AudioRecord` as phone microphone audio and keep
  raw glasses microphone access unproven unless a target-specific route exists;
- keep Web Apps text/offline/back/gesture/sensor features source-conflicted;
- map Gen 2 through runtime/device/firmware evidence and keep Gen 3 gated;
- return source, SDK, compile, fixture, connected, physical, signed,
  release-channel, and production evidence rows separately.

## Device-generation fixture

Input: “Support Ray-Ban Meta Gen 2, Meta Glasses/Gen 3, and Ray-Ban Display
with the full SDK.”

Expected result:

- separate the consumer product label, SDK model identifier, and runtime
  capability profile;
- treat the official Gen 2 and Meta Glasses announcements as naming/source
  evidence only, not as DAT support or Display proof;
- record the selected package/artifact, runtime model, firmware, companion
  version, compatibility state, and capability predicates;
- create `GEN-SRC-01`, `GEN-STATIC-01`, `GEN-CONNECTED-01`,
  `GEN-PHYSICAL-01`, and `GEN-CROSS-01` evidence rows;
- leave “Gen 3” `to-verify` when no current public mapping and named-device
  result establish it, with a phone/mock fallback.

## Version-dependency and firmware-drift fixture

Input: “Ray-Ban Meta Gen 2 worked on firmware 126, then failed after the
glasses updated to 127 on DAT 0.9.0. Tell me whether Gen 2 is supported and
whether the regular SDK or Gen 3 route fixes it.”

Expected result:

- freeze the exact iOS/Android package or artifact, repository revision, phone
  OS/build, Meta AI version, on-glasses DAT-app version, firmware before/after,
  observed runtime `DeviceType`, link, account mode, and first failing state;
- reopen the official version-dependencies page and record its actual access
  state; if login-gated, leave the exact support value unresolved rather than
  importing a remembered table;
- classify the public issue or other troubleshooting report as community
  evidence, never as first-party compatibility policy;
- compare registration, permission, device discovery, session, camera/audio,
  Display/input, update, disconnect, and recovery as independent capability
  rows;
- preserve the current 0.8→0.9 migration gates and do not infer that a newer
  Web Apps route, `.metaGlasses`, or “Gen 3” wording repairs native DAT support;
- return `COMP-SOURCE-01`, `COMP-STATIC-01`, `COMP-VERSION-01`,
  `COMP-TUPLE-01`, `COMP-CAPABILITY-01`, `COMP-FIRMWARE-01`,
  `COMP-GEN3-01`, and `COMP-RELEASE-01`, with physical and release rows
  `not-run` when the named target/account/build is unavailable.

## On-device compliance fixture

Input: “Keep camera/audio/sensor processing on device, use a phone fallback,
and ship a Ray-Ban Display experience without leaking private data.”

Expected result:

- classify every path as glasses-native, phone-local, remote, mixed, or unknown;
- record the exact source, package/artifact, permissions, consent trigger,
  network destination, storage/retention, model/runtime location, and deletion
  path;
- bound frame/audio queues, logs, cache, thermal/background behavior, and
  stop/doff/disconnect recovery;
- label phone microphone, remote transcription, Web App service workers, and
  mock/browser output separately from glasses-native evidence;
- return `ODC-SOURCE-01`, `ODC-STATIC-01`, `ODC-MOCK-01`, `ODC-PHYS-01`, and
  `ODC-RELEASE-01` rows with typed fallbacks and open gates.

## Operational-readiness fixture

Input: “The app registers in Developer Mode but the signed release cannot
start a session; the glasses may need a firmware or on-glasses DAT-app update.
Diagnose it without exposing credentials and tell me what is actually proven.”

Expected result:

- freeze the iOS/Android target, DAT package/artifact, phone OS, Meta AI version,
  runtime model, firmware, on-glasses DAT-app state, account/project, mode,
  signing identity, and release-channel/tester state;
- distinguish a Developer Mode success from release authorization, app
  attestation, provisioning, or signed-channel evidence;
- classify the first failing state as configuration, account/channel, companion,
  firmware, on-glasses DAT app, transport, permission, lifecycle, thermal/power,
  or source/runtime conflict;
- apply one documented, least-invasive recovery and record the post-action
  firmware/DAT-app/link/registration/session state plus whether the original
  operation completed;
- use `OPS-SOURCE-01`, `OPS-CONFIG-01`, `OPS-PAIR-01`, `OPS-RECOVERY-01`,
  `OPS-THERMAL-01`, and `OPS-CHANNEL-01` at the appropriate evidence levels;
- leave unknown version tables, community issue reports, Gen 3 mapping, and
  unobserved recovery as `access-gated`/`source-conflict`/`to-verify`, and
  redact application IDs, tokens, signatures, serials, and diagnostics.

## Debugging-and-observability fixture

Input: “The DAT app cannot connect to the glasses. Use the live debug tools if
available, diagnose the first failure, and prepare a safe handoff without
exposing credentials or private media.”

Expected result:

- freeze platform, app target/build, DAT package/artifact revision, phone OS,
  product wording/runtime type, firmware, Meta AI version, mode/channel, and
  exact operation;
- distinguish debug-server connection from SDK readiness, registration,
  permission, device eligibility, link, session, capability, and stream/audio/
  Display state;
- when a local DAT Inspector exists, run `discover_debug_servers`,
  `connect_to_debug_server`, `get_connection_status`, `get_sdk_state`, and
  `get_dat_readiness` before using boundary/path/event tools;
- use `get_companion_boundary_diagnosis`, `get_device_path`,
  `get_permissions`, and `get_device_properties` only as needed, ask for one
  narrow reproduction, then use a bounded `wait_for_events`, `get_errors`, or
  `get_event_digest`;
- export a diagnostic bundle only when needed, inspect/redact raw media,
  tokens, identifiers, personal data, and private URLs, and retain only the
  minimum metadata needed for the handoff;
- return `DBG-SOURCE-01`, `DBG-CONN-01`, `DBG-READINESS-01`,
  `DBG-BOUNDARY-01`, `DBG-PATH-01`, `DBG-EVENT-01`, `DBG-BUNDLE-01`,
  `DBG-REDACTION-01`, `DBG-PHYSICAL-01`, and `DBG-RELEASE-01` at the proper
  evidence levels; never call app-visible debug events companion introspection,
  physical proof, or release proof.

## Application-architecture fixture

Input: “Build one iOS + Android product that can show a compact result on
native Display, fall back to the phone, and later support a Ray-Ban Display Web
App. Keep the state correct through disconnects and avoid duplicating the DAT
logic in every view.”

Expected result:

- choose the actual native DAT, native Display, Web App, and phone routes;
- define shared product state/events/policy without importing Swift, Kotlin, or
  browser SDK types into the shared layer;
- assign one coordinator and one capability owner, with session epochs,
  cancellation, terminal cleanup, bounded frame/audio queues, and stale-event
  rejection;
- map iOS SPM/`AsyncSequence` or publisher behavior, Android Maven/`Flow`/
  `StateFlow`/`DatResult`, and Web App lifecycle separately;
- provide typed unsupported, disconnected, permission-denied, thermal, stale,
  and phone-fallback states;
- specify reducer, platform-fake, MockDevice, browser-simulator, build,
  connected, physical, and signed-release evidence separately;
- return `ARCH-SOURCE-01`, `ARCH-STATIC-01`, `ARCH-TEST-01`, `ARCH-MOCK-01`,
  `ARCH-PHYS-01`, and `ARCH-RELEASE-01` rows, with Gen 3 and undocumented
  parity left `to-verify`.

## Transport-and-reliability fixture

Input: “Use DAT camera and glasses audio over the best available link on iOS
and Android. Support Wi-Fi where available, keep processing on-device or
explicitly local, and recover cleanly from disconnects and heat.”

Expected result:

- freeze the platform, DAT package/artifact, companion, firmware/DAT-app,
  account/mode/channel, runtime model, and requested camera/Display/audio
  workload;
- classify Bluetooth control, Wi-Fi/local-network media, HFP input, A2DP
  output, Internet, and unknown hops independently;
- inspect iOS Bluetooth/local-network/Bonjour/audio configuration and Android
  Bluetooth/Internet/Manifest/artifact configuration without assuming parity;
- mark the reviewed Android Wi-Fi contract `to-verify` unless the selected
  artifact, current docs, and target run establish it;
- bound frame/audio queues, define drop/coalesce/backpressure and stop order,
  preserve session epochs, and reject stale events;
- treat thermal, battery, peak-power, doff/fold, background, timeout, route,
  and permission failures as typed fallbacks with one bounded recovery;
- classify raw-data processing as glasses-native, phone-local, remote, mixed, or
  unknown separately from transport;
- return `TRN-SOURCE-01`, `TRN-CONFIG-01`, `TRN-LINK-01`, `TRN-AUDIO-01`,
  `TRN-STREAM-01`, `TRN-THERMAL-01`, `TRN-RECOVERY-01`, `TRN-PHYSICAL-01`, and
  `TRN-RELEASE-01`, leaving unobserved Wi-Fi parity, Gen 3, and physical audio
  behavior `to-verify`.

## Security-and-attestation fixture

Input: “Configure a private iOS and Android DAT build for a Ray-Ban Display
app, keep Developer Mode working, prepare a release channel, and make sure no
Meta credentials or callback data leak while we call the feature on-device.”

Expected result:

- freeze the platform identity tuple: bundle/package/application ID, callback
  scheme, selected DAT package/artifact, project/platform app, build variant,
  mode/channel, target device, phone OS, companion version, and firmware;
- distinguish iOS `AppLinkURLScheme`/`MetaAppID`/`ClientToken`/`TeamID` from
  Android `APPLICATION_ID`/`CLIENT_TOKEN`, GitHub Packages access, signing, and
  the hosted Web App origin; do not copy one platform's recipe to the other;
- inspect key presence and build/variant alignment with values redacted, keep
  package/client/signing secrets in the approved environment, and scan logs,
  fixtures, screenshots, archives, source maps, and generated output for
  credentials, raw callback URLs, account identifiers, and device identifiers;
- validate owned callback scheme/host, malformed/unexpected/stale/duplicate
  behavior, SDK handoff, and terminal state without logging the payload;
- keep Developer Mode placeholder/registration evidence separate from release
  attestation, signed distribution, tester/channel state, physical capability,
  App Store/Play review, and on-device processing;
- route processing location, network/storage, consent, retention, and deletion
  to the privacy/on-device roles, and keep “Gen 3” `to-verify` without aliasing a
  product label or enum;
- return `SEC-SOURCE-01`, `SEC-STATIC-01`, `SEC-CREDENTIAL-01`,
  `SEC-CALLBACK-01`, `SEC-ATTEST-01`, `SEC-DEVMODE-01`, `SEC-CHANNEL-01`,
  `SEC-PHYSICAL-01`, and `SEC-RELEASE-01`, leaving account, secret validity,
  signing, physical, review, and production outcomes unobserved when they were
  not actually run.

## Sources

- [Meta Wearables Device Access Toolkit announcement](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/)
- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Full SDK capability and source-conflict matrix](../../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md)
- [Device-generation and runtime-support matrix](../../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
- [On-device compliance and runtime contract](../../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md)
- [Security, attestation, and credential-boundaries route](../../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md)
- [Meta Wearables Web App repository](https://github.com/facebook/meta-wearables-webapp)
- [Apple AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)

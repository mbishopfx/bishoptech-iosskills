# Transport, audio, and runtime reliability

Transport is part of the product contract, not an implementation detail. A
Meta Wearables feature can traverse Bluetooth control/registration, Wi-Fi or
local-network media, HFP microphone input, A2DP output, the phone process, and
an Internet service. These hops must be named independently before a team
claims “on-device,” low latency, camera, audio, Display, or reliable support.

This route was added after a fresh review of the DAT 0.9 sources. The iOS 0.8
changelog explicitly adds Wi-Fi transport and the current iOS integration guide
shows local-network disclosure/Bonjour configuration for Wi-Fi camera/display
paths. The reviewed Android 0.9 changelog and setup establish Bluetooth,
Internet, session, camera, and Display surfaces but do not establish the same
Wi-Fi contract. Treat cross-platform Wi-Fi parity as `to-verify` until the
resolved artifact, current docs, and named target agree.

## Transport map

```text
user intent
   -> Meta AI registration/permission
   -> Bluetooth control and device selection
   -> session negotiation
   -> capability transport
        camera/display: Bluetooth or target-specific Wi-Fi/local network
        microphone: HFP, 8 kHz mono in the public guide
        playback: A2DP
   -> bounded phone consumer / native Display presenter
   -> local or remote processing (separate claim)
   -> stop, disconnect, thermal, power, or fallback
```

| Hop | iOS source signal | Android source signal | Proof boundary |
| --- | --- | --- | --- |
| Bluetooth/control | Bluetooth usage/background configuration and DAT registration/session route | Bluetooth permissions, callback, app metadata, and DAT session route | A connected or registered device is not camera, Display, HFP, or Wi-Fi proof. |
| Wi-Fi/local-network media | DAT 0.8 adds Wi-Fi transport; current setup calls for `NSLocalNetworkUsageDescription` and Bonjour configuration for camera/display streaming | 0.9 public setup/changelog does not expose an equivalent explicit contract; `INTERNET` is not enough to claim DAT Wi-Fi | Resolve exact artifact/API and run negotiation plus sustained workload on the named target. |
| HFP microphone | Platform audio route; public reference documents 8 kHz mono glasses input | Platform audio route; exact artifact/device route remains target-specific | Phone mic and remote transcription are different claims. |
| A2DP playback | Bluetooth output route | Bluetooth output route | Playback does not prove microphone input or speaker quality. |
| Web App network | Hosted HTTPS/Display Web App route | Hosted HTTPS/Display Web App route | Browser/Web App network behavior is not native DAT transport. |

## iOS configuration contract

The current official integration route exposes transport-sensitive target
configuration. Inspect the selected package and target rather than copying a
snippet blindly:

- Bluetooth usage disclosure and `bluetooth-central` background mode for the
  required companion behavior;
- `NSLocalNetworkUsageDescription` when the selected Wi-Fi camera/display path
  requires local-network access;
- the documented Bonjour service entry for automatic discovery;
- callback URL scheme, DAT app identity, and signing metadata as a separate
  registration/attestation contract;
- `AVAudioSession` category/mode/route policy for HFP and A2DP, with route
  settlement and interruption handling.

The presence of these keys is static evidence only. Record whether local
network permission was granted, which link was negotiated, what capability was
started, and whether the stream stayed usable after route change/background,
doff/fold, or thermal events.

## Android configuration contract

The public Android setup route documents Bluetooth permissions, `INTERNET`, an
intent callback, and `APPLICATION_ID`/`CLIENT_TOKEN` metadata. Use local
properties or environment-backed placeholders for credentials. The exact
resolved 0.9 artifact/API reference owns any additional transport behavior.

Do not infer Android Wi-Fi parity from iOS `Info.plist`, a broad Internet
permission, a sample name, or a Kotlin symbol. Mark the route
`source-conflict`/`to-verify` until the selected artifact and target prove it.
Keep Android runtime permission results, link state, session state, and audio
route in separate fields.

## Reliability state machine

```text
unconfigured -> permission/account -> registering -> link-negotiating
    -> session-started -> capability-started -> consuming
    -> paused / route-changed / doffed / backgrounded
    -> resumed or stopping -> stopped
```

At every transition:

1. preserve the session/capability epoch;
2. cancel or drain work according to the ownership contract;
3. keep frame/audio queues bounded and record the drop/coalesce policy;
4. reject stale events from a previous session;
5. surface a useful phone fallback or explicit unavailable state;
6. stop automatic retries for thermal, battery, peak-power, unknown-protocol,
   or repeated transport failures.

## Camera and Display over a variable link

Start with the smallest resolution/frame rate/codec that serves the user task.
Requested configuration is not observed configuration: record actual frame
dimensions, codec, rate, drops, latency category, thermal/battery state, and
stop latency. The camera resource owns its child stream in DAT 0.9; stop the
stream/preview, then camera, then session, while cancelling consumers and
closing files.

For native Display, capability-gate the session, keep content compact, model
tap/button input as events, and clear/stop on disconnect. For a Web App, keep
600x600 layout, public HTTPS, browser-simulator, and physical Display evidence
separate. Neither native Display nor Web App evidence closes the Android Wi-Fi
parity question.

## Audio route contract

- HFP is the documented glasses microphone path and is described as 8 kHz
  mono; verify route settlement and actual input on the target.
- A2DP is the documented output path; verify interruption, volume, output
  selection, and restoration independently.
- A phone microphone, mock audio, a transcript, or an A2DP-only test must be
  labeled as that exact thing.
- Camera + HFP is a combined workload: define ordering, consent, buffering,
  interruption, route changes, and teardown before implementing it.
- Remote transcription or inference must be labeled `remote`/`mixed` and
  disclosed; the transport path does not make it glasses-native.

## Failure and fallback matrix

| First failure | Class | Bounded response | User-visible fallback |
| --- | --- | --- | --- |
| Permission or local-network denial | configuration/consent | Explain purpose, request once, record denial, do not loop | Phone-only or manual flow |
| Bluetooth/control unavailable | transport | Verify power/fold/wear/companion/link tuple, then one documented recovery | Phone-first state |
| Wi-Fi negotiation or sustained stream failure | transport/source parity | Preserve the first error; stop the workload; verify artifact/docs before changing config | Lower-bandwidth confirmed route or phone fallback |
| HFP route absent | audio route | Stop capture, restore prior route, do not substitute phone mic silently | Text/manual or explicit phone-mic choice |
| Queue growth/drops | backpressure | Bound queue, reduce workload, record policy and observed drops | Lower quality/rate or phone processing |
| Thermal/battery/peak power | safety | Stop workload and wait for safe deliberate restart | Status plus non-wearable fallback |
| Doff/fold/background/disconnect | lifecycle | Pause/stop according to SDK state, reject stale events, release resources | Resume prompt or phone state |

## Evidence packet

Use the companion [transport contract](../skills/packages/meta-wearables-transport-reliability/references/transport-contract.md) and add these rows to the shared [device/release evidence packet](12-device-and-release-evidence-packet.md):

| ID | Level | Operation | Claim supported |
| --- | --- | --- | --- |
| `TRN-SOURCE-01` | source/access-gated | Freeze iOS/Android transport sources, MCP lookup, and date. | Known source snapshot. |
| `TRN-CONFIG-01` | static/build | Inspect target keys, permissions, artifact, audio policy, and privacy disclosures. | Declared route is configured. |
| `TRN-LINK-01` | connected/physical | Observe registration, link negotiation, timeout, reconnect, and route change. | Named link behavior. |
| `TRN-AUDIO-01` | physical | Exercise HFP and A2DP independently with route/sample/restore fields. | Named physical audio path. |
| `TRN-STREAM-01` | physical | Run bounded camera/Display workload, stop, disconnect, and recover. | Named transport/capability reliability. |
| `TRN-THERMAL-01` | physical | Observe thermal, battery, peak-power, doff/fold, and terminal stop. | Safety behavior for that workload. |
| `TRN-RECOVERY-01` | connected/physical | Apply one documented recovery and repeat the original operation. | Attempted versus observed recovery. |
| `TRN-PHYSICAL-01` | physical | Repeat on exact model, firmware, companion, build, and mode/channel. | Exact target only. |
| `TRN-RELEASE-01` | signed/release-channel | Repeat critical transport/fallback flow from the signed channel. | Release-channel evidence. |

No source, compile, mock, browser, or phone-only result closes the physical
rows. No transport result closes a Gen 3 mapping or proves a processing
location without a separate data-flow observation.

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [DAT iOS repository/setup](https://github.com/facebook/meta-wearables-dat-ios#readme)
- [DAT Android repository/setup](https://github.com/facebook/meta-wearables-dat-android#readme)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Apple AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Apple local network privacy](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Apple Network framework](https://developer.apple.com/documentation/network)
- [Android Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions)

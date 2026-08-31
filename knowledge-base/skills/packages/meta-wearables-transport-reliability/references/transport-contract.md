# Transport and reliability contract

Use this contract for every transport-sensitive Meta Wearables task. A field
may be `source`, `static`, `compile`, `mock`, `connected`, `physical`,
`access-gated`, `source-conflict`, `to-verify`, or `not-run`; never fill it with
an adjacent platform or product label.

## Required identity

| Field | Required value |
| --- | --- |
| `platform` | iOS, Android, Web App, or phone fallback |
| `dat_revision` | Exact package/artifact tag and resolved revision |
| `device_identity` | Consumer label plus observed runtime/model identity |
| `companion_firmware_tuple` | Meta AI version, glasses firmware, on-glasses DAT-app version/state |
| `mode_channel` | Developer Mode, release channel, or unknown |
| `transport_hops` | Bluetooth control, Wi-Fi/local network, HFP, A2DP, Internet, or unknown |
| `processing_location` | glasses-native, phone-local, remote, mixed, or unknown |
| `capability` | Camera, photo, Display, input, HFP, A2DP, or combined workload |
| `first_failure` | Ordered first error/state, or `not-run` |
| `recovery` | Attempted action, post-action state, and whether the original operation recovered |

## Platform configuration matrix

| Surface | Source-supported signal | Keep separate |
| --- | --- | --- |
| iOS Bluetooth/control | Bluetooth usage and `bluetooth-central` background configuration appear in the official integration route. | Registration callback, link state, and physical camera/Display capability. |
| iOS Wi-Fi/local network | DAT 0.8 changelog adds Wi-Fi transport; the current guide calls for local-network disclosure and Bonjour configuration for Wi-Fi camera/display paths. | A source key is not a successful Wi-Fi negotiation or sustained stream. |
| Android Bluetooth/control | Official setup uses Bluetooth permissions, including `BLUETOOTH` and `BLUETOOTH_CONNECT`, plus callback and app metadata. | Android Wi-Fi parity; `INTERNET` alone is not a DAT Wi-Fi capability claim. |
| Android Wi-Fi/local network | The reviewed 0.9 changelog/setup does not establish an iOS-equivalent Wi-Fi transport contract. | Mark `source-conflict`/`to-verify` until the resolved artifact, docs, and target run agree. |
| HFP microphone | Full reference documents glasses microphone input through HFP as 8 kHz mono. | Phone microphone, A2DP playback, and remote transcription. |
| A2DP output | Full reference documents Bluetooth audio output through A2DP. | Speaker/latency/physical quality and HFP input. |
| Web App network | Hosted HTTPS and browser-simulator behavior are separate Web App concerns. | Native DAT transport and Web App physical delivery. |

## Evidence IDs

| ID | Operation | Required evidence | Does not prove |
| --- | --- | --- | --- |
| `TRN-SOURCE-01` | Freeze iOS/Android changelogs, full reference, MCP lookup, and date. | Current transport source snapshot. | Package compile or hardware behavior. |
| `TRN-CONFIG-01` | Inspect iOS keys/Bonjour/audio target and Android Manifest/permissions/artifact. | Target configuration and declared route. | Successful negotiation or processing location. |
| `TRN-LINK-01` | Observe registration, Bluetooth/link state, Wi-Fi/local-network negotiation, timeout, and reconnect. | Named connected link behavior. | Camera/Display/audio capability. |
| `TRN-AUDIO-01` | Exercise HFP input and A2DP output independently; record route/sample format/restore. | Named physical audio route. | Phone mic, remote speech, or another model. |
| `TRN-STREAM-01` | Run camera/Display workload with bounded queue, drop policy, stop, and route change. | Stream reliability and resource cleanup. | Long-term battery/thermal safety without a duration-tested run. |
| `TRN-THERMAL-01` | Observe battery, thermal, peak-power, doff/fold, pause, and terminal stop behavior. | Safety fallback for the named workload. | Other hardware or generation behavior. |
| `TRN-RECOVERY-01` | Apply one least-invasive transport recovery and repeat the same operation. | Attempted versus observed recovery. | An unobserved retry or documentation step. |
| `TRN-PHYSICAL-01` | Repeat the named transport/capability script on exact glasses, firmware, companion, and app build. | Physical route for that target. | Gen-wide or release-wide support. |
| `TRN-RELEASE-01` | Repeat critical transport and fallback flow from the signed release channel. | Release-channel transport evidence. | App Store/Play approval or production behavior. |

## Failure classification

```text
configuration -> account/channel -> companion -> firmware/DAT-app
    -> Bluetooth/control -> Wi-Fi/local-network -> permission/audio route
    -> session/lifecycle -> queue/backpressure -> thermal/power
    -> SDK/API/source conflict -> unknown
```

Record only the first observed failure, then apply one bounded recovery. A
later successful retry must not erase the original state or convert an
unverified route into a supported one.

## Privacy and on-device fields

For each hop record whether raw camera/audio leaves the glasses, phone, or app;
whether inference is local or remote; what is retained; what is deleted; and
what the user sees. A Bluetooth or Wi-Fi hop describes transport, not the
location of inference. Redact SSIDs, device identifiers, tokens, raw media,
and account identifiers from the evidence packet.

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT iOS integration guide](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Apple AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Apple local network privacy](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Android Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions)

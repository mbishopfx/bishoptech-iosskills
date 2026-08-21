# External Accessory MFi proof matrix

External Accessory crosses manufacturer authorization, protocol declaration, connected-accessory state, EASession streams, MFi Wi-Fi configuration, platform limits, physical device behavior, and release configuration. Verify each layer separately.

## Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, app/extension targets, target membership |
| SDK/deployment | Xcode, SDK, iOS/iPadOS target, Mac Catalyst or Mac-on-Apple-silicon target |
| Manufacturer | MFi partner, accessory model, firmware, protocol document |
| Protocol | Reverse-DNS string, version, framing, authentication, max frame |
| Info.plist | UISupportedExternalAccessoryProtocols value |
| Entitlement | Wireless Accessory Configuration signed entitlement, if used |
| Background | external-accessory mode, user-started feature, lock/background state |
| Device | Physical iPhone/iPad, connector/wireless path, OS build |
| Accessory | Serial/test ID, firmware, authentication state, physical setup |
| Session | EASession state, protocolString, stream status, run loop |
| Evidence | Framed input/output, acknowledgement, domain result, freshness |
| Privacy | Metadata/raw stream redaction, retention, deletion |
| Accessibility | VoiceOver, Dynamic Type, Voice Control, Switch Control, reduced effects |
| Artifact | Signed build, App Store/MFi configuration, release notes |

Use manufacturer-approved or synthetic test fixtures. Do not put serial numbers, raw stream payloads, or room/device names in shared screenshots or logs.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| External Accessory is the correct route | Manufacturer protocol and transport record | A connector or Bluetooth symbol |
| App declares a supported protocol | Signed UISupportedExternalAccessoryProtocols | An Info.plist source file |
| Accessory is connected | Physical accessory and current manager inventory | Cached accessory object |
| Protocol is currently supported | Runtime protocolStrings includes the intended value | Model number alone |
| Session opens | EASession created for selected pair | Accessory connected |
| Streams are usable | Open/status, scheduled delegates, read/write events | Session object is nonnil |
| Framing is correct | Partial, malformed, oversized, duplicate, and real-fixture tests | One string read |
| Command is accepted | Protocol/device acknowledgement with request ID | OutputStream accepted bytes |
| Physical operation completed | Device-reported domain result or measurement | Transport callback |
| Wi-Fi configuration is allowed | Signed entitlement and target configuration | Capability name in Xcode |
| Wi-Fi setup works | Physical accessory, system UI, status callback, post-config protocol check | Sheet dismissal |
| Background works | Configured target, physical lock/background run, stream evidence | UIBackgroundModes source |
| Mac-on-Apple-silicon behavior | Explicit unsupported connection record | Successful framework import |
| AI stays bounded | Typed proposal, validator, redacted input, no arbitrary frames | Generated explanation |
| Release ready | Final signed artifact, manufacturer/MFi state, physical/system proof | Debug or simulator run |

## Connected accessory scenarios

- [ ] No connected accessories.
- [ ] One connected accessory with compatible protocol.
- [ ] Multiple accessories with duplicate names.
- [ ] Accessory connected but protocolStrings is empty.
- [ ] Accessory connected with unsupported protocol.
- [ ] Accessory disconnect notification is delivered after registration.
- [ ] Accessory reconnects with a changed firmware revision.
- [ ] connectedAccessories is refreshed rather than cached as permanent state.
- [ ] Person selects an accessory before session creation.
- [ ] EASession init returns nil.
- [ ] EASession protocolString matches the selected protocol.
- [ ] Input and output streams open.
- [ ] Input stream reports partial, complete, malformed, and oversized frames.
- [ ] Output stream reports no space, partial write, error, and close.
- [ ] Accessory disconnects during an active write.
- [ ] Session teardown removes delegates and closes streams.
- [ ] Duplicate and stale request IDs are rejected.

## Wi-Fi accessory configuration scenarios

- [ ] Wireless Accessory Configuration capability is signed.
- [ ] Browser is created with the intended delegate queue.
- [ ] Search starts only from explicit user setup.
- [ ] Search filter matches the intended accessory family.
- [ ] No result, Wi-Fi unavailable, and browser stopped states are visible.
- [ ] Desired accessory is found and search stops immediately.
- [ ] Person selects the desired accessory.
- [ ] System-provided configuration UI appears.
- [ ] Configuration succeeds.
- [ ] Person cancels configuration.
- [ ] Configuration fails.
- [ ] Connected-accessory inventory is re-read after configuration.
- [ ] protocolStrings is checked before EASession.
- [ ] Entitlement missing/invalid path fails safely.

## Background and platform scenarios

| Scenario | Expected evidence |
| --- | --- |
| Foreground direct iPhone | Session, stream, framing, result |
| Foreground direct iPad | Session and accessory compatibility |
| external-accessory background mode | Lock/background stream behavior in named target |
| Device lock/protected data | Privacy-safe status and recovery |
| Process termination | Relaunch/reconnect behavior if product claims it |
| Accessory disconnect | Stale state and durable result policy |
| iPhone/iPad app on Mac with Apple silicon | Connection is documented as unsupported |
| App without Wi-Fi entitlement | Configuration route unavailable, no misleading success |

Record exact OS build, accessory firmware, connector/wireless path, timing, and whether the app was terminated. Simulator and Mac-on-Apple-silicon runs are not external accessory proof.

## Privacy, AI, and side-effect checks

- [ ] Manufacturer, model, serial, firmware, protocol strings, and raw stream bytes are redacted from logs.
- [ ] App-owned accessory record has a delete/forget path.
- [ ] AI prompt contains approved typed context only.
- [ ] AI proposal maps to an allowlisted protocol operation.
- [ ] Confirmation appears before consequential commands.
- [ ] Request ID/replay and timeout behavior are tested.
- [ ] Transport acknowledgement is not labeled physical success.
- [ ] Device-reported result is fresh and tied to the selected accessory.
- [ ] Widgets, notifications, and Live Activities do not expose sensitive accessory data by default.
- [ ] External model upload is blocked or explicitly governed.

## Accessibility matrix

- [ ] VoiceOver reads accessory name, protocol state, session state, freshness, and result.
- [ ] Async connection/configuration returns focus to a useful summary.
- [ ] Dynamic Type preserves Configure, Confirm, Stop, Retry, Forget, and Close.
- [ ] Voice Control distinguishes duplicate accessory names.
- [ ] Switch Control reaches all setup, control, and recovery actions.
- [ ] Reduce Motion preserves searching/configuring meaning.
- [ ] Reduce Transparency and increased contrast preserve stale/error/ready states.
- [ ] RTL, localization, long names, and error strings work.
- [ ] Keyboard/pointer focus and non-gesture alternatives work where supported.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| connected | System reports an accessory in the current inventory |
| compatible | Runtime protocol list contains the app-supported protocol |
| authenticated | Accessory/device protocol gate passed as defined by the manufacturer |
| session-open | EASession exists for the selected accessory/protocol |
| stream-ready | Required streams opened and can deliver/accept events |
| framed | App codec validated a complete message |
| acknowledged | Transport or protocol acknowledgement; specify which |
| completed | Domain/physical result was observed |
| configured | Wi-Fi system configuration returned success and the next protocol check passed |
| stale | Last confirmed data is outside the product’s freshness boundary |
| unknown | The app cannot prove the physical or domain result |

## Sources

- [External Accessory](https://developer.apple.com/documentation/externalaccessory)
- [EAAccessoryManager](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager)
- [EAAccessory](https://developer.apple.com/documentation/externalaccessory/eaaccessory)
- [EASession](https://developer.apple.com/documentation/externalaccessory/easession)
- [EAAccessory protocol strings](https://developer.apple.com/documentation/externalaccessory/eaaccessory/protocolstrings)
- [EASession initialization](https://developer.apple.com/documentation/externalaccessory/easession/init%28accessory%3Aforprotocol%3A%29)
- [EASession input stream](https://developer.apple.com/documentation/externalaccessory/easession/inputstream)
- [EASession output stream](https://developer.apple.com/documentation/externalaccessory/easession/outputstream)
- [Connected accessories](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/connectedaccessories)
- [Register for local accessory notifications](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/registerforlocalnotifications%28%29)
- [Supported external accessory protocols](https://developer.apple.com/documentation/bundleresources/information-property-list/uisupportedexternalaccessoryprotocols)
- [Wireless Accessory Configuration Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.external-accessory.wireless-configuration)
- [EAWiFiUnconfiguredAccessoryBrowser](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser)
- [Start searching for unconfigured accessories](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/startsearchingforunconfiguredaccessories%28matching%3A%29)
- [Stop searching for unconfigured accessories](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/stopsearchingforunconfiguredaccessories%28%29)
- [Configure an unconfigured accessory](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/configureaccessory%28_%3Awithconfigurationuion%3A%29)
- [Configuration status](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessoryconfigurationstatus)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

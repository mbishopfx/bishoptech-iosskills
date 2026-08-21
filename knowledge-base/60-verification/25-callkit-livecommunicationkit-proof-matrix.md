# CallKit, LiveCommunicationKit, and VoIP proof matrix

Use this matrix to separate a call-state fixture from a real system call, a PushKit registration from incoming delivery, and a configured entitlement from a user-selected default calling/dialer role. Record the SDK, deployment target, OS build, device model, account, region, carrier, provider/server, APNs environment, audio route, and exact user actions.

## Evidence levels

| Level | Can prove | Cannot prove by itself |
| --- | --- | --- |
| Documentation | API roles, required system boundaries, entitlement names, and regional/device caveats | Target provisioning, APNs delivery, system UI, provider quality |
| Source/compile | State model, target imports, action types, delegate signatures, and availability branches | Incoming call delivery, system acceptance, audio hardware, real media |
| Preview/UI test | App-owned dialer/in-call states, accessibility, fallback, and redaction | Phone-like system UI, PushKit, default-app settings, remote connection |
| Simulator | App-owned flow, some CallKit action seams, fixture audio state | Reliable VoIP push delivery, cellular/default dialer route, physical audio/Bluetooth |
| Signed physical device | Selected CallKit/LCK UI, target entitlement, audio route, lock-screen behavior | All regions/carriers/devices, APNs reliability, provider/backend correctness |
| Controlled APNs/provider | Token registration, incoming invitation, server reconciliation, and provider outcome for tested device | Universal background timing, App Store review, all network/account states |
| Default-role test | User-selected calling/dialer behavior in the required OS/device/region | Eligibility or behavior for every account, region, or future OS |
| Production call | Observed provider/media result for the tested account/device | Universal uptime, privacy compliance, or future system policy |

## Target and entitlement matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| CallKit import/availability | Build the named target with selected SDK and deployment target | Wrong platform/target, unavailable symbol, outdated signature | The selected target can compile the chosen CallKit route |
| LiveCommunicationKit import/availability | Build the named target with the selected SDK | Preliminary/availability-sensitive API, wrong target | The selected target can compile the chosen LCK route |
| Push Notifications capability | Inspect built entitlements and developer account | APS environment absent, wrong App ID, development-only configuration | The artifact is provisioned for the tested push environment |
| VoIP push use | Source policy and route review | PushKit used for generic background work | The product uses the specialized push type for a real call route |
| Calling-app entitlement | Built entitlements and current developer configuration | Missing or unapproved entitlement, wrong role | The artifact carries the selected calling-app configuration |
| Default Dialer App entitlement | Built entitlements, account/region/device prerequisites | EU requirement not met, wrong device location, unsupported route | The tested artifact is configured for the selected default-dialer experiment |
| App/server identity | Redacted token registration and account mapping | Token or account ID exposed in logs, stale device mapping | The selected device/account route is registered |
| Microphone permission | Physical permission grant/deny/settings change | Missing usage string, denial hidden, permission assumed | The app handles the tested permission state |

## PushKit and APNs matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Registry creation at launch | Background/foreground launch trace | Registry created too late, delegate nil, desired types set first | Registry was configured on the tested launch path |
| VoIP token update | PKPushRegistry delegate, environment, server registration | Token stale, environment mismatch, token logged | The server has the tested opaque token mapping |
| APNs request | Provider/server trace with correct topic/push type/expiry | Wrong topic, expired invitation, malformed payload | APNs accepted the tested request |
| Device delivery | Signed physical device receives push callback | Simulator/local notification used as substitute | Delivery occurred for the tested device/account |
| Payload privacy | Redacted payload and server schema | Transcript, secret, or excessive contact data included | Payload is minimized for the selected route |
| Duplicate invitation | Same call ID/UUID sent twice | Two system calls, non-idempotent server state | Duplicate handling works for the tested identifier |
| Expired invitation | Short expiry/late-delivery fixture | Stale call reported after end | Expired calls are reconciled without a false UI |
| Missing/invalid token | APNs error and server token cleanup | Invalid token retried forever | Token lifecycle handles the tested failure |
| CallKit handoff | Push callback to reportNewIncomingCall trace | Local notification, private imitation, delayed report | The system report was attempted for the tested call |

## CallKit incoming and outgoing matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Provider configuration | CXProviderConfiguration and built resource review | Wrong icon/ringtone, unsupported capability | Selected native call UI configuration is present |
| Provider delegate queue | Serialized delegate trace | Reentrancy, UI mutation off main actor, action loss | Actions are handled on the selected isolation path |
| Incoming update | CXCallUpdate fields and system report | Wrong caller, missing handle, fake connected state | Incoming report used the tested identity/capabilities |
| Report acceptance | Physical system UI or documented error result | Blocked/Focus/error ignored | The system allowed/disallowed the observed report |
| Answer action | CXAnswerCallAction trace to media connection | Action fulfilled before service ready, timeout | Answer behavior works for selected provider/device |
| Start action | CXStartCallAction in CXTransaction and provider trace | Button connects separately, duplicate transaction | Outgoing start uses the system action path |
| End action | CXEndCallAction and provider/server teardown | Call remains active, audio not stopped | End action stops the tested call path |
| Hold/mute/group/DTMF | Action-specific provider trace | UI toggles without media/service result | Each tested action is fulfilled or failed correctly |
| Call progress | reportOutgoingCall connecting/connected trace | Connected label before media | Observed progress is reported for the selected call |
| Call update | CXCallUpdate changed caller/video/capability state | Stale display, private data leaked | System update reflects the tested change |
| End reason | reportCall ended with reason and server record | Generic end for provider failure or timeout | The observed end reason is reconciled |
| Provider reset | providerDidReset and call-store cleanup | Orphaned calls, active audio, stale UI | Reset recovery works for the tested process |

## LiveCommunicationKit matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| ConversationManager start/reset | Delegate begin/reset trace | Manager reused after reset, pending actions lost | Manager lifecycle works for the selected target |
| Conversation action | Action UUID, timeoutDate, perform, fulfill/fail trace | Timeout ignored, action fulfilled early | Tested action reaches the documented terminal state |
| Incoming conversation | reportNewIncomingConversation or documented PushKit handoff | Unsupported signature, stale invitation | System incoming conversation route was observed |
| Conversation events | Started connecting, connected, updated, ended event trace | Local state only, missing end reason | Reported events match selected service state |
| Audio activation | didActivate/didDeactivate delegate trace | Media starts before activation, never stops | Audio handoff works for selected device |
| Active conversations | conversations and pendingActions reconciliation | Stale list, duplicate conversation | Manager state is reconciled after process events |
| VoIP default calling role | Entitlement, system selection, incoming/outgoing VoIP call | Framework present but not selected | Default calling behavior was observed after user choice |
| Cellular fallback | Documented fallback action/URL and real call result | VoIP failure leaves dead UI, fallback assumed | Fallback works for tested region/device/account |
| Default dialer | Entitlement, EU account/device prerequisite, Settings choice, cellular call | Non-EU test, missing entitlement, no user selection | Default dialer behavior is proven only for recorded conditions |
| Conversation history | Role/entitlement and current-history observation | App reads history as a normal caller | History access is evidenced under the selected role |

## Audio and media matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Category/mode/options | Source and runtime audio-session log | Wrong category, Bluetooth option unsupported | Configuration was applied on tested hardware |
| Activation | System manager/provider activation to AVAudioSession trace | Audio starts from view appear, activation race | Media starts after the selected activation event |
| Interruption | Incoming system call, alarm, route loss, and resume test | Audio continues over interruption, duplicate engine | Interruption recovery works for selected device |
| Route change | Receiver/speaker/wired/Bluetooth route sequence | UI says speaker while receiver active | Observed route is reflected in app state |
| Microphone denial | Permission denied/changed in Settings | Call claims connected with no input | Denied input state is handled visibly |
| Media failure | Provider connected but media unavailable fixture | False connected, no retry/end path | Media failure is separate from call authorization |
| Teardown | End/reset/background/suspension trace | Audio session stays active, capture leak | Audio is torn down for selected terminal states |

## Privacy, accessibility, and communication design matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Contact/handle data | Data-flow review and redacted logs | Recipient data in analytics/payloads without need | Selected contact scope is minimized |
| Notification content | Locked-device preview and hidden-preview test | Transcript/token/private link exposed | Tested notification follows privacy policy |
| Focus behavior | Focus/Do Not Disturb/notification setting run | Low-priority call bypasses policy | Observed system behavior is recorded |
| VoiceOver | Answer, end, mute, speaker, hold, error, and reconnect tasks | State only color/motion, focus lost after system handoff | Selected call task is accessible |
| Dynamic Type/localization | Large text and long names/handles | End action clipped, caller name truncated incorrectly | App-owned surfaces adapt for tested locales |
| Reduced effects | Reduce Motion/transparency/high contrast | Glass hides connected/media state | Fallback keeps state and actions clear |
| Alternate input | Voice Control, Switch Control, keyboard/pointer where supported | Essential action requires precise gesture | Selected input paths complete the task |
| AI consent | Audio/transcript consent and retention fixture | AI processes private audio silently | Model input scope and consent are recorded |

## AI and system-action matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Contact proposal | Ambiguous names/handles and typed validation | Model selects wrong recipient | Model proposes a candidate only |
| Call-method proposal | VoIP/cellular/default role fixture | Model bypasses required system choice | Method is reviewed and validated |
| Call action | User review to CallKit/LCK request trace | Auto-dial, duplicate action | Side effect follows the tested user/system path |
| Transcript/summary | Consent, local processing, provenance, edit/save trace | Summary claimed as transcript truth | Generated output is a reviewable proposal |
| No-model fallback | Model unavailable/canceled fixture | Calling blocked by AI | Manual route remains usable |

## Required evidence packet

- SDK, deployment target, OS build, device model, account, region, and carrier.
- Built entitlements, provisioning profile, usage descriptions, and target membership.
- PushKit token/environment registration and redacted APNs/provider trace.
- Call UUID, server call ID, invitation expiry, and idempotence record.
- CallKit/LCK system-surface recording or screenshots for incoming/outgoing actions.
- Provider delegate or ConversationManager action timeline with fulfill/fail/timeout.
- Audio-session activation, route, interruption, microphone, and teardown logs.
- Default calling/dialer system selection evidence where applicable.
- Accessibility settings, localization, locked-device, Focus, and reduced-effects observations.
- AI proposal, consent, validation, user review, and final call/record action.

## Claim language

Use bounded language:

- “The system call UI appeared on the tested device after a valid VoIP push.”
- “The provider fulfilled the answer action after the media service connected.”
- “The app was selected as the default calling app in the tested system/device configuration.”
- “The default-dialer route was exercised under the required EU account/device conditions.”
- “The model proposed a recipient and the user confirmed it.”

Avoid “VoIP works,” “the app is a default dialer,” “calls always arrive,” or “AI made the call” without the corresponding evidence packet.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXProviderConfiguration](https://developer.apple.com/documentation/callkit/cxproviderconfiguration)
- [CXProviderDelegate](https://developer.apple.com/documentation/callkit/cxproviderdelegate)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [CXTransaction](https://developer.apple.com/documentation/callkit/cxtransaction)
- [CXCallAction](https://developer.apple.com/documentation/callkit/cxcallaction)
- [CXCallUpdate](https://developer.apple.com/documentation/callkit/cxcallupdate)
- [CXStartCallAction](https://developer.apple.com/documentation/callkit/cxstartcallaction)
- [CXAnswerCallAction](https://developer.apple.com/documentation/callkit/cxanswercallaction)
- [CXEndCallAction](https://developer.apple.com/documentation/callkit/cxendcallaction)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [PKPushRegistry](https://developer.apple.com/documentation/pushkit/pkpushregistry)
- [Supporting PushKit Notifications in Your App](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManager](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
- [ConversationAction](https://developer.apple.com/documentation/livecommunicationkit/conversationaction)
- [StartConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startconversationaction)
- [Conversation.Event](https://developer.apple.com/documentation/livecommunicationkit/conversation/event)
- [Conversation.Update](https://developer.apple.com/documentation/livecommunicationkit/conversation/update)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Managing Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

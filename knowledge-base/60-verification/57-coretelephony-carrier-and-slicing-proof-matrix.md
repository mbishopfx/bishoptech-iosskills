# Core Telephony carrier and network-slicing proof matrix

Core Telephony is especially easy to overclaim. A radio-access value, restricted-state callback, slice object, or quick-switch state is evidence about one system signal; it is not proof of connectivity, speed, account identity, or successful work.

## Evidence levels

| Level | Establishes | Does not establish |
| --- | --- | --- |
| Source inspection | API lifecycle, deprecations, entitlements, beta markers, documented states | Selected target availability, carrier eligibility, physical service behavior |
| Compile | Imports, symbol availability, async/delegate signatures, target configuration | Real carrier, path, background launch, entitlement, or server behavior |
| Fixture/unit | Policy decisions, state transitions, offline fallback, idempotent handoff | Cellular hardware, carrier network, radio changes, actual route quality |
| Simulator | SwiftUI states, accessibility labels, localization, handoff UI | Carrier service, SIM/eSIM, network slice, radio registration, live device transition |
| Physical iPhone | Service/radio/policy observations, request behavior, device transition | Universal carrier/region coverage, production release readiness |
| Signed/TestFlight | Release configuration, privacy copy, entitlement and target behavior | Every carrier/device/OS combination |

## Route matrix

| Claim | Minimum evidence | Failure and recovery cases |
| --- | --- | --- |
| The app knows its cellular data policy | CTCellularData reports a named state and the UI updates after a policy change | restricted, unknown, notifier teardown, Wi-Fi still available |
| The app knows the active data service | CTTelephonyNetworkInfo returns a service identifier and delegate changes are reconciled | SIM/service swap, nil value, multiple services, stale snapshot |
| The app observes radio access technology | serviceCurrentRadioAccessTechnology is recorded per service on a physical iPhone | no registration, service change, value unavailable, misleading performance inference |
| A transfer adapts safely | Core Telephony signal, NWPathMonitor state, and actual URLSession result drive a deterministic policy | path changes mid-request, cellular restriction, server timeout, cached/offline fallback |
| A preferred network slice is available | CTSlicingManager reports the category in availableSliceAppCategories | missing entitlement, category unavailable, unsupported device/carrier, ENOTSUP |
| New connections use the preferred slice | Activation occurs before connection creation and activeSlices is observed | connection created too early, activation error, slice disappears, normal-route fallback |
| The app supports quick switch | Eligible physical devices produce active/passive/unknown state changes and app state handoff is resumable | background registration failure, passive device, unknown state, duplicate migration |
| The app provisions an eSIM | Eligible carrier target with entitlement completes support check and handles success/cancel/fail/unknown | non-carrier target, missing entitlement, unsupported hardware, region/plan failure |
| The app integrates cellular calls | Supported call-system behavior is tested through CallKit | deprecated CTCall/CTCallCenter assumptions, no call service, interruption |
| AI network help is safe | Fixed observation fixture produces a typed explanation/policy proposal and deterministic validation controls the action | stale state, prompt injection in labels, model unavailable, rejected policy |
| The native surface is accessible | Dynamic Type, VoiceOver, reduced motion, localization, offline, retry, pause, and cancel tasks pass | color-only status, network callback spam, unreadable long text, focus loss |
| Release readiness is claimed | Signed build on the target iPhone with entitlements, privacy copy, and route behavior recorded | TestFlight mismatch, entitlement change, carrier gap, OS availability gap |

## Environment record

For each run, record:

- app version/build, target, SDK/Xcode, and git revision;
- iPhone model and OS;
- SIM/eSIM/carrier/region conditions without storing unnecessary subscriber data;
- Wi-Fi and cellular state;
- observed Core Telephony values and timestamps;
- Network path and actual request result;
- entitlement and category evidence for slicing;
- quick-switch device and service state, if applicable;
- eSIM eligibility/entitlement, if applicable;
- logs, screenshots, signed artifact, and recovery result.

## Non-claims

Do not use these as shorthand:

- radio technology = speed;
- active slice = guaranteed latency;
- carrier identifier = user identity;
- unrestricted cellular = Internet reachability;
- quick-switch active = server session migrated;
- eSIM success callback = plan fully usable by every app;
- simulator state = physical carrier proof.

## Sources

- [Core Telephony](https://developer.apple.com/documentation/coretelephony)
- [CTTelephonyNetworkInfo](https://developer.apple.com/documentation/coretelephony/cttelephonynetworkinfo)
- [CTCellularData](https://developer.apple.com/documentation/coretelephony/ctcellulardata)
- [CTCellularDataRestrictedState](https://developer.apple.com/documentation/coretelephony/ctcellulardatarestrictedstate)
- [CTSlicingManager](https://developer.apple.com/documentation/coretelephony/ctslicingmanager)
- [CTSlicingManager.AppCategory](https://developer.apple.com/documentation/coretelephony/ctslicingmanager/appcategory)
- [CTSlicingManager.Slice](https://developer.apple.com/documentation/coretelephony/ctslicingmanager/slice)
- [iPhone quick switch](https://developer.apple.com/documentation/coretelephony/iphone-quick-switch)
- [CTCellularPlanProvisioning](https://developer.apple.com/documentation/coretelephony/ctcellularplanprovisioning)
- [Network](https://developer.apple.com/documentation/network)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

***

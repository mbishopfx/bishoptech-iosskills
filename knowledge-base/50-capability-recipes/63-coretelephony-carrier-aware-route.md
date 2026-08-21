# Core Telephony carrier-aware capability route

Use this route when an app needs to adapt transfers, continuity, or network behavior to current cellular policy and service state. Select only the subroute the target is eligible to use.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Continue offline, adapt a transfer, request a supported preferred route, or hand off active-device state |
| Observations | CTTelephonyNetworkInfo, CTCellularData, CTSlicingManager, CTQuickSwitchManager |
| Adjacent proof | NWPathMonitor/Network, URLSession, server response, AVAudioSession or app feature state |
| Specialized route | CTCellularPlanProvisioning only for an eligible carrier app |
| Domain model | Immutable cellular observation, policy state, route request state, handoff state |
| UI | Transfer policy, route explanation, continuity sheet, recovery action |
| AI | Typed explanation or user-approved policy proposal only |
| Proof | Physical iPhone/carrier conditions, entitlement, service changes, signed release behavior |

## Step 1: Choose the narrowest subroute

### Resilient transfer

Use CTCellularData plus Network path and actual URLSession results to choose between transfer, cache, retry, or offline mode.

### Network slicing

Use CTSlicingManager when the selected target has the entitlement and the product needs a documented preferred category. Query availability before activation and activate before creating the connections that should use it.

### iPhone quick switch

Use CTQuickSwitchManager for eligible multi-iPhone service continuity. Define exactly which app credentials, local state, and server state move or become passive.

### Carrier eSIM

Use CTCellularPlanProvisioning only after the carrier target and entitlement are confirmed. For a general app, mark the route unavailable rather than building a speculative UI.

## Step 2: Define the observation model

Keep observations typed and time-stamped:

- data service identifier, if available;
- radio access technology per service, if available;
- cellular data restriction;
- network path interface and constraints;
- preferred slice category requested;
- available categories and active slices;
- quick-switch device/phone-number state;
- eSIM capability and provisioning result, only in the carrier target.

An observation is not a product decision. Derive a decision through deterministic policy so it can be tested with fixtures.

## Step 3: Start observation ownership

Create one service owner per feature scope. It should:

1. start CTTelephonyNetworkInfo delegate observation;
2. read CTCellularData and retain its notifier;
3. start NWPathMonitor on its own queue if path information is needed;
4. expose CTSlicingManager availability only when the route is enabled;
5. register quick-switch background events only after eligibility and handoff design are complete;
6. stop observation and unregister callbacks during teardown.

Do not place global observer ownership in a transient SwiftUI view.

## Step 4: Apply a deterministic transfer policy

Use a policy such as:

1. If the server operation is complete, show complete.
2. If the path is unavailable, keep a local retryable state.
3. If cellular data is restricted and Wi-Fi is absent, pause or offer a smaller local action.
4. If the path is available, attempt the request and observe the real response.
5. If the request fails, report the request error rather than blaming the radio technology.

This avoids the common error of treating “radio registered” as “request will succeed.”

## Step 5: Activate a network slice safely

The slice route should:

1. query availableSliceAppCategories;
2. verify the requested category;
3. show the user what the app is requesting;
4. call activatePreferredSliceForCategory;
5. create new network connections after activation;
6. observe activeSlices;
7. fall back to the normal route if unsupported or unavailable.

Existing connections may not change retroactively. Keep the order visible in logs and tests. Never call a category because an AI suggested it without checking availability and entitlement.

## Step 6: Handle quick-switch state changes

When CTQuickSwitchManager reports a transition:

- stop assuming the device is the active owner;
- checkpoint local work;
- obtain or refresh server-side session state;
- migrate only the artifacts the product is authorized to move;
- show active/passive/unknown state;
- restore normal work only after the app’s own session and server checks pass.

Background launch is a system opportunity, not a guarantee that every migration finishes. Make the handoff idempotent and resumable.

## Step 7: Project to native SwiftUI

Present:

- primary task state;
- policy/path reason;
- optional route details;
- one safe next action;
- offline/cache alternative;
- an AI explanation or proposal only when the user asks.

Use Liquid Glass for a compact inspector or review sheet. Keep the main task usable without the framework data.

## Step 8: Proof gates

Before release, verify the exact subroute:

- physical iPhone with the needed SIM/eSIM/carrier state;
- cellular restriction change and Wi-Fi fallback;
- radio/service change while the app is running;
- request result alongside Core Telephony observation;
- network-slice entitlement/category/activation order/active state;
- quick-switch active/passive/background transition and resumable handoff;
- carrier-only eSIM entitlement, if applicable;
- accessibility, localization, reduced motion, and offline states;
- signed target and release configuration.

## Sources

- [Core Telephony](https://developer.apple.com/documentation/coretelephony)
- [CTTelephonyNetworkInfo](https://developer.apple.com/documentation/coretelephony/cttelephonynetworkinfo)
- [CTCellularData](https://developer.apple.com/documentation/coretelephony/ctcellulardata)
- [CTSlicingManager](https://developer.apple.com/documentation/coretelephony/ctslicingmanager)
- [CTSlicingManager.AppCategory](https://developer.apple.com/documentation/coretelephony/ctslicingmanager/appcategory)
- [iPhone quick switch](https://developer.apple.com/documentation/coretelephony/iphone-quick-switch)
- [CTCellularPlanProvisioning](https://developer.apple.com/documentation/coretelephony/ctcellularplanprovisioning)
- [Network](https://developer.apple.com/documentation/network)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

***

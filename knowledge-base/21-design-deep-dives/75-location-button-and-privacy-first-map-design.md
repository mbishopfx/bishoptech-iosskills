# Location Button and privacy-first map design

Location is one of the clearest places to make an iOS app feel native: the permission moment is understandable, the system control is recognizable, and the map or place result has a strong visual hierarchy. The design fails when a decorative custom button disguises a permission request, a map implies precision that the app does not have, or a model turns a coordinate into an overconfident story.

Use this composition:

~~~text
why this feature needs a location
  -> system LocationButton
  -> current state and accuracy disclosure
  -> map/place result
  -> optional reviewable AI proposal
  -> save/share with retention choice
~~~

## Use the system location control

LocationButton is not a generic button with an arrow icon. It is the native authorization surface for one-time location access. Use a title that describes the action:

- Current Location for a feature that centers or reads the current point;
- Send Current Location when the feature will prepare a message or handoff;
- Share My Current Location when the person is choosing to share;
- a feature-specific explanation beside the button, not hidden in a tooltip.

Use the provided icon and label styles. Choose filled or outlined glyph treatment, a suitable background and foreground color, and a corner radius that fits the surrounding design. Do not replace the recognizable location mark with a custom icon, place the button inside an unreadable glass layer, or let localization truncate the title.

Apple’s HIG guidance says the system can warn about low contrast, excessive translucency, and text that does not fit at accessibility sizes or in translation. Test the real button at extra-large text, dark and light appearances, high contrast, reduced transparency, and long localized strings. If a custom appearance makes the button look unlike a location button, simplify it.

## Permission is part of the feature, not onboarding

Ask for location when the person engages the feature that needs it. A pre-permission explanation can say:

~~~text
Use your current location to show nearby places.
You can allow access for this feature only, and change it later in Settings.
~~~

Do not request location at launch for a feature the person has not used. Do not place a fake Cancel or dismiss action on a screen whose only purpose is to prepare for the system permission alert. If location is optional, let the person continue with a manual place search or a coarse, user-entered region.

After the tap, show an honest state:

| State | UI language | Next action |
| --- | --- | --- |
| ready to ask | Use current location | LocationButton |
| waiting for authorization | Checking access | Wait or cancel if the route allows it |
| authorized, waiting | Getting your location | Keep the result area stable |
| approximate result | Approximate location | Continue with coarse route or explain precision |
| precise result | Current location ready | Inspect, use, or discard |
| denied/restricted | Location access is off | Settings guidance or manual fallback |
| unavailable | Location unavailable right now | Retry or choose a manual route |

Do not show a map marker at a guessed default coordinate while permission is pending. A blank or neutral map state is more trustworthy than a false point.

## Map hierarchy

Treat the map as a context surface, not the entire product:

1. keep the page title and current task visible;
2. show the marker or region only after the app has a current accepted value;
3. expose approximate versus precise status near the result;
4. keep a readable place label and coordinate disclosure outside the map gesture area;
5. offer manual search or correction when the result is wrong or too coarse;
6. use a bottom sheet, inspector, or detail column for the actual decision.

Maps are visually dense. A Liquid Glass overlay should carry a small set of controls such as filter, recenter, layer selection, or review. It should not cover a marker, route instruction, selected place, or privacy disclosure. Use semantic buttons and menus, and keep the primary action stable as the map changes.

## Liquid Glass without hiding location semantics

Glass is a useful container for floating map controls because the map can change behind them. Keep the layering shallow:

~~~text
map/content
  -> one glass control group
  -> one review/action group
  -> system sheet or inspector for details
~~~

Avoid a glass-on-glass stack of a toolbar, filter pill, status chip, and AI card. Merge related controls into one group or move secondary details into a sheet. Use system materials, system colors, and semantic control styles when they already solve the problem.

Do not use glass to make a permission request feel like a custom app transaction. The system alert and LocationButton should remain recognizable. Do not claim that a translucent background makes location private; privacy comes from authorization, data minimization, retention, and downstream behavior.

## Approximate accuracy is a design state

The person may grant reduced accuracy. That should be represented in the UI, not silently converted into a precise-looking pin. For a nearby recommendation, show a region or radius. For a route that requires a precise point, explain the consequence and request temporary full accuracy at the moment of need.

Use language such as:

- Approximate area;
- Nearby results;
- Precise location needed for turn-by-turn directions;
- Location updated just now;
- Last known location from an earlier session.

Avoid:

- exact address when only a coarse location is known;
- “you are here” when the location is stale or approximate;
- a confidence ring that looks mathematically exact when it is only a product visualization;
- a model-generated place name presented as official.

## AI review surface

An on-device model can make a map feature more useful, but the design should show what the model received:

~~~text
current location or selected place
  -> bounded nearby context
  -> generated recommendation or label
  -> reason/source disclosure
  -> accept, edit, dismiss, or search manually
~~~

Good examples include suggesting a nearby category after the person taps a location button, summarizing a selected place, or turning a reviewed location into a journal tag. Keep the proposal separate from the coordinate and from any map provider result.

Do not use a model to guess a person’s identity, infer a sensitive trait from a location, verify that someone visited a place, or create an automatic message/share without review. If a model is unavailable, the map and manual search should remain useful.

## Sharing and retention

Before a location leaves the app, say what will be shared and for how long. A share sheet or message draft should distinguish:

- current point versus approximate region;
- a place label versus raw coordinates;
- one-time share versus persisted record;
- app-owned storage versus external destination;
- user-authored note versus model-generated description.

Offer a clear delete or stop-sharing path. If location is attached to a photo, contact, calendar event, or note, show it as an editable field before the final system handoff. A location button does not grant permission to share the result with another service.

## Accessibility and input

- Label the location action with the real outcome, not “GPS”.
- Announce authorization, approximate/precise status, stale data, and errors.
- Keep map actions available through accessible buttons and menus; do not make a gesture-only task.
- Support Dynamic Type in status and review views.
- Test VoiceOver focus when a marker or bottom sheet appears.
- Respect Reduce Motion for map transitions and glass morphing.
- Test increased contrast and reduced transparency over map tiles.
- Provide keyboard, pointer, and Voice Control paths on iPad and Mac Catalyst where the feature exists.
- Avoid flashing location indicators or using haptics as the only state signal.

## Design review checklist

- The LocationButton is recognizable and uses a system-provided title.
- Permission is requested at the moment of need.
- The map never shows a guessed marker while authorization is pending.
- Approximate, precise, stale, denied, and unavailable states are distinct.
- Liquid Glass surrounds controls without hiding map content or permission semantics.
- Manual place search remains available when location is denied or unavailable.
- AI suggestions identify themselves and remain editable proposals.
- Sharing states the precision, destination, and retention consequence.
- Long text, localization, VoiceOver, reduced effects, high contrast, and alternate input have been tested.

## Related routes

- [CoreLocationUI and least-privilege location access](../42-framework-deep-dives/55-corelocationui-and-least-privilege-location.md)
- [CoreLocationUI and on-device location route](../50-capability-recipes/78-corelocationui-and-on-device-location-route.md)
- [CoreLocationUI proof matrix](../60-verification/72-corelocationui-location-proof-matrix.md)
- [CoreLocationUI and LocationButton recipes](../70-code-recipes/90-corelocationui-locationbutton-recipes.md)

## Sources

- [Human Interface Guidelines privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Human Interface Guidelines designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [CoreLocationUI](https://developer.apple.com/documentation/corelocationui)
- [LocationButton](https://developer.apple.com/documentation/corelocationui/locationbutton)
- [CLLocationButton](https://developer.apple.com/documentation/corelocationui/cllocationbutton)
- [Core Location](https://developer.apple.com/documentation/CoreLocation)
- [Requesting authorization to use location services](https://developer.apple.com/documentation/CoreLocation/requesting-authorization-to-use-location-services?changes=_7)
- [CLAuthorizationStatus](https://developer.apple.com/documentation/corelocation/clauthorizationstatus)
- [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

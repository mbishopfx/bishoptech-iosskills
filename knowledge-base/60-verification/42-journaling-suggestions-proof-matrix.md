# Journaling Suggestions Proof Matrix

Journaling Suggestions crosses a special entitlement, system picker, person-controlled selection, high-level content projection, optional personal-context AI, universal-link notification routing, and sensitive retention. Verify each boundary separately.

## Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, app/extension targets, target membership |
| SDK/deployment | Xcode, SDK, iOS/iPadOS target, availability |
| Entitlement | com.apple.developer.journal.allow from signed artifact |
| Notification property | JSNotificationURLFormat value, if used |
| Universal links | Associated domains, URL scheme/host/path validation |
| Device | Physical iPhone/iPad model, OS build, locale, account |
| Settings | Journaling Suggestions enrollment, notifications, preferred app |
| Entry fixture | Synthetic draft ID, editor state, deletion policy |
| Selected type | Photo, location, contact, workout, media, reflection, etc. |
| AI state | Model availability, input projection, external-upload audit |
| Privacy | Raw content retention, logs, analytics, sync/export |
| Accessibility | VoiceOver, Dynamic Type, Voice Control, Switch Control, reduced effects |

Use synthetic or consented test content in screenshots and recordings. Do not place real personal suggestions in a shared evidence packet.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Journaling Suggestions is the correct route | Writing workflow and person-selected moment outcome | A desire for continuous health/location data |
| Picker capability configured | Target capability plus signed entitlement | Entitlements source file |
| Picker presents | Physical-device system picker run | SwiftUI preview |
| No extra authorization before selection | Observed picker flow and source-doc contract | App’s own permission copy |
| Selection returns high-level details | Person selection and completion result | Picker shown with no selection |
| Type-specific content works | Selected type and content(forType:) result | Mock model data |
| Raw source access is not claimed | Product copy and code audit | Storing a full source object |
| AI is local | Model/device trace and no external upload | “Private” label |
| Entry is user-approved | Edit/remove/save interaction evidence | Automatic draft insertion |
| Notification route configured | Entitlement, JSNotificationURLFormat, associated domain, Settings selection | Universal-link source file |
| Notification deep link works | Cold launch, onOpenURL, token, prepopulated picker | Opening the app manually |
| General reminder works | URL without identifier and normal picker route | Assuming every notification has a moment ID |
| Settings schedule is shown accurately | Configuration value and Settings comparison | Hard-coded “on” label |
| Content deletion works | Remove context, delete entry, cache/sync audit | Hiding the UI only |
| Health/privacy claims are safe | Copy/policy review and sensitive fixtures | StateOfMind result shown as diagnosis |
| Release ready | Final signed artifact, universal links, physical/system proof | Development run |

## Picker scenarios

- [ ] Present from a blank new-entry screen with clear rationale.
- [ ] Person dismisses picker.
- [ ] Person selects a photo.
- [ ] Person selects a location.
- [ ] Person selects a location group.
- [ ] Person selects a contact.
- [ ] Person selects a workout or motion activity.
- [ ] Person selects media/song/podcast.
- [ ] Person selects reflection/state-of-mind content.
- [ ] Person selects an event poster.
- [ ] Selection includes date/title but no supported asset.
- [ ] Completion returns after backgrounding.
- [ ] Entry is deleted before completion.
- [ ] App has no entitlement/build support.
- [ ] Picker is unavailable on the selected device/OS.

Record the exact selected type and the app’s redacted projection. Do not interpret no-suggestion/no-content as no personal events.

## Content and privacy checks

| Test | Expected result |
| --- | --- |
| Photo selected | Only selected photo/content needed for entry is retained |
| Location selected | Product uses stated coarse/exact policy |
| Contact selected | No relationship inference |
| Workout selected | No diagnosis, treatment, or fitness guarantee |
| StateOfMind selected | Reflective language; no clinical claim |
| Media selected | Source/title provenance and licensing-aware copy |
| Full suggestion object logged | Test fails; raw content is redacted |
| External model call | Test fails unless separately approved and disclosed |
| Entry deleted | Selected context and app-owned derivative data follow deletion policy |
| Account sign-out | Personal-context cache is cleared or reauthorized |

## Notification and universal-link scenarios

- [ ] Journaling Suggestions enrollment completed.
- [ ] Notifications allowed.
- [ ] App is selected in Open Notifications With when multiple apps exist.
- [ ] JSNotificationURLFormat path form is valid.
- [ ] Query-argument form is valid if used.
- [ ] URL host/path/scheme validation rejects an unexpected URL.
- [ ] Moment identifier parsed into JournalingSuggestionPresentationToken.
- [ ] General reminder with empty identifier opens a normal picker.
- [ ] Cold launch restores pending entry.
- [ ] Warm launch handles onOpenURL.
- [ ] Duplicate notification does not duplicate an entry.
- [ ] Invalid/expired identifier recovers to normal entry.
- [ ] Configuration reports smart, custom, and off accurately.
- [ ] Settings changes are reflected after foregrounding.

The notification URL is a route token, not a source of personal content. Never treat the identifier as the selected event itself.

## AI evaluation matrix

| Fixture | Expected behavior |
| --- | --- |
| Selected photo + title | Draft references only selected context |
| Selected location | Draft avoids unsupported exact itinerary claims |
| Selected workout | Draft remains descriptive, not medical |
| State of Mind content | No diagnosis, treatment, or risk inference |
| Missing content | Fixed prompt asks the person to add details |
| Ambiguous date | Draft preserves uncertainty |
| Edited source context | Draft recomputed or clearly stale |
| Model unavailable | Deterministic template remains |
| Person rejects draft | No save/mutation |
| External-upload audit | Raw personal context is blocked |

## Accessibility matrix

- [ ] VoiceOver can open the picker button and understand its purpose.
- [ ] Picker return places focus on selected-context summary.
- [ ] Dynamic Type keeps Save/Remove actions visible.
- [ ] Voice Control reaches Choose, Remove, Save, and Discard.
- [ ] Switch Control reaches the same actions.
- [ ] Reduce Motion preserves context updates.
- [ ] Reduce Transparency preserves contrast.
- [ ] RTL and long localized titles work.
- [ ] iPad layout supports picker/editor flow.
- [ ] Notification deep link remains understandable with assistive settings.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| eligible | Target/SDK/entitlement can present the route |
| presented | System picker appeared |
| dismissed | Person left without selecting |
| selected | Person chose a suggestion |
| projected | App converted selected content into a redacted model |
| reviewed | Person saw/edited the context or draft |
| saved | App persisted a user-approved entry |
| tokenized | Notification identifier became a presentation token |
| prepopulated | Picker opened with a system-provided moment context |
| deleted | App-owned entry/context/cache followed deletion policy |

## Sources

- [Journaling Suggestions](https://developer.apple.com/documentation/journalingsuggestions)
- [Presenting the suggestions picker and processing a selection](https://developer.apple.com/documentation/journalingsuggestions/presenting-the-suggestions-picker-and-processing-a-selection)
- [JournalingSuggestion](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestion)
- [Receiving journaling suggestions system notifications](https://developer.apple.com/documentation/journalingsuggestions/receiving-journaling-suggestions-from-system-notifications)
- [JournalingSuggestionPresentationToken](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionpresentationtoken)
- [JournalingSuggestionsConfiguration](https://developer.apple.com/documentation/journalingsuggestions/journalingsuggestionsconfiguration)
- [Journaling Suggestions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.journal.allow)
- [Journaling Suggestions updates](https://developer.apple.com/documentation/updates/journalingsuggestions)
- [Universal links](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)

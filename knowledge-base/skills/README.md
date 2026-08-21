# Reusable iOS Skill Blueprints

These Markdown files are readable blueprints for Codex skills or project-specific agent instructions. They are intentionally source-linked and evidence-aware. The workspace-scoped [skill packages](packages/README.md) turn the strongest blueprints into reusable `SKILL.md` instructions without mutating global Codex configuration.

For the public role map, feature descriptions, handoffs, and evidence vocabulary, see the [complete skill catalog](../../docs/skills-catalog.md).

## Skill contract

Every skill should declare:

- when to use it;
- what files or project state it may inspect;
- which official sources it relies on;
- what assumptions it refuses to make;
- what it may change;
- how it verifies the result;
- what evidence it must not overclaim.

## Available blueprints

- [SwiftUI native design](swiftui-native-design.md)
- [Liquid Glass design](liquid-glass-design.md)
- [On-device AI feature](on-device-ai-feature.md)
- [Apple SDK route selection](apple-sdk-route.md)
- [Agentic Apple engineering team](packages/ios-agentic-apple-engineering-team/SKILL.md)

## Workspace-scoped packages

- [Skill package index](packages/README.md)
- [SwiftUI native design package](packages/swiftui-native-design/SKILL.md)
- [Liquid Glass design package](packages/liquid-glass-design/SKILL.md)
- [On-device AI feature package](packages/on-device-ai-feature/SKILL.md)
- [Apple SDK route package](packages/apple-sdk-route/SKILL.md)
- [iOS capability route planner package](packages/ios-capability-route-planner/SKILL.md)
- [iOS project, target, and module architect package](packages/ios-project-target-architect/SKILL.md)
- [iOS system surfaces and background package](packages/ios-system-surfaces-and-background/SKILL.md)
- [iOS companion and communications package](packages/ios-companion-communications/SKILL.md)
- [iOS device and release proof package](packages/ios-device-release-proof/SKILL.md)
- [iOS media, ML, and physical-input package](packages/ios-media-ml-and-inputs/SKILL.md)
- [iOS spatial, graphics, and games package](packages/ios-spatial-graphics-and-games/SKILL.md)
- [iOS native design and Liquid Glass verification package](packages/ios-native-design-verification/SKILL.md)
- [iOS data and device services package](packages/ios-data-and-device-services/SKILL.md)
- [iOS commerce, identity, and security package](packages/ios-commerce-identity-and-security/SKILL.md)
- [iOS on-device intelligence evaluation package](packages/ios-on-device-intelligence-evaluation/SKILL.md)
- [iOS privacy, performance, and release-proof package](packages/ios-privacy-performance-release-proof/SKILL.md)
- [iOS testing and release-assurance package](packages/ios-testing-and-release-assurance/SKILL.md)
- [iOS source refresh and availability-maintenance package](packages/ios-source-refresh-and-availability/SKILL.md)
- [Agentic Apple engineering team package](packages/ios-agentic-apple-engineering-team/SKILL.md)

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

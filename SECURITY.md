# Security and responsible disclosure

This repository contains documentation, recipes, and agent skill instructions. It is not itself a production app, backend, entitlement service, or secret store.

## Do not commit

- API keys, signing certificates, provisioning profiles, tokens, passwords, private prompts, or user data;
- health, contact, media, account, or device identifiers from real users;
- private workspace paths or generated test artifacts that reveal local environments;
- copied credentials or unreviewed model output presented as platform authority.

## Reporting a problem

For a security issue in the repository, open a private GitHub Security Advisory once the public repository is hosted. For a sensitive issue before that point, contact the repository maintainer privately and include the affected path, impact, reproduction, and a safe remediation.

Do not publish an exploit, credential, or private data in a public issue.

## Scope boundary

The skill bundle can help an LLM identify security and privacy work, but it does not certify an app, server, entitlement, payment flow, authentication system, or release. Verify security-sensitive behavior against the current Apple documentation, SDK, target configuration, real services, and appropriate device or production evidence.

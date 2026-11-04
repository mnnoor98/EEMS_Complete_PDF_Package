# Release Candidate Security Review

Reviewed: 2026-11-04

## Dependency audit

- Runtime audit threshold: high; the production dependency audit reports no high or critical findings.
- The full development audit reports eight moderate findings in Karma, glob, minimatch, rimraf, and related Angular test-build tooling.
- These packages are used only in the build/test stage and are absent from the final Nginx runtime image.
- npm currently proposes an Angular 22 → 19 breaking downgrade as the automated remediation. That change is rejected for this release candidate because it would introduce a larger compatibility risk.
- Reassess when the Angular toolchain publishes a compatible fix. Dependabot/registry advisories remain a release input.

## Release controls

- Images are built from an immutable tag after backend, frontend, E2E, and container CI gates pass.
- Secrets are injected by the deployment environment and excluded from source control.
- Bootstrap and startup migrations are disabled after initial staging initialization.
- Tenant isolation, maker-checker operations, audit logging, HSTS, security headers, rate limiting, liveness, and readiness probes are enabled.

This review is not a penetration test. Production approval still requires staging acceptance, infrastructure review, backup/restore evidence, and operator sign-off.

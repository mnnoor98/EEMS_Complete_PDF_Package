# EEMS 1.0 Release Candidate Checklist

## Automated gates

- [ ] Backend unit, integration, and architecture tests pass in Release mode.
- [ ] Angular production build passes within bundle budgets.
- [ ] Playwright Chromium release smoke suite passes.
- [ ] Backend and frontend container images build.
- [ ] `docker compose config --quiet` passes with non-production CI secrets.
- [ ] Dependency audit findings are reviewed and accepted or remediated; do not apply breaking `--force` upgrades without regression testing.
- [x] Development-only moderate audit findings are documented in `SECURITY_REVIEW.md`; runtime high/critical audit gate is automated.

## Environment and security

- [ ] Replace every value copied from `.env.example`; use at least 32 random characters for the JWT signing key.
- [ ] Set explicit production CORS origins and terminate TLS at the ingress.
- [ ] Run migrations once as a controlled job; disable startup migrations when scaling API replicas.
- [ ] Disable bootstrap after the first administrator is created and rotate the initial password.
- [ ] Confirm tenant row-level security policies and least-privilege database credentials.
- [ ] Verify `/health/live` and `/health/ready` through the deployment platform.

## Operational acceptance

- [ ] Complete a staging walkthrough: election → candidate → workforce → polling → inventory/finance/events → results → export.
- [ ] Verify maker-checker rules using two distinct accounts.
- [ ] Verify audit correlation, security notifications, backup, restore, and rollback procedures.
- [ ] Capture stakeholder acceptance and tag the approved commit as `v1.0.0-rc.1`.
- [ ] Confirm the tag workflow published both GHCR images and created the prerelease entry.

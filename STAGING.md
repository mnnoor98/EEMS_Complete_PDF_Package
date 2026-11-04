# Staging Deployment Runbook

## Prerequisites

- Docker Engine with Compose v2 on the staging host.
- TLS-terminating ingress or load balancer forwarding `X-Forwarded-Proto`.
- A dedicated PostgreSQL volume, backup target, and least-privilege credentials.
- A staging `.env` created from `.env.example`; never commit it.

## First staging deployment

1. Pull the tagged source or copy `compose.yaml` and `compose.staging.yaml` to the host.
2. Set `EEMS_VERSION=v1.0.0-rc.1` and all required secrets in `.env`.
3. Temporarily run one API instance with `Database__ApplyMigrations=true` and bootstrap enabled to initialize the schema and first administrator.
4. Sign in, rotate the administrator password, then set bootstrap and startup migrations to `false`.
5. Start the tagged stack:

   ```bash
   docker compose -f compose.yaml -f compose.staging.yaml pull
   docker compose -f compose.yaml -f compose.staging.yaml up -d
   ```

6. Verify `/health/live`, `/health/ready`, login, dashboard, and the operational walkthrough in `RELEASE_CHECKLIST.md`.

## Upgrade and rollback

- Back up PostgreSQL before migrations and record the running image tag.
- Deploy a new immutable tag only after CI and staging acceptance.
- For application rollback, restore the prior `EEMS_VERSION` and run Compose again.
- If a migration is not backward compatible, restore the matching database backup before starting the previous application tag.

No staging host or credentials are stored in this repository; deployment to a real host remains an operator action.

# Deployment Discipline

**Status**: Parking lot — capturing ideas as they emerge from other work

## Scope

CI/CD, infrastructure, release management, monitoring, rollback strategies.

## Parking Lot

*Add deployment insights here as they emerge during work. Include date and source context.*

### Seeded Insights

- **E2E tests in CI/CD are a deferred optimization.** When a testing process is first being established, defer CI/CD integration. Optimize for learning velocity first. Design the integration point once the testing process has proven itself. When ready, consider: pre-deploy smoke suite, post-deploy verification, Playwright in GitHub Actions.

- **Breaking auth changes require deployment coordination.** When tokens or session formats change, existing sessions become invalid. Deployment should include a communication step. The frontend 401 interceptor pattern handles it gracefully for users who stay logged in, but users with old tokens must re-authenticate.

- **Playwright runs headless by default — good for CI.** Playwright CLI can be invoked from GitHub Actions without a display server. Auth state persistence (`storageState`) handles authentication across CI runs without re-authenticating each time.

- **Health check prerequisite pattern.** The testing discipline's health check recipe (verify frontend, API, and any proxy endpoints are up) should become a deployment readiness check. Same checks, different context: pre-deploy instead of pre-test.

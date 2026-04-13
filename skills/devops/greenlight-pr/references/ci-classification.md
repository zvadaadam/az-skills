# CI Failure Classification

## Branch-Related (fix locally, commit, push)

The failure is caused by code in the PR branch:

- Compile/typecheck/lint failures in files touched by the branch
- Deterministic test failures in changed areas
- Snapshot output changes caused by UI/text modifications
- Static analysis violations introduced by the latest push
- Build script/config changes in the PR causing a deterministic failure

## Flaky / Infrastructure (retry with `--retry-failed`)

The failure is transient or external to the branch:

- DNS/network/registry timeout errors while fetching dependencies
- Runner image provisioning or startup failures
- GitHub Actions infrastructure/service outages
- Cloud/service rate limits or transient API errors (429, 502, 503)
- Non-deterministic failures in unrelated integration tests

## Decision Tree

1. Read the failed logs: `gh run view <run-id> --log-failed`
2. If logs mention files/modules YOU changed → **branch-related** → fix it
3. If logs mention timeouts, DNS, provisioning, rate limits → **flaky** → retry
4. If unclear → inspect once manually, then decide
5. After 3 retries on the same SHA → stop and report to user

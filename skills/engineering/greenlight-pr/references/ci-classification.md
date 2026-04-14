# CI Failure Classification

## Decision pseudocode

```
def classify_failure(check):
  logs = check.log_excerpt

  if logs mention files or modules YOU changed:
    return "branch"  # your code broke it — fix locally

  if logs match any flaky pattern:
    # timeout, DNS, 429, 502, 503, runner provisioning,
    # registry error, infrastructure outage
    return "flaky"   # transient — retry

  if logs mention test failures in code you didn't touch:
    return "flaky"   # unrelated test — retry

  if unclear:
    read the full logs manually (gh run view <run-id> --log-failed)
    make a call

  return classification
```

## What to do

```
if all failures are "flaky":
  gl-snapshot.py --retry-failed
  # budget: 3 retries per SHA, then stop and ask user

if any failure is "branch":
  read the log_excerpt
  find the root cause in your code
  fix it — commit — push
  # do NOT retry branch failures, they will fail again
```

## Branch-related signals

- Compile / typecheck / lint errors in files touched by the branch
- Deterministic test failures in changed areas
- Snapshot output changes caused by UI/text modifications
- Static analysis violations introduced by the latest push
- Build config changes in the PR causing deterministic failure

## Flaky / infrastructure signals

- DNS / network / registry timeout errors
- Runner image provisioning or startup failures
- GitHub Actions service outages
- Rate limits or transient API errors (429, 502, 503)
- Non-deterministic failures in unrelated tests

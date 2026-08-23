# KP-001: Create a Resource over HTTP

## Scenario Definition

| Field | Value |
|---|---|
| Repository / Revision | example/repo @ abc123 |
| Actor | API Client |
| External stimulus | POST /v1/resources |
| Initial state | The target key does not exist |
| Build target | //cmd:server |
| Runtime config | default |
| Feature flags | none |
| Expected final state | The resource is persisted and the server returns 201 |
| Oracle | HTTP 201 and the data record exists |
| Runtime evidence | Not run |

## Path Steps

| Step | Trigger/caller | Component and symbol | Input | State before→after | Side effects | Error/timeout/retry/degradation | Claim | Evidence | Confidence |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | HTTP Router | `CreateHandler` | JSON body | No change | Reads request body | Returns 413 when the body is too large | CLM-001 | EV-001 | C2 |
| 2 | `CreateHandler` | `Service.Create` | Domain object | New→Validated | Validation | Returns 400 when validation fails | CLM-002 | EV-002 | C3 |
| 3 | `Service.Create` | `Repository.Insert` | Valid object | Absent→Stored | Database write | Returns 409 on conflict | CLM-003 | EV-003 | C3 |

## MAY versus OBSERVED

| Relationship | Static result | Runtime result | Explanation or unknown |
|---|---|---|---|
| Handler → Audit hook | MAY | Not observed | No runtime environment is available; keep this pending validation |

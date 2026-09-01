# States: Loading, Empty, Error, Offline, Permission, Disabled

Do not model Loading, Empty, Error, and Offline as one mutually exclusive
enum. The model below is a C-class engineering suggestion from the source
methodology, not a platform-mandated data structure — but the failures it
prevents (error disguised as empty, cache presented as live, one global
spinner) are class A/B concerns.

## State dimensions — legal combinations exist

```text
data:        not-fetched / empty / has-data
request:     idle / first-load / background-refresh / failed
connection:  online / offline / unstable
permission:  unknown / granted / denied / restricted
operation:   unsubmitted / submitting / confirmed-success / failed / pending-confirmation
control:     default / pressed / focused / selected / disabled / read-only
```

"Has cached data + offline + last refresh failed" is a legal combination.
Do not collapse it into a full-screen error.

## What each situation must communicate

| Situation | What the user needs to know | Recommended handling | Do not |
|---|---|---|---|
| First load, nothing to show | What is being fetched | Loading feedback that matches the content structure; a way out or cancel path | Show a fabricated percentage |
| Has data, background refresh | Current content still usable, update incomplete | Keep content; show refresh status locally | Blank the whole screen on every refresh |
| First use, no data yet | Nothing has been created | Explain the purpose; offer create/import entry when a sensible next step exists | Treat blank as an error; push a meaningless CTA |
| Search with no results | Nothing matches the current conditions | Keep the query; offer to modify or clear filters | Clear the query and make the user retype |
| Everything done | The task is complete | State completion plainly; no extra action required | Invent filler tasks to occupy the page |
| Request failed | Which part failed; whether existing content is still trustworthy | Feedback near the failure; preserve input; offer retry or an alternative path | Say only "something went wrong"; describe failure as "no data" |
| Offline with cache | What can be viewed; what has not synced | Mark cache/sync status; show last-updated time when relevant | Present cached content as live |
| Result pending confirmation | Request sent, final outcome unknown | Block duplicate submission; offer a way to check the result | Announce success before confirmation, or invite repeated submits |
| Disabled | Why it cannot run now; how to satisfy the precondition | Explain the prerequisite somewhere perceivable | A greyed-out button whose only explanation is on hover |
| Read-only | Information can be read but not edited | Keep readability and proper assistive access | Render important content as a low-contrast disabled form |

Basis: official progress-feedback guidance plus mature empty/loading/disabled
patterns and offline-first architecture practice (A/B). Copy, layout, and
state combinations still need validation per business.

## Design rules that fall out of this

- State must be driven by data and operation facts, not by which mockup was
  drawn (see rules R12–R15 in references/rules.md).
- Preserve the user's completed work on recovery paths; a field error must
  not reset the whole form.
- Loading feedback should be scoped to what is actually loading.
- Progress and results express only known facts: indeterminate progress for
  unknown duration, success only after confirmation.

## Verification for states

Inject the conditions, don't imagine them: slow request, offline, timeout,
partial failure, double tap, reconnect; first run with no data; search with
no results; permission denied; disabled with unmet preconditions. Then check
that assistive technology announces the same state the pixels show.

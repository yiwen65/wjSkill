# Static-only performance diagnosis

Use this mode only when runtime evidence is explicitly out of scope or cannot be
obtained within the authorized environment. Inspect source, build configuration,
tests, and already-existing compiler-generated artifacts only. Its result is a
prioritized set of static performance candidates and a validation plan, not a
runtime bottleneck or speedup claim.

Apply the selected runtime adapter's Static-only focus and interpretation
boundaries. Do not follow its measured tool or execution guidance in this mode.

## Establish the static contract

Record only what changes the analysis:

- the exact target files or directory and whether the scope is the full target,
  a supplied diff, or named symbols;
- which callers, callees, tests, build files, generated code, or other existing
  static artifacts may be read as context;
- the known or assumed workload shape, input sizes, call frequency, concurrency,
  hardware, and build configuration;
- forbidden actions such as execution, compilation, instrumentation, file edits,
  dependency changes, or external access; and
- the requested output: diagnosis only, ranked recommendations, or a minimal
  runtime validation plan.

Do not silently reduce a full-directory request to Git changes. Keep target-owned
findings separate from external context read only to understand the target.

If a missing workload assumption would reverse or invalidate the ranking, state
both relevant cases or ask one focused question. Otherwise proceed and label the
assumption.

## Trace the executable cost paths statically

Start from target entry points and follow the paths that could perform meaningful
work. Inspect only the dimensions relevant to the code:

- **Work multiplicity:** nested or repeated traversal, recomputation, parsing,
  conversion, retry, polling, and per-item calls; derive symbolic operation counts
  from input variables when possible.
- **Data structures and access:** lookup/update mix, iteration order, working-set
  growth, pointer chasing, hot/cold fields, padding, invalidation, and worst-case
  behavior. Big-O alone does not establish the faster representation.
- **Allocation and lifetime:** per-item allocation, temporary objects, container
  growth, copies/moves, ownership boundaries, cross-thread frees, retained
  capacity, and arena or pool release semantics.
- **Concurrency:** shared writes, lock scope and acquisition frequency, atomics,
  cache-line adjacency, queue bounds, task granularity, imbalance, shutdown,
  ordering, and memory-order requirements.
- **I/O and serialization:** per-record operations, small reads/writes, flushes,
  repeated encoding/decoding, buffer reuse, batching bounds, backpressure, and
  partial-completion behavior.
- **Build and generated-code preconditions:** actual optimization flags, target
  ISA policy, LTO/PGO inputs, virtual or indirect calls, aliasing, control flow,
  inlining/vectorization barriers, and code-size risks. Source shape does not
  prove the compiler's final output.

Trace callers and configuration far enough to determine whether candidate code
is reachable and under what condition. Do not infer runtime frequency, input
distribution, cache behavior, contention, generated instructions, or product
impact from reachability alone.

## Classify every conclusion

Use exactly these evidence classes:

- **STATIC FACT:** directly established by the inspected source, build
  configuration, or an existing artifact, such as an allocation inside a loop or
  an effective build flag.
- **CONDITIONAL RISK:** a plausible performance mechanism whose impact depends on
  runtime frequency, sizes, contention, data distribution, hardware, or generated
  code.
- **UNKNOWN:** required evidence is absent or conflicting, so direction or
  materiality cannot be determined statically.

Do not label a location as a `hotspot`, `dominant bottleneck`, `root cause`,
`performance regression`, or `optimization win` in this mode. Do not assign a
speedup percentage, latency reduction, severity based on guessed frequency, or
precise hardware cost.

Rank candidates using only supported factors: symbolic complexity, work or bytes
performed per invocation, reachability conditions, statically derived call
multiplicity, resource amplification, affected correctness constraints, and
confidence. Make the ranking conditional when workload assumptions control it.

## Finding gate

Report a candidate only when all of the following are available:

1. a precise location and relevant call or data path;
2. the code fact and trigger condition;
3. a causal mechanism linking that fact to a potentially affected metric;
4. the evidence class and material assumptions;
5. the main alternative explanation or reason impact may be negligible; and
6. the smallest runtime measurement or generated-code check that could confirm
   or reject materiality.

Do not report generic advice, style preferences, unsupported container swaps,
speculative SIMD, or a broad compiler flag list. If no candidate passes the gate,
say that no actionable static performance risk was found in the inspected scope;
do not imply that runtime performance is healthy.

Recommendations remain proposals in diagnosis-only mode. Preserve semantics,
ownership, thread safety, memory ordering, error handling, portability, and
resource bounds; do not trade correctness for an unmeasured benefit.

## Stop conditions

Stop when the relevant target paths and necessary context have been inspected,
all reportable candidates pass the finding gate, and further progress requires
runtime data, generated code, a missing caller/configuration, or broader scope.
Do not continue searching merely to produce a requested number of findings.

## Static-only report

Lead with the boundary that this is static analysis, then include only supported
sections:

```markdown
## Static-analysis contract
Target, scope, allowed evidence, forbidden actions, workload assumptions, and
important unknowns.

## Candidate findings
For each candidate: priority, evidence class, file:line, relevant path, code fact,
trigger, mechanism, potentially affected metric, assumptions, alternative
explanations, and bounded recommendation when requested.

## Minimum validation plan
The smallest benchmark, profiler/counter, generated-code inspection, workload
scan, or A/B experiment that would confirm or reject each material candidate.

## Coverage and limits
Inspected target and context, unavailable paths or artifacts, conclusions that
cannot be made statically, and whether no candidate passed the finding gate.
```

Never emit empty measured-baseline, profiler, before/after, or verified-speedup
sections in this mode.

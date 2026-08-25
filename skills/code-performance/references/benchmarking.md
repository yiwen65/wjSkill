# Benchmarking and regression evidence

Read this reference when creating or assessing a benchmark, comparing two
implementations, claiming a performance change, or defining continuous gates.

## Choose the smallest useful benchmark layer

| Layer | Best use | Cannot prove alone |
|---|---|---|
| Microbenchmark | Isolate a function, loop, data structure, or allocation policy | Product-level benefit |
| Component benchmark | Retain realistic threading, allocator, serialization, and interfaces | Full request or pipeline behavior |
| End-to-end load | Measure business throughput, tail latency, and capacity | Local causal mechanism |
| Long/stress run | Expose throttling, fragmentation, leaks, periodic work, and queue growth | Cheap iteration on a local change |

Use end-to-end evidence to confirm relevance, a smaller benchmark to shorten the
causal search, and end-to-end evidence again to validate the result.

## Record a reproducible contract

Keep the fields that can change the decision:

- revision, worktree state, binary hash, compiler/runtime and exact versions;
- complete effective build/link flags, dependencies, allocator, LTO/PGO profile;
- CPU/hardware model and topology, OS/kernel, power/frequency policy, NUMA,
  storage/network state when relevant;
- immutable dataset ID or content hash, input distribution, request mix, seed,
  concurrency, offered load, load model, duration, and cold/steady mode;
- timer boundaries, sample count, warm-up, cache/process reset policy, profiler
  configuration, lost samples, and raw repeated results.

Report user-visible results and normalized machine costs together. Prefer metrics
such as items/s, latency P50/P95/P99, cycles/op, instructions/op, core-seconds per
unit, allocations/op, bytes/op, syscalls/op, lock wait/op, or energy/op over
unnormalized CPU percentages and architecture-specific raw counters.

## Prevent invalid measurements

- Use a production-equivalent optimized build and retain symbols needed for
  attribution. Do not compare instrumented sanitizer/profiler builds with native
  release builds as if instrumentation were free.
- Keep benchmark results observable. Use the benchmark framework's optimization
  barriers; `volatile` is not a general barrier. Inspect generated code when the
  compiler might remove, fold, or move the measured work.
- Separate setup and validation from the timed region without accidentally
  changing the cache or allocation behavior being studied.
- Separate cold-start and steady-state results. Neither substitutes for the other
  when both matter to the product.
- Cover representative, hotspot, adversarial, hit/miss, small/large working-set,
  normal-load, and overload inputs as relevant. Uniform random data is rarely
  sufficient by itself.
- For request systems, prevent coordinated omission: use a fixed-arrival/open-loop
  load or explicitly correct the histogram, and retain the full distribution.
- Control or record affinity, NUMA placement, SMT, boost/frequency policy,
  temperature, background load, interrupts, and first-touch behavior when their
  variation is material. Match production policy for capacity conclusions.

## Compare A/B rigorously

1. Start each version independently multiple times.
2. Randomize or interleave A/B order.
3. Keep every raw sample and note outlier handling before inspecting results.
4. Report effect size or ratio with uncertainty, not only two means.
5. Require both statistical support and a project-defined practical impact when
   the decision depends on a small change.
6. Check that the predicted resource metric and the user-visible metric move in
   a causally consistent direction.

If layout, linking, ASLR, thermal state, or host noise can plausibly explain the
effect, run a discriminating control rather than attributing the result to code.

## Continuous regression gates

Use layers proportional to signal quality:

- **PR/shared runner:** correctness, complexity cliffs, allocations, code size,
  and large regressions; avoid blocking on tiny wall-time changes in noisy hosts.
- **Dedicated periodic host:** component/end-to-end latency, throughput, PMU,
  scaling, NUMA, memory, and production build configurations.
- **Long-run or canary:** fragmentation, throttling, queue growth, periodic work,
  tail latency, and capacity cost.

Maintain distinct baselines when hardware, OS/kernel, compiler, standard library,
allocator, build configuration, PGO profile, or dataset changes. Gate on practical
impact, uncertainty, consistency across repetitions/layers, resource tradeoffs,
and historical drift. Preserve raw samples and the first regressing revision so
the change can be bisected.

# Ecosystem Routing

Use this reference to select project-native candidate detectors and validation.
Inspect manifests, build definitions, entry points, deployment artifacts, CI,
and installed tool versions before choosing commands. Prefer tools already
configured by the repository; verify current official documentation before
introducing or making version-sensitive claims about a new tool.

Every detector starts in report-only mode. Tool output is a candidate source,
not deletion permission.

## Language and runtime routes

### Java and Kotlin

- Candidate signals: compiler/IDE or Qodana unused declarations, Error Prone,
  SpotBugs, detekt, `jdeps`, build graphs, JaCoCo, and organization CodeQL rules.
- Model explicitly: Spring/Jakarta registration, dependency injection,
  annotations, reflection, service loaders, serialization, JNI, processors,
  generated sources, tests, and published libraries.
- Validate the real build profiles, application startup and component discovery,
  integration/contract tests, packaged artifacts, and supported runtime versions.

### JavaScript and TypeScript

- Candidate signals: TypeScript unused checks, ESLint, Knip, workspace/project
  graphs, and bundler output analysis.
- Model explicitly: dynamic imports, framework routes, auto-imports, re-exports,
  package entry points, generated files, plugins, CSS/polyfills, and module
  side-effect declarations.
- Validate each package and bundle mode, server and browser entry points,
  installation, startup, route discovery, and supported workspace targets.
  Tree-shaking from one bundle proves only that artifact, not source-level death.

### Python

- Candidate signals: Ruff or another configured linter, Vulture, dependency
  analysis, import graphs, and coverage contexts.
- Model explicitly: decorators, Django/Flask or other route discovery, entry
  points, `importlib`, monkey patching, `__init__.py` re-exports, editable installs,
  plugins, subprocesses, native extensions, and generated modules.
- Validate import and startup behavior, route/test discovery, packaged wheels or
  applications, supported environments, integration processes, and entry points.

### Go

- Candidate signals: compiler checks, Staticcheck, package/build graphs, and
  integration coverage.
- Model explicitly: exported APIs, interface satisfaction, `init`, build tags,
  OS/architecture, `go:generate`, plugins, reflection, cgo, tools, and examples.
- Validate all supported tag and platform combinations, generated artifacts,
  package tests, integration binaries, startup, and public compatibility.

### C and C++

- Candidate signals: configured compiler warnings, clang-tidy, include-cleaner,
  CodeQL or project call graphs, coverage, linker maps, and build queries.
- Model explicitly: translation-unit limits, headers, macros, templates, weak
  symbols, address-taken callbacks, FFI, `dlopen`, registries, linker scripts,
  platform macros, generated sources, and multiple binaries.
- Use the complete compilation database and supported build matrix. Validate all
  relevant link targets, platforms/configurations, startup and plugin discovery,
  ABI/API compatibility, packaging, and representative system tests. Linker
  section collection is evidence about one linked artifact only.

### C# and .NET

- Candidate signals: Roslyn unused/private diagnostics, configured analyzers,
  trimming analysis, dependency graphs, and coverage.
- Model explicitly: reflection, dependency injection, serializers, test
  discovery, XAML, source generators, attributes, native interop, and libraries.
- Validate build and publish variants, trimmed packages when applicable, startup,
  discovery, serialization, integration/contract tests, and supported runtimes.
  A trimming warning or retained assembly is not by itself a dead-code verdict.

### Rust

- Candidate signals: rustc unused/dead-code lints, configured dependency tools,
  feature/target graphs, and coverage.
- Model explicitly: public APIs, traits, proc macros, `build.rs`, generated code,
  optional features, target triples, examples/benches, dynamic loading, and FFI.
- Validate all supported features and targets, build scripts, examples and
  packages, tests, startup, FFI boundaries, and public compatibility. A fast
  dependency scanner may intentionally trade precision for speed.

### Unlisted or polyglot systems

Do not substitute a nearby language's tools by analogy. Use compiler/build
capabilities documented by the repository and state missing specialization.
For polyglot systems, analyze one executable or deployable boundary at a time;
add a second route only when a candidate or consumer crosses that boundary.

## Monorepo and build-graph routes

### Bazel

- `query` describes the declared target graph.
- `cquery` describes configured targets and is required when `select`, platforms,
  transitions, or toolchains affect reachability.
- `aquery` exposes actions and generated artifacts.

Use reverse dependencies and configured target matrices to bound impact, then
perform symbol- and runtime-level analysis separately. A target graph does not
prove every symbol in a retained target is live.

### Buck2

Prefer configured queries for platform, transition, toolchain, and execution
dependencies. As with Bazel, combine target-graph evidence with language,
generated-action, and runtime consumer evidence.

### Nx and JavaScript/TypeScript workspaces

Use the current project graph and affected calculation to identify packages and
validation scope. Confirm workspace entry points, package publication, framework
plugins, generated projects, and build configurations. "Unaffected by this Git
change" is not "unused."

### Other build systems

Recover the equivalent layers:

1. declared dependencies and reverse dependencies;
2. configuration-specific targets;
3. generated actions and artifacts;
4. packaged/deployed entry points; and
5. consumers outside the build graph.

If these layers cannot be recovered, declare the build boundary incomplete and
do not auto-delete non-local assets.

## CI integration

When continuous governance is requested:

- establish a reproducible baseline before enabling failures on a legacy codebase;
- fail on justified net-new issues rather than every historical candidate;
- require suppressions to name an owner, reason, affected boundary, and expiry;
- keep high-risk findings report-only until their dynamic and contract models are
  trustworthy;
- let automation create small reviewable changes, not bypass review or lifecycle
  gates; and
- track candidate precision, decision time, owner coverage, build/test impact,
  rollback or change-failure rate, and stale suppressions rather than optimizing
  primarily for deleted lines.

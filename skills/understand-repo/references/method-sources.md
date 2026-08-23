# EDRU Method Sources and Boundaries

Load this file only when the user asks about methodological grounding, research sources, or method boundaries. During repository understanding, treat target-repository evidence as authoritative.

## Source areas

| Area | Influence on EDRU | Representative source |
|---|---|---|
| Architecture reconstruction | Extract facts from implementation and aggregate them progressively; one system needs multiple views | SEI, Architecture Reconstruction Guidelines |
| Multi-view architecture | Deployment, module, build, runtime, and data views cannot substitute for one another | SEI, Views and Beyond |
| Intended versus implemented design | Maintain both intended architecture and as-built architecture | Murphy, Notkin, Sullivan, Software Reflexion Models |
| Feature location | Finding a starting point differs from determining the full impact scope | Dit et al., Feature Location in Source Code |
| Static and dynamic analysis | Static analysis describes possible paths; dynamic evidence covers only executed inputs and configurations | Program analysis and software reconnaissance research |
| Code graphs | Syntax, symbols, control flow, and data flow are useful fact layers but do not automatically recover business architecture | Joern CPG, CodeQL, SCIP, Kythe, Glean |
| Repository-level agents | Iterative retrieval, hierarchical localization, planning, and tool interfaces outperform loading a repository all at once | SWE-agent, RepoCoder, Agentless, and related public research |
| Build impact analysis | Build reverse dependencies and affected targets are part of the impact closure | Bazel Query, Nx affected |
| Test impact analysis | Coverage can map actual execution but cannot prove uncovered paths do not exist | Test Impact Analysis engineering practice |
| Software archaeology | Blame is only an entry point; also inspect content, paths, PRs, issues, and rollback history | Git documentation and software-evolution practice |

## References

- https://www.sei.cmu.edu/library/architecture-reconstruction-guidelines/
- https://www.sei.cmu.edu/library/views-and-beyond-collection/
- https://www.cs.ubc.ca/tr/1997/tr-97-15
- https://www.cs.wm.edu/~denys/pubs/JSME-FL-SurveyCRCV1.pdf
- https://docs.joern.io/code-property-graph/
- https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/
- https://bazel.build/query/guide
- https://opentelemetry.io/docs/concepts/context-propagation/
- https://aider.chat/docs/repomap.html
- https://glean.software/blog/incremental/
- https://git-scm.com/docs/git-blame
- https://martinfowler.com/articles/rise-test-impact-analysis.html

## Evidence boundary

The following are EDRU engineering conventions, not industry standards calibrated through a common benchmark:

- the C0–C4 confidence scale;
- the `survey`, `takeover`, and `change-ready` modes;
- phase gates and completion states;
- asset names and directory layout.

Continue calibrating these conventions across languages, repository sizes, and real change tasks.

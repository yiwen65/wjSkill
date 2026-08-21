# EDRU 方法来源与边界

本文件只在用户询问方法依据、研究来源或方法边界时加载。执行仓库理解时，以目标仓库证据为权威来源。

## 主要来源方向

| 方向 | 对 EDRU 的启发 | 代表资料 |
|---|---|---|
| 架构恢复 | 从实现提取事实并逐层聚合；同一系统需要多个视图 | SEI, Architecture Reconstruction Guidelines |
| 多视图架构 | 部署、模块、构建、运行和数据视图不能互相替代 | SEI, Views and Beyond |
| 设计与实现差异 | 同时维护 intended architecture 和 as-built architecture | Murphy, Notkin, Sullivan, Software Reflexion Models |
| Feature Location | 定位起点与确定完整影响范围是不同任务 | Dit et al., Feature Location in Source Code |
| 静态与动态分析 | 静态描述可能路径，动态只覆盖已执行输入与配置 | 程序分析与软件侦察相关研究 |
| 代码图谱 | 语法、符号、控制流和数据流适合作为事实层，不等于自动恢复业务架构 | Joern CPG, CodeQL, SCIP, Kythe, Glean |
| 仓库级 Agent | 迭代检索、层级定位、计划和工具接口优于一次性加载仓库 | SWE-agent、RepoCoder、Agentless 等公开研究 |
| 构建影响分析 | 构建反向依赖和 affected targets 是影响闭包的一部分 | Bazel Query, Nx affected |
| 测试影响分析 | 覆盖数据可提供实际执行映射，但不能证明未覆盖路径不存在 | Test Impact Analysis 工程实践 |
| 软件考古 | blame 只是入口，还需内容、路径、PR、Issue 和回滚历史 | Git 官方文档及软件演化实践 |

## 参考链接

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

## 证据边界

以下内容是 EDRU 的工程约定，不是经过统一基准校准的行业标准：

- C0–C4 置信度分级；
- `survey`、`takeover`、`change-ready` 三种模式；
- 阶段门禁和完成状态；
- 资产文件命名和目录结构。

这些约定应通过不同语言、仓库规模和真实变更任务持续校准。

# EDRU Repository Understanding

EDRU 用可追溯证据恢复大型或陌生仓库的可执行拓扑、关键链路、边界、状态和变更影响。核心规则与触发边界见 `SKILL.md`。

## 资源

- `references/takeover-protocol.md`：复杂接管和 `change-ready` 的执行检查点；
- `templates/`：按资产类型加载的输出模板；
- `schemas/`：manifest、claim、evidence 和 readiness 的机器校验契约；
- `examples/`：只在结构不清楚时参考的最小示例；
- `scripts/validate_edru_assets.py`：资产结构校验器；
- `evals/evals.json`：路由、权限和证据边界的行为评测场景；
- `references/method-sources.md`：仅用于解释方法来源与边界。

## 资产校验

```bash
python3 scripts/validate_edru_assets.py /path/to/.edru --mode takeover
```

校验通过只表示必要文件存在且基础格式可解析，不表示仓库结论真实。

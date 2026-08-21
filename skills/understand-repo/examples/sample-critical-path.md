# KP-001：HTTP 创建资源

## 场景定义

| 字段 | 内容 |
|---|---|
| Repository / Revision | example/repo @ abc123 |
| 参与者 | API Client |
| 外部刺激 | POST /v1/resources |
| 初始状态 | 目标 key 不存在 |
| Build target | //cmd:server |
| Runtime config | default |
| Feature flags | none |
| 预期最终状态 | 资源持久化，返回 201 |
| Oracle | HTTP 201 + 数据记录存在 |
| 运行证据 | 未执行 |

## 逐步链路

| 步骤 | 触发/调用者 | 组件与符号 | 输入 | 状态前→后 | 副作用 | 异常/超时/重试/降级 | Claim | 证据 | 置信度 |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | HTTP Router | `CreateHandler` | JSON body | 无变化 | 读取请求体 | body 过大返回 413 | CLM-001 | EV-001 | C2 |
| 2 | `CreateHandler` | `Service.Create` | Domain object | New→Validated | 校验 | 校验失败返回 400 | CLM-002 | EV-002 | C3 |
| 3 | `Service.Create` | `Repository.Insert` | Valid object | Absent→Stored | 数据库写入 | 冲突返回 409 | CLM-003 | EV-003 | C3 |

## MAY 与 OBSERVED 差异

| 关系 | 静态结果 | 运行结果 | 解释或未知 |
|---|---|---|---|
| Handler → Audit hook | MAY | 未观察 | 当前没有运行环境；保持待验证 |

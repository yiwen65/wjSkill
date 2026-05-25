#!/usr/bin/env python3
"""Generate a self-contained macOS disk cleanup checklist HTML file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


VALID_RISKS = {"low", "medium-low", "medium", "high"}


SAMPLE_DATA = {
    "title": "macOS 安全清理勾选列表",
    "intro": "选择你愿意清理的项目，页面只生成命令预览和清理报告脚本，不会执行删除。执行前请关闭相关应用、停止项目构建，并再次确认路径。",
    "disk": {
        "available": "686Gi 可用",
        "summary": "数据卷已用约 218Gi，总量 926Gi。推荐先清可再生成内容。"
    },
    "items": [
        {
            "path": "/Users/w/Projects/Example/.build",
            "type": "Swift/Xcode 构建产物。可再生成。",
            "sizeText": "12G",
            "sizeGiB": 12,
            "risk": "low",
            "riskText": "低",
            "recommended": True,
            "command": "rm -rf \"/Users/w/Projects/Example/.build\""
        },
        {
            "path": "/Users/w/Library/Developer/Xcode/iOS DeviceSupport/iPhone15,3 26.5 (23F77)",
            "type": "真机调试符号。再次调试该设备和系统版本时可能重新生成或下载。",
            "sizeText": "5.6G",
            "sizeGiB": 5.6,
            "risk": "medium",
            "riskText": "中",
            "recommended": False,
            "command": "rm -rf \"/Users/w/Library/Developer/Xcode/iOS DeviceSupport/iPhone15,3 26.5 (23F77)\""
        }
    ]
}


def load_data(args: argparse.Namespace) -> dict:
    if args.sample:
        return SAMPLE_DATA
    if not args.input:
        raise SystemExit("Provide --input candidates.json or --sample.")
    return json.loads(Path(args.input).read_text(encoding="utf-8"))


def validate_data(data: dict) -> None:
    if not isinstance(data.get("items"), list) or not data["items"]:
        raise SystemExit("Input JSON must contain a non-empty items array.")
    for index, item in enumerate(data["items"], start=1):
        missing = [key for key in ("path", "type", "sizeText", "sizeGiB", "risk", "riskText", "recommended", "command") if key not in item]
        if missing:
            raise SystemExit(f"Item {index} is missing required keys: {', '.join(missing)}")
        if item["risk"] not in VALID_RISKS:
            raise SystemExit(f"Item {index} has invalid risk: {item['risk']}")
        if "\n" in item["command"] or "\r" in item["command"]:
            raise SystemExit(f"Item {index} command must be a single line.")
        if not isinstance(item["recommended"], bool):
            raise SystemExit(f"Item {index} recommended must be true or false.")


def render_html(data: dict) -> str:
    title = data.get("title", "macOS 安全清理勾选列表")
    intro = data.get("intro", "选择你愿意清理的项目，页面只生成命令预览和清理报告脚本，不会执行删除。执行前请关闭相关应用、停止项目构建，并再次确认路径。")
    disk = data.get("disk", {})
    available = disk.get("available", "磁盘概况")
    summary = disk.get("summary", "请先完成只读盘点，再选择清理项。")
    items_json = json.dumps(data["items"], ensure_ascii=False)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --ink: #17212b; --muted: #5f6f7d; --line: #d9e1e7; --panel: #ffffff; --page: #f4f7f6;
      --green: #11735f; --green-soft: #dff4ee; --amber: #946200; --amber-soft: #fff0c2;
      --red: #a23b35; --red-soft: #f8dddd; --blue: #245b9a; --blue-soft: #e0edf9;
      --shadow-soft: 0 2px 0 rgba(23, 33, 43, 0.04);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; color: var(--ink);
      background: linear-gradient(135deg, rgba(255,255,255,.94), rgba(244,247,246,.84)),
        repeating-linear-gradient(90deg, rgba(23,33,43,.04) 0, rgba(23,33,43,.04) 1px, transparent 1px, transparent 32px);
      font-family: ui-sans-serif, "Avenir Next", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      letter-spacing: 0;
    }}
    .shell {{ max-width: 1320px; margin: 0 auto; padding: 26px 22px 44px; }}
    header {{ display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 22px; align-items: center; border-bottom: 1px solid var(--line); padding-bottom: 20px; }}
    h1 {{ margin: 0 0 10px; font-size: clamp(28px, 3vw, 40px); line-height: 1.05; font-weight: 760; }}
    .intro {{ margin: 0; color: var(--muted); max-width: 840px; line-height: 1.6; font-size: 15px; }}
    .disk {{ min-width: 300px; background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--green); box-shadow: var(--shadow-soft); padding: 16px 18px; }}
    .disk strong {{ display: block; font-size: 26px; line-height: 1; }}
    .disk span {{ display: block; color: var(--muted); margin-top: 8px; font-size: 13px; }}
    .toolbar {{ position: sticky; top: 0; z-index: 4; display: grid; grid-template-columns: 1fr auto; gap: 12px; align-items: center; margin: 18px 0 14px; padding: 10px; background: rgba(255,255,255,.94); backdrop-filter: blur(10px); border: 1px solid var(--line); box-shadow: var(--shadow-soft); }}
    .filters, .actions {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    button, .filter {{ min-height: 36px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); padding: 8px 12px; font: inherit; cursor: pointer; border-radius: 6px; transition: transform .16s ease, border-color .16s ease, background .16s ease; }}
    button:hover, .filter:hover {{ transform: translateY(-1px); border-color: #9fb2c1; }}
    button.primary {{ background: var(--ink); color: white; border-color: var(--ink); }}
    button.primary.is-done {{ background: var(--green); border-color: var(--green); }}
    .filter {{ display: inline-flex; gap: 7px; align-items: center; color: #314354; font-weight: 650; }}
    .filter:has(input:checked) {{ background: #edf8f3; border-color: #a9d7c8; color: #174b40; }}
    .filter input {{ margin: 0; }}
    .summary {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .metric {{ background: var(--panel); border: 1px solid var(--line); box-shadow: var(--shadow-soft); padding: 16px 18px; min-height: 96px; display: flex; flex-direction: column; justify-content: center; }}
    .metric b {{ display: block; font-size: 26px; line-height: 1; margin-bottom: 10px; }}
    .metric span {{ color: var(--muted); font-size: 13px; font-weight: 650; }}
    .metric:first-child {{ border-left: 4px solid var(--blue); }}
    .metric:nth-child(2) {{ border-left: 4px solid var(--green); }}
    .metric:nth-child(3) {{ border-left: 4px solid var(--amber); }}
    .layout {{ display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(340px, .65fr); gap: 18px; align-items: start; }}
    table {{ width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 0; background: var(--panel); border: 1px solid var(--line); box-shadow: var(--shadow-soft); overflow: hidden; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid var(--line); vertical-align: top; text-align: left; font-size: 14px; }}
    th {{ background: #edf3f4; color: #324657; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    th:nth-child(1), td:nth-child(1) {{ width: 52px; }}
    th:nth-child(2), td:nth-child(2) {{ width: 29%; }}
    th:nth-child(4), td:nth-child(4) {{ width: 92px; }}
    th:nth-child(5), td:nth-child(5) {{ width: 104px; }}
    th:nth-child(6), td:nth-child(6) {{ width: 100px; }}
    tr:last-child td {{ border-bottom: 0; }}
    tbody tr:hover td {{ background: #f8fbfa; }}
    tr[data-selected="true"] td {{ background: #fbfdfb; }}
    .checkcell input {{ width: 18px; height: 18px; accent-color: var(--green); }}
    .path {{ font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; color: #233442; }}
    .kind {{ color: var(--muted); line-height: 1.45; }}
    .size {{ white-space: nowrap; font-variant-numeric: tabular-nums; font-weight: 700; }}
    .risk {{ display: inline-flex; min-width: 56px; justify-content: center; border-radius: 999px; padding: 4px 8px; font-size: 12px; font-weight: 700; white-space: nowrap; }}
    .low {{ color: var(--green); background: var(--green-soft); }}
    .medium-low {{ color: var(--blue); background: var(--blue-soft); }}
    .medium {{ color: var(--amber); background: var(--amber-soft); }}
    .high {{ color: var(--red); background: var(--red-soft); }}
    .advice {{ font-weight: 700; color: #2d4a3f; }}
    .side {{ position: sticky; top: 86px; display: grid; gap: 14px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); box-shadow: var(--shadow-soft); padding: 16px; }}
    .panel h2 {{ margin: 0 0 10px; font-size: 16px; }}
    .confirm {{ display: flex; gap: 10px; align-items: flex-start; color: #324657; line-height: 1.55; font-size: 14px; }}
    .confirm input {{ margin-top: 4px; accent-color: var(--green); }}
    textarea {{ width: 100%; min-height: 260px; resize: vertical; border: 1px solid var(--line); border-radius: 6px; background: #101820; color: #eaf2ef; padding: 12px; font: 12px/1.6 ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }}
    textarea.copy-flash {{ animation: commandFlash 1.4s ease; }}
    @keyframes commandFlash {{ 0% {{ border-color: var(--green); box-shadow: 0 0 0 4px rgba(17,115,95,.18); }} 100% {{ border-color: var(--line); box-shadow: none; }} }}
    .note {{ margin: 10px 0 0; color: var(--muted); font-size: 13px; line-height: 1.55; }}
    .blocked-list {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.7; font-size: 13px; }}
    .toast {{ min-height: 20px; color: var(--green); font-size: 13px; margin-top: 8px; }}
    .feedback {{ position: fixed; right: 24px; top: 24px; z-index: 20; width: min(420px, calc(100vw - 32px)); padding: 14px 16px; border: 1px solid var(--line); border-left: 4px solid var(--green); border-radius: 8px; background: #fff; color: var(--ink); box-shadow: 0 22px 54px rgba(23,33,43,.2); font-weight: 750; line-height: 1.45; opacity: 0; pointer-events: none; transform: translateY(-14px); transition: opacity .18s ease, transform .18s ease; }}
    .feedback.show {{ opacity: 1; transform: translateY(0); }}
    .feedback.warn {{ border-left-color: var(--amber); background: #fffaf0; }}
    .feedback.error {{ border-left-color: var(--red); background: #fff6f5; }}
    @media (max-width: 980px) {{ header, .toolbar, .layout, .summary {{ grid-template-columns: 1fr; }} .side {{ position: static; }} .disk {{ min-width: 0; }} }}
    @media (max-width: 720px) {{ .shell {{ padding: 18px 12px 30px; }} table, thead, tbody, th, td, tr {{ display: block; }} thead {{ display: none; }} tr {{ border-bottom: 1px solid var(--line); }} td {{ border: 0; padding: 8px 12px; width: 100% !important; }} td::before {{ content: attr(data-label); display: block; color: var(--muted); font-size: 11px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: .08em; }} .checkcell::before {{ content: "选择"; }} }}
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <section><h1>{title}</h1><p class="intro">{intro}</p></section>
      <aside class="disk"><strong>{available}</strong><span>{summary}</span></aside>
    </header>
    <section class="toolbar" aria-label="筛选和批量操作">
      <div class="filters">
        <label class="filter"><input type="checkbox" id="showLow" checked> 低风险</label>
        <label class="filter"><input type="checkbox" id="showMediumLow" checked> 中低风险</label>
        <label class="filter"><input type="checkbox" id="showMedium" checked> 中风险</label>
        <label class="filter"><input type="checkbox" id="showHigh"> 较高风险</label>
      </div>
      <div class="actions">
        <button type="button" id="selectRecommended">选择推荐项</button>
        <button type="button" id="clearSelected">清空选择</button>
        <button type="button" id="copyCommands" class="primary">复制命令</button>
      </div>
    </section>
    <section class="summary" aria-label="选择摘要">
      <div class="metric"><b id="totalItems">0</b><span>总条目</span></div>
      <div class="metric"><b id="selectedCount">0</b><span>已选项目</span></div>
      <div class="metric"><b id="selectedSize">0B</b><span>预计释放</span></div>
    </section>
    <section class="layout">
      <table aria-label="可选择清理项">
        <thead><tr><th>选</th><th>路径</th><th>类型和影响</th><th>大小</th><th>风险</th><th>建议</th></tr></thead>
        <tbody id="items"></tbody>
      </table>
      <aside class="side">
        <section class="panel"><h2>执行前确认</h2><label class="confirm"><input type="checkbox" id="confirmed"><span>我已确认所选路径无个人文件、源码、密钥、账号数据、聊天记录、邮件、照片、文档或 iCloud 数据；相关应用和构建任务已关闭。</span></label><p class="note">未勾选确认时仍可预览命令，但不能复制。复制内容末尾会生成简短清理报告；页面不会运行任何命令。</p></section>
        <section class="panel"><h2>命令预览</h2><textarea id="commands" spellcheck="false" readonly></textarea><div class="toast" id="toast" role="status" aria-live="polite"></div></section>
        <section class="panel"><h2>不建议清理</h2><ul class="blocked-list"><li>不清理 Documents、Desktop、Pictures、Downloads 中的个人文件。</li><li>不清理 Mail、Messages、Keychains、iCloud、Safari 资料库和账号数据。</li><li>不直接删除整个 ~/Library/Caches 或整个 Simulator 设备目录。</li></ul></section>
      </aside>
    </section>
  </main>
  <div class="feedback" id="feedback" role="status" aria-live="polite"></div>
  <script>
    const cleanupItems = {items_json};
    const tbody = document.getElementById("items");
    const commands = document.getElementById("commands");
    const totalItems = document.getElementById("totalItems");
    const selectedCount = document.getElementById("selectedCount");
    const selectedSize = document.getElementById("selectedSize");
    const toast = document.getElementById("toast");
    const confirmed = document.getElementById("confirmed");
    const copyButton = document.getElementById("copyCommands");
    const feedback = document.getElementById("feedback");
    let feedbackTimer;
    const filters = {{ low: document.getElementById("showLow"), "medium-low": document.getElementById("showMediumLow"), medium: document.getElementById("showMedium"), high: document.getElementById("showHigh") }};
    function formatGiB(value) {{ if (value >= 10) return `${{Math.round(value)}}G`; if (value >= 1) return `${{value.toFixed(1).replace(/\\.0$/, "")}}G`; return `${{Math.round(value * 1024)}}M`; }}
    function shellQuote(value) {{ return "'" + String(value).replace(/'/g, "'\\\\''") + "'"; }}
    function buildReportBlock(selected, total) {{
      const selectedLines = selected.map((item, index) => {{
        const detail = `${{index + 1}}. ${{item.sizeText}} | ${{item.riskText}} | ${{item.path}} | ${{item.type}}`;
        return "  printf '%s\\n' " + shellQuote(detail);
      }});
      return [
        "# 生成简短清理报告（只读汇总）",
        "REPORT=\\"$HOME/disk-cleanup-report-$(date +%Y%m%d-%H%M%S).txt\\"",
        "{{",
        "  echo \\"macOS 磁盘清理报告\\"",
        "  echo \\"生成时间: $(date '+%Y-%m-%d %H:%M:%S')\\"",
        "  printf '%s\\n' " + shellQuote("预计释放: " + formatGiB(total)),
        "  echo",
        "  echo \\"清理后磁盘概况:\\"",
        "  df -h / /System/Volumes/Data 2>/dev/null || df -h /",
        "  echo",
        "  echo \\"本次选择的清理项:\\"",
        ...selectedLines,
        "}} > \\"$REPORT\\"",
        "echo \\"清理报告已生成: $REPORT\\""
      ].join("\\n");
    }}
    function renderRows() {{
      tbody.innerHTML = cleanupItems.map((item, index) => `
        <tr data-risk="${{item.risk}}" data-selected="false">
          <td class="checkcell" data-label="选择"><input type="checkbox" data-index="${{index}}" aria-label="选择 ${{item.path}}"></td>
          <td data-label="路径"><div class="path">${{item.path}}</div></td>
          <td data-label="类型和影响"><div class="kind">${{item.type}}</div></td>
          <td data-label="大小"><span class="size">${{item.sizeText}}</span></td>
          <td data-label="风险"><span class="risk ${{item.risk}}">${{item.riskText}}</span></td>
          <td data-label="建议"><span class="advice">${{item.recommended ? "建议清理" : "需单独确认"}}</span></td>
        </tr>`).join("");
      tbody.addEventListener("change", updateSummary);
    }}
    function getSelectedItems() {{ return Array.from(tbody.querySelectorAll("input:checked")).map(input => cleanupItems[Number(input.dataset.index)]); }}
    function updateSummary() {{
      const selected = getSelectedItems();
      const total = selected.reduce((sum, item) => sum + item.sizeGiB, 0);
      const commandLines = selected.map(item => item.command);
      totalItems.textContent = cleanupItems.length;
      selectedCount.textContent = selected.length;
      selectedSize.textContent = formatGiB(total);
      commands.value = commandLines.length ? commandLines.join("\\n") + "\\n\\n" + buildReportBlock(selected, total) : "请选择左侧清理项。";
      Array.from(tbody.querySelectorAll("tr")).forEach(row => {{ row.dataset.selected = String(row.querySelector("input").checked); }});
    }}
    function applyFilters() {{ Array.from(tbody.querySelectorAll("tr")).forEach(row => {{ row.style.display = filters[row.dataset.risk].checked ? "" : "none"; }}); }}
    function showFeedback(message, tone = "success") {{ window.clearTimeout(feedbackTimer); feedback.textContent = message; feedback.className = `feedback ${{tone}} show`; feedbackTimer = window.setTimeout(() => feedback.classList.remove("show"), 2600); }}
    function markCopySuccess() {{ const originalText = copyButton.textContent; copyButton.textContent = "已复制"; copyButton.classList.add("is-done"); commands.classList.remove("copy-flash"); void commands.offsetWidth; commands.classList.add("copy-flash"); window.setTimeout(() => {{ copyButton.textContent = originalText; copyButton.classList.remove("is-done"); commands.classList.remove("copy-flash"); }}, 1600); }}
    document.getElementById("selectRecommended").addEventListener("click", () => {{ Array.from(tbody.querySelectorAll("input")).forEach(input => {{ input.checked = cleanupItems[Number(input.dataset.index)].recommended; }}); updateSummary(); }});
    document.getElementById("clearSelected").addEventListener("click", () => {{ Array.from(tbody.querySelectorAll("input")).forEach(input => input.checked = false); updateSummary(); }});
    copyButton.addEventListener("click", async () => {{
      toast.textContent = "";
      if (!getSelectedItems().length) {{ toast.textContent = "没有可复制的命令。"; showFeedback("没有可复制的命令：请先勾选清理项。", "warn"); return; }}
      if (!confirmed.checked) {{ toast.textContent = "请先勾选执行前确认，再复制命令。"; showFeedback("请先勾选执行前确认，再复制命令。", "warn"); return; }}
      try {{ await navigator.clipboard.writeText(commands.value); toast.textContent = "已复制命令和报告生成脚本。请粘贴到终端前再次核对。"; markCopySuccess(); showFeedback("命令已复制，末尾会自动生成简短清理报告。"); }}
      catch {{ commands.select(); toast.textContent = "浏览器未允许自动复制，已选中命令文本。"; showFeedback("浏览器未允许自动复制，已帮你选中命令文本。", "error"); }}
    }});
    Object.values(filters).forEach(input => input.addEventListener("change", applyFilters));
    renderRows(); updateSummary(); applyFilters();
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Path to candidate JSON.")
    parser.add_argument("--output", required=True, help="Path to write HTML.")
    parser.add_argument("--sample", action="store_true", help="Use built-in sample data.")
    args = parser.parse_args()

    data = load_data(args)
    validate_data(data)
    output = Path(args.output)
    output.write_text(render_html(data), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

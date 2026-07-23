#!/usr/bin/env python3
"""
cron 状态仪表盘
检查所有 cron 任务的状态，输出 HTML / Markdown 仪表盘
"""

import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


WORKSPACE = Path("/Users/fengyue/.qclaw/workspace-agent-71243473")
OUTPUT_DIR = WORKSPACE / "finance" / "dashboards"


OPENCLAW_BIN = "/Users/fengyue/Library/Application Support/QClaw/openclaw/config/bin/openclaw"


def fetch_cron_list():
    """通过 gateway CLI 列出 cron"""
    try:
        result = subprocess.run(
            [OPENCLAW_BIN, "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        # CLI 把 proxy-bootstrap warning 也打到 stdout，需要从 { 开始解析
        text = result.stdout + result.stderr
        start = text.find("{")
        if start == -1:
            return None
        try:
            return json.loads(text[start:])
        except Exception:
            return None
    except Exception as e:
        return None


def parse_next_run(next_run_ms):
    if not next_run_ms:
        return "N/A"
    dt = datetime.fromtimestamp(next_run_ms / 1000)
    now = datetime.now()
    diff = dt - now
    if diff.days > 0:
        return f"{dt.strftime('%Y-%m-%d %H:%M')}（{diff.days} 天后）"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{dt.strftime('%m-%d %H:%M')}（{hours} 小时后）"
    elif diff.seconds > 0:
        minutes = diff.seconds // 60
        return f"{dt.strftime('%H:%M')}（{minutes} 分钟后）"
    else:
        return f"{dt.strftime('%Y-%m-%d %H:%M')}（已到期）"


def render_markdown(jobs_data):
    jobs = jobs_data.get("jobs", [])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append(f"# cron 状态仪表盘")
    lines.append("")
    lines.append(f"> 生成时间：{now}")
    lines.append(f"> 任务总数：{len(jobs)} 个")
    lines.append("")

    lines.append("## 一、任务清单")
    lines.append("")
    lines.append("| 状态 | 名称 | 触发时机 | 下次执行 | 备注 |")
    lines.append("|---|---|---|---|---|")

    for job in jobs:
        enabled = "🟢" if job.get("enabled") else "🔴"
        name = job.get("name", "未命名")
        schedule = job.get("schedule", {})
        kind = schedule.get("kind", "")
        if kind == "cron":
            expr = schedule.get("expr", "")
            tz = schedule.get("tz", "")
            schedule_str = f"`{expr}` ({tz})"
        elif kind == "at":
            at = schedule.get("at", "")
            schedule_str = f"at {at}"
        else:
            schedule_str = str(schedule)

        next_run = parse_next_run(job.get("state", {}).get("nextRunAtMs"))
        delete_after = "🗑️ 一次性" if job.get("deleteAfterRun") else "🔁 循环"
        lines.append(f"| {enabled} | {name} | {schedule_str} | {next_run} | {delete_after} |")

    lines.append("")

    # 按触发时间排序
    lines.append("## 二、执行时间轴")
    lines.append("")
    upcoming = []
    for job in jobs:
        next_run_ms = job.get("state", {}).get("nextRunAtMs")
        if next_run_ms and job.get("enabled"):
            dt = datetime.fromtimestamp(next_run_ms / 1000)
            upcoming.append((dt, job.get("name")))

    upcoming.sort()
    if upcoming:
        for dt, name in upcoming[:10]:
            days_left = (dt - datetime.now()).days
            if days_left == 0:
                marker = "🔥 今天"
            elif days_left == 1:
                marker = "⏰ 明天"
            elif days_left <= 7:
                marker = f"📅 {days_left} 天后"
            else:
                marker = f"📆 {dt.strftime('%m-%d')}"
            lines.append(f"- {marker} **{dt.strftime('%Y-%m-%d %H:%M')}** — {name}")
    else:
        lines.append("- 暂无即将执行的任务")

    lines.append("")

    lines.append("## 三、运维建议")
    lines.append("")
    enabled_count = sum(1 for j in jobs if j.get("enabled"))
    lines.append(f"- 当前启用任务：{enabled_count}/{len(jobs)}")
    if enabled_count < len(jobs):
        lines.append(f"- ⚠️ 有 {len(jobs) - enabled_count} 个任务被禁用，建议确认是否仍需要")
    lines.append("- 💡 每个 cron 任务都设置 bestEffort=true，失败不影响其他任务")
    lines.append("- 💡 临时关闭某个任务：编辑 → enabled=false")
    lines.append("- 💡 立即触发：openclaw cron run --jobId <id>")

    return "\n".join(lines)


def render_html(jobs_data):
    md = render_markdown(jobs_data)
    md_escaped = md.replace("<", "&lt;").replace(">", "&gt;")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>cron 状态仪表盘</title>
    <style>
        body {{ font-family: -apple-system, "PingFang SC", sans-serif; background: #f8f9fa; color: #1a1a2e; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ color: #0066ff; }}
        h2 {{ color: #1a1a2e; margin-top: 32px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        th {{ background: #0066ff; color: #fff; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; font-size: 0.9rem; }}
        tr:hover {{ background: #f8f9fa; }}
        pre {{ background: #1a1a2e; color: #10b981; padding: 20px; border-radius: 6px; overflow-x: auto; }}
        code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
        .meta {{ color: #6b7280; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⏰ cron 状态仪表盘</h1>
        <p class="meta">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>任务总览</h2>
        <table>
            <thead>
                <tr><th>状态</th><th>名称</th><th>触发时机</th><th>下次执行</th></tr>
            </thead>
            <tbody>"""

    jobs = jobs_data.get("jobs", [])
    for job in jobs:
        enabled = "🟢" if job.get("enabled") else "🔴"
        schedule = job.get("schedule", {})
        kind = schedule.get("kind", "")
        if kind == "cron":
            expr = schedule.get("expr", "")
            tz = schedule.get("tz", "")
            schedule_str = f"<code>{expr}</code> ({tz})"
        elif kind == "at":
            schedule_str = f"at {schedule.get('at', '')}"
        else:
            schedule_str = str(schedule)

        next_run = parse_next_run(job.get("state", {}).get("nextRunAtMs"))
        html += f"""
                <tr>
                    <td>{enabled}</td>
                    <td><strong>{job.get('name', '')}</strong></td>
                    <td>{schedule_str}</td>
                    <td>{next_run}</td>
                </tr>"""

    html += """
            </tbody>
        </table>

        <h2>原始 Markdown</h2>
        <pre>""" + md_escaped + """</pre>
    </div>
</body>
</html>"""

    return html


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    jobs_data = fetch_cron_list()
    if not jobs_data:
        print("❌ 无法获取 cron 列表（请检查 openclaw CLI）")
        return

    md = render_markdown(jobs_data)
    md_path = OUTPUT_DIR / "cron_dashboard.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    html = render_html(jobs_data)
    html_path = OUTPUT_DIR / "cron_dashboard.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    jobs = jobs_data.get("jobs", [])
    print(f"")
    print(f"✅ cron 仪表盘生成完成")
    print(f"📊 任务总数：{len(jobs)} 个")
    print(f"")
    print(f"📄 Markdown：{md_path}")
    print(f"📄 HTML：{html_path}")
    print(f"")
    print(f"📅 最近 3 个即将触发的任务：")
    upcoming = []
    for job in jobs:
        next_run_ms = job.get("state", {}).get("nextRunAtMs")
        if next_run_ms and job.get("enabled"):
            dt = datetime.fromtimestamp(next_run_ms / 1000)
            upcoming.append((dt, job.get("name")))
    upcoming.sort()
    for dt, name in upcoming[:3]:
        days_left = (dt - datetime.now()).days
        print(f"   - {dt.strftime('%Y-%m-%d %H:%M')} ({days_left} 天后): {name}")


if __name__ == "__main__":
    main()
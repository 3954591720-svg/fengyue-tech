#!/usr/bin/env python3
"""
周报自动生成器
读取 finance/pomodoro.json + git log 生成周报
用法：
  python3 weekly_report.py                    # 本周周报
  python3 weekly_report.py 2026 7 21          # 指定周（年 月 日）
"""

import sys
import os
import json
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path


WORKSPACE = Path("/Users/fengyue/.qclaw/workspace-agent-71243473")
POMODORO_FILE = WORKSPACE / "finance" / "pomodoro.json"
REPORTS_DIR = WORKSPACE / "finance" / "weekly_reports"


def get_week_range(year, month, day):
    """返回该日期所在周的周一~周日"""
    d = date(year, month, day)
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_git_log(start_date, end_date):
    """获取指定日期范围的 git commit 记录"""
    since = start_date.isoformat()
    until = (end_date + timedelta(days=1)).isoformat()
    result = subprocess.run(
        ["git", "-C", str(WORKSPACE),
         "log", f"--since={since}", f"--until={until}",
         "--pretty=format:%h %s"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    commits = []
    for line in result.stdout.strip().split("\n"):
        if line:
            commits.append(line)
    return commits


def get_pomodoro_data(start_date, end_date):
    """获取指定日期范围的番茄数据"""
    if not POMODORO_FILE.exists():
        return {"total": 0, "minutes": 0, "by_project": {}, "by_day": {}}

    with open(POMODORO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    sessions = data.get("sessions", [])
    week_sessions = [s for s in sessions
                     if start_date.isoformat() <= s["start_time"][:10] <= end_date.isoformat()]

    total_minutes = sum(s["actual_minutes"] for s in week_sessions)
    by_project = {}
    by_day = {}

    for s in week_sessions:
        p = s["project"]
        if p not in by_project:
            by_project[p] = {"count": 0, "minutes": 0}
        by_project[p]["count"] += 1
        by_project[p]["minutes"] += s["actual_minutes"]

        d = s["start_time"][:10]
        if d not in by_day:
            by_day[d] = 0
        by_day[d] += s["actual_minutes"]

    return {
        "total": len(week_sessions),
        "minutes": total_minutes,
        "by_project": by_project,
        "by_day": by_day,
    }


def generate_report(year, month, day):
    monday, sunday = get_week_range(year, month, day)

    commits = get_git_log(monday, sunday)
    pomodoro = get_pomodoro_data(monday, sunday)

    lines = []
    lines.append(f"# 周报 — {monday.strftime('%Y-%m-%d')} ~ {sunday.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> 报告人：丰悦")
    lines.append("")

    # 本周概览
    lines.append("## 一、本周概览")
    lines.append("")
    lines.append(f"- 📅 周一：{monday.strftime('%m-%d')} 周日：{sunday.strftime('%m-%d')}")
    lines.append(f"- 🍅 番茄总数：{pomodoro['total']} 个")
    lines.append(f"- ⏱️  总专注时长：{pomodoro['minutes']:.0f} 分钟 ({pomodoro['minutes']/60:.1f} 小时)")
    lines.append(f"- 📦 代码提交：{len(commits)} 个 commit")
    lines.append("")

    # 完成事项（基于 commit）
    if commits:
        lines.append("## 二、完成事项（按 commit 提炼）")
        lines.append("")
        for c in commits[:20]:  # 最多展示 20 条
            hash_short, *msg_parts = c.split(" ", 1)
            msg = msg_parts[0] if msg_parts else ""
            lines.append(f"- `{hash_short}` {msg}")
        if len(commits) > 20:
            lines.append(f"- ... 还有 {len(commits) - 20} 个 commit")
        lines.append("")

    # 时间分配
    if pomodoro["by_project"]:
        lines.append("## 三、时间分配")
        lines.append("")
        lines.append("| 项目 | 番茄数 | 时长 |")
        lines.append("|---|---:|---:|")
        for project, info in sorted(pomodoro["by_project"].items(), key=lambda x: -x[1]["minutes"]):
            lines.append(f"| {project} | {info['count']} | {info['minutes']:.0f} 分钟 |")
        lines.append("")

    # 按天
    if pomodoro["by_day"]:
        lines.append("## 四、按天分布")
        lines.append("")
        lines.append("| 日期 | 时长 | 分布 |")
        lines.append("|---|---:|---|")
        current = monday
        while current <= sunday:
            mins = pomodoro["by_day"].get(current.isoformat(), 0)
            bar = "█" * int(mins / 5) if mins > 0 else ""
            lines.append(f"| {current.isoformat()} | {mins:.0f} 分钟 | {bar} |")
            current += timedelta(days=1)
        lines.append("")

    # 下周计划（占位）
    lines.append("## 五、下周计划")
    lines.append("")
    lines.append("- [ ] 待填：本周最关键的 3-5 件事")
    lines.append("- [ ] 待填：已识别的风险/障碍")
    lines.append("- [ ] 待填：下周要推进的核心项目")
    lines.append("")

    # 反思
    lines.append("## 六、反思")
    lines.append("")
    lines.append("- **本周做对了什么**：待填")
    lines.append("- **本周做错了什么**：待填")
    lines.append("- **下周要改变什么**：待填")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*自动生成（{datetime.now().strftime('%Y-%m-%d %H:%M')}）。代码提交基于 git log，专注时长基于番茄钟数据。*")

    return "\n".join(lines)


def main():
    if len(sys.argv) >= 4:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
    else:
        today = date.today()
        year = today.year
        month = today.month
        day = today.day

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    monday, sunday = get_week_range(year, month, day)
    report = generate_report(year, month, day)

    output_path = REPORTS_DIR / f"周报_{monday.isoformat()}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"")
    print(f"✅ 周报生成完成")
    print(f"📅 {monday} ~ {sunday}")
    print(f"📄 文件：{output_path}")
    print(f"")


if __name__ == "__main__":
    main()
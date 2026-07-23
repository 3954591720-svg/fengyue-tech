#!/usr/bin/env python3
"""
番茄钟 + 项目时间追踪
用法：
  python3 pomodoro.py start "项目名"          # 启动 25 分钟专注
  python3 pomodoro.py break 5                # 启动 5 分钟休息
  python3 pomodoro.py status                  # 查看当前状态
  python3 pomodoro.py stop                    # 停止并记录
  python3 pomodoro.py report                  # 本周报表
  python3 pomodoro.py report 2026 7           # 指定月份报表
"""

import sys
import os
import json
import time
import signal
from datetime import datetime, date, timedelta
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "finance"
DATA_FILE = DATA_DIR / "pomodoro.json"


def load_data():
    if not DATA_FILE.exists():
        return {"sessions": [], "current": None}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def countdown(minutes, label):
    """带提示的倒计时"""
    seconds = minutes * 60
    end_time = time.time() + seconds
    try:
        while True:
            remaining = int(end_time - time.time())
            if remaining <= 0:
                break
            mins, secs = divmod(remaining, 60)
            print(f"\r⏱️  {label} — 剩余 {mins:02d}:{secs:02d}", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        elapsed = minutes * 60 - remaining
        return elapsed
    print(f"\r✅ {label} — 完成！                    ")
    return seconds


def cmd_start(project):
    data = load_data()

    if data.get("current"):
        print(f"⚠️  已有进行中的会话：{data['current']['project']}")
        print(f"   开始于 {data['current']['start_time']}")
        print(f"   请先 stop 再开新会话")
        return

    minutes = 25
    print(f"🍅 番茄钟启动 — {project}")
    print(f"   时长：{minutes} 分钟")
    print(f"   提示：Ctrl+C 可随时结束（会自动记录已完成时间）")
    print("")

    start_dt = datetime.now()
    elapsed = countdown(minutes, f"专注：{project}")

    end_dt = datetime.now()
    actual_minutes = elapsed / 60

    # 记录
    session = {
        "project": project,
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "planned_minutes": minutes,
        "actual_minutes": round(actual_minutes, 2),
        "completed": elapsed >= seconds_of(minutes),
        "type": "focus",
    }

    data["sessions"].append(session)
    data["current"] = None
    save_data(data)

    print(f"")
    print(f"✅ 已记录：{actual_minutes:.1f} 分钟")
    if elapsed < seconds_of(minutes):
        print(f"   ⚠️  未完成完整 {minutes} 分钟")
    else:
        print(f"   🎉 完成一个完整番茄！")
    print(f"")
    print(f"💡 休息 5 分钟后再启动下一个")


def seconds_of(minutes):
    return minutes * 60


def cmd_break(minutes=5):
    minutes = int(minutes) if minutes else 5
    print(f"☕ 休息开始 — {minutes} 分钟")
    countdown(minutes, f"休息")
    print(f"✅ 休息结束，回到工作！")


def cmd_status():
    data = load_data()
    if not data.get("current"):
        print("当前无进行中的番茄")
        return
    cur = data["current"]
    print(f"🍅 当前番茄：{cur['project']}")
    print(f"   开始于 {cur['start_time']}")
    elapsed = (datetime.now() - datetime.fromisoformat(cur["start_time"])).total_seconds() / 60
    print(f"   已进行：{elapsed:.1f} 分钟")


def cmd_stop():
    data = load_data()
    if not data.get("current"):
        print("⚠️  当前无进行中的番茄")
        return

    cur = data["current"]
    end_dt = datetime.now()
    elapsed = (end_dt - datetime.fromisoformat(cur["start_time"])).total_seconds() / 60

    session = {
        "project": cur["project"],
        "start_time": cur["start_time"],
        "end_time": end_dt.isoformat(),
        "planned_minutes": cur["planned_minutes"],
        "actual_minutes": round(elapsed, 2),
        "completed": False,
        "type": "focus",
        "stopped_manually": True,
    }

    data["sessions"].append(session)
    data["current"] = None
    save_data(data)

    print(f"⏹️  已停止：{cur['project']}")
    print(f"   记录 {elapsed:.1f} 分钟")


def cmd_report(year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    data = load_data()
    sessions = [s for s in data["sessions"] if s["start_time"].startswith(f"{year:04d}-{month:02d}")]

    if not sessions:
        print(f"⚠️  {year} 年 {month} 月无记录")
        return

    total_minutes = sum(s["actual_minutes"] for s in sessions)
    total_sessions = len(sessions)
    completed = sum(1 for s in sessions if s.get("completed"))

    # 按项目聚合
    by_project = {}
    for s in sessions:
        p = s["project"]
        if p not in by_project:
            by_project[p] = {"count": 0, "minutes": 0}
        by_project[p]["count"] += 1
        by_project[p]["minutes"] += s["actual_minutes"]

    # 按天聚合
    by_day = {}
    for s in sessions:
        d = s["start_time"][:10]
        if d not in by_day:
            by_day[d] = 0
        by_day[d] += s["actual_minutes"]

    print(f"")
    print(f"📊 番茄钟报表 — {year} 年 {month} 月")
    print(f"")
    print(f"总番茄数：{total_sessions}")
    print(f"总时长：{total_minutes:.1f} 分钟 ({total_minutes/60:.1f} 小时)")
    print(f"完成率：{completed/total_sessions*100:.0f}% ({completed}/{total_sessions})")
    print(f"")
    print(f"📁 按项目：")
    print(f"")
    for project, info in sorted(by_project.items(), key=lambda x: -x[1]["minutes"]):
        print(f"  {project}: {info['count']} 个番茄 / {info['minutes']:.0f} 分钟 ({info['minutes']/60:.1f} 小时)")
    print(f"")
    print(f"📅 按天：")
    for d in sorted(by_day.keys()):
        mins = by_day[d]
        bar = "█" * int(mins / 5)
        print(f"  {d}: {mins:5.1f} 分钟 {bar}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "start":
        if len(sys.argv) < 3:
            print("用法：python3 pomodoro.py start <项目名>")
            return
        project = " ".join(sys.argv[2:])
        cmd_start(project)

    elif cmd == "break":
        minutes = sys.argv[2] if len(sys.argv) > 2 else "5"
        cmd_break(minutes)

    elif cmd == "status":
        cmd_status()

    elif cmd == "stop":
        cmd_stop()

    elif cmd == "report":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else None
        month = int(sys.argv[3]) if len(sys.argv) > 3 else None
        cmd_report(year, month)

    else:
        print(f"未知命令：{cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
备案号下来后自动更新网站脚本
用法：
  python3 update_icp.py                       # 自动 git commit
  python3 update_icp.py --commit "msg"        # 自定义提交信息
"""

import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path


WORKSPACE = Path("/Users/fengyue/.qclaw/workspace-agent-71243473")
INDEX_HTML = WORKSPACE / "index.html"
CASES_HTML = WORKSPACE / "cases.html"
PRIVACY_HTML = WORKSPACE / "privacy-policy.html"
TERMS_HTML = WORKSPACE / "terms.html"

# 当前占位符
ICP_PLACEHOLDER = "陕ICP备XXXXXXXX号-1"
SECURITY_PLACEHOLDER = "陕公网安备 XXXXXXXXXXXXXXX 号"


def update_file(file_path, replacements):
    """在指定文件中做占位符替换"""
    if not file_path.exists():
        print(f"⚠️  文件不存在：{file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)

    if content == original:
        print(f"   {file_path.name}: 无需更新")
        return False

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"   ✅ {file_path.name}: 已更新")
    return True


def update_all(icp_no=None, security_no=None, push=True):
    if not icp_no and not security_no:
        print("⚠️  请提供备案号或公网安备号")
        return False

    print(f"")
    print(f"🔄 开始更新网站备案信息...")
    print(f"")

    replacements = {}
    if icp_no:
        replacements[ICP_PLACEHOLDER] = icp_no
        # 安全备案号前两位需与 ICP 一致
        if not security_no and icp_no.startswith("陕ICP备"):
            # 自动推测：陕ICP备{icp_no}号-1 → 陕公网安备 {icp_no省简称}xxxxxxxxxxxxx 号
            print(f"   ⚠️  公网安备号需手动提供，请运行：")
            print(f"       python3 update_icp.py --icp {icp_no} --security '陕公网安备 610XXXXXXXXXXXXX 号'")
    if security_no:
        replacements[SECURITY_PLACEHOLDER] = security_no

    files_updated = []
    for f in [INDEX_HTML, CASES_HTML, PRIVACY_HTML, TERMS_HTML]:
        if update_file(f, replacements):
            files_updated.append(f.name)

    if not files_updated:
        print(f"")
        print(f"✅ 全部文件已是最新备案号，无需更新")
        return True

    print(f"")
    print(f"📝 已更新文件：")
    for name in files_updated:
        print(f"   - {name}")

    if push:
        commit_and_push(files_updated)
    else:
        print(f"")
        print(f"💡 文件已修改，请手动 git add + commit + push")

    return True


def commit_and_push(files):
    print(f"")
    print(f"📦 提交并推送...")

    # git add
    subprocess.run(["git", "-C", str(WORKSPACE), "add"] + [str(WORKSPACE / f) for f in files], check=True)

    # commit
    commit_msg = f"chore: 更新备案号 ({datetime.now().strftime('%Y-%m-%d')})"
    result = subprocess.run(
        ["git", "-C", str(WORKSPACE),
         "-c", "user.email=3954591720@qq.com",
         "-c", "user.name=fengyue",
         "commit", "-m", commit_msg],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"   ⚠️  commit 失败：{result.stderr}")
        return False

    print(f"   ✅ commit: {commit_msg}")

    # push
    subprocess.run(
        ["git", "-C", str(WORKSPACE), "config", "http.version", "HTTP/1.1"],
        check=False
    )
    result = subprocess.run(
        ["git", "-C", str(WORKSPACE), "push", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"   ⚠️  push 失败：{result.stderr}")
        return False

    print(f"   ✅ push 成功")
    print(f"")
    print(f"🌐 网站将在 1-2 分钟内自动重新部署")
    print(f"   https://fengyue-tech.vercel.app")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="更新网站备案号")
    parser.add_argument("--icp", help="ICP 备案号，例如：陕ICP备2026000001号-1")
    parser.add_argument("--security", help="公网安备号，例如：陕公网安备 61030000000001 号")
    parser.add_argument("--no-push", action="store_true", help="只更新文件，不提交推送")
    args = parser.parse_args()

    if not args.icp and not args.security:
        parser.print_help()
        print("")
        print("示例：")
        print('  python3 update_icp.py --icp "陕ICP备2026000001号-1" --security "陕公网安备 61030200000001 号"')
        return

    update_all(icp_no=args.icp, security_no=args.security, push=not args.no_push)


if __name__ == "__main__":
    main()
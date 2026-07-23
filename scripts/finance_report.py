#!/usr/bin/env python3
"""
财务月度报表生成器
读取 finance/records.csv 生成 Markdown / HTML / PDF 报表
"""

import os
import sys
import csv
from datetime import datetime, date
from pathlib import Path


FINANCE_DIR = Path(__file__).parent.parent / "finance"
RECORDS_FILE = FINANCE_DIR / "records.csv"
OUTPUT_DIR = FINANCE_DIR / "reports"


def ensure_dirs():
    FINANCE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not RECORDS_FILE.exists():
        # 写入示例表头
        with open(RECORDS_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "日期", "类型", "客户/供应商", "项目/科目",
                "金额", "付款方式", "发票号", "状态", "备注"
            ])
        print(f"✅ 已创建账本文件：{RECORDS_FILE}")
        print("   请按以下列添加记录：日期,类型,客户/供应商,项目/科目,金额,付款方式,发票号,状态,备注")
        print("")
        print("   示例：")
        print("   2026-07-24,收入,某教育公司,智能客服系统,28000,银行转账,20260724001,已收款,首付款 50%")
        print("   2026-07-24,支出,腾讯云,云服务器,60,自动扣款,,已支付,7月份服务器费")


def load_records():
    if not RECORDS_FILE.exists():
        return []
    records = []
    with open(RECORDS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["金额"] = float(row["金额"] or 0)
            records.append(row)
    return records


def filter_by_month(records, year, month):
    return [r for r in records if r["日期"].startswith(f"{year:04d}-{month:02d}")]


def calc_summary(records):
    income = [r for r in records if r["类型"] == "收入" and r["状态"] == "已收款"]
    expense = [r for r in records if r["类型"] == "支出" and r["状态"] == "已支付"]
    receivable = [r for r in records if r["类型"] == "收入" and r["状态"] == "应收未收"]
    payable = [r for r in records if r["类型"] == "支出" and r["状态"] == "应付未付"]

    income_total = sum(r["金额"] for r in income)
    expense_total = sum(r["金额"] for r in expense)
    receivable_total = sum(r["金额"] for r in receivable)
    payable_total = sum(r["金额"] for r in payable)

    return {
        "收入已收": (income_total, len(income)),
        "支出已付": (expense_total, len(expense)),
        "应收未收": (receivable_total, len(receivable)),
        "应付未付": (payable_total, len(payable)),
        "净利润": (income_total - expense_total, 0),
    }


def generate_markdown(year, month, records, summary):
    lines = []
    lines.append(f"# 财务报表 — {year} 年 {month} 月")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # 总览
    lines.append("## 一、收支总览")
    lines.append("")
    lines.append("| 项目 | 金额（元） | 笔数 |")
    lines.append("|---|---:|---:|")
    for k, (amount, count) in summary.items():
        lines.append(f"| {k} | {amount:,.2f} | {count} |")
    lines.append("")

    # 收入明细
    income_records = [r for r in records if r["类型"] == "收入"]
    if income_records:
        lines.append("## 二、收入明细")
        lines.append("")
        lines.append("| 日期 | 客户 | 项目 | 金额 | 方式 | 发票号 | 状态 | 备注 |")
        lines.append("|---|---|---|---:|---|---|---|---|")
        for r in sorted(income_records, key=lambda x: x["日期"]):
            lines.append(f"| {r['日期']} | {r['客户/供应商']} | {r['项目/科目']} | {r['金额']:,.2f} | {r['付款方式']} | {r['发票号']} | {r['状态']} | {r['备注']} |")
        lines.append("")

    # 支出明细
    expense_records = [r for r in records if r["类型"] == "支出"]
    if expense_records:
        lines.append("## 三、支出明细")
        lines.append("")
        lines.append("| 日期 | 供应商 | 科目 | 金额 | 方式 | 发票号 | 状态 | 备注 |")
        lines.append("|---|---|---|---:|---|---|---|---|")
        for r in sorted(expense_records, key=lambda x: x["日期"]):
            lines.append(f"| {r['日期']} | {r['客户/供应商']} | {r['项目/科目']} | {r['金额']:,.2f} | {r['付款方式']} | {r['发票号']} | {r['状态']} | {r['备注']} |")
        lines.append("")

    # 待收/待付
    if summary["应收未收"][0] > 0 or summary["应付未付"][0] > 0:
        lines.append("## 四、待收/待付提醒")
        lines.append("")
        lines.append(f"- 🟡 待收：¥{summary['应收未收'][0]:,.2f}（{summary['应收未收'][1]} 笔）")
        lines.append(f"- 🟡 待付：¥{summary['应付未付'][0]:,.2f}（{summary['应付未付'][1]} 笔）")
        lines.append("")
        lines.append("**催收建议**：本周内邮件/微信提醒对应客户。")
        lines.append("**待付**：月初/月末集中处理，避免违约。")
        lines.append("")

    # 建议
    lines.append("## 五、本月经营建议")
    lines.append("")
    profit = summary["净利润"][0]
    if profit > 0:
        rate = (summary["收入已收"][0] - summary["支出已付"][0]) / max(summary["收入已收"][0], 1) * 100
        lines.append(f"- ✅ 本月盈利 ¥{profit:,.2f}，利润率 {rate:.1f}%")
    else:
        lines.append(f"- ⚠️ 本月亏损 ¥{abs(profit):,.2f}，建议分析原因")
    lines.append(f"- 📊 本月完成 {summary['收入已收'][1]} 笔收款，{summary['支出已付'][1]} 笔付款")
    lines.append(f"- 💰 应收账款 ¥{summary['应收未收'][0]:,.2f}，建议 7 天内催收")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*本报表由脚本自动生成，最终数据以银行流水为准。*")

    return "\n".join(lines)


def generate_html(year, month, records, summary):
    profit = summary["净利润"][0]
    profit_color = "#10b981" if profit > 0 else "#ef4444"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>财务报表 - {year} 年 {month} 月</title>
    <style>
        body {{ font-family: -apple-system, "PingFang SC", sans-serif; background: #f8f9fa; color: #1a1a2e; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ color: #0066ff; margin-bottom: 8px; }}
        .meta {{ color: #6b7280; margin-bottom: 32px; }}
        h2 {{ color: #1a1a2e; margin-top: 32px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        th {{ background: #0066ff; color: #fff; padding: 12px; text-align: left; font-size: 0.9rem; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; font-size: 0.9rem; }}
        tr:hover {{ background: #f8f9fa; }}
        .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .profit {{ color: {profit_color}; font-weight: 700; font-size: 1.2rem; }}
        .alert {{ background: #fef3c7; padding: 16px; border-radius: 6px; margin: 16px 0; }}
        .positive {{ background: #d1fae5; padding: 16px; border-radius: 6px; margin: 16px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>财务报表 — {year} 年 {month} 月</h1>
        <p class="meta">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>一、收支总览</h2>
        <table>
            <thead><tr><th>项目</th><th class="num">金额（元）</th><th class="num">笔数</th></tr></thead>
            <tbody>"""

    for k, (amount, count) in summary.items():
        html += f"<tr><td>{k}</td><td class='num'>{amount:,.2f}</td><td class='num'>{count}</td></tr>"

    html += f"""
            </tbody>
        </table>
        <p>净利润：<span class='profit'>¥{profit:,.2f}</span></p>

        <div class='positive'>
            <h2>二、本月总结</h2>
            <p>本月完成 <strong>{summary['收入已收'][1]}</strong> 笔收款，<strong>{summary['支出已付'][1]}</strong> 笔付款。</p>
            <p>应收账款：<strong>¥{summary['应收未收'][0]:,.2f}</strong>（{summary['应收未收'][1]} 笔）</p>
            <p>应付账款：<strong>¥{summary['应付未付'][0]:,.2f}</strong>（{summary['应付未付'][1]} 笔）</p>
        </div>

        <h2>三、明细数据</h2>
        <p>详细明细请查看 Markdown 版本报表，包含所有收支流水。</p>

        <p style="margin-top: 40px; text-align: center; color: #9ca3af; font-size: 0.85rem;">
            本报表由脚本自动生成，最终数据以银行流水为准
        </p>
    </div>
</body>
</html>"""
    return html


def main():
    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    else:
        now = datetime.now()
        year = now.year
        month = now.month

    ensure_dirs()
    all_records = load_records()
    if not all_records:
        print("⚠️ 暂无财务记录")
        print(f"   请编辑 {RECORDS_FILE} 添加记录后重跑")
        return

    records = filter_by_month(all_records, year, month)
    if not records:
        print(f"⚠️ {year} 年 {month} 月无记录")
        print(f"   总记录数：{len(all_records)} 笔")
        return

    summary = calc_summary(records)

    # 生成 Markdown
    md = generate_markdown(year, month, records, summary)
    md_path = OUTPUT_DIR / f"财务报表_{year}年{month:02d}月.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    # 生成 HTML
    html = generate_html(year, month, records, summary)
    html_path = OUTPUT_DIR / f"财务报表_{year}年{month:02d}月.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"")
    print(f"✅ 财务报表生成完成")
    print(f"📊 {year} 年 {month} 月")
    print(f"")
    print(f"📄 Markdown：{md_path}")
    print(f"📄 HTML：{html_path}")
    print(f"")
    print(f"💰 收入：¥{summary['收入已收'][0]:,.2f}（{summary['收入已收'][1]} 笔）")
    print(f"💸 支出：¥{summary['支出已付'][0]:,.2f}（{summary['支出已付'][1]} 笔）")
    print(f"📈 净利润：¥{summary['净利润'][0]:,.2f}")
    print(f"")
    print(f"💼 待收：¥{summary['应收未收'][0]:,.2f}（{summary['应收未收'][1]} 笔）")
    print(f"💼 待付：¥{summary['应付未付'][0]:,.2f}（{summary['应付未付'][1]} 笔）")


if __name__ == "__main__":
    main()
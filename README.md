# 宝鸡丰悦云创科技 — 官方运营仓库

[![Website](https://img.shields.io/badge/Website-Live-0066ff)](https://fengyue-tech.vercel.app)
[![ICP](https://img.shields.io/badge/ICP-Pending-orange)](https://beian.miit.gov.cn/)
[![GitHub](https://img.shields.io/badge/GitHub-3954591720--svg-black)](https://github.com/3954591720-svg/fengyue-tech)

> 一人公司 · 全栈开发 · 软件技术服务 · 坐标陕西宝鸡

---

## 🌐 在线访问

- 官网：https://fengyue-tech.vercel.app
- 案例：https://fengyue-tech.vercel.app/cases.html
- 公开报价：https://fengyue-tech.vercel.app/pricing.html
- SLA 服务承诺：https://fengyue-tech.vercel.app/sla.html
- 数据策略：https://fengyue-tech.vercel.app/data-policy.html
- 隐私政策：https://fengyue-tech.vercel.app/privacy-policy.html
- 服务条款：https://fengyue-tech.vercel.app/terms.html

---

## 📦 项目结构

```
fengyue-tech/                       ← 公网仓库（仅放公开内容）
├── index.html                      ← 官网首页
├── cases.html                      ← 案例展示（脱敏）
├── pricing.html                    ← 公开报价
├── sla.html                        ← SLA 服务承诺
├── data-policy.html                ← 数据保留与删除策略
├── privacy-policy.html             ← 隐私政策
├── terms.html                      ← 服务条款
├── logo.svg                        ← 品牌 logo
├── sitemap.xml                     ← SEO
├── robots.txt                      ← 搜索引擎规则
├── content/                        ← 内容资产
│   ├── 技术文章.md                 ← 一人公司 AI 效率文章
│   ├── 公众号介绍文章.md           ← 公众号首篇文章
│   ├── 公众号简介文案.md           ← 公众号注册文案
│   ├── 客户沟通SOP.md              ← 销售流程
│   ├── 客户跟进机制.md             ← 跟进自动化
│   ├── AI自动化方案.md             ← AI 工具链
│   ├── 业务边界清单.md             ← 做/不做红线
│   ├── 任务看板模板.md             ← 项目管理
│   └── 合规合法合理合情建设进度.md  ← 战略进度追踪
├── contracts/                      ← 合同模板
│   ├── 技术服务合同模板.md          ← 一次性项目
│   ├── 长期技术合作协议模板.md     ← 年度签约
│   ├── 维护服务协议模板.md          ← 售后运维
│   ├── 项目验收清单标准模板.md      ← 验收阶段
│   └── 保密协议模板.md
├── operations/                     ← 运营手册
│   ├── ICP备案完整操作指南.md
│   ├── ICP备案前-域名与服务器选型.md
│   ├── 数据保留与删除策略.md
│   ├── 备份与灾难恢复方案.md
│   └── 业务连续性计划.md
├── scripts/                        ← 自动化工具
│   ├── generate_quote.py           ← 报价单 PDF 生成
│   ├── generate_contract.py        ← 合同 PDF 生成
│   ├── generate_invoice.py         ← 发票 PDF 生成
│   ├── finance_report.py           ← 月度财务报表
│   ├── pomodoro.py                 ← 番茄钟工时追踪
│   ├── weekly_report.py            ← 周报自动生成
│   ├── cron_dashboard.py           ← Cron 任务监控
│   └── update_icp.py               ← ICP 备案号更新脚本
├── company_plan.md                 ← 全景运营方案
└── 运营交付_20260723.md            ← 交付记录

fengyue-yunchuang-platform/         ← 私有仓库（商业代码，单独仓库）
└── （丰悦汇 / 乡邻通 等商业项目）
```

---

## 🚀 快速开始（开发者）

### 本地预览

```bash
python3 -m http.server 8899
# 访问 http://127.0.0.1:8899
```

### 重新部署到 Vercel

```bash
# 任何 push 到 main → Vercel 自动触发部署
git add .
git commit -m "your change"
git push origin main
```

### 生成报价单 / 合同 PDF

```bash
# 报价单
python3 scripts/generate_quote.py "客户名" "项目名" 28000

# 合同
python3 scripts/generate_contract.py "客户名" "项目名" 28000 "联系人" "电话" "邮箱"
```

---

## 🎯 服务范围

| 业务 | 起价 |
|---|---|
| 企业官网 / 落地页 | ¥2,000 |
| 软件定制开发 | ¥3,000 |
| AI 应用落地 | ¥10,000 |
| 云部署 / 运维 | ¥2,000/次 |
| 技术咨询 | ¥300/小时 |

详见 https://fengyue-tech.vercel.app/#services

---

## 📞 联系

- 📧 邮箱：3954591720@qq.com
- 🌐 官网：https://fengyue-tech.vercel.app
- 📍 地址：陕西省宝鸡市渭滨区高新开发区

---

## 📜 许可证

本仓库对外公开内容（官网、文案、模板）仅用于展示与合作沟通。
商业代码（丰悦汇、乡邻通等）在私有仓库 `fengyue-yunchuang-platform` 维护。

© 2026 宝鸡丰悦云创科技有限公司 · 陕ICP备XXXXXXXX号-1
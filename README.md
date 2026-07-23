# 宝鸡丰悦云创科技 — 运营体系

> 2026-07-23 搭建完成 | 一人公司 · 软件开发/技术服务

---

## 📁 文件结构

```
├── website/
│   ├── index.html      ← 官网（可直接部署）
│   ├── vercel.json     ← Vercel 部署配置
│   └── deploy.sh      ← 部署脚本（支持 Vercel/GitHub Pages/本地预览）
├── content/
│   ├── 技术文章.md      ← 《一人技术公司，我如何用AI把开发效率翻了3倍》
│   ├── 公众号介绍文章.md ← 《在宝鸡，一个人做软件公司是什么体验》+ 4周内容规划
│   ├── 客户沟通SOP.md   ← 完整话术 + 报价模板 + 交付流程
│   ├── AI自动化方案.md  ← 工具链 + 每日工作流 + 一键启动指南
│   └── 任务看板模板.md  ← P0/P1/P2分级任务 + 本周日历 + 指标看板
├── company_plan.md      ← 全景运营方案
└── 运营交付_20260723.md ← 交付记录
```

---

## 🌐 官网部署（3选1）

### 方式一：Vercel（推荐，30秒上线）

```bash
# 1. 获取 Vercel Token
#    访问 https://vercel.com/account/tokens → Create Token

# 2. 部署（一条命令）
export VERCEL_TOKEN='你的Token'
cd website && npx vercel --token "$VERCEL_TOKEN" --yes --prod
```

### 方式二：GitHub Pages（免费，需 GitHub 账号）

```bash
# 推送 website/ 目录到 GitHub 仓库
# Settings → Pages → Source: gh-pages branch
# 等待 2 分钟，网站上线
```

### 方式三：Netlify（拖拽上线，无需命令行）

1. 访问 [app.netlify.com/drop](https://app.netlify.com/drop)
2. 把 `website/` 文件夹拖进去
3. 完成！获得一个 `xxx.netlify.app` 链接

---

## 📝 内容发布

| 平台 | 操作步骤 |
|------|---------|
| **公众号** | 登录公众号后台 → 新建图文消息 → 复制 `content/公众号介绍文章.md` 内容 → 预览 → 发布 |
| **掘金** | 登录 [juejin.cn](https://juejin.cn) → 写文章 → 粘贴 `content/技术文章.md` 内容 → 发布 |
| **知乎** | 登录 [zhihu.com](https://zhihu.com) → 写文章 → 粘贴技术文章内容 → 发布 |

---

## 💬 客户沟通 SOP

直接打开 `content/客户沟通SOP.md`，里面有：
- 4套高频话术模板（接需求/问价/跟进/比价）
- 完整项目报价单模板
- 8步成交流程
- 售后跟进话术（1周/1个月/3个月）

---

## 🤖 AI 自动化配置

打开 `content/AI自动化方案.md`，按以下顺序配置（耗时约1小时）：

1. **AI 编码助手** → 装 Cursor 或通义灵码
2. **AI 客服机器人** → 用扣子 Coze 搭（免费，5分钟上线）
3. **内容生成** → 腾讯元宝 / Kimi / ChatGPT

---

## ✅ 今日待办（本周内完成）

- [ ] 打开 `website/index.html` 确认官网效果
- [ ] 注册 Vercel 账号 + 部署官网
- [ ] 注册公众号 + 发布第一篇文章
- [ ] 在掘金/知乎发布技术文章
- [ ] 读一遍 `content/客户沟通SOP.md`，熟悉话术
- [ ] 按 `任务看板模板.md` 规划本周工作

---

> **提示**：本地预览服务器在 `http://127.0.0.1:8899`，修改 `website/index.html` 后刷新即可看到更新。

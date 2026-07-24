# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 环境备忘

### GitHub CLI（gh）
- 路径：`/Users/fengyue/homebrew/bin/gh`（Homebrew 非默认路径安装）
- 认证账号：`3954591720-svg`
- 使用前需手动 export PATH：
  ```bash
  export PATH="/Users/fengyue/homebrew/bin:$PATH"
  ```

### GitHub 认证走 gh credential helper
- `git config http.version HTTP/1.1` 解决 push 时偶发的 HTTP/2 framing error
- 直连偶发超时，多试一次

### 公网仓库（fengyue-tech）
- 仓库：`3954591720-svg/fengyue-tech`（公开）
- 自动部署：push → Vercel 自动触发
- 仅放官网文件；商业代码绝对不能进

### 私有仓库（fengyue-yunchuang-platform）
- 仓库：`3954591720-svg/fengyue-yunchuang-platform`（私有）
- 丰悦汇/乡邻通商业代码

### 商标 92784506
- 第 42 类（软件开发/技术服务）
- 已缴费，cron 跟进审查进度（30 天后）

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)

# 小说创作工坊 · NovelCraft

[![License](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**NovelCraft** 是一个基于大语言模型的小说创作辅助工具，旨在为写作者提供一个**结构化、高效率、可协作**的智能写作环境。

无论你是网文作者、同人写手、还是刚刚开始尝试写作的新人，NovelCraft 都能帮助你跨越从"灵感"到"成稿"之间最艰难的鸿沟。它将 AI 的生成能力与精心设计的写作工作流相结合——让你专注于故事本身，而非格式、组织或反复的复制粘贴。

**NovelCraft** is a novel-writing assistant powered by large language models. It provides a structured, efficient, and collaborative writing environment — helping authors bridge the gap between inspiration and finished manuscript.

Whether you're a web novel author, a fan-fiction writer, or someone just starting their creative journey, NovelCraft combines AI generation with a carefully designed writing workflow. Focus on your story, not on formatting, organizing, or copy-pasting.

---

### 🎯 解决什么问题 · Why This Exists

| 痛点 | NovelCraft 的方案 |
|------|-------------------|
| AI 聊天窗口写长文，复制粘贴来回切换 | 对话与正文面板同屏，内容自动归位 |
| 写了后面忘了前面，角色设定散落各处 | 侧边栏统一管理角色卡与情节大纲 |
| 想让 AI 续写，每次都要重新描述上下文 | 一键续写，自动携带角色、大纲、前文 |
| 修改一段内容，结果全文被替换 | 智能追加/替换双模式 + 多级安全拦截 |
| 多个故事同时进行，文件管理混乱 | 多小说项目切换，数据独立存储 |
| 想导出给朋友看，格式不统一 | 一键导出 TXT / Word / PDF |

---

## ✨ 功能特性 · Features

| 功能 | Feature |
|------|---------|
| AI 协作写作 | AI-powered collaborative writing — draft, continue, or revise |
| 角色与情节管理 | Character & plot management — manual editing or AI auto-generation |
| 智能内容处理 | Smart content organization — auto-append or replace based on context |
| 多格式导出 | Multi-format export — TXT, Word (.docx), PDF |
| 多用户系统 | Multi-user support — isolated workspaces with registration & login |
| 管理员面板 | Admin panel — oversight of all users' works (first user is admin) |
| 多服务商支持 | Multi-provider — DeepSeek, OpenAI, or any compatible API |
| 外观自定义 | Customizable UI — themes, fonts, backgrounds |

## 🚀 快速开始 · Quick Start

**环境要求 / Prerequisites**：Python 3.10+ · [DeepSeek](https://platform.deepseek.com/) 或 [OpenAI](https://platform.openai.com/) 的 API Key

```bash
pip install -r requirements.txt
python app.py
# 浏览器打开 http://127.0.0.1:5000，注册账号后在设置中填入 API Key 即可开始
# Open http://127.0.0.1:5000, register, configure your API key, and start writing
```

> Windows 用户可直接双击 `启动.bat` / Windows users: double-click `启动.bat`

## 🏗️ 技术架构 · Architecture

```
浏览器 / Browser ←→ Flask (Python) ←→ LLM API
                         │
                   文件存储 / File-based
                 (用户隔离 / per-user isolation)
```

| 层 / Layer | 技术栈 / Stack |
|------------|----------------|
| 后端 / Backend | Python Flask |
| 前端 / Frontend | Vanilla HTML/CSS/JS (零框架依赖 / zero dependencies) |
| AI 接口 / AI Interface | OpenAI-compatible format |
| 存储 / Storage | Local JSON + TXT，用户目录隔离 / user-isolated directories |
| 认证 / Auth | Session-based，PBKDF2-SHA256 密码哈希 / password hashing |

## 📖 使用说明 · Usage

详见 [使用说明.md](./使用说明.md) · See [使用说明.md](./使用说明.md) (Chinese)

| 操作 / Action | 方式 / How |
|---------------|-----------|
| 开始写作 / Start | 对话区输入，如"开始写第一章" |
| 续写 / Continue | 点击 ▶ 续写 按钮 |
| 修改 / Revise | 对话中说明修改需求，AI 输出修改后全文 |
| 手动编辑 / Edit | 右侧面板切换编辑模式 |
| 角色卡 / Characters | 点击 🎭 让 AI 自动生成 |
| 情节大纲 / Plot | 点击 📋 让 AI 自动生成 |
| 导出 / Export | 点击 📥 选择格式 |

## 🔮 发展规划 · Roadmap

- [x] 本地浏览器应用 / Local browser-based application
- [x] 多用户认证与数据隔离 / Multi-user auth & data isolation
- [x] 智能内容增删 (追加 vs 替换) / Smart content diff
- [x] AI 自动生成角色资料卡与情节大纲 / Auto-generated profiles & outlines
- [x] 自动续写（一路写到底） / Auto-continue mode
- [~] ~~网页部署与持久化公网访问~~（已放弃 / Abandoned）
- [ ] PWA 移动端安装支持 / PWA support for mobile
- [ ] Android APK (手机独立运行) / Standalone Android APK
- [ ] 版本历史与写作快照 / Version history & snapshots
- [ ] 实时协作写作 / Real-time collaborative writing
- [ ] 更多 AI 服务商接入 / More AI provider integrations

## 📋 更新日志 · Changelog

### v0.2.0 — 2026-06-11

- **🚀 自动续写**：新增「一路写到底」按钮，一键自动续写多段，写完自动继续，直到大纲结束或手动停止
- **🛡️ 内容安全保护**：AI 异常返回（拒绝消息、过短内容）时自动拦截，防止全文被错误覆盖
- **📝 标签机制优化**：系统提示词中重写了内容标签的使用说明，AI 更清楚「追加」「替换」「建议」的区分，减少误操作
- **👥 快速生成按钮**：新增「生成角色卡」和「生成大纲」快捷按钮，一键让 AI 输出结构化设定
- **🎨 UI 优化**：替换内容折叠显示（不刷屏）、编辑弹窗替代原生 prompt、主题/字体/背景自定义
- **🔍 调试面板**：可查看当前发送给 AI 的完整上下文与系统提示词

### v0.1.0 — 2026-06-10

- 首个版本发布
- 基础功能：AI 协作写作、角色与情节管理、多用户系统、多格式导出、多服务商支持

---

## 🤝 联系方式 · Contact

如有改进建议、技术实现探讨，或任何与程序相关的交流，欢迎联系：

For questions, suggestions, or technical discussion:

**QQ**: 1004874101

---

## 📄 许可协议 · License

[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — 个人学习与非商业用途可自由使用和修改，需注明出处。商业使用需作者书面授权。

Non-commercial use only. Attribution required. Commercial use requires explicit written permission.

---

<p align="center">
  <sub>为写作者而生 · Built with care for writers, by writers.</sub>
</p>

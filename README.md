# AI 小说写作助手 · AI Novel Assistant

[![License](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

基于大语言模型的智能写作工具，辅助作者完成从角色设计、情节构思到正文写作、修改润色、导出成稿的全流程创作。

An intelligent writing tool powered by large language models — assisting authors from character design and plot outlining, to drafting chapters, revising content, and exporting finished works.

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

## ⚠️ 关于版本 · About Versions

**本仓库为社区版（轻量试用版）。**

**This repository contains the Community Edition (Lite Version).**

完整版在 AI 交互层面进行了更深入的优化——旨在减少创作过程中 AI 对合理文学情节的**误判和不当拒绝**。当前许多大语言模型的内容审核机制过于宽泛，常常将正常的小说创作内容错误地标记为"敏感"，例如：战斗与冲突场面、角色的道德困境与灰色选择、悲剧情节与死亡描写、复杂的人物关系发展、对社会现象的文学化呈现，等等。这些内容在任何一部成熟的文学作品中都司空见惯，却频频被 AI 拒之门外——这不仅打断了创作流程，也严重限制了作者正常表达的空间。完整版通过更精准的上下文引导，帮助 AI 更好地理解"这是一部文学作品"这一基本前提，让作者能够在艺术表达的合理范围内正常创作。

The Full Version offers deeper optimization in AI interaction — specifically designed to reduce **false positives in content moderation** during creative writing. Many LLMs today employ overly broad content filters that mistakenly flag perfectly normal novel content as "sensitive": battle and conflict scenes, moral dilemmas and gray-area choices, tragedy and death, complex character relationships, literary depictions of social issues, and more. These elements are commonplace in any mature literary work, yet they are frequently blocked by AI — disrupting the creative flow and severely limiting the author's expressive range. The Full Version provides more precise contextual guidance to help the AI recognize the fundamental premise that "this is a literary work," enabling authors to write normally within the bounds of artistic expression.

**需要强调的是**，完整版严格遵循中华人民共和国法律法规，优化措施**仅服务于文学艺术创作**，严禁用于任何非法行为或生成违法违规内容。出于对我国法律的尊重与遵守，完整版不会、也从未计划公开发布。

**Important**: The Full Version strictly complies with the laws of the People's Republic of China. All optimizations are designed **solely for legitimate literary and artistic creation**, and must never be used for illegal activities or generating prohibited content. Out of respect for and compliance with applicable laws, the Full Version is intentionally kept private and has no plan for public release.

> 随着 AI 模型本身的不断进步，其理解能力和上下文判断力将持续提升，两个版本之间的体验差距也将逐渐缩小。与此同时，社区版和完整版均会不定期更新，持续改进功能和创作体验。
>
> As AI models grow more intelligent and context-aware over time, the experience gap between the two versions will naturally narrow. Both editions will continue to receive regular updates and improvements.

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

- 首个社区版发布
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

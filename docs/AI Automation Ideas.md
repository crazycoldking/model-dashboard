下面是一些**在 GitHub 上开源且结合 AI 技术的自动化测试解决方案**（包括测试用例生成、测试脚本生成、AI 驱动的测试流程等），适合作为参考或集成到你自己的项目中：

---

## 1. Test-Agent — 智能测试助理（AI 驱动）

**GitHub 项目**: **codefuse-ai/Test-Agent**

* 利用大模型（如 TestGPT-7B）为测试领域构建智能体，目标是自动化生成测试用例和补全断言。
* 特点包括：多语言测试用例生成（Java/Python/JavaScript）、对现有测试用例自动补充 Assert。
* 支持本地化部署与交互式 ChatBot 页面。 ([GitHub][1])

适用于：需要 AI 辅助生成测试用例和提高测试覆盖率的团队。

---

## 2. Keploy — 自动化测试 & Mock 生成

**GitHub 项目**: **keploy/keploy**

* 自动记录应用行为并生成 API 测试用例和数据 Mock。
* 使用 EBPF 技术实现**无侵入式测试**，支持多语言环境（如 Go、Python、Java 等）。
* 适合微服务测试、CI 集成、跨环境测试数据一致性验证。 ([GitHub Share][2])

适用于：服务端 API 自动测试、快速构建可复现的测试场景。

---

## 3. AUTOTEST — 基于 LLM 自动生成 Selenium 脚本

**GitHub 项目**: **mindfiredigital/AUTOTEST**

* 利用 LLM（可配置 OpenAI、Gemini 等）扫描网页并生成 **Selenium 自动化测试脚本** 和测试用例。
* 支持动态分析网页内容，自动提取 URL 并递归生成测试脚本。
* 成果包括针对登录/表单等功能的正负向测试脚本。 ([GitHub][3])

适用于：Web UI 自动探测和基于浏览器执行的自动化测试。

---

## 4. 自定义 AI 生成测试脚本流程（示例）

**概念 Gist**: AutoDev 自动测试流程

* 通过 AI 自动为新特性生成测试用例并自动执行。
* 在测试失败时，AI 可基于失败日志自动定位和修复问题。
* 这是一个概念性集成，可以作为 **将 AI 与 CI/CD 测试闭环结合的参考**。 ([Gist][4])

适用于：希望构建完整自动化开发 + 测试 + 修复链路的项目。

---

## 5. （可扩展方向）AI 代码审查与 PR 测试建议

**Codium pr-agent / Qodo**

* 这些开源工具不是自动化测试本身，但能在 PR 评论中提供 AI 驱动的代码质量/潜在 Bug 检测建议。
* 常见用于 **代码审核自动提示**，可结合测试工具提升质量。 ([reddit.com][5])

适用于：结合测试结果进行代码质量提升。

---

## 6. （社群项目 / 灵感类）AI 测试 Agents & Bots

一些 GitHub 或社区项目展示了自动触发测试或质量任务的 AI agent 方法，例如：

* 自动化 QA Agent 结合自然语言描述自动运行测试。
* UI、API、Visual、Accessibility 统一测试 agent（虽然部分未详列 Repo，但展示了 AI 在多类型测试中的应用思路）。 ([reddit.com][6])

适用于：构建更智能、更综合的测试 agent 设计思路。

---

## 其他参考（可辅助应用）

虽然不是严格 “AI 测试生成”，但这些开源项目常与测试自动化结合：

* **EvoSuite** — Java 单元测试用例自动生成（搜索/进化算法驱动）([维基百科][7])
* **Playwright** — 浏览器自动化测试框架，可与 AI 脚本生成策略结合。 ([维基百科][8])

---

## 如何选择与使用建议（工程实践角度）

1. **需求型选择**

   * 需要自动生成单元测试：考虑 **Keploy / Test-Agent**。
   * 需要 UI/端到端脚本：考虑 **AUTOTEST + Playwright/Selenium**。
   * 需要集成进 CI/CD 的自动化流程：参考 **AutoDev 概念集成 + GitHub Actions**。

2. **集成策略**

   * 将 AI 生成测试纳入 PR/MR pipeline，提高覆盖率和可靠性。
   * 自定义 LLM Prompt 与测试框架结合，提升扩大测试场景覆盖。

3. **部署与安全**

   * 对于企业级应用，建议私有化部署模型或 API，避免泄露敏感代码。

---

如果你愿意，我可以进一步整理一个 **自动化测试 AI 工具功能对比表** （包括技术栈、支持语言、成熟度、集成方式等），帮助你更快评估和选择。你是否需要这样的对比表？

[1]: https://github.com/codefuse-ai/Test-Agent?utm_source=chatgpt.com "GitHub - codefuse-ai/Test-Agent: Agent that empowers software testing with LLMs; industrial-first in China"
[2]: https://www.githubshare.com/article/2316?utm_source=chatgpt.com "🚀 Keploy：开发者必备的AI测试神器！🔥 自动化测试新纪元 | githubshare"
[3]: https://github.com/mindfiredigital/AUTOTEST?utm_source=chatgpt.com "GitHub - mindfiredigital/AUTOTEST: An open-source Generative AI (GenAI) framework and application designed to generate automated test cases and python Selenium scripts after dynamically analysing the web-page using large language models (LLMs)."
[4]: https://gist.github.com/thehunmonkgroup/f2f8870ff299e6da3eca8fb84e85b6ab?utm_source=chatgpt.com "Summary: AutoDev: Automated AI-Driven Development · GitHub"
[5]: https://www.reddit.com//r/codereview/comments/1gpbq93/any_ai_code_review_tools_for_github_prs/?utm_source=chatgpt.com "Any AI code review tools for GitHub PRs?"
[6]: https://www.reddit.com/r/devops/comments/1ig0lfk?utm_source=chatgpt.com "We made an open source testing agent for UI, API, Visual, Accessibility and Security testing"
[7]: https://en.wikipedia.org/wiki/EvoSuite?utm_source=chatgpt.com "EvoSuite"
[8]: https://en.wikipedia.org/wiki/Playwright_%28software%29?utm_source=chatgpt.com "Playwright (software)"

# 006 · oil-tone：写作约束如何落实到成稿

> 用 23 条文字规则引导 AI 起草、润色和调整结构，让表达自然、清楚并保留事实；我们可以把这套方法复用为文章、产品文案和口播的编辑标准。

| 信息 | 内容 |
| --- | --- |
| 上游 | [oil-oil/oil-tone](https://github.com/oil-oil/oil-tone) |
| 作者 | oil-oil |
| 固定版本 | [39cbf92f76c90b7bb27a5b5d4ed88a1fc5fa31f6](https://github.com/oil-oil/oil-tone/tree/39cbf92f76c90b7bb27a5b5d4ed88a1fc5fa31f6)，2026-09-23 |
| 上游许可 | MIT；[原样保留的 LICENSE](upstream/LICENSE) |
| 研究日期 | 2026-10-21 |
| 网页 | [能力、规则与完整改稿实验](web/index.html) |
| 发布状态 | 静态网页；线上地址与部署结果在完成验证后登记 |

![oil-tone 理解总结：能力、原理、五组约束、场景、意义与边界](assets/understanding-summary.png)

使用内置 ImageGen 生成的原创研究总结图，依据固定版本源码整理，已核对规则计数、可选检查箭头与能力边界。图片来源、生成提示词及记录见 [assets/README.md](assets/README.md)。

## 我们的理解

**能力是什么：**引导 AI 起草、润色和调整文章结构，保留关键事实、补清逻辑关系、删去无依据的评价与重复空话，使稿件更自然、清楚。它提供的是编辑规范，最终效果依赖模型、事实材料和具体任务。

**原理是什么：**宿主把 SKILL.md 中的 23 条文字规则与任务、事实、原稿一起交给 AI；模型理解条件，选择修改动作，再按清单复核。五组规则分别约束目标、组织、句子与语气、呈现形式、最终复核，共 4/6/7/2/4 条。它们不是 23 个依次调用的程序。openai.yaml 提供界面配置；可选的 tone_lint.py 使用 16 组正则提示可疑表达，有 WARN 也返回 0。脚本不核实事实、不自动改写，也不调用模型 API。

**使用场景是什么：**文章与个人体验需要保留具体观察；产品与网站介绍需要讲清功能、步骤和限制；技术说明需要解释术语与关系；演讲、口播和 PPT 需要调整阅读顺序与拗口表达。

**对我们的意义是什么：**把“写自然一点、不要空话”变成能反复使用的判断条件、修改动作和复核清单。可以直接复制网页的完整提示词，也可以按自己的读者、场景和真实案例维护编辑标准，用逐处批注解释修改依据。

这里没有独立的生成服务、自动质量评分器或“不达标就强制重写”的流程。规则复制进上下文也能发挥类似作用；Skill 的价值是组织和复用编辑经验，能力不等于事实核验服务或 AI 文本检测器。

## 网页内容

- 能力、场景与边界：区分源库能力和研究展示页提供的阅读工具。
- 六步实现链路：标出宿主 Agent、模型指令和 Python 的责任。
- 23 条规则：分组、搜索、查看原文行号、编辑动作、例子与条件。
- 完整提示词：包含 A1—E4 全部 23 条、可填写的任务模板与交付要求，支持一键复制和下载，无需安装 Skill；[提示词文本](prompts/oil-tone-writing-prompt.txt)。
- 完整改稿：8 条虚构事实、完整原稿、21 个可点击批注、完整成稿。每处批注说明规则、原因和事实依据。
- 程序证据：对同一原稿与成稿真实运行固定脚本，提醒为 9 → 0；展示原始结果和脚本无法识别的错误。
- 源码阅读：完整 SKILL、检查器与 YAML，提供复制、下载和上游行号链接。

## 示例的真实性

“资料盒”、体验和测试数据均为虚构教学设定，不代表真实产品和实测性能。改稿由本次助手按规范完成，未调用独立的模型 API，也没有进行模型对照实验。真实执行的是 Python 脚本的自检与两份文本扫描。0 条提醒不等于自然、准确或质量达标。

数据源是 [content.json](content.json)。原稿与成稿在 [examples/](examples/)，完整扫描结果是 [lint-results.json](examples/lint-results.json)。A—E 是本研究添加的对照编号，上游原文没有这些编号。

## 运行与复现

环境：Windows PowerShell，Python 3.10.11，Node.js 用于 JS 语法检查。网页不依赖 Node、npm、API Key、外部 CDN 或前端框架，浏览器即可运行。

在仓库根目录执行：

```powershell
python projects/006-oil-tone/scripts/package_web.py
python projects/006-oil-tone/scripts/package_web.py --check
node --check projects/006-oil-tone/web/app.js
python scripts/project_catalog.py check
python -m http.server 8000 --bind 127.0.0.1
```

打开 <http://127.0.0.1:8000/projects/006-oil-tone/web/>。也可直接打开 web/index.html；使用本地 HTTP 能更稳定地支持剪贴板等浏览器功能。

全站构建遵守 [部署约定](../../docs/deployment.md)，使用新的空输出目录：

```powershell
python scripts/build_site.py --output _site/oil-tone-preview
python -m http.server 8000 --bind 127.0.0.1 --directory _site/oil-tone-preview
```

打开 <http://127.0.0.1:8000/006-oil-tone/>。现有汇总器会直接复制本项目 web/，已提交的网页无需额外构建步骤。修改 content.json 或快照后先运行 package_web.py，再提交生成结果。

## 文件结构

```text
content.json                 原始研究内容、规则与示例
upstream/                    固定版本原样快照、MIT 许可与 SHA-256
examples/                    原稿、成稿与真实扫描结果
assets/cover.svg             原创研究图解
scripts/package_web.py       校验、运行检查器并生成可发布数据
web/                         独立静态网站及发布资源
```

## 记录与来源

- [研究笔记](notes.md)
- [验证记录](verification.md)
- [上游快照清单与哈希](upstream/manifest.json)
- [返回项目总索引](../../README.md)

# 验证范围

日期 2026-10-22，Asia/Shanghai。独立新上下文验证：**not performed**。本次研究网页开发没有启用上游完整开发协议，不声称获得上游意义的 SPEC 审批。

## 原版部分复现

固定 `a0eb529d393a1cb3ccc564e32b2104e7e75c7a29`，Windows、Python 3.12.13、上游固定版本依赖。入口 `python projects/013-old-coder/scripts/reproduce_upstream.py`。

- 原始应用与属性测试：41 passed，随机顺序 seed 42。
- 实现覆盖率：49/49 statements、20/20 branches，100%，阈值门槛开启。
- mypy、ruff check、ruff format --check：通过。
- 原始 demo：五次为 `[True, True, True, False, False]`，bob 独立，窗口后 alice 恢复。
- pip-audit：120 秒超时，unverified，不沿用作者历史审计结论。

未运行完整 POSIX gauntlet、原始 POSIX 路径变异器、9 个源码绑定测试、shell 自测、10 次重复套件、独立复核协议。源文件未为 Windows 修改。命令、退出码和原始输出见 [upstream-reproduction.json](results/upstream-reproduction.json)，安装环境见 [environment-freeze.txt](results/environment-freeze.txt)。

## 教学引擎

`node projects/013-old-coder/scripts/verify_labs.cjs` 直接加载网页使用的引擎。16 项检查通过：4 个场景完整契约各 6 项；11 个手选缺陷被发现；简化检查在各场景至少漏过一个缺陷。库存用 2/3/10/50 次重复验证连续、交错、重启和故障模式；限流用 10 个种子各 4000 次输入对照独立模型；明确检查一律拒绝通过上界但违背可用性；权限检查伪造租户不跨越详情、列表与导出边界。

原始断言及引擎哈希见 [lab-verification.json](results/lab-verification.json)。这些是本地模型结果，不包含真实数据库、支付、身份服务、分布式并发或真实 AI 对照。

## 网页

内置浏览器实际操作四个实验：缺陷实现出现失败，修复后各 6/6；手选变异分别发现 3/3、3/3、2/2、3/3。一律拒绝配简化限流检查得到 1/1，演示单向断言的盲区。

375、768、1440 宽度无页面横向溢出。原文搜索/切换、复制下载、模板、证据导出、轨迹、键盘页签和筛选的具体结果见 [browser-verification.json](results/browser-verification.json)。控制台记录仅针对此次浏览器，不等于所有浏览器兼容结论。

结构与来源校验：`python projects/013-old-coder/scripts/verify_web.py`。登记表：`python scripts/project_catalog.py check`。根汇总器直接复制 web；本次未线上发布。

## 一图总览增补

新增 1800 × 2600 PNG 与可编辑 SVG。内置 ImageGen 两次网络失败，最终由 `scripts/build_overview.py` 用同源形状与文字绘制 SVG/PNG；历史请求与失败已记录，没有把代码绘制写成模型成功生成。

检查覆盖能力、场景、六阶段原理、价值与库存 10 / 重复 10 次 / 缺陷 0 / 修复 9 的数字；修复明确为原子提交模型。PNG 及 SVG 与发布副本的 SHA-256 一致。验证命令：`python projects/013-old-coder/scripts/build_overview.py --check`。

浏览器验证图片完整加载、1800 × 2600 原尺寸、放大对话框、Esc 关闭、PNG 下载及下载内容哈希，375 / 1440 宽度无页面横向溢出。结果见 `results/overview-browser-verification.json`。此前全页交互报告保留其当时源码哈希，不作为新增图解页面状态的完整重测。

## 正式网页发布验收

2026-10-22 内容提交 `d7278623e192ae6148eaf59961c9132c0746d052` 的 Pages 工作流 [39791306660](https://github.com/yydshly/1022_codex_project/actions/runs/39791306660)构建和部署成功，目录校验工作流同时通过。公开入口为 <https://yydshly.github.io/1022_codex_project/013-old-coder/>。

- 16 个提交内发布文件均 HTTP 200，SHA-256 与该内容提交逐字节一致；总导航的完整能力/效果/沉淀/扩展摘要与 PNG 引导图已核对。
- 线上四个场景的缺陷版会失败，修复版均 6/6；手选变异发现数依次 3/3、3/3、2/2、3/3。
- 31 份原文加载；图解对话框开/关、Esc 关闭、PNG 下载通过，下载哈希为 `5361ec4a2d8d03873c7cbf2dacf29a3c3f953cb26d01f3903c4ce5291f4d9f60`。
- 375 / 768 / 1440 宽度无页面横向溢出；本次浏览器控制台无警告或错误。

证据：[deployment-verification.json](deployment-verification.json)、[publication-browser-verification.json](publication-browser-verification.json)。身份检查可用 `scripts/verify_deployment.py --commit <精确内容提交> --run-url <Actions URL>` 复跑。网页发布验收不扩大为真实业务服务、原版完整 gauntlet 或独立新上下文验证结论。

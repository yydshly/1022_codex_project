# 网页验证 · 2026-10-21

页面已本地构建，接入总导航与现有 GitHub Pages 打包流程；未发布新的线上版本，登记表 `demo_url` 留空。

| 检查 | 实际结果 |
| --- | --- |
| 打包与目录 | 31 个发布资源的源文件／副本一致，项目目录检查通过 |
| HTTP | 在 `/1022_codex_project/005-scene-card-studio/` 下验证 29 个页面引用资源，均为 HTTP 200，字节与本地一致 |
| 提示词 | 精简／完整／返修三份全文逐字与文件核对一致；复制按钮显示成功，方向键和 Home 可切换页签 |
| 兼容关系 | 浏览器逐项选择全部 80 个组合，11 种系统的可选项与原始规则一致，显示摘要正确 |
| 图片 | 六张图片无损坏；两组 before／after 哈希与上游 source／reference-output 一致；切换后的输入照片可放大，Esc 关闭并还原焦点 |
| 效果总览 | 刺绣、水彩、浮雕、国风四张成片默认可见，不依赖折叠或案例切换；两条案例入口跳转并选择正确原图与成片，浮雕／国风图片可放大关闭 |
| 简明说明 | 首屏明确说明基于原图二次创作，以及可复用、可检查的规则流程；1280／375 视口无横向溢出，四种效果仍默认可见，见[首屏截图](assets/web-preview-essence.png) |
| 理解总结图 | 内置 ImageGen 生成 1 张 1536×1024 中文信息图，已看图核对能力、原理、四种效果标签、原图公开范围、扩展场景与意义；图片、生成请求和五张参考图均记录哈希。网页可放大，Esc 关闭并还原焦点；1280／375 视口无横向溢出，原有四种效果仍默认可见 |
| 完整案例 | 湖泊刺绣、人物水彩两组的原图、要求、规则、成片、完整提示词和证据链接同步切换；键盘方向键可切换，复制按钮显示成功 |
| 响应式 | 375、768、1280 视口均无页面横向溢出、无损坏图片；实际查看手机效果区及桌面首屏 |
| 控制台 | 验证时无 warning/error |
| 源码 | JavaScript 语法、HTML 内部锚点、相对资源和 Git 空白检查通过 |

复制按钮的成功状态已看到；未读回系统剪贴板验证字节。内置浏览器未返回原生下载完成事件，两种受支持的下载测试均超时；下载链接的目标文件和 HTTP 字节均已验证，不能将此记为原生保存流程通过。

截图：[理解总结图桌面](assets/web-preview-understanding.png)、[理解总结图手机](assets/web-preview-understanding-mobile.png)、[效果总览桌面](assets/web-preview-effects-restored.png)、[效果总览手机](assets/web-preview-effects-restored-mobile.png)、[完整案例桌面](assets/web-preview-inputs.png)、[完整案例手机](assets/web-preview-inputs-mobile.png)。中文要求为场景卡整理，非用户原话；浮雕与国风在总览中直接展示，明确标注仅成片、原图未公开。详细记录：[HTTP／资源检查](web-verification.json)、[浏览器交互](browser-checks.json)。

复现：

```powershell
python projects/005-scene-card-studio/scripts/package_web.py
python projects/005-scene-card-studio/scripts/package_web.py --check
python projects/005-scene-card-studio/scripts/verify_web.py
node --check projects/005-scene-card-studio/web/app.js
python scripts/project_catalog.py check
python scripts/build_site.py --output _site/scene-card-review/1022_codex_project
python -m http.server 8037 --bind 127.0.0.1 --directory _site/scene-card-review
```

构建输出目录必须为空；复用已有输出时换一个新目录，不删除已有产物。另一个终端可运行 `verify_web.py --base-url http://127.0.0.1:8037/1022_codex_project/005-scene-card-studio/ --report` 核对 HTTP 文件。

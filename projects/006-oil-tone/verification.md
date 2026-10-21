# 验证记录

研究版本：39cbf92f76c90b7bb27a5b5d4ed88a1fc5fa31f6；研究日期：2026-10-21。

## 已执行的程序检查

- 固定版本脚本自检 PASS。
- content.json 原稿 9 条提醒，成稿 0 条；计算结果与 examples/lint-results.json 一致。
- 打包器验证 23 条规则和 21 处唯一、不重叠的批注原文。
- 4 个上游文件按 SHA-256 校验，保留原字节与许可。
- JavaScript 语法检查通过。

## 浏览器与构建

- 根汇总器构建成功，本次登记表 6 个项目，其中 5 个具备 web/index.html；006 的专用 web/ 已进入编号路径。
- 在编号路径下检查 11 个页面、脚本、样式、图片、源码和 JSON 资源，均 HTTP 200，且响应字节与发布目录一致；见 http-verification.json。
- 检查 HTML 中的本地资源链接存在，且没有以斜杠开头的站点根绝对资源路径。
- 浏览器验证六步执行链路的内容切换；五个分组分别显示 4/6/7/2/4 条，全部显示 23 条。
- 搜索“虚词”显示 4 条；不存在的词显示 0 条和空态；清空恢复规则列表。
- 21 处批注逐一点击，均只有一个原文选中项，显示修改原因、规则和相应材料。批注中的 A4 链接可展开并定位规则原文。
- 完整原稿、批注稿、最终稿切换正常；成稿包含数据表格、步骤、限制和虚构声明。
- 三个源码页签切换正常，Python 源码可复制，剪贴板含 WARNING_RULES。
- 实现链路的键盘 End/Home 操作能分别选择最后与第一个页签。
- 成稿下载成功，下载文件与 examples/final.md 的 UTF-8 字节完全一致。
- 375 / 768 / 1280 宽度下，页面 scrollWidth 分别为 360 / 753 / 1265，与 clientWidth 相同，没有页面级横向溢出（15px 为系统滚动条）。手机批注布局为单列。
- 浏览器采集的 warning/error 日志为空。该结论针对本次测试范围，不是全部浏览器兼容性认证。
- 桌面与手机真实浏览器预览保存在 assets/desktop-preview.png 和 assets/mobile-preview.png。

## 未验证范围

- 真实产品性能：示例为虚构教学材料。
- 多模型改稿质量、独立评审和读者盲测。
- 安装到不同宿主后自动识别 Skill 的行为。
- 尚未发布新的线上版本，不将本地成功写成线上验证。

## 2026-10-21 · 完整提示词入口

- 新增完整提示词，覆盖 A1—E4 共 23 个唯一编号，包含任务、材料、原稿和交付方式；共 4,100 字符，含来源与 MIT 许可。
- 浏览器一键复制后，剪贴板全文与页面显示的文本一致；手机宽度下也成功复制全部 4,100 字符。
- 浏览器实际下载成功，文件与 prompts/oil-tone-writing-prompt.txt、web/assets/oil-tone-writing-prompt.txt 的 UTF-8 字节完全一致。
- 下载使用浏览器端 Blob；HTML 保留静态文件链接作为无 JavaScript 时的后备入口。
- 375px 宽度下，scrollWidth 与 clientWidth 均为 360px，没有页面级横向溢出；复制按钮、下载入口和全文框可用。已恢复浏览器默认尺寸。
- 浏览器采集的 error/warn 日志为空；完整提示词的字节与覆盖记录见 prompt-verification.json。
- 更新后的全站构建成功（6 个具有 web/index.html 的项目）。编号路径下的 12 个资源均 HTTP 200 且内容字节一致；见 http-verification.json。
- 截图见 assets/prompt-preview.png、assets/prompt-mobile-preview.png。本轮检查针对复制、下载和布局，没有再进行模型改稿效果实验。

## 2026-10-21 · 理解总结图

- 使用内置 ImageGen 生成 1536×1024 PNG，并用同一工具做一次定向箭头修订。完整生成与修订指令、来源和哈希保存在 assets/understanding-summary.prompts.json 与 understanding-summary.image.json。
- 已目视核对能力、上下文机制、23 条规则的五组计数 4/6/7/2/4、16 组正则、可选检查送回复核的箭头、场景、意义和边界声明。没有新增文案质量评分或性能评测。
- 源 PNG、web 发布副本和 HTTP 响应逐字节一致。全站总导航已使用新的总结图作为项目封面；13 个资源 HTTP 200 且内容一致。
- 浏览器确认图片 naturalWidth=1536、naturalHeight=1024，加载成功；1280 与 375 宽度下页面无横向溢出，error/warn 日志为空。已恢复默认尺寸。
- 网页整合截图见 assets/summary-web-preview.png；结构化记录见 summary-verification.json。仍为本地构建验证，未发布新线上版本。

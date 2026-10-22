# 图片与来源

上游：[Leonxlnx / verdant-forest](https://github.com/Leonxlnx/verdant-forest)，固定提交 `bb724d84fb683b8f1dea790c3e56f2ffadeb051e`，2026-10-22 获取。

| 本地文件 | 上游路径 | 用途 / 图注 |
| --- | --- | --- |
| `upstream/forest-floor.png` | `artifacts/browser-approved-review/frame-0240.png` | 首页封面与图集；8 秒林下视角，1280 × 720 |
| `upstream/canopy-start.png` | `artifacts/browser-approved-review/frame-0750.png` | 25 秒树冠展开镜头，1280 × 720 |
| `upstream/canopy.png` | `artifacts/browser-approved-review/frame-0840.png` | 28 秒树冠镜头；观察远景层次 |
| `upstream/bark-comparison.jpg` | `artifacts/upgrade-bark/comparison.jpg` | 白桦树皮的离线材质改进对照，非浏览器截图 |

图片均为上游原始字节，未裁切、重新压缩或经 AI 改图。三张浏览器图的哈希同时与作者采样台账核验；来源链接、文件大小和 SHA-256 见 [source-manifest.json](source-manifest.json)。图像中展示的程序化森林由作者创建，原始权利归作者及相应资产提供者。整体项目未见仓库级许可证，具体范围见 [第三方说明](../THIRD_PARTY_NOTICES.md)。

`evidence/` 保留作者的原始采样记录、影片验证记录、树皮对照说明和资产声明。`web/assets/` 中的媒体与证据副本由 `scripts/package_web.py` 按字节生成，不重复提交。网页中的教学 Canvas 由本研究实时绘制，并以文字和可访问描述标明其示意性质。

## 研究总览图

- `understanding-overview.png`：内置 ImageGen 生成的 1672 × 941 横向研究总结图。汇总能力、两种效果参考、原理链路和资产 / 生成 / 工程 / 体验四类价值。
- 参考输入：`upstream/forest-floor.png`、`upstream/canopy.png`，均为作者保存的真实浏览器帧。图中的效果区由模型参考原图编排，不宣称逐像素保留；原图在既有图集中独立展示。
- `overview-prompt.txt`：实际使用的完整生成指令。
- `overview.json`：生成方式、图像尺寸、输出与输入哈希、内容检查和权利来源。
- 总览图用于网页、研究 README 和首页项目封面；原始材料仍遵循其原有权利归属。

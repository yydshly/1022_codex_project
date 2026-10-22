# 来源、署名与许可

本目录是独立研究和展示，与 HEYTEA / 喜茶没有合作、背书或官方归属关系。

## 上游代码和文档

- 项目：[Hchen1218/heytea-style](https://github.com/Hchen1218/heytea-style)
- 作者署名：heytea-style contributors
- 版本：`d5125372adcc945c2314cfb649c50407379a18ab`
- `upstream/` 中的代码与文档保留原文。MIT 原始许可保存为 `LICENSE.upstream.txt` 和 `upstream/LICENSE`。
- 网页使用原始 `EpisodePlayer`（发布路径 `assets/runtime/episode-player.js`），未修改源文件；MIT 许可随网页下载内容保存。
- 网页布局、中文分析和 Canvas 演示适配器为本研究新增。未直接复制 Electron 主进程的窗口与物理实现。

## 上游例图与角色素材

`assets/upstream/` 对应上游 `assets/examples/` 和 `examples/desktop-pet/pink-green-flavor-monster-v3/`。按固定版本 [ASSET-NOTICE.md](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/ASSET-NOTICE.md) 的说明，以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 引用，署名 **heytea-style contributors**。

这些原始文件未做改动。浏览器中有缩放、帧条裁取、透明合成和脚底位置对齐；截图记录了本研究网页对原图的排版呈现。下载的示例 ZIP 在原始角色文件外增加 `ATTRIBUTION.txt` 署名文件。

照片和例图中已有的商标、标识或其他第三方作品，权利仍归对应权利人。CC BY 说明不构成品牌授权或权利转移。本项目未从 `private-assets/reference-cutouts/` 引入研究素材。

每个原文件的原始路径、固定版本 URL、字节数和 SHA-256 见 `SOURCE.json`。网页内的样张说明与下载文件也保留上述署名。

## 新增研究总览

`assets/capability-overview.png` 使用内置 ImageGen，根据五份上游素材进行概览合成，布局与图中效果为模型重新组织。参考素材署名仍为 heytea-style contributors，CC BY 4.0。桌面场景为示意，不能作为原生运行验证；上游未修改原作另行保留。提示词、参考路径、尺寸及输出哈希见 `OVERVIEW.md` 和 `image-generation.json`。

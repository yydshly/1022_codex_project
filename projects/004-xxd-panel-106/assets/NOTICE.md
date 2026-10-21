# 第三方来源与生成声明

## XXD Panel 106

- 作者：nevertoday。
- 仓库：https://github.com/nevertoday/xxd-panel-106
- 固定提交：12a70f6e4d9200b28a95d1b81c808439a5590c74。
- `upstream/sample-05.png` 至 `sample-12.png` 为上游提供的 8 张扩展样张，按字节原样复制。
- `upstream/README.original.md` 保存原样张说明；`upstream/LICENSE.txt` 保存原许可。
- `../prompts/original.zh-CN.md` 及各请求开头的中文正文来自上游原始风格提示词；本研究保留原文，追加交付参数。
- 上游许可为 PolyForm Noncommercial License 1.0.0。本研究是非商业研究展示；没有为上游样张、提示词或本研究的衍生作品另行授予更宽松许可。
- 上游未附样张原始照片或逐图独立摄影署名；摄影区域的更细来源无法由该提交核验，不宣称其为我们拍摄或本次生成。

## 真实演示输入

- 作品：Eiffel Tower, Paris France。
- 摄影：Chris Karidis，https://unsplash.com/@chriskaridis 。
- 原作品页：https://unsplash.com/photos/eiffel-tower-paris-france-nnzkZNYWHaU
- 原图地址：https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=2400&q=90&fit=max
- 下载日期：2026-10-21；保存下载服务返回的 2400×1596 JPEG，无额外裁切或调色。
- Unsplash License：https://unsplash.com/license 。保留原作品署名与链接；不将其作为素材库或未经实质修改的出售物。

## 本次生成作品

- `demo/` 中除 `source-paris.jpg` 外的 PNG 均为 2026-10-21 通过内置 `image_gen.imagegen` 生成。
- 共 10 次生成请求，保留 7 张演示成品和 3 张未通过检查的结果。具体提示词、输入关系、像素和哈希见 `../media.json`。
- 图像工具没有公开底层实际模型标识，不将上游默认模型名当作本次已验证模型。
- 未使用程序绘图替代生成作品；未将一张壁纸裁成四端；未对返回图片做裁切、拉伸、拼合或去除生成来源元数据。
- 对照图中的摄影参考区同样由模型生成，不能当作逐像素保持的原照片。真实输入单独保存在 `source-paris.jpg`。
- 本研究保留 AI 生成声明，不以图像风格或元数据推断作品是真实摄影。

## 理解总结图

- `library-overview.png` 于2026-10-21通过内置image_gen.imagegen额外生成1次，原样保存为1536×1024 PNG。
- 参考图为上述Chris Karidis实拍与本次left-right.png；图中照片和海报缩略图由模型重新表达，均标明示意，不将其当作原始实测证据。
- 图中文字是本研究归纳，提示词引文为摘要；完整上游风格正文及10份海报请求在网页提示词区和项目prompts/。
- 完整总结图生成请求保存在 `../guides/overview-prompt.txt`。本图不计入海报实测的10次请求，单独登记为study_guides。

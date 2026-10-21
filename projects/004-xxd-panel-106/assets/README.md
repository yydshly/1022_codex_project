# 图片说明与来源

逐图链接、实际尺寸、SHA-256、输入关系和提示词见 [media.json](../media.json)，许可与AI生成声明见 [NOTICE.md](NOTICE.md)。

| 文件 | 来源与替代文字说明 |
| --- | --- |
| upstream/sample-05.png | 上游原图：城市与摩天轮像素左右对照 |
| upstream/sample-06.png | 上游原图：灯光、酒杯与花束像素左右对照 |
| upstream/sample-07.png | 上游原图：蒲公英与落日像素左右对照 |
| upstream/sample-08.png | 上游原图：粉红花束与黑包装像素左右对照 |
| upstream/sample-09.png | 上游原图：城市航拍与像素城市上下对照 |
| upstream/sample-10.png | 上游原图：石拱门与粉色花枝像素上下对照 |
| upstream/sample-11.png | 上游原图：骑手、马匹与光弧像素上下对照 |
| upstream/sample-12.png | 上游原图：露营提灯与倾倒饮料像素上下对照 |
| demo/source-paris.jpg | Chris Karidis实拍：巴黎铁塔、塞纳河和桥梁；[原作品](https://unsplash.com/photos/eiffel-tower-paris-france-nnzkZNYWHaU)／[Unsplash License](https://unsplash.com/license) |
| demo/left-right.png | 本次生成，左右对照与准确中文；真实效果示例 |
| demo/top-bottom.png | 本次生成，上下对照与自动英文 |
| demo/design-only.png | 本次生成，无文字纯设计海报 |
| demo/wallpaper-phone.png | 本次生成，手机壁纸及连贯家族定调 |
| demo/wallpaper-ipad.png | 本次生成，原照＋定调图重新构图的平板壁纸 |
| demo/wallpaper-desktop.png | 本次生成，横向电脑壁纸 |
| demo/wallpaper-watch.png | 本次生成，正方形手表壁纸，未验证真机 |
| demo/rejected/ | 本次三个首次失败：纯设计与手机保留摄影区，手表比例不正确 |
| library-overview.png | 本研究一图理解，用作首页封面、总导航与网页首屏引导：能力、风格、提示词、效果差异、意义和边界；图内缩略图为示意、提示词为摘要；[生成请求](../guides/overview-prompt.txt) |

上游来源是nevertoday/xxd-panel-106提交12a70f6的assets/examples，原样保存，原说明及许可证在upstream/。样张未附可核验原始照片，不声明其中摄影由我们拍摄。

2026-10-21通过内置image_gen.imagegen生成本次10张海报演示PNG与1张总结图，未程序化改图或去除AI元数据。底层模型名未公开，不宣称与上游首选模型相同。输入保存原站返回的2400×1596 JPEG，无额外裁切与调色。web-preview图片如存在，则为本地页面截图。

总结图另生成1次，实际1536×1024，不计入原有10次海报演示请求。它参考已署名实拍与本次左右成品，图内缩略图不是原照或成品的逐像素复刻。web-preview-prompts、web-preview-overview如存在，为本次网页更新的实际浏览器截图。

web-live-overview.png为正式GitHub Pages页面的实际浏览器截图，展示指定引导图及风格库样本的说明。页面截图不计入生图次数。

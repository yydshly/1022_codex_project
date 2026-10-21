# 原生 SwiftUI / Metal 展示

这里直接调用固定版本 SwiftUIShaders 的 **41 个公开修饰器**。它与网页移植版共用参数来源，适合在真实 Apple 渲染环境中逐一核对效果。

## 运行条件

- macOS 14 或更新版本，Xcode 15 或更新版本，并安装 Metal 工具链。
- 本地 Swift Package 依赖为 `../upstream`，无需重新拉取上游。
- **本次研究在 Windows 上进行，原生工程尚未在 Xcode 编译或在 Apple 设备实测。**网页预览通过并不代表原生工程已经验证。

## 在 Xcode 中运行

打开 `ShaderGallery.xcodeproj`，选择共享的 **ShaderGallery** scheme 和 **My Mac**，执行 Run。工程包含 41 项目录、全部效果参数、原图切换，以及透镜与涟漪的拖动交互。

也可在本目录执行以下待 macOS 验证的构建命令：

```bash
xcodebuild -project ShaderGallery.xcodeproj -scheme ShaderGallery -destination 'platform=macOS' -derivedDataPath ../../../_upstream/swiftui-shaders-derived build
```

请使用 Xcode / `xcodebuild`，上游明确说明裸 `swift build` 不会执行所需的 Metal 编译与资源打包。

## 参数及原图

- 默认值保持上游配置。缺失的参数范围采用与网页一致、明确标注的实验区间；霓虹效果的滑块包含原默认值 `glowAmount = 4`。
- 触摸涟漪的 `touchAge` 在交互后由 `TimelineView` 推进，也可以手动调整。
- 预览图来自本研究原创 [SVG 测试封面](../web/assets/sample-cover.svg)，资源 PNG 为其栅格化版本。
- 所有修饰器仍使用上游默认 `maxSampleOffset = 64×64`；较强位移可能需要在 Swift 调用中增大该值。

`ShaderGalleryApp.swift` 由以下命令生成，避免手动维护 41 份参数映射：

```bash
python projects/001-swiftui-shaders/scripts/build_native.py
```

上游代码与许可保留在 [`upstream/`](../upstream/)；原生工程不改动其算法。

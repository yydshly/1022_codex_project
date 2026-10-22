# 本地展示与上游复现条件

资料浏览与真实渲染分开加载。早期只做了静态研究，现已准备固定依赖并运行 Cornell Box、完整村庄、海滩与森林的 WebGPU 主管线，作为展示页的真实交互；其余场景尚未逐项验收。准确来源、配置和启动步骤见 [RUNTIME.md](RUNTIME.md)。以下也保留原始快照的缺口，不能把补齐一个演示环境理解成全库已修复。

## 1. 运行本次研究展示

首次构建真实演示需要 Git、Python 3.10+、Node.js 22 和 npm。产物完成后，用静态 HTTP 服务即可；浏览研究资料不需要 WebGPU，点击演示后才初始化 WebGPU。

```powershell
python projects/009-webgpu-render-pipeline/scripts/setup_runtime.py
python projects/009-webgpu-render-pipeline/scripts/build_runtime.py
python projects/009-webgpu-render-pipeline/scripts/package_web.py
python projects/009-webgpu-render-pipeline/scripts/package_web.py --check
python -m http.server 8049 --bind 127.0.0.1 --directory projects/009-webgpu-render-pipeline/web
```

在 [本地研究页](http://127.0.0.1:8049/) 检索，例如“反射”“泡沫”“漏光”“FFT”，切换类别和接入状态，打开能力详情查看固定提交的源码。场景卡提供复制路由功能；复制的文本供未来上游服务使用，不会在当前研究页执行。

页面支持手机宽度、键盘操作、图片放大与 Escape 关闭。完整验证结果以 [verification.json](verification.json) 为准。

## 2. 更新可复核资料

```powershell
# 联网按固定 SHA 下载文本到根目录被忽略的 _upstream/，不执行上游代码
python projects/009-webgpu-render-pipeline/scripts/fetch_evidence.py
# 从维护数据和源码行号生成清单、参数索引及页面数据
python projects/009-webgpu-render-pipeline/scripts/build_research.py
python projects/009-webgpu-render-pipeline/scripts/build_research.py --check
python projects/009-webgpu-render-pipeline/scripts/package_web.py
python scripts/project_catalog.py check
```

没有本地上游缓存时，`build_research.py --check` 使用已保存的 `evidence.json`、源文件哈希与行数核对；它不需要联网。联网刷新时重新从实际源码定位锚点。上游有更新时应新增研究版本记录，不要静默改变 `COMMIT` 后沿用旧行号。

## 3. 上游启动前已发现的缺口

| 核对点 | 固定版本事实 | 对复现的影响 |
| --- | --- | --- |
| React 包 | 源码使用 `react`、`react-dom`；`package.json` 未声明这些直接依赖 | 需要确认并补齐兼容版本 |
| Vite React 插件 | `vite.config.ts` 顶部导入 `@vitejs/plugin-react`，包清单未声明 | 配置加载可能首先失败 |
| 定制 Three.js | Vite 默认 alias 到 `vendor/three/src`；该目录被忽略且不在树中 | 需按作者分支/补丁准备源码；npm three 包不能自动补齐所有修复 |
| 定制 R3F | alias 到 `vendor/react-three-fiber/packages/fiber/src/index.tsx`，但 vendor 不在树中 | 村庄/天空等 TSX 场景会受影响，不只是单独 fiber lab |
| TypeScript JSX | `tsconfig.json` 纳入 `src`，包含多处 TSX，但没有 `jsx` 选项 | `typecheck` 配置需要核对，不能仅修 npm 安装后宣告完成 |
| 独立页面装配 | 只有主应用根 `index.html`；实验室入口 TS/TSX 有代码，但没有对应 HTML/路由接线 | `/labs/water/`、`/labs/fiber/`、`/pipeline` 需补入口；Vite SPA 回退不等于加载正确模块 |
| 历史参考应用 | `dev:gi` 以缺失的 `vendor/webgiya` 为根 | 这是供 A/B 的另一个应用，不能当作主应用启动命令 |
| 部分 npm 脚本 | `check:comments` 引用未在固定树发现的 `scripts/check-no-comments.mjs` | 不能假设 package 中每条脚本都可执行 |
| 资源与数据 | 有一项模型 `.bin` 记录为 0 字节；部分图目录声明的 preview 路径未在树中发现 | 资产是否实际被使用、哪些入口受影响仍需逐项确认 |
| 烘焙缓存写入 | 写入由 Vite 插件处理，静态 Pages 只有读取能力 | 发布前需要提前生成并打包缓存，或设计其他持久化流程 |

依据：[package.json](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/package.json)、[Vite 配置](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/vite.config.ts)、[tsconfig](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/tsconfig.json)、[完整固定树](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/tree/ca576b601bf84527102f1768372aa8cd96a3c55a)。

## 4. 后续上游复现的建议顺序

这是最初的复现顺序。固定依赖、Cornell Box、完整村庄、海滩、森林和明确显示配置现已完成，准确成功记录见 [RUNTIME.md](RUNTIME.md)；走廊与独立实验室仍是后续工作。

1. 在独立、被忽略的 `_upstream/` 克隆仓库并检出固定提交，保留上游修改边界。
2. 先检查许可和原始素材来源，再核对 React、Vite 插件、TSX 和定制 R3F 的依赖关系。
3. 按作者文档准备定制 Three.js 分支，并确定所需补丁是否已包含；记录实际 fork SHA。`VITE_THREE_STOCK=1` 只用于 A/B 排错，不能视为等价修复。
4. 先跑 Cornell Box，核对 WebGPU limits、所有资源、光照烘焙和第一帧；再跑走廊和 `leak-room`，最后到村庄和水实验室。
5. 明确是否加载保存的 GUI 设置，固定曝光、颗粒、TAA 收敛状态和相机后再截图比较。
6. 每次只验证一个边界：服务启动 → 资源加载 → 计算通道 → 缓存 → 最终画面；记录浏览器、显卡、分辨率、DPR、构建模式、冷/热缓存和时间。

作者提供的相关命令包括 `npm run dev`、`npm run typecheck`、`npm run build`、`npm test`、`npm run shot`；待环境补齐后再执行，并把实际结果写入新的验证记录。

## 5. WebGPU 设备条件

渲染器主动拒绝没有 `navigator.gpu` 的环境，不降级到 WebGL。它申请 `maxStorageBuffersPerShaderStage: 14`、`maxComputeWorkgroupSizeX: 1024`、`maxComputeInvocationsPerWorkgroup: 1024`，并依据 adapter 申请存储绑定与 buffer 大小。

因此，“浏览器有 WebGPU”不代表这些额外上限都满足。当前演示已在报告 NVIDIA / Lovelace 的适配器上完成初始化与出帧；页面会预先检查所需上限，失败时显示具体原因。尚未推断其他设备或实际手机 GPU 的兼容性。

## 6. 静态发布

发布资源全部位于 `web/`。先由 `build_runtime.py` 构建真实渲染至 `web/live/`，再由 `package_web.py` 核对构建哈希、复制资料并支持 `--check`。仓库根汇总器复制至 `/009-webgpu-render-pipeline/`，运行产物无需额外服务端。Pages 工作流已加入 Node 与真实构建步骤。

目前没有推送或部署本子项目，登记表 `demo_url` 留空。文档与打包页面的资源引用使用相对路径；本地验证应另外覆盖带仓库前缀的编号路径。

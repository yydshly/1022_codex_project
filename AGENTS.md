# 仓库维护约定

本仓库用于研究多个 GitHub 开源项目，默认以中文撰写研究说明。

- 根 `README.md` 保持为索引、引导摘要和项目配图入口；深入分析与运行步骤写入子项目。
- `projects/catalog.json` 是项目登记表。目录采用 `projects/001-slug/` 格式；编号按收录顺序递增，保留归档项目，不重排或复用已有编号。
- 新增项目优先使用 `python scripts/project_catalog.py add`。不要把示例项目当成真实研究记录收录。
- 首页 `PROJECT_INDEX` 和 `PROJECT_CARDS` 标记之间的内容由脚本生成。修改登记表后执行 `python scripts/project_catalog.py sync`。
- 项目图片放在各自的 `assets/` 中，使用相对路径，提供替代文字、说明及来源。首页封面应能说明项目，模板占位图应尽快换成真实图片。
- 记录上游仓库、研究时的 commit/tag、许可与复现环境。引入第三方代码时保留其许可证和必要声明。
- 子项目可以使用不同技术栈，各自记录依赖和运行命令；有实际需要时再建立 `src/`、`web/` 等目录。
- GitHub Pages 采用一个站点下多个编号路径。根仓库不预设统一前端框架；部署规范见 `docs/deployment.md`。
- 提交前执行 `python scripts/project_catalog.py check`。修改目录脚本时还应执行 `python -m unittest discover -s scripts/tests -v`。

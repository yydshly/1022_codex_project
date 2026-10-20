# 子项目研究约定

## 编号与排序

- 目录使用 `projects/001-slug/`，`slug` 使用小写英文、数字和短横线。
- 编号表示收录顺序，至少补齐三位；按编号升序展示。
- 归档项目仍保留登记项、目录和编号；新项目使用当前最大编号加一。
- 名称、描述和研究进度可以调整，已分配编号不随这些信息变化。

## 登记表

`projects/catalog.json` 是首页索引和项目图览的唯一数据源。初始为空，不包含虚构的研究项目。

每条记录的格式如下。这是填写说明，不是已收录项目：

```json
{
  "id": "001",
  "slug": "project-slug",
  "name": "项目名称",
  "repo": "https://github.com/owner/repository",
  "summary": "项目用途与研究价值的一句话摘要",
  "status": "planned",
  "tags": ["工具", "可视化"],
  "cover": "assets/cover.svg",
  "cover_caption": "截图展示的功能、界面或使用场景",
  "demo_url": ""
}
```

| 字段 | 约定 |
| --- | --- |
| `id` | 固定编号，如 `001` |
| `slug` | 目录名后缀，仓库内唯一 |
| `name` | 首页展示名称 |
| `repo` | 原项目 GitHub 仓库 HTTPS 地址 |
| `summary` | 简短、可独立阅读的一句话摘要 |
| `status` | `planned` 待研究 / `researching` 研究中 / `completed` 已完成 / `archived` 已归档 |
| `tags` | 技术或主题标签，可为空数组 |
| `cover` | 相对子项目目录的本地图片路径，不能为空 |
| `cover_caption` | 图片说明，默认占位图需明确标记 |
| `demo_url` | 已发布演示的完整 HTTPS 地址，尚未发布时留空 |

修改后运行 `python scripts/project_catalog.py sync`。不要直接维护首页自动生成区块，以免下次同步时被覆盖。

## 最小研究记录

每个项目至少包含：

1. **来源**：上游仓库、作者、commit/tag、许可证和收录日期。
2. **摘要**：用途、研究价值和适用场景。
3. **复现**：实际验证过的环境、命令和结果；尚未验证的内容明确标注。
4. **研究**：关键模块、实现思路、取舍和结论，过程记录在 `notes.md`。
5. **配图**：功能截图或架构图，提供替代文字、图注和来源。

需要实验代码时增加 `src/` 或 `experiments/`；需要 Web 演示时增加 `web/`。各项目自行管理依赖与锁文件，不强制统一技术栈。

## 上游代码与许可

优先用上游链接和 commit 固定研究范围。临时克隆可放入被 Git 忽略的 `_upstream/`；确需将代码纳入本仓库时，保留上游许可和署名，说明修改范围及运行方法。避免引入嵌套 `.git` 目录或与研究无关的大型资源。

## 日常检查

```bash
python scripts/project_catalog.py sync
python scripts/project_catalog.py check
```

检查会核对编号、目录、必要文档、封面文件和首页同步状态。推送及 Pull Request 会自动运行同样的检查。修改脚本时还要运行其回归测试：

```bash
python -m unittest discover -s scripts/tests -v
```

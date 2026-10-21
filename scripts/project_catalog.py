"""Maintain the ordered research catalog using only Python's standard library."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from html import escape
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
STATUSES = {
    "planned": "待研究",
    "researching": "研究中",
    "completed": "已完成",
    "archived": "已归档",
}
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
REPO = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?")
TEXT_FIELDS = ("id", "slug", "name", "repo", "summary", "status", "cover", "cover_caption")


class CatalogError(ValueError):
    """A catalog or template error that can be shown without a traceback."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CatalogError(message)


def single_line(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not any(
        ord(char) < 32 or ord(char) == 127 for char in value
    )


def directory_name(project: dict) -> str:
    return f"{project['id']}-{project['slug']}"


def markdown(value: str) -> str:
    # Keep metadata plain text even inside Markdown links, headings and tables.
    value = value.replace("\\", "\\\\")
    return re.sub(r"([`*_{}\[\]<>()|#!])", r"\\\1", value)


def url(value: str) -> str:
    return quote(value, safe="/:?=&%+~.-_#")


def load_catalog(root: Path) -> dict:
    data = json.loads((root / "projects/catalog.json").read_text(encoding="utf-8"))
    require(isinstance(data, dict), "登记表必须是 JSON 对象。")
    require(type(data.get("schema_version")) is int and data["schema_version"] == 1,
            "不支持的 schema_version，当前应为 1。")
    require(isinstance(data.get("projects"), list), "projects 必须是数组。")
    ids, slugs, folders = set(), set(), set()
    for project in data["projects"]:
        require(isinstance(project, dict), "每条项目记录必须是对象。")
        for key in TEXT_FIELDS:
            require(single_line(project.get(key)), f"{key} 必须是非空单行文本。")
        project_id = project["id"]
        require(re.fullmatch(r"[0-9]{3,}", project_id) is not None,
                f"编号应为至少三位数字：{project_id}")
        require(int(project_id) > 0 and f"{int(project_id):03d}" == project_id,
                f"编号格式错误：{project_id}")
        require(project_id not in ids, f"编号重复：{project_id}")
        require(SLUG.fullmatch(project["slug"]) is not None,
                f"slug 只能含小写字母、数字和短横线：{project['slug']}")
        require(project["slug"] not in slugs, f"slug 重复：{project['slug']}")
        require(REPO.fullmatch(project["repo"]) is not None,
                f"原项目必须是 GitHub 仓库 HTTPS 地址：{project['repo']}")
        require(project["status"] in STATUSES, f"未知研究进度：{project['status']}")
        tags = project.get("tags")
        require(isinstance(tags, list) and all(single_line(tag) for tag in tags),
                f"{project_id}: tags 必须是单行文本数组。")
        demo = project.get("demo_url")
        require(isinstance(demo, str), f"{project_id}: demo_url 必须是文本，未部署时留空。")
        if demo:
            require(single_line(demo) and not any(char.isspace() for char in demo),
                    f"{project_id}: 演示地址不能包含空白。")
            parsed = urlsplit(demo)
            require(parsed.scheme == "https" and bool(parsed.hostname)
                    and not parsed.username and not parsed.password,
                    f"{project_id}: 演示地址必须是完整 HTTPS URL。")
        folder = directory_name(project)
        project_dir = root / "projects" / folder
        for relative in ("README.md", "notes.md", "assets/README.md"):
            require((project_dir / relative).is_file(), f"缺少文件：projects/{folder}/{relative}")
        cover = Path(project["cover"])
        require(not cover.is_absolute() and "\\" not in project["cover"]
                and ".." not in cover.parts and len(cover.parts) >= 2 and cover.parts[0] == "assets",
                f"{project_id}: cover 必须是 assets/ 内的相对路径。")
        image = (project_dir / cover).resolve()
        require(image.is_relative_to((project_dir / "assets").resolve()),
                f"{project_id}: cover 超出了项目图片目录。")
        require(image.is_file(), f"封面文件不存在：projects/{folder}/{project['cover']}")
        require(image.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"},
                f"{project_id}: 不支持的封面格式。")
        ids.add(project_id)
        slugs.add(project["slug"])
        folders.add(folder)
    for directory in (root / "projects").iterdir():
        if directory.is_dir() and re.match(r"[0-9]{3,}-", directory.name):
            require(directory.name in folders, f"项目目录尚未登记：{directory.name}")
    data["projects"].sort(key=lambda project: int(project["id"]))
    return data


def render_index(projects: list[dict]) -> str:
    lines = [f"当前收录 **{len(projects)}** 个项目。", "",
             "| 编号 | 项目 | 关注源库 | 一句话摘要 | 研究进度 | Web 演示 |",
             "| --- | --- | --- | --- | --- | --- |"]
    for project in projects:
        path = f"projects/{directory_name(project)}/README.md"
        demo = f"[在线演示]({url(project['demo_url'])})" if project["demo_url"] else "—"
        source_name = project["repo"].rstrip("/").rsplit("/", 1)[-1]
        lines.append(f"| {project['id']} | [{markdown(project['name'])}]({path}) | "
                     f"[{markdown(source_name)}]({url(project['repo'])}) | "
                     f"{markdown(project['summary'])} | {STATUSES[project['status']]} | {demo} |")
    if not projects:
        lines.append("| — | 暂无子项目 | — | 首个真实项目将从 001 开始收录 | — | — |")
    return "\n".join(lines)


def render_cards(projects: list[dict]) -> str:
    if not projects:
        return "暂无项目配图。添加子项目后，这里会按编号展示封面、图片说明和研究入口。"
    cards = []
    for project in projects:
        path = f"projects/{directory_name(project)}"
        lines = [f"### {project['id']} · {markdown(project['name'])}", "",
                 f"{markdown(project['summary'])}", "",
                 f"![{project['id']} · {markdown(project['name'])} 项目封面]"
                 f"({url(path + '/' + project['cover'])})", "",
                 f"> {markdown(project['cover_caption'])}", "",
                 f"[研究详情]({path}/README.md) · [原始仓库]({project['repo']})"]
        if project["demo_url"]:
            lines[-1] += f" · [在线演示]({url(project['demo_url'])})"
        if project["tags"]:
            lines.extend(["", "标签：" + " / ".join(markdown(tag) for tag in project["tags"])])
        cards.append("\n".join(lines))
    return "\n\n".join(cards)


def updated_readme(root: Path, data: dict) -> str:
    content = (root / "README.md").read_text(encoding="utf-8")
    for key, body in (("PROJECT_INDEX", render_index(data["projects"])),
                      ("PROJECT_CARDS", render_cards(data["projects"]))):
        start, end = f"<!-- {key}:START -->", f"<!-- {key}:END -->"
        require(content.count(start) == 1 and content.count(end) == 1,
                f"README.md 必须包含且仅包含一对 {key} 标记。")
        require(content.index(start) < content.index(end), f"{key} 标记顺序错误。")
        pattern = re.escape(start) + r".*?" + re.escape(end)
        content = re.sub(pattern, lambda _: f"{start}\n{body}\n{end}", content, flags=re.DOTALL)
    return content


def write_text(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def sync(root: Path) -> None:
    data = load_catalog(root)
    write_text(root / "README.md", updated_readme(root, data))


def check(root: Path) -> int:
    data = load_catalog(root)
    require((root / "README.md").read_text(encoding="utf-8") == updated_readme(root, data),
            "首页索引已过期，请运行 python scripts/project_catalog.py sync。")
    return len(data["projects"])


def add(root: Path, *, slug: str, name: str, repo: str, summary: str) -> str:
    require(SLUG.fullmatch(slug) is not None, "slug 只能含小写字母、数字和短横线。")
    require(single_line(name) and single_line(summary), "名称和摘要必须是非空单行文本。")
    require(REPO.fullmatch(repo) is not None, "repo 必须是 GitHub 仓库 HTTPS 地址。")
    data = load_catalog(root)
    updated_readme(root, data)  # Validate markers before creating any files.
    require(not any(project["slug"] == slug for project in data["projects"]),
            f"slug 已存在：{slug}")
    number = max((int(project["id"]) for project in data["projects"]), default=0) + 1
    project_id = f"{number:03d}"
    project = {
        "id": project_id, "slug": slug, "name": name, "repo": repo,
        "summary": summary, "status": "planned", "tags": [],
        "cover": "assets/cover.svg", "cover_caption": "模板占位图，待替换为真实项目截图。",
        "demo_url": "",
    }
    destination = root / "projects" / directory_name(project)
    require(not destination.exists(), f"目录已存在：{destination.name}")
    template = root / "templates/project"
    require(template.is_dir(), "缺少 templates/project 模板目录。")
    values = {"ID": project_id, "NAME": name, "REPO": repo, "SUMMARY": summary,
              "DATE": datetime.now(timezone(timedelta(hours=8))).date().isoformat()}
    catalog_path, readme_path = root / "projects/catalog.json", root / "README.md"
    old_catalog, old_readme = catalog_path.read_bytes(), readme_path.read_bytes()
    try:
        shutil.copytree(template, destination)
        for path in destination.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".svg"}:
                continue
            replacements = {key: escape(value) if path.suffix == ".svg" else
                            (value if key in {"ID", "DATE", "REPO"} else markdown(value))
                            for key, value in values.items()}
            content = re.sub(r"__(ID|NAME|REPO|SUMMARY|DATE)__",
                             lambda match: replacements[match[1]],
                             path.read_text(encoding="utf-8"))
            write_text(path, content)
        data["projects"].append(project)
        write_text(catalog_path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        sync(root)
    except Exception:
        catalog_path.write_bytes(old_catalog)
        readme_path.write_bytes(old_readme)
        # Only remove the new, verified directory below this workspace's projects/.
        resolved = destination.resolve()
        if resolved.parent == (root / "projects").resolve() and destination.is_dir():
            shutil.rmtree(resolved)
        raise
    return directory_name(project)


def main() -> int:
    parser = argparse.ArgumentParser(description="创建研究项目并维护按编号排序的首页索引。")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("add", help="分配编号并从模板创建项目")
    for field in ("slug", "name", "repo", "summary"):
        create.add_argument(f"--{field}", required=True)
    commands.add_parser("sync", help="根据登记表更新首页索引与图览")
    commands.add_parser("check", help="检查登记表、项目目录、图片与首页")
    args = parser.parse_args()
    try:
        if args.command == "add":
            folder = add(ROOT, slug=args.slug, name=args.name, repo=args.repo, summary=args.summary)
            print(f"Created projects/{folder}/ and updated README.md")
        elif args.command == "sync":
            sync(ROOT)
            print("README.md index and project cards updated.")
        else:
            print(f"Catalog OK: {check(ROOT)} project(s); README.md is up to date.")
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

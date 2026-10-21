"""Regression tests for ordering, generated links and safe project creation."""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import project_catalog as catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        (self.root / "projects").mkdir()
        shutil.copy(catalog.ROOT / "README.md", self.root / "README.md")
        shutil.copytree(catalog.ROOT / "templates", self.root / "templates")
        self.save({"schema_version": 1, "projects": []})
        catalog.sync(self.root)

    def save(self, data):
        (self.root / "projects/catalog.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def create(self, slug="example", name="示例项目"):
        return catalog.add(self.root, slug=slug, name=name,
                           repo="https://github.com/owner/repository", summary="测试用途与研究价值")

    def test_empty_catalog_and_stale_index(self):
        self.assertEqual(catalog.check(self.root), 0)
        readme = self.root / "README.md"
        original = readme.read_text(encoding="utf-8")
        catalog.sync(self.root)
        self.assertEqual(readme.read_text(encoding="utf-8"), original)
        readme.write_text(original.replace("暂无子项目", "被手动修改"), encoding="utf-8")
        with self.assertRaisesRegex(catalog.CatalogError, "过期"):
            catalog.check(self.root)
        catalog.sync(self.root)
        self.assertEqual(catalog.check(self.root), 0)

    def test_add_creates_sequential_projects_and_resolves_template(self):
        self.assertEqual(self.create(), "001-example")
        self.assertEqual(self.create("second"), "002-second")
        self.assertEqual(catalog.check(self.root), 2)
        project = self.root / "projects/001-example"
        readme = (project / "README.md").read_text(encoding="utf-8")
        self.assertIn("001 · 示例项目", readme)
        self.assertNotIn("__NAME__", readme)
        self.assertTrue((project / "notes.md").is_file())
        ET.parse(project / "assets/cover.svg")

    def test_index_links_source_with_original_repository_name(self):
        catalog.add(self.root, slug="shader-study", name="着色器能力研究",
                    repo="https://github.com/krispuckett/SwiftUIShaders/",
                    summary="测试源库原名与研究名称的区分")
        text = (self.root / "README.md").read_text(encoding="utf-8")
        index = text.split("<!-- PROJECT_INDEX:START -->", 1)[1].split(
            "<!-- PROJECT_INDEX:END -->", 1)[0]
        self.assertIn("| 项目 | 关注源库 |", index)
        self.assertIn("[着色器能力研究](projects/001-shader-study/README.md)", index)
        self.assertIn("[SwiftUIShaders](https://github.com/krispuckett/SwiftUIShaders/)", index)
        rows = [line for line in index.splitlines() if line.startswith("|")]
        self.assertTrue(all(len(row.split("|")) == 8 for row in rows))
        self.assertEqual(catalog.check(self.root), 1)

    def test_maximum_number_is_preserved_for_archived_projects(self):
        self.create()
        data = catalog.load_catalog(self.root)
        data["projects"][0].update(id="010", status="archived")
        (self.root / "projects/001-example").rename(self.root / "projects/010-example")
        self.save(data)
        self.assertEqual(self.create("next"), "011-next")
        self.assertEqual(catalog.check(self.root), 2)

    def test_numeric_order_and_metadata_escaping(self):
        self.create("first", "工具 < & [x] | 说明")
        self.create("second")
        data = catalog.load_catalog(self.root)
        data["projects"][0]["demo_url"] = "https://example.com/demo_(one)/"
        data["projects"].reverse()
        self.save(data)
        catalog.sync(self.root)
        text = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertLess(text.index("| 001 |"), text.index("| 002 |"))
        self.assertIn(r"\[x\] \|", text)
        self.assertIn("demo_%28one%29", text)
        svg = ET.parse(self.root / "projects/001-first/assets/cover.svg")
        self.assertIn("工具 < & [x] | 说明", "".join(svg.getroot().itertext()))
        self.assertEqual(catalog.check(self.root), 2)

    def test_duplicate_slug_and_invalid_slug_leave_files_unchanged(self):
        self.create()
        original = (self.root / "projects/catalog.json").read_bytes()
        with self.assertRaisesRegex(catalog.CatalogError, "slug 已存在"):
            self.create()
        with self.assertRaises(catalog.CatalogError):
            self.create("../escape")
        self.assertEqual((self.root / "projects/catalog.json").read_bytes(), original)
        self.assertEqual(catalog.check(self.root), 1)

    def test_duplicate_ids_and_missing_assets_are_rejected(self):
        self.create()
        self.create("second")
        data = catalog.load_catalog(self.root)
        data["projects"][1]["id"] = "001"
        self.save(data)
        with self.assertRaisesRegex(catalog.CatalogError, "编号重复"):
            catalog.check(self.root)
        data["projects"].pop()
        shutil.rmtree(self.root / "projects/002-second")
        data["projects"][0]["cover"] = "assets/missing.png"
        self.save(data)
        with self.assertRaisesRegex(catalog.CatalogError, "封面文件不存在"):
            catalog.check(self.root)

    def test_cover_paths_cannot_escape_assets(self):
        self.create()
        data = catalog.load_catalog(self.root)
        for cover in ("../README.md", ".", "assets/../../README.md", "assets\\cover.svg"):
            with self.subTest(cover=cover):
                data["projects"][0]["cover"] = cover
                self.save(data)
                with self.assertRaisesRegex(catalog.CatalogError, "相对路径"):
                    catalog.check(self.root)

    def test_failed_creation_rolls_back_catalog_readme_and_directory(self):
        original_catalog = (self.root / "projects/catalog.json").read_bytes()
        original_readme = (self.root / "README.md").read_bytes()
        (self.root / "templates/project/notes.md").unlink()
        with self.assertRaisesRegex(catalog.CatalogError, "缺少文件"):
            self.create()
        self.assertEqual((self.root / "projects/catalog.json").read_bytes(), original_catalog)
        self.assertEqual((self.root / "README.md").read_bytes(), original_readme)
        self.assertFalse((self.root / "projects/001-example").exists())

    def test_missing_readme_marker_prevents_creation(self):
        (self.root / "README.md").write_text("# No markers\n", encoding="utf-8")
        with self.assertRaisesRegex(catalog.CatalogError, "标记"):
            self.create()
        self.assertFalse((self.root / "projects/001-example").exists())


if __name__ == "__main__":
    unittest.main()

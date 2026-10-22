"""Keep project-specific guide captions accurate in the shared navigation."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("build_site", Path(__file__).resolve().parents[1] / "build_site.py")
BUILD_SITE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_SITE)


class GuideCaptionTests(unittest.TestCase):
    def test_forest_cover_uses_its_caption_and_shader_atlas_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            projects = []
            for identity, slug, caption in (
                ("001", "swiftui-shaders", "Shader cover"),
                ("016", "verdant-forest", "植物生成、LOD 与风动；可扩展自然展厅与空间叙事。"),
            ):
                web = root / "projects" / f"{identity}-{slug}" / "web"
                (web / "assets").mkdir(parents=True)
                (web / "index.html").write_text("<!doctype html><title>fixture</title>")
                (web / "assets/understanding-overview.png").write_bytes(b"fixture")
                if identity == "001":
                    (web / "assets/effect-atlas.png").write_bytes(b"fixture")
                projects.append({"id": identity, "slug": slug, "repo": f"https://github.com/test/{slug}",
                                 "name": slug, "summary": slug, "cover": "assets/understanding-overview.png",
                                 "cover_caption": caption})
            (root / "projects/catalog.json").write_text(json.dumps({"projects": projects}), encoding="utf-8")
            with patch.object(BUILD_SITE, "ROOT", root):
                BUILD_SITE.build(root / "output")
            html = (root / "output/index.html").read_text(encoding="utf-8")
            forest = html.split('<span>研究项目 016</span>', 1)[1].split("</article>", 1)[0]
            self.assertIn(projects[1]["cover_caption"], forest)
            self.assertIn('./016-verdant-forest/assets/understanding-overview.png', forest)
            self.assertNotIn("实时视图输出", forest)
            self.assertIn("effect-atlas.png", html)
            self.assertIn("同一张原创封面", html)


if __name__ == "__main__":
    unittest.main()

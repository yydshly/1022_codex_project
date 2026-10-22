"""Exercise the actual page: sources, gallery, keyboard, phases, and viewport bounds.

Development only: requires an existing local HTTP server and Playwright Chromium.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main(url, screenshots_dir=None, report_path=None):
    screenshots_dir = Path(screenshots_dir) if screenshots_dir else ROOT / "assets"
    report_path = Path(report_path) if report_path else ROOT / "browser-verification.json"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"date": "2026-10-22", "url": url, "status": "passed", "checks": [], "viewports": []}
    errors, failed_responses = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: failed_responses.append({"url": response.url, "status": response.status}) if response.status >= 400 else None)
        assert page.goto(url, wait_until="networkidle", timeout=90000).status == 200
        page.wait_for_function("document.querySelector('#pet-canvas').dataset.behavior === 'awake-story'")
        report["browser"] = browser.version
        variants = {"poster": 2, "monster": 2, "fusion": 1, "pet": 2}
        for capability, count in variants.items():
            page.locator(f"[data-capability='{capability}']").click()
            for index in range(count):
                page.locator(f"[data-variant='{index}']").click()
                page.wait_for_function("document.querySelector('#output-image').complete && document.querySelector('#output-image').naturalWidth > 0")
                assert page.locator(f"[data-capability='{capability}']").get_attribute("aria-selected") == "true"
                assert page.locator(f"[data-variant='{index}']").get_attribute("aria-pressed") == "true"
        report["checks"].append("7 gallery variants load and expose correct selection")
        page.locator("#tab-poster").focus()
        page.keyboard.press("ArrowRight")
        assert page.locator("#tab-monster").get_attribute("aria-selected") == "true"
        page.keyboard.press("End")
        assert page.locator("#tab-pet").get_attribute("aria-selected") == "true"
        page.keyboard.press("Home")
        assert page.locator("#tab-poster").get_attribute("aria-selected") == "true"
        page.locator("#zoom-image").click()
        assert page.locator("#image-dialog").evaluate("dialog => dialog.open")
        page.keyboard.press("Escape")
        assert not page.locator("#image-dialog").evaluate("dialog => dialog.open")
        assert page.locator("#zoom-image").evaluate("element => element === document.activeElement")
        report["checks"].append("keyboard tab navigation, image dialog Escape, and focus return")
        for path, count in [("poster", 5), ("monster", 4), ("desktop", 5)]:
            page.locator(f"[data-pipeline='{path}']").click()
            assert page.locator("#pipeline-steps button").count() == count
            for index in range(count):
                page.locator(f"[data-step='{index}']").click()
                assert "d5125372adcc945c2314cfb649c50407379a18ab" in page.locator("#step-content a").get_attribute("href")
                assert page.locator("#step-content h3").inner_text()
        report["checks"].append("14 steps across 3 pipelines show pinned source evidence")
        texts = []
        for scenario in ["content", "character", "companion", "workflow"]:
            page.locator("#scenario").select_option(scenario)
            texts.append(page.locator("#scenario-result").inner_text())
        assert len(set(texts)) == 4
        report["checks"].append("4 distinct value and validation scenarios")

        # A separate clock-controlled page observes every intervening frame and phase.
        pet = browser.new_page(viewport={"width": 1100, "height": 900})
        pet.on("pageerror", lambda error: errors.append(str(error)))
        pet.clock.install()
        pet.goto(url, wait_until="networkidle", timeout=90000)
        pet.wait_for_function("document.querySelector('#pet-canvas').dataset.behavior === 'awake-story'")
        state = lambda name: pet.locator("#pet-canvas").get_attribute("data-" + name)
        choose = lambda name: pet.locator(f"[data-behavior='{name}']").click()
        event = lambda: pet.locator("#phase-event").click()
        choose("sleep-cycle")
        assert state("phase") == "sleep-enter"
        pet.clock.run_for(3500)
        assert state("phase") == "sleeping-loop"
        pet.clock.run_for(7000)
        assert state("phase") == "sleeping-loop"
        event()
        assert state("phase") == "wake-exit"
        pet.clock.run_for(2300)
        assert state("behavior") == "affection-click"
        report["checks"].append("persistent sleep, explicit wake exit, then click response")
        choose("explore-walk")
        pet.clock.run_for(1100)
        assert state("phase") == "walk-loop"
        pet.clock.run_for(4000)
        assert state("phase") == "walk-loop"
        event()
        assert state("phase") == "stop"
        pet.clock.run_for(2000)
        report["checks"].append("walk enters loop, awaits motion-finished, then stops")
        choose("held")
        pet.clock.run_for(2300)
        assert state("phase") == "held-loop"
        event()
        assert state("behavior") == "drop-recover" and state("phase") == "fall-loop"
        pet.clock.run_for(2200)
        assert state("phase") == "fall-loop"
        event()
        assert state("phase") == "impact"
        pet.clock.run_for(2600)
        assert state("phase") == "settle"
        report["checks"].append("held release leads to fall; floor-impact advances recovery")
        choose("cursor-encounter")
        pet.clock.run_for(1700)
        assert state("phase") == "approach"
        event()
        assert state("phase") == "touch"
        pet.clock.run_for(950)
        assert state("phase") == "retreat"
        event()
        assert state("phase") == "settle"
        report["checks"].append("cursor notice, approach, touch, retreat, settle sequence")
        choose("awake-story")
        pet.locator("#pause-pet").click()
        frame = state("frame")
        pet.clock.run_for(5000)
        assert state("paused") == "true" and state("frame") == frame
        pet.locator("#pause-pet").click()
        pet.clock.run_for(650)
        assert state("paused") == "false" and state("frame") != frame
        pet.locator("#pet-canvas").focus()
        pet.keyboard.press("Enter")
        assert state("behavior") == "affection-click"
        report["checks"].append("pause freezes frames, resume progresses, keyboard activates pet")
        pet.close()

        reduced = browser.new_page(reduced_motion="reduce")
        reduced.goto(url, wait_until="networkidle", timeout=90000)
        reduced.wait_for_function("document.querySelector('#pet-canvas').dataset.paused === 'true'")
        assert reduced.locator("#pause-pet").get_attribute("aria-pressed") == "true"
        reduced.close()
        report["checks"].append("reduced-motion defaults to a paused animation")

        offline_context = browser.new_context(offline=True)
        offline = offline_context.new_page()
        offline.on("pageerror", lambda error: errors.append(str(error)))
        network_requests = []
        offline.on("request", lambda request: network_requests.append(request.url) if request.url.startswith(("https://", "http://")) else None)
        offline.goto((ROOT / "web/standalone.html").as_uri(), wait_until="load")
        offline.wait_for_function("document.querySelector('#pet-canvas').dataset.behavior === 'awake-story'")
        offline.locator("#tab-fusion").click()
        offline.wait_for_function("document.querySelector('#output-image').complete && document.querySelector('#output-image').naturalWidth > 0")
        offline.locator("[data-behavior='sleep-cycle']").click()
        assert offline.locator("#pet-canvas").get_attribute("data-phase") == "sleep-enter"
        with offline.expect_download() as download:
            offline.get_by_role("link", name="下载研究笔记").click()
        assert download.value.suggested_filename == "research-notes.md"
        assert Path(download.value.path()).read_bytes() == (ROOT / "notes.md").read_bytes()
        assert not network_requests, "Offline page attempted a network request"
        offline_context.close()
        report["checks"].append("standalone file works with network offline, gallery, animation and notes download")

        for width in [320, 375, 390, 768, 1024, 1440]:
            page.set_viewport_size({"width": width, "height": 900})
            for capability in variants:
                page.locator(f"[data-capability='{capability}']").click()
                assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), f"Overflow at {width}, {capability}"
            page.locator("#tab-poster").click()
            assert page.evaluate("Array.from(document.images).filter(i => i.getAttribute('src')).every(i => i.complete && i.naturalWidth > 0)")
            report["viewports"].append({"width": width, "horizontal_overflow": False, "broken_images": 0})
        report["checks"].append("all 4 capability layouts fit 6 viewport widths")
        for name in ["research-notes.md", "SOURCE.json", "NOTICE.md", "LICENSE.upstream.txt", "example-pet-v3.zip"]:
            assert page.request.get(url + "downloads/" + name).status == 200
        report["checks"].append("all 5 downloadable files return HTTP 200")
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        page.screenshot(path=str(screenshots_dir / "overview.png"))
        page.locator("#pet-lab").screenshot(path=str(screenshots_dir / "preview-pet.png"))
        page.locator("#principles").screenshot(path=str(screenshots_dir / "preview-principles.png"))
        page.set_viewport_size({"width": 390, "height": 844})
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        page.screenshot(path=str(screenshots_dir / "preview-mobile-hero.png"))
        page.screenshot(path=str(screenshots_dir / "preview-mobile.png"), full_page=True)
        browser.close()
    assert not errors, errors
    assert not failed_responses, failed_responses
    report["page_errors"], report["failed_http_responses"] = errors, failed_responses
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8015/projects/015-heytea-style/web/")
    parser.add_argument("--screenshots-dir", help="Save verification screenshots without changing published assets")
    parser.add_argument("--report", help="Save a separate report, for example for public deployment verification")
    args = parser.parse_args()
    main(args.url.rstrip("/") + "/", args.screenshots_dir, args.report)

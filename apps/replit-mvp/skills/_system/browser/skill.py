"""
Browser automation skill - Safe web automation with screenshot artifacts
"""
from typing import Optional, List, Dict
import os
import re
import time
from playwright.sync_api import sync_playwright
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

SAFE_URL_RE = re.compile(r"^https?://", re.I)

class Inputs(SkillInputs):
    url: str
    extract_h1: bool = True
    extract_title: bool = True
    extract_images_alt_limit: int = 3
    wait_ms: int = 500  # light wait for network idle-like behavior

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "browser"
    version = "0.1.0"
    caps = {"net"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        if not SAFE_URL_RE.match(args.url):
            return Outputs(ok=False, message="Only http(s) URLs are allowed.")

        # screenshot path in tenant-scoped workdir
        os.makedirs(ctx.workdir, exist_ok=True)
        shot_path = os.path.join(ctx.workdir, f"snap_{int(time.time()*1000)}.png")

        result: Dict[str, object] = {"url": args.url}

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    page.goto(args.url, timeout=15000)
                    if args.wait_ms > 0:
                        page.wait_for_timeout(args.wait_ms)

                    if args.extract_title:
                        result["title"] = page.title()

                    if args.extract_h1:
                        h1 = page.locator("h1").first
                        result["h1"] = (h1.inner_text().strip() if h1.count() > 0 else None)

                    limit = max(0, int(args.extract_images_alt_limit))
                    if limit > 0:
                        alts = page.locator("img[alt]").evaluate_all("els => els.slice(0, arguments[0]).map(e=>e.getAttribute('alt'))", limit)
                        result["image_alts"] = [a for a in alts if a] if alts else []

                    page.screenshot(path=shot_path, full_page=True)
                finally:
                    browser.close()

            return Outputs(ok=True, data=result, artifacts={"screenshot": shot_path}, message="browser task done")
        
        except Exception as e:
            return Outputs(ok=False, message=f"Browser automation failed: {str(e)}")
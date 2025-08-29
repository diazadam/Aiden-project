"""
Enhanced browser automation skill - Multi-step automation with per-step screenshots
"""
from typing import Optional, List, Dict, Literal
import os
import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

SAFE_URL_RE = re.compile(r"^https?://", re.I)
SAFE_ACTIONS = {"open", "click", "type", "wait", "extract"}
MAX_SELECTOR_LEN = 256

class StepDict(SkillInputs):
    action: Literal["open","click","type","wait","extract"]
    selector: Optional[str] = None     # used by click/type/extract
    text: Optional[str] = None         # used by type
    timeout_ms: int = 5000             # for waits
    # extract fields
    extract: Optional[Literal["title","h1","alts"]] = None
    limit: int = 3                     # for alts

class Inputs(SkillInputs):
    url: str
    steps: List[StepDict] = []         # run after opening url
    screenshot_after_each: bool = True
    wait_ms: int = 500                 # initial settle wait
    headless: bool = True

class Outputs(SkillOutputs):
    pass

def _safe_selector(sel: Optional[str]) -> Optional[str]:
    """Validate and sanitize CSS selectors"""
    if sel is None:
        return None
    if len(sel) > MAX_SELECTOR_LEN:
        raise ValueError("selector too long")
    if sel.strip().lower().startswith(("javascript:", "data:")):
        raise ValueError("disallowed selector scheme")
    return sel

class SkillImpl(Skill):
    name = "browser"
    version = "0.2.0"
    caps = {"net"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        if not SAFE_URL_RE.match(args.url):
            return Outputs(ok=False, message="Only http(s) URLs are allowed.")

        os.makedirs(ctx.workdir, exist_ok=True)
        artifacts: Dict[str, str] = {}
        data: Dict[str, object] = {"url": args.url, "steps": []}
        shot_idx = 0

        def snapshot(page, label: str):
            """Take a screenshot and return the path"""
            nonlocal shot_idx
            path = os.path.join(ctx.workdir, f"browser_{int(time.time()*1000)}_{shot_idx}_{label}.png")
            shot_idx += 1
            page.screenshot(path=path, full_page=True)
            return path

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=args.headless)
                page = browser.new_page()
                try:
                    # Initial page load
                    page.goto(args.url, timeout=15000)
                    if args.wait_ms > 0: 
                        page.wait_for_timeout(args.wait_ms)
                    if args.screenshot_after_each:
                        artifacts[f"snap_0_open"] = snapshot(page, "open")

                    # Execute scripted steps
                    for i, step in enumerate(args.steps or []):
                        if step.action not in SAFE_ACTIONS:
                            data["steps"].append({
                                "i": i, 
                                "action": step.action, 
                                "ok": False, 
                                "error": "unsupported action"
                            })
                            continue

                        try:
                            if step.action == "open":
                                return Outputs(ok=False, message="Nested `open` not allowed; provide only initial url.")

                            elif step.action == "click":
                                sel = _safe_selector(step.selector)
                                page.locator(sel).first.click(timeout=step.timeout_ms)

                            elif step.action == "type":
                                sel = _safe_selector(step.selector)
                                page.locator(sel).first.fill(step.text or "", timeout=step.timeout_ms)

                            elif step.action == "wait":
                                # either wait for selector or just timeout_ms
                                if step.selector:
                                    sel = _safe_selector(step.selector)
                                    page.locator(sel).first.wait_for(timeout=step.timeout_ms)
                                else:
                                    page.wait_for_timeout(step.timeout_ms)

                            elif step.action == "extract":
                                result = None
                                if step.extract == "title":
                                    result = page.title()
                                elif step.extract == "h1":
                                    h1 = page.locator("h1").first
                                    result = (h1.inner_text().strip() if h1.count() > 0 else None)
                                elif step.extract == "alts":
                                    limit = max(0, int(step.limit or 3))
                                    alts = page.locator("img[alt]").evaluate_all(
                                        "els => els.slice(0, arguments[0]).map(e=>e.getAttribute('alt'))", limit
                                    )
                                    result = [a for a in (alts or []) if a]

                                data["steps"].append({
                                    "i": i, 
                                    "action": step.action, 
                                    "extract": step.extract, 
                                    "result": result
                                })
                                # Skip screenshot duplication – result recorded in data
                                continue

                            # Record successful step
                            data["steps"].append({"i": i, "action": step.action, "ok": True})
                            
                            # Take screenshot after each step (except extract)
                            if args.screenshot_after_each:
                                artifacts[f"snap_{i+1}_{step.action}"] = snapshot(page, step.action)

                        except PWTimeout as e:
                            data["steps"].append({
                                "i": i, 
                                "action": step.action, 
                                "ok": False, 
                                "error": "timeout"
                            })
                        except Exception as e:
                            data["steps"].append({
                                "i": i, 
                                "action": step.action, 
                                "ok": False, 
                                "error": str(e)[:200]
                            })
                finally:
                    browser.close()

        except Exception as e:
            return Outputs(ok=False, message=f"browser error: {str(e)[:200]}")

        return Outputs(ok=True, data=data, artifacts=artifacts, message="browser steps complete")
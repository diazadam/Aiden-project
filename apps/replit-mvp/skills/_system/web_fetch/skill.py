"""
Web fetch skill - Extract basic content from web pages
"""
from typing import List, Optional
import re
import requests
from bs4 import BeautifulSoup
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

class Inputs(SkillInputs):
    url: str

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "web_fetch"
    version = "0.1.0"
    caps = {"net"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        try:
            resp = requests.get(args.url, timeout=12)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Extract title
            title = (soup.title.string.strip() if soup.title and soup.title.string else None)
            
            # Extract first H1
            h1 = (soup.find("h1").get_text(strip=True) if soup.find("h1") else None)
            
            # Extract up to 3 image alt texts
            alts = []
            for img in soup.find_all("img"):
                if img.has_attr("alt") and img["alt"]:
                    alts.append(img["alt"])
                if len(alts) >= 3:
                    break
            
            return Outputs(
                ok=True, 
                data={
                    "title": title, 
                    "h1": h1, 
                    "image_alts": alts
                },
                message=f"Successfully fetched {args.url}"
            )
        except requests.RequestException as e:
            return Outputs(ok=False, message=f"Request failed: {str(e)}")
        except Exception as e:
            return Outputs(ok=False, message=f"Parse error: {str(e)}")
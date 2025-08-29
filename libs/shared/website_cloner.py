#!/usr/bin/env python3
"""
Aiden Pro Website Cloner & Remixer
Clone any website and remix components for rapid development
"""
import os, json, re, requests, subprocess, shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import tempfile
import base64

try:
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import cssutils
    import js2py
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

@dataclass
class ClonedComponent:
    name: str
    html: str
    css: str
    js: str
    assets: List[str]
    component_type: str  # header, navbar, hero, card, form, footer, etc.
    framework: str  # react, vue, vanilla, etc.
    responsive: bool
    dependencies: List[str]

@dataclass
class ClonedSite:
    url: str
    title: str
    pages: Dict[str, str]  # page_name -> html_content
    assets: Dict[str, bytes]  # asset_path -> content
    stylesheets: List[str]
    scripts: List[str]
    components: List[ClonedComponent]
    metadata: Dict
    clone_timestamp: datetime

class WebsiteCloner:
    def __init__(self):
        self.clone_dir = Path(__file__).parent.parent.parent / "cloned_sites"
        self.clone_dir.mkdir(exist_ok=True)
        
        self.components_dir = self.clone_dir / "components"
        self.components_dir.mkdir(exist_ok=True)
        
        self.remix_dir = self.clone_dir / "remixes"
        self.remix_dir.mkdir(exist_ok=True)
        
        # Component detection patterns
        self.component_patterns = {
            "navbar": [
                "nav", ".navbar", ".nav", ".navigation", 
                "[role='navigation']", ".header-nav"
            ],
            "hero": [
                ".hero", ".banner", ".jumbotron", ".hero-section",
                ".landing-hero", ".main-banner"
            ],
            "card": [
                ".card", ".box", ".tile", ".panel", 
                ".product-card", ".service-card"
            ],
            "form": [
                "form", ".form", ".contact-form", ".signup-form",
                ".login-form", ".search-form"
            ],
            "footer": [
                "footer", ".footer", ".site-footer", 
                "[role='contentinfo']"
            ],
            "header": [
                "header", ".header", ".site-header", 
                "[role='banner']"
            ],
            "sidebar": [
                ".sidebar", ".aside", "aside", ".side-nav",
                ".secondary-nav"
            ],
            "modal": [
                ".modal", ".popup", ".overlay", ".dialog",
                "[role='dialog']"
            ],
            "gallery": [
                ".gallery", ".image-grid", ".photo-gallery",
                ".carousel", ".slider"
            ],
            "testimonial": [
                ".testimonial", ".review", ".quote",
                ".customer-review"
            ]
        }
        
        # Framework detection patterns
        self.framework_patterns = {
            "react": ["react", "jsx", "_next", "react-dom"],
            "vue": ["vue", "nuxt", "vuejs"],
            "angular": ["angular", "ng-", "@angular"],
            "svelte": ["svelte", "_svelte"],
            "bootstrap": ["bootstrap", "bs-", "btn-"],
            "tailwind": ["tailwind", "tw-", "bg-", "text-", "p-", "m-"],
            "foundation": ["foundation", "fi-"],
            "bulma": ["bulma", "is-", "has-"],
            "materialize": ["materialize", "material"]
        }
    
    def clone_website(self, url: str, clone_name: str = None, 
                     pages: List[str] = None, deep_clone: bool = True) -> Dict:
        """Clone a complete website"""
        try:
            print(f"🌐 Cloning website: {url}")
            
            if not clone_name:
                clone_name = self._generate_clone_name(url)
            
            clone_path = self.clone_dir / clone_name
            clone_path.mkdir(exist_ok=True)
            
            # Initialize browser for dynamic content
            driver = self._get_webdriver()
            
            # Clone main page
            main_page = self._clone_page(url, driver)
            
            cloned_site = ClonedSite(
                url=url,
                title=main_page.get("title", ""),
                pages={"index": main_page["html"]},
                assets={},
                stylesheets=[],
                scripts=[],
                components=[],
                metadata={
                    "framework": self._detect_framework(main_page["html"]),
                    "responsive": self._is_responsive(main_page["html"]),
                    "clone_name": clone_name
                },
                clone_timestamp=datetime.now()
            )
            
            # Clone additional pages if specified
            if pages:
                for page_url in pages:
                    if not page_url.startswith("http"):
                        page_url = urljoin(url, page_url)
                    
                    page_data = self._clone_page(page_url, driver)
                    page_name = self._get_page_name(page_url)
                    cloned_site.pages[page_name] = page_data["html"]
            
            # Download assets if deep clone
            if deep_clone:
                assets_result = self._download_assets(url, main_page["html"], clone_path)
                cloned_site.assets = assets_result["assets"]
                cloned_site.stylesheets = assets_result["stylesheets"]
                cloned_site.scripts = assets_result["scripts"]
            
            # Extract reusable components
            components = self._extract_components(main_page["html"], cloned_site.metadata["framework"])
            cloned_site.components = components
            
            # Save cloned site
            self._save_cloned_site(cloned_site, clone_path)
            
            # Generate remix templates
            self._generate_remix_templates(cloned_site, clone_path)
            
            driver.quit()
            
            return {
                "success": True,
                "clone_name": clone_name,
                "clone_path": str(clone_path),
                "pages_cloned": len(cloned_site.pages),
                "assets_downloaded": len(cloned_site.assets),
                "components_extracted": len(cloned_site.components),
                "framework_detected": cloned_site.metadata["framework"],
                "responsive": cloned_site.metadata["responsive"]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def extract_component(self, url: str, component_selector: str, 
                         component_name: str = None, remix_for: str = "vanilla") -> Dict:
        """Extract a specific component from a website"""
        try:
            print(f"🎯 Extracting component from: {url}")
            
            driver = self._get_webdriver()
            page_data = self._clone_page(url, driver)
            
            soup = BeautifulSoup(page_data["html"], 'html.parser')
            
            # Find the component element
            component_element = soup.select_one(component_selector)
            if not component_element:
                driver.quit()
                return {"error": f"Component not found: {component_selector}"}
            
            # Extract component HTML
            component_html = str(component_element)
            
            # Extract relevant CSS
            component_css = self._extract_component_css(page_data["html"], component_selector)
            
            # Extract relevant JS
            component_js = self._extract_component_js(page_data["html"], component_selector)
            
            # Detect component type
            component_type = self._detect_component_type(component_html)
            
            # Get assets used by component
            component_assets = self._get_component_assets(component_html, url)
            
            component = ClonedComponent(
                name=component_name or f"{component_type}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                html=component_html,
                css=component_css,
                js=component_js,
                assets=component_assets,
                component_type=component_type,
                framework=self._detect_framework(component_html),
                responsive=self._is_responsive(component_html),
                dependencies=self._extract_dependencies(component_html)
            )
            
            # Convert to target framework if specified
            if remix_for != "vanilla":
                component = self._remix_component_for_framework(component, remix_for)
            
            # Save component
            component_path = self._save_component(component)
            
            driver.quit()
            
            return {
                "success": True,
                "component": component,
                "component_path": component_path,
                "component_type": component_type,
                "framework": component.framework,
                "remix_framework": remix_for
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def remix_components(self, components: List[ClonedComponent], 
                        remix_name: str, target_framework: str = "react",
                        layout_template: str = "modern") -> Dict:
        """Remix multiple components into a new page/app"""
        try:
            print(f"🎨 Remixing components into: {remix_name}")
            
            remix_path = self.remix_dir / remix_name
            remix_path.mkdir(exist_ok=True)
            
            # Generate layout based on template
            layout_html = self._generate_layout_template(layout_template, target_framework)
            
            # Process each component for the target framework
            remixed_components = []
            for component in components:
                remixed = self._remix_component_for_framework(component, target_framework)
                remixed_components.append(remixed)
            
            # Combine components into layout
            combined_html = self._combine_components_in_layout(
                layout_html, remixed_components, target_framework
            )
            
            # Generate necessary files
            files_generated = self._generate_remix_files(
                remix_path, combined_html, remixed_components, target_framework
            )
            
            # Create package.json if needed
            if target_framework in ["react", "vue", "svelte"]:
                self._generate_package_json(remix_path, target_framework, remix_name)
            
            return {
                "success": True,
                "remix_name": remix_name,
                "remix_path": str(remix_path),
                "components_remixed": len(remixed_components),
                "target_framework": target_framework,
                "files_generated": files_generated,
                "ready_for_development": True
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_component_library(self, source_urls: List[str], 
                               library_name: str = "aiden_components") -> Dict:
        """Create a reusable component library from multiple sites"""
        try:
            print(f"📚 Creating component library: {library_name}")
            
            library_path = self.components_dir / library_name
            library_path.mkdir(exist_ok=True)
            
            all_components = []
            
            # Extract components from each source
            for url in source_urls:
                clone_result = self.clone_website(url, deep_clone=False)
                if clone_result.get("success"):
                    # Load the cloned site
                    clone_path = Path(clone_result["clone_path"])
                    site_data_file = clone_path / "site_data.json"
                    
                    if site_data_file.exists():
                        with open(site_data_file, 'r') as f:
                            site_data = json.load(f)
                            all_components.extend(site_data.get("components", []))
            
            # Organize components by type
            organized_components = self._organize_components(all_components)
            
            # Generate documentation
            docs = self._generate_component_docs(organized_components, library_name)
            
            # Save component library
            self._save_component_library(library_path, organized_components, docs)
            
            return {
                "success": True,
                "library_name": library_name,
                "library_path": str(library_path),
                "total_components": len(all_components),
                "component_types": len(organized_components),
                "documentation_generated": True,
                "ready_for_use": True
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_webdriver(self) -> webdriver.Chrome:
        """Initialize Chrome webdriver for dynamic content"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        return webdriver.Chrome(options=options)
    
    def _clone_page(self, url: str, driver: webdriver.Chrome) -> Dict:
        """Clone a single page including dynamic content"""
        try:
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source after JavaScript execution
            html = driver.page_source
            title = driver.title
            
            # Get all loaded resources
            resources = driver.execute_script("""
                return performance.getEntriesByType('resource').map(r => ({
                    name: r.name,
                    type: r.initiatorType
                }));
            """)
            
            return {
                "html": html,
                "title": title,
                "url": url,
                "resources": resources,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _download_assets(self, base_url: str, html: str, save_path: Path) -> Dict:
        """Download CSS, JS, and image assets"""
        soup = BeautifulSoup(html, 'html.parser')
        assets = {}
        stylesheets = []
        scripts = []
        
        # Create assets directory
        assets_dir = save_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Download stylesheets
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            href = link.get('href')
            if href:
                asset_url = urljoin(base_url, href)
                asset_content = self._download_asset(asset_url)
                if asset_content:
                    asset_name = self._get_asset_name(href)
                    asset_path = assets_dir / f"css/{asset_name}"
                    asset_path.parent.mkdir(exist_ok=True)
                    asset_path.write_bytes(asset_content)
                    assets[f"css/{asset_name}"] = asset_content
                    stylesheets.append(f"css/{asset_name}")
        
        # Download scripts
        for script in soup.find_all('script', {'src': True}):
            src = script.get('src')
            if src:
                asset_url = urljoin(base_url, src)
                asset_content = self._download_asset(asset_url)
                if asset_content:
                    asset_name = self._get_asset_name(src)
                    asset_path = assets_dir / f"js/{asset_name}"
                    asset_path.parent.mkdir(exist_ok=True)
                    asset_path.write_bytes(asset_content)
                    assets[f"js/{asset_name}"] = asset_content
                    scripts.append(f"js/{asset_name}")
        
        # Download images
        for img in soup.find_all('img', {'src': True}):
            src = img.get('src')
            if src:
                asset_url = urljoin(base_url, src)
                asset_content = self._download_asset(asset_url)
                if asset_content:
                    asset_name = self._get_asset_name(src)
                    asset_path = assets_dir / f"images/{asset_name}"
                    asset_path.parent.mkdir(exist_ok=True)
                    asset_path.write_bytes(asset_content)
                    assets[f"images/{asset_name}"] = asset_content
        
        return {
            "assets": assets,
            "stylesheets": stylesheets,
            "scripts": scripts
        }
    
    def _download_asset(self, url: str) -> Optional[bytes]:
        """Download individual asset"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                return response.content
        except:
            pass
        return None
    
    def _extract_components(self, html: str, framework: str) -> List[ClonedComponent]:
        """Extract reusable components from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        components = []
        
        for component_type, selectors in self.component_patterns.items():
            for selector in selectors:
                elements = soup.select(selector)
                for i, element in enumerate(elements):
                    component = ClonedComponent(
                        name=f"{component_type}_{i+1}",
                        html=str(element),
                        css=self._extract_component_css(html, selector),
                        js="",  # Will be enhanced later
                        assets=self._get_component_assets(str(element), ""),
                        component_type=component_type,
                        framework=framework,
                        responsive=self._is_responsive(str(element)),
                        dependencies=self._extract_dependencies(str(element))
                    )
                    components.append(component)
        
        return components
    
    def _remix_component_for_framework(self, component: ClonedComponent, 
                                     target_framework: str) -> ClonedComponent:
        """Convert component to target framework"""
        if target_framework == "react":
            return self._convert_to_react(component)
        elif target_framework == "vue":
            return self._convert_to_vue(component)
        elif target_framework == "svelte":
            return self._convert_to_svelte(component)
        else:
            return component
    
    def _convert_to_react(self, component: ClonedComponent) -> ClonedComponent:
        """Convert component to React"""
        # Convert HTML attributes to React props
        html = component.html
        
        # Basic conversions
        conversions = {
            'class=': 'className=',
            'for=': 'htmlFor=',
            'onclick=': 'onClick=',
            'onchange=': 'onChange=',
            'oninput=': 'onInput=',
        }
        
        for old, new in conversions.items():
            html = html.replace(old, new)
        
        # Wrap in React component
        component_name = component.name.title().replace('_', '')
        react_component = f"""
import React from 'react';
import './{component.name}.css';

const {component_name} = () => {{
  return (
    {html}
  );
}};

export default {component_name};
"""
        
        return ClonedComponent(
            name=component.name,
            html=react_component,
            css=component.css,
            js="",
            assets=component.assets,
            component_type=component.component_type,
            framework="react",
            responsive=component.responsive,
            dependencies=component.dependencies + ["react"]
        )
    
    def _detect_framework(self, html: str) -> str:
        """Detect the framework used in the HTML"""
        html_lower = html.lower()
        
        for framework, patterns in self.framework_patterns.items():
            if any(pattern in html_lower for pattern in patterns):
                return framework
        
        return "vanilla"
    
    def _is_responsive(self, html: str) -> bool:
        """Check if the HTML is responsive"""
        responsive_indicators = [
            "@media", "viewport", "responsive", "col-", "flex", 
            "grid", "container", "row", "bootstrap"
        ]
        
        return any(indicator in html.lower() for indicator in responsive_indicators)
    
    def _save_cloned_site(self, site: ClonedSite, save_path: Path):
        """Save the cloned site data"""
        # Save HTML pages
        for page_name, html in site.pages.items():
            page_file = save_path / f"{page_name}.html"
            page_file.write_text(html, encoding='utf-8')
        
        # Save metadata
        metadata = {
            "url": site.url,
            "title": site.title,
            "pages": list(site.pages.keys()),
            "stylesheets": site.stylesheets,
            "scripts": site.scripts,
            "components": [
                {
                    "name": comp.name,
                    "type": comp.component_type,
                    "framework": comp.framework,
                    "responsive": comp.responsive
                } for comp in site.components
            ],
            "metadata": site.metadata,
            "clone_timestamp": site.clone_timestamp.isoformat()
        }
        
        metadata_file = save_path / "site_data.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def install_dependencies(self) -> Dict:
        """Install required dependencies for website cloning"""
        try:
            packages = [
                "beautifulsoup4",
                "selenium",
                "cssutils", 
                "js2py",
                "requests",
                "lxml"
            ]
            
            installed = []
            failed = []
            
            for package in packages:
                try:
                    subprocess.run(
                        ["pip", "install", package],
                        capture_output=True,
                        check=True
                    )
                    installed.append(package)
                except subprocess.CalledProcessError:
                    failed.append(package)
            
            # Also need Chrome driver
            try:
                subprocess.run(["brew", "install", "chromedriver"], capture_output=True)
                installed.append("chromedriver")
            except:
                failed.append("chromedriver")
            
            return {
                "success": len(failed) == 0,
                "installed": installed,
                "failed": failed
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    # Utility methods for component processing
    def _generate_clone_name(self, url: str) -> str:
        """Generate a clone name from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").replace(".", "_")
        return f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    def _get_asset_name(self, url: str) -> str:
        """Get asset name from URL"""
        parsed = urlparse(url)
        path = parsed.path
        if not path or path == "/":
            return "index"
        return Path(path).name or "asset"
    
    def _get_page_name(self, url: str) -> str:
        """Get page name from URL"""
        parsed = urlparse(url)
        path = parsed.path
        if not path or path == "/":
            return "index"
        return Path(path).stem or "page"

# Global instance
website_cloner = WebsiteCloner()
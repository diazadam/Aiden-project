"""
🌐 AIDEN BROWSER AUTOMATION V1 - PLAYWRIGHT INTEGRATION
Advanced web automation for intelligent browsing and data extraction.
"""

import asyncio
import json
import tempfile
import base64
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Try importing Playwright
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    async_playwright = None
    Browser = None
    Page = None
    BrowserContext = None
    PLAYWRIGHT_AVAILABLE = False


@dataclass
class BrowserResponse:
    """Standardized response for browser operations"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    screenshot_path: Optional[str] = None


class AidenBrowserAutomation:
    """Advanced browser automation with Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.default_timeout = 30000  # 30 seconds
        
    async def initialize(self, headless: bool = True, browser_type: str = "chromium") -> BrowserResponse:
        """Initialize browser automation system"""
        start_time = asyncio.get_event_loop().time()
        
        if not PLAYWRIGHT_AVAILABLE:
            return BrowserResponse(
                success=False,
                error="Playwright not installed. Run: pip install playwright && playwright install",
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000
            )
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser based on type
            if browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=headless)
            elif browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=headless)
            else:  # default to chromium
                self.browser = await self.playwright.chromium.launch(headless=headless)
            
            # Create context with realistic user agent
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Create initial page
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.default_timeout)
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={"browser_type": browser_type, "headless": headless},
                metadata={"ready": True},
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def navigate_to(self, url: str, wait_for: Optional[str] = None) -> BrowserResponse:
        """Navigate to a URL"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized. Call initialize() first.",
                execution_time_ms=0
            )
        
        try:
            # Navigate to URL
            response = await self.page.goto(url, wait_until="networkidle")
            
            # Wait for specific element if requested
            if wait_for:
                await self.page.wait_for_selector(wait_for)
            
            # Get page info
            title = await self.page.title()
            current_url = self.page.url
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={
                    "title": title,
                    "url": current_url,
                    "status": response.status if response else None
                },
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def extract_data(self, selectors: Dict[str, str]) -> BrowserResponse:
        """Extract data from page using CSS selectors"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized.",
                execution_time_ms=0
            )
        
        try:
            extracted_data = {}
            
            for key, selector in selectors.items():
                try:
                    # Wait for element to be present
                    await self.page.wait_for_selector(selector, timeout=5000)
                    
                    # Extract text content
                    element = await self.page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        extracted_data[key] = text.strip()
                    else:
                        extracted_data[key] = None
                        
                except Exception:
                    # Element not found or timeout
                    extracted_data[key] = None
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data=extracted_data,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def take_screenshot(self, path: Optional[str] = None, full_page: bool = True) -> BrowserResponse:
        """Take a screenshot of the current page"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized.",
                execution_time_ms=0
            )
        
        try:
            if not path:
                path = f"logs/screenshot_{int(datetime.now().timestamp())}.png"
            
            # Ensure directory exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            # Take screenshot
            await self.page.screenshot(path=path, full_page=full_page)
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={"screenshot_path": path, "full_page": full_page},
                screenshot_path=path,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def fill_form(self, form_data: Dict[str, str]) -> BrowserResponse:
        """Fill out form fields"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized.",
                execution_time_ms=0
            )
        
        try:
            filled_fields = {}
            
            for selector, value in form_data.items():
                try:
                    # Wait for field and fill it
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.fill(selector, value)
                    filled_fields[selector] = "success"
                except Exception as e:
                    filled_fields[selector] = f"failed: {str(e)}"
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={"filled_fields": filled_fields},
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def click_element(self, selector: str, wait_for_navigation: bool = False) -> BrowserResponse:
        """Click an element on the page"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized.",
                execution_time_ms=0
            )
        
        try:
            # Wait for element to be clickable
            await self.page.wait_for_selector(selector)
            
            if wait_for_navigation:
                # Click and wait for navigation
                async with self.page.expect_navigation():
                    await self.page.click(selector)
            else:
                await self.page.click(selector)
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={"clicked": selector, "navigation": wait_for_navigation},
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def execute_javascript(self, script: str) -> BrowserResponse:
        """Execute JavaScript on the page"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized.",
                execution_time_ms=0
            )
        
        try:
            result = await self.page.evaluate(script)
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={"result": result, "script": script},
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def wait_for_element(self, selector: str, timeout: int = 30000) -> BrowserResponse:
        """Wait for an element to appear"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized.",
                execution_time_ms=0
            )
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={"selector": selector, "found": True},
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def get_page_content(self) -> BrowserResponse:
        """Get full page content (HTML)"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.page:
            return BrowserResponse(
                success=False,
                error="Browser not initialized.",
                execution_time_ms=0
            )
        
        try:
            content = await self.page.content()
            title = await self.page.title()
            url = self.page.url
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={
                    "html": content,
                    "title": title,
                    "url": url,
                    "length": len(content)
                },
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def close(self) -> BrowserResponse:
        """Close browser and clean up resources"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=True,
                data={"closed": True},
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class BrowserTaskAutomation:
    """High-level browser task automation"""
    
    def __init__(self):
        self.browser = AidenBrowserAutomation()
    
    async def scrape_website_data(
        self, 
        url: str, 
        selectors: Dict[str, str],
        take_screenshot: bool = True
    ) -> BrowserResponse:
        """Complete website scraping workflow"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Initialize browser
            init_result = await self.browser.initialize()
            if not init_result.success:
                return init_result
            
            # Navigate to website
            nav_result = await self.browser.navigate_to(url)
            if not nav_result.success:
                return nav_result
            
            # Extract data
            data_result = await self.browser.extract_data(selectors)
            
            screenshot_path = None
            if take_screenshot:
                screenshot_result = await self.browser.take_screenshot()
                if screenshot_result.success:
                    screenshot_path = screenshot_result.data["screenshot_path"]
            
            # Close browser
            await self.browser.close()
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=data_result.success,
                data={
                    "url": url,
                    "extracted_data": data_result.data,
                    "page_info": nav_result.data,
                    "screenshot_path": screenshot_path
                },
                error=data_result.error,
                screenshot_path=screenshot_path,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            await self.browser.close()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def automate_form_submission(
        self,
        url: str,
        form_data: Dict[str, str],
        submit_selector: str,
        wait_after_submit: int = 3000
    ) -> BrowserResponse:
        """Complete form automation workflow"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Initialize browser
            init_result = await self.browser.initialize()
            if not init_result.success:
                return init_result
            
            # Navigate to form page
            nav_result = await self.browser.navigate_to(url)
            if not nav_result.success:
                return nav_result
            
            # Fill form fields
            fill_result = await self.browser.fill_form(form_data)
            if not fill_result.success:
                return fill_result
            
            # Take screenshot before submission
            before_screenshot = await self.browser.take_screenshot(
                path=f"logs/form_before_{int(datetime.now().timestamp())}.png"
            )
            
            # Submit form
            submit_result = await self.browser.click_element(submit_selector, wait_for_navigation=True)
            
            # Wait and take screenshot after submission
            await asyncio.sleep(wait_after_submit / 1000)
            after_screenshot = await self.browser.take_screenshot(
                path=f"logs/form_after_{int(datetime.now().timestamp())}.png"
            )
            
            # Get final page info
            final_content = await self.browser.get_page_content()
            
            # Close browser
            await self.browser.close()
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return BrowserResponse(
                success=submit_result.success,
                data={
                    "url": url,
                    "form_data": form_data,
                    "filled_fields": fill_result.data,
                    "submitted": submit_result.success,
                    "final_page": final_content.data if final_content.success else None,
                    "screenshots": {
                        "before": before_screenshot.screenshot_path if before_screenshot.success else None,
                        "after": after_screenshot.screenshot_path if after_screenshot.success else None
                    }
                },
                error=submit_result.error,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            await self.browser.close()
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return BrowserResponse(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )


# Global browser automation instance
browser_automation = AidenBrowserAutomation()


async def quick_scrape(url: str, selectors: Dict[str, str]) -> BrowserResponse:
    """Quick website scraping function"""
    task_automation = BrowserTaskAutomation()
    return await task_automation.scrape_website_data(url, selectors)


async def quick_form_submit(url: str, form_data: Dict[str, str], submit_selector: str) -> BrowserResponse:
    """Quick form submission function"""
    task_automation = BrowserTaskAutomation()
    return await task_automation.automate_form_submission(url, form_data, submit_selector)


# Export key classes and functions
__all__ = [
    "BrowserResponse",
    "AidenBrowserAutomation",
    "BrowserTaskAutomation",
    "browser_automation",
    "quick_scrape",
    "quick_form_submit",
    "PLAYWRIGHT_AVAILABLE"
]
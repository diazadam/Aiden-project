"""
Test suite for browser skill - Validates Playwright automation capabilities
"""
import os
from skills.registry import REGISTRY

def test_browser_skill_runs_example_com(tmp_path):
    """Test browser skill can navigate to example.com and extract content"""
    REGISTRY.load_all()
    rs = REGISTRY.get("browser")
    assert rs is not None and rs.enabled
    
    # Create mock context
    class MockContext:
        def __init__(self, workdir):
            self.account_id = "test"
            self.workdir = str(workdir)
            self.trace_id = "test_trace"
            self.caps_token = None
    
    ctx = MockContext(tmp_path)
    
    # Test browser skill
    out = rs.instance.run(
        ctx=ctx,
        args=rs.instance.Inputs(
            url="https://example.com", 
            extract_h1=True, 
            extract_title=True
        )
    )
    
    assert out.ok, f"Browser skill failed: {out.message}"
    assert out.data["title"] and "Example" in out.data["title"]
    assert out.data["h1"] and "Example" in out.data["h1"]
    assert "screenshot" in (out.artifacts or {})
    
    # Verify screenshot file was created
    screenshot_path = out.artifacts["screenshot"]
    assert os.path.exists(screenshot_path), "Screenshot file not created"
    assert os.path.getsize(screenshot_path) > 0, "Screenshot file is empty"

def test_browser_skill_rejects_invalid_urls():
    """Test browser skill rejects non-http(s) URLs"""
    REGISTRY.load_all()
    rs = REGISTRY.get("browser")
    assert rs is not None
    
    class MockContext:
        def __init__(self):
            self.account_id = "test"
            self.workdir = "/tmp"
            self.trace_id = "test_trace"  
            self.caps_token = None
    
    ctx = MockContext()
    
    # Test invalid URL
    out = rs.instance.run(
        ctx=ctx,
        args=rs.instance.Inputs(url="ftp://invalid.url")
    )
    
    assert not out.ok
    assert "Only http(s) URLs are allowed" in out.message
"""
Browser actions test suite for multi-step automation validation

Tests the enhanced browser skill's multi-step automation capabilities:
- Open page and take initial screenshot
- Execute click/type/wait/extract actions
- Validate per-step screenshot artifacts
- Test error handling and timeout scenarios
"""
import os
import sys
sys.path.append('/Users/adammach/aiden-project/apps/replit-mvp')
import json
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from skills.runtime import run_skill
from skills.contracts import SkillContext


class TestBrowserActions:
    """Test suite for browser multi-step automation"""

    @pytest.fixture
    def browser_context(self):
        """Create a test context with temporary workdir"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SkillContext(
                account_id="test",
                workdir=tmpdir,
                trace_id="test-trace-123"
            )

    def test_basic_page_open_with_screenshot(self, browser_context):
        """Test basic page open with screenshot artifact"""
        from skills.registry import REGISTRY
        REGISTRY.load_all()  # Load skills before testing
        
        with patch('playwright.sync_api.sync_playwright') as mock_pw, \
             patch('security.policies.CapsPolicy') as mock_policy, \
             patch('security.policies.SECRET_PIN', 'test-pin'):
            
            # Mock security policy 
            mock_policy.return_value.requires_pin.return_value = False
            
            # Mock Playwright components
            mock_browser = Mock()
            mock_page = Mock()
            mock_page.title.return_value = "Test Page"
            mock_page.screenshot.return_value = None
            mock_browser.new_page.return_value = mock_page
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

            inputs = {
                "url": "https://example.com",
                "screenshot_after_each": True,
                "headless": True
            }

            result = run_skill("browser", "test", inputs, caps_token="test-pin")

            assert result.ok is True
            assert "browser steps complete" in result.message
            assert result.data["url"] == "https://example.com"
            assert "snap_0_open" in result.artifacts
            mock_page.goto.assert_called_once_with("https://example.com", timeout=15000)

    def test_multi_step_automation_sequence(self, browser_context):
        """Test complete multi-step automation with all action types"""
        with patch('skills._system.browser.skill.sync_playwright') as mock_pw:
            # Mock Playwright components
            mock_browser = Mock()
            mock_page = Mock()
            mock_locator = Mock()
            mock_page.locator.return_value = mock_locator
            mock_locator.first = mock_locator
            mock_page.title.return_value = "Search Results"
            mock_page.screenshot.return_value = None
            mock_browser.new_page.return_value = mock_page
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

            inputs = {
                "url": "https://example.com",
                "steps": [
                    {"action": "click", "selector": "#search-button"},
                    {"action": "type", "selector": "input[name='q']", "text": "test query"},
                    {"action": "wait", "timeout_ms": 1000},
                    {"action": "extract", "extract": "title"}
                ],
                "screenshot_after_each": True
            }

            result = run_skill("browser", "test", inputs, caps_token="test-pin")

            assert result.ok is True
            assert len(result.data["steps"]) == 4
            
            # Verify click action
            assert result.data["steps"][0]["action"] == "click"
            assert result.data["steps"][0]["ok"] is True
            
            # Verify type action  
            assert result.data["steps"][1]["action"] == "type"
            assert result.data["steps"][1]["ok"] is True
            
            # Verify wait action
            assert result.data["steps"][2]["action"] == "wait"
            assert result.data["steps"][2]["ok"] is True
            
            # Verify extract action
            assert result.data["steps"][3]["action"] == "extract"
            assert result.data["steps"][3]["result"] == "Search Results"

            # Verify screenshots taken for each step (except extract)
            assert "snap_1_click" in result.artifacts
            assert "snap_2_type" in result.artifacts  
            assert "snap_3_wait" in result.artifacts
            # Extract doesn't generate screenshot

            mock_locator.click.assert_called_once()
            mock_locator.fill.assert_called_once_with("test query", timeout=5000)

    def test_extract_actions_all_types(self, browser_context):
        """Test all extract action types: title, h1, alts"""
        with patch('skills._system.browser.skill.sync_playwright') as mock_pw:
            mock_browser = Mock()
            mock_page = Mock()
            
            # Mock different locator responses
            mock_title_loc = Mock()
            mock_h1_loc = Mock() 
            mock_img_loc = Mock()
            
            mock_page.title.return_value = "Page Title"
            mock_h1_loc.count.return_value = 1
            mock_h1_loc.inner_text.return_value = "Main Heading"
            mock_img_loc.evaluate_all.return_value = ["Alt text 1", "Alt text 2"]
            
            def locator_side_effect(selector):
                if selector == "h1":
                    return mock_h1_loc
                elif selector == "img[alt]":
                    return mock_img_loc
                return Mock()
            
            mock_page.locator.side_effect = locator_side_effect
            mock_page.screenshot.return_value = None
            mock_browser.new_page.return_value = mock_page
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

            inputs = {
                "url": "https://example.com",
                "steps": [
                    {"action": "extract", "extract": "title"},
                    {"action": "extract", "extract": "h1"}, 
                    {"action": "extract", "extract": "alts", "limit": 2}
                ]
            }

            result = run_skill("browser", "test", inputs, caps_token="test-pin")

            assert result.ok is True
            assert len(result.data["steps"]) == 3
            
            # Check title extraction
            assert result.data["steps"][0]["result"] == "Page Title"
            
            # Check h1 extraction
            assert result.data["steps"][1]["result"] == "Main Heading"
            
            # Check alts extraction
            assert result.data["steps"][2]["result"] == ["Alt text 1", "Alt text 2"]

    def test_error_handling_timeout(self, browser_context):
        """Test error handling for timeout scenarios"""
        with patch('skills._system.browser.skill.sync_playwright') as mock_pw:
            from playwright.sync_api import TimeoutError as PWTimeout
            
            mock_browser = Mock()
            mock_page = Mock()
            mock_locator = Mock()
            mock_locator.first.click.side_effect = PWTimeout("Element not found")
            mock_page.locator.return_value = mock_locator
            mock_page.screenshot.return_value = None
            mock_browser.new_page.return_value = mock_page
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

            inputs = {
                "url": "https://example.com", 
                "steps": [
                    {"action": "click", "selector": "#missing-element", "timeout_ms": 1000}
                ]
            }

            result = run_skill("browser", "test", inputs, caps_token="test-pin")

            assert result.ok is True  # Overall success even with step failure
            assert len(result.data["steps"]) == 1
            assert result.data["steps"][0]["ok"] is False
            assert result.data["steps"][0]["error"] == "timeout"

    def test_invalid_url_rejection(self, browser_context):
        """Test rejection of invalid/unsafe URLs"""
        inputs = {
            "url": "javascript:alert('xss')",
            "steps": []
        }

        result = run_skill("browser", "test", inputs, caps_token="test-pin")

        assert result.ok is False
        assert "Only http(s) URLs are allowed" in result.message

    def test_unsafe_selector_rejection(self, browser_context):
        """Test rejection of unsafe CSS selectors"""
        with patch('skills._system.browser.skill.sync_playwright') as mock_pw:
            mock_browser = Mock()
            mock_page = Mock()
            mock_page.screenshot.return_value = None
            mock_browser.new_page.return_value = mock_page
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

            inputs = {
                "url": "https://example.com",
                "steps": [
                    {"action": "click", "selector": "javascript:alert('xss')"}
                ]
            }

            result = run_skill("browser", "test", inputs, caps_token="test-pin")

            # Should complete overall but reject the unsafe step
            assert result.ok is True
            assert result.data["steps"][0]["ok"] is False
            assert "error" in result.data["steps"][0]

    def test_nested_open_action_rejection(self, browser_context):
        """Test rejection of nested 'open' actions in steps"""
        with patch('skills._system.browser.skill.sync_playwright') as mock_pw:
            mock_browser = Mock()
            mock_page = Mock()
            mock_page.screenshot.return_value = None
            mock_browser.new_page.return_value = mock_page
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

            inputs = {
                "url": "https://example.com",
                "steps": [
                    {"action": "open"}  # Invalid - nested open
                ]
            }

            result = run_skill("browser", "test", inputs, caps_token="test-pin")

            assert result.ok is False
            assert "Nested `open` not allowed" in result.message

    def test_screenshot_artifacts_naming(self, browser_context):
        """Test screenshot artifact naming convention"""
        with patch('skills._system.browser.skill.sync_playwright') as mock_pw:
            mock_browser = Mock()
            mock_page = Mock()
            mock_locator = Mock()
            mock_page.locator.return_value = mock_locator
            mock_locator.first = mock_locator
            mock_page.screenshot.return_value = None
            mock_browser.new_page.return_value = mock_page
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

            inputs = {
                "url": "https://example.com",
                "steps": [
                    {"action": "click", "selector": "#btn1"},
                    {"action": "type", "selector": "#input1", "text": "test"}
                ],
                "screenshot_after_each": True
            }

            result = run_skill("browser", "test", inputs, caps_token="test-pin")

            assert result.ok is True
            
            # Check artifact naming pattern: snap_{step}_{action}
            assert "snap_0_open" in result.artifacts
            assert "snap_1_click" in result.artifacts
            assert "snap_2_type" in result.artifacts
            
            # Verify file paths contain timestamp and step info
            for artifact_path in result.artifacts.values():
                assert artifact_path.endswith(".png")
                assert "browser_" in os.path.basename(artifact_path)
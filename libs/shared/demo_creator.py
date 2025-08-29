#!/usr/bin/env python3
"""
Aiden Pro Demo Creator & Screen Recorder
Create amazing demos and advertisements automatically
"""
import os, json, subprocess, tempfile, time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
import threading
import asyncio

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import moviepy.editor as mp
    from moviepy.config import check_output_path
    import pyautogui
    import pyttsx3
    MEDIA_DEPENDENCIES_AVAILABLE = True
except ImportError:
    MEDIA_DEPENDENCIES_AVAILABLE = False

@dataclass
class DemoScene:
    name: str
    duration: float
    script: str
    actions: List[Dict]  # mouse, keyboard, wait, highlight actions
    voiceover: str
    background_music: str = ""
    transitions: Dict = None

@dataclass
class DemoProject:
    name: str
    description: str
    scenes: List[DemoScene]
    output_format: str  # mp4, gif, webm
    resolution: tuple  # (width, height)
    fps: int
    branding: Dict  # logo, colors, fonts
    metadata: Dict

class DemoCreator:
    def __init__(self):
        self.projects_dir = Path(__file__).parent.parent.parent / "demos"
        self.projects_dir.mkdir(exist_ok=True)
        
        self.assets_dir = self.projects_dir / "assets"
        self.assets_dir.mkdir(exist_ok=True)
        
        self.recordings_dir = self.projects_dir / "recordings"
        self.recordings_dir.mkdir(exist_ok=True)
        
        # Screen recording settings
        self.recording = False
        self.current_recording = None
        
        # Demo templates
        self.templates = {
            "product_showcase": {
                "scenes": ["intro", "features", "demo", "call_to_action"],
                "duration": 60,
                "style": "modern"
            },
            "tutorial": {
                "scenes": ["introduction", "step_by_step", "summary"],
                "duration": 120,
                "style": "educational"
            },
            "advertisement": {
                "scenes": ["hook", "problem", "solution", "benefits", "cta"],
                "duration": 30,
                "style": "commercial"
            },
            "feature_demo": {
                "scenes": ["setup", "demonstration", "results"],
                "duration": 45,
                "style": "technical"
            }
        }
        
        # Initialize TTS engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
        except:
            self.tts_engine = None
    
    def create_aiden_advertisement(self, features_to_showcase: List[str], 
                                 duration: int = 60, style: str = "modern") -> Dict:
        """Create an advertisement showcasing Aiden's capabilities"""
        try:
            print(f"🎬 Creating Aiden advertisement - {duration}s {style} style")
            
            # Generate demo script
            script = self._generate_aiden_script(features_to_showcase, duration, style)
            
            # Create scenes
            scenes = self._create_aiden_scenes(script, features_to_showcase)
            
            # Setup project
            project = DemoProject(
                name=f"aiden_ad_{datetime.now().strftime('%Y%m%d_%H%M')}",
                description="Aiden AI Assistant Advertisement",
                scenes=scenes,
                output_format="mp4",
                resolution=(1920, 1080),
                fps=30,
                branding={
                    "colors": ["#2563eb", "#1d4ed8", "#3b82f6"],  # Blue theme
                    "font": "SF Pro Display",
                    "logo": "aiden_logo.png"
                },
                metadata={
                    "features": features_to_showcase,
                    "style": style,
                    "duration": duration
                }
            )
            
            # Record the demo
            recording_result = self._record_aiden_demo(project)
            
            # Generate voiceover
            voiceover_result = self._generate_voiceover(project)
            
            # Create final video
            video_result = self._create_final_video(project, recording_result, voiceover_result)
            
            return {
                "success": True,
                "project_name": project.name,
                "video_path": video_result.get("path"),
                "duration": duration,
                "scenes": len(scenes),
                "features_showcased": features_to_showcase,
                "ready_for_sharing": True
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def record_screen_demo(self, demo_name: str, duration: int = 60, 
                          region: tuple = None, with_audio: bool = True) -> Dict:
        """Record a screen demonstration"""
        try:
            print(f"📹 Recording screen demo: {demo_name}")
            
            # Setup recording
            if not region:
                region = (0, 0, *pyautogui.size())
            
            output_path = self.recordings_dir / f"{demo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            # Start recording
            recording_result = self._start_screen_recording(output_path, region, duration, with_audio)
            
            if recording_result.get("success"):
                # Process recording
                processed_result = self._process_recording(output_path)
                
                return {
                    "success": True,
                    "demo_name": demo_name,
                    "recording_path": str(output_path),
                    "duration": duration,
                    "resolution": region[2:],
                    "file_size": output_path.stat().st_size if output_path.exists() else 0,
                    "processed": processed_result.get("success", False)
                }
            else:
                return recording_result
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_tutorial_video(self, topic: str, steps: List[Dict], 
                            tutorial_type: str = "screen_recording") -> Dict:
        """Create a comprehensive tutorial video"""
        try:
            print(f"🎓 Creating tutorial: {topic}")
            
            tutorial_name = f"tutorial_{topic.lower().replace(' ', '_')}"
            
            # Generate tutorial script
            script = self._generate_tutorial_script(topic, steps)
            
            # Create tutorial scenes
            scenes = self._create_tutorial_scenes(script, steps, tutorial_type)
            
            project = DemoProject(
                name=tutorial_name,
                description=f"Tutorial: {topic}",
                scenes=scenes,
                output_format="mp4",
                resolution=(1920, 1080),
                fps=30,
                branding={
                    "colors": ["#059669", "#10b981", "#34d399"],  # Green theme
                    "font": "Inter",
                    "logo": "tutorial_logo.png"
                },
                metadata={
                    "topic": topic,
                    "steps": len(steps),
                    "type": tutorial_type
                }
            )
            
            if tutorial_type == "screen_recording":
                # Record actual screen demo
                recording_result = self._record_tutorial_demo(project, steps)
            else:
                # Create animated tutorial
                recording_result = self._create_animated_tutorial(project, steps)
            
            # Add voiceover and effects
            final_result = self._finalize_tutorial(project, recording_result)
            
            return {
                "success": True,
                "tutorial_name": tutorial_name,
                "video_path": final_result.get("path"),
                "topic": topic,
                "steps_covered": len(steps),
                "type": tutorial_type,
                "ready_for_publishing": True
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_product_showcase(self, product_name: str, features: List[str], 
                              showcase_style: str = "premium") -> Dict:
        """Create a polished product showcase video"""
        try:
            print(f"✨ Creating product showcase: {product_name}")
            
            showcase_name = f"showcase_{product_name.lower().replace(' ', '_')}"
            
            # Design showcase flow
            showcase_flow = self._design_showcase_flow(product_name, features, showcase_style)
            
            # Create scenes
            scenes = self._create_showcase_scenes(showcase_flow, showcase_style)
            
            project = DemoProject(
                name=showcase_name,
                description=f"Product Showcase: {product_name}",
                scenes=scenes,
                output_format="mp4",
                resolution=(1920, 1080),
                fps=60,  # Higher FPS for premium feel
                branding={
                    "colors": ["#7c3aed", "#8b5cf6", "#a78bfa"],  # Purple theme
                    "font": "SF Pro Display",
                    "logo": "product_logo.png"
                },
                metadata={
                    "product": product_name,
                    "features": features,
                    "style": showcase_style
                }
            )
            
            # Record showcase
            recording_result = self._record_showcase(project, showcase_flow)
            
            # Add premium effects
            effects_result = self._add_premium_effects(project, recording_result)
            
            # Generate final video
            final_result = self._generate_showcase_video(project, effects_result)
            
            return {
                "success": True,
                "showcase_name": showcase_name,
                "video_path": final_result.get("path"),
                "product": product_name,
                "features_showcased": len(features),
                "style": showcase_style,
                "premium_quality": True
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_social_media_ad(self, platform: str, content: Dict, 
                             ad_type: str = "engagement") -> Dict:
        """Create platform-optimized social media advertisements"""
        try:
            print(f"📱 Creating {platform} ad - {ad_type}")
            
            # Platform-specific settings
            platform_specs = self._get_platform_specs(platform)
            
            ad_name = f"{platform}_ad_{ad_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            # Create ad content
            ad_scenes = self._create_social_ad_scenes(content, ad_type, platform_specs)
            
            project = DemoProject(
                name=ad_name,
                description=f"{platform} Advertisement - {ad_type}",
                scenes=ad_scenes,
                output_format="mp4",
                resolution=platform_specs["resolution"],
                fps=30,
                branding=content.get("branding", {}),
                metadata={
                    "platform": platform,
                    "ad_type": ad_type,
                    "content": content
                }
            )
            
            # Create the ad
            creation_result = self._create_social_ad(project, platform_specs)
            
            # Optimize for platform
            optimized_result = self._optimize_for_platform(project, creation_result, platform)
            
            return {
                "success": True,
                "ad_name": ad_name,
                "platform": platform,
                "video_path": optimized_result.get("path"),
                "duration": platform_specs.get("max_duration", 30),
                "optimized": True,
                "ready_for_upload": True
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_aiden_script(self, features: List[str], duration: int, style: str) -> Dict:
        """Generate script for Aiden advertisement"""
        if style == "modern":
            hook = "Meet Aiden - the AI assistant that actually does what you ask."
        elif style == "professional":
            hook = "Introducing Aiden Pro - advanced AI automation for modern businesses."
        else:
            hook = "Tired of AI that just talks? Meet Aiden - the AI that takes action."
        
        # Generate feature demonstrations
        feature_demos = []
        for feature in features:
            if feature == "website_cloning":
                feature_demos.append({
                    "text": "Clone any website and remix it instantly",
                    "action": "demonstrate_website_cloning",
                    "duration": 8
                })
            elif feature == "google_cloud":
                feature_demos.append({
                    "text": "Deploy to Google Cloud with a single command",
                    "action": "demonstrate_cloud_deployment", 
                    "duration": 7
                })
            elif feature == "automation":
                feature_demos.append({
                    "text": "Automate complex workflows with n8n integration",
                    "action": "demonstrate_automation",
                    "duration": 8
                })
            elif feature == "self_improvement":
                feature_demos.append({
                    "text": "Continuously learns and improves itself",
                    "action": "demonstrate_learning",
                    "duration": 6
                })
        
        return {
            "hook": hook,
            "features": feature_demos,
            "call_to_action": "Ready to work smarter? Get Aiden today.",
            "total_duration": duration
        }
    
    def _create_aiden_scenes(self, script: Dict, features: List[str]) -> List[DemoScene]:
        """Create demo scenes for Aiden advertisement"""
        scenes = []
        
        # Intro scene
        scenes.append(DemoScene(
            name="intro",
            duration=5.0,
            script=script["hook"],
            actions=[
                {"type": "title_animation", "text": script["hook"]},
                {"type": "logo_reveal", "logo": "aiden_logo.png"}
            ],
            voiceover=script["hook"]
        ))
        
        # Feature demonstration scenes
        for i, feature_demo in enumerate(script["features"]):
            scenes.append(DemoScene(
                name=f"feature_{i+1}",
                duration=feature_demo["duration"],
                script=feature_demo["text"],
                actions=[
                    {"type": "screen_demo", "action": feature_demo["action"]},
                    {"type": "highlight", "areas": ["demo_result"]}
                ],
                voiceover=feature_demo["text"]
            ))
        
        # Call to action scene
        scenes.append(DemoScene(
            name="cta",
            duration=5.0,
            script=script["call_to_action"],
            actions=[
                {"type": "cta_animation", "text": script["call_to_action"]},
                {"type": "contact_info", "display": "github.com/aiden-ai"}
            ],
            voiceover=script["call_to_action"]
        ))
        
        return scenes
    
    def _start_screen_recording(self, output_path: Path, region: tuple, 
                              duration: int, with_audio: bool) -> Dict:
        """Start screen recording using system tools"""
        try:
            # Use macOS screen recording
            cmd = [
                "screencapture", 
                "-v",  # Video
                "-r", "30",  # Frame rate
                "-R", f"{region[0]},{region[1]},{region[2]},{region[3]}",  # Region
                str(output_path)
            ]
            
            if with_audio:
                cmd.append("-a")  # Audio
            
            # Start recording in background
            process = subprocess.Popen(cmd)
            
            # Wait for specified duration
            time.sleep(duration)
            
            # Stop recording
            process.terminate()
            
            return {"success": True, "process_id": process.pid}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_voiceover(self, project: DemoProject) -> Dict:
        """Generate voiceover for all scenes"""
        if not self.tts_engine:
            return {"error": "TTS engine not available"}
        
        try:
            voiceover_files = []
            
            for scene in project.scenes:
                if scene.voiceover:
                    audio_path = self.assets_dir / f"{project.name}_{scene.name}_voice.wav"
                    
                    # Generate speech
                    self.tts_engine.save_to_file(scene.voiceover, str(audio_path))
                    self.tts_engine.runAndWait()
                    
                    voiceover_files.append(str(audio_path))
            
            return {
                "success": True,
                "files": voiceover_files,
                "total_scenes": len(voiceover_files)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_platform_specs(self, platform: str) -> Dict:
        """Get platform-specific video specifications"""
        specs = {
            "instagram": {
                "resolution": (1080, 1080),  # Square
                "max_duration": 60,
                "aspect_ratio": "1:1"
            },
            "tiktok": {
                "resolution": (1080, 1920),  # Vertical
                "max_duration": 60,
                "aspect_ratio": "9:16"
            },
            "youtube": {
                "resolution": (1920, 1080),  # Horizontal
                "max_duration": 300,
                "aspect_ratio": "16:9"
            },
            "twitter": {
                "resolution": (1200, 675),  # Horizontal
                "max_duration": 140,
                "aspect_ratio": "16:9"
            },
            "linkedin": {
                "resolution": (1200, 627),  # Horizontal
                "max_duration": 600,
                "aspect_ratio": "1.91:1"
            }
        }
        
        return specs.get(platform, specs["youtube"])
    
    def install_dependencies(self) -> Dict:
        """Install required dependencies for demo creation"""
        try:
            packages = [
                "opencv-python",
                "pillow",
                "moviepy",
                "pyautogui",
                "pyttsx3",
                "numpy"
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
            
            # Install FFmpeg for video processing
            try:
                subprocess.run(["brew", "install", "ffmpeg"], capture_output=True)
                installed.append("ffmpeg")
            except:
                failed.append("ffmpeg")
            
            return {
                "success": len(failed) == 0,
                "installed": installed,
                "failed": failed
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_demo_templates(self) -> Dict:
        """Get available demo templates"""
        return {
            "templates": self.templates,
            "total": len(self.templates),
            "categories": ["product", "tutorial", "advertisement", "showcase"]
        }

# Global instance
demo_creator = DemoCreator()
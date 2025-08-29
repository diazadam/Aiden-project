"""
Expo app scaffolding skill - Creates complete React Native app with EAS configuration.

Features:
- Creates Expo app using create-expo-app template
- Configures app.json with custom name, slug, bundle IDs
- Generates EAS build configuration
- Creates branded icon and splash screen assets
- Sets up deep linking and proper iOS/Android identifiers
"""
import os, json, subprocess, sys, shutil
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

def _run(cmd, cwd=None, env=None, timeout=600):
    """Run subprocess command with timeout and error handling"""
    p = subprocess.Popen(cmd, cwd=cwd, env=env or os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out, err

class Inputs(SkillInputs):
    app_name: str
    slug: Optional[str] = None
    bundle_identifier: Optional[str] = None   # e.g., com.company.app
    scheme: Optional[str] = None              # deep link scheme
    theme_color: str = "#0ea5e9"              # sky-500 default
    icon_text: str = "A"                      # single letter for icon

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "mobile_expo_scaffold"
    version = "0.1.0"
    caps = {"fs_write","exec","net"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        # Prepare project directory
        project_name = (args.slug or args.app_name).lower().replace(' ','-')
        proj_dir = os.path.join(ctx.workdir, project_name)
        
        if os.path.exists(proj_dir): 
            shutil.rmtree(proj_dir)
        os.makedirs(proj_dir, exist_ok=True)

        # 1) Create Expo app using latest template  
        try:
            code, out, err = _run(["npx","--yes","create-expo-app@latest", proj_dir, "--template","blank"])
            if code != 0:
                return Outputs(ok=False, message=f"create-expo-app failed: {err[:300]}")
        except subprocess.TimeoutExpired:
            return Outputs(ok=False, message="create-expo-app timed out")

        # 2) Configure app.json with custom settings
        appjson = {
          "expo": {
            "name": args.app_name,
            "slug": (args.slug or args.app_name).lower().replace(" ","-"),
            "scheme": args.scheme or (args.slug or args.app_name).lower().replace(" ",""),
            "ios": {
                "bundleIdentifier": args.bundle_identifier or f"com.example.{project_name.replace('-','')}"
            },
            "android": {
                "package": (args.bundle_identifier or f"com.example.{project_name.replace('-','')}").replace("com.","com.example.")
            },
            "runtimeVersion": {"policy": "appVersion"},
            "version": "1.0.0",
            "orientation": "portrait",
            "icon": "./assets/icon.png",
            "splash": {
                "image":"./assets/splash.png",
                "resizeMode":"contain",
                "backgroundColor": args.theme_color
            },
            "extra": {
                "eas": {
                    "projectId": "placeholder-will-be-set-on-first-build"
                }
            }
          }
        }
        
        with open(os.path.join(proj_dir,"app.json"),"w") as f:
            json.dump(appjson,f,indent=2)

        # 3) Configure EAS build settings
        easjson = {
          "cli": {"appVersionSource":"app.json"},
          "build": {
            "preview": {
                "distribution":"internal",
                "ios":{"resourceClass":"m-medium"},
                "channel":"preview"
            },
            "production": {
                "channel":"production" 
            }
          },
          "submit": {
            "production": {}
          }
        }
        
        with open(os.path.join(proj_dir,"eas.json"),"w") as f:
            json.dump(easjson,f,indent=2)

        # 4) Generate branded icon and splash assets
        assets_dir = os.path.join(proj_dir,"assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Generate 1024x1024 icon with theme color and letter
        icon = Image.new("RGBA", (1024,1024), args.theme_color)
        d = ImageDraw.Draw(icon)
        
        # Draw circular background with border
        d.ellipse([64,64,960,960], fill=args.theme_color, outline="#ffffff", width=32)
        
        # Draw letter in center (simplified - no font dependency)
        letter = args.icon_text.upper()[:1] if args.icon_text else "A"
        
        # Simple block letter rendering (can be enhanced with actual fonts)
        if letter == "A":
            # Draw simple "A" shape
            d.polygon([(400,700), (512,300), (624,700), (580,700), (560,640), (464,640), (444,700)], fill="#ffffff")
            d.rectangle([480,550,544,590], fill=args.theme_color)  # crossbar
        else:
            # Fallback: draw a rectangle for other letters
            d.rectangle([400,300,624,700], fill="#ffffff")
            d.rectangle([450,350,574,650], fill=args.theme_color)
        
        icon.save(os.path.join(assets_dir,"icon.png"))

        # Generate 2048x2048 splash screen
        splash = Image.new("RGBA", (2048,2048), args.theme_color)
        splash_draw = ImageDraw.Draw(splash)
        
        # Add centered app name text (simple approach)
        splash_draw.rectangle([512,900,1536,1148], fill="#ffffff", outline=args.theme_color, width=8)
        
        splash.save(os.path.join(assets_dir,"splash.png"))

        # 5) Update package.json with EAS build script
        package_json_path = os.path.join(proj_dir, "package.json")
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Add EAS build scripts
            if "scripts" not in package_data:
                package_data["scripts"] = {}
            
            package_data["scripts"]["build:ios"] = "eas build --platform ios"
            package_data["scripts"]["build:android"] = "eas build --platform android"
            package_data["scripts"]["submit:ios"] = "eas submit --platform ios"
            
            with open(package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)

        return Outputs(
            ok=True, 
            message=f"Expo app '{args.app_name}' scaffolded successfully",
            artifacts={
                "project_dir": proj_dir,
                "app_name": args.app_name,
                "bundle_id": args.bundle_identifier or f"com.example.{project_name.replace('-','')}",
                "scheme": args.scheme or project_name
            },
            data={
                "project_path": proj_dir,
                "bundle_identifier": args.bundle_identifier or f"com.example.{project_name.replace('-','')}",
                "deep_link_scheme": args.scheme or project_name,
                "created_files": ["app.json", "eas.json", "assets/icon.png", "assets/splash.png"]
            }
        )
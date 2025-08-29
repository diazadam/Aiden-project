"""
Image watermark skill - Add text watermarks to images
"""
import os
from PIL import Image, ImageDraw, ImageFont
from ...skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

class Inputs(SkillInputs):
    input_path: str
    text: str = "K. Rae Kreations"

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "image_watermark"
    version = "0.1.0"
    caps = {"fs_write"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        try:
            in_path = args.input_path
            if not os.path.exists(in_path):
                return Outputs(ok=False, message="Input file not found")
            
            # Open image and convert to RGBA for transparency support
            im = Image.open(in_path).convert("RGBA")
            draw = ImageDraw.Draw(im)
            W, H = im.size
            text = args.text
            
            # Calculate text position (bottom-right with padding)
            try:
                # Try to use default font
                font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
            except:
                # Fallback for older Pillow versions
                w, h = draw.textsize(text)
            
            x = W - w - 20
            y = H - h - 10
            
            # Add text with semi-transparent background
            draw.text((x, y), text, fill=(255, 255, 255, 180))
            
            # Save to tenant workdir
            out_filename = f"wm_{os.path.basename(in_path)}"
            out_path = os.path.join(ctx.workdir, out_filename)
            im.save(out_path)
            
            return Outputs(
                ok=True, 
                artifacts={"output_path": out_path}, 
                message=f"Watermarked image saved to {out_path}",
                data={"output_file": out_filename}
            )
        except Exception as e:
            return Outputs(ok=False, message=f"Watermark failed: {str(e)}")
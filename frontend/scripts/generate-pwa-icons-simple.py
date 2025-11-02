#!/usr/bin/env python3
"""
Generate PWA icons using Pillow (no SVG dependencies).
Requires: pip install pillow
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"Error: {e}")
    print("Install dependencies: pip install pillow")
    sys.exit(1)

def create_icon(size: int, output_path: Path):
    """Create a simple PWA icon."""
    # Create image with sky blue background
    img = Image.new('RGB', (size, size), color='#0ea5e9')
    draw = ImageDraw.Draw(img)
    
    # Draw mosquito-inspired abstract shapes
    center_x, center_y = size // 2, size // 2
    
    # Body (ellipses)
    head_radius = int(size * 0.08)
    body_radius = int(size * 0.1)
    
    # Head
    draw.ellipse(
        [center_x - head_radius, center_y - int(size*0.15) - head_radius,
         center_x + head_radius, center_y - int(size*0.15) + head_radius],
        fill='white'
    )
    
    # Body
    draw.ellipse(
        [center_x - body_radius, center_y - body_radius,
         center_x + body_radius, center_y + body_radius + int(size*0.05)],
        fill='white'
    )
    
    # Wings (arcs)
    wing_width = int(size * 0.15)
    wing_height = int(size * 0.08)
    
    # Left wing
    draw.ellipse(
        [center_x - wing_width - body_radius, center_y - wing_height,
         center_x - body_radius, center_y + wing_height],
        fill='white', outline='white'
    )
    
    # Right wing
    draw.ellipse(
        [center_x + body_radius, center_y - wing_height,
         center_x + wing_width + body_radius, center_y + wing_height],
        fill='white', outline='white'
    )
    
    # Legs (lines)
    leg_length = int(size * 0.12)
    leg_width = max(2, size // 100)
    
    # Left legs
    draw.line([center_x - body_radius//2, center_y + body_radius,
               center_x - body_radius - leg_length//2, center_y + body_radius + leg_length],
              fill='white', width=leg_width)
    
    # Right legs
    draw.line([center_x + body_radius//2, center_y + body_radius,
               center_x + body_radius + leg_length//2, center_y + body_radius + leg_length],
              fill='white', width=leg_width)
    
    # Add text at bottom
    try:
        # Try to use a system font
        font_size = max(24, size // 12)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = None
    
    text = "TechDengue"
    
    # Get text bounding box
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * (size // 20)
        text_height = size // 15
    
    text_x = (size - text_width) // 2
    text_y = size - text_height - int(size * 0.08)
    
    draw.text((text_x, text_y), text, fill='white', font=font)
    
    # Save
    img.save(output_path, 'PNG')
    print(f"✓ Generated {output_path.name} ({size}x{size})")

def main():
    # Paths
    script_dir = Path(__file__).parent
    public_dir = script_dir.parent / 'public'
    
    # Generate icons
    sizes = [
        (192, 'pwa-192x192.png'),
        (512, 'pwa-512x512.png'),
    ]
    
    for size, filename in sizes:
        output_path = public_dir / filename
        create_icon(size, output_path)
    
    print("\n✓ All PWA icons generated successfully!")

if __name__ == '__main__':
    main()

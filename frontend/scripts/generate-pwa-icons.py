#!/usr/bin/env python3
"""
Generate PWA icons from SVG source.
Requires: pip install cairosvg pillow
"""
import sys
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    import io
except ImportError as e:
    print(f"Error: {e}")
    print("Install dependencies: pip install cairosvg pillow")
    sys.exit(1)

def generate_png_from_svg(svg_path: Path, output_path: Path, size: int):
    """Convert SVG to PNG at specified size."""
    png_data = cairosvg.svg2png(
        url=str(svg_path),
        output_width=size,
        output_height=size
    )
    
    # Save PNG
    with open(output_path, 'wb') as f:
        f.write(png_data)
    
    print(f"✓ Generated {output_path.name} ({size}x{size})")

def main():
    # Paths
    script_dir = Path(__file__).parent
    public_dir = script_dir.parent / 'public'
    svg_path = public_dir / 'pwa-icon.svg'
    
    if not svg_path.exists():
        print(f"Error: SVG not found at {svg_path}")
        sys.exit(1)
    
    # Generate icons
    sizes = [
        (192, 'pwa-192x192.png'),
        (512, 'pwa-512x512.png'),
    ]
    
    for size, filename in sizes:
        output_path = public_dir / filename
        generate_png_from_svg(svg_path, output_path, size)
    
    print("\n✓ All PWA icons generated successfully!")

if __name__ == '__main__':
    main()

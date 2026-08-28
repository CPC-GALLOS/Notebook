# Dependencies:
#   - Python (pip): Pillow          -> pip install Pillow
#   - System (Linux CLI): pdftoppm  -> sudo apt install poppler-utils
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageFilter, ImageDraw
except ImportError:
    sys.exit("Missing dependency: Pillow. Install it with: pip install Pillow")

if shutil.which("pdftoppm") is None:
    sys.exit(
        "Missing dependency: pdftoppm. Install it with: sudo apt install poppler-utils"
    )

def extract_page(pdf_path: str, page_num: int, output_prefix: str, dpi: int = 150) -> str:
    """Extract a specific page from PDF as PNG using pdftoppm."""
    cmd = [
        "pdftoppm",
        "-png",
        "-r", str(dpi),
        "-f", str(page_num),
        "-l", str(page_num),
        pdf_path,
        output_prefix
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    parent = Path(output_prefix).parent
    prefix_name = Path(output_prefix).name
    matches = sorted(parent.glob(f"{prefix_name}*.png"))
    if not matches:
        raise FileNotFoundError(f"pdftoppm did not produce a PNG for page {page_num}")
    return str(matches[0])

PDF_FILENAME = "Notebook-TRD.pdf"
DEFAULT_PAGES = (1, 6, 8)

def create_preview(pages_to_extract=DEFAULT_PAGES):
    workspace_root = Path(__file__).resolve().parent
    if not (workspace_root / PDF_FILENAME).exists() and (workspace_root.parent / PDF_FILENAME).exists():
        workspace_root = workspace_root.parent
    pdf_path = workspace_root / PDF_FILENAME
    output_path = workspace_root / "src" / "preview.png"

    if not pdf_path.exists():
        print(f"PDF not found at {pdf_path}. Attempting to build with npm run build...")
        subprocess.run(["npm", "run", "build"], cwd=workspace_root, check=True)

    # Dimensions
    canvas_width = 1610
    canvas_height = 700
    page_width = 490
    page_height = 634

    # Page positions (X coordinates)
    x_positions = [40, 560, 1080]
    # Y position (vertically centered)
    y_position = (canvas_height - page_height) // 2

    canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))

    with tempfile.TemporaryDirectory() as tmpdir:
        pages = []
        for page_num in pages_to_extract:
            prefix = os.path.join(tmpdir, f"page_{page_num}")
            img_path = extract_page(str(pdf_path), page_num, prefix, dpi=150)
            img = Image.open(img_path).convert("RGBA")
            resized = img.resize((page_width, page_height), Image.Resampling.LANCZOS)
            pages.append(resized)

        # Shadow configuration
        blur_radius = 24
        shadow_width = page_width + 2 * blur_radius
        shadow_height = page_height + 2 * blur_radius

        shadow_mask = Image.new("RGBA", (shadow_width, shadow_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow_mask)
        draw.rectangle(
            [blur_radius, blur_radius, blur_radius + page_width, blur_radius + page_height],
            fill=(0, 0, 0, 36)
        )
        shadow_blurred = shadow_mask.filter(ImageFilter.GaussianBlur(blur_radius))

        # Paste shadows
        for x in x_positions:
            shadow_x = x - blur_radius
            shadow_y = y_position - blur_radius + 2
            canvas.paste(shadow_blurred, (shadow_x, shadow_y), shadow_blurred)

        # Paste pages with subtle border
        for i, x in enumerate(x_positions):
            page = pages[i].copy()
            draw_page = ImageDraw.Draw(page)
            draw_page.rectangle([0, 0, page_width - 1, page_height - 1], outline=(210, 210, 210, 255))
            canvas.paste(page, (x, y_position), page)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(str(output_path), "PNG")
        print(f"Successfully generated {output_path} (Pages {list(pages_to_extract)})!")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        pages = [int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])]
        create_preview(pages)
    elif len(sys.argv) == 1:
        create_preview([1, 6, 8])
    else:
        print("Usage: python3 generate_preview.py [pageA pageB pageC]")
        print("Example: python3 generate_preview.py 1 6 8")
        sys.exit(1)

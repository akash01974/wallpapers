import os
from pathlib import Path

# Configuration
WALLPAPER_DIR = "."
README_FILE = "README.md"
IMAGES_PER_ROW = 3
THUMBNAIL_WIDTH = "280px"

def generate_markdown(images):
    """Generates Markdown for a responsive grid of clickable images."""
    rows = []
    current_row = []
    
    for i, img in enumerate(images, start=1):
        # Create a clickable thumbnail linking to the actual file
        img_html = (
            f"<a href='{img}'>"
            f"<img src='{img}' alt='{img}' width='{THUMBNAIL_WIDTH}' "
            f"style='border-radius: 8px; margin: 5px; border: 1px solid #333;'></a>"
        )
        current_row.append(img_html)
        
        if i % IMAGES_PER_ROW == 0:
            rows.append("<div align='center'>\n" + "\n".join(current_row) + "\n</div>")
            current_row = []
            
    # Add any remaining images in the last row
    if current_row:
        rows.append("<div align='center'>\n" + "\n".join(current_row) + "\n</div>")
        
    return "\n".join(rows)

def main():
    # Get all images, excluding hidden files and sorted alphabetically
    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp")
    images = sorted([
        f.name for f in Path(WALLPAPER_DIR).iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions and not f.name.startswith(".")
    ])

    if not images:
        print("❌ No wallpapers found in the current directory.")
        return

    print(f"🖼️  Found {len(images)} wallpapers. Generating README...")

    markdown_grid = generate_markdown(images)

    readme_content = [
        "# 🌌 Wallpapers Collection",
        f"\nTotal Wallpapers: **{len(images)}**\n",
        "Click on any image to view it in full resolution.\n",
        "---",
        markdown_grid,
        "\n---",
        "\n*Generated automatically by `generate_readme.py`*"
    ]

    with open(README_FILE, "w", encoding="utf-8") as readme:
        readme.write("\n".join(readme_content))

    print(f"✅ Successfully updated {README_FILE}!")

if __name__ == "__main__":
    main()

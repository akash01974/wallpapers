#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from pathlib import Path

# --- Configuration ---
WALLPAPER_DIR = "."
README_FILE = "README.md"
IMAGES_PER_ROW = 3
THUMBNAIL_WIDTH = "280px"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")

class WallpaperUpdateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Repo Updater")
        self.root.geometry("600x520")
        self.root.configure(bg="#1e1e1e")

        # Set the working directory to the script's location
        self.repo_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.repo_dir)

        self.setup_ui()

    def setup_ui(self):
        header = tk.Label(
            self.root, text="🌌 Wallpaper Repository Manager", 
            font=("Arial", 16, "bold"), fg="#ffffff", bg="#1e1e1e", pady=10
        )
        header.pack()

        self.stats_label = tk.Label(
            self.root, text="Click 'Start Update' to refresh the gallery.", 
            font=("Arial", 10), fg="#aaaaaa", bg="#1e1e1e"
        )
        self.stats_label.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(
            self.root, width=70, height=15, 
            bg="#252526", fg="#d4d4d4", font=("Consolas", 10),
            padx=10, pady=10
        )
        self.log_area.pack(padx=20, pady=10)
        self.log_area.insert(tk.END, "Ready to update...\n")
        self.log_area.configure(state='disabled')

        self.run_btn = tk.Button(
            self.root, text="🚀 Start Update", 
            command=self.run_update,
            font=("Arial", 11, "bold"), bg="#007acc", fg="white",
            activebackground="#005a9e", activeforeground="white",
            padx=20, pady=10, border=0
        )
        self.run_btn.pack(pady=15)

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update_idletasks()

    def generate_readme_content(self, images):
        """Logic originally from auto_readme.py"""
        rows = []
        current_row = []
        for i, img in enumerate(images, start=1):
            img_html = (
                f"<a href='{img}'>"
                f"<img src='{img}' alt='{img}' width='{THUMBNAIL_WIDTH}' "
                f"style='border-radius: 8px; margin: 5px; border: 1px solid #333;'></a>"
            )
            current_row.append(img_html)
            if i % IMAGES_PER_ROW == 0:
                rows.append("<div align='center'>\n" + "\n".join(current_row) + "\n</div>")
                current_row = []
        if current_row:
            rows.append("<div align='center'>\n" + "\n".join(current_row) + "\n</div>")
        
        markdown_grid = "\n".join(rows)
        
        return [
            "# 🌌 Wallpapers Collection",
            "\nA bunch of wallpapers I’ve made + collected from around the internet. If you recognize your work and would like credit or removal, feel free to reach out. Anyone is welcome to use these wallpapers for personal use.\n",
            f"Total Wallpapers: **{len(images)}**\n",
            "Click on any image to view it in full resolution.\n",
            "---",
            markdown_grid,
            "\n---",
            f"\n*Generated automatically by `update_repo_gui.py`*"
        ]

    def run_update(self):
        self.run_btn.config(state='disabled', text="Processing...", bg="#555555")
        self.log("--- Starting Update Process ---")

        try:
            # 1. Get images and count new ones
            images = sorted([
                f.name for f in Path(WALLPAPER_DIR).iterdir()
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith(".")
            ])
            
            git_status = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8")
            new_count = len([l for l in git_status.split("\n") if l.startswith("??") and any(l.lower().endswith(e) for e in IMAGE_EXTENSIONS)])
            
            self.log(f"Found {len(images)} total wallpapers ({new_count} new).")
            self.stats_label.config(text=f"Total: {len(images)} | New: {new_count}", fg="#4ec9b0")

            # 2. Generate README
            self.log("Refreshing README gallery...")
            readme_content = self.generate_readme_content(images)
            with open(README_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(readme_content))
            self.log("README updated successfully.")

            # 3. Check for any changes to commit
            status = subprocess.check_output(["git", "status", "-s"]).decode("utf-8")
            if not status.strip():
                self.log("No changes detected. Repository is clean.")
                messagebox.showinfo("Done", "No new changes to commit.")
            else:
                # 4. Stage and Commit
                self.log("Staging changes...")
                subprocess.check_call(["git", "add", "."])
                
                commit_msg = f"Auto-update: Added {new_count} new wallpapers on {datetime.now().strftime('%Y-%m-%d')}"
                self.log(f"Committing changes: '{commit_msg}'")
                subprocess.check_call(["git", "commit", "-m", commit_msg])
                
                self.log("✅ Changes committed locally!")
                self.log("⚠️  PUSH SKIPPED: You can push manually when ready.")
                messagebox.showinfo("Success", f"Updated and committed {new_count} new wallpapers locally!")

        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.run_btn.config(state='normal', text="🚀 Start Update", bg="#007acc")
            self.log("--- Finished ---")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperUpdateGUI(root)
    root.mainloop()

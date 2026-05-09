#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
from pathlib import Path

# --- Configuration ---
WALLPAPER_DIR = "."
README_FILE = "README.md"
IMAGES_PER_ROW = 3
THUMBNAIL_WIDTH = "280px"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")

# --- UI Constants ---
BG_COLOR = "#0a0a0c"      # Deepest black/blue
SURFACE_COLOR = "#16161a" # Card/Surface color
ACCENT_COLOR = "#6366f1"  # Modern Indigo
ACCENT_HOVER = "#818cf8"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
SHELL_BG = "#000000"
SUCCESS_COLOR = "#22c55e"
ERROR_COLOR = "#ef4444"

class CustomModal(tk.Toplevel):
    def __init__(self, parent, title, message, is_error=False):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x220")
        self.configure(bg=SURFACE_COLOR)
        self.resizable(False, False)
        self.transient(parent)
        
        # Ensure the window is shown before grabbing focus
        self.withdraw()  # Hide while building
        
        # Center the modal
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 110
        self.geometry(f"+{x}+{y}")

        color = ERROR_COLOR if is_error else SUCCESS_COLOR
        
        tk.Label(self, text="●", font=("Arial", 24), fg=color, bg=SURFACE_COLOR).pack(pady=(20, 0))
        tk.Label(self, text=title.upper(), font=("Segoe UI", 12, "bold"), fg=TEXT_PRIMARY, bg=SURFACE_COLOR).pack(pady=5)
        
        msg_label = tk.Label(self, text=message, font=("Segoe UI", 10), fg=TEXT_SECONDARY, 
                             bg=SURFACE_COLOR, wraplength=350, justify="center")
        msg_label.pack(pady=10, padx=20)
        
        btn = tk.Button(self, text="CLOSE", command=self.destroy, font=("Segoe UI", 9, "bold"), 
                        bg="#2d2d35", fg=TEXT_PRIMARY, activebackground="#3d3d45", 
                        activeforeground="white", border=0, padx=30, pady=8, cursor="hand2")
        btn.pack(pady=(10, 20))

        self.deiconify() # Show it
        self.wait_visibility() # Wait until it's on screen
        self.grab_set() # Now grab focus safely

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=45, radius=22, color=ACCENT_COLOR):
        super().__init__(parent, width=width, height=height, bg=BG_COLOR, highlightthickness=0)
        self.command = command
        self.color = color
        self.radius = radius
        self.text = text
        
        self.rect = self.create_rounded_rect(0, 0, width, height, radius, fill=color)
        self.label = self.create_text(width/2, height/2, text=text, fill="white", font=("Segoe UI", 10, "bold"))
        
        self.tag_bind(self.rect, "<Button-1>", lambda e: self.on_click())
        self.tag_bind(self.label, "<Button-1>", lambda e: self.on_click())
        self.tag_bind(self.rect, "<Enter>", lambda e: self.on_hover(True))
        self.tag_bind(self.rect, "<Leave>", lambda e: self.on_hover(False))

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_hover(self, hovering):
        color = ACCENT_HOVER if hovering else self.color
        self.itemconfig(self.rect, fill=color)

    def on_click(self):
        self.itemconfig(self.rect, fill="#4f46e5")
        self.after(100, lambda: self.itemconfig(self.rect, fill=self.color))
        self.command()

class WallpaperUpdateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Manager Pro")
        self.root.geometry("750x680")
        self.root.configure(bg=BG_COLOR)
        
        # Working directory setup
        self.repo_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.repo_dir)

        self.setup_ui()

    def setup_ui(self):
        # 1. Navbar-style Header (Top)
        nav = tk.Frame(self.root, bg=SURFACE_COLOR, height=60)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)
        
        tk.Label(nav, text="REPOSITORY SHELL", font=("Consolas", 10, "bold"), fg=ACCENT_COLOR, bg=SURFACE_COLOR).pack(side="left", padx=25)
        self.time_label = tk.Label(nav, font=("Consolas", 9), fg=TEXT_SECONDARY, bg=SURFACE_COLOR)
        self.time_label.pack(side="right", padx=25)
        self.update_time()

        # 2. Footer Actions (Bottom - Pack first to pin it)
        footer = tk.Frame(self.root, bg=BG_COLOR, pady=30)
        footer.pack(fill="x", side="bottom")
        
        self.run_btn = RoundedButton(footer, text="SYNC REPOSITORY", command=self.run_update)
        self.run_btn.pack()

        # 3. Main Content (Fill remaining space)
        content = tk.Frame(self.root, bg=BG_COLOR, padx=40, pady=20)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="System Status", font=("Segoe UI", 16, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR).pack(anchor="w")
        self.stats_label = tk.Label(content, text="Sync required for new assets", font=("Segoe UI", 10), fg=TEXT_SECONDARY, bg=BG_COLOR)
        self.stats_label.pack(anchor="w", pady=(5, 15))

        # Shell Interface
        shell_frame = tk.Frame(content, bg="#1e1e26", padx=1, pady=1)
        shell_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.log_area = scrolledtext.ScrolledText(
            shell_frame, bg=SHELL_BG, fg="#a1a1aa", font=("Consolas", 10),
            padx=20, pady=20, borderwidth=0, highlightthickness=0,
            insertbackground=ACCENT_COLOR
        )
        self.log_area.pack(fill="both", expand=True)
        self.log_area.tag_configure("prompt", foreground=ACCENT_COLOR)
        self.log_area.tag_configure("success", foreground=SUCCESS_COLOR)
        self.log_area.tag_configure("error", foreground=ERROR_COLOR)
        self.log("System initialized and ready.", "prompt")
        self.log_area.configure(state='disabled')

    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_time)

    def log(self, message, tag=None):
        self.log_area.configure(state='normal')
        if tag == "prompt":
            self.log_area.insert(tk.END, "> ", "prompt")
        elif tag == "success":
            self.log_area.insert(tk.END, "✓ ", "success")
        elif tag == "error":
            self.log_area.insert(tk.END, "× ", "error")
        else:
            self.log_area.insert(tk.END, "  ")
            
        self.log_area.insert(tk.END, f"{message}\n", tag)
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update_idletasks()

    def generate_readme_content(self, images):
        rows = []
        current_row = []
        for i, img in enumerate(images, start=1):
            img_html = f"<a href='{img}'><img src='{img}' alt='{img}' width='{THUMBNAIL_WIDTH}' style='border-radius: 8px; margin: 5px; border: 1px solid #333;'></a>"
            current_row.append(img_html)
            if i % IMAGES_PER_ROW == 0:
                rows.append("<div align='center'>\n" + "\n".join(current_row) + "\n</div>")
                current_row = []
        if current_row:
            rows.append("<div align='center'>\n" + "\n".join(current_row) + "\n</div>")
        
        return [
            "# 🌌 Wallpapers Collection",
            f"\nA bunch of wallpapers I’ve made + collected from around the internet.\n\nTotal Wallpapers: **{len(images)}**\n",
            "\n".join(rows),
            f"\n*Generated automatically by `repo-update.py`*"
        ]

    def run_update(self):
        self.log("Initializing synchronization protocol...", "prompt")

        try:
            images = sorted([f.name for f in Path(WALLPAPER_DIR).iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith(".")])
            git_status = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8")
            new_count = len([l for l in git_status.split("\n") if l.startswith("??") and any(l.lower().endswith(e) for e in IMAGE_EXTENSIONS)])
            
            self.log(f"Found {len(images)} total assets.")
            self.log(f"New wallpapers detected: {new_count}")
            self.stats_label.config(text=f"{len(images)} Assets Indexed • {new_count} Unstaged", fg=SUCCESS_COLOR)

            self.log("Regenerating Markdown gallery...")
            content = self.generate_readme_content(images)
            with open(README_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(content))
            
            status = subprocess.check_output(["git", "status", "-s"]).decode("utf-8")
            if not status.strip():
                self.log("Local repository is already up to date.", "success")
                CustomModal(self.root, "No Changes", "Your repository is already in sync.")
            else:
                self.log("Staging assets to local index...")
                subprocess.check_call(["git", "add", "."])
                msg = "Add wallpapers collection"
                self.log(f"Executing commit: {msg}")
                subprocess.check_call(["git", "commit", "-m", msg])
                
                self.log("Successfully committed changes to local branch.", "success")
                CustomModal(self.root, "Update Complete", f"Successfully indexed {new_count} new wallpapers locally.")

        except Exception as e:
            self.log(f"Critical Error: {e}", "error")
            CustomModal(self.root, "System Error", str(e), is_error=True)
        finally:
            self.log("Protocol finished.", "prompt")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperUpdateGUI(root)
    root.mainloop()

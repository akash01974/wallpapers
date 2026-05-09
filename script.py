#!/usr/bin/env python3
import os
import subprocess
import math
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
from pathlib import Path
import threading

# --- Configuration ---
WALLPAPER_DIR = "."
README_FILE = "README.md"
IMAGES_PER_ROW = 3
THUMBNAIL_WIDTH = "280px"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")

# --- UI Constants ---
BG_COLOR = "#0d1117"
SURFACE_COLOR = "#161b22"
BORDER_COLOR = "#30363d"
ACCENT_COLOR = "#238636"
ACCENT_HOVER = "#2ea043"
TEXT_PRIMARY = "#c9d1d9"
TEXT_SECONDARY = "#8b949e"
SHELL_BG = "#010409"
SUCCESS_COLOR = "#3fb950"
ERROR_COLOR = "#f85149"

class CustomModal(tk.Toplevel):
    def __init__(self, parent, title, message, is_error=False):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x180") # Made slightly smaller since dot is gone
        self.configure(bg=SURFACE_COLOR)
        self.resizable(False, False)
        self.transient(parent)
        
        # Ensure the window is shown before grabbing focus
        self.withdraw()
        
        # Center the modal
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 90
        self.geometry(f"+{x}+{y}")

        color = ERROR_COLOR if is_error else ACCENT_COLOR
        
        # Header without the dot
        tk.Label(self, text=title.upper(), font=("Segoe UI", 11, "bold"), 
                 fg=color, bg=SURFACE_COLOR).pack(pady=(25, 5))
        
        msg_label = tk.Label(self, text=message, font=("Segoe UI", 10), fg=TEXT_PRIMARY, 
                             bg=SURFACE_COLOR, wraplength=350, justify="center")
        msg_label.pack(pady=10, padx=20)
        
        btn = RoundedButton(self, text="DONE", command=self.destroy, width=120, height=35, radius=17, color="#21262d")
        btn.pack(pady=(10, 20))

        self.deiconify()
        self.wait_visibility()
        self.grab_set()

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=45, radius=22, color=ACCENT_COLOR):
        super().__init__(parent, width=width, height=height, bg=BG_COLOR, highlightthickness=0)
        self.command = command
        self.color = color
        self.radius = radius
        self.text = text
        self.is_loading = False
        self._anim_id = None
        self._dot_count = 0
        
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
        if self.is_loading: return
        color = ACCENT_HOVER if hovering else self.color
        self.itemconfig(self.rect, fill=color)

    def set_loading(self, loading):
        self.is_loading = loading
        if loading:
            self.itemconfig(self.label, state='hidden')
            self.itemconfig(self.rect, fill=SURFACE_COLOR)
            self._create_dots()
            self._animate_loading_dots(0)
        else:
            if self._anim_id:
                self.after_cancel(self._anim_id)
                self._anim_id = None
            self._remove_dots()
            self.itemconfig(self.label, state='normal')
            self.itemconfig(self.rect, fill=self.color)

    def _create_dots(self):
        self._dots = []
        w = self.winfo_width()
        h = self.winfo_height()
        for i in range(3):
            x = (w / 2) + (i - 1) * 15
            dot = self.create_oval(x-3, h/2-3, x+3, h/2+3, fill=TEXT_SECONDARY, outline="")
            self._dots.append(dot)

    def _remove_dots(self):
        if hasattr(self, '_dots'):
            for dot in self._dots:
                self.delete(dot)
            self._dots = []

    def _animate_loading_dots(self, step):
        if not self.is_loading: return
        h = self.winfo_height()
        w = self.winfo_width()
        for i, dot in enumerate(self._dots):
            # Sine wave for vertical bounce
            y_offset = math.sin(step + i * 1.2) * 6
            x = (w / 2) + (i - 1) * 15
            self.coords(dot, x-3, h/2-3 + y_offset, x+3, h/2+3 + y_offset)
            
            # Pulse color/opacity
            opacity = int(127 + 128 * math.sin(step + i * 1.2))
            color = f'#{opacity:02x}{opacity:02x}{opacity:02x}'
            # self.itemconfig(dot, fill=color) # Tkinter colors are tricky, let's just stick to movement for now or use fixed shades

        self._anim_id = self.after(30, self._animate_loading_dots, step + 0.3)

    def on_click(self):
        if self.is_loading: return
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
        shell_frame = tk.Frame(content, bg=BORDER_COLOR, padx=1, pady=1)
        shell_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.log_area = scrolledtext.ScrolledText(
            shell_frame, bg=SHELL_BG, fg=TEXT_SECONDARY, font=("Consolas", 10),
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
        self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
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
            f"\n*Generated automatically by `script.py`*"
        ]

    def safe_log(self, message, tag=None):
        self.root.after(0, self.log, message, tag)

    def safe_modal(self, title, message, is_error=False):
        self.root.after(0, lambda: CustomModal(self.root, title, message, is_error))

    def run_update(self):
        def sync_thread():
            try:
                # 1. Get images and git status
                images = sorted([f.name for f in Path(WALLPAPER_DIR).iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith(".")])
                
                git_status = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8").splitlines()
                
                added = len([l for l in git_status if l.startswith("??") and any(l.lower().endswith(e) for e in IMAGE_EXTENSIONS)])
                removed = len([l for l in git_status if l.startswith(" D") and any(l.lower().endswith(e) for e in IMAGE_EXTENSIONS)])
                
                self.safe_log(f"Found {len(images)} total assets.")
                self.root.after(0, lambda: self.stats_label.config(text=f"{len(images)} Assets Indexed • +{added} / -{removed}", fg=SUCCESS_COLOR))

                # 2. Generate README
                self.safe_log("Regenerating Markdown gallery...")
                content = self.generate_readme_content(images)
                with open(README_FILE, "w", encoding="utf-8") as f:
                    f.write("\n".join(content))
                
                # 3. Check for any changes to commit
                status = subprocess.check_output(["git", "status", "-s"]).decode("utf-8")
                if not status.strip():
                    self.safe_log("Local repository is already up to date.", "success")
                    self.safe_modal("All Caught Up", "Everything is perfect! Your collection is already up to date.")
                else:
                    # 4. Stage and Commit
                    self.safe_log(f"Syncing changes: +{added} added, -{removed} removed...")
                    subprocess.check_call(["git", "add", "."])
                    
                    # Simplified commit message
                    if added > 0 and removed > 0:
                        msg = f"Update wallpapers: +{added} / -{removed}"
                    elif added > 0:
                        msg = f"Add {added} wallpapers"
                    elif removed > 0:
                        msg = f"Remove {removed} wallpapers"
                    else:
                        msg = "Sync repository"
                        
                    subprocess.check_call(["git", "commit", "-m", msg])
                    self.safe_log("Successfully committed changes.", "success")
                    
                    # 5. Push to Remote
                    self.safe_log("Pushing changes to GitHub...", "prompt")
                    subprocess.check_call(["git", "push"])
                    self.safe_log("Successfully pushed to remote repository.", "success")
                    
                    # Determine the final message
                    if added > 0 and removed > 0:
                        final_msg = f"Collection updated! Added {added} and removed {removed} wallpapers."
                    elif added > 0:
                        final_msg = f"Sweet! Added {added} new wallpapers to your collection."
                    elif removed > 0:
                        final_msg = f"Cleanup complete! Removed {removed} wallpapers from the gallery."
                    else:
                        final_msg = "Gallery refreshed and repository updated successfully."
                    
                    self.safe_modal("Update Complete", final_msg)

            except Exception as e:
                self.safe_log(f"Critical Error: {e}", "error")
                self.safe_modal("System Error", str(e), is_error=True)
            finally:
                self.safe_log("Protocol finished.", "prompt")
                self.root.after(0, lambda: self.run_btn.set_loading(False))

        self.run_btn.set_loading(True)
        self.log("Initializing synchronization protocol...", "prompt")
        threading.Thread(target=sync_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperUpdateGUI(root)
    root.mainloop()

#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from pathlib import Path

class WallpaperUpdateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Repo Updater")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e1e")

        # Set the working directory to the script's location
        self.repo_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.repo_dir)

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Label(
            self.root, text="🌌 Wallpaper Repository Manager", 
            font=("Arial", 16, "bold"), fg="#ffffff", bg="#1e1e1e", pady=10
        )
        header.pack()

        # Stats Label
        self.stats_label = tk.Label(
            self.root, text="Click 'Start Update' to scan for new wallpapers.", 
            font=("Arial", 10), fg="#aaaaaa", bg="#1e1e1e"
        )
        self.stats_label.pack(pady=5)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(
            self.root, width=70, height=15, 
            bg="#252526", fg="#d4d4d4", font=("Consolas", 10),
            padx=10, pady=10
        )
        self.log_area.pack(padx=20, pady=10)
        self.log_area.insert(tk.END, "Ready to update...\n")
        self.log_area.configure(state='disabled')

        # Run Button
        self.run_btn = tk.Button(
            self.root, text="🚀 Start Update", 
            command=self.run_update,
            font=("Arial", 11, "bold"), bg="#007acc", fg="white",
            activebackground="#005a9e", activeforeground="white",
            padx=20, pady=10, border=0
        )
        self.run_btn.pack(pady=20)

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update_idletasks()

    def count_new_wallpapers(self):
        try:
            # Check for untracked image files
            cmd = ["git", "status", "--porcelain"]
            result = subprocess.check_output(cmd).decode("utf-8")
            image_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp")
            
            new_images = [
                line for line in result.split("\n") 
                if line.startswith("??") and any(line.lower().endswith(ext) for ext in image_exts)
            ]
            return len(new_images)
        except Exception as e:
            self.log(f"Error counting wallpapers: {e}")
            return 0

    def run_update(self):
        self.run_btn.config(state='disabled', text="Processing...", bg="#555555")
        self.log("--- Starting Update Process ---")

        try:
            # 1. Count new items
            new_count = self.count_new_wallpapers()
            self.log(f"Detected {new_count} new wallpapers.")
            self.stats_label.config(text=f"Detected {new_count} new wallpapers.", fg="#4ec9b0")

            # 2. Run the README generator
            self.log("Refreshing README gallery...")
            subprocess.check_call(["python3", "auto_readme.py"])
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

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error during update: {e}")
            messagebox.showerror("Error", "An error occurred during the update process.")
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.run_btn.config(state='normal', text="🚀 Start Update", bg="#007acc")
            self.log("--- Finished ---")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperUpdateGUI(root)
    root.mainloop()

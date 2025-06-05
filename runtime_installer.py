import subprocess
import sys
import importlib
import tkinter as tk
from Util import *

REQUIREMENTS_FILE = "requirements.txt"

class InstallerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Installing dependencies...")
        self.label = tk.Label(self.root, text="Initializing...", width=50)
        self.label.pack(padx=20, pady=20)
        self.root.update()

    def update_status(self, message):
        self.label.config(text=message)
        self.root.update()

    def close(self):
        self.root.destroy()


def parse_requirements(path):
    path = get_resource_path(path)
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                yield line


def install(package_spec, ui: InstallerUI):
    pkg_name = package_spec.split("==")[0].strip().split("[", 1)[0]  # strip extras
    try:
        importlib.import_module(pkg_name)
        ui.update_status(f"✅ {pkg_name} already installed.")
    except ImportError:
        ui.update_status(f"📦 Installing {package_spec}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
        ui.update_status(f"✅ {pkg_name} installed successfully.")


def ensure_dependencies():
    ui = InstallerUI()
    try:
        for requirement in parse_requirements(REQUIREMENTS_FILE):
            install(requirement, ui)
    finally:
        ui.update_status("All dependencies installed.")
        ui.root.after(1000, ui.close)
        ui.root.mainloop()
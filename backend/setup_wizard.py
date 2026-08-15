"""
Initial Setup Wizard for AI Lora Model Manager.

Guides users through selecting model directories and basic settings on first install.
Can be run standalone: python backend/setup_wizard.py
"""

import os
import sys
import json
import subprocess

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
EXAMPLE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config-example.json')

PREFERRED_ORDER = [
    "port",
    "autoOpenBrowser",
    "theme",
    "defaultView",
    "defaultSort",
    "filterFoldersWithBaseModel",
    "safeModeDefault",
    "safeModeOnReload",
    "nsfwBlurOverlay",
    "modelsDirectory",
    "checkpointsDirectory",
    "defaultDownloadDirectory",
    "defaultSortingDirectory",
    "visibleColumns",
    "columnOrder",
    "gridCard",
    "filenameFormats",
    "modelTypeRoots",
    "scanSettings"
]


def load_current_config():
    """Load settings from config.json, or fallback to config-example.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    if os.path.exists(EXAMPLE_CONFIG_FILE):
        try:
            with open(EXAMPLE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    # Default fallback
    return {
        "port": 8080,
        "modelsDirectory": "",
        "checkpointsDirectory": "",
        "defaultDownloadDirectory": "",
        "defaultSortingDirectory": "",
        "theme": "dark",
        "defaultView": "grid",
        "defaultSort": "date-desc"
    }


def save_config(data):
    """Save settings to config.json preserving standard key order."""
    ordered_data = {}
    for key in PREFERRED_ORDER:
        if key in data:
            ordered_data[key] = data[key]
    for key in data:
        if key not in ordered_data:
            ordered_data[key] = data[key]

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(ordered_data, f, indent=2)


def open_folder_dialog(title="Select Folder"):
    """Open a native Windows directory picker dialog via tkinter subprocess."""
    try:
        script = (
            "import tkinter as tk\n"
            "from tkinter import filedialog\n"
            "root = tk.Tk()\n"
            "root.withdraw()\n"
            "root.attributes('-topmost', True)\n"
            f"path = filedialog.askdirectory(title='{title}')\n"
            "print(path)\n"
            "root.destroy()\n"
        )
        cmd = [sys.executable, '-c', script]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        path = result.stdout.strip()
        if path:
            return os.path.normpath(path)
    except Exception:
        pass
    return None


def prompt_directory(label, current_value="", is_optional=False):
    """Interactive prompt to select or type a directory path."""
    print(f"\n[{label}]")
    if current_value:
        print(f"Current setting: {current_value}")
    
    while True:
        print("  [1] Open Folder Browser Dialog")
        print("  [2] Type / Paste Folder Path Manually")
        if current_value:
            print("  [3] Keep Current Setting")
        else:
            print("  [3] Skip for Now (Configure Later in Web UI)")

        choice = input("Select an option (1/2/3) [Default: 1]: ").strip()
        if not choice:
            choice = "1"

        if choice == "1":
            print("Opening folder selection window...")
            selected = open_folder_dialog(f"Select {label}")
            if selected:
                print(f"Selected: {selected}")
                return selected
            else:
                print("No folder selected in dialog.")
                retry = input("Try again or type manually? (y/n) [y]: ").strip().lower()
                if retry in ('n', 'no'):
                    return current_value

        elif choice == "2":
            manual_path = input("Enter full folder path: ").strip().strip('"').strip("'")
            if not manual_path:
                if is_optional:
                    return ""
                print("Path cannot be empty. Try again or skip.")
                continue

            manual_path = os.path.normpath(manual_path)
            if not os.path.exists(manual_path):
                print(f"\nWarning: The path '{manual_path}' does not exist.")
                create = input("Do you want to create this directory? (y/n) [y]: ").strip().lower()
                if create not in ('n', 'no'):
                    try:
                        os.makedirs(manual_path, exist_ok=True)
                        print(f"Created directory: {manual_path}")
                        return manual_path
                    except Exception as e:
                        print(f"Failed to create directory: {e}")
                else:
                    use_anyway = input("Save this path anyway? (y/n) [y]: ").strip().lower()
                    if use_anyway not in ('n', 'no'):
                        return manual_path
            else:
                return manual_path

        elif choice == "3":
            return current_value

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def run_wizard():
    """Main setup wizard flow."""
    print("=" * 64)
    print("       AI LORA MODEL MANAGER - INITIAL SETUP WIZARD")
    print("=" * 64)
    print("Welcome! This wizard helps configure your model directories.")
    print("You can change any of these settings anytime in the Web UI.")
    print("-" * 64)

    config = load_current_config()

    # 1. LoRA Directory
    print("\n--- Step 1: LoRA Models Directory ---")
    print("This is the main folder where your LoRA .safetensors files are stored")
    print("(e.g. C:\\ComfyUI\\models\\loras or C:\\stable-diffusion-webui\\models\\Lora)")
    loras_dir = prompt_directory(
        "LoRA Models Directory",
        config.get("modelsDirectory", ""),
        is_optional=False
    )
    config["modelsDirectory"] = loras_dir

    # 2. Checkpoints Directory
    print("\n--- Step 2: Checkpoints Directory (Optional) ---")
    print("If you want to manage Checkpoint models too, specify that folder here")
    print("(e.g. C:\\ComfyUI\\models\\checkpoints or C:\\stable-diffusion-webui\\models\\Stable-diffusion)")
    checkpoints_dir = prompt_directory(
        "Checkpoints Directory",
        config.get("checkpointsDirectory", ""),
        is_optional=True
    )
    config["checkpointsDirectory"] = checkpoints_dir

    # 3. Port Configuration
    print("\n--- Step 3: Web Server Port ---")
    current_port = config.get("port", 8080)
    print(f"Default port is 8080 (currently configured: {current_port})")
    port_input = input(f"Enter server port [Press Enter for {current_port}]: ").strip()
    if port_input:
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                config["port"] = port
            else:
                print(f"Port out of range (1-65535). Keeping {current_port}.")
                config["port"] = current_port
        except ValueError:
            print(f"Invalid port number. Keeping {current_port}.")
            config["port"] = current_port
    else:
        config["port"] = current_port
    save_config(config)

    print("\n" + "=" * 64)
    print("                 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 64)
    print(f"  LoRA Directory:       {config.get('modelsDirectory') or '(Not configured yet)'}")
    print(f"  Checkpoint Directory: {config.get('checkpointsDirectory') or '(Not configured)'}")
    print(f"  Server URL:           http://localhost:{config.get('port', 8080)}")
    print("=" * 64)
    print("Configuration saved to backend/config.json\n")


if __name__ == '__main__':
    try:
        run_wizard()
    except KeyboardInterrupt:
        print("\n\nSetup wizard cancelled. Default configuration retained.")
        sys.exit(0)

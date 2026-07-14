"""
Settings API Routes
"""

from flask import Blueprint, request, jsonify
import json
import os

settings_bp = Blueprint('settings', __name__)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')


def _load_settings():
    """Load settings from config.json."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        default_settings = {
            "modelsDirectory": "",
            "checkpointsDirectory": "",
            "defaultDownloadDirectory": "",
            "defaultSortingDirectory": "",
            "theme": "dark",
            "defaultView": "grid",
            "defaultSort": "name-asc",
            "filterFoldersWithBaseModel": False,
            "hideNSFW": False,
            "visibleColumns": {
                "thumbnail": True,
                "filename": True,
                "civitaiName": True,
                "baseModel": True,
                "category": True,
                "path": True,
                "size": True,
                "date": True,
                "url": True,
                "nsfw": True,
                "positiveWords": True,
                "negativeWords": True,
                "authorsWords": True,
                "description": True
            }
        }
        _save_settings(default_settings)
        return default_settings
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {CONFIG_FILE}")
        return {"modelsDirectory": ""}


def _save_settings(data):
    """Save settings to config.json with strict ordering."""
    try:
        preferred_order = [
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
        
        ordered_data = {}
        for key in preferred_order:
            if key in data:
                ordered_data[key] = data[key]
                
        for key in data:
            if key not in ordered_data:
                ordered_data[key] = data[key]

        with open(CONFIG_FILE, 'w') as f:
            json.dump(ordered_data, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")


def get_path_for_location(location_type):
    """Get the directory path for the given location type."""
    settings = _load_settings()
    if location_type == 'checkpoints':
        return settings.get('checkpointsDirectory', '')
    return settings.get('modelsDirectory', '')


@settings_bp.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all settings."""
    settings = _load_settings()
    return jsonify(settings)


@settings_bp.route('/api/settings', methods=['PUT'])
def save_settings():
    """Save settings. Returns the saved settings."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    _save_settings(data)
    return jsonify({'status': 'success'})


@settings_bp.route('/api/settings/browse', methods=['POST'])
def browse_folder():
    """Open a native folder selection dialog and return the path."""
    import subprocess
    try:
        # Run tkinter in a subprocess to avoid blocking the main Flask thread
        script = (
            "import tkinter as tk\n"
            "from tkinter import filedialog\n"
            "root = tk.Tk()\n"
            "root.withdraw()\n"
            "root.attributes('-topmost', True)\n"
            "path = filedialog.askdirectory()\n"
            "print(path)\n"
            "root.destroy()\n"
        )
        cmd = ['python', '-c', script]
        result = subprocess.run(cmd, capture_output=True, text=True)
        path = result.stdout.strip()
        
        if path:
            # tkinter sometimes returns paths with forward slashes on Windows
            path = os.path.normpath(path)
            return jsonify({'status': 'success', 'path': path})
        else:
            return jsonify({'status': 'cancelled'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

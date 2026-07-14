"""
Lora Model Manager — Flask Application Entry Point

Replaces the legacy http.server-based manager.py with a proper Flask application.
Serves the Vue frontend in production and provides a REST API for all operations.
"""

import os
import sys
import json
import shutil
import webbrowser
import mimetypes
from flask import Flask, send_from_directory, send_file, Response
from flask_cors import CORS

from .database import init_db, sync_models
from .routes.settings import settings_bp, get_path_for_location, _load_settings
from .routes.models import models_bp
from .routes.files import files_bp
from .routes.civitai import civitai_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=None)

    # Enable CORS for Vue dev server (localhost:5173)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(settings_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(civitai_bp)

    # Initialize SQLite database
    init_db()

    # -----------------------------------------------------------
    # Static file serving
    # -----------------------------------------------------------

    # Path to the Vue production build
    frontend_dist = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'frontend', 'dist'
    )

    # Path to assets (favicon, placeholder, etc.)
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Serve application assets (favicon, placeholder images, Vue JS/CSS)."""
        # Try frontend/dist/assets first (for compiled Vue JS/CSS)
        dist_assets = os.path.join(frontend_dist, 'assets')
        if os.path.exists(os.path.join(dist_assets, filename)):
            return send_from_directory(dist_assets, filename)
            
        # Fallback to backend/assets (for legacy placeholders)
        return send_from_directory(assets_dir, filename)

    @app.route('/model-file/<path:filepath>')
    def serve_model_file(filepath):
        """
        Serve files from the models directories (preview images, etc.).
        The frontend constructs URLs like /model-file/relative/path/to/preview.png
        """
        settings = _load_settings()
        directories = [
            settings.get('modelsDirectory', ''),
            settings.get('checkpointsDirectory', '')
        ]

        for models_dir in directories:
            if not models_dir:
                continue

            file_path = os.path.join(models_dir, filepath)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Determine content type
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/octet-stream'

                return send_file(file_path, mimetype=content_type)

        return Response('File not found', status=404)

    # Serve Vue frontend (production mode)
    if os.path.exists(frontend_dist):
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_vue(path):
            """Serve the Vue SPA. Falls through to index.html for client-side routing."""
            # Don't intercept API routes
            if path.startswith('api/') or path.startswith('assets/') or path.startswith('model-file/'):
                return Response('Not found', status=404)

            # Try to serve the exact file first
            full_path = os.path.join(frontend_dist, path)
            if path and os.path.exists(full_path) and os.path.isfile(full_path):
                return send_from_directory(frontend_dist, path)

            # Fall back to index.html for SPA routing
            return send_from_directory(frontend_dist, 'index.html')

    return app


def main():
    """Run the Flask application."""
    port = int(os.environ.get('PORT', 8080))
    app = create_app()

    # Auto-sync models on startup
    settings = _load_settings()
    models_dir = settings.get('modelsDirectory', '')
    checkpoints_dir = settings.get('checkpointsDirectory', '')

    if models_dir and os.path.exists(models_dir):
        print(f"Syncing LoRA models from: {models_dir}")
        sync_models(models_dir, 'loras')

    if checkpoints_dir and os.path.exists(checkpoints_dir):
        print(f"Syncing checkpoints from: {checkpoints_dir}")
        sync_models(checkpoints_dir, 'checkpoints')

    print(f"\nLora Model Manager running at: http://localhost:{port}")
    print("Press Ctrl+C to stop.\n")

    # Open browser
    # webbrowser.open(f"http://localhost:{port}")

    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()

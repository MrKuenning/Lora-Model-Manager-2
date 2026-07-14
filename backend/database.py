"""
SQLite Database Layer for Lora Model Manager

This module provides the SQLite caching/indexing layer. JSON sidecar files
remain the source of truth — SQLite mirrors them for fast querying.

Sync strategy:
- On startup, walk the models directory and compare file mtime vs last_synced
- Only re-read JSON files that have changed (incremental sync)
- Full re-sync available via refresh
- Writes go to BOTH JSON file AND SQLite row
"""

import sqlite3
import os
import json
import time
from pathlib import Path
from .constants import MODEL_EXTENSIONS


DB_FILENAME = 'lora_manager.db'


def get_db_path():
    """Get the path to the SQLite database file (next to app.py)."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILENAME)


def get_connection():
    """Create a new database connection with row_factory for dict-like access."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent read performance
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database schema. Safe to call multiple times."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            location TEXT DEFAULT 'loras',
            folder TEXT,
            size INTEGER,
            date_modified REAL,
            base_model TEXT DEFAULT 'Unknown',
            sd_version TEXT DEFAULT 'Unknown',
            category TEXT,
            subcategory TEXT,
            activation_text TEXT,
            preferred_weight REAL,
            negative_text TEXT,
            nsfw TEXT DEFAULT 'false',
            high_low TEXT,
            description TEXT,
            example_prompt TEXT,
            example_prompt_2 TEXT,
            tags TEXT,
            civitai_name TEXT,
            civitai_url TEXT,
            creator TEXT,
            sha256 TEXT,
            model_version TEXT,
            preview_url TEXT,
            preview_images TEXT,
            json_data TEXT,
            civitai_data TEXT,
            associated_files TEXT,
            last_synced REAL
        );

        CREATE INDEX IF NOT EXISTS idx_models_base_model ON models(base_model);
        CREATE INDEX IF NOT EXISTS idx_models_category ON models(category);
        CREATE INDEX IF NOT EXISTS idx_models_location ON models(location);
        CREATE INDEX IF NOT EXISTS idx_models_nsfw ON models(nsfw);
        CREATE INDEX IF NOT EXISTS idx_models_sd_version ON models(sd_version);
        CREATE INDEX IF NOT EXISTS idx_models_folder ON models(folder);
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def _map_sd_version(base_model):
    """Map a base model name to its SD version shorthand."""
    if not base_model:
        return 'Unknown'

    mapping = {
        'SD 1.5': 'sd',
        'SDXL 1.0': 'xl',
        'Pony': 'xl',
        'Illustrious': 'xl',
        'Flux.1 D': 'flux',
        'Flux.1 S': 'flux',
        'Flux.2 Klein 9B': 'klein',
        'Flux.2 Klein 9B-Base': 'klein',
        'Flux.2 Klein 9B-base': 'klein',
        'Qwen': 'qwen',
        'ZImageTurbo': 'zit',
        'ZImageBase': 'zit',
        'Wan Video 2.2 I2V-A14B': 'wan',
        'Wan Video 2.2 T2V-A14B': 'wan',
        'Anima': 'anima',
        'Ernie': 'ernie',
        'Krea 2': 'krea',
    }
    return mapping.get(base_model, 'Unknown')


def _parse_model_from_filesystem(model_name, root, file, models_dir):
    """
    Parse a single model's data from the filesystem.
    Returns a dict compatible with the API response format.
    """
    preview_path = os.path.join(root, f"{model_name}.preview.png")
    json_path = os.path.join(root, f"{model_name}.json")
    civitai_path = os.path.join(root, f"{model_name}.civitai.info")

    # Preview images
    relative_preview_path = os.path.relpath(preview_path, models_dir).replace("\\", "/")
    preview_images = []
    if os.path.exists(preview_path):
        preview_images.append("/" + relative_preview_path)

    for i in range(2, 5):
        extra_preview_path = os.path.join(root, f"{model_name}.preview{i}.png")
        if os.path.exists(extra_preview_path):
            relative_extra = os.path.relpath(extra_preview_path, models_dir).replace("\\", "/")
            preview_images.append("/" + relative_extra)

    main_preview_url = preview_images[0] if preview_images else "/assets/placeholder.png"

    # Base model
    base_model = "Unknown"
    json_data = {}
    civitai_data = {}

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding='utf-8-sig') as f:
                json_data = json.load(f)
                if "baseModel" in json_data:
                    base_model = json_data["baseModel"]
                elif "base model" in json_data:
                    base_model = json_data["base model"]
        except Exception as e:
            print(f"Error reading JSON: {json_path} - {e}")

    if base_model == "Unknown" and os.path.exists(civitai_path):
        try:
            with open(civitai_path, "r", encoding='utf-8-sig') as f:
                civitai_data = json.load(f)
                if "baseModel" in civitai_data:
                    base_model = civitai_data["baseModel"]
                elif "base model" in civitai_data:
                    base_model = civitai_data["base model"]
        except Exception as e:
            print(f"Error reading civitai.info: {civitai_path} - {e}")

    if not civitai_data and os.path.exists(civitai_path):
        try:
            with open(civitai_path, "r", encoding='utf-8-sig') as f:
                civitai_data = json.load(f)
        except Exception as e:
            print(f"Error reading civitai.info: {civitai_path} - {e}")

    # Associated files
    associated_files = []
    for associated_file in os.listdir(root):
        if associated_file.startswith(model_name + "."):
            associated_files.append(associated_file)

    file_path = os.path.join(root, file)
    relative_folder = os.path.relpath(root, models_dir).replace("\\", "/")
    if relative_folder == ".":
        relative_folder = ""

    # Extract fields from json_data
    sd_version = json_data.get('sd version', _map_sd_version(base_model))
    category = json_data.get('category', os.path.basename(root))
    subcategory = json_data.get('subcategory', '')
    activation_text = json_data.get('activation text', '')
    preferred_weight = json_data.get('preferred weight', 0)
    negative_text = json_data.get('negative text', '')
    nsfw = str(json_data.get('nsfw', 'false'))
    high_low = json_data.get('high low', '')
    description = json_data.get('description', '')
    example_prompt = json_data.get('example prompt 1', json_data.get('example prompt', ''))
    example_prompt_2 = json_data.get('example prompt 2', '')
    tags = json_data.get('tags', '')
    parsed_name = json_data.get('name', model_name)
    model_version = json_data.get('model version', json_data.get('name', ''))
    sha256 = json_data.get('sha256', '')

    # Civitai-specific fields
    wcd = json_data.get('web_civitai_data', {})
    civitai_name = wcd.get('civitai name', json_data.get('civitai name', ''))
    civitai_url = wcd.get('url', json_data.get('url', ''))
    creator = wcd.get('creator', json_data.get('creator', ''))

    # Also check civitai_data for URL
    if not civitai_url and civitai_data:
        civitai_url = civitai_data.get('url', '')

    return {
        'id': model_name,
        'name': parsed_name,
        'filename': file,
        'path': file_path,
        'folder': relative_folder,
        'size': os.path.getsize(file_path),
        'date_modified': os.path.getmtime(file_path),
        'base_model': base_model,
        'sd_version': sd_version,
        'category': category,
        'subcategory': subcategory,
        'activation_text': activation_text,
        'preferred_weight': preferred_weight,
        'negative_text': negative_text,
        'nsfw': nsfw,
        'high_low': high_low,
        'description': description,
        'example_prompt': example_prompt,
        'example_prompt_2': example_prompt_2,
        'tags': tags,
        'civitai_name': civitai_name,
        'civitai_url': civitai_url,
        'creator': creator,
        'sha256': sha256,
        'model_version': model_version,
        'preview_url': main_preview_url,
        'preview_images': preview_images,
        'json_data': json_data,
        'civitai_data': civitai_data,
        'associated_files': associated_files,
    }


def sync_models(models_dir, location='loras', force=False):
    """
    Sync models from the filesystem into the SQLite database.

    Args:
        models_dir: Path to the models directory
        location: 'loras' or 'checkpoints'
        force: If True, re-sync all models regardless of mtime
    
    Returns:
        Number of models synced
    """
    if not models_dir or not os.path.exists(models_dir):
        print(f"Models directory does not exist: {models_dir}")
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    synced_count = 0
    found_ids = set()

    for root, dirs, files in os.walk(models_dir):
        for file in files:
            if file.endswith(MODEL_EXTENSIONS):
                # Extract filename without extension
                model_name = os.path.splitext(file)[0]
                model_id = model_name
                found_ids.add(model_id)

                file_path = os.path.join(root, file)
                file_mtime = os.path.getmtime(file_path)

                # Check JSON mtime too (edits to metadata should trigger re-sync)
                json_path = os.path.join(root, f"{model_name}.json")
                json_mtime = os.path.getmtime(json_path) if os.path.exists(json_path) else 0
                latest_mtime = max(file_mtime, json_mtime)

                # Check if we need to sync this model
                if not force:
                    existing = cursor.execute(
                        "SELECT last_synced FROM models WHERE id = ? AND location = ?",
                        (model_id, location)
                    ).fetchone()

                    if existing and existing['last_synced'] and existing['last_synced'] >= latest_mtime:
                        continue  # Skip, already up to date

                # Parse and upsert
                try:
                    model_data = _parse_model_from_filesystem(model_name, root, file, models_dir)
                    _upsert_model(cursor, model_data, location)
                    synced_count += 1
                except Exception as e:
                    print(f"Error syncing model {model_name}: {e}")

    # Remove models from DB that no longer exist on disk for this location
    cursor.execute("SELECT id FROM models WHERE location = ?", (location,))
    db_ids = {row['id'] for row in cursor.fetchall()}
    removed_ids = db_ids - found_ids

    if removed_ids:
        placeholders = ','.join('?' * len(removed_ids))
        cursor.execute(
            f"DELETE FROM models WHERE id IN ({placeholders}) AND location = ?",
            list(removed_ids) + [location]
        )
        print(f"Removed {len(removed_ids)} stale models from database.")

    conn.commit()
    conn.close()
    print(f"Synced {synced_count} models for location '{location}'.")
    return synced_count

def sync_single_model(model_id, models_dir, location='loras'):
    """
    Sync a single model from the filesystem into the SQLite database.
    """
    if not models_dir or not os.path.exists(models_dir):
        return False

    conn = get_connection()
    cursor = conn.cursor()

    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from services.file_service import find_model_file
    except ImportError:
        from .services.file_service import find_model_file
    
    model_file_path = find_model_file(models_dir, model_id)
    if not model_file_path:
        return False

    root = os.path.dirname(model_file_path)
    file = os.path.basename(model_file_path)

    try:
        model_data = _parse_model_from_filesystem(model_id, root, file, models_dir)
        _upsert_model(cursor, model_data, location)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error syncing single model {model_id}: {e}")
        return False


def _upsert_model(cursor, model_data, location):
    """Insert or update a model row in the database."""
    now = time.time()

    cursor.execute("""
        INSERT INTO models (
            id, name, filename, path, location, folder, size, date_modified,
            base_model, sd_version, category, subcategory, activation_text,
            preferred_weight, negative_text, nsfw, high_low, description,
            example_prompt, example_prompt_2, tags, civitai_name, civitai_url,
            creator, sha256, model_version, preview_url, preview_images,
            json_data, civitai_data, associated_files, last_synced
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?
        )
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, filename=excluded.filename, path=excluded.path,
            location=excluded.location, folder=excluded.folder, size=excluded.size,
            date_modified=excluded.date_modified, base_model=excluded.base_model,
            sd_version=excluded.sd_version, category=excluded.category,
            subcategory=excluded.subcategory, activation_text=excluded.activation_text,
            preferred_weight=excluded.preferred_weight, negative_text=excluded.negative_text,
            nsfw=excluded.nsfw, high_low=excluded.high_low, description=excluded.description,
            example_prompt=excluded.example_prompt, example_prompt_2=excluded.example_prompt_2,
            tags=excluded.tags, civitai_name=excluded.civitai_name,
            civitai_url=excluded.civitai_url, creator=excluded.creator,
            sha256=excluded.sha256, model_version=excluded.model_version,
            preview_url=excluded.preview_url, preview_images=excluded.preview_images,
            json_data=excluded.json_data, civitai_data=excluded.civitai_data,
            associated_files=excluded.associated_files, last_synced=excluded.last_synced
    """, (
        model_data['id'], model_data['name'], model_data['filename'],
        model_data['path'], location, model_data['folder'],
        model_data['size'], model_data['date_modified'],
        model_data['base_model'], model_data['sd_version'],
        model_data['category'], model_data['subcategory'],
        model_data['activation_text'], model_data['preferred_weight'],
        model_data['negative_text'], model_data['nsfw'],
        model_data['high_low'], model_data['description'],
        model_data['example_prompt'], model_data['example_prompt_2'],
        model_data['tags'], model_data['civitai_name'],
        model_data['civitai_url'], model_data['creator'],
        model_data['sha256'], model_data['model_version'],
        model_data['preview_url'],
        json.dumps(model_data['preview_images']),
        json.dumps(model_data['json_data']),
        json.dumps(model_data['civitai_data']),
        json.dumps(model_data['associated_files']),
        now
    ))


def get_all_models(location='loras'):
    """Get all models for a location from the database."""
    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        "SELECT * FROM models WHERE location = ? ORDER BY name",
        (location,)
    ).fetchall()

    models = [_row_to_api_dict(row) for row in rows]
    conn.close()
    return models


def get_model(model_id, location=None):
    """Get a single model by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    if location:
        row = cursor.execute(
            "SELECT * FROM models WHERE id = ? AND location = ?",
            (model_id, location)
        ).fetchone()
    else:
        row = cursor.execute(
            "SELECT * FROM models WHERE id = ?",
            (model_id,)
        ).fetchone()

    conn.close()
    if row:
        return _row_to_api_dict(row)
    return None


def update_model_field(model_id, field, value):
    """Update a single field on a model in the database."""
    conn = get_connection()
    # Sanitize field name (whitelist approach)
    allowed_fields = {
        'base_model', 'sd_version', 'category', 'subcategory',
        'activation_text', 'preferred_weight', 'negative_text',
        'nsfw', 'high_low', 'description', 'example_prompt',
        'tags', 'civitai_name', 'civitai_url', 'creator',
        'sha256', 'model_version', 'preview_url', 'preview_images',
        'json_data', 'civitai_data', 'associated_files', 'path',
        'folder', 'name', 'filename', 'size', 'date_modified'
    }
    if field not in allowed_fields:
        conn.close()
        raise ValueError(f"Field '{field}' is not allowed for update.")

    conn.execute(
        f"UPDATE models SET {field} = ?, last_synced = ? WHERE id = ?",
        (value, time.time(), model_id)
    )
    conn.commit()
    conn.close()


def delete_model(model_id):
    """Delete a model from the database."""
    conn = get_connection()
    conn.execute("DELETE FROM models WHERE id = ?", (model_id,))
    conn.commit()
    conn.close()


def get_unique_values(field, location='loras'):
    """Get all unique non-empty values for a field (for combo box population)."""
    conn = get_connection()
    allowed_fields = {
        'base_model', 'sd_version', 'category', 'subcategory',
        'creator', 'high_low', 'tags'
    }
    if field not in allowed_fields:
        conn.close()
        return []

    rows = conn.execute(
        f"SELECT DISTINCT {field} FROM models WHERE location = ? AND {field} IS NOT NULL AND {field} != '' ORDER BY {field}",
        (location,)
    ).fetchall()

    conn.close()
    return [row[0] for row in rows]


def _row_to_api_dict(row):
    """Convert a sqlite3.Row to the API response dict format (matching current frontend expectations)."""
    d = dict(row)

    # Parse JSON-encoded fields back to Python objects
    for json_field in ('preview_images', 'json_data', 'civitai_data', 'associated_files'):
        if d.get(json_field):
            try:
                d[json_field] = json.loads(d[json_field])
            except (json.JSONDecodeError, TypeError):
                d[json_field] = [] if json_field != 'json_data' and json_field != 'civitai_data' else {}

    # Map to the API format the frontend expects
    return {
        'id': d['id'],
        'name': d['name'],
        'filename': d['filename'],
        'path': d['path'],
        'previewUrl': d.get('preview_url', '/assets/placeholder.png'),
        'previewImages': d.get('preview_images', []),
        'size': d.get('size', 0),
        'dateModified': d.get('date_modified', 0),
        'category': d.get('category', ''),
        'baseModel': d.get('base_model', 'Unknown'),
        'sdVersion': d.get('sd_version', 'Unknown'),
        'subcategory': d.get('subcategory', ''),
        'highLow': d.get('high_low', ''),
        'nsfw': d.get('nsfw', 'false'),
        
        # Additional mapped fields for UI
        'activationText': d.get('activation_text', ''),
        'activation_text': d.get('activation_text', ''),
        'preferredWeight': d.get('preferred_weight', 0),
        'negativeTriggerWords': d.get('negative_text', ''),
        'description': d.get('description', ''),
        'examplePrompt': d.get('example_prompt', ''),
        'example_prompt': d.get('example_prompt', ''),
        'examplePrompt2': d.get('example_prompt_2', ''),
        'example_prompt_2': d.get('example_prompt_2', ''),
        'tags': d.get('tags', ''),
        'civitaiName': d.get('civitai_name', ''),
        'civitaiUrl': d.get('civitai_url', ''),
        'civitai_url': d.get('civitai_url', ''),
        'creator': d.get('creator', ''),
        'modelVersion': d.get('model_version', ''),
        
        # Pulling these from json_data since they aren't explicit columns
        'notes': d.get('json_data', {}).get('notes', ''),
        'tested': str(d.get('json_data', {}).get('tested', 'false')).lower() == 'true',
        'allTriggerWords': d.get('civitai_data', {}).get('civitai text', d.get('json_data', {}).get('web_civitai_data', {}).get('civitai text', '')),
        'all_trigger_words': d.get('civitai_data', {}).get('civitai text', d.get('json_data', {}).get('web_civitai_data', {}).get('civitai text', '')),
        
        'json': d.get('json_data', {}),
        'civitaiInfo': d.get('civitai_data', {}),
        'associatedFiles': d.get('associated_files', []),
        'folder': d.get('folder', ''),
        'sha256': d.get('sha256', ''),
    }

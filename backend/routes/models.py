"""
Models API Routes — load, save, delete, move, rename, hash
"""

from flask import Blueprint, request, jsonify
import json
import os
import hashlib

from ..database import (
    sync_models, sync_single_model, get_all_models, get_model, update_model_field,
    delete_model as db_delete_model, get_unique_values, _parse_model_from_filesystem, _upsert_model, get_connection
)
from ..services.file_service import (
    find_file_path, find_model_file, rename_model, move_model,
    delete_model_files
)
from ..routes.settings import get_path_for_location, _load_settings

models_bp = Blueprint('models', __name__)


@models_bp.route('/api/models', methods=['GET'])
def load_models():
    """
    Load all models for a location.
    Query params: location (default 'loras'), refresh (default 'false')
    """
    location = request.args.get('location', 'loras')
    refresh = request.args.get('refresh', 'false').lower() == 'true'

    models_path = get_path_for_location(location)
    if not models_path:
        return jsonify({'error': f'Directory not set for location: {location}'}), 400
    if not os.path.exists(models_path):
        return jsonify({'error': f'Directory does not exist: {models_path}'}), 400

    # Sync from filesystem to SQLite (incremental unless refresh=true)
    sync_models(models_path, location, force=refresh)

    # Read from SQLite
    models = get_all_models(location)
    return jsonify(models)


@models_bp.route('/api/models/<path:model_id>', methods=['GET'])
def load_single_model(model_id):
    """Load a single model's data, re-syncing from disk."""
    location = request.args.get('location', 'loras')
    models_path = get_path_for_location(location)

    if not models_path or not os.path.exists(models_path):
        return jsonify({'error': f'Directory not set or does not exist for location: {location}'}), 400

    # Find model file on disk and re-parse
    model_file_path = find_model_file(models_path, model_id)
    if not model_file_path:
        return jsonify({'error': f'Model file not found: {model_id}'}), 404

    root = os.path.dirname(model_file_path)
    file = os.path.basename(model_file_path)

    try:
        model_data = _parse_model_from_filesystem(model_id, root, file, models_path)

        # Update in SQLite
        conn = get_connection()
        cursor = conn.cursor()
        _upsert_model(cursor, model_data, location)
        conn.commit()
        conn.close()

        # Return from SQLite for consistent format
        model = get_model(model_id, location)
        if model:
            return jsonify(model)
        return jsonify({'error': 'Model not found after sync'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@models_bp.route('/api/models/<path:model_id>', methods=['PUT'])
def save_model(model_id):
    """Save/update model data (writes to both JSON file and SQLite)."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    settings = _load_settings()
    directories = [
        settings.get('modelsDirectory', ''),
        settings.get('checkpointsDirectory', '')
    ]

    # Find the JSON file path
    json_path = None
    model_path = None

    for directory in directories:
        if not directory:
            continue
        json_path = find_file_path(directory, model_id + ".json")
        if json_path:
            break
        model_path = find_model_file(directory, model_id)
        if model_path:
            break

    if not json_path and model_path:
        json_path = os.path.splitext(model_path)[0] + ".json"

    if not json_path:
        return jsonify({'status': 'error', 'message': 'Model file not found'}), 404

    try:
        json_data = data.get('json', {})

        # Map flat payload fields to the standard JSON schema
        if 'name' in data: json_data['name'] = data['name']
        if 'baseModel' in data: 
            json_data['baseModel'] = data['baseModel']
            json_data['base model'] = data['baseModel']
        if 'sdVersion' in data: json_data['sd version'] = data['sdVersion']
        if 'category' in data: json_data['category'] = data['category']
        if 'subcategory' in data: json_data['subcategory'] = data['subcategory']
        if 'highLow' in data: json_data['high low'] = data['highLow']
        if 'nsfw' in data: json_data['nsfw'] = str(data['nsfw']).lower()
        if 'preferredWeight' in data: json_data['preferred weight'] = data['preferredWeight']
        if 'tested' in data: json_data['tested'] = str(data['tested']).lower()
        if 'activation_text' in data: json_data['activation text'] = data['activation_text']
        if 'negative_trigger_words' in data: json_data['negative text'] = data['negative_trigger_words']
        if 'example_prompt' in data: json_data['example prompt 1'] = data['example_prompt']
        if 'example_prompt_2' in data: json_data['example prompt 2'] = data['example_prompt_2']
        if 'description' in data: json_data['description'] = data['description']
        if 'notes' in data: json_data['notes'] = data['notes']
        if 'tags' in data: json_data['tags'] = data['tags']
        if 'version' in data: json_data['model version'] = data['version']
        
        # Slider fields
        if 'isSlider' in data or 'slider' in data:
            json_data['slider'] = bool(data.get('isSlider', data.get('slider', False)))
        if 'sliderMin' in data or 'sliderMax' in data or 'sliderRange' in data:
            min_val = float(data.get('sliderMin', -3.0)) if 'sliderMin' in data else (data.get('sliderRange', [-3.0, 3.0])[0] if isinstance(data.get('sliderRange'), list) and len(data.get('sliderRange')) >= 1 else -3.0)
            max_val = float(data.get('sliderMax', 3.0)) if 'sliderMax' in data else (data.get('sliderRange', [-3.0, 3.0])[1] if isinstance(data.get('sliderRange'), list) and len(data.get('sliderRange')) >= 2 else 3.0)
            json_data['slider range'] = [min_val, max_val]
        if 'sliderMinDesc' in data: json_data['slider min description'] = data['sliderMinDesc']
        if 'sliderMaxDesc' in data: json_data['slider max description'] = data['sliderMaxDesc']

        # Nested Civitai Data
        if 'creator' in data or 'civitaiName' in data or 'civitaiUrl' in data or 'all_trigger_words' in data:
            if 'web_civitai_data' not in json_data:
                json_data['web_civitai_data'] = {}
            if 'creator' in data: json_data['web_civitai_data']['creator'] = data['creator']
            if 'civitaiName' in data: json_data['web_civitai_data']['civitai name'] = data['civitaiName']
            if 'civitaiUrl' in data: json_data['web_civitai_data']['url'] = data['civitaiUrl']
            if 'all_trigger_words' in data: json_data['web_civitai_data']['civitai text'] = data['all_trigger_words']

        # Write to JSON file
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=4)

        # Re-sync this model in SQLite
        for directory in directories:
            if not directory:
                continue
            safetensors_path = find_model_file(directory, model_id)
            if safetensors_path:
                location = 'checkpoints' if directory == settings.get('checkpointsDirectory', '') else 'loras'
                root = os.path.dirname(safetensors_path)
                file = os.path.basename(safetensors_path)
                model_data = _parse_model_from_filesystem(model_id, root, file, directory)
                conn = get_connection()
                cursor = conn.cursor()
                _upsert_model(cursor, model_data, location)
                conn.commit()
                conn.close()
                break

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@models_bp.route('/api/models/<path:model_id>/json', methods=['PUT'])
def save_json(model_id):
    """Save raw JSON data for a model."""
    settings = _load_settings()
    directories = [
        settings.get('modelsDirectory', ''),
        settings.get('checkpointsDirectory', '')
    ]

    file_path = None
    for directory in directories:
        if not directory:
            continue
        file_path = find_file_path(directory, model_id + ".json")
        if file_path:
            break

    if not file_path:
        return jsonify({'status': 'error', 'message': 'JSON file not found'}), 404

    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=4)

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@models_bp.route('/api/models/<path:model_id>/rename', methods=['POST'])
def rename(model_id):
    """Rename a model and all associated files."""
    data = request.get_json()
    new_name = data.get('newName')
    if not new_name:
        return jsonify({'status': 'error', 'message': 'Missing newName'}), 400

    settings = _load_settings()
    directories = [
        settings.get('modelsDirectory', ''),
        settings.get('checkpointsDirectory', '')
    ]

    for directory in directories:
        if not directory:
            continue
        model_file = find_model_file(directory, model_id)
        if model_file:
            result = rename_model(directory, model_id, new_name)

            if result['status'] == 'success':
                # Update SQLite: delete old, sync new
                db_delete_model(model_id)
                location = 'checkpoints' if directory == settings.get('checkpointsDirectory', '') else 'loras'
                sync_single_model(new_name, directory, location)

            return jsonify(result)

    return jsonify({'status': 'error', 'message': 'Model not found'}), 404


@models_bp.route('/api/models/<path:model_id>/move', methods=['POST'])
def move(model_id):
    """Move a model and all associated files to a new folder."""
    data = request.get_json()
    target_folder = data.get('targetFolder', '')

    settings = _load_settings()
    directories = [
        settings.get('modelsDirectory', ''),
        settings.get('checkpointsDirectory', '')
    ]

    for directory in directories:
        if not directory:
            continue
        model_file = find_model_file(directory, model_id)
        if model_file:
            result = move_model(directory, model_id, target_folder)

            if result['status'] == 'success':
                location = 'checkpoints' if directory == settings.get('checkpointsDirectory', '') else 'loras'
                sync_single_model(model_id, directory, location)

            return jsonify(result)

    return jsonify({'status': 'error', 'message': 'Model not found'}), 404


@models_bp.route('/api/models/<path:model_id>', methods=['DELETE'])
def delete(model_id):
    """Delete a model and all associated files."""
    data = request.get_json() or {}
    model_path = data.get('modelPath')

    if not model_path:
        # Try to find it from the database
        model = get_model(model_id)
        if model:
            model_path = model.get('path')

    if not model_path:
        return jsonify({'status': 'error', 'message': 'Model path not found'}), 404

    result = delete_model_files(model_path)

    if result['status'] in ('success', 'partial'):
        db_delete_model(model_id)

    return jsonify(result)


@models_bp.route('/api/models/<path:model_id>/hash', methods=['POST'])
def generate_hash(model_id):
    """Generate SHA256 hash for a model and save to its JSON file."""
    data = request.get_json() or {}
    model_path = data.get('modelPath')

    if not model_path:
        model = get_model(model_id)
        if model:
            model_path = model.get('path')

    if not model_path or not os.path.exists(model_path):
        return jsonify({'status': 'error', 'message': 'Model file not found'}), 404

    try:
        sha256_hash = hashlib.sha256()
        with open(model_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        hash_hex = sha256_hash.hexdigest()

        # Update JSON file
        json_path = os.path.splitext(model_path)[0] + ".json"
        json_data = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding='utf-8-sig') as f:
                    json_data = json.load(f)
            except Exception:
                pass

        json_data['sha256'] = hash_hex
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)

        # Update SQLite
        update_model_field(model_id, 'sha256', hash_hex)

        return jsonify({
            'status': 'success',
            'hash': hash_hex,
            'message': f'Generated SHA256: {hash_hex}'
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@models_bp.route('/api/models/unique-values/<field>', methods=['GET'])
def unique_values(field):
    """Get unique values for a field (for combo box population)."""
    location = request.args.get('location', 'loras')
    values = get_unique_values(field, location)
    return jsonify(values)

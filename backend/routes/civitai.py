"""
Civitai API Routes — scan, fetch info, download previews, convert, hash, find duplicates.
Delegates heavy lifting to civitai_handler service.
"""

from flask import Blueprint, request, jsonify
import os
import json

from ..services import civitai_handler
from ..services.file_service import find_file_path
from ..routes.settings import get_path_for_location
from ..database import sync_models, sync_single_model

civitai_bp = Blueprint('civitai', __name__)


def _sync_model_path_to_db(model_path):
    """Helper to sync a model into the SQLite DB after metadata/preview update."""
    try:
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        # Determine location based on path or fallback to loras
        checkpoints_dir = get_path_for_location('checkpoints')
        loras_dir = get_path_for_location('loras')
        
        if checkpoints_dir and os.path.abspath(model_path).startswith(os.path.abspath(checkpoints_dir)):
            sync_single_model(model_name, checkpoints_dir, 'checkpoints')
        elif loras_dir:
            sync_single_model(model_name, loras_dir, 'loras')
    except Exception as e:
        print(f"Error syncing model to DB: {e}")


@civitai_bp.route('/api/civitai/scan', methods=['POST'])
def scan_models():
    """Scan models directory and return list with status."""
    try:
        location = request.args.get('location', 'loras')
        models_path = get_path_for_location(location)

        if not models_path:
            return jsonify({'status': 'error', 'message': f'Directory not set for location: {location}'}), 400

        models = civitai_handler.scan_models_directory(models_path)
        return jsonify({'status': 'success', 'models': models})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/fetch-by-hash', methods=['POST'])
def fetch_by_hash():
    """Generate hash and fetch model info from Civitai."""
    try:
        data = request.get_json() or {}
        model_path = data.get('modelPath')
        logs = []

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400

        filename = os.path.basename(model_path)

        # 1. Creating hash
        logs.append({'message': f"Creating hash for {filename}...", 'type': 'info'})
        file_hash = civitai_handler.generate_sha256(model_path)

        if not file_hash:
            logs.append({'message': "Failed to generate SHA256 hash", 'type': 'error'})
            return jsonify({'status': 'error', 'message': 'Failed to generate SHA256 hash', 'logs': logs})

        logs.append({'message': f"Hash generated successfully ({file_hash[:10]}...)", 'type': 'success'})

        # 2. Gathering Metadata
        logs.append({'message': "Gathering Metadata...", 'type': 'info'})
        model_info = civitai_handler.fetch_model_info_by_hash(file_hash)

        if not model_info:
            logs.append({'message': "Not found on Civitai. Checking CivArchive...", 'type': 'warning'})
            model_info = civitai_handler.scrape_civarchive_by_hash(file_hash)

        if model_info is None:
            logs.append({'message': "Failed to connect to Civitai / CivArchive APIs.", 'type': 'error'})
            return jsonify({'status': 'error', 'message': 'Failed to connect to APIs', 'logs': logs})

        if not model_info:
            logs.append({'message': f"Metadata not found on Civitai or CivArchive", 'type': 'error'})
            return jsonify({'status': 'not_found', 'message': 'Model not found on Civitai or CivArchive', 'logs': logs})

        # 3. JSON created successfully
        success = civitai_handler.save_civitai_info(model_path, model_info)
        civitai_handler.save_sha256_to_json(model_path, file_hash)

        if not success:
            logs.append({'message': "Failed to save JSON.", 'type': 'error'})
            return jsonify({'status': 'error', 'message': 'Failed to save model JSON', 'logs': logs})

        logs.append({'message': "JSON created successfully", 'type': 'success'})

        # 4. Fetching Preview Images
        logs.append({'message': "Fetching Preview Images...", 'type': 'info'})
        preview_success = civitai_handler.download_preview_image(model_path)
        if preview_success:
            logs.append({'message': "Thumbnail downloaded successfully", 'type': 'success'})
        else:
            logs.append({'message': "Thumbnail skipped (no preview available or skipped)", 'type': 'warning'})

        _sync_model_path_to_db(model_path)

        return jsonify({
            'status': 'success',
            'message': 'JSON and thumbnails created successfully' if preview_success else 'JSON created successfully, thumbnail skipped',
            'previewSuccess': preview_success,
            'modelInfo': model_info,
            'logs': logs
        })

    except Exception as e:
        print(f"Error in fetch-by-hash: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civarchive/fetch-by-hash', methods=['POST'])
def fetch_civarchive_by_hash():
    """Generate hash and fetch model info from CivArchive."""
    try:
        data = request.get_json() or {}
        model_path = data.get('modelPath')
        logs = []

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400

        filename = os.path.basename(model_path)

        # 1. Creating hash
        logs.append({'message': f"Creating hash for {filename}...", 'type': 'info'})
        file_hash = civitai_handler.generate_sha256(model_path)

        if not file_hash:
            logs.append({'message': "Failed to generate SHA256 hash", 'type': 'error'})
            return jsonify({'status': 'error', 'message': 'Failed to generate SHA256 hash', 'logs': logs})

        logs.append({'message': f"Hash generated successfully ({file_hash[:10]}...)", 'type': 'success'})

        # 2. Gathering Metadata from CivArchive
        logs.append({'message': "Gathering Metadata from CivArchive...", 'type': 'info'})
        model_info = civitai_handler.scrape_civarchive_by_hash(file_hash)

        if model_info is None:
            logs.append({'message': "Failed to connect to CivArchive.", 'type': 'error'})
            return jsonify({'status': 'error', 'message': 'Failed to connect to CivArchive', 'logs': logs})

        if not model_info:
            logs.append({'message': "Model not found on CivArchive.", 'type': 'error'})
            return jsonify({'status': 'not_found', 'message': 'Model not found on CivArchive', 'logs': logs})

        # 3. JSON created successfully
        success = civitai_handler.save_civitai_info(model_path, model_info)
        civitai_handler.save_sha256_to_json(model_path, file_hash)

        if not success:
            logs.append({'message': "Failed to save JSON.", 'type': 'error'})
            return jsonify({'status': 'error', 'message': 'Failed to save model JSON', 'logs': logs})

        logs.append({'message': "JSON created successfully", 'type': 'success'})

        # 4. Fetching Preview Images
        logs.append({'message': "Fetching Preview Images...", 'type': 'info'})
        preview_success = civitai_handler.download_preview_image(model_path)
        if preview_success:
            logs.append({'message': "Thumbnail downloaded successfully", 'type': 'success'})
        else:
            logs.append({'message': "Thumbnail skipped (no preview available or skipped)", 'type': 'warning'})

        _sync_model_path_to_db(model_path)

        return jsonify({
            'status': 'success',
            'message': 'Model data saved to JSON successfully from CivArchive',
            'previewSuccess': preview_success,
            'modelInfo': model_info,
            'logs': logs
        })

    except Exception as e:
        print(f"Error in fetch_civarchive_by_hash: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/fetch-by-url', methods=['POST'])
def fetch_by_url():
    """Fetch model info from Civitai using a manually provided URL."""
    try:
        data = request.get_json() or {}
        model_path = data.get('modelPath')
        civitai_url = data.get('civitaiUrl')
        logs = []

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400
        if not civitai_url:
            return jsonify({'status': 'error', 'message': 'Missing civitaiUrl'}), 400

        filename = os.path.basename(model_path)
        logs.append({'message': f"Gathering Metadata from URL: {civitai_url}", 'type': 'info'})

        # Handle explicit 'ignore' URL
        if civitai_url == 'https://no-match.com/ignored':
            model_info = {"ignored": True, "url": civitai_url, "name": filename}
        elif 'civarchive.com' in civitai_url or 'civitaiarchive.com' in civitai_url:
            model_info = civitai_handler.scrape_civarchive_by_url(civitai_url)
            if model_info is None:
                return jsonify({'status': 'error', 'message': 'Failed to connect to CivArchive', 'logs': logs})
            if not model_info:
                return jsonify({'status': 'not_found', 'message': 'Model/version not found on CivArchive', 'logs': logs})
        else:
            model_id, version_id = civitai_handler.parse_civitai_url(civitai_url)
            if not version_id and not model_id:
                return jsonify({'status': 'error', 'message': 'Could not parse model or version ID from URL.', 'logs': logs})

            if version_id:
                model_info = civitai_handler.fetch_model_info_by_version_id(version_id)
            else:
                model_info = civitai_handler.fetch_model_info_by_id(model_id)
                if model_info and 'modelVersions' in model_info and model_info['modelVersions']:
                    model_info = model_info['modelVersions'][0]

            if model_info is None:
                return jsonify({'status': 'error', 'message': 'Failed to connect to Civitai API', 'logs': logs})
            if not model_info:
                return jsonify({'status': 'not_found', 'message': 'Model/version not found on Civitai', 'logs': logs})

        success = civitai_handler.save_civitai_info(model_path, model_info)
        if not success:
            return jsonify({'status': 'error', 'message': 'Failed to save model JSON', 'logs': logs})

        logs.append({'message': "JSON created successfully", 'type': 'success'})

        preview_success = False
        if not model_info.get('ignored'):
            logs.append({'message': "Fetching Preview Images...", 'type': 'info'})
            preview_success = civitai_handler.download_preview_image(model_path)
            if preview_success:
                logs.append({'message': "Thumbnail downloaded successfully", 'type': 'success'})
            else:
                logs.append({'message': "Thumbnail skipped (no preview available or skipped)", 'type': 'warning'})

        _sync_model_path_to_db(model_path)

        return jsonify({
            'status': 'success',
            'message': 'Model data saved to JSON from URL',
            'previewSuccess': preview_success,
            'modelInfo': model_info,
            'logs': logs
        })

    except Exception as e:
        print(f"Error in fetch-by-url: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/download-preview', methods=['POST'])
def download_preview():
    """Download preview image for a model."""
    try:
        data = request.get_json() or {}
        model_path = data.get('modelPath')
        max_size = data.get('maxSize', False)
        skip_nsfw = data.get('skipNsfw', False)
        force_additional = data.get('forceAdditional', False)
        logs = []

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400

        logs.append({'message': "Fetching Preview Images...", 'type': 'info'})
        success = civitai_handler.download_preview_image(model_path, max_size, skip_nsfw, force_additional)

        if success:
            _sync_model_path_to_db(model_path)
            logs.append({'message': "Thumbnail downloaded successfully", 'type': 'success'})
        else:
            logs.append({'message': "Thumbnail skipped or not found", 'type': 'warning'})

        return jsonify({
            'status': 'success' if success else 'skipped',
            'message': 'Thumbnail downloaded successfully' if success else 'Thumbnail skipped or not found',
            'logs': logs
        })

    except Exception as e:
        print(f"Error in download-preview: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/convert', methods=['POST'])
def convert_to_json():
    """Convert civitai.info to JSON format."""
    try:
        data = request.get_json()
        model_path = data.get('modelPath')
        use_api = data.get('useApi', True)

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400

        base_path = os.path.splitext(model_path)[0]
        info_path = f"{base_path}.civitai.info"

        if not os.path.exists(info_path):
            return jsonify({'status': 'error', 'message': 'No .civitai.info file found'})

        # Check for existing creator
        json_path = f"{base_path}.json"
        existing_creator = ''
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_json = json.load(f)
                    existing_creator = existing_json.get('creator', '')
            except Exception:
                pass

        api_call_made = use_api and not existing_creator
        mapped_data = civitai_handler.parse_civitai_info_file(info_path, use_api, existing_creator)

        # Add enhanced fields from info file
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info_data = json.load(f)

            existing_wcd = mapped_data.pop('web_civitai_data', {})

            wcd = {
                'civitai name': existing_wcd.get('civitai name') or mapped_data.pop('civitai name', ''),
                'civitai text': existing_wcd.get('civitai text') or mapped_data.pop('civitai text', ''),
                'creator': existing_wcd.get('creator') or mapped_data.pop('creator', ''),
                'downloadUrl': existing_wcd.get('downloadUrl', ''),
                'file_id': existing_wcd.get('file_id', ''),
                'model_id': existing_wcd.get('model_id', ''),
                'original_filename': existing_wcd.get('original_filename', ''),
                'preview_image_1': existing_wcd.get('preview_image_1', ''),
                'preview_image_2': existing_wcd.get('preview_image_2', ''),
                'published_date': existing_wcd.get('published_date', ''),
                'url': existing_wcd.get('url') or mapped_data.pop('url', '')
            }

            if 'modelId' in info_data:
                wcd['model_id'] = info_data['modelId']
            if 'id' in info_data:
                wcd['file_id'] = info_data['id']
            if 'publishedAt' in info_data:
                wcd['published_date'] = info_data['publishedAt']
            if 'baseModelType' in info_data:
                mapped_data['base_model_type'] = info_data['baseModelType']
            if 'model' in info_data and 'type' in info_data['model']:
                mapped_data['model_type'] = info_data['model']['type']

            if 'files' in info_data and isinstance(info_data['files'], list) and info_data['files']:
                first_file = info_data['files'][0]
                if 'name' in first_file:
                    wcd['original_filename'] = first_file['name']
                if 'downloadUrl' in first_file:
                    wcd['downloadUrl'] = first_file['downloadUrl']
            if not wcd.get('downloadUrl') and 'downloadUrl' in info_data:
                wcd['downloadUrl'] = info_data['downloadUrl']

            if 'images' in info_data and isinstance(info_data['images'], list):
                if len(info_data['images']) > 0 and 'url' in info_data['images'][0]:
                    wcd['preview_image_1'] = info_data['images'][0]['url']
                if len(info_data['images']) > 1 and 'url' in info_data['images'][1]:
                    wcd['preview_image_2'] = info_data['images'][1]['url']
                if len(info_data['images']) > 1:
                    second_img = info_data['images'][1]
                    if 'meta' in second_img and isinstance(second_img['meta'], dict) and 'prompt' in second_img['meta']:
                        mapped_data['example prompt 2'] = second_img['meta']['prompt']

            if not wcd['url'] and wcd['model_id'] and wcd['file_id']:
                wcd['url'] = f"https://civitai.com/models/{wcd['model_id']}?modelVersionId={wcd['file_id']}"

            mapped_data['web_civitai_data'] = wcd

        except Exception as e:
            print(f"Error adding new fields from info file: {e}")

        # Preserve existing fields
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

                    fields_to_preserve = [
                        'activation text', 'sd version', 'preferred weight',
                        'negative text', 'nsfw', 'example prompt 1',
                        'category', 'subcategory', 'tags',
                        'name', 'model version', 'high low', 'sha256'
                    ]
                    for field in fields_to_preserve:
                        if field in existing_data and existing_data[field] is not None and existing_data[field] != '':
                            mapped_data[field] = existing_data[field]

                    if not mapped_data.get('base model'):
                        existing_bm = existing_data.get('base model') or existing_data.get('baseModel')
                        if existing_bm:
                            mapped_data['base model'] = existing_bm

                    existing_wcd = existing_data.get('web_civitai_data', {})
                    for field in ['civitai text', 'url', 'creator']:
                        if field in existing_wcd and existing_wcd[field]:
                            mapped_data['web_civitai_data'][field] = existing_wcd[field]
                        elif field in existing_data and existing_data[field] is not None and existing_data[field] != '':
                            mapped_data['web_civitai_data'][field] = existing_data[field]
            except Exception as e:
                print(f"Error preserving existing fields: {e}")

        if mapped_data.get('base model'):
            mapped_data['baseModel'] = mapped_data['base model']
        elif mapped_data.get('baseModel'):
            mapped_data['base model'] = mapped_data['baseModel']

        civitai_handler.write_json_file(info_path, mapped_data)

        return jsonify({
            'status': 'success',
            'message': 'Converted to JSON successfully',
            'apiCallMade': api_call_made
        })

    except Exception as e:
        print(f"Error in convert-to-json: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/fix-thumbnail', methods=['POST'])
def fix_thumbnail():
    """Fix thumbnail name to .preview.png format."""
    try:
        data = request.get_json()
        model_path = data.get('modelPath')

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400

        status, message = civitai_handler.fix_thumbnail_name(model_path)
        return jsonify({'status': status, 'message': message})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/create-placeholder', methods=['POST'])
def create_placeholder():
    """Create a placeholder JSON file for models not found on Civitai."""
    try:
        data = request.get_json()
        model_path = data.get('modelPath')

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400

        success = civitai_handler.create_dummy_info_file(model_path)

        if success:
            return jsonify({'status': 'success', 'message': 'Placeholder JSON created'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create placeholder'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/generate-hash', methods=['POST'])
def generate_hash():
    """Generate SHA256 hash for a model and save to JSON."""
    try:
        data = request.get_json()
        model_path = data.get('modelPath')
        skip_if_exists = data.get('skipIfExists', False)

        if not model_path:
            return jsonify({'status': 'error', 'message': 'Missing modelPath'}), 400

        if skip_if_exists:
            base_path = os.path.splitext(model_path)[0]
            json_path = f"{base_path}.json"
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8-sig') as f:
                        existing_data = json.load(f)
                        if existing_data.get('sha256'):
                            return jsonify({
                                'status': 'skipped',
                                'message': 'Hash already exists',
                                'sha256': existing_data['sha256']
                            })
                except Exception:
                    pass

        file_hash = civitai_handler.generate_sha256(model_path)

        if file_hash:
            civitai_handler.save_sha256_to_json(model_path, file_hash)
            return jsonify({
                'status': 'success',
                'message': 'Hash generated and saved',
                'sha256': file_hash
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to generate hash'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/find-duplicates', methods=['POST'])
def find_duplicates():
    """Find duplicate models by comparing SHA256 hashes."""
    try:
        data = request.get_json() or {}
        location = data.get('location', 'loras')
        models_path = get_path_for_location(location)

        if not models_path:
            return jsonify({'status': 'error', 'message': f'Directory not set for location: {location}'}), 400

        result = civitai_handler.find_duplicate_models(models_path)

        return jsonify({
            'status': 'success',
            'duplicates': result['duplicates'],
            'missingHash': result['missing_hash'],
            'totalScanned': result['total_scanned'],
            'duplicateGroupCount': len(result['duplicates']),
            'duplicateFileCount': sum(len(group) for group in result['duplicates'])
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@civitai_bp.route('/api/civitai/save-info', methods=['POST'])
def save_civitai_info():
    """Save civitai.info data for a model."""
    try:
        data = request.get_json()
        model_name = data.get('name')

        if not model_name:
            return jsonify({'status': 'error', 'message': 'Missing name'}), 400

        from ..routes.settings import _load_settings
        settings = _load_settings()
        directories = [
            settings.get('modelsDirectory', ''),
            settings.get('checkpointsDirectory', '')
        ]

        file_path = None
        for directory in directories:
            if not directory:
                continue
            file_path = find_file_path(directory, model_name + ".civitai.info")
            if file_path:
                break

        if not file_path:
            return jsonify({'status': 'error', 'message': 'Civitai info file not found'}), 404

        try:
            json_data = data.get('data', {})
            with open(file_path, 'w') as f:
                json.dump(json_data, f, indent=4)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

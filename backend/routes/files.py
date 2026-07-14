"""
Files API Routes — folders, upload preview, delete/reorder thumbnails, serve model files
"""

from flask import Blueprint, request, jsonify
import os
import glob

from ..constants import MODEL_EXTENSIONS
from ..services.file_service import (
    get_folders, save_uploaded_preview, delete_thumbnail, reorder_thumbnails,
    find_file_path
)
from ..routes.settings import get_path_for_location

files_bp = Blueprint('files', __name__)


@files_bp.route('/api/folders', methods=['GET'])
def list_folders():
    """Get all subdirectories in the models directory."""
    location = request.args.get('location', 'loras')
    models_path = get_path_for_location(location)

    if not models_path or not os.path.exists(models_path):
        return jsonify({'error': f'Directory not set or does not exist for location: {location}'}), 400

    folders = get_folders(models_path)
    return jsonify({'folders': folders})


@files_bp.route('/api/models/<model_id>/preview', methods=['POST'])
def upload_preview(model_id):
    """Upload a preview image for a model."""
    if 'imageFile' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image file provided'}), 400

    image_file = request.files['imageFile']
    location = request.form.get('location', 'loras')

    if not image_file:
        return jsonify({'status': 'error', 'message': 'Empty image file'}), 400

    image_data = image_file.read()
    if not image_data:
        return jsonify({'status': 'error', 'message': 'Empty image data'}), 400

    location_dir = get_path_for_location(location)
    if not location_dir:
        return jsonify({'status': 'error', 'message': f'Directory not set for location: {location}'}), 400

    result = save_uploaded_preview(location_dir, model_id, image_data, location_dir)
    return jsonify(result)


@files_bp.route('/api/models/<model_id>/thumbnail', methods=['DELETE'])
def remove_thumbnail(model_id):
    """Delete a specific thumbnail and renumber remaining ones."""
    data = request.get_json()
    thumbnail_index = data.get('thumbnailIndex')
    location = data.get('location', 'loras')

    if thumbnail_index is None:
        return jsonify({'status': 'error', 'message': 'Missing thumbnailIndex'}), 400

    base_path = get_path_for_location(location)
    if not base_path:
        return jsonify({'status': 'error', 'message': f'Directory not set for location: {location}'}), 400

    result = delete_thumbnail(base_path, model_id, thumbnail_index)
    return jsonify(result)


@files_bp.route('/api/models/<model_id>/thumbnails/reorder', methods=['POST'])
def reorder(model_id):
    """Reorder thumbnails for a model."""
    data = request.get_json()
    new_order = data.get('newOrder')
    location = data.get('location', 'loras')

    if not new_order:
        return jsonify({'status': 'error', 'message': 'Missing newOrder'}), 400

    base_path = get_path_for_location(location)
    if not base_path:
        return jsonify({'status': 'error', 'message': f'Directory not set for location: {location}'}), 400

    result = reorder_thumbnails(base_path, model_id, new_order)
    return jsonify(result)


@files_bp.route('/api/files/sort-downloads', methods=['POST'])
def sort_downloads():
    """Move all models from download directory to sorting directory."""
    from ..routes.settings import _load_settings
    import shutil
    import glob
    
    settings = _load_settings()
    download_dir = settings.get('defaultDownloadDirectory')
    sorting_dir = settings.get('defaultSortingDirectory')
    
    if not download_dir or not os.path.exists(download_dir):
        return jsonify({'status': 'error', 'message': 'Download directory is not set or does not exist.'}), 400
        
    if not sorting_dir or not os.path.exists(sorting_dir):
        return jsonify({'status': 'error', 'message': 'Sorting directory is not set or does not exist.'}), 400
        
    if os.path.normpath(download_dir) == os.path.normpath(sorting_dir):
        return jsonify({'status': 'error', 'message': 'Download and Sorting directories are the same.'}), 400

    moved_count = 0
    errors = []
    
    # Find all model files in download_dir
    model_files = []
    for ext in MODEL_EXTENSIONS:
        model_files.extend(glob.glob(os.path.join(glob.escape(download_dir), f'*{ext}')))
    
    for file_path in model_files:
        try:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Common extensions associated with a model
            extensions = list(MODEL_EXTENSIONS) + [
                ".json", ".civitai.info", ".txt",
                ".preview.png", ".preview2.png", ".preview3.png", ".preview4.png",
                ".png", ".jpg", ".jpeg", ".webp", ".mp4", ".gif"
            ]
            
            for ext in extensions:
                src = os.path.join(download_dir, base_name + ext)
                if os.path.exists(src):
                    dst = os.path.join(sorting_dir, base_name + ext)
                    shutil.move(src, dst)
                    
            moved_count += 1
        except Exception as e:
            errors.append(f"Failed to move {os.path.basename(file_path)}: {str(e)}")
            
    return jsonify({
        'status': 'success',
        'moved_count': moved_count,
        'errors': errors
    })


@files_bp.route('/api/files/associated', methods=['GET'])
def get_associated_files():
    """Get all files sharing the same prefix as the model."""
    import glob
    model_path = request.args.get('modelPath')
    
    if not model_path or not os.path.exists(model_path):
        return jsonify({'status': 'error', 'message': 'Model not found'}), 404
        
    model_dir = os.path.dirname(model_path)
    model_name = os.path.splitext(os.path.basename(model_path))[0]
    
    if not os.path.exists(model_dir):
        return jsonify({'status': 'error', 'message': 'Directory not found'}), 404
        
    files = []
    for f in os.listdir(model_dir):
        if f.startswith(model_name + "."):
            files.append(os.path.join(model_dir, f))
    
    result = []
    
    for f in files:
        if not os.path.isfile(f):
            continue
            
        filename = os.path.basename(f)
        ext = os.path.splitext(filename)[1].lower()
        size_bytes = os.path.getsize(f)
        
        file_type = 'unknown'
        if ext in ['.png', '.jpg', '.jpeg', '.webp']:
            file_type = 'image'
        elif ext in ['.mp4', '.webm', '.gif']:
            file_type = 'video'
        elif ext == '.json' or ext == '.info':
            file_type = 'metadata'
        elif ext in MODEL_EXTENSIONS:
            file_type = 'model'
        elif ext == '.txt':
            file_type = 'text'
            
        # Determine relative path for preview serving
        from ..routes.settings import _load_settings
        settings = _load_settings()
        directories = [
            settings.get('modelsDirectory', ''),
            settings.get('checkpointsDirectory', '')
        ]
        relative_path = ""
        for directory in directories:
            if directory and f.startswith(directory):
                relative_path = os.path.relpath(f, directory).replace("\\", "/")
                break
                
        result.append({
            'filename': filename,
            'path': f,  # Absolute path to be used by delete endpoint
            'relativePath': relative_path,
            'sizeBytes': size_bytes,
            'type': file_type
        })
        
    return jsonify({'status': 'success', 'files': result})


@files_bp.route('/api/files/associated', methods=['DELETE'])
def delete_associated_file():
    """Delete a specific associated file."""
    data = request.get_json()
    file_path = data.get('filePath')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
    if not os.path.isfile(file_path):
        return jsonify({'status': 'error', 'message': 'Path is not a file'}), 400
        
    try:
        os.remove(file_path)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@files_bp.route('/api/files/clean-json', methods=['POST'])
def clean_json():
    import os, json
    from ..services.civitai_handler import parse_civitai_info_file, write_json_file
    from ..routes.settings import _load_settings
    
    settings = _load_settings()
    directories = [
        settings.get('modelsDirectory', ''),
        settings.get('checkpointsDirectory', '')
    ]
    
    cleaned_count = 0
    errors = []
    
    for directory in directories:
        if not directory or not os.path.exists(directory):
            continue
            
        for root_dir, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.civitai.info'):
                    info_path = os.path.join(root_dir, file)
                    base_path = info_path[:-13]
                    json_path = base_path + '.json'
                    
                    try:
                        mapped_data = parse_civitai_info_file(info_path, use_api=False)
                        
                        if os.path.exists(json_path):
                            with open(json_path, 'r', encoding='utf-8') as jf:
                                existing_data = json.load(jf)
                            
                            fields_to_preserve = [
                                'activation text', 'sd version', 'preferred weight',
                                'negative text', 'nsfw', 'base model', 'example prompt 1',
                                'category', 'subcategory', 'tags',
                                'name', 'model version', 'high low', 'sha256'
                            ]
                            for field in fields_to_preserve:
                                if field in existing_data and existing_data[field] is not None and existing_data[field] != '':
                                    mapped_data[field] = existing_data[field]
                            
                            existing_wcd = existing_data.get('web_civitai_data', {})
                            for field in ['civitai text', 'url', 'creator']:
                                if field in existing_wcd and existing_wcd[field]:
                                    mapped_data['web_civitai_data'][field] = existing_wcd[field]
                                elif field in existing_data and existing_data[field] is not None and existing_data[field] != '':
                                    mapped_data['web_civitai_data'][field] = existing_data[field]
                        
                        write_json_file(info_path, mapped_data)
                        
                        if os.path.exists(info_path):
                            os.remove(info_path)
                            
                        cleaned_count += 1
                    except Exception as e:
                        errors.append(f'Failed on {file}: {str(e)}')
                        
    return jsonify({'status': 'success', 'cleaned': cleaned_count, 'errors': errors})

@files_bp.route('/api/files/open-folder', methods=['POST'])
def open_folder():
    """Open a folder in the OS file explorer."""
    data = request.get_json()
    path = data.get('path')
    
    if not path or not os.path.exists(path):
        return jsonify({'status': 'error', 'message': 'Invalid path or path does not exist'}), 400
        
    try:
        if os.path.isfile(path):
            folder_path = os.path.dirname(path)
        else:
            folder_path = path

        if hasattr(os, 'startfile'):
            os.startfile(folder_path)
        else:
            import subprocess
            import sys
            if sys.platform == 'darwin':
                subprocess.Popen(['open', folder_path])
            else:
                subprocess.Popen(['xdg-open', folder_path])
                
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

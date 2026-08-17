"""
File Service — handles all filesystem operations for models.
Extracted from the original manager.py for clean separation of concerns.
"""

import os
import shutil
import json
from ..constants import MODEL_EXTENSIONS

def find_file_path(directory, filename):
    """
    Find a file within a directory tree (case-insensitive search).
    Returns the full path if found, None otherwise.
    """
    if not directory or not os.path.exists(directory):
        return None

    filename_lower = filename.lower()
    filename_base, filename_ext = os.path.splitext(filename)

    for root, dirs, files in os.walk(directory):
        # First try exact match
        if filename in files:
            return os.path.join(root, filename)

        # Then try case-insensitive match
        for file in files:
            if file.lower() == filename_lower:
                return os.path.join(root, file)

            # Special handling for known extensions like .preview.png
            if '.preview.' in filename_lower:
                file_base, file_ext = os.path.splitext(file)
                if file_base.lower() == filename_base.lower() and file_ext.lower() == filename_ext.lower():
                    return os.path.join(root, file)

    return None


def find_model_file(directory, model_name):
    """
    Find a model file matching any supported extension.
    Returns the path if found, None otherwise.
    """
    for ext in MODEL_EXTENSIONS:
        path = find_file_path(directory, model_name + ext)
        if path:
            return path
    return None


def get_folders(models_dir):
    """
    Get all subdirectories within the models directory.
    Returns a sorted list of folder dicts with 'path' and 'name' keys.
    """
    if not models_dir or not os.path.exists(models_dir):
        return []

    folders = [{'path': '', 'name': 'Root'}]

    for root, dirs, files in os.walk(models_dir):
        for dir_name in dirs:
            full_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(full_path, models_dir).replace("\\", "/")
            folders.append({
                'path': relative_path,
                'name': relative_path
            })

    # Sort hierarchically
    folders.sort(key=lambda f: (
        0 if f['path'] == '' else 1,
        tuple(f['path'].lower().split('/'))
    ))

    return folders


def rename_model(base_dir, old_name, new_name):
    """
    Rename a model and all its associated files.
    Returns a dict with status and details.
    """
    old_model_path = find_model_file(base_dir, old_name)
    if not old_model_path:
        return {'status': 'error', 'message': f'Model file not found: {old_name}'}

    # Verify that the new name doesn't already exist
    new_model_path = find_model_file(base_dir, new_name)
    if new_model_path:
        return {'status': 'error', 'message': f'A model with the name "{new_name}" already exists. Please choose a different name.'}

    model_dir = os.path.dirname(old_model_path)

    try:
        # Find all associated files dynamically
        associated_files = []
        for file in os.listdir(model_dir):
            if file.startswith(old_name + "."):
                associated_files.append(file)

        # Rename all of them
        for file in associated_files:
            old_path = os.path.join(model_dir, file)
            extension = file[len(old_name):]  # e.g., '.json' or '.preview.jpg'
            new_path = os.path.join(model_dir, new_name + extension)
            os.rename(old_path, new_path)

        return {'status': 'success'}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def move_model(base_dir, model_name, target_folder):
    """
    Move a model and all its associated files to a new folder.
    Returns a dict with status and details.
    """
    model_file = find_model_file(base_dir, model_name)
    if not model_file:
        return {'status': 'error', 'message': 'Model file not found'}

    model_dir = os.path.dirname(model_file)

    # Determine target directory
    if target_folder:
        target_dir = os.path.join(base_dir, target_folder)
    else:
        target_dir = base_dir

    # Create target directory if needed
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to create target directory: {e}'}

    # Find all associated files dynamically
    files_to_move = []
    for file in os.listdir(model_dir):
        if file.startswith(model_name + "."):
            files_to_move.append(os.path.join(model_dir, file))

    try:
        for file_path in files_to_move:
            filename = os.path.basename(file_path)
            new_path = os.path.join(target_dir, filename)

            if os.path.exists(new_path):
                return {'status': 'error', 'message': f'File already exists in target: {filename}'}

            shutil.move(file_path, new_path)

        return {
            'status': 'success',
            'message': f'Moved {len(files_to_move)} file(s)',
            'filesMoved': len(files_to_move)
        }

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def delete_model_files(model_path):
    """
    Delete a model and all its associated files.
    Returns a dict with status and details.
    """
    if not model_path or not os.path.exists(model_path):
        return {'status': 'error', 'message': f'Model file not found: {model_path}'}

    model_name = os.path.splitext(os.path.basename(model_path))[0]
    model_dir = os.path.dirname(model_path)

    deleted_files = []
    failed_files = []

    # Find all associated files dynamically
    if os.path.exists(model_dir):
        for file in os.listdir(model_dir):
            if file.startswith(model_name + "."):
                file_path = os.path.join(model_dir, file)
                try:
                    os.remove(file_path)
                    deleted_files.append(file)
                except Exception as e:
                    failed_files.append(file)

    return {
        'status': 'success' if not failed_files else 'partial',
        'message': f'Deleted {len(deleted_files)} files',
        'deletedFiles': deleted_files,
        'failedFiles': failed_files
    }


def _find_thumbnail_file_for_slot(directory, model_name, slot):
    """Find the existing thumbnail file for a specific slot number (1-based) with any supported extension."""
    exts = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp')
    if slot == 1:
        for ext in exts:
            p = os.path.join(directory, f"{model_name}.preview{ext}")
            if os.path.exists(p):
                return p
        for ext in exts:
            p = os.path.join(directory, f"{model_name}{ext}")
            if os.path.exists(p):
                return p
    else:
        for ext in exts:
            p = os.path.join(directory, f"{model_name}.preview{slot}{ext}")
            if os.path.exists(p):
                return p
    return None


def save_uploaded_preview(base_dir, model_name, image_data, location_dir):
    """
    Save an uploaded preview image for a model.
    Automatically determines the next available preview number and preserves image format.
    """
    model_file = find_model_file(location_dir, model_name)
    if not model_file:
        return {'status': 'error', 'message': 'Model not found'}

    model_dir = os.path.dirname(model_file)

    # Detect extension from magic bytes
    ext = '.png'
    if image_data.startswith(b'\xff\xd8\xff'):
        ext = '.jpg'
    elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:16]:
        ext = '.webp'
    elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
        ext = '.png'

    # Determine next preview slot
    if not _find_thumbnail_file_for_slot(model_dir, model_name, 1):
        preview_filename = f"{model_name}.preview{ext}"
    else:
        n = 2
        while _find_thumbnail_file_for_slot(model_dir, model_name, n):
            n += 1
        preview_filename = f"{model_name}.preview{n}{ext}"

    preview_path = os.path.join(model_dir, preview_filename)

    with open(preview_path, 'wb') as f:
        f.write(image_data)

    return {
        'status': 'success',
        'message': f'Preview image saved as {preview_filename}',
        'filename': preview_filename
    }


def delete_thumbnail(base_dir, model_name, thumbnail_index):
    """
    Delete a specific thumbnail and renumber remaining ones.
    thumbnail_index is 1-based. Supports .png, .jpg, .jpeg, .webp.
    """
    model_file = find_model_file(base_dir, model_name)
    if not model_file:
        return {'status': 'error', 'message': f'Model not found: {model_name}'}

    base_dir_path = os.path.dirname(model_file)
    target_thumb_path = _find_thumbnail_file_for_slot(base_dir_path, model_name, thumbnail_index)
    if not target_thumb_path or not os.path.exists(target_thumb_path):
        return {'status': 'error', 'message': f'Thumbnail not found for slot {thumbnail_index}'}

    os.remove(target_thumb_path)

    # Find remaining thumbnails (slots 1..10)
    remaining_thumbs = []
    for i in range(1, 11):
        if i == thumbnail_index:
            continue
        p = _find_thumbnail_file_for_slot(base_dir_path, model_name, i)
        if p and os.path.exists(p):
            ext = os.path.splitext(p)[1]
            remaining_thumbs.append((i, p, ext))

    # Renumber using temp names to avoid conflicts
    temp_renames = []
    for idx, (original_idx, file_path, ext) in enumerate(remaining_thumbs, 1):
        temp_name = f"{model_name}.preview_temp_{idx}{ext}"
        temp_path = os.path.join(base_dir_path, temp_name)
        os.rename(file_path, temp_path)
        temp_renames.append((temp_path, idx, ext))

    for temp_path, final_idx, ext in temp_renames:
        if final_idx == 1:
            final_name = f"{model_name}.preview{ext}"
        else:
            final_name = f"{model_name}.preview{final_idx}{ext}"
        final_path = os.path.join(base_dir_path, final_name)
        os.rename(temp_path, final_path)

    return {'status': 'success', 'message': 'Thumbnail deleted and renumbered'}


def reorder_thumbnails(base_dir, model_name, new_order):
    """
    Reorder thumbnails based on a new ordering array.
    new_order is a list like [2, 1, 3, 4] meaning preview2 becomes the new preview.
    Supports .png, .jpg, .jpeg, .webp.
    """
    model_file = find_model_file(base_dir, model_name)
    if not model_file:
        return {'status': 'error', 'message': 'Model file not found'}

    base_dir_path = os.path.dirname(model_file)

    # Step 1: Rename to temp names
    existing_files = []
    for orig_idx in new_order:
        file_path = _find_thumbnail_file_for_slot(base_dir_path, model_name, orig_idx)
        if file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1]
            temp_name = f"{model_name}.preview_temp_{orig_idx}{ext}"
            temp_path = os.path.join(base_dir_path, temp_name)
            os.rename(file_path, temp_path)
            existing_files.append((orig_idx, temp_path, ext))

    # Step 2: Rename to final positions
    for new_idx, (orig_idx, temp_path, ext) in enumerate(existing_files, 1):
        if new_idx == 1:
            final_name = f"{model_name}.preview{ext}"
        else:
            final_name = f"{model_name}.preview{new_idx}{ext}"

        final_path = os.path.join(base_dir_path, final_name)
        os.rename(temp_path, final_path)

    return {'status': 'success', 'message': 'Thumbnails reordered successfully'}

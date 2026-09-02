# -*- coding: UTF-8 -*-
"""
Civitai Handler Module
Handles all Civitai API interactions, file hashing, and model info management
"""

import os
import hashlib
import json
import requests
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from html import unescape
from ..constants import MODEL_EXTENSIONS

# Civitai API endpoints
CIVITAI_API_URLS = {
    "model_page": "https://civitai.com/models/",
    "model_id": "https://civitai.com/api/v1/models/",
    "model_version_id": "https://civitai.com/api/v1/model-versions/",
    "hash": "https://civitai.com/api/v1/model-versions/by-hash/"
}

# Default headers for requests (modern browser UA to prevent Cloudflare/WAF blocks)
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

DEFAULT_IMAGE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://civitai.com/',
}

_HTTP_SESSION = None

def get_http_session():
    """Get or initialize shared HTTP Session for connection pooling."""
    global _HTTP_SESSION
    if _HTTP_SESSION is None:
        _HTTP_SESSION = requests.Session()
        _HTTP_SESSION.headers.update(DEFAULT_HEADERS)
    return _HTTP_SESSION


def get_civitai_headers():
    """
    Get HTTP headers for Civitai requests, including optional API key from settings.
    """
    headers = dict(DEFAULT_HEADERS)
    try:
        from ..routes.settings import _load_settings
        settings = _load_settings()
        api_key = settings.get('civitaiApiKey', '').strip()
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
    except Exception:
        pass
    return headers


def get_image_headers():
    """
    Get HTTP headers specifically optimized for Civitai Cloudflare CDN image requests.
    """
    return dict(DEFAULT_IMAGE_HEADERS)


def get_url_variants(url, max_size=False):
    """
    Generate prioritized URL variants for Civitai images, handling Cloudflare transformations.
    """
    if not url:
        return []
    variants = []
    
    if 'image.civitai.com' in url:
        parts = url.split('/')
        # Structure: https://image.civitai.com/<account>/<uuid>/<transformation>/<filename>
        if len(parts) >= 6:
            prefix = '/'.join(parts[:5])  # https://image.civitai.com/<account>/<uuid>
            filename = parts[-1] if len(parts) > 6 else 'preview.jpeg'
            
            if max_size:
                variants.append(f"{prefix}/original=true/{filename}")
                variants.append(f"{prefix}/width=1024/{filename}")
                variants.append(url)
                variants.append(f"{prefix}/width=450/{filename}")
            else:
                variants.append(f"{prefix}/anim=false,width=450,optimized=true/{filename}")
                variants.append(f"{prefix}/width=450/{filename}")
                variants.append(f"{prefix}/original=true/{filename}")
                variants.append(url)
    
    if url not in variants:
        variants.append(url)
        
    return variants


# File extensions
INFO_EXTENSION = '.civitai.info'
PREVIEW_EXTENSION = '.preview.png'


def map_sd_version(base_model):
    if not base_model:
        return 'Unknown'
    
    if base_model == 'SD 1.5': return 'sd'
    if base_model in ['SDXL 1.0', 'Pony', 'Illustrious']: return 'xl'
    if base_model in ['Flux.1 D', 'Flux.1 S']: return 'flux'
    if base_model in ['Flux.2 Klein 9B', 'Flux.2 Klein 9B-Base', 'Flux.2 Klein 9B-base']: return 'klein'
    if base_model == 'Qwen': return 'qwen'
    if base_model in ['ZImageTurbo', 'ZImageBase']: return 'zit'
    if base_model in ['Wan Video 2.2 I2V-A14B', 'Wan Video 2.2 T2V-A14B']: return 'wan'
    if base_model == 'Anima': return 'anima'
    if base_model == 'Ernie': return 'ernie'
    if base_model == 'Krea 2': return 'krea'
    
    return 'Unknown'

def load_json_robust(file_path):
    """
    Load JSON from a file with robust encoding handling and error reporting.
    Specifically handles UTF-8 with BOM (common on Windows).
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        dict: The loaded data, or None if the file doesn't exist or is invalid.
    """
    if not os.path.exists(file_path):
        return None
        
    try:
        # Try utf-8-sig first to handle potential BOM
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error: Could not read JSON file {file_path}: {e}")
        return None


def generate_sha256(file_path, chunk_size=4*1024*1024):
    """
    Generate SHA256 hash for a file
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read (default 4MB)
        
    Returns:
        SHA256 hash as hex string, or None on error
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error generating SHA256 for {file_path}: {e}")
        return None


def save_sha256_to_json(model_path, sha256_hash):
    """
    Save SHA256 hash to the model's JSON file
    
    Args:
        model_path: Path to the model file
        sha256_hash: SHA256 hash string to save
        
    Returns:
        True on success, False on error
    """
    try:
        base_path = os.path.splitext(model_path)[0]
        json_path = f"{base_path}.json"
        
        # Load existing JSON if it exists
        existing_data = load_json_robust(json_path)
        if existing_data is None and os.path.exists(json_path):
            # If the file exists but we couldn't read it, ABORT to prevent data loss!
            print(f"CRITICAL: Failed to read existing JSON at {json_path}. Aborting update to prevent data loss.")
            return False
            
        if existing_data is None:
            existing_data = {}
            
        # Update with SHA256
        existing_data['sha256'] = sha256_hash
        
        # Write back
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4)
        
        print(f"Saved SHA256 to: {json_path}")
        return True
    except Exception as e:
        print(f"Error saving SHA256 to JSON: {e}")
        return False


def find_duplicate_models(directory):
    """
    Find duplicate models by comparing SHA256 hashes from JSON files
    
    Args:
        directory: Path to scan
        
    Returns:
        dict with:
            - duplicates: list of groups (each group is list of paths with same hash)
            - missing_hash: list of model paths without SHA256 in JSON
            - total_scanned: count of models scanned
    """
    hash_map = {}  # sha256 -> list of model paths
    missing_hash = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in MODEL_EXTENSIONS):
                    model_path = os.path.join(root, filename)
                    base_path = os.path.splitext(model_path)[0]
                    json_path = f"{base_path}.json"
                    
                    json_data = load_json_robust(json_path)
                    if json_data:
                        sha256 = json_data.get('sha256')
                        if sha256:
                            if sha256 not in hash_map:
                                hash_map[sha256] = []
                            hash_map[sha256].append(model_path)
                        else:
                            missing_hash.append(model_path)
                    else:
                        missing_hash.append(model_path)
    except Exception as e:
        print(f"Error scanning for duplicates: {e}")
    
    # Find groups with more than one file (duplicates)
    duplicates = [paths for paths in hash_map.values() if len(paths) > 1]
    
    return {
        'duplicates': duplicates,
        'missing_hash': missing_hash,
        'total_scanned': sum(len(paths) for paths in hash_map.values()) + len(missing_hash)
    }


def fetch_model_info_by_hash(file_hash):
    """
    Fetch model info from Civitai using SHA256 hash
    
    Args:
        file_hash: SHA256 hash of the model file
        
    Returns:
        Model info dict, or None on error
    """
    try:
        url = f"{CIVITAI_API_URLS['hash']}{file_hash}"
        response = requests.get(url, headers=get_civitai_headers(), timeout=10)
        
        if response.status_code == 404:
            print(f"Model not found on Civitai for hash: {file_hash}")
            return {}
        elif not response.ok:
            print(f"Civitai API error {response.status_code}: {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Error fetching model info: {e}")
        return None

def _parse_civarchive_html(html):
    """Helper to parse __NEXT_DATA__ and map CivArchive to Civitai API format"""
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not match:
        print("Could not find __NEXT_DATA__ in CivArchive response")
        return None
        
    next_data = json.loads(match.group(1))
    
    try:
        page_props = next_data['props']['pageProps']
        if 'model' in page_props:
            raw_model = page_props['model']
        elif 'models' in page_props and isinstance(page_props['models'], list) and len(page_props['models']) > 0:
            raw_model = page_props['models'][0]
        else:
            raise KeyError("Neither 'model' nor 'models' found")
            
        raw_version = raw_model.get('version', {})
    except (KeyError, TypeError) as e:
        print(f"Could not find model/version in CivArchive JSON: {e}")
        return {}
        
    root_download_url = raw_version.get('download_url', '')
    if root_download_url.startswith('/'):
        root_download_url = f"https://civitaiarchive.com{root_download_url}"
        
    # Map to Civitai API format expected by create_json_from_api_data
    model_data = {
        'id': raw_version.get('id', raw_version.get('civitai_model_version_id')),
        'modelId': raw_model.get('id', raw_version.get('civitai_model_id')),
        'name': raw_version.get('name'),
        'creator': {
            'username': raw_model.get('creator_username') or raw_model.get('username') or 'Unknown'
        },
        'description': raw_version.get('description', raw_model.get('description', '')),
        'baseModel': raw_version.get('base_model', 'Unknown'),
        'baseModelType': raw_version.get('base_model_type', ''),
        'publishedAt': raw_version.get('created_at', raw_model.get('created_at', '')),
        'downloadUrl': root_download_url,
        'isCivArchive': True,
        'model': {
            'name': raw_model.get('name', ''),
            'type': raw_model.get('type', ''),
            'nsfw': raw_model.get('is_nsfw', False)
        },
        'trainedWords': [],
        'files': [],
        'images': []
    }
    
    # Map images
    if 'images' in raw_version and raw_version['images']:
        for img in raw_version['images']:
            # Prioritize image_url over link (which often points to HTML pages)
            img_url = img.get('image_url', img.get('url', img.get('link', '')))
            if img_url.startswith('/'):
                img_url = f"https://civitaiarchive.com{img_url}"
                
            meta = {}
            if img.get('meta'):
                meta = img['meta']
                
            model_data['images'].append({
                'url': img_url,
                'nsfwLevel': img.get('nsfwLevel', 1),
                'width': img.get('width', 0),
                'height': img.get('height', 0),
                'meta': meta
            })
            
    if raw_version.get('trigger'):
        trigger = raw_version.get('trigger')
        if isinstance(trigger, list):
            model_data['trainedWords'] = trigger
        elif isinstance(trigger, str):
            model_data['trainedWords'] = trigger.split(', ')
        
    if 'files' in raw_version and raw_version['files']:
        for f in raw_version['files']:
            file_url = f.get('download_url', '')
            if file_url.startswith('/'):
                file_url = f"https://civitaiarchive.com{file_url}"
            
            model_data['files'].append({
                'id': f.get('id'),
                'name': f.get('name', f.get('filename', '')),
                'downloadUrl': file_url,
                'hashes': { 'SHA256': f.get('sha256', '') } if f.get('sha256') else {}
            })
                
    return model_data


def scrape_civarchive_by_hash(file_hash):
    """
    Fetch model info from CivArchive using SHA256 hash
    
    Args:
        file_hash: SHA256 hash of the model file
        
    Returns:
        Model info dict (in Civitai API format), or None on error
    """
    try:
        url = f"https://civitaiarchive.com/sha256/{file_hash}"
        print(f"Fetching from CivArchive: {url}")
        response = requests.get(url, headers=get_civitai_headers(), timeout=10, allow_redirects=True)
        
        if response.status_code == 404:
            print(f"Model not found on CivArchive for hash: {file_hash}")
            return {}
        elif not response.ok:
            print(f"CivArchive error {response.status_code}: {response.text}")
            return None
            
        return _parse_civarchive_html(response.text)
    except Exception as e:
        print(f"Error fetching model info from CivArchive: {e}")
        return None


def scrape_civarchive_by_url(url):
    """
    Fetch model info from CivArchive using a direct URL
    
    Args:
        url: CivArchive URL (e.g. https://civarchive.com/models/...)
        
    Returns:
        Model info dict (in Civitai API format), or None on error
    """
    try:
        print(f"Fetching from CivArchive URL: {url}")
        response = requests.get(url, headers=get_civitai_headers(), timeout=10)
        
        if response.status_code == 404:
            print(f"Model not found on CivArchive for URL: {url}")
            return {}
        elif not response.ok:
            print(f"CivArchive error {response.status_code}: {response.text}")
            return None
            
        return _parse_civarchive_html(response.text)
    except Exception as e:
        print(f"Error fetching model info from CivArchive URL: {e}")
        return None


def fetch_model_info_by_id(model_id):
    """
    Fetch model info from Civitai using model ID
    
    Args:
        model_id: Civitai model ID
        
    Returns:
        Model info dict, or None on error
    """
    try:
        url = f"{CIVITAI_API_URLS['model_id']}{model_id}"
        response = requests.get(url, headers=get_civitai_headers(), timeout=10)
        
        if not response.ok:
            print(f"Civitai API error {response.status_code}: {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Error fetching model info by ID: {e}")
        return None


def fetch_model_info_by_version_id(version_id):
    """
    Fetch model version info from Civitai using version ID
    
    Args:
        version_id: Civitai model version ID
        
    Returns:
        Model version info dict (same format as hash lookup), or None on error
    """
    try:
        url = f"{CIVITAI_API_URLS['model_version_id']}{version_id}"
        print(f"Fetching model version from: {url}")
        response = requests.get(url, headers=get_civitai_headers(), timeout=10)
        
        if response.status_code == 404:
            print(f"Model version not found on Civitai: {version_id}")
            return {}
        elif not response.ok:
            print(f"Civitai API error {response.status_code}: {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Error fetching model info by version ID: {e}")
        return None


def parse_civitai_url(url):
    """
    Parse Civitai URL to extract model ID and version ID
    
    Supports URLs like:
    - https://civitai.com/models/402800?modelVersionId=1473181
    - https://civitai.com/models/402800/model-name?modelVersionId=1473181
    - https://civitai.com/models/402800
    
    Args:
        url: Civitai URL string
        
    Returns:
        tuple: (model_id, version_id) - version_id may be None
    """
    if not url:
        return (None, None)
    
    model_id = None
    version_id = None
    
    try:
        # Extract modelVersionId from query params
        if 'modelVersionId=' in url:
            match = re.search(r'modelVersionId=(\d+)', url)
            if match:
                version_id = match.group(1)
        
        # Extract model ID from path
        # Pattern: /models/{id} or /models/{id}/slug
        match = re.search(r'/models/(\d+)', url)
        if match:
            model_id = match.group(1)
            
    except Exception as e:
        print(f"Error parsing Civitai URL: {e}")
    
    return (model_id, version_id)


def strip_html_tags(text):
    """
    Remove HTML tags from text using regular expressions
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', text)


def get_creator_from_api(model_id, use_api=True):
    """
    Fetch creator information from Civitai API using model ID
    """
    if not use_api:
        return ''
    try:
        api_url = f"https://civitai.com/api/v1/models/{model_id}"
        response = requests.get(api_url, headers=get_civitai_headers(), timeout=10)
        if response.status_code == 200:
            model_data = response.json()
            if 'creator' in model_data and 'username' in model_data['creator']:
                return model_data['creator']['username']
        return 'Unknown'
    except Exception as e:
        print(f"Error fetching creator information: {e}")
        return 'Unknown'


def create_json_from_api_data(model_path, api_data, use_api_for_creator=True, existing_creator=''):
    """
    Create a .json file directly from Civitai API response data.
    This replaces the old two-step process of saving .civitai.info then converting.
    
    Args:
        model_path: Path to the model file
        api_data: Dict from Civitai API response
        use_api_for_creator: Whether to make API call for creator info
        existing_creator: Existing creator name to preserve
        
    Returns:
        True on success, False on error
    """
    try:
        base_path = os.path.splitext(model_path)[0]
        json_path = f"{base_path}.json"
        
        # Fast path for ignored models (dummy URL)
        if api_data.get("ignored"):
            existing_data = load_json_robust(json_path) or {}
            if 'web_civitai_data' not in existing_data:
                existing_data['web_civitai_data'] = {}
            existing_data['web_civitai_data']['url'] = api_data.get("url", "https://no-match.com/ignored")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4)
            return True
        
        # Initialize all fields with empty values (same structure as existing JSONs)
        mapped_data = {
            'activation text': '',
            'base model': '',
            'baseModel': '',
            'base_model_type': '',
            'category': '',
            'description': '',
            'example prompt 1': '',
            'example prompt 2': '',
            'folder': '',
            'high low': '',
            'model version': '',
            'model_type': '',
            'name': '',
            'negative text': '',
            'notes': '',
            'nsfw': '',
            'preferred weight': 0,
            'sd version': '',
            'sha256': '',
            'subcategory': '',
            'tags': '',
            'web_civitai_data': {
                'civitai name': '',
                'civitai text': '',
                'creator': '',
                'downloadUrl': '',
                'file_id': '',
                'model_id': '',
                'original_filename': '',
                'preview_image_1': '',
                'preview_image_2': '',
                'published_date': '',
                'url': ''
            }
        }
        
        # --- Extract data from API response ---
        
        # Trained words / activation text
        if 'trainedWords' in api_data:
            trained_words = api_data['trainedWords']
            if isinstance(trained_words, list) and trained_words:
                mapped_data['activation text'] = trained_words[0]
                mapped_data['web_civitai_data']['civitai text'] = ', '.join(trained_words)
        
        # Base model
        api_base_model = api_data.get('baseModel') or api_data.get('base_model')
        if api_base_model:
            mapped_data['base model'] = api_base_model
            mapped_data['baseModel'] = api_base_model
            mapped_data['sd version'] = map_sd_version(api_base_model)
        
        # Base model type (NEW)
        if 'baseModelType' in api_data:
            mapped_data['base_model_type'] = api_data['baseModelType']
        
        # Model info (name, nsfw, type)
        if 'model' in api_data:
            if 'name' in api_data['model']:
                mapped_data['web_civitai_data']['civitai name'] = api_data['model']['name']
                mapped_data['name'] = api_data['model']['name']
            if 'nsfw' in api_data['model']:
                mapped_data['nsfw'] = str(api_data['model']['nsfw']).lower()
            # Model type (NEW)
            if 'type' in api_data['model']:
                mapped_data['model_type'] = api_data['model']['type']
        
        # Model ID and File/Version ID (NEW)
        if 'modelId' in api_data:
            mapped_data['web_civitai_data']['model_id'] = api_data['modelId']
        if 'id' in api_data:
            mapped_data['web_civitai_data']['file_id'] = api_data['id']
        
        # Published date (NEW)
        if 'publishedAt' in api_data:
            mapped_data['web_civitai_data']['published_date'] = api_data['publishedAt']
        
        # Files info: original filename, download URL (NEW)
        if 'files' in api_data and isinstance(api_data['files'], list) and api_data['files']:
            first_file = api_data['files'][0]
            if 'name' in first_file:
                mapped_data['web_civitai_data']['original_filename'] = first_file['name']
            if 'downloadUrl' in first_file:
                mapped_data['web_civitai_data']['downloadUrl'] = first_file['downloadUrl']
            # Also get SHA256 from file hashes if available
            if 'hashes' in first_file and 'SHA256' in first_file['hashes']:
                mapped_data['sha256'] = first_file['hashes']['SHA256'].lower()
        
        # Root-level download URL fallback
        if not mapped_data['web_civitai_data']['downloadUrl'] and 'downloadUrl' in api_data:
            mapped_data['web_civitai_data']['downloadUrl'] = api_data['downloadUrl']
        
        # Process description for notes field
        description = ''
        if 'description' in api_data and api_data['description']:
            description = api_data['description']
            description = unescape(description)
            description = strip_html_tags(description)
            description = ' '.join(description.split())
        
        # Extract example prompts and preview image URLs from images
        if 'images' in api_data:
            images = api_data['images']
            if isinstance(images, list) and images:
                # Save full image URLs list in web_civitai_data for fallback resolution
                mapped_data['web_civitai_data']['images'] = [
                    img.get('url') for img in images if isinstance(img, dict) and img.get('url')
                ]
                
                # Separate static images vs video to prioritize clean static preview images
                static_images = [
                    img for img in images 
                    if isinstance(img, dict) and img.get('url') and not (
                        '.mp4' in img.get('url', '').lower() or 
                        '.webm' in img.get('url', '').lower() or 
                        img.get('type') == 'video'
                    )
                ]
                candidate_pool = static_images if static_images else images
                
                # First image: example prompt + preview URL
                first_image = candidate_pool[0]
                if 'meta' in first_image and isinstance(first_image['meta'], dict):
                    if 'prompt' in first_image['meta']:
                        mapped_data['example prompt 1'] = first_image['meta']['prompt']
                    if 'negativePrompt' in first_image['meta']:
                        mapped_data['negative text'] = first_image['meta']['negativePrompt']
                if 'url' in first_image:
                    mapped_data['web_civitai_data']['preview_image_1'] = first_image['url']
                
                # Second image: example prompt 2 + preview URL
                if len(candidate_pool) > 1:
                    second_image = candidate_pool[1]
                    if 'meta' in second_image and isinstance(second_image['meta'], dict):
                        if 'prompt' in second_image['meta']:
                            mapped_data['example prompt 2'] = second_image['meta']['prompt']
                    if 'url' in second_image:
                        mapped_data['web_civitai_data']['preview_image_2'] = second_image['url']
        
        # Build URL and notes
        wcd = mapped_data['web_civitai_data']
        if wcd['model_id'] and wcd['file_id']:
            if api_data.get('isCivArchive'):
                url = f"https://civitaiarchive.com/models/{wcd['model_id']}?modelVersionId={wcd['file_id']}"
            else:
                url = f"https://civitai.com/models/{wcd['model_id']}?modelVersionId={wcd['file_id']}"
            wcd['url'] = url
            
            # Get creator
            if existing_creator:
                wcd['creator'] = existing_creator
            elif use_api_for_creator:
                creator = get_creator_from_api(wcd['model_id'], use_api_for_creator)
                if creator:
                    wcd['creator'] = creator
            
            # Construct notes field
            notes = [f"URL: {url}"]
            if 'baseModel' in api_data:
                notes.append(f"Base Model: {api_data['baseModel']}")
            if 'trainedWords' in api_data and api_data['trainedWords']:
                notes.append(f"Activation Words: {', '.join(api_data['trainedWords'])}")
            if description:
                notes.append(f"Description: {description}")
            mapped_data['notes'] = '\n'.join(notes)
        
 
        # --- Merge with existing JSON data (preserve user-edited fields) ---
        existing_data = load_json_robust(json_path)
        if existing_data:
            try:
                # Fields to preserve if already populated by user (note: 'base model' is NOT protected so Civitai can populate it)
                fields_to_preserve = [
                    'activation text', 'preferred weight',
                    'negative text',
                    'nsfw', 'example prompt 1',
                    'category', 'subcategory', 'tags',
                    'name', 'model version', 'high low',
                    'sha256', 'folder', 'description'
                ]
                for field in fields_to_preserve:
                    if field in existing_data and existing_data[field] is not None and existing_data[field] != '':
                        mapped_data[field] = existing_data[field]
                
                # If API didn't provide a base model, fall back to existing if available
                if not mapped_data.get('base model') or mapped_data.get('base model') == 'Unknown':
                    existing_bm = existing_data.get('base model') or existing_data.get('baseModel')
                    if existing_bm and existing_bm != 'Unknown':
                        mapped_data['base model'] = existing_bm
                        mapped_data['baseModel'] = existing_bm
                        if not mapped_data.get('sd version') or mapped_data.get('sd version') == 'Unknown':
                            mapped_data['sd version'] = map_sd_version(existing_bm)

                # For sd version: if not mapped or Unknown, preserve existing if valid
                if not mapped_data.get('sd version') or mapped_data.get('sd version') == 'Unknown':
                    existing_sd = existing_data.get('sd version')
                    if existing_sd and existing_sd != 'Unknown':
                        mapped_data['sd version'] = existing_sd

                # Preserve web_civitai_data sub-fields if they exist in old format
                # (migrate from old flat format to nested)
                existing_wcd = existing_data.get('web_civitai_data', {})
                wcd_fields_to_preserve = ['civitai text', 'url', 'creator']
                for field in wcd_fields_to_preserve:
                    # Check nested location first
                    if field in existing_wcd and existing_wcd[field]:
                        mapped_data['web_civitai_data'][field] = existing_wcd[field]
                    # Fallback: check old flat location
                    elif field in existing_data and existing_data[field] is not None and existing_data[field] != '':
                        mapped_data['web_civitai_data'][field] = existing_data[field]
                
                # Also preserve any extra fields in existing JSON not in our template
                fields_to_ignore = {'creator', 'original_filename', 'downloadUrl', 'z_info_file', 'baseModel'}
                for key, value in existing_data.items():
                    if key not in mapped_data and key not in fields_to_ignore:
                        mapped_data[key] = value
                        
            except Exception as e:
                print(f"Error merging existing JSON data: {e}")
        elif os.path.exists(json_path):
            print(f"WARNING: Could not read existing JSON for merging at {json_path}. Proceeding with new data only.")
        
        # Ensure both 'base model' and 'baseModel' are in sync
        if mapped_data.get('base model'):
            mapped_data['baseModel'] = mapped_data['base model']
        elif mapped_data.get('baseModel'):
            mapped_data['base model'] = mapped_data['baseModel']
        
        # --- Write sorted JSON ---
        sorted_data = {k: mapped_data[k] for k in sorted(mapped_data.keys())}
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_data, f, indent=4)
        
        print(f"Created JSON directly from API data: {json_path}")
        return True
        
    except Exception as e:
        print(f"Error creating JSON from API data: {e}")
        return False


def save_civitai_info(model_path, model_info):
    """
    Save model info directly as .json file (no longer creates .civitai.info).
    This is the main entry point called by the server routes.
    
    Args:
        model_path: Path to the model file
        model_info: Model info dict from Civitai API
        
    Returns:
        True on success, False on error
    """
    return create_json_from_api_data(model_path, model_info)


def create_dummy_info_file(model_path):
    """
    Create a minimal .json file to mark model as already checked but not found on Civitai.
    No longer creates .civitai.info files.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        True on success, False on error
    """
    try:
        base_path = os.path.splitext(model_path)[0]
        json_path = f"{base_path}.json"
        
        # Load existing JSON if it exists to preserve data
        existing_data = load_json_robust(json_path)
        if existing_data is None and os.path.exists(json_path):
            # If the file exists but we couldn't read it, ABORT to prevent data loss!
            print(f"CRITICAL: Failed to read existing JSON at {json_path}. Aborting dummy creation to prevent data loss.")
            return False
            
        if existing_data is None:
            existing_data = {}
        
        # Mark as checked but not found
        existing_data['civitai_matched'] = False
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4)
        
        print(f"Created dummy JSON marker: {json_path}")
        return True
    except Exception as e:
        print(f"Error creating dummy JSON: {e}")
        return False


def get_full_size_image_url(image_url, width=None):
    """
    Convert Civitai image URL to full size version or specific width
    """
    if not image_url:
        return ''
    if 'image.civitai.com' in image_url:
        parts = image_url.split('/')
        if len(parts) >= 6:
            prefix = '/'.join(parts[:5])
            filename = parts[-1] if len(parts) > 6 else 'preview.jpeg'
            if width:
                return f"{prefix}/width={width}/{filename}"
            return f"{prefix}/original=true/{filename}"
    return re.sub(r'/width=\d+/', f'/width={width}/' if width else '/original=true/', image_url)


def check_ffmpeg_available():
    """
    Check if FFmpeg is available on the system
    
    Returns:
        True if FFmpeg is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def extract_video_frames(video_path, output_base_path):
    """
    Extract first and last frames from video using FFmpeg
    
    Args:
        video_path: Path to the video file
        output_base_path: Base path for output files (without extension)
        
    Returns:
        tuple: (success, message)
    """
    if not check_ffmpeg_available():
        return (False, "FFmpeg not available on system")
    
    try:
        preview_path = f"{output_base_path}{PREVIEW_EXTENSION}"
        preview2_path = f"{output_base_path}.preview2.png"
        
        # Extract first frame using select filter (as in the standalone version)
        first_frame_cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', 'select=eq(n\\,0)',
            '-vframes', '1',
            '-q:v', '2',
            preview_path
        ]
        
        print(f"Executing: {' '.join(first_frame_cmd)}")
        result = subprocess.run(
            first_frame_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode()
            print(f"FFmpeg error extracting first frame: {error_msg}")
            return (False, f"FFmpeg error extracting first frame: {error_msg[:200]}")
        
        # Extract last frame using reverse filter (proven method from standalone version)
        last_frame_cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', 'reverse',
            '-vframes', '1',
            '-q:v', '2',
            preview2_path
        ]
        
        print(f"Executing: {' '.join(last_frame_cmd)}")
        result = subprocess.run(
            last_frame_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode()
            print(f"FFmpeg error extracting last frame: {error_msg}")
            
            # Fallback: Just try to get one frame normally for the second slot if reverse fails
            fallback_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                preview2_path
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            return (True, "Extracted first frame (last frame fallback used)")
        
        return (True, "Extracted first and last frames")
        
    except subprocess.TimeoutExpired:
        return (False, "FFmpeg timeout - video too long or complex")
    except Exception as e:
        return (False, f"Error extracting frames: {str(e)}")


def _save_pil_image(image_bytes, target_path):
    """
    Safely open and convert image bytes to standard RGB PNG and save to target_path.
    If PIL is not available or fails, falls back to directly writing raw image bytes.
    """
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes))
        # Handle different modes
        if img.mode in ('RGBA', 'P', 'LA'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                bg.paste(img, mask=img.split()[-1])
                img = bg
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(target_path, format='PNG')
        return True
    except ImportError:
        # Fallback if Pillow is not installed
        try:
            with open(target_path, 'wb') as f:
                f.write(image_bytes)
            print(f"Saved raw image bytes to {target_path} (Pillow not installed)")
            return True
        except Exception as e:
            print(f"Error saving raw image bytes to {target_path}: {e}")
            return False
    except Exception as e:
        # Fallback if image conversion fails
        try:
            with open(target_path, 'wb') as f:
                f.write(image_bytes)
            print(f"Saved raw image bytes fallback to {target_path}: {e}")
            return True
        except Exception as ex:
            print(f"Error writing image fallback to {target_path}: {ex}")
            return False


def download_preview_image(model_path, max_size=False, skip_nsfw=False, force_additional=False):
    """
    Download preview image for a model.
    Reads image URLs from the model's .json file, with automatic fallback to
    querying Civitai API or CivArchive if URLs are missing or returning 404.
    
    Args:
        model_path: Path to the model file
        max_size: Download full size image if True
        skip_nsfw: Skip NSFW images if True
        force_additional: If True, try to download additional images even if some exist
        
    Returns:
        True on success, False on error or skip
    """
    try:
        base_path = os.path.splitext(model_path)[0]
        info_path = f"{base_path}{INFO_EXTENSION}"
        json_path = f"{base_path}.json"
        
        # Check which preview slots are available across all formats (.png, .jpg, .jpeg, .webp)
        exts = ('.png', '.jpg', '.jpeg', '.webp')
        existing_p1 = None
        for ext in exts:
            p = f"{base_path}.preview{ext}"
            if os.path.exists(p):
                existing_p1 = p
                break
        if not existing_p1:
            for ext in exts:
                p = f"{base_path}{ext}"
                if os.path.exists(p):
                    existing_p1 = p
                    break

        existing_p2 = None
        for ext in exts:
            p = f"{base_path}.preview2{ext}"
            if os.path.exists(p):
                existing_p2 = p
                break

        has_preview1 = bool(existing_p1)
        has_preview2 = bool(existing_p2)
        preview_path = existing_p1 if existing_p1 else f"{base_path}.preview.png"
        preview2_path = existing_p2 if existing_p2 else f"{base_path}.preview2.png"
        
        # In normal mode, if both slots exist, we're done
        if not force_additional and has_preview1 and has_preview2:
            print(f"All preview slots filled: {existing_p1}")
            return True
            
        if not force_additional and has_preview1 and not os.path.exists(json_path) and not os.path.exists(info_path):
            print(f"Preview exists: {existing_p1}")
            return True

        # --- Collect candidate items from local files ---
        candidate_items = []
        json_data = None
        
        if os.path.exists(json_path):
            try:
                json_data = load_json_robust(json_path) or {}
                wcd = json_data.get('web_civitai_data', {})
                
                # Check preview_image fields
                img1 = wcd.get('preview_image_1') or json_data.get('preview_image_1', '')
                img2 = wcd.get('preview_image_2') or json_data.get('preview_image_2', '')
                if img1:
                    candidate_items.append({'url': img1, 'type': 'video' if ('.mp4' in img1.lower() or '.webm' in img1.lower()) else 'image', 'nsfwLevel': 1})
                if img2:
                    candidate_items.append({'url': img2, 'type': 'video' if ('.mp4' in img2.lower() or '.webm' in img2.lower()) else 'image', 'nsfwLevel': 1})
                    
                # Check images list in web_civitai_data
                wcd_images = wcd.get('images', [])
                if isinstance(wcd_images, list):
                    for img in wcd_images:
                        if isinstance(img, str) and img and not any(c.get('url') == img for c in candidate_items):
                            candidate_items.append({'url': img, 'type': 'video' if ('.mp4' in img.lower() or '.webm' in img.lower()) else 'image', 'nsfwLevel': 1})
                        elif isinstance(img, dict) and img.get('url') and not any(c.get('url') == img.get('url') for c in candidate_items):
                            candidate_items.append(img)
                
                # Check z_info_file
                z_info = json_data.get('z_info_file', {})
                if isinstance(z_info.get('images'), list):
                    for img in z_info['images']:
                        if isinstance(img, dict) and img.get('url') and not any(c.get('url') == img.get('url') for c in candidate_items):
                            candidate_items.append(img)
            except Exception as e:
                print(f"Error reading JSON for candidate images: {e}")
                
        if not candidate_items and os.path.exists(info_path):
            try:
                info_data = load_json_robust(info_path) or {}
                if isinstance(info_data.get('images'), list):
                    for img in info_data['images']:
                        if isinstance(img, dict) and img.get('url'):
                            candidate_items.append(img)
            except Exception as e:
                print(f"Error reading info file for candidate images: {e}")

        # Helper to attempt downloading from a list of candidate items
        def _try_download_from_candidates(candidates):
            downloaded = 0
            need_p1 = not has_preview1 or force_additional
            need_p2 = not has_preview2 or force_additional
            
            # Filter candidates based on NSFW setting
            usable_candidates = []
            for item in candidates:
                if not item:
                    continue
                if isinstance(item, str):
                    usable_candidates.append({'url': item, 'type': 'video' if ('.mp4' in item.lower() or '.webm' in item.lower()) else 'image', 'nsfwLevel': 1})
                elif isinstance(item, dict):
                    if skip_nsfw:
                        # Skip if marked NSFW (Civitai nsfwLevel: 1=PG, >1 is NSFW, or nsfw: True/'true')
                        nsfw_level = item.get('nsfwLevel', 1)
                        is_nsfw = item.get('nsfw')
                        if (isinstance(nsfw_level, (int, float)) and nsfw_level > 1) or (is_nsfw and str(is_nsfw).lower() not in ('false', 'none', '0')):
                            continue
                    usable_candidates.append(item)
            
            # Separate static images vs videos
            static_candidates = [c for c in usable_candidates if c.get('type') != 'video' and not ('.mp4' in c.get('url', '').lower() or '.webm' in c.get('url', '').lower())]
            video_candidates = [c for c in usable_candidates if c.get('type') == 'video' or ('.mp4' in c.get('url', '').lower() or '.webm' in c.get('url', '').lower())]
            
            # 1. Try static images first
            candidate_idx = 0
            session = get_http_session()
            img_headers = get_image_headers()
            
            if need_p1:
                while candidate_idx < len(static_candidates):
                    item = static_candidates[candidate_idx]
                    candidate_idx += 1
                    raw_url = item.get('url')
                    if not raw_url:
                        continue
                    
                    variants = get_url_variants(raw_url, max_size)
                    saved = False
                    for v_url in variants:
                        try:
                            resp = session.get(v_url, headers=img_headers, timeout=5)
                            if resp.ok and resp.content and _save_pil_image(resp.content, preview_path):
                                print(f"Downloaded preview 1: {preview_path} (from {v_url})")
                                downloaded += 1
                                need_p1 = False
                                saved = True
                                break
                            else:
                                status = resp.status_code if resp is not None else 'no response'
                                print(f"Preview 1 fetch failed for {v_url}: status={status}")
                        except Exception as e:
                            print(f"Exception on preview 1 {v_url}: {e}")
                    if saved:
                        break
                        
            if need_p2:
                while candidate_idx < len(static_candidates):
                    item = static_candidates[candidate_idx]
                    candidate_idx += 1
                    raw_url = item.get('url')
                    if not raw_url:
                        continue
                    
                    variants = get_url_variants(raw_url, max_size)
                    saved = False
                    for v_url in variants:
                        try:
                            resp = session.get(v_url, headers=img_headers, timeout=5)
                            if resp.ok and resp.content and _save_pil_image(resp.content, preview2_path):
                                print(f"Downloaded preview 2: {preview2_path} (from {v_url})")
                                downloaded += 1
                                need_p2 = False
                                saved = True
                                break
                            else:
                                status = resp.status_code if resp is not None else 'no response'
                                print(f"Preview 2 fetch failed for {v_url}: status={status}")
                        except Exception as e:
                            print(f"Exception on preview 2 {v_url}: {e}")
                    if saved:
                        break
            
            # 2. If slots still needed, try video frame extraction with FFmpeg
            if (need_p1 or need_p2) and video_candidates and check_ffmpeg_available():
                for v_item in video_candidates:
                    v_url = v_item.get('url')
                    if not v_url:
                        continue
                    try:
                        v_resp = requests.get(v_url, headers=get_civitai_headers(), timeout=60, stream=True)
                        if v_resp.ok:
                            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_video:
                                for chunk in v_resp.iter_content(chunk_size=8192):
                                    tmp_video.write(chunk)
                                tmp_video_path = tmp_video.name
                            
                            success, msg = extract_video_frames(tmp_video_path, base_path)
                            try:
                                os.unlink(tmp_video_path)
                            except Exception:
                                pass
                                
                            if success:
                                print(f"Extracted frames from video: {msg}")
                                downloaded += 1
                                break
                    except Exception as v_err:
                        print(f"Error downloading/extracting video preview: {v_err}")
                        
            return downloaded

        # Attempt downloading with existing candidates
        initial_downloaded = 0
        if candidate_items:
            initial_downloaded = _try_download_from_candidates(candidate_items)
            if not force_additional and os.path.exists(preview_path) and os.path.exists(preview2_path):
                return True
            if not force_additional and os.path.exists(preview_path) and len(candidate_items) == 1:
                return True
            if initial_downloaded > 0 and os.path.exists(preview_path):
                return True

        # --- Dynamic Civitai / CivArchive Lookup Fallback ---
        # If no candidates existed OR initial download failed (e.g. 404 URLs), look up online!
        print(f"Querying Civitai/CivArchive online for fresh metadata & thumbnail URLs for {os.path.basename(model_path)}...")
        
        fresh_api_data = None
        
        # 1. Try version_id / model_id if available in JSON
        if json_data:
            wcd = json_data.get('web_civitai_data', {})
            version_id = wcd.get('file_id') or json_data.get('file_id')
            model_id = wcd.get('model_id') or json_data.get('model_id')
            civitai_url = wcd.get('url') or json_data.get('url')
            
            if version_id:
                fresh_api_data = fetch_model_info_by_version_id(version_id)
            if not fresh_api_data and civitai_url and ('civitai.com' in civitai_url or 'civarchive' in civitai_url):
                m_id, v_id = parse_civitai_url(civitai_url)
                if v_id:
                    fresh_api_data = fetch_model_info_by_version_id(v_id)
                elif m_id:
                    fresh_api_data = fetch_model_info_by_id(m_id)
                    if fresh_api_data and 'modelVersions' in fresh_api_data and fresh_api_data['modelVersions']:
                        fresh_api_data = fresh_api_data['modelVersions'][0]
            if not fresh_api_data and model_id:
                m_data = fetch_model_info_by_id(model_id)
                if m_data and 'modelVersions' in m_data and m_data['modelVersions']:
                    fresh_api_data = m_data['modelVersions'][0]
        
        # 2. Try SHA256 hash lookup
        if not fresh_api_data:
            sha256 = None
            if json_data:
                sha256 = json_data.get('sha256')
            if not sha256 and os.path.exists(model_path):
                print(f"Computing SHA256 for {os.path.basename(model_path)}...")
                sha256 = generate_sha256(model_path)
                if sha256:
                    save_sha256_to_json(model_path, sha256)
            
            if sha256:
                fresh_api_data = fetch_model_info_by_hash(sha256)
                if not fresh_api_data:
                    fresh_api_data = scrape_civarchive_by_hash(sha256)

        # 3. If fresh data retrieved, update JSON and download candidates
        if fresh_api_data and isinstance(fresh_api_data, dict) and 'images' in fresh_api_data:
            create_json_from_api_data(model_path, fresh_api_data)
            fresh_candidates = fresh_api_data.get('images', [])
            if fresh_candidates:
                downloaded_fresh = _try_download_from_candidates(fresh_candidates)
                if downloaded_fresh > 0 or os.path.exists(preview_path):
                    return True
                    
        # Check final status
        if os.path.exists(preview_path):
            return True
            
        print(f"No suitable preview thumbnail could be downloaded for: {model_path}")
        return False
        
    except Exception as e:
        print(f"Error downloading preview for {model_path}: {e}")
        return False


def scan_models_directory(directory):
    """
    Scan directory for model files and check for civitai info
    
    Args:
        directory: Path to scan
        
    Returns:
        List of dicts with model info: {path, name, has_info, has_preview, has_json, has_hash}
    """
    models = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                # Check if file is a model
                if any(filename.lower().endswith(ext) for ext in MODEL_EXTENSIONS):
                    file_path = os.path.join(root, filename)
                    base_path = os.path.splitext(file_path)[0]
                    json_path = f"{base_path}.json"
                    
                    # Check if hash exists in JSON and if model has civitai data
                    json_data = load_json_robust(json_path)
                    has_hash = False
                    has_civitai_data = False
                    
                    if json_data:
                        has_hash = bool(json_data.get('sha256'))
                        # Model has civitai data if it has z_info_file, web_civitai_data, or civitai_matched marker
                        has_civitai_data = bool(
                            json_data.get('z_info_file') or 
                            json_data.get('web_civitai_data', {}).get('model_id') or
                            json_data.get('model_id') or  # legacy flat format
                            json_data.get('civitai_matched') is not None
                        )
                    
                    model_data = {
                        'path': file_path,
                        'name': filename,
                        'has_info': has_civitai_data or os.path.exists(f"{base_path}{INFO_EXTENSION}"),
                        'has_preview': os.path.exists(f"{base_path}{PREVIEW_EXTENSION}"),
                        'has_json': os.path.exists(json_path),
                        'has_hash': has_hash
                    }
                    models.append(model_data)
    except Exception as e:
        print(f"Error scanning directory: {e}")
    
    return models


def get_model_id_from_url(url_or_id):
    """
    Extract model ID from Civitai URL or return ID if already numeric
    
    Args:
        url_or_id: Civitai URL or model ID
        
    Returns:
        Model ID as string, or empty string on error
    """
    if not url_or_id:
        return ""
    
    # Check if already numeric
    if str(url_or_id).isnumeric():
        return str(url_or_id)
    
    # Try to extract from URL
    # Remove query parameters and split by /
    parts = re.sub(r'\?.+$', '', url_or_id).split('/')
    
    if len(parts) < 2:
        return ""
    
    # Check last two parts for numeric ID
    if parts[-2].isnumeric():
        return parts[-2]
    elif parts[-1].isnumeric():
        return parts[-1]
    
    return ""


def fix_thumbnail_name(model_path):
    """
    Rename adjacent image files to .preview.png format
    
    Args:
        model_path: Path to the model file
        
    Returns:
        tuple: (status, message) where status is 'success', 'skipped', or 'error'
    """
    try:
        base_path = os.path.splitext(model_path)[0]
        model_dir = os.path.dirname(model_path)
        model_basename = os.path.basename(base_path)
        target_preview = f"{base_path}{PREVIEW_EXTENSION}"
        
        # If .preview.png already exists, skip
        if os.path.exists(target_preview):
            return ('skipped', 'Already has .preview.png')
        
        # Look for image files with the same base name
        image_extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
        
        for ext in image_extensions:
            potential_image = f"{base_path}{ext}"
            if os.path.exists(potential_image):
                # Found an image file, rename it
                os.rename(potential_image, target_preview)
                return ('success', f'Renamed {model_basename}{ext} to {model_basename}.preview.png')
        
        # No image file found
        return ('skipped', 'No image file found')
        
    except Exception as e:
        print(f"Error fixing thumbnail name: {e}")
        return ('error', str(e))

# ===== zCivitai-2-JSONv4 Ported Functions =====

def strip_html_tags(text):
    # Remove HTML tags from text using regular expressions
    clean = re.compile('<.*?>')
    # Replace HTML tags with a space to preserve spacing
    return re.sub(clean, ' ', text)

def get_creator_from_api(model_id, use_api=True):
    """
    Fetch creator information from Civitai API using model ID
    """
    # If API calls are disabled, return empty string
    if not use_api:
        return ''
        
    try:
        # Make API request to get model information
        api_url = f"https://civitai.com/api/v1/models/{model_id}"
        response = requests.get(api_url, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            model_data = response.json()
            # Extract creator information
            if 'creator' in model_data and 'username' in model_data['creator']:
                return model_data['creator']['username']
        
        # If we reach here, either the request failed or creator info wasn't found
        return 'Unknown'
    except Exception as e:
        print(f"Error fetching creator information: {e}")
        return 'Unknown'

def parse_civitai_info_file(file_path, use_api=True, existing_creator=''):
    civitai_info_data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        civitai_info_data = json.load(file)
    # Initialize all fields with empty values
    mapped_data = {
        'activation text': '',
        'base model': '',
        'category': '',
        'description': '',  # Will keep this empty as per requirement
        'example prompt 1': '',
        'high low': '',  # High/Low toggle field
        'model version': '',  # Model version field
        'name': '',  # Model name field (populated from civitai name)
        'negative text': '',
        'notes': '',
        'nsfw': '',
        'preferred weight': 0,
        'sd version': '',
        'subcategory': '',
        'tags': '',
        'web_civitai_data': {
            'civitai name': '',
            'civitai text': '',
            'creator': '',
            'url': ''
        }
    }
    
    # Extract data from civitai.info
    if 'trainedWords' in civitai_info_data:
        trained_words = civitai_info_data['trainedWords']
        if isinstance(trained_words, list) and trained_words:
            mapped_data['activation text'] = trained_words[0]
            mapped_data['web_civitai_data']['civitai text'] = ', '.join(trained_words)

    if 'baseModel' in civitai_info_data:
        mapped_data['base model'] = civitai_info_data['baseModel']
        mapped_data['sd version'] = map_sd_version(civitai_info_data['baseModel'])

    if 'model' in civitai_info_data:
        if 'name' in civitai_info_data['model']:
            mapped_data['web_civitai_data']['civitai name'] = civitai_info_data['model']['name']
            # Also populate the 'name' field with civitai name
            mapped_data['name'] = civitai_info_data['model']['name']
        if 'nsfw' in civitai_info_data['model']:
            mapped_data['nsfw'] = str(civitai_info_data['model']['nsfw']).lower()

    # Process description for notes field but don't map to description field
    description = ''
    if 'description' in civitai_info_data:
        description = civitai_info_data['description']
        if description:
            description = unescape(description)
            description = strip_html_tags(description)
            # Normalize spaces by stripping leading/trailing spaces and reducing multiple spaces to a single space
            description = ' '.join(description.split())
            # No longer mapping to description field, but keeping for notes

    # Extract example prompt from images -> meta -> prompt
    if 'images' in civitai_info_data:
        images = civitai_info_data['images']
        if isinstance(images, list) and images:
            first_image = images[0]
            # Check if 'meta' is a dictionary before accessing 'prompt'
            if 'meta' in first_image and isinstance(first_image['meta'], dict) and 'prompt' in first_image['meta']:
                mapped_data['example prompt 1'] = first_image['meta']['prompt']
            # Check if 'meta' has 'negativePrompt'
            if 'meta' in first_image and isinstance(first_image['meta'], dict) and 'negativePrompt' in first_image['meta']:
                mapped_data['negative text'] = first_image['meta']['negativePrompt']

    # Build URL and notes
    if 'modelId' in civitai_info_data and 'id' in civitai_info_data:
        model_id = civitai_info_data['modelId']
        version_id = civitai_info_data['id']
        url = f"https://civitai.com/models/{model_id}?modelVersionId={version_id}"
        mapped_data['web_civitai_data']['url'] = url

        # Use existing creator if provided, otherwise get from API if enabled
        if existing_creator:
            mapped_data['web_civitai_data']['creator'] = existing_creator
        elif use_api:
            creator = get_creator_from_api(model_id, use_api)
            if creator:
                mapped_data['web_civitai_data']['creator'] = creator

        # Construct notes field
        notes = [f"URL: {url}"]
        if 'baseModel' in civitai_info_data:
            notes.append(f"Base Model: {civitai_info_data['baseModel']}")
        if 'trainedWords' in civitai_info_data and civitai_info_data['trainedWords']:
            notes.append(f"Activation Words: {', '.join(civitai_info_data['trainedWords'])}")
        if description:
            notes.append(f"Description: {description}")
        mapped_data['notes'] = '\n'.join(notes)

    return mapped_data

def write_json_file(file_path, data):
    json_file_path = file_path[:-len('.civitai.info')] + '.json'  # Create corresponding JSON file path
    # Sort the data alphabetically by keys
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    with open(json_file_path, 'w') as file:
        json.dump(sorted_data, file, indent=4)

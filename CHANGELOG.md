# Lora Model Manager - Changelog

### 07/14/2026

**Added**
- **Model Identity Layout:** Restructured the Model Identity section in the Model Card. The Filename input now sits exclusively on the left side, making room for a brand new "Flags / Actions" box on the right. 
- **Tested Toggle:** Added a new "Tested" toggle button next to the Filename to easily mark models as tested. This state natively saves directly to the model's `.json` configuration file and tracks within the SQLite database.
- **Open File Location:** Added a clickable folder icon next to the "File Path" property in the Model Card that instantly launches your native OS file explorer directly to the model's containing directory.
- **Datalist Dropdowns:** Converted the Base Model, SD Version, Category, and Subcategory text fields into hybrid `datalist` dropdowns. They now provide instant autocomplete suggestions based on all existing values in your database, while also featuring a convenient clear "X" button to quickly empty the field.
- **Tag Cloud Input:** Upgraded the Tags field into an interactive tag cloud. Typing a word and pressing Tab or Enter instantly converts it into a distinct pill, complete with a removal button and Backspace support for quick clearing, while maintaining compatibility with the underlying comma-separated data structure.
- **Balanced Keywords Grid:** Reorganized the Keywords & Prompts section into a perfectly balanced 3-row by 2-column grid. Trigger Words, Negative Trigger Words, and All Trigger Words sit logically on the left, paired symmetrically with Preferred Weight, Example Prompt 1, and Example Prompt 2 on the right.
- **Tested Badges:** Added a visual "Tested" checkmark badge to both the Grid View model cards and the Table View thumbnails, aligning with the existing NSFW badge styling.

**Changed**
- **Manual Textbox Resizing:** Removed the automatic dynamic-expanding behavior from all multi-line text boxes (Trigger Words, Prompts, Tags, Notes, and Descriptions). They now load at a clean, consistent 2-line height but feature manual vertical drag-resizing, giving users full control over the modal's footprint.
- **Consolidated Flag Buttons:** Relocated the "NSFW" and "High/Low" toggle buttons from their disparate locations in the Model Card and grouped them neatly into the new "Flags / Actions" box.
- **Bulk Move Interface:** Upgraded the Bulk Move folder selection from a basic dropdown to a scrollable list view for better visibility of deep folder structures.
- **Dynamic Versioning:** Refactored the UI header to dynamically pull the application version directly from `package.json`, ensuring the interface is always perfectly in sync with the codebase.

**Fixed**
- **Settings Persistence:** Fixed a bug where the "Filter folders with base model filter" setting would fail to visually check its box in the UI and wouldn't properly save to `config.json`. The backend JSON compiler now correctly orders and persists this setting.

### 07/13/2026

**Added**
- **Global Model Extension Support:** Added comprehensive support for additional model file extensions (such as `.gguf`, `.ckpt`, `.pt`, and `.pth`). The application now natively recognizes, syncs, moves, renames, and manages these file types alongside `.safetensors` files without treating them as unknown sidecar files.

**Fixed**
- **Associated Files Glob Matching:** Fixed an issue where models containing square brackets in their names (e.g. `[Z] Checkpoint`) would display zero associated files in the Model Details "Files" tab. The backend file scanner now properly escapes brackets before performing `glob` matching to accurately locate the model's sidecar files.

**Changed**
- **Local Network Support:** Updated the frontend startup batch script to expose Vite on all network interfaces (`--host`), allowing you to preview the app from other devices on your local network.
- **Repository Cleanup:** Created an `Extra Files` directory and moved all unused and legacy `.py`, `.js`, and concept test files out of the project root.


### 07/12/2026

**Added**
- **Advanced Boolean Search Engine:** Completely rewrote the Vue search parser to support "Everything Search" style syntax. It now supports precise filtering using Boolean operators (`|` OR, `!` NOT, space for AND), `< >` groupings, `" "` exact phrases, and explicit field targeting (e.g. `cat:anime`). 
- **Global Substring Matching:** The default search functionality has been upgraded. If no specific field is provided, the search engine now instantly rips through a massive combined text block containing the model's name, tags, description, category, creator, and more—and accurately matches middle-of-word substrings (e.g., `ree` finds `tree`).
- **Files Management Tab:** Added a brand new "Files" tab to the Model Card modal. It scans the local disk for all files sharing the exact same base name prefix and displays them in a neat table. Includes tiny image previews for thumbnails, readable file sizes, and a secure Delete button to clean up redundant associated files without touching the file explorer.
- **Search UI Helpers:** Added a helpful syntax cheat sheet popover that appears when hovering over the new `(?)` icon in the search bar. Also added a reactive `X` button to instantly clear complex search queries.

### 07/11/2026

**Added**
- **Structured Scanner Logging:** Modernized the backend Civitai scanner to stream structured JSON log dictionaries instead of plain text strings. The frontend log terminal now beautifully color-codes log entries (Info, Success, Warning, Error) in real-time.
- **Scanner Progress Tracking:** Implemented a visible progress bar in the Scanner View that accurately fills up during bulk scanning processes.
- **Dummy URL "Ignore" Workflow:** Completely overhauled the "Mark not matchable" system for Unresolved Models. Clicking it now seamlessly passes a `https://no-match.com/ignored` dummy URL to the backend, which intercepts the request, bypasses the internet scraper, and writes a minimal `.json` file to safely quarantine the model from all future scans.

**Changed**
- **Scanner UI Enhancements:** 
  - Adjusted the layout of the scanner terminal to be taller and removed redundant titles to maximize visible console space.
  - Added vertical scrolling (`max-height: 400px`) to the Unresolved Models list to prevent it from infinitely stretching off the bottom of the page.
- **CivArchive Graceful Fails:** The backend HTML parser now gracefully handles CivArchive "mirror-only" placeholder pages (where the page returns HTTP 200 but lacks actual Civitai model metadata). Instead of crashing with an internal Python `KeyError`, it safely returns an empty payload to trigger a proper "Not Found" state.

**Fixed**
- **Database Model Version Reloading:** Fixed an issue where a saved `modelVersion` would blank out when closing and reopening the Model Modal. Synchronized the frontend `ModelModal.vue` state loader to correctly read the `modelVersion` key emitted by the SQLite `database.py` mapper.
- **Scanner Button Overlap:** Fixed a CSS grid/flexbox issue where action buttons in the Scanner View were overlapping each other by applying proper `display: flex` rules to the container.
- **Dummy JSON Parsing:** Fixed a bug in the SQLite database importer where models marked as "unmatchable" (ignored) were failing to have their dummy URLs indexed because the backend wrote `civitaiUrl` into the `.json` file instead of the expected `url` key.
- **Thumbnail Success Reporting:** Corrected thumbnail downloading feedback so that it accurately prints failure statuses to the log instead of incorrectly declaring "SUCCESS" when Civitai connections fail.
- **Vue Store Update Bug:** Fixed a `TypeError` in the Unresolved Models list where clicking "Mark not matchable" attempted to invoke a non-existent `updateModel` function on the local Vue Pinia store instead of correctly hitting the API client.

### 07/10/2026

**Added**
- **Advanced Bulk Actions Toolbar:** Expanded the grid/list view bulk tools interface to include 5 distinct operations: Move, Edit, Rename, Delete, and Show Duplicates.
  - **Bulk Move**: Analyzes the model's base model against `modelTypeRoots` to filter valid destination folders natively. Relocates all selected models and their associated data/preview files simultaneously.
  - **Bulk Rename**: Runs the "Recommended Formatting" settings logic across all selected models, generating a clean comparison table showing the Old vs New filename with checkboxes to selectively skip files before executing the rename.
  - **Bulk Delete**: Safely deletes all selected models and their entire suite of associated sidecar files off the disk natively.
  - **Show Duplicates**: Interfaces with the backend `civitaiFindDuplicates` engine to index every model's stored `sha256` hash in your current location, rendering a clean visual dashboard grouping identical files to easily clear up disk space.
- **Table Column Mapping:** Added dynamic key translation between the frontend's camelCase config and backend's snake_case data schema, ensuring all custom-selected fields correctly populate with data in the table view.
- **Safe Mode Startup Settings:** Added dedicated settings for "Enabled by default" (server start / new session) and "Enabled on reload" (forcing on refresh) to fine-tune how Safe Mode persists.
- **Inline Filename Magic Actions:** When modifying the filename in the Model Modal, action buttons appear immediately below the input to quickly apply Recommended names, clean the syntax, use the Model Name directly, or append the Creator's Suffix.
- **Identity Quick-Tools:** Added quick-action toolbars that appear when editing identity fields. Editing the Model Name reveals "Civitai Name", "Clean", and "Trim". Editing the Model Version reveals "Guess Version" and "Clean".
- **Dynamic Grid Settings:** Added a comprehensive suite of grid card customizations to the Settings modal, including toggling the Card Title between Model Name and File Name, a Card Size dropdown (Small, Medium, Large), and independent toggles for High/Low tags, Folder tags, Trigger Words buttons, and URL buttons.

**Changed**
- **Seamless Identity Edits:** The Model Modal now remains fully open and seamlessly updates its internal route state when saving a Rename or executing a Move, preventing unnecessary window closing.
- **Intelligent Inline Move Dropdown:** Replaced the legacy generic prompt with a sleek, inline dropdown menu for moving models.
  - Analyzes the model's base model against `modelTypeRoots` to filter the move targets (e.g. only showing Krea 2 root folders and subfolders for Krea 2 models).
  - Sweeps up all associated files (`.safetensors`, `.json`, `.civitai.info`, and up to four `.preview.png` images) simultaneously when a move is executed.
- **Model Modal Layout Updates:** 
  - Restyled the `High/Low` and `NSFW` toggles into distinct colored action buttons and grouped them together in the left info column.
  - Moved the `Model Version` input directly to the right of the `Model Name` for better space utilization.
  - Made the Identity Quick-Tools (Clean, Trim, Guess) permanently visible under their respective inputs instead of requiring a mouse hover.
  - Trim Name logic correctly strips comma-separated sub-models and collapses spacing (added Klein9b).

**Fixed**
- **Rename & Move Performance:** Rewrote the backend SQLite synchronization logic for file modification endpoints to utilize `sync_single_model()`. Renaming or moving a model now executes instantly by updating only the relevant row, rather than dragging down performance with a `force=True` full directory rescan. Added active spinning loaders to the Save and Move buttons for immediate feedback.
- **Duplicate Scanner Visuals:** Fixed a CSS flexbox layout issue where model cards in the Duplicates Modal were being collapsed to zero height. The duplicate model cards are now fully visible and stack correctly.
- **Model Navigation Routing:** Resolved a 404 Axios error that occurred when clicking the Next or Previous buttons in the Model details modal. Modified the URL encoding logic in the frontend and Flask routing logic on the backend to correctly handle model IDs containing subfolder paths and special characters.
- **Configuration Sort Enforcement:** The backend now strictly enforces key sorting and structure when saving `config.json`, preventing key displacement and ensuring properties like Safe Mode stay grouped intuitively.

---

## 🚀 Migration to Vue 3 & Vite

We have successfully migrated the frontend architecture of the Lora Model Manager from the legacy vanilla HTML/JS and jQuery setup to a modern, reactive single-page application powered by **Vue 3** and **Vite**.

### Core Architecture Enhancements
- **Vue 3 SFCs (Single File Components):** Transitioned UI logic, styling, and templates into clean, modular Vue components (e.g. `ModelModal.vue`, `TableView.vue`, `GridView.vue`).
- **Pinia State Store:** Introduced Pinia store modules (`src/stores/models.js`, `src/stores/settings.js`) to coordinate centralized reactive states across views and settings.
- **Vite Build System:** Shifted to Vite for super-fast Hot Module Replacement (HMR) and optimized frontend asset production.
- **RESTful API Boundary:** Refactored Flask routes to act exclusively as a decoupled JSON API layer, shifting presentation completely to the Vue client.

### Key Sub-Changes & Features Ported
- **Rebuilt View Formats:** Ported Grid View, Grouped Grid View, and Table View into fully reactive Vue layouts, respecting columns configuration dynamically.
- **Centralized Model Details Modal (`ModelModal.vue`):** Created a multi-tab editor for Identity/Renaming/Moving, Metadata fields mapping, Civitai scanning, and Raw JSON editing.
- **Settings Dashboard:** Re-implemented the Settings modal with tabs for General settings, Table Column visibility/ordering, Grid Card custom items, and Filename Formatting.
- **Bulk Action Flow:** Rewrote the bulk-editor, bulk-mover, and bulk-deletor modals to work natively with Vue state arrays, removing complex jQuery selector synchronization.
- **Unified API Client:** Consolidated all server fetches under a promise-based Axios client (`src/api/client.js`), featuring local asset routing and Civitai handler bindings.
- **Reactivity & Auto-saving:** Bound metadata fields directly to form models, triggering debounced updates to the database via API.

---

### 07/09/2026

**Added**
- **Model Card Quick View in Bulk Mode**
  - Added an info icon (`fa-info-circle`) next to the selection checkboxes on model cards when bulk mode is active.
  - Allows opening the Model Card popup to view/edit details for a model directly without affecting the bulk selection state.
- **Detailed Settings Descriptions**
  - Added verbose, user-friendly descriptive labels below controls in General settings, Table Columns, Grid Card customization, and Filename Formatting tabs.
- **Combo Boxes for Metadata Fields**
  - Converted `Base Model`, `SD Version`, `Category`, and `Subcategory` into combo boxes in both the Model Card details popup and the Bulk Edit Modal.
  - Dropdowns dynamically fetch and display all unique values currently in use in the database.
  - Includes a "Custom..." option that reveals a manual text input for entering custom values.
- **Bulk Edit Modal Restructuring**
  - Grouped Category & Subcategory fields, and Base Model & SD Version fields.
  - Renamed the "High/Low" toggle field to "WAN High / Low".
  - Added "NSFW" toggle selection to bulk operations.
  - Removed the deprecated "Model Version" field from bulk editing.
- **Hover Preview Swapping**
  - Enabled hover-based switching of preview images in the thumbnail strip of the Model Card details popup.

- **Civitai Management Tools**
  - Renamed "Fetch by Hash" to "Check Civitai for Metadata" for better clarity.
  - Added a "Download Thumbnails" utility button to manually trigger downloading missing preview images and videos from Civitai.

**Changed**
- **Settings Layout Spacing and Order**
  - Fixed a grid layout issue in General settings that pushed the Theme option to the top.
- **Model Identity High/Low Input**
  - Converted the "High/Low" selector into a sleek toggle button that cycles between High, Low, and None, while ensuring values are strictly capitalized before writing to the JSON file.
  - Restructured setting group margins on Grid Card settings to resolve squished UI text issues.
- **Consolidated Scan Script**
  - Ported the `.civitai.info` parsing and JSON creation functions from `zCivitai-2-JSONv4.py` directly into `civitai_handler.py`.
  - Refactored `manager.py` to call `civitai_handler.py` directly.
  - Deleted the legacy `zCivitai-2-JSONv4.py` script.
- **Image Action Overlay**
  - Moved the "Set as Default" and "Delete" thumbnail actions to overlay directly on the main preview image, appearing seamlessly on mouse hover as compact icon buttons.

**Fixed**
- **Settings UI Javascript Crash**
  - Fixed an issue where the settings modal script crashed on loading because it searched for the removed "Hide NSFW" DOM element, preventing other settings tabs from displaying their items.
- **Bulk Edit NSFW Data Type**
  - Fixed an issue where the bulk edit NSFW toggle saved the value as a boolean `true`/`false` instead of the expected string `"true"`/`"false"`.
- **Model Editor Inline Action Buttons**
  - Added inline action buttons below the Model Name and Model Version fields that appear when interacting with them. 
  - Model Name buttons allow you to quickly set the name from Civitai, "Clean" the formatting, or "Trim" out base-model references (e.g. Pony, SDXL).
  - Model Version buttons allow you to quickly format the version string or "Guess Version" intelligently by parsing the filename and existing name data.
- **Inline Filename Editor Mode**
  - Clicking "Modify Name" or "Use Recommended" no longer triggers an invasive browser prompt. Instead, the filename field itself transforms into an active text input box.
  - While editing the filename, a suite of helper buttons (`Recommended`, `Clean`, `Model Name`, `Creator Suffix`) appear immediately below the field to assist in formatting the physical file's name.
  - Added dedicated `Save` and `Cancel` buttons during filename editing to commit the actual file rename operation to the filesystem via the backend.
- **Civitai Metadata Bulk Scanner UI**
  - Redesigned the Civitai Scanner page to replicate and improve upon the legacy application's multi-functional interface.
  - Added a unified task queue engine to run sequential operations (fetching metadata, downloading thumbnails, generating hashes) without overwhelming the API or browser.
  - Added new options to specifically target missing data or force fetch all data across all models.
  - Added a new `Scanner` tab to the global settings menu, exposing scan preferences such as skipping existing data, skipping NSFW previews, and configuring delay between API requests to avoid rate limits.
  - Corrected mapping of user schema fields such as `name`, `notes`, and `web_civitai_data.civitai text` ("All Trigger Words") to ensure they save/load perfectly from both the SQLite layer and sidecar JSON files. (Model Name now properly parses from the `name` json property rather than defaulting strictly to the filename).
- **Raw JSON Editor Isolation**
  - Configured the Raw JSON editor tab to strictly edit the underlying sidecar JSON file content rather than displaying/clobbering it with the flattened Vue UI model state.
- **Sorting State Persistence**
  - Fixed an issue where the `Sort By` dropdown forgot the user's selection on page refresh. It now correctly saves the selection to browser local storage, while gracefully falling back to the global `Default Sort` setting on initial loads.
- **UI Theme Consistency**
  - Fixed an issue where generic buttons and `.btn-icon` elements (like the refresh and bulk edit toggle buttons) fell back to default browser white backgrounds.
  - Fixed an issue where the bulk edit toolbar lost its opaque background when a model was selected, making it transparent.
- **Auto-save API Route Routing**
  - Fixed the auto-save functionality in the details modal to call the mapper-friendly save endpoint (`api.saveModel`) rather than the raw JSON overwrite endpoint.
- **Thumbnail Renaming & Reordering Logic**
  - Corrected index offsets (0-based vs 1-based) and index array compilation in frontend calls to reorder and delete thumbnail endpoints, preventing file collisions and deletion failures on disk.

**Removed**
- **Redundant NSFW Settings**
  - Removed the duplicate "Hide NSFW Content" checkbox option from General settings, as it is already handled by SafeMode.

---

### 07/07/2026

**Added**
- **SD Version Mapping & Column**
  - Integrated `sd version` mapping into Civitai scanning logic based on `baseModel` attributes.
  - Added `SD Version` to the table list view columns list (complete with sorting, visibility toggle, and configuration persistence).
  - Integrated `Base Model` and `SD Version` fields into the Bulk Edit modal for batch updating.

**Fixed**
- **Incorrect SD2 Tags**
  - Ran database migration to clean up incorrect "SD2" tags and update all existing model JSON files to match correct SD Version mapping configurations.
  - Applied the new mapping logic to the standalone `All-In-One Scan.py` script to ensure it correctly populates `sd version` going forward.

---

### 05/28/2026

**Fixed**
- **Bulk Model Moving Filter**
  - Updated bulk move folder filtering to check if all selected models resolve to the exact same configured root folder (even if they have different base model names, such as different Wan Video variants), ensuring the destination folder list is still filtered correctly.

---

### 05/26/2026

**Added**
- **Model Type Roots**
  - Added a new Settings tab for mapping Base Model Types to specific subdirectory paths within the models directory.
  - Implemented dropdown/combo-box selection using a <datalist> populated with actual folders from the backend, ensuring valid relative paths are configured.
  - Added dynamic filtering for folder dropdowns in single-model moving operations based on configured model roots.
  - Added dynamic filtering for folder dropdowns in bulk-moving operations (applies when all selected models share the same base model).

---

### 04/01/2026

**Added**
- **SHA256 Generation & Display**
  - Added a "Generate SHA256" button to the model actions panel.
  - Hashes are now persisted in the model's `.json` file and displayed in the "File Info" section of the model popup.
- **Model Deletion**
  - Added a "Delete Model" button to the model popup for streamlined file management.

**Changed**
- **Model Popup Layout Refinement**
  - Renamed "Civitai Actions" to "Actions".
  - Restructured the actions area to display buttons and associated files side-by-side for better space utilization.
- **Multi-Select Model Filter**
  - Refined the multi-select model filter with a custom checkbox-based dropdown.
  - Increased the dropdown height and tightened item spacing for improved usability in large collections.

**Fixed**
- **Checkpoint Bulk Operations**
  - Resolved a bug where Lora folders were incorrectly displayed in bulk edit/move modals when viewing Checkpoints.
- **Server Stability**
  - Fixed a Python `SyntaxError` in `manager.py` related to global cache declarations.
- **UI Feedback**
  - Corrected DOM element selection in `civitai-api.js` to ensure operation status messages are properly displayed.
- **Creator Suffix Button**
  - Fixed the "Creator Suffix" button logic to correctly retrieve the creator's name from the new `web_civitai_data` nested JSON object.

---

### 03/20/2026

**Fixed**
- **Video Thumbnail Extraction**
  - Fixed an issue where `.mp4` and `.webm` video URLs from Civitai were being mistakenly saved directly as unreadable `.png` files. The application now correctly identifies video URLs and passes them to FFmpeg to extract proper image frames for thumbnails.
  - Implemented this fix for both the standalone `All-In-One Scan.py` script and the main web UI backend (`civitai_handler.py`).

---

### 03/19/2026

**Changed**
- **Unified JSON Architecture**
  - Eliminated the redundant two-step file generation pipeline. The `.civitai.info` files are no longer created; Civitai API data is mapped and injected directly into the model's `.json` file at scan time.
  - Added a dedicated nested `web_civitai_data` object in the JSON to neatly house all WebUI/API-exclusive variables (`creator`, `published_date`, `url`, `preview_image_1/2`, `model_id`, `file_id`, `downloadUrl`, `original_filename`).
- **Bloat Removal**
  - Removed the bulky, unformatted `z_info_file` raw payload from the JSON completely to save substantial storage space.
- **Example Prompts**
  - Standardized prompt terminology: The legacy `example prompt` root-level key has been structurally renamed to `example prompt 1` to gracefully pair with `example prompt 2`.

---

### 03/10/2026

**Added**
- **Folder Pane Persistence**
  - The folder pane's state (visible/hidden) and view mode (Tree/List) now persist across sessions using `localStorage`.

---

### 03/05/2026

**Added**
- **All-In-One Scan Button**
  - New "Run All-In-One Scan" button on the Civitai scan page to automate matching, info file creation, and thumbnail downloads in one click.
- **Multi-Select Model Filter**
  - Replaced the single-select model filter with a multi-select dropdown, allowing users to filter by multiple base models simultaneously.

**Changed**
- **Model Popup UI Cleanup**
  - Refined the model card interface for better clarity and added new action buttons.

---

### 03/02/2026

**Changed**
- **Clean Name Improvements**
  - The "Clean Name" button now automatically converts ALL-CAPS names to Title Case for better readability.
- **Fast Media Updates**
  - Optimized the media update process to bypass slow disk scans, allowing new images to appear in the UI almost instantly.

---

### 02/24/2026

**Added**
- **Folder Tree & List View**
  - New sidebar with toggleable Tree and List views for enhanced folder navigation and management.

---

### 01/27/2026

**Fixed**
- **Model Cache Persistence**  
  Fixed a critical bug where the model cache was not actually persisting between requests. The cache was stored on handler instances which are recreated per HTTP request, defeating the caching entirely. Moved cache to module-level variables so models are scanned once on first load, then served instantly from cache. Use the refresh button to force a re-scan when needed.

- **Refresh Button Not Detecting New Files**  
  Fixed an issue where clicking the refresh button would not detect newly added model files. The refresh button now correctly passes `refresh=true` to the backend, forcing a full re-scan of the models directory.

- **SafeMode Toggle Invalidating Cache**  
  Fixed an issue where toggling SafeMode (or changing any setting) would incorrectly invalidate the model cache and force a slow re-scan. Cache is now only invalidated when the models directory path actually changes.

---

### 01/26/2026

**Changed**
- **Base Model Dropdown**  
  The Base Model field on the model card is now a dropdown populated with all existing base models from your collection (same list used for grid filtering). Includes a "Custom..." option to enter values not in the list.

---

### 01/21/2026

**Added**
- **Bulk Delete**  
  New delete button in bulk edit mode allows deleting selected models and all associated files (.json, .civitai.info, preview images).
- **Civitai Scan Page Redesign**  
  Actions reorganized into card-based layout with icons, descriptions, and grouped buttons.
- **Settings Gear on Civitai Scan Page**  
  Scan options moved to a settings modal, accessible via gear icon. Settings auto-save to config.json.
- **High/Low Required Field Validation**  
  When filename formats use `{highlow}`, models missing this value show warnings during rename operations.

**Changed**
- **Button Colors**  
  Added `btn-danger` (red) and `btn-warning` (muted orange) button styles for better visual hierarchy.
- **Action Button Sections**  
  Civitai Scan buttons now organized into labeled sections: Civitai Data, JSON, Thumbnails, Hashes, and Duplicates.

---

### 01/20/2026

**Added**
- **SHA256 Hash Storage**  
  SHA256 hashes are now saved to each model's JSON file when fetching Civitai data. This enables duplicate detection and faster lookups.
- **Generate Hashes Buttons**  
  New buttons on Civitai Scan page: "Generate Hashes - Missing" (skips models with existing hashes) and "Generate Hashes - All" (regenerates all).
- **Find Duplicates Button**  
  New button on Civitai Scan page to detect duplicate model files by comparing their SHA256 hashes.

**Changed**
- **Hierarchical Folder Sorting**  
  Folders now sort hierarchically so subfolders appear directly after their parent folders (e.g., Animals, Animals/Cats, Trees, Trees/Green). Applies to Group By Folder/Path views and all folder dropdowns.
- **Bulk Move Folder List**  
  Replaced the dropdown with a scrollable, clickable folder list for easier folder selection when bulk moving models.

---

### 01/17/2026

**Added**
- **Grid Card Settings Tab**  
  New settings tab to customize grid view card display. Configure image mode (single vs carousel), title source (filename or model name), and up to 3 subtitle fields from various options including folder, category, base model, version, and more.
- **Configurable Subtitles**  
  Grid cards now show customizable subtitle fields joined with " | ", with empty fields automatically hidden.

**Changed**
- **Folder Field Deprecated**  
  The `folder` JSON field is no longer stored in model files. Folder is now derived dynamically from the model's file path, eliminating stale data when files are moved.
- **Grid Card Display**  
  Grid cards now use settings for title and subtitle content instead of hardcoded values.

---

### 01/13/2026

**Added**
- **Favicon**  
  Added application favicon in assets folder.
- **Modal Navigation Arrows**  
  Previous/next buttons in model popup header to navigate between models. Keyboard shortcuts: Left/Right arrow keys.
- **Modern Tag Input**  
  Pill-style tag input component for the Tags field. Type and press Enter to add, click X to remove.
- **Use Folder Button**  
  When editing Category or Subcategory, a "Use Folder" button appears to populate the field with the model's current folder name.
- **Search by Tags**  
  Search now includes tags in addition to name, filename, and category.
- **Filename Customization**  
  Added settings to configure "Recommended Filename" formats per Base Model using variables like `{modelname}` and `{version}`.
- **Smart Rule Creation**  
  When adding a new format rule, a dropdown now lists detected Base Models that aren't yet configured.
- **Bulk Editing Mode**  
  Select multiple models at once to perform batch operations:
  - **Bulk Move**: Move all selected models to a different folder
  - **Bulk Edit**: Update Category, Subcategory, Version, and High/Low for all selected models
  - **Bulk Rename**: Preview and apply recommended filenames to selected models
- **Guess Version Button**  
  When editing Model Version, a button appears to auto-detect version numbers from the model name or filename (e.g., "v2.0" → "2").

**Changed**
- **Keywords Section Reorganized**  
  Trigger words (positive, negative, all) now on the left, Example Prompts on the right. Section renamed to "Keywords & Prompts".
- **Table View Grouping**  
  Table view now supports grouping just like grid view. Group headers span all columns with model counts.
- **Settings Modal Tabs**  
  Organized settings into tabs (General, Table Columns, Filename Formatting) for better navigation.
- **Header Button Text**  
  Shortened button labels: "Grid View" → "Grid", "Table View" → "Table", "Civitai Scan" → "Civitai".
- **Categorization Section Reorganized**  
  Category/Subcategory now on left, Tags on right. Improved modal header button spacing.
- **Modal UI Cleanup**  
  Consistent spacing and dark theme colors in left column. Larger nav/refresh/close icons.

---

### 01/08/2026

**Added**
- **Video Thumbnail Extraction**  
  Extracts first and last frames from Civitai video previews using FFmpeg when no images are available.
- **Multi-Image Downloads**  
  Thumbnail download now fetches up to 2 images per model (`.preview.png` and `.preview2.png`).
- **Download Thumbnails - All Button**  
  New button on Civitai Scan page to download/update thumbnails for ALL models, not just missing ones.
- **Requirements File**  
  Added `requirements.txt` with Python dependencies and FFmpeg installation notes.

**Changed**
- **Smart Thumbnail Filling**  
  Download Thumbnail button now fills empty preview slots without re-downloading existing images.

---

### 01/03/2026

**Changed**
- **Model Identity Layout**  
  Model Version and High/Low toggle now display side by side (70/30 split).

---

### 01/01/2026

**Changed**
- **Modal Title Styling**  
  Moved horizontal rule to directly under title text instead of full header width.

**Fixed**
- **Duplicate Horizontal Rules**  
  Removed duplicate HR styling that caused two lines to appear under modal title.
- **Thumbnail Border Radius**  
  Fixed thumbnail corners to be rounded on all sides, not just top.

---

### 12/31/2025

**Changed**
- **Textarea Auto-Resize**  
  View mode shrinks to fit content (max 20 lines with scrollbar); edit mode expands to show all.
- **Changelog Format**  
  Migrated changelog from TXT to Markdown format with improved structure.

**Fixed**
- **Text Spacing**  
  Fixed spacing issues in UI text elements.
- **Model Weight Display**  
  Corrected model weight rendering in the interface.

---

### 12/30/2025

**Added**
- **Manual Civitai URL Matching**  
  Prompts for manual URL entry when hash matching fails, or creates dummy file.

**Fixed**
- **Move Location Dropdown**  
  Fixed dropdown to show correct folders for LoRAs vs Checkpoints.
- **Preferred Weight Slider**  
  Fixed slider display and value updates in edit mode.

---

### 12/29/2025

**Added**
- **Checkpoint Model Support**  
  Added second model location for Checkpoints with separate UI tab.

**Fixed**
- **Checkpoint Move Function**  
  Fixed file moving for Checkpoint models.
- **Checkpoint Civitai Scan**  
  Fixed scanning and matching for Checkpoint models.

---

### 12/28/2025

**Added**
- **Creator Suffix Button**  
  Appends " - [creator name]" to proposed filename.
- **Trim Name Button**  
  Removes base model and version suffixes from model name.

**Changed**
- **Move/Rename UI**  
  Improved visibility toggles, added recommended button outside edit mode.
- **Civitai2JSON Script**  
  Writes Civitai name to Model Name field; preserves existing Model Name, High/Low, and Version when updating.

---

### 12/27/2025

**Added**
- **Filename Helper Buttons**  
  Model Name button copies to filename; Recommended builds filename from metadata.

**Changed**
- **Naming Buttons Reorganization**  
  Moved Civitai Name and Clean buttons under Model Name field.

---

### 12/26/2025

**Added**
- **Model Name Field**  
  New field to store display name (separate from filename), auto-populated from Civitai.
- **High/Low Toggle**  
  Toggle for Wan2.2 model variants (High or Low).

**Changed**
- **Split Info Panels**  
  Separated read-only area into File Info and File Data sections.

---

### 12/25/2025

**Added**
- **Version in Title Bar**  
  Displays model version in popup title when available.
- **Description Section**  
  Added organized section for Notes and Description fields.

**Changed**
- **Thumbnail Aspect Ratio**  
  Thumbnails now use consistent 3:4 aspect ratio with cover fit.
- **Recommended Name Button**  
  Generates suggested filename based on model type and metadata.
- **File Management Overhaul**  
  Redesigned file operations area for better usability.

---

### 12/24/2025

**Added**
- **Settings and Model JSON Handling**  
  Improved model JSON handling and new settings options.
- **Civitai Integration**  
  Initial Civitai API integration for model metadata.

**Changed**
- **.gitignore Update**  
  Added Python cache directories to .gitignore.

**Fixed**
- **Deleted File Cleanup**  
  Removed stale deleted file references from the project.

---

### 12/15/2025

**Added**
- **Loading Indicator**  
  Visual loading indicator while models are being scanned.
- **Search and Filter**  
  Search bar and filter options for model browsing.
- **Sorting Options**  
  Sort models by various criteria.
- **Auto-Create JSON Files**  
  Creates model JSON file automatically when a field is populated.
- **Dummy Civitai Info Files**  
  Prompts to create placeholder file when no Civitai match is found.
- **Copy Prompt Button**  
  Added clipboard copy button for prompt text boxes.
- **New JSON Fields**  
  Added Example Prompt 2 and Model Version fields.
- **Comprehensive Styling**  
  New CSS files for general, model, and settings modals plus components and layout.

**Changed**
- **Renamed Fields**  
  Positive Words → Triggerwords for WebUI; Negative Words → Negative Words for WebUI; Civitai Words → All Triggerwords.
- **Default Application Port**  
  Set default port for the application.

**Fixed**
- **Thumbnail Mouseover**  
  Fixed thumbnail mouseover functionality in grid view.

---

### 12/14/2025

**Added**
- **Civitai Integration**  
  Civitai API integration for model information and preview images.
- **Civitai Scan UI**  
  UI for scanning models against Civitai database.
- **Direct Preview Upload**  
  Upload preview images directly from the UI.

---

### 12/13/2025

**Added**
- **Multi-Image Preview Carousel**  
  Carousel with side navigation and indicator for model cards.

---

### 12/12/2025

**Added**
- **Initial Web UI**  
  Lora model management interface with grid/table views.
- **Backend Endpoints**  
  API endpoints for folder listing and model moving.
- **Civitai Metadata Parser**  
  Script to generate JSON files from Civitai metadata.
- **Model Details Modal**  
  Popup modal for viewing detailed model information.
- **Search & Filters**  
  Search, filter, and sort functionality for models.
- **README Documentation**  
  Comprehensive README detailing features, installation, and usage.

---

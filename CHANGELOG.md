# Lora Model Manager - Changelog

### 07/21/2026 - v2.0.22

**Added**
- **LoRA Slider Metadata & DB Support**: Added complete end-to-end support for LoRA slider models, including `is_slider`, `slider_min`, `slider_max`, `slider_min_desc`, and `slider_max_desc` SQLite database columns and sidecar `.json` metadata fields.
- **Proportional Fat Track Weight Bar**: Unified Preferred Weight slider interface in Model Details modal featuring a custom gradient fat track bar, neutral `0` line marker, dynamic floating value pin badge, and highlighted range fill. Custom slider models display min/max bounds and concept labels; standard models default to `-3.0` to `+3.0`.
- **Model Name Slider Action**: Added a micro `Slider` action button under Model Name next to `Trim` that formats and inserts or updates slider tags directly in the model name (e.g. `[-5 Less ↔ More 5]`) and auto-saves.
- **Slider Badges**: Added visual `Slider` badges and range metadata tags to Grid Cards and Table View thumbnails.

**Changed**
- **Model Modal Details Layout**: Swapped Preferred Weight / Slider into the **Model Identity** section (top right grid cell) and relocated **Description** to the **Keywords & Prompts** section (row 1 right grid cell) for improved layout symmetry.
- **Compact Slider Config Controls**: Formatted min/max numerical value inputs into compact `55px` columns with centered text alignment and added `min-width: 0` / text clipping protections to prevent text overlap.

### 07/17/2026 - v2.0.21

**Fixed**
- **Network Access:** Fixed an issue where the WebUI would fail to load models (displaying a "Network Error") when accessed from another computer on the local network. The frontend API client now correctly uses relative paths in development mode, enabling the Vite proxy to properly route requests.

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


<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content settings-modal">
      <div class="modal-header">
        <h2><i class="fas fa-cog"></i> Settings</h2>
        <button class="btn btn-icon" @click="emit('close')"><i class="fas fa-times"></i></button>
      </div>
      
      <div class="modal-body" v-if="!settings.loading">
        <div class="settings-tabs">
          <button class="tab-btn" :class="{ active: activeTab === 'general' }" @click="activeTab = 'general'">General</button>
          <button class="tab-btn" :class="{ active: activeTab === 'views' }" @click="activeTab = 'views'">Views</button>
          <button class="tab-btn" :class="{ active: activeTab === 'grid' }" @click="activeTab = 'grid'">Grid View</button>
          <button class="tab-btn" :class="{ active: activeTab === 'columns' }" @click="activeTab = 'columns'">Table View</button>
          <button class="tab-btn" :class="{ active: activeTab === 'safemode' }" @click="activeTab = 'safemode'">Safe Mode</button>
          <button class="tab-btn" :class="{ active: activeTab === 'formatting' }" @click="activeTab = 'formatting'">File Names</button>
          <button class="tab-btn" :class="{ active: activeTab === 'roots' }" @click="activeTab = 'roots'">Folder Roots</button>
          <button class="tab-btn" :class="{ active: activeTab === 'trimnames' }" @click="activeTab = 'trimnames'">Trim Names</button>
          <button class="tab-btn" :class="{ active: activeTab === 'scanner' }" @click="activeTab = 'scanner'">Scanner</button>
        </div>
        
        <div class="settings-content">
          <!-- General Tab -->
          <div v-if="activeTab === 'general'" class="settings-section">
            <!-- Server & Startup -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Server & Launch Configuration</h3>
                <span class="variables-help">Network port and automatic startup options</span>
              </div>
              
              <div class="setting-row-2col" style="margin-top: 6px;">
                <div class="setting-group">
                  <div class="checkbox-title-row">
                    <label style="margin: 0;"><i class="fas fa-network-wired" style="color: #3498db;"></i> Server Port</label>
                    <span class="preview-meta-tag"><i class="fas fa-server" style="color: #3498db;"></i> Port {{ localSettings.port || 8080 }}</span>
                  </div>
                  <input type="number" v-model.number="localSettings.port" class="form-control" placeholder="8080" min="1" max="65535">
                  <small>Backend Flask server port (requires server restart to take effect)</small>
                  <div v-if="isRestrictedPort(localSettings.port)" class="warning-text" style="margin-top: 5px; margin-bottom: 0;">
                    <i class="fas fa-exclamation-triangle"></i> Port {{ localSettings.port }} is blocked by web browsers for security (ERR_UNSAFE_PORT). Please use ports like 8080, 8000, 5000, 3000, or 8888.
                  </div>
                </div>

                <div class="setting-group">
                  <div class="checkbox-title-row">
                    <label style="margin: 0;"><i class="fas fa-desktop" style="color: #2ecc71;"></i> Browser Launch</label>
                  </div>
                  <label class="checkbox-desc-item" style="height: 100%;">
                    <input type="checkbox" v-model="localSettings.autoOpenBrowser">
                    <div class="checkbox-text">
                      <div class="checkbox-title-row">
                        <span class="checkbox-title">Auto-Open Browser</span>
                        <span class="preview-badge badge-tested"><i class="fas fa-external-link-alt"></i> Launch</span>
                      </div>
                      <span class="checkbox-desc">Automatically open WebUI in your default browser on server start</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            <!-- Model Storage Directories -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Model Storage Directories</h3>
                <span class="variables-help">Primary root directories containing your model collections</span>
              </div>

              <div class="setting-group" style="margin-top: 6px;">
                <div class="checkbox-title-row">
                  <label style="margin: 0;"><i class="fas fa-layer-group" style="color: #9b59b6;"></i> LoRA Models Directory</label>
                  <span class="preview-meta-tag"><i class="fas fa-shapes" style="color: #9b59b6;"></i> LoRA Library</span>
                </div>
                <div class="input-with-button">
                  <input type="text" v-model="localSettings.modelsDirectory" class="form-control" placeholder="e.g. C:\AI\Models\LoRA">
                  <button class="btn btn-secondary" @click="browseForFolder('modelsDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
                </div>
                <small>Path to your primary LoRA models folder</small>
              </div>

              <div class="setting-group" style="margin-top: 6px;">
                <div class="checkbox-title-row">
                  <label style="margin: 0;"><i class="fas fa-cube" style="color: #2ecc71;"></i> Checkpoints Directory</label>
                  <span class="preview-meta-tag"><i class="fas fa-cubes" style="color: #2ecc71;"></i> Base Models</span>
                </div>
                <div class="input-with-button">
                  <input type="text" v-model="localSettings.checkpointsDirectory" class="form-control" placeholder="e.g. C:\AI\Models\Stable-Diffusion">
                  <button class="btn btn-secondary" @click="browseForFolder('checkpointsDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
                </div>
                <small>Path to your primary Checkpoint models folder</small>
              </div>
            </div>

            <!-- Workflow Directories -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Workflow Directories</h3>
                <span class="variables-help">Paths for incoming downloads and file processing queues</span>
              </div>

              <div class="setting-group" style="margin-top: 6px;">
                <div class="checkbox-title-row">
                  <label style="margin: 0;"><i class="fas fa-download" style="color: #3498db;"></i> Default Download Directory</label>
                  <span class="preview-meta-tag"><i class="fas fa-cloud-download-alt" style="color: #3498db;"></i> Incoming</span>
                </div>
                <div class="input-with-button">
                  <input type="text" v-model="localSettings.defaultDownloadDirectory" class="form-control" placeholder="e.g. C:\AI\Downloads">
                  <button class="btn btn-secondary" @click="browseForFolder('defaultDownloadDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
                </div>
                <small>Default folder path where newly downloaded models will be saved</small>
              </div>

              <div class="setting-group" style="margin-top: 6px;">
                <div class="checkbox-title-row">
                  <label style="margin: 0;"><i class="fas fa-random" style="color: #e67e22;"></i> Default Sorting Directory</label>
                  <span class="preview-meta-tag"><i class="fas fa-inbox" style="color: #e67e22;"></i> Sorting Queue</span>
                </div>
                <div class="input-with-button">
                  <input type="text" v-model="localSettings.defaultSortingDirectory" class="form-control" placeholder="e.g. C:\AI\Sorting">
                  <button class="btn btn-secondary" @click="browseForFolder('defaultSortingDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
                </div>
                <small>Default folder path used for processing/sorting unorganized models</small>
              </div>
            </div>
          </div>
          
          <!-- Views Tab -->
          <div v-if="activeTab === 'views'" class="settings-section">
            <!-- Default View & Sorting -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Default View & Sorting</h3>
                <span class="variables-help">Initial library presentation and model sorting order</span>
              </div>

              <div class="setting-row-2col" style="margin-top: 10px;">
                <div class="setting-group">
                  <div class="checkbox-title-row">
                    <label style="margin: 0;">Default View</label>
                    <span class="preview-meta-tag">
                      <i :class="localSettings.defaultView === 'grid' ? 'fas fa-th-large' : 'fas fa-table'" style="color: #3498db;"></i>
                      {{ localSettings.defaultView === 'grid' ? 'Grid Cards' : 'Table View' }}
                    </span>
                  </div>
                  <select v-model="localSettings.defaultView" class="form-control">
                    <option value="grid">Grid View (Cards)</option>
                    <option value="table">Table View (Detailed rows)</option>
                  </select>
                  <small>Default display layout when opening libraries</small>
                </div>

                <div class="setting-group">
                  <div class="checkbox-title-row">
                    <label style="margin: 0;">Default Sort Order</label>
                    <span class="preview-meta-tag">
                      <i class="fas fa-sort-amount-down" style="color: #9b59b6;"></i> Sorted
                    </span>
                  </div>
                  <select v-model="localSettings.defaultSort" class="form-control">
                    <option value="name-asc">Name (A-Z)</option>
                    <option value="name-desc">Name (Z-A)</option>
                    <option value="date-desc">Date (Newest)</option>
                    <option value="date-asc">Date (Oldest)</option>
                    <option value="size-desc">Size (Largest)</option>
                    <option value="size-asc">Size (Smallest)</option>
                  </select>
                  <small>Default order when models load</small>
                </div>
              </div>
            </div>

            <!-- Folder Tree Filtering -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Folder Navigation & Filtering</h3>
                <span class="variables-help">Sidebar folder tree behavior and dynamic filtering</span>
              </div>

              <div class="checkbox-desc-grid" style="margin-top: 10px;">
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.filterFoldersWithBaseModel">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Filter Folders with Base Model Filter</span>
                      <span class="preview-meta-tag"><i class="fas fa-filter" style="color: #e67e22;"></i> Smart Filter</span>
                    </div>
                    <span class="checkbox-desc">Only show folders containing models that match your current base model filter (e.g. SDXL, Pony, Flux)</span>
                  </div>
                </label>
              </div>
            </div>
          </div>
          
          <!-- Grid Card Tab -->
          <div v-if="activeTab === 'grid'" class="settings-section grid-card-settings">
            
            <!-- Card Appearance Section -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Card Appearance</h3>
                <span class="variables-help">Title format and card dimensions</span>
              </div>
              <div class="setting-row-2col" style="margin-top: 10px;">
                <div class="setting-group">
                  <label>Card Title Display</label>
                  <select v-model="localSettings.gridCard.titleDisplay" class="form-control">
                    <option value="modelName">Model Name</option>
                    <option value="fileName">File Name</option>
                  </select>
                  <small>Header displays friendly model name or file name.</small>
                </div>
                <div class="setting-group">
                  <label>Card Size</label>
                  <select v-model="localSettings.gridCard.cardSize" class="form-control">
                    <option value="small">Small (Compact view)</option>
                    <option value="medium">Medium (Standard view)</option>
                    <option value="large">Large (High-detail view)</option>
                  </select>
                  <small>Default card thumbnail size across library grids.</small>
                </div>
              </div>
            </div>

            <!-- Image Badges Section -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Image Badges</h3>
                <span class="variables-help">Banners and icon overlays displayed over the preview thumbnail</span>
              </div>

              <div class="checkbox-desc-grid" style="margin-top: 10px;">
                <!-- Truncated Badge Style -->
                <label class="checkbox-desc-item">
                  <input 
                    type="checkbox" 
                    :checked="localSettings.gridCard.badgeStyle === 'truncated'" 
                    @change="localSettings.gridCard.badgeStyle = $event.target.checked ? 'truncated' : 'full'"
                  >
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Truncated Badge Icons</span>
                      <div class="badge-preview-row">
                        <span class="preview-mini-icon badge-nsfw"><i class="fas fa-ban"></i></span>
                        <span class="preview-mini-icon badge-slider"><i class="fas fa-arrows-alt-h"></i></span>
                        <span class="preview-mini-icon badge-tested"><i class="fas fa-check"></i></span>
                      </div>
                    </div>
                    <span class="checkbox-desc">Show compact circular icons instead of wide text banners</span>
                  </div>
                </label>

                <!-- NSFW Badge -->
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showNsfwBadge">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">NSFW Badge</span>
                      <span class="preview-badge badge-nsfw">NSFW</span>
                    </div>
                    <span class="checkbox-desc">Red indicator on models flagged as adult or NSFW content</span>
                  </div>
                </label>

                <!-- Slider Badge -->
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showSliderBadge">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Slider Badge</span>
                      <span class="preview-badge badge-slider">Slider</span>
                    </div>
                    <span class="checkbox-desc">Purple indicator on LoRAs with weight ranges</span>
                  </div>
                </label>

                <!-- Tested Badge -->
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showTestedBadge">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Tested Badge</span>
                      <span class="preview-badge badge-tested"><i class="fas fa-check"></i> Tested</span>
                    </div>
                    <span class="checkbox-desc">Green indicator on models verified and marked as tested</span>
                  </div>
                </label>
              </div>
            </div>

            <!-- Display Below Title Section -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Display Below Title</h3>
                <span class="variables-help">Metadata tags shown under the model title</span>
              </div>

              <div class="checkbox-desc-grid" style="margin-top: 10px;">
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showSliderRange">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Slider Range</span>
                      <span class="preview-meta-tag"><i class="fas fa-sliders-h" style="color: #9b59b6;"></i> -3 to 3</span>
                    </div>
                    <span class="checkbox-desc">Displays numeric weight bounds</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showFolder">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Folder Path</span>
                      <span class="preview-meta-tag"><i class="fas fa-folder-open" style="color: #f39c12;"></i> Styles</span>
                    </div>
                    <span class="checkbox-desc">Displays the folder directory location</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showCategory">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Category</span>
                      <span class="preview-meta-tag"><i class="fas fa-folder" style="color: #3498db;"></i> Clothing</span>
                    </div>
                    <span class="checkbox-desc">Displays the assigned category tag</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showBaseModel">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Base Model</span>
                      <span class="preview-meta-tag"><i class="fas fa-cube" style="color: #2ecc71;"></i> SDXL</span>
                    </div>
                    <span class="checkbox-desc">Displays architecture (SDXL, Pony, Flux)</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.gridCard.showHighLow">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">High / Low</span>
                      <span class="preview-meta-tag"><i class="fas fa-layer-group" style="color: #e67e22;"></i> High</span>
                    </div>
                    <span class="checkbox-desc">Displays strength classification</span>
                  </div>
                </label>
              </div>

              <!-- Sub-Option: Folder Truncation -->
              <div v-if="localSettings.gridCard.showFolder" class="sub-setting-indent" style="margin-top: 8px;">
                <label class="checkbox-desc-item" style="border: none; background: transparent; padding: 0;">
                  <input type="checkbox" v-model="localSettings.gridCard.truncateFolder">
                  <div class="checkbox-text">
                    <span class="checkbox-title">Truncate Folder Path to Last Two Folders</span>
                    <span class="checkbox-desc">Shortens paths to save space (e.g. Models/Anime/Style/Retro → Style/Retro)</span>
                  </div>
                </label>
              </div>
            </div>

            <!-- Action Buttons Bar Section -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Action Buttons Bar</h3>
                <span class="variables-help">Quick actions and button placement</span>
              </div>

              <label class="checkbox-desc-item" style="margin-top: 10px; margin-bottom: 6px;">
                <input type="checkbox" v-model="localSettings.gridCard.showActions">
                <div class="checkbox-text">
                  <span class="checkbox-title">Enable Action Buttons Bar</span>
                  <span class="checkbox-desc">Displays quick one-click action buttons on each model card</span>
                </div>
              </label>

              <template v-if="localSettings.gridCard.showActions">
                <div class="checkbox-desc-grid" style="margin-top: 6px;">
                  <label class="checkbox-desc-item">
                    <input 
                      type="checkbox" 
                      :checked="localSettings.gridCard.actionsPosition === 'overlay'" 
                      @change="localSettings.gridCard.actionsPosition = $event.target.checked ? 'overlay' : 'bottom'"
                    >
                    <div class="checkbox-text">
                      <div class="checkbox-title-row">
                        <span class="checkbox-title">Place on Image Overlay</span>
                        <span class="preview-mini-action"><i class="fas fa-layer-group"></i> Overlay</span>
                      </div>
                      <span class="checkbox-desc">Semi-transparent buttons over bottom of image</span>
                    </div>
                  </label>

                  <label class="checkbox-desc-item">
                    <input type="checkbox" v-model="localSettings.gridCard.showCopyTriggerWords">
                    <div class="checkbox-text">
                      <div class="checkbox-title-row">
                        <span class="checkbox-title">Copy Trigger Words</span>
                        <span class="preview-mini-action"><i class="fas fa-magic" style="color: #9b59b6;"></i> <i class="fas fa-comment-dots" style="color: #3498db;"></i></span>
                      </div>
                      <span class="checkbox-desc">Activation words and prompt buttons</span>
                    </div>
                  </label>

                  <label class="checkbox-desc-item">
                    <input type="checkbox" v-model="localSettings.gridCard.showUrlButton">
                    <div class="checkbox-text">
                      <div class="checkbox-title-row">
                        <span class="checkbox-title">Civitai URL Button</span>
                        <span class="preview-mini-action"><i class="fas fa-external-link-alt" style="color: #3498db;"></i> Civitai</span>
                      </div>
                      <span class="checkbox-desc">Opens model page on Civitai</span>
                    </div>
                  </label>

                  <label class="checkbox-desc-item">
                    <input type="checkbox" v-model="localSettings.gridCard.showInfoButton">
                    <div class="checkbox-text">
                      <div class="checkbox-title-row">
                        <span class="checkbox-title">Info / Details Button</span>
                        <span class="preview-mini-action"><i class="fas fa-info-circle" style="color: #2ecc71;"></i> Details</span>
                      </div>
                      <span class="checkbox-desc">Opens full model details modal</span>
                    </div>
                  </label>
                </div>
              </template>
            </div>

          </div>

          <!-- Table View Tab -->
          <div v-if="activeTab === 'columns'" class="settings-section">
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Table Columns & Display Sequence</h3>
                <span class="variables-help">Select visible table columns and reorder their position using the arrow controls</span>
              </div>

              <div class="columns-reorder-grid" style="margin-top: 10px;">
                <div v-for="(col, index) in localSettings.columnOrder" :key="col" class="column-reorder-card">
                  <label class="column-checkbox-label">
                    <input type="checkbox" v-model="localSettings.visibleColumns[col]">
                    <div class="column-info-text">
                      <div class="checkbox-title-row">
                        <span class="checkbox-title">{{ formatColumnName(col) }}</span>
                        <span class="preview-meta-tag">
                          <i :class="getColumnInfo(col).icon" :style="{ color: getColumnInfo(col).color }"></i>
                          #{{ index + 1 }}
                        </span>
                      </div>
                      <span class="checkbox-desc">{{ getColumnInfo(col).desc }}</span>
                    </div>
                  </label>
                  <div class="reorder-controls">
                    <button class="btn btn-icon btn-small" @click="moveColumnUp(index)" :disabled="index === 0" title="Move Left / Up">
                      <i class="fas fa-arrow-up"></i>
                    </button>
                    <button class="btn btn-icon btn-small" @click="moveColumnDown(index)" :disabled="index === localSettings.columnOrder.length - 1" title="Move Right / Down">
                      <i class="fas fa-arrow-down"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Safe Mode Tab -->
          <div v-if="activeTab === 'safemode'" class="settings-section">
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Content Safety & NSFW Protection</h3>
                <span class="variables-help">Startup protection defaults and NSFW image visibility</span>
              </div>

              <div class="checkbox-desc-grid" style="margin-top: 10px;">
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.safeModeDefault">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Enabled by Default</span>
                      <span class="preview-badge badge-tested"><i class="fas fa-shield-alt"></i> Protected</span>
                    </div>
                    <span class="checkbox-desc">Safe Mode starts enabled on new browser sessions or server restarts to safeguard adult content</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.safeModeOnReload">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Reset on Page Reload</span>
                      <span class="preview-meta-tag"><i class="fas fa-redo-alt" style="color: #3498db;"></i> Auto-Lock</span>
                    </div>
                    <span class="checkbox-desc">Refreshing the browser re-engages Safe Mode instead of remembering temporary unshielded state</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.nsfwBlurOverlay">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Blur NSFW Images</span>
                      <span class="preview-badge badge-nsfw"><i class="fas fa-eye-slash"></i> Blurred</span>
                    </div>
                    <span class="checkbox-desc">Applies a frosted glass blur overlay on adult-rated model previews until clicked to reveal</span>
                  </div>
                </label>
              </div>
            </div>
          </div>
          
          <!-- Formatting Tab -->
          <div v-if="activeTab === 'formatting'" class="settings-section">
            <!-- Filename Options -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Filename Options</h3>
                <span class="variables-help">General formatting preferences for generated filenames</span>
              </div>

              <div class="checkbox-desc-grid" style="margin-top: 10px;">
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.filenameSnakeCase">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Snake Case</span>
                      <span class="preview-meta-tag"><i class="fas fa-underline" style="color: #3498db;"></i> snake_case</span>
                    </div>
                    <span class="checkbox-desc">Use underscores instead of spaces</span>
                  </div>
                </label>
              </div>
            </div>

            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Filename Formatting Rules</h3>
                <span class="variables-help">Define a filename formatting by base model type to be used when renaming the models.</span>
              </div>

              <!-- Available Template Variables -->
              <div style="margin-top: 10px;">
                <div style="font-size: 0.82em; color: var(--color-text-secondary); margin-bottom: 6px; font-weight: 600;">Available Format Variables:</div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                  <span class="preview-meta-tag"><i class="fas fa-file-signature" style="color: #3498db;"></i> {modelname}</span>
                  <span class="preview-meta-tag"><i class="fas fa-code-branch" style="color: #2ecc71;"></i> {version}</span>
                  <span class="preview-meta-tag"><i class="fas fa-layer-group"></i> {highlow}*</span>
                  <span class="preview-meta-tag"><i class="fas fa-folder" style="color: #3498db;"></i> {category}</span>
                  <span class="preview-meta-tag"><i class="fas fa-folder-open" style="color: #9b59b6;"></i> {subcategory}</span>
                </div>
              </div>

              <div class="sub-setting-indent" style="border-left-color: #f39c12; margin-top: 12px; margin-bottom: 6px;">
                <span class="checkbox-desc" style="color: #f39c12; display: flex; align-items: center; gap: 6px;">
                  <i class="fas fa-exclamation-triangle"></i>
                  <span><strong>* {WAN: High/Low} </strong> If {highlow} is in a format string, models must have High/Low populated to execute renaming.</span>
                </span>
              </div>

              <div class="list-container" style="margin-top: 8px;">
                <!-- Column Headers (Shown once above rows) -->
                <div v-if="localSettings.filenameFormats.length > 0" class="list-header-row">
                  <div class="list-header-col" style="flex: 0 0 35%;">
                    <span class="checkbox-title">Base Model</span>
                    <span class="preview-meta-tag"><i class="fas fa-cube" style="color: #2ecc71;"></i> Model Type</span>
                  </div>
                  <div class="list-header-col" style="flex: 1;">
                    <span class="checkbox-title">Format Pattern</span>
                    <span class="preview-meta-tag"><i class="fas fa-font" style="color: #9b59b6;"></i> Template</span>
                  </div>
                  <div style="flex: 0 0 38px;"></div>
                </div>

                <div v-for="(format, index) in localSettings.filenameFormats" :key="index" class="list-row-card">
                  <!-- Base Model Column -->
                  <div style="flex: 0 0 35%;">
                    <!-- Default rule: locked input -->
                    <input 
                      v-if="format.baseModel === 'Default'" 
                      type="text" 
                      v-model="format.baseModel" 
                      class="form-control" 
                      disabled
                    >

                    <!-- Custom manual input mode -->
                    <div v-else-if="format.isCustom" style="display: flex; gap: 6px;">
                      <input 
                        type="text" 
                        v-model="format.baseModel" 
                        class="form-control" 
                        placeholder="e.g. Pony, SDXL"
                      >
                      <button 
                        type="button" 
                        class="btn-icon-toggle" 
                        @click="format.isCustom = false" 
                        title="Switch to dropdown list of base models"
                      >
                        <i class="fas fa-list"></i>
                      </button>
                    </div>

                    <!-- Dropdown select mode -->
                    <div v-else style="display: flex; gap: 6px;">
                      <select 
                        v-model="format.baseModel" 
                        class="form-control" 
                        @change="handleFormatSelectChange(format)"
                      >
                        <option value="" disabled>-- Select Base Model --</option>
                        <option v-for="bm in getAvailableBaseModelsForFormat(index)" :key="bm" :value="bm">
                          {{ bm }}
                        </option>
                        <option value="__custom__">+ Enter Custom Model Type...</option>
                      </select>
                      <button 
                        type="button" 
                        class="btn-icon-toggle" 
                        @click="format.isCustom = true; if (format.baseModel === '__custom__') format.baseModel = '';" 
                        title="Type a custom base model"
                      >
                        <i class="fas fa-pen"></i>
                      </button>
                    </div>
                  </div>

                  <!-- Format Pattern Column -->
                  <div style="flex: 1;">
                    <input type="text" v-model="format.format" class="form-control" placeholder="{modelname}_{version}_{highlow}">
                  </div>

                  <!-- Action Button Column -->
                  <div style="flex: 0 0 auto;">
                    <button v-if="format.baseModel === 'Default'" class="btn-lock" disabled title="Cannot remove default rule">
                      <i class="fas fa-lock"></i>
                    </button>
                    <button v-else class="btn-remove" @click="removeFilenameFormat(index)" title="Remove Rule">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>

                <button class="btn btn-secondary" style="width: 100%; justify-content: center; gap: 8px; margin-top: 6px;" @click="addFilenameFormat">
                  <i class="fas fa-plus-circle" style="color: #2ecc71;"></i> Add Format Rule
                </button>
              </div>
            </div>
          </div>
          
          <!-- Roots Tab -->
          <div v-if="activeTab === 'roots'" class="settings-section">
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Model Type Root Mappings</h3>
                <span class="variables-help">Map Base Models to root folders to automatically scope folder destinations in the Move modal</span>
              </div>

              <div class="sub-setting-indent" style="border-left-color: #3498db; margin-top: 10px; margin-bottom: 6px;">
                <span class="checkbox-desc" style="display: flex; align-items: flex-start; gap: 8px;">
                  <i class="fas fa-info-circle" style="color: #3498db; margin-top: 2px;"></i>
                  <span>When moving models with a matching Base Model, the folder picker is filtered to show only that root folder and its subdirectories. Use a <strong>relative folder path</strong> (e.g., <code>Pony/Characters</code> or <code>SDXL/Styles</code>).</span>
                </span>
              </div>

              <div class="list-container" style="margin-top: 8px;">
                <!-- Column Headers (Shown once above rows) -->
                <div v-if="localSettings.modelTypeRoots.length > 0" class="list-header-row">
                  <div class="list-header-col" style="flex: 0 0 35%;">
                    <span class="checkbox-title">Base Model</span>
                    <span class="preview-meta-tag"><i class="fas fa-cube" style="color: #2ecc71;"></i> Model Type</span>
                  </div>
                  <div class="list-header-col" style="flex: 1;">
                    <span class="checkbox-title">Root Folder Destination</span>
                    <span class="preview-meta-tag"><i class="fas fa-folder-open" style="color: #f39c12;"></i> Root Path</span>
                  </div>
                  <div style="flex: 0 0 38px;"></div>
                </div>

                <div v-for="(root, index) in localSettings.modelTypeRoots" :key="index" class="list-row-card">
                  <!-- Base Model Column -->
                  <div style="flex: 0 0 35%;">
                    <!-- Custom manual input mode -->
                    <div v-if="root.isCustom" style="display: flex; gap: 6px;">
                      <input 
                        type="text" 
                        v-model="root.baseModel" 
                        class="form-control" 
                        placeholder="e.g. Pony, Flux.1 D"
                      >
                      <button 
                        type="button" 
                        class="btn-icon-toggle" 
                        @click="root.isCustom = false" 
                        title="Switch to dropdown list of base models"
                      >
                        <i class="fas fa-list"></i>
                      </button>
                    </div>

                    <!-- Dropdown select mode -->
                    <div v-else style="display: flex; gap: 6px;">
                      <select 
                        v-model="root.baseModel" 
                        class="form-control" 
                        @change="handleRootSelectChange(root)"
                      >
                        <option value="" disabled>-- Select Base Model --</option>
                        <option v-for="bm in getAvailableBaseModelsForRoot(index)" :key="bm" :value="bm">
                          {{ bm }}
                        </option>
                        <option value="__custom__">+ Enter Custom Model Type...</option>
                      </select>
                      <button 
                        type="button" 
                        class="btn-icon-toggle" 
                        @click="root.isCustom = true; if (root.baseModel === '__custom__') root.baseModel = '';" 
                        title="Type a custom base model"
                      >
                        <i class="fas fa-pen"></i>
                      </button>
                    </div>
                  </div>

                  <!-- Root Folder Destination Column -->
                  <div style="flex: 1;">
                    <input type="text" v-model="root.rootFolder" class="form-control" placeholder="e.g. Pony/Characters">
                  </div>

                  <!-- Action Button Column -->
                  <div style="flex: 0 0 auto;">
                    <button class="btn-remove" @click="removeModelTypeRoot(index)" title="Remove Mapping">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                </div>

                <button class="btn btn-secondary" style="width: 100%; justify-content: center; gap: 8px; margin-top: 6px;" @click="addModelTypeRoot">
                  <i class="fas fa-plus-circle" style="color: #2ecc71;"></i> Add Root Mapping
                </button>
              </div>
            </div>
          </div>
          
          <!-- Trim Names Tab -->
          <div v-if="activeTab === 'trimnames'" class="settings-section" style="flex: 1; overflow: hidden; display: flex; flex-direction: column;">
            <div class="settings-group-clean" style="border-bottom: none; padding-bottom: 0; margin-bottom: 0; flex: 1; display: flex; flex-direction: column;">
              <div class="settings-header-clean" style="flex: 0 0 auto;">
                <div class="checkbox-title-row">
                  <h3>Trim Names Filter List</h3>
                  <span class="preview-meta-tag"><i class="fas fa-tags" style="color: #9b59b6;"></i> {{ localSettings.trimNames.length }} Filter Terms</span>
                </div>
                <span class="variables-help">These words and patterns are automatically stripped out when clicking Trim on model names</span>
              </div>

              <div class="sub-setting-indent" style="border-left-color: #9b59b6; margin-top: 10px; margin-bottom: 12px; flex: 0 0 auto;">
                <span class="checkbox-desc" style="display: flex; align-items: flex-start; gap: 8px;">
                  <i class="fas fa-magic" style="color: #9b59b6; margin-top: 2px;"></i>
                  <span>Clicking <strong>Trim</strong> strips these terms along with common noise brackets (<code>[]</code>, <code>()</code>) and surrounding periods. Clean titles keep libraries organized and searchable.</span>
                </span>
              </div>

              <div class="add-tag-container" style="flex: 0 0 auto;">
                <div class="input-with-button" style="width: 100%;">
                  <input 
                    type="text" 
                    v-model="newTrimName" 
                    @keydown.enter="addTrimName" 
                    placeholder="Enter a keyword or noise tag to remove (e.g. [v1.0], SDXL, LoRA)..." 
                    class="form-control" 
                  />
                  <button class="btn btn-secondary" @click="addTrimName" style="white-space: nowrap;">
                    <i class="fas fa-plus-circle" style="color: #2ecc71;"></i> Add Filter Term
                  </button>
                </div>
              </div>

              <div class="tags-container" style="flex: 1; max-height: none; overflow-y: auto; align-content: flex-start; margin-top: 10px;">
                <div v-for="(name, index) in localSettings.trimNames" :key="index" class="tag-chip">
                  <i class="fas fa-tag" style="color: #e67e22; font-size: 0.85em;"></i>
                  <span>{{ name }}</span>
                  <button class="btn-remove-tag" @click="removeTrimName(index)" title="Remove Term">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Scanner Tab -->
          <div v-if="activeTab === 'scanner'" class="settings-section">
            <!-- API Authentication & Rate Limiting -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Civitai Authentication & Rate Limiting</h3>
                <span class="variables-help">API credentials and request delay throttling</span>
              </div>

              <div class="setting-row-2col" style="margin-top: 10px;">
                <div class="setting-group">
                  <div class="checkbox-title-row">
                    <label style="margin: 0;"><i class="fas fa-key" style="color: #f1c40f;"></i> Civitai API Key (Optional)</label>
                    <span class="preview-meta-tag"><i class="fas fa-shield-alt" style="color: #f1c40f;"></i> API Key</span>
                  </div>
                  <input type="password" v-model="localSettings.civitaiApiKey" class="form-control" placeholder="Enter your Civitai API Key">
                  <small>Required to download restricted, early-access, or member-only model metadata & thumbnails</small>
                </div>

                <div class="setting-group">
                  <div class="checkbox-title-row">
                    <label style="margin: 0;"><i class="fas fa-stopwatch" style="color: #e67e22;"></i> Delay Between Requests</label>
                    <span class="preview-meta-tag"><i class="fas fa-tachometer-alt" style="color: #e67e22;"></i> Rate Limit</span>
                  </div>
                  <input type="number" step="0.1" min="0" v-model="localSettings.scanSettings.delayBetweenRequests" class="form-control" placeholder="Seconds">
                  <small>Throttles bulk scanning speed to avoid Civitai HTTP 429 rate limit errors (in seconds)</small>
                </div>
              </div>
            </div>

            <!-- Scanning Preferences -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Scanning Preferences</h3>
                <span class="variables-help">Control which models to scan and what assets to download</span>
              </div>

              <div class="checkbox-desc-grid" style="margin-top: 10px;">
                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.scanSettings.skipExistingData">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Skip Existing Data</span>
                      <span class="preview-meta-tag"><i class="fas fa-forward" style="color: #3498db;"></i> Skip</span>
                    </div>
                    <span class="checkbox-desc">Only scan models that do not already have downloaded Civitai metadata</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.scanSettings.skipNsfwPreviews">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Skip NSFW Previews</span>
                      <span class="preview-badge badge-nsfw"><i class="fas fa-ban"></i> Safe Only</span>
                    </div>
                    <span class="checkbox-desc">Prevents downloading preview images flagged with adult/NSFW content</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.scanSettings.downloadMaxSize">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Full-Size Previews</span>
                      <span class="preview-meta-tag"><i class="fas fa-expand" style="color: #9b59b6;"></i> HD Images</span>
                    </div>
                    <span class="checkbox-desc">Downloads full resolution cover images instead of standard compressed thumbnails</span>
                  </div>
                </label>

                <label class="checkbox-desc-item">
                  <input type="checkbox" v-model="localSettings.scanSettings.fetchCreatorInfo">
                  <div class="checkbox-text">
                    <div class="checkbox-title-row">
                      <span class="checkbox-title">Fetch Creator Info</span>
                      <span class="preview-meta-tag"><i class="fas fa-user-circle" style="color: #2ecc71;"></i> Creator</span>
                    </div>
                    <span class="checkbox-desc">Pulls extended creator profile details and social links (slightly slower scan)</span>
                  </div>
                </label>
              </div>
            </div>

            <!-- Maintenance -->
            <div class="settings-group-clean">
              <div class="settings-header-clean">
                <h3>Library Maintenance</h3>
                <span class="variables-help">Utilities for metadata cleanup and database consistency</span>
              </div>

              <div class="setting-group" style="margin-top: 10px;">
                <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                  <button class="btn btn-secondary" @click="cleanJsonFiles" :disabled="cleaningJson">
                    <i class="fas fa-broom" :class="{'fa-spin': cleaningJson}"></i> {{ cleaningJson ? 'Cleaning...' : 'Clean JSON Files' }}
                  </button>
                  <small style="margin: 0; flex: 1;">Migrate any remaining legacy .civitai.info files into standard .json metadata files and delete the old info files.</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn btn-primary" @click="save" :disabled="saving">
          <i class="fas fa-save" v-if="!saving"></i>
          <i class="fas fa-spinner fa-spin" v-else></i> 
          Save Configuration
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useSettingsStore } from '../../stores/settings';
import { useModelsStore } from '../../stores/models';
import { useToast } from '../../composables/useToast';
import { api } from '../../api/client';

const emit = defineEmits(['close']);
const settings = useSettingsStore();
const modelsStore = useModelsStore();
const toast = useToast();

const activeTab = ref('general');
const saving = ref(false);
const newTrimName = ref('');

const RESTRICTED_PORTS = [
  1, 7, 9, 11, 13, 15, 17, 19, 20, 21, 22, 23, 25, 37, 42, 43, 53, 69, 77, 79, 87, 95, 101, 102, 103, 104, 109, 110, 111, 113, 115, 117, 119, 123, 135, 137, 139, 143, 161, 179, 389, 427, 465, 512, 513, 514, 515, 526, 530, 531, 532, 540, 548, 554, 563, 587, 601, 636, 989, 990, 993, 995, 1719, 1720, 1723, 2049, 3659, 4045, 5060, 5061, 6000, 6566, 6665, 6666, 6667, 6668, 6669, 6697, 10080
];

const isRestrictedPort = (port) => {
  return RESTRICTED_PORTS.includes(Number(port));
};

// Create a deep reactive copy of settings for editing
const localSettings = reactive({
  port: 8080,
  autoOpenBrowser: true,
  theme: 'dark',
  defaultView: 'grid',
  defaultSort: 'name-asc',
  safeModeDefault: true,
  safeModeOnReload: true,
  nsfwBlurOverlay: true,
  filterFoldersWithBaseModel: false,
  modelsDirectory: '',
  checkpointsDirectory: '',
  defaultDownloadDirectory: '',
  defaultSortingDirectory: '',
  civitaiApiKey: '',
  visibleColumns: {},
  columnOrder: [],
  gridCard: {},
  filenameFormats: [],
  filenameSnakeCase: false,
  modelTypeRoots: [],
  trimNames: [],
  scanSettings: {}
});

onMounted(() => {
  // Initialize local copy
  localSettings.port = settings.port || 8080;
  localSettings.autoOpenBrowser = settings.autoOpenBrowser !== false; // Default true
  localSettings.theme = settings.theme;
  localSettings.defaultView = settings.defaultView;
  localSettings.defaultSort = settings.defaultSort;
  localSettings.safeModeDefault = settings.safeModeDefault !== false; // Default true
  localSettings.safeModeOnReload = settings.safeModeOnReload !== false; // Default true
  localSettings.nsfwBlurOverlay = settings.nsfwBlurOverlay !== false; // Default true
  localSettings.filterFoldersWithBaseModel = settings.filterFoldersWithBaseModel || false;
  localSettings.filenameSnakeCase = settings.filenameSnakeCase || false;
  localSettings.modelsDirectory = settings.modelsDirectory;
  localSettings.checkpointsDirectory = settings.checkpointsDirectory;
  localSettings.defaultDownloadDirectory = settings.defaultDownloadDirectory;
  localSettings.defaultSortingDirectory = settings.defaultSortingDirectory;
  localSettings.civitaiApiKey = settings.civitaiApiKey || '';
  localSettings.visibleColumns = JSON.parse(JSON.stringify(settings.visibleColumns || {}));
  
  // Ensure columnOrder has all visibleColumns keys
  const defaultOrder = ['thumbnail', 'name', 'civitaiName', 'baseModel', 'category', 'size', 'date', 'filename'];
  let currentOrder = Array.isArray(settings.columnOrder) ? [...settings.columnOrder] : defaultOrder;
  
  // Add any missing columns to order
  Object.keys(localSettings.visibleColumns).forEach(key => {
    if (!currentOrder.includes(key)) {
      currentOrder.push(key);
    }
  });
  localSettings.columnOrder = currentOrder;
  
  // Grid card defaults
  const defaultGridCard = {
    titleDisplay: 'modelName',
    cardSize: 'medium',
    showNsfwBadge: true,
    showTestedBadge: true,
    showSliderBadge: true,
    badgeStyle: 'full',
    showBaseModel: true,
    showCategory: true,
    showHighLow: true,
    showSliderRange: true,
    showFolder: true,
    truncateFolder: false,
    showActions: true,
    actionsPosition: 'bottom',
    showCopyTriggerWords: true,
    showUrlButton: true,
    showInfoButton: true
  };
  localSettings.gridCard = Object.assign({}, defaultGridCard, settings.gridCard || {});
  
  localSettings.filenameFormats = JSON.parse(JSON.stringify(settings.filenameFormats || [])).map(f => ({
    ...f,
    isCustom: f.baseModel && f.baseModel !== 'Default' && !allBaseModels.value.some(b => b.toLowerCase() === f.baseModel.trim().toLowerCase())
  }));
  localSettings.modelTypeRoots = JSON.parse(JSON.stringify(settings.modelTypeRoots || [])).map(r => ({
    ...r,
    isCustom: r.baseModel && !allBaseModels.value.some(b => b.toLowerCase() === r.baseModel.trim().toLowerCase())
  }));
  localSettings.trimNames = JSON.parse(JSON.stringify(settings.trimNames || []));
  
  if (!modelsStore.models.length && typeof modelsStore.fetchModels === 'function') {
    modelsStore.fetchModels();
  }
  
  const defaultScanSettings = {
    skipExistingData: true,
    skipNsfwPreviews: true,
    downloadMaxSize: false,
    fetchCreatorInfo: true,
    delayBetweenRequests: 0.5
  };
  localSettings.scanSettings = JSON.parse(JSON.stringify(settings.scanSettings || defaultScanSettings));
});

// All base models from library + defaults + current settings
const allBaseModels = computed(() => {
  const set = new Set();
  if (modelsStore.uniqueBaseModels && modelsStore.uniqueBaseModels.length > 0) {
    modelsStore.uniqueBaseModels.forEach(bm => {
      if (bm && typeof bm === 'string' && bm.trim()) set.add(bm.trim());
    });
  }
  // Standard defaults in case models list is empty or minimal
  ['SD 1.5', 'SDXL', 'Pony', 'Illustrious', 'Flux.1 D', 'Flux.1 S', 'NoobAI'].forEach(b => set.add(b));
  // Include existing configured formats & roots
  if (Array.isArray(localSettings.filenameFormats)) {
    localSettings.filenameFormats.forEach(f => {
      if (f.baseModel && f.baseModel !== 'Default' && f.baseModel !== '__custom__' && f.baseModel.trim()) {
        set.add(f.baseModel.trim());
      }
    });
  }
  if (Array.isArray(localSettings.modelTypeRoots)) {
    localSettings.modelTypeRoots.forEach(r => {
      if (r.baseModel && r.baseModel !== '__custom__' && r.baseModel.trim()) {
        set.add(r.baseModel.trim());
      }
    });
  }
  return Array.from(set).sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }));
});

// Available base models for a specific format rule index (excludes base models already defined in other format rules)
const getAvailableBaseModelsForFormat = (currentIndex) => {
  const otherRows = new Set(
    localSettings.filenameFormats
      .filter((f, idx) => idx !== currentIndex && f.baseModel && f.baseModel !== '__custom__')
      .map(f => f.baseModel.trim().toLowerCase())
  );
  
  return allBaseModels.value.filter(bm => {
    const isCurrent = localSettings.filenameFormats[currentIndex]?.baseModel?.trim().toLowerCase() === bm.toLowerCase();
    return isCurrent || !otherRows.has(bm.toLowerCase());
  });
};

const handleFormatSelectChange = (format) => {
  if (format.baseModel === '__custom__') {
    format.baseModel = '';
    format.isCustom = true;
  }
};

// Available base models for a specific root mapping index (excludes base models already defined in other root mappings)
const getAvailableBaseModelsForRoot = (currentIndex) => {
  const otherRows = new Set(
    localSettings.modelTypeRoots
      .filter((r, idx) => idx !== currentIndex && r.baseModel && r.baseModel !== '__custom__')
      .map(r => r.baseModel.trim().toLowerCase())
  );
  
  return allBaseModels.value.filter(bm => {
    const isCurrent = localSettings.modelTypeRoots[currentIndex]?.baseModel?.trim().toLowerCase() === bm.toLowerCase();
    return isCurrent || !otherRows.has(bm.toLowerCase());
  });
};

const handleRootSelectChange = (root) => {
  if (root.baseModel === '__custom__') {
    root.baseModel = '';
    root.isCustom = true;
  }
};

const formatColumnName = (key) => {
  // Convert camelCase to Title Case
  const result = key.replace(/([A-Z])/g, " $1");
  return result.charAt(0).toUpperCase() + result.slice(1);
};

const getColumnInfo = (col) => {
  const meta = {
    thumbnail: { icon: 'fas fa-image', color: '#3498db', desc: 'Cover image thumbnail preview' },
    name: { icon: 'fas fa-signature', color: '#2ecc71', desc: 'Display title / model friendly name' },
    civitaiName: { icon: 'fas fa-globe', color: '#3498db', desc: 'Civitai release version title' },
    baseModel: { icon: 'fas fa-cube', color: '#2ecc71', desc: 'Model architecture (SDXL, Pony, Flux, etc.)' },
    category: { icon: 'fas fa-folder', color: '#3498db', desc: 'Assigned category classification tag' },
    size: { icon: 'fas fa-hdd', color: '#9b59b6', desc: 'File size on disk (MB / GB)' },
    date: { icon: 'fas fa-calendar-alt', color: '#f39c12', desc: 'File creation or modification date' },
    filename: { icon: 'fas fa-file-code', color: '#e67e22', desc: 'Actual filename on disk' }
  };
  return meta[col] || { icon: 'fas fa-columns', color: '#9b59b6', desc: 'Table column display' };
};

const moveColumnUp = (index) => {
  if (index > 0) {
    const arr = localSettings.columnOrder;
    [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]];
  }
};

const moveColumnDown = (index) => {
  if (index < localSettings.columnOrder.length - 1) {
    const arr = localSettings.columnOrder;
    [arr[index + 1], arr[index]] = [arr[index], arr[index + 1]];
  }
};

const addFilenameFormat = () => {
  localSettings.filenameFormats.push({ baseModel: '', format: '', isCustom: false });
};

const removeFilenameFormat = (index) => {
  localSettings.filenameFormats.splice(index, 1);
};

const addModelTypeRoot = () => {
  localSettings.modelTypeRoots.push({ baseModel: '', rootFolder: '', isCustom: false });
};

const removeModelTypeRoot = (index) => {
  localSettings.modelTypeRoots.splice(index, 1);
};

const addTrimName = () => {
  if (newTrimName.value.trim()) {
    const term = newTrimName.value.trim();
    const exists = localSettings.trimNames.some(
      n => n.toLowerCase() === term.toLowerCase()
    );
    
    if (!exists) {
      localSettings.trimNames.push(term);
      localSettings.trimNames.sort((a, b) => {
        const cleanA = a.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
        const cleanB = b.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
        return cleanA.localeCompare(cleanB);
      });
    } else {
      toast.showToast(`"${term}" already exists in the list`, 'warning');
    }
    newTrimName.value = '';
  }
};

const removeTrimName = (index) => {
  localSettings.trimNames.splice(index, 1);
};

const save = async () => {
  saving.value = true;
  // Clean up isCustom UI flags before saving settings payload
  const payload = JSON.parse(JSON.stringify(localSettings));
  if (Array.isArray(payload.filenameFormats)) {
    payload.filenameFormats = payload.filenameFormats.map(f => {
      const { isCustom, ...rest } = f;
      return rest;
    });
  }
  if (Array.isArray(payload.modelTypeRoots)) {
    payload.modelTypeRoots = payload.modelTypeRoots.map(r => {
      const { isCustom, ...rest } = r;
      return rest;
    });
  }
  const success = await settings.saveSettings(payload);
  saving.value = false;
  
  if (success) {
    toast.showToast('Settings saved successfully', 'success');
    emit('close');
  } else {
    toast.showToast('Failed to save settings', 'error');
  }
};

const browseForFolder = async (key) => {
  try {
    const res = await api.browseFolder();
    if (res.status === 'success' && res.path) {
      localSettings[key] = res.path;
    } else if (res.status === 'error') {
      toast.showToast('Failed to open folder browser', 'error');
    }
  } catch (err) {
    console.error("Failed to browse folder", err);
    toast.showToast('Failed to open folder browser', 'error');
  }
};

const cleaningJson = ref(false);
const cleanJsonFiles = async () => {
  cleaningJson.value = true;
  try {
    const response = await fetch('/api/files/clean-json', {
      method: 'POST'
    });
    const result = await response.json();
    if (result.status === 'success') {
      toast.showToast(`Cleaned ${result.cleaned} files successfully!`, 'success');
      if (result.errors && result.errors.length > 0) {
        console.warn('Errors during clean:', result.errors);
        toast.showToast(`${result.errors.length} errors occurred. Check console.`, 'warning');
      }
    } else {
      toast.showToast(result.message || 'Error cleaning JSON files', 'error');
    }
  } catch (err) {
    console.error('Failed to clean json:', err);
    toast.showToast('Failed to trigger JSON clean', 'error');
  } finally {
    cleaningJson.value = false;
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.settings-modal {
  width: 90%;
  max-width: 800px;
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.2em;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-body {
  flex: 1;
  overflow: hidden;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.settings-tabs {
  display: flex;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 2;
  overflow-x: auto;
  scrollbar-width: none;
}

.settings-tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  flex: 1;
  padding: 12px 6px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 0.88em;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.tab-btn:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
}

.tab-btn.active {
  color: var(--color-btn-primary);
  border-bottom-color: var(--color-btn-primary);
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.input-with-button {
  display: flex;
  gap: 10px;
}
.input-with-button .form-control {
  flex-grow: 1;
}
.input-with-button .btn {
  white-space: nowrap;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-group.compact {
  flex-direction: row;
  align-items: center;
}

.setting-group.compact label {
  width: 120px;
  font-size: 0.9em;
  font-weight: bold;
}

.setting-group.compact .form-control {
  flex: 1;
}

.setting-group label {
  font-weight: 600;
  color: var(--color-text);
}

.setting-group small {
  color: var(--color-text-secondary);
  font-size: 0.85em;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.settings-header h3 {
  margin: 0;
  font-size: 1.1em;
  color: var(--color-text);
}

.variables-help {
  font-size: 0.85em;
  color: var(--color-text-secondary);
}

.warning-text {
  color: #f39c12;
  font-size: 0.85em;
  margin-bottom: 15px;
}

.list-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.col-left {
  flex: 0 0 30%;
}

.col-right {
  flex: 1;
}

.btn-remove {
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  width: 38px;
  height: 38px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-remove:hover {
  opacity: 0.8;
}

.btn-lock {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: none;
  border-radius: 4px;
  width: 38px;
  height: 38px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: not-allowed;
}

.btn-add-full {
  width: 100%;
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  margin-top: 5px;
  transition: background-color 0.2s;
}

.btn-add-full:hover {
  background-color: var(--color-bg-hover);
}

.form-control {
  padding: 10px 12px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: var(--border-radius-sm);
  font-size: 1em;
  width: 100%;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-btn-primary);
}

.columns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 15px;
}

/* Clean Group Layouts without Card Backgrounds */
.settings-group-clean {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 22px;
  margin-bottom: 22px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.settings-group-clean:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.settings-header-clean {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.settings-header-clean h3 {
  margin: 0;
  font-size: 1.05em;
  font-weight: 600;
  color: var(--color-text, #eee);
  letter-spacing: 0.3px;
}

.settings-header-clean .variables-help {
  font-size: 0.82em;
  color: var(--color-text-secondary, #999);
}

.setting-row-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.checkbox-desc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px 16px;
}

.checkbox-desc-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  padding: 9px 12px;
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.07);
  transition: all 0.2s ease;
}

.checkbox-desc-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.16);
}

.checkbox-desc-item:has(input:checked) {
  background-color: rgba(52, 152, 219, 0.07);
  border-color: rgba(52, 152, 219, 0.28);
}

.checkbox-desc-item input[type="checkbox"] {
  margin-top: 3px;
  cursor: pointer;
  flex-shrink: 0;
  accent-color: var(--color-btn-primary, #3498db);
}

.checkbox-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 100%;
}

.checkbox-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
}

.checkbox-title {
  font-size: 0.92em;
  font-weight: 600;
  color: var(--color-text, #eee);
  line-height: 1.2;
}

.checkbox-desc {
  font-size: 0.8em;
  color: var(--color-text-secondary, #888);
  line-height: 1.3;
}

/* Visual Settings Previews & Badges */
.badge-preview-row {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.preview-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 0.72em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
  flex-shrink: 0;
}

.preview-badge.badge-nsfw {
  background-color: rgba(231, 76, 60, 0.95);
  color: #ffffff;
}

.preview-badge.badge-slider {
  background-color: rgba(155, 89, 182, 0.95);
  color: #ffffff;
}

.preview-badge.badge-tested {
  background-color: rgba(46, 204, 113, 0.95);
  color: #ffffff;
}

.preview-mini-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
}

.preview-mini-icon.badge-nsfw {
  background-color: rgba(231, 76, 60, 0.95);
}

.preview-mini-icon.badge-slider {
  background-color: rgba(155, 89, 182, 0.95);
}

.preview-mini-icon.badge-tested {
  background-color: rgba(46, 204, 113, 0.95);
}

.preview-meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.75em;
  font-weight: 600;
  color: var(--color-text-secondary, #bbb);
  flex-shrink: 0;
}

.preview-mini-action {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 5px;
  background: rgba(35, 35, 35, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.18);
  font-size: 0.75em;
  font-weight: 500;
  color: #ddd;
  flex-shrink: 0;
}

.sub-setting-indent {
  padding: 8px 14px;
  background-color: rgba(255, 255, 255, 0.03);
  border-left: 3px solid var(--color-btn-primary, #3498db);
  border-radius: 4px;
  margin-top: 2px;
}

.setting-hint {
  font-size: 0.85em;
  color: var(--color-text-secondary, #888);
  font-style: italic;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  font-size: 0.92em;
}

/* Table Column Reordering Cards */
.columns-reorder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 10px 14px;
}

.column-reorder-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.07);
  transition: all 0.2s ease;
}

.column-reorder-card:hover {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.16);
}

.column-reorder-card:has(input:checked) {
  background-color: rgba(52, 152, 219, 0.07);
  border-color: rgba(52, 152, 219, 0.28);
}

.column-checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  flex: 1;
  user-select: none;
}

.column-checkbox-label input[type="checkbox"] {
  margin-top: 3px;
  cursor: pointer;
  accent-color: var(--color-btn-primary, #3498db);
  flex-shrink: 0;
}

.column-info-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.reorder-controls {
  display: flex;
  gap: 5px;
}

/* List Header & Row Cards for Formatting & Roots */
.list-header-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 14px 4px 14px;
}

.list-header-col {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.list-row-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 14px;
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.07);
  transition: all 0.2s ease;
}

.list-row-card:hover {
  background-color: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.14);
}

.input-with-label {
  display: flex;
  flex-direction: column;
}

.btn-icon-toggle {
  background-color: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--color-border, #3a3a3a);
  color: var(--color-text-secondary, #aaa);
  border-radius: var(--border-radius-sm, 4px);
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.btn-icon-toggle:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: var(--color-text, #fff);
  border-color: var(--color-btn-primary, #3498db);
}

.section-help {
  margin: 0 0 15px 0;
  color: var(--color-text-secondary);
  font-size: 0.9em;
  line-height: 1.4;
}

.section-help code {
  background-color: rgba(255, 255, 255, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--color-btn-primary, #3498db);
}

.modal-footer {
  padding: 15px 20px;
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.add-tag-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 5px;
}

.tag-chip {
  background-color: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88em;
  font-weight: 500;
  transition: all 0.2s ease;
  color: var(--color-text, #eee);
}

.tag-chip:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.22);
  transform: translateY(-1px);
}

.btn-remove-tag {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1em;
  transition: color 0.2s, transform 0.2s;
  opacity: 0.75;
}

.btn-remove-tag:hover {
  color: #c0392b;
  opacity: 1;
  transform: scale(1.15);
}
</style>

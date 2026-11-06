<template>
  <div class="civitai-scan-view">
    <AppHeader />
    
    <div class="scan-container">
      <div class="scan-header-wrapper">
        <div class="scan-header">
          <div class="scan-header-top-row">
            <h2><i class="fas fa-radar"></i> Manage Library &mdash; {{ isLoras ? 'LoRAs' : 'Checkpoints' }}</h2>
            <div class="header-path-pill" :title="activeDirectoryPath">
              <i class="fas fa-folder-open"></i>
              <span>{{ activeDirectoryPath || 'No directory configured' }}</span>
            </div>
          </div>
          <p class="subtitle">Scan, download missing metadata, and inspect library analytics for your local {{ isLoras ? 'LoRA' : 'Checkpoint' }} collection.</p>
        </div>
      </div>
      
      <!-- Unresolved Items Assistant Section (Positioned ABOVE console & buttons) -->
      <div 
        class="resolution-section" 
        v-if="!isScanning && (failedModels.length > 0 || failedThumbnailModels.length > 0) && !isResolutionDismissed"
      >
        <div class="resolution-header">
          <div class="resolution-title-area">
            <h3>
              <i class="fas fa-wrench text-warning"></i>
              <span>Unresolved Items Assistant</span>
            </h3>
            <p class="resolution-subtitle">
              Some items could not be matched automatically. Provide an override or mark them to stop future lookups.
            </p>
          </div>

          <div class="resolution-header-controls">
            <!-- Tabs -->
            <div class="resolution-tabs">
              <button 
                class="resolution-tab-btn" 
                :class="{ active: activeResolutionTab === 'metadata' }"
                @click="activeResolutionTab = 'metadata'"
                v-if="failedModels.length > 0"
              >
                <i class="fas fa-file-alt"></i>
                Missing Metadata
                <span class="tab-badge">{{ failedModels.length }}</span>
              </button>

              <button 
                class="resolution-tab-btn" 
                :class="{ active: activeResolutionTab === 'thumbnails' }"
                @click="activeResolutionTab = 'thumbnails'"
                v-if="failedThumbnailModels.length > 0"
              >
                <i class="fas fa-image"></i>
                Missing Thumbnails
                <span class="tab-badge">{{ failedThumbnailModels.length }}</span>
              </button>
            </div>

            <!-- Bulk actions & Dismiss -->
            <div class="resolution-global-actions">
              <button 
                v-if="activeResolutionTab === 'metadata' && failedModels.length > 1" 
                class="btn-bulk btn-bulk-meta" 
                @click="ignoreAllModels"
                title="Mark all unresolved metadata models as unmatchable"
              >
                <i class="fas fa-ban"></i>
                Mark All Unmatchable
              </button>

              <button 
                v-if="activeResolutionTab === 'thumbnails' && failedThumbnailModels.length > 1" 
                class="btn-bulk btn-bulk-thumb" 
                @click="ignoreAllThumbnails"
                title="Mark all unresolved models as having no thumbnail"
              >
                <i class="fas fa-eye-slash"></i>
                Mark All as No Thumbnail
              </button>

              <button 
                class="btn-icon-close" 
                @click="isResolutionDismissed = true" 
                title="Dismiss resolution panel"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Metadata Resolution Tab Content -->
        <div class="resolution-tab-content" v-if="activeResolutionTab === 'metadata' && failedModels.length > 0">
          <div class="resolution-items-list">
            <div class="resolution-row" v-for="model in failedModels" :key="model.path">
              <div class="row-left">
                <span class="model-filename" :title="model.filename">{{ model.filename }}</span>
                <span class="model-folder-pill" v-if="model.folder" :title="model.folder">
                  <i class="fas fa-folder"></i> {{ model.folder }}
                </span>
                <span class="row-badge badge-meta-warning">
                  <i class="fas fa-exclamation-triangle"></i> No Metadata Match
                </span>
              </div>

              <div class="row-right">
                <div class="row-input-wrap">
                  <i class="fas fa-link row-input-icon"></i>
                  <input 
                    type="text" 
                    class="row-input" 
                    v-model="fallbackUrlMap[model.path]" 
                    placeholder="Civitai / CivArchive URL..."
                    @keyup.enter="resolveManualUrl(model)"
                  />
                </div>

                <button 
                  class="btn-row-action btn-fetch" 
                  @click="resolveManualUrl(model)" 
                  :disabled="!fallbackUrlMap[model.path]"
                  title="Fetch metadata from manual URL"
                >
                  <i class="fas fa-cloud-download-alt"></i> Fetch
                </button>

                <button 
                  class="btn-row-action btn-unmatchable" 
                  @click="ignoreModel(model)"
                  title="Mark model as unmatchable so it won't be scanned again"
                >
                  <i class="fas fa-ban"></i> Mark Unmatchable
                </button>

                <button 
                  class="btn-row-dismiss" 
                  @click="dismissMetadataModel(model)"
                  title="Dismiss from list"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Thumbnails Resolution Tab Content -->
        <div class="resolution-tab-content" v-if="activeResolutionTab === 'thumbnails' && failedThumbnailModels.length > 0">
          <div class="resolution-items-list">
            <div class="resolution-row" v-for="model in failedThumbnailModels" :key="model.path">
              <div class="row-left">
                <span class="model-filename" :title="model.filename">{{ model.filename }}</span>
                <span class="model-folder-pill" v-if="model.folder" :title="model.folder">
                  <i class="fas fa-folder"></i> {{ model.folder }}
                </span>
                <span class="row-badge badge-thumb-warning">
                  <i class="fas fa-image"></i> No Preview Online
                </span>
              </div>

              <div class="row-right">
                <div class="row-input-wrap">
                  <i class="fas fa-image row-input-icon"></i>
                  <input 
                    type="text" 
                    class="row-input" 
                    v-model="fallbackImageUrlMap[model.path]" 
                    placeholder="Optional: Direct image URL..."
                    @keyup.enter="downloadCustomThumbnail(model)"
                  />
                </div>

                <button 
                  v-if="fallbackImageUrlMap[model.path]"
                  class="btn-row-action btn-save-image" 
                  @click="downloadCustomThumbnail(model)"
                  title="Download and save preview image from URL"
                >
                  <i class="fas fa-download"></i> Save
                </button>

                <button 
                  class="btn-row-action btn-no-thumb" 
                  @click="ignoreThumbnail(model)"
                  title="Mark this model as having no thumbnail available"
                >
                  <i class="fas fa-eye-slash"></i> No Thumbnail Available
                </button>

                <button 
                  class="btn-row-dismiss" 
                  @click="dismissThumbnailModel(model)"
                  title="Dismiss from list"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="scan-main-layout">
        <!-- Left Column: Controls -->
        <div class="scan-controls-col">
          <!-- Decision-Making Stats Bar -->
          <div class="scan-stats">
            <div class="stat-box stat-box-total">
              <div class="stat-top">
                <i class="fas fa-layer-group stat-icon"></i>
                <span class="stat-label">Total {{ isLoras ? 'LoRAs' : 'Checkpoints' }}</span>
              </div>
              <div class="stat-value">{{ totalModels.toLocaleString() }}</div>
            </div>

            <div class="stat-box stat-box-meta" :class="{ 'has-missing': missingMetadata > 0 }">
              <div class="stat-top">
                <i class="fas fa-file-alt stat-icon"></i>
                <span class="stat-label">Missing MetaData</span>
              </div>
              <div class="stat-value" :class="missingMetadata > 0 ? 'text-danger' : 'text-muted'">{{ missingMetadata }}</div>
            </div>

            <div class="stat-box stat-box-thumbs" :class="{ 'has-missing': missingThumbnails > 0 }">
              <div class="stat-top">
                <i class="fas fa-image stat-icon"></i>
                <span class="stat-label">Missing Thumbnails</span>
              </div>
              <div class="stat-value" :class="missingThumbnails > 0 ? 'text-danger' : 'text-muted'">{{ missingThumbnails }}</div>
            </div>

            <div class="stat-box stat-box-hashes" :class="{ 'has-missing': missingHashes > 0 }">
              <div class="stat-top">
                <i class="fas fa-hashtag stat-icon"></i>
                <span class="stat-label">Missing Hashes</span>
              </div>
              <div class="stat-value" :class="missingHashes > 0 ? 'text-danger' : 'text-muted'">{{ missingHashes }}</div>
            </div>

            <div class="stat-box stat-box-unchecked" :class="{ 'has-missing': uncheckedOnlineCount > 0 }">
              <div class="stat-top">
                <i class="fas fa-globe stat-icon"></i>
                <span class="stat-label">Unchecked Status</span>
              </div>
              <div class="stat-value" :class="uncheckedOnlineCount > 0 ? 'text-warning' : 'text-muted'">{{ uncheckedOnlineCount }}</div>
            </div>
          </div>

          <div class="scan-actions" v-if="!isScanning && !isMovingDownloads">
            <!-- 1. Import from Downloads (Top Position, above All-in-One Scan) -->
            <div class="action-group import-downloads">
              <div class="action-group-header">
                <i class="fas fa-exchange-alt group-header-icon text-info"></i>
                <div class="group-title-wrap">
                  <h3>Import from Downloads</h3>
                  <span class="dir-hint" v-if="downloadDirName">
                    <span :title="settingsStore.defaultDownloadDirectory">{{ downloadDirName }}</span>
                    <i class="fas fa-arrow-right dir-arrow"></i>
                    <span :title="settingsStore.defaultSortingDirectory">{{ sortingDirName }}</span>
                  </span>
                </div>
              </div>
              <p class="action-desc">
                Look for Safetensor models and their associated files and move them from the Download Directory to the Sorting Directory.
              </p>
              <button 
                class="btn btn-action btn-import-scan" 
                :class="{ 'has-pending': pendingDownloadsCount > 0 }"
                :disabled="isMovingDownloads" 
                @click="sortDownloadedModels"
              >
                <i class="fas" :class="isMovingDownloads ? 'fa-spinner fa-spin' : 'fa-exchange-alt text-info'"></i>
                <span>{{ isMovingDownloads ? 'Moving Files...' : `Move Files (${pendingDownloadsCount})` }}</span>
              </button>
            </div>

            <!-- 2. All-in-One Scan -->
            <div class="action-group all-in-one">
              <div class="action-group-header">
                <i class="fas fa-bolt group-header-icon text-warning"></i>
                <div class="group-title-wrap">
                  <h3>All-in-One Comprehensive Scan</h3>
                  <span class="all-in-one-tag">Executes Steps 1 &ndash; 4 In One Pass</span>
                </div>
              </div>
              <p class="action-desc">
                Runs all four steps below in sequence (Check Online Availability &rarr; Generate SHA256 Hashes &rarr; Scrape Metadata &rarr; Download Thumbnails) in a single unified command.
              </p>
              <button class="btn btn-primary-scan btn-large" @click="runAllInOne">
                <i class="fas fa-bolt"></i> Run All-in-One Scan (All 4 Steps) &bull; {{ allInOneTargetsCount }} Items
              </button>
            </div>
            


            
            <div class="action-columns">
              <!-- Step 1: Check Online Availability -->
              <div class="action-col">
                <div class="card-header-bar">
                  <span class="step-badge">1</span>
                  <i class="fas fa-globe header-icon text-success"></i>
                  <h3>Check Online Availability</h3>
                </div>
                <p class="action-desc">Audit whether models are still live on Civitai or preserved on CivArchive.</p>
                <div class="availability-btn-grid">
                  <button class="btn btn-action btn-availability btn-availability-unchecked" @click="checkUncheckedAvailability" :disabled="uncheckedOnlineCount === 0" title="Check models that have not been audited for online availability yet">
                    <i class="fas fa-question-circle text-warning"></i> Check Unchecked ({{ uncheckedOnlineCount }})
                  </button>
                  <button class="btn btn-action btn-availability" @click="checkCivitaiAvailability" :disabled="onlineCivitaiCount === 0" title="Check availability of models currently marked as active on Civitai">
                    <i class="fas fa-check-circle text-info"></i> Civitai ({{ onlineCivitaiCount }})
                  </button>
                  <button class="btn btn-action btn-availability" @click="checkCivArchiveAvailability" :disabled="onlineCivArchiveCount === 0" title="Check availability of models currently on CivArchive">
                    <i class="fas fa-archive text-purple"></i> Archive ({{ onlineCivArchiveCount }})
                  </button>
                  <button class="btn btn-action btn-availability btn-availability-primary" @click="checkOnlineAvailability" title="Scan all eligible models (skips models already verified offline on both platforms)">
                    <i class="fas fa-globe text-success"></i> Check All Eligible ({{ availabilityScanTargetsCount }})
                  </button>
                </div>
              </div>

              <!-- Step 2: Generate Hashes -->
              <div class="action-col">
                <div class="card-header-bar">
                  <span class="step-badge">2</span>
                  <i class="fas fa-hashtag header-icon text-purple"></i>
                  <h3>Generate SHA256 Hashes</h3>
                </div>
                <p class="action-desc">Generate SHA256 checksums used for exact Civitai lookups and duplicate detection.</p>
                <div class="btn-row">
                  <button class="btn btn-action" @click="generateMissingHashes">
                    <i class="fas fa-hashtag text-purple"></i> Generate Missing ({{ missingHashes }})
                  </button>
                  <button class="btn btn-action" @click="regenerateAllHashes">
                    <i class="fas fa-sync-alt text-info"></i> Regenerate All ({{ totalModels.toLocaleString() }})
                  </button>
                </div>
              </div>

              <!-- Step 3: Scrape Metadata -->
              <div class="action-col">
                <div class="card-header-bar">
                  <span class="step-badge">3</span>
                  <i class="fas fa-cloud-download-alt header-icon text-info"></i>
                  <h3>Scrape Metadata</h3>
                </div>
                <p class="action-desc">Fetch model info from Civitai or CivArchive using file hashes.</p>
                <div class="btn-row">
                  <button class="btn btn-action" @click="fetchMissingData('civitai')">
                    <i class="fas fa-cloud-download-alt text-info"></i> Fetch Missing Metadata ({{ missingMetadata }})
                  </button>
                </div>
              </div>
              
              <!-- Step 4: Download Thumbnails -->
              <div class="action-col">
                <div class="card-header-bar">
                  <span class="step-badge">4</span>
                  <i class="fas fa-image header-icon text-warning"></i>
                  <h3>Download Thumbnails</h3>
                </div>
                <p class="action-desc">Download preview images from Civitai and standardize thumbnail filenames for compatibility.</p>
                <div class="btn-row">
                  <button class="btn btn-action" @click="getMissingThumbnails">
                    <i class="fas fa-image text-warning"></i> Get Missing ({{ missingThumbnails }})
                  </button>
                  <button class="btn btn-action" @click="getAllThumbnails">
                    <i class="fas fa-images text-info"></i> Get All ({{ totalModels.toLocaleString() }})
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="active-scan-box" v-else-if="isScanning">
            <h3 style="margin-top: 0;">Scanning in progress...</h3>
            <button class="btn btn-danger btn-large" @click="stopScan">
              <i class="fas fa-stop"></i> Stop Scan
            </button>
          </div>

          <div class="active-scan-box" v-else-if="isMovingDownloads">
            <h3 style="margin-top: 0;"><i class="fas fa-spinner fa-spin text-info"></i> Moving Downloaded Models...</h3>
            <p class="subtitle" style="margin-top: 5px;">Transferring incoming models and sidecars to sorting directory.</p>
          </div>
          
          <div class="progress-section" v-if="isScanning || scanComplete || isMovingDownloads">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            </div>
            <div class="progress-text">
              <span v-if="isMovingDownloads">Moving {{ currentIndex }} of {{ currentQueueLength }} models ({{ progressPercentage }}%)</span>
              <span v-else>Processed {{ currentIndex }} of {{ currentQueueLength }} items ({{ progressPercentage }}%)</span>
            </div>
          </div>
        </div>
      
        <!-- Right Column: Logs -->
        <div class="scan-log-col">
          <div class="log-section">
            <div class="log-header-bar">
              <div class="log-header-left">
                <i class="fas fa-terminal terminal-icon"></i>
                <span class="log-title">Scan Console</span>
                <span class="console-status-dot" :class="{ 'is-running': isScanning }"></span>
                <span class="console-status-text">{{ isScanning ? 'Scanning...' : 'Idle' }}</span>
              </div>
              <div class="log-header-right">
                <button v-if="logs.length > 0" class="btn-clear-logs" @click="logs = []" title="Clear console output">
                  <i class="fas fa-trash-alt"></i> Clear
                </button>
              </div>
            </div>
            <div class="log-container" ref="logContainer">
              <div v-for="(log, idx) in logs" :key="idx" class="log-entry" :class="log.type">
                <span class="timestamp">[{{ log.time }}]</span>
                <span class="message">{{ log.message }}</span>
              </div>
              <div v-if="logs.length === 0" class="empty-log">
                <i class="fas fa-terminal empty-icon"></i>
                <div class="empty-title">Ready to scan</div>
                <div class="empty-sub">Select an action on the left to begin scanning.</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Library Info & Statistics Section -->
      <div class="library-info-section">
        <div class="library-info-header">
          <div class="header-titles">
            <h3>
              <i class="fas fa-chart-pie"></i>
              <span>{{ isLoras ? 'LoRA' : 'Checkpoint' }} Library Info</span>
            </h3>
            <p class="subtitle">
              Comprehensive analytics, storage metrics, and architecture breakdown for your {{ isLoras ? 'LoRA' : 'Checkpoint' }} collection.
            </p>
          </div>
          <div class="header-actions">
            <button class="btn btn-action btn-refresh" @click="modelsStore.fetchModels(true)" :disabled="modelsStore.refreshing" title="Refresh library data from disk">
              <i class="fas" :class="modelsStore.refreshing ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i>
              {{ modelsStore.refreshing ? 'Refreshing...' : 'Refresh Library' }}
            </button>
          </div>
        </div>

        <!-- Detailed Metric Cards Grid -->
        <div class="library-metric-grid">
          <!-- Total Models Card -->
          <div class="metric-card metric-card-total">
            <div class="metric-header">
              <span class="metric-label">Total {{ isLoras ? 'LoRAs' : 'Checkpoints' }}</span>
              <i class="fas" :class="isLoras ? 'fa-layer-group' : 'fa-cube'"></i>
            </div>
            <div class="metric-val">{{ totalModels.toLocaleString() }}</div>
            <div class="metric-meta">
              <span>Total Size: <strong>{{ formatBytes(totalLibraryBytes) }}</strong></span>
              <span>Avg: <strong>{{ formatBytes(avgModelSizeBytes) }}</strong></span>
            </div>
          </div>

          <!-- Space Used Card -->
          <div class="metric-card metric-card-space">
            <div class="metric-header">
              <span class="metric-label">Total Space Used</span>
              <i class="fas fa-database text-info"></i>
            </div>
            <div class="metric-val text-info">{{ formatBytes(totalLibraryBytes) }}</div>
            <div class="metric-meta">
              <span>Across <strong>{{ totalModels }}</strong> files</span>
              <span>Largest: <strong>{{ formatBytes(largestModelSize) }}</strong></span>
            </div>
          </div>

          <!-- Online Available Card -->
          <div class="metric-card metric-card-online">
            <div class="metric-header">
              <span class="metric-label">Online Available</span>
              <i class="fas fa-globe text-success"></i>
            </div>
            <div class="metric-val text-success">{{ onlineAvailableCount.toLocaleString() }}</div>
            <div class="metric-meta">
              <span class="pill-badge ci" title="Civitai Online"><i class="fas fa-check-circle"></i> {{ onlineCivitaiCount }} Civitai</span>
              <span class="pill-badge ca" title="CivArchive Online"><i class="fas fa-archive"></i> {{ onlineCivArchiveCount }} Archive</span>
            </div>
          </div>

          <!-- Offline / Removed Card -->
          <div class="metric-card metric-card-offline">
            <div class="metric-header">
              <span class="metric-label">Removed Online (Offline)</span>
              <i class="fas fa-unlink text-danger"></i>
            </div>
            <div class="metric-val" :class="offlineCount > 0 ? 'text-danger' : 'text-muted'">{{ offlineCount.toLocaleString() }}</div>
            <div class="metric-meta">
              <span>Removed from both platforms</span>
              <span v-if="uncheckedOnlineCount > 0" class="text-warning">({{ uncheckedOnlineCount }} unchecked)</span>
            </div>
          </div>

          <!-- Model Types Card -->
          <div class="metric-card metric-card-types">
            <div class="metric-header">
              <span class="metric-label">Model Architectures</span>
              <i class="fas fa-cubes text-purple"></i>
            </div>
            <div class="metric-val text-purple">{{ totalModelTypes }}</div>
            <div class="metric-meta">
              <span>{{ totalCategories }} Categories</span>
              <span>{{ uniqueFoldersCount }} Subfolders</span>
            </div>
          </div>

          <!-- Curation & Testing Card -->
          <div class="metric-card metric-card-curation">
            <div class="metric-header">
              <span class="metric-label">Curation & Testing</span>
              <i class="fas fa-shield-alt text-warning"></i>
            </div>
            <div class="metric-val">
              {{ sfwCount }} <small class="sub-num">SFW</small> / {{ nsfwCount }} <small class="sub-num">NSFW</small>
            </div>
            <div class="metric-meta">
              <span><i class="fas fa-check text-success"></i> {{ testedCount }} Tested</span>
              <span v-if="isLoras"><i class="fas fa-sliders-h text-purple"></i> {{ sliderCount }} Sliders</span>
            </div>
          </div>
        </div>

        <!-- Dynamic Table Container -->
        <div class="library-table-container">
          <div class="table-toolbar">
            <div class="table-tabs">
              <button 
                class="table-tab" 
                :class="{ active: activeTableTab === 'types' }"
                @click="activeTableTab = 'types'"
              >
                <i class="fas fa-cubes"></i> Model Architectures ({{ totalModelTypes }})
              </button>
              <button 
                class="table-tab" 
                :class="{ active: activeTableTab === 'categories' }"
                @click="activeTableTab = 'categories'"
              >
                <i class="fas fa-tags"></i> Categories ({{ totalCategories }})
              </button>
              <button 
                class="table-tab" 
                :class="{ active: activeTableTab === 'online' }"
                @click="activeTableTab = 'online'"
              >
                <i class="fas fa-globe"></i> Online Status Breakdown
              </button>
            </div>

            <div class="table-search" v-if="activeTableTab !== 'online'">
              <i class="fas fa-search search-icon"></i>
              <input 
                type="text" 
                v-model="tableSearchQuery" 
                :placeholder="activeTableTab === 'types' ? 'Filter model types (e.g. SDXL, Flux)...' : 'Filter categories...'"
                class="table-search-input"
              />
              <button v-if="tableSearchQuery" class="clear-search-btn" @click="tableSearchQuery = ''">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>

          <!-- TAB 1: DYNAMIC TABLE OF MODEL TYPES -->
          <div v-if="activeTableTab === 'types'" class="table-responsive">
            <table class="library-data-table">
              <thead>
                <tr>
                  <th class="sortable col-type" @click="toggleModelTypeSort('name')">
                    Model Architecture
                    <i class="fas" :class="getModelTypeSortIcon('name')"></i>
                  </th>
                  <th class="sortable col-count text-right" @click="toggleModelTypeSort('count')">
                    Number of {{ isLoras ? 'LoRAs' : 'Checkpoints' }}
                    <i class="fas" :class="getModelTypeSortIcon('count')"></i>
                  </th>
                  <th class="col-percent text-center">% of Library</th>
                  <th class="sortable col-size text-right" @click="toggleModelTypeSort('size')">
                    Space Used
                    <i class="fas" :class="getModelTypeSortIcon('size')"></i>
                  </th>
                  <th class="col-size-bar">Storage Share</th>
                  <th class="sortable col-avg text-right" @click="toggleModelTypeSort('avgSize')">
                    Avg Size
                    <i class="fas" :class="getModelTypeSortIcon('avgSize')"></i>
                  </th>
                  <th class="sortable col-online text-center" @click="toggleModelTypeSort('online')">
                    Online Status
                    <i class="fas" :class="getModelTypeSortIcon('online')"></i>
                  </th>
                  <th class="col-health text-center">Missing Data</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="type in filteredModelTypes" :key="type.name">
                  <td class="col-type font-bold">
                    <span class="type-badge">{{ type.name }}</span>
                  </td>
                  <td class="col-count text-right font-bold">{{ type.count.toLocaleString() }}</td>
                  <td class="col-percent text-center">
                    <span class="percent-text">{{ type.countPercent }}%</span>
                  </td>
                  <td class="col-size text-right font-bold">{{ formatBytes(type.size) }}</td>
                  <td class="col-size-bar">
                    <div class="storage-bar-wrapper">
                      <div class="storage-bar">
                        <div class="storage-bar-fill" :style="{ width: Math.max(Number(type.sizePercent), 2) + '%' }"></div>
                      </div>
                      <span class="storage-bar-label">{{ type.sizePercent }}%</span>
                    </div>
                  </td>
                  <td class="col-avg text-right text-muted">{{ formatBytes(type.avgSize) }}</td>
                  <td class="col-online text-center">
                    <div class="online-status-tags">
                      <span class="status-tag tag-ci" v-if="type.civitaiOnline > 0" title="Online on Civitai">
                        <i class="fas fa-check-circle"></i> CI: {{ type.civitaiOnline }}
                      </span>
                      <span class="status-tag tag-ca" v-if="type.civArchiveOnline > 0" title="Online on CivArchive">
                        <i class="fas fa-archive"></i> CA: {{ type.civArchiveOnline }}
                      </span>
                      <span class="status-tag tag-off" v-if="type.offline > 0" title="Offline / Removed from both">
                        <i class="fas fa-unlink"></i> Off: {{ type.offline }}
                      </span>
                      <span class="status-tag tag-pending" v-if="type.unchecked > 0" title="Not checked yet">
                        <i class="fas fa-clock"></i> {{ type.unchecked }}
                      </span>
                    </div>
                  </td>
                  <td class="col-health text-center">
                    <span v-if="type.missingMetadata === 0 && type.missingThumbnails === 0" class="status-tag tag-ok">
                      <i class="fas fa-check"></i> Complete
                    </span>
                    <div v-else class="missing-tags">
                      <span v-if="type.missingMetadata > 0" class="status-tag tag-danger" title="Missing metadata JSON">
                        Meta: {{ type.missingMetadata }}
                      </span>
                      <span v-if="type.missingThumbnails > 0" class="status-tag tag-warning" title="Missing preview image">
                        Thumb: {{ type.missingThumbnails }}
                      </span>
                    </div>
                  </td>
                </tr>
                <tr v-if="filteredModelTypes.length === 0">
                  <td colspan="8" class="empty-table-msg">
                    No model types found matching "{{ tableSearchQuery }}"
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="table-total-row">
                  <td><strong>Total ({{ filteredModelTypes.length }} Types)</strong></td>
                  <td class="text-right"><strong>{{ totalFilteredModelsCount.toLocaleString() }}</strong></td>
                  <td class="text-center"><strong>100%</strong></td>
                  <td class="text-right"><strong>{{ formatBytes(totalFilteredModelsBytes) }}</strong></td>
                  <td></td>
                  <td class="text-right"><strong>{{ formatBytes(totalFilteredModelsAvgBytes) }}</strong></td>
                  <td class="text-center">
                    <strong>{{ totalFilteredOnlineCount }} Online / {{ totalFilteredOfflineCount }} Offline</strong>
                  </td>
                  <td class="text-center">
                    <strong>{{ totalFilteredMissingMeta }} Meta / {{ totalFilteredMissingThumbs }} Thumbs</strong>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- TAB 2: CATEGORIES BREAKDOWN -->
          <div v-else-if="activeTableTab === 'categories'" class="table-responsive">
            <table class="library-data-table">
              <thead>
                <tr>
                  <th class="sortable col-type" @click="toggleCategorySort('name')">
                    Category
                    <i class="fas" :class="getCategorySortIcon('name')"></i>
                  </th>
                  <th class="sortable col-count text-right" @click="toggleCategorySort('count')">
                    Number of {{ isLoras ? 'LoRAs' : 'Checkpoints' }}
                    <i class="fas" :class="getCategorySortIcon('count')"></i>
                  </th>
                  <th class="col-percent text-center">% of Library</th>
                  <th class="sortable col-size text-right" @click="toggleCategorySort('size')">
                    Space Used
                    <i class="fas" :class="getCategorySortIcon('size')"></i>
                  </th>
                  <th class="col-size-bar">Storage Share</th>
                  <th class="sortable col-avg text-right" @click="toggleCategorySort('avgSize')">
                    Avg Size
                    <i class="fas" :class="getCategorySortIcon('avgSize')"></i>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="cat in filteredCategories" :key="cat.name">
                  <td class="col-type font-bold">
                    <span class="category-badge">{{ cat.name }}</span>
                  </td>
                  <td class="col-count text-right font-bold">{{ cat.count.toLocaleString() }}</td>
                  <td class="col-percent text-center">
                    <span class="percent-text">{{ cat.countPercent }}%</span>
                  </td>
                  <td class="col-size text-right font-bold">{{ formatBytes(cat.size) }}</td>
                  <td class="col-size-bar">
                    <div class="storage-bar-wrapper">
                      <div class="storage-bar">
                        <div class="storage-bar-fill category-fill" :style="{ width: Math.max(Number(cat.sizePercent), 2) + '%' }"></div>
                      </div>
                      <span class="storage-bar-label">{{ cat.sizePercent }}%</span>
                    </div>
                  </td>
                  <td class="col-avg text-right text-muted">{{ formatBytes(cat.avgSize) }}</td>
                </tr>
                <tr v-if="filteredCategories.length === 0">
                  <td colspan="6" class="empty-table-msg">
                    No categories found matching "{{ tableSearchQuery }}"
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="table-total-row">
                  <td><strong>Total ({{ filteredCategories.length }} Categories)</strong></td>
                  <td class="text-right"><strong>{{ totalFilteredCategoriesCount.toLocaleString() }}</strong></td>
                  <td class="text-center"><strong>100%</strong></td>
                  <td class="text-right"><strong>{{ formatBytes(totalFilteredCategoriesBytes) }}</strong></td>
                  <td></td>
                  <td class="text-right"><strong>{{ formatBytes(totalFilteredCategoriesAvgBytes) }}</strong></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- TAB 3: ONLINE STATUS BREAKDOWN -->
          <div v-else-if="activeTableTab === 'online'" class="online-analytics-panel">
            <div class="online-stacked-bar-container">
              <div class="stacked-bar-title">Overall Online Availability Ratio</div>
              <div class="stacked-bar">
                <div 
                  class="bar-slice slice-ci" 
                  :style="{ width: ((onlineCivitaiCount / Math.max(totalModels, 1)) * 100) + '%' }"
                  :title="'Civitai: ' + onlineCivitaiCount + ' (' + (((onlineCivitaiCount / Math.max(totalModels, 1)) * 100).toFixed(1)) + '%)'"
                ></div>
                <div 
                  class="bar-slice slice-ca" 
                  :style="{ width: ((onlineCivArchiveCount / Math.max(totalModels, 1)) * 100) + '%' }"
                  :title="'CivArchive: ' + onlineCivArchiveCount + ' (' + (((onlineCivArchiveCount / Math.max(totalModels, 1)) * 100).toFixed(1)) + '%)'"
                ></div>
                <div 
                  class="bar-slice slice-off" 
                  :style="{ width: ((offlineCount / Math.max(totalModels, 1)) * 100) + '%' }"
                  :title="'Offline: ' + offlineCount + ' (' + (((offlineCount / Math.max(totalModels, 1)) * 100).toFixed(1)) + '%)'"
                ></div>
                <div 
                  class="bar-slice slice-pending" 
                  :style="{ width: ((uncheckedOnlineCount / Math.max(totalModels, 1)) * 100) + '%' }"
                  :title="'Unchecked: ' + uncheckedOnlineCount + ' (' + (((uncheckedOnlineCount / Math.max(totalModels, 1)) * 100).toFixed(1)) + '%)'"
                ></div>
              </div>
              <div class="stacked-legend">
                <div class="legend-item"><span class="legend-color color-ci"></span> Civitai Available ({{ onlineCivitaiCount }})</div>
                <div class="legend-item"><span class="legend-color color-ca"></span> CivArchive Only ({{ onlineCivArchiveCount }})</div>
                <div class="legend-item"><span class="legend-color color-off"></span> Offline / Removed ({{ offlineCount }})</div>
                <div class="legend-item"><span class="legend-color color-pending"></span> Unchecked ({{ uncheckedOnlineCount }})</div>
              </div>
            </div>

            <div class="online-cards-row">
              <div class="online-detail-card card-ci">
                <div class="detail-icon"><i class="fas fa-check-circle"></i></div>
                <div class="detail-body">
                  <h4>Civitai Available</h4>
                  <div class="detail-count">{{ onlineCivitaiCount }}</div>
                  <p>Active and downloadable on Civitai.</p>
                </div>
              </div>
              <div class="online-detail-card card-ca">
                <div class="detail-icon"><i class="fas fa-archive"></i></div>
                <div class="detail-body">
                  <h4>CivArchive Only</h4>
                  <div class="detail-count">{{ onlineCivArchiveCount }}</div>
                  <p>Removed from Civitai, but preserved in the CivArchive repository.</p>
                </div>
              </div>
              <div class="online-detail-card card-off">
                <div class="detail-icon"><i class="fas fa-unlink"></i></div>
                <div class="detail-body">
                  <h4>Offline / Removed</h4>
                  <div class="detail-count">{{ offlineCount }}</div>
                  <p>Confirmed removed (404) from both Civitai and CivArchive. Safe to hold on to!</p>
                </div>
              </div>
              <div class="online-detail-card card-pending">
                <div class="detail-icon"><i class="fas fa-clock"></i></div>
                <div class="detail-body">
                  <h4>Pending Audit</h4>
                  <div class="detail-count">{{ uncheckedOnlineCount }}</div>
                  <p>Not yet checked for online availability. Click "Check Online Availability" above to audit.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { api } from '../api/client';
import { useModelsStore } from '../stores/models';
import { useSettingsStore } from '../stores/settings';
import { useToast } from '../composables/useToast';
import AppHeader from '../components/layout/AppHeader.vue';

const modelsStore = useModelsStore();
const settingsStore = useSettingsStore();
const toast = useToast();

const isScanning = ref(false);
const scanComplete = ref(false);
const shouldStop = ref(false);
const currentIndex = ref(0);
const currentQueueLength = ref(0);
const logs = ref([]);
const logContainer = ref(null);
const failedModels = ref([]);
const fallbackUrlMap = ref({});
const failedThumbnailModels = ref([]);
const fallbackImageUrlMap = ref({});
const activeResolutionTab = ref('metadata');
const isResolutionDismissed = ref(false);

// Download Import State
const pendingDownloadsCount = ref(0);
const isMovingDownloads = ref(false);

const downloadDirName = computed(() => {
  const dir = settingsStore.defaultDownloadDirectory;
  if (!dir) return '';
  const parts = dir.replace(/\\/g, '/').split('/').filter(Boolean);
  return parts.slice(-2).join('/') || dir;
});

const sortingDirName = computed(() => {
  const dir = settingsStore.defaultSortingDirectory;
  if (!dir) return '';
  const parts = dir.replace(/\\/g, '/').split('/').filter(Boolean);
  return parts.slice(-2).join('/') || dir;
});

const checkDownloadCandidates = async () => {
  try {
    const res = await api.getDownloadCandidates();
    if (res && res.status === 'success') {
      pendingDownloadsCount.value = res.count || 0;
    }
  } catch (e) {
    // Ignore background check failure
  }
};

// State & Location
const isLoras = computed(() => modelsStore.currentLocation === 'loras');
const activeDirectoryPath = computed(() => isLoras.value ? settingsStore.modelsDirectory : settingsStore.checkpointsDirectory);

const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Stats Computed Properties
const totalModels = computed(() => modelsStore.models.length);
const totalLibraryBytes = computed(() => modelsStore.models.reduce((acc, m) => acc + (Number(m.size) || 0), 0));
const avgModelSizeBytes = computed(() => totalModels.value > 0 ? totalLibraryBytes.value / totalModels.value : 0);
const largestModelSize = computed(() => Math.max(0, ...modelsStore.models.map(m => Number(m.size) || 0)));

const getMissingMetadataModels = () => modelsStore.models.filter(m => 
  !m.civitaiUrl && !m.civitai_url && !m.unmatchable && !m.ignored && !m.no_metadata
);
const getMissingThumbnailModels = () => modelsStore.models.filter(m => 
  (!m.previewUrl || m.previewUrl.includes('placeholder')) && !m.noThumbnail && !m.no_thumbnail
);
const getMissingHashModels = () => modelsStore.models.filter(m => !m.sha256);

const missingMetadata = computed(() => getMissingMetadataModels().length);
const missingThumbnails = computed(() => getMissingThumbnailModels().length);
const missingHashes = computed(() => getMissingHashModels().length);

const allInOneTargetsCount = computed(() => {
  const metadataTargets = getMissingMetadataModels();
  const metadataTargetPaths = new Set(metadataTargets.map(m => m.path));
  const otherMissingThumbs = getMissingThumbnailModels().filter(m => !metadataTargetPaths.has(m.path));
  return metadataTargets.length + otherMissingThumbs.length;
});

// Online availability helpers & breakdown
const getCivitaiOnlineModels = () => modelsStore.models.filter(m => {
  const ci = m.civitaiAvailable !== undefined ? m.civitaiAvailable : m.civitai_available;
  return ci === true || String(ci).toLowerCase() === 'true';
});

const getCivArchiveOnlineModels = () => modelsStore.models.filter(m => {
  const ci = m.civitaiAvailable !== undefined ? m.civitaiAvailable : m.civitai_available;
  const ca = m.civarchiveAvailable !== undefined ? m.civarchiveAvailable : m.civarchive_available;
  const ciTrue = ci === true || String(ci).toLowerCase() === 'true';
  const caTrue = ca === true || String(ca).toLowerCase() === 'true';
  return !ciTrue && caTrue;
});

const getUncheckedOnlineModels = () => modelsStore.models.filter(m => {
  const ci = m.civitaiAvailable !== undefined ? m.civitaiAvailable : m.civitai_available;
  const ca = m.civarchiveAvailable !== undefined ? m.civarchiveAvailable : m.civarchive_available;
  const ciTrue = ci === true || String(ci).toLowerCase() === 'true';
  const caTrue = ca === true || String(ca).toLowerCase() === 'true';
  const ciFalse = ci === false || String(ci).toLowerCase() === 'false';
  const caFalse = ca === false || String(ca).toLowerCase() === 'false';
  if (ciTrue || caTrue) return false;
  if (ciFalse && caFalse) return false;
  return true;
});

const onlineCivitaiCount = computed(() => getCivitaiOnlineModels().length);
const onlineCivArchiveCount = computed(() => getCivArchiveOnlineModels().length);
const onlineAvailableCount = computed(() => onlineCivitaiCount.value + onlineCivArchiveCount.value);

const offlineCount = computed(() => {
  return modelsStore.models.filter(m => {
    const ci = m.civitaiAvailable !== undefined ? m.civitaiAvailable : m.civitai_available;
    const ca = m.civarchiveAvailable !== undefined ? m.civarchiveAvailable : m.civarchive_available;
    const ciFalse = ci === false || String(ci).toLowerCase() === 'false';
    const caFalse = ca === false || String(ca).toLowerCase() === 'false';
    return ciFalse && caFalse;
  }).length;
});

const uncheckedOnlineCount = computed(() => getUncheckedOnlineModels().length);

// Health & Curation
const withMetadataCount = computed(() => Math.max(0, totalModels.value - missingMetadata.value));
const withThumbnailsCount = computed(() => Math.max(0, totalModels.value - missingThumbnails.value));
const withHashesCount = computed(() => Math.max(0, totalModels.value - missingHashes.value));
const metadataCoveragePercent = computed(() => totalModels.value > 0 ? ((withMetadataCount.value / totalModels.value) * 100).toFixed(1) : '0');

const nsfwCount = computed(() => modelsStore.models.filter(m => String(m.nsfw).toLowerCase() === 'true').length);
const sfwCount = computed(() => Math.max(0, totalModels.value - nsfwCount.value));
const testedCount = computed(() => modelsStore.models.filter(m => m.tested === true).length);
const untestedCount = computed(() => Math.max(0, totalModels.value - testedCount.value));
const sliderCount = computed(() => modelsStore.models.filter(m => m.isSlider === true || m.slider === true).length);

const uniqueFoldersCount = computed(() => {
  const folders = new Set();
  modelsStore.models.forEach(m => {
    if (m.folder) folders.add(m.folder);
  });
  return folders.size;
});

// Dynamic Table State & Tabs
const activeTableTab = ref('types');
const tableSearchQuery = ref('');
const modelTypeSortBy = ref('count');
const modelTypeSortDesc = ref(true);
const categorySortBy = ref('count');
const categorySortDesc = ref(true);

const toggleModelTypeSort = (column) => {
  if (modelTypeSortBy.value === column) {
    modelTypeSortDesc.value = !modelTypeSortDesc.value;
  } else {
    modelTypeSortBy.value = column;
    modelTypeSortDesc.value = column !== 'name';
  }
};

const getModelTypeSortIcon = (column) => {
  if (modelTypeSortBy.value !== column) return 'fa-sort';
  return modelTypeSortDesc.value ? 'fa-sort-down' : 'fa-sort-up';
};

const toggleCategorySort = (column) => {
  if (categorySortBy.value === column) {
    categorySortDesc.value = !categorySortDesc.value;
  } else {
    categorySortBy.value = column;
    categorySortDesc.value = column !== 'name';
  }
};

const getCategorySortIcon = (column) => {
  if (categorySortBy.value !== column) return 'fa-sort';
  return categorySortDesc.value ? 'fa-sort-down' : 'fa-sort-up';
};

// Model Types Dynamic Analytics
const modelTypesData = computed(() => {
  const totalBytes = totalLibraryBytes.value || 1;
  const totalCount = totalModels.value || 1;
  const map = new Map();

  modelsStore.models.forEach(m => {
    const rawType = m.baseModel || m.sdVersion || 'Unknown';
    const type = rawType.trim() || 'Unknown';

    if (!map.has(type)) {
      map.set(type, {
        name: type,
        count: 0,
        size: 0,
        civitaiOnline: 0,
        civArchiveOnline: 0,
        offline: 0,
        unchecked: 0,
        missingMetadata: 0,
        missingThumbnails: 0
      });
    }

    const item = map.get(type);
    item.count += 1;
    item.size += (Number(m.size) || 0);

    const hasMeta = Boolean(m.civitaiUrl || m.civitai_url);
    if (!hasMeta) item.missingMetadata += 1;

    const hasThumb = Boolean(m.previewUrl && !m.previewUrl.includes('placeholder'));
    if (!hasThumb) item.missingThumbnails += 1;

    const ci = m.civitaiAvailable !== undefined ? m.civitaiAvailable : m.civitai_available;
    const ca = m.civarchiveAvailable !== undefined ? m.civarchiveAvailable : m.civarchive_available;
    const ciTrue = ci === true || String(ci).toLowerCase() === 'true';
    const ciFalse = ci === false || String(ci).toLowerCase() === 'false';
    const caTrue = ca === true || String(ca).toLowerCase() === 'true';
    const caFalse = ca === false || String(ca).toLowerCase() === 'false';

    if (ciTrue) {
      item.civitaiOnline += 1;
    } else if (caTrue) {
      item.civArchiveOnline += 1;
    } else if (ciFalse && caFalse) {
      item.offline += 1;
    } else {
      item.unchecked += 1;
    }
  });

  return Array.from(map.values()).map(item => {
    const onlineTotal = item.civitaiOnline + item.civArchiveOnline;
    return {
      ...item,
      countPercent: ((item.count / totalCount) * 100).toFixed(1),
      sizePercent: ((item.size / totalBytes) * 100).toFixed(1),
      avgSize: item.count > 0 ? item.size / item.count : 0,
      onlineTotal,
      onlinePercent: item.count > 0 ? ((onlineTotal / item.count) * 100).toFixed(0) : '0'
    };
  });
});

const totalModelTypes = computed(() => modelTypesData.value.length);

const filteredModelTypes = computed(() => {
  let list = modelTypesData.value;
  if (tableSearchQuery.value.trim() && activeTableTab.value === 'types') {
    const q = tableSearchQuery.value.toLowerCase().trim();
    list = list.filter(t => t.name.toLowerCase().includes(q));
  }

  return [...list].sort((a, b) => {
    let diff = 0;
    if (modelTypeSortBy.value === 'name') {
      diff = a.name.localeCompare(b.name);
    } else if (modelTypeSortBy.value === 'count') {
      diff = a.count - b.count;
    } else if (modelTypeSortBy.value === 'size') {
      diff = a.size - b.size;
    } else if (modelTypeSortBy.value === 'avgSize') {
      diff = a.avgSize - b.avgSize;
    } else if (modelTypeSortBy.value === 'online') {
      diff = a.onlineTotal - b.onlineTotal;
    }
    return modelTypeSortDesc.value ? -diff : diff;
  });
});

const totalFilteredModelsCount = computed(() => filteredModelTypes.value.reduce((acc, t) => acc + t.count, 0));
const totalFilteredModelsBytes = computed(() => filteredModelTypes.value.reduce((acc, t) => acc + t.size, 0));
const totalFilteredModelsAvgBytes = computed(() => totalFilteredModelsCount.value > 0 ? totalFilteredModelsBytes.value / totalFilteredModelsCount.value : 0);
const totalFilteredOnlineCount = computed(() => filteredModelTypes.value.reduce((acc, t) => acc + t.onlineTotal, 0));
const totalFilteredOfflineCount = computed(() => filteredModelTypes.value.reduce((acc, t) => acc + t.offline, 0));
const totalFilteredMissingMeta = computed(() => filteredModelTypes.value.reduce((acc, t) => acc + t.missingMetadata, 0));
const totalFilteredMissingThumbs = computed(() => filteredModelTypes.value.reduce((acc, t) => acc + t.missingThumbnails, 0));

// Categories Dynamic Analytics
const categoriesData = computed(() => {
  const totalBytes = totalLibraryBytes.value || 1;
  const totalCount = totalModels.value || 1;
  const map = new Map();

  modelsStore.models.forEach(m => {
    const rawCat = m.category || 'Uncategorized';
    const cat = rawCat.trim() || 'Uncategorized';

    if (!map.has(cat)) {
      map.set(cat, {
        name: cat,
        count: 0,
        size: 0
      });
    }

    const item = map.get(cat);
    item.count += 1;
    item.size += (Number(m.size) || 0);
  });

  return Array.from(map.values()).map(item => ({
    ...item,
    countPercent: ((item.count / totalCount) * 100).toFixed(1),
    sizePercent: ((item.size / totalBytes) * 100).toFixed(1),
    avgSize: item.count > 0 ? item.size / item.count : 0
  }));
});

const totalCategories = computed(() => categoriesData.value.length);

const filteredCategories = computed(() => {
  let list = categoriesData.value;
  if (tableSearchQuery.value.trim() && activeTableTab.value === 'categories') {
    const q = tableSearchQuery.value.toLowerCase().trim();
    list = list.filter(c => c.name.toLowerCase().includes(q));
  }

  return [...list].sort((a, b) => {
    let diff = 0;
    if (categorySortBy.value === 'name') {
      diff = a.name.localeCompare(b.name);
    } else if (categorySortBy.value === 'count') {
      diff = a.count - b.count;
    } else if (categorySortBy.value === 'size') {
      diff = a.size - b.size;
    } else if (categorySortBy.value === 'avgSize') {
      diff = a.avgSize - b.avgSize;
    }
    return categorySortDesc.value ? -diff : diff;
  });
});

const totalFilteredCategoriesCount = computed(() => filteredCategories.value.reduce((acc, c) => acc + c.count, 0));
const totalFilteredCategoriesBytes = computed(() => filteredCategories.value.reduce((acc, c) => acc + c.size, 0));
const totalFilteredCategoriesAvgBytes = computed(() => totalFilteredCategoriesCount.value > 0 ? totalFilteredCategoriesBytes.value / totalFilteredCategoriesCount.value : 0);

const getAvailabilityScanModels = () => modelsStore.models.filter(m => {
  const ci = m.civitaiAvailable !== undefined ? m.civitaiAvailable : m.civitai_available;
  const ca = m.civarchiveAvailable !== undefined ? m.civarchiveAvailable : m.civarchive_available;
  const ciFalse = ci === false || String(ci).toLowerCase() === 'false';
  const caFalse = ca === false || String(ca).toLowerCase() === 'false';
  return !(ciFalse && caFalse);
});

const availabilityScanTargetsCount = computed(() => getAvailabilityScanModels().length);

const progressPercentage = computed(() => {
  if (currentQueueLength.value === 0) return 0;
  return Math.round((currentIndex.value / currentQueueLength.value) * 100);
});

onMounted(async () => {
  await settingsStore.fetchSettings();
  await checkDownloadCandidates();
  if (modelsStore.models.length === 0) {
    await modelsStore.fetchModels();
  }
});

const addLog = (message, type = 'info') => {
  const time = new Date().toLocaleTimeString();
  logs.value.push({ time, message, type });
  
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  });
};

const stopScan = () => {
  shouldStop.value = true;
  addLog('Scan stopping after current task finishes...', 'warning');
};

// Unified Queue Engine
const runScanQueue = async (tasks) => {
  if (tasks.length === 0) {
    addLog('No tasks to run.', 'warning');
    return;
  }
  
  isScanning.value = true;
  scanComplete.value = false;
  shouldStop.value = false;
  isResolutionDismissed.value = false;
  currentIndex.value = 0;
  currentQueueLength.value = tasks.length;
  logs.value = [];
  
  let successCount = 0;
  let errorCount = 0;
  
  addLog(`Starting scan queue with ${tasks.length} tasks...`, 'info');
  
  for (let i = 0; i < tasks.length; i++) {
    if (shouldStop.value) {
      addLog('Scan aborted by user.', 'warning');
      break;
    }
    
    const task = tasks[i];
    currentIndex.value = i + 1;
    
    addLog(`[${currentIndex.value}/${tasks.length}] ${task.actionName}: ${task.model.filename}...`, 'info');
    
    try {
      await task.actionFn(task.model);
      successCount++;
    } catch (err) {
      errorCount++;
      const detail = err?.response?.status === 404
        ? 'Backend route not found — please restart the Lora Manager server'
        : (err?.response?.data?.message || err?.message || '');
      addLog(`ERROR: ${task.actionName} failed for ${task.model.filename}${detail ? ` (${detail})` : ''}.`, 'error');
      
      // Track metadata failures specifically
      if (task.actionName === 'Fetch Metadata' || task.actionName === 'Fetch from CivArchive' || task.actionName === 'Process Metadata & Thumbnails') {
        if (!failedModels.value.some(m => m.path === task.model.path)) {
          failedModels.value.push(task.model);
        }
      }
      if (task.actionName === 'Download Thumbnail') {
        if (!failedThumbnailModels.value.some(m => m.path === task.model.path)) {
          failedThumbnailModels.value.push(task.model);
        }
      }
    }
    
    // Delay between requests to respect API rate limits
    const delayS = settingsStore.scanSettings?.delayBetweenRequests || 0.5;
    await new Promise(r => setTimeout(r, delayS * 1000));
  }
  
  isScanning.value = false;
  scanComplete.value = true;
  addLog(`Queue complete! Success: ${successCount}, Failed: ${errorCount}`, 'info');

  if (failedModels.value.length > 0) {
    activeResolutionTab.value = 'metadata';
  } else if (failedThumbnailModels.value.length > 0) {
    activeResolutionTab.value = 'thumbnails';
  }
  
  // Refresh store
  await modelsStore.fetchModels();
};

// Queue Builders
const fetchMissingData = (source = 'civitai') => {
  const targets = getMissingMetadataModels();
  if (targets.length === 0) {
    addLog('No missing metadata found. All models have metadata or are marked as unmatchable!', 'success');
    return;
  }
  failedModels.value = [];
  activeResolutionTab.value = 'metadata';

  const tasks = targets.map(model => ({
    model,
    actionName: source === 'civarchive' ? 'Fetch from CivArchive' : 'Fetch Metadata',
    actionFn: async (m) => {
      const res = source === 'civarchive' 
        ? await api.civArchiveFetchByHash(m.path) 
        : await api.civitaiFetchByHash(m.path);
        
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'not_found') throw new Error('not found');
      if (res && res.status === 'error') throw new Error(res.message);
    }
  }));
  runScanQueue(tasks);
};

const getMissingThumbnails = () => {
  const targets = getMissingThumbnailModels();
  if (targets.length === 0) {
    addLog('No missing thumbnails found. All models have thumbnails or are marked as unavailable!', 'success');
    return;
  }

  const skipNsfw = settingsStore.scanSettings?.skipNsfwPreviews === true;
  const maxSize = settingsStore.scanSettings?.downloadMaxSize === true;
  failedThumbnailModels.value = [];
  activeResolutionTab.value = 'thumbnails';
  
  const tasks = targets.map(model => ({
    model,
    actionName: 'Download Thumbnail',
    actionFn: async (m) => {
      const res = await api.civitaiDownloadPreview(m.path, skipNsfw, maxSize, false);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
      if (res && res.status === 'skipped') {
        addLog(`SKIPPED: ${m.filename} (${res.message || 'No thumbnail found'})`, 'warning');
        if (!failedThumbnailModels.value.some(f => f.path === m.path)) {
          failedThumbnailModels.value.push(m);
        }
      }
    }
  }));
  runScanQueue(tasks);
};

const getAllThumbnails = () => {
  const targets = modelsStore.models;
  const skipNsfw = settingsStore.scanSettings?.skipNsfwPreviews === true;
  const maxSize = settingsStore.scanSettings?.downloadMaxSize === true;
  
  const tasks = targets.map(model => ({
    model,
    actionName: 'Download Thumbnail',
    actionFn: async (m) => {
      const res = await api.civitaiDownloadPreview(m.path, skipNsfw, maxSize, true);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
      if (res && res.status === 'skipped') {
        addLog(`SKIPPED: ${m.filename} (${res.message || 'No thumbnail found'})`, 'warning');
      }
    }
  }));
  runScanQueue(tasks);
};

const generateMissingHashes = () => {
  const targets = getMissingHashModels();
  const tasks = targets.map(model => ({
    model,
    actionName: 'Generate Hash',
    actionFn: async (m) => {
      const res = await api.civitaiGenerateHash(m.path, true);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
      if (res && res.status === 'success' && !res.logs) {
        addLog(`Hash generated successfully for ${m.filename}`, 'success');
      }
    }
  }));
  runScanQueue(tasks);
};

const regenerateAllHashes = () => {
  const targets = modelsStore.models;
  const tasks = targets.map(model => ({
    model,
    actionName: 'Regenerate Hash',
    actionFn: async (m) => {
      const res = await api.civitaiGenerateHash(m.path, false);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
      if (res && res.status === 'success' && !res.logs) {
        addLog(`Hash regenerated successfully for ${m.filename}`, 'success');
      }
    }
  }));
  runScanQueue(tasks);
};

const checkOnlineAvailability = () => {
  const targets = getAvailabilityScanModels();
  if (targets.length === 0) {
    addLog('No eligible models to check for online availability.', 'warning');
    return;
  }
  const tasks = targets.map(model => ({
    model,
    actionName: 'Check Online Availability',
    actionFn: async (m) => {
      const res = await api.civitaiCheckAvailability(m.path, false);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
    }
  }));
  runScanQueue(tasks);
};

const checkCivitaiAvailability = () => {
  const targets = getCivitaiOnlineModels();
  if (targets.length === 0) {
    addLog('No models currently marked on Civitai to check.', 'warning');
    return;
  }
  const tasks = targets.map(model => ({
    model,
    actionName: 'Check Civitai Availability',
    actionFn: async (m) => {
      const res = await api.civitaiCheckAvailability(m.path, false);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
    }
  }));
  runScanQueue(tasks);
};

const checkCivArchiveAvailability = () => {
  const targets = getCivArchiveOnlineModels();
  if (targets.length === 0) {
    addLog('No models currently marked on CivArchive to check.', 'warning');
    return;
  }
  const tasks = targets.map(model => ({
    model,
    actionName: 'Check CivArchive Availability',
    actionFn: async (m) => {
      const res = await api.civitaiCheckAvailability(m.path, false);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
    }
  }));
  runScanQueue(tasks);
};

const checkUncheckedAvailability = () => {
  const targets = getUncheckedOnlineModels();
  if (targets.length === 0) {
    addLog('No unchecked models found. All models have already been audited!', 'success');
    return;
  }
  const tasks = targets.map(model => ({
    model,
    actionName: 'Check Unchecked Availability',
    actionFn: async (m) => {
      const res = await api.civitaiCheckAvailability(m.path, false);
      if (res && res.logs) {
        res.logs.forEach(log => {
          const msg = typeof log === 'object' ? log.message : log;
          const type = typeof log === 'object' ? log.type : 'info';
          addLog(msg, type);
        });
      }
      if (res && res.status === 'error') throw new Error(res.message);
    }
  }));
  runScanQueue(tasks);
};

const runAllInOne = () => {
  failedModels.value = [];
  failedThumbnailModels.value = [];
  
  // Step 1: Missing metadata targets (fetch metadata & auto-download thumbnails)
  const metadataTargets = getMissingMetadataModels();
  const tasks = [];
  
  metadataTargets.forEach(model => {
    tasks.push({
      model,
      actionName: 'Process Metadata & Thumbnails',
      actionFn: async (m) => {
        const res = await api.civitaiFetchByHash(m.path);
        if (res && res.logs) {
          res.logs.forEach(log => {
            const msg = typeof log === 'object' ? log.message : log;
            const type = typeof log === 'object' ? log.type : 'info';
            addLog(msg, type);
          });
        }
        if (res && res.status === 'not_found') throw new Error('not found');
        if (res && res.status === 'error') throw new Error(res.message);
        
        // If metadata saved but preview skipped / missing
        if (res && res.status === 'success' && res.previewSuccess === false) {
          if (!failedThumbnailModels.value.some(f => f.path === m.path)) {
            failedThumbnailModels.value.push(m);
          }
        }
      }
    });
  });
  
  // Step 2: Models that already had metadata but are missing thumbnails
  const metadataTargetPaths = new Set(metadataTargets.map(m => m.path));
  const otherMissingThumbs = getMissingThumbnailModels().filter(m => !metadataTargetPaths.has(m.path));
  const skipNsfw = settingsStore.scanSettings?.skipNsfwPreviews === true;
  const maxSize = settingsStore.scanSettings?.downloadMaxSize === true;
  
  otherMissingThumbs.forEach(model => {
    tasks.push({
      model,
      actionName: 'Download Thumbnail',
      actionFn: async (m) => {
        const res = await api.civitaiDownloadPreview(m.path, skipNsfw, maxSize, false);
        if (res && res.logs) {
          res.logs.forEach(log => {
            const msg = typeof log === 'object' ? log.message : log;
            const type = typeof log === 'object' ? log.type : 'info';
            addLog(msg, type);
          });
        }
        if (res && res.status === 'error') throw new Error(res.message);
        if (res && res.status === 'skipped') {
          addLog(`SKIPPED: ${m.filename} (${res.message || 'No thumbnail found'})`, 'warning');
          if (!failedThumbnailModels.value.some(f => f.path === m.path)) {
            failedThumbnailModels.value.push(m);
          }
        }
      }
    });
  });

  if (tasks.length === 0) {
    addLog('No missing metadata or thumbnails to process!', 'success');
    return;
  }
  
  runScanQueue(tasks);
};

const resolveManualUrl = async (model) => {
  const url = fallbackUrlMap.value[model.path];
  if (!url) {
    addLog(`No URL provided for ${model.filename}`, 'warning');
    return;
  }
  
  try {
    addLog(`Manual fetch for ${model.filename} from ${url}...`, 'info');
    const res = await api.civitaiFetchByUrl(model.path, url);
    if (res && res.status === 'error') throw new Error(res.message);
    
    addLog(`SUCCESS: Manual fetch for ${model.filename}`, 'success');
    toast.showToast(`Fetched metadata for ${model.filename}`, 'success');
    
    // Remove from failed list
    failedModels.value = failedModels.value.filter(m => m.path !== model.path);
    
    // Refresh models
    await modelsStore.fetchModels();
  } catch (e) {
    addLog(`ERROR: Manual fetch failed for ${model.filename}`, 'error');
    toast.showToast(`Failed to fetch metadata from URL`, 'error');
  }
};

const ignoreModel = async (model) => {
  try {
    addLog(`Marking ${model.filename} as unmatchable...`, 'info');
    const res = await api.civitaiFetchByUrl(model.path, 'https://no-match.com/ignored');
    if (res && res.status === 'error') throw new Error(res.message);
    
    failedModels.value = failedModels.value.filter(m => m.path !== model.path);
    addLog(`SUCCESS: Marked ${model.filename} as unmatchable`, 'success');
    toast.showToast(`Marked ${model.filename} as unmatchable`, 'info');
    await modelsStore.fetchModels();
  } catch (e) {
    addLog(`ERROR: Failed to mark ${model.filename} as unmatchable`, 'error');
    toast.showToast('Failed to mark model as unmatchable', 'error');
  }
};

const ignoreAllModels = async () => {
  if (failedModels.value.length === 0) return;
  const paths = failedModels.value.map(m => m.path);
  try {
    addLog(`Bulk marking ${paths.length} models as unmatchable...`, 'info');
    const res = await api.civitaiIgnoreModelsBulk(paths);
    if (res && res.status === 'error') throw new Error(res.message);
    
    failedModels.value = [];
    addLog(`SUCCESS: Marked ${paths.length} models as unmatchable`, 'success');
    toast.showToast(`Marked ${paths.length} models as unmatchable`, 'success');
    await modelsStore.fetchModels();
  } catch (e) {
    addLog(`ERROR: Failed to bulk mark models as unmatchable`, 'error');
    toast.showToast('Failed to bulk mark models as unmatchable', 'error');
  }
};

const dismissMetadataModel = (model) => {
  failedModels.value = failedModels.value.filter(m => m.path !== model.path);
};

// Thumbnail Resolution Methods
const ignoreThumbnail = async (model) => {
  try {
    addLog(`Marking ${model.filename} as having no thumbnail...`, 'info');
    const res = await api.civitaiIgnoreThumbnail(model.path);
    if (res && res.status === 'error') throw new Error(res.message);
    
    failedThumbnailModels.value = failedThumbnailModels.value.filter(m => m.path !== model.path);
    addLog(`SUCCESS: Marked ${model.filename} as no thumbnail available`, 'success');
    toast.showToast(`Marked ${model.filename}: No thumbnail available`, 'info');
    await modelsStore.fetchModels();
  } catch (e) {
    addLog(`ERROR: Failed to mark thumbnail for ${model.filename}`, 'error');
    toast.showToast('Failed to mark thumbnail as unavailable', 'error');
  }
};

const ignoreAllThumbnails = async () => {
  if (failedThumbnailModels.value.length === 0) return;
  const paths = failedThumbnailModels.value.map(m => m.path);
  try {
    addLog(`Bulk marking ${paths.length} models as having no thumbnail...`, 'info');
    const res = await api.civitaiIgnoreThumbnailsBulk(paths);
    if (res && res.status === 'error') throw new Error(res.message);
    
    failedThumbnailModels.value = [];
    addLog(`SUCCESS: Marked ${paths.length} models as having no thumbnail`, 'success');
    toast.showToast(`Marked ${paths.length} models: No thumbnail available`, 'success');
    await modelsStore.fetchModels();
  } catch (e) {
    addLog(`ERROR: Failed to bulk ignore thumbnails`, 'error');
    toast.showToast('Failed to bulk mark thumbnails as unavailable', 'error');
  }
};

const downloadCustomThumbnail = async (model) => {
  const url = fallbackImageUrlMap.value[model.path];
  if (!url) {
    addLog(`No image URL provided for ${model.filename}`, 'warning');
    return;
  }
  
  try {
    addLog(`Downloading custom image for ${model.filename} from ${url}...`, 'info');
    const res = await api.civitaiDownloadPreviewFromUrl(model.path, url);
    if (res && res.status === 'error') throw new Error(res.message);
    
    addLog(`SUCCESS: Custom image downloaded for ${model.filename}`, 'success');
    toast.showToast(`Thumbnail saved for ${model.filename}`, 'success');
    
    failedThumbnailModels.value = failedThumbnailModels.value.filter(m => m.path !== model.path);
    await modelsStore.fetchModels();
  } catch (e) {
    addLog(`ERROR: Failed to download image from URL for ${model.filename}`, 'error');
    toast.showToast('Failed to download image from URL', 'error');
  }
};

const dismissThumbnailModel = (model) => {
  failedThumbnailModels.value = failedThumbnailModels.value.filter(m => m.path !== model.path);
};

const sortDownloadedModels = async () => {
  if (isMovingDownloads.value) return;
  
  try {
    addLog('Checking Download Directory for models to import...', 'info');
    const candidatesRes = await api.getDownloadCandidates();
    
    if (candidatesRes.status !== 'success' || !candidatesRes.models || candidatesRes.models.length === 0) {
      pendingDownloadsCount.value = 0;
      addLog('No model files found in the download directory.', 'warning');
      toast.showToast('No models found to import', 'warning');
      return;
    }
    
    const candidates = candidatesRes.models;
    pendingDownloadsCount.value = candidates.length;
    addLog(`Found ${candidates.length} model(s) waiting in Download Directory:`, 'info');
    candidates.forEach((c, idx) => {
      const sidecarInfo = c.sidecars && c.sidecars.length > 0 ? ` (+${c.sidecars.length} sidecar${c.sidecars.length > 1 ? 's' : ''})` : '';
      addLog(`  ${idx + 1}. ${c.filename}${sidecarInfo}`, 'info');
    });
    
    isMovingDownloads.value = true;
    scanComplete.value = false;
    currentIndex.value = 0;
    currentQueueLength.value = candidates.length;
    
    let movedTotal = 0;
    const moveErrors = [];
    
    for (let i = 0; i < candidates.length; i++) {
      const candidate = candidates[i];
      currentIndex.value = i + 1;
      addLog(`[${i + 1}/${candidates.length}] Moving ${candidate.filename}...`, 'info');
      
      try {
        const moveRes = await api.moveDownloadCandidate(candidate.filename);
        if (moveRes.status === 'success') {
          movedTotal++;
          const sidecarCount = (moveRes.moved_files?.length || 1) - 1;
          const sidecarText = sidecarCount > 0 ? ` (+${sidecarCount} sidecar file${sidecarCount > 1 ? 's' : ''})` : '';
          addLog(`✓ [${i + 1}/${candidates.length}] Successfully moved ${candidate.filename}${sidecarText} to sorting directory.`, 'success');
          if (moveRes.errors && moveRes.errors.length > 0) {
            moveRes.errors.forEach(err => addLog(`  ⚠ ${err}`, 'warning'));
          }
        } else {
          moveErrors.push(candidate.filename);
          addLog(`✕ Failed to move ${candidate.filename}: ${moveRes.message || 'Unknown error'}`, 'error');
        }
      } catch (err) {
        moveErrors.push(candidate.filename);
        addLog(`✕ Failed to move ${candidate.filename}: ${err.message}`, 'error');
      }
    }
    
    pendingDownloadsCount.value = Math.max(0, candidates.length - movedTotal);
    
    if (movedTotal > 0) {
      addLog(`All ${movedTotal} model(s) moved to sorting directory. Updating library data...`, 'success');
      toast.showToast(`Sorted ${movedTotal} model(s) into library`, 'success');
      
      // Refresh models so the scan page detects the newly imported files
      addLog('Refreshing local model list and scanning analytics...', 'info');
      await modelsStore.fetchModels(true);
      await checkDownloadCandidates();
      addLog('✓ Library data updated successfully.', 'success');
    } else {
      addLog('No models were successfully moved.', 'error');
      toast.showToast('Failed to move models', 'error');
    }
    
  } catch (err) {
    const errorMsg = err.response?.data?.message || err.message;
    addLog(`Error sorting models: ${errorMsg}`, 'error');
    toast.showToast('Failed to sort models', 'error');
  } finally {
    isMovingDownloads.value = false;
  }
};
</script>

<style scoped>
.civitai-scan-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--app-background);
  color: var(--color-text);
  overflow-y: auto;
}

.civitai-scan-view::-webkit-scrollbar {
  width: 10px;
}

.civitai-scan-view::-webkit-scrollbar-track {
  background: var(--scrollbar-track);
}

.civitai-scan-view::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 5px;
  border: 2px solid var(--scrollbar-track);
}

.civitai-scan-view::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover);
}

.scan-container {
  flex: 1;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.scan-header-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 5px;
  width: 100%;
}

.scan-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 6px;
}

.scan-header-top-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.scan-header h2 {
  font-size: 2.2em;
  font-weight: 800;
  margin: 0;
  color: var(--color-accent-title);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  letter-spacing: -0.3px;
}

.subtitle {
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.96em;
  margin: 0;
}

.mt-10 { margin-top: 10px; }

.scan-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  width: 100%;
}

@media (max-width: 1200px) {
  .scan-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .scan-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

.scan-main-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.scan-controls-col {
  flex: 1.1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.scan-log-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
}

@media (max-width: 1024px) {
  .scan-main-layout {
    flex-direction: column;
  }
}

.stat-box {
  background: var(--color-card-bg-subtle);
  border-radius: 8px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: left;
  border: 1px solid var(--color-border);
  border-top: 3px solid #3b82f6;
  min-height: 72px;
  cursor: default;
  user-select: none;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), var(--shadow-card);
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.stat-box:hover {
  transform: translateY(-1px);
  border-color: var(--card-hover-border, var(--color-border-hover));
  box-shadow: var(--card-hover-shadow, var(--shadow-hover));
}

.stat-box-total { border-top-color: #38bdf8; }
.stat-box-space { border-top-color: #06b6d4; }
.stat-box-meta { border-top-color: #475569; }
.stat-box-meta.has-missing { 
  border-top-color: #ef4444; 
  border-color: rgba(239, 68, 68, 0.35);
  background: linear-gradient(180deg, rgba(239, 68, 68, 0.12) 0%, var(--color-card-bg-subtle) 100%); 
}
.stat-box-thumbs { border-top-color: #475569; }
.stat-box-thumbs.has-missing { 
  border-top-color: #f59e0b; 
  border-color: rgba(245, 158, 11, 0.35);
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.12) 0%, var(--color-card-bg-subtle) 100%); 
}
.stat-box-hashes { border-top-color: #475569; }
.stat-box-hashes.has-missing { 
  border-top-color: #ef4444; 
  border-color: rgba(239, 68, 68, 0.35);
  background: linear-gradient(180deg, rgba(239, 68, 68, 0.12) 0%, var(--color-card-bg-subtle) 100%); 
}
.stat-box-unchecked { border-top-color: #475569; }
.stat-box-unchecked.has-missing { 
  border-top-color: #f59e0b; 
  border-color: rgba(245, 158, 11, 0.35);
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.12) 0%, var(--color-card-bg-subtle) 100%); 
}
.stat-box-online { border-top-color: #10b981; }
.stat-box-offline.has-offline { border-top-color: #ef4444; }
.stat-box-types { border-top-color: #a855f7; }

.stat-top {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 4px;
}

.stat-icon {
  font-size: 0.9em;
  opacity: 0.85;
}

.stat-box-total .stat-icon { color: #38bdf8; }
.stat-box-space .stat-icon { color: #06b6d4; }
.stat-box-meta .stat-icon { color: #94a3b8; }
.stat-box-meta.has-missing .stat-icon { color: #ef4444; }
.stat-box-thumbs .stat-icon { color: #94a3b8; }
.stat-box-thumbs.has-missing .stat-icon { color: #f59e0b; }
.stat-box-hashes .stat-icon { color: #94a3b8; }
.stat-box-hashes.has-missing .stat-icon { color: #ef4444; }
.stat-box-unchecked .stat-icon { color: #94a3b8; }
.stat-box-unchecked.has-missing .stat-icon { color: #f59e0b; }
.stat-box-online .stat-icon { color: #10b981; }
.stat-box-offline .stat-icon { color: #ef4444; }
.stat-box-types .stat-icon { color: #a855f7; }

.stat-label {
  color: #94a3b8;
  font-size: 0.72em;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value {
  font-size: 1.6em;
  font-weight: 800;
  color: #f1f5f9;
  line-height: 1.1;
  white-space: nowrap;
}

.text-success { color: #2ecc71; }
.text-danger { color: #e74c3c; }
.text-warning { color: #f39c12; }
.text-info { color: #3498db; }
.text-purple { color: #9b59b6; }
.text-muted { color: var(--color-text-secondary, #888); }

/* Header Active Directory Path Badge */
.header-path-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.84em;
  color: var(--color-text-secondary);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  padding: 5px 14px;
  border-radius: 20px;
  max-width: 600px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  margin-top: 0;
}

.all-in-one-tag {
  font-size: 0.72em;
  font-weight: 700;
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.35);
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-left: 10px;
}

.header-path-pill i {
  color: var(--color-btn-primary);
}

.header-path-pill:hover {
  border-color: var(--color-btn-secondary-hover-border, var(--color-border-hover));
  color: var(--color-text);
  background: var(--color-bg-hover);
}

[data-theme="midnight"] .header-path-pill:hover {
  border-color: #38bdf8;
  box-shadow: 0 0 8px rgba(56, 189, 248, 0.25);
}

/* Library Info Section */
.library-info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
  margin-bottom: 50px;
}

.library-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-card-bg);
  padding: 20px 24px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
}

.header-titles h3 {
  margin: 0 0 6px 0;
  font-size: 1.5em;
  font-weight: 700;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-titles h3 i {
  color: var(--color-text-link);
}

.header-titles .subtitle {
  margin: 0;
  font-size: 0.95em;
  color: var(--color-text-secondary);
}

/* Metric Cards Grid */
.library-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 15px;
}

.metric-card {
  background: var(--color-card-bg-subtle);
  border: 1px solid var(--color-border);
  border-top: 3px solid #475569;
  border-radius: 10px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: var(--shadow-card);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-hover);
}

.metric-card-total { border-top-color: #38bdf8; }
.metric-card-space { border-top-color: #06b6d4; }
.metric-card-online { border-top-color: #10b981; }
.metric-card-offline { border-top-color: #ef4444; }
.metric-card-types { border-top-color: #a855f7; }
.metric-card-curation { border-top-color: #f59e0b; }

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #94a3b8;
  font-size: 0.78em;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 700;
}

.metric-header i {
  font-size: 1.2em;
}

.metric-val {
  font-size: 1.9em;
  font-weight: 800;
  color: #f1f5f9;
  line-height: 1.1;
}

.sub-num {
  font-size: 0.55em;
  color: #94a3b8;
  font-weight: 600;
}

.metric-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.82em;
  color: #94a3b8;
  margin-top: 4px;
}

.pill-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.82em;
  font-weight: 600;
}

.pill-badge.ci {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.pill-badge.ca {
  background: rgba(168, 85, 247, 0.15);
  color: #a855f7;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

/* Library Table Container */
.library-table-container {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: var(--shadow-card);
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 16px;
}

.table-tabs {
  display: flex;
  background: var(--color-card-bg-subtle);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 4px;
  gap: 4px;
}

.table-tab {
  background: transparent;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 0.88em;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.table-tab:hover:not(.active) {
  color: var(--color-text);
  background: rgba(255, 255, 255, 0.04);
}

.table-tab.active {
  background: var(--color-btn-primary);
  color: white;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.4);
}

.table-search {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 280px;
}

.table-search .search-icon {
  position: absolute;
  left: 12px;
  color: var(--color-text-secondary);
  font-size: 0.9em;
}

.table-search-input {
  width: 100%;
  padding: 9px 32px 9px 34px;
  background-color: var(--color-console-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  font-size: 0.9em;
  outline: none;
  transition: all 0.2s ease;
}

.table-search-input:focus {
  border-color: var(--color-text-link);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
}

.table-search .clear-search-btn {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px;
}

.table-search .clear-search-btn:hover {
  color: var(--color-text);
}

/* Data Table */
.table-responsive {
  width: 100%;
  overflow-x: auto;
}

.library-data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9em;
}

.library-data-table th, 
.library-data-table td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--color-border-subtle);
}

.library-data-table th {
  background: var(--color-card-bg-subtle);
  color: var(--color-text-secondary);
  font-size: 0.76em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 5;
  border-bottom: 2px solid var(--color-border);
}

.library-data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.library-data-table th.sortable:hover {
  color: #ffffff;
  background: var(--color-bg-hover);
}

.library-data-table tbody tr {
  transition: background-color 0.15s ease;
}

.library-data-table tbody tr:hover {
  background-color: var(--color-bg-hover);
}

.table-total-row {
  background: var(--color-card-bg-subtle);
  font-weight: 700;
  border-top: 2px solid var(--color-border);
  color: var(--color-text);
}

.text-right { text-align: right; }
.text-center { text-align: center; }
.font-bold { font-weight: 600; }

.type-badge {
  display: inline-block;
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(56, 189, 248, 0.25);
  font-weight: 600;
  font-size: 0.9em;
}

.category-badge {
  display: inline-block;
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(16, 185, 129, 0.25);
  font-weight: 600;
  font-size: 0.9em;
}

.percent-text {
  font-size: 0.88em;
  color: #94a3b8;
  font-weight: 500;
}

.storage-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 140px;
}

.storage-bar {
  flex: 1;
  height: 8px;
  background: var(--color-console-bg);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--color-border-subtle);
}

.storage-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8 0%, #6366f1 100%);
  border-radius: 4px;
}

.storage-bar-fill.category-fill {
  background: linear-gradient(90deg, #10b981 0%, #06b6d4 100%);
}

.storage-bar-label {
  font-size: 0.82em;
  color: #94a3b8;
  min-width: 42px;
  text-align: right;
  font-weight: 600;
}

.online-status-tags, .missing-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 5px;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.8em;
  font-weight: 600;
}

.status-tag.tag-ci {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.25);
}

.status-tag.tag-ca {
  background: rgba(168, 85, 247, 0.15);
  color: #a855f7;
  border: 1px solid rgba(168, 85, 247, 0.25);
}

.status-tag.tag-off {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.status-tag.tag-pending {
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.status-tag.tag-ok {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.status-tag.tag-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.status-tag.tag-warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.empty-table-msg {
  text-align: center;
  padding: 30px;
  color: #94a3b8;
}

/* Online Analytics Panel */
.online-analytics-panel {
  display: flex;
  flex-direction: column;
  gap: 25px;
  padding: 10px 0;
}

.online-stacked-bar-container {
  background: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stacked-bar-title {
  font-weight: 700;
  font-size: 1.05em;
  color: #f1f5f9;
}

.stacked-bar {
  width: 100%;
  height: 22px;
  background-color: #0d1117;
  border-radius: 11px;
  display: flex;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4);
}

.bar-slice {
  height: 100%;
  transition: width 0.3s ease;
}

.bar-slice.slice-ci { background-color: #38bdf8; }
.bar-slice.slice-ca { background-color: #a855f7; }
.bar-slice.slice-off { background-color: #ef4444; }
.bar-slice.slice-pending { background-color: #475569; }

.stacked-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 0.88em;
  color: #94a3b8;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  display: inline-block;
}

.legend-color.color-ci { background-color: #38bdf8; }
.legend-color.color-ca { background-color: #a855f7; }
.legend-color.color-off { background-color: #ef4444; }
.legend-color.color-pending { background-color: #475569; }

.online-cards-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 15px;
}

.online-detail-card {
  background: var(--color-card-bg-subtle);
  border: 1px solid var(--color-border);
  border-left: 3px solid #38bdf8;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  gap: 15px;
  align-items: flex-start;
  box-shadow: var(--shadow-card);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.online-detail-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-border-hover);
}

.online-detail-card.card-ci { border-left-color: #38bdf8; }
.online-detail-card.card-ca { border-left-color: #a855f7; }
.online-detail-card.card-off { border-left-color: #ef4444; }
.online-detail-card.card-pending { border-left-color: #64748b; }

.online-detail-card .detail-icon {
  font-size: 1.8em;
  margin-top: 2px;
}

.online-detail-card.card-ci .detail-icon { color: #38bdf8; }
.online-detail-card.card-ca .detail-icon { color: #a855f7; }
.online-detail-card.card-off .detail-icon { color: #ef4444; }
.online-detail-card.card-pending .detail-icon { color: #94a3b8; }

.online-detail-card .detail-body h4 {
  margin: 0 0 4px 0;
  font-size: 1.05em;
  font-weight: 700;
  color: var(--color-text);
}

.online-detail-card .detail-count {
  font-size: 1.8em;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 6px;
}

.online-detail-card .detail-body p {
  margin: 0;
  font-size: 0.85em;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.scan-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-group.import-downloads {
  background: var(--color-card-bg);
  padding: 20px 24px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-group.import-downloads .action-group-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.group-title-wrap h3 {
  margin: 0;
  font-size: 1.3em;
  color: var(--color-text);
}

.dir-hint {
  font-size: 0.82em;
  color: var(--color-text-secondary);
  background: var(--color-bg-tertiary);
  padding: 3px 10px;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.dir-hint .dir-arrow {
  font-size: 0.8em;
  color: var(--color-btn-primary);
}

.btn-import-scan {
  padding: 12px 24px;
  font-size: 1.05em;
  font-weight: 700;
  border-radius: 8px;
  width: 100%;
}

.btn-import-scan.has-pending {
  border-color: rgba(56, 189, 248, 0.4);
}

[data-theme="midnight"] .btn-import-scan.has-pending {
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
}

.action-group.all-in-one {
  background: var(--color-card-bg);
  padding: 22px 25px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-group-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-header-icon {
  color: #f39c12;
  font-size: 1.3em;
}

.action-group h3 {
  margin: 0;
  font-size: 1.3em;
  color: var(--color-text);
}

.btn-primary-scan {
  background: var(--color-btn-primary-bg, var(--color-btn-primary));
  color: white;
  border: 1px solid var(--color-btn-primary-border, transparent);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.btn-primary-scan:hover {
  background: var(--color-btn-primary-hover-bg, var(--color-btn-primary-hover));
  border-color: var(--color-btn-primary-hover-border, transparent);
  transform: translateY(-2px);
  box-shadow: var(--color-btn-primary-hover-shadow, 0 6px 18px rgba(0, 0, 0, 0.4));
}

.btn-primary-scan:active {
  transform: translateY(1px);
  box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
}

.action-columns {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-col {
  background: var(--color-card-bg);
  padding: 18px 20px;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-col.full-width-card {
  grid-column: 1 / -1;
}

.card-header-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header-bar h3 {
  margin: 0;
  font-size: 1.1em;
  color: var(--color-text);
  font-weight: 600;
}

.step-badge {
  background: #3498db;
  color: white;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  font-weight: 700;
}

.header-icon {
  font-size: 1.15em;
}

.action-desc {
  margin: 0;
  font-size: 0.86em;
  line-height: 1.45;
  color: var(--color-text-secondary);
  background: rgba(0, 0, 0, 0.22);
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 3px solid rgba(52, 152, 219, 0.4);
  flex-grow: 1;
}

.btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 4px;
}

.btn-action {
  flex: 1;
  min-width: 120px;
  padding: 9px 16px;
  border-radius: 7px;
  font-size: 0.9em;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: var(--color-btn-action-bg);
  color: var(--color-text);
  border: 1px solid var(--color-btn-action-border, transparent);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
  transition: all 0.15s ease;
}

.btn-action:hover {
  background: var(--color-btn-action-hover-bg);
  border-color: var(--color-btn-action-hover-border, transparent);
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: var(--color-btn-action-hover-shadow, none);
}

.btn-action:active {
  transform: translateY(1px);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.btn-availability {
  padding: 10px 14px;
  font-size: 0.88em;
}

.btn-availability:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.availability-btn-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 4px;
}

.btn-availability-primary {
  grid-column: 1 / -1;
  padding: 10px 16px;
  font-size: 0.92em;
  font-weight: 700;
  background: var(--color-btn-action-bg);
  border: 1px solid var(--color-btn-action-border, transparent);
}

.btn-availability-unchecked {
  grid-column: 1 / -1;
  padding: 10px 16px;
  font-size: 0.92em;
  font-weight: 700;
}

.btn-availability-primary:hover:not(:disabled) {
  background: var(--color-btn-action-hover-bg);
  border-color: var(--color-btn-action-hover-border, transparent);
  box-shadow: var(--color-btn-action-hover-shadow, none);
}

@media (max-width: 900px) {
  .availability-btn-grid {
    grid-template-columns: 1fr;
  }
}

.btn-refresh {
  min-width: auto;
  padding: 8px 18px;
}

.active-scan-box {
  background: var(--color-card-bg);
  padding: 35px 25px;
  border-radius: 12px;
  border: 1px solid var(--color-border-hover);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.active-scan-box h3 {
  margin: 0;
  font-size: 1.25em;
  font-weight: 700;
  color: var(--color-text);
}

.btn-large {
  padding: 15px 30px;
  font-size: 1.2em;
  width: 100%;
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.progress-bar {
  width: 100%;
  height: 14px;
  background-color: var(--color-console-bg);
  border-radius: 7px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8 0%, #3b82f6 50%, #818cf8 100%);
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-size: 0.88em;
  font-weight: 600;
  color: #94a3b8;
}

/* Log Section */
.log-section {
  background: var(--color-card-bg);
  padding: 18px 20px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  height: 700px;
  max-height: 700px;
  min-height: 0;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.log-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.log-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.terminal-icon {
  color: var(--color-text-link);
  font-size: 0.95em;
}

.log-title {
  font-weight: 700;
  font-size: 0.92em;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.console-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #64748b;
  margin-left: 4px;
  transition: all 0.3s ease;
}

.console-status-dot.is-running {
  background-color: #10b981;
  box-shadow: 0 0 8px #10b981;
  animation: pulse-dot 1.5s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.15); }
}

.console-status-text {
  font-size: 0.78em;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.btn-clear-logs {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.78em;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.btn-clear-logs:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.4);
  color: #f87171;
}

.log-container {
  flex: 1;
  min-height: 0;
  background-color: var(--color-console-bg);
  border: 1px solid var(--color-border-subtle);
  border-radius: 8px;
  padding: 14px 16px;
  overflow-y: auto;
  font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
  font-size: 0.88em;
  display: flex;
  flex-direction: column;
  gap: 5px;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4);
}

.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: var(--color-console-bg);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover);
}

.log-entry {
  line-height: 1.5;
  word-break: break-all;
}

.log-entry .timestamp {
  color: #64748b;
  margin-right: 10px;
  font-size: 0.88em;
  user-select: none;
}

.log-entry.info .message { color: #cbd5e1; }
.log-entry.success .message { color: #4ade80; }
.log-entry.error .message { color: #f87171; }
.log-entry.warning .message { color: #fbbf24; }

.empty-log {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
  gap: 8px;
  user-select: none;
  min-height: 200px;
}

.empty-log .empty-icon {
  font-size: 2.2em;
  opacity: 0.35;
  color: #38bdf8;
  margin-bottom: 4px;
}

.empty-log .empty-title {
  font-size: 1.05em;
  font-weight: 700;
  color: #94a3b8;
}

.empty-log .empty-sub {
  font-size: 0.82em;
  color: #64748b;
}

/* ==========================================================================
   Unresolved Items Assistant Section (Metadata & Thumbnails)
   ========================================================================== */
.resolution-section {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-top: 3px solid #f59e0b;
  border-radius: 10px;
  padding: 14px 20px 16px 20px;
  box-shadow: var(--shadow-card), 0 4px 18px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.resolution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.resolution-title-area {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.resolution-title-area h3 {
  margin: 0;
  font-size: 1.1em;
  font-weight: 700;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 8px;
}

.resolution-subtitle {
  margin: 0;
  font-size: 0.82em;
  color: var(--color-text-secondary);
}

.resolution-header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.resolution-tabs {
  display: inline-flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.3);
  padding: 3px;
  border-radius: 6px;
  border: 1px solid var(--color-border-subtle);
}

.resolution-tab-btn {
  background: transparent;
  border: none;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 0.82em;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.resolution-tab-btn:hover {
  color: var(--color-text);
  background: rgba(255, 255, 255, 0.05);
}

.resolution-tab-btn.active {
  background: var(--color-btn-action-bg);
  color: #ffffff;
  border: 1px solid var(--color-btn-action-border, transparent);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.tab-badge {
  background: rgba(245, 158, 11, 0.22);
  color: #fbbf24;
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 0.78em;
  font-weight: 700;
}

.resolution-global-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-bulk {
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 0.8em;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.btn-bulk-thumb {
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24;
}

.btn-bulk-thumb:hover {
  background: #f59e0b;
  color: #0f172a;
  border-color: #f59e0b;
  font-weight: 700;
  transform: translateY(-1px);
}

.btn-bulk-meta {
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
}

.btn-bulk-meta:hover {
  background: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
  font-weight: 700;
  transform: translateY(-1px);
}

.btn-icon-close {
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 1.05em;
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.btn-icon-close:hover {
  color: #f87171;
  background: rgba(239, 68, 68, 0.15);
}

.resolution-tab-content {
  display: flex;
  flex-direction: column;
}

.resolution-items-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 4px;
}

.resolution-items-list::-webkit-scrollbar {
  width: 6px;
}

.resolution-items-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.resolution-items-list::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 3px;
}

.resolution-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--color-border-subtle);
  border-radius: 6px;
  padding: 7px 12px;
  min-height: 44px;
  box-sizing: border-box;
  transition: all 0.15s ease;
}

.resolution-row:hover {
  background: rgba(0, 0, 0, 0.38);
  border-color: rgba(56, 189, 248, 0.35);
}

.row-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.model-filename {
  font-weight: 600;
  font-size: 0.88em;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.model-folder-pill {
  font-size: 0.74em;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-text-secondary);
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.row-badge {
  font-size: 0.74em;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.badge-thumb-warning {
  background: rgba(245, 158, 11, 0.12);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.28);
}

.badge-meta-warning {
  background: rgba(239, 68, 68, 0.12);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.28);
}

.row-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.row-input-wrap {
  position: relative;
  width: 240px;
  display: flex;
  align-items: center;
}

.row-input {
  width: 100%;
  height: 30px;
  background: var(--color-console-bg, #0b1120);
  border: 1px solid var(--color-border);
  border-radius: 5px;
  color: var(--color-text);
  font-size: 0.82em;
  padding: 2px 8px 2px 26px;
  outline: none;
  transition: all 0.15s ease;
}

.row-input:focus {
  border-color: var(--color-text-link, #38bdf8);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.row-input-icon {
  position: absolute;
  left: 8px;
  font-size: 0.76em;
  color: var(--color-text-secondary);
  pointer-events: none;
}

.btn-row-action {
  height: 30px;
  padding: 0 11px;
  border-radius: 5px;
  font-size: 0.81em;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-no-thumb {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.38);
  color: #fbbf24;
}

.btn-no-thumb:hover {
  background: #f59e0b;
  color: #0f172a;
  border-color: #f59e0b;
  font-weight: 700;
  transform: translateY(-1px);
}

.btn-save-image,
.btn-fetch {
  background: var(--color-btn-primary, #3b82f6);
  border: 1px solid transparent;
  color: #ffffff;
}

.btn-save-image:hover,
.btn-fetch:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-unmatchable {
  background: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.38);
  color: #f87171;
}

.btn-unmatchable:hover {
  background: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
  transform: translateY(-1px);
}

.btn-row-dismiss {
  background: transparent;
  border: none;
  color: #64748b;
  width: 26px;
  height: 26px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.82em;
  transition: all 0.15s ease;
}

.btn-row-dismiss:hover {
  color: #f87171;
  background: rgba(239, 68, 68, 0.15);
}
</style>

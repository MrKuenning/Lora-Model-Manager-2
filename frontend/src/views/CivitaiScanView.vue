<template>
  <div class="civitai-scan-view">
    <AppHeader />
    
    <div class="scan-container">
      <div class="scan-header-wrapper">
        <div class="back-btn-container">
          <button class="btn btn-back-manager" @click="$router.push('/')">
            <i class="fas fa-arrow-left"></i> Back to Manager
          </button>
        </div>
        <div class="scan-header">
          <h2><i class="fas fa-radar"></i> Metadata Import &mdash; {{ isLoras ? 'LoRAs' : 'Checkpoints' }}</h2>
          <p class="subtitle">Scan, download missing metadata, and inspect library analytics for your local {{ isLoras ? 'LoRA' : 'Checkpoint' }} collection.</p>
        </div>
        <div class="library-state-indicator">
          <div class="state-badge-pill" :class="modelsStore.currentLocation">
            <i class="fas" :class="isLoras ? 'fa-layer-group' : 'fa-cube'"></i>
            <span class="state-title">{{ isLoras ? 'LoRAs Library' : 'Checkpoints Library' }}</span>
          </div>
          <div class="state-path-text" :title="activeDirectoryPath">
            <i class="fas fa-folder"></i> <span>{{ activeDirectoryPath || 'No directory configured' }}</span>
          </div>
          <div class="state-switch-tabs">
            <button 
              class="state-switch-tab" 
              :class="{ active: isLoras }"
              @click="modelsStore.setLocation('loras')"
              title="Switch to LoRAs Library"
            >
              <i class="fas fa-layer-group"></i> LoRAs
            </button>
            <button 
              class="state-switch-tab" 
              :class="{ active: !isLoras }"
              @click="modelsStore.setLocation('checkpoints')"
              title="Switch to Checkpoints Library"
            >
              <i class="fas fa-cube"></i> Checkpoints
            </button>
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
          </div>

          <div class="scan-actions" v-if="!isScanning && !(scanComplete && failedModels.length > 0)">
            <div class="action-group all-in-one">
              <div class="action-group-header">
                <i class="fas fa-bolt group-header-icon"></i>
                <h3>All-in-One Scan</h3>
              </div>
              <p class="action-desc">Perform all steps automatically: Generate missing hashes, Fetch missing metadata, and Download preview thumbnails.</p>
              <button class="btn btn-primary-scan btn-large" @click="runAllInOne">
                <i class="fas fa-bolt"></i> Run All-in-One Scan ({{ allInOneTargetsCount }})
              </button>
            </div>
            


            
            <div class="action-columns">
              <div class="action-col">
                <div class="card-header-bar">
                  <span class="step-badge">1</span>
                  <h3>Scrape Metadata</h3>
                </div>
                <p class="action-desc">Fetch model info from Civitai or CivArchive using file hashes.</p>
                <div class="btn-row">
                  <button class="btn btn-action" @click="fetchMissingData('civitai')">
                    <i class="fas fa-cloud-download-alt text-info"></i> Fetch Missing Metadata ({{ missingMetadata }})
                  </button>
                </div>
              </div>
              
              <div class="action-col">
                <div class="card-header-bar">
                  <span class="step-badge">2</span>
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

              <div class="action-col">
                <div class="card-header-bar">
                  <i class="fas fa-exchange-alt header-icon text-info"></i>
                  <h3>Import from Downloads</h3>
                </div>
                <p class="action-desc">Move incoming models and their associated sidecars from Download Directory to Sorting Directory.</p>
                <div class="btn-row">
                  <button class="btn btn-action" @click="sortDownloadedModels">
                    <i class="fas fa-exchange-alt text-info"></i> Move Files
                  </button>
                </div>
              </div>

              <div class="action-col">
                <div class="card-header-bar">
                  <i class="fas fa-hashtag header-icon text-purple"></i>
                  <h3>Generate Hashes</h3>
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

              <div class="action-col full-width-card">
                <div class="card-header-bar">
                  <i class="fas fa-globe header-icon text-success"></i>
                  <h3>Check Online Availability</h3>
                </div>
                <p class="action-desc">Audit whether models are still live on Civitai or preserved on CivArchive. Choose a targeted check or scan all eligible models.</p>
                <div class="availability-btn-grid">
                  <button class="btn btn-action btn-availability btn-availability-primary" @click="checkOnlineAvailability" title="Scan all eligible models (skips models already verified offline on both platforms)">
                    <i class="fas fa-globe text-success"></i> Check All Eligible ({{ availabilityScanTargetsCount }})
                  </button>
                  <button class="btn btn-action btn-availability" @click="checkCivitaiAvailability" :disabled="onlineCivitaiCount === 0" title="Check availability of models currently marked as active on Civitai">
                    <i class="fas fa-check-circle text-info"></i> Check Civitai Models ({{ onlineCivitaiCount }})
                  </button>
                  <button class="btn btn-action btn-availability" @click="checkCivArchiveAvailability" :disabled="onlineCivArchiveCount === 0" title="Check availability of models currently on CivArchive">
                    <i class="fas fa-archive text-purple"></i> Check CivArchive Models ({{ onlineCivArchiveCount }})
                  </button>
                  <button class="btn btn-action btn-availability" @click="checkUncheckedAvailability" :disabled="uncheckedOnlineCount === 0" title="Check models that have not been audited for online availability yet">
                    <i class="fas fa-question-circle text-warning"></i> Check Unchecked Models ({{ uncheckedOnlineCount }})
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="active-scan-box" v-else>
            <h3 style="margin-top: 0;">Scanning in progress...</h3>
            <button class="btn btn-danger btn-large" @click="stopScan">
              <i class="fas fa-stop"></i> Stop Scan
            </button>
          </div>
          
          <div class="progress-section" v-if="isScanning || scanComplete">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            </div>
            <div class="progress-text">
              Processed {{ currentIndex }} of {{ currentQueueLength }} items ({{ progressPercentage }}%)
            </div>
          </div>
        </div>
      
        <!-- Right Column: Logs -->
        <div class="scan-log-col">
          <div class="log-section" :style="scanComplete && failedModels.length > 0 ? 'height: 320px; max-height: 320px;' : ''">
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

      <div class="resolution-section mt-20" v-if="!isScanning && scanComplete && failedModels.length > 0">
        <h3><i class="fas fa-exclamation-triangle text-warning"></i> Unresolved Models</h3>
        <p>The following models could not be found on Civitai or CivArchive. You can provide a manual URL or mark them to be ignored in future scans.</p>
        
        <div class="failed-models-list">
          <div class="failed-model-card" v-for="model in failedModels" :key="model.path">
            <div class="failed-model-name">{{ model.filename }}</div>
            <div class="failed-model-actions">
              <input type="text" class="form-control" v-model="fallbackUrlMap[model.path]" placeholder="Enter URL (e.g., https://civitai.com/models/1234)">
              <button class="btn btn-primary" @click="resolveManualUrl(model)">Fetch</button>
              <button class="btn btn-secondary" @click="ignoreModel(model)">Mark not matchable</button>
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

const getMissingMetadataModels = () => modelsStore.models.filter(m => !m.civitaiUrl && !m.civitai_url);
const getMissingThumbnailModels = () => modelsStore.models.filter(m => !m.previewUrl || m.previewUrl.includes('placeholder'));
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
  currentIndex.value = 0;
  currentQueueLength.value = tasks.length;
  logs.value = [];
  failedModels.value = [];
  
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
      if (task.actionName === 'Fetch Metadata') {
        if (!failedModels.value.some(m => m.path === task.model.path)) {
          failedModels.value.push(task.model);
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
  
  // Refresh store
  await modelsStore.fetchModels();
};

// Queue Builders
const fetchMissingData = (source = 'civitai') => {
  const targets = getMissingMetadataModels();
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
  const skipNsfw = settingsStore.scanSettings?.skipNsfwPreviews === true;
  const maxSize = settingsStore.scanSettings?.downloadMaxSize === true;
  
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
        }
      }
    });
  });
  
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
    
    // Remove from failed list
    failedModels.value = failedModels.value.filter(m => m.path !== model.path);
    
    // Refresh models
    await modelsStore.fetchModels();
  } catch (e) {
    addLog(`ERROR: Manual fetch failed for ${model.filename}`, 'error');
  }
};

const ignoreModel = async (model) => {
  try {
    addLog(`Ignoring ${model.filename} in future scans...`, 'info');
    // Using a dummy URL to prevent future missing metadata checks
    const res = await api.civitaiFetchByUrl(model.path, 'https://no-match.com/ignored');
    if (res && res.status === 'error') throw new Error(res.message);
    
    // Remove from failed list
    failedModels.value = failedModels.value.filter(m => m.path !== model.path);
    addLog(`SUCCESS: Ignored ${model.filename}`, 'success');
  } catch (e) {
    addLog(`ERROR: Failed to ignore ${model.filename}`, 'error');
    toast.showToast('Failed to mark model as unmatchable', 'error');
  }
};

const sortDownloadedModels = async () => {
  try {
    addLog('Starting to sort downloaded models...', 'info');
    const res = await api.sortDownloads();
    
    if (res.status === 'success') {
      if (res.moved_count > 0) {
        addLog(`Successfully moved ${res.moved_count} models to the sorting directory.`, 'success');
        toast.showToast(`Sorted ${res.moved_count} models`, 'success');
        
        // Refresh models so the scan page detects the newly imported files
        addLog('Refreshing local model list...', 'info');
        await modelsStore.fetchModels(true);
      } else {
        addLog('No .safetensors files found in the download directory.', 'warning');
        toast.showToast('No models found to sort', 'warning');
      }
      
      if (res.errors && res.errors.length > 0) {
        res.errors.forEach(err => addLog(err, 'error'));
      }
    } else {
      addLog(`Error: ${res.message}`, 'error');
      toast.showToast(res.message || 'Error sorting models', 'error');
    }
  } catch (err) {
    const errorMsg = err.response?.data?.message || err.message;
    addLog(`Error sorting models: ${errorMsg}`, 'error');
    toast.showToast('Failed to sort models', 'error');
  }
};
</script>

<style scoped>
.civitai-scan-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: radial-gradient(ellipse 100% 50% at 50% 0%, rgba(14, 116, 144, 0.15), transparent 70%), #0a0e17;
  color: #e2e8f0;
  overflow-y: auto;
}

.civitai-scan-view::-webkit-scrollbar {
  width: 10px;
}

.civitai-scan-view::-webkit-scrollbar-track {
  background: #0a0e17;
}

.civitai-scan-view::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 5px;
  border: 2px solid #0a0e17;
}

.civitai-scan-view::-webkit-scrollbar-thumb:hover {
  background: #334155;
}

/* Align AppHeader seamlessly with the deep navy theme */
.civitai-scan-view :deep(.app-header) {
  background: #0c101a;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.civitai-scan-view :deep(.app-header .btn-secondary) {
  background: #181d26;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
}

.civitai-scan-view :deep(.app-header .btn-secondary:hover) {
  background: #232a37;
  border-color: #38bdf8;
  color: #ffffff;
}

.civitai-scan-view :deep(.app-header .view-toggles) {
  background: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.civitai-scan-view :deep(.app-header .view-toggles .btn.active) {
  background: #1e293b;
  color: #38bdf8;
}

.civitai-scan-view :deep(.app-header .location-tab) {
  color: #94a3b8;
}

.civitai-scan-view :deep(.app-header .location-tab.active) {
  background: #0284c7;
  color: #ffffff;
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
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 20px;
  padding-bottom: 5px;
}

.back-btn-container {
  justify-self: start;
}

.btn-back-manager {
  background: #181d26;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #cbd5e1;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9em;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-back-manager:hover {
  background: #232a37;
  border-color: #38bdf8;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(56, 189, 248, 0.25);
}

.scan-header {
  text-align: center;
}

.scan-header h2 {
  font-size: 2.2em;
  font-weight: 800;
  margin: 0 0 6px 0;
  color: #38bdf8;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  letter-spacing: -0.3px;
}

.subtitle {
  color: #94a3b8;
  font-size: 0.96em;
  margin: 0;
}

.mt-10 { margin-top: 10px; }

.scan-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  width: 100%;
}

@media (max-width: 900px) {
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
  background: #11151c;
  border-radius: 8px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: left;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top: 3px solid #3b82f6;
  min-height: 72px;
  cursor: default;
  user-select: none;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 2px 6px rgba(0, 0, 0, 0.3);
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.stat-box:hover {
  transform: translateY(-1px);
  border-color: rgba(255, 255, 255, 0.16);
}

.stat-box-total { border-top-color: #38bdf8; }
.stat-box-space { border-top-color: #06b6d4; }
.stat-box-meta { border-top-color: #475569; }
.stat-box-meta.has-missing { 
  border-top-color: #ef4444; 
  border-color: rgba(239, 68, 68, 0.35);
  background: linear-gradient(180deg, rgba(239, 68, 68, 0.12) 0%, #11151c 100%); 
}
.stat-box-thumbs { border-top-color: #475569; }
.stat-box-thumbs.has-missing { 
  border-top-color: #f59e0b; 
  border-color: rgba(245, 158, 11, 0.35);
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.12) 0%, #11151c 100%); 
}
.stat-box-hashes { border-top-color: #475569; }
.stat-box-hashes.has-missing { 
  border-top-color: #ef4444; 
  border-color: rgba(239, 68, 68, 0.35);
  background: linear-gradient(180deg, rgba(239, 68, 68, 0.12) 0%, #11151c 100%); 
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

/* Library State Indicator in Header */
.library-state-indicator {
  justify-self: end;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.state-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.9em;
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.state-badge-pill.checkpoints {
  background: rgba(168, 85, 247, 0.12);
  color: #a855f7;
  border-color: rgba(168, 85, 247, 0.3);
}

.state-path-text {
  font-size: 0.8em;
  color: #94a3b8;
  background: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 4px 10px;
  border-radius: 6px;
  max-width: 320px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  gap: 6px;
}

.state-switch-tabs {
  display: flex;
  background: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 3px;
  gap: 4px;
}

.state-switch-tab {
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 0.82em;
  font-weight: 600;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.state-switch-tab:hover:not(.active) {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.04);
}

.state-switch-tab.active {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: white;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.4);
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
  background: #181d26;
  padding: 20px 24px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.header-titles h3 {
  margin: 0 0 6px 0;
  font-size: 1.5em;
  font-weight: 700;
  color: #f1f5f9;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-titles h3 i {
  color: #38bdf8;
}

.header-titles .subtitle {
  margin: 0;
  font-size: 0.95em;
  color: #94a3b8;
}

/* Metric Cards Grid */
.library-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 15px;
}

.metric-card {
  background: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top: 3px solid #475569;
  border-radius: 10px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.16);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
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
  background: #181d26;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 16px;
}

.table-tabs {
  display: flex;
  background: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 4px;
  gap: 4px;
}

.table-tab {
  background: transparent;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.88em;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.table-tab:hover:not(.active) {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.04);
}

.table-tab.active {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
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
  color: #94a3b8;
  font-size: 0.9em;
}

.table-search-input {
  width: 100%;
  padding: 9px 32px 9px 34px;
  background-color: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 0.9em;
  outline: none;
  transition: all 0.2s ease;
}

.table-search-input:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
}

.table-search .clear-search-btn {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
}

.table-search .clear-search-btn:hover {
  color: #f1f5f9;
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.library-data-table th {
  background: #11151c;
  color: #94a3b8;
  font-size: 0.76em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 5;
  border-bottom: 2px solid rgba(255, 255, 255, 0.08);
}

.library-data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.library-data-table th.sortable:hover {
  color: #ffffff;
  background: #1a202c;
}

.library-data-table tbody tr {
  transition: background-color 0.15s ease;
}

.library-data-table tbody tr:hover {
  background-color: rgba(56, 189, 248, 0.04);
}

.table-total-row {
  background: #11151c;
  font-weight: 700;
  border-top: 2px solid rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
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
  background: #0d1117;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
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
  background: #11151c;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-left: 3px solid #38bdf8;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  gap: 15px;
  align-items: flex-start;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.online-detail-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.16);
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
  color: #f1f5f9;
}

.online-detail-card .detail-count {
  font-size: 1.8em;
  font-weight: 800;
  color: #f1f5f9;
  margin-bottom: 6px;
}

.online-detail-card .detail-body p {
  margin: 0;
  font-size: 0.85em;
  color: #94a3b8;
  line-height: 1.4;
}

.scan-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-group.all-in-one {
  background: #181d26;
  padding: 22px 25px;
  border-radius: 12px;
  border: 1px solid rgba(52, 152, 219, 0.35);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
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
  color: #f1f5f9;
}

.btn-primary-scan {
  background: linear-gradient(135deg, #3498db 0%, #2475a8 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.35);
  transition: all 0.2s ease;
}

.btn-primary-scan:hover {
  background: linear-gradient(135deg, #42a5f5 0%, #2980b9 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(52, 152, 219, 0.5);
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
  background: #181d26;
  padding: 18px 20px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
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
  color: #f1f5f9;
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
  color: #94a3b8;
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
  background: linear-gradient(180deg, #2b3342 0%, #202633 100%);
  color: #e2e8f0;
  border: 1px solid #3e4859;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.35);
  transition: all 0.15s ease;
}

.btn-action:hover {
  background: linear-gradient(180deg, #384255 0%, #283040 100%);
  border-color: #60a5fa;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.45);
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
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 4px;
}

.btn-availability-primary {
  grid-column: 1 / -1;
  padding: 11px 20px;
  font-size: 0.95em;
  background: linear-gradient(180deg, #1e3a5f 0%, #152943 100%);
  border-color: rgba(56, 189, 248, 0.4);
}

.btn-availability-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #244775 0%, #1a3353 100%);
  border-color: #38bdf8;
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35);
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
  background: #181d26;
  padding: 35px 25px;
  border-radius: 12px;
  border: 1px solid rgba(56, 189, 248, 0.35);
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
  color: #f1f5f9;
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
  background-color: #0d1117;
  border-radius: 7px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
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

/* Resolution Section */
.resolution-section {
  background: #181d26;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 12px;
  padding: 22px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.resolution-section h3 {
  margin: 0 0 8px 0;
  font-size: 1.25em;
  color: #f1f5f9;
}

.resolution-section p {
  color: #94a3b8;
  font-size: 0.9em;
  margin: 0 0 16px 0;
}

.failed-models-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.failed-model-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #11151c;
  padding: 14px 18px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.failed-model-name {
  font-weight: 600;
  color: #f1f5f9;
  flex: 1;
  word-break: break-all;
  margin-right: 20px;
}

.failed-model-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.failed-model-actions input {
  width: 320px;
  background: #0d1117;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  border-radius: 6px;
  padding: 8px 12px;
  outline: none;
  font-size: 0.9em;
  transition: border-color 0.2s ease;
}

.failed-model-actions input:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

/* Log Section */
.log-section {
  background: #181d26;
  padding: 18px 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.log-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.terminal-icon {
  color: #38bdf8;
  font-size: 0.95em;
}

.log-title {
  font-weight: 700;
  font-size: 0.92em;
  color: #f1f5f9;
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
  color: #94a3b8;
  font-weight: 500;
}

.btn-clear-logs {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #94a3b8;
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
  background-color: #0d1117;
  border: 1px solid rgba(255, 255, 255, 0.06);
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
  background: #0d1117;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #334155;
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
</style>

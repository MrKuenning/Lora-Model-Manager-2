<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content model-modal">
      
      <!-- Top Header -->
      <div class="modal-header">
        <h2>
          {{ form.name || 'Unknown' }} 
          <span class="base-model-light">{{ form.baseModel || form.sdVersion || '' }}</span>
        </h2>
        <div style="display: flex; gap: 10px; margin-right: 20px; align-items: center; margin-left: auto;">
          <button class="btn btn-micro" :class="form.nsfw ? 'btn-danger' : 'btn-secondary'" @click="form.nsfw = !form.nsfw; debouncedSave()" style="font-weight: bold;" title="Toggle NSFW Status">
            NSFW: {{ form.nsfw ? 'Yes' : 'No' }}
          </button>
          <button class="btn btn-micro" :class="form.tested ? 'btn-success' : 'btn-secondary'" @click="form.tested = !form.tested; debouncedSave()" style="font-weight: bold;" title="Mark as Tested">
            Tested: {{ form.tested ? 'Yes' : 'No' }}
          </button>
        </div>

        <div class="header-actions">
          <button class="btn btn-icon" @click="navigatePrevious" title="Previous"><i class="fas fa-chevron-left"></i></button>
          <button class="btn btn-icon" @click="navigateNext" title="Next"><i class="fas fa-chevron-right"></i></button>
          <button class="btn btn-icon" @click="loadModel" title="Reload"><i class="fas fa-sync-alt"></i></button>
          <button class="btn btn-icon" @click="emit('close')" title="Close"><i class="fas fa-times"></i></button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin fa-3x"></i>
        <p>Loading model details...</p>
      </div>

      <div v-else-if="model" class="model-details-layout">
        
        <!-- LEFT COLUMN -->
        <div class="left-column">
          <!-- Image Section -->
          <div class="image-section" @dragover.prevent @drop.prevent="handleDrop">
            <div class="main-image-container" @click="handleMainImageClick" :title="images.length > 0 ? 'Click to view full size preview' : 'Click to add preview image'">
              <button 
                type="button" 
                class="drop-overlay drop-overlay-btn" 
                @click.stop="triggerFileInput" 
                title="Click to browse file or drag & drop image here"
              >
                <i class="fas fa-upload"></i> Browse or Drop Image
              </button>
              <img 
                v-if="images.length > 0"
                :src="api.getAssetUrl(images[currentImageIndex], modelsStore.getCacheBuster(model.path))" 
                alt="Preview" 
                class="main-preview"
              />
              <div v-else class="no-preview">No Image</div>
              
              <!-- Hover Actions -->
              <div class="image-hover-actions" v-if="images.length > 0" @click.stop>
                <button class="btn btn-primary btn-small icon-btn" @click.stop="setAsDefault" title="Make this the primary thumbnail">
                  <i class="fas fa-star"></i>
                </button>
                <button class="btn btn-danger btn-small icon-btn" @click.stop="deleteCurrentImage" title="Delete thumbnail">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>

            <!-- Thumbnail Strip -->
            <div class="thumbnail-strip" v-if="images.length > 0">
              <img 
                v-for="(img, idx) in images" 
                :key="idx"
                :src="api.getAssetUrl(img, modelsStore.getCacheBuster(model.path))"
                class="thumb"
                :class="{ active: idx === currentImageIndex }"
                @mouseover="currentImageIndex = idx"
                @click="setPrimaryImage(idx)"
                @contextmenu.prevent="deleteImage(idx)"
                title="Left click: Set primary | Right click: Delete"
                loading="lazy"
              />
              <div class="add-thumb" @click="triggerFileInput" title="Add new thumbnail"><i class="fas fa-plus"></i></div>
            </div>
            
            <input type="file" ref="fileInput" @change="handleFileUpload" accept="image/*" style="display: none;">
          </div>

          <!-- MODEL INFO CARD -->
          <div class="detail-card info-card">
            <div class="detail-card-header">
              <i class="fas fa-info-circle text-info section-title-icon"></i>
              <span class="detail-section-title">Model Info</span>
            </div>
            <div class="info-card-content">
              <div class="info-field-group">
                <span class="info-field-label">Base Model</span>
                <div class="info-val with-edit">
                  <div class="info-link-group" v-if="editingField !== 'baseModel'">
                    <template v-if="form.baseModel">
                      <a 
                        href="#" 
                        class="info-link" 
                        @click.prevent="searchAndClose(form.baseModel)"
                        :title="`Search models with base model: ${form.baseModel}`"
                      >{{ form.baseModel }}</a>
                      <span 
                        class="info-count-badge" 
                        @click="searchAndClose(form.baseModel)"
                        :title="`${baseModelCount} model${baseModelCount === 1 ? '' : 's'} with base model ${form.baseModel}`"
                      >{{ baseModelCount }}</span>
                    </template>
                    <span v-else>-</span>
                  </div>
                  <div v-else style="position: relative; flex: 1; display: flex; align-items: center; width: 100%;">
                    <input 
                      id="inline-edit-baseModel"
                      type="text" 
                      v-model="form.baseModel" 
                      list="baseModelsList" 
                      class="inline-edit-input"
                      @blur="stopEditingField"
                      @keydown.enter="stopEditingField"
                      style="padding-right: 40px;"
                    >
                    <i class="fas fa-times" 
                       style="position: absolute; right: 22px; cursor: pointer; color: #888; font-size: 0.9em;"
                       @mousedown.prevent="form.baseModel = ''"
                       title="Clear"
                    ></i>
                  </div>
                  <datalist id="baseModelsList">
                    <option v-for="opt in uniqueBaseModels" :key="opt" :value="opt"></option>
                  </datalist>
                  <i class="fas fa-edit edit-icon" v-if="editingField !== 'baseModel'" @click="startEditingField('baseModel')" title="Edit Base Model"></i>
                </div>
              </div>

              <div class="info-field-group">
                <span class="info-field-label">Forge Model Type</span>
                <div class="info-val with-edit">
                  <span v-if="editingField !== 'sdVersion'">{{ form.sdVersion || '-' }}</span>
                  <div v-else style="position: relative; flex: 1; display: flex; align-items: center; width: 100%;">
                    <input 
                      id="inline-edit-sdVersion"
                      type="text" 
                      v-model="form.sdVersion" 
                      list="sdVersionsList" 
                      class="inline-edit-input"
                      @blur="stopEditingField"
                      @keydown.enter="stopEditingField"
                      style="padding-right: 40px;"
                    >
                    <i class="fas fa-times" 
                       style="position: absolute; right: 22px; cursor: pointer; color: #888; font-size: 0.9em;"
                       @mousedown.prevent="form.sdVersion = ''"
                       title="Clear"
                    ></i>
                  </div>
                  <datalist id="sdVersionsList">
                    <option v-for="opt in uniqueSdVersions" :key="opt" :value="opt"></option>
                  </datalist>
                  <i class="fas fa-edit edit-icon" v-if="editingField !== 'sdVersion'" @click="startEditingField('sdVersion')"></i>
                </div>
              </div>

              <div class="info-field-group">
                <span class="info-field-label">Creator</span>
                <div class="info-val with-edit">
                  <div class="info-link-group">
                    <template v-if="form.creator">
                      <a 
                        href="#" 
                        class="info-link" 
                        @click.prevent="searchAndClose(form.creator)"
                        :title="`Search models by creator: ${form.creator}`"
                      >{{ form.creator }}</a>
                      <span 
                        class="info-count-badge" 
                        @click="searchAndClose(form.creator)"
                        :title="`${creatorCount} model${creatorCount === 1 ? '' : 's'} by creator ${form.creator}`"
                      >{{ creatorCount }}</span>
                    </template>
                    <span v-else>-</span>
                  </div>
                  <i class="fas fa-edit edit-icon" @click="promptEditField('creator', 'Creator')" title="Edit Creator"></i>
                </div>
              </div>

              <div class="info-field-group">
                <span class="info-field-label">Original Name</span>
                <div class="info-val with-edit">
                  <span>{{ form.civitaiName || '-' }}</span>
                  <i class="fas fa-edit edit-icon" @click="promptEditField('civitaiName', 'Civitai Name')"></i>
                </div>
              </div>

              <div class="info-field-group">
                <span class="info-field-label">Download Source</span>
                <div class="info-val with-edit">
                  <a 
                    :href="resolvedCivitaiUrl" 
                    target="_blank" 
                    v-if="resolvedCivitaiUrl" 
                    class="download-source-link" 
                    :class="{ 'mature-source': isCivitaiRed }"
                    :title="isCivitaiRed ? 'Opens on Civitai mature portal (civitai.red)' : 'Opens on Civitai'"
                  >
                    <span>{{ getDomainName(resolvedCivitaiUrl) }}</span>
                    <span v-if="isCivitaiRed" class="mature-badge">18+</span>
                    <i class="fas fa-external-link-alt external-icon"></i>
                  </a>
                  <span v-else>-</span>
                  <i class="fas fa-edit edit-icon" @click="promptEditField('civitaiUrl', 'Civitai URL')"></i>
                </div>
              </div>

              <div class="info-field-group">
                <span class="info-field-label">Online Status</span>
                <div class="info-val with-edit">
                  <span v-if="onlineStatusInfo.badge" class="online-status-pill" :class="onlineStatusInfo.cls">
                    <i class="fas" :class="onlineStatusInfo.icon"></i> {{ onlineStatusInfo.text }}
                  </span>
                  <span v-else style="color: var(--color-text-muted); font-size: 0.9em;">Not Checked</span>
                  <i class="fas fa-sync-alt edit-icon" :class="{ 'fa-spin': isCheckingOnline }" @click="checkOnlineAvailability" title="Check if still available online"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- FILE INFO CARD -->
          <div class="detail-card info-card">
            <div class="detail-card-header">
              <i class="fas fa-file-alt text-purple section-title-icon"></i>
              <span class="detail-section-title">File Info</span>
            </div>
            <div class="info-card-content">
              <div class="info-field-group">
                <span class="info-field-label">File Path</span>
                <div class="info-path-box">
                  <span class="info-path-text" :title="model.path">{{ model.path }}</span>
                  <i class="fas fa-folder-open info-path-btn" @click="openFolderPath" title="Open containing folder in file explorer"></i>
                </div>
              </div>

              <div class="info-field-group">
                <span class="info-field-label">Original Filename</span>
                <div class="info-path-box">
                  <span class="info-path-text" :title="originalFilename || '-'">{{ originalFilename || '-' }}</span>
                  <i class="fas fa-copy info-copy-btn" v-if="originalFilename" @click="copyToClipboard(originalFilename)" title="Copy original filename"></i>
                </div>
              </div>
              
              <div class="info-meta-row">
                <div class="info-field-group">
                  <span class="info-field-label">Size</span>
                  <span class="info-meta-val">{{ formatBytes(model.size) }}</span>
                </div>
                
                <div class="info-field-group">
                  <span class="info-field-label">Date Modified</span>
                  <span class="info-meta-val">{{ formatDate(model.date_modified || model.dateModified) }}</span>
                </div>
              </div>

              <div class="info-field-group">
                <span class="info-field-label">SHA256 Hash</span>
                <div class="info-hash-val" :title="model.sha256 || model.hash || '-'">{{ model.sha256 || model.hash || '-' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN -->
        <div class="right-column">
          
          <div class="tabs-header">
            <button :class="{ active: activeTab === 'details' }" @click="activeTab = 'details'">Details</button>
            <button :class="{ active: activeTab === 'civitai' }" @click="activeTab = 'civitai'">Scrape metadata</button>
            <button :class="{ active: activeTab === 'json' }" @click="activeTab = 'json'">Raw JSON</button>
            <button :class="{ active: activeTab === 'files' }" @click="activeTab = 'files'">Files</button>
          </div>

          <!-- TAB: DETAILS -->
          <div class="tab-content details-modern-tab" v-if="activeTab === 'details'">
            
            <!-- Section 1: Model Identity & Filesystem -->
            <div class="detail-card">
              <div class="detail-card-header">
                <i class="fas fa-cube text-muted section-title-icon"></i>
                <span class="detail-section-title">Model Identity</span>
              </div>

              <div class="detail-identity-grid">
                <!-- ROW 1, COL 1: Model Name -->
                <div class="modern-field-group">
                  <div class="field-label-bar">
                    <label><i class="fas fa-tag text-muted"></i> Model Name</label>
                    <div class="field-actions-modern">
                      <button class="btn btn-action-xs" @click="autoFormatIdentity" title="Auto streamline: Clean → Trim → Clean → Version">
                        <i class="fas fa-bolt text-warning"></i> Auto
                      </button>
                      <button class="btn btn-action-xs" @click="setNameFromCivitai" title="Use original name from Civitai">
                        <i class="fas fa-globe text-info"></i> Original
                      </button>
                      <button class="btn btn-action-xs" @click="cleanName" title="Fix capitalization and formatting">
                        <i class="fas fa-broom text-success"></i> Clean
                      </button>
                      <button class="btn btn-action-xs" @click="trimName" title="Remove model keywords">
                        <i class="fas fa-cut text-danger"></i> Trim
                      </button>
                      <button class="btn btn-action-xs" @click="addSliderToName" title="Add slider tag [-5 Less ↔ More 5]">
                        <i class="fas fa-sliders-h text-purple"></i> Slider
                      </button>
                    </div>
                  </div>
                  <input type="text" v-model="form.name" class="form-control modern-input" @change="debouncedSave">
                </div>

                <!-- ROW 1, COL 2: Model Version -->
                <div class="modern-field-group">
                  <div class="field-label-bar">
                    <label><i class="fas fa-code-branch text-muted"></i> Model Version</label>
                    <div class="field-actions-modern">
                      <button class="btn btn-action-xs" @click="guessVersion" title="Guess version from filename">
                        <i class="fas fa-lightbulb text-warning"></i> Guess Version
                      </button>
                      <button class="btn btn-action-xs" @click="cleanVersion" title="Clean formatting">
                        <i class="fas fa-broom text-success"></i> Clean
                      </button>
                      <button class="btn btn-action-xs" @click="clearVersion" title="Clear model version">
                        <i class="fas fa-times text-danger"></i> Clear
                      </button>
                    </div>
                  </div>
                  <input type="text" v-model="form.version" class="form-control modern-input" placeholder="(empty)" @change="debouncedSave">
                </div>

                <!-- ROW 2, COL 1: Filename on Disk & File Tools -->
                <div class="modern-field-group">
                  <div class="field-label-bar">
                    <label><i class="fas fa-file-alt text-muted"></i> Filename on Disk</label>
                    <div class="field-actions-modern" v-if="editingFilename">
                      <button class="btn btn-action-xs" @click="applyRecommendedFilename"><i class="fas fa-magic text-warning"></i> Recommended</button>
                      <button class="btn btn-action-xs" @click="triggerAutoRecommendedRename" title="Auto format name & version, then apply recommended filename"><i class="fas fa-bolt text-warning"></i> Auto</button>
                      <button class="btn btn-action-xs" @click="cleanFilename"><i class="fas fa-broom text-success"></i> Clean</button>
                      <button class="btn btn-action-xs" @click="applyModelName"><i class="fas fa-tag text-purple"></i> Model Name</button>
                      <button class="btn btn-action-xs" @click="appendCreatorSuffix"><i class="fas fa-user-plus text-info"></i> Creator</button>
                    </div>
                  </div>

                  <div class="modern-filename-wrap">
                    <div class="filename-input-box">
                      <input type="text" v-if="!editingFilename" v-model="filenameNoExt" class="form-control modern-input filename-input" readonly>
                      <input type="text" v-else v-model="newFilenameTemp" class="form-control modern-input filename-input editing" @keydown.enter="saveRename">
                      <span class="modern-file-ext">{{ getExtension() }}</span>
                    </div>

                    <!-- Filename Actions Bar -->
                    <div class="filename-actions-bar" v-if="!editingFilename">
                      <button class="btn btn-action-sm" @click="promptRename" title="Rename file on disk">
                        <i class="fas fa-edit text-info"></i> Rename
                      </button>
                      <button class="btn btn-action-sm" @click="triggerRecommendedRename" title="Apply recommended standardized name">
                        <i class="fas fa-magic text-warning"></i> Recommended
                      </button>
                      <button class="btn btn-action-sm" @click="triggerAutoRecommendedRename" title="Auto format name & version, then apply recommended filename">
                        <i class="fas fa-bolt text-warning"></i> Auto
                      </button>

                      <!-- Move button / dropdown -->
                      <div class="move-inline-tool" v-if="!movingFile">
                        <button class="btn btn-action-sm" @click="startMove" title="Move model to folder">
                          <i class="fas fa-arrows-alt text-purple"></i> Move
                        </button>
                      </div>
                      <div class="move-active-box" v-else>
                        <select v-model="targetMoveFolder" class="form-control move-select-sm" :disabled="isMoving">
                          <option v-for="folder in availableMoveFolders" :key="folder" :value="folder">
                            {{ folder === '' ? 'Root' : folder }}
                          </option>
                        </select>
                        <button class="btn btn-success btn-xs" @click="executeMove" :disabled="isMoving">
                          <i class="fas fa-check" v-if="!isMoving"></i>
                          <i class="fas fa-spinner fa-spin" v-else></i>
                        </button>
                        <button class="btn btn-danger btn-xs" @click="movingFile = false" :disabled="isMoving">
                          <i class="fas fa-times"></i>
                        </button>
                      </div>

                      <!-- Priority H/L pill -->
                      <button 
                        class="btn btn-priority-pill" 
                        :class="form.highLow === 'High' ? 'priority-high' : (form.highLow === 'Low' ? 'priority-low' : 'priority-none')" 
                        @click="toggleHighLow" 
                        title="Toggle High/Low Priority"
                      >
                        <i class="fas fa-flag"></i> H/L: {{ form.highLow || 'None' }}
                      </button>
                    </div>

                    <div class="filename-actions-bar editing" v-else>
                      <button class="btn btn-success btn-sm btn-save-rename" @click="saveRename" :disabled="isRenaming">
                        <i class="fas fa-spinner fa-spin" v-if="isRenaming"></i>
                        <i class="fas fa-check" v-else></i>
                        {{ isRenaming ? 'Renaming...' : 'Save Rename' }}
                      </button>
                      <button class="btn btn-secondary btn-sm" @click="cancelRename" :disabled="isRenaming">
                        <i class="fas fa-times"></i> Cancel
                      </button>
                    </div>
                  </div>
                </div>

                <!-- ROW 2, COL 2: Preferred Weight & Slider Configuration -->
                <div class="modern-field-group">
                  <div class="field-label-bar">
                    <label><i class="fas fa-balance-scale text-muted"></i> Preferred Weight</label>
                    <button 
                      type="button" 
                      class="btn btn-slider-mode-toggle"
                      :class="form.isSlider ? 'active' : ''" 
                      @click="toggleSliderMode"
                      title="Toggle Slider Mode"
                    >
                      <span class="slider-toggle-indicator" :class="{ on: form.isSlider }"></span>
                      <i class="fas fa-sliders-h text-purple"></i>
                      <span>Slider: {{ form.isSlider ? 'ON' : 'OFF' }}</span>
                    </button>
                  </div>

                  <!-- Fat Track Slider Bar with dynamic value pin -->
                  <div class="modern-slider-container">
                    <div class="custom-slider-wrapper" style="flex: 1; position: relative;">
                      <!-- Dynamic Floating Value Pin -->
                      <div 
                        class="thumb-value-pin"
                        :style="{
                          position: 'absolute',
                          left: `${sliderThumbPct}%`,
                          transform: 'translateX(-50%)',
                          top: '-24px',
                          zIndex: 5,
                          pointerEvents: 'none'
                        }"
                      >
                        <div class="value-pin-bubble">
                          <i class="fas fa-caret-down pin-caret"></i>
                          <span>{{ form.preferredWeight }}</span>
                        </div>
                      </div>

                      <!-- Fat Track -->
                      <div class="fat-track-modern">
                        <div 
                          class="track-fill-highlight" 
                          :style="{
                            position: 'absolute',
                            top: 0,
                            bottom: 0,
                            left: Math.min(sliderZeroPct, sliderThumbPct) + '%',
                            width: Math.abs(sliderThumbPct - sliderZeroPct) + '%',
                            background: 'var(--slider-gradient, linear-gradient(90deg, #3498db 0%, #9b59b6 100%))',
                            opacity: 0.65,
                            borderRadius: '4px'
                          }"
                        ></div>

                        <!-- Neutral Zero Marker Line (Center line) -->
                        <div 
                          v-if="sliderMinVal < 0 && sliderMaxVal > 0"
                          class="zero-marker"
                          :style="{
                            position: 'absolute',
                            left: `${sliderZeroPct}%`,
                            transform: 'translateX(-50%)',
                            top: 0,
                            bottom: 0,
                            width: '2px',
                            background: 'var(--slider-zero-marker, rgba(255, 255, 255, 0.5))',
                            zIndex: 2
                          }"
                          title="Neutral (0)"
                        ></div>

                        <!-- Dragging Marker Thumb Line on the track itself -->
                        <div 
                          class="track-thumb-indicator"
                          :style="{
                            position: 'absolute',
                            left: `${sliderThumbPct}%`,
                            transform: 'translateX(-50%)',
                            top: '2px',
                            bottom: '2px',
                            width: '4px',
                            background: 'var(--slider-thumb-color, #38bdf8)',
                            borderRadius: '2px',
                            boxShadow: 'var(--slider-thumb-shadow, 0 0 6px rgba(56, 189, 248, 0.9))',
                            zIndex: 3
                          }"
                        ></div>

                        <div class="track-endpoint left">
                          <span class="badge-endpoint min">
                            <span class="badge-num">{{ sliderMinVal }}</span>
                            <span v-if="form.isSlider && form.sliderMinDesc" class="badge-label">{{ form.sliderMinDesc }}</span>
                          </span>
                        </div>

                        <div class="track-endpoint right">
                          <span class="badge-endpoint max">
                            <span v-if="form.isSlider && form.sliderMaxDesc" class="badge-label">{{ form.sliderMaxDesc }}</span>
                            <span class="badge-num">{{ sliderMaxVal }}</span>
                          </span>
                        </div>
                      </div>

                      <!-- Native Range Input -->
                      <input 
                        type="range" 
                        :min="sliderMinVal" 
                        :max="sliderMaxVal" 
                        step="0.1" 
                        v-model.number="form.preferredWeight" 
                        class="fat-slider-input"
                      >
                    </div>

                    <!-- Number Input box alongside -->
                    <input type="number" v-model.number="form.preferredWeight" class="weight-number-input" step="0.1">
                  </div>

                  <!-- Compact Slider Endpoint Configuration -->
                  <div v-if="form.isSlider" class="compact-slider-config">
                    <!-- Min Endpoint -->
                    <div class="endpoint-control-row min">
                      <span class="endpoint-pill min">Min</span>
                      <div class="stepper-group min">
                        <button type="button" class="btn-stepper" @click="stepSliderMin(-0.5)" title="Decrease Min (-0.5)">-</button>
                        <input type="number" v-model.number="form.sliderMin" step="0.5" class="stepper-input min" @change="debouncedSave">
                        <button type="button" class="btn-stepper" @click="stepSliderMin(0.5)" title="Increase Min (+0.5)">+</button>
                      </div>
                      <input 
                        type="text" 
                        v-model="form.sliderMinDesc" 
                        placeholder="Description (e.g. Dark)" 
                        class="form-control compact-desc-input"
                        @change="debouncedSave"
                      >
                    </div>

                    <!-- Max Endpoint -->
                    <div class="endpoint-control-row max">
                      <span class="endpoint-pill max">Max</span>
                      <div class="stepper-group max">
                        <button type="button" class="btn-stepper" @click="stepSliderMax(-0.5)" title="Decrease Max (-0.5)">-</button>
                        <input type="number" v-model.number="form.sliderMax" step="0.5" class="stepper-input max" @change="debouncedSave">
                        <button type="button" class="btn-stepper" @click="stepSliderMax(0.5)" title="Increase Max (+0.5)">+</button>
                      </div>
                      <input 
                        type="text" 
                        v-model="form.sliderMaxDesc" 
                        placeholder="Description (e.g. Light)" 
                        class="form-control compact-desc-input"
                        @change="debouncedSave"
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 2: Categorization & Tags -->
            <div class="detail-card">
              <div class="detail-card-header">
                <i class="fas fa-tags text-muted section-title-icon"></i>
                <span class="detail-section-title">Categorization &amp; Tags</span>
              </div>

              <div class="categorization-grid">
                <!-- Col 1: Category & Subcategory side by side -->
                <div class="cat-fields-row">
                  <div class="modern-field-group" style="flex: 1;">
                    <div class="field-label-bar">
                      <label><i class="fas fa-folder text-muted"></i> Category</label>
                    </div>
                    <div class="input-with-clear">
                      <input type="text" v-model="form.category" class="form-control modern-input" placeholder="(empty)" @change="debouncedSave" list="categoriesListModern">
                      <i class="fas fa-times clear-btn" v-if="form.category" @mousedown.prevent="form.category = ''; debouncedSave()" title="Clear"></i>
                    </div>
                    <datalist id="categoriesListModern">
                      <option v-for="opt in uniqueCategories" :key="opt" :value="opt"></option>
                    </datalist>
                  </div>

                  <div class="modern-field-group" style="flex: 1;">
                    <div class="field-label-bar">
                      <label><i class="fas fa-folder-open text-muted"></i> Subcategory</label>
                    </div>
                    <div class="input-with-clear">
                      <input type="text" v-model="form.subcategory" class="form-control modern-input" placeholder="(empty)" @change="debouncedSave" list="subcategoriesListModern">
                      <i class="fas fa-times clear-btn" v-if="form.subcategory" @mousedown.prevent="form.subcategory = ''; debouncedSave()" title="Clear"></i>
                    </div>
                    <datalist id="subcategoriesListModern">
                      <option v-for="opt in uniqueSubcategories" :key="opt" :value="opt"></option>
                    </datalist>
                  </div>
                </div>

                <!-- Col 2: Tags Cloud -->
                <div class="modern-field-group">
                  <div class="field-label-bar">
                    <label><i class="fas fa-hashtag text-muted"></i> Search &amp; Filter Tags</label>
                    <span class="tag-counter-pill">{{ parsedTags.length }} tags</span>
                  </div>
                  <div class="modern-tag-cloud" @click="focusTagInput">
                    <span class="modern-tag-pill" v-for="(tag, index) in parsedTags" :key="index">
                      <span>{{ tag }}</span>
                      <i class="fas fa-times remove-tag-icon" @click.stop="removeTag(index)"></i>
                    </span>
                    <input 
                      type="text" 
                      ref="tagInputRef"
                      v-model="newTag" 
                      @keydown.enter.prevent="addTag" 
                      @keydown.tab="addTagIfNotEmpty" 
                      @keydown.delete="handleTagDelete" 
                      @blur="addTag"
                      placeholder="Add tag and press Enter..." 
                      class="modern-tag-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 3: Keywords & Prompts -->
            <div class="detail-card">
              <div class="detail-card-header">
                <i class="fas fa-terminal text-muted section-title-icon"></i>
                <span class="detail-section-title">Keywords &amp; Prompts</span>
              </div>

              <div class="prompts-grid-modern">
                <!-- Column 1: Trigger Tokens -->
                <div class="prompts-col">
                  <!-- Trigger Words -->
                  <div class="modern-field-group">
                    <div class="field-label-bar">
                      <label><i class="fas fa-plus text-muted"></i> Trigger Words (WebUI)</label>
                      <button class="btn btn-copy-mini" @click="copyToClipboard(form.activationText)" title="Copy trigger words">
                        <i class="fas fa-copy text-info"></i> Copy
                      </button>
                    </div>
                    <textarea v-model="form.activationText" class="form-control modern-textarea" placeholder="(empty)" @change="debouncedSave"></textarea>
                  </div>

                  <!-- Negative Trigger Words -->
                  <div class="modern-field-group">
                    <div class="field-label-bar">
                      <label><i class="fas fa-minus-circle text-muted"></i> Negative Trigger Words</label>
                      <button class="btn btn-copy-mini" @click="copyToClipboard(form.negativeTriggerWords)" title="Copy negative words">
                        <i class="fas fa-copy text-info"></i> Copy
                      </button>
                    </div>
                    <textarea v-model="form.negativeTriggerWords" class="form-control modern-textarea" placeholder="(empty)" @change="debouncedSave"></textarea>
                  </div>

                  <!-- All Trigger Words -->
                  <div class="modern-field-group">
                    <div class="field-label-bar">
                      <label><i class="fas fa-list-ul text-muted"></i> All Trigger Words (Civitai)</label>
                      <button class="btn btn-copy-mini" @click="copyToClipboard(form.allTriggerWords)" title="Copy all trigger words">
                        <i class="fas fa-copy text-info"></i> Copy
                      </button>
                    </div>
                    <textarea v-model="form.allTriggerWords" class="form-control modern-textarea" placeholder="(empty)" @change="debouncedSave"></textarea>
                  </div>
                </div>

                <!-- Column 2: Prompts & Description -->
                <div class="prompts-col">
                  <!-- Example Prompt 1 -->
                  <div class="modern-field-group">
                    <div class="field-label-bar">
                      <label><i class="fas fa-comment-alt text-muted"></i> Example Prompt 1</label>
                      <button class="btn btn-copy-mini" @click="copyToClipboard(form.examplePrompt)" title="Copy prompt 1">
                        <i class="fas fa-copy text-info"></i> Copy
                      </button>
                    </div>
                    <textarea v-model="form.examplePrompt" class="form-control modern-textarea" placeholder="(empty)" @change="debouncedSave"></textarea>
                  </div>

                  <!-- Example Prompt 2 -->
                  <div class="modern-field-group">
                    <div class="field-label-bar">
                      <label><i class="fas fa-comment-alt text-muted"></i> Example Prompt 2</label>
                      <button class="btn btn-copy-mini" @click="copyToClipboard(form.examplePrompt2)" title="Copy prompt 2">
                        <i class="fas fa-copy text-info"></i> Copy
                      </button>
                    </div>
                    <textarea v-model="form.examplePrompt2" class="form-control modern-textarea" placeholder="(empty)" @change="debouncedSave"></textarea>
                  </div>

                  <!-- Description -->
                  <div class="modern-field-group">
                    <div class="field-label-bar">
                      <label><i class="fas fa-info-circle text-muted"></i> Model Description</label>
                    </div>
                    <textarea v-model="form.description" class="form-control modern-textarea" placeholder="(empty)" @change="debouncedSave"></textarea>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section 4: Notes -->
            <div class="detail-card">
              <div class="detail-card-header">
                <i class="fas fa-sticky-note text-muted section-title-icon"></i>
                <span class="detail-section-title">Notes</span>
              </div>
              <textarea v-model="form.notes" class="form-control modern-textarea notes-textarea" placeholder="Add custom notes, recommended settings, clip skips, or trigger guidelines..." @change="debouncedSave"></textarea>
            </div>

          </div>

          <!-- TAB: CIVITAI MANAGEMENT / SCRAPE METADATA -->
          <div class="tab-content civitai-tab" v-else-if="activeTab === 'civitai'">
            
            <!-- Hero: All-in-One Fetch -->
            <div class="civitai-hero-card">
              <div class="hero-header">
                <i class="fas fa-bolt hero-icon text-warning"></i>
                <div class="hero-title-wrap">
                  <h3>All-in-One Civitai Fetch</h3>
                  <span class="all-in-one-tag">Metadata &amp; Thumbnails</span>
                </div>
              </div>
              <p class="hero-desc">
                Downloads complete model metadata (trigger words, description, tags) and preview thumbnails in one unified command.
              </p>
              <button class="btn btn-hero-fetch" @click="fetchAllCivitaiData">
                <i class="fas fa-bolt text-warning"></i>
                <span>Get All Civitai Data (All Steps)</span>
              </button>
            </div>

            <!-- 4-Step Sequenced Action Cards Grid -->
            <div class="step-cards-grid">
              
              <!-- Step 1: Check Online Availability -->
              <div class="step-card">
                <div class="step-card-header">
                  <span class="step-badge">1</span>
                  <i class="fas fa-globe header-icon text-success"></i>
                  <h4>Check Online Availability</h4>
                </div>
                <p class="step-desc">Audit whether this model is still live on Civitai or preserved on CivArchive.</p>
                <div class="step-status-row">
                  <span class="status-label">Status:</span>
                  <span v-if="onlineStatusInfo.badge" class="online-status-pill" :class="onlineStatusInfo.cls">
                    <i class="fas" :class="onlineStatusInfo.icon"></i> {{ onlineStatusInfo.text }}
                  </span>
                  <span v-else class="status-unchecked-pill">
                    <i class="fas fa-question-circle text-warning"></i> Not Checked
                  </span>
                </div>
                <div class="step-btn-row">
                  <button class="btn btn-action" @click="checkOnlineAvailability" :disabled="isCheckingOnline" title="Check availability on Civitai and CivArchive">
                    <i class="fas" :class="isCheckingOnline ? 'fa-spinner fa-spin' : 'fa-globe text-success'"></i>
                    <span>Check Availability</span>
                  </button>
                </div>
              </div>

              <!-- Step 2: Generate Hashes -->
              <div class="step-card">
                <div class="step-card-header">
                  <span class="step-badge">2</span>
                  <i class="fas fa-hashtag header-icon text-purple"></i>
                  <h4>Generate SHA256 Hash</h4>
                </div>
                <p class="step-desc">Calculate file checksum used for exact Civitai matching and duplicate detection.</p>
                <div class="step-btn-row">
                  <button class="btn btn-action" @click="generateHash" title="Calculate SHA256 checksum">
                    <i class="fas fa-fingerprint text-purple"></i>
                    <span>Generate SHA256 Hash</span>
                  </button>
                </div>
              </div>

              <!-- Step 3: Scrape Metadata -->
              <div class="step-card">
                <div class="step-card-header">
                  <span class="step-badge">3</span>
                  <i class="fas fa-cloud-download-alt header-icon text-info"></i>
                  <h4>Scrape Metadata</h4>
                </div>
                <p class="step-desc">Fetch model information, trigger words, and tags via hash lookup or manual URL.</p>
                <div class="step-btn-row wrap-btns">
                  <button class="btn btn-action" @click="fetchCivitaiByHash" title="Fetch metadata from Civitai by hash">
                    <i class="fas fa-cloud-download-alt text-info"></i>
                    <span>Civitai</span>
                  </button>
                  <button class="btn btn-action" @click="fetchCivArchiveByHash" title="Search the community archive by hash">
                    <i class="fas fa-archive text-purple"></i>
                    <span>CivArchive</span>
                  </button>
                  <button class="btn btn-action" @click="promptCivitaiUrl" title="Manually link this model to a Civitai page">
                    <i class="fas fa-link text-info"></i>
                    <span>By URL</span>
                  </button>
                </div>
              </div>

              <!-- Step 4: Download Thumbnails -->
              <div class="step-card">
                <div class="step-card-header">
                  <span class="step-badge">4</span>
                  <i class="fas fa-image header-icon text-warning"></i>
                  <h4>Download Thumbnails</h4>
                </div>
                <p class="step-desc">Download preview images from Civitai and standardize thumbnail filenames.</p>
                <div class="step-btn-row">
                  <button class="btn btn-action" @click="downloadThumbnails" title="Download preview images from Civitai">
                    <i class="fas fa-images text-warning"></i>
                    <span>Get Thumbnails</span>
                  </button>
                  <button class="btn btn-action" @click="fixThumbnail" title="Ensures the thumbnail uses the correct format">
                    <i class="fas fa-wrench text-info"></i>
                    <span>Fix Format</span>
                  </button>
                </div>
              </div>

            </div>

          </div>

          <!-- TAB: FILES -->
          <div class="tab-content files-tab" v-else-if="activeTab === 'files'">
            <div class="files-card">
              <div class="files-header-bar">
                <div class="files-title-group">
                  <div class="files-icon-box">
                    <i class="fas fa-folder-tree text-info"></i>
                  </div>
                  <div>
                    <h3>Associated Model Files</h3>
                    <p class="files-subtitle">Physical model file and all associated sidecars (.json, .preview.png, etc.) on disk.</p>
                  </div>
                </div>

                <div class="files-controls">
                  <span class="files-summary-pill" v-if="associatedFiles.length > 0">
                    <i class="fas fa-layer-group text-purple"></i>
                    <span>{{ associatedFiles.length }} files &bull; {{ formatBytes(totalAssociatedSize) }}</span>
                  </span>
                  <button class="btn btn-action-sm" @click="fetchAssociatedFiles" :disabled="isLoadingFiles" title="Refresh file list">
                    <i class="fas" :class="isLoadingFiles ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i>
                    <span>Refresh</span>
                  </button>
                </div>
              </div>

              <!-- Loading State -->
              <div v-if="isLoadingFiles" class="files-loading-state">
                <i class="fas fa-spinner fa-spin fa-2x text-info"></i>
                <span>Loading associated files...</span>
              </div>

              <!-- Files Table -->
              <div class="files-table-container" v-else-if="associatedFiles.length > 0">
                <table class="files-table">
                  <thead>
                    <tr>
                      <th class="th-preview">Preview</th>
                      <th class="th-filename">Filename</th>
                      <th class="th-type">Type</th>
                      <th class="th-size">Size</th>
                      <th class="th-actions">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="file in associatedFiles" :key="file.path" class="file-row">
                      <!-- Preview / Icon -->
                      <td class="td-preview">
                        <div 
                          v-if="file.type === 'image'" 
                          class="file-thumb-wrap" 
                          @click="handleAssociatedImageClick(file)"
                          title="Click to preview image"
                        >
                          <img 
                            :src="api.getAssetUrl(file.relativePath, modelsStore.getCacheBuster(model.path))" 
                            alt="preview" 
                            class="file-thumb-img" 
                          />
                          <div class="thumb-zoom-overlay">
                            <i class="fas fa-search-plus"></i>
                          </div>
                        </div>
                        <div v-else class="file-icon-box" :class="'icon-' + file.type">
                          <i class="fas" :class="getFileIcon(file.filename)"></i>
                        </div>
                      </td>

                      <!-- Filename -->
                      <td class="td-filename">
                        <div class="file-name-wrap" :title="file.path">
                          <span class="file-main-name">{{ file.filename }}</span>
                        </div>
                      </td>

                      <!-- File Type Badge -->
                      <td class="td-type">
                        <span class="file-type-pill" :class="'type-' + file.type">
                          <i class="fas fa-cube" v-if="file.type === 'model'"></i>
                          <i class="fas fa-file-code" v-else-if="file.type === 'metadata'"></i>
                          <i class="fas fa-image" v-else-if="file.type === 'image'"></i>
                          <i class="fas fa-file-alt" v-else-if="file.type === 'text'"></i>
                          <i class="fas fa-film" v-else-if="file.type === 'video'"></i>
                          <i class="fas fa-file" v-else></i>
                          {{ file.type.toUpperCase() }}
                        </span>
                      </td>

                      <!-- Size -->
                      <td class="td-size">
                        <span class="file-size-text">{{ formatBytes(file.sizeBytes) }}</span>
                      </td>

                      <!-- Actions -->
                      <td class="td-actions">
                        <button 
                          class="btn-file-delete" 
                          @click="deleteAssociatedFile(file)" 
                          :title="file.type === 'model' ? 'Delete entire model file!' : 'Delete this sidecar file'"
                        >
                          <i class="fas fa-trash-alt"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Empty State -->
              <div class="files-empty-state" v-else>
                <i class="fas fa-folder-open empty-icon"></i>
                <h4>No Associated Files Found</h4>
                <p>No matching files were discovered sharing the model prefix in this directory.</p>
                <button class="btn btn-action-sm" @click="fetchAssociatedFiles">
                  <i class="fas fa-sync-alt"></i> Try Refreshing
                </button>
              </div>
            </div>

            <!-- Local File Management -->
            <div class="local-tools-card">
              <div class="local-tools-header">
                <i class="fas fa-folder-open text-muted"></i>
                <div class="local-title-wrap">
                  <h4>Local File Tools</h4>
                  <span class="local-desc">Manage physical model files and directories on disk</span>
                </div>
              </div>
              <div class="local-tools-actions">
                <!-- Move Model -->
                <div class="tool-cell move-cell">
                  <button class="btn btn-action btn-full" @click="startMove" v-if="!movingFile">
                    <i class="fas fa-arrows-alt text-info"></i>
                    <span>Move Model to Folder</span>
                  </button>
                  <div class="move-inline-wrap" v-else>
                    <span class="move-label">Move to folder:</span>
                    <div class="move-controls">
                      <select v-model="targetMoveFolder" class="form-control move-select" :disabled="isMoving">
                        <option v-for="folder in availableMoveFolders" :key="folder" :value="folder">
                          {{ folder === '' ? 'Root' : folder }}
                        </option>
                      </select>
                      <button class="btn btn-success btn-move-confirm" @click="executeMove" :disabled="isMoving">
                        <i class="fas fa-check" v-if="!isMoving"></i>
                        <i class="fas fa-spinner fa-spin" v-else></i>
                        <span>Move</span>
                      </button>
                      <button class="btn btn-secondary btn-move-cancel" @click="movingFile = false" :disabled="isMoving">
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Delete Model -->
                <div class="tool-cell delete-cell">
                  <button class="btn btn-danger-action btn-full" @click="deleteModel">
                    <i class="fas fa-trash-alt"></i>
                    <span>Delete Model File &amp; Metadata</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB: RAW JSON -->
          <div class="tab-content json-tab" v-else-if="activeTab === 'json'">
            <div class="json-card">
              <!-- Header Bar -->
              <div class="json-header-bar">
                <div class="json-title-group">
                  <div class="json-icon-box">
                    <i class="fas fa-code text-info"></i>
                  </div>
                  <div>
                    <div class="json-title-row">
                      <h3>Model JSON Sidecar</h3>
                      <span v-if="isJsonValid" class="json-status-pill valid">
                        <i class="fas fa-check-circle"></i> Valid JSON
                      </span>
                      <span v-else class="json-status-pill invalid">
                        <i class="fas fa-exclamation-triangle"></i> Syntax Error
                      </span>
                    </div>
                    <p class="json-subtitle">Physical .json metadata containing trigger words, notes, and Civitai parameters.</p>
                  </div>
                </div>

                <!-- Action Toolbar -->
                <div class="json-toolbar">
                  <button class="btn btn-action-sm" @click="copyRawJson" title="Copy raw JSON to clipboard">
                    <i class="fas fa-copy"></i>
                    <span>Copy</span>
                  </button>
                  <button class="btn btn-action-sm" @click="formatRawJson" title="Prettify and format JSON">
                    <i class="fas fa-magic"></i>
                    <span>Format</span>
                  </button>
                  <button class="btn btn-action-sm" @click="resetRawJson" title="Revert changes back to saved state">
                    <i class="fas fa-undo"></i>
                    <span>Reset</span>
                  </button>
                  <button 
                    class="btn btn-save-json" 
                    @click="saveRawJson" 
                    :disabled="!isJsonValid" 
                    title="Save changes to sidecar .json file"
                  >
                    <i class="fas fa-save"></i>
                    <span>Save JSON</span>
                  </button>
                </div>
              </div>

              <!-- Editor Box -->
              <div class="json-editor-wrap">
                <textarea 
                  v-model="rawJsonText" 
                  class="json-editor" 
                  spellcheck="false"
                  placeholder="Enter JSON metadata..."
                ></textarea>
              </div>

              <!-- Footer Bar -->
              <div class="json-footer-bar">
                <div class="json-stats">
                  <span><i class="fas fa-align-left text-muted"></i> {{ jsonStats.lines }} lines</span>
                  <span class="stat-dot">&bull;</span>
                  <span><i class="fas fa-font text-muted"></i> {{ jsonStats.chars.toLocaleString() }} characters</span>
                </div>
                <div class="json-syntax-indicator" :class="{ 'has-error': !isJsonValid }">
                  <span v-if="isJsonValid"><i class="fas fa-shield-alt text-success"></i> Ready to save</span>
                  <span v-else><i class="fas fa-times-circle text-danger"></i> Correct syntax error before saving</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
      
    </div>

    <!-- FULL SIZE IMAGE CAROUSEL LIGHTBOX -->
    <div 
      v-if="showImageCarousel && images.length > 0" 
      class="image-carousel-lightbox" 
      @click.self="closeImageCarousel"
    >
      <div class="carousel-top-bar">
        <div class="carousel-title-group">
          <span class="carousel-model-name">{{ form.name || model?.name || 'Model Image Preview' }}</span>
          <span class="carousel-counter">{{ carouselIndex + 1 }} / {{ images.length }}</span>
        </div>
        <div class="carousel-actions">
          <a 
            :href="api.getAssetUrl(images[carouselIndex], modelsStore.getCacheBuster(model.path))" 
            target="_blank" 
            class="btn btn-secondary btn-icon carousel-action-btn"
            title="Open original image in new tab"
          >
            <i class="fas fa-external-link-alt"></i>
          </a>
          <button 
            type="button" 
            class="btn btn-secondary btn-icon carousel-action-btn" 
            @click="closeImageCarousel" 
            title="Close preview (Esc)"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <!-- Main Carousel Content Viewport -->
      <div class="carousel-stage">
        <button 
          v-if="images.length > 1"
          type="button" 
          class="carousel-nav-btn prev-btn" 
          @click.stop="prevCarouselImage" 
          title="Previous image (Left Arrow)"
        >
          <i class="fas fa-chevron-left"></i>
        </button>

        <div class="carousel-image-wrapper" @click.self="closeImageCarousel">
          <img 
            :src="api.getAssetUrl(images[carouselIndex], modelsStore.getCacheBuster(model.path))" 
            :alt="`${form.name || 'Model'} Image ${carouselIndex + 1}`" 
            class="carousel-main-img"
            @click="images.length > 1 ? nextCarouselImage() : null"
            :title="images.length > 1 ? 'Click to advance to next image' : ''"
          />
        </div>

        <button 
          v-if="images.length > 1"
          type="button" 
          class="carousel-nav-btn next-btn" 
          @click.stop="nextCarouselImage" 
          title="Next image (Right Arrow)"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>

      <!-- Bottom Thumbnail Carousel Filmstrip -->
      <div class="carousel-bottom-filmstrip" v-if="images.length > 1">
        <div 
          v-for="(img, idx) in images" 
          :key="idx"
          class="carousel-filmstrip-thumb"
          :class="{ active: idx === carouselIndex }"
          @click="selectCarouselImage(idx)"
        >
          <img 
            :src="api.getAssetUrl(img, modelsStore.getCacheBuster(model.path))" 
            alt="Thumbnail"
            loading="lazy"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, watch, nextTick } from 'vue';
import { api } from '../../api/client';
import { useModelsStore } from '../../stores/models';
import { useSettingsStore } from '../../stores/settings';
import { useToast } from '../../composables/useToast';

const props = defineProps({
  modelId: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['close', 'change-model']);

const navigatePrevious = () => {
  const modelsList = modelsStore.filteredModels && modelsStore.filteredModels.length > 0 
    ? modelsStore.filteredModels 
    : modelsStore.models;
  const currentIndex = modelsList.findIndex(m => m.id === props.modelId);
  if (currentIndex > 0) {
    const prevModel = modelsList[currentIndex - 1];
    emit('change-model', prevModel.id);
  }
};

const navigateNext = () => {
  const modelsList = modelsStore.filteredModels && modelsStore.filteredModels.length > 0 
    ? modelsStore.filteredModels 
    : modelsStore.models;
  const currentIndex = modelsList.findIndex(m => m.id === props.modelId);
  if (currentIndex >= 0 && currentIndex < modelsList.length - 1) {
    const nextModel = modelsList[currentIndex + 1];
    emit('change-model', nextModel.id);
  }
};
const modelsStore = useModelsStore();
const settingsStore = useSettingsStore();
const toast = useToast();

const model = ref(null);
const loading = ref(true);
const fileInput = ref(null);
const activeTab = ref('details');
const associatedFiles = ref([]);
const isLoadingFiles = ref(false);

const fetchAssociatedFiles = async () => {
  if (model.value && model.value.path) {
    isLoadingFiles.value = true;
    try {
      associatedFiles.value = await api.getAssociatedFiles(model.value.path);
    } catch (e) {
      console.error(e);
      toast.showToast('Failed to fetch associated files', 'error');
    } finally {
      isLoadingFiles.value = false;
    }
  }
};

const deleteAssociatedFile = async (file) => {
  if (!confirm(`Are you sure you want to delete ${file.filename}?\nThis action cannot be undone.`)) return;
  try {
    const res = await api.deleteAssociatedFile(file.path);
    if (res.status === 'success') {
      toast.showToast(`Deleted ${file.filename}`, 'success');
      await fetchAssociatedFiles();
      if (file.type === 'model') {
         await modelsStore.fetchModels(true);
         emit('close');
      }
    } else {
      toast.showToast(res.message || 'Failed to delete file', 'error');
    }
  } catch (e) {
    console.error(e);
    toast.showToast('Failed to delete file', 'error');
  }
};

// Image Carousel State
const images = ref([]);
const currentImageIndex = ref(0);
const showImageCarousel = ref(false);
const carouselIndex = ref(0);

const openImageCarousel = (idx = currentImageIndex.value) => {
  if (!images.value || images.value.length === 0) return;
  carouselIndex.value = Math.max(0, Math.min(idx, images.value.length - 1));
  showImageCarousel.value = true;
};

const closeImageCarousel = () => {
  showImageCarousel.value = false;
};

const nextCarouselImage = () => {
  if (!images.value || images.value.length === 0) return;
  carouselIndex.value = (carouselIndex.value + 1) % images.value.length;
  currentImageIndex.value = carouselIndex.value;
};

const prevCarouselImage = () => {
  if (!images.value || images.value.length === 0) return;
  carouselIndex.value = (carouselIndex.value - 1 + images.value.length) % images.value.length;
  currentImageIndex.value = carouselIndex.value;
};

const selectCarouselImage = (idx) => {
  carouselIndex.value = idx;
  currentImageIndex.value = idx;
};

const handleMainImageClick = () => {
  if (images.value && images.value.length > 0) {
    openImageCarousel(currentImageIndex.value);
  } else {
    triggerFileInput();
  }
};

const openFolderPath = async () => {
  if (!model.value || !model.value.path) return;
  try {
    await api.openFolder(model.value.path);
  } catch (err) {
    console.error("Failed to open folder:", err);
    toast.showToast('Failed to open folder', 'error');
  }
};

// Raw JSON State
const rawJsonText = ref('');

// Form Data for two-way binding
const form = reactive({
  name: '',
  baseModel: '',
  sdVersion: '',
  creator: '',
  civitaiName: '',
  civitaiUrl: '',
  nsfw: false,
  preferredWeight: 1.0,
  isSlider: false,
  sliderMin: -3.0,
  sliderMax: 3.0,
  sliderMinDesc: '',
  sliderMaxDesc: '',
  version: '',
  highLow: '',
  tested: false,
  category: '',
  subcategory: '',
  tags: '',
  activationText: '',
  negativeTriggerWords: '',
  allTriggerWords: '',
  examplePrompt: '',
  examplePrompt2: '',
  notes: '',
  description: '',
  originalFilename: ''
});

// UI State
const hoverName = ref(false);
const focusName = ref(false);
const hoverVersion = ref(false);
const focusVersion = ref(false);

const editingFilename = ref(false);
const newFilenameTemp = ref('');
const movingFile = ref(false);
const targetMoveFolder = ref('');
const isRenaming = ref(false);
const isMoving = ref(false);

const tagInputRef = ref(null);
const newTag = ref('');

const parsedTags = computed(() => {
  if (!form.tags) return [];
  return form.tags.split(',').map(s => s.trim()).filter(s => s);
});

const addTag = () => {
  const t = newTag.value.trim();
  if (!t) return;
  const currentTags = [...parsedTags.value];
  if (!currentTags.includes(t)) {
    currentTags.push(t);
    form.tags = currentTags.join(', ');
    debouncedSave();
  }
  newTag.value = '';
};

const addTagIfNotEmpty = (e) => {
  if (newTag.value.trim()) {
    e.preventDefault();
    addTag();
  }
};

const handleTagDelete = (e) => {
  if (newTag.value === '' && parsedTags.value.length > 0) {
    e.preventDefault();
    removeTag(parsedTags.value.length - 1);
  }
};

const removeTag = (index) => {
  const currentTags = [...parsedTags.value];
  currentTags.splice(index, 1);
  form.tags = currentTags.join(', ');
  debouncedSave();
};

const focusTagInput = () => {
  if (tagInputRef.value) {
    tagInputRef.value.focus();
  }
};


const filenameNoExt = computed(() => {
  if (!model.value || !model.value.filename) return '';
  const parts = model.value.filename.split('.');
  if (parts.length > 1) parts.pop();
  return parts.join('.');
});

const originalFilename = computed(() => {
  const json = model.value?.json || {};
  const wcd = json.web_civitai_data || {};
  return wcd.original_filename || 
         wcd['original filename'] || 
         wcd.originalFilename || 
         json.original_filename || 
         json['original filename'] || 
         json.originalFilename || 
         model.value?.original_filename || 
         model.value?.originalFilename || 
         '';
});

const resolvedCivitaiUrl = computed(() => {
  const raw = form.civitaiUrl || form.civitai_url || '';
  if (!raw) return '';
  if (form.nsfw) {
    return raw.replace(/civitai\.com/gi, 'civitai.red');
  } else {
    return raw.replace(/civitai\.red/gi, 'civitai.com');
  }
});

const isCivitaiRed = computed(() => {
  return Boolean(resolvedCivitaiUrl.value && /civitai\.red/i.test(resolvedCivitaiUrl.value));
});

const availableMoveFolders = computed(() => {
  const baseModel = form.baseModel || (model.value ? (model.value.base_model || model.value.baseModel) : '') || '';
  const roots = settingsStore.modelTypeRoots || [];
  const matchedRoot = roots.find(r => r.baseModel && r.baseModel.trim().toLowerCase() === baseModel.trim().toLowerCase());
  
  let folderPaths = (modelsStore.folders || []).map(f => f.path);
  
  if (matchedRoot && matchedRoot.rootFolder && matchedRoot.rootFolder.trim()) {
    const rawRoot = matchedRoot.rootFolder.trim().replace(/\\/g, '/').replace(/\/+$/, '');
    const rootLower = rawRoot.toLowerCase();
    
    folderPaths = folderPaths.filter(f => {
      const normF = (f || '').replace(/\\/g, '/').toLowerCase();
      return normF === rootLower || normF.startsWith(rootLower + '/');
    });
    
    const exactOrCasedRoot = folderPaths.find(f => (f || '').replace(/\\/g, '/').toLowerCase() === rootLower);
    if (!exactOrCasedRoot) {
      folderPaths.unshift(rawRoot);
    }
  } else {
    if (!folderPaths.includes('')) {
      folderPaths.unshift('');
    }
  }
  
  return folderPaths;
});

const getExtension = () => {
  if (!model.value || !model.value.filename) return '';
  const parts = model.value.filename.split('.');
  return '.' + (parts.length > 1 ? parts.pop() : '');
};

const loadModel = async () => {
  loading.value = true;
  try {
    const data = await api.getModel(props.modelId, modelsStore.currentLocation);
    model.value = data;
    
    // Map to form
    form.name = data.name || '';
    form.baseModel = data.baseModel || '';
    form.sdVersion = data.sdVersion || '';
    form.creator = data.creator || '';
    form.civitaiName = data.civitaiName || '';
    form.civitaiUrl = data.civitaiUrl || data.civitai_url || '';
    form.nsfw = String(data.nsfw).toLowerCase() === 'true';
    form.preferredWeight = data.preferredWeight !== undefined ? data.preferredWeight : 1.0;
    form.isSlider = data.isSlider === true || data.slider === true;
    form.sliderMin = data.sliderMin !== undefined && data.sliderMin !== null ? Number(data.sliderMin) : -3.0;
    form.sliderMax = data.sliderMax !== undefined && data.sliderMax !== null ? Number(data.sliderMax) : 3.0;
    form.sliderMinDesc = data.sliderMinDesc || '';
    form.sliderMaxDesc = data.sliderMaxDesc || '';
    form.version = data.version || data.modelVersion || data.model_version || '';
    
    let hl = data.highLow || '';
    if (hl.toLowerCase() === 'high') hl = 'High';
    else if (hl.toLowerCase() === 'low') hl = 'Low';
    form.highLow = hl;
    
    form.tested = data.tested === true;
    
    form.category = data.category || '';
    form.subcategory = data.subcategory || '';
    form.tags = Array.isArray(data.tags) ? data.tags.join(', ') : (data.tags || '');
    form.activationText = data.activation_text || data.activationText || '';
    form.negativeTriggerWords = data.negative_trigger_words || data.negativeTriggerWords || '';
    form.allTriggerWords = data.all_trigger_words || data.allTriggerWords || '';
    form.examplePrompt = data.example_prompt || data.examplePrompt || '';
    form.examplePrompt2 = data.example_prompt_2 || data.examplePrompt2 || '';
    form.notes = data.notes || '';
    form.originalFilename = data.original_filename || 
                            data.originalFilename || 
                            data.json?.web_civitai_data?.original_filename || 
                            data.json?.original_filename || 
                            data.json?.['original filename'] || 
                            data.civitaiInfo?.original_filename || 
                            '';
    
    // Convert HTML desc to plain text for textarea if needed, but for now just bind
    form.description = data.description || '';
    
    // Process images
    images.value = [];
    if (data.previewUrl) images.value.push(data.previewUrl);
    if (data.previewImages && Array.isArray(data.previewImages)) {
      data.previewImages.forEach(img => {
        if (!images.value.includes(img)) images.value.push(img);
      });
    }
    currentImageIndex.value = 0;
    resetRawJson();
  } catch (err) {
    console.error("Failed to load model details:", err);
    toast.showToast('Failed to load model details', 'error');
  } finally {
    loading.value = false;
  }
};

const handleKeydown = (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

  if (showImageCarousel.value) {
    if (e.key === 'Escape') {
      e.stopPropagation();
      closeImageCarousel();
      return;
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevCarouselImage();
      return;
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      nextCarouselImage();
      return;
    }
  }

  if (e.key === 'ArrowLeft') {
    navigatePrevious();
  } else if (e.key === 'ArrowRight') {
    navigateNext();
  }
};

onMounted(() => {
  loadModel();
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});

watch(() => props.modelId, (newId, oldId) => {
  if (newId !== oldId) {
    loadModel();
  }
});

const toggleSliderMode = () => {
  form.isSlider = !form.isSlider;
  debouncedSave();
};

const stepSliderMin = (delta) => {
  const current = Number(form.sliderMin !== undefined && form.sliderMin !== null ? form.sliderMin : -3.0);
  form.sliderMin = Math.round((current + delta) * 10) / 10;
  debouncedSave();
};

const stepSliderMax = (delta) => {
  const current = Number(form.sliderMax !== undefined && form.sliderMax !== null ? form.sliderMax : 3.0);
  form.sliderMax = Math.round((current + delta) * 10) / 10;
  debouncedSave();
};

// Proportional Slider Track Computations
const sliderMinVal = computed(() => {
  if (form.isSlider) {
    return Number(form.sliderMin ?? -3);
  }
  return -3.0;
});

const sliderMaxVal = computed(() => {
  if (form.isSlider) {
    return Number(form.sliderMax ?? 3);
  }
  return 3.0;
});
const sliderCurrentVal = computed(() => Number(form.preferredWeight ?? 1.0));

const sliderThumbPct = computed(() => {
  const min = sliderMinVal.value;
  const max = sliderMaxVal.value;
  if (max <= min) return 50;
  const val = Math.min(Math.max(sliderCurrentVal.value, min), max);
  return ((val - min) / (max - min)) * 100;
});

const sliderZeroPct = computed(() => {
  const min = sliderMinVal.value;
  const max = sliderMaxVal.value;
  if (max <= min) return 50;
  if (0 < min) return 0;
  if (0 > max) return 100;
  return ((0 - min) / (max - min)) * 100;
});

// Auto-save logic
let saveTimeout = null;
const debouncedSave = () => {
  if (saveTimeout) clearTimeout(saveTimeout);
  saveTimeout = setTimeout(async () => {
    try {
      const payload = { ...model.value, ...form };
      payload.tags = form.tags;
      payload.original_filename = form.originalFilename;
      payload.originalFilename = form.originalFilename;
      if (payload.json && typeof payload.json === 'object') {
        payload.json.tags = form.tags;
        if (!payload.json.web_civitai_data) payload.json.web_civitai_data = {};
        payload.json.web_civitai_data.original_filename = form.originalFilename;
      }
      payload.nsfw = form.nsfw;
      payload.activation_text = form.activationText;
      payload.example_prompt = form.examplePrompt;
      payload.example_prompt_2 = form.examplePrompt2;
      payload.negative_trigger_words = form.negativeTriggerWords;
      payload.all_trigger_words = form.allTriggerWords;
      payload.civitaiUrl = form.civitaiUrl;
      payload.isSlider = form.isSlider;
      payload.sliderMin = form.sliderMin;
      payload.sliderMax = form.sliderMax;
      payload.sliderMinDesc = form.sliderMinDesc;
      payload.sliderMaxDesc = form.sliderMaxDesc;
      payload.sliderRange = [form.sliderMin, form.sliderMax];
      
      await api.saveModel(props.modelId, payload);
      toast.showToast('Changes saved', 'success');
      if (model.value) {
        model.value.tags = form.tags;
        model.value.original_filename = form.originalFilename;
        model.value.originalFilename = form.originalFilename;
        if (model.value.json && typeof model.value.json === 'object') {
          model.value.json.tags = form.tags;
          if (!model.value.json.web_civitai_data) model.value.json.web_civitai_data = {};
          model.value.json.web_civitai_data.original_filename = form.originalFilename;
        }
      }
      modelsStore.reloadSingleModel(props.modelId);
      
    } catch (err) {
      toast.showToast('Failed to save changes', 'error');
    }
  }, 1000);
};

watch(() => form.nsfw, debouncedSave);
watch(() => form.preferredWeight, debouncedSave);
watch(() => form.isSlider, debouncedSave);

const editingField = ref(null);

const startEditingField = async (field) => {
  editingField.value = field;
  await nextTick();
  const el = document.getElementById(`inline-edit-${field}`);
  if (el) el.focus();
};

const stopEditingField = () => {
  if (editingField.value) {
    debouncedSave();
    editingField.value = null;
  }
};

const baseModelCount = computed(() => {
  const target = (form.baseModel || '').trim().toLowerCase();
  if (!target) return 0;
  return modelsStore.models.filter(m => (m.baseModel || m.base_model || '').trim().toLowerCase() === target).length;
});

const creatorCount = computed(() => {
  const target = (form.creator || '').trim().toLowerCase();
  if (!target) return 0;
  return modelsStore.models.filter(m => (m.creator || '').trim().toLowerCase() === target).length;
});

const searchAndClose = (text) => {
  if (!text) return;
  modelsStore.searchQuery = text.trim();
  emit('close');
};

const uniqueBaseModels = computed(() => {
  const set = new Set();
  modelsStore.models.forEach(m => { if (m.baseModel) set.add(m.baseModel) });
  return Array.from(set).sort();
});

const uniqueSdVersions = computed(() => {
  const set = new Set();
  modelsStore.models.forEach(m => { if (m.sdVersion) set.add(m.sdVersion) });
  return Array.from(set).sort();
});

const uniqueCategories = computed(() => {
  const set = new Set();
  modelsStore.models.forEach(m => { if (m.category) set.add(m.category) });
  return Array.from(set).sort();
});

const uniqueSubcategories = computed(() => {
  const set = new Set();
  modelsStore.models.forEach(m => { if (m.subcategory) set.add(m.subcategory) });
  return Array.from(set).sort();
});

const promptEditField = async (field, label) => {
  const newVal = prompt(`Edit ${label}:`, form[field]);
  if (newVal !== null) {
    form[field] = newVal;
    debouncedSave();
  }
};

const copyToClipboard = (text) => {
  if (text) {
    navigator.clipboard.writeText(text);
    toast.showToast('Copied to clipboard', 'success');
  }
};

// Upload Logic
const toggleHighLow = () => {
  const current = form.highLow;
  if (!current) {
    form.highLow = 'High';
  } else if (current === 'High' || current === 'high') {
    form.highLow = 'Low';
  } else if (current === 'Low' || current === 'low') {
    form.highLow = '';
  } else {
    form.highLow = 'High';
  }
  debouncedSave();
};

// Text Field Helpers
const setNameFromCivitai = () => {
  if (form.civitaiName) {
    form.name = form.civitaiName;
    debouncedSave();
  }
};

const fixUnmatchedPairs = (text, openChar, closeChar) => {
  if (!text) return '';
  const chars = text.split('');
  const openStack = [];
  const toRemove = new Set();
  for (let i = 0; i < chars.length; i++) {
    if (chars[i] === openChar) {
      openStack.push(i);
    } else if (chars[i] === closeChar) {
      if (openStack.length > 0) {
        openStack.pop();
      } else {
        toRemove.add(i);
      }
    }
  }
  for (const idx of openStack) {
    toRemove.add(idx);
  }
  return chars.filter((_, idx) => !toRemove.has(idx)).join('');
};

const cleanText = (text) => {
  if (!text) return '';
  let n = text;
  n = n.replace(/\//g, ' - ');
  n = n.replace(/[\\:*?"<>|]/g, '');
  n = n.replace(/_/g, ' ');
  n = n.replace(/[—–―‒−]/g, '-');
  n = n.replace(/-/g, ' - ');
  n = n.replace(/\s+/g, ' ');
  n = n.replace(/-+/g, '-');
  n = n.trim();
  n = n.replace(/\b([A-Z]{2,})\b/g, (match) => {
      return match.charAt(0).toUpperCase() + match.slice(1).toLowerCase();
  });
  n = n.replace(/\b[a-z]/g, char => char.toUpperCase());
  // Fix apostrophe capitalization (e.g. Cat'S -> Cat's, Don'T -> Don't, Cat’S -> Cat’s)
  n = n.replace(/(['’])([A-Za-z]+)\b/g, (match, apos, letters) => apos + letters.toLowerCase());
  // Remove unmatched/open-ended brackets
  n = fixUnmatchedPairs(n, '(', ')');
  n = fixUnmatchedPairs(n, '[', ']');
  n = fixUnmatchedPairs(n, '{', '}');
  n = n.replace(/\s*-\s*-\s*/g, ' - '); 
  n = n.replace(/^\s*-\s*/, ''); 
  n = n.replace(/\s*-\s*$/, ''); 
  return n.replace(/\s+/g, ' ').trim();
};

const cleanName = () => {
  if (!form.name) return;
  form.name = cleanText(form.name);
  debouncedSave();
};

const addSliderToName = () => {
  const minVal = form.isSlider ? (form.sliderMin ?? -3) : -3;
  const maxVal = form.isSlider ? (form.sliderMax ?? 3) : 3;
  const minDesc = (form.sliderMinDesc || '').trim();
  const maxDesc = (form.sliderMaxDesc || '').trim();

  let sliderTag = '';
  if (minDesc || maxDesc) {
    sliderTag = `[${minVal} ${minDesc} ↔ ${maxDesc} ${maxVal}]`.replace(/\s+/g, ' ');
  } else {
    sliderTag = `[${minVal} ↔ ${maxVal}]`;
  }

  let currentName = form.name || '';
  const sliderRegex = /\[[^\]]*↔[^\]]*\]/;
  if (sliderRegex.test(currentName)) {
    form.name = currentName.replace(sliderRegex, sliderTag).trim();
  } else {
    form.name = currentName ? `${currentName} ${sliderTag}` : sliderTag;
  }
  debouncedSave();
  toast.showToast('Slider tag added to Model Name', 'success');
};

const trimName = () => {
  if (!form.name) return;
  let modelName = form.name;

  const baseModelPrefixes = settingsStore.trimNames && settingsStore.trimNames.length > 0
    ? settingsStore.trimNames
    : [
      'Pony', 'PXL', '[P]', '[Pony]', '[PXL]',
      'SDXL', 'SDXL 1.0', 'SDXL1.0', '[X]', '[SDXL]',
      'SD', 'SD 1.5', 'SD1.5', 'SD 1.4', 'SD1.4', 'SD1', '[SD]',
      'SD 2.0', 'SD2.0', 'SD 2.1', 'SD2.1', 'SD2',
      'Illustrious', 'Ill', '[I]', '[Ill]', '[Illustrious]',
      'Noob', 'NoobAI', 'Noob AI', '[Noob]', '[N]',
      'ZImageTurbo', 'Zit', '[Z]', '[Zit]', 'Z Turbo', 'Z-Image', 'ZImage',
      'Flux', 'Flux.1', 'Flux 1', '[Flux]', '[F]',
      'Wan', 'Wan21', 'Wan 2.1', 'Wan2.1', 'Wan22', 'Wan 2.2', 'Wan2.2',
      'Wan Video', 'Wan Video 14B', 'WanVideo', '[Wan]', '[W]',
      'T2V', 'I2V', '14B', '[WAN 2.2 I2V]',
      'Hunyuan', 'HunyuanVideo', 'Hunyuan Video', '[Hunyuan]', '[H]',
      'CogVideo', 'Cog', 'CogVideoX', '[Cog]', '[CogVideo]',
      'Mochi', '[Mochi]', '[M]',
      'LTX', 'LTX Video', 'LTXVideo', '[LTX]', '[L]',
      'Krea', 'Krea 2', 'Krea2', '[Krea]',
      'Anima', 'Anima Pencil', '[Anima]',
      'Ernie', 'Ernie Bot', '[Ernie]',
      'Kling', 'Luma', 'Sora', 'Minimax', 'Haiper', 'Midjourney', 'DALL-E', 'DALLE', 'Klein', 'Klein9b',
      'LoRA',
      'Checkpoint', 'ckpt',
      'Embedding', 'TI', 'Textual Inversion',
      'High', 'Low', '720p', '1080p', '4K',
      'XL', 'Turbo', 'Lightning', 'LCM', 'Hyper', 'for'
  ];

  const sep = `(?:\\s*[-_,|:]+\\s*|\\s+)`;

  const escapeRegExp = (string) => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Sort by length descending so longer terms like "Krea 2" are matched before shorter terms like "Krea"
  const sortedPrefixes = [...baseModelPrefixes].sort((a, b) => b.length - a.length);

  sortedPrefixes.forEach(prefix => {
      const escapedPrefix = escapeRegExp(prefix);
      const prefixToken = `(?:\\[\\s*${escapedPrefix}\\s*\\]|\\(\\s*${escapedPrefix}\\s*\\)|${escapedPrefix})`;

      const startPattern = new RegExp(`^${sep}*${prefixToken}${sep}*`, 'i');
      modelName = modelName.replace(startPattern, '');

      const endPattern = new RegExp(`${sep}*${prefixToken}${sep}*$`, 'i');
      modelName = modelName.replace(endPattern, '');

      const middlePattern = new RegExp(`(${sep})${prefixToken}(${sep})`, 'gi');
      modelName = modelName.replace(middlePattern, '$1$2');
  });

  // Cleanup orphaned brackets and pipes from list extraction
  modelName = modelName.replace(/\[\s*\|\s*/g, '[');
  modelName = modelName.replace(/\s*\|\s*\]/g, ']');
  modelName = modelName.replace(/\[\s*\]/g, '');
  modelName = modelName.replace(/\(\s*\|\s*\)/g, '');
  modelName = modelName.replace(/\(\s*\)/g, '');
  modelName = modelName.replace(/\s*\|\s*\|\s*/g, ' | ');

  modelName = modelName.replace(/\s*[-_]?\s*v(?:ersion)?\s*[\d.]+\s*$/i, '');
  modelName = modelName.replace(/\s*[-_]\s*v(?:ersion)?\s*[\d.]+\s*[-_]\s*/gi, ' - ');

  const commonSuffixes = ['LoRA', 'Lora', 'lora', 'Checkpoint', 'checkpoint', 'ckpt'];
  commonSuffixes.forEach(suffix => {
      const suffixPattern = new RegExp(`\\s*[-_]?\\s*${suffix}\\s*$`, 'i');
      modelName = modelName.replace(suffixPattern, '');
  });

  modelName = modelName.replace(/^\[[A-Z]\]\s*/i, '');
  modelName = modelName.replace(/\s+/g, ' ');
  modelName = modelName.replace(/\s*,\s*,\s*/g, ', ');
  modelName = modelName.replace(/\s*-\s*-\s*/g, ' - ');
  modelName = modelName.replace(/^\s*[-_,]\s*/, '');
  modelName = modelName.replace(/\s*[-_,]\s*$/, '');
  
  // Remove any unmatched/open-ended brackets
  modelName = fixUnmatchedPairs(modelName, '(', ')');
  modelName = fixUnmatchedPairs(modelName, '[', ']');
  modelName = fixUnmatchedPairs(modelName, '{', '}');
  modelName = modelName.replace(/\s+/g, ' ').trim();

  form.name = modelName;
  debouncedSave();
};

const formatVersionNumber = (versionStr) => {
  const num = parseFloat(versionStr);
  if (num === Math.floor(num)) return String(Math.floor(num));
  return String(num);
};

const guessVersion = (silent = false) => {
  if (!model.value) return;

  const modelName = form.name || model.value.name || '';
  const filename = model.value.filename || '';
  const civitaiName = form.civitaiName || model.value.civitaiName || '';
  const originalFile = form.originalFilename || originalFilename.value || '';
  const searchTexts = [modelName, filename, civitaiName, originalFile];
  let bestVersion = null;

  // Pass 1: Explicit version pattern (e.g. Scar_v1, Scar-v2, Scar v1.5, Scar.v1, ScarV2, ver 1, version 2)
  // Accommodates non-letter delimiters like _, -, ., space, brackets, and camelCase
  const vPattern = /(?:^|[^a-zA-Z]|(?<=[a-z])(?=[A-Z]))(?:v|ver(?:sion)?)[_\s-]*(\d+(?:\.\d+)?)(?=$|[^a-zA-Z0-9]|\.[a-zA-Z]+$)/gi;

  for (const text of searchTexts) {
    if (!text) continue;
    const matches = [...text.matchAll(vPattern)];
    if (matches && matches.length > 0) {
      const lastMatch = matches[matches.length - 1];
      if (lastMatch && lastMatch[1]) {
        bestVersion = formatVersionNumber(lastMatch[1]);
        break;
      }
    }
  }

  // Pass 2: Fallback numeric search after stripping known base models, resolutions, parameter counts
  if (!bestVersion) {
    const baseModelPrefixes = settingsStore.trimNames && settingsStore.trimNames.length > 0
      ? settingsStore.trimNames
      : [
        'Pony', 'PXL', '[P]', '[Pony]', '[PXL]',
        'SDXL', 'SDXL 1.0', 'SDXL1.0', '[X]', '[SDXL]',
        'SD', 'SD 1.5', 'SD1.5', 'SD 1.4', 'SD1.4', 'SD1', '[SD]',
        'SD 2.0', 'SD2.0', 'SD 2.1', 'SD2.1', 'SD2',
        'Illustrious', 'Ill', '[I]', '[Ill]', '[Illustrious]',
        'Noob', 'NoobAI', 'Noob AI', '[Noob]', '[N]',
        'ZImageTurbo', 'Zit', '[Z]', '[Zit]', 'Z Turbo', 'Z-Image', 'ZImage',
        'Flux', 'Flux.1', 'Flux 1', '[Flux]', '[F]',
        'Wan', 'Wan21', 'Wan 2.1', 'Wan2.1', 'Wan22', 'Wan 2.2', 'Wan2.2',
        'Wan Video', 'Wan Video 14B', 'WanVideo', '[Wan]', '[W]',
        'T2V', 'I2V', '14B', '[WAN 2.2 I2V]',
        'Hunyuan', 'HunyuanVideo', 'Hunyuan Video', '[Hunyuan]', '[H]',
        'CogVideo', 'Cog', 'CogVideoX', '[Cog]', '[CogVideo]',
        'Mochi', '[Mochi]', '[M]',
        'LTX', 'LTX Video', 'LTXVideo', '[LTX]', '[L]',
        'Krea', 'Krea 2', 'Krea2', '[Krea]',
        'Anima', 'Anima Pencil', '[Anima]',
        'Ernie', 'Ernie Bot', '[Ernie]',
        'Kling', 'Luma', 'Sora', 'Minimax', 'Haiper', 'Midjourney', 'DALL-E', 'DALLE', 'Klein', 'Klein9b',
        'LoRA', 'Checkpoint', 'ckpt', 'Embedding', 'TI',
        '720p', '1080p', '4K', 'XL', 'Turbo', 'Lightning', 'LCM', 'Hyper'
      ];
    const sortedPrefixes = [...baseModelPrefixes].sort((a, b) => b.length - a.length);

    for (const text of searchTexts) {
      if (!text) continue;
      let sanitized = text;

      // Strip file extensions first like .safetensors, .pt
      sanitized = sanitized.replace(/\.(?:safetensors|pt|ckpt|bin)$/i, '');

      // Strip base models so terms like "Krea 2", "SD 1.5", "Wan 2.1" don't get misidentified as versions
      for (const prefix of sortedPrefixes) {
        const escaped = prefix.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        sanitized = sanitized.replace(new RegExp(`(?:^|[^a-zA-Z0-9])${escaped}(?=[^a-zA-Z0-9]|$)`, 'gi'), ' ');
      }
      sanitized = sanitized.replace(/\b\d+\s*[bB]\b/g, ' ');
      sanitized = sanitized.replace(/\b(512|768|1024|720|1080)\b/g, ' ');
      sanitized = sanitized.replace(/\b\d+k\b/gi, ' ');
      sanitized = sanitized.replace(/\b(?:step|ep|epoch)\s*\d+\b/gi, ' ');
      sanitized = sanitized.replace(/[_]/g, ' ');

      const matches = sanitized.match(/\b(\d+(?:\.\d+)?)\b/g);
      if (matches && matches.length > 0) {
        for (let i = matches.length - 1; i >= 0; i--) {
          const num = parseFloat(matches[i]);
          if (num > 0 && num < 100) {
            bestVersion = formatVersionNumber(matches[i]);
            break;
          }
        }
        if (bestVersion) break;
      }
    }
  }

  if (bestVersion) {
    form.version = bestVersion;
    debouncedSave();
    if (!silent) toast.showToast(`Guessed version: ${bestVersion}`, 'success');
  } else {
    if (!silent) toast.showToast('Could not detect version', 'warning');
  }
};

const clearVersion = () => {
  form.version = '';
  debouncedSave();
  toast.showToast('Version cleared', 'info');
};

const autoFormatIdentity = () => {
  const oldVersion = form.version;
  cleanName();
  trimName();
  cleanName();
  guessVersion(true);

  if (form.version && form.version !== oldVersion) {
    toast.showToast(`Cleaned & trimmed name, set v${form.version}`, 'success');
  } else {
    toast.showToast('Cleaned and trimmed model name', 'success');
  }
};

const cleanVersion = () => {
  if (!form.version) return;
  let v = cleanText(form.version);
  // if it's just numbers, prepend v
  if (!v.toLowerCase().startsWith('v') && /^\d+(\.\d+)?$/.test(v)) {
    v = 'V' + v;
  }
  form.version = v;
  debouncedSave();
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileUpload = async (e) => {
  if (e.target.files && e.target.files[0]) {
    await doUpload(e.target.files[0]);
  }
};

const handleDrop = async (e) => {
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    await doUpload(e.dataTransfer.files[0]);
  }
};

const doUpload = async (file) => {
  toast.showToast('Uploading image...', 'info', 0);
  try {
    await api.uploadPreview(props.modelId, modelsStore.currentLocation, file);
    toast.removeToast(0);
    toast.showToast('Preview uploaded successfully', 'success');
    await loadModel(); 
  } catch (err) {
    toast.removeToast(0);
    toast.showToast('Upload failed', 'error');
  }
};

const deleteCurrentImage = async () => {
  if (images.value.length === 0) return;
  if (!confirm('Are you sure you want to delete this preview image?')) return;
  try {
    await api.deleteThumbnail(props.modelId, modelsStore.currentLocation, currentImageIndex.value + 1);
    toast.showToast('Image deleted', 'success');
    await loadModel();
  } catch (err) {
    toast.showToast('Failed to delete image', 'error');
  }
};

const setAsDefault = async () => {
  if (currentImageIndex.value === 0) return;
  
  const totalImages = images.value.length;
  const newOrder = [currentImageIndex.value + 1];
  
  for (let i = 1; i <= totalImages; i++) {
    if (i !== currentImageIndex.value + 1) {
      newOrder.push(i);
    }
  }

  try {
    await api.reorderThumbnails(props.modelId, modelsStore.currentLocation, newOrder);
    toast.showToast('Set as default thumbnail', 'success');
    await loadModel();
  } catch(err) {
    toast.showToast('Failed to set default', 'error');
  }
};

// File Management
const promptRename = () => {
  newFilenameTemp.value = filenameNoExt.value;
  editingFilename.value = true;
};

const cancelRename = () => {
  editingFilename.value = false;
};

const saveRename = async () => {
  if (newFilenameTemp.value && newFilenameTemp.value !== filenameNoExt.value) {
    isRenaming.value = true;
    try {
      const response = await api.renameModel(props.modelId, newFilenameTemp.value);
      
      if (response && response.status === 'error') {
        toast.showToast(response.message || 'Failed to rename', 'error');
        return;
      }
      
      toast.showToast('Renamed successfully', 'success');
      modelsStore.fetchModels();
      
      const parts = props.modelId.split('/');
      parts[parts.length - 1] = newFilenameTemp.value;
      const newModelId = parts.join('/');
      
      emit('change-model', newModelId);
      editingFilename.value = false;
    } catch (err) {
      toast.showToast(err?.response?.data?.message || 'Failed to rename', 'error');
    } finally {
      isRenaming.value = false;
    }
  } else {
    editingFilename.value = false;
  }
};

const generateRecommendedFilename = () => {
  const baseModel = form.baseModel || '';
  const formats = settingsStore.filenameFormats || [];
  
  let matchingFormat = formats.find(f => f.baseModel && f.baseModel.toLowerCase() === baseModel.toLowerCase());
  if (!matchingFormat) {
    matchingFormat = formats.find(f => f.baseModel === 'Default');
  }
  
  let formatString = matchingFormat ? matchingFormat.format : '{modelname} {version}';
  
  if (formatString.toLowerCase().includes('{highlow}') && (!form.highLow || form.highLow.toLowerCase() === 'none')) {
    toast.showToast("This format requires a High/Low value to be selected.", 'warning');
    return '';
  }
  
  let result = formatString;
  result = result.replace(/\{modelname\}/gi, form.name || form.civitaiName || '');
  result = result.replace(/\{civitainame\}/gi, form.civitaiName || form.name || '');
  result = result.replace(/\{version\}/gi, form.version || '');
  result = result.replace(/\{versionname\}/gi, form.version || '');
  result = result.replace(/\{highlow\}/gi, form.highLow || '');
  result = result.replace(/\{category\}/gi, form.category || '');
  result = result.replace(/\{subcategory\}/gi, form.subcategory || '');
  
  result = result.replace(/\s+/g, ' ').trim();
  if (settingsStore.filenameSnakeCase) {
    result = result.replace(/\s+/g, '_');
  }
  return result;
};

const applyRecommendedFilename = () => {
  const recommended = generateRecommendedFilename();
  if (recommended) {
    newFilenameTemp.value = recommended;
  }
};

const triggerRecommendedRename = () => {
  const recommended = generateRecommendedFilename();
  if (recommended) {
    newFilenameTemp.value = recommended;
    editingFilename.value = true;
  }
};

const triggerAutoRecommendedRename = () => {
  cleanName();
  trimName();
  cleanName();
  guessVersion(true);
  const recommended = generateRecommendedFilename();
  if (recommended) {
    newFilenameTemp.value = recommended;
    editingFilename.value = true;
    toast.showToast('Auto formatted identity & applied recommended filename', 'success');
  } else {
    editingFilename.value = true;
  }
};

const cleanFilename = () => {
  if (!newFilenameTemp.value) return;
  let n = newFilenameTemp.value;
  n = n.replace(/\//g, ' - ');
  n = n.replace(/[\\:*?"<>|]/g, '');
  n = n.replace(/_/g, ' ');
  n = n.replace(/[—–―‒−]/g, '-');
  n = n.replace(/-/g, ' - ');
  n = n.replace(/\s+/g, ' ');
  n = n.replace(/-+/g, '-');
  n = n.trim();
  n = n.replace(/\b([A-Z]{2,})\b/g, (match) => match.charAt(0).toUpperCase() + match.slice(1).toLowerCase());
  n = n.replace(/\b[a-z]/g, char => char.toUpperCase());
  // Fix apostrophe capitalization (e.g. Cat'S -> Cat's, Don'T -> Don't, Cat’S -> Cat’s)
  n = n.replace(/(['’])([A-Za-z]+)\b/g, (match, apos, letters) => apos + letters.toLowerCase());
  // Remove unmatched/open-ended brackets
  n = fixUnmatchedPairs(n, '(', ')');
  n = fixUnmatchedPairs(n, '[', ']');
  n = fixUnmatchedPairs(n, '{', '}');
  n = n.replace(/\s*-\s*-\s*/g, ' - '); 
  n = n.replace(/^\s*-\s*/, ''); 
  n = n.replace(/\s*-\s*$/, ''); 
  n = n.replace(/\s+/g, ' ').trim();
  if (settingsStore.filenameSnakeCase) {
    n = n.replace(/\s+/g, '_');
  }
  newFilenameTemp.value = n;
};

const applyModelName = () => {
  if (form.name) {
    newFilenameTemp.value = form.name;
  }
};

const appendCreatorSuffix = () => {
  if (form.creator && !newFilenameTemp.value.includes(form.creator)) {
    newFilenameTemp.value = `${newFilenameTemp.value} - ${form.creator}`;
  }
};



const startMove = () => {
  movingFile.value = true;
  
  // Set default to current folder, or root if current folder isn't in available list (case-insensitive check)
  const currentFolderNorm = (model.value?.folder || '').toLowerCase().replace(/\\/g, '/');
  const matchedFolder = availableMoveFolders.value.find(f => (f || '').toLowerCase().replace(/\\/g, '/') === currentFolderNorm);
  
  if (matchedFolder !== undefined) {
    targetMoveFolder.value = matchedFolder;
  } else if (availableMoveFolders.value.length > 0) {
    targetMoveFolder.value = availableMoveFolders.value[0];
  } else {
    targetMoveFolder.value = '';
  }
};

const executeMove = async () => {
  if (targetMoveFolder.value !== null) {
    isMoving.value = true;
    try {
      await api.moveModel(props.modelId, targetMoveFolder.value);
      toast.showToast('Moved successfully', 'success');
      modelsStore.fetchModels();
      
      const parts = props.modelId.split('/');
      const basename = parts[parts.length - 1];
      const newModelId = targetMoveFolder.value ? `${targetMoveFolder.value}/${basename}` : basename;
      
      emit('change-model', newModelId);
      movingFile.value = false;
    } catch (err) {
      toast.showToast('Failed to move', 'error');
    } finally {
      isMoving.value = false;
    }
  }
};

const deleteModel = async () => {
  if (confirm(`Are you sure you want to completely delete ${model.value.name} and all its files?`)) {
    try {
      await modelsStore.deleteModel(props.modelId, model.value.path);
      toast.showToast('Model deleted', 'success');
      emit('close');
    } catch (err) {
      toast.showToast(err.message, 'error');
    }
  }
};

// Civitai Tools
const fetchAllCivitaiData = async () => {
  if (saveTimeout) clearTimeout(saveTimeout);
  toast.showToast('Fetching all Civitai metadata & thumbnails...', 'info');
  try {
    const res = await api.civitaiFetchByHash(model.value.path);
    if (res && res.status === 'not_found') {
      toast.showToast(res.message || 'Model not found on Civitai or CivArchive', 'warning');
      return;
    }
    if (res && res.status === 'error') {
      toast.showToast(res.message || 'Failed to fetch metadata', 'error');
      return;
    }
    const thumbRes = await api.civitaiDownloadPreview(model.value.path, false, false, true);
    if (thumbRes && thumbRes.status === 'success') {
      toast.showToast('All Civitai metadata & thumbnails downloaded!', 'success');
    } else {
      toast.showToast('Metadata saved, preview status: ' + (thumbRes?.message || 'Done'), 'info');
    }
    await loadModel();
    modelsStore.fetchModels();
  } catch (err) {
    toast.showToast('Failed to fetch all data', 'error');
  }
};

const fetchCivitaiByHash = async () => {
  if (saveTimeout) clearTimeout(saveTimeout);
  toast.showToast('Fetching metadata via hash...', 'info');
  try {
    await api.civitaiFetchByHash(model.value.path);
    toast.showToast('Metadata updated!', 'success');
    await loadModel();
    modelsStore.fetchModels();
  } catch (err) {
    toast.showToast('Failed to fetch from Civitai', 'error');
  }
};

const fetchCivArchiveByHash = async () => {
  if (saveTimeout) clearTimeout(saveTimeout);
  toast.showToast('Checking CivArchive via hash...', 'info');
  try {
    const res = await api.civArchiveFetchByHash(model.value.path);
    if (res && res.status === 'not_found') {
      toast.showToast(res.message || 'Model not found on CivArchive', 'warning');
      return;
    }
    if (res && res.status === 'error') {
      toast.showToast(res.message || 'Failed to fetch from CivArchive', 'error');
      return;
    }
    toast.showToast('Metadata updated from CivArchive!', 'success');
    
    // Automatically trigger thumbnail download for convenience
    await downloadThumbnails();
    
    await loadModel();
    modelsStore.fetchModels();
  } catch (err) {
    toast.showToast('Failed to fetch from CivArchive', 'error');
  }
};

const promptCivitaiUrl = async () => {
  const url = prompt('Enter Civitai URL:');
  if (url) {
    if (saveTimeout) clearTimeout(saveTimeout);
    toast.showToast('Fetching metadata via URL...', 'info');
    try {
      await api.civitaiFetchByUrl(model.value.path, url);
      toast.showToast('Metadata updated!', 'success');
      await loadModel();
      modelsStore.fetchModels();
    } catch (err) {
      toast.showToast('Failed to fetch from Civitai', 'error');
    }
  }
};

const generateHash = async () => {
  toast.showToast('Generating hash...', 'info');
  try {
    await api.generateHash(props.modelId, model.value.path);
    toast.showToast('Hash generated!', 'success');
    await loadModel();
  } catch (err) {
    toast.showToast('Failed to generate hash', 'error');
  }
};

const fixThumbnail = async () => {
  try {
    await api.civitaiFixThumbnail(model.value.path);
    toast.showToast('Thumbnail fixed!', 'success');
    await loadModel();
  } catch (err) {
    toast.showToast('Failed to fix thumbnail', 'error');
  }
};

const downloadThumbnails = async () => {
  toast.showToast('Downloading thumbnails...', 'info');
  try {
    const res = await api.civitaiDownloadPreview(model.value.path, false, false, true);
    if (res && res.status === 'success') {
      toast.showToast('Thumbnails downloaded!', 'success');
    } else {
      toast.showToast(res?.message || 'No thumbnails found or already exists', 'info');
    }
    await loadModel();
    modelsStore.fetchModels();
  } catch (err) {
    toast.showToast('Failed to download thumbnails', 'error');
  }
};

const isCheckingOnline = ref(false);

const onlineStatusInfo = computed(() => {
  if (!model.value) return { badge: false, text: 'Not Checked', cls: '', icon: '' };
  const ci = model.value.civitaiAvailable !== undefined ? model.value.civitaiAvailable : model.value.civitai_available;
  const ca = model.value.civarchiveAvailable !== undefined ? model.value.civarchiveAvailable : model.value.civarchive_available;

  if (ci === true || String(ci).toLowerCase() === 'true') {
    return { badge: true, text: 'Civitai Online', cls: 'status-civitai', icon: 'fa-check-circle' };
  }
  const ciFalse = ci === false || String(ci).toLowerCase() === 'false';
  const caTrue = ca === true || String(ca).toLowerCase() === 'true';
  const caFalse = ca === false || String(ca).toLowerCase() === 'false';

  if (caTrue) {
    return { badge: true, text: 'CivArchive Only', cls: 'status-civarchive', icon: 'fa-archive' };
  }
  if (ciFalse && caFalse) {
    return { badge: true, text: 'Not Available Online', cls: 'status-offline', icon: 'fa-unlink' };
  }
  return { badge: false, text: 'Not Checked', cls: '', icon: '' };
});

const checkOnlineAvailability = async () => {
  if (!model.value || isCheckingOnline.value) return;
  if (saveTimeout) clearTimeout(saveTimeout);
  isCheckingOnline.value = true;
  toast.showToast('Checking online availability...', 'info');
  try {
    const res = await api.civitaiCheckAvailability(model.value.path, true);
    if (res && res.status === 'error') {
      toast.showToast(res.message || 'Failed to check availability', 'error');
    } else if (res) {
      if (res.civitai_available === true) {
        toast.showToast('Available on Civitai!', 'success');
      } else if (res.civarchive_available === true) {
        toast.showToast('Removed from Civitai, available on CivArchive!', 'info');
      } else {
        toast.showToast('Not available on Civitai or CivArchive', 'warning');
      }
      await loadModel();
      modelsStore.fetchModels();
    }
  } catch (err) {
    if (err?.response?.status === 404) {
      toast.showToast('Please restart the Lora Manager server to enable availability checking', 'error');
    } else {
      const detail = err?.response?.data?.message || err?.message || '';
      toast.showToast(detail ? `Failed to check online availability: ${detail}` : 'Failed to check online availability', 'error');
    }
  } finally {
    isCheckingOnline.value = false;
  }
};

// JSON
const resetRawJson = () => {
  if (model.value) {
    const rawData = model.value.json ? { ...model.value.json } : {};
    rawJsonText.value = JSON.stringify(rawData, null, 2);
  }
};

const isJsonValid = computed(() => {
  if (!rawJsonText.value) return true;
  try {
    JSON.parse(rawJsonText.value);
    return true;
  } catch (e) {
    return false;
  }
});

const jsonStats = computed(() => {
  if (!rawJsonText.value) return { lines: 0, chars: 0 };
  const lines = rawJsonText.value.split('\n').length;
  const chars = rawJsonText.value.length;
  return { lines, chars };
});

const formatRawJson = () => {
  try {
    const parsed = JSON.parse(rawJsonText.value);
    rawJsonText.value = JSON.stringify(parsed, null, 2);
    toast.showToast('JSON formatted', 'info');
  } catch (e) {
    toast.showToast('Cannot format: invalid JSON syntax', 'warning');
  }
};

const copyRawJson = async () => {
  try {
    await navigator.clipboard.writeText(rawJsonText.value);
    toast.showToast('JSON copied to clipboard!', 'success');
  } catch (e) {
    toast.showToast('Failed to copy to clipboard', 'error');
  }
};

const saveRawJson = async () => {
  try {
    const parsed = JSON.parse(rawJsonText.value);
    await api.saveModelJson(props.modelId, parsed);
    toast.showToast('JSON saved successfully', 'success');
    await loadModel();
  } catch (err) {
    toast.showToast('Invalid JSON syntax or save failed', 'error');
  }
};

const totalAssociatedSize = computed(() => {
  return associatedFiles.value.reduce((acc, f) => acc + (f.sizeBytes || 0), 0);
});

const handleAssociatedImageClick = (file) => {
  if (file.type !== 'image' || !file.relativePath) return;
  const idx = images.value.indexOf(file.relativePath);
  if (idx !== -1) {
    openImageCarousel(idx);
  } else {
    window.open(api.getAssetUrl(file.relativePath, modelsStore.getCacheBuster(model.value?.path)), '_blank');
  }
};

const formatBytes = (bytes) => {
  if (bytes === 0 || !bytes) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getDomainName = (url) => {
  if (!url) return '';
  try {
    const domain = new URL(url).hostname;
    return domain.replace(/^www\./, '');
  } catch (e) {
    return 'Link';
  }
};

const formatDate = (timestamp) => {
  if (!timestamp) return '-';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString();
};

watch(activeTab, (newTab) => {
  if (newTab === 'json') {
    resetRawJson();
  } else if (newTab === 'files') {
    fetchAssociatedFiles();
  }
});

const getFileIcon = (filename) => {
  if (!filename) return 'fa-file';
  const ext = filename.split('.').pop().toLowerCase();
  if (['safetensors', 'ckpt', 'pt', 'bin'].includes(ext)) return 'fa-cube';
  if (['json', 'info'].includes(ext)) return 'fa-file-code';
  if (ext === 'txt') return 'fa-file-alt';
  if (['mp4', 'webm', 'gif'].includes(ext)) return 'fa-file-video';
  return 'fa-file';
};
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--text-color, #e0e0e0);
  gap: 15px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.model-modal {
  width: 98%;
  max-width: 1600px;
  height: 95vh;
  background-color: var(--color-card-bg, var(--color-bg-secondary));
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: var(--color-text);
}

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: var(--color-header-bg, var(--color-bg-secondary));
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.2em;
  font-weight: 600;
  color: var(--color-text);
}

.file-bracket { color: var(--color-text-muted); }
.base-model-light { color: var(--color-text-secondary); font-weight: 400; margin-left: 10px; }

.header-actions {
  display: flex;
  gap: 15px;
}
.header-actions .btn-icon { color: var(--color-text-secondary); }
.header-actions .btn-icon:hover { color: var(--color-text); }

.model-details-layout {
  display: flex;
  height: 100%;
  overflow: hidden;
}

/* Left Column */
.left-column {
  width: 320px;
  background-color: var(--color-sidebar-bg, var(--color-bg-secondary));
  padding: 14px;
  overflow-y: auto;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.main-image-container {
  width: 100%;
  aspect-ratio: 3/4;
  background-color: var(--color-bg-image, #0b1120);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.main-image-container:hover {
  border-color: rgba(56, 189, 248, 0.4);
}

.drop-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(11, 17, 32, 0.75);
  backdrop-filter: blur(8px);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.76em;
  font-weight: 500;
  color: var(--color-text);
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.drop-overlay:hover {
  background: var(--color-btn-primary);
  border-color: transparent;
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
.drop-overlay:active {
  transform: translateY(0);
}

.main-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}

.thumbnail-strip {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.thumb, .add-thumb {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s ease;
  opacity: 0.75;
}
.thumb:hover {
  opacity: 1;
  transform: translateY(-1px);
}
.thumb.active {
  border-color: #38bdf8;
  opacity: 1;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.45);
}

.add-thumb {
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  border: 1px dashed rgba(255, 255, 255, 0.2);
}
.add-thumb:hover {
  border-color: #38bdf8;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.08);
  opacity: 1;
  transform: translateY(-1px);
}

.main-image-container .image-hover-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 10;
}
.main-image-container:hover .image-hover-actions {
  opacity: 1;
}
.image-hover-actions .icon-btn {
  padding: 6px 10px;
  background-color: rgba(11, 17, 32, 0.8);
  backdrop-filter: blur(6px);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  transition: all 0.15s ease;
}
.image-hover-actions .btn-danger:hover {
  background-color: rgba(239, 68, 68, 0.9);
  border-color: transparent;
  transform: scale(1.05);
}
.image-hover-actions .btn-primary:hover {
  background-color: rgba(56, 189, 248, 0.9);
  border-color: transparent;
  transform: scale(1.05);
}
.btn-danger { background-color: var(--color-btn-danger); color: white; border-color: var(--color-btn-danger-border, transparent); }
.btn-danger:hover { background-color: var(--color-btn-danger-hover); border-color: var(--color-btn-danger-hover-border, transparent); }
.btn-success { background-color: var(--color-btn-success); color: white; }
.btn-success:hover { background-color: var(--color-btn-success-hover); }

/* Left Column Info Cards */
.info-card {
  gap: 10px;
  padding: 12px 14px;
}

.info-card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-field-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-field-label {
  font-size: 0.76em;
  font-weight: 500;
  color: var(--color-text-secondary, #94a3b8);
  letter-spacing: 0.01em;
}

.info-val { 
  font-size: 0.86em;
  color: var(--color-text); 
  word-break: break-all;
  overflow-wrap: anywhere;
}
.info-val a {
  color: var(--color-text-link);
  text-decoration: none;
}
.info-val a:hover {
  text-decoration: underline;
  color: var(--color-text-link-hover);
}
.download-source-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-link, #38bdf8) !important;
  text-decoration: none !important;
  font-weight: 500;
  transition: all 0.2s ease;
}
.download-source-link:hover {
  color: var(--color-text-link-hover, #7dd3fc) !important;
  text-decoration: none !important;
}
.download-source-link.mature-source {
  color: #f87171 !important;
}
.download-source-link.mature-source:hover {
  color: #fca5a5 !important;
}
.mature-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72em;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 3px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
  letter-spacing: 0.02em;
  line-height: 1;
}
.external-icon {
  font-size: 0.75em;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.download-source-link:hover .external-icon {
  opacity: 1;
}
.info-val span {
  word-break: break-all;
  overflow-wrap: anywhere;
}
.info-val.with-edit { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  gap: 8px; 
  min-height: 24px;
}

.info-path-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 5px 8px;
  border-radius: 5px;
  color: var(--color-text-secondary, #94a3b8);
}

.info-path-text {
  word-break: break-all;
  overflow-wrap: anywhere;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 0.82em;
  line-height: 1.35;
}

.info-path-btn {
  color: #38bdf8;
  cursor: pointer;
  flex-shrink: 0;
  font-size: 0.9em;
  transition: transform 0.15s ease, color 0.15s ease;
}

.info-path-btn:hover {
  color: #ffffff;
  transform: scale(1.15);
}

.info-meta-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-meta-val {
  font-size: 0.84em;
  font-weight: 600;
  color: var(--color-text, #f1f5f9);
}

.info-hash-val {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 0.78em;
  color: var(--color-text-secondary, #94a3b8);
  word-break: break-all;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 5px 8px;
  border-radius: 5px;
  line-height: 1.35;
}

.info-link-group {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.info-link {
  color: var(--color-text-link);
  text-decoration: none;
  cursor: pointer;
  word-break: break-word;
  transition: color 0.15s ease;
}
.info-link:hover {
  text-decoration: underline;
  color: var(--color-text-link-hover);
}
.info-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75em;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 10px;
  background: rgba(56, 189, 248, 0.15);
  color: var(--color-text-link);
  border: 1px solid rgba(56, 189, 248, 0.35);
  cursor: pointer;
  line-height: 1.3;
  user-select: none;
  transition: all 0.15s ease;
}
.info-count-badge:hover {
  background: rgba(56, 189, 248, 0.3);
  color: #ffffff;
  border-color: rgba(56, 189, 248, 0.6);
  transform: scale(1.05);
}
.edit-icon { 
  color: var(--color-text-secondary, #94a3b8); 
  font-size: 0.85em;
  opacity: 0.5;
  cursor: pointer; 
  transition: all 0.15s ease;
  flex-shrink: 0;
}
.edit-icon:hover { 
  opacity: 1;
  color: #38bdf8; 
  transform: scale(1.1);
}
.info-copy-btn {
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
  flex-shrink: 0;
  font-size: 0.85em;
  opacity: 0.5;
  transition: transform 0.15s ease, color 0.15s ease, opacity 0.15s ease;
}
.info-copy-btn:hover {
  opacity: 1;
  color: #38bdf8;
  transform: scale(1.15);
}
.online-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  font-weight: 600;
}
.online-status-pill.status-civitai {
  background: rgba(52, 152, 219, 0.2);
  color: #5dade2;
  border: 1px solid rgba(52, 152, 219, 0.45);
}
.online-status-pill.status-civarchive {
  background: rgba(142, 68, 173, 0.25);
  color: #c39bd3;
  border: 1px solid rgba(142, 68, 173, 0.5);
}
.online-status-pill.status-offline {
  background: rgba(192, 57, 43, 0.25);
  color: #ec7063;
  border: 1px solid rgba(192, 57, 43, 0.5);
}
.info-row.stacked { margin-top: 5px; }

.weight-control { display: flex; align-items: center; gap: 10px; }
.weight-slider { flex: 1; }
.weight-input { width: 50px; background: var(--color-bg-input, #111); border: 1px solid var(--color-border); color: var(--color-text); padding: 2px 5px; }

.inline-edit-input {
  flex: 1;
  background: var(--color-bg-input, #111);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 2px 5px;
  border-radius: 3px;
  width: 100%;
}

.mt-10 { margin-top: 10px; }
.mt-20 { margin-top: 20px; }

/* Right Column */
.right-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tabs-header {
  display: flex;
  background-color: var(--color-header-bg, var(--color-bg-secondary));
  border-bottom: 1px solid var(--color-border);
}
.tabs-header button {
  padding: 15px 25px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--color-text-secondary);
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.tabs-header button:hover { color: var(--color-text); }
.tabs-header button.active {
  color: var(--color-accent-title, var(--color-btn-primary));
  border-bottom-color: var(--color-accent-title, var(--color-btn-primary));
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: var(--color-card-bg, var(--color-bg-secondary));
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.section-title {
  font-weight: bold;
  font-size: 1em;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 5px;
}

.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.85em; color: var(--color-text-secondary); display: flex; align-items: center; gap: 5px; }
.form-control {
  background-color: var(--color-bg-input, #222);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 8px 12px;
  border-radius: 4px;
  font-family: inherit;
  font-size: 0.9em;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.form-control:focus {
  border-color: var(--input-focus-border, var(--color-btn-primary));
  outline: none;
  box-shadow: var(--input-focus-shadow, none);
}
textarea.form-control { 
  height: 56px; 
  min-height: 56px;
  max-height: 500px;
  overflow-y: auto; 
  resize: vertical; 
}

.tag-cloud-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  background-color: var(--color-bg-input, #222);
  border: 1px solid var(--color-border);
  padding: 5px;
  border-radius: 4px;
  height: 60px;
  overflow-y: auto;
  align-items: flex-start;
  cursor: text;
  transition: border-color 0.2s ease;
}
.tag-cloud-container:focus-within {
  border-color: var(--input-focus-border, var(--color-btn-primary));
  box-shadow: var(--input-focus-shadow, none);
}
.tag-pill {
  background: var(--color-btn-primary);
  color: #fff;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 5px;
}
.tag-pill .remove-tag {
  cursor: pointer;
  font-size: 0.9em;
  opacity: 0.8;
}
.tag-pill .remove-tag:hover {
  opacity: 1;
}
.tag-input {
  flex: 1;
  min-width: 120px;
  background: transparent;
  border: none;
  color: var(--color-text);
  outline: none;
  font-family: inherit;
  font-size: 0.9em;
  padding: 2px 5px;
}

.form-grid-identity, .form-grid-category, .form-grid-keywords, .form-grid-description {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.filename-input-group { display: flex; }
.filename-input-group input { flex: 1; border-radius: 4px 0 0 4px; }
.file-ext { background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-left: none; padding: 8px; color: var(--color-text-secondary); border-radius: 0 4px 4px 0; font-size: 0.9em; }

.identity-buttons {
  grid-column: 1 / -1;
  display: flex;
  gap: 10px;
  margin-top: 5px;
}

.field-actions {
  display: flex;
  gap: 5px;
  margin-top: 5px;
  animation: fadeIn 0.2s ease-in-out;
}

.btn-micro {
  font-size: 0.75rem;
  padding: 4px 10px;
  background-color: var(--color-btn-secondary);
  color: var(--color-text);
  border: 1px solid var(--color-btn-secondary-border, transparent);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
  font-weight: 600;
}

.btn-micro:hover {
  background-color: var(--color-btn-secondary-hover);
  border-color: var(--color-btn-secondary-hover-border, transparent);
  box-shadow: var(--color-btn-secondary-hover-shadow, none);
  color: #fff;
}

.btn-micro.btn-danger {
  background-color: var(--color-btn-danger);
  color: white;
  border-color: var(--color-btn-danger-border, transparent);
}
.btn-micro.btn-danger:hover {
  background-color: var(--color-btn-danger-hover);
  border-color: var(--color-btn-danger-hover-border, transparent);
  box-shadow: var(--color-btn-danger-hover-shadow, none);
}

.btn-micro.btn-success {
  background-color: var(--color-btn-success);
  color: white;
  border-color: transparent;
}
.btn-micro.btn-success:hover {
  background-color: var(--color-btn-success-hover);
}

.label-with-actions { display: flex; justify-content: space-between; align-items: center; }
.label-with-actions .actions { display: flex; gap: 10px; color: var(--color-text-muted); }
.label-with-actions .actions i { cursor: pointer; }
.label-with-actions .actions i:hover { color: var(--color-text); }

/* Color Helper Utilities */
.text-success { color: #2ecc71; }
.text-danger { color: #e74c3c; }
.text-warning { color: #f39c12; }
.text-info { color: #3498db; }
.text-purple { color: #9b59b6; }
.text-muted { color: var(--color-text-secondary, #888); }

/* Civitai Tab & Scrape Metadata Layout */
.civitai-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  box-sizing: border-box;
}

/* Hero: All-in-One Card */
.civitai-hero-card {
  background: var(--color-card-bg, #1e293b);
  border: 1px solid var(--color-border);
  border-left: 4px solid #f59e0b;
  border-radius: 12px;
  padding: 18px 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
  box-sizing: border-box;
}

.hero-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hero-icon {
  font-size: 1.5em;
}

.hero-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-title-wrap h3 {
  margin: 0;
  font-size: 1.18em;
  font-weight: 700;
  color: var(--color-text);
}

.all-in-one-tag {
  font-size: 0.72em;
  font-weight: 700;
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.35);
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hero-desc {
  margin: 0;
  font-size: 0.88em;
  line-height: 1.45;
  color: var(--color-text-secondary);
}

.btn-hero-fetch {
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.98em;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
  transition: all 0.2s ease;
  width: 100%;
}

.btn-hero-fetch:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(2, 132, 199, 0.5);
  filter: brightness(1.08);
}

.btn-hero-fetch:active {
  transform: translateY(1px);
}

/* 4-Step Sequenced Action Cards Grid */
.step-cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  width: 100%;
  box-sizing: border-box;
}

@media (max-width: 900px) {
  .step-cards-grid {
    grid-template-columns: 1fr;
  }
}

.step-card {
  background: var(--color-card-bg, #1e293b);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.step-card:hover {
  border-color: var(--card-hover-border, var(--color-border-hover));
}

.step-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
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
  font-size: 0.78em;
  font-weight: 700;
  flex-shrink: 0;
}

.header-icon {
  font-size: 1.15em;
}

.step-card-header h4 {
  margin: 0;
  font-size: 1.02em;
  font-weight: 700;
  color: var(--color-text);
}

.step-desc {
  margin: 0;
  font-size: 0.85em;
  line-height: 1.45;
  color: var(--color-text-secondary);
  background: rgba(0, 0, 0, 0.22);
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 3px solid rgba(52, 152, 219, 0.4);
  flex-grow: 1;
}

.step-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.84em;
  padding: 2px 0;
}

.status-label {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.status-unchecked-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.82em;
  font-weight: 600;
  background: rgba(245, 158, 11, 0.12);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.step-btn-row {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.btn-action {
  flex: 1;
  min-width: 80px;
  padding: 9px 14px;
  border-radius: 7px;
  font-size: 0.88em;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  background: var(--color-btn-action-bg, #262626);
  color: var(--color-text);
  border: 1px solid var(--color-btn-action-border, transparent);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-action:hover:not(:disabled) {
  background: var(--color-btn-action-hover-bg, #383838);
  border-color: var(--color-btn-action-hover-border, transparent);
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: var(--color-btn-action-hover-shadow, 0 3px 8px rgba(0, 0, 0, 0.3));
}

.btn-action:active:not(:disabled) {
  transform: translateY(1px);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-full {
  width: 100%;
}

/* Local File Tools */
.local-tools-card {
  background: var(--color-card-bg, #1e293b);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  box-sizing: border-box;
}

.local-tools-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.local-title-wrap {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.local-title-wrap h4 {
  margin: 0;
  font-size: 1.02em;
  font-weight: 700;
  color: var(--color-text);
}

.local-desc {
  font-size: 0.82em;
  color: var(--color-text-secondary);
}

.local-tools-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: center;
}

@media (max-width: 900px) {
  .local-tools-actions {
    grid-template-columns: 1fr;
  }
}

.btn-danger-action {
  width: 100%;
  padding: 9px 14px;
  border-radius: 7px;
  font-size: 0.88em;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  background: rgba(239, 68, 68, 0.14);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.38);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-danger-action:hover {
  background: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
}

.move-inline-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.move-label {
  font-size: 0.82em;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.move-controls {
  display: flex;
  gap: 6px;
  width: 100%;
}

.move-select {
  flex: 2;
  height: 34px;
  font-size: 0.88em;
}

.btn-move-confirm {
  flex: 1;
  height: 34px;
  padding: 0 10px;
  font-size: 0.85em;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.btn-move-cancel {
  flex: 0 0 34px;
  height: 34px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* ==========================================================================
   Files Tab Formatting
   ========================================================================== */
.files-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  box-sizing: border-box;
}

.files-card {
  background: var(--color-card-bg, #1e293b);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
  box-sizing: border-box;
}

.files-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border);
}

.files-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.files-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25em;
  flex-shrink: 0;
}

.files-title-group h3 {
  margin: 0;
  font-size: 1.15em;
  font-weight: 700;
  color: var(--color-text);
}

.files-subtitle {
  margin: 2px 0 0 0;
  font-size: 0.84em;
  color: var(--color-text-secondary);
}

.files-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.files-summary-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.82em;
  font-weight: 600;
  background: rgba(168, 85, 247, 0.12);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.btn-action-sm {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.84em;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--color-btn-action-bg, #262626);
  color: var(--color-text);
  border: 1px solid var(--color-btn-action-border, transparent);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: all 0.15s ease;
}

.btn-action-sm:hover:not(:disabled) {
  background: var(--color-btn-action-hover-bg, #383838);
  border-color: var(--color-btn-action-hover-border, transparent);
  color: #ffffff;
  transform: translateY(-1px);
}

.btn-action-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.files-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 12px;
  color: var(--color-text-secondary);
  font-size: 0.92em;
}

.files-table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.files-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88em;
}

.files-table thead tr {
  background: rgba(0, 0, 0, 0.25);
  border-bottom: 1px solid var(--color-border);
}

.files-table th {
  padding: 10px 14px;
  font-weight: 700;
  font-size: 0.8em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
}

.th-preview { width: 68px; text-align: center; }
.th-filename { min-width: 220px; }
.th-type { width: 120px; }
.th-size { width: 100px; }
.th-actions { width: 70px; text-align: center; }

.file-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background-color 0.15s ease;
}

.file-row:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.file-row td {
  padding: 8px 14px;
  vertical-align: middle;
}

.file-thumb-wrap {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  background: #000;
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.file-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.thumb-zoom-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  color: #ffffff;
  font-size: 0.85em;
  transition: opacity 0.15s ease;
}

.file-thumb-wrap:hover .thumb-zoom-overlay {
  opacity: 1;
}

.file-thumb-wrap:hover .file-thumb-img {
  transform: scale(1.08);
}

.file-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1em;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.file-icon-box.icon-model {
  background: rgba(168, 85, 247, 0.12);
  border-color: rgba(168, 85, 247, 0.3);
  color: #c084fc;
}

.file-icon-box.icon-metadata {
  background: rgba(56, 189, 248, 0.12);
  border-color: rgba(56, 189, 248, 0.3);
  color: #38bdf8;
}

.file-icon-box.icon-text {
  background: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}

.file-name-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.file-main-name {
  font-weight: 600;
  color: var(--color-text);
  word-break: break-all;
}

.file-type-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.74em;
  font-weight: 700;
  letter-spacing: 0.4px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-text-secondary);
}

.file-type-pill.type-model {
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.35);
}

.file-type-pill.type-metadata {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.35);
}

.file-type-pill.type-image {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.35);
}

.file-type-pill.type-text {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.file-type-pill.type-video {
  background: rgba(236, 72, 153, 0.15);
  color: #f472b6;
  border: 1px solid rgba(236, 72, 153, 0.35);
}

.file-size-text {
  font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
  font-size: 0.88em;
  color: var(--color-text-secondary);
}

.btn-file-delete {
  background: transparent;
  border: 1px solid transparent;
  color: #64748b;
  width: 30px;
  height: 30px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-file-delete:hover {
  color: #ffffff;
  background: #ef4444;
  border-color: #ef4444;
  transform: translateY(-1px);
}

.files-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  gap: 8px;
}

.empty-icon {
  font-size: 2.5em;
  color: #64748b;
  margin-bottom: 6px;
}

.files-empty-state h4 {
  margin: 0;
  font-size: 1.1em;
  font-weight: 700;
  color: var(--color-text);
}

.files-empty-state p {
  margin: 0 0 12px 0;
  font-size: 0.86em;
  color: var(--color-text-secondary);
}

/* ==========================================================================
   Raw JSON Tab Formatting
   ========================================================================== */
.json-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  box-sizing: border-box;
}

.json-card {
  background: var(--color-card-bg, #1e293b);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
  box-sizing: border-box;
}

.json-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border);
}

.json-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.json-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25em;
  flex-shrink: 0;
}

.json-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.json-title-row h3 {
  margin: 0;
  font-size: 1.15em;
  font-weight: 700;
  color: var(--color-text);
}

.json-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.76em;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.json-status-pill.valid {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.35);
}

.json-status-pill.invalid {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.35);
}

.json-subtitle {
  margin: 2px 0 0 0;
  font-size: 0.84em;
  color: var(--color-text-secondary);
}

.json-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-save-json {
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.84em;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.35);
  transition: all 0.15s ease;
}

.btn-save-json:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.1);
  box-shadow: 0 4px 10px rgba(2, 132, 199, 0.45);
}

.btn-save-json:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.json-editor-wrap {
  width: 100%;
  position: relative;
}

.json-editor {
  width: 100%;
  box-sizing: border-box;
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, Menlo, monospace;
  font-size: 0.88em;
  line-height: 1.55;
  padding: 16px 18px;
  resize: vertical;
  min-height: 480px;
  background-color: var(--color-console-bg, #0b1120);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: #f1f5f9;
  outline: none;
  tab-size: 2;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.json-editor:focus {
  border-color: var(--color-text-link, #38bdf8);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25);
}

.json-footer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: 0.8em;
  color: var(--color-text-secondary);
  padding-top: 6px;
  flex-wrap: wrap;
}

.json-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'JetBrains Mono', Consolas, monospace;
}

.stat-dot {
  color: #475569;
}

.json-syntax-indicator {
  font-weight: 600;
}

.json-syntax-indicator.has-error {
  color: #f87171;
}

/* Full Size Image Carousel Lightbox */
.image-carousel-lightbox {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.92);
  backdrop-filter: blur(10px);
  z-index: 2500;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  user-select: none;
  animation: carouselFadeIn 0.2s ease-out;
}

@keyframes carouselFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.carousel-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.75), transparent);
  z-index: 2510;
}

.carousel-title-group {
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 80%;
  overflow: hidden;
}

.carousel-model-name {
  font-size: 1.15rem;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}

.carousel-counter {
  font-size: 0.88rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 4px 10px;
  border-radius: 20px;
  color: #ddd;
  font-weight: 500;
  white-space: nowrap;
}

.carousel-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.carousel-action-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(40, 40, 40, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: all 0.2s ease;
  cursor: pointer;
  text-decoration: none;
}

.carousel-action-btn:hover {
  background: var(--color-btn-secondary-hover);
  border-color: var(--color-btn-secondary-hover-border, #3498db);
  box-shadow: var(--color-btn-secondary-hover-shadow, none);
  color: #fff;
  transform: scale(1.08);
}

.carousel-stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  min-height: 0;
  overflow: hidden;
}

.carousel-image-wrapper {
  flex: 1;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 10px 20px;
}

.carousel-main-img {
  max-width: 100%;
  max-height: calc(100vh - 200px);
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.85);
  transition: transform 0.2s ease;
  cursor: pointer;
}

.carousel-main-img:active {
  transform: scale(0.99);
}

.carousel-nav-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(30, 30, 30, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #fff;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 2510;
}

.carousel-nav-btn:hover {
  background: var(--color-btn-primary);
  border-color: var(--color-btn-primary-hover-border, #3498db);
  transform: scale(1.12);
  box-shadow: var(--color-btn-primary-hover-shadow, 0 4px 16px rgba(52, 152, 219, 0.4));
}

.carousel-bottom-filmstrip {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 16px 20px 24px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  overflow-x: auto;
  max-width: 100%;
  z-index: 2510;
}

.carousel-filmstrip-thumb {
  width: 56px;
  height: 56px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  opacity: 0.65;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.carousel-filmstrip-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.carousel-filmstrip-thumb:hover {
  opacity: 0.95;
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px);
}

.carousel-filmstrip-thumb.active {
  opacity: 1;
  border-color: #3498db;
  box-shadow: 0 0 10px rgba(52, 152, 219, 0.6);
  transform: translateY(-2px) scale(1.05);
}

/* ==========================================================================
   Details Modern Preview Tab Formatting
   ========================================================================== */
.tab-btn-modern-preview {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.details-modern-tab {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
  box-sizing: border-box;
}

.detail-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-sizing: border-box;
}

.detail-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.section-title-icon {
  font-size: 0.9em;
  opacity: 0.85;
}

.detail-section-title {
  font-size: 0.9em;
  font-weight: 600;
  color: var(--color-text, #f1f5f9);
  letter-spacing: 0.02em;
}

.detail-identity-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 20px;
}

@media (max-width: 950px) {
  .detail-identity-grid {
    grid-template-columns: 1fr;
  }
}

.modern-field-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-label-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.field-label-bar label {
  font-size: 0.82em;
  font-weight: 500;
  color: var(--color-text-secondary, #94a3b8);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  letter-spacing: 0.01em;
}

.field-label-bar label i {
  font-size: 0.88em;
  opacity: 0.75;
}

.field-actions-modern {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.btn-action-xs {
  padding: 2px 7px;
  font-size: 0.73em;
  font-weight: 500;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-secondary, #94a3b8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s ease;
}

.btn-action-xs:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.modern-input {
  height: 36px;
  font-size: 0.9em;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-input, #0b1120);
  color: var(--color-text);
  box-sizing: border-box;
  transition: all 0.15s ease;
}

.modern-input:focus {
  border-color: var(--color-text-link, #38bdf8);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25);
  outline: none;
}

.modern-filename-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.filename-input-box {
  display: flex;
  align-items: center;
  width: 100%;
}

.filename-input {
  flex: 1;
  min-width: 0;
  width: 100%;
  border-top-right-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
  border-right: none !important;
}

.filename-input.editing {
  border-color: #f59e0b;
}

.modern-file-ext {
  height: 36px;
  padding: 0 12px;
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--color-border);
  border-left: none;
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 0.85em;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.filename-actions-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.filename-actions-bar.editing {
  gap: 10px;
}

.btn-save-rename {
  flex: 2;
  font-weight: 700;
}

.btn-priority-pill {
  margin-left: auto;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 0.78em;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-priority-pill.priority-high {
  background: rgba(56, 189, 248, 0.18);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.4);
}

.btn-priority-pill.priority-low {
  background: rgba(34, 197, 94, 0.18);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.4);
}

.btn-priority-pill.priority-none {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-secondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.move-active-box {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 4px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
}

.move-select-sm {
  height: 28px;
  font-size: 0.82em;
  padding: 2px 6px;
}

.btn-xs {
  padding: 3px 8px;
  font-size: 0.8em;
}

.btn-slider-mode-toggle {
  padding: 3px 10px;
  border-radius: 14px;
  font-size: 0.74rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-slider-mode-toggle:hover {
  background: var(--slider-toggle-active-bg, rgba(168, 85, 247, 0.12));
  border-color: var(--slider-toggle-active-border, rgba(168, 85, 247, 0.35));
  color: var(--slider-toggle-active-color, #c084fc);
}

.btn-slider-mode-toggle.active {
  background: var(--slider-toggle-active-bg, rgba(168, 85, 247, 0.18));
  color: var(--slider-toggle-active-color, #f3e8ff);
  border-color: var(--slider-toggle-active-border, rgba(168, 85, 247, 0.55));
  box-shadow: 0 0 10px rgba(168, 85, 247, 0.25);
}

.slider-toggle-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #64748b;
  transition: all 0.2s ease;
}

.slider-toggle-indicator.on {
  background: var(--slider-toggle-active-color, #c084fc);
  box-shadow: 0 0 6px var(--slider-toggle-active-color, #c084fc);
}

.modern-slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 24px;
}

.fat-track-modern {
  position: relative;
  height: 38px;
  background: var(--slider-track-bg, linear-gradient(180deg, #181818 0%, #222222 100%));
  border-radius: 8px;
  border: 1px solid var(--slider-track-border, var(--color-border));
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  box-shadow: var(--slider-track-shadow, inset 0 2px 5px rgba(0, 0, 0, 0.55));
}

.fat-slider-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 38px;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
  margin: 0;
}

.value-pin-bubble {
  background: var(--slider-thumb-color, var(--color-accent-title, #3498db));
  color: #ffffff;
  font-weight: 700;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  position: relative;
}

.pin-caret {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  color: var(--slider-thumb-color, var(--color-accent-title, #3498db));
  font-size: 0.85rem;
}

.track-endpoint {
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 45%;
  z-index: 2;
  pointer-events: none;
}

.badge-endpoint {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.72rem;
  line-height: 1.2;
  backdrop-filter: blur(6px);
  user-select: none;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
}

.badge-endpoint.min {
  background: var(--slider-endpoint-min-bg, rgba(52, 152, 219, 0.16));
  color: var(--slider-endpoint-min-color, #3498db);
  border: 1px solid var(--slider-endpoint-min-border, rgba(52, 152, 219, 0.35));
}

.badge-endpoint.max {
  background: var(--slider-endpoint-max-bg, rgba(155, 89, 182, 0.16));
  color: var(--slider-endpoint-max-color, #bb6bd9);
  border: 1px solid var(--slider-endpoint-max-border, rgba(155, 89, 182, 0.35));
}

.badge-endpoint .badge-label {
  font-weight: 600;
  color: var(--color-text, #f1f5f9);
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge-endpoint.min .badge-label {
  border-left: 1px solid var(--slider-endpoint-min-border, rgba(52, 152, 219, 0.35));
  padding-left: 5px;
  margin-left: 1px;
}

.badge-endpoint.max .badge-label {
  border-right: 1px solid var(--slider-endpoint-max-border, rgba(155, 89, 182, 0.35));
  padding-right: 5px;
  margin-right: 1px;
}

.weight-number-input {
  width: 65px;
  height: 38px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-input, #0b1120);
  color: var(--color-text);
  font-weight: 700;
  text-align: center;
  flex-shrink: 0;
  box-sizing: border-box;
}

/* Compact Slider Endpoint Configuration */
.compact-slider-config {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 8px;
  align-items: center;
}

.endpoint-control-row {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--color-bg-tertiary, rgba(0, 0, 0, 0.25));
  border: 1px solid var(--color-border-subtle, var(--color-border));
  border-radius: 6px;
  padding: 3px 6px;
}

.endpoint-control-row.min {
  border-left: 3px solid var(--slider-endpoint-min-color, #3498db);
}

.endpoint-control-row.max {
  border-left: 3px solid var(--slider-endpoint-max-color, #bb6bd9);
}

.endpoint-pill {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 0 2px;
  user-select: none;
  flex-shrink: 0;
}

.endpoint-pill.min {
  color: var(--slider-endpoint-min-color, #3498db);
}

.endpoint-pill.max {
  color: var(--slider-endpoint-max-color, #bb6bd9);
}

.stepper-group {
  display: inline-flex;
  align-items: center;
  background: var(--color-bg-input, #1e1e1e);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow: hidden;
  height: 26px;
  flex-shrink: 0;
}

.btn-stepper {
  width: 20px;
  height: 100%;
  background: transparent;
  border: none;
  color: var(--color-text-secondary, #94a3b8);
  font-weight: 700;
  font-size: 0.85rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 0.15s ease;
  user-select: none;
}

.btn-stepper:hover {
  background: var(--color-bg-hover, rgba(255, 255, 255, 0.15));
  color: var(--color-text, #ffffff);
}

.stepper-input {
  width: 38px;
  height: 100%;
  background: transparent;
  border: none;
  border-left: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  border-right: 1px solid var(--color-border-subtle, rgba(255, 255, 255, 0.08));
  color: var(--color-text, #ffffff);
  font-size: 0.8rem;
  font-weight: 700;
  text-align: center;
  padding: 0;
  outline: none;
  -moz-appearance: textfield;
}

.stepper-input::-webkit-outer-spin-button,
.stepper-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.compact-desc-input {
  flex: 1;
  min-width: 0;
  height: 26px;
  background: var(--color-bg-input, #1e1e1e);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text);
  font-size: 0.78rem;
  padding: 0 8px;
}

.compact-desc-input:focus {
  border-color: var(--slider-toggle-active-border, var(--color-border-accent, #3498db));
  outline: none;
}

/* Categorization & Tags (Single Line Row) */
.categorization-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px 24px;
  align-items: start;
}

@media (max-width: 950px) {
  .categorization-grid {
    grid-template-columns: 1fr;
  }
}

.cat-fields-row {
  display: flex;
  gap: 14px;
}

.input-with-clear {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-with-clear .modern-input {
  padding-right: 32px;
  width: 100%;
}

.clear-btn {
  position: absolute;
  right: 10px;
  cursor: pointer;
  color: #64748b;
  font-size: 0.88em;
  transition: color 0.15s ease;
}

.clear-btn:hover {
  color: #f87171;
}

.tag-counter-pill {
  font-size: 0.76em;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: rgba(255, 255, 255, 0.06);
  padding: 2px 8px;
  border-radius: 10px;
}

.modern-tag-cloud {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  background-color: var(--color-bg-input, #0b1120);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0 8px;
  height: 36px;
  min-height: 36px;
  max-height: 36px;
  box-sizing: border-box;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.modern-tag-cloud::-webkit-scrollbar {
  height: 3px;
}

.modern-tag-cloud::-webkit-scrollbar-thumb {
  background: rgba(56, 189, 248, 0.3);
  border-radius: 2px;
}

.modern-tag-cloud:focus-within {
  border-color: var(--color-text-link, #38bdf8);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25);
}

.modern-tag-pill {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.35);
  padding: 2px 8px;
  height: 24px;
  box-sizing: border-box;
  border-radius: 12px;
  font-size: 0.78em;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  flex-shrink: 0;
}

.remove-tag-icon {
  cursor: pointer;
  font-size: 0.85em;
  opacity: 0.7;
  transition: opacity 0.15s ease;
}

.remove-tag-icon:hover {
  opacity: 1;
  color: #f87171;
}

.modern-tag-input {
  flex: 1;
  min-width: 100px;
  height: 26px;
  border: none;
  background: transparent;
  color: var(--color-text);
  font-size: 0.85em;
  padding: 0 4px;
  outline: none;
  box-sizing: border-box;
}

/* Trigger Words & Prompts */
.prompts-grid-modern {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

@media (max-width: 900px) {
  .prompts-grid-modern {
    grid-template-columns: 1fr;
  }
}

.prompts-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.btn-copy-mini {
  padding: 1px 6px;
  font-size: 0.72em;
  font-weight: 500;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary, #94a3b8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s ease;
  opacity: 0.75;
}

.btn-copy-mini:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.2);
  opacity: 1;
  transform: translateY(-1px);
}

.modern-textarea {
  min-height: 64px;
  font-size: 0.88em;
  line-height: 1.45;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-input, #0b1120);
  color: var(--color-text);
  resize: vertical;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.15s ease;
}

.modern-textarea:focus {
  border-color: var(--color-text-link, #38bdf8);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25);
}

.notes-textarea {
  min-height: 85px;
}
</style>

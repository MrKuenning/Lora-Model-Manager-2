<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content model-modal">
      
      <!-- Top Header -->
      <div class="modal-header">
        <h2>
          {{ form.name || 'Unknown' }} 
          <span class="base-model-light">{{ form.baseModel || form.sdVersion || '' }}</span>
        </h2>
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
            <div class="main-image-container" @click="triggerFileInput">
              <div class="drop-overlay"><i class="fas fa-upload"></i> Drop image to add</div>
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

          <!-- MODEL INFO BOX -->
          <div class="info-box">
            <div class="info-box-header">MODEL INFO</div>
            <div class="info-box-content">
              <div class="info-row">
                <label>BASE MODEL:</label>
                <div class="info-val with-edit">
                  <span v-if="editingField !== 'baseModel'">{{ form.baseModel || '-' }}</span>
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
                  <i class="fas fa-edit edit-icon" v-if="editingField !== 'baseModel'" @click="startEditingField('baseModel')"></i>
                </div>
              </div>
              <div class="info-row">
                <label>Forge Model Type:</label>
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
              <div class="info-row">
                <label>CREATOR:</label>
                <div class="info-val with-edit">
                  <span>{{ form.creator || '-' }}</span>
                  <i class="fas fa-edit edit-icon" @click="promptEditField('creator', 'Creator')"></i>
                </div>
              </div>
              <div class="info-row">
                <label>Original Name:</label>
                <div class="info-val with-edit">
                  <span>{{ form.civitaiName || '-' }}</span>
                  <i class="fas fa-edit edit-icon" @click="promptEditField('civitaiName', 'Civitai Name')"></i>
                </div>
              </div>
              <div class="info-row">
                <label>Download Source:</label>
                <div class="info-val with-edit">
                  <a :href="form.civitaiUrl || form.civitai_url" target="_blank" v-if="form.civitaiUrl || form.civitai_url">{{ getDomainName(form.civitaiUrl || form.civitai_url) }}</a>
                  <span v-else>-</span>
                  <i class="fas fa-edit edit-icon" @click="promptEditField('civitaiUrl', 'Civitai URL')"></i>
                </div>
              </div>
              

              <div class="info-row stacked mt-10">
                <label>Preferred Weight:</label>
                <div class="weight-control">
                  <input type="range" min="-2" max="2" step="0.1" v-model="form.preferredWeight" class="weight-slider">
                  <input type="number" v-model="form.preferredWeight" class="weight-input" step="0.1">
                </div>
              </div>

            </div>
          </div>

          <div class="info-box">
            <div class="info-box-header">FILE INFO</div>
            <div class="info-box-content">
              <div class="info-row stacked">
                <label>File Path:</label>
                <div class="info-val-small" style="word-break: break-all; color: #aaa; display: flex; align-items: center; gap: 8px;">
                  <span>{{ model.path }}</span>
                  <i class="fas fa-folder-open" style="cursor: pointer; color: #3498db;" @click="openFolderPath" title="Open containing folder"></i>
                </div>
              </div>
              
              <div style="display: flex; gap: 15px; margin-top: 10px;">
                <div class="info-row stacked" style="flex: 1; margin-top: 0;">
                  <label>SIZE:</label>
                  <div class="info-val-small" style="color: #ddd;">{{ formatBytes(model.size) }}</div>
                </div>
                
                <div class="info-row stacked" style="flex: 1; margin-top: 0;">
                  <label>Added Date:</label>
                  <div class="info-val-small" style="color: #ddd;">{{ formatDate(model.date_modified || model.dateModified) }}</div>
                </div>
              </div>

              <div class="info-row stacked">
                <label>Hash:</label>
                <div class="info-val-small" style="word-break: break-all; color: #ddd;">{{ model.sha256 || model.hash || '-' }}</div>
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
          <div class="tab-content" v-if="activeTab === 'details'">
            <!-- Model Identity -->
            <div class="form-section">
              <div class="section-title">Model Identity</div>
              <div class="form-grid-identity">
                <div class="form-group">
                  <label>Model Name:</label>
                  <input type="text" v-model="form.name" class="form-control" @change="debouncedSave">
                  <div class="field-actions">
                    <button class="btn btn-micro" @click="setNameFromCivitai" title="Use Civitai Name">Civitai Name</button>
                    <button class="btn btn-micro" @click="cleanName" title="Fix capitalization and formatting">Clean</button>
                    <button class="btn btn-micro" @click="trimName" title="Remove model keywords">Trim</button>
                  </div>
                </div>
                
                <div class="form-group">
                  <label>Model Version:</label>
                  <input type="text" v-model="form.version" class="form-control" placeholder="(empty)" @change="debouncedSave">
                  <div class="field-actions">
                    <button class="btn btn-micro" @click="guessVersion" title="Guess version from filename">Guess Version</button>
                    <button class="btn btn-micro" @click="cleanVersion" title="Clean formatting">Clean</button>
                  </div>
                </div>
                


                <div class="form-group" style="grid-column: 1; margin-top: 5px;">
                  <label>Filename:</label>
                  <div class="filename-input-group">
                    <input type="text" v-if="!editingFilename" v-model="filenameNoExt" class="form-control" readonly>
                    <input type="text" v-else v-model="newFilenameTemp" class="form-control" @keydown.enter="saveRename">
                    <span class="file-ext">{{ getExtension() }}</span>
                  </div>
                  
                  <div class="field-actions" v-if="editingFilename" style="flex-wrap: wrap; gap: 8px;">
                    <button class="btn btn-micro" @click="applyRecommendedFilename"><i class="fas fa-magic"></i> Recommended</button>
                    <button class="btn btn-micro" @click="cleanFilename"><i class="fas fa-broom"></i> Clean</button>
                    <button class="btn btn-micro" @click="applyModelName"><i class="fas fa-tag"></i> Model Name</button>
                    <button class="btn btn-micro" @click="appendCreatorSuffix"><i class="fas fa-user-plus"></i> Creator Suffix</button>
                  </div>

                  <!-- Buttons row -->
                  <div class="identity-buttons" v-if="!editingFilename" style="flex-wrap: wrap; align-items: center;">
                    <button class="btn btn-secondary" @click="promptRename"><i class="fas fa-edit"></i> Modify Name</button>
                    <button class="btn btn-primary" @click="triggerRecommendedRename"><i class="fas fa-magic"></i> Use Recommended</button>
                    
                    <!-- Small Move Button -->
                    <button class="btn btn-secondary" @click="startMove" v-if="!movingFile">
                      <i class="fas fa-arrows-alt"></i> Move
                    </button>
                    <div v-else style="display: flex; gap: 5px; align-items: center; background: #222; padding: 2px 4px; border-radius: 4px; border: 1px solid #444;">
                      <select v-model="targetMoveFolder" class="form-control" style="height: 28px; font-size: 0.9em; padding: 0 5px;" :disabled="isMoving">
                        <option v-for="folder in availableMoveFolders" :key="folder" :value="folder">
                          {{ folder === '' ? 'Root' : folder }}
                        </option>
                      </select>
                      <button class="btn btn-success" @click="executeMove" style="padding: 2px 8px;" :disabled="isMoving">
                        <i class="fas fa-check" v-if="!isMoving"></i>
                        <i class="fas fa-spinner fa-spin" v-else></i>
                      </button>
                      <button class="btn btn-danger" @click="movingFile = false" style="padding: 2px 8px;" :disabled="isMoving">
                        <i class="fas fa-times"></i>
                      </button>
                    </div>

                  </div>
                  <div class="identity-buttons" v-else-if="editingFilename">
                    <button class="btn btn-success" @click="saveRename" style="flex: 2;" :disabled="isRenaming">
                      <i class="fas fa-spinner fa-spin" v-if="isRenaming"></i>
                      <i class="fas fa-check" v-else></i>
                      {{ isRenaming ? 'Renaming...' : 'Save' }}
                    </button>
                    <button class="btn btn-danger" @click="cancelRename" style="flex: 1;" :disabled="isRenaming"><i class="fas fa-times"></i> Cancel</button>
                  </div>
                </div>

                <div class="form-group" style="grid-column: 2; margin-top: 5px;">
                  <label>Flags / Actions:</label>
                  <div style="display: flex; gap: 10px; align-items: stretch; height: 100%;">
                    <button class="btn" :class="form.nsfw ? 'btn-danger' : 'btn-secondary'" @click="form.nsfw = !form.nsfw; debouncedSave()" style="flex: 1; font-weight: bold;">
                      NSFW: {{ form.nsfw ? 'Yes' : 'No' }}
                    </button>
                    
                    <button class="btn" :class="form.highLow === 'High' ? 'btn-primary' : (form.highLow === 'Low' ? 'btn-success' : 'btn-secondary')" @click="toggleHighLow" style="flex: 1; font-weight: bold;">
                      H/L: {{ form.highLow || 'None' }}
                    </button>
                    
                    <button class="btn" :class="form.tested ? 'btn-success' : 'btn-secondary'" @click="form.tested = !form.tested; debouncedSave()" style="flex: 1; font-weight: bold;">
                      Tested: {{ form.tested ? 'Yes' : 'No' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Categorization -->
            <div class="form-section">
              <div class="section-title">Categorization</div>
              <div class="form-grid-category">
                <div class="form-group">
                  <label>Category:</label>
                  <div style="position: relative; width: 100%; display: flex; align-items: center;">
                    <input type="text" v-model="form.category" class="form-control" placeholder="(empty)" @change="debouncedSave" list="categoriesList" style="padding-right: 30px;">
                    <i class="fas fa-times" 
                       style="position: absolute; right: 10px; cursor: pointer; color: #888; font-size: 0.9em;"
                       @mousedown.prevent="form.category = ''; debouncedSave()"
                       title="Clear"
                    ></i>
                  </div>
                  <datalist id="categoriesList">
                    <option v-for="opt in uniqueCategories" :key="opt" :value="opt"></option>
                  </datalist>
                </div>
                
                <div class="form-group" style="grid-row: span 2;">
                  <label>Tags:</label>
                  <textarea v-model="form.tags" class="form-control tags-textarea" placeholder="Type and press Enter to add tag..." @change="debouncedSave"></textarea>
                </div>
                
                <div class="form-group">
                  <label>Subcategory:</label>
                  <div style="position: relative; width: 100%; display: flex; align-items: center;">
                    <input type="text" v-model="form.subcategory" class="form-control" placeholder="(empty)" @change="debouncedSave" list="subcategoriesList" style="padding-right: 30px;">
                    <i class="fas fa-times" 
                       style="position: absolute; right: 10px; cursor: pointer; color: #888; font-size: 0.9em;"
                       @mousedown.prevent="form.subcategory = ''; debouncedSave()"
                       title="Clear"
                    ></i>
                  </div>
                  <datalist id="subcategoriesList">
                    <option v-for="opt in uniqueSubcategories" :key="opt" :value="opt"></option>
                  </datalist>
                </div>
              </div>
            </div>

            <!-- Keywords & Prompts -->
            <div class="form-section">
              <div class="section-title">Keywords & Prompts</div>
              <div class="form-grid-keywords">
                
                <div class="form-group">
                  <div class="label-with-actions">
                    <label>Trigger Words (Viewed in WebUI):</label>
                    <div class="actions">
                      <i class="fas fa-copy" @click="copyToClipboard(form.activationText)" title="Copy"></i>
                    </div>
                  </div>
                  <textarea v-model="form.activationText" class="form-control" @change="debouncedSave"></textarea>
                </div>
                
                <div class="form-group">
                  <div class="label-with-actions">
                    <label>Example Prompt 1:</label>
                    <div class="actions">
                      <i class="fas fa-copy" @click="copyToClipboard(form.examplePrompt)" title="Copy"></i>
                    </div>
                  </div>
                  <textarea v-model="form.examplePrompt" class="form-control" @change="debouncedSave"></textarea>
                </div>

                <div class="form-group">
                  <div class="label-with-actions">
                    <label>Negative Trigger Words (Viewed in WebUI):</label>
                    <div class="actions">
                      <i class="fas fa-copy" @click="copyToClipboard(form.negativeTriggerWords)" title="Copy"></i>
                    </div>
                  </div>
                  <textarea v-model="form.negativeTriggerWords" class="form-control" @change="debouncedSave"></textarea>
                </div>
                
                <div class="form-group">
                  <div class="label-with-actions">
                    <label>Example Prompt 2:</label>
                    <div class="actions">
                      <i class="fas fa-copy" @click="copyToClipboard(form.examplePrompt2)" title="Copy"></i>
                    </div>
                  </div>
                  <textarea v-model="form.examplePrompt2" class="form-control" @change="debouncedSave"></textarea>
                </div>

                <div class="form-group">
                  <div class="label-with-actions">
                    <label>All Trigger Words:</label>
                    <div class="actions">
                      <i class="fas fa-copy" @click="copyToClipboard(form.allTriggerWords)" title="Copy"></i>
                    </div>
                  </div>
                  <textarea v-model="form.allTriggerWords" class="form-control" @change="debouncedSave"></textarea>
                </div>
                
              </div>
            </div>

            <!-- Description -->
            <div class="form-section">
              <div class="section-title">Description</div>
              <div class="form-grid-description">
                <div class="form-group">
                  <label>Notes:</label>
                  <textarea v-model="form.notes" class="form-control" @change="debouncedSave"></textarea>
                </div>
                
                <div class="form-group">
                  <label><i class="fas fa-edit"></i> Description:</label>
                  <textarea v-model="form.description" class="form-control" placeholder="(empty)" @change="debouncedSave"></textarea>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB: CIVITAI MANAGEMENT -->
          <div class="tab-content civitai-tab" v-else-if="activeTab === 'civitai'">
            <div class="form-section">
              <div class="section-title">Metadata Fetching</div>
              <p class="help-text">Automatically download metadata (trigger words, description, tags, etc.) from Civitai.</p>
              
              <div class="action-grid-large">
                <!-- Row 1 -->
                <button class="btn btn-primary btn-large" @click="fetchAllCivitaiData">
                  <i class="fas fa-cloud-download-alt fa-2x"></i> 
                  <span><strong>Get All Civitai Data</strong><br>Downloads metadata and thumbnails in one click.</span>
                </button>
                <button class="btn btn-secondary btn-large" @click="fetchCivArchiveByHash">
                  <i class="fas fa-archive fa-2x"></i> 
                  <span><strong>Check CivArchive</strong><br>Search the community archive by hash.</span>
                </button>
                
                <!-- Row 2 -->
                <button class="btn btn-warning btn-large" @click="downloadThumbnails">
                  <i class="fas fa-images fa-2x"></i>
                  <span><strong>Download Thumbnails</strong><br>Download preview images/video from Civitai.</span>
                </button>
                <button class="btn btn-secondary btn-large" @click="promptCivitaiUrl">
                  <i class="fas fa-link fa-2x"></i> 
                  <span><strong>Fetch by URL</strong><br>Manually link this model to a Civitai page.</span>
                </button>
              </div>
            </div>

            <div class="form-section mt-20">
              <div class="section-title">Local File Tools</div>
              <p class="help-text">Utilities for managing the physical files on disk.</p>
              
              <div class="action-grid-large">
                <button class="btn btn-secondary btn-large" @click="generateHash">
                  <i class="fas fa-fingerprint fa-2x"></i>
                  <span><strong>Generate Hash</strong><br>Calculate the SHA256 hash if missing.</span>
                </button>
                <button class="btn btn-secondary btn-large" @click="fixThumbnail">
                  <i class="fas fa-wrench fa-2x"></i>
                  <span><strong>Fix Thumbnails</strong><br>Ensures the thumbnail uses the correct format.</span>
                </button>
                
                <!-- MOVE MODEL WIDGET -->
                <button class="btn btn-secondary btn-large" @click="startMove" v-if="!movingFile">
                  <i class="fas fa-arrows-alt fa-2x"></i>
                  <span><strong>Move Model</strong><br>Move file to a different folder.</span>
                </button>
                <div class="btn btn-secondary btn-large" v-else style="display: flex; flex-direction: column; justify-content: center; padding: 10px; cursor: default; align-items: stretch;">
                  <span style="margin-bottom: 5px; font-size: 0.9em; font-weight: bold; text-align: left;">Move to:</span>
                  <div style="display: flex; gap: 5px; width: 100%;">
                    <select v-model="targetMoveFolder" class="form-control" style="flex: 2; height: 35px;" :disabled="isMoving">
                      <option v-for="folder in availableMoveFolders" :key="folder" :value="folder">
                        {{ folder === '' ? 'Root' : folder }}
                      </option>
                    </select>
                    <button class="btn btn-success" @click="executeMove" style="flex: 1; padding: 0;" :disabled="isMoving">
                      <i class="fas fa-check" v-if="!isMoving"></i>
                      <i class="fas fa-spinner fa-spin" v-else></i> Move
                    </button>
                    <button class="btn btn-danger" @click="movingFile = false" style="flex: 0 0 35px; padding: 0;" :disabled="isMoving"><i class="fas fa-times"></i></button>
                  </div>
                </div>
                
                <button class="btn btn-danger btn-large" @click="deleteModel">
                  <i class="fas fa-trash fa-2x"></i>
                  <span><strong>Delete Model</strong><br>Permanently remove the model file and metadata.</span>
                </button>
              </div>
            </div>
          </div>

          <!-- TAB: FILES -->
          <div class="tab-content files-tab" v-else-if="activeTab === 'files'">
            <div class="form-section">
              <div class="section-title">Associated Files</div>
              <p class="help-text">Manage all files associated with this model.</p>
              
              <div v-if="isLoadingFiles" class="text-center py-4">
                <i class="fas fa-spinner fa-spin fa-2x"></i>
                <div class="mt-2 text-muted">Loading files...</div>
              </div>
              <div class="table-responsive mt-3" v-else>
                <table class="table text-light" style="width: 100%; border-collapse: collapse;">
                  <thead>
                    <tr style="border-bottom: 1px solid #444;">
                      <th style="width: 80px; padding: 10px;">Preview</th>
                      <th style="padding: 10px;">Filename</th>
                      <th style="padding: 10px;">Size</th>
                      <th style="width: 80px; text-align: center; padding: 10px;">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="file in associatedFiles" :key="file.path" style="border-bottom: 1px solid #333;">
                      <td style="padding: 10px;">
                        <div class="file-icon">
                          <img :src="api.getAssetUrl(file.relativePath, modelsStore.getCacheBuster(model.path))" alt="preview" style="max-height: 40px; max-width: 60px; object-fit: contain; background: #000; border-radius: 4px;" v-if="file.type === 'image'" />
                          <i v-else class="fas" :class="getFileIcon(file.filename)"></i>
                        </div>
                      </td>
                      <td style="vertical-align: middle; padding: 10px; word-break: break-all;">{{ file.filename }}</td>
                      <td style="vertical-align: middle; padding: 10px; white-space: nowrap;">{{ formatBytes(file.sizeBytes) }}</td>
                      <td style="text-align: center; vertical-align: middle; padding: 10px;">
                        <button class="btn btn-danger btn-sm" @click="deleteAssociatedFile(file)" title="Delete File" style="padding: 5px 10px;">
                          <i class="fas fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                    <tr v-if="associatedFiles.length === 0">
                      <td colspan="4" class="text-center text-muted py-4">No files found</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- TAB: RAW JSON -->
          <div class="tab-content json-tab" v-else-if="activeTab === 'json'">
            <div class="raw-actions">
              <button class="btn btn-primary" @click="saveRawJson"><i class="fas fa-save"></i> Save JSON</button>
              <button class="btn btn-secondary" @click="resetRawJson"><i class="fas fa-undo"></i> Reset Changes</button>
            </div>
            <textarea v-model="rawJsonText" class="form-control json-editor" spellcheck="false"></textarea>
          </div>

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
  description: ''
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

const filenameNoExt = computed(() => {
  if (!model.value || !model.value.filename) return '';
  const parts = model.value.filename.split('.');
  if (parts.length > 1) parts.pop();
  return parts.join('.');
});

const availableMoveFolders = computed(() => {
  const baseModel = form.baseModel || (model.value ? (model.value.base_model || model.value.baseModel) : '') || '';
  const roots = settingsStore.modelTypeRoots || [];
  const matchedRoot = roots.find(r => r.baseModel && r.baseModel.toLowerCase() === baseModel.toLowerCase());
  
  let folderPaths = (modelsStore.folders || []).map(f => f.path);
  
  if (matchedRoot && matchedRoot.rootFolder) {
    const rootPath = matchedRoot.rootFolder;
    folderPaths = folderPaths.filter(f => f === rootPath || f.startsWith(rootPath + '/') || f.startsWith(rootPath + '\\'));
    
    if (!folderPaths.includes(rootPath)) {
      folderPaths.unshift(rootPath);
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
    form.preferredWeight = data.preferredWeight || 1.0;
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

// Auto-save logic
let saveTimeout = null;
const debouncedSave = () => {
  if (saveTimeout) clearTimeout(saveTimeout);
  saveTimeout = setTimeout(async () => {
    try {
      const payload = { ...model.value, ...form };
      payload.nsfw = form.nsfw;
      payload.activation_text = form.activationText;
      payload.example_prompt = form.examplePrompt;
      payload.example_prompt_2 = form.examplePrompt2;
      payload.negative_trigger_words = form.negativeTriggerWords;
      payload.all_trigger_words = form.allTriggerWords;
      payload.civitaiUrl = form.civitaiUrl;
      
      await api.saveModel(props.modelId, payload);
      toast.showToast('Changes saved', 'success');
      modelsStore.reloadSingleModel(props.modelId);
      
    } catch (err) {
      toast.showToast('Failed to save changes', 'error');
    }
  }, 1000);
};

watch(() => form.nsfw, debouncedSave);
watch(() => form.preferredWeight, debouncedSave);

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

const cleanText = (text) => {
  if (!text) return '';
  let n = text;
  n = n.replace(/\//g, ' - ');
  n = n.replace(/[\\:*?"<>|]/g, '');
  n = n.replace(/_/g, ' ');
  n = n.replace(/-/g, ' - ');
  n = n.replace(/\s+/g, ' ');
  n = n.replace(/-+/g, '-');
  n = n.trim();
  n = n.replace(/\b([A-Z]{2,})\b/g, (match) => {
      return match.charAt(0).toUpperCase() + match.slice(1).toLowerCase();
  });
  n = n.replace(/\b[a-z]/g, char => char.toUpperCase());
  n = n.replace(/\s*-\s*-\s*/g, ' - '); 
  n = n.replace(/^\s*-\s*/, ''); 
  n = n.replace(/\s*-\s*$/, ''); 
  return n.trim();
};

const cleanName = () => {
  if (!form.name) return;
  form.name = cleanText(form.name);
  debouncedSave();
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

  const sep = `(?:\\s*[-_,\\[\\]|()]+\\s*|\\s+)`;

  const escapeRegExp = (string) => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Sort by length descending so longer terms like "Krea 2" are matched before shorter terms like "Krea"
  const sortedPrefixes = [...baseModelPrefixes].sort((a, b) => b.length - a.length);

  sortedPrefixes.forEach(prefix => {
      const escapedPrefix = escapeRegExp(prefix);
      const startPattern = new RegExp(`^${sep}*${escapedPrefix}${sep}*`, 'i');
      modelName = modelName.replace(startPattern, '');

      const endPattern = new RegExp(`${sep}*${escapedPrefix}${sep}*$`, 'i');
      modelName = modelName.replace(endPattern, '');

      const middlePattern = new RegExp(`(${sep})${escapedPrefix}(${sep})`, 'gi');
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
  modelName = modelName.trim();
  modelName = modelName.trim();

  form.name = modelName;
  debouncedSave();
};

const formatVersionNumber = (versionStr) => {
  const num = parseFloat(versionStr);
  if (num === Math.floor(num)) return String(Math.floor(num));
  return String(num);
};

const guessVersion = () => {
  if (!model.value) return;

  const modelName = form.name || model.value.name || '';
  const filename = model.value.filename || '';
  const civitaiName = form.civitaiName || model.value.civitaiName || '';
  const searchTexts = [modelName, filename, civitaiName];
  let bestVersion = null;

  for (const text of searchTexts) {
    if (!text) continue;
    const vMatches = text.match(/v(\d+(?:\.\d+)?)/gi);
    if (vMatches && vMatches.length > 0) {
      const lastMatch = vMatches[vMatches.length - 1];
      const numMatch = lastMatch.match(/v(\d+(?:\.\d+)?)/i);
      if (numMatch) {
        bestVersion = formatVersionNumber(numMatch[1]);
        break;
      }
    }
  }

  if (!bestVersion) {
    for (const text of searchTexts) {
      if (!text) continue;
      const matches = text.match(/\b(\d+(?:\.\d+)?)\b/g);
      if (matches && matches.length > 0) {
        for (let i = matches.length - 1; i >= 0; i--) {
          const num = parseFloat(matches[i]);
          if (num < 100) {
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
    toast.showToast(`Guessed version: ${bestVersion}`, 'success');
  } else {
    toast.showToast('Could not detect version', 'warning');
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
      await api.renameModel(props.modelId, newFilenameTemp.value);
      toast.showToast('Renamed successfully', 'success');
      modelsStore.fetchModels();
      
      const parts = props.modelId.split('/');
      parts[parts.length - 1] = newFilenameTemp.value;
      const newModelId = parts.join('/');
      
      emit('change-model', newModelId);
      editingFilename.value = false;
    } catch (err) {
      toast.showToast('Failed to rename', 'error');
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

const cleanFilename = () => {
  if (!newFilenameTemp.value) return;
  let n = newFilenameTemp.value;
  n = n.replace(/\//g, ' - ');
  n = n.replace(/[\\:*?"<>|]/g, '');
  n = n.replace(/_/g, ' ');
  n = n.replace(/-/g, ' - ');
  n = n.replace(/\s+/g, ' ');
  n = n.replace(/-+/g, '-');
  n = n.trim();
  n = n.replace(/\b([A-Z]{2,})\b/g, (match) => match.charAt(0).toUpperCase() + match.slice(1).toLowerCase());
  n = n.replace(/\b[a-z]/g, char => char.toUpperCase());
  n = n.replace(/\s*-\s*-\s*/g, ' - '); 
  n = n.replace(/^\s*-\s*/, ''); 
  n = n.replace(/\s*-\s*$/, ''); 
  n = n.trim();
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
  
  // Set default to current folder, or root if current folder isn't in available list
  if (availableMoveFolders.value.includes(model.value.folder)) {
    targetMoveFolder.value = model.value.folder;
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
  toast.showToast('Fetching all Civitai metadata & thumbnails...', 'info');
  try {
    await api.civitaiFetchByHash(model.value.path);
    await api.civitaiDownloadPreview(model.value.path);
    toast.showToast('All Civitai data downloaded!', 'success');
    await loadModel();
    modelsStore.fetchModels();
  } catch (err) {
    toast.showToast('Failed to fetch all data', 'error');
  }
};

const fetchCivitaiByHash = async () => {
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
    await api.civitaiDownloadPreview(model.value.path);
    toast.showToast('Thumbnails downloaded!', 'success');
    await loadModel();
  } catch (err) {
    toast.showToast('Failed to download thumbnails', 'error');
  }
};

// JSON
const resetRawJson = () => {
  if (model.value) {
    const rawData = model.value.json ? { ...model.value.json } : {};
    rawJsonText.value = JSON.stringify(rawData, null, 2);
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
  background-color: #2b2b2b;
  border-radius: 8px;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #e0e0e0;
}

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #222;
  border-bottom: 1px solid #444;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.2em;
  font-weight: 600;
  color: white;
}

.file-bracket { color: #aaa; }
.base-model-light { color: #777; font-weight: 400; margin-left: 10px; }

.header-actions {
  display: flex;
  gap: 15px;
}
.header-actions .btn-icon { color: #aaa; }
.header-actions .btn-icon:hover { color: white; }

.model-details-layout {
  display: flex;
  height: 100%;
  overflow: hidden;
}

/* Left Column */
.left-column {
  width: 320px;
  background-color: #333;
  padding: 15px;
  overflow-y: auto;
  border-right: 1px solid #444;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.image-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.main-image-container {
  width: 100%;
  aspect-ratio: 3/4;
  background-color: #222;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
}
.main-image-container:hover { border-color: #555; }

.drop-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0,0,0,0.6);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  color: #ccc;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 5px;
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
  color: #666;
}

.thumbnail-strip {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.thumb, .add-thumb {
  width: 45px;
  height: 45px;
  border-radius: 4px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
}
.thumb.active { border-color: #3498db; }

.add-thumb {
  background: #222;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  border: 1px dashed #555;
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
  padding: 8px 12px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}
.image-hover-actions .btn-danger:hover {
  background-color: rgba(231, 76, 60, 0.9);
}
.image-hover-actions .btn-primary:hover {
  background-color: rgba(52, 152, 219, 0.9);
}
.btn-danger { background-color: #e74c3c; color: white; }
.btn-danger:hover { background-color: #c0392b; }
.btn-success { background-color: var(--color-btn-success); color: white; }
.btn-success:hover { background-color: var(--color-btn-success-hover); }

/* Info Box */
.info-box {
  background-color: #2b2b2b;
  border: 1px solid #444;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.info-box-header {
  background-color: #222;
  padding: 8px 12px;
  font-size: 0.85em;
  font-weight: bold;
  color: #aaa;
  border-bottom: 1px solid #444;
}

.info-box-content {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row { display: flex; flex-direction: column; font-size: 0.85em; }
.info-row label { color: #888; margin-bottom: 2px; }
.info-val { 
  color: #ddd; 
  word-break: break-all;
  overflow-wrap: anywhere;
}
.info-val a {
  color: #4a90e2;
  text-decoration: none;
}
.info-val a:hover {
  text-decoration: underline;
  color: #6eb0ff;
}
.info-val span {
  word-break: break-all;
  overflow-wrap: anywhere;
}
.info-val.with-edit { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.edit-icon { color: #666; cursor: pointer; }
.edit-icon:hover { color: #fff; }
.info-row.stacked { margin-top: 5px; }

.weight-control { display: flex; align-items: center; gap: 10px; }
.weight-slider { flex: 1; }
.weight-input { width: 50px; background: #111; border: 1px solid #444; color: white; padding: 2px 5px; }

.inline-edit-input {
  flex: 1;
  background: #111;
  border: 1px solid #444;
  color: white;
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
  background-color: #222;
  border-bottom: 1px solid #444;
}
.tabs-header button {
  padding: 15px 25px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: #888;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
}
.tabs-header button:hover { color: white; }
.tabs-header button.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.section-title {
  font-weight: bold;
  font-size: 1em;
  color: #fff;
  border-bottom: 1px solid #444;
  padding-bottom: 5px;
}

.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.85em; color: #aaa; display: flex; align-items: center; gap: 5px; }
.form-control {
  background-color: #222;
  border: 1px solid #444;
  color: #eee;
  padding: 8px 12px;
  border-radius: 4px;
  font-family: inherit;
  font-size: 0.9em;
}
.form-control:focus { border-color: #3498db; outline: none; }
textarea.form-control { 
  height: 56px; 
  min-height: 56px;
  max-height: 500px;
  overflow-y: auto; 
  resize: vertical; 
}

.form-grid-identity, .form-grid-category, .form-grid-keywords, .form-grid-description {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.filename-input-group { display: flex; }
.filename-input-group input { flex: 1; border-radius: 4px 0 0 4px; }
.file-ext { background: #333; border: 1px solid #444; border-left: none; padding: 8px; color: #888; border-radius: 0 4px 4px 0; font-size: 0.9em; }

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
  padding: 3px 8px;
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-micro:hover {
  background-color: var(--color-btn-primary);
  color: #fff;
  border-color: var(--color-btn-primary);
}

.label-with-actions { display: flex; justify-content: space-between; align-items: center; }
.label-with-actions .actions { display: flex; gap: 10px; color: #888; }
.label-with-actions .actions i { cursor: pointer; }
.label-with-actions .actions i:hover { color: #fff; }

/* Civitai Tab */
.civitai-tab {
  align-items: center;
}
.help-text {
  color: #aaa;
  margin: 0 0 10px 0;
}
.action-grid-large {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  width: 100%;
  max-width: 100%;
}
.btn-large {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 30px;
  text-align: center;
  background-color: #222;
  border: 1px solid #444;
  border-radius: 8px;
}
.btn-large:hover {
  background-color: #333;
  border-color: #555;
  transform: translateY(-2px);
}
.btn-large span {
  font-size: 0.9em;
  color: #888;
  line-height: 1.4;
}
.btn-large strong {
  font-size: 1.2em;
  color: #fff;
}
.btn-danger.btn-large {
  background-color: rgba(231, 76, 60, 0.1);
  border-color: #e74c3c;
  color: #e74c3c;
}
.btn-danger.btn-large:hover {
  background-color: rgba(231, 76, 60, 0.2);
}
.btn-danger.btn-large strong {
  color: #e74c3c;
}

.btn-primary.btn-large {
  background-color: rgba(52, 152, 219, 0.1);
  border-color: #3498db;
  color: #3498db;
}
.btn-primary.btn-large:hover {
  background-color: rgba(52, 152, 219, 0.2);
}
.btn-primary.btn-large strong {
  color: #3498db;
}

.btn-warning.btn-large {
  background-color: rgba(230, 126, 34, 0.1);
  border-color: #e67e22;
  color: #e67e22;
}
.btn-warning.btn-large:hover {
  background-color: rgba(230, 126, 34, 0.2);
}
.btn-warning.btn-large strong {
  color: #e67e22;
}

/* JSON Tab */
.json-tab {
  display: flex;
  flex-direction: column;
}
.raw-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 15px;
}
.json-editor {
  flex: 1;
  font-family: monospace;
  font-size: 0.9em;
  padding: 20px;
  resize: none;
  min-height: 500px;
}
</style>

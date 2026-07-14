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
          <button class="tab-btn" :class="{ active: activeTab === 'views' }" @click="activeTab = 'views'">View Settings</button>
          <button class="tab-btn" :class="{ active: activeTab === 'safemode' }" @click="activeTab = 'safemode'">Safe Mode</button>
          <button class="tab-btn" :class="{ active: activeTab === 'columns' }" @click="activeTab = 'columns'">Table Columns</button>
          <button class="tab-btn" :class="{ active: activeTab === 'grid' }" @click="activeTab = 'grid'">Grid Card</button>
          <button class="tab-btn" :class="{ active: activeTab === 'formatting' }" @click="activeTab = 'formatting'">Filename Formatting</button>
          <button class="tab-btn" :class="{ active: activeTab === 'roots' }" @click="activeTab = 'roots'">Model Type Roots</button>
          <button class="tab-btn" :class="{ active: activeTab === 'trimnames' }" @click="activeTab = 'trimnames'">Trim Names</button>
          <button class="tab-btn" :class="{ active: activeTab === 'scanner' }" @click="activeTab = 'scanner'">Scanner</button>
        </div>
        
        <div class="settings-content">
          <!-- General Tab -->
          <div v-if="activeTab === 'general'" class="settings-section">


            
            <div class="setting-group">
              <label>LoRA Models Directory</label>
              <div class="input-with-button">
                <input type="text" v-model="localSettings.modelsDirectory" class="form-control" placeholder="e.g. C:\AI\Models\LoRA">
                <button class="btn btn-secondary" @click="browseForFolder('modelsDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
              </div>
              <small>Path to your primary LoRA models folder</small>
            </div>
            
            <div class="setting-group">
              <label>Checkpoints Directory</label>
              <div class="input-with-button">
                <input type="text" v-model="localSettings.checkpointsDirectory" class="form-control" placeholder="e.g. C:\AI\Models\Stable-Diffusion">
                <button class="btn btn-secondary" @click="browseForFolder('checkpointsDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
              </div>
              <small>Path to your primary Checkpoint models folder</small>
            </div>
            
            <div class="setting-group">
              <label>Default Download Directory</label>
              <div class="input-with-button">
                <input type="text" v-model="localSettings.defaultDownloadDirectory" class="form-control" placeholder="e.g. C:\AI\Downloads">
                <button class="btn btn-secondary" @click="browseForFolder('defaultDownloadDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
              </div>
              <small>Default folder path where newly downloaded models will be saved</small>
            </div>
            
            <div class="setting-group">
              <label>Default Sorting Directory</label>
              <div class="input-with-button">
                <input type="text" v-model="localSettings.defaultSortingDirectory" class="form-control" placeholder="e.g. C:\AI\Sorting">
                <button class="btn btn-secondary" @click="browseForFolder('defaultSortingDirectory')"><i class="fas fa-folder-open"></i> Browse</button>
              </div>
              <small>Default folder path used for processing/sorting unorganized models</small>
            </div>
          </div>
          
          <!-- Views Tab -->
          <div v-if="activeTab === 'views'" class="settings-section">
            <div class="setting-group">
              <label>Default View</label>
              <select v-model="localSettings.defaultView" class="form-control">
                <option value="grid">Grid View</option>
                <option value="table">Table View</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>Default Sort</label>
              <select v-model="localSettings.defaultSort" class="form-control">
                <option value="name-asc">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
                <option value="date-desc">Date (Newest)</option>
                <option value="date-asc">Date (Oldest)</option>
                <option value="size-desc">Size (Largest)</option>
                <option value="size-asc">Size (Smallest)</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label class="checkbox-label" style="margin-top: 10px;">
                <input type="checkbox" v-model="localSettings.filterFoldersWithBaseModel">
                <strong>Filter folders with base model filter</strong>
              </label>
              <small style="margin-left: 24px;">When enabled, the folder list will only show folders containing models that match your current base model filter.</small>
            </div>
          </div>
          
          <!-- Safe Mode Tab -->
          <div v-if="activeTab === 'safemode'" class="settings-section">
            <div class="setting-group">
              <label class="checkbox-label" style="margin-top: 10px;">
                <input type="checkbox" v-model="localSettings.safeModeDefault">
                <strong>Safe Mode: Enabled by default</strong>
              </label>
              <small style="margin-left: 24px;">When checked, Safe Mode is on for new sessions or server starts. If unchecked, it starts disabled.</small>
            </div>

            <div class="setting-group">
              <label class="checkbox-label" style="margin-top: 10px;">
                <input type="checkbox" v-model="localSettings.safeModeOnReload">
                <strong>Safe Mode: Enabled on reload</strong>
              </label>
              <small style="margin-left: 24px;">When checked, refreshing the page always resets Safe Mode to its default state. When unchecked, it remembers your current state.</small>
            </div>
            
            <div class="setting-group">
              <label class="checkbox-label" style="margin-top: 10px;">
                <input type="checkbox" v-model="localSettings.nsfwBlurOverlay">
                <strong>Blur NSFW Images by default</strong>
              </label>
              <small style="margin-left: 24px;">When enabled, NSFW images will be blurred until clicked.</small>
            </div>
          </div>
          
          <!-- Columns Tab -->
          <div v-if="activeTab === 'columns'" class="settings-section columns-list">
            <p class="section-help">Select which columns to display and drag to reorder them.</p>
            <div v-for="(col, index) in localSettings.columnOrder" :key="col" class="column-reorder-item">
              <label class="checkbox-label">
                <input type="checkbox" v-model="localSettings.visibleColumns[col]">
                {{ formatColumnName(col) }}
              </label>
              <div class="reorder-controls">
                <button class="btn btn-icon btn-small" @click="moveColumnUp(index)" :disabled="index === 0" title="Move Up">
                  <i class="fas fa-arrow-up"></i>
                </button>
                <button class="btn btn-icon btn-small" @click="moveColumnDown(index)" :disabled="index === localSettings.columnOrder.length - 1" title="Move Down">
                  <i class="fas fa-arrow-down"></i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Grid Card Tab -->
          <div v-if="activeTab === 'grid'" class="settings-section columns-grid">
            <div class="setting-group" style="grid-column: 1 / -1; display: flex; gap: 20px;">
              <div style="flex: 1;">
                <label>Card Title Display</label>
                <select v-model="localSettings.gridCard.titleDisplay" class="form-control">
                  <option value="modelName">Model Name</option>
                  <option value="fileName">File Name</option>
                </select>
              </div>
              <div style="flex: 1;">
                <label>Card Size</label>
                <select v-model="localSettings.gridCard.cardSize" class="form-control">
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                </select>
              </div>
            </div>

            <div class="settings-header" style="grid-column: 1 / -1; margin-top: 15px; margin-bottom: 0;">
              <h3 style="margin: 0;">Tags</h3>
            </div>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showBaseModel"> Show Base Model Tag
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showCategory"> Show Category Tag
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showHighLow"> Show High/Low Tag
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showFolder"> Show Folder Tag
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showNsfwBadge"> Show NSFW Badge
            </label>

            <div class="settings-header" style="grid-column: 1 / -1; margin-top: 15px; margin-bottom: 0;">
              <h3 style="margin: 0;">Action Buttons</h3>
            </div>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showActions"> Show Action Buttons Bar
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showCopyTriggerWords"> Show Copy Trigger Words
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showUrlButton"> Show URL Button
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.gridCard.showInfoButton"> Show Info Button
            </label>
          </div>
          
          <!-- Formatting Tab -->
          <div v-if="activeTab === 'formatting'" class="settings-section">
            <div class="settings-header">
              <h3 style="margin: 0;">Filename Formatting:</h3>
              <span class="variables-help">Variables: {modelname}, {version}, <span style="color: #f39c12; font-weight: bold;">{highlow}*</span>, {category}, {subcategory}</span>
            </div>
            <div class="warning-text">
              <i class="fas fa-exclamation-triangle"></i> * {highlow} is a required field. If you include it models will require it to be populated. rename.
            </div>
            
            <div class="list-container">
              <div v-for="(format, index) in localSettings.filenameFormats" :key="index" class="list-row">
                <input type="text" v-model="format.baseModel" class="form-control col-left" placeholder="Base Model (e.g. Pony)">
                <input type="text" v-model="format.format" class="form-control col-right" placeholder="Format string">
                <button v-if="format.baseModel === 'Default'" class="btn-lock" disabled title="Cannot remove default">
                  <i class="fas fa-lock"></i>
                </button>
                <button v-else class="btn-remove" @click="removeFilenameFormat(index)" title="Remove">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <button class="btn-add-full" @click="addFilenameFormat">
                <i class="fas fa-plus"></i> Add Format Rule
              </button>
            </div>
          </div>
          
          <!-- Roots Tab -->
          <div v-if="activeTab === 'roots'" class="settings-section">
            <div class="settings-header">
              <h3 style="margin: 0;">Model Type Roots:</h3>
              <span class="variables-help">Map Model Types to root folders to filter Move UI</span>
            </div>
            <p class="section-help" style="margin-bottom: 5px;">
              When moving models, if the model has a matching Model Type (Base Model), the folder dropdown will be filtered to only show the root folder and its subdirectories. You should use a <strong>relative path</strong> (e.g., Comfy/QWEN) rather than a full system path. You can select existing folders from the dropdown.
            </p>
            
            <div class="list-container">
              <div v-for="(root, index) in localSettings.modelTypeRoots" :key="index" class="list-row">
                <input type="text" v-model="root.baseModel" class="form-control col-left" placeholder="Base Model (e.g. Pony)">
                <input type="text" v-model="root.rootFolder" class="form-control col-right" placeholder="Root Folder">
                <button class="btn-remove" @click="removeModelTypeRoot(index)" title="Remove">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <button class="btn-add-full" @click="addModelTypeRoot">
                <i class="fas fa-plus"></i> Add Root Mapping
              </button>
            </div>
          </div>
          
          <!-- Trim Names Tab -->
          <div v-if="activeTab === 'trimnames'" class="settings-section" style="flex: 1; overflow: hidden;">
            <div class="settings-header" style="flex: 0 0 auto;">
              <h3 style="margin: 0;">Trim Names List:</h3>
              <span class="variables-help">These terms are removed from model names when clicking Trim. Special characters like [] and . are handled automatically.</span>
            </div>
            
            <div class="add-tag-container" style="flex: 0 0 auto;">
              <input 
                type="text" 
                v-model="newTrimName" 
                @keydown.enter="addTrimName" 
                placeholder="Type a term to remove and press Enter" 
                class="form-control" 
              />
              <button class="btn btn-secondary" @click="addTrimName">
                <i class="fas fa-plus"></i> Add
              </button>
            </div>

            <div class="tags-container" style="flex: 1; max-height: none; overflow-y: auto; align-content: flex-start;">
              <div v-for="(name, index) in localSettings.trimNames" :key="index" class="tag-chip">
                {{ name }}
                <button class="btn-remove-tag" @click="removeTrimName(index)" title="Remove">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Scanner Tab -->
          <div v-if="activeTab === 'scanner'" class="settings-section columns-grid">
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.scanSettings.skipExistingData"> Skip models with existing Civitai data
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.scanSettings.skipNsfwPreviews"> Skip NSFW preview images
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.scanSettings.downloadMaxSize"> Download full-size preview images
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="localSettings.scanSettings.fetchCreatorInfo"> Fetch creator info from API (slower)
            </label>
            
            <div class="setting-group" style="margin-top: 20px;">
              <label>Delay between requests (seconds)</label>
              <input type="number" step="0.1" min="0" v-model="localSettings.scanSettings.delayBetweenRequests" class="form-control" style="width: 100px;">
              <small>Controls how fast the bulk scanner hits the Civitai API to avoid rate limiting.</small>
            </div>
            
            <div class="settings-header" style="grid-column: 1 / -1; margin-top: 15px; margin-bottom: 0;">
              <h3 style="margin: 0;">Maintenance</h3>
            </div>
            <div class="setting-group" style="grid-column: 1 / -1;">
              <button class="btn btn-secondary" @click="cleanJsonFiles" :disabled="cleaningJson">
                <i class="fas fa-broom" :class="{'fa-spin': cleaningJson}"></i> {{ cleaningJson ? 'Cleaning...' : 'Clean JSON Files' }}
              </button>
              <small>Migrate any remaining .civitai.info files into standard .json metadata files and delete the old info files.</small>
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
import { useToast } from '../../composables/useToast';
import { api } from '../../api/client';

const emit = defineEmits(['close']);
const settings = useSettingsStore();
const toast = useToast();

const activeTab = ref('general');
const saving = ref(false);
const newTrimName = ref('');

// Create a deep reactive copy of settings for editing
const localSettings = reactive({
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
  visibleColumns: {},
  columnOrder: [],
  gridCard: {},
  filenameFormats: [],
  modelTypeRoots: [],
  trimNames: [],
  scanSettings: {}
});

onMounted(() => {
  // Initialize local copy
  localSettings.theme = settings.theme;
  localSettings.defaultView = settings.defaultView;
  localSettings.defaultSort = settings.defaultSort;
  localSettings.safeModeDefault = settings.safeModeDefault !== false; // Default true
  localSettings.safeModeOnReload = settings.safeModeOnReload !== false; // Default true
  localSettings.nsfwBlurOverlay = settings.nsfwBlurOverlay !== false; // Default true
  localSettings.filterFoldersWithBaseModel = settings.filterFoldersWithBaseModel || false;
  localSettings.modelsDirectory = settings.modelsDirectory;
  localSettings.checkpointsDirectory = settings.checkpointsDirectory;
  localSettings.defaultDownloadDirectory = settings.defaultDownloadDirectory;
  localSettings.defaultSortingDirectory = settings.defaultSortingDirectory;
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
    showBaseModel: true,
    showCategory: true,
    showActions: true,
    showCivitaiLink: true,
    showNsfwBadge: true,
    showInfoButton: true
  };
  localSettings.gridCard = JSON.parse(JSON.stringify(settings.gridCard || defaultGridCard));
  
  localSettings.filenameFormats = JSON.parse(JSON.stringify(settings.filenameFormats || []));
  localSettings.modelTypeRoots = JSON.parse(JSON.stringify(settings.modelTypeRoots || []));
  localSettings.trimNames = JSON.parse(JSON.stringify(settings.trimNames || []));
  
  const defaultScanSettings = {
    skipExistingData: true,
    skipNsfwPreviews: true,
    downloadMaxSize: false,
    fetchCreatorInfo: true,
    delayBetweenRequests: 0.5
  };
  localSettings.scanSettings = JSON.parse(JSON.stringify(settings.scanSettings || defaultScanSettings));
});

const formatColumnName = (key) => {
  // Convert camelCase to Title Case
  const result = key.replace(/([A-Z])/g, " $1");
  return result.charAt(0).toUpperCase() + result.slice(1);
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
  localSettings.filenameFormats.push({ baseModel: '', format: '' });
};

const removeFilenameFormat = (index) => {
  localSettings.filenameFormats.splice(index, 1);
};

const addModelTypeRoot = () => {
  localSettings.modelTypeRoots.push({ baseModel: '', rootFolder: '' });
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
  const success = await settings.saveSettings(localSettings);
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
}

.tab-btn {
  flex: 1;
  padding: 12px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.columns-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.column-reorder-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-border);
}

.reorder-controls {
  display: flex;
  gap: 5px;
}

.section-help {
  margin: 0 0 15px 0;
  color: var(--color-text-secondary);
  font-size: 0.9em;
  line-height: 1.4;
}

.section-help code {
  background-color: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
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
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 5px;
}

.tag-chip {
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  padding: 6px 12px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: monospace;
  font-size: 0.9em;
  transition: border-color 0.2s;
}

.tag-chip:hover {
  border-color: var(--color-text-secondary);
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
  font-size: 1.1em;
  transition: color 0.2s;
}

.btn-remove-tag:hover {
  color: #c0392b;
}
</style>

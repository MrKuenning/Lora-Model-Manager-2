<template>
  <div class="app-wrapper">
    <AppHeader @open-settings="showSettings = true" @open-duplicates="showBulkDuplicates = true" />
    
    <div class="main-content-wrapper">
      <FolderSidebar />
      
      <main class="content-area">
        <div class="controls-bar">
          <button v-if="models.sidebarHidden" class="btn btn-secondary" @click="models.sidebarHidden = false" title="Show Sidebar" style="margin-right: 10px;">
            <i class="fas fa-folder"></i> Folders
          </button>
          <div class="filter-controls">
            <div class="custom-dropdown" @click="dropdownOpen = !dropdownOpen" ref="dropdownRef">
              <div class="dropdown-header">
                {{ (Array.isArray(models.baseModelFilter) && models.baseModelFilter.length > 0) ? models.baseModelFilter.join(', ') : 'All Base Models' }}
                <i class="fas fa-chevron-down"></i>
              </div>
              <div class="dropdown-list" v-if="dropdownOpen" @click.stop>
                <label class="dropdown-item">
                  <input type="checkbox" :checked="!Array.isArray(models.baseModelFilter) || models.baseModelFilter.length === 0" @change="models.baseModelFilter = []">
                  All Base Models
                </label>
                <label class="dropdown-item" v-for="base in models.uniqueBaseModels" :key="base">
                  <input type="checkbox" :value="base" v-model="models.baseModelFilter">
                  {{ base }}
                </label>
              </div>
            </div>
            
            <select v-model="models.sortBy" class="form-select">
              <optgroup label="Name & File">
                <option value="name-asc">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
                <option value="filename-asc">Filename (A-Z)</option>
                <option value="filename-desc">Filename (Z-A)</option>
              </optgroup>
              <optgroup label="Metadata">
                <option value="baseModel-asc">Base Model (A-Z)</option>
                <option value="baseModel-desc">Base Model (Z-A)</option>
                <option value="category-asc">Category (A-Z)</option>
                <option value="category-desc">Category (Z-A)</option>
                <option value="subcategory-asc">Subcategory (A-Z)</option>
                <option value="subcategory-desc">Subcategory (Z-A)</option>
              </optgroup>
              <optgroup label="File Info">
                <option value="folder-asc">Folder (A-Z)</option>
                <option value="folder-desc">Folder (Z-A)</option>
                <option value="date-desc">Newest First</option>
                <option value="date-asc">Oldest First</option>
                <option value="size-desc">Largest First</option>
                <option value="size-asc">Smallest First</option>
              </optgroup>
            </select>
            
            <select v-model="models.groupBy" class="form-select">
              <option value="none">No Grouping</option>
              <option value="folder">Group by Folder</option>
              <option value="baseModel">Group by Base Model</option>
              <option value="category">Group by Category</option>
              <option value="subcategory">Group by Subcategory</option>
              <option value="highLow">Group by High/Low</option>
              <option value="nsfw">Group by NSFW</option>
              <option value="size">Group by Size</option>
              <option value="tags">Group by Tags</option>
            </select>
          </div>
          
          <div class="search-container">
            <i class="fas fa-search search-icon"></i>
            <input 
              type="text" 
              v-model="models.searchQuery" 
              placeholder="Search (e.g. cat:plants !red <blue | green>)..."
              class="search-input"
            >
            <div class="search-actions">
              <button v-if="models.searchQuery" class="clear-search-btn" @click="models.searchQuery = ''" title="Clear Search">
                <i class="fas fa-times"></i>
              </button>
              <div class="search-help">
                <i class="far fa-question-circle help-icon"></i>
                <div class="help-popover">
                  <div class="help-title">Search Syntax</div>
                  <ul>
                    <li><strong>space</strong> = AND</li>
                    <li><strong>|</strong> = OR</li>
                    <li><strong>!</strong> or <strong>-</strong> = NOT</li>
                    <li><strong>&lt; &gt;</strong> = Group</li>
                    <li><strong>" "</strong> = Exact phrase</li>
                    <li><strong>field:</strong> = cat, name, tag, url...</li>
                  </ul>
                  <div class="help-example">
                    Example: <br><code>cat:plants !red &lt;"yellow tree" | leaf&gt;</code>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="models-container">
          <div v-if="models.loading" class="loading-state">
            <i class="fas fa-spinner fa-spin fa-3x"></i>
            <p>Loading models...</p>
          </div>
          
          <div v-else-if="models.error" class="error-state">
            <i class="fas fa-exclamation-circle fa-3x"></i>
            <p>{{ models.error }}</p>
          </div>
          
          <div v-else-if="models.filteredModels.length === 0" class="empty-state">
            <i class="fas fa-folder-open fa-3x"></i>
            <p>No models found.</p>
          </div>
          
          <div v-else class="view-renderer">
            <template v-if="models.groupBy === 'none'">
              <GridView 
                v-if="settings.defaultView === 'grid'" 
                :models="models.filteredModels" 
                @open-model="openModelModal" 
              />
              <TableView 
                v-else
                :models-list="models.filteredModels"
                @open-model="openModelModal"
              />
            </template>
            
            <template v-else>
              <div v-for="(groupList, groupName) in models.groupedModels" :key="groupName" class="model-group-wrapper">
                <div class="group-header">
                  <h3 class="group-title">{{ groupName || 'Uncategorized' }}</h3>
                  <span class="group-count">{{ groupList.length }} models</span>
                </div>
                
                <GridView 
                  v-if="settings.defaultView === 'grid'" 
                  :models="groupList" 
                  @open-model="openModelModal" 
                />
                <TableView 
                  v-else
                  :models-list="groupList"
                  @open-model="openModelModal"
                />
              </div>
            </template>
          </div>
        </div>
      </main>
    </div>
    
    <!-- Modals -->
    <SettingsModal v-if="showSettings" @close="showSettings = false" />
    <ModelModal v-if="selectedModelId" :modelId="selectedModelId" @close="selectedModelId = null" @change-model="selectedModelId = $event" />
    <BulkEditModal v-if="showBulkEdit" @close="showBulkEdit = false" />
    <BulkMoveModal v-if="showBulkMove" @close="showBulkMove = false" />
    <BulkRenameModal v-if="showBulkRename" @close="showBulkRename = false" />
    <BulkDuplicatesModal v-if="showBulkDuplicates" @close="showBulkDuplicates = false" />
    
    <!-- Floating Toolbars -->
    <BulkToolbar 
      @open-edit="showBulkEdit = true" 
      @open-move="showBulkMove = true"
      @open-rename="showBulkRename = true"
      @trigger-delete="confirmBulkDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useModelsStore } from '../stores/models';
import { useSettingsStore } from '../stores/settings';
import { useBulkStore } from '../stores/bulk';
import { api } from '../api/client';
import AppHeader from '../components/layout/AppHeader.vue';
import FolderSidebar from '../components/layout/FolderSidebar.vue';
import BulkToolbar from '../components/layout/BulkToolbar.vue';
import GridView from '../components/models/GridView.vue';
import TableView from '../components/models/TableView.vue';
import SettingsModal from '../components/layout/SettingsModal.vue';
import ModelModal from '../components/models/ModelModal.vue';
import BulkEditModal from '../components/models/BulkEditModal.vue';
import BulkMoveModal from '../components/models/BulkMoveModal.vue';
import BulkRenameModal from '../components/models/BulkRenameModal.vue';
import BulkDuplicatesModal from '../components/models/BulkDuplicatesModal.vue';

const models = useModelsStore();
const settings = useSettingsStore();
const bulkStore = useBulkStore();

const showSettings = ref(false);
const showBulkEdit = ref(false);
const showBulkMove = ref(false);
const showBulkRename = ref(false);
const showBulkDuplicates = ref(false);
const selectedModelId = ref(null);
const emit = defineEmits(['open-settings']);

const dropdownOpen = ref(false);
const dropdownRef = ref(null);

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
      dropdownOpen.value = false;
    }
  });
});

const openModelModal = (id) => {
  selectedModelId.value = id;
};

const confirmBulkDelete = async () => {
  if (confirm(`Are you sure you want to completely delete ${bulkStore.selectedCount} selected models and all their files?`)) {
    try {
      const selectedModels = bulkStore.getSelectedModels(models.models);
      for (const m of selectedModels) {
        await models.deleteModel(m.id, m.path);
      }
      bulkStore.clearSelection();
      bulkStore.toggleBulkMode();
    } catch (err) {
      console.error(err);
      alert('Failed to delete some models.');
    }
  }
};

onMounted(async () => {
  await settings.fetchSettings();
  
  // Set initial sort order from memory, fallback to global settings default
  const savedSort = localStorage.getItem('lora_manager_sortBy');
  if (savedSort) {
    models.sortBy = savedSort;
  } else if (settings.defaultSort) {
    models.sortBy = settings.defaultSort;
  }

  // Initialize safe mode based on global settings
  if (settings.safeModeOnReload) {
    models.safemode = settings.safeModeDefault;
  } else {
    const savedState = localStorage.getItem('safemodeState');
    if (savedState !== null) {
      models.safemode = savedState === 'true';
    } else {
      models.safemode = settings.safeModeDefault;
    }
  }

  // Watch and persist safe mode if user toggles it during the session
  watch(() => models.safemode, (newVal) => {
    localStorage.setItem('safemodeState', newVal.toString());
  });
  
  models.fetchModels();
});

// Watch for sort changes and persist to memory
watch(() => models.sortBy, (newSort) => {
  localStorage.setItem('lora_manager_sortBy', newSort);
});
</script>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.main-content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--color-bg-primary);
}

.controls-bar {
  padding: 15px 20px;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-container {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
}

.search-input {
  width: 100%;
  padding: 10px 80px 10px 40px;
  border-radius: 20px;
  border: 1px solid var(--color-border);
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
  font-size: 1em;
}

.search-actions {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
}

.clear-search-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1em;
}

.clear-search-btn:hover {
  color: #e74c3c;
}

.search-help {
  position: relative;
  display: flex;
  align-items: center;
}

.help-icon {
  color: var(--color-text-secondary);
  cursor: help;
  font-size: 1.1em;
}

.help-icon:hover {
  color: var(--color-text);
}

.help-popover {
  display: none;
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  width: 250px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 15px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  font-size: 0.9em;
}

.search-help:hover .help-popover {
  display: block;
}

.help-title {
  font-weight: bold;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 5px;
}

.help-popover ul {
  list-style-type: none;
  padding: 0;
  margin: 0 0 10px 0;
}

.help-popover li {
  margin-bottom: 5px;
}

.help-example {
  font-size: 0.85em;
  color: var(--color-text-secondary);
  background: var(--color-bg-tertiary);
  padding: 8px;
  border-radius: 4px;
}

.help-example code {
  color: #3498db;
}

.models-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  gap: 15px;
}

.error-state {
  color: #e74c3c;
}

/* Temporary Grid Styles for Placeholder */
.placeholder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.placeholder-card {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-standard);
}

.placeholder-card img {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
}

.placeholder-card .card-info {
  padding: 10px;
}

.placeholder-card h4 {
  margin: 0;
  font-size: 0.9em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bulk-toggle-btn.active {
  background-color: var(--color-btn-primary);
  color: white;
  border-color: var(--color-btn-primary);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.4);
}

.filter-controls {
  display: flex;
  gap: 10px;
}

.form-select {
  padding: 8px 12px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: var(--border-radius-sm);
  font-size: 0.9em;
  outline: none;
}

.form-select:focus {
  border-color: var(--color-btn-primary);
}

/* Custom Dropdown */
.custom-dropdown {
  position: relative;
  min-width: 180px;
  user-select: none;
}

.dropdown-header {
  padding: 8px 12px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: var(--border-radius-sm);
  font-size: 0.9em;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-header:hover {
  border-color: var(--color-btn-primary);
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 5px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  z-index: 100;
  max-height: 60vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.dropdown-item {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9em;
  color: var(--color-text);
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background-color: var(--color-bg-hover);
}

.dropdown-item input[type="checkbox"] {
  accent-color: var(--color-btn-primary);
  width: 16px;
  height: 16px;
}

/* Grouped View Styles */
.view-renderer {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.model-group-wrapper {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--color-border);
  position: sticky;
  top: -20px; /* Offset for container padding */
  background-color: var(--color-bg-primary);
  z-index: 10;
  padding-top: 10px;
}

.group-title {
  margin: 0;
  font-size: 1.4em;
  color: var(--color-text);
}

.group-count {
  background-color: var(--color-bg-secondary);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85em;
  color: var(--color-text-secondary);
}
</style>

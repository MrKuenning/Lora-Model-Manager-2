<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content bulk-modal">
      <div class="modal-header">
        <h2><i class="fas fa-arrows-alt"></i> Bulk Move ({{ selectedModels.length }} Models)</h2>
        <button class="close-btn" @click="emit('close')"><i class="fas fa-times"></i></button>
      </div>

      <div class="modal-body" v-if="loading">
        <div class="loading-spinner">Moving...</div>
      </div>

      <div class="modal-body" v-else>
        <div class="bulk-form">
          <div class="form-group">
            <label>Target Folder:</label>
            <div class="folder-list">
              <div 
                v-for="folder in availableFolders" 
                :key="folder" 
                class="folder-list-item"
                :class="{ selected: targetFolder === folder }"
                @click="targetFolder = folder"
              >
                <i class="fas fa-folder" v-if="folder !== ''"></i>
                <i class="fas fa-hdd" v-else></i>
                {{ folder === '' ? 'Root' : folder }}
              </div>
            </div>
            <small class="help-text">
              Target folders are automatically filtered to match the base model roots of your selected models. If your selection contains conflicting base models, all available folders are shown.
            </small>
          </div>
          
          <div class="models-preview-list mt-20">
            <h4>Models to Move:</h4>
            <ul>
              <li v-for="m in selectedModels" :key="m.id">
                <i class="fas fa-file-alt"></i> {{ m.name || m.filename }} 
                <span class="badge" v-if="m.baseModel || m.base_model || m.sdVersion">{{ m.baseModel || m.base_model || m.sdVersion }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="modal-footer" v-if="!loading">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn btn-success" @click="executeMove" :disabled="selectedModels.length === 0">
          <i class="fas fa-check"></i> Move {{ selectedModels.length }} Models
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useBulkStore } from '../../stores/bulk';
import { useModelsStore } from '../../stores/models';
import { useSettingsStore } from '../../stores/settings';
import { api } from '../../api/client';
import { useToast } from '../../composables/useToast';

const emit = defineEmits(['close']);
const bulkStore = useBulkStore();
const modelsStore = useModelsStore();
const settingsStore = useSettingsStore();
const toast = useToast();

const loading = ref(false);
const selectedModels = computed(() => bulkStore.getSelectedModels(modelsStore.models));
const targetFolder = ref('');

const availableFolders = computed(() => {
  // Find common root across all selected models
  const roots = settingsStore.modelTypeRoots || [];
  let commonRootPath = null;
  let hasConflict = false;
  
  if (selectedModels.value.length > 0) {
    for (const m of selectedModels.value) {
      const baseModel = m.baseModel || m.base_model || '';
      const matchedRoot = roots.find(r => r.baseModel && r.baseModel.toLowerCase() === baseModel.toLowerCase());
      const rootPath = matchedRoot ? matchedRoot.rootFolder : null;
      
      if (commonRootPath === null && !hasConflict) {
        commonRootPath = rootPath; // First model's root
      } else if (commonRootPath !== rootPath) {
        hasConflict = true;
      }
    }
  }
  
  let folderPaths = (modelsStore.folders || []).map(f => f.path);
  
  if (commonRootPath && !hasConflict) {
    folderPaths = folderPaths.filter(f => f === commonRootPath || f.startsWith(commonRootPath + '/') || f.startsWith(commonRootPath + '\\'));
    if (!folderPaths.includes(commonRootPath)) {
      folderPaths.unshift(commonRootPath);
    }
  } else {
    if (!folderPaths.includes('')) {
      folderPaths.unshift('');
    }
  }
  
  return folderPaths;
});

// Set default target
if (availableFolders.value.length > 0) {
  targetFolder.value = availableFolders.value[0];
}

const executeMove = async () => {
  if (targetFolder.value === null) return;
  
  loading.value = true;
  let successCount = 0;
  
  for (const model of selectedModels.value) {
    try {
      await api.moveModel(model.id, targetFolder.value);
      successCount++;
    } catch (err) {
      console.error(`Failed to move ${model.name}`, err);
    }
  }
  
  loading.value = false;
  
  if (successCount === selectedModels.value.length) {
    toast.showToast(`Successfully moved ${successCount} models.`, 'success');
  } else {
    toast.showToast(`Moved ${successCount} models. Failed to move ${selectedModels.value.length - successCount}.`, 'warning');
  }
  
  bulkStore.clearSelection();
  bulkStore.toggleBulkMode();
  modelsStore.fetchModels();
  emit('close');
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

.bulk-modal {
  width: 90%;
  max-width: 600px;
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
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

.close-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1.2em;
}

.close-btn:hover {
  color: var(--color-text);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: 70vh;
}

.modal-footer {
  padding: 15px 20px;
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-weight: 600;
  color: var(--color-text);
}

.form-control {
  padding: 10px 12px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: var(--border-radius-sm);
  font-size: 1em;
}

.models-preview-list {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  border-radius: 8px;
  padding: 10px;
}

.models-preview-list h4 {
  margin: 0 0 10px 0;
  color: var(--color-text);
}

.models-preview-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.models-preview-list li {
  padding: 6px 10px;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9em;
}

.models-preview-list li:last-child {
  border-bottom: none;
}

.badge {
  font-size: 0.75em;
  background-color: var(--color-btn-primary);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: auto;
}

.help-text {
  display: block;
  margin-top: 6px;
  color: var(--color-text-muted);
  font-size: 0.85em;
  line-height: 1.4;
}

.mt-20 { margin-top: 20px; }

.folder-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-sm);
}

.folder-list-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text);
  font-size: 0.95em;
  transition: background-color 0.2s;
}

.folder-list-item:last-child {
  border-bottom: none;
}

.folder-list-item:hover {
  background-color: var(--color-bg-hover, rgba(255,255,255,0.05));
}

.folder-list-item.selected {
  background-color: var(--color-btn-primary);
  color: white;
  font-weight: bold;
}
</style>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content bulk-modal">
      <div class="modal-header">
        <h2><i class="fas fa-font"></i> Bulk Rename ({{ selectedModels.length }} Models)</h2>
        <button class="close-btn" @click="emit('close')"><i class="fas fa-times"></i></button>
      </div>

      <div class="modal-body" v-if="loading">
        <div class="loading-spinner">Renaming...</div>
      </div>

      <div class="modal-body" v-else>
        <div class="help-text mb-20">
          The following list shows what the files will be renamed to based on your Recommended Formatting settings. Uncheck any models you wish to skip.
        </div>

        <div class="rename-table-container">
          <table class="rename-table">
            <thead>
              <tr>
                <th style="width: 40px; text-align: center;">
                  <input type="checkbox" :checked="allChecked" @change="toggleAll">
                </th>
                <th>Current Filename</th>
                <th>New Filename</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in renameItems" :key="item.model.id">
                <td style="text-align: center;">
                  <input type="checkbox" v-model="item.selected">
                </td>
                <td class="text-truncate" :title="item.oldName">{{ item.oldName }}</td>
                <td class="text-truncate" :title="item.newName">
                  <span v-if="item.oldName === item.newName" class="text-muted">No change</span>
                  <span v-else class="text-success">{{ item.newName }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="modal-footer" v-if="!loading">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn btn-success" @click="executeRename" :disabled="selectedToRenameCount === 0">
          <i class="fas fa-check"></i> Rename {{ selectedToRenameCount }} Models
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

const generateRecommendedFilename = (model) => {
  const baseModel = model.baseModel || model.base_model || '';
  const formats = settingsStore.filenameFormats || [];
  
  let matchingFormat = formats.find(f => f.baseModel && f.baseModel.toLowerCase() === baseModel.toLowerCase());
  if (!matchingFormat) {
    matchingFormat = formats.find(f => f.baseModel === 'Default');
  }
  
  let formatString = matchingFormat ? matchingFormat.format : '{modelname} {version}';
  
  let result = formatString;
  const name = model.name || '';
  const civitaiName = model.civitai_name || model.civitaiName || name;
  const version = model.version || model.model_version || '';
  const highLow = model.highLow || model.high_low || '';
  const category = model.category || '';
  const subcategory = model.subcategory || '';
  
  result = result.replace(/\{modelname\}/gi, name || civitaiName);
  result = result.replace(/\{civitainame\}/gi, civitaiName);
  result = result.replace(/\{version\}/gi, version);
  result = result.replace(/\{versionname\}/gi, version);
  result = result.replace(/\{highlow\}/gi, highLow);
  result = result.replace(/\{category\}/gi, category);
  result = result.replace(/\{subcategory\}/gi, subcategory);
  
  // Clean up
  result = result.replace(/\s+/g, ' ').trim();
  
  // Also run the "clean" logic
  let n = result;
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
  
  return n;
};

const renameItems = ref(selectedModels.value.map(model => {
  const filenameNoExt = model.filename ? model.filename.split('.').slice(0, -1).join('.') : '';
  const newName = generateRecommendedFilename(model);
  
  return {
    model: model,
    oldName: filenameNoExt,
    newName: newName,
    selected: filenameNoExt !== newName && newName.length > 0 // Auto-select if there's a valid change
  };
}));

const allChecked = computed(() => {
  if (renameItems.value.length === 0) return false;
  return renameItems.value.every(item => item.selected);
});

const selectedToRenameCount = computed(() => {
  return renameItems.value.filter(item => item.selected).length;
});

const toggleAll = (e) => {
  const checked = e.target.checked;
  renameItems.value.forEach(item => {
    item.selected = checked;
  });
};

const executeRename = async () => {
  const itemsToProcess = renameItems.value.filter(item => item.selected);
  if (itemsToProcess.length === 0) return;
  
  loading.value = true;
  let successCount = 0;
  
  for (const item of itemsToProcess) {
    try {
      await api.renameModel(item.model.id, item.newName);
      successCount++;
    } catch (err) {
      console.error(`Failed to rename ${item.model.name}`, err);
    }
  }
  
  loading.value = false;
  
  if (successCount === itemsToProcess.length) {
    toast.showToast(`Successfully renamed ${successCount} models.`, 'success');
  } else {
    toast.showToast(`Renamed ${successCount} models. Failed to rename ${itemsToProcess.length - successCount}.`, 'warning');
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
  max-width: 900px;
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

.rename-table-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.rename-table {
  width: 100%;
  border-collapse: collapse;
}

.rename-table th,
.rename-table td {
  padding: 10px;
  border-bottom: 1px solid var(--color-border-light);
  text-align: left;
}

.rename-table th {
  background-color: var(--color-bg-secondary);
  position: sticky;
  top: 0;
  z-index: 10;
}

.text-truncate {
  max-width: 350px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-success {
  color: #2ecc71;
  font-weight: 500;
}

.text-muted {
  color: var(--color-text-muted);
  font-style: italic;
}

.mb-20 { margin-bottom: 20px; }
</style>

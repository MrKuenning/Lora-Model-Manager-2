<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content bulk-modal">
      <div class="modal-header">
        <h2><i class="fas fa-layer-group"></i> Bulk Edit ({{ bulkStore.selectedCount }} Models)</h2>
        <button class="btn btn-icon" @click="emit('close')"><i class="fas fa-times"></i></button>
      </div>

      <div class="modal-body">
        <div class="info-alert">
          <i class="fas fa-info-circle"></i>
          Any fields left blank will remain unchanged. Fields with values will OVERWRITE existing metadata for ALL selected models.
        </div>

        <div class="bulk-form">
          <div class="form-row">
            <div class="form-group flex-1">
              <label>Category:</label>
              <input type="text" v-model="form.category" class="form-control" list="bulk-categories" placeholder="Leave blank to keep existing">
              <datalist id="bulk-categories">
                <option v-for="cat in uniqueCategories" :key="cat" :value="cat"></option>
              </datalist>
            </div>
            
            <div class="form-group flex-1">
              <label>Sub Category:</label>
              <input type="text" v-model="form.subcategory" class="form-control" list="bulk-subcategories" placeholder="Leave blank to keep existing">
              <datalist id="bulk-subcategories">
                <option v-for="sub in uniqueSubcategories" :key="sub" :value="sub"></option>
              </datalist>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group flex-1">
              <label>Base Model:</label>
              <input type="text" v-model="form.baseModel" class="form-control" list="bulk-basemodels" placeholder="Leave blank to keep existing">
              <datalist id="bulk-basemodels">
                <option v-for="base in uniqueBaseModels" :key="base" :value="base"></option>
              </datalist>
            </div>
            
            <div class="form-group flex-1">
              <label>SD Version:</label>
              <input type="text" v-model="form.sdVersion" class="form-control" list="bulk-sdversions" placeholder="Leave blank to keep existing">
              <datalist id="bulk-sdversions">
                <option v-for="sd in uniqueSdVersions" :key="sd" :value="sd"></option>
              </datalist>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group flex-1">
              <label>WAN High / Low:</label>
              <select v-model="form.highLow" class="form-control">
                <option value="">-- Do not change --</option>
                <option value="High">High</option>
                <option value="Low">Low</option>
                <option value="None">None</option>
              </select>
            </div>

            <div class="form-group flex-1">
              <label>NSFW:</label>
              <select v-model="form.nsfw" class="form-control">
                <option value="">-- Do not change --</option>
                <option value="true">True (NSFW)</option>
                <option value="false">False (Safe)</option>
              </select>
            </div>
          </div>
          
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn btn-primary" @click="applyChanges" :disabled="saving">
          <i class="fas fa-save" v-if="!saving"></i>
          <i class="fas fa-spinner fa-spin" v-else></i>
          Apply Bulk Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue';
import { useBulkStore } from '../../stores/bulk';
import { useModelsStore } from '../../stores/models';
import { api } from '../../api/client';
import { useToast } from '../../composables/useToast';

const emit = defineEmits(['close']);
const bulkStore = useBulkStore();
const modelsStore = useModelsStore();
const toast = useToast();

const saving = ref(false);

const form = reactive({
  category: '',
  subcategory: '',
  baseModel: '',
  sdVersion: '',
  highLow: '',
  nsfw: ''
});

// Computed properties for datalists (Combo boxes)
const uniqueCategories = computed(() => [...new Set(modelsStore.models.map(m => m.category).filter(Boolean))].sort());
const uniqueSubcategories = computed(() => [...new Set(modelsStore.models.map(m => m.subcategory).filter(Boolean))].sort());
const uniqueBaseModels = computed(() => [...new Set(modelsStore.models.map(m => m.baseModel || m.base_model).filter(Boolean))].sort());
const uniqueSdVersions = computed(() => [...new Set(modelsStore.models.map(m => m.sdVersion || m.sd_version).filter(Boolean))].sort());

const applyChanges = async () => {
  saving.value = true;
  let successCount = 0;
  let failCount = 0;

  const targetIds = Array.from(bulkStore.selectedModelIds);
  
  // Create change payload
  const changes = {};
  if (form.category) changes.category = form.category;
  if (form.subcategory) changes.subcategory = form.subcategory;
  if (form.baseModel) changes.baseModel = form.baseModel;
  if (form.sdVersion) changes.sdVersion = form.sdVersion;
  if (form.highLow) changes.highLow = form.highLow === 'None' ? '' : form.highLow;
  if (form.nsfw !== '') changes.nsfw = form.nsfw === 'true' ? "true" : "false";

  if (Object.keys(changes).length === 0) {
    saving.value = false;
    emit('close');
    return;
  }

  for (const id of targetIds) {
    try {
      const model = modelsStore.models.find(m => m.id === id);
      if (!model) continue;

      const newMeta = { ...model, ...changes };

      // Save metadata
      await api.saveModelJson(id, newMeta);

      successCount++;
    } catch (err) {
      console.error(`Failed to update ${id}`, err);
      failCount++;
    }
  }

  saving.value = false;
  toast.showToast(`Bulk update complete: ${successCount} succeeded, ${failCount} failed`, failCount > 0 ? 'warning' : 'success');
  
  if (successCount > 0) {
    modelsStore.fetchModels(); // Refresh view completely
    bulkStore.clearSelection();
    emit('close');
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

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: 70vh;
}

.info-alert {
  background-color: rgba(241, 196, 15, 0.1);
  color: #f39c12;
  border-left: 4px solid #f1c40f;
  padding: 12px 15px;
  margin-bottom: 20px;
  border-radius: 0 4px 4px 0;
  display: flex;
  gap: 10px;
  line-height: 1.4;
}

.info-alert i {
  margin-top: 2px;
}

.bulk-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.flex-1 {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.9em;
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

.modal-footer {
  padding: 15px 20px;
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}
</style>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content bulk-modal">
      <div class="modal-header">
        <h2><i class="fas fa-copy"></i> Find Duplicates</h2>
        <button class="close-btn" @click="emit('close')"><i class="fas fa-times"></i></button>
      </div>

      <div class="modal-body" v-if="loading">
        <div class="loading-spinner">Scanning all models for duplicate SHA256 hashes...</div>
      </div>

      <div class="modal-body" v-else>
        <div class="stats-row mb-20">
          <div class="stat-card">
            <div class="stat-value">{{ scanResult.totalScanned || 0 }}</div>
            <div class="stat-label">Total Scanned</div>
          </div>
          <div class="stat-card">
            <div class="stat-value text-warning">{{ scanResult.missingHash?.length || 0 }}</div>
            <div class="stat-label">Missing Hashes</div>
          </div>
          <div class="stat-card">
            <div class="stat-value text-danger">{{ scanResult.duplicateGroupCount || 0 }}</div>
            <div class="stat-label">Duplicate Groups</div>
          </div>
        </div>

        <div v-if="scanResult.duplicateGroupCount > 0">
          <h4>Duplicate Files Found</h4>
          <div class="duplicates-list">
            <div v-for="(group, idx) in scanResult.duplicates" :key="idx" class="duplicate-group">
              <div class="group-header">Group {{ idx + 1 }} ({{ group.length }} identical files)</div>
              <div class="duplicate-cards-container">
                <div v-for="file in group" :key="file" class="duplicate-card">
                  <div class="card-image" v-if="getModelInfo(file)">
                    <img :src="api.getAssetUrl(getModelInfo(file).previewUrl, modelsStore.getCacheBuster(file))" @error="$event.target.src = 'data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'100\' height=\'100\' viewBox=\'0 0 100 100\'><rect width=\'100%\' height=\'100%\' fill=\'%232a2a2a\'/><text x=\'50\' y=\'50\' font-family=\'Arial\' font-size=\'12\' fill=\'%23777\' text-anchor=\'middle\' dy=\'.3em\'>No Image</text></svg>'" />
                  </div>
                  
                  <div class="card-details" v-if="getModelInfo(file)">
                    <div class="card-title">{{ getModelInfo(file).name }}</div>
                    <div class="card-meta">
                      <span class="meta-item"><i class="fas fa-folder"></i> {{ formatFilePath(file) }}</span>
                      <span class="meta-item"><i class="fas fa-hdd"></i> {{ formatSize(getModelInfo(file).size) }}</span>
                    </div>
                  </div>
                  
                  <div class="card-details" v-else>
                    <div class="card-meta">
                      <span class="meta-item"><i class="fas fa-file"></i> {{ formatFilePath(file) }}</span>
                    </div>
                  </div>

                  <div class="card-actions">
                    <button class="btn btn-danger btn-block" @click="deleteDuplicate(file)">
                      <i class="fas fa-trash"></i> Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center mt-20">
          <i class="fas fa-check-circle fa-3x text-success mb-10"></i>
          <h4>No duplicates found!</h4>
          <p class="text-muted">All scanned models with hashes are unique.</p>
        </div>
        
        <div class="help-text mt-20">
          Note: This scan compares the SHA256 hashes inside your model JSON files. Models missing a hash ({{ scanResult.missingHash?.length || 0 }}) cannot be compared. Use the Civitai Scanner to generate missing hashes.
        </div>
      </div>

      <div class="modal-footer" v-if="!loading">
        <button class="btn btn-secondary" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useModelsStore } from '../../stores/models';
import { api } from '../../api/client';
import { useToast } from '../../composables/useToast';

const emit = defineEmits(['close']);
const modelsStore = useModelsStore();
const toast = useToast();

const loading = ref(true);
const scanResult = ref({});

onMounted(async () => {
  try {
    const result = await api.civitaiFindDuplicates(modelsStore.currentLocation);
    if (result.status === 'success') {
      scanResult.value = result;
    } else {
      toast.showToast('Failed to scan for duplicates', 'error');
    }
  } catch (err) {
    console.error(err);
    toast.showToast('Error connecting to server', 'error');
  } finally {
    loading.value = false;
  }
});

const formatFilePath = (path) => {
  try {
    if (!path) return '';
    const normalized = String(path).replace(/\\/g, '/');
    const parts = normalized.split('/');
    if (parts.length > 2) {
      return parts.slice(-3).join('/');
    }
    return normalized;
  } catch (e) {
    return String(path);
  }
};

const getModelInfo = (path) => {
  try {
    if (!path) return null;
    const normalizedPath = String(path).replace(/\\/g, '/');
    return modelsStore.models.find(m => m.path && String(m.path).replace(/\\/g, '/') === normalizedPath);
  } catch (e) {
    return null;
  }
};

const formatSize = (bytes) => {
  try {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  } catch (e) {
    return '0 B';
  }
};

const deleteDuplicate = async (filePath) => {
  if (!confirm(`Are you sure you want to delete this duplicate file?\n\n${formatFilePath(filePath)}`)) {
    return;
  }
  
  try {
    // Backend allows 'unknown' as id if we provide modelPath in payload
    await api.deleteModel('unknown', filePath);
    toast.showToast('Model deleted successfully', 'success');
    
    // Remove from UI
    for (let i = 0; i < scanResult.value.duplicates.length; i++) {
      const group = scanResult.value.duplicates[i];
      const index = group.indexOf(filePath);
      if (index !== -1) {
        group.splice(index, 1);
        break;
      }
    }
    
    // Filter out groups that no longer have duplicates (length <= 1)
    scanResult.value.duplicates = scanResult.value.duplicates.filter(g => g.length > 1);
    scanResult.value.duplicateGroupCount = scanResult.value.duplicates.length;
    
    // Remove from store
    const normalizedPath = filePath.replace(/\\/g, '/');
    modelsStore.models = modelsStore.models.filter(m => !m.path || m.path.replace(/\\/g, '/') !== normalizedPath);
    
  } catch (err) {
    console.error(err);
    toast.showToast(err.response?.data?.message || 'Failed to delete model', 'error');
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
  max-width: 800px;
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

.stats-row {
  display: flex;
  gap: 15px;
}

.stat-card {
  flex: 1;
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
}

.stat-value {
  font-size: 1.8em;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9em;
  color: var(--color-text-muted);
}

.duplicates-list {
  max-height: 350px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.duplicate-group {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-danger);
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.group-header {
  background-color: rgba(231, 76, 60, 0.1);
  padding: 8px 12px;
  font-weight: bold;
  border-bottom: 1px solid var(--color-border-light);
}

.duplicate-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.duplicate-group li {
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border-light);
  font-size: 0.9em;
  word-break: break-all;
}

.duplicate-group li:last-child {
  border-bottom: none;
}

.duplicate-group li i {
  color: var(--color-text-muted);
  margin-right: 8px;
}

.text-danger { color: #e74c3c; }
.text-warning { color: #f1c40f; }
.text-success { color: #2ecc71; }
.mb-20 { margin-bottom: 20px; }
.mb-10 { margin-bottom: 10px; }
.mt-20 { margin-top: 20px; }

.help-text {
  color: var(--color-text-muted);
  font-size: 0.85em;
  font-style: italic;
  line-height: 1.4;
}

.duplicate-cards-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 15px;
}

.duplicate-card {
  display: flex;
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  align-items: center;
}

.card-image {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  border-right: 1px solid var(--color-border);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-details {
  flex: 1;
  padding: 10px 15px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  overflow: hidden;
}

.card-title {
  font-weight: 600;
  font-size: 1.05em;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-item {
  font-size: 0.85em;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta-item i {
  width: 16px;
  text-align: center;
  color: var(--color-text-muted);
}

.card-actions {
  padding: 15px;
}

.btn-block {
  width: 100%;
  padding: 8px 15px;
}
</style>

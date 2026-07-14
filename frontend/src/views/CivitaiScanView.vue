<template>
  <div class="civitai-scan-view">
    <AppHeader />
    
    <div class="scan-container">
      <div class="scan-header-wrapper">
        <div class="back-btn-container">
          <button class="btn btn-secondary" @click="$router.push('/')">
            <i class="fas fa-arrow-left"></i> Back to Manager
          </button>
        </div>
        <div class="scan-header">
          <h2><i class="fas fa-radar"></i> Metadata Import</h2>
          <p class="subtitle">Automatically find and download missing metadata for your local models.</p>
        </div>
        <div></div> <!-- Empty div for grid balance -->
      </div>
      
      <div class="scan-main-layout">
        <!-- Left Column: Controls -->
        <div class="scan-controls-col">
          <div class="scan-stats">
            <div class="stat-box">
              <div class="stat-value">{{ totalModels }}</div>
              <div class="stat-label">Total Models</div>
            </div>
            <div class="stat-box">
              <div class="stat-value" :class="{'text-danger': missingMetadata > 0}">{{ missingMetadata }}</div>
              <div class="stat-label">Missing MetaData</div>
            </div>
            <div class="stat-box">
              <div class="stat-value" :class="{'text-danger': missingThumbnails > 0}">{{ missingThumbnails }}</div>
              <div class="stat-label">Missing Thumbnails</div>
            </div>
            <div class="stat-box">
              <div class="stat-value" :class="{'text-danger': missingHashes > 0}">{{ missingHashes }}</div>
              <div class="stat-label">Missing Hashes</div>
            </div>
          </div>
          
          <div class="scan-actions" v-if="!isScanning && !(scanComplete && failedModels.length > 0)">
            <div class="action-group all-in-one">
              <h3>All-in-One Scan</h3>
              <p>Perform all steps: Generate hashes, Fetch missing data and Download missing thumbnails.</p>
              <button class="btn btn-primary btn-large" @click="runAllInOne">
                <i class="fas fa-bolt"></i> Run All-in-One Scan
              </button>
            </div>
            


            
            <div class="action-columns">
              <div class="action-col">
                <h3>1. Scrape Metadata</h3>
                <p>Fetch model info from Civitai or CivArchive using file hashes.</p>
                <div class="btn-row">
                  <button class="btn btn-secondary" @click="fetchMissingData('civitai')"><i class="fas fa-cloud-download-alt"></i> Fetch missing metadata</button>
                </div>
              </div>
              
              <div class="action-col">
                <h3>2. Download Thumbnails</h3>
                <p>Download preview images from Civitai. Also fixes naming for compatibility.</p>
                <div class="btn-row">
                  <button class="btn btn-secondary" @click="getMissingThumbnails"><i class="fas fa-image"></i> Get Missing</button>
                  <button class="btn btn-secondary" @click="getAllThumbnails"><i class="fas fa-images"></i> Get All</button>
                </div>
              </div>

              <div class="action-col">
                <h3>3. Import from Downloads</h3>
                <p>Move models from Download Directory to Sorting Directory.</p>
                <button class="btn btn-secondary" @click="sortDownloadedModels"><i class="fas fa-exchange-alt"></i> Move Files</button>
              </div>

              <div class="action-col">
                <h3>4. Generate Hashes</h3>
                <p>Generate SHA256 file hashes for duplicate detection and Civitai lookups.</p>
                <div class="btn-row">
                  <button class="btn btn-secondary" @click="generateMissingHashes"><i class="fas fa-hashtag"></i> Generate Missing</button>
                  <button class="btn btn-secondary" @click="regenerateAllHashes"><i class="fas fa-sync-alt"></i> Regenerate All</button>
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
          <div class="log-section" :style="scanComplete && failedModels.length > 0 ? 'height: 300px;' : ''">
            <div class="log-container" ref="logContainer">
              <div v-for="(log, idx) in logs" :key="idx" class="log-entry" :class="log.type">
                <span class="timestamp">[{{ log.time }}]</span>
                <span class="message">{{ log.message }}</span>
              </div>
              <div v-if="logs.length === 0" class="empty-log">
                Ready to scan.
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

// Stats Computed Properties
const totalModels = computed(() => modelsStore.models.length);
const getMissingMetadataModels = () => modelsStore.models.filter(m => !m.civitaiUrl && !m.civitai_url);
const getMissingThumbnailModels = () => modelsStore.models.filter(m => !m.previewUrl || m.previewUrl.includes('placeholder'));
const getMissingHashModels = () => modelsStore.models.filter(m => !m.sha256);

const missingMetadata = computed(() => getMissingMetadataModels().length);
const missingThumbnails = computed(() => getMissingThumbnailModels().length);
const missingHashes = computed(() => getMissingHashModels().length);

const progressPercentage = computed(() => {
  if (currentQueueLength.value === 0) return 0;
  return Math.round((currentIndex.value / currentQueueLength.value) * 100);
});

onMounted(() => {
  if (modelsStore.models.length === 0) {
    modelsStore.fetchModels();
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
      addLog(`ERROR: ${task.actionName} failed for ${task.model.filename}.`, 'error');
      
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
      addLog(`SUCCESS: Fetched metadata for ${m.filename}`, 'success');
    }
  }));
  runScanQueue(tasks);
};

const getMissingThumbnails = () => {
  const targets = getMissingThumbnailModels();
  const skipNsfw = settingsStore.scanSettings?.skipNsfwPreviews !== false;
  const maxSize = settingsStore.scanSettings?.downloadMaxSize === true;
  
  const tasks = targets.map(model => ({
    model,
    actionName: 'Download Thumbnail',
    actionFn: async (m) => {
      const res = await api.civitaiDownloadPreview(m.path, skipNsfw, maxSize);
      if (res && res.status === 'error') throw new Error(res.message);
      if (res && res.status === 'skipped') throw new Error(res.message);
      addLog(`SUCCESS: Downloaded thumbnail for ${m.filename}`, 'success');
    }
  }));
  runScanQueue(tasks);
};

const getAllThumbnails = () => {
  const targets = modelsStore.models;
  const skipNsfw = settingsStore.scanSettings?.skipNsfwPreviews !== false;
  const maxSize = settingsStore.scanSettings?.downloadMaxSize === true;
  
  const tasks = targets.map(model => ({
    model,
    actionName: 'Download Thumbnail',
    actionFn: async (m) => {
      const res = await api.civitaiDownloadPreview(m.path, skipNsfw, maxSize);
      if (res && res.status === 'error') throw new Error(res.message);
      if (res && res.status === 'skipped') throw new Error(res.message);
      addLog(`SUCCESS: Downloaded thumbnail for ${m.filename}`, 'success');
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
      if (res && res.status === 'error') throw new Error(res.message);
      addLog(`SUCCESS: Generated hash for ${m.filename}`, 'success');
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
      if (res && res.status === 'error') throw new Error(res.message);
      addLog(`SUCCESS: Regenerated hash for ${m.filename}`, 'success');
    }
  }));
  runScanQueue(tasks);
};

const runAllInOne = () => {
  // Build Tasks for Fetch Missing Metadata
  const metadataTargets = getMissingMetadataModels();
  const tasks = metadataTargets.map(model => ({
    model,
    actionName: 'Fetch Metadata',
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
      addLog(`SUCCESS: Fetched metadata for ${m.filename}`, 'success');
    }
  }));
  
  // Build Tasks for Download Missing Thumbnails
  const thumbTargets = getMissingThumbnailModels();
  const skipNsfw = settingsStore.scanSettings?.skipNsfwPreviews !== false;
  const maxSize = settingsStore.scanSettings?.downloadMaxSize === true;
  
  thumbTargets.forEach(model => {
    tasks.push({
      model,
      actionName: 'Download Thumbnail',
      actionFn: async (m) => {
        const res = await api.civitaiDownloadPreview(m.path, skipNsfw, maxSize);
        if (res && res.status === 'error') throw new Error(res.message);
        if (res && res.status === 'skipped') throw new Error(res.message);
        addLog(`SUCCESS: Downloaded thumbnail for ${m.filename}`, 'success');
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
  background-color: var(--color-bg-primary);
  overflow-y: auto;
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
  align-items: start;
}

.back-btn-container {
  justify-self: start;
  margin-top: 5px;
}

.scan-header {
  text-align: center;
}

.scan-header h2 {
  font-size: 2.5em;
  margin: 0 0 10px 0;
  color: var(--color-btn-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 1.2em;
}

.mt-10 { margin-top: 10px; }

.scan-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
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
  height: 100%;
}

.scan-actions {
  background: var(--bg-dark);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-box {
  flex: 1;
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-md);
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 1px solid var(--color-border);
}

.stat-value {
  font-size: 2em;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 5px;
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.text-success { color: #2ecc71; }
.text-danger { color: #e74c3c; }

.action-group {
  background-color: var(--color-bg-secondary);
  padding: 30px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  text-align: center;
}

.action-group h3 {
  margin-top: 0;
  color: var(--color-text);
}

.action-columns {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.action-col {
  flex: 1;
  background-color: var(--color-bg-secondary);
  padding: 15px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.action-col h3 {
  margin-top: 0;
  color: var(--color-text);
}

.action-col p {
  color: var(--color-text-secondary);
  flex-grow: 1;
  margin-bottom: 20px;
}

.btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: auto;
}

.btn-row .btn {
  flex: 1;
  min-width: 120px;
}

.active-scan-box {
  background-color: var(--color-bg-secondary);
  padding: 40px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  text-align: center;
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
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: var(--color-bg-secondary);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.progress-fill {
  height: 100%;
  background: var(--color-btn-primary);
  transition: width 0.3s ease;
}
.progress-text {
  text-align: center;
  margin-top: 10px;
  color: #ccc;
}

/* Resolution Section */
.log-section {
  background: var(--color-bg-secondary);
  padding: 20px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  height: 700px;
  display: flex;
  flex-direction: column;
}

.failed-models-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.failed-model-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1a1a1a;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #333;
}
.failed-model-name {
  font-weight: bold;
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
  width: 300px;
}

.log-section h3 {
  margin: 0;
  color: var(--color-text);
}

.log-container {
  flex: 1;
  background-color: #111;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  padding: 15px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 0.9em;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.log-entry {
  line-height: 1.4;
}
.log-entry .timestamp {
  color: #888;
  margin-right: 10px;
}
.log-entry.info .message { color: #ccc; }
.log-entry.success .message { color: #2ecc71; }
.log-entry.error .message { color: #e74c3c; }
.log-entry.warning .message { color: #f1c40f; }

.empty-log {
  color: #666;
  text-align: center;
  padding: 40px;
}
</style>

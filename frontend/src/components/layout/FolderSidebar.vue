<template>
  <aside class="sidebar" :class="[models.sidebarSize, { collapsed: isCollapsed }]" v-if="!models.sidebarHidden">
    <div class="sidebar-header">
      <h3 v-if="!isCollapsed">Folders</h3>
      <div class="sidebar-controls" v-if="!isCollapsed">
        <button class="btn btn-icon btn-small" @click="models.isTreeMode = !models.isTreeMode" :title="models.isTreeMode ? 'Switch to Flat View' : 'Switch to Tree View'">
          <i class="fas" :class="models.isTreeMode ? 'fa-list-ul' : 'fa-sitemap'"></i>
        </button>
        <button class="btn btn-icon btn-small" @click="toggleSize" :title="models.sidebarSize === 'comfy' ? 'Compact Size' : 'Comfy Size'">
          <i class="fas" :class="models.sidebarSize === 'comfy' ? 'fa-compress-alt' : 'fa-expand-alt'"></i>
        </button>
        <button class="btn btn-icon btn-small" @click="models.sidebarHidden = true" title="Hide Sidebar">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="sidebar-controls" v-else>
        <button class="btn btn-icon btn-small" @click="isCollapsed = !isCollapsed" title="Expand Sidebar">
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
    
    <div v-if="!isCollapsed" class="sidebar-content">
      <div class="sidebar-options">
        <template v-if="!models.isTreeMode">
          <label class="opt-label"><input type="checkbox" v-model="models.flatHideRoot"> Hide Root</label>
          <label class="opt-label"><input type="checkbox" v-model="models.flatHidePath"> Hide Path</label>
        </template>
        <template v-else>
          <button class="btn btn-secondary btn-tiny" @click="collapseTo(2)">1st Layer</button>
          <button class="btn btn-secondary btn-tiny" @click="collapseTo(3)">2nd Layer</button>
          <button class="btn btn-secondary btn-tiny" @click="expandAll">Expand All</button>
        </template>
      </div>

      <!-- FLAT VIEW -->
      <ul v-if="!models.isTreeMode" class="folder-list flat-view">
        <li 
          v-for="folder in flatFolders" 
          :key="folder.path"
          :class="{ active: models.currentFolder === folder.path }"
          @click="models.currentFolder = folder.path"
        >
          <i class="fas" :class="folder.path === '' ? 'fa-home' : (models.currentFolder === folder.path ? 'fa-folder-open' : 'fa-folder')"></i>
          
          <span class="folder-name-container">
            <span v-if="folder.path === ''" class="folder-name bold">Root</span>
            <template v-else>
              <span class="folder-path dim" v-if="!models.flatHidePath && folder.parentPath">{{ folder.parentPath }}/</span>
              <span class="folder-name bold">{{ folder.name }}</span>
            </template>
          </span>

          <!-- ACTIONS IN MANAGE MODE -->
          <span class="folder-actions" v-if="isManagingFolders" @click.stop>
            <button 
              class="action-btn btn-add" 
              @click.stop="openNewModal(folder.path)" 
              title="Add subfolder"
            >
              <i class="fas fa-plus"></i>
            </button>
            <button 
              v-if="folder.path !== ''" 
              class="action-btn btn-rename" 
              @click.stop="openRenameModal(folder.path)" 
              title="Rename folder"
            >
              <i class="fas fa-pencil-alt"></i>
            </button>
            <button 
              v-if="folder.path !== ''" 
              class="action-btn btn-delete" 
              :class="{ disabled: isFolderNonEmpty(folder.path) }" 
              @click.stop="openDeleteModal(folder.path)" 
              :title="isFolderNonEmpty(folder.path) ? 'Cannot delete: folder contains models/subfolders' : 'Delete empty folder'"
            >
              <i class="fas fa-times"></i>
            </button>
          </span>
          <span class="folder-count" v-else>{{ models.folderCounts.immediate[folder.path] || 0 }}</span>
        </li>
      </ul>
      
      <!-- TREE VIEW -->
      <ul v-else class="folder-list tree-view">
        <FolderTreeNode 
          :node="treeData" 
          :expandedState="expandedNodes"
          @toggle="toggleNode"
          @select="models.currentFolder = $event"
        />
      </ul>
    </div>

    <!-- SIDEBAR FOOTER (MANAGE FOLDERS TOGGLE) -->
    <div v-if="!isCollapsed" class="sidebar-footer">
      <button 
        class="btn-manage-folders" 
        :class="{ active: isManagingFolders }"
        @click="isManagingFolders = !isManagingFolders"
        :title="isManagingFolders ? 'Exit Folder Manager' : 'Manage Folders'"
      >
        <i class="fas" :class="isManagingFolders ? 'fa-check' : 'fa-folder-cog'"></i>
        <span>{{ isManagingFolders ? 'Done Managing' : 'Manage Folders' }}</span>
      </button>
    </div>

    <!-- FOLDER ACTION MODALS -->
    <div v-if="activeModal" class="folder-modal-overlay" @click.self="closeModal">
      <div class="folder-modal-card">
        <div class="folder-modal-header">
          <h4>
            <i class="fas" :class="{
              'fa-folder-plus': activeModal === 'new',
              'fa-pencil-alt': activeModal === 'rename',
              'fa-trash-alt': activeModal === 'delete'
            }"></i>
            <span v-if="activeModal === 'new'">Create New Folder</span>
            <span v-else-if="activeModal === 'rename'">Rename Folder</span>
            <span v-else-if="activeModal === 'delete'">Delete Empty Folder</span>
          </h4>
          <button class="close-btn" @click="closeModal"><i class="fas fa-times"></i></button>
        </div>

        <div class="folder-modal-body">
          <template v-if="activeModal === 'new'">
            <p class="modal-instruction">
              Create a new folder inside: <strong>{{ modalTargetFolder === '' ? 'Root' : modalTargetFolder }}</strong>
            </p>
            <input 
              type="text" 
              v-model="modalInputName" 
              class="form-control" 
              placeholder="New folder name" 
              @keydown.enter.prevent="confirmModalAction"
              @keydown.esc="closeModal"
              ref="modalInputRef"
              :disabled="isSubmitting"
            />
          </template>

          <template v-else-if="activeModal === 'rename'">
            <p class="modal-instruction">
              Rename folder: <strong>{{ modalTargetFolder }}</strong>
            </p>
            <input 
              type="text" 
              v-model="modalInputName" 
              class="form-control" 
              placeholder="New name" 
              @keydown.enter.prevent="confirmModalAction"
              @keydown.esc="closeModal"
              ref="modalInputRef"
              :disabled="isSubmitting"
            />
            <p class="modal-hint">
              <i class="fas fa-info-circle"></i> This will rename the folder on disk and update all models within it.
            </p>
          </template>

          <template v-else-if="activeModal === 'delete'">
            <p class="modal-instruction">
              Are you sure you want to delete this folder?
            </p>
            <p class="delete-folder-target"><code>{{ modalTargetFolder }}</code></p>
            
            <div v-if="isCheckingFolder" class="checking-box">
              <i class="fas fa-spinner fa-spin"></i> Checking folder contents on disk...
            </div>
            
            <template v-else-if="folderCheckResult">
              <!-- Case 1: Contains model files -->
              <div v-if="folderCheckResult.modelCount > 0" class="danger-box">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                  <strong>Folder contains {{ folderCheckResult.modelCount }} model file(s)</strong>
                  <div class="file-samples">e.g. {{ folderCheckResult.modelFilesSample.join(', ') }}</div>
                  <span>Models must be moved or deleted before this folder can be removed.</span>
                </div>
              </div>
              
              <!-- Case 2: Contains other files (lset, json, configs, etc.) but 0 models -->
              <div v-else-if="folderCheckResult.otherFileCount > 0" class="warning-box">
                <i class="fas fa-exclamation-circle"></i>
                <div>
                  <strong>No models found, but contains {{ folderCheckResult.otherFileCount }} other file(s) on disk</strong>
                  <div class="file-samples">e.g. {{ folderCheckResult.otherFilesSample.join(', ') }}</div>
                  <span>Only completely empty folders can be removed to prevent accidental data loss.</span>
                </div>
              </div>
              
              <!-- Case 3: Completely empty -->
              <div v-else-if="folderCheckResult.isEmpty" class="safety-box">
                <i class="fas fa-check-circle"></i>
                <span>Folder is completely empty on disk (0 models, 0 other files). Safe to delete.</span>
              </div>

              <!-- Case 4: Error during check -->
              <div v-else class="danger-box">
                <i class="fas fa-times-circle"></i>
                <span>{{ folderCheckResult.message || 'Unable to verify folder contents.' }}</span>
              </div>
            </template>

            <!-- Fallback if check hasn't run yet -->
            <div v-else-if="isFolderNonEmpty(modalTargetFolder)" class="danger-box">
              <i class="fas fa-exclamation-triangle"></i> This folder contains models or subfolders and cannot be deleted.
            </div>
          </template>
        </div>

        <div class="folder-modal-footer">
          <button class="btn btn-secondary" @click="closeModal" :disabled="isSubmitting">Cancel</button>
          
          <button 
            v-if="activeModal === 'new'" 
            class="btn btn-success" 
            @click="confirmModalAction" 
            :disabled="!modalInputName.trim() || isSubmitting"
          >
            <i class="fas fa-check" v-if="!isSubmitting"></i>
            <i class="fas fa-spinner fa-spin" v-else></i> Create
          </button>
          
          <button 
            v-else-if="activeModal === 'rename'" 
            class="btn btn-primary" 
            @click="confirmModalAction" 
            :disabled="!modalInputName.trim() || isSubmitting"
          >
            <i class="fas fa-check" v-if="!isSubmitting"></i>
            <i class="fas fa-spinner fa-spin" v-else></i> Rename
          </button>

          <button 
            v-else-if="activeModal === 'delete'" 
            class="btn btn-danger" 
            @click="confirmModalAction" 
            :disabled="isCheckingFolder || !folderCheckResult || !folderCheckResult.isEmpty || isSubmitting"
            :title="(!folderCheckResult || !folderCheckResult.isEmpty) ? 'Folder is not empty' : 'Delete empty folder'"
          >
            <i class="fas fa-trash-alt" v-if="!isSubmitting"></i>
            <i class="fas fa-spinner fa-spin" v-else></i> Delete Folder
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, provide, nextTick } from 'vue';
import { useModelsStore } from '../../stores/models';
import { useSettingsStore } from '../../stores/settings';
import { api } from '../../api/client';
import { useToast } from '../../composables/useToast';
import FolderTreeNode from './FolderTreeNode.vue';

const models = useModelsStore();
const settings = useSettingsStore();
const toast = useToast();
const isCollapsed = ref(false);

const expandedNodes = ref({});

// Folder Management state
const isManagingFolders = ref(false);
const activeModal = ref(null); // 'new' | 'rename' | 'delete' | null
const modalTargetFolder = ref('');
const modalInputName = ref('');
const isSubmitting = ref(false);
const modalInputRef = ref(null);

const isFolderNonEmpty = (folderPath) => {
  if (!folderPath) return true; // Root cannot be deleted
  const norm = folderPath.replace(/\\/g, '/').toLowerCase();
  
  // 1. Check if any model in the library is inside this folder or its subfolders
  const hasModels = models.models.some(m => {
    const f = (m.folder || '').replace(/\\/g, '/').toLowerCase();
    return f === norm || f.startsWith(norm + '/');
  });
  if (hasModels) return true;
  
  // 2. Check if any subfolder exists
  const hasSubfolders = models.folders.some(f => {
    const p = (f.path || '').replace(/\\/g, '/').toLowerCase();
    return p !== norm && p.startsWith(norm + '/');
  });
  return hasSubfolders;
};

const folderCheckResult = ref(null);
const isCheckingFolder = ref(false);

const openNewModal = async (parentPath = '') => {
  modalTargetFolder.value = parentPath;
  modalInputName.value = '';
  activeModal.value = 'new';
  await nextTick();
  if (modalInputRef.value) modalInputRef.value.focus();
};

const openRenameModal = async (folderPath) => {
  if (!folderPath) return;
  modalTargetFolder.value = folderPath;
  modalInputName.value = folderPath.split(/[\/\\]/).pop() || '';
  activeModal.value = 'rename';
  await nextTick();
  if (modalInputRef.value) modalInputRef.value.focus();
};

const openDeleteModal = async (folderPath) => {
  if (!folderPath) return;
  modalTargetFolder.value = folderPath;
  folderCheckResult.value = null;
  activeModal.value = 'delete';
  isCheckingFolder.value = true;
  try {
    const res = await api.checkFolder(folderPath, models.currentLocation);
    folderCheckResult.value = res;
  } catch (err) {
    folderCheckResult.value = {
      status: 'error',
      isEmpty: false,
      message: err?.response?.data?.message || 'Failed to inspect folder on disk'
    };
  } finally {
    isCheckingFolder.value = false;
  }
};

const closeModal = () => {
  activeModal.value = null;
  modalTargetFolder.value = '';
  modalInputName.value = '';
  folderCheckResult.value = null;
  isCheckingFolder.value = false;
};

const confirmModalAction = async () => {
  if (isSubmitting.value) return;
  
  if (activeModal.value === 'new') {
    const name = modalInputName.value.trim();
    if (!name) return;
    
    isSubmitting.value = true;
    try {
      const res = await api.createFolder(modalTargetFolder.value, name, models.currentLocation);
      if (res && res.status === 'success') {
        toast.showToast(res.message || `Folder "${name}" created.`, 'success');
        await models.fetchFolders();
        models.currentFolder = res.path;
        if (modalTargetFolder.value) {
          expandedNodes.value[modalTargetFolder.value] = true;
        }
        closeModal();
      } else {
        toast.showToast(res?.message || 'Failed to create folder', 'error');
      }
    } catch (err) {
      toast.showToast(err?.response?.data?.message || err.message || 'Failed to create folder', 'error');
    } finally {
      isSubmitting.value = false;
    }
  } else if (activeModal.value === 'rename') {
    const newName = modalInputName.value.trim();
    if (!newName) return;
    
    isSubmitting.value = true;
    try {
      const res = await api.renameFolder(modalTargetFolder.value, newName, models.currentLocation);
      if (res && res.status === 'success') {
        toast.showToast(res.message || `Folder renamed to "${newName}".`, 'success');
        
        if (models.currentFolder === modalTargetFolder.value) {
          models.currentFolder = res.newPath;
        } else if (models.currentFolder.startsWith(modalTargetFolder.value + '/')) {
          models.currentFolder = res.newPath + models.currentFolder.slice(modalTargetFolder.value.length);
        }
        
        await models.fetchFolders();
        await models.fetchModels();
        closeModal();
      } else {
        toast.showToast(res?.message || 'Failed to rename folder', 'error');
      }
    } catch (err) {
      toast.showToast(err?.response?.data?.message || err.message || 'Failed to rename folder', 'error');
    } finally {
      isSubmitting.value = false;
    }
  } else if (activeModal.value === 'delete') {
    isSubmitting.value = true;
    try {
      const res = await api.deleteFolder(modalTargetFolder.value, models.currentLocation);
      if (res && res.status === 'success') {
        toast.showToast(res.message || `Folder deleted.`, 'success');
        
        if (models.currentFolder === modalTargetFolder.value || models.currentFolder.startsWith(modalTargetFolder.value + '/')) {
          models.currentFolder = '';
        }
        
        await models.fetchFolders();
        closeModal();
      } else {
        toast.showToast(res?.message || 'Failed to delete folder', 'error');
      }
    } catch (err) {
      toast.showToast(err?.response?.data?.message || err.message || 'Failed to delete folder', 'error');
    } finally {
      isSubmitting.value = false;
    }
  }
};

provide('folderManager', {
  isManagingFolders,
  openNewModal,
  openRenameModal,
  openDeleteModal,
  isFolderNonEmpty
});

const toggleSize = () => {
  models.sidebarSize = models.sidebarSize === 'comfy' ? 'compact' : 'comfy';
};

// Tree Mode Logic
const treeData = computed(() => {
  const root = { path: '', name: 'Root', children: [] };
  const nodeMap = { '': root };

  let sortedFolders = [...models.folders].filter(f => f.path !== '').sort((a, b) => a.path.localeCompare(b.path));

  if (settings.filterFoldersWithBaseModel && models.baseModelFilter && models.baseModelFilter.length > 0) {
    sortedFolders = sortedFolders.filter(f => models.folderCounts.nested[f.path] > 0);
  }

  for (const f of sortedFolders) {
    const parts = f.path.split(/[\/\\]/).filter(p => p);
    let currentPath = '';
    let parentPath = '';
    
    for (let i = 0; i < parts.length; i++) {
      parentPath = currentPath;
      currentPath = currentPath ? `${currentPath}/${parts[i]}` : parts[i];
      
      if (!nodeMap[currentPath]) {
        const newNode = { path: currentPath, name: parts[i], children: [] };
        nodeMap[currentPath] = newNode;
        if (nodeMap[parentPath]) {
          nodeMap[parentPath].children.push(newNode);
        }
      }
    }
  }

  return root;
});

const toggleNode = (path) => {
  expandedNodes.value[path] = !expandedNodes.value[path];
};

const setExpandedDepth = (node, currentDepth, targetDepth) => {
  if (currentDepth < targetDepth) {
    expandedNodes.value[node.path] = true;
  } else {
    expandedNodes.value[node.path] = false;
  }
  if (node.children) {
    for (const child of node.children) {
      setExpandedDepth(child, currentDepth + 1, targetDepth);
    }
  }
};

const collapseTo = (layer) => {
  setExpandedDepth(treeData.value, 0, layer);
};

const expandAll = () => {
  setExpandedDepth(treeData.value, 0, 999);
};

onMounted(() => {
  collapseTo(2);
});

// Flat Mode Logic
const flatFolders = computed(() => {
  let sourceFolders = models.folders;
  if (settings.filterFoldersWithBaseModel && models.baseModelFilter && models.baseModelFilter.length > 0) {
    sourceFolders = sourceFolders.filter(f => f.path === '' || models.folderCounts.immediate[f.path] > 0);
  }

  return sourceFolders.map(f => {
    if (f.path === '') return { ...f, parentPath: '', name: 'Root' };
    
    let pathParts = f.path.split(/[\/\\]/).filter(p => p);
    let name = pathParts.pop();
    let parentPath = pathParts.join('/');
    
    if (models.flatHideRoot && pathParts.length > 0) {
      pathParts.shift();
      parentPath = pathParts.join('/');
    }
    
    return {
      path: f.path,
      parentPath: parentPath,
      name: name
    };
  });
});
</script>

<style scoped>
.sidebar {
  width: 280px;
  background-color: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow-y: hidden;
  overflow-x: hidden;
}

.sidebar.collapsed {
  width: 50px;
}

.sidebar-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
  flex-shrink: 0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.1em;
  color: var(--color-text);
  white-space: nowrap;
}

.sidebar-controls {
  display: flex;
  gap: 5px;
}

.sidebar-controls .btn-icon {
  padding: 4px;
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
}

.sidebar-controls .btn-icon:hover {
  color: var(--color-text);
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow: hidden;
}

.sidebar-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  background-color: var(--color-bg-tertiary);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.opt-label {
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.btn-tiny {
  padding: 2px 6px;
  font-size: 0.8em;
  border-radius: 4px;
}

.folder-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex-grow: 1;
}

.flat-view li {
  padding: 8px 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text-secondary);
  transition: background-color 0.2s, color 0.2s;
  white-space: nowrap;
}

.flat-view li:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
}

.flat-view li.active {
  background-color: var(--color-bg-tertiary);
  color: var(--color-btn-primary);
  border-left: 3px solid var(--color-btn-primary);
  padding-left: 7px;
}

.folder-name-container {
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: baseline;
}

.folder-path.dim {
  color: var(--color-text-muted);
  font-size: 0.9em;
  opacity: 0.7;
}

.folder-name.bold {
  font-weight: 500;
  color: var(--color-text);
}

.folder-count {
  background-color: var(--color-bg-primary);
  color: var(--color-text-muted);
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 0.8em;
  font-weight: normal;
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.sidebar.compact .flat-view li {
  padding-top: 4px;
  padding-bottom: 4px;
  font-size: 0.9em;
}

.sidebar.comfy .flat-view li {
  padding-top: 8px;
  padding-bottom: 8px;
  font-size: 1.05em;
}

.tree-view {
  padding: 5px 0;
}

/* Sidebar Footer & Manage Button */
.sidebar-footer {
  padding: 10px;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
  flex-shrink: 0;
}

.btn-manage-folders {
  width: 100%;
  padding: 8px 12px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  color: var(--color-text);
  font-size: 0.9em;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-manage-folders:hover {
  background-color: var(--color-bg-hover);
  border-color: var(--color-text-muted);
}

.btn-manage-folders.active {
  background-color: var(--color-btn-primary);
  border-color: var(--color-btn-primary);
  color: #fff;
}

/* Action Buttons for Folder Manager */
.folder-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.action-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  width: 22px;
  height: 22px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.75em;
  color: var(--color-text-muted);
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
  border-color: var(--color-text-muted);
}

.action-btn.btn-add:hover {
  color: #4ade80;
  border-color: #4ade80;
}

.action-btn.btn-rename:hover {
  color: #3b82f6;
  border-color: #3b82f6;
}

.action-btn.btn-delete:hover {
  color: #ef4444;
  border-color: #ef4444;
}

.action-btn.btn-delete.disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

/* Modal Overlay & Card */
.folder-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
}

.folder-modal-card {
  width: 90%;
  max-width: 440px;
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg, 8px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.folder-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.folder-modal-header h4 {
  margin: 0;
  font-size: 1.05em;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text);
}

.folder-modal-header .close-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1.1em;
}

.folder-modal-header .close-btn:hover {
  color: var(--color-text);
}

.folder-modal-body {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-instruction {
  margin: 0;
  font-size: 0.95em;
  color: var(--color-text);
}

.modal-instruction strong {
  color: var(--color-btn-primary);
}

.modal-hint {
  margin: 0;
  font-size: 0.85em;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.delete-folder-target {
  margin: 0;
}

.delete-folder-target code {
  display: block;
  padding: 8px 10px;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
  color: var(--color-text);
  word-break: break-all;
  font-weight: bold;
}

.danger-box {
  padding: 10px 12px;
  background-color: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 6px;
  color: #f87171;
  font-size: 0.85em;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  line-height: 1.4;
}

.warning-box {
  padding: 10px 12px;
  background-color: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 6px;
  color: #fbbf24;
  font-size: 0.85em;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  line-height: 1.4;
}

.checking-box {
  padding: 10px 12px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text-muted);
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-samples {
  font-family: monospace;
  font-size: 0.9em;
  opacity: 0.9;
  margin: 4px 0;
  word-break: break-all;
}

.safety-box {
  padding: 10px 12px;
  background-color: rgba(74, 222, 128, 0.15);
  border: 1px solid rgba(74, 222, 128, 0.4);
  border-radius: 6px;
  color: #4ade80;
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.folder-modal-footer {
  padding: 12px 18px;
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

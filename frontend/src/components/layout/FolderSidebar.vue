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
          <span class="folder-count">{{ models.folderCounts.immediate[folder.path] || 0 }}</span>
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
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useModelsStore } from '../../stores/models';
import { useSettingsStore } from '../../stores/settings';
import FolderTreeNode from './FolderTreeNode.vue';

const models = useModelsStore();
const settings = useSettingsStore();
const isCollapsed = ref(false);

const expandedNodes = ref({});

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
</style>

<template>
  <li 
    class="tree-node"
    :class="{ active: models.currentFolder === node.path }"
  >
    <div class="node-content" :style="{ paddingLeft: `${depth * 15 + 10}px` }" @click.stop="selectNode">
      <span class="toggle-icon" @click.stop="toggleNode" v-if="node.children && node.children.length > 0">
        <i class="fas" :class="isExpanded ? 'fa-caret-down' : 'fa-caret-right'"></i>
      </span>
      <span class="toggle-icon placeholder" v-else></span>
      
      <i class="fas" :class="node.path === '' ? 'fa-home' : (models.currentFolder === node.path ? 'fa-folder-open' : 'fa-folder')"></i>
      
      <span class="folder-name">{{ node.name || 'Root' }}</span>
      <span class="folder-count">{{ models.folderCounts.nested[node.path] || 0 }}</span>
    </div>
    
    <ul v-if="isExpanded && node.children && node.children.length > 0" class="folder-list nested">
      <FolderTreeNode 
        v-for="child in node.children" 
        :key="child.path" 
        :node="child" 
        :depth="depth + 1"
        :expandedState="expandedState"
        @toggle="$emit('toggle', $event)"
        @select="$emit('select', $event)"
      />
    </ul>
  </li>
</template>

<script setup>
import { computed } from 'vue';
import { useModelsStore } from '../../stores/models';

const props = defineProps({
  node: Object,
  depth: { type: Number, default: 0 },
  expandedState: Object
});

const emit = defineEmits(['toggle', 'select']);
const models = useModelsStore();

const isExpanded = computed(() => !!props.expandedState[props.node.path]);

const toggleNode = () => {
  emit('toggle', props.node.path);
};

const selectNode = () => {
  emit('select', props.node.path);
};
</script>

<script>
export default {
  name: 'FolderTreeNode'
}
</script>

<style scoped>
.tree-node {
  list-style: none;
}

.node-content {
  padding: 6px 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary);
  transition: background-color 0.2s, color 0.2s;
  white-space: nowrap;
}

.node-content:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
}

.tree-node.active > .node-content {
  background-color: var(--color-bg-tertiary);
  color: var(--color-btn-primary);
  font-weight: bold;
  border-left: 3px solid var(--color-btn-primary);
  /* Adjust padding to account for the border */
  padding-left: calc(v-bind('`${depth * 15 + 10}px`') - 3px);
}

.toggle-icon {
  width: 16px;
  text-align: center;
  cursor: pointer;
}

.toggle-icon.placeholder {
  cursor: default;
}

.folder-name {
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-count {
  background-color: var(--color-bg-primary);
  color: var(--color-text-muted);
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 0.8em;
  font-weight: normal;
  border: 1px solid var(--color-border);
}

.nested {
  padding: 0;
  margin: 0;
  list-style: none;
}

/* Inherit size from sidebar */
.sidebar.compact .node-content {
  padding-top: 4px;
  padding-bottom: 4px;
  font-size: 0.9em;
}
.sidebar.comfy .node-content {
  padding-top: 8px;
  padding-bottom: 8px;
  font-size: 1.05em;
}
</style>

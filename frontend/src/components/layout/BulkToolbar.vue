<template>
  <div class="bulk-toolbar" v-if="bulkStore.isBulkMode" :class="{ 'has-selection': bulkStore.hasSelection }">
    <div class="toolbar-content">
      <div class="selection-info">
        <span class="count">{{ bulkStore.selectedCount }}</span> models selected
      </div>
      
      <div class="toolbar-actions">
        <button class="btn btn-secondary" @click="bulkStore.clearSelection()">
          Clear Selection
        </button>
        <button class="btn btn-primary" :disabled="!bulkStore.hasSelection" @click="emit('open-move')">
          <i class="fas fa-arrows-alt"></i> Move
        </button>
        <button class="btn btn-primary" :disabled="!bulkStore.hasSelection" @click="emit('open-edit')">
          <i class="fas fa-edit"></i> Edit
        </button>
        <button class="btn btn-primary" :disabled="!bulkStore.hasSelection" @click="emit('open-rename')">
          <i class="fas fa-font"></i> Rename
        </button>
        <button class="btn btn-danger" :disabled="!bulkStore.hasSelection" @click="emit('trigger-delete')">
          <i class="fas fa-trash"></i> Delete
        </button>
        <button class="btn btn-secondary" @click="bulkStore.toggleBulkMode()">
          Cancel Bulk Mode
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBulkStore } from '../../stores/bulk';

const emit = defineEmits(['open-edit', 'open-move', 'open-rename', 'trigger-delete']);
const bulkStore = useBulkStore();
</script>

<style scoped>
.bulk-toolbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: var(--color-bg-secondary);
  border-top: 2px solid var(--color-btn-primary);
  padding: 15px 30px;
  z-index: 900;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.5);
  transform: translateY(100%);
  animation: slideUp 0.3s forwards;
}

@keyframes slideUp {
  to { transform: translateY(0); }
}

.toolbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.selection-info {
  font-size: 1.1em;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 10px;
}

.count {
  background-color: var(--color-btn-primary);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: bold;
}

.toolbar-actions {
  display: flex;
  gap: 15px;
}

.has-selection {
  background: linear-gradient(rgba(52, 152, 219, 0.15), rgba(52, 152, 219, 0.15)), var(--color-bg-secondary);
}
</style>

<template>
  <div class="grouped-grid-view">
    <div v-if="Object.keys(groupedModels).length === 0" class="empty-state">
      <i class="fas fa-search fa-3x"></i>
      <p>No models found for current filters.</p>
    </div>

    <div 
      v-else 
      v-for="(groupList, groupName) in groupedModels" 
      :key="groupName" 
      class="model-group"
    >
      <div class="group-header">
        <h3 class="group-title">
          <i class="fas fa-folder-open" v-if="modelsStore.groupBy === 'folder'"></i>
          <i class="fas fa-layer-group" v-else-if="modelsStore.groupBy === 'baseModel'"></i>
          <i class="fas fa-tags" v-else-if="modelsStore.groupBy === 'category'"></i>
          <i class="fas fa-list" v-else></i>
          {{ groupName || 'Uncategorized' }}
        </h3>
        <span class="group-count">{{ groupList.length }} {{ groupList.length === 1 ? 'model' : 'models' }}</span>
        
        <div class="group-actions" v-if="bulkStore.isBulkMode">
          <button class="btn btn-secondary btn-small" @click="selectAllInGroup(groupList)">
            Select All in Group
          </button>
        </div>
      </div>
      
      <div :class="['models-grid', 'size-' + settings.gridCard.cardSize]">
        <ModelCard 
          v-for="model in groupList" 
          :key="model.id" 
          :model="model" 
          @click="emit('open-model', model.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useModelsStore } from '../../stores/models';
import { useBulkStore } from '../../stores/bulk';
import { useSettingsStore } from '../../stores/settings';
import ModelCard from './ModelCard.vue';

const emit = defineEmits(['open-model']);
const modelsStore = useModelsStore();
const bulkStore = useBulkStore();
const settings = useSettingsStore();

// groupedModels is passed from the store getter
const groupedModels = computed(() => modelsStore.groupedModels);

const selectAllInGroup = (groupList) => {
  bulkStore.selectAll(groupList);
};
</script>

<style scoped>
.grouped-grid-view {
  display: flex;
  flex-direction: column;
  gap: 40px;
  padding-bottom: 40px;
}

.model-group {
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
  top: 0;
  background-color: var(--color-bg-primary);
  z-index: 10;
  padding-top: 10px;
}

.group-title {
  margin: 0;
  font-size: 1.4em;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-title i {
  color: var(--color-text-secondary);
}

.group-count {
  background-color: var(--color-bg-secondary);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85em;
  color: var(--color-text-secondary);
}

.group-actions {
  margin-left: auto;
}

.models-grid {
  display: grid;
  gap: 20px;
  width: 100%;
}

.models-grid.size-small {
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
}

.models-grid.size-medium {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.models-grid.size-large {
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--color-text-secondary);
  gap: 15px;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  border: 1px dashed var(--color-border);
}
</style>

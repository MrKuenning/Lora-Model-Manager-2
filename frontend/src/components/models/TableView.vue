<template>
  <div class="table-view">
    <table class="data-table">
      <thead>
        <tr>
          <th class="col-checkbox" v-if="bulkStore.isBulkMode">
            <input type="checkbox" @click="toggleAll" :checked="allSelected" :indeterminate.prop="someSelected && !allSelected">
          </th>
          <template v-for="col in activeColumns" :key="col">
            <th v-if="col === 'thumbnail'" class="col-thumb">Preview</th>
            <th v-else-if="col === 'modelName' || col === 'name'" class="col-name sortable" @click="setSort('name')">
              Name <i class="fas" :class="getSortIcon('name')"></i>
            </th>
            <th v-else-if="col === 'civitaiName'" class="sortable" @click="setSort('civitaiName')">
              Civitai Name <i class="fas" :class="getSortIcon('civitaiName')"></i>
            </th>
            <th v-else-if="col === 'baseModel'" class="sortable" @click="setSort('baseModel')">
              Base <i class="fas" :class="getSortIcon('baseModel')"></i>
            </th>
            <th v-else-if="col === 'category'" class="sortable" @click="setSort('category')">
              Category <i class="fas" :class="getSortIcon('category')"></i>
            </th>
            <th v-else-if="col === 'size'" class="sortable" @click="setSort('size')">
              Size <i class="fas" :class="getSortIcon('size')"></i>
            </th>
            <th v-else-if="col === 'date'" class="sortable" @click="setSort('date')">
              Date <i class="fas" :class="getSortIcon('date')"></i>
            </th>
            <th v-else-if="col === 'filename'" class="sortable" @click="setSort('filename')">
              Filename <i class="fas" :class="getSortIcon('filename')"></i>
            </th>
            <th v-else class="sortable" @click="setSort(col)">
              {{ formatColumnName(col) }} <i class="fas" :class="getSortIcon(col)"></i>
            </th>
          </template>
          <th class="col-actions">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="model in modelsList" 
          :key="model.id"
          :class="{ selected: bulkStore.isSelected(model.id) }"
          @click="handleClick(model.id)"
        >
          <td class="col-checkbox" v-if="bulkStore.isBulkMode">
            <input type="checkbox" :checked="bulkStore.isSelected(model.id)" @click.stop="bulkStore.toggleSelection(model.id)">
          </td>
          
          <template v-for="col in activeColumns" :key="col">
            <td v-if="col === 'thumbnail'" class="col-thumb">
              <div class="thumb-container" v-if="settings.visibleColumns.thumbnail">
                  <img 
                  :src="api.getAssetUrl(model.previewUrl, modelsStore.getCacheBuster(model.path))" 
                  :alt="model.name || model.filename"
                  :class="{ blurred: isNsfw(model) && !revealed.has(model.id) && settings.nsfwBlurOverlay }"
                  @click.stop="toggleReveal(model.id)"
                  @error="handleImageError($event, model)"
                >
                <div v-if="isNsfw(model)" class="nsfw-badge" title="NSFW Content">!</div>
              </div>
            </td>
            
            <td v-else-if="col === 'modelName' || col === 'name'" class="col-name font-bold" :title="model.name">{{ model.name }}</td>
            <td v-else-if="col === 'civitaiName'" :title="model.civitai_name || model.civitaiName">{{ model.civitai_name || model.civitaiName || '-' }}</td>
            <td v-else-if="col === 'baseModel'">
              <span class="badge" v-if="model.base_model || model.baseModel">{{ model.base_model || model.baseModel }}</span>
            </td>
            <td v-else-if="col === 'category'">
              <span class="badge category" v-if="model.category">{{ model.category }}</span>
            </td>
            <td v-else-if="col === 'size'">{{ formatBytes(model.size) }}</td>
            <td v-else-if="col === 'date'">{{ formatDate(model.date_modified || model.dateModified) }}</td>
            <td v-else-if="col === 'filename'" class="text-truncate" :title="model.filename">{{ getFilenameNoExt(model.filename) }}</td>
            <td v-else class="text-truncate" :title="getMappedValue(model, col)">
              {{ getMappedValue(model, col) || '-' }}
            </td>
          </template>
          
          <td class="col-actions">
            <button class="btn btn-icon btn-small" @click.stop="emit('open-model', model.id)" title="View Details">
              <i class="fas fa-info-circle"></i>
            </button>
            <a 
              v-if="model.civitaiUrl || model.civitai_url"
              :href="model.civitaiUrl || model.civitai_url"
              target="_blank"
              class="btn btn-icon btn-small"
              @click.stop
              title="Open in Civitai"
            >
              <img :src="'/assets/civitai-logo.png'" alt="C" class="civitai-icon" @error="$event.target.outerHTML = '<i class=\'fas fa-external-link-alt\'></i>'" />
            </a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { api } from '../../api/client';
import { useModelsStore } from '../../stores/models';
import { useSettingsStore } from '../../stores/settings';
import { useBulkStore } from '../../stores/bulk';

const props = defineProps({
  modelsList: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['open-model']);

const modelsStore = useModelsStore();
const settings = useSettingsStore();
const bulkStore = useBulkStore();

const revealed = ref(new Set());

const activeColumns = computed(() => {
  const defaultOrder = ['thumbnail', 'name', 'civitaiName', 'baseModel', 'category', 'size', 'date', 'filename'];
  const order = Array.isArray(settings.columnOrder) && settings.columnOrder.length > 0 ? settings.columnOrder : defaultOrder;
  return order.filter(col => settings.visibleColumns[col] !== false);
});

const formatColumnName = (key) => {
  const result = key.replace(/([A-Z])/g, " $1");
  return result.charAt(0).toUpperCase() + result.slice(1);
};

const isNsfw = (model) => String(model.nsfw).toLowerCase() === 'true';

const toggleReveal = (id) => {
  if (revealed.value.has(id)) {
    revealed.value.delete(id);
  } else {
    revealed.value.add(id);
  }
};

const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (timestamp) => {
  if (!timestamp) return '-';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString();
};

const getFilenameNoExt = (filename) => {
  if (!filename) return '';
  const parts = filename.split('.');
  if (parts.length > 1) {
    parts.pop();
    return parts.join('.');
  }
  return filename;
};

const getMappedValue = (model, col) => {
  if (model[col] !== undefined && model[col] !== null) return model[col];
  
  const map = {
    authorsWords: 'activation_text',
    creator: 'creator',
    authorName: 'creator',
    description: 'description',
    examplePrompt: 'example_prompt',
    folder: 'folder',
    highLow: 'high_low',
    modelVersion: 'model_version',
    negativeWords: 'negative_text',
    notes: 'notes',
    nsfw: 'nsfw',
    path: 'path',
    positiveWords: 'example_prompt',
    sdVersion: 'sd_version',
    subcategory: 'subcategory',
    tags: 'tags',
    url: 'civitai_url'
  };

  const key = map[col] || col;
  return model[key] !== undefined && model[key] !== null ? model[key] : '';
};

const setSort = (column) => {
  let currentSort = modelsStore.sortBy;
  let newSort = `${column}-asc`;
  
  if (currentSort === `${column}-asc`) {
    newSort = `${column}-desc`;
  }
  
  modelsStore.sortBy = newSort;
};

const getSortIcon = (column) => {
  if (modelsStore.sortBy === `${column}-asc`) return 'fa-sort-up';
  if (modelsStore.sortBy === `${column}-desc`) return 'fa-sort-down';
  return 'fa-sort';
};

const handleClick = (id) => {
  if (bulkStore.isBulkMode) {
    bulkStore.toggleSelection(id);
  } else {
    emit('open-model', id);
  }
};

const allSelected = computed(() => {
  if (props.modelsList.length === 0) return false;
  return props.modelsList.every(m => bulkStore.isSelected(m.id));
});

const someSelected = computed(() => {
  return props.modelsList.some(m => bulkStore.isSelected(m.id));
});

const toggleAll = (e) => {
  if (e.target.checked) {
    bulkStore.selectAll(props.modelsList);
  } else {
    bulkStore.clearSelection();
  }
};

const handleImageError = (e, model) => {
  if (model.previewUrl) {
    e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100%" height="100%" fill="%232a2a2a"/><text x="50" y="50" font-family="Arial" font-size="12" fill="%23777" text-anchor="middle" dy=".3em">No Image</text></svg>';
  }
};
</script>

<style scoped>
.table-view {
  width: 100%;
  overflow-x: auto;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-standard);
  margin-bottom: 40px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th, 
.data-table td {
  padding: 12px 15px;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-weight: 600;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
}

.data-table tbody tr {
  transition: background-color 0.2s;
}

.data-table tbody tr:hover {
  background-color: var(--color-bg-hover);
}

.data-table tbody tr.selected {
  background-color: rgba(52, 152, 219, 0.1);
}

.col-checkbox {
  width: 40px;
  text-align: center;
}

.col-thumb {
  width: 80px;
}

.thumb-container {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  background-color: var(--color-bg-primary);
}

.thumb-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 0.3s;
}

.thumb-container img.blurred {
  filter: blur(10px) brightness(0.7);
  cursor: pointer;
}

.nsfw-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: #e74c3c;
  color: white;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
}

.col-name {
  min-width: 200px;
  max-width: 300px;
}

.font-bold {
  font-weight: 600;
  color: var(--color-text);
}

.text-truncate {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge {
  background-color: var(--color-bg-primary);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85em;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  display: inline-block;
  white-space: nowrap;
}

.badge.category {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
  border-color: rgba(46, 204, 113, 0.2);
}

.col-actions {
  width: 100px;
  text-align: right;
  white-space: nowrap;
}

.col-actions .btn {
  margin-left: 5px;
}

.civitai-icon {
  width: 14px;
  height: 14px;
  object-fit: contain;
}
</style>

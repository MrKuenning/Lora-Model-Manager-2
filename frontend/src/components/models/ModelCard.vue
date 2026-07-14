<template>
  <div 
    class="model-card" 
    :class="{ 
      selected: bulkStore.isSelected(model.id),
      'has-nsfw': isNsfw
    }"
    @click="handleClick"
  >
    <div class="card-image-container">
      <!-- NSFW Overlay -->
      <div v-if="isNsfw && settings.nsfwBlurOverlay" class="nsfw-overlay" @click.stop="toggleNsfwReveal">
        <i class="fas fa-eye-slash fa-2x"></i>
        <span>NSFW Content</span>
        <small>(Click to reveal)</small>
      </div>

      <div class="model-image-wrapper">
        <img 
        :src="api.getAssetUrl(model.previewUrl, modelsStore.getCacheBuster(model.path))" 
        :alt="model.name || model.filename"
        class="card-image"
        :class="{ blurred: isNsfw && !nsfwRevealed && settings.nsfwBlurOverlay }"
        loading="lazy"
        @error="handleImageError"
      >
      </div>
      
      <!-- SafeMode Badge -->
      <div v-if="isNsfw && settings.gridCard.showNsfwBadge" class="card-badge badge-nsfw">NSFW</div>

      <!-- Bulk Select Checkbox -->
      <div 
        class="bulk-checkbox"
        :class="{ checked: bulkStore.isSelected(model.id) }"
        @click.stop="bulkStore.toggleSelection(model.id)"
      >
        <i class="fas" :class="bulkStore.isSelected(model.id) ? 'fa-check-square' : 'fa-square'"></i>
      </div>

      <!-- Info Overlay -->
      <div class="info-overlay" v-if="settings.gridCard.showInfoButton">
        <button class="btn btn-icon" @click.stop="emit('open-model', model.id)" title="View Model Details">
          <i class="fas fa-info-circle"></i>
        </button>
      </div>
    </div>

    <div class="card-content">
      <h3 class="card-title" :title="settings.gridCard.titleDisplay === 'fileName' ? model.filename : model.name">{{ settings.gridCard.titleDisplay === 'fileName' ? getFilenameNoExt(model.filename) : model.name }}</h3>
      
      <div class="card-meta">
        <span class="meta-tag" v-if="model.baseModel && settings.gridCard.showBaseModel" :title="'Base Model: ' + model.baseModel">
          <i class="fas fa-cube"></i> {{ model.baseModel }}
        </span>
        <span class="meta-tag" v-if="model.category && settings.gridCard.showCategory" :title="'Category: ' + model.category">
          <i class="fas fa-folder"></i> {{ model.category }}
        </span>
        <span class="meta-tag" v-if="(model.highLow || model.high_low) && settings.gridCard.showHighLow" :title="'High/Low: ' + (model.highLow || model.high_low)">
          <i class="fas fa-layer-group"></i> {{ model.highLow || model.high_low }}
        </span>
        <span class="meta-tag" v-if="model.folder && settings.gridCard.showFolder" :title="'Folder: ' + model.folder">
          <i class="fas fa-folder-open"></i> {{ model.folder }}
        </span>
      </div>

      <!-- Quick action buttons -->
      <div class="card-actions" v-if="!bulkStore.isBulkMode && settings.gridCard.showActions">
        <button v-if="settings.gridCard.showCopyTriggerWords" class="btn btn-small btn-secondary" @click.stop="copyActivationText" title="Copy Activation Text">
          <i class="fas fa-magic"></i>
        </button>
        <button v-if="settings.gridCard.showCopyTriggerWords" class="btn btn-small btn-secondary" @click.stop="copyExamplePrompt" title="Copy Example Prompt">
          <i class="fas fa-comment-dots"></i>
        </button>
        <a 
          v-if="(model.civitai_url || model.civitaiUrl) && settings.gridCard.showUrlButton" 
          :href="model.civitai_url || model.civitaiUrl" 
          target="_blank" 
          class="btn btn-small btn-secondary civitai-link"
          @click.stop
          title="Open in Civitai"
        >
          <img :src="'/assets/civitai-logo.png'" alt="C" class="civitai-icon" />
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { api } from '../../api/client';
import { useBulkStore } from '../../stores/bulk';
import { useSettingsStore } from '../../stores/settings';
import { useToast } from '../../composables/useToast';
import { useModelsStore } from '../../stores/models';

const props = defineProps({
  model: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['open-model']);
const bulkStore = useBulkStore();
const settings = useSettingsStore();
const modelsStore = useModelsStore();

const getFilenameNoExt = (filename) => {
  if (!filename) return '';
  const parts = filename.split('.');
  if (parts.length > 1) {
    parts.pop();
    return parts.join('.');
  }
  return filename;
};
const toast = useToast();

const nsfwRevealed = ref(false);

const isNsfw = computed(() => {
  return String(props.model.nsfw).toLowerCase() === 'true';
});

const toggleNsfwReveal = () => {
  nsfwRevealed.value = !nsfwRevealed.value;
};

const handleImageError = (e) => {
  if (props.model.previewUrl) {
    // Fallback to a base64 SVG placeholder that will never fail to load
    e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100%" height="100%" fill="%232a2a2a"/><text x="50" y="50" font-family="Arial" font-size="12" fill="%23777" text-anchor="middle" dy=".3em">No Image</text></svg>';
  }
};

const handleClick = () => {
  if (bulkStore.isBulkMode) {
    bulkStore.toggleSelection(props.model.id);
  } else {
    emit('open-model', props.model.id);
  }
};

const copyActivationText = () => {
  const text = props.model.activation_text || props.model.activationText || '';
  if (!text) {
    toast.showToast('No activation text found', 'warning');
    return;
  }
  navigator.clipboard.writeText(text).then(() => {
    toast.showToast('Activation text copied to clipboard', 'success');
  }).catch(err => {
    toast.showToast('Failed to copy', 'error');
    console.error(err);
  });
};

const copyExamplePrompt = () => {
  const text = props.model.example_prompt || props.model.examplePrompt || props.model.example_prompt_2 || '';
  if (!text) {
    toast.showToast('No example prompt found', 'warning');
    return;
  }
  navigator.clipboard.writeText(text).then(() => {
    toast.showToast('Example prompt copied to clipboard', 'success');
  }).catch(err => {
    toast.showToast('Failed to copy', 'error');
    console.error(err);
  });
};

</script>

<style scoped>
.model-card {
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-standard);
  transition: var(--transition-standard);
  display: flex;
  flex-direction: column;
  position: relative;
  cursor: pointer;
  border: 2px solid transparent;
}

.model-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-hover);
  border-color: var(--color-border);
}

.model-card.selected {
  border-color: var(--color-btn-primary);
  box-shadow: 0 0 0 2px var(--color-btn-primary), var(--shadow-hover);
}

.card-image-container {
  position: relative;
  width: 100%;
  padding-top: 150%; /* 2:3 aspect ratio */
  background-color: var(--color-bg-image);
  overflow: hidden;
}

.card-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: filter 0.3s ease;
}

.card-image.blurred {
  filter: blur(20px) brightness(0.7);
}

.nsfw-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2;
  color: #fff;
  background-color: rgba(0, 0, 0, 0.4);
  cursor: pointer;
  gap: 10px;
}

.nsfw-overlay:hover {
  background-color: rgba(0, 0, 0, 0.6);
}

.card-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75em;
  font-weight: bold;
  z-index: 3;
}

.badge-nsfw {
  background-color: rgba(231, 76, 60, 0.9);
  color: white;
}

.bulk-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 4;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.5em;
  background: rgba(0,0,0,0.3);
  border-radius: 4px;
  padding: 2px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.model-card:hover .bulk-checkbox,
.bulk-checkbox.checked {
  opacity: 1;
}

.bulk-checkbox.checked {
  color: var(--color-btn-primary);
}

.info-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 10px;
  background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%);
  display: flex;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 3;
}

.model-card:hover .info-overlay {
  opacity: 1;
}

.card-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 1em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text);
}

.card-meta {
  display: flex;
  gap: 8px;
  font-size: 0.8em;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.meta-tag {
  background-color: var(--color-bg-tertiary);
  padding: 3px 8px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 5px;
  margin-top: auto;
  border-top: 1px solid var(--color-border);
  padding-top: 10px;
}

.btn-small {
  padding: 4px 8px;
  font-size: 0.9em;
  flex: 1;
}

.civitai-link {
  flex: 0 0 auto;
  padding: 4px;
}

.civitai-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}
</style>

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
      
      <!-- Badges -->
      <div class="card-badges">
        <!-- NSFW Badge -->
        <template v-if="isNsfw && settings.gridCard?.showNsfwBadge !== false">
          <div 
            v-if="settings.gridCard?.badgeStyle === 'truncated'" 
            class="icon-badge badge-nsfw" 
            title="NSFW Content"
          >
            <i class="fas fa-ban"></i>
          </div>
          <div v-else class="card-badge badge-nsfw" title="NSFW Content">NSFW</div>
        </template>

        <!-- Tested Badge -->
        <template v-if="isTested && settings.gridCard?.showTestedBadge !== false">
          <div 
            v-if="settings.gridCard?.badgeStyle === 'truncated'" 
            class="icon-badge badge-tested" 
            title="Tested Model"
          >
            <i class="fas fa-check"></i>
          </div>
          <div v-else class="card-badge badge-tested" title="Tested Model">
            <i class="fas fa-check"></i> Tested
          </div>
        </template>

        <!-- Slider Badge -->
        <template v-if="isSlider && settings.gridCard?.showSliderBadge !== false">
          <div 
            v-if="settings.gridCard?.badgeStyle === 'truncated'" 
            class="icon-badge badge-slider" 
            :title="'Slider (' + sliderRangeText + ')'"
          >
            <i class="fas fa-arrows-alt-h"></i>
          </div>
          <div 
            v-else 
            class="card-badge badge-slider" 
            :title="'Slider Range: ' + sliderRangeText"
          >
            Slider
          </div>
        </template>
      </div>

      <!-- Bulk Select Checkbox -->
      <div 
        class="bulk-checkbox"
        :class="{ checked: bulkStore.isSelected(model.id) }"
        @click.stop="bulkStore.toggleSelection(model.id)"
      >
        <i class="fas" :class="bulkStore.isSelected(model.id) ? 'fa-check-square' : 'fa-square'"></i>
      </div>

      <!-- Image Action Bar Overlay (when actionsPosition === 'overlay') -->
      <div 
        class="image-actions-overlay" 
        v-if="!bulkStore.isBulkMode && settings.gridCard?.showActions && settings.gridCard?.actionsPosition === 'overlay'"
        @click.stop
      >
        <button 
          v-if="settings.gridCard?.showCopyTriggerWords" 
          class="btn-overlay-action" 
          @click.stop="copyActivationText" 
          title="Copy Activation Text"
        >
          <i class="fas fa-magic"></i>
        </button>
        <button 
          v-if="settings.gridCard?.showCopyTriggerWords" 
          class="btn-overlay-action" 
          @click.stop="copyExamplePrompt" 
          title="Copy Example Prompt"
        >
          <i class="fas fa-comment-dots"></i>
        </button>
        <a 
          v-if="(model.civitai_url || model.civitaiUrl) && settings.gridCard?.showUrlButton" 
          :href="model.civitai_url || model.civitaiUrl" 
          target="_blank" 
          class="btn-overlay-action"
          @click.stop
          title="Open in Civitai"
        >
          <i class="fas fa-external-link-alt"></i>
        </a>
        <button 
          v-if="settings.gridCard?.showInfoButton" 
          class="btn-overlay-action" 
          @click.stop="emit('open-model', model.id)" 
          title="View Model Details"
        >
          <i class="fas fa-info-circle"></i>
        </button>
      </div>

      <!-- Info Overlay (when actions are NOT on image overlay) -->
      <div class="info-overlay" v-else-if="settings.gridCard?.showInfoButton">
        <button class="btn btn-icon" @click.stop="emit('open-model', model.id)" title="View Model Details">
          <i class="fas fa-info-circle"></i>
        </button>
      </div>
    </div>

    <div class="card-content">
      <h3 class="card-title" :title="settings.gridCard.titleDisplay === 'fileName' ? model.filename : model.name">{{ settings.gridCard.titleDisplay === 'fileName' ? getFilenameNoExt(model.filename) : model.name }}</h3>
      
      <div class="card-meta">
        <span class="meta-tag" v-if="isSlider && settings.gridCard?.showSliderRange !== false" :title="'Slider Range: ' + sliderRangeText">
          <i class="fas fa-sliders-h"></i> {{ sliderRangeText }}
        </span>
        <span class="meta-tag" v-if="model.folder && settings.gridCard?.showFolder !== false" :title="'Folder: ' + model.folder">
          <i class="fas fa-folder-open"></i> {{ displayedFolder }}
        </span>
        <span class="meta-tag" v-if="model.category && settings.gridCard?.showCategory !== false" :title="'Category: ' + model.category">
          <i class="fas fa-folder"></i> {{ model.category }}
        </span>
        <span class="meta-tag" v-if="model.baseModel && settings.gridCard?.showBaseModel !== false" :title="'Base Model: ' + model.baseModel">
          <i class="fas fa-cube"></i> {{ model.baseModel }}
        </span>
        <span class="meta-tag" v-if="(model.highLow || model.high_low) && settings.gridCard?.showHighLow !== false" :title="'High/Low: ' + (model.highLow || model.high_low)">
          <i class="fas fa-layer-group"></i> {{ model.highLow || model.high_low }}
        </span>
      </div>

      <!-- Standard Quick action buttons (when actionsPosition !== 'overlay') -->
      <div class="card-actions" v-if="!bulkStore.isBulkMode && settings.gridCard?.showActions && settings.gridCard?.actionsPosition !== 'overlay'">
        <button v-if="settings.gridCard?.showCopyTriggerWords" class="btn btn-small btn-secondary" @click.stop="copyActivationText" title="Copy Activation Text">
          <i class="fas fa-magic"></i>
        </button>
        <button v-if="settings.gridCard?.showCopyTriggerWords" class="btn btn-small btn-secondary" @click.stop="copyExamplePrompt" title="Copy Example Prompt">
          <i class="fas fa-comment-dots"></i>
        </button>
        <a 
          v-if="(model.civitai_url || model.civitaiUrl) && settings.gridCard?.showUrlButton" 
          :href="model.civitai_url || model.civitaiUrl" 
          target="_blank" 
          class="btn btn-small btn-secondary civitai-link"
          @click.stop
          title="Open in Civitai"
        >
          <i class="fas fa-external-link-alt civitai-icon"></i>
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
const isTested = computed(() => props.model.tested === true);
const isSlider = computed(() => props.model.isSlider === true || props.model.slider === true);
const sliderRangeText = computed(() => {
  const min = props.model.sliderMin !== undefined && props.model.sliderMin !== null ? props.model.sliderMin : -3;
  const max = props.model.sliderMax !== undefined && props.model.sliderMax !== null ? props.model.sliderMax : 3;
  const minDesc = props.model.sliderMinDesc ? ` (${props.model.sliderMinDesc})` : '';
  const maxDesc = props.model.sliderMaxDesc ? ` (${props.model.sliderMaxDesc})` : '';
  return `${min}${minDesc} to ${max}${maxDesc}`;
});

const displayedFolder = computed(() => {
  const folder = props.model.folder;
  if (!folder) return '';
  if (settings.gridCard?.truncateFolder) {
    const parts = folder.replace(/\\/g, '/').split('/').filter(Boolean);
    if (parts.length > 2) {
      return parts.slice(-2).join('/');
    }
  }
  return folder;
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

.card-badges {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
  z-index: 3;
  align-items: center;
}

.card-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.72em;
  font-weight: bold;
  letter-spacing: 0.3px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}

.icon-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}

.badge-nsfw {
  background-color: rgba(231, 76, 60, 0.9);
  color: white;
}

.badge-tested {
  background-color: rgba(46, 204, 113, 0.9);
  color: white;
}

.badge-slider {
  background-color: rgba(155, 89, 182, 0.9);
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

/* Semi-transparent Image Action Bar Overlay */
.image-actions-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 12px 10px 8px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.88) 0%, rgba(0, 0, 0, 0.45) 70%, transparent 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  opacity: 0.85;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 5;
  box-sizing: border-box;
}

.model-card:hover .image-actions-overlay {
  opacity: 1;
}

.btn-overlay-action {
  background: rgba(35, 35, 35, 0.65);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.88em;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  flex-shrink: 0;
}

.btn-overlay-action:hover {
  background: var(--color-btn-primary, #3498db);
  border-color: rgba(255, 255, 255, 0.6);
  color: #fff;
  transform: translateY(-2px) scale(1.08);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.6);
}

.btn-overlay-action:active {
  transform: translateY(0) scale(1);
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

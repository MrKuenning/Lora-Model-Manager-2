<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo">
        <i class="fas fa-cube"></i>
        <span>Lora Model Manager <small>v2.0.18</small></span>
      </div>
      <div class="view-toggles">
        <button 
          class="btn btn-icon" 
          :class="{ active: settings.defaultView === 'grid' }"
          @click="settings.defaultView = 'grid'"
          title="Grid View"
        >
          <i class="fas fa-th"></i>
        </button>
        <button 
          class="btn btn-icon" 
          :class="{ active: settings.defaultView === 'table' }"
          @click="settings.defaultView = 'table'"
          title="Table View"
        >
          <i class="fas fa-list"></i>
        </button>
      </div>
      
      <div class="location-toggle">
        <button 
          class="location-tab" 
          :class="{ active: models.currentLocation === 'loras' }"
          @click="models.setLocation('loras')"
        >
          LoRAs
        </button>
        <button 
          class="location-tab" 
          :class="{ active: models.currentLocation === 'checkpoints' }"
          @click="models.setLocation('checkpoints')"
        >
          Checkpoints
        </button>
      </div>
    </div>

    <div class="header-right">
      <button 
        class="btn" 
        :class="bulkStore.isBulkMode ? 'btn-primary' : 'btn-secondary'"
        @click="bulkStore.toggleBulkMode()"
      >
        <i class="fas fa-layer-group"></i> Bulk Edit
      </button>
      
      <button 
        class="btn btn-secondary" 
        @click="router.push('/scan')"
      >
        <i class="fas fa-magic"></i> Civitai Scan
      </button>
      
      <button 
        class="btn btn-secondary" 
        @click="emit('open-duplicates')"
      >
        <i class="fas fa-copy"></i> Duplicates
      </button>

      <button class="btn btn-secondary" @click="models.fetchModels(true)" title="Force Refresh from Disk">
        <i class="fas fa-sync-alt" :class="{ 'fa-spin': models.loading }"></i> Refresh
      </button>

      <div class="safemode-toggle">
        <span class="safemode-label">SafeMode</span>
        <label class="switch">
          <input type="checkbox" v-model="models.safemode">
          <span class="slider round"></span>
        </label>
      </div>

      <button class="settings-gear" @click="emit('open-settings')" title="Settings">
        <i class="fas fa-cog"></i>
      </button>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useSettingsStore } from '../../stores/settings';
import { useModelsStore } from '../../stores/models';
import { useBulkStore } from '../../stores/bulk';

const emit = defineEmits(['open-settings', 'open-duplicates']);
const router = useRouter();
const settings = useSettingsStore();
const models = useModelsStore();
const bulkStore = useBulkStore();
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-xl);
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

.logo i {
  color: var(--color-btn-primary);
  font-size: 1.2em;
}

.logo small {
  font-size: 0.6em;
  color: var(--color-btn-primary);
  background: rgba(52, 152, 219, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
}

.view-toggles {
  display: flex;
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-sm);
  padding: 2px;
}

.view-toggles .btn {
  background: transparent;
  border: none;
  padding: 6px 12px;
  color: var(--color-text-secondary);
}

.view-toggles .btn.active {
  background: var(--color-bg-hover);
  color: var(--color-text);
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.location-toggle {
  display: flex;
  background-color: var(--color-bg-tertiary);
  border-radius: 20px;
  padding: 3px;
}

.location-tab {
  padding: 6px 16px;
  border-radius: 16px;
  text-decoration: none;
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: all 0.2s ease;
  background: transparent;
  border: none;
  cursor: pointer;
}

.location-tab.active {
  background-color: var(--color-btn-primary);
  color: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.safemode-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-bg-tertiary);
  padding: 4px 12px;
  border-radius: 20px;
}

.safemode-label {
  font-weight: 600;
  font-size: 0.9em;
}

.settings-gear {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 1.4em;
  cursor: pointer;
  transition: transform 0.3s ease, color 0.2s ease;
}

.settings-gear:hover {
  color: var(--color-text);
  transform: rotate(45deg);
}
</style>

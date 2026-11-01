<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo">
        <i class="fas fa-cube"></i>
        <span>Lora Model Manager <small>v{{ appVersion }}</small></span>
      </div>

      <!-- Top-Level Navigation Switch: Models vs Manage Library -->
      <nav class="nav-tabs" aria-label="Main Navigation">
        <button 
          class="nav-tab" 
          :class="{ active: !isScanPage }"
          @click="router.push('/')"
          title="Browse & Manage Models"
        >
          <i class="fas fa-cubes"></i> Models
        </button>
        <button 
          class="nav-tab" 
          :class="{ active: isScanPage }"
          @click="router.push('/scan')"
          title="Metadata & Library Scans"
        >
          <i class="fas fa-radar"></i> Manage Library
        </button>
      </nav>

      <!-- View toggles: Grid/Table (Manager view only) -->
      <div v-if="!isScanPage" class="view-toggles">
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
      
      <!-- Location toggle: LoRAs vs Checkpoints -->
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
      <!-- Manager-Only Controls -->
      <template v-if="!isScanPage">
        <button 
          class="btn" 
          :class="bulkStore.isBulkMode ? 'btn-primary' : 'btn-secondary'"
          @click="bulkStore.toggleBulkMode()"
        >
          <i class="fas fa-layer-group"></i> Bulk Edit
        </button>
        
        <button 
          class="btn btn-secondary" 
          @click="emit('open-duplicates')"
        >
          <i class="fas fa-copy"></i> Duplicates
        </button>
      </template>

      <!-- Common Controls -->
      <button class="btn btn-secondary" @click="models.fetchModels(true)" title="Force Refresh from Disk">
        <i class="fas" :class="models.refreshing ? 'fa-spinner fa-spin' : 'fa-sync-alt'"></i> {{ models.refreshing ? 'Refreshing...' : 'Refresh' }}
      </button>

      <div class="safemode-toggle">
        <span class="safemode-label">SafeMode</span>
        <label class="switch">
          <input type="checkbox" v-model="models.safemode">
          <span class="slider round"></span>
        </label>
      </div>

      <button class="settings-gear" @click="openSettings" title="Settings">
        <i class="fas fa-cog"></i>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useSettingsStore } from '../../stores/settings';
import { useModelsStore } from '../../stores/models';
import { useBulkStore } from '../../stores/bulk';
import { version as appVersion } from '../../../package.json';

const emit = defineEmits(['open-settings', 'open-duplicates']);
const router = useRouter();
const route = useRoute();
const settings = useSettingsStore();
const models = useModelsStore();
const bulkStore = useBulkStore();

const isScanPage = computed(() => route.path === '/scan');

function openSettings() {
  settings.openSettings();
  emit('open-settings');
}
</script>

<style scoped>
.app-header {
  position: relative;
  z-index: 70;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-xl);
  background-color: var(--color-header-bg, var(--color-bg-secondary));
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
  backdrop-filter: blur(10px);
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

.nav-tabs {
  display: flex;
  background-color: var(--color-bg-tertiary);
  border-radius: 20px;
  padding: 3px;
  gap: 3px;
}

.nav-tab {
  padding: 6px 14px;
  border-radius: 16px;
  text-decoration: none;
  color: var(--color-text-secondary);
  font-weight: 500;
  font-size: 0.88em;
  transition: all 0.2s ease;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.nav-tab:hover {
  color: var(--color-text);
  background: var(--color-bg-hover);
}

[data-theme="midnight"] .nav-tab:not(.active):hover {
  border-color: rgba(56, 189, 248, 0.4);
  color: #f1f5f9;
}

.nav-tab.active {
  background: var(--tab-active-bg, var(--color-btn-primary));
  color: white;
  border-color: var(--tab-active-border, transparent);
  box-shadow: var(--tab-active-shadow, 0 2px 5px rgba(0,0,0,0.2));
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
  background: var(--toggle-active-bg, var(--color-bg-hover));
  color: var(--toggle-active-color, var(--color-text));
  border: 1px solid var(--toggle-active-border, transparent);
  box-shadow: var(--toggle-active-shadow, 0 1px 3px rgba(0,0,0,0.2));
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
  border: 1px solid transparent;
  cursor: pointer;
}

.location-tab.active {
  background: var(--tab-active-bg, var(--color-btn-primary));
  color: white;
  border-color: var(--tab-active-border, transparent);
  box-shadow: var(--tab-active-shadow, 0 2px 5px rgba(0,0,0,0.2));
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

<template>
  <router-view></router-view>
  <SettingsModal v-if="settingsStore.isSettingsOpen" @close="settingsStore.closeSettings" />
  <ToastContainer />
</template>

<script setup>
import { onMounted } from 'vue';
import ToastContainer from './components/shared/ToastContainer.vue';
import SettingsModal from './components/layout/SettingsModal.vue';
import { useSettingsStore } from './stores/settings';

const settingsStore = useSettingsStore();

onMounted(async () => {
  try {
    const cachedTheme = localStorage.getItem('theme') || 'slate';
    settingsStore.applyTheme(cachedTheme);
  } catch (e) {}
  await settingsStore.fetchSettings();
});
</script>

<style>
/* Global styles pulled from App1 */
@import './styles/variables.css';
@import './styles/base.css';

body {
  margin: 0;
  padding: 0;
  font-family: var(--font-family-base);
  background: var(--app-background, var(--color-bg-primary));
  color: var(--color-text);
  overflow: hidden; /* App wrapper handles scrolling */
}

/* Custom theme-matched scrollbars globally */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--scrollbar-track);
}

::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 5px;
  border: 2px solid var(--scrollbar-track);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover);
}

/* Base button styles since we use them everywhere */
.btn {
  padding: 8px 16px;
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--color-btn-secondary-border, transparent);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: var(--color-btn-secondary);
  color: var(--color-text);
}

.btn:hover {
  background-color: var(--color-btn-secondary-hover);
  border-color: var(--color-btn-secondary-hover-border, transparent);
  box-shadow: var(--color-btn-secondary-hover-shadow, none);
}

.btn-icon {
  background-color: transparent;
  color: var(--color-text-secondary);
  padding: 8px;
  border: 1px solid transparent;
}

.btn-icon:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
  border-color: var(--color-btn-secondary-hover-border, transparent);
}

.btn-primary {
  background: var(--color-btn-primary-bg, var(--color-btn-primary));
  color: white;
  border: 1px solid var(--color-btn-primary-border, transparent);
}

.btn-primary:hover {
  background: var(--color-btn-primary-hover-bg, var(--color-btn-primary-hover));
  border-color: var(--color-btn-primary-hover-border, transparent);
  box-shadow: var(--color-btn-primary-hover-shadow, none);
}

.btn-secondary {
  background: var(--color-btn-secondary);
  color: var(--color-text);
  border: 1px solid var(--color-btn-secondary-border, transparent);
}

.btn-secondary:hover {
  background: var(--color-btn-secondary-hover);
  border-color: var(--color-btn-secondary-hover-border, transparent);
  box-shadow: var(--color-btn-secondary-hover-shadow, none);
  color: #ffffff;
}

.btn-danger {
  background: var(--color-btn-danger);
  color: white;
  border: 1px solid var(--color-btn-danger-border, transparent);
}

.btn-danger:hover {
  background: var(--color-btn-danger-hover);
  border-color: var(--color-btn-danger-hover-border, transparent);
  box-shadow: var(--color-btn-danger-hover-shadow, none);
}

.btn-warning {
  background-color: var(--color-btn-warning);
  color: white;
  border: 1px solid transparent;
}

.btn-warning:hover {
  background-color: var(--color-btn-warning-hover);
}
</style>

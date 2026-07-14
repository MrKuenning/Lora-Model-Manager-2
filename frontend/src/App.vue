<template>
  <router-view></router-view>
  <ToastContainer />
</template>

<script setup>
import ToastContainer from './components/shared/ToastContainer.vue';
</script>

<style>
/* Global styles pulled from App1 */
@import './styles/variables.css';
@import './styles/base.css';

body {
  margin: 0;
  padding: 0;
  font-family: var(--font-family-base);
  background-color: var(--color-bg-primary);
  color: var(--color-text);
  overflow: hidden; /* App wrapper handles scrolling */
}

/* Base button styles since we use them everywhere */
.btn {
  padding: 8px 16px;
  border-radius: var(--border-radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition-standard);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: var(--color-btn-secondary);
  color: var(--color-text);
}

.btn:hover {
  background-color: var(--color-btn-secondary-hover);
}

.btn-icon {
  background-color: transparent;
  color: var(--color-text-secondary);
  padding: 8px;
}

.btn-icon:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text);
}

.btn-primary {
  background-color: var(--color-btn-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-btn-primary-hover);
}

.btn-secondary {
  background-color: var(--color-btn-secondary);
  color: var(--color-text);
}

.btn-secondary:hover {
  background-color: var(--color-btn-secondary-hover);
}

.btn-warning {
  background-color: var(--color-btn-warning);
  color: white;
}

.btn-warning:hover {
  background-color: var(--color-btn-warning-hover);
}
</style>

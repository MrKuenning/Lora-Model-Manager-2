<template>
  <div id="toast-container" class="toast-container">
    <TransitionGroup name="toast-list">
      <div 
        v-for="toast in toasts" 
        :key="toast.id" 
        class="toast" 
        :class="`toast-${toast.type}`"
        @click="removeToast(toast.id)"
      >
        <i class="fas" :class="toast.icon"></i>
        <span>{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '../../composables/useToast';

const { toasts, removeToast } = useToast();
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
  padding: 12px 20px;
  border-radius: var(--border-radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 250px;
  max-width: 400px;
  border-left: 4px solid var(--color-text-secondary);
  pointer-events: auto;
  cursor: pointer;
}

.toast-success {
  border-left-color: var(--color-btn-success);
}

.toast-error {
  border-left-color: #e74c3c;
}

.toast-warning {
  border-left-color: #f39c12;
}

.toast-info {
  border-left-color: var(--color-btn-primary);
}

.toast i {
  font-size: 1.2em;
}

.toast-success i { color: var(--color-btn-success); }
.toast-error i { color: #e74c3c; }
.toast-warning i { color: #f39c12; }
.toast-info i { color: var(--color-btn-primary); }

/* Transitions */
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}
.toast-list-enter-from {
  opacity: 0;
  transform: translateX(50px);
}
.toast-list-leave-to {
  opacity: 0;
  transform: translateX(50px);
}
</style>

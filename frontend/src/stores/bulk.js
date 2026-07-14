import { defineStore } from 'pinia';

export const useBulkStore = defineStore('bulk', {
  state: () => ({
    isBulkMode: false,
    selectedModelIds: new Set()
  }),

  getters: {
    selectedCount: (state) => state.selectedModelIds.size,
    hasSelection: (state) => state.selectedModelIds.size > 0,
    isSelected: (state) => (id) => state.selectedModelIds.has(id),
    getSelectedModels: (state) => (allModels) => allModels.filter(m => state.selectedModelIds.has(m.id))
  },

  actions: {
    toggleBulkMode() {
      this.isBulkMode = !this.isBulkMode;
      if (!this.isBulkMode) {
        this.clearSelection();
      }
    },

    toggleSelection(id) {
      if (this.selectedModelIds.has(id)) {
        this.selectedModelIds.delete(id);
      } else {
        this.selectedModelIds.add(id);
      }
    },

    selectAll(models) {
      models.forEach(m => this.selectedModelIds.add(m.id));
    },

    clearSelection() {
      this.selectedModelIds.clear();
    }
  }
});

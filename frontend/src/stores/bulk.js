import { defineStore } from 'pinia';

export const useBulkStore = defineStore('bulk', {
  state: () => ({
    isBulkMode: false,
    selectedModelIds: new Set(),
    lastSelectedId: null
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

    toggleSelection(id, event = null, orderedModels = null) {
      const isShift = event && event.shiftKey;

      if (isShift && this.lastSelectedId && Array.isArray(orderedModels) && orderedModels.length > 0) {
        const lastIdx = orderedModels.findIndex(m => m.id === this.lastSelectedId);
        const currIdx = orderedModels.findIndex(m => m.id === id);

        if (lastIdx !== -1 && currIdx !== -1) {
          const start = Math.min(lastIdx, currIdx);
          const end = Math.max(lastIdx, currIdx);
          const shouldSelect = !this.selectedModelIds.has(id);

          for (let i = start; i <= end; i++) {
            const modelId = orderedModels[i].id;
            if (shouldSelect) {
              this.selectedModelIds.add(modelId);
            } else {
              this.selectedModelIds.delete(modelId);
            }
          }
          this.lastSelectedId = id;
          return;
        }
      }

      if (this.selectedModelIds.has(id)) {
        this.selectedModelIds.delete(id);
      } else {
        this.selectedModelIds.add(id);
      }
      this.lastSelectedId = id;
    },

    selectAll(models) {
      models.forEach(m => this.selectedModelIds.add(m.id));
    },

    clearSelection() {
      this.selectedModelIds.clear();
      this.lastSelectedId = null;
    }
  }
});

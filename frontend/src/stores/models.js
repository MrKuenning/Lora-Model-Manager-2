import { defineStore } from 'pinia';
import { api } from '../api/client';
import { filterModelsByQuery } from '../composables/useSearch';

export const useModelsStore = defineStore('models', {
  state: () => ({
    models: [],
    folders: [],
    loading: false,
    error: null,
    searchQuery: '',
    currentLocation: 'loras', // 'loras' or 'checkpoints'
    sortBy: 'name-asc',
    groupBy: 'none',
    baseModelFilter: [], // array of selected base models, empty means 'all'
    currentFolder: '', // empty means root/all
    safemode: true,
    sidebarHidden: false,
    isTreeMode: true,
    sidebarSize: 'comfy', // 'comfy' or 'compact'
    flatHideRoot: false,
    flatHidePath: false,
    lastUpdated: Date.now(),
    modelUpdates: {}
  }),

  getters: {
    folderCounts: (state) => {
      // Pre-filter models by all filters EXCEPT folder filter
      let result = state.models;
      if (state.baseModelFilter && state.baseModelFilter.length > 0) {
        result = result.filter(m => {
          const sdVer = (m.baseModel || m.sdVersion || '').toLowerCase();
          return state.baseModelFilter.some(filterValue => {
            if (filterValue === 'sd' && sdVer.includes('1.5')) return true;
            return sdVer.includes(filterValue.toLowerCase());
          });
        });
      }
      if (state.safemode) {
        result = result.filter(m => String(m.nsfw).toLowerCase() !== 'true');
      }
      if (state.searchQuery) {
        result = filterModelsByQuery(result, state.searchQuery);
      }

      const counts = { immediate: {}, nested: {} };
      state.folders.forEach(f => {
        counts.immediate[f.path] = 0;
        counts.nested[f.path] = 0;
      });
      counts.immediate[''] = 0;
      counts.nested[''] = 0;

      result.forEach(m => {
        const f = m.folder || '';
        if (counts.immediate[f] !== undefined) {
          counts.immediate[f]++;
        } else {
          counts.immediate[f] = 1;
          counts.nested[f] = 0;
        }

        counts.nested['']++;
        let currentPath = '';
        const parts = f.split(/[\/\\]/).filter(p => p);
        for (let i = 0; i < parts.length; i++) {
          currentPath = currentPath ? `${currentPath}/${parts[i]}` : parts[i];
          if (counts.nested[currentPath] !== undefined) {
            counts.nested[currentPath]++;
          } else {
            counts.nested[currentPath] = 1;
          }
        }
      });
      return counts;
    },

    getCacheBuster: (state) => (path) => {
      return state.modelUpdates[path] || state.lastUpdated;
    },

    // Pipeline: 1. Folder -> 2. Base Model -> 3. SafeMode -> 4. Search -> 5. Sort
    filteredModels: (state) => {
      let result = state.models;

      // 1. Filter by folder
      if (state.currentFolder) {
        if (state.isTreeMode) {
          result = result.filter(m => m.folder === state.currentFolder || m.folder.startsWith(state.currentFolder + '/') || m.folder.startsWith(state.currentFolder + '\\'));
        } else {
          result = result.filter(m => m.folder === state.currentFolder);
        }
      }

      // 2. Filter by Base Model (array of strings)
      if (state.baseModelFilter && state.baseModelFilter.length > 0) {
        result = result.filter(m => {
          const sdVer = (m.baseModel || m.sdVersion || '').toLowerCase();
          return state.baseModelFilter.some(filterValue => {
            if (filterValue === 'sd' && sdVer.includes('1.5')) return true;
            return sdVer.includes(filterValue.toLowerCase());
          });
        });
      }

      // 3. SafeMode
      if (state.safemode) {
        result = result.filter(m => String(m.nsfw).toLowerCase() !== 'true');
      }

      // 4. Search Query (using our advanced parser)
      if (state.searchQuery) {
        result = filterModelsByQuery(result, state.searchQuery);
      }

      // 5. Sort
      return [...result].sort((a, b) => {
        let valA, valB;
        switch (state.sortBy) {
          case 'name-asc':
          case 'name-desc':
            valA = (a.name || '').toLowerCase();
            valB = (b.name || '').toLowerCase();
            break;
          case 'filename-asc':
          case 'filename-desc':
            valA = (a.filename || '').toLowerCase();
            valB = (b.filename || '').toLowerCase();
            break;
          case 'baseModel-asc':
          case 'baseModel-desc':
            valA = (a.baseModel || a.sdVersion || '').toLowerCase();
            valB = (b.baseModel || b.sdVersion || '').toLowerCase();
            break;
          case 'category-asc':
          case 'category-desc':
            valA = (a.category || '').toLowerCase();
            valB = (b.category || '').toLowerCase();
            break;
          case 'subcategory-asc':
          case 'subcategory-desc':
            valA = (a.subcategory || '').toLowerCase();
            valB = (b.subcategory || '').toLowerCase();
            break;
          case 'folder-asc':
          case 'folder-desc':
            valA = (a.folder || '').toLowerCase();
            valB = (b.folder || '').toLowerCase();
            break;
          case 'date-desc':
          case 'date-asc':
            valA = a.dateModified || 0;
            valB = b.dateModified || 0;
            break;
          case 'size-desc':
          case 'size-asc':
            valA = a.size || 0;
            valB = b.size || 0;
            break;
          default:
            valA = (a.name || '').toLowerCase();
            valB = (b.name || '').toLowerCase();
        }

        if (valA < valB) return state.sortBy.endsWith('-asc') ? -1 : 1;
        if (valA > valB) return state.sortBy.endsWith('-asc') ? 1 : -1;
        return 0;
      });
    },

    groupedModels: (state) => {
      const models = state.filteredModels;
      if (state.groupBy === 'none') return { 'All Models': models };

      const groups = {};
      models.forEach(model => {
        let key = 'Unknown';
        if (state.groupBy === 'baseModel') {
          key = model.baseModel || model.sdVersion || 'Unknown';
        } else if (state.groupBy === 'category') {
          key = model.category || 'Uncategorized';
        } else if (state.groupBy === 'subcategory') {
          key = model.subcategory || 'Uncategorized';
        } else if (state.groupBy === 'highLow') {
          key = model.highLow || 'Unknown';
        } else if (state.groupBy === 'nsfw') {
          key = String(model.nsfw).toLowerCase() === 'true' ? 'NSFW' : 'SFW';
        } else if (state.groupBy === 'size') {
          const mb = (model.size || 0) / (1024 * 1024);
          if (mb < 50) key = 'Small (<50MB)';
          else if (mb < 200) key = 'Medium (50-200MB)';
          else if (mb < 1000) key = 'Large (200MB-1GB)';
          else key = 'Huge (>1GB)';
        } else if (state.groupBy === 'tags') {
          // Models can have multiple tags, so we might want to duplicate models into multiple groups,
          // but for a simple grouping we usually pick the first tag or group by exact tag string.
          // Let's use the first tag, or "Untagged"
          if (model.tags && typeof model.tags === 'string' && model.tags.trim()) {
            key = model.tags.split(',')[0].trim() || 'Untagged';
          } else if (Array.isArray(model.tags) && model.tags.length > 0) {
            key = model.tags[0].trim() || 'Untagged';
          } else {
            key = 'Untagged';
          }
        } else if (state.groupBy === 'folder') {
          key = model.folder || 'Root';
        }

        if (!groups[key]) groups[key] = [];
        groups[key].push(model);
      });

      // Sort keys
      return Object.keys(groups).sort().reduce((acc, key) => {
        acc[key] = groups[key];
        return acc;
      }, {});
    },

    uniqueBaseModels: (state) => {
      const bases = new Set();
      state.models.forEach(m => {
        if (m.baseModel) bases.add(m.baseModel);
        else if (m.sdVersion) bases.add(m.sdVersion);
      });
      return Array.from(bases).sort();
    }
  },

  actions: {
    async fetchModels(refresh = false) {
      if (this.models.length === 0) {
        this.loading = true;
      }
      this.error = null;
      try {
        const fetchedModels = await api.getModels(this.currentLocation, refresh);
        this.models = fetchedModels;
        if (refresh) {
          this.lastUpdated = Date.now();
        }
        await this.fetchFolders();
      } catch (err) {
        this.error = err.response?.data?.error || err.message;
      } finally {
        this.loading = false;
      }
    },

    async fetchFolders() {
      try {
        this.folders = await api.getFolders(this.currentLocation);
      } catch (err) {
        console.error("Failed to load folders", err);
      }
    },

    setLocation(loc) {
      if (this.currentLocation !== loc) {
        this.currentLocation = loc;
        this.currentFolder = '';
        this.models = [];
        this.fetchModels();
      }
    },

    async deleteModel(modelId, modelPath) {
      try {
        await api.deleteModel(modelId, modelPath);
        this.models = this.models.filter(m => m.id !== modelId);
        return true;
      } catch (err) {
        throw new Error(err.response?.data?.message || err.message);
      }
    },

    async reloadSingleModel(modelId) {
      try {
        const updated = await api.getModel(modelId, this.currentLocation);
        const index = this.models.findIndex(m => m.id === modelId);
        if (index !== -1) {
          this.models[index] = updated;
        } else {
          this.models.push(updated);
        }
        if (updated.path) {
          this.modelUpdates[updated.path] = Date.now();
        }
      } catch (err) {
        console.error("Failed to reload model", err);
      }
    }
  }
});

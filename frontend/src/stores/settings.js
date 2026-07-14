import { defineStore } from 'pinia';
import { api } from '../api/client';

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    modelsDirectory: '',
    checkpointsDirectory: '',
    defaultDownloadDirectory: '',
    defaultSortingDirectory: '',
    theme: 'dark',
    defaultView: 'grid',
    defaultSort: 'name-asc',
    safeModeDefault: true,
    safeModeOnReload: true,
    nsfwBlurOverlay: true,
    filterFoldersWithBaseModel: false,
    columnOrder: [
      'thumbnail',
      'name',
      'civitaiName',
      'baseModel',
      'category',
      'size',
      'date',
      'filename'
    ],
    gridCard: {
      titleDisplay: 'modelName', // 'modelName' or 'fileName'
      cardSize: 'medium', // 'small', 'medium', 'large'
      showBaseModel: true,
      showCategory: true,
      showFolder: true,
      showHighLow: true,
      showActions: true,
      showCopyTriggerWords: true,
      showUrlButton: true,
      showNsfwBadge: true,
      showInfoButton: true
    },
    visibleColumns: {
      thumbnail: true,
      filename: true,
      civitaiName: true,
      baseModel: true,
      category: true,
      path: true,
      size: true,
      date: true,
      url: true,
      nsfw: true,
      positiveWords: true,
      negativeWords: true,
      authorsWords: true,
      description: true
    },
    filenameFormats: [],
    modelTypeRoots: [],
    trimNames: [
      'Pony', 'PXL', '[P]', '[Pony]', '[PXL]',
      'SDXL', 'SDXL 1.0', 'SDXL1.0', '[X]', '[SDXL]',
      'SD', 'SD 1.5', 'SD1.5', 'SD 1.4', 'SD1.4', 'SD1', '[SD]',
      'SD 2.0', 'SD2.0', 'SD 2.1', 'SD2.1', 'SD2',
      'Illustrious', 'Ill', '[I]', '[Ill]', '[Illustrious]',
      'Noob', 'NoobAI', 'Noob AI', '[Noob]', '[N]',
      'ZImageTurbo', 'Zit', '[Z]', '[Zit]', 'Z Turbo', 'Z-Image', 'ZImage',
      'Flux', 'Flux.1', 'Flux 1', '[Flux]', '[F]',
      'Wan', 'Wan21', 'Wan 2.1', 'Wan2.1', 'Wan22', 'Wan 2.2', 'Wan2.2',
      'Wan Video', 'Wan Video 14B', 'WanVideo', '[Wan]', '[W]',
      'T2V', 'I2V', '14B', '[WAN 2.2 I2V]',
      'Hunyuan', 'HunyuanVideo', 'Hunyuan Video', '[Hunyuan]', '[H]',
      'CogVideo', 'Cog', 'CogVideoX', '[Cog]', '[CogVideo]',
      'Mochi', '[Mochi]', '[M]',
      'LTX', 'LTX Video', 'LTXVideo', '[LTX]', '[L]',
      'Krea', 'Krea 2', 'Krea2', '[Krea]',
      'Anima', 'Anima Pencil', '[Anima]',
      'Ernie', 'Ernie Bot', '[Ernie]',
      'Kling', 'Luma', 'Sora', 'Minimax', 'Haiper', 'Midjourney', 'DALL-E', 'DALLE', 'Klein', 'Klein9b',
      'LoRA',
      'Checkpoint', 'ckpt',
      'Embedding', 'TI', 'Textual Inversion',
      'High', 'Low', '720p', '1080p', '4K',
      'XL', 'Turbo', 'Lightning', 'LCM', 'Hyper', 'for'
    ],
    scanSettings: {
      skipExistingData: true,
      skipNsfwPreviews: true,
      downloadMaxSize: false,
      fetchCreatorInfo: true,
      delayBetweenRequests: 0.5
    },
    loading: false
  }),

  actions: {
    async fetchSettings() {
      this.loading = true;
      try {
        const data = await api.getSettings();
        
        // Handle backwards compatibility for filenameFormat (object) -> filenameFormats (array)
        if (data.filenameFormat && !Array.isArray(data.filenameFormat)) {
          const arr = [];
          for (const [key, value] of Object.entries(data.filenameFormat)) {
            arr.push({ baseModel: key, format: value });
          }
          data.filenameFormats = arr;
          delete data.filenameFormat;
        }
        
        // Handle backwards compatibility for modelTypeRoots (object) -> array
        if (data.modelTypeRoots && !Array.isArray(data.modelTypeRoots)) {
          const arr = [];
          for (const [key, value] of Object.entries(data.modelTypeRoots)) {
            arr.push({ baseModel: key, rootFolder: value });
          }
          data.modelTypeRoots = arr;
        }

        // Handle backward compatibility for trimNames (unescape regex literals)
        if (data.trimNames && Array.isArray(data.trimNames)) {
          data.trimNames = data.trimNames.map(name => name.replace(/\\(.)/g, '$1'));
        }

        // Merge fetched settings with state
        Object.assign(this, data);
        
        // Apply theme to document
        document.body.className = this.theme;
      } catch (err) {
        console.error("Failed to load settings", err);
      } finally {
        this.loading = false;
      }
    },

    async saveSettings(newSettings) {
      try {
        if (newSettings.filenameFormats) {
          newSettings.filenameFormats.sort((a, b) => {
            const baseA = a.baseModel || '';
            const baseB = b.baseModel || '';
            if (baseA === 'Default') return -1;
            if (baseB === 'Default') return 1;
            return baseA.localeCompare(baseB, undefined, { sensitivity: 'base' });
          });
        }
        if (newSettings.modelTypeRoots) {
          newSettings.modelTypeRoots.sort((a, b) => {
            const baseA = a.baseModel || '';
            const baseB = b.baseModel || '';
            return baseA.localeCompare(baseB, undefined, { sensitivity: 'base' });
          });
        }
        if (newSettings.trimNames) {
          const unique = new Map();
          newSettings.trimNames.forEach(name => {
            if (name && name.trim()) {
              const lower = name.trim().toLowerCase();
              if (!unique.has(lower)) {
                unique.set(lower, name.trim());
              }
            }
          });
          newSettings.trimNames = Array.from(unique.values()).sort((a, b) => {
            const cleanA = a.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
            const cleanB = b.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
            return cleanA.localeCompare(cleanB);
          });
        }
        await api.saveSettings(newSettings);
        Object.assign(this, newSettings);
        document.body.className = this.theme;
        return true;
      } catch (err) {
        console.error("Failed to save settings", err);
        return false;
      }
    }
  }
});

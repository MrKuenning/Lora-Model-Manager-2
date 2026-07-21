import axios from 'axios';

// Create an Axios instance with a base URL matching our Flask backend
// In production, the backend serves the frontend on the same port, so we can use relative paths
// In development, we use Vite on 5173 and proxy to Flask on 8080 (or absolute URL if CORS)
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Helper for file uploads since they require multipart/form-data
const fileUploadClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});

export const api = {
  // Settings
  getSettings: () => apiClient.get('/settings').then(res => res.data),
  saveSettings: (settings) => apiClient.put('/settings', settings).then(res => res.data),
  browseFolder: () => apiClient.post('/settings/browse').then(res => res.data),
  
  // Folders
  getFolders: (location) => apiClient.get(`/folders?location=${location}`).then(res => res.data.folders),
  sortDownloads: () => apiClient.post('/files/sort-downloads').then(res => res.data),
  
  // Associated Files
  getAssociatedFiles: (modelPath) => apiClient.get(`/files/associated?modelPath=${encodeURIComponent(modelPath)}`).then(res => res.data.files),
  deleteAssociatedFile: (filePath) => apiClient.delete('/files/associated', { data: { filePath } }).then(res => res.data),
  
  // Helper to safely encode IDs which might contain slashes
  _encodeId: (id) => id ? id.split('/').map(encodeURIComponent).join('/') : '',

  // Models
  getModels: (location, refresh = false) => apiClient.get(`/models?location=${location}&refresh=${refresh}`).then(res => res.data),
  getModel: (id, location) => apiClient.get(`/models/${api._encodeId(id)}?location=${location}`).then(res => res.data),
  saveModel: (id, data) => apiClient.put(`/models/${api._encodeId(id)}`, data).then(res => res.data),
  saveModelJson: (id, jsonData) => apiClient.put(`/models/${api._encodeId(id)}/json`, jsonData).then(res => res.data),
  renameModel: (id, newName) => apiClient.post(`/models/${api._encodeId(id)}/rename`, { newName }).then(res => res.data),
  moveModel: (id, targetFolder) => apiClient.post(`/models/${api._encodeId(id)}/move`, { targetFolder }).then(res => res.data),
  deleteModel: (id, modelPath) => apiClient.delete(`/models/${api._encodeId(id)}`, { data: { modelPath } }).then(res => res.data),
  generateHash: (id, modelPath) => apiClient.post(`/models/${api._encodeId(id)}/hash`, { modelPath }).then(res => res.data),
  
  // Files / Previews
  openFolder: (path) => apiClient.post('/files/open-folder', { path }).then(res => res.data),
  uploadPreview: (id, location, imageFile) => {
    const formData = new FormData();
    formData.append('imageFile', imageFile);
    formData.append('location', location);
    return fileUploadClient.post(`/models/${api._encodeId(id)}/preview`, formData).then(res => res.data);
  },
  deleteThumbnail: (id, location, thumbnailIndex) => apiClient.delete(`/models/${api._encodeId(id)}/thumbnail`, { data: { location, thumbnailIndex } }).then(res => res.data),
  reorderThumbnails: (id, location, newOrder) => apiClient.post(`/models/${api._encodeId(id)}/thumbnails/reorder`, { location, newOrder }).then(res => res.data),
  
  // Civitai
  civitaiScan: (location) => apiClient.post(`/civitai/scan?location=${location}`).then(res => res.data),
  civitaiFetchByHash: (modelPath) => apiClient.post('/civitai/fetch-by-hash', { modelPath }).then(res => res.data),
  civArchiveFetchByHash: (modelPath) => apiClient.post('/civarchive/fetch-by-hash', { modelPath }).then(res => res.data),
  civitaiFetchByUrl: (modelPath, civitaiUrl) => apiClient.post('/civitai/fetch-by-url', { modelPath, civitaiUrl }).then(res => res.data),
  civitaiDownloadPreview: (modelPath, skipNsfw = true, maxSize = false, forceAdditional = false) => 
    apiClient.post('/civitai/download-preview', { modelPath, skipNsfw, maxSize, forceAdditional }).then(res => res.data),
  civitaiConvertToJson: (modelPath, useApi = true) => apiClient.post('/civitai/convert', { modelPath, useApi }).then(res => res.data),
  civitaiFixThumbnail: (modelPath) => apiClient.post('/civitai/fix-thumbnail', { modelPath }).then(res => res.data),
  civitaiCreatePlaceholder: (modelPath) => apiClient.post('/civitai/create-placeholder', { modelPath }).then(res => res.data),
  civitaiGenerateHash: (modelPath, skipIfExists = false) => apiClient.post('/civitai/generate-hash', { modelPath, skipIfExists }).then(res => res.data),
  civitaiFindDuplicates: (location) => apiClient.post('/civitai/find-duplicates', { location }).then(res => res.data),
  
  // Helper for generating local asset URLs
  getAssetUrl: (path, cacheBuster = '') => {
    if (!path) return '/assets/placeholder.png';
    if (path.startsWith('http')) return path; // external URL
    
    let url = '';
    if (path.startsWith('/assets/')) {
      url = path;
    } else {
      // Convert relative model paths to the static file server route
      const modelFilePath = path.startsWith('/') ? path.substring(1) : path;
      url = `/model-file/${modelFilePath}`;
    }
    
    if (cacheBuster) {
      url += (url.includes('?') ? '&' : '?') + `t=${cacheBuster}`;
    }
    return url;
  }
};

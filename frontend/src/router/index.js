import { createRouter, createWebHistory } from 'vue-router';
import ManagerView from '../views/ManagerView.vue';
import CivitaiScanView from '../views/CivitaiScanView.vue';

const routes = [
  {
    path: '/',
    name: 'Manager',
    component: ManagerView
  },
  {
    path: '/scan',
    name: 'CivitaiScan',
    component: CivitaiScanView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;

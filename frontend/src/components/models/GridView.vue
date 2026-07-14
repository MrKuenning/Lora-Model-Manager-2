<template>
  <div :class="['grid-view', 'size-' + settings.gridCard.cardSize]">
    <ModelCard 
      v-for="model in models" 
      :key="model.id" 
      :model="model"
      @open-model="id => emit('open-model', id)"
    />
  </div>
</template>

<script setup>
import ModelCard from './ModelCard.vue';
import { useSettingsStore } from '../../stores/settings';

const settings = useSettingsStore();

defineProps({
  models: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['open-model']);
</script>

<style scoped>
.grid-view {
  display: grid;
  gap: 20px;
  padding-bottom: 40px;
}

.grid-view.size-small {
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
}

.grid-view.size-medium {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.grid-view.size-large {
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}
</style>

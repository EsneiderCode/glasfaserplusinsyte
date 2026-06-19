<template>
  <div>
    <template v-if="compact">
      <span v-for="(val, key) in flatData" :key="key" class="mr-3 text-sm">
        <span class="text-500 font-semibold">{{ key }}:</span>
        <span class="text-900 ml-1">{{ formatValue(val) }}</span>
      </span>
    </template>
    <template v-else>
      <div v-for="(val, key) in flatData" :key="key" class="flex gap-2 mb-1 text-sm">
        <span class="text-500 font-semibold" style="min-width: 140px">{{ key }}</span>
        <span class="text-900">{{ formatValue(val) }}</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: [Object, Array], default: () => ({}) },
  compact: { type: Boolean, default: false },
})

const flatData = computed(() => {
  if (!props.data || typeof props.data !== 'object') return {}
  if (Array.isArray(props.data)) return props.data
  return props.data
})

function formatValue(val) {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}
</script>

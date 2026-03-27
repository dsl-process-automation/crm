<template>
  <span
    v-if="value"
    class="inline-block max-w-[200px] truncate rounded px-2 py-0.5 text-xs font-medium"
    :class="colorClass"
    :title="value"
  >
    {{ value }}
  </span>
  <span v-else class="text-ink-gray-4">—</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: String,
})

const colorClass = computed(() => {
  const v = props.value || ''
  if (v.startsWith('Happy') || v.includes('recommending'))
    return 'bg-surface-green-1 text-ink-gray-8'
  if (v.startsWith('Satisfied') || v.startsWith('Members'))
    return 'bg-surface-blue-1 text-ink-gray-8'
  if (v.startsWith('Disappointed') || v.includes('Limited'))
    return 'bg-surface-amber-1 text-ink-gray-8'
  if (v.startsWith('new partnership') || v.includes('not started'))
    return 'bg-surface-gray-2 text-ink-gray-6'
  return 'bg-surface-gray-2 text-ink-gray-6'
})
</script>

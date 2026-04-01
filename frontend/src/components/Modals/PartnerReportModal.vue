<template>
  <Dialog v-model="show" :options="{ size: '7xl' }">
    <template #body-title>
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
          {{ __('New Partner Report') }}
        </h3>
        <Button variant="ghost" class="w-7" icon="x" @click="show = false" />
      </div>
    </template>
    <template #body-content>
      <div class="-mx-4 -mb-4 sm:-mx-6 max-h-[82vh] overflow-hidden">
        <PartnerReport report-id="new" :in-dialog="true" @submitted="handleSubmitted" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import PartnerReport from '@/pages/PartnerReport.vue'
import { Button } from 'frappe-ui'

const show = defineModel({ type: Boolean })

const emit = defineEmits(['submitted'])

function handleSubmitted(name) {
  emit('submitted', name)
  show.value = false
}
</script>